"""Gera os banners de divulgação em PNG (banners/*.png) a partir de banners/banners.html.

Três peças (novos, destaque, volta) em dois formatos: feed 1080×1350 (WhatsApp/Instagram) e story 1080×1920 (status).
Usam só produtos com estoque > 0 no totem: rodar antes python3 tools/sincronizar_ton.py.
Uso: python3 tools/gerar_banners.py   (precisa do Google Chrome instalado)
"""
import functools, http.server, os, subprocess, tempfile, threading

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
TAM = {"feed": (1080, 1350), "story": (1080, 1920)}


def main():
    class Quieto(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a):
            pass
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Quieto, directory=RAIZ))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    porta = srv.server_address[1]
    with tempfile.TemporaryDirectory() as perfil:
        for b in ("novos", "destaque", "volta"):
            for f, (w, hgt) in TAM.items():
                saida = os.path.join(RAIZ, "banners", f"{b}-{f}.png")
                subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", f"--user-data-dir={perfil}",
                                f"--window-size={w},{hgt}", "--force-device-scale-factor=1", "--virtual-time-budget=10000",
                                f"--screenshot={saida}", f"http://127.0.0.1:{porta}/banners/banners.html?b={b}&f={f}"],
                               check=True, capture_output=True)
                print("ok", os.path.relpath(saida, RAIZ))
    srv.shutdown()


if __name__ == "__main__":
    main()
