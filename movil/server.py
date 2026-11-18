# Servidor local de la app móvil: sirve los archivos de movil/ igual que
# "python -m http.server" y además recibe el Anexo A capturado en el celular
# (POST /api/anexo-a) y lo guarda en anexo_a_movil.json, en la raíz del
# proyecto, para que SAPE2.py lo pueda importar ("Anexo A -> Importar del
# celular").
import datetime
import http.server
import json
import socketserver
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
SALIDA = RAIZ.parent / "anexo_a_movil.json"


class ManejadorAnexoA(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(RAIZ), **kwargs)

    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_POST(self):
        if self.path != "/api/anexo-a":
            self.send_error(404, "Ruta no encontrada")
            return
        largo = int(self.headers.get("Content-Length", 0) or 0)
        crudo = self.rfile.read(largo) if largo else b""
        try:
            registro = json.loads(crudo.decode("utf-8"))
        except (ValueError, UnicodeDecodeError):
            self.send_error(400, "JSON inválido")
            return
        registros = []
        if SALIDA.exists():
            try:
                registros = json.loads(SALIDA.read_text(encoding="utf-8"))
            except ValueError:
                registros = []
        registro["recibido"] = datetime.datetime.now().isoformat(timespec="seconds")
        clave = (registro.get("modulo"), registro.get("equipo"))
        registros = [
            r for r in registros
            if (r.get("modulo"), r.get("equipo")) != clave
        ]
        registros.insert(0, registro)
        SALIDA.write_text(
            json.dumps(registros[:100], ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        cuerpo = json.dumps({"ok": True}).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(cuerpo)))
        self.end_headers()
        self.wfile.write(cuerpo)

    def log_message(self, formato, *args):
        # Silencia el log de acceso normal; solo avisa errores.
        if args and str(args[1]).startswith(("4", "5")):
            super().log_message(formato, *args)


if __name__ == "__main__":
    puerto = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("0.0.0.0", puerto), ManejadorAnexoA) as httpd:
        print(f"S.A.P.E. móvil: sirviendo movil/ en 0.0.0.0:{puerto}")
        print(f"Anexo A capturado se guarda en: {SALIDA}")
        httpd.serve_forever()
