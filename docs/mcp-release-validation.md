# MCP fix e prontidão para LIA — 2026-11-05

## Diagnóstico

A revisão anterior contou como omissão a ausência de um finding sobre `inputSchema.required`. A evidência nativa confirma que a referência MCP foi carregada: a falha não foi seleção ausente da skill. O texto então dizia apenas para validar inputs, limites e campos desconhecidos; não separava explicitamente presença obrigatória, validade do schema, validade da instância e alinhamento com handler.

Há também um defeito na rubrica antiga: requirements.md não definia quais argumentos eram obrigatórios. Em JSON Schema, properties não implica required; um objeto sem required permite ausência dessas propriedades e pode ser um schema válido. Exigir que todo campo de properties apareça em required gera falsos positivos, especialmente para tenant derivado da autenticação e campos opcionais. A conclusão histórica “MCP atual reprovado” descreve a rubrica então usada, mas não prova isoladamente um erro normativo de JSON Schema ou causalidade do prompt.

Fontes verificadas: [JSON Schema — objetos](https://json-schema.org/understanding-json-schema/reference/object) e [MCP tools](https://modelcontextprotocol.io/specification/2025-06-18/server/tools). inputSchema anuncia o contrato de argumentos; schema e enforcement no servidor são coisas distintas.

## Correção mínima

Somente a referência MCP da skill ai-engineering foi refinada nesta etapa: verificar properties/required/tipos/restrições e relação com contrato e implementação; distinguir propriedade ausente da instância de obrigação não codificada no schema; respeitar defaults/opcionais/composição e política de additionalProperties; demonstrar entradas válidas/inválidas antes de efeitos.

A avaliação agora possui fixture paralela com customer_id/email explicitamente obrigatórios e não vazios, sem reescrever o cenário histórico. Acrescenta seis casos de schema/instância/handler e preserva a referência pré-correção como artefato de A/B. Não altera Harness, agentes ou projeto LIA. O avaliador existente aceita um snapshot completo de skills pré-correção e um arquivo de cenários; versões sem os novos argumentos mantêm defaults anteriores. A leitura de outputs nativos agora decodifica JSON aninhado, corrigindo o falso negativo observado na evidência de carregamento, sem aceitar declarações do assistente como prova.

## Testes reproduzíveis

- examples/behavioral/mcp-schema-fixtures.json: schema válido/entrada válida com campo opcional; required ausente na entrada; argumento obrigatório por contrato não requerido pelo schema; tipo errado; campo adicional proibido; assinatura divergente.
- examples/behavioral/mcp-schema-expectations.json: critérios booleanos de revisão. Todos os schemas são sintaticamente válidos. O schema fraco aceita {}, embora viole o contrato e falhe na chamada ao handler. implementation_compatible mede binding Python dos argumentos da instância, independentemente da validade pelo schema.
- tests/test_mcp_schema_contracts.py usa Draft202012Validator do jsonschema já disponível no sistema. Nada foi instalado. Se o pacote estiver ausente em outro ambiente, esses testes registram skip: não são aprovação de standards nesse ambiente. Eles não implementam um validador JSON Schema próprio nem provam interoperabilidade com servidor MCP real.

Comandos:

```bash
python3 -m unittest discover -s tests -v
python3 scripts/validate_skills.py
# Snapshot baseline reproduzível, fora de diretórios de descoberta:
mkdir -p .local-evidence/mcp-pre-fix
cp -a skills .local-evidence/mcp-pre-fix/
cp examples/behavioral/mcp-reference-before-fix.md .local-evidence/mcp-pre-fix/skills/ai-engineering/references/mcp-engineering.md
PATH=/usr/local/libexec/engineering-os:$PATH python3 scripts/evaluate_engineering_behavior.py --execute --provider all --cases-file examples/behavioral/mcp-release-cases.json --baseline-skills .local-evidence/mcp-pre-fix/skills --timeout 180
```

Baseline desta comparação é a referência imediatamente anterior ao fix, com todas as outras skills iguais; não é 9a774be, que precede toda a integração. Hashes dos arquivos realmente instalados constam nos summaries locais. Os prompts de cada par são idênticos e não fornecem respostas esperadas. Ativação explícita não mede seleção espontânea.

Uma primeira execução exploratória do bundle deixou ambíguo se implementation_compatible significava compatibilidade geral schema/handler ou binding da instância fornecida. Antes da repetição final, definiu-se binding explicitamente e alinhou-se o oráculo à execução real de inspect.signature.bind. Essa mudança é na mensuração, não uma correção para forçar o agente a aceitar um resultado. O primeiro bundle permanece exploratório e não é misturado ao par final. O cenário de contrato explícito daquele run mantém utilidade própria porque seu prompt não foi alterado.

## Escopo da aprovação

LIA não foi aberta, editada ou implantada. Codex CLI 0.166.0 foi usado em sandbox read-only com o helper previamente aprovado, sem sudo nesta etapa. Claude ausente continua not_run. Resultados de contrato/schema não equivalem a execução de um servidor MCP nem validação da integração LIA. Uma execução pareada por cenário não demonstra ganho estatístico ou superioridade geral. O helper root-owned provisionado requer manutenção administrativa e PATH específico; não faz parte da distribuição portátil de skills.

## Resultados finais e comparação

- Run 20261105T144340Z: par MCP com contrato explícito aprovado nas duas versões; par schema exploratório não usado para decisão final devido à ambiguidade de binding já descrita.
- Run 20261105T144604Z: bundle schema com binding definido explicitamente, baseline e corrigida coincidem com todos os valores do oráculo. Detectam missing required na entrada, obrigação ausente do schema, tipo, additionalProperties e mismatch de parâmetro. Não apontam problema no caso válido nem tornam note obrigatório.
- Run 20261105T144716Z: cenário MCP histórico repetido sem alterações de fixture. As duas versões cobrem autorização, readOnlyHint, replay e segredo. A baseline acrescenta incompletude do schema; a corrigida não infere obrigatoriedade não explicitada. Não reprovar essa ausência sob a rubrica corrigida: não há exemplo de instância inválida nem requisito explícito que a sustente nesse cenário.
- A referência corrigida foi confirmada por corpo exato em outputs nativos decodificados nos cenários finais; outputs originais e hashes permanecem preservados. Uma leitura não prova causalidade; respostas e critérios foram examinados separadamente.
- Zero falsos positivos observados no caso válido/opcional do bundle final; isto não é estimativa geral de precisão. Baseline também passou: não há melhoria comportamental comparativa demonstrada.
- Claude indisponível, not_run. Não se simularam execuções.

[Evidências e respostas por caso](../tests/evidence/mcp-release-2026-11-05.json). Streams privados ficam em .local-evidence/behavioral/<run_id>. A comparação pré-fix versus corrigida utiliza os mesmos arquivos e prompt por par; as diferenças entre cenários explícito/histórico não são tratadas como efeito da skill.

## Prontidão de integração

Candidata registrada: **2.0.1-rc.1**, sem publicação/tag/commit automático. O [manifesto do núcleo validado](../tests/evidence/release-core-manifest.json) registra o commit base, hashes exatos de skills, agentes, Harness, scripts, testes e fixtures, e content_id. Ele identifica os arquivos validados ainda locais; não afirma que 9a774be contém a correção. Documentação e relatórios de evidência não integram esse content_id para evitar autorreferência. Para distribuição, transportar o snapshot correspondente ao manifesto, não apenas clonar a main remota.

Validação: 69 testes passaram em 12,201 s, sem skips neste ambiente; inclui seis testes JSON Schema e um novo teste de leitura nativa com JSON aninhado. Validator de sete skills e links passou, git diff --check passou. Testes existentes confirmam três agentes canônicos, mapeamentos, geração dos adaptadores e contratos retrocompatíveis. Nenhuma nova skill ou agente; Harness inalterado nesta etapa. Se jsonschema não estiver disponível no ambiente de destino, os seis testes ficam explicitamente não executados até haver validador aprovado.

**Recomendação: APROVAR esta candidata para integração controlada no projeto LIA pelo caminho Codex validado.** Não há bloqueio remanescente no escopo de revisão MCP aqui testado. A recomendação não declara release publicada, operação de servidor MCP real validada, integração LIA concluída ou paridade runtime com Claude. Antes de promover uma versão estável para distribuição ampla, confirmar os requisitos do ambiente consumidor e repetir seus testes de aceitação. Não foi aberto nem alterado o projeto LIA e não houve deploy.
