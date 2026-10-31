# AD Car Aura — versões e arquivos

Distribuição do **AD Car Aura**, interface para a central multimídia Android do Jeep Renegade.

## Versões distintas

| Produto | Versão | Status | Arquivo |
|---|---:|---|---|
| AD Car Aura (APK Android) | 2.7.0 | Publicada para central | [AD-Car-Aura-2.7.0.apk](AD-Car-Aura-2.7.0.apk) |
| AD Car Aura (prévia web) | 2.8.1 | Interface testável; **não é um APK** | [Abrir código web](web/index.html) |
| AD Car Ponte (Android) | 1.0.0 | Ponte OBD2 separada | [AD-Car-Ponte.apk](AD-Car-Ponte.apk) |
| AD Car legado (APK) | 2.0.0 | Legado | [AD-Car.apk](AD-Car.apk) |

O manifesto [aura-latest.json](aura-latest.json) aponta **somente** para APKs Android completos e assinados. A prévia 2.8.1 **não altera** o OTA 2.7.0.

## Como testar o visual novo

- Arquivo único: [web/index.html](web/index.html), com HTML, CSS e JS embutidos.
- Demonstração: [web/demo.html](web/demo.html); mostra dados simulados identificados como demonstração.
- Instruções, limitações e próximos passos: [web/README.md](web/README.md).

Para abrir como site, hospede `web/index.html` em HTTPS (por exemplo, GitHub Pages após habilitar Pages nas configurações do repositório). O link GitHub de visualização do código **não** executa o aplicativo.

## O que falta para o APK 2.8.1

A versão web não inclui a ponte Java/Kotlin `window.ADNative` nem o serviço nativo Android. Para gerar e publicar um APK instalável é necessário integrar a interface ao projeto Android original, compilar, assinar com a chave de atualização **idêntica** à usada no 2.7.0 e testar mídia, GPS, OBD2, permissão de notificações, áudio e interface na central. Não republicar o manifesto de atualização antes dessas validações.
