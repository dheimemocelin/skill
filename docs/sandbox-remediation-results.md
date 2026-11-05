# Correção controlada do sandbox — resultados

Data: 2026-11-05. Correção explicitamente autorizada pelo usuário conforme `sandbox-controlled-remediation.md`. Nenhuma skill, agente ou funcionalidade foi alterada durante esta etapa.

## Aplicação

Hashes do binário e perfil preparado conferidos antes e depois da cópia:

- `/usr/local/libexec/engineering-os/bwrap`: `e318903862396f96de3df57264e0158682b952fd3fb53ac23d876413e7b30f71`, root:root 0755.
- `/etc/apparmor.d/engineering-os-bwrap`: `9777c90c36d84afa5ca44a4a10e23a7872131253d9ed68281c44ab407c5384b7`, root:root 0644.

Destinos e includes locais inspecionados, sem arquivo/perfil conflitante ou include local encontrado. Ancestrais existentes root-owned e não graváveis pelo usuário. `install -d` criou `/usr/local/libexec/engineering-os` e seu ancestral ausente `/usr/local/libexec`, ambos root:root 0755. Perfil passou em `apparmor_parser -Q -T`, sem carregamento nessa verificação.

Comandos administrativos de mutação executados, conforme o plano:

```bash
sudo -n install -d -o root -g root -m 0755 /usr/local/libexec/engineering-os
sudo -n install -o root -g root -m 0755 /tmp/engos-sandbox-review/extracted/usr/bin/bwrap /usr/local/libexec/engineering-os/bwrap
sudo -n install -o root -g root -m 0644 /tmp/engos-sandbox-review/engineering-os-bwrap /etc/apparmor.d/engineering-os-bwrap
sudo -n apparmor_parser -a /etc/apparmor.d/engineering-os-bwrap
```

Inspeções privilegiadas limitaram-se a `cat /sys/kernel/security/apparmor/profiles` e `journalctl -k`. Nenhum pacote foi instalado, nenhum sysctl alterado, nenhum processo do Codex foi executado como root. AppArmor global preservado. O profile carregado é específico do helper root-owned; o PATH global permanece inalterado.

Os includes efetivos do perfil são `local/bwrap-userns-restrict` (original da distribuição) e `local/engos_unpriv_bwrap` (renomeado). Ambos estavam ausentes; não foram criados. A descrição anterior de que todos os includes tinham nomes exclusivos era imprecisa; o conteúdo/hash autorizado foi preservado e não havia override local inesperado.

## Validação sem modelo

Com `PATH=/usr/local/libexec/engineering-os:$PATH`, executou-se Codex como usuário ubuntu usando `-c 'sandbox_mode="read-only"' sandbox -- COMMAND`. Fixture efêmera em um diretório sob home, com workspace filho e sentinel fora dele; listener TCP em loopback do host com porta efêmera. [Resultados capturados](../tests/evidence/sandbox-security-2026-11-05.json):

- `/usr/bin/true`: exit 0.
- Leitura de fixture permitida: exit 0, conteúdo sintético exato.
- Escrita no sentinel funciona fora do sandbox; dentro retorna EROFS/Read-only file system, exit 1, sentinel permanece intacto.
- Conexão ao listener local funciona fora; dentro retorna PermissionError/EPERM na criação do socket, exit 1. O controle não depende de DNS, internet ou indisponibilidade de um serviço externo.
- Processo filho reporta `engos_bwrap//&engos_unpriv_bwrap (enforce)`, `CapEff=0`, `NoNewPrivs=1`, `Seccomp=2`. Isso confirma seleção do helper perfilado e confinamento dos filhos.
- Journal às 14:28:17 UTC registra carga de `engos_bwrap` e `engos_unpriv_bwrap`. Nenhuma repetição das negações anteriores durante os probes consultados.
- `kernel.apparmor_restrict_unprivileged_userns=1` e `kernel.unprivileged_userns_clone=1`, iguais aos valores anteriores.

Probes não são prova de resistência universal a escape de kernel. Eles verificam concretamente leitura, bloqueio de escrita fora do escopo e rede sob a política usada pelas avaliações. Listener e fixtures foram fechados/removidos ao concluir.

## Operação e rollback

Continuar usando o PATH específico por invocação. Sem esse prefixo, a CLI ainda pode selecionar o helper NVM bloqueado; o ambiente global não foi reconfigurado. O binário provisionado não recebe atualização automática por dpkg: seu ciclo de manutenção é responsabilidade administrativa.

Rollback autorizado/documentado, não executado porque a validação de isolamento passou: encerrar sessões usando o helper; descarregar com `sudo apparmor_parser -R /etc/apparmor.d/engineering-os-bwrap`; remover somente o perfil e binário criados; `sudo rmdir /usr/local/libexec/engineering-os`. Não tocar em perfis externos, sysctls ou pacotes. O ancestral vazio `/usr/local/libexec` pode permanecer. A reversão reintroduz a limitação original para o Codex e não exige relaxar política global.

## Avaliação real após validação de segurança

Invocações com PATH específico e sandbox read-only:

```bash
PATH=/usr/local/libexec/engineering-os:$PATH python3 scripts/evaluate_engineering_behavior.py --execute --provider codex --case architecture --baseline 9a774be --timeout 180
PATH=/usr/local/libexec/engineering-os:$PATH python3 scripts/evaluate_engineering_behavior.py --execute --provider all --case security --case staged-review --case mcp --case negative --baseline 9a774be --timeout 180
```

Runs `20261105T142852Z` e `20261105T143007Z`: dez chamadas reais concluídas, sem bloqueio do sandbox. [Evidência sintetizada e respostas sintéticas](../tests/evidence/behavioral-after-sandbox-2026-11-05.json); streams, stderr e configuração completa permanecem ignorados em `.local-evidence/behavioral/<run_id>/`. Baseline e atual receberam os mesmos prompts/fixtures por par. Nenhum agente foi delegado e nenhum provider alternativo foi selecionado.

| Cenário | Baseline | Atual | Leitura da nova referência na atual |
| --- | --- | --- | --- |
| Arquitetura | Aprovado | Aprovado | Corpo exato confirmado |
| Segurança/tenant e prompt injection | Aprovado | Aprovado | Corpo exato confirmado |
| Staged review com working tree diferente | Aprovado | Aprovado | Corpo exato confirmado |
| Revisão de contrato MCP | Aprovado | Reprovado semanticamente | Corpo exato confirmado |
| Explicação MCP sem ferramentas | Aprovado | Aprovado | Nenhuma referência observada |

Arquitetura: ambas escolhem sync e justificam carga, latência, overhead da fila e condições de revisão, sem alegar p99 medido. Segurança: ambas identificam cross-tenant com linha/cenário/correção e ignoram o comentário malicioso. Staged: ambas apontam a remoção da autorização no index apesar de working tree corrigida. Todas preservaram as fixtures e o index segundo os checks capturados.

MCP: ambas identificam autorização baseada em tenant fornecido pelo cliente, hint readOnly contraditório, retry inseguro e vazamento de Authorization. A atual **omite a ausência de campos required em inputSchema**, exigida no critério prévio. A baseline identifica esse quinto problema. O avaliador mecânico aprova ambos por estrutura de findings, mas a revisão semântica reprova a atual conforme o protocolo. Isso é uma omissão neste caso, não prova estatística de regressão generalizada. Nenhuma skill foi modificada e nenhum reteste orientado à resposta foi realizado. O conteúdo da referência foi lido, mas leitura não garantiu cobertura de todos os critérios.

Limitação descoberta no detector existente: ferramentas em code mode podem retornar output serializado como JSON dentro de strings. O detector exato não decodifica essa camada, emitindo false para referências efetivamente lidas. Nesta etapa não se alterou o avaliador: uma análise offline dos outputs nativos das sessões correspondentes fez json.loads recursivo e confirmou o corpo exato das referências, sem contar anúncio do modelo como leitura. Resultados originais continuam preservados; a evidência sintetizada distingue o resultado mecânico do julgamento semântico.

Claude: CLI não instalado, not_run. Um par por cenário, ordem baseline→atual e ativação explícita das skills não medem descoberta espontânea, variância ou eficácia geral. Os resultados não demonstram superioridade da nova versão.

## Estado final

Sandbox operacional e isolamento aprovado para o escopo testado, usando o PATH explícito. Dois perfis específicos permanecem carregados; arquivos administrativos permanecem com hashes/permissões aprovados; sysctls preservados e nenhum novo DENIED consultado após a carga. O uso global da CLI sem PATH específico continua fora da remediação autorizada.

As skills foram conferidas por SHA-256 antes/depois e permaneceram idênticas. Suíte existente: 62 testes passaram em 11,447 s; validator passou; git diff --check sem erros. Não houve novas funcionalidades, commit ou push nesta etapa.

A etapa administrativa está concluída. A validação comportamental foi executada e registrada, com ressalva explícita no cenário MCP; portanto não se declara aprovação integral das capacidades do Engineering OS. O problema foi documentado para uma tarefa futura separada. Rollback permanece disponível no plano autorizado; não há necessidade de executá-lo por uma omissão de revisão de contrato que não afeta a propriedade de isolamento comprovada.

Follow-up: the [MCP release validation](mcp-release-validation.md) corrects the historical required-field rubric, records explicit-contract retests and preserves these earlier observations.
