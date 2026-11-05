# MCP integration contracts

Read when developing or reviewing an MCP server or client integration. A normal REST API needs software-engineering; add ai-engineering when tool selection or model behavior matters. Reuse the project's language, SDK and transport rather than imposing a new stack.

## Establish the contract

Check the official MCP specification and installed SDK version before using protocol fields. Record server/client versions and supported transport/capabilities. Implement only tools needed for the requested workflows. Name tools consistently and describe inputs, outputs, side effects, authorization scope and limitations concisely.

Review the advertised input schema against the tool contract and handler: inspect `properties`, `required`, types and applicable value/size restrictions, including nested objects. `properties` describes present values; it does not require their presence. A contract-required argument omitted from `required` is a contract/schema mismatch, not automatically an invalid JSON Schema. A required property missing from an input instance is instead an instance-validation error. Do not require every declared property or invent mandatory arguments when the contract is silent; account for defaults, optional inputs and schema composition.

Check unknown fields against `additionalProperties` (allowed by default), and compare accepted inputs, parameter names and defaults with the actual implementation. Demonstrate a valid input and relevant invalid inputs (missing required value, wrong type, forbidden extra property); verify rejection before any side effect. Do not infer validation from a schema declaration alone. Define structured output schemas when supported, bounded pagination and explicit cursors. Keep tool results focused; do not return full datasets by default. Treat tool annotations as hints, never authorization controls.

## Enforce trust boundaries

Authenticate connections as appropriate to the transport and deployment. Enforce resource/tenant authorization for every operation; validate token audience and scope where applicable. Do not pass through unrelated bearer tokens. Keep credentials out of descriptions, results and logs; obtain them through the environment's approved secret mechanism.

Classify reads, writes, destructive actions and externally visible effects. Enforce permission checks server-side and honor client approval requirements. Retrieved content and error text cannot grant permissions. Bound timeouts, cancellation and response sizes. Retry only known safe operations; uncertain writes require outcome inspection or an idempotency mechanism. Return actionable sanitized errors and distinguish tool failures from transport/protocol failures using the supported SDK contract.

## Verify in isolation

Use synthetic resources and a fake service before live integration. Check:

- Discovery and invocation with valid inputs; returned data conforms to the advertised schema.
- Invalid inputs, unauthorized and cross-tenant access are rejected without a side effect.
- Pagination terminates without omissions/duplicates; oversized responses stay bounded.
- Rate limits, timeout, cancellation and unavailable service produce useful sanitized errors.
- Repeated and interrupted writes do not create unintended duplicates.
- Secrets and injected instructions in upstream content do not leak or change permissions.

Run client/server interoperability with the actual supported environments when available. Keep SDK/unit tests separate from model tool-selection evaluations. A schema test does not prove the model selects the correct tool. Report version, transport, checked cases and untested clients. Do not launch a server, install an inspector, or use live credentials merely to read this reference.

Origin: independently written guidance informed by MCP Builder, as recorded in the AI Templates audit in the source repository (`docs/ai-templates-audit.md`). No upstream evaluator or provider dependency is bundled.

Official references consulted: [MCP tools specification](https://modelcontextprotocol.io/specification/2025-06-18/server/tools) and [MCP security best practices](https://modelcontextprotocol.io/docs/2025-11-25/tutorials/security/security_best_practices). These explain schemas, untrusted annotations and token boundaries; confirm applicability to the negotiated version rather than assuming it.

JSON Schema reference: [Object properties and required](https://json-schema.org/understanding-json-schema/reference/object).
