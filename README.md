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
| `categoria` | Uma destas: Bebidas · Energéticos · Snacks · Biscoitos & Cereais · Chocolates & Doces · Instantâneos · Refrigerados & Congelados · Mercearia · Higiene & Cuidados. Uma categoria nova também funciona, com ícone genérico. |
| `preco` | Preço de venda, ex.: `4,00`. |
| `preco_promo` | Preço da oferta. Vazio = sem oferta. Só vale se for menor que `preco`. |
| `promo_ate` | Último dia da oferta (`31/10/2026`). Vazio = até tirar. |
| `foto` | `img/<sku>.jpg` para fotos do site, ou um link `https://` de imagem. |
| `mais_procurado` | `S` para aparecer em "Mais procurados". |
| `novidade_desde` | Data de chegada de um produto novo (`21/10/2026`). Fica em "Acabou de chegar" e nos banners por 14 dias. |
| `ativo` | `N` esconde o produto (saiu de linha, ou comprado e ainda sem preço na Ton). |
| `ordem` | Número para ordenar dentro da categoria. |
| `reabastecido_em` | Data em que um produto que já existia voltou a ser abastecido. Fica em "Reabastecidos" e no banner "Seus favoritos estão de volta" por 14 dias. |

**Nunca** coloque custo ou margem nesta aba: ela é publicada na internet.

## Disponibilidade (estoque do totem)

O site não mostra o que não está no totem. A cada 30 minutos o GitHub Actions (`.github/workflows/estoque.yml`) lê o catálogo público da Ton e grava `data/estoque.json`:

- estoque > 0 → **disponível**;
- estoque 0 → **Esgotado**: card apagado, no fim da categoria, fora dos destaques e dos banners;
- produto sem par na Ton (`data/ton_map.json`) → **oculto**.

Produto novo: cadastre na Ton e na planilha. Depois rode `python3 tools/sincronizar_ton.py --mapear`, que lista os produtos Ton sem SKU, e acrescente o par em `data/ton_map.json`.

## Banners

`banners/banners.html` monta três peças com os dados do site: novidades, novos em destaque e reabastecidos. Cada uma sai em dois formatos, feed (1080×1350) e story (1080×1920). Para gerar os PNGs: `python3 tools/sincronizar_ton.py && python3 tools/gerar_banners.py`. Só entram produtos com estoque no totem. Nenhuma peça anuncia desconto.

## Estrutura

- `src/app.html` — a interface inteira (CSS + JS). Editar aqui e rodar `python3 tools/montar_index.py`.
- `index.html` — gerado a partir de `src/app.html`.
- `js/config.js` — link da planilha publicada e do site.
- `data/produtos.json` — cópia de segurança dos produtos, usada se a planilha estiver fora do ar.
- `img/` — fotos 600×600 (origem em `img/FONTES.csv`); `img/marca/` — logo e ícones.
- `tools/gerar_dados.py` — gera `produtos.csv` e `data/produtos.json`; `tools/padronizar.swift` — padroniza fotos.
- `tools/sincronizar_ton.py` — estoque do totem → `data/estoque.json`; `tools/gerar_banners.py` — banners em PNG.
- `sw.js` + `manifest.webmanifest` — abre rápido, funciona sem internet e pode ser instalado na tela inicial.
