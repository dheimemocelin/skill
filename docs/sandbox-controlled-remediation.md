# Correção controlada — aguardando aprovação

Verificação 2026-11-05: Codex 0.166.0, bwrap do sistema ausente, helper embutido no caminho registrado no diagnóstico anterior. Reprodução sem modelo voltou a falhar. Journal legível nesta sessão confirmou negações AppArmor setpcap/net_admin às 14:20:02 UTC. Lista de perfis carregados requer sudo e não foi lida nesta etapa. Restrição global permanece 1. Nenhum sudo foi executado.

Documentação: https://learn.chatgpt.com/docs/sandboxing#prerequisites. O perfil da distribuição se aplica a /usr/bin/bwrap, não ao helper NVM. Pacotes foram somente baixados por apt-get download e extraídos em /tmp/engos-sandbox-review; nada instalado.

Descoberta que altera o plano anterior: bubblewrap 0.9.0-1ubuntu0.3 inclui /usr/lib/sysctl.d/50-bubblewrap.conf e postinst executa sysctl --system para kernel.unprivileged_userns_clone. Como o usuário proibiu alteração global de sysctl, não se propõe essa instalação. Instalar apparmor-profiles também atualizaria apparmor/libapparmor1 e instalaria outros perfis. Não é necessário.

Alternativa mínima proposta: provisionar somente o bwrap extraído do pacote oficial em caminho root-owned exclusivo, com perfil específico derivado do perfil distribuído. Isso não é instalação gerenciada pelo dpkg: atualização de segurança/removal ficam sob responsabilidade administrativa. Usar somente com PATH explícito nos testes, sem alterar PATH global. Binário e perfil precisam ser revalidados por hash antes da cópia; /tmp não é fronteira de confiança. Não executar binário com sudo.

Preparado: /tmp/engos-sandbox-review/engineering-os-bwrap. Únicas adaptações de política: attachment /usr/local/libexec/engineering-os/bwrap e nomes engos_bwrap/engos_unpriv_bwrap para evitar colisão com perfil da distribuição. Includes locais também recebem nome exclusivo. O perfil original permite capacidades ao launcher e nega capacidades nos filhos por stacking; ele não substitui mounts/namespace/seccomp do Codex. apparmor_parser -Q -T validou o perfil sem carregá-lo.

Hashes aprováveis:
- binário: e318903862396f96de3df57264e0158682b952fd3fb53ac23d876413e7b30f71
- perfil: 9777c90c36d84afa5ca44a4a10e23a7872131253d9ed68281c44ab407c5384b7

## Comandos propostos após aprovação explícita

Primeiro inspeção administrativa read-only; parar se houver colisão de perfil ou caminho, symlink, include local inesperado ou hash divergente:

```bash
sudo -n cat /sys/kernel/security/apparmor/profiles
sudo -n journalctl -k --since '15 minutes ago' --no-pager
```

Após confirmar ausência de arquivos/perfis homônimos, verificar hashes e criar apenas estes artefatos:

```bash
sudo install -d -o root -g root -m 0755 /usr/local/libexec/engineering-os
sudo install -o root -g root -m 0755 /tmp/engos-sandbox-review/extracted/usr/bin/bwrap /usr/local/libexec/engineering-os/bwrap
sudo install -o root -g root -m 0644 /tmp/engos-sandbox-review/engineering-os-bwrap /etc/apparmor.d/engineering-os-bwrap
sudo apparmor_parser -a /etc/apparmor.d/engineering-os-bwrap
```

Não sobrescrever arquivo existente; verificar ownership/permissões dos ancestrais. Não instalar pacote ou alterar sysctl. Testes como ubuntu, prefixando PATH=/usr/local/libexec/engineering-os:$PATH somente na chamada: codex sandbox true; leitura de fixture; tentativa de escrita em sentinel fora do escopo com controle positivo fora do sandbox; conexão a listener loopback do host com controle positivo e timeout; journal AppArmor. A sintaxe/config efetiva read-only será conferida no CLI. Falha em qualquer propriedade interrompe avaliação comportamental.

Depois executar arquitetura baseline/current, revisar evidências e só então security/staged-review/MCP. Skills permanecem intactas. Não há resultado de segurança pós-correção ou comportamental novo nesta etapa.

## Reversão

Somente para artefatos criados por esta operação, sem sessões usando o helper:

```bash
sudo apparmor_parser -R /etc/apparmor.d/engineering-os-bwrap
sudo rm /etc/apparmor.d/engineering-os-bwrap
sudo rm /usr/local/libexec/engineering-os/bwrap
sudo rmdir /usr/local/libexec/engineering-os
```

Não remover diretório não vazio. Se carregamento falhar, verificar quais perfis foram carregados antes de remover. Não descarregar perfis existentes. Encerrar uso do PATH específico. Nenhuma configuração global sysctl ou AppArmor principal necessita reversão.

Riscos: acesso ao kernel por namespaces do launcher, política distribuída ampla antes do stacking, ausência de atualização automática do binário provisionado, mudanças na seleção de helper pelo Codex e possível comportamento diferente entre versões. Exigir testes negativos e logs; não presumir isolamento por simples exit zero.
