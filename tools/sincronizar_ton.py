"""Lê o catálogo público da Ton (estoque e preço de cada produto no totem) e grava data/estoque.json.

O site usa esse arquivo para marcar cada produto como disponível (estoque > 0) ou esgotado (0);
produto sem par na Ton fica oculto. Roda no GitHub Actions a cada 30 min (.github/workflows/estoque.yml)
ou à mão: python3 tools/sincronizar_ton.py

Fonte: a mesma chamada que a página catalogo.ton.com.br/eguadomercado faz para listar produtos
(server action "getProductList", paginada por cursor). Se o ID da action mudar num deploy da Ton,
ele é redescoberto nos scripts da página. O mapa SKU do site -> produto Ton fica em data/ton_map.json.
Uso: python3 tools/sincronizar_ton.py [--mapear]   (--mapear sugere pares para SKUs ainda sem mapa)
"""
import base64, datetime as dt, json, os, re, sys, unicodedata, urllib.error, urllib.request

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOJA = "https://catalogo.ton.com.br/eguadomercado"
LOJA_ID = "01a13d5c-4424-752e-a7e1-ddbd59716feb"
ACTION_PADRAO = "40c3671931f2a8599a2324b1c03e6ba2e821d52b8b"
UA = {"User-Agent": "Mozilla/5.0 (EguaCatalogo; estoque)"}
MAPA = os.path.join(RAIZ, "data", "ton_map.json")
SAIDA = os.path.join(RAIZ, "data", "estoque.json")


def baixar(url, dados=None, cab=None):
    req = urllib.request.Request(url, data=dados, headers={**UA, **(cab or {})})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8")


def descobrir_action():
    """Procura o ID da server action getProductList nos scripts da página."""
    html = baixar(LOJA)
    for js in sorted(set(re.findall(r'/_next/static/chunks/[^"\s\\]+\.js', html))):
        m = re.search(r'createServerReference\)\("([0-9a-f]{40,})"[^)]*"getProductList"\)', baixar("https://catalogo.ton.com.br" + js))
        if m:
            return m.group(1)
    raise RuntimeError("action getProductList não encontrada na página da Ton")


def pagina(action, cursor):
    corpo = json.dumps([{"storeId": LOJA_ID, "status": "public", "productName": "", "categoryId": "", "cursor": cursor}]).encode()
    txt = baixar(LOJA, corpo, {"Next-Action": action, "Accept": "text/x-component", "Content-Type": "text/plain;charset=UTF-8"})
    for linha in txt.splitlines():
        _, _, js = linha.partition(":")
        if js.startswith('{"data"'):
            return json.loads(js)["data"]
    raise ValueError("resposta da Ton sem lista de produtos")


# Primeiro cursor pedindo 200 por página: a paginação de 9 em 9 da Ton às vezes repete uma página e pula outra.
CURSOR_0 = base64.b64encode(json.dumps({"lo_f": {"i": ["public"], "j": False},
                                        "lo_p": {"lo_obc": "name", "lo_od": "asc", "lo_ir": 0, "lo_ps": 200}},
                                       separators=(",", ":")).encode()).decode()


def ler_ton():
    action = ACTION_PADRAO
    for tentativa in range(2):
        try:
            por_id, cursor = {}, CURSOR_0
            while cursor:
                d = pagina(action, cursor)
                por_id.update((p["id"], p) for p in d["items"])
                cursor = d.get("nextPageCursor")
                if len(por_id) > 2000:
                    raise RuntimeError("paginação não termina")
            if not por_id:
                raise ValueError("Ton devolveu lista vazia")
            return list(por_id.values())
        except (ValueError, urllib.error.HTTPError, json.JSONDecodeError):
            if tentativa:
                raise
            action = descobrir_action()


def norm(s):
    return re.sub(r"[^a-z0-9]+", " ", unicodedata.normalize("NFD", s or "").encode("ascii", "ignore").decode().lower()).strip()


def main():
    ton = ler_ton()
    por_id = {p["id"]: p for p in ton}
    mapa = json.load(open(MAPA, encoding="utf-8"))
    itens = {}
    for sku, m in mapa.items():
        p = por_id.get(m["id"])
        if not p:
            continue  # saiu da Ton: o site oculta
        v = p["variants"][0]
        itens[sku] = {"estoque": max(0, int((v.get("stock") or {}).get("current") or 0)),
                      "preco_ton": round(((v.get("price") or {}).get("sale") or 0) / 100, 2)}
    usados = {m["id"] for m in mapa.values()}
    sem_mapa = sorted(p["name"] for p in ton if p["id"] not in usados)
    novo = {"atualizado": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"), "fonte": LOJA,
            "itens": dict(sorted(itens.items())), "sem_mapa": sem_mapa}
    antigo = json.load(open(SAIDA, encoding="utf-8")) if os.path.exists(SAIDA) else {}
    if {k: antigo.get(k) for k in ("itens", "sem_mapa")} == {k: novo[k] for k in ("itens", "sem_mapa")}:
        print(f"sem mudança ({len(itens)} SKUs)")
        return
    with open(SAIDA, "w", encoding="utf-8") as f:
        json.dump(novo, f, ensure_ascii=False, indent=1)
    print(f"{len(ton)} produtos na Ton · {len(itens)} SKUs com estoque · {sum(1 for i in itens.values() if i['estoque'] == 0)} esgotados"
          f" · {len(sem_mapa)} sem mapa: {', '.join(sem_mapa)}")
    if "--mapear" in sys.argv:
        for p in ton:
            if p["id"] not in usados:
                print(f'  "{p["id"]}"  {p["name"]}')


if __name__ == "__main__":
    main()
