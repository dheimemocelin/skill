"""Owned process trees; a stdin handshake prevents execution before containment.

Windows uses a kill-on-close Job Object. POSIX uses a new process session.
Raw output is never written to disk. Detached POSIX processes remain outside this
boundary; callers must treat a lost parent/unknown outcome conservatively.
"""

import base64
import ctypes
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import threading
import time


class WindowsJob:
    def __init__(self, pid):
        from ctypes import wintypes as w

        class Basic(ctypes.Structure):
            _fields_ = [("process_time", ctypes.c_int64), ("job_time", ctypes.c_int64),
                        ("flags", w.DWORD), ("min_ws", ctypes.c_size_t), ("max_ws", ctypes.c_size_t),
                        ("active_limit", w.DWORD), ("affinity", ctypes.c_size_t),
                        ("priority", w.DWORD), ("scheduling", w.DWORD)]

        class IO(ctypes.Structure):
            _fields_ = [(name, ctypes.c_uint64) for name in ("ro", "wo", "oo", "rb", "wb", "ob")]

        class Extended(ctypes.Structure):
            _fields_ = [("basic", Basic), ("io", IO)] + [(n, ctypes.c_size_t) for n in ("process_mem", "job_mem", "peak_process", "peak_job")]

        self.api = ctypes.WinDLL("kernel32", use_last_error=True)
        for name, args, result in (
            ("CreateJobObjectW", [w.LPVOID, w.LPCWSTR], w.HANDLE),
            ("SetInformationJobObject", [w.HANDLE, ctypes.c_int, w.LPVOID, w.DWORD], w.BOOL),
            ("OpenProcess", [w.DWORD, w.BOOL, w.DWORD], w.HANDLE),
            ("AssignProcessToJobObject", [w.HANDLE, w.HANDLE], w.BOOL),
            ("TerminateJobObject", [w.HANDLE, w.UINT], w.BOOL),
            ("QueryInformationJobObject", [w.HANDLE, ctypes.c_int, w.LPVOID, w.DWORD, w.LPVOID], w.BOOL),
            ("CloseHandle", [w.HANDLE], w.BOOL),
        ):
            fn = getattr(self.api, name)
            fn.argtypes, fn.restype = args, result
        self.handle = self.api.CreateJobObjectW(None, None)
        if not self.handle:
            raise OSError("Job creation failed")
        limits = Extended()
        limits.basic.flags = 0x2000  # JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
        process_handle = self.api.OpenProcess(0x0100 | 0x0001, False, pid)
        try:
            if not self.api.SetInformationJobObject(self.handle, 9, ctypes.byref(limits), ctypes.sizeof(limits)) or not process_handle or not self.api.AssignProcessToJobObject(self.handle, process_handle):
                raise OSError("Process containment unavailable")
        except Exception:
            self.close()
            raise
        finally:
            if process_handle:
                self.api.CloseHandle(process_handle)

    def stop(self):
        # JOBOBJECT_BASIC_ACCOUNTING_INFORMATION: four int64, four DWORD.
        class Accounting(ctypes.Structure):
            _fields_ = [(n, ctypes.c_int64) for n in ("user", "kernel", "period_user", "period_kernel")] + [(n, ctypes.c_uint32) for n in ("faults", "total", "active", "terminated")]
        self.api.TerminateJobObject(self.handle, 1)
        for _ in range(50):
            info = Accounting()
            if self.api.QueryInformationJobObject(self.handle, 1, ctypes.byref(info), ctypes.sizeof(info), None) and info.active == 0:
                return True
            time.sleep(0.02)
        return False

    def close(self):
        if self.handle:
            self.api.CloseHandle(self.handle)
            self.handle = None


def _stop_group(child):
    try:
        os.killpg(child.pid, signal.SIGKILL)
    except ProcessLookupError:
        return True
    except OSError:
        return False
    child.wait(timeout=5)
    for _ in range(50):
        try:
            os.killpg(child.pid, 0)
        except ProcessLookupError:
            return True
        except OSError:
            return False
        time.sleep(0.02)
    return False


def run_process(command, workspace, timeout, payload=None, capture=False, on_line=None, env=None):
    started = time.monotonic()
    child = subprocess.Popen([sys.executable, "-I", str(Path(__file__).resolve())], cwd=workspace,
                             stdin=subprocess.PIPE, stdout=subprocess.PIPE if capture or on_line else subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL, start_new_session=os.name != "nt", env=env)
    job, reader = None, None
    output, truncated, reader_error = bytearray(), False, False

    def drain():
        nonlocal truncated, reader_error
        discarding = False
        try:
            while line := child.stdout.readline(65537):
                if len(line) > 65536 or discarding:
                    truncated = True
                    discarding = not line.endswith(b"\n")
                    continue
                if on_line:
                    on_line(line)
                if capture:
                    if len(output) + len(line) <= 4_000_000:
                        output.extend(line)
                    else:
                        truncated = True
        except Exception:
            reader_error = True

    timed_out, interrupted, confirmed = False, False, False
    code = None
    try:
        if os.name == "nt":
            job = WindowsJob(child.pid)
        if capture or on_line:
            reader = threading.Thread(target=drain, daemon=True)
            reader.start()
        message = json.dumps({"command": command, "payload": base64.b64encode(payload).decode() if payload is not None else None}).encode() + b"\n"
        child.stdin.write(message)
        child.stdin.close()
        try:
            code = child.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            timed_out = True
        except KeyboardInterrupt:
            interrupted = True
    finally:
        if job:
            confirmed = job.stop()
            job.close()
        elif os.name != "nt":
            confirmed = _stop_group(child)
        else:
            # No command was sent if Job Object setup failed.
            child.kill()
        child.wait(timeout=5)
        if reader:
            reader.join(timeout=2)
            if reader.is_alive():
                confirmed = False
        if child.stdout and (not reader or not reader.is_alive()):
            child.stdout.close()
        if not child.stdin.closed:
            child.stdin.close()
    if interrupted:
        raise KeyboardInterrupt
    return {"exit_code": code if code is not None else child.returncode, "timeout": timed_out,
            "seconds": round(time.monotonic() - started, 3), "termination_confirmed": confirmed,
            "output_truncated": truncated or reader_error}, bytes(output) if capture else None


def bridge():
    message = json.loads(sys.stdin.buffer.readline())
    payload = base64.b64decode(message["payload"]) if message["payload"] is not None else None
    try:
        process = subprocess.Popen(message["command"], stdin=subprocess.PIPE if payload is not None else subprocess.DEVNULL,
                                   stdout=sys.stdout.buffer, stderr=subprocess.DEVNULL, shell=False)
        process.communicate(payload)
        return process.returncode if process.returncode >= 0 else 1
    except OSError:
        return 127


if __name__ == "__main__":
    sys.exit(bridge())
