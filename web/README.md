# AD Car Aura 2.8.1 — prévia web

Este diretório contém uma **versão web autocontida** da interface Aura In-Cabin OS.

- [index.html](index.html): HTML executável com CSS/JavaScript incorporados.
- [demo.html](demo.html): demonstração com dados fictícios identificados na tela.

## O que funciona sem APK

Painel, abas, configurações, temas, layouts, escala, controles visuais, mapa com tiles OpenStreetMap, busca e rotas online (dependendo de conexão e serviços externos), GPS via permissão do navegador em origem segura e clima por serviço externo.

**Não são funções nativas reais nesta prévia:** OBD2 Bluetooth ou via Ponte, controle das sessões de mídia/Spotify e capas obtidas do Android, volume de sistema, rádio FM nativo, abertura de apps instalados e atualização/instalação de APK. Sem `window.ADNative`, a interface exibe recursos indisponíveis; dados de demonstração não são do carro.

## Publicação

O HTML não depende de instalação de pacotes. Para testes locais, baixe o arquivo e abra no Chrome/Android. Geolocalização normalmente exige HTTPS. Para uma URL pública, habilite GitHub Pages ou outro hosting estático HTTPS e disponibilize `web/index.html`. O projeto **não ativa automaticamente GitHub Pages**, que pode precisar de configuração do proprietário.

## Compatibilidade

JavaScript ES5 na UI para WebView Android 8.1; targets amplos para toque e ajustes para centrais 800×480, 1024×600 e 1280×720. Mapa base é online e depende da disponibilidade do OpenStreetMap. Não substitui o painel original do veículo. Não configure enquanto dirige.

## APK futuro

Para atualizar a central instalada com 2.7.0, só depois de obter o projeto Android completo, integrar a interface web à ponte `ADNative`, compilar e assinar com a **mesma chave da versão anterior**. Atualize `aura-latest.json` apenas com o APK verificado, versão, checksum e tamanho corretos.
