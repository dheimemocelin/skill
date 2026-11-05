# Diagnóstico do sandbox — 2026-11-05

## Conclusão

Causa confirmada do bloqueio observado: a política AppArmor do Ubuntu restringe as capabilities no user namespace criado pelo Bubblewrap embutido no Codex. O helper entra em `unprivileged_userns (enforce)` e o kernel nega `net_admin` e `setpcap`. A negação de NET_ADMIN é consistente com a falha de configuração do endereço do loopback via RTM_NEWADDR. Não é um defeito das skills nem uma falha de autenticação do provider.

O pacote Bubblewrap do sistema está ausente, logo o executor usa seu helper embutido numa instalação sob o home do usuário. A correção candidata é usar o pacote da distribuição e seu perfil AppArmor apropriado, mantendo a restrição global ativa. A correção ainda não foi aplicada ou validada. Nenhuma instalação, mudança de perfil, sysctl, capability, sandbox, skill ou configuração do Codex foi feita neste diagnóstico.

## Ambiente e evidências

- Ubuntu 24.04.5 LTS, kernel AWS `7.0.0-1012-aws`, x86_64; `systemd-detect-virt --vm` retorna `amazon`; `--container` retorna `none`. Evidências indicam VM AWS, sem container detectado. Isto não é prova da ausência de toda camada externa do provedor.
- UID/GID 1000, processo pai fora de sandbox OS identificado: AppArmor `unconfined`, `Seccomp: 0`, `NoNewPrivs: 0`, CapEff/CapPrm/CapAmb zerados. Não há filtro seccomp ou política de container visível explicando esta falha.
- Namespace IDs do processo correspondem aos namespaces iniciais usuais: user `4026531837`, net `4026531833`, pid `4026531836`; NSpid tem um nível. `/proc/1/ns` foi inacessível ao usuário, portanto a comparação direta com PID 1 ficou limitada. Cgroup: `0::/init.scope`.
- `kernel.unprivileged_userns_clone=1`; `user.max_user_namespaces=12455`; `user.max_net_namespaces=12455`. Não há limite zero ou bloqueio global de criação.
- AppArmor ativo (`Y`), `kernel.apparmor_restrict_unprivileged_userns=1`; perfil `unprivileged_userns (enforce)` carregado. Nenhum perfil bwrap/codex foi encontrado na lista consultada.
- `unshare --user` cria namespace novo e passa para `unprivileged_userns (enforce)`. `unshare --user --map-root-user` falha ao escrever uid_map; kernel registra negação `sys_admin`. Habilitar userns não garante que seu mapeamento/capabilities seja autorizado.
- `unshare --user --net` cria net namespace `4026532426`, mas `ip link set lo up` retorna `RTNETLINK answers: Operation not permitted`. Sem userns, `unshare --net` falha por ausência normal de privilégio.
- Codex CLI `0.166.0`. `codex sandbox -- /usr/bin/true` reproduz o erro bwrap sem chamada de modelo. A tentativa exploratória `codex sandbox linux --help` também iniciou o sandbox e falhou; a ajuda desta versão documenta `codex sandbox -- COMMAND`, que é a sintaxe usada na reprodução mínima.
- `~/.codex/config.toml` foi lido seletivamente com tomllib: apenas chaves superiores `projects` e `tui`, sem overrides sandbox/features identificados. Conteúdo das entradas e credenciais não foi impresso. Não existe `.codex/config.toml` no projeto; arquivos usuais em `/etc/codex` consultados não foram encontrados. Isto não exclui políticas gerenciadas entregues por outro mecanismo.
- `command -v bwrap` não encontra executável; `/usr/bin/bwrap` ausente; `dpkg-query`/`apt-cache policy` confirmam bubblewrap não instalado. Candidato local: `0.9.0-1ubuntu0.3`. `apparmor-profiles` e `apparmor-utils` ausentes; `/usr/sbin/apparmor_parser` existe. Perfil extra bwrap não encontrado nos dois caminhos consultados.
- Helper observado no audit do kernel: `/home/ubuntu/.nvm/versions/node/v24.21.0/lib/node_modules/@openai/codex/node_modules/@openai/codex-linux-x64/vendor/x86_64-unknown-linux-musl/codex-resources/bwrap`. `--version`: `bubblewrap built for Codex`. SHA-256: `77360cb751ccedc5971391444ac86a8a33c15b04d6b4a6fe45f5d25496e62c4c`.

Trecho sintetizado do journal do kernel, da reprodução de 13:33:01 UTC:

```text
apparmor="AUDIT" operation="userns_create" profile="unconfined"
  target="unprivileged_userns" pid=2705648 execpath=".../codex-resources/bwrap"
apparmor="DENIED" operation="capable" profile="unprivileged_userns"
  pid=2705649 capability=8 capname="setpcap"
apparmor="DENIED" operation="capable" profile="unprivileged_userns"
  pid=2705649 capability=12 capname="net_admin"
```

O mesmo padrão aparece nas sessões reais de avaliação de 13:22–13:23. `comm="3"` nesses registros não é nome de container; o execpath identifica o helper. Os logs foram consultados com `sudo -n journalctl` e a lista de perfis com `sudo -n cat`, apenas leitura. Não foi usado sudo para executar Codex, Bubblewrap ou testes.

## Comandos executados

Comandos de inspeção e probes, agrupados por propósito; os resultados relevantes estão acima. Nenhum comando de remediação abaixo foi executado.

```bash
uname -a
cat /etc/os-release
systemd-detect-virt
systemd-detect-virt --container
systemd-detect-virt --vm
id
cat /proc/self/status | rg 'Cap|Seccomp|NoNewPrivs|NSpid'
cat /proc/1/cgroup
ls -l /proc/self/ns /proc/1/ns
cat /proc/self/attr/current
cat /proc/sys/kernel/unprivileged_userns_clone /proc/sys/user/max_user_namespaces /proc/sys/user/max_net_namespaces /proc/sys/kernel/apparmor_restrict_unprivileged_userns
cat /sys/module/apparmor/parameters/enabled
command -v bwrap
command -v unshare
command -v ip
command -v apparmor_parser
unshare --user -- sh -c 'readlink /proc/self/ns/user; cat /proc/self/attr/current; cat /proc/self/uid_map'
unshare --user --map-root-user -- sh -c 'id; cat /proc/self/attr/current; cat /proc/self/uid_map'
unshare --user --map-root-user --net -- sh -c 'id; cat /proc/self/status | grep Cap; ip link set lo up'
unshare --user --net -- sh -c 'readlink /proc/self/ns/net; cat /proc/self/attr/current; ip link set lo up'
unshare --net -- /usr/bin/true
codex --version
codex exec --help
codex sandbox --help
codex sandbox linux --help
codex sandbox -- /usr/bin/true
sudo -n journalctl -k --since '30 minutes ago' --no-pager | rg -i 'apparmor|userns|bwrap|denied' | tail -35
sudo -n journalctl -k --since '2 minutes ago' --no-pager | rg 'apparmor=.*(DENIED|AUDIT)' | tail -12
sudo -n journalctl -k --since '2026-11-05 13:33:00' --until '2026-11-05 13:33:02' --no-pager | rg 'apparmor='
sudo -n cat /sys/kernel/security/apparmor/profiles | rg 'unprivileged_userns|bwrap|codex|unshare'
ls /etc/apparmor.d | rg 'bwrap|bubble|unshare|codex'
ls -ld /etc/codex /etc/codex/requirements.toml /etc/codex/managed_config.toml
ls -l /usr/bin/bwrap /usr/bin/bubblewrap
ls -l /usr/share/apparmor/extra-profiles/bwrap-userns-restrict /etc/apparmor.d/bwrap-userns-restrict
dpkg-query -W bubblewrap apparmor apparmor-utils
apt-cache policy bubblewrap apparmor-profiles apparmor-utils
```

Além disso, Python leu apenas as chaves de configuração citadas e calculou SHA-256 do helper; o helper foi invocado com `--version`. Ausências de arquivos e negações nos probes são resultados esperados, não verificações aprovadas. `unshare`/`ip` operaram em processos e namespaces efêmeros, sem alterar a rede do host.

## Correção mínima recomendada — revisão administrativa antes de aplicar

A [documentação oficial do sandbox Codex](https://learn.chatgpt.com/docs/sandboxing#prerequisites) recomenda o bwrap da distribuição e, no Ubuntu 24.04, o perfil extra `bwrap-userns-restrict`. Esta é uma mudança de política específica de executável, ainda que menor que desabilitar a restrição global. O usuário pediu diagnóstico e vedou mudanças automáticas de segurança; portanto o procedimento está documentado para revisão/aplicação administrativa.

1. Verificar origem/assinatura e impacto do pacote; revisar uma simulação de instalação, incluindo possíveis atualizações de AppArmor. Usar os pacotes dos repositórios oficiais, sem adicionar PPA.
2. Instalar Bubblewrap do sistema e obter o perfil distribuído; ler o perfil inteiro e procurar perfis existentes que já se apliquem ao mesmo executável. Não sobrescrever um arquivo existente. Confirmar que o alvo é `/usr/bin/bwrap`, root-owned, sem escrita por usuário/grupo comum. Não adicionar exceção com wildcard para a instalação NVM, que é gravável pelo usuário.
3. Carregar somente o perfil específico após revisão, preservando a restrição global em 1. Não recarregar todos os perfis sem necessidade.

Comandos propostos, **não executados**:

```bash
sudo apt-get --simulate install bubblewrap apparmor-profiles apparmor-utils
# Após revisar a transação:
sudo apt-get install bubblewrap apparmor-profiles apparmor-utils
cat /usr/share/apparmor/extra-profiles/bwrap-userns-restrict
stat -c '%U %G %a %n' /usr/bin/bwrap
# Inspecionar também perfis carregados e evitar perfis sobrepostos.
# Só se o destino estiver ausente e o perfil tiver sido revisado:
sudo install -m 0644 /usr/share/apparmor/extra-profiles/bwrap-userns-restrict /etc/apparmor.d/bwrap-userns-restrict
sudo apparmor_parser -r /etc/apparmor.d/bwrap-userns-restrict
```

Se o arquivo extra estiver ausente após a instalação, parar e conferir a versão/pacote da distribuição; não improvisar um perfil permissivo. O pacote não foi baixado/inspecionado neste diagnóstico, logo o conteúdo final da política ainda requer revisão. Para rollback de um perfil recém-adicionado, o administrador deve descarregá-lo com apparmor_parser e remover apenas o arquivo criado, preservando perfis prévios e a configuração global; não remover pacotes compartilhados indiscriminadamente.

## Validação após a correção

Executar primeiro probes sem modelo, como usuário comum:

```bash
command -v bwrap
bwrap --version
cat /proc/sys/kernel/apparmor_restrict_unprivileged_userns
bwrap --unshare-user --unshare-net --ro-bind / / --proc /proc --dev /dev -- /usr/bin/true
codex -c 'sandbox_mode="read-only"' sandbox -- /usr/bin/true
```

Critérios: dois probes retornam 0, restrição global continua 1 e audit do kernel não mostra a mesma negação para o novo bwrap. Confirmar no audit/proc que o executor passou a usar `/usr/bin/bwrap`; sucesso isolado do bwrap não prova que o Codex o selecionou.

Antes de consumir quota, verificar as duas propriedades do isolamento: um arquivo descartável gravável pelo usuário fora do workspace permanece inalterado após uma tentativa de escrita no sandbox read-only; conexão TCP direta para um listener **local** do host é negada dentro do sandbox, embora funcione fora. Usar arquivos sintéticos e um listener loopback descartável, nunca segredo/arquivo de sistema ou serviço externo. Não considerar uma escrita negada por permissões Unix normais prova de sandbox; a mesma escrita deve ser possível fora. Não abrir a rede para corrigir o loopback: configurar o loopback interno faz parte do isolamento de rede.

Repetir então um cenário real, inspecionar resultado e leituras nativas; só ampliar quando esse probe tiver sucesso:

```bash
python3 scripts/evaluate_engineering_behavior.py --execute --provider codex --case architecture --baseline 9a774be --timeout 180
# Depois, os casos positivos pendentes:
python3 scripts/evaluate_engineering_behavior.py --execute --provider codex --case security --case staged-review --case mcp --baseline 9a774be --timeout 180
```

Não executado neste diagnóstico. Essas chamadas usam quota; exigir novamente evidência de skill/referência lida, fixture preservada e aprovação semântica. Manter resultados antigos como blocked. Os 62 testes anteriores não substituem esta validação do SO.

## Alternativa em ambiente confiável

Se o administrador não puder carregar a política específica neste host, usar uma VM dedicada Linux suportada, com usuário comum, kernel e distribuição atualizados, bwrap empacotado e política da distribuição permitindo sua execução isolada. Evitar container aninhado como primeira alternativa: ele adiciona seccomp/capabilities/namespaces a diagnosticar.

Transferir um snapshot revisado do projeto que inclua os arquivos locais ainda não commitados do avaliador e das skills; clonar somente a main remota não garante esse conteúdo. Verificar hashes de casos, skills e scripts; manter `9a774be` disponível para baseline. Instalar Codex por canal oficial e autenticar diretamente na VM, sem copiar auth.json ou dumps de ambiente. Não disponibilizar credenciais de produção. Fixar/registrar versões, modelo efetivo e configuração, executar os probes de isolamento acima e só então repetir o avaliador. Registrar novo ambiente e run IDs: isto é uma nova avaliação, não continuação idêntica da máquina anterior.

## Riscos e limites

Permitir namespaces ao bwrap aumenta a superfície de ataque do kernel para quem pode invocá-lo, mesmo sem capabilities no host. Preferir binário mantido pela distribuição, root-owned e perfil específico; manter atualizações e revisar política. Não aplicar setuid, setcap, CAP_SYS_ADMIN/NET_ADMIN no host, container privilegiado, sandbox desabilitado ou sysctl global relaxado como correção. Não conceder root ao agente.

A prova presente identifica a negação AppArmor neste host. Não garante que instalar o pacote resolverá toda falha seguinte; a seleção de bwrap e o perfil precisam ser validados. Não houve teste comportamental novo nem alteração das skills nesta etapa. O próximo passo é revisão administrativa do procedimento específico, seguida dos probes sem modelo e do par de arquitetura.
