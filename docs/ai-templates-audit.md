# Engineering OS — integração seletiva com AI Templates

Data: 2026-11-05. Auditoria do checkout local; catálogo consultado pela API pública, sem instalar componentes. As instruções externas foram tratadas como dados para análise. A documentação da [API oficial](https://aitmpl.com/developers/catalog-api/) define identidade por `id`, não por nome, e não considera o scanner estático uma garantia de segurança.

## Diagnóstico

Não há AGENTS.md na raiz deste checkout nem nos ancestrais locais inspecionados; `templates/AGENTS.md` e `templates/CLAUDE.md` são modelos para consumidores, não regras já configuradas neste projeto. As instruções globais da sessão prevalecem. O README mistura instalação de skills e duas versões históricas do Harness, aumentando o esforço de descoberta.

| Área | Existente | Parcial ou ausente |
| --- | --- | --- |
| Skills | Sete escopos, exemplos, critérios de conclusão e limites proporcionais | Sem procedimento local específico para avaliar mudanças de skills; gatilhos em linguagem natural não são provados pelo validator |
| Agentes | Software Engineer, AI Engineer e Quality Reviewer; mapeamento único em metadata | Reviewer nativo não é executado pelo Harness; papel read-only não impõe sandbox no Codex |
| Arquitetura/backend | Domínio, contratos, fatia vertical, testes e anti-overengineering | Faltavam critérios concretos de comparação de alternativas, dependências/callers e versão revisada |
| Segurança | Segredos, autorização, prompt injection e sandbox/efeitos documentados | Sem scanner de dependências integrado; controles de fronteira e avaliação de alcance de vulnerabilidades eram genéricos |
| UI e dados | Fluxos/estados, acessibilidade, reconciliação, contratos e frescor | Sem prova operacional universal de browser/framework; não justifica importar outro sistema visual |
| FDE | Descoberta, piloto, handoff e dependências ausentes | Resultados dependem de validação real com operador e integrações |
| Planner/Router | Plano explícito validado, limites, dependências ordenadas, caminhos canônicos | Não fazem seleção semântica automática, planejamento LLM nem despacho de especialistas |
| Context | Checkpoints atômicos com hash/backup/lock, últimas cinco decisões e evidência das dependências | Sem orçamento global de contexto; recorte de decisões não prova relevância semântica |
| Recovery | Tentativas persistidas, confirmação única, preservação de passos concluídos, incerteza bloqueia | Processos destacados POSIX/efeitos remotos não são totalmente contidos |
| Evidence/Gates | Evidência estruturada, hashes, Python/Node opt-in, Codex read-only e eventos terminais | Outputs brutos descartados limitam diagnóstico; gate review bloqueia explicitamente |
| Adaptadores/CI | Arquivos nativos distintos, cópia progressiva de skills, três sistemas em CI | Compatibilidade estrutural não equivale a runtime; histórico Claude não executado |
| MCP | Ferramentas/least privilege genéricos em AI | Faltava procedimento para contratos, transporte, autorização, paginação e falhas MCP |

Arquivos inspecionados incluem as sete skills, os três agentes, referências, templates, documentação, módulos do Harness, geradores/smoke runners, exemplos, CI e testes/evidências. Não foi feita auditoria formal de segurança de todas as linhas nem execução dos scripts externos.

## Pesquisa e decisões

Classificação: ADOTAR = usar diretamente; ADAPTAR = incorporar técnica em instruções próprias; REFERENCIAR = manter como fonte condicional, sem incorporar nesta entrega; DESCARTAR = rejeitar o componente para esta integração. Nenhum componente foi adotado integralmente.

A tabela abaixo registra entrypoints reais lidos. Links fixam a revisão do repositório do catálogo; metadados ausentes não foram convertidos em licença presumida do autor original. A licença raiz é MIT (Daniel Ávila, 2025), mas licenças locais prevalecem. A origem histórica além de declarações/links do componente não foi comprovada para todos os itens. Scripts e arquivos auxiliares foram inspecionados seletivamente; nenhuma linha significa auditoria completa do pacote.

Snapshot: schema `1.1.0`, gerado `2026-11-05T03:06:47Z`, 1.940 componentes. SHA-256 do JSON baixado: `739c507329cb2401e9e24dd9f2034c600a54bde9da2d4f3d882da5f0fbfdd442`. Revisão fixada: `3fb3205142fa453d4079ebad48a94d5a4aa19564`. Versões individuais são frequentemente nulas; revisão e hashes identificam o conteúdo, sem inventar versões.

| Componente e origem consultada | Decisão | Técnica, sobreposição, licença e execução |
| --- | --- | --- |
| [agents/development-tools/code-reviewer](https://github.com/davila7/claude-code-templates/blob/3fb3205142fa453d4079ebad48a94d5a4aa19564/cli-tool/components/agents/development-tools/code-reviewer.md) | ADAPTAR | Escopo/versão do diff, callers e cenários de falha complementam o reviewer existente. Skill MIT v2.0.0; agente tem Write/Edit/Bash e pressupõe HEAD~1: não importar permissões nem outro papel. |
| [agents/development-tools/context-manager](https://github.com/davila7/claude-code-templates/blob/3fb3205142fa453d4079ebad48a94d5a4aa19564/cli-tool/components/agents/development-tools/context-manager.md) | DESCARTAR | Duplica Context/Router e cria papel sobreposto. Variante development-tools usa Read/Write/Edit/TodoWrite; expert-advisors propõe infraestrutura distribuída e metas sem medição. Raiz MIT; sem runtime adicional adotado. |
| [agents/expert-advisors/context-manager](https://github.com/davila7/claude-code-templates/blob/3fb3205142fa453d4079ebad48a94d5a4aa19564/cli-tool/components/agents/expert-advisors/context-manager.md) | DESCARTAR | Duplica Context/Router e cria papel sobreposto. Variante development-tools usa Read/Write/Edit/TodoWrite; expert-advisors propõe infraestrutura distribuída e metas sem medição. Raiz MIT; sem runtime adicional adotado. |
| [agents/security/supply-chain-security](https://github.com/davila7/claude-code-templates/blob/3fb3205142fa453d4079ebad48a94d5a4aa19564/cli-tool/components/agents/security/supply-chain-security.md) | ADAPTAR | Manifest/lockfile, scripts, licença e alcance real de advisory. Raiz MIT, origem anterior não comprovada. Scanners/SBOM/registry podem acessar rede; não importar instalação, mudanças de CI ou severidade automática por falta de lockfile. |
| [commands/testing/webapp-testing](https://github.com/davila7/claude-code-templates/blob/3fb3205142fa453d4079ebad48a94d5a4aa19564/cli-tool/components/commands/testing/webapp-testing.md) | ADAPTAR | Reconhecimento antes da ação e asserts de comportamento; não impor networkidle nem sleeps fixos. LICENSE.txt Apache-2.0; depende de Playwright/browser e helper que inicia servidor. Nada disso instalado ou executado. |
| [hooks/security/secret-scanner](https://github.com/davila7/claude-code-templates/blob/3fb3205142fa453d4079ebad48a94d5a4aa19564/cli-tool/components/hooks/security/secret-scanner.json) | DESCARTAR | Config PreToolUse/Bash chama python3 em $CLAUDE_PROJECT_DIR/.claude/hooks/secret-scanner.py; esse JSON sozinho não contém scanner. Hook específico Claude não protege Codex nem substitui CI. Raiz MIT; não habilitado. |
| [skills/creative-design/frontend-design](https://github.com/davila7/claude-code-templates/blob/3fb3205142fa453d4079ebad48a94d5a4aa19564/cli-tool/components/skills/creative-design/frontend-design/SKILL.md) | REFERENCIAR | Direção visual e microcopy se sobrepõem a ui-ux-design/Impeccable. LICENSE.txt Apache-2.0; instruções não exigem pacote, mas implementação pode escrever UI. Não impor preferências estéticas universais. |
| [skills/development/clean-code](https://github.com/davila7/claude-code-templates/blob/3fb3205142fa453d4079ebad48a94d5a4aa19564/cli-tool/components/skills/development/clean-code/SKILL.md) | DESCARTAR | Já coberto por convenções e simplicidade; limites universais de 20 linhas/3 argumentos e prioridade CRITICAL causam conflito e refatoração sem evidência. allowed-tools Read/Write/Edit; raiz MIT, origem anterior não comprovada. |
| [skills/development/code-reviewer](https://github.com/davila7/claude-code-templates/blob/3fb3205142fa453d4079ebad48a94d5a4aa19564/cli-tool/components/skills/development/code-reviewer/SKILL.md) | ADAPTAR | Escopo/versão do diff, callers e cenários de falha complementam o reviewer existente. Skill MIT v2.0.0; agente tem Write/Edit/Bash e pressupõe HEAD~1: não importar permissões nem outro papel. |
| [skills/development/context-architecture](https://github.com/davila7/claude-code-templates/blob/3fb3205142fa453d4079ebad48a94d5a4aa19564/cli-tool/components/skills/development/context-architecture/SKILL.md) | REFERENCIAR | Referências verificáveis e contexto próximo ao código são úteis; CC-BY-4.0 no metadata. Não incorporar metodologia de nove princípios, reorganização nem proteção universal de toda verificação. Reusar mecanismo local de links. |
| [skills/development/mcp-builder](https://github.com/davila7/claude-code-templates/blob/3fb3205142fa453d4079ebad48a94d5a4aa19564/cli-tool/components/skills/development/mcp-builder/SKILL.md) | ADAPTAR | Schemas, descrições, paginação, erros e testes de ferramentas. LICENSE.txt Apache-2.0; evaluator requer anthropic>=0.39.0 e mcp>=1.1.0. Não importar avaliador, preferência de linguagem nem cobertura total de APIs. |
| [skills/development/react-best-practices](https://github.com/davila7/claude-code-templates/blob/3fb3205142fa453d4079ebad48a94d5a4aa19564/cli-tool/components/skills/development/react-best-practices/SKILL.md) | REFERENCIAR | Waterfalls/bundle antes de micro-otimizações são úteis quando React/Next está no escopo. Variante web-development declara MIT, development não declara licença local; origem declarada Vercel. Regras dependem das versões; download_rules.sh na variante web não foi executado. |
| [skills/development/senior-architect](https://github.com/davila7/claude-code-templates/blob/3fb3205142fa453d4079ebad48a94d5a4aa19564/cli-tool/components/skills/development/senior-architect/SKILL.md) | DESCARTAR | dependency_analyzer.py apenas valida o caminho e retorna success/findings vazio; tech_decision_guide contém Scenario 1/Benefit 1. Instalações, fixes e deploy sugeridos não justificam automação. Sem licença local declarada; raiz MIT, origem anterior não comprovada. |
| [skills/development/senior-backend](https://github.com/davila7/claude-code-templates/blob/3fb3205142fa453d4079ebad48a94d5a4aa19564/cli-tool/components/skills/development/senior-backend/SKILL.md) | DESCARTAR | api_load_tester.py não gera carga: analyze retorna success/findings vazio. Duplica software-engineering e sugere instalação/migração/deploy. Raiz MIT; origem anterior não comprovada. |
| [skills/development/skill-creator](https://github.com/davila7/claude-code-templates/blob/3fb3205142fa453d4079ebad48a94d5a4aa19564/cli-tool/components/skills/development/skill-creator/SKILL.md) | ADAPTAR | Avaliações com/sem skill e gatilhos positivos/negativos; reaproveitar validator e smoke runner. LICENSE.txt Apache-2.0; scripts/loops podem chamar provider e criar arquivos: não importar. |
| [skills/development/systematic-debugging](https://github.com/davila7/claude-code-templates/blob/3fb3205142fa453d4079ebad48a94d5a4aa19564/cli-tool/components/skills/development/systematic-debugging/SKILL.md) | REFERENCIAR | Causa antes de correção já existe; tracing e espera por condição são úteis em bugs difíceis. MIT Jesse Vincent, 2025; find-polluter.sh executa testes, requer revisão antes de uso. |
| [skills/development/webapp-testing](https://github.com/davila7/claude-code-templates/blob/3fb3205142fa453d4079ebad48a94d5a4aa19564/cli-tool/components/skills/development/webapp-testing/SKILL.md) | ADAPTAR | Reconhecimento antes da ação e asserts de comportamento; não impor networkidle nem sleeps fixos. LICENSE.txt Apache-2.0; depende de Playwright/browser e helper que inicia servidor. Nada disso instalado ou executado. |
| [skills/productivity/skill-creator](https://github.com/davila7/claude-code-templates/blob/3fb3205142fa453d4079ebad48a94d5a4aa19564/cli-tool/components/skills/productivity/skill-creator/SKILL.md) | ADAPTAR | Avaliações com/sem skill e gatilhos positivos/negativos; reaproveitar validator e smoke runner. LICENSE.txt Apache-2.0; scripts/loops podem chamar provider e criar arquivos: não importar. |
| [skills/security/security-threat-model](https://github.com/davila7/claude-code-templates/blob/3fb3205142fa453d4079ebad48a94d5a4aa19564/cli-tool/components/skills/security/security-threat-model/SKILL.md) | ADAPTAR | Ativos, fronteiras e caminhos de abuso concretos para alterações de risco. Autor declarado OpenAI, LICENSE.txt Apache-2.0. Não importar pausa obrigatória nem novo papel; nenhum teste ofensivo automático. |
| [skills/security/webapp-testing](https://github.com/davila7/claude-code-templates/blob/3fb3205142fa453d4079ebad48a94d5a4aa19564/cli-tool/components/skills/security/webapp-testing/SKILL.md) | ADAPTAR | Reconhecimento antes da ação e asserts de comportamento; não impor networkidle nem sleeps fixos. LICENSE.txt Apache-2.0; depende de Playwright/browser e helper que inicia servidor. Nada disso instalado ou executado. |
| [skills/web-development/react-best-practices](https://github.com/davila7/claude-code-templates/blob/3fb3205142fa453d4079ebad48a94d5a4aa19564/cli-tool/components/skills/web-development/react-best-practices/SKILL.md) | REFERENCIAR | Waterfalls/bundle antes de micro-otimizações são úteis quando React/Next está no escopo. Variante web-development declara MIT, development não declara licença local; origem declarada Vercel. Regras dependem das versões; download_rules.sh na variante web não foi executado. |

## Identidade do conteúdo lido

Hashes dos entrypoints na revisão fixada (arquivos auxiliares não estão incluídos nesses hashes):

| ID | SHA-256 |
| --- | --- |
| `agents/development-tools/code-reviewer` | `970643dc8c5ecd3810654ad7cc2dce012420f54eef81ecefe72236f9403f5635` |
| `agents/development-tools/context-manager` | `70fbed3038bf854a595f47418b071b1938113c16e1f074c60f0ba465ee97731e` |
| `agents/expert-advisors/context-manager` | `b7969af78d1ef8de43d77e9b06fa16305444ff831aa6d073095886ff6b0ccdfc` |
| `agents/security/supply-chain-security` | `17afd45100b484d3927ea802ade918a0761e9e455365a8cd4cce7e1995646f3a` |
| `commands/testing/webapp-testing` | `971681dbc987fd4fcd5fd4273229e47ba95ac90cf56bb35090cd890b728cfc33` |
| `hooks/security/secret-scanner` | `cd6bc2baaa848648b576057938d44f997142a9096f340a9c4cfbc54b4afd78df` |
| `skills/creative-design/frontend-design` | `d91970639e9f5c37682ac7ab60094d35f1c7c1f38d731bd56396563aee10c1d3` |
| `skills/development/clean-code` | `82a711dfc1ef0502033308ca87540d4be8c6269b55d3577464538e752281eb76` |
| `skills/development/code-reviewer` | `373eb45232241fc46fd63ef5cd37563b68d43618cea9260d831058f35e4f007c` |
| `skills/development/context-architecture` | `9fb7ead8856e6d1f7bd950ef6295d0cb4bb35a7ff934673070a050b21f1031f1` |
| `skills/development/mcp-builder` | `0f4592dcb53cf2b5d6b7febee6b4152018b565551a1c29e3c612f57b218ab295` |
| `skills/development/react-best-practices` | `57ea0c22c82e275c9aede5bac28023020768db34461517aef6e265193e187fb3` |
| `skills/development/senior-architect` | `59c6829066912ad8db5a8ca0a95407a86c990a5638e348fb2c0a31d9dc118268` |
| `skills/development/senior-backend` | `de1c35674ab09c38b0895ab29eddfaf501ceff19ecf4db39617d7fb1cbf8762d` |
| `skills/development/skill-creator` | `dcd4803e61e913e6fc27294184cd3a71f09f5e924ff20c8a9a20173e7b3c2bcf` |
| `skills/development/systematic-debugging` | `98c593a96258d15ffcee71edb0f4743f9e90449c6412c46742b1ffc580db43c4` |
| `skills/development/webapp-testing` | `51b7349e77ec63b7744a6f63647e7566a0b4d2e301121cc10e8c2113af6556a2` |
| `skills/productivity/skill-creator` | `dcd4803e61e913e6fc27294184cd3a71f09f5e924ff20c8a9a20173e7b3c2bcf` |
| `skills/security/security-threat-model` | `7b884137b3df35f78064bcadfa404f785f6d7f97e290b13a4f74e6bd91e8196d` |
| `skills/security/webapp-testing` | `51b7349e77ec63b7744a6f63647e7566a0b4d2e301121cc10e8c2113af6556a2` |
| `skills/web-development/react-best-practices` | `d50e89e51236da293114e4b4d58621713cad8fb1f4757ea87b39b75cc6bc7bd6` |

## Até três melhorias implementadas

1. **Revisão de arquitetura, regressão e segurança:** referência condicional em software-engineering, acessível também por git-quality. Critérios de decisão, leitura da versão certa, consumers, testes negativos, fronteiras e dependências. Nenhum novo agente ou scanner. Benefício verificável nesta entrega: referência portável em ambos os adaptadores; benefício sobre defeitos reais ainda precisa de avaliação operacional.
2. **Contratos MCP:** referência condicional em ai-engineering com schemas, autorização por recurso/tenant, erros, paginação, replay e testes sintéticos. Não implementa servidor nem executor. SDK/protocolo devem ser verificados na versão de cada projeto.
3. **Skill engineering e contexto progressivo:** validator existente passa a rejeitar referências Markdown locais das skills que escapam do pacote ou apontam para diretórios; testes verificam cópia integral e resolução em ambos os layouts. Procedimento de avaliação reaproveita smoke runner existente. Não foi criado registry: diretórios canônicos + metadata de agentes + SOURCES + esta auditoria já resolvem descoberta e proveniência. Este relatório é um snapshot de pesquisa, sem semântica de instalação/execução.

Código e procedimentos foram escritos independentemente a partir das técnicas analisadas; não foram copiados scripts, templates ou blocos de instrução dos componentes. Referências externas não concedem permissões. Nenhuma instalação, hook, nova dependência, alteração de checkpoint ou comando externo do Harness foi introduzido. A validação é estática/determinística e não constitui enforcement de instruções ou avaliação semântica do modelo.

## Validação e limites

- `python3 -m unittest discover -s tests -q`: 56 testes passaram em 11,345 s na primeira execução após implementação (53 existentes + 3 novos).
- `python3 scripts/validate_skills.py`: sete skills e links locais válidos; repetido após finalizar documentação.
- Novos testes: referências ausentes/escape/diretório rejeitadas; cópia byte a byte e links resolvidos em Claude/Codex; composição de rotas explícitas MCP/review e rejeição de skill inexistente.
- Testes existentes preservam os contratos de Planner, Context, Recovery, gates, executor, três agentes e sete skills. Não testam automaticamente ausência de toda contradição semântica; a revisão manual verificou autorização, papel read-only, escopo, referências e progressividade.
- Execução local Linux/Python 3.12. Nenhuma chamada paga de provider, teste com conta real, browser ou scanner externo. Claude/Codex runtime após estas alterações e CI Windows/macOS não foram executados. Evidência histórica tem versões/escopos próprios e não foi reclassificada como nova evidência.
- Os cenários de linguagem natural em `skill-evaluation.md` são especificação de avaliação futura. Rotas explícitas e arquivos corretos não provam seleção automática correta. Não há nota 9/10 ou ganho de produtividade medido nesta entrega.

## Próximas evoluções

Executar avaliação pareada autorizada com o smoke runner para staged review, seleção MCP e casos negativos; medir resultados e custo sem atribuir causalidade a uma amostra pequena. Em projeto consumidor, testar um servidor MCP mínimo com fake service e dois clientes reais antes de alegar interoperabilidade. Avaliar scanners já disponíveis no CI do consumidor; propor integração separada se necessária. Separar histórico do Harness do início rápido do README quando houver evidência de dificuldade de onboarding. Qualquer novo executor ou hook requer plano e análise próprios.

Final verification: 56 tests passed again in 10,246 s on Python 3.12.3 / Node v24.21.0; skill/link validator and `git diff --check` exited 0. Root/ancestor AGENTS paths were checked explicitly.

Files changed: `skills/software-engineering/SKILL.md`, `skills/git-quality/SKILL.md`, `skills/ai-engineering/SKILL.md`, the two new conditional references, `scripts/validate_skills.py`, `tests/test_skill_references.py`, `docs/skill-evaluation.md`, this audit, `README.md`, `SOURCES.md` and `CHANGELOG.md`. Harness, canonical agent definitions and adapter generator remain unchanged.
