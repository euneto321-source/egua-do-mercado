"""Gera a base inicial do catálogo a partir do catálogo Ton (20/10/2026).

Saídas:
  produtos.csv          -> importar no Google Sheets (aba Catalogo)
  data/produtos.json    -> cópia embutida no site (usada se a planilha falhar)
  img/<sku>.jpg         -> fotos padronizadas 600x600, fundo branco
  img/FONTES.csv        -> origem de cada foto

Só leva colunas públicas: nunca custo nem margem.
Uso: python3 tools/gerar_dados.py [--sem-fotos]
"""
import csv, json, os, subprocess, sys, urllib.request

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CDN = "https://swh-cdn-prd.stone.com.br/swh-hub/images/raw/store-01a13d5c-4424-752e-a7e1-ddbd59716feb/"

# sku, nome, marca, apresentacao, categoria, preco, arquivo da foto no CDN da Ton
P = [
    # Bebidas
    ("agua-crystal-gas-500", "Água Mineral com Gás", "Crystal", "500 ml", "Bebidas", 3.50, "01a15995-62c5-7863-801f-8bda2b3ef36b.png"),
    ("coca-cola-lata-220", "Coca-Cola", "Coca-Cola", "Lata 220 ml", "Bebidas", 4.00, "01a15096-b7f6-78cf-b8f4-de84991edaf3.jpeg"),
    ("coca-cola-zero-lata-220", "Coca-Cola Sem Açúcar", "Coca-Cola", "Lata 220 ml", "Bebidas", 4.00, "01a15096-2a1a-7ef3-a7e2-a576cfc820a4.jpeg"),
    ("fanta-laranja-lata-350", "Fanta Laranja", "Fanta", "Lata 350 ml", "Bebidas", 4.00, "01a150a1-72a0-7bb4-b6ba-bd1e1558221f.jpeg"),
    ("guarana-antarctica-lata-350", "Guaraná Antarctica", "Antarctica", "Lata 350 ml", "Bebidas", 4.00, "01a15097-e642-739c-8388-d53b5dc727ba.jpeg"),
    ("nescau-pronto-270", "Nescau Bebida Láctea", "Nestlé", "270 ml", "Bebidas", 9.00, "01a1508e-6f98-71ff-ad70-b2d240493231.jpeg"),
    ("toddynho-200", "Toddynho", "Toddynho", "200 ml", "Bebidas", 4.00, "01a1508f-7796-7c4f-a97d-69b7adcdacb6.jpeg"),
    ("3coracoes-baunilha-250", "Bebida Láctea Baunilha", "3 Corações", "250 ml", "Bebidas", 10.00, "01a15152-ef04-7f41-9322-2c50f703b53f.jpeg"),
    ("3coracoes-chocolate-250", "Bebida Láctea Chocolate", "3 Corações", "250 ml", "Bebidas", 10.00, "01a15153-d27d-772d-beb5-001f4fc57495.jpeg"),
    ("3coracoes-napolitano-250", "Bebida Láctea Napolitano", "3 Corações", "250 ml", "Bebidas", 10.00, "01a1516c-7997-7423-b564-3f8aba7707b1.jpeg"),
    ("marata-abacaxi-200", "Suco de Abacaxi", "Maratá", "200 ml", "Bebidas", 3.00, "01a15155-361a-74e3-b3af-2394cb6d4ebf.jpeg"),
    ("marata-morango-200", "Suco de Morango", "Maratá", "200 ml", "Bebidas", 3.00, "01a15154-cf10-7ee7-96f6-8196d790d7fe.jpeg"),
    ("dafruta-laranja-200", "Suco de Laranja", "Dafruta", "200 ml", "Bebidas", 2.00, "01a1515c-3ae5-7577-b276-bdc7f1b2e41b.jpeg"),
    # Energéticos
    ("monster-473", "Energético Monster", "Monster", "Lata 473 ml", "Energéticos", 14.50, "01a1508c-74ec-7bef-81e0-a65ac26772ef.jpeg"),
    ("red-bull-250", "Energético Red Bull", "Red Bull", "Lata 250 ml", "Energéticos", 13.00, "01a1508c-ce12-7c40-b9bd-abedf03928b3.jpeg"),
    # Snacks
    ("pringles-original-35", "Pringles Original", "Pringles", "35 g", "Snacks", 9.00, "01a15086-3e43-7b18-9b06-a2b1e58ed2e0.jpeg"),
    ("pringles-original-latao", "Pringles Original Latão", "Pringles", "Lata grande", "Snacks", 12.00, "01a15982-a1a8-7833-8fed-218dbb398dad.png"),
    ("crony-35", "Batata Crony", "Crony", "35 g", "Snacks", 5.50, "01a15086-fac6-7552-9a1e-96f7c6a2d3bd.jpeg"),
    ("refinata-picanha-40", "Batata Refinata Picanha", "Refinata", "40 g", "Snacks", 6.50, "01a150a0-1368-75a2-8895-60afffa8cec5.jpeg"),
    ("doritos-nacho-32", "Doritos Queijo Nacho", "Doritos", "32 g", "Snacks", 7.00, "01a1508b-ccc1-7c2e-9fd3-c08d8a8c2ff9.jpeg"),
    ("cheetos-lua-35", "Cheetos Lua", "Cheetos", "35 g", "Snacks", 6.00, "01a15085-c47d-7b05-95cc-b3deedc78183.jpeg"),
    ("cheetos-bola-35", "Cheetos Bola", "Cheetos", "35 g", "Snacks", 6.50, "01a150a2-98b2-7bc2-be11-77911811363c.jpeg"),
    ("cheetos-onda-40", "Cheetos Onda", "Cheetos", "40 g", "Snacks", 5.00, "01a15084-883f-77d0-9d9f-5af08e7beb05.jpeg"),
    ("fandangos-queijo-35", "Fandangos Queijo", "Fandangos", "35 g", "Snacks", 4.70, "01a15986-38cf-7582-867a-2e0ce2d75bed.png"),
    ("torcida-bacon-35", "Torcida Bacon", "Torcida", "35 g", "Snacks", 3.00, "01a15091-6238-7d61-99cf-ff4148f5e724.jpeg"),
    ("torcida-churrasco-35", "Torcida Churrasco", "Torcida", "35 g", "Snacks", 3.00, "01a15091-cb79-7305-af23-4514e4c34b8c.jpeg"),
    ("pipoca-mariza-manteiga-100", "Pipoca de Micro-ondas Manteiga", "Mariza", "100 g", "Snacks", 3.00, "01a150a9-ea97-709c-b3aa-bf62de55a389.jpeg"),
    ("pipoca-mariza-queijo-100", "Pipoca de Micro-ondas Queijo", "Mariza", "100 g", "Snacks", 3.00, "01a150a6-83cd-7056-a4df-27989b0eda11.jpeg"),
    ("pipoca-mariza-natural-100", "Pipoca de Micro-ondas Natural", "Mariza", "100 g", "Snacks", 3.00, "01a1508d-eaa2-7954-b143-da98f177fcb1.jpeg"),
    # Biscoitos & Cereais
    ("mini-oreo-35", "Mini Oreo", "Oreo", "35 g", "Biscoitos & Cereais", 5.00, "01a15088-f10a-7b46-90af-52c7726ba15b.jpeg"),
    ("negresco-morango-90", "Negresco Morango", "Nestlé", "90 g", "Biscoitos & Cereais", 5.00, "01a1515e-5f9e-7133-997c-9e8c77e1587b.jpeg"),
    ("passatempo-morango-130", "Passatempo Morango", "Nestlé", "130 g", "Biscoitos & Cereais", 5.50, "01a15088-7587-7bf4-9ead-84d83ab344d1.jpeg"),
    ("bono-chocolate-90", "Bono Chocolate", "Nestlé", "90 g", "Biscoitos & Cereais", 5.00, "01a15089-6f1f-7856-9b1f-b408ff64b560.jpeg"),
    ("cookie-garoto-crocante", "Cookie Crocante Chocolate", "Garoto", "Pacote", "Biscoitos & Cereais", 4.50, "01a15094-afb7-7345-9bd8-a5b30a796a24.jpeg"),
    ("club-social-integral-288", "Club Social Integral", "Club Social", "Sachê", "Biscoitos & Cereais", 2.50, "01a1515b-cb06-70ba-aaa9-f2fcd21563b6.jpeg"),
    ("cereal-nescau-120", "Cereal Nescau", "Nestlé", "120 g", "Biscoitos & Cereais", 8.00, "01a1515d-1ec2-70dc-bb50-5ca9f952baec.jpeg"),
    ("nutry-banana-22", "Barra de Cereal Banana", "Nutry", "22 g", "Biscoitos & Cereais", 3.00, "01a15088-0845-7b1e-8114-52c0cb34bf99.jpeg"),
    # Chocolates & Doces
    ("crunch-garoto-80", "Chocolate Crunch", "Garoto", "80 g", "Chocolates & Doces", 9.50, "01a15089-f970-7c12-833f-7927de121fb9.jpeg"),
    ("crunch-nestle-80", "Chocolate Crunch", "Nestlé", "80 g", "Chocolates & Doces", 11.00, "01a1508a-4370-71ba-a84b-a46a8f36622d.jpeg"),
    ("kitkat-dark-41", "KitKat Dark", "Nestlé", "41,5 g", "Chocolates & Doces", 6.00, "01a1508d-1669-7c32-96ea-0362f43f2c60.jpeg"),
    ("bis-original-100", "Bis Original", "Lacta", "100,8 g · 16 unidades", "Chocolates & Doces", 12.50, "01a1509c-0d2b-7012-ac5e-bb9ddf6f8eb0.jpeg"),
    ("halls-morango", "Halls Morango", "Halls", "Unidade", "Chocolates & Doces", 2.00, "01a15090-dbee-77a9-b37a-6e9473c4bce9.jpeg"),
    ("trident", "Trident", "Trident", "Unidade", "Chocolates & Doces", 3.00, "01a1515b-4baf-7562-873c-6bdd32b98655.jpeg"),
    # Instantâneos
    ("cup-noodles-carne-69", "Cup Noodles Carne", "Nissin", "69 g", "Instantâneos", 6.00, "01a1508b-3253-7bd5-b24e-aa00949a3e7e.jpeg"),
    ("nissin-carne-85", "Lámen Carne", "Nissin", "85 g", "Instantâneos", 3.50, "01a15090-836a-7765-beed-1d1a9494d8ed.jpeg"),
    ("nissin-galinha-caipira-85", "Lámen Galinha Caipira", "Nissin", "85 g", "Instantâneos", 3.50, "01a1515d-d3c5-78ec-99d1-6fdc7a208497.jpeg"),
    # Refrigerados & Congelados
    ("lasanha-sadia-bolonhesa-350", "Lasanha Bolonhesa", "Sadia", "350 g", "Refrigerados & Congelados", 19.00, "01a15167-2c57-7acb-bfc0-e7e7240b2172.jpeg"),
    ("fettuccine-perdigao-bolonhesa", "Fettuccine Bolonhesa", "Perdigão", "Pacote", "Refrigerados & Congelados", 11.00, "01a15162-1a6d-797c-9ba0-ba70dcfd2e89.jpeg"),
    ("sanduiche-sadia-frango-145", "Sanduíche de Frango", "Sadia", "145 g", "Refrigerados & Congelados", 13.50, "01a15166-19c4-7aa5-a3c9-420acf6ec4c9.jpeg"),
    ("hot-hit-seara-xbacon-145", "Hot Hit X-Bacon", "Seara", "145 g", "Refrigerados & Congelados", 12.00, "01a1516a-8c20-77ea-8bf1-fcd43885562d.jpeg"),
    ("pizza-beni-calabresa-110", "Pizza Calabresa", "Beni", "110 g", "Refrigerados & Congelados", 7.50, "01a15177-ea44-7a48-b657-0a3f6572fb35.jpeg"),
    ("nuggets-275", "Nuggets", "Aurora", "275 g", "Refrigerados & Congelados", 11.00, ""),
    ("tirinha-frango-aurora-275", "Tirinhas de Frango", "Aurora", "275 g", "Refrigerados & Congelados", 11.00, "01a15169-a29b-7b47-8faf-8a787098fb78.jpeg"),
    ("hamburguer-perdigao-56", "Hambúrguer Bovino", "Perdigão", "56 g", "Refrigerados & Congelados", 2.00, "01a15160-0a93-79e7-9146-e8c79dfac485.jpeg"),
    ("pao-de-queijo-minas-400", "Pão de Queijo", "Minas", "400 g", "Refrigerados & Congelados", 13.50, "01a1517a-5510-7640-9068-1498184553b7.jpeg"),
    ("batata-bem-brasil-400", "Batata para Assar", "Bem Brasil", "400 g", "Refrigerados & Congelados", 10.50, "01a15175-96e6-7561-8805-8504b01eacfa.jpeg"),
    ("danoninho-70", "Danoninho", "Danone", "70 g", "Refrigerados & Congelados", 5.50, "01a15159-6f40-7080-8282-bf112ea7f457.jpeg"),
    ("iogurte-nestle-morango-170", "Iogurte Morango", "Nestlé", "170 g", "Refrigerados & Congelados", 5.50, "01a15158-b7fd-78de-a0ab-58f8d2f4d518.jpeg"),
    ("flambynho-morango-100", "Flambynho Morango", "Flambynho", "100 g", "Refrigerados & Congelados", 4.50, "01a15159-d5e5-708c-848f-c761bf3f1b30.jpeg"),
    ("requeijao-tirolez-200", "Requeijão Tradicional", "Tirolez", "200 g", "Refrigerados & Congelados", 12.50, "01a15158-0aca-7895-8623-c246c30db5f5.jpeg"),
    ("margarina-qualy-sal-250", "Margarina com Sal", "Qualy", "250 g", "Refrigerados & Congelados", 8.50, "01a1508f-21ec-720b-bc71-d6db6d7e5e01.jpeg"),
    # Mercearia
    ("leite-em-po-200", "Leite em Pó Integral", "Camponesa", "200 g", "Mercearia", 8.00, "01a15093-fbf3-7331-8a1b-94f53cd2bbbe.jpeg"),
    ("ovos-2un", "Ovos", "", "2 unidades", "Mercearia", 2.00, "01a156a2-1dfe-77ea-8063-e36ef2b2af6d.png"),
    # 3ª compra (cupom 21/10/2026): preço e foto do cadastro Ton de cada produto
    ("moving-protein-310", "Moving Protein Booster", "Moving", "310 ml", "Bebidas", 18.00, "01a1638a-a963-7aa7-963e-ef84b5d44540.png"),
    ("banana-chips-50", "Banana Chips", "", "50 g", "Snacks", 5.00, "01a16377-984d-776b-8518-18559dfdfda1.png"),
    ("flay-queijo-40", "Flay Sabor Queijo", "Parati", "40 g", "Snacks", 3.75, "01a16379-72d7-7617-97d6-6023924798e5.png"),
    ("oreo-original-18", "Oreo Original", "Oreo", "18 g", "Biscoitos & Cereais", 2.50, "01a16367-4880-73a8-bf99-b96813ef4a09.png"),
    ("cookies-nestle-60", "Cookies Chocolate", "Nestlé", "60 g", "Biscoitos & Cereais", 5.00, "01a1636b-9ec5-7e9e-bffa-df7d2557e4bf.png"),
    ("bolinho-bauducco-duplo-chocolate-40", "Bolinho Duplo Chocolate", "Bauducco", "40 g", "Biscoitos & Cereais", 3.00, "01a16364-d221-7413-9cdf-37b7e4630c55.png"),
    ("rancheiro-rosquinha-coco-300", "Rosquinha de Coco", "Rancheiro", "300 g", "Biscoitos & Cereais", 7.00, "01a16376-585a-7af6-bd7e-7edc2a6f5e01.png"),
    ("jasmine-rosquinha-laranja-cenoura", "Rosquinhas Integrais Laranja e Cenoura", "Jasmine", "Pacote", "Biscoitos & Cereais", 14.75, "01a16372-3e3c-7278-b7c9-0faa5f9f97cd.png"),
    ("jasmine-sousweet-banana-aveia-135", "Biscoito Integral SOUsweet Banana e Aveia", "Jasmine", "135 g", "Biscoitos & Cereais", 6.50, "01a1636d-7b1d-74ef-8ff5-be4b0af66c88.png"),
    ("sonho-de-valsa", "Bombom Sonho de Valsa", "Lacta", "Unidade", "Chocolates & Doces", 1.50, "01a1637b-c6a7-7187-82b2-b84ec4c5b3ce.png"),
    ("nutella", "Nutella", "Ferrero", "Pote", "Chocolates & Doces", 15.00, "01a16369-a725-742f-9c72-5f1df10018c7.png"),
    ("coxinha-asa-ave-serra-600", "Coxinha da Asa Temperada Air Fryer", "Ave Serra", "600 g", "Refrigerados & Congelados", 21.00, "01a16385-8894-78e1-913a-2bcdc6f6ae54.png"),
    ("steak-frango-rezende-100", "Steak de Frango", "Rezende", "100 g", "Refrigerados & Congelados", 3.00, "01a16387-98a8-7bdb-a3c1-e4bf9ba4479c.png"),
    ("iogurte-duo-morango-120", "Iogurte Duo Morango", "Canto de Minas", "120 g", "Refrigerados & Congelados", 5.00, "01a1638c-5ebc-7bc7-a020-1d582660b59d.png"),
    ("pao-bauducco-fermentacao-390", "Pão de Forma Fermentação Natural", "Bauducco", "390 g", "Mercearia", 10.00, "01a16383-ce82-7908-8a50-bd6feb9159af.png"),
    ("colgate-tripla-acao-xtra-white", "Creme Dental Tripla Ação Xtra White", "Colgate", "Tubo", "Higiene & Cuidados", 6.00, "01a16382-92b2-7854-a852-f3e07a7de35a.png"),
    ("escova-colgate-classic-clean", "Escova de Dentes Classic Clean", "Colgate", "Macia", "Higiene & Cuidados", 8.00, "01a16380-341d-7b43-b56f-eec9571077c2.png"),
    ("always-basic-10", "Absorvente Always Basic", "Always", "10 unidades", "Higiene & Cuidados", 6.00, "01a1637e-dc43-7b2b-a87f-63feba35c0d7.png"),
    # comprados na 3ª compra, ainda sem cadastro (nem preço) na Ton: ficam ocultos até ter preço
    ("cassini-polvilho", "Biscoito de Polvilho", "Cassini", "Pacote", "Biscoitos & Cereais", None, ""),
    ("cream-cracker-mammamia", "Cream Cracker", "Mammamia", "Pacote", "Biscoitos & Cereais", None, ""),
    ("kinder-joy", "Kinder Joy", "Kinder", "Unidade", "Chocolates & Doces", None, ""),
    ("iogurte-nestle-zero-morango-170", "Iogurte Zero Morango", "Nestlé", "170 g", "Refrigerados & Congelados", None, ""),
    ("pao-de-queijo-300", "Pão de Queijo Tradicional", "", "300 g", "Refrigerados & Congelados", None, ""),
    # 4ª compra (NFC-e 226172 Atacadão, 23/10/2026): preço e foto do cadastro Ton
    ("fanta-laranja-lata-220", "Fanta Laranja", "Fanta", "Lata 220 ml", "Bebidas", 3.50, "01a169c4-82a9-71b8-9f23-fb01dfacf400.png"),
    ("fanta-uva-lata-220", "Fanta Uva", "Fanta", "Lata 220 ml", "Bebidas", 3.50, "01a169c8-eca6-7e24-8497-e65f4fda3bf6.png"),
    ("red-bull-zero-250", "Energético Red Bull Zero", "Red Bull", "Lata 250 ml", "Energéticos", 13.00, "01a16912-fd19-7e79-96c4-034636e1dbf6.png"),
    ("club-social-presunto", "Club Social Presunto", "Club Social", "Sachê", "Biscoitos & Cereais", 2.50, "01a169ce-7f33-70fc-b1e1-4793d1fe0c4a.png"),
    ("bauducco-barrinha-chocolate-25", "Barrinha Recheada Chocolate", "Bauducco", "25 g", "Biscoitos & Cereais", 2.25, "01a16910-464f-7139-ac84-03cb4d3b7eaa.png"),
    ("bauducco-biscoito-chocolate-108", "Biscoito Recheado Chocolate", "Bauducco", "108 g", "Biscoitos & Cereais", 4.00, "01a16911-dd37-7677-9113-33fa8bbe9880.png"),
    ("cup-noodles-yakissoba-70", "Cup Noodles Yakissoba", "Nissin", "70 g", "Instantâneos", 6.00, "01a16901-6ab7-790e-b07a-47e3e8603328.png"),
    ("lasanha-seara-bolonhesa-300", "Lasanha à Bolonhesa Air Fryer", "Seara", "300 g", "Refrigerados & Congelados", 15.00, "01a16902-d016-7e44-bf35-545b1893381b.png"),
    ("hot-hit-seara-xpicanha-145", "Hot Hit X-Picanha com Ketchup", "Seara", "145 g", "Refrigerados & Congelados", 12.00, "01a1690d-5d30-7594-8c18-64a686849647.png"),
    ("toscanaburguer-perdigao-145", "Toscanaburguer Montana", "Perdigão", "145 g", "Refrigerados & Congelados", 12.00, "01a1690b-b33b-7ffd-9624-55ca417e0791.png"),
    ("faroeste-burger-145", "Faroeste Burger X-Bacon com Requeijão", "", "145 g", "Refrigerados & Congelados", 12.00, "01a16904-939b-731b-ab92-b7ac6cc2440a.png"),
    ("empanado-presunto-queijo-110", "Recheado Presunto e Queijo", "Seara", "110 g", "Refrigerados & Congelados", 5.00, "01a1690e-b7e1-7045-8ea7-dcad49e62c14.png"),
    # comprado para revenda, ainda sem cadastro (nem preço) na Ton: oculto até ter preço
    ("coca-cola-pet-15", "Coca-Cola", "Coca-Cola", "Garrafa 1,5 L", "Bebidas", None, ""),
]
NOVIDADE = {**{sku: "21/10/2026" for sku, *_ in P[63:86]}, **{sku: "23/10/2026" for sku, *_ in P[86:]}}
REABASTECIDO = {"coca-cola-lata-220": "21/10/2026", "coca-cola-zero-lata-220": "21/10/2026",
                **{s: "23/10/2026" for s in ("bono-chocolate-90", "crony-35", "pringles-original-latao", "doritos-nacho-32",
                                             "club-social-integral-288", "hot-hit-seara-xbacon-145")}}

COLUNAS = ["sku", "nome", "marca", "apresentacao", "categoria", "preco", "preco_promo", "promo_ate",
           "foto", "mais_procurado", "novidade_desde", "ativo", "ordem", "reabastecido_em"]


def baixar_foto(sku, arq):
    destino = os.path.join(RAIZ, "img", f"{sku}.jpg")
    if os.path.exists(destino):
        return f"img/{sku}.jpg"
    bruto = os.path.join(RAIZ, "img", "raw", sku + os.path.splitext(arq)[1])
    req = urllib.request.Request(CDN + arq, headers={"User-Agent": "EguaCatalogo/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r, open(bruto, "wb") as f:
        f.write(r.read())
    # PNG com transparência: achata sobre branco antes de virar JPEG
    subprocess.run([os.path.join(RAIZ, "tools", "padronizar"), bruto, destino], check=True)  # swiftc -O tools/padronizar.swift -o tools/padronizar
    return f"img/{sku}.jpg"


def main():
    com_fotos = "--sem-fotos" not in sys.argv
    linhas, fontes = [], []
    for i, (sku, nome, marca, apres, cat, preco, arq) in enumerate(P, start=1):
        foto = ""
        if arq and com_fotos:
            foto = baixar_foto(sku, arq)
            fontes.append((sku, "Catálogo Ton Égua do Mercado (foto cadastrada pelo dono)", CDN + arq))
        elif arq:
            foto = f"img/{sku}.jpg"
        linhas.append({"sku": sku, "nome": nome, "marca": marca, "apresentacao": apres, "categoria": cat,
                       "preco": "" if preco is None else f"{preco:.2f}".replace(".", ","), "preco_promo": "", "promo_ate": "",
                       "foto": foto, "mais_procurado": "", "novidade_desde": NOVIDADE.get(sku, ""),
                       "ativo": "N" if preco is None else "S", "ordem": i, "reabastecido_em": REABASTECIDO.get(sku, "")})
    with open(os.path.join(RAIZ, "produtos.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLUNAS)
        w.writeheader()
        w.writerows(linhas)
    with open(os.path.join(RAIZ, "data", "produtos.json"), "w", encoding="utf-8") as f:
        json.dump({"atualizado": "2026-10-22", "produtos": linhas}, f, ensure_ascii=False, indent=1)
    if fontes:
        with open(os.path.join(RAIZ, "img", "FONTES.csv"), "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["sku", "origem", "url"])
            w.writerows(fontes)
    print(f"{len(linhas)} produtos, {sum(1 for l in linhas if l['foto'])} com foto")


if __name__ == "__main__":
    main()
