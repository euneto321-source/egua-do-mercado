# Égua do Mercado — catálogo digital

Catálogo dos produtos e preços do minimercado autônomo 24h. Só consulta, sem pedido nem pagamento.

- **Site:** https://euneto321-source.github.io/egua-do-mercado/
- **Cartaz com QR Code:** https://euneto321-source.github.io/egua-do-mercado/qr.html

## Como atualizar preços e produtos

Tudo é feito na planilha Google (aba **Catalogo**). O site lê a planilha e atualiza nos celulares em até ~10 minutos.

| Coluna | O que colocar |
|---|---|
| `sku` | Código único, sem espaço (ex.: `coca-cola-lata-220`). Não mude depois de criado. |
| `nome` | Nome que aparece no card. |
| `marca` | Marca. |
| `apresentacao` | Peso, volume ou quantidade (ex.: `Lata 350 ml`, `35 g`). |
| `categoria` | Uma destas: Bebidas · Energéticos · Snacks · Biscoitos & Cereais · Chocolates & Doces · Instantâneos · Refrigerados & Congelados · Mercearia. Uma categoria nova também funciona, com ícone genérico. |
| `preco` | Preço de venda, ex.: `4,00`. |
| `preco_promo` | Preço da oferta. Vazio = sem oferta. Só vale se for menor que `preco`. |
| `promo_ate` | Último dia da oferta (`31/10/2026`). Vazio = até tirar. |
| `foto` | `img/<sku>.jpg` para fotos do site, ou um link `https://` de imagem. |
| `mais_procurado` | `S` para aparecer em "Mais procurados". |
| `novidade_desde` | Data de chegada (`20/10/2026`). Fica em "Chegou agora" por 14 dias. |
| `ativo` | `N` esconde o produto (acabou, saiu de linha). |
| `ordem` | Número para ordenar dentro da categoria. |

**Nunca** coloque custo ou margem nesta aba: ela é publicada na internet.

## Estrutura

- `src/app.html` — a interface inteira (CSS + JS). Editar aqui e rodar `python3 tools/montar_index.py`.
- `index.html` — gerado a partir de `src/app.html`.
- `js/config.js` — link da planilha publicada e do site.
- `data/produtos.json` — cópia de segurança dos produtos, usada se a planilha estiver fora do ar.
- `img/` — fotos 600×600 (origem em `img/FONTES.csv`); `img/marca/` — logo e ícones.
- `tools/gerar_dados.py` — gera `produtos.csv` e `data/produtos.json`; `tools/padronizar.swift` — padroniza fotos.
- `sw.js` + `manifest.webmanifest` — abre rápido, funciona sem internet e pode ser instalado na tela inicial.
