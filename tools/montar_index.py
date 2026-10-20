"""Monta index.html (site publicado) a partir de src/app.html (mesmo arquivo usado no protótipo).

O protótipo publicado como Artifact recebe src/app.html direto; o site no GitHub Pages
precisa do documento completo, do manifest do PWA e do js/config.js.
Uso: python3 tools/montar_index.py
"""
import os

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
app = open(os.path.join(RAIZ, "src", "app.html"), encoding="utf-8").read()

cabeca = """<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="description" content="Catálogo do Égua do Mercado: produtos e preços do minimercado 24 horas.">
<link rel="manifest" href="manifest.webmanifest">
<link rel="icon" href="img/marca/icone-192.png">
<link rel="apple-touch-icon" href="img/marca/icone-180.png">
<link rel="preload" href="data/produtos.json" as="fetch" crossorigin>
<script src="js/config.js"></script>
"""
# Tudo antes de </style> é cabeçalho; o resto é corpo.
corte = app.index("</style>") + len("</style>")
html = cabeca + app[:corte] + "\n<style>[hidden]{display:none!important}:root{padding-top:env(safe-area-inset-top,0px)}</style>\n</head>\n<body>\n" + app[corte:] + """
<script>if ("serviceWorker" in navigator) navigator.serviceWorker.register("sw.js").catch(() => {});</script>
</body>
</html>
"""
open(os.path.join(RAIZ, "index.html"), "w", encoding="utf-8").write(html)
print("index.html montado")
