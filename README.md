# AD Car Aura — distribuição oficial

Este repositório distribui o **AD Car Aura** para central multimídia Android, incluindo histórico de versões e manifesto de atualização OTA.

## Versões

| Produto | Versão | Distribuição |
|---|---|---|
| **AD Car Aura Android (atual)** | **2.8.0 (versionCode 16)** | [Baixar APK 2.8.0](AD-Car-Aura-2.8.0.apk) |
| AD Car Aura Android (anterior) | 2.7.0 (versionCode 15) | [Baixar APK 2.7.0](AD-Car-Aura-2.7.0.apk) |
| AD Car Ponte | 1.0.0 | [Baixar APK Ponte](AD-Car-Ponte.apk) |
| Prévia da interface web (sem serviços nativos) | 2.8.1 | [web/index.html](web/index.html) |

**Atualizador do Aura:** [aura-latest.json](aura-latest.json) → APK **2.8.0**. O manifesto mantém pacote `br.com.adcomintegrada.adcar.aura` e fornece versão, checksum SHA-256 e tamanho do instalador.

## Verificações de release

- O APK 2.8.0 foi analisado em 31/10/2026, e contém `minSdkVersion=26` (Android 8.0) e `targetSdkVersion=32`.
- O identificador do aplicativo é o mesmo do 2.7.0 e a assinatura digital X.509 é **idêntica** à do APK 2.7.0, confirmada no GitHub Actions.
- O manifesto foi publicado com SHA-256 e tamanho exatos do arquivo, e a validação automática do repositório confere ambos.
- **Não foram realizados testes físicos na central.** GPS, media sessions/arte, OBD2, Ponte, permissões, rádio FM, mapas locais, instalação pelo atualizador e UI de sistema precisam de teste em veículo parado.
- O APK foi compilado externamente e enviado pronto. Nenhuma alteração foi aplicada ao binário assinado.

### Instalação

Com internet na central: abra AD Car Aura → Ajustes → Atualizações → Verificar → Instalar, caso a versão instalada disponibilize esse fluxo. Alternativamente, baixe o [APK 2.8.0](AD-Car-Aura-2.8.0.apk) e instale-o no Android, mantendo o app anterior para preservar dados, e confirme as permissões necessárias.

Se aparecer erro de instalação, **não desinstale a versão atual imediatamente**: obtenha os detalhes e verifique se o app instalado tem o pacote e assinatura esperados. A assinatura idêntica verificada vale para os APKs 2.7.0 e 2.8.0 no repositório.

### Web de demonstração

O diretório `web/` contém uma prévia experimental 2.8.1, diferente do APK Android 2.8.0. Ela não substitui o APK e não fornece ponte Android `ADNative` quando acessada em navegador convencional.

## Candidato 2.8.1 (teste manual; OTA ainda 2.8.0)

- [Baixar AD-Car-Aura-2.8.1-RC.apk](AD-Car-Aura-2.8.1-RC.apk) — **APK assinado, mas ainda não validado na central KOWAN**.
- [Ficha de integridade e limitações](aura-rc-2.8.1.json).
- [Código-fonte da integração](https://github.com/andredeveza/Renegade-Cockpit/tree/aura-2.8.1-integracoes).
- Telefone: discador por ação Android; áudio das ligações depende HFP/OEM. Microfone: teste de nível sem armazenar áudio; voz depende de reconhecedor no sistema. Waze: iframe de visualização de trânsito (sem navegação integrada).
- **Não atualizar** `aura-latest.json` para 2.8.1 até o usuário confirmar Ponte, GPS, mídia, telefone, microfone e mapa na central; versão estável fica 2.8.0.
