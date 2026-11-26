from pathlib import Path
import ctypes
import os

# SAPE_1.py, al importarse, se relanza en otra consola y termina el proceso
# (sys.exit) salvo que vea esta variable. Sin ella los diagramas de bloques
# no abren cuando SAPE2 se inicia desde el .bat o con doble clic.
os.environ["SAPE_CONSOLA_LISTA"] = "1"
from datetime import datetime
import json
import math
import re
import subprocess
import sys
import tempfile
import tkinter as tk
from tkinter import filedialog, font as tkfont, messagebox, ttk

import customtkinter as ctk
import matplotlib
matplotlib.use("TkAgg") 
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.patches as patches
import webview

NAVY = "#0B141E"
TEXTO = "#F1F5F9"
VERDE_CLARO = "#4ADE80"
VERDE_CYAN = "#00F5C4"
AMARILLO_BRILLANTE = "#FFFF00"
GRIS = "#94A3B8"
NEON = "#00F0FF"
CUADRI = "#075A66"
ROJO_SUTERM = "#FF2222"
RA_BG = "#FFFFFF"
RA_SIDEBAR_BG = "#007A33"
RA_TEXT = "#0A2540"
RA_GREEN = "#007A33"
RA_GREEN_HOVER = "#005C25"
RA_BLUE = "#0056B3"
RA_MUTED = "#4A5568"
RA_DISABLED = "#CBD5E1"
RA_NARANJA_PASTEL = "#EC7A4C"
RA_MANDARINA_CLARO = "#FDE8DF"
RA_AZUL_PASTEL = "#93C5FD"
RA_AZUL_MARINO = "#0C5BB7"
RA_AZUL_FONDO = "#0F1D36"
RA_MOSTAZA = "#E1AD01"
RA_TEXTO_MOSTAZA = "#0B1325"
RA_MANDARINA_BOTON = "#EC6A37"
RA_MANDARINA_HOVER = "#C65328"
RA_VISTA_FONDO = "#F5F2EB"
RA_VISTA_SIDEBAR = "#1E252B"
RA_VISTA_SIDEBAR_OSCURO = "#14191E"
RA_VISTA_ITEM = "#1E252B"
RA_VISTA_HOVER = "#2A343D"
RA_VISTA_NARANJA = "#EA580C"  # mismo naranja que usa la app móvil.
RA_VISTA_NARANJA_OSCURO = "#9A3412"
RA_VISTA_AMBAR_CLARO = "#F59E0B"
RA_VISTA_ACCION = "#E67E22"
RA_VISTA_TARJETA = "#FAF8F3"
RA_VISTA_BORDE = "#D6CEC0"
RA_VISTA_INPUT = "#EFECE6"
RA_VISTA_PANEL = "#14191E"
# Paleta predominante del módulo Factor de Potencia: verdes esmeralda.
FP_VERDE = "#10B981"
FP_VERDE_OSCURO = "#059669"
FP_VERDE_HOVER = "#047857"
FP_VERDE_CLARO = "#6EE7B7"
FP_VERDE_TEXTO = "#D1FAE5"
FP_VERDE_FONDO = "#006662"
FP_ROJO_PASTEL = "#FF8080"
# Paleta predominante del módulo Relación de Transformación: morado.
TTR_MORADO = "#7C3AED"
TTR_MORADO_OSCURO = "#6D28D9"
TTR_MORADO_HOVER = "#5B21B6"
TTR_MORADO_CLARO = "#DDD6FE"
TTR_MORADO_TEXTO = "#F5F3FF"
TTR_ROSA = "#FF69B4"
TTR_PLATA = "#C0C0C0"
TTR_NUMERO = TTR_ROSA
TTR_ROSA_MEDICION = "#FF0077"  # bornes/bolitas/línea que se están midiendo.
TTR_ROSA_PASTEL = "#F5A3D0"
TTR_MORADO_PASTEL = "#C4B5FD"
TTR_MORADO_TRAS = "#D8C4FB"
TTR_MORADO_NEON = "#8E22BB"  # bornes libres (sin rol en la prueba).
TTR_LILA_FASE = "#AB49CC"  # etiquetas ∅A/∅B/∅C.
# Pastilla "Modo Diagnóstico" del encabezado de cada paso, igual que en RA/FP.
TTR_VISTA_PASTEL = "#EDE9FE"
TTR_VISTA_PASTEL_BORDE = "#C4B5FD"
RA_FONT = "Classic Robot"
RA_FONT_PATH = Path(__file__).with_name("fonts") / "Classic Robot.otf"
APP_ICON_PATH = (
    Path(ctk.__file__).parent
    / "assets"
    / "icons"
    / "CustomTkinter_icon_Windows.ico"
)
_WEBVIEW_ICON_HANDLES = []

RUTA_HISTORIAL = Path(__file__).with_name("historial_sape.json")


def _cargar_historial():
    try:
        datos = json.loads(RUTA_HISTORIAL.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    return datos if isinstance(datos, list) else []


def _agregar_historial(registro):
    historial = _cargar_historial()
    historial.insert(0, registro)
    try:
        RUTA_HISTORIAL.write_text(
            json.dumps(historial, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    except OSError:
        return False
    return True


RUTA_LECTURAS_ANEXO_A = Path(__file__).with_name("lecturas_anexo_a.json")
RUTA_ANEXO_TTR = Path(__file__).with_name("lecturas_anexo_a_ttr.json")


def _cargar_anexo_ttr():
    """Anexo A de TTR guardado, por tipo de equipo."""
    try:
        datos = json.loads(RUTA_ANEXO_TTR.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return datos if isinstance(datos, dict) else {}


def _guardar_anexo_ttr_archivo(registros):
    try:
        RUTA_ANEXO_TTR.write_text(
            json.dumps(registros, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    except OSError:
        return False
    return True


def _cargar_lecturas_anexo_a():
    try:
        datos = json.loads(RUTA_LECTURAS_ANEXO_A.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return datos if isinstance(datos, dict) else {}


def _guardar_lecturas_anexo_a_archivo(lecturas):
    try:
        RUTA_LECTURAS_ANEXO_A.write_text(
            json.dumps(lecturas, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    except OSError:
        return False
    return True


def _cargar_fuente_ra(root):
    if sys.platform != "win32":
        raise OSError("La carga privada de la fuente RA requiere Windows.")
    if not RA_FONT_PATH.is_file():
        raise FileNotFoundError(f"No se encontró la fuente RA: {RA_FONT_PATH}")

    gdi32 = ctypes.WinDLL("gdi32", use_last_error=True)
    add_font = gdi32.AddFontResourceExW
    add_font.argtypes = (ctypes.c_wchar_p, ctypes.c_uint, ctypes.c_void_p)
    add_font.restype = ctypes.c_int
    if not add_font(str(RA_FONT_PATH), 0x10, None):
        raise ctypes.WinError(ctypes.get_last_error())

    user32 = ctypes.WinDLL("user32", use_last_error=True)
    send_message = user32.SendMessageW
    send_message.argtypes = (
        ctypes.c_void_p, ctypes.c_uint, ctypes.c_void_p, ctypes.c_void_p,
    )
    send_message.restype = ctypes.c_ssize_t
    # WM_FONTCHANGE solo a esta ventana. SendMessage a HWND_BROADCAST
    # espera a todas las ventanas del escritorio y no regresa si el menú
    # web (u otra ventana) no contesta.
    send_message(ctypes.c_void_p(root.winfo_id()), 0x001D, None, None)

    if RA_FONT not in tkfont.families(root):
        raise RuntimeError(
            f"Windows cargó la fuente, pero Tk no reconoce la familia {RA_FONT!r}."
        )


def _aplicar_icono_webview(window):
    if sys.platform != "win32" or window.native is None:
        return

    user32 = ctypes.WinDLL("user32", use_last_error=True)
    load_image = user32.LoadImageW
    load_image.argtypes = (
        ctypes.c_void_p, ctypes.c_wchar_p, ctypes.c_uint,
        ctypes.c_int, ctypes.c_int, ctypes.c_uint,
    )
    load_image.restype = ctypes.c_void_p    
    icon_handle = load_image(
        None, str(APP_ICON_PATH), 1, 0, 0, 0x10 | 0x40
    )
    if not icon_handle:
        raise ctypes.WinError(ctypes.get_last_error())

    send_message = user32.SendMessageW
    send_message.argtypes = (
        ctypes.c_void_p, ctypes.c_uint, ctypes.c_size_t, ctypes.c_ssize_t,
    )
    send_message.restype = ctypes.c_ssize_t
    hwnd = ctypes.c_void_p(window.native.Handle.ToInt64())
    send_message(hwnd, 0x0080, 0, icon_handle)
    send_message(hwnd, 0x0080, 1, icon_handle)
    _WEBVIEW_ICON_HANDLES.append(icon_handle)


CFE_ASCII = (
    " ██████╗ ███████╗ ███████╗\n"
    "██╔════╝ ██╔════╝ ██╔════╝\n"
    "██║      █████╗   █████╗  \n"
    "██║      ██╔══╝   ██╔══╝  \n"
    "╚██████╗ ██║      ███████╗\n"
    " ╚═════╝ ╚═╝      ╚══════╝"
)

SAPE_ASCII = (
    "███████╗      █████╗      ██████╗      ███████╗\n"
    "██╔════╝     ██╔══██╗     ██╔══██╗     ██╔════╝\n"
    "███████╗     ███████║     ██████╔╝     █████╗\n"
    "╚════██║     ██╔══██║     ██╔═══╝      ██╔══╝\n"
    "███████║ ██╗ ██║  ██║ ██╗ ██║      ██╗ ███████╗ ██╗\n"
    "╚══════╝ ╚═╝ ╚═╝  ╚═╝ ╚═╝ ╚═╝      ╚═╝ ╚══════╝ ╚═╝"
)


def _imagen_sape_ascii(tam=11, fondo="#1E293B", color="#FFFFFF"):
    """SAPE_ASCII como imagen: Tk desalinea las esquinas ╔╗╚╝, PIL no."""
    from PIL import Image, ImageDraw, ImageFont

    # Cada renglón se dibuja pegado al anterior, a la altura exacta del bloque
    # █: así las letras quedan lisas, sin rayas blancas entre renglones. Se
    # dibuja a 4x y se reduce para que los bordes salgan suaves.
    escala = 4
    fuente = ImageFont.truetype(r"C:\Windows\Fonts\consolab.ttf", tam * escala)
    _x0, arriba, _x1, abajo = fuente.getbbox("█")
    alto_celda = abajo - arriba
    lineas = SAPE_ASCII.split("\n")
    ancho = max(int(fuente.getlength(linea)) + 1 for linea in lineas)
    margen = 2 * escala
    grande = Image.new(
        "RGB",
        (ancho + margen * 2, alto_celda * len(lineas) + margen * 2),
        fondo,
    )
    trazo = ImageDraw.Draw(grande)
    ancho_celda = fuente.getlength("█")
    for indice, linea in enumerate(lineas):
        y = margen + indice * alto_celda
        # Los bloques █ se rellenan como rectángulos contiguos: la fuente deja
        # una rendija entre un bloque y el siguiente.
        for columna, glifo in enumerate(linea):
            if glifo == "█":
                trazo.rectangle(
                    (
                        margen + round(columna * ancho_celda), y,
                        margen + round((columna + 1) * ancho_celda) - 1,
                        y + alto_celda - 1,
                    ),
                    fill=color,
                )
        trazo.text(
            (margen, y - arriba), linea.replace("█", " "),
            font=fuente, fill=color,
        )
    imagen = grande.resize(
        (grande.width // escala, grande.height // escala), Image.LANCZOS,
    )
    return ctk.CTkImage(light_image=imagen, size=imagen.size)


def _dibujar_diagrama_tc(padre):
    """Diagrama del TC: P1-P2 arriba, aislador, caja S1-S4 y tierra desde S4."""
    s = 0.8
    lienzo = tk.Canvas(
        padre, width=640, height=int(820 * s) + 14,
        bg="#FFFFFF", highlightthickness=1, highlightbackground="#E2E8F0",
    )
    lienzo.pack(fill="x", padx=15, pady=(10, 4))
    ox = (640 - 600 * s) / 2
    oy = 6

    def X(x):
        return ox + x * s

    def Y(y):
        return oy + y * s

    def fuente(tam, negrita=True):
        return ("Arial", max(8, round(tam * s)), "bold" if negrita else "normal")

    def rect(x, y, ancho, alto, **kw):
        lienzo.create_rectangle(X(x), Y(y), X(x + ancho), Y(y + alto), **kw)

    def ovalo(cx, cy, r, **kw):
        lienzo.create_oval(X(cx - r), Y(cy - r), X(cx + r), Y(cy + r), **kw)

    def linea(x1, y1, x2, y2, **kw):
        lienzo.create_line(X(x1), Y(y1), X(x2), Y(y2), **kw)

    def texto(x, y, txt, tam, color="#333333", negrita=True, ancla="w"):
        lienzo.create_text(
            X(x), Y(y), text=txt, font=fuente(tam, negrita),
            fill=color, anchor=ancla,
        )

    rojo = "#CC0000"
    azul = "#0055AA"
    # Textos aclaratorios
    texto(30, 80, "PRIMARIO", 22, rojo)
    texto(30, 105, "(Línea de AT)", 15, rojo, negrita=False)
    linea(180, 90, 210, 90, fill=rojo, width=2, dash=(4, 4))
    texto(410, 670, "SECUNDARIO", 22, azul)
    texto(410, 695, "(Instrumentos)", 15, azul, negrita=False)
    linea(380, 680, 400, 680, fill=azul, width=2, dash=(4, 4))
    # Cabeza superior del TC
    rect(200, 80, 200, 140, fill="#E0E0E0", outline="#333333", width=2)
    rect(220, 90, 160, 120, fill="#D0D0D0", outline="#333333", width=1)
    for cx, cy in ((215, 95), (385, 95), (215, 205), (385, 205)):
        ovalo(cx, cy, 4, fill="#666666", outline="#666666")
    # Primario P1-P2 con barra conductora
    linea(150, 150, 250, 150, fill=rojo, width=5)
    ovalo(150, 150, 8, fill=rojo, outline=rojo)
    texto(100, 156, "P1", 20, rojo)
    linea(350, 150, 450, 150, fill=rojo, width=5)
    ovalo(450, 150, 8, fill=rojo, outline=rojo)
    texto(470, 156, "P2", 20, rojo)
    rect(250, 140, 100, 20, fill=rojo, outline="#800000", width=2)
    rect(230, 220, 140, 15, fill="#A0A0A0", outline="#333333", width=2)
    # Aislador con anillos
    rect(275, 235, 50, 380, fill="#F9F9F9", outline="#888888", width=1)
    for i in range(12):
        rect(
            235, 245 + 30 * i, 130, 18,
            fill="#EEEEEE", outline="#555555", width=1,
        )
    rect(230, 615, 140, 15, fill="#A0A0A0", outline="#333333", width=2)
    # Base / tanque
    lienzo.create_polygon(
        X(210), Y(630), X(390), Y(630), X(410), Y(750), X(190), Y(750),
        fill="#B0B0B0", outline="#333333", width=2,
    )
    rect(200, 630, 200, 10, fill="#909090", outline="#333333", width=2)
    # Caja de bornes S1-S4
    rect(210, 660, 180, 70, fill="#DCDCDC", outline="#333333", width=2)
    linea(210, 695, 390, 695, fill="#999999", width=1, dash=(2, 2))
    for bx, nombre in ((250, "S1"), (350, "S2")):
        ovalo(bx, 680, 5, fill=azul, outline=azul)
        texto(bx - 35, 685, nombre, 16, azul)
    for bx, nombre in ((250, "S3"), (350, "S4")):
        ovalo(bx, 715, 5, fill=azul, outline=azul)
        texto(bx - 35, 720, nombre, 16, azul)
    # Puesta a tierra desde S4
    linea(355, 715, 420, 715, fill="green", width=3) 
    linea(420, 715, 420, 770, fill="green", width=3)
    linea(400, 770, 440, 770, fill="green", width=4)
    linea(408, 778, 432, 778, fill="green", width=4)
    linea(416, 786, 424, 786, fill="green", width=4)
    texto(450, 780, "Tierra", 14, "green")
    return lienzo


def _dibujar_diagrama_tpc(padre):   
    """Diagrama del TPC: divisor capacitivo C1/C2, tanque y caja de bornes."""
    s = 0.72
    lienzo = tk.Canvas( 
        padre, width=640, height=int(1050 * s) + 14,
        bg="#FFFFFF", highlightthickness=1, highlightbackground="#E2E8F0",
    )
    lienzo.pack(fill="x", padx=15, pady=(10, 4))
    ox = (640 - 850 * s) / 2
    oy = 6

    def X(x):
        return ox + x * s

    def Y(y):
        return oy + y * s

    def fuente(tam, negrita=True):
        return ("Arial", max(8, round(tam * s)), "bold" if negrita else "normal")

    def rect(x, y, ancho, alto, **kw):
        lienzo.create_rectangle(X(x), Y(y), X(x + ancho), Y(y + alto), **kw)

    def ovalo(cx, cy, r, **kw):
        lienzo.create_oval(X(cx - r), Y(cy - r), X(cx + r), Y(cy + r), **kw)

    def linea(x1, y1, x2, y2, **kw):
        lienzo.create_line(X(x1), Y(y1), X(x2), Y(y2), **kw)

    def texto(x, y, txt, tam, color="#333333", negrita=True, ancla="w"):
        lienzo.create_text(
            X(x), Y(y), text=txt, font=fuente(tam, negrita),
            fill=color, anchor=ancla,
        )

    rojo = "#CC0000"
    azul = "#0055AA"
    # Textos aclaratorios
    texto(50, 80, "PRIMARIO", 20, rojo)
    texto(50, 105, "(Alta Tensión)", 14, rojo, negrita=False)
    linea(170, 90, 210, 90, fill=rojo, width=2, dash=(4, 4))
    # Borne H1
    linea(350, 30, 350, 60, fill=rojo, width=5)
    ovalo(350, 30, 8, fill=rojo, outline=rojo)
    texto(365, 38, "H1", 20, rojo)
    rect(275, 60, 150, 40, fill="#D0D0D0", outline="#333333", width=2)
    rect(285, 70, 130, 20, fill="#B0B0B0", outline="#333333", width=1)
    # Parte capacitiva (divisor)
    rect(
        200, 120, 300, 450, fill="#FAFAFA", outline=azul, width=2, dash=(8, 4),
    )
    rect(210, 105, 280, 30, fill=azul, outline=azul)
    texto(
        350, 125, "PARTE CAPACITIVA (DIVISOR)", 12, "#FFFFFF", ancla="center",
    )
    linea(350, 140, 350, 550, fill="#333333", width=3)
    for y_c, nombre in ((160, "C1A"), (230, "C1B"), (300, "C1C"), (470, "C2")):
        linea(300, y_c, 400, y_c, fill="#333333", width=4)
        linea(300, y_c + 10, 400, y_c + 10, fill="#333333", width=4)
        texto(410, y_c + 10, nombre, 18, azul)
    ovalo(350, 390, 7, fill="#333333", outline="#333333")
    texto(350, 420, "Toma intermedia", 14, "#333333", ancla="center")
    linea(350, 480, 350, 540, fill="#333333", width=3)
    linea(330, 540, 370, 540, fill="green", width=4)
    linea(338, 548, 362, 548, fill="green", width=4)
    linea(346, 556, 354, 556, fill="green", width=4)
    texto(40, 385, "CD", 20, rojo)
    texto(40, 405, "(Cap. Total)", 12, rojo, negrita=False)
    linea(92, 390, 330, 390, fill=rojo, width=2, dash=(4, 4))
    rect(500, 365, 180, 50, fill="#FFF0F0", outline=rojo, width=2)
    texto(590, 385, "CD = (C1 × C2)", 14, "#333333", ancla="center")
    texto(590, 405, "/ (C1 + C2)", 14, "#333333", ancla="center")
    # Tanque y transformador electromagnético
    rect(260, 590, 180, 20, fill="#A0A0A0", outline="#333333", width=2)
    rect(230, 610, 240, 260, fill="#C0C0C0", outline="#333333", width=2)
    rect(250, 630, 200, 70, fill="#B0B0B0", outline="#555555", width=1)
    texto(350, 660, "Transformador", 15, "#333333", ancla="center")
    texto(350, 680, "Electromagnético", 15, "#333333", ancla="center")
    rect(250, 720, 80, 60, fill="#A0A0A0", outline="#555555", width=1)
    for y_r in (735, 745, 755, 765):
        linea(260, y_r, 320, y_r, fill="#333333", width=2)
    texto(290, 800, "Reactor", 13, "#333333", ancla="center")
    # Caja de bornes con palancas a tierra
    rect(360, 720, 140, 120, fill="#DCDCDC", outline="#333333", width=2)
    texto(430, 730, "Caja de Bornes", 11, "#333333", ancla="center")
    for bx, nombre in ((385, "X1"), (430, "X2"), (475, "X3")):
        ovalo(bx, 745, 5, fill=azul, outline=azul)
        texto(bx, 765, nombre, 14, azul, ancla="center")
    for bx, nombre in ((385, "Y1"), (430, "Y2"), (475, "Y3")):
        ovalo(bx, 805, 5, fill=azul, outline=azul)
        texto(bx, 825, nombre, 14, azul, ancla="center")
    linea(370, 780, 490, 780, fill="green", width=2)
    linea(490, 780, 490, 830, fill="green", width=2)
    ovalo(430, 745, 7, fill="", outline="green", width=2)
    linea(430, 745, 430, 780, fill="green", width=3)
    ovalo(430, 805, 7, fill="", outline="green", width=2)
    linea(430, 805, 430, 780, fill="green", width=3)
    # Rótulos externos: quedan a la derecha, sin encimarse entre sí ni
    # sobre la caja de bornes.
    linea(500, 715, 525, 715, fill=azul, width=2, dash=(4, 4))
    texto(535, 710, "SECUNDARIO", 18, azul)
    texto(535, 730, "(Instrumentos)", 12, azul, negrita=False)
    linea(500, 780, 525, 780, fill="green", width=2, dash=(4, 4))
    texto(535, 775, "PUESTA A TIERRA", 12, "green")
    texto(535, 792, "del secundario", 10, "green", negrita=False)
    # Puesta a tierra general H2 y tierra del secundario
    linea(260, 870, 260, 920, fill=rojo, width=3)
    ovalo(260, 920, 6, fill=rojo, outline=rojo)
    texto(272, 905, "H2", 20, rojo)
    linea(240, 955, 280, 955, fill="green", width=4)
    linea(248, 963, 272, 963, fill="green", width=4)
    linea(256, 971, 264, 971, fill="green", width=4)
    texto(290, 965, "Tierra Tanque", 12, "green")
    linea(490, 830, 490, 920, fill="green", width=2)
    linea(470, 920, 510, 920, fill="green", width=4)
    linea(478, 928, 502, 928, fill="green", width=4)
    linea(486, 936, 494, 936, fill="green", width=4)
    texto(520, 930, "Tierra Secundario", 12, "green")
    return lienzo


def _marcar_conexiones_planta(lienzo, X, Y, s, marcas, roles):
    """Marca sobre el dibujo de planta los bujes que llevan conexión de prueba:
    aro negro (CN/GN) o rojo (CR/GR) y el rol encima del buje.

    marcas: (nombre, cx, cy, radio) de cada buje; roles: token -> [CN, CR, ...].
    """
    for nombre, cx, cy, radio in marcas:
        rs = [rol for rol in ("CN", "CR", "GN", "GR") if rol in roles.get(nombre, [])]
        if not rs:
            continue
        color = "#FF0000" if ("CR" in rs or "GR" in rs) else "#000000"
        lienzo.create_oval(
            X(cx - radio - 7), Y(cy - radio - 7), X(cx + radio + 7), Y(cy + radio + 7),
            outline=color, width=3,
        )
        lienzo.create_text(
            X(cx), Y(cy - radio - 16), text="/".join(rs), fill=color,
            font=("Arial", max(8, round(11 * s)), "bold"),
        )


def _dibujar_diagrama_transformador_2d(padre, monofasico=False, roles=None):
    """Transformador de potencia 2 devanados (vista de planta)."""
    s = 0.62
    lienzo = tk.Canvas(
        padre, width=640, height=int(700 * s) + 14,
        bg="#FFFFFF", highlightthickness=1, highlightbackground="#E2E8F0",
    )
    lienzo.pack(fill="x", padx=15, pady=(10, 4))
    ox = (640 - 950 * s) / 2
    oy = 6

    def X(x):
        return ox + x * s

    def Y(y):
        return oy + y * s

    def fuente(tam, negrita=True):
        return ("Arial", max(8, round(tam * s)), "bold" if negrita else "normal")

    def rect(x, y, ancho, alto, **kw):
        lienzo.create_rectangle(X(x), Y(y), X(x + ancho), Y(y + alto), **kw)

    def ovalo(cx, cy, r, **kw):
        lienzo.create_oval(X(cx - r), Y(cy - r), X(cx + r), Y(cy + r), **kw)

    def linea(x1, y1, x2, y2, **kw):
        lienzo.create_line(X(x1), Y(y1), X(x2), Y(y2), **kw)

    def texto(x, y, txt, tam, color="#222222", negrita=True, ancla="w"):
        lienzo.create_text(
            X(x), Y(y), text=txt, font=fuente(tam, negrita),
            fill=color, anchor=ancla,
        )

    rojo = "#CC0000"
    azul = "#0055AA"
    # Tanque principal y tornillos
    rect(240, 140, 520, 320, outline="#222222", width=2)
    rect(
        255, 155, 490, 290, outline="#222222", width=1, dash=(4, 4),
    )
    for x_t in range(270, 721, 50):
        ovalo(x_t, 150, 2, fill="#222222", outline="#222222")
        ovalo(x_t, 450, 2, fill="#222222", outline="#222222")
    for y_t in range(180, 431, 50):
        ovalo(250, y_t, 2, fill="#222222", outline="#222222")
        ovalo(740, y_t, 2, fill="#222222", outline="#222222")
    # Radiadores
    rect(330, 60, 340, 80, outline="#222222", width=1)
    rect(330, 460, 340, 80, outline="#222222", width=1)
    for x_r in range(335, 666, 15):
        linea(x_r, 60, x_r, 140, fill="#222222", width=1)
        linea(x_r, 460, x_r, 540, fill="#222222", width=1)
    rect(160, 220, 80, 160, outline="#222222", width=1)
    rect(760, 220, 80, 160, outline="#222222", width=1)
    for y_r in range(225, 376, 15):
        linea(160, y_r, 240, y_r, fill="#222222", width=1)
        linea(760, y_r, 840, y_r, fill="#222222", width=1)
    for x_u, y_u in ((420, 140), (580, 140), (420, 440), (580, 440)):
        linea(x_u, y_u, x_u, y_u + 20, fill="#222222", width=2)
    linea(240, 260, 260, 260, fill="#222222", width=2)
    linea(240, 340, 260, 340, fill="#222222", width=2)
    linea(740, 260, 760, 260, fill="#222222", width=2)
    linea(740, 340, 760, 340, fill="#222222", width=2)
    # Bujes de alta tensión
    bujes_at = (
        ((420, "H1"), (580, "H2")) if monofasico
        else ((390, "H1"), (500, "H2"), (610, "H3"), (700, "H0"))
    )
    for cx, nombre in bujes_at:
        ovalo(cx, 210, 20, fill="#FFFFFF", outline="#333333", width=2)
        ovalo(cx, 210, 12, outline="#333333", width=1)
        ovalo(cx, 210, 5, fill="#333333", outline="#333333")
        linea(cx, 230, cx, 300, fill="#222222", width=1, dash=(3, 3))
        texto(cx, 260, nombre, 14, "#333333", ancla="center")
    # Bujes de baja tensión
    bujes_bt = (
        ((470, "X1"), (530, "X2")) if monofasico
        else ((420, "X1"), (475, "X2"), (530, "X3"), (585, "X0"))
    )
    for cx, nombre in bujes_bt:
        ovalo(cx, 360, 14, fill="#FFFFFF", outline="#333333", width=2)
        ovalo(cx, 360, 7, outline="#333333", width=1)
        ovalo(cx, 360, 3, fill="#333333", outline="#333333")
        texto(cx, 395, nombre, 14, "#333333", ancla="center")
    # Conexiones de prueba sobre los bujes (CN/CR/GN/GR).
    if roles:
        _marcar_conexiones_planta(
            lienzo, X, Y, s,
            [(n, c, 210, 20) for c, n in bujes_at] + [(n, c, 360, 14) for c, n in bujes_bt],
            roles,
        )
    # Accesorios
    for cx in (290, 710):
        ovalo(cx, 390, 12, outline="#222222", width=1)
        linea(cx - 12, 390, cx + 12, 390, fill="#222222", width=1)
        linea(cx, 378, cx, 402, fill="#222222", width=1)
    for x_a, y_a in ((270, 250), (714, 250), (270, 350), (714, 350)):
        rect(x_a, y_a, 16, 8, outline="#222222", width=1)
    # Etiquetas fuera del dibujo, sobre una franja blanca.
    etiquetas_lat = (
        (
            205, "ALTA TENSIÓN",
            "(H1, H2)" if monofasico else "(H0, H1, H2, H3)", rojo,
        ),
        (
            415, "BAJA TENSIÓN",
            "(X1, X2)" if monofasico else "(X1, X2, X3, X0)", azul,
        ),
    )
    for y_et, titulo_et, sub_et, color_et in etiquetas_lat:
        lienzo.create_rectangle(
            X(2), Y(y_et - 16), X(148), Y(y_et + 28),
            fill="#FFFFFF", outline="",
        )
        texto(8, y_et, titulo_et, 12, color_et)
        texto(8, y_et + 19, sub_et, 10, color_et, negrita=False)
    # Títulos y especificaciones
    texto(
        475, 610,
        "TRANSFORMADOR DE POTENCIA MONOFÁSICO" if monofasico
        else "TRANSFORMADOR DE POTENCIA TRIFÁSICO",
        20, "#222222", ancla="center",
    )
    texto(
        475, 635, "2 DEVANADOS (VISTA DE PLANTA)", 16, "#222222",
        ancla="center",
    )
    texto(
        475, 665,
        "Devanado Primario: Fases H1, H2" if monofasico
        else "Devanado Primario: Conexión Estrella (H1, H2, H3)",
        14, "#555555", negrita=False, ancla="center",
    )
    texto(
        475, 685,
        "Devanado Secundario: Fases X1, X2" if monofasico
        else "Devanado Secundario: Conexión Estrella con Neutro (X1, X2, X3, X0)",
        14, "#555555", negrita=False, ancla="center",
    )
    return lienzo


def _dibujar_diagrama_transformador_3d(padre, naranja="#FF8C00", roles=None):
    """Transformador de potencia trifásico 3 devanados (vista de planta)."""
    s = 0.62
    lienzo = tk.Canvas(
        padre, width=640, height=int(700 * s) + 14,
        bg="#FFFFFF", highlightthickness=1, highlightbackground="#E2E8F0",
    )
    lienzo.pack(fill="x", padx=15, pady=(10, 4))
    ox = (640 - 950 * s) / 2
    oy = 6

    def X(x):
        return ox + x * s

    def Y(y):
        return oy + y * s

    def fuente(tam, negrita=True):
        return ("Arial", max(8, round(tam * s)), "bold" if negrita else "normal")

    def rect(x, y, ancho, alto, **kw):
        lienzo.create_rectangle(X(x), Y(y), X(x + ancho), Y(y + alto), **kw)

    def ovalo(cx, cy, r, **kw):
        lienzo.create_oval(X(cx - r), Y(cy - r), X(cx + r), Y(cy + r), **kw)

    def linea(x1, y1, x2, y2, **kw):
        lienzo.create_line(X(x1), Y(y1), X(x2), Y(y2), **kw)

    def texto(x, y, txt, tam, color="#222222", negrita=True, ancla="w"):
        lienzo.create_text(
            X(x), Y(y), text=txt, font=fuente(tam, negrita),
            fill=color, anchor=ancla,
        )

    rojo = "#CC0000"
    azul = "#0055AA"
    # Tanque principal y tornillos
    rect(220, 140, 560, 320, outline="#222222", width=2)
    rect(235, 155, 530, 290, outline="#222222", width=1, dash=(4, 4))
    for x_t in range(250, 751, 50):
        ovalo(x_t, 150, 2, fill="#222222", outline="#222222")
        ovalo(x_t, 450, 2, fill="#222222", outline="#222222")
    for y_t in range(180, 431, 50):
        ovalo(230, y_t, 2, fill="#222222", outline="#222222")
        ovalo(770, y_t, 2, fill="#222222", outline="#222222")
    # Radiadores
    rect(320, 60, 360, 80, outline="#222222", width=1)
    rect(320, 460, 360, 80, outline="#222222", width=1)
    for x_r in range(325, 671, 15):
        linea(x_r, 60, x_r, 140, fill="#222222", width=1)
        linea(x_r, 460, x_r, 540, fill="#222222", width=1)
    rect(140, 220, 80, 160, outline="#222222", width=1)
    rect(780, 220, 80, 160, outline="#222222", width=1)
    for y_r in range(225, 376, 15):
        linea(140, y_r, 220, y_r, fill="#222222", width=1)
        linea(780, y_r, 860, y_r, fill="#222222", width=1)
    for x_u, y_u in ((420, 140), (580, 140), (420, 440), (580, 440)):
        linea(x_u, y_u, x_u, y_u + 20, fill="#222222", width=2)
    linea(220, 260, 240, 260, fill="#222222", width=2)
    linea(220, 340, 240, 340, fill="#222222", width=2)
    linea(760, 260, 780, 260, fill="#222222", width=2)
    linea(760, 340, 780, 340, fill="#222222", width=2)
    # Bujes de alta tensión
    for cx, nombre in ((380, "H1"), (500, "H2"), (620, "H3"), (740, "H0")):
        ovalo(cx, 200, 16, fill="#FFFFFF", outline="#333333", width=2)
        ovalo(cx, 200, 9, outline="#333333", width=1)
        ovalo(cx, 200, 4, fill="#333333", outline="#333333")
        texto(cx, 240, nombre, 12, "#333333", ancla="center")
    # Bujes del terciario
    for cx, nombre in ((320, "Y1"), (380, "Y2"), (440, "Y3")):
        ovalo(cx, 360, 14, fill="#FFFFFF", outline="#333333", width=2)
        ovalo(cx, 360, 7, outline="#333333", width=1)
        ovalo(cx, 360, 3, fill="#333333", outline="#333333")
        texto(cx, 395, nombre, 12, "#333333", ancla="center")
    # Bujes de baja tensión
    for cx, nombre in ((540, "X1"), (590, "X2"), (640, "X3"), (690, "X0")):
        ovalo(cx, 360, 12, fill="#FFFFFF", outline="#333333", width=2)
        ovalo(cx, 360, 6, outline="#333333", width=1)
        ovalo(cx, 360, 2, fill="#333333", outline="#333333")
        texto(cx, 390, nombre, 12, "#333333", ancla="center")
    # Conexiones de prueba sobre los bujes (CN/CR/GN/GR).
    if roles:
        _marcar_conexiones_planta(
            lienzo, X, Y, s,
            [("H1", 380, 200, 16), ("H2", 500, 200, 16), ("H3", 620, 200, 16), ("H0", 740, 200, 16),
             ("Y1", 320, 360, 14), ("Y2", 380, 360, 14), ("Y3", 440, 360, 14),
             ("X1", 540, 360, 12), ("X2", 590, 360, 12), ("X3", 640, 360, 12),
             ("X0", 690, 360, 12)],
            roles,
        )
    # Accesorios
    for cx in (270, 730):
        ovalo(cx, 400, 10, outline="#222222", width=1)
        linea(cx - 10, 400, cx + 10, 400, fill="#222222", width=1)
        linea(cx, 390, cx, 410, fill="#222222", width=1)
    for x_a in (250, 736):
        rect(x_a, 250, 14, 6, outline="#222222", width=1)
    # Etiquetas fuera del dibujo, sin líneas que crucen radiadores o tanque.
    etiquetas_lat = (
        (175, "ALTA TENSIÓN", "(H0, H1, H2, H3)", rojo),
        (375, "TERCIARIO", "(Y1, Y2, Y3)", naranja),
        (475, "BAJA TENSIÓN", "(X1, X2, X3, X0)", azul),
    )
    for y_et, titulo_et, sub_et, color_et in etiquetas_lat:
        lienzo.create_rectangle(
            X(2), Y(y_et - 16), X(138), Y(y_et + 28),
            fill="#FFFFFF", outline="",
        )
        texto(8, y_et, titulo_et, 12, color_et)
        texto(8, y_et + 19, sub_et, 10, color_et, negrita=False)
    # Títulos y especificaciones
    texto(
        475, 610, "TRANSFORMADOR DE POTENCIA TRIFÁSICO", 20, "#222222",
        ancla="center",
    )
    texto(
        475, 635, "3 DEVANADOS (VISTA DE PLANTA)", 16, "#222222",
        ancla="center",
    )
    texto(
        475, 665,
        "Primario: H1, H2, H3 | Terciario: Y1, Y2, Y3 | "
        "Secundario: X1, X2, X3, X0",
        14, "#555555", negrita=False, ancla="center",
    )
    return lienzo


def _dibujar_diagrama_autotransformador(padre, monofasico=False, naranja="#FF8C00"):
    """Autotransformador con terciario y neutro común (vista de planta)."""
    s = 0.62
    lienzo = tk.Canvas(
        padre, width=640, height=int(750 * s) + 14,
        bg="#FFFFFF", highlightthickness=1, highlightbackground="#E2E8F0",
    )
    lienzo.pack(fill="x", padx=15, pady=(10, 4))
    ox = (640 - 950 * s) / 2
    oy = 6

    def X(x):
        return ox + x * s

    def Y(y):
        return oy + y * s

    def fuente(tam, negrita=True):
        return ("Arial", max(8, round(tam * s)), "bold" if negrita else "normal")

    def rect(x, y, ancho, alto, **kw):
        lienzo.create_rectangle(X(x), Y(y), X(x + ancho), Y(y + alto), **kw)

    def ovalo(cx, cy, r, **kw):
        lienzo.create_oval(X(cx - r), Y(cy - r), X(cx + r), Y(cy + r), **kw)

    def linea(x1, y1, x2, y2, **kw):
        lienzo.create_line(X(x1), Y(y1), X(x2), Y(y2), **kw)

    def texto(x, y, txt, tam, color="#222222", negrita=True, ancla="w"):
        lienzo.create_text(
            X(x), Y(y), text=txt, font=fuente(tam, negrita),
            fill=color, anchor=ancla,
        )

    rojo = "#CC0000"
    azul = "#0055AA"
    gris = "#333333"
    # Tanque principal y tornillos
    rect(220, 140, 560, 340, outline="#222222", width=2)
    rect(235, 155, 530, 310, outline="#222222", width=1, dash=(4, 4))
    for x_t in range(250, 751, 50):
        ovalo(x_t, 150, 2, fill="#222222", outline="#222222")
        ovalo(x_t, 470, 2, fill="#222222", outline="#222222")
    for y_t in range(180, 431, 50):
        ovalo(230, y_t, 2, fill="#222222", outline="#222222")
        ovalo(770, y_t, 2, fill="#222222", outline="#222222")
    # Radiadores
    rect(320, 60, 360, 80, outline="#222222", width=1)
    rect(320, 480, 360, 80, outline="#222222", width=1)
    for x_r in range(325, 671, 15):
        linea(x_r, 60, x_r, 140, fill="#222222", width=1)
        linea(x_r, 480, x_r, 560, fill="#222222", width=1)
    rect(140, 220, 80, 160, outline="#222222", width=1)
    rect(780, 220, 80, 160, outline="#222222", width=1)
    for y_r in range(225, 376, 15):
        linea(140, y_r, 220, y_r, fill="#222222", width=1)
        linea(780, y_r, 860, y_r, fill="#222222", width=1)
    for x_u, y_u in ((420, 140), (580, 140), (420, 460), (580, 460)):
        linea(x_u, y_u, x_u, y_u + 20, fill="#222222", width=2)
    linea(220, 260, 240, 260, fill="#222222", width=2)
    linea(220, 340, 240, 340, fill="#222222", width=2)
    linea(760, 260, 780, 260, fill="#222222", width=2)
    linea(760, 340, 780, 340, fill="#222222", width=2)
    # Bujes del terciario (columna izquierda)
    if monofasico:
        bujes_y = ((320, 280, "Y1"), (320, 360, "Y2"))
        radio_y, radio_y2, radio_y3 = 14, 7, 3
    else:
        bujes_y = ((300, 250, "Y1"), (300, 330, "Y2"), (300, 410, "Y3"))
        radio_y, radio_y2, radio_y3 = 12, 6, 2
    for cx_y, cy_y, nombre in bujes_y:
        ovalo(cx_y, cy_y, radio_y, fill="#FFFFFF", outline=naranja, width=2)
        ovalo(cx_y, cy_y, radio_y2, outline=naranja, width=1)
        ovalo(cx_y, cy_y, radio_y3, fill=naranja, outline=naranja)
        texto(cx_y, cy_y + 35, nombre, 12, naranja, ancla="center")
    # Bujes primario (H) y secundario (X) por fase
    if monofasico:
        pares_hx = ((480, 250, 340, "H1", "X1"),)
    else:
        pares_hx = (
            (420, 220, 300, "H1", "X1"), (530, 220, 300, "H2", "X2"),
            (640, 220, 300, "H3", "X3"),
        )
    for cx, cy_h, cy_x, nom_h, nom_x in pares_hx:
        ovalo(cx, cy_h, 16, fill="#FFFFFF", outline=rojo, width=2)
        ovalo(cx, cy_h, 9, outline=rojo, width=1)
        ovalo(cx, cy_h, 4, fill=rojo, outline=rojo)
        texto(cx, cy_h + 35, nom_h, 12, rojo, ancla="center")
        ovalo(cx, cy_x, 14, fill="#FFFFFF", outline=azul, width=2)
        ovalo(cx, cy_x, 7, outline=azul, width=1)
        ovalo(cx, cy_x, 3, fill=azul, outline=azul)
        texto(cx, cy_x + 35, nom_x, 12, azul, ancla="center")
    # Borne común H0 / X0 (neutro)
    if monofasico:
        nx, ny, radio_n, radio_n2 = 640, 290, 20, 12
    else:
        nx, ny, radio_n, radio_n2 = 530, 400, 18, 11
    ovalo(nx, ny, radio_n, fill="#FFFFFF", outline=gris, width=2)
    ovalo(nx, ny, radio_n2, outline=gris, width=1)
    ovalo(nx, ny, 5, fill=gris, outline=gris)
    texto(nx - 32, ny + 2, "H0 / X0", 14, gris, ancla="e")
    texto(nx - 32, ny + 18, "(Neutro)", 11, gris, ancla="e")
    # Accesorios
    ovalo(730, 400, 10, outline="#222222", width=1)
    linea(720, 400, 740, 400, fill="#222222", width=1)
    linea(730, 390, 730, 410, fill="#222222", width=1)
    rect(736, 220 if monofasico else 250, 14, 6, outline="#222222", width=1)
    rect(250, 250, 14, 6, outline="#222222", width=1)
    # Etiquetas generales: se dibujan al final, sobre fondo blanco y a la
    # izquierda del tanque, para que el texto no se encime en el dibujo.
    etiquetas_lat = (
        (180, "PRIMARIO (H)", "(H1)" if monofasico else "(H1, H2, H3)", rojo),
        (
            240, "SECUNDARIO (X)", "(X1)" if monofasico else "(X1, X2, X3)",
            azul,
        ),
        (
            380, "TERCIARIO (Y)",
            "(Y1, Y2)" if monofasico else "(Y1, Y2, Y3 - Delta)", naranja,
        ),
        (500, "NEUTRO COMÚN", "(H0 / X0)", gris),
    )
    for y_et, titulo_et, sub_et, color_et in etiquetas_lat:
        lienzo.create_rectangle(
            X(2), Y(y_et - 16), X(138), Y(y_et + 28),
            fill="#FFFFFF", outline="",
        )
        texto(-8, y_et, titulo_et, 12, color_et)
        texto(-8, y_et + 20, sub_et, 10, color_et, negrita=False)
    # Títulos y especificaciones
    texto(
        475, 630,
        "AUTOTRANSFORMADOR DE POTENCIA MONOFÁSICO" if monofasico
        else "AUTOTRANSFORMADOR DE POTENCIA TRIFÁSICO",
        20, "#222222", ancla="center",
    )
    texto(
        475, 655, "CON TERCIARIO Y NEUTRO COMÚN (VISTA DE PLANTA)", 16,
        "#222222", ancla="center",
    )
    texto(
        475, 685,
        "Terciario (Izquierda): Y1, Y2" if monofasico
        else "Terciario (Izquierda): Y1, Y2, Y3 (Delta)",
        14, "#555555", negrita=False, ancla="center",
    )
    texto(
        475, 705,
        "Devanado Compartido (Centro): H1 - X1" if monofasico
        else "Devanados Compartidos: H1-X1 | H2-X2 | H3-X3",
        14, "#555555", negrita=False, ancla="center",
    )
    texto(
        475, 725,
        "Punto Neutro Común (Derecha): H0 / X0" if monofasico
        else "Punto Neutro Común (Centro): H0 / X0",
        14, "#555555", negrita=False, ancla="center",
    )
    return lienzo


def _dibujar_diagrama_reactor(padre):
    """Reactor de potencia monofásico (vista de planta): H1 y H0."""
    s = 0.62
    lienzo = tk.Canvas(
        padre, width=640, height=int(750 * s) + 14,
        bg="#FFFFFF", highlightthickness=1, highlightbackground="#E2E8F0",
    )
    lienzo.pack(fill="x", padx=15, pady=(10, 4))
    ox = (640 - 950 * s) / 2
    oy = 6

    def X(x):
        return ox + x * s

    def Y(y):
        return oy + y * s

    def fuente(tam, negrita=True):
        return ("Arial", max(8, round(tam * s)), "bold" if negrita else "normal")

    def rect(x, y, ancho, alto, **kw):
        lienzo.create_rectangle(X(x), Y(y), X(x + ancho), Y(y + alto), **kw)

    def ovalo(cx, cy, r, **kw):
        lienzo.create_oval(X(cx - r), Y(cy - r), X(cx + r), Y(cy + r), **kw)

    def linea(x1, y1, x2, y2, **kw):
        lienzo.create_line(X(x1), Y(y1), X(x2), Y(y2), **kw)

    def texto(x, y, txt, tam, color="#222222", negrita=True, ancla="w"):
        lienzo.create_text(
            X(x), Y(y), text=txt, font=fuente(tam, negrita),
            fill=color, anchor=ancla,
        )

    rojo = "#CC0000"
    gris = "#333333"
    # Tanque principal y tornillos
    rect(220, 140, 560, 320, outline="#222222", width=2)
    rect(235, 155, 530, 290, outline="#222222", width=1, dash=(4, 4))
    for x_t in range(250, 751, 50):
        ovalo(x_t, 150, 2, fill="#222222", outline="#222222")
        ovalo(x_t, 450, 2, fill="#222222", outline="#222222")
    for y_t in range(180, 431, 50):
        ovalo(230, y_t, 2, fill="#222222", outline="#222222")
        ovalo(770, y_t, 2, fill="#222222", outline="#222222")
    # Radiadores
    rect(320, 60, 360, 80, outline="#222222", width=1)
    rect(320, 460, 360, 80, outline="#222222", width=1)
    for x_r in range(325, 671, 15):
        linea(x_r, 60, x_r, 140, fill="#222222", width=1)
        linea(x_r, 460, x_r, 540, fill="#222222", width=1)
    rect(140, 220, 80, 160, outline="#222222", width=1)
    rect(780, 220, 80, 160, outline="#222222", width=1)
    for y_r in range(225, 376, 15):
        linea(140, y_r, 220, y_r, fill="#222222", width=1)
        linea(780, y_r, 860, y_r, fill="#222222", width=1)
    for x_u, y_u in ((420, 140), (580, 140), (420, 440), (580, 440)):
        linea(x_u, y_u, x_u, y_u + 20, fill="#222222", width=2)
    linea(220, 260, 240, 260, fill="#222222", width=2)
    linea(220, 340, 240, 340, fill="#222222", width=2)
    linea(760, 260, 780, 260, fill="#222222", width=2)
    linea(760, 340, 780, 340, fill="#222222", width=2)
    # Buje H1 (fase) y buje H0 (neutro)
    ovalo(420, 210, 18, fill="#FFFFFF", outline=rojo, width=2)
    ovalo(420, 210, 10, outline=rojo, width=1)
    ovalo(420, 210, 5, fill=rojo, outline=rojo)
    texto(420, 245, "H1", 14, rojo, ancla="center")
    ovalo(580, 210, 18, fill="#FFFFFF", outline=gris, width=2)
    ovalo(580, 210, 10, outline=gris, width=1)
    ovalo(580, 210, 5, fill=gris, outline=gris)
    texto(580, 245, "H0", 14, gris, ancla="center")
    # Accesorios
    for cx in (290, 710):
        ovalo(cx, 390, 12, outline="#222222", width=1)
        linea(cx - 12, 390, cx + 12, 390, fill="#222222", width=1)
        linea(cx, 378, cx, 402, fill="#222222", width=1)
    # Etiquetas fuera del dibujo, sobre fondo blanco.
    for y_et, titulo_et, sub_et, color_et in (
        (195, "ALTA TENSIÓN", "(Fase - H1)", rojo),
        (495, "NEUTRO", "(H0)", gris),
    ):
        lienzo.create_rectangle(
            X(2), Y(y_et - 16), X(138), Y(y_et + 28),
            fill="#FFFFFF", outline="",
        )
        texto(8, y_et, titulo_et, 12, color_et)
        texto(8, y_et + 19, sub_et, 10, color_et, negrita=False)
    # Títulos y especificaciones
    texto(
        475, 610, "REACTOR DE POTENCIA MONOFÁSICO", 20, "#222222",
        ancla="center",
    )
    texto(
        475, 635, "VISTA DE PLANTA", 16, "#222222", ancla="center",
    )
    texto(
        475, 665, "Conexión de Fase (Alta Tensión): H1",
        14, "#555555", negrita=False, ancla="center",
    )
    texto(
        475, 685, "Conexión de Neutro: H0",
        14, "#555555", negrita=False, ancla="center",
    )
    return lienzo


def _dibujar_diagrama_apartarrayos(padre):
    """Apartarrayos de óxido de zinc de 4 secciones (vista de alzado)."""
    s = 0.62
    lienzo = tk.Canvas(
        padre, width=640, height=int(850 * s) + 14,
        bg="#FFFFFF", highlightthickness=1, highlightbackground="#E2E8F0",
    )
    lienzo.pack(fill="x", padx=15, pady=(10, 4))
    ox = (640 - 950 * s) / 2
    oy = 6

    def X(x):
        return ox + x * s

    def Y(y):
        return oy + y * s

    def fuente(tam, negrita=True):
        return ("Arial", max(8, round(tam * s)), "bold" if negrita else "normal")

    def rect(x, y, ancho, alto, **kw):
        lienzo.create_rectangle(X(x), Y(y), X(x + ancho), Y(y + alto), **kw)

    def ovalo(cx, cy, r, **kw):
        lienzo.create_oval(X(cx - r), Y(cy - r), X(cx + r), Y(cy + r), **kw)

    def linea(x1, y1, x2, y2, **kw):
        lienzo.create_line(X(x1), Y(y1), X(x2), Y(y2), **kw)

    def texto(x, y, txt, tam, color="#222222", negrita=True, ancla="w"):
        lienzo.create_text(
            X(x), Y(y), text=txt, font=fuente(tam, negrita),
            fill=color, anchor=ancla,
        )

    rojo = "#CC0000"
    verde = "#005500"
    # Borne H1 y tapa superior
    linea(475, 40, 475, 90, fill=rojo, width=4)
    ovalo(475, 40, 8, fill=rojo, outline=rojo)
    texto(495, 50, "H1", 18, rojo)
    rect(425, 90, 100, 20, fill="#A0A0A0", outline="#333333", width=2)
    rect(435, 110, 80, 15, fill="#909090", outline="#333333", width=1)
    # Eje de porcelana y secciones
    rect(460, 125, 30, 480, fill="#F9F9F9", outline="#888888", width=1)
    secciones = (
        (130, 5, "#EEEEEE", "Sección 4", 200),
        (305, 5, "#F4F4F4", "Sección 3", 375),
        (480, 3, "#EEEEEE", "Sección 2", 525),
        (595, 2, "#F4F4F4", "Sección 1", 625),
    )
    for y0, cantidad, relleno, nombre, y_nombre in secciones:
        for i in range(cantidad):
            rect(
                405, y0 + 30 * i, 140, 20,
                fill=relleno, outline="#555555", width=1,
            )
        texto(560, y_nombre, nombre, 14, "#333333")
    for y_brida in (280, 455, 570):
        rect(435, y_brida, 80, 15, fill="#A0A0A0", outline="#333333", width=2)
    # Brida inferior y base metálica
    rect(425, 655, 100, 20, fill="#A0A0A0", outline="#333333", width=2)
    lienzo.create_polygon(
        X(380), Y(675), X(570), Y(675), X(590), Y(750), X(360), Y(750),
        fill="#B0B0B0", outline="#333333", width=2,
    )
    rect(370, 675, 210, 10, fill="#909090", outline="#333333", width=2)
    # Puesta a tierra en la base
    linea(380, 720, 300, 720, fill=verde, width=3)
    ovalo(380, 720, 6, fill=verde, outline=verde)
    texto(380, 700, "T", 16, verde, ancla="center")
    linea(260, 720, 300, 720, fill=verde, width=3)
    linea(268, 730, 292, 730, fill=verde, width=3)
    linea(276, 740, 284, 740, fill=verde, width=3)
    # Etiquetas fuera del dibujo, sin líneas que lo crucen.
    for y_et, titulo_et, sub_et, color_et in (
        (80, "ALTA TENSIÓN", "(Fase - H1)", rojo),
        (650, "PUESTA A TIERRA", "(Base Metálica - T)", verde),
    ):
        lienzo.create_rectangle(
            X(2), Y(y_et - 18), X(230), Y(y_et + 32),
            fill="#FFFFFF", outline="",
        )
        texto(8, y_et, titulo_et, 14, color_et)
        texto(8, y_et + 22, sub_et, 11, color_et, negrita=False)
    # Títulos
    texto(
        475, 800, "APARTARRAYOS DE ÓXIDO DE ZINC (ZnO) DE 4 SECCIONES",
        16, "#222222", ancla="center",
    )
    texto(
        475, 825, "VISTA DE ALZADO (LATERAL)", 14, "#222222",
        ancla="center",
    )
    return lienzo


def _dibujar_diagrama_tp(padre):
    """Diagrama del TP: H1 arriba, aislador, base con H2 y caja de bornes."""
    s = 0.8
    lienzo = tk.Canvas(
        padre, width=640, height=int(850 * s) + 14,
        bg="#FFFFFF", highlightthickness=1, highlightbackground="#E2E8F0",
    )
    lienzo.pack(fill="x", padx=15, pady=(10, 4))
    ox = (640 - 600 * s) / 2
    oy = 6

    def X(x):
        return ox + x * s

    def Y(y):
        return oy + y * s

    def fuente(tam, negrita=True):
        return ("Arial", max(8, round(tam * s)), "bold" if negrita else "normal")

    def rect(x, y, ancho, alto, **kw):
        lienzo.create_rectangle(X(x), Y(y), X(x + ancho), Y(y + alto), **kw)

    def ovalo(cx, cy, r, **kw):
        lienzo.create_oval(X(cx - r), Y(cy - r), X(cx + r), Y(cy + r), **kw)

    def linea(x1, y1, x2, y2, **kw):
        lienzo.create_line(X(x1), Y(y1), X(x2), Y(y2), **kw)

    def texto(x, y, txt, tam, color="#333333", negrita=True, ancla="w"):
        lienzo.create_text(
            X(x), Y(y), text=txt, font=fuente(tam, negrita),
            fill=color, anchor=ancla,
        )

    rojo = "#CC0000"
    azul = "#0055AA"
    # Textos aclaratorios
    texto(20, 80, "PRIMARIO", 22, rojo)
    texto(20, 105, "(Alta Tensión)", 15, rojo, negrita=False)
    linea(154, 90, 196, 90, fill=rojo, width=2, dash=(4, 4))
    texto(420, 680, "SECUNDARIO", 22, azul)
    texto(420, 705, "(Baja Tensión)", 15, azul, negrita=False)
    linea(400, 690, 416, 690, fill=azul, width=2, dash=(4, 4))
    # Borne H1 y cabeza superior
    linea(300, 10, 300, 40, fill=rojo, width=4)
    ovalo(300, 10, 7, fill=rojo, outline=rojo)
    texto(315, 8, "H1", 20, rojo)
    rect(200, 40, 200, 80, fill="#E0E0E0", outline="#333333", width=2)
    rect(220, 50, 160, 60, fill="#D0D0D0", outline="#333333", width=1)
    rect(230, 25, 140, 15, fill="#B0B0B0", outline="#333333", width=2)
    ovalo(300, 70, 12, fill="#FFFFFF", outline="#333333", width=2)
    ovalo(300, 70, 6, fill="#ADD8E6", outline="#ADD8E6")
    texto(412, 75, "Indicador nivel", 12, negrita=False)
    rect(230, 120, 140, 15, fill="#A0A0A0", outline="#333333", width=2)
    # Aislador con anillos
    rect(275, 135, 50, 510, fill="#F9F9F9", outline="#888888", width=1)
    for i in range(17):
        rect(
            235, 145 + 30 * i, 130, 18,
            fill="#EEEEEE", outline="#555555", width=1,
        )
    rect(230, 645, 140, 15, fill="#A0A0A0", outline="#333333", width=2)
    # Base / tanque
    lienzo.create_polygon(
        X(210), Y(660), X(390), Y(660), X(410), Y(780), X(190), Y(780),
        fill="#B0B0B0", outline="#333333", width=2,
    )
    rect(200, 660, 200, 10, fill="#909090", outline="#333333", width=2)
    rect(365, 700, 20, 30, fill="#909090", outline="#333333", width=1)
    ovalo(375, 715, 5, fill="#333333", outline="#333333")
    texto(412, 728, "Toma de", 11, negrita=False)
    texto(412, 743, "muestras", 11, negrita=False)
    # H2 con tierra
    linea(140, 760, 140, 790, fill=rojo, width=4)
    ovalo(140, 790, 7, fill=rojo, outline=rojo)
    texto(155, 772, "H2", 20, rojo)
    linea(120, 805, 160, 805, fill="green", width=4)
    linea(128, 813, 152, 813, fill="green", width=4)
    linea(136, 821, 144, 821, fill="green", width=4)
    # Caja de bornes X / Y
    texto(180, 720, "Caja de Bornes", 13, "#333333", ancla="e")
    rect(220, 680, 120, 80, fill="#DCDCDC", outline="#333333", width=2)
    for bx, nombre in ((245, "X1"), (280, "X2"), (315, "X3")):
        ovalo(bx, 705, 5, fill=azul, outline=azul)
        texto(bx - 10, 695, nombre, 14, azul)
    for bx, nombre in ((245, "Y1"), (280, "Y2"), (315, "Y3")):
        ovalo(bx, 740, 5, fill=azul, outline=azul)
        texto(bx - 10, 755, nombre, 14, azul)
    return lienzo


def _lineas_documento(widget, lineas=None):
    """Extrae textos y valores capturados de un formato para el documento."""
    if lineas is None:
        lineas = []
    try:
        hijos = widget.winfo_children()
    except tk.TclError:
        return lineas
    for hijo in hijos:
        clase = hijo.__class__.__name__
        es_captura = clase in ("CTkEntry", "CTkComboBox", "Entry", "Combobox")
        try:
            if clase in ("Label", "CTkLabel"):
                texto = str(hijo.cget("text") or "").strip()
                if texto and "█" not in texto and texto != "●":
                    lineas.append(texto)
            elif clase == "Canvas":
                lineas.append("[Diagrama]")
            elif es_captura:
                valor = hijo.get()
                if valor and str(valor).strip():
                    lineas.append(str(valor).strip())
        except (tk.TclError, AttributeError):
            pass
        if not es_captura:
            _lineas_documento(hijo, lineas)
    return lineas


def _imprimir_documento(titulo, lineas):
    """Genera el documento en HTML y abre el diálogo de impresión."""
    import html
    import tempfile
    import webbrowser

    filas = "\n".join(
        f"<p>{html.escape(str(linea))}</p>" for linea in lineas if str(linea).strip()
    )
    documento = f"""<!DOCTYPE html>
<html lang="es"><head><meta charset="utf-8">
<title>{html.escape(titulo)}</title>
<style>
body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 40px; color: #1E293B; }}
.encabezado {{ background: #1E293B; color: #00E5FF; padding: 16px 20px;
  font-family: Consolas, monospace; font-weight: bold; font-size: 20px; }}
h1 {{ font-size: 18px; border-bottom: 3px solid #1E293B; padding-bottom: 8px; }}
p {{ margin: 4px 0; font-size: 13px; white-space: pre-wrap; }}
</style></head><body>
<div class="encabezado">[ S.A.P.E. ]</div>
<h1>{html.escape(titulo)}</h1>
{filas}
<script>window.onload = () => setTimeout(() => window.print(), 400);</script>
</body></html>"""
    ruta = Path(tempfile.gettempdir()) / "documento_anexo_a.html"
    ruta.write_text(documento, encoding="utf-8")
    webbrowser.open(ruta.as_uri())


def _capturar_formato(contenido):
    """Imagen completa de un CTkScrollableFrame, tal como se ve en pantalla.

    Recorre el formato de arriba a abajo, captura cada tramo visible y los
    une en una sola imagen (incluye lo que queda fuera de la vista).
    """
    import time
    from PIL import Image, ImageGrab

    lienzo = contenido._parent_canvas
    ventana = contenido.winfo_toplevel()
    posicion = lienzo.yview()[0]
    ventana.lift()
    ventana.attributes("-topmost", True)
    try:
        ventana.focus_set()  # quita el cursor de texto de las capturas
        ventana.update()
        ancho = lienzo.winfo_width()
        alto_vista = lienzo.winfo_height()
        caja = lienzo.bbox("all")
        alto_total = max(alto_vista, (caja[3] - caja[1]) if caja else 0)
        alto_total = max(alto_total, contenido.winfo_height())
        imagen = Image.new("RGB", (ancho, alto_total), "#FFFFFF")
        desplazamiento = 0
        while True:
            lienzo.yview_moveto(desplazamiento / alto_total)
            ventana.update()
            time.sleep(0.12)
            ventana.update()
            real = int(round(lienzo.canvasy(0)))
            x, y = lienzo.winfo_rootx(), lienzo.winfo_rooty()
            tramo = ImageGrab.grab(
                bbox=(x, y, x + ancho, y + alto_vista), all_screens=True,
            )
            imagen.paste(tramo, (0, real))
            if real + alto_vista >= alto_total:
                break
            desplazamiento = real + alto_vista
        return imagen
    finally:
        ventana.attributes("-topmost", False)
        lienzo.yview_moveto(posicion)


def _imprimir_formato_carta(contenido, titulo):
    """Imprime el formato tal como aparece en pantalla, completo en una hoja carta."""
    import html
    import tempfile
    import webbrowser

    imagen = _capturar_formato(contenido)
    # Hoja carta 8.5 x 11 in con margen de 0.35 in: el formato se escala para
    # caber entero, sin cortarse ni pasar a una segunda hoja.
    margen = 0.35
    ancho_util, alto_util = 8.5 - 2 * margen, 11 - 2 * margen
    escala = min(ancho_util / imagen.width, alto_util / imagen.height)
    ancho_in, alto_in = imagen.width * escala, imagen.height * escala
    carpeta = Path(tempfile.gettempdir())
    ruta_img = carpeta / "formato_anexo_a.png"
    imagen.save(ruta_img)
    sello = datetime.now().strftime("%Y%m%d%H%M%S")
    documento = f"""<!DOCTYPE html>
<html lang="es"><head><meta charset="utf-8">
<title>{html.escape(titulo)}</title>
<style>
@page {{ size: 8.5in 11in; margin: 0; }}
html, body {{ margin: 0; padding: 0; background: #FFFFFF; }}
.hoja {{ width: 8.5in; height: 11in; box-sizing: border-box;
  padding: {margen}in; overflow: hidden; page-break-after: avoid;
  display: flex; justify-content: center; align-items: flex-start; }}
img {{ width: {ancho_in:.3f}in; height: {alto_in:.3f}in; display: block; }}
@media screen {{ body {{ background: #64748B; }}
  .hoja {{ background: #FFFFFF; margin: 16px auto;
    box-shadow: 0 2px 12px rgba(0,0,0,.4); }} }}
</style></head><body>
<div class="hoja"><img src="{ruta_img.name}?v={sello}" alt="{html.escape(titulo)}"></div>
<script>window.onload = () => setTimeout(() => window.print(), 400);</script>
</body></html>"""
    ruta = carpeta / "formato_anexo_a.html"
    ruta.write_text(documento, encoding="utf-8")
    webbrowser.open(ruta.as_uri())
    return ruta


def _visualizar_documento(padre, contenedor, titulo):
    """Vista previa del documento del Anexo A, con botón para imprimir."""
    lineas = _lineas_documento(contenedor)
    visor = tk.Toplevel(padre)
    visor.title(f"Vista previa — {titulo}")
    visor.configure(bg="#F4F6F8")
    visor.geometry("900x720")
    visor.minsize(720, 520)
    visor.transient(padre)
    barra = tk.Frame(visor, bg="#1E293B")
    barra.pack(fill="x")
    tk.Label(
        barra, text=f"📄 {titulo}", bg="#1E293B", fg="#FFFFFF",
        font=("Segoe UI", 13, "bold"),
    ).pack(side="left", padx=16, pady=12)
    ctk.CTkButton(
        barra, text="IMPRIMIR", fg_color="#10B981",
        hover_color="#059669", text_color="white",
        font=ctk.CTkFont(size=12, weight="bold"), width=120, height=34,
        command=lambda: _imprimir_documento(titulo, lineas),
    ).pack(side="right", padx=(8, 16), pady=8)
    ctk.CTkButton(
        barra, text="CERRAR", fg_color="#64748B",
        hover_color="#475569", text_color="white",
        font=ctk.CTkFont(size=12, weight="bold"), width=100, height=34,
        command=visor.destroy,
    ).pack(side="right", pady=8)
    caja = ctk.CTkTextbox(
        visor, font=ctk.CTkFont(family="Consolas", size=12), wrap="word",
    )
    caja.pack(fill="both", expand=True, padx=16, pady=16)
    caja.insert("1.0", "\n".join(str(linea) for linea in lineas))
    caja.configure(state="disabled")
    visor.focus_force()
    return visor


LOGO_SUTERM = (
    "███████╗██╗   ██╗████████╗███████╗██████╗ ███╗   ███╗\n"
    "██╔════╝██║   ██║╚══██╔══╝██╔════╝██╔══██╗████╗ ████║\n"
    "███████╗██║   ██║   ██║   █████╗  ██████╔╝██╔████╔██║\n"
    "╚════██║██║   ██║   ██║   ██╔══╝  ██╔══██╗██║╚██╔╝██║\n"
    "███████║╚██████╔╝   ██║   ███████╗██║  ██║██║ ╚═╝ ██║\n"
    "╚══════╝ ╚═════╝    ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝"
)

OPCIONES = [
    ("1.", "Resistencia de Aislamiento", "[ R.A.Ω ]"),
    ("2.", "Factor de Potencia al Aislamiento", "[ %F.P. ]"),
    ("3.", "Relación de Transformación", "[ T.T.R. ]"),
    ("4.", "Corriente de Excitación", "[ I.EXC ]"),
    ("5.", "Resistencia Óhmica de Devanados", "[ R.O.Ω ]"),
    ("6.", "Normativa y Procedimientos", "[ CFE-IEEE ]"),
    ("7.", "Historial de Análisis", "[ ]"),
    ("8.", "Desarrollador", "[ ]"),
    ("9.", "Salir", "[ ]"),
]

# Tablas TTR copiadas de SAPE_1 (ST-CT-007, figuras 5 a 9).
PRUEBAS_TTR_YD = (
    (1, "H1", "H0", "X1", "X2", "H – X φ1"),
    (2, "H2", "H0", "X2", "X3", "H – X φ2"),
    (3, "H3", "H0", "X3", "X1", "H – X φ3"),
)
PRUEBAS_TTR_DY = (
    (1, "H1", "H2", "X0", "X2", "H – X φ1"),
    (2, "H2", "H3", "X0", "X3", "H – X φ2"),
    (3, "H3", "H1", "X0", "X1", "H – X φ3"),
)
PRUEBAS_TTR_YY = (
    (1, "H1", "H0", "X1", "X0", "H – X φ1"),
    (2, "H2", "H0", "X2", "X0", "H – X φ2"),
    (3, "H3", "H0", "X3", "X0", "H – X φ3"),
)
PRUEBAS_TTR_DD = (
    (1, "H1", "H2", "X1", "X2", "H – X φ1"),
    (2, "H2", "H3", "X2", "X3", "H – X φ2"),
    (3, "H3", "H1", "X3", "X1", "H – X φ3"),
)
PRUEBAS_TTR_YYD = (
    (1, "H1", "H0", "X1", "X0", "H – X φ1"),
    (2, "H2", "H0", "X2", "X0", "H – X φ2"),
    (3, "H3", "H0", "X3", "X0", "H – X φ3"),
    (4, "H1", "H0", "Y1", "Y2", "H – Y φ1"),
    (5, "H2", "H0", "Y2", "Y3", "H – Y φ2"),
    (6, "H3", "H0", "Y3", "Y1", "H – Y φ3"),
    (7, "X1", "X0", "Y1", "Y2", "X – Y φ1"),
    (8, "X2", "X0", "Y2", "Y3", "X – Y φ2"),
    (9, "X3", "X0", "Y3", "Y1", "X – Y φ3"),
)
PRUEBAS_TTR_YYD_MONO = (
    (1, "H1", "H0", "X1", "X0", "H – X"),
    (2, "H1", "H0", "Y1", "Y2", "H – Y"),
    (3, "X1", "X0", "Y1", "Y2", "X – Y"),
)
PRUEBAS_TTR_AUTO_TRIF = (
    (1, "H1", "H0-X0", "X1", "H0-X0", "H – X φ1"),
    (2, "H2", "H0-X0", "X2", "H0-X0", "H – X φ2"),
    (3, "H3", "H0-X0", "X3", "H0-X0", "H – X φ3"),
    (4, "H1", "H0-X0", "Y1", "H0-X0", "H – Y φ1"),
    (5, "H2", "H0-X0", "Y2", "H0-X0", "H – Y φ2"),
    (6, "H3", "H0-X0", "Y3", "H0-X0", "H – Y φ3"),
    (7, "X1", "H0-X0", "Y1", "H0-X0", "X – Y φ1"),
    (8, "X2", "H0-X0", "Y2", "H0-X0", "X – Y φ2"),
    (9, "X3", "H0-X0", "Y3", "H0-X0", "X – Y φ3"),
)
PRUEBAS_TTR_AUTO_MONO = (
    (1, "H1", "H0-X0", "Y1", "H0-X0", "H – X"),
    (2, "H1", "H0-X0", "Y1", "Y2", "H – Y"),
    (3, "X1", "H0-X0", "Y1", "Y2", "X – Y"),
)
PRUEBAS_TTR_MONO_2D = (
    (1, "H1", "H0", "X1", "X2", "H – X"),
)
CONEXIONES_TTR_2D = (
    "Delta - Estrella",
    "Estrella - Delta",
    "Delta - Delta",
    "Estrella - Estrella",
)
CONEXIONES_TTR_AUTO = (
    "Estrella - Estrella",
    "Estrella - Estrella - Delta",
)
_NOTAS_TTR_2D = {
    "Estrella - Delta": "Figura 5 — Estrella-Delta (Y-D), 30°.",
    "Delta - Estrella": "Figura 6 — Delta-Estrella (D-Y), 30°.",
    "Estrella - Estrella": "Estrella-Estrella (Y-Y), desplazamiento 0°.",
    "Delta - Delta": "Delta-Delta (D-D), desplazamiento 0°.",
}
_FILAS_TTR_2D = {
    "Estrella - Delta": PRUEBAS_TTR_YD,
    "Delta - Estrella": PRUEBAS_TTR_DY,
    "Estrella - Estrella": PRUEBAS_TTR_YY,
    "Delta - Delta": PRUEBAS_TTR_DD,
}


def _opciones_conexion_ttr(equipo, configuracion):
    """Conexiones que SAPE_1 pregunta según el tipo de equipo."""
    if "2 Devanados" in equipo:
        return CONEXIONES_TTR_2D
    if "Autotransformadores" in equipo and configuracion != "Monofásico":
        return CONEXIONES_TTR_AUTO
    return ()


def _filas_ttr(equipo, configuracion, conexion):
    """Misma selección que obtener_tabla_conexiones_ttr de SAPE_1."""
    mono = configuracion == "Monofásico"
    if "Reactores" in equipo:
        return [], "ST-CT-007 no publica conexiones TTR para reactores."
    if "3 Devanados" in equipo and mono:
        return (
            PRUEBAS_TTR_YYD_MONO,
            "Tres devanados monofásico — Alta H1-H0, Baja X1-X0, Terciario Y1-Y2.",
        )
    if "3 Devanados" in equipo:
        return (
            PRUEBAS_TTR_YYD,
            "Figura 7 — Estrella-Estrella-Delta (Y-Y-D), 0° / 30°.",
        )
    if "Autotransformadores" in equipo and mono:
        return PRUEBAS_TTR_AUTO_MONO, "Figura 9 — Autotransformador monofásico."
    if "Autotransformadores" in equipo:
        if conexion == "Estrella - Estrella":
            nota = "Figura 8 — Autotransformador estrella-estrella (Y-Y)."
        else:
            nota = "Figura 8 — Autotransformador estrella-estrella-delta (Y-Y-D)."
        return PRUEBAS_TTR_AUTO_TRIF, nota
    if mono:
        return PRUEBAS_TTR_MONO_2D, "Anexo A — Monofásico de dos devanados."
    filas = _FILAS_TTR_2D.get(conexion, PRUEBAS_TTR_YD)
    nota = _NOTAS_TTR_2D.get(conexion, _NOTAS_TTR_2D["Estrella - Delta"])
    return filas, nota


# ---------- Captura y dictamen del paso 04 de TTR ----------
# Se construye con el procedimiento ST-CT-007: Tabla 1 (relación teórica
# según conexión) y ecuación 14 (%DIF). No existía una versión previa de
# este cálculo en SAPE2.

TABS_TTR = {
    "Sin carga [ 5 TAPs ]": (5, 3),
    "Bajo carga [ 21 TAPs ]": (21, 11),
    "Bajo carga [ 23 TAPs ]": (23, 12),
}


def _taps_ttr(tipo_cambiador):
    """Cuántos taps tiene el cambiador y cuál es el central (neutro)."""
    return TABS_TTR.get(tipo_cambiador, (5, 3))


def _mantener_nominal_ttr(tipo_cambiador):
    """Taps alrededor del central que conservan la RT nominal (sin paso de
    regulación): en el cambiador de 23 taps (nominal triple), central ±1."""
    return 1 if tipo_cambiador == "Bajo carga [ 23 TAPs ]" else 0


def _par_mide_ttr(mide):
    """Qué par de devanados mide la prueba, para elegir los kV de placa."""
    t = (mide or "").replace("–", "-").replace("—", "-")
    if "X" in t and "Y" in t and "H" not in t:
        return "X-Y"
    if "H" in t and "Y" in t and "X" not in t:
        return "H-Y"
    return "H-X"


def _leer_ttr(texto):
    bruto = re.sub(r"\s*(kv|v)\s*$", "", (texto or "").strip(), flags=re.IGNORECASE)
    bruto = bruto.strip().replace(",", ".")
    if not bruto:
        return None
    try:
        valor = float(bruto)
    except ValueError:
        return None
    return valor if math.isfinite(valor) else None


def _relacion_nominal_ttr(datos, prueba, equipo, conexion):
    """Relación teórica nominal (tap central), Tabla 1 del ST-CT-007: el
    factor √3 solo aplica entre devanados Delta-Estrella de un
    transformador de 2 devanados; en los demás casos se usa la relación
    directa de los kV de placa del par que mide la prueba."""
    par = _par_mide_ttr(prueba.get("mide") if prueba else "")
    campo_p = "voltaje_x" if par == "X-Y" else "voltaje_h"
    campo_s = "voltaje_x" if par == "H-X" else "voltaje_y"
    vp = _leer_ttr(datos[campo_p].get())
    vs = _leer_ttr(datos[campo_s].get())
    if vp is None or vs is None or vs == 0:
        return None, par
    factor = 1.0
    if par == "H-X" and "2 Devanados" in equipo:
        if conexion == "Delta - Estrella":
            factor = 1.73
        elif conexion == "Estrella - Delta":
            factor = 1 / 1.73
    return (vp / vs) * factor, par


def _relacion_teorica_tap_ttr(nominal, tap, centro, usar_regulacion, mantener=0):
    """Regulación CFE: 0.625 % por paso de tap, a partir del tap central.
    Los taps a `mantener` pasos del central conservan la RT nominal."""
    if nominal is None:
        return None
    if not usar_regulacion or abs(tap - centro) <= mantener:
        return nominal
    return nominal * (1 + 0.00625 * (tap - centro))


def _evaluar_ttr(rt, rm):
    """%DIF = 100 × (RT − RM) / RT (ecuación 14, ST-CT-007)."""
    if rt is None or rt == 0 or rm is None:
        return None
    dif = 100.0 * (rt - rm) / rt
    if abs(dif) <= 0.5:
        estado = "ACEPTADO"
        frase = (
            "La diferencia está dentro del 0.5 % que exige ST-CT-007 para "
            "la primera medición (puesta en servicio contra la relación "
            "teórica de placa)."
        )
    else:
        estado = "INVESTIGAR"
        frase = (
            "La diferencia rebasa el 0.5 %: revise el equipo de medición y "
            "las conexiones, la ejecución de la prueba, la calibración del "
            "TTR y, si nada de eso explica la diferencia, investigue "
            "espiras en corto en el transformador."
        )
    return {"dif": dif, "estado": estado, "frase": frase, "rt": rt, "rm": rm}


# Diagramas vectoriales de SAPE_1 (ST-CT-007, figuras 5 a 9).
# Cada grupo: tipo, pie de medición, pie de conexión y bornes.
_VECTORES_TTR = {
    "Y-D": ("Estrella-Delta Y-D", "Fig. 5", "30°", (
        ("estrella", "ALTA", "ESTRELLA", "H2", "H1", "H0", "H3"),
        ("delta", "BAJA", "DELTA", "X2", "X1", "X3"),
    )),
    "D-Y": ("Delta-Estrella D-Y", "Fig. 6", "30°", (
        ("delta", "ALTA", "DELTA", "H2", "H1", "H3"),
        ("estrella", "BAJA", "ESTRELLA", "X2", "X1", "X0", "X3"),
    )),
    "Y-Y": ("Estrella-Estrella Y-Y", "—", "0°", (
        ("estrella", "ALTA", "ESTRELLA", "H2", "H1", "H0", "H3"),
        ("estrella", "BAJA", "ESTRELLA", "X2", "X1", "X0", "X3"),
    )),
    "D-D": ("Delta-Delta D-D", "—", "0°", (
        ("delta", "ALTA", "DELTA", "H2", "H1", "H3"),
        ("delta", "BAJA", "DELTA", "X2", "X1", "X3"),
    )),
    "Y-Y-D": ("Estrella-Estrella-Delta Y-Y-D", "Fig. 7", "0° / 30°", (
        ("estrella", "ALTA", "ESTRELLA", "H2", "H1", "H0", "H3"),
        ("estrella", "BAJA", "ESTRELLA", "X2", "X1", "X0", "X3"),
        ("delta", "TERCIARIO", "DELTA", "Y2", "Y1", "Y3"),
    )),
    "Y-Y-D_MONO": (
        "Estrella-Estrella-Delta Y-Y-D monofásico",
        "Fig. 7",
        "H1-H0 / X1-X0 / Y1-Y2",
        (
            ("vertical", "ALTA", "ESTRELLA", "H1", "H0"),
            ("vertical", "BAJA", "ESTRELLA", "X1", "X0"),
            ("horizontal", "TERCIARIO", "DELTA", "Y1", "Y2"),
        ),
    ),
    "AUTO_YY": ("Autotransformador Y-Y", "Fig. 8", "0°", (
        ("estrella", "ALTA-BAJA", "ESTRELLA-ESTRELLA", "H2·X2", "H1·X1", "H0·X0", "H3·X3"),
    )),
    "AUTO_YYD": ("Autotransformador Y-Y-D", "Fig. 8", "0° / 30°", (
        ("estrella", "ALTA-BAJA", "ESTRELLA-ESTRELLA", "H2·X2", "H1·X1", "H0·X0", "H3·X3"),
        ("delta", "TERCIARIO", "DELTA", "Y2", "Y1", "Y3"),
    )),
    "AUTO_MONO": ("Autotransformador monofásico", "Fig. 9", "Ie por par H·X·Y", (
        ("estrella", "ALTA-BAJA", "ESTRELLA-ESTRELLA", "H1", "X1", "H0/X0", ""),
        ("vertical", "TERCIARIO", "DELTA", "Y2", "Y1"),
    )),
    "MONO_2D": ("Monofásico 2 devanados", "Anexo A", "Ie H–X", (
        ("vertical", "ALTA", "ESTRELLA", "H1", "H0"),
        ("vertical", "BAJA", "DELTA", "X1", "X2"),
    )),
}
_TTR_MAGENTA_BORNE = TTR_MORADO_NEON
_TTR_ROSA_PIE = "#DB2777"


def _clave_vector_ttr(equipo, configuracion, conexion):
    """Misma clave que _ttr_clave_diagrama_vectorial de SAPE_1."""
    mono = configuracion == "Monofásico"
    if "Reactores" in equipo:
        return None
    if "Autotransformadores" in equipo:
        if mono:
            return "AUTO_MONO"
        if "Delta" in conexion:
            return "AUTO_YYD"
        return "AUTO_YY"
    if "3 Devanados" in equipo:
        return "Y-Y-D_MONO" if mono else "Y-Y-D"
    if mono:
        return "MONO_2D"            
    return {
        "Estrella - Delta": "Y-D",
        "Delta - Estrella": "D-Y",
        "Estrella - Estrella": "Y-Y",
        "Delta - Delta": "D-D",
    }.get(conexion, "Y-D")


def _expandir_campo_ttr(valor):
    if not valor or valor == "—":
        return []
    tokens = []
    for parte in re.split(r"[,;]+", str(valor).strip()):
        parte = parte.strip()
        if not parte:
            continue
        tokens.append(parte)
        if "H0-X0" in parte or "H0/X0" in parte:
            tokens.extend(["H0", "X0"])
        tokens.extend(m.upper() for m in re.findall(r"[HXY]\d+", parte, flags=re.I))
    vistos = []
    for tok in tokens:
        if tok not in vistos:
            vistos.append(tok)
    return vistos


def _tokens_borne_ttr(texto):
    partes = [m.upper() for m in re.findall(r"[HXY]\d+", texto or "", flags=re.I)]
    if "H0" in partes and "X0" in partes:
        partes.extend(["H0-X0", "H0/X0", "H0·X0"])
    return partes


def _estilos_vector_ttr(prueba, modo):
    """Medición: bornes en naranja. Conexiones: CN/GN negro y CR/GR carmesí."""
    colores = {}
    roles = {}
    if not prueba:
        return colores, roles
    if modo == "mide":
        for campo in ("cn", "cr", "gn", "gr"):
            for tok in _expandir_campo_ttr(prueba.get(campo)):
                colores[tok] = "#F76707"
        if any(t in colores for t in ("H0", "X0", "H0-X0", "H0/X0", "H0·X0")):
            for alias in ("H0-X0", "H0/X0", "H0·X0"):
                colores.setdefault(alias, "#F76707")
        return colores, roles
    for campo, rol, color in (
        ("cn", "CN", "#000000"),
        ("gn", "GN", "#000000"),
        ("cr", "CR", "#FF0000"),
        ("gr", "GR", "#FF0000"),
    ):
        for tok in _expandir_campo_ttr(prueba.get(campo)):
            colores[tok] = color
            lista = roles.setdefault(tok, [])
            if rol not in lista:
                lista.append(rol)
    union = []
    for tok in ("H0-X0", "H0/X0", "H0·X0", "H0", "X0"):
        for rol in roles.get(tok, []):
            if rol not in union:
                union.append(rol)
    if union:
        for alias in ("H0-X0", "H0/X0", "H0·X0"):
            roles[alias] = list(union)
            colores.setdefault(alias, colores.get("H0") or colores.get("X0"))
    return colores, roles


def _color_etiqueta_ttr(texto, colores, libre=None):
    if libre is None:
        libre = _TTR_MAGENTA_BORNE
    if not colores:
        return libre
    hallados = []
    if texto in colores:
        hallados.append(colores[texto])
    for tok in _tokens_borne_ttr(texto):
        if tok in colores:
            hallados.append(colores[tok])
    for tinta in (
        "#FF0000", "#DC143C", "#000000", "#111111",
        TTR_ROSA_MEDICION, "#F76707",
    ):
        if tinta in hallados:
            return tinta
    return libre


def _letra_fase_ttr(texto, delta=False):
    """Estrella: 1 → A, 2 → B, 3 → C. Delta: 1 → C, 2 → A, 3 → B."""
    numeros = re.findall(r"[HXY](\d)", texto or "", flags=re.I)
    if not numeros:
        return ""
    tabla = {"1": "C", "2": "A", "3": "B"} if delta else {"1": "A", "2": "B", "3": "C"}
    return tabla.get(numeros[-1], "")


def _fase_a_mitad_ttr(
    lienzo, x1, y1, x2, y2, borne, lado=1, delta=False, parpadeo=False,
):
    """∅A/∅B/∅C en la mitad de la línea, separado del trazo."""
    letra = _letra_fase_ttr(borne, delta)
    if not letra:
        return
    dx = x2 - x1
    dy = y2 - y1
    largo = math.hypot(dx, dy) or 1
    marca = lienzo.create_text(
        (x1 + x2) / 2 + (-dy / largo) * 16 * lado,
        (y1 + y2) / 2 + (dx / largo) * 16 * lado,
        text=f"∅{letra}",
        fill=TTR_ROSA_MEDICION if parpadeo else TTR_LILA_FASE,
        font=("Segoe UI", 9, "bold"),
    )
    if parpadeo:
        lienzo.addtag_withtag("parpadeo_fase", marca)


def _roles_etiqueta_ttr(texto, roles):
    if not roles:
        return ""
    unidos = []
    for tok in (texto, *_tokens_borne_ttr(texto)):
        for rol in roles.get(tok, []):
            if rol not in unidos:
                unidos.append(rol)
    return "/".join(rol for rol in ("CN", "CR", "GN", "GR") if rol in unidos)


def _color_rol_ttr(rol):
    """CN y GN en negro; CR y GR en rojo intenso."""
    if "CR" in rol or "GR" in rol:
        return "#FF0000"
    return "#000000"


_SECUENCIA_CONEXIONES_TTR = ("linea", "roles")


def _registrar_seq_ttr(lienzo, item, grupo, color):
    """Marca un item del esquema de conexiones para la secuencia de parpadeo.

    Las etiquetas de rol (CN, CR, GN, GR) van juntas en el grupo "roles".
    """
    if grupo != "linea":
        grupo = "roles"
    lienzo.addtag_withtag(f"seq_{grupo}", item)
    lienzo.addtag_withtag("seq_todo", item)
    if not hasattr(lienzo, "_seq_color"):
        lienzo._seq_color = {}
    lienzo._seq_color.setdefault((item, grupo), color)


def _poner_borne_ttr(
    lienzo, x, y, texto, colores, roles, anchor="center", rol_arriba=False,
    rol_derecha=False,
):
    libre = getattr(lienzo, "_tono_libre_ttr", None)
    colores_borne = getattr(lienzo, "_colores_borne_ttr", None)
    if colores_borne is None:
        colores_borne = colores
    color = _color_etiqueta_ttr(texto, colores_borne, libre)
    marca = lienzo.create_text(
        x, y, text=texto, fill=color, anchor=anchor,
        font=("Consolas", 11, "bold"),
    )
    # El borne se queda fijo en el color de medición; no parpadea (solo la
    # bolita y la fase).
    x1, y1, x2, y2 = lienzo.bbox(marca)
    fondo = lienzo.create_rectangle(x1 - 3, y1 - 1, x2 + 3, y2 + 1, fill="#FFFFFF", outline="")
    lienzo.tag_raise(marca)
    rol = _roles_etiqueta_ttr(texto, roles)
    if not rol:
        return
    color_rol = _color_rol_ttr(rol)
    if rol_derecha:
        posicion = dict(x=x2 + 8, y=(y1 + y2) / 2, anchor="w")
    else:
        ry = (y1 - 11) if rol_arriba else (y2 + 11)
        posicion = dict(x=(x1 + x2) / 2, y=ry, anchor="center")
    tamano_rol = 10 if ("CR" in rol or "GR" in rol) else 9
    etiqueta = lienzo.create_text(
        posicion["x"], posicion["y"], text=rol, fill=color_rol,
        anchor=posicion["anchor"], font=("Segoe UI", tamano_rol, "bold"),
    )
    for grupo in rol.split("/"):
        _registrar_seq_ttr(lienzo, etiqueta, grupo, _color_rol_ttr(grupo))
    rx1, ry1, rx2, ry2 = lienzo.bbox(etiqueta)
    lienzo.create_rectangle(rx1 - 2, ry1 - 1, rx2 + 2, ry2 + 1, fill="#FFFFFF", outline="")
    lienzo.tag_raise(etiqueta)
    lienzo.tag_raise(marca)
    lienzo.tag_lower(fondo)


_COLOR_LINEA_TTR = "#7F00B2"  # líneas del diagrama vectorial.


def _linea_ttr(
    lienzo, x1, y1, x2, y2, nodos,
    mide_a=False, mide_b=False, color_a=None, color_b=None,
    punto_a=None, punto_b=None,
):
    """Morado fijo: no parpadea. Solo la línea entre el punto negro y el
    rojo va partida. Lo que parpadea es el borne/punto en medición."""
    base = _COLOR_LINEA_TTR
    ca = color_a or base
    cb = color_b or base

    def trazo(ax, ay, bx, by, color, parpadeo=False):
        linea = lienzo.create_line(
            ax, ay, bx, by, fill=color, width=6,
            capstyle="projecting", joinstyle="miter",
        )
        if parpadeo:
            lienzo.addtag_withtag("parpadeo", linea)
        if color in ("#000000", "#FF0000"):
            _registrar_seq_ttr(lienzo, linea, "linea", color)

    if mide_a and mide_b:
        trazo(x1, y1, x2, y2, TTR_ROSA_MEDICION, parpadeo=True)
        ca = cb = TTR_ROSA_MEDICION
    elif {ca, cb} <= {"#000000", "#111111", "#FF0000"} and ca != cb:
        mx = (x1 + x2) / 2
        my = (y1 + y2) / 2
        trazo(x1, y1, mx, my, ca)
        trazo(mx, my, x2, y2, cb)
    else:
        trazo(x1, y1, x2, y2, base)
    nodos.append((x1, y1, mide_a, punto_a or ca))
    nodos.append((x2, y2, mide_b, punto_b or cb))


def _puntos_ttr(lienzo, nodos):
    radio = 4.5
    rango = {TTR_ROSA_MEDICION: 4, "#FF0000": 3, "#000000": 2, "#111111": 2}
    grupos = {}
    for x, y, mide, color in nodos:
        clave = (round(x, 1), round(y, 1))
        previo = grupos.get(clave)
        if previo is None:
            grupos[clave] = (x, y, mide, color)
            continue
        _, _, mide_p, color_p = previo
        if rango.get(color, 1) >= rango.get(color_p, 1):
            color_p = color
        grupos[clave] = (x, y, mide_p or mide, color_p)
    for x, y, mide, color in grupos.values():
        punto = lienzo.create_oval(
            x - radio, y - radio, x + radio, y + radio,
            fill=color, outline=color,
        )
        if color == TTR_ROSA_MEDICION:
            lienzo.addtag_withtag("parpadeo", punto)
        elif color in ("#000000", "#FF0000"):
            _registrar_seq_ttr(lienzo, punto, "linea", color)


def _pie_grupo_ttr(lienzo, cx, texto):
    lienzo.create_text(
        cx, 262, text=texto, fill=_TTR_ROSA_PIE,
        font=("Segoe UI", 9, "bold"),
    )


def _medida_vector_ttr(n):
    """Centros juntos y a la izquierda, para dejar la lista a la derecha."""
    paso = 200 if n >= 3 else 230
    margen = 190 if n == 1 else 140
    ancho = margen + max(0, n - 1) * paso + 165
    return margen, paso, ancho


def _lados_mide_ttr(mide):
    """Qué devanados compara la columna MIDE."""
    base = (mide or "").split("φ")[0].replace(" ", "").replace("–", "-").replace("—", "-")
    if "H" in base and "Y" in base and "X" not in base:
        return "alta (H) contra el terciario (Y)"
    if "X" in base and "Y" in base and "H" not in base:
        return "baja (X) contra el terciario (Y)"
    if "H" in base and "X" in base:
        return "alta (H) contra baja (X)"
    return "los devanados de esta prueba"


def _formula_rt_ttr(clave):
    """Tabla 1 ST-CT-007 §3.5."""
    return {
        "Y-D": "(VP / VS) / √3",
        "D-Y": "√3 × (VP / VS)",
        "Y-Y-D": "VP / VS, según el par",
        "AUTO_YYD": "VP / VS, según el par",
    }.get(clave, "VP / VS")


def _desplazamiento_par_ttr(clave, mide, desplaz):
    texto = (mide or "").replace("–", "-").replace("—", "-")
    if clave in ("Y-Y-D", "AUTO_YYD", "Y-Y-D_MONO"):
        if "H - Y" in texto or "X - Y" in texto:
            return "30° en el par con el terciario en delta"
        if "H - X" in texto:
            return "0° entre alta y baja"
    return desplaz or ""


def _fases_leyenda_ttr(clave):
    """∅A, ∅B y ∅C con el borne de cada devanado, como en el fasorial."""
    ficha = _VECTORES_TTR.get(clave) if clave else None
    if not ficha:
        return []
    por_fase = {"A": [], "B": [], "C": []}
    for grupo in ficha[3]:
        devanado = str(grupo[1]).lower()
        for borne in grupo[3:]:
            letra = _letra_fase_ttr(borne, grupo[0] == "delta")
            if not letra:
                continue
            texto = f"{borne} {devanado}"
            if texto not in por_fase[letra]:
                por_fase[letra].append(texto)
    filas = []
    for letra in ("A", "B", "C"):
        if not por_fase[letra]:
            continue
        filas.append((
            f"∅{letra}",
            ", ".join(por_fase[letra]),
            TTR_LILA_FASE,
        ))
    return filas


def _leyenda_fasorial_ttr(prueba, clave=None, medicion="Directa", polaridad="Sustractiva"):
    """Datos de ST-CT-007 para la prueba elegida, no la lista de bornes."""
    if not prueba:
        return []
    ficha = _VECTORES_TTR.get(clave) if clave else None
    nombre = ficha[0] if ficha else ""
    figura = ficha[1] if ficha else ""
    desplaz = _desplazamiento_par_ttr(
        clave, prueba.get("mide"), ficha[2] if ficha else "",
    )
    mide = str(prueba.get("mide") or "").strip()
    cn = str(prueba.get("cn") or "").strip()
    cr = str(prueba.get("cr") or "").strip()
    gn = str(prueba.get("gn") or "").strip()
    gr = str(prueba.get("gr") or "").strip()
    filas = []
    if mide and mide not in ("—", "-----", "---"):
        fase = ""
        if "φ" in mide:
            fase = f", fase {mide.split('φ')[-1].strip()}"
        filas.append((
            "MIDE",
            f"{mide}: relación de {_lados_mide_ttr(mide)}{fase}.",
            TTR_ROSA_MEDICION,
        ))
    filas.extend(_fases_leyenda_ttr(clave))
    if nombre or desplaz:
        dato = nombre
        if desplaz:
            dato = f"{dato}, desplazamiento {desplaz}" if dato else f"Desplazamiento {desplaz}"
        if figura and figura != "—":
            dato = f"{dato}. {figura} ST-CT-007"
        filas.append(("DESPL.", dato + ".", TTR_MORADO))
    filas.append((
        "RT",
        f"{_formula_rt_ttr(clave)}. Tabla 1 §3.5. VP y VS son de línea.",
        TTR_MORADO,
    ))
    if medicion == "Inversa":
        pinzas = (
            f"Inversa: GN ({gn}) y GR ({gr}) inyectan; "
            f"CN ({cn}) y CR ({cr}) leen."
        )
    elif medicion == "Ambas":
        pinzas = (
            f"Directa: CN/CR inyectan y GN/GR leen. "
            f"Inversa: al revés. Un negro y un rojo en cada lado."
        )
    else:
        pinzas = (
            f"Directa: CN ({cn}) y CR ({cr}) inyectan; "
            f"GN ({gn}) y GR ({gr}) leen."
        )
    filas.append(("PINZAS", pinzas, "#000000"))
    if polaridad == "Aditiva":
        pol = "Aditiva: H1 con X2. Usual en transmisión (230/69 kV)."
    else:
        pol = "Sustractiva: H1 con X1. Usual en distribución."
    filas.append(("POLAR.", pol, TTR_MORADO))
    filas.append((
        "%DIF",
        "Primera lectura ≤ 0.5 % contra placa. Luego, variación ≤ 0.05 %.",
        TTR_MORADO,
    ))
    return filas


def _leyenda_conexiones_ttr(prueba):
    """CN, CR, GN y GR con el borne de la prueba, como en RA."""
    if not prueba:
        return []
    textos = (
        ("cn", "CN", "Terminal secundaria (negra)", "#000000"),
        ("cr", "CR", "Terminal secundaria (roja)", "#FF0000"),
        ("gn", "GN", "Excitación (negra)", "#000000"),
        ("gr", "GR", "Excitación (roja)", "#FF0000"),
    )
    filas = []
    for campo, codigo, desc, color in textos:
        valor = str(prueba.get(campo) or "").strip()
        if not valor or valor in ("—", "-----", "---"):
            continue
        filas.append((codigo, f"{desc}: {valor}", color))
    return filas


_AZUL_GUIA_TTR = "#0369A1"


def _letra_devanado_ttr(*bornes):
    """H, X o Y del lado, sin tomar el neutro común H0-X0 como devanado."""
    for borne in bornes:
        limpio = (
            str(borne or "").upper()
            .replace("H0-X0", " ")
            .replace("H0/X0", " ")
            .replace("H0·X0", " ")
        )
        hallado = re.search(r"[HXY]", limpio)
        if hallado:
            return hallado.group(0)
    for borne in bornes:
        hallado = re.search(r"[HXY]", str(borne or "").upper())
        if hallado:
            return hallado.group(0)
    return ""


def _lado_devanado_ttr(letra):
    return {
        "H": "lado AT (H)",     
        "X": "lado BT (X)",
        "Y": "lado Terciario (Y)",
    }.get(letra, "lado —")


def _texto_guia(padre, texto, color="#334155", negrita=False, arriba=0):
    tk.Label(
        padre, text=texto, bg="#FFFFFF", fg=color, anchor="w", justify="left",
        font=("Segoe UI", 11, "bold" if negrita else "normal"),
        wraplength=300,
    ).pack(anchor="w", pady=(arriba, 0))


def _pintar_guia_fasorial_ttr(marco, prueba, medicion, polaridad):
    """Solo lo que cambia la lectura: modo, quién excita y polaridad."""
    for hijo in marco.winfo_children():
        hijo.destroy()
    titulo = {
        "Inversa": "MEDICIÓN INVERSA",
        "Ambas": "MEDICIÓN DIRECTA E INVERSA",
    }.get(medicion, "MEDICIÓN DIRECTA")
    _texto_guia(marco, titulo, TTR_ROSA_MEDICION, True)
    if prueba:
        pares = []
        if medicion != "Inversa":
            pares.append(((prueba.get("cn"), prueba.get("cr")),
                          (prueba.get("gn"), prueba.get("gr"))))
        if medicion != "Directa":
            pares.append(((prueba.get("gn"), prueba.get("gr")),
                          (prueba.get("cn"), prueba.get("cr"))))
        for exc, lec in pares:
            letra_exc = _letra_devanado_ttr(*exc)
            letra_lec = _letra_devanado_ttr(*lec)
            if letra_exc and letra_lec:
                _texto_guia(
                    marco, f"Excita {letra_exc}  →  lee {letra_lec}",
                    _AZUL_GUIA_TTR,
                )
    if polaridad == "Aditiva":
        pol = "Polaridad aditiva (H1–X2)"
    else:
        pol = "Polaridad sustractiva (H1–X1)"
    _texto_guia(marco, pol, _AZUL_GUIA_TTR, True, 8)


def _pintar_guia_conexiones_ttr(marco, prueba, clave, medicion):
    """Qué pinza va a qué borne: una línea por pinza, excitación y lectura."""
    for hijo in marco.winfo_children():
        hijo.destroy()
    if not prueba:
        return
    if medicion == "Inversa":
        exc = (("GN", "negro", prueba.get("gn"), "#000000"),
               ("GR", "rojo", prueba.get("gr"), "#FF0000"))
        lec = (("CN", "negro", prueba.get("cn"), "#000000"),
               ("CR", "rojo", prueba.get("cr"), "#FF0000"))
        letra_exc = _letra_devanado_ttr(prueba.get("gn"), prueba.get("gr"))
        letra_lec = _letra_devanado_ttr(prueba.get("cn"), prueba.get("cr"))
    else:
        exc = (("CN", "negro", prueba.get("cn"), "#000000"),
               ("CR", "rojo", prueba.get("cr"), "#FF0000"))
        lec = (("GN", "negro", prueba.get("gn"), "#000000"),
               ("GR", "rojo", prueba.get("gr"), "#FF0000"))
        letra_exc = _letra_devanado_ttr(prueba.get("cn"), prueba.get("cr"))
        letra_lec = _letra_devanado_ttr(prueba.get("gn"), prueba.get("gr"))
    for titulo, pares, letra in (
        ("Excitación", exc, letra_exc),
        ("Lectura", lec, letra_lec),
    ):
        _texto_guia(
            marco, f"{titulo} — {_lado_devanado_ttr(letra)}",
            _AZUL_GUIA_TTR, True, 6,
        )
        for pinza, color, borne, tinta in pares:
            _texto_guia(marco, f"{pinza} ({color}) → {borne or '—'}", tinta)


def _dibujar_vector_ttr(lienzo, clave, prueba, modo, solo=None, anexo=False):
    """Dibuja el vector de medición o el de conexiones. Con `solo`, solo el
    devanado con ese índice (para un diagrama por devanado)."""
    lienzo.delete("all")
    lienzo._seq_color = {}
    ficha = _VECTORES_TTR.get(clave)
    if not ficha:
        return
    grupos = ficha[3] if solo is None else (ficha[3][solo],)
    colores, roles = _estilos_vector_ttr(prueba, modo)
    if anexo:
        # Anexo A: bornes en morado oscuro y líneas moradas, sin rosa.
        colores = {}
    if modo != "cables":
        roles = {}
        for tok, tinta in list(colores.items()):
            if tinta == "#F76707":
                colores[tok] = TTR_ROSA_MEDICION
    lienzo._tono_libre_ttr = "#6D28D9" if anexo else TTR_MORADO_NEON
    lienzo._colores_borne_ttr = None
    n = len(grupos)
    margen, paso, _ancho = _medida_vector_ttr(n)
    nodos = []

    def mide(texto):
        return (
            modo == "mide"
            and _color_etiqueta_ttr(texto, colores) == TTR_ROSA_MEDICION
        )

    def color_borne(texto):
        if modo != "cables":
            return _COLOR_LINEA_TTR
        return color_punto(texto) or _COLOR_LINEA_TTR

    def color_punto(texto):
        if modo != "cables":
            return None
        tinta = _color_etiqueta_ttr(texto, colores, "")
        if tinta in ("#000000", "#FF0000"):
            return tinta
        return None

    def linea(x1, y1, x2, y2, borne_a, borne_b):
        _linea_ttr(
            lienzo, x1, y1, x2, y2, nodos,
            mide(borne_a), mide(borne_b),
            color_borne(borne_a), color_borne(borne_b),
            color_punto(borne_a), color_punto(borne_b),
        )

    for i, grupo in enumerate(grupos):
        cx = margen + i * paso
        kind = grupo[0]
        pie = grupo[2] if anexo else (grupo[1] if modo == "mide" else grupo[2])
        bornes = grupo[3:]
        brazo = 108 if n == 1 else 58
        if kind == "estrella":
            arriba, izq, centro, der = bornes
            largo = 78 if n > 1 else 96
            cy = 128
            x_izq = cx - largo
            y_izq = cy
            x_arr = cx + largo * 0.5
            y_arr = cy - largo * 0.866
            x_der = cx + largo * 0.5
            y_der = cy + largo * 0.866
            linea(x_izq, y_izq, cx, cy, izq, centro)
            linea(x_arr, y_arr, cx, cy, arriba, centro)
            linea(x_der, y_der, cx, cy, der, centro)
            _poner_borne_ttr(
                lienzo, x_izq - 12, y_izq, izq, colores, roles, "e",
            )
            _poner_borne_ttr(
                lienzo, x_arr + 8, y_arr - 6, arriba, colores, roles, "sw",
            )
            if der:
                _poner_borne_ttr(
                    lienzo, x_der + 8, y_der + 6, der, colores, roles, "nw",
                )
            _poner_borne_ttr(
                lienzo, cx + 28, cy, centro, colores, roles, "w",
                rol_derecha=True,
            )
            _fase_a_mitad_ttr(
                lienzo, x_izq, y_izq, cx, cy, izq, 1,
                parpadeo=mide(izq) and mide(centro),
            )
            _fase_a_mitad_ttr(
                lienzo, cx, cy, x_arr, y_arr, arriba, -1,
                parpadeo=mide(arriba) and mide(centro),
            )
            _fase_a_mitad_ttr(
                lienzo, cx, cy, x_der, y_der, der, -1,
                parpadeo=mide(der) and mide(centro),
            )
        elif kind == "delta":
            apex, izq, der = bornes
            medio = 46 if n == 1 else 40
            linea(cx, 96, cx - medio, 176, apex, izq)
            linea(cx, 96, cx + medio, 176, apex, der)
            linea(cx - medio, 176, cx + medio, 176, izq, der)
            _poner_borne_ttr(lienzo, cx, 80, apex, colores, roles, "s", True)
            _poner_borne_ttr(lienzo, cx - medio, 190, izq, colores, roles, "n")
            _poner_borne_ttr(lienzo, cx + medio, 190, der, colores, roles, "n")
            _fase_a_mitad_ttr(
                lienzo, cx, 96, cx - medio, 176, apex, 1, True,
                parpadeo=mide(apex) and mide(izq),
            )
            _fase_a_mitad_ttr(
                lienzo, cx, 96, cx + medio, 176, der, -1, True,
                parpadeo=mide(apex) and mide(der),
            )
            _fase_a_mitad_ttr(
                lienzo, cx - medio, 176, cx + medio, 176, izq, 1, True,
                parpadeo=mide(izq) and mide(der),
            )
        elif kind == "cruz":
            arriba, izq, der, abajo = bornes
            linea(cx, 56, cx, 124, arriba, arriba)
            linea(cx, 124, cx, 196, abajo, abajo)
            linea(cx - brazo, 124, cx, 124, izq, izq)
            linea(cx, 124, cx + brazo, 124, der, der)
            _poner_borne_ttr(lienzo, cx, 40, arriba, colores, roles, "s", True)
            _poner_borne_ttr(lienzo, cx - brazo - 16, 124, izq, colores, roles, "e")
            _poner_borne_ttr(lienzo, cx + brazo + 16, 124, der, colores, roles, "w")
            _poner_borne_ttr(lienzo, cx, 212, abajo, colores, roles, "n")
        elif kind == "vertical3":
            arriba, medio_b, abajo = bornes
            linea(cx, 64, cx, 128, arriba, medio_b)
            linea(cx, 128, cx, 196, medio_b, abajo)
            _poner_borne_ttr(lienzo, cx, 46, arriba, colores, roles, "s", True)
            _poner_borne_ttr(lienzo, cx + 14, 128, medio_b, colores, roles, "w")
            _poner_borne_ttr(lienzo, cx, 214, abajo, colores, roles, "n")
        elif kind == "horizontal":
            izq, der = bornes
            linea(cx - brazo, 128, cx + brazo, 128, izq, der)
            _poner_borne_ttr(lienzo, cx - brazo - 16, 128, izq, colores, roles, "e")
            _poner_borne_ttr(lienzo, cx + brazo + 16, 128, der, colores, roles, "w")
        else:
            arriba, abajo = bornes
            linea(cx, 78, cx, 186, arriba, abajo)
            _poner_borne_ttr(lienzo, cx, 60, arriba, colores, roles, "s", True)
            _poner_borne_ttr(lienzo, cx, 204, abajo, colores, roles, "n")
        _pie_grupo_ttr(lienzo, cx, pie)
    _puntos_ttr(lienzo, nodos)


EQUIPOS_AISLAMIENTO = [
    "Transformadores de 2 Devanados",
    "Transformadores de 3 Devanados",
    "Autotransformadores",
    "Reactores",
    "Generadores / Máquinas Rotatorias",
    "Transformadores de Corriente - TCs",
    "Transformadores de Potencial - TPs",
    "Transformadores de Potencial Capacitivo - TPCs",
    "Apartarrayos",
]


PRUEBAS_TCS = [
    {
        "prueba": "1",
        "kv": "5000",
        "linea": "P1, P2",
        "tierra": "S1, S2, S3, S4",
        "guarda": "Porcelana",
        "medicion": "RP + RPC",
        "minutos": 1,
    },
    {
        "prueba": "2",
        "kv": "500",
        "linea": "S1, S2, S3, S4",
        "tierra": "P1, P2",
        "guarda": "-----",
        "medicion": "RSC",
        "minutos": 1,
    },
]

# ST-CT-001, Fig. 16 y formato SC-CT-001-H. El secundario se prueba con 500 V
# como máximo (inciso 4.3.1).
PRUEBAS_TPS = [
    {
        "prueba": "1", "kv": "5000", "linea": "P",
        "tierra": "Tq", "guarda": "S",
        "medicion": "RP", "minutos": 1,
    },
    {
        "prueba": "2", "kv": "5000", "linea": "P",
        "tierra": "S", "guarda": "Tq",
        "medicion": "RPS + RP", "minutos": 1,
    },
    {
        "prueba": "3", "kv": "500", "linea": "S",
        "tierra": "Tq", "guarda": "P",
        "medicion": "RS", "minutos": 1,
    },
]

# El procedimiento no trae tabla propia para TPC: remite al formato H.
PRUEBAS_TPCS = [prueba.copy() for prueba in PRUEBAS_TPS]

PRUEBAS_TRANSFORMADORES_2D = [
    {
        "prueba": "1", "kv": "2500-5000", "linea": "H",
        "tierra": "Tq", "guarda": "X",
        "medicion": "RH", "minutos": 10,
    },
    {
        "prueba": "2", "kv": "2500-5000", "linea": "X",
        "tierra": "Tq", "guarda": "H",
        "medicion": "RX", "minutos": 10,
    },
    {
        "prueba": "3", "kv": "2500-5000", "linea": "X",
        "tierra": "H", "guarda": "-----",
        "medicion": "RHX", "minutos": 10,
    },
    {
        "prueba": "4", "kv": "2500-5000", "linea": "H",
        "tierra": "X+Tq", "guarda": "-----",
        "medicion": "RH + RHX", "minutos": 10,
    },
    {
        "prueba": "5", "kv": "2500-5000", "linea": "X",
        "tierra": "H+Tq", "guarda": "-----",
        "medicion": "RX + RHX", "minutos": 10,
    },
]

PRUEBAS_TRANSFORMADORES_3D = [
    {
        "prueba": "1", "kv": "2500-5000", "linea": "H",
        "tierra": "Tq", "guarda": "X+Y",
        "medicion": "RH", "minutos": 10,
    },
    {
        "prueba": "2", "kv": "2500-5000", "linea": "X",
        "tierra": "Tq", "guarda": "H+Y",
        "medicion": "RX", "minutos": 10,
    },
    {
        "prueba": "3", "kv": "2500-5000", "linea": "Y",
        "tierra": "Tq", "guarda": "H+X",
        "medicion": "RY", "minutos": 10,
    },
    {
        "prueba": "4", "kv": "2500-5000", "linea": "H",
        "tierra": "X", "guarda": "Y+Tq",
        "medicion": "RHX", "minutos": 10,
    },
    {
        "prueba": "5", "kv": "2500-5000", "linea": "H",
        "tierra": "Y", "guarda": "X+Tq",
        "medicion": "RHY", "minutos": 10,
    },
    {
        "prueba": "6", "kv": "2500-5000", "linea": "X",
        "tierra": "Y", "guarda": "H+Tq",
        "medicion": "RXY", "minutos": 10,
    },
    {
        "prueba": "7", "kv": "2500-5000", "linea": "H+X+Y",
        "tierra": "Tq", "guarda": "-----",
        "medicion": "RH + RX + RY", "minutos": 10,
    },
    {
        "prueba": "8", "kv": "2500-5000", "linea": "H",
        "tierra": "X+Y+Tq", "guarda": "-----",
        "medicion": "RH + RHY + RHX", "minutos": 10,
    },
    {
        "prueba": "9", "kv": "2500-5000", "linea": "X",
        "tierra": "H+Y+Tq", "guarda": "-----",
        "medicion": "RX + RXY + RHX", "minutos": 10,
    },
    {
        "prueba": "10", "kv": "2500-5000", "linea": "Y",
        "tierra": "H+X+Tq", "guarda": "-----",
        "medicion": "RY + RHY + RXY", "minutos": 10,
    },
]

PRUEBAS_AUTOTRANSFORMADOR = [
    {
        "prueba": "1", "kv": "2500-5000", "linea": "H-X",
        "tierra": "Y+Tq", "guarda": "-----",
        "medicion": "RHX + RHXY", "minutos": 10,
    },
    {
        "prueba": "2", "kv": "2500-5000", "linea": "H-X",
        "tierra": "Tq", "guarda": "Y",
        "medicion": "RHX", "minutos": 10,
    },
    {
        "prueba": "3", "kv": "2500-5000", "linea": "H-X",
        "tierra": "Y", "guarda": "Tq",
        "medicion": "RHXY", "minutos": 10,
    },
    {
        "prueba": "4", "kv": "2500-5000", "linea": "Y",
        "tierra": "H-X+Tq", "guarda": "-----",
        "medicion": "RY + RHXY", "minutos": 10,
    },
    {
        "prueba": "5", "kv": "2500-5000", "linea": "Y",
        "tierra": "Tq", "guarda": "H-X",
        "medicion": "RY", "minutos": 10,
    },
]

PRUEBA_AUTOTRANSFORMADOR_SIN_TERCIARIO = {
    "prueba": "1", "kv": "2500-5000", "linea": "H-X",
    "tierra": "Tq", "guarda": "-----", "medicion": "RHX",
    "minutos": 10,
}

PRUEBAS_REACTOR = [
    {
        "prueba": "1", "kv": "2500-5000", "linea": "H",
        "tierra": "Tq", "guarda": "-----", "medicion": "RH",
        "minutos": 10,
    },
]

# ST-CT-001, Fig. 10 (sin guarda) y formato SC-CT-001-F: cinco pruebas de
# 10 minutos, corregidas a 40 °C. El voltaje sale de la Tabla 2 según la
# tensión de la bobina; el rotor se prueba con 500 V (inciso 4.2.4).
# El formato F trae cruzados los renglones Guarda/Tierra; aquí van como en
# la Fig. 10, donde las otras fases y la carcasa van a tierra.
PRUEBAS_MAQUINAS_ROTATIVAS = [
    {
        "prueba": str(numero), "kv": kv, "linea": linea, "tierra": tierra,
        "guarda": "-----", "medicion": medicion, "minutos": 10,
    }
    for numero, kv, linea, tierra, medicion in (
        (1, "Según Tabla 2", "A", "B+C+Carcasa", "RAT + RAB + RAC"),
        (2, "Según Tabla 2", "B", "A+C+Carcasa", "RBT + RAB + RBC"),
        (3, "Según Tabla 2", "C", "A+B+Carcasa", "RCT + RAC + RBC"),
        (4, "Según Tabla 2", "A+B+C", "Carcasa", "RAT + RBT + RCT"),
        (5, "500", "Rotor", "Carcasa", "RRT"),
    )
]

PRUEBAS_APARTARRAYOS_UNA_SECCION = [
    {
        "prueba": "1", "kv": "2500/5000", "linea": "A",
        "tierra": "B", "guarda": "-----", "medicion": "RAB",
        "minutos": 1,
    },
]

PRUEBAS_APARTARRAYOS_VARIAS_SECCIONES = [
    {
        "prueba": str(numero), "kv": "5000", "linea": linea,
        "tierra": tierra, "guarda": guarda, "medicion": medicion,
        "minutos": 1,
    }
    for numero, linea, tierra, guarda, medicion in (
        # ST-CT-001, Fig. 17 b): tres secciones, sin guarda.
        (1, "A", "B+C+D", "-----", "RAB"),
        (2, "B", "C+D", "-----", "RBC"),
        (3, "C", "D", "-----", "RCD"),
        (4, "A", "D", "-----", "RAD"),
    )
]


_SGR_BLOQUE = re.compile(r"\x1b\[([0-9;]*)m")
_AZUL_NEON_SAPE = "#00FFFF"
_COLOR_TRAZO_BLOQUE = _AZUL_NEON_SAPE
_COLOR_LINEA_BLOQUE = _AZUL_NEON_SAPE
_TEXTO_BLOQUE = "#e2e8f0"
_TRAZO_NEON_BLOQUE = {
    "#00f0ff", "#00f7ff", "#5cfff6", "#4ade80", "#00ff9d", "#00e5ff",
}
_TRAZOS_BLOQUE = {
    "─": "we", "│": "ns", "┌": "se", "┐": "sw", "└": "ne", "┘": "nw",
    "├": "nse", "┤": "nsw", "┬": "wes", "┴": "wen", "┼": "nsew",
    "═": "WE", "║": "NS",
    "╔": "SE", "╗": "SW", "╚": "NE", "╝": "NW",
    "╠": "NSE", "╣": "NSW", "╦": "WES", "╩": "WEN", "╬": "NSEW",
    "╧": "WEN", "╪": "NSEW",
    "┄": "w.e", "┈": "w.e", "┆": "n.s", "┊": "n.s",
}
_ZIGZAG_BLOQUE = set("╱╲∨")


def _color_sgr_bloque(numeros, color):
    if not numeros or numeros == [0]:
        return _TEXTO_BLOQUE
    i = 0
    while i < len(numeros):
        n = numeros[i]
        if n in (0, 39):
            color = _TEXTO_BLOQUE
        elif n == 38 and i + 4 < len(numeros) and numeros[i + 1] == 2:
            r, g, b = numeros[i + 2:i + 5]
            color = f"#{r:02x}{g:02x}{b:02x}"
            i += 4
        elif n == 48 and i + 4 < len(numeros) and numeros[i + 1] == 2:
            i += 4
        i += 1
    return color


def _teñir_letra_suelta(filas, letra, color):
    """Pinta H o X sueltos en la caja. No toca la H de RH ni la X de RX."""
    for fila in filas:
        for i, (glifo, _) in enumerate(fila):
            if glifo != letra:
                continue
            antes = fila[i - 1][0] if i else " "
            despues = fila[i + 1][0] if i + 1 < len(fila) else " "
            if antes.isalnum() or despues.isalnum():
                continue
            fila[i] = (glifo, color)


def _estilo_plano_conexiones(
    filas, tierra_en_tanque, guarda_en_tanque, tierra_en_tierra=False,
    letras_linea=None, tierra_en_devanado=False,
):
    """CONEXIONES: el trazo en azul y los rótulos en gris oscuro."""
    cable = RA_AZUL_MARINO
    tono = "#1E293B"
    rojo_intenso = "#FF0000"
    azul_intenso = "#1E3A8A"
    _limpiar_cajas_conexiones(filas)
    roles = (
        ("LÍNEA", rojo_intenso),
        ("LINEA", rojo_intenso),
        ("TIERRA", "#000000"),
        ("GUARDA", "#1E40AF"),
    )
    for fila in filas:
        for i, (glifo, _color) in enumerate(fila):
            if glifo in _TRAZOS_BLOQUE or glifo in _ZIGZAG_BLOQUE:
                continue
            if glifo in (" ", "○"):
                continue
            fila[i] = (glifo, tono)
    for palabra_tanque in ("TANQUE", "CARCASA"):
        _teñir_palabra_bloques(
            filas, palabra_tanque, "#000000" if tierra_en_tanque else tono,
        )
    for codigo in _CODIGOS_RESISTENCIA_RA:
        _teñir_palabra_bloques(filas, codigo, tono)
    for palabra, color in roles:
        if palabra in ("TIERRA", "LÍNEA", "LINEA"):
            _teñir_palabra_en_caja(filas, palabra, color)
        else:
            _teñir_palabra_bloques(filas, palabra, color)
        marco = "#3B82F6" if palabra == "GUARDA" else color
        if palabra == "TIERRA" and not (tierra_en_tierra or tierra_en_devanado):
            marco = cable
        _teñir_marco_de(filas, palabra, marco)
    if tierra_en_tierra:
        _teñir_palabra_fuera_de_caja(filas, "TIERRA", "#000000")
    rojas = {
        letra for letra in (letras_linea or ())
        if letra in "HXYPSABCD"
    }
    for letra in rojas:
        _teñir_letra_suelta(filas, letra, rojo_intenso)
    if "X" not in rojas:
        _teñir_letra_suelta(filas, "X", azul_intenso)
    for fila in filas:
        for i, (glifo, color) in enumerate(fila):
            if glifo == "╧":
                for k, (g, _) in enumerate(fila):
                    if g in _TRAZOS_BLOQUE or g in _ZIGZAG_BLOQUE:
                        fila[k] = (g, cable)
                break
        else:
            continue
        break
    for fila in filas:
        for i, (glifo, color) in enumerate(fila):
            if glifo not in _TRAZOS_BLOQUE and glifo not in _ZIGZAG_BLOQUE:
                continue
            if str(color).lower() in _TRAZO_NEON_BLOQUE or str(color).lower() in {
                "#00ffff", "#e2e8f0", "#00f0ff",
            }:
                fila[i] = (glifo, cable)
    _teñir_caida_vertical(filas, cable)


def _teñir_roles_junto_a_bus(filas):
    """Apartarrayos: el rol va escrito junto al borne, no dentro de una caja.

    Con el color de su conexión el rótulo parpadea igual que en los demás
    equipos (la pantalla agrupa el parpadeo por ese color).
    """
    for palabra, color in (
        ("LÍNEA", "#DC2626"), ("LINEA", "#DC2626"),
        ("TIERRA", "#111111"), ("GUARDA", "#2563EB"),
    ):
        _teñir_palabra_junto_a_bus(filas, palabra, color)


def _teñir_palabra_junto_a_bus(filas, palabra, color):
    """Pinta el rótulo que queda pegado a la izquierda de la vertical."""
    n = len(palabra)
    for fila in filas:
        chars = "".join(ch for ch, _ in fila)
        inicio = 0
        while True:
            i = chars.find(palabra, inicio)
            if i < 0:
                break
            inicio = i + n
            sigue = chars[i + n:i + n + 3]
            if not sigue.strip() or sigue.strip()[0] not in "│║":
                continue
            # Dentro de una caja ya lo pinta el rol del devanado.
            if any(g in "│║" for g in chars[max(0, i - 9):i]):
                continue
            for k in range(n):
                fila[i + k] = (fila[i + k][0], color)


def _quitar_letras_cajas_fp(filas):
    """Quita la letra del devanado dentro de las cajas FP; el rol queda centrado."""
    roles = ("GROUND", "GUARD", "UST", "HV")
    nfil = len(filas)
    for r, fila in enumerate(filas):
        chars = "".join(ch for ch, _ in fila)
        c = 0
        while c < len(fila):
            if fila[c][0] != "┌":
                c += 1
                continue
            cierre = chars.find("┐", c + 1)
            if cierre < 0:
                break
            abajo = r + 1
            while abajo < nfil and not (
                c < len(filas[abajo]) and filas[abajo][c][0] == "└"
            ):
                abajo += 1
            if abajo < nfil and abajo > r + 1:
                rol = None
                for rr in range(r + 1, abajo):
                    texto = "".join(
                        g for g, _ in filas[rr][c + 1:cierre]
                    )
                    for nombre in roles:
                        if nombre in texto:
                            rol = nombre
                            break
                    if rol:
                        break
                for rr in range(r + 1, abajo):
                    for k in range(c + 1, min(cierre, len(filas[rr]))):
                        if filas[rr][k][0] != " ":
                            filas[rr][k] = (" ", filas[rr][k][1])
                if rol:
                    ancho = cierre - (c + 1)
                    inicio = c + 1 + max(0, (ancho - len(rol)) // 2)
                    mitad = (r + 1 + abajo - 1) // 2
                    fila_rol = filas[mitad]
                    for k, ch in enumerate(rol):
                        if inicio + k < len(fila_rol):
                            fila_rol[inicio + k] = (
                                ch, fila_rol[inicio + k][1],
                            )
            c = cierre + 1


_CAPS_FP = (
    "C(T1-T2)", "C(B1+B2)", "C(B1+B3)", "C(B3+B2)",
    "CHXY", "CTOT", "C1-3", "C1-2", "C1-1",
    "CHS", "CHX", "CHY", "CXY", "CPC", "CPS", "CSC",
    "CAB", "CBC", "CCD", "CB1", "CB2", "CB3",
    "CH", "CX", "CY", "CP", "CS", "C1", "C2", "C",
)


def _teñir_capacitancias_fp(filas, pastel, naranja):
    """Etiquetas de capacitancia. La que ya está en naranja es la medida."""
    codigos = sorted(_CAPS_FP, key=len, reverse=True)
    for fila in filas:
        chars = "".join(glifo for glifo, _ in fila)
        ocupado = [False] * len(chars)
        for codigo in codigos:
            inicio = 0
            while True:
                i = chars.find(codigo, inicio)
                if i < 0:
                    break
                fin = i + len(codigo)
                inicio = i + 1
                antes = chars[i - 1] if i else " "
                despues = chars[fin] if fin < len(chars) else " "
                if antes.isalnum() or despues.isalnum():
                    continue
                if any(ocupado[i:fin]):
                    continue
                for k in range(i, fin):
                    ocupado[k] = True
                if any(
                    str(fila[k][1]).lower() == naranja.lower()
                    for k in range(i, fin)
                ):
                    continue
                for k in range(i, fin):
                    if fila[k][0] != " ":
                        fila[k] = (fila[k][0], pastel)


def _estilo_plano_fp(filas, medicion=False, naranja="#F76707", ground_en_tanque=False):
    """Los dos diagramas en verde. En MEDICIÓN, la C de esa columna queda naranja."""
    if not medicion:
        _estilo_conexiones_fp(filas, ground_en_tanque=ground_en_tanque)
        return
    verde = FP_VERDE_OSCURO
    for fila in filas:
        for i, (glifo, color) in enumerate(fila):
            if glifo == " ":
                continue
            if _es_amarillo_hex(color):
                fila[i] = (glifo, naranja)
            else:
                fila[i] = (glifo, verde)
    # MEDICIÓN: ALTA, BAJA, capacitancias, TANQUE y TIERRA quedan del
    # mismo verde que TERCIARIO. La capacitancia medida sigue en naranja.
    _teñir_placas_medidas_fp(filas, naranja)


def _teñir_placas_medidas_fp(filas, naranja):
    """Las placas de la capacitancia medida toman el naranja de su rótulo.

    Así el símbolo completo, y no solo el rótulo, parpadea en MEDICIÓN.
    """
    codigos = set(_CAPS_FP)
    for r, fila in enumerate(filas):
        chars = "".join(glifo for glifo, _ in fila)
        for hallado in re.finditer(r"[A-Z0-9()+\-]+", chars):
            c, fin = hallado.start(), hallado.end()
            if hallado.group() not in codigos:
                continue
            if str(fila[c][1]).lower() != naranja.lower():
                continue
            # Capacitancia horizontal: las placas ┤ ├ están en el renglón
            # de arriba.
            arriba = filas[r - 1] if r > 0 else []
            placas = [
                k for k in range(max(0, c - 3), min(len(arriba), fin + 3))
                if arriba[k][0] in "┤├"
            ]
            if placas:
                for k in placas:
                    arriba[k] = (arriba[k][0], naranja)
                continue
            # Capacitancia vertical: placas ─┴─ a la izquierda del rótulo
            # y ─┬─ en el renglón siguiente.
            for k in range(max(0, c - 6), c):
                if fila[k][0] != "┴":
                    continue
                for rr in (r, r + 1):
                    if rr >= len(filas):
                        continue
                    for kk in (k - 1, k, k + 1):
                        if 0 <= kk < len(filas[rr]) and filas[rr][kk][0] in "─┴┬":
                            filas[rr][kk] = (filas[rr][kk][0], naranja)
                break


def _estilo_conexiones_fp(filas, ground_en_tanque=False):
    """Verde como MEDICIÓN. HV negro, GROUND rojo, GUARD y UST azul: el color de su columna."""
    _quitar_letras_cajas_fp(filas)
    cable = FP_VERDE_OSCURO
    tono = FP_VERDE_OSCURO
    for fila in filas:
        for i, (glifo, _color) in enumerate(fila):
            if glifo == " ":
                continue
            if glifo in _TRAZOS_BLOQUE or glifo in _ZIGZAG_BLOQUE:
                fila[i] = (glifo, cable)
            else:
                fila[i] = (glifo, tono)
    _teñir_capacitancias_fp(filas, tono, "#F76707")
    for palabra in ("TANQUE", "TIERRA", "ALTA", "BAJA"):
        _teñir_palabra_bloques(filas, palabra, tono)
    if ground_en_tanque:
        _teñir_palabra_bloques(filas, "TANQUE", "#FF4D4D")
    # Mismos colores que las columnas de la tabla de pruebas FP.
    _teñir_palabra_bloques(filas, "HV", "#000000")
    _teñir_palabra_bloques(filas, "GROUND", "#FF4D4D")
    _teñir_palabra_bloques(filas, "GUARD", "#4D9AFF")
    _teñir_palabra_bloques(filas, "UST", "#4D9AFF")
    _teñir_caida_vertical(filas, cable)


def _estilo_plano_conexiones_fp(filas):
    """CONEXIONES FP en blanco: cada caja con el color de su rol en la prueba."""
    _quitar_letras_cajas_fp(filas)
    cable = "#334155"
    tono = "#006066"
    rojo = "#E03131"
    roles = (
        ("HV", "#CC00CC"),
        ("GROUND", rojo),
        ("GUARD", "#3B82F6"),
        ("UST", "#3B82F6"),
    )
    for fila in filas:
        for i, (glifo, _color) in enumerate(fila):
            if glifo in _TRAZOS_BLOQUE or glifo in _ZIGZAG_BLOQUE:
                continue
            if glifo in (" ", "○"):
                continue
            fila[i] = (glifo, tono)
    _teñir_palabra_bloques(filas, "TANQUE", tono)
    _teñir_palabra_bloques(filas, "TIERRA", tono)
    for palabra, color in roles:
        _teñir_palabra_bloques(filas, palabra, color)
        _teñir_marco_de(filas, palabra, color)
    for fila in filas:
        for i, (glifo, color) in enumerate(fila):
            if glifo == "╧":
                for k, (g, _) in enumerate(fila):
                    if g in _TRAZOS_BLOQUE or g in _ZIGZAG_BLOQUE:
                        fila[k] = (g, "#000000")
                break
        else:
            continue
        break
    for fila in filas:
        for i, (glifo, color) in enumerate(fila):
            if glifo not in _TRAZOS_BLOQUE and glifo not in _ZIGZAG_BLOQUE:
                continue
            if str(color).lower() in _TRAZO_NEON_BLOQUE or str(color).lower() in {
                "#00ffff", "#e2e8f0", "#00f0ff",
            }:
                fila[i] = (glifo, cable)
    _teñir_caida_vertical(filas, "#3B82F6")


def _es_amarillo_hex(color):
    texto = str(color).lstrip("#")
    if len(texto) != 6:
        return False
    try:
        rojo, verde, azul = int(texto[0:2], 16), int(texto[2:4], 16), int(texto[4:6], 16)
    except ValueError:
        return False
    return rojo > 220 and verde > 220 and azul < 80


def _estilo_plano_medicion(filas, oro="#F76707"):
    """Texto en azul. El rótulo de lo que se mide queda en su color."""
    for fila in filas:
        for i, (glifo, color) in enumerate(fila):
            if glifo == " ":
                continue
            if _es_amarillo_hex(color):
                fila[i] = (glifo, oro)
            elif glifo in _TRAZOS_BLOQUE or glifo in _ZIGZAG_BLOQUE or glifo == "○":
                fila[i] = (glifo, RA_AZUL_MARINO)
            else:
                fila[i] = (glifo, RA_AZUL_MARINO)


def _teñir_marco_de(filas, palabra, color):
    """Pinta solo la caja que tiene la palabra entre dos │. No toca el tanque."""
    nfil = len(filas)
    for r, fila in enumerate(filas):
        chars = "".join(ch for ch, _ in fila)
        inicio = 0
        while True:
            i = chars.find(palabra, inicio)
            if i < 0:
                break
            inicio = i + len(palabra)
            ncols = len(fila)
            fin_pal = i + len(palabra) - 1
            izq = i - 1
            while izq >= 0 and i - izq <= 8 and fila[izq][0] not in "│║":
                izq -= 1
            der = fin_pal + 1
            while der < ncols and der - fin_pal <= 8 and fila[der][0] not in "│║":
                der += 1
            if izq < 0 or der >= ncols:
                continue
            if fila[izq][0] not in "│║" or fila[der][0] not in "│║":
                continue
            arriba = r
            while arriba > 0 and r - arriba < 6:
                g = filas[arriba - 1][izq][0] if izq < len(filas[arriba - 1]) else ""
                if g in "┌╔":
                    arriba -= 1
                    break
                if g in "│║":
                    arriba -= 1
                    continue
                break
            abajo = r
            while abajo < nfil - 1 and abajo - r < 6:
                g = filas[abajo + 1][izq][0] if izq < len(filas[abajo + 1]) else ""
                if g in "└╚":
                    abajo += 1
                    break
                if g in "│║":
                    abajo += 1
                    continue
                break
            for cc in range(izq, der + 1):
                for rr in (arriba, abajo):
                    if cc < len(filas[rr]) and filas[rr][cc][0] in _TRAZOS_BLOQUE:
                        filas[rr][cc] = (filas[rr][cc][0], color)
            for rr in range(arriba, abajo + 1):
                for cc in (izq, der):
                    if cc < len(filas[rr]) and filas[rr][cc][0] in _TRAZOS_BLOQUE:
                        filas[rr][cc] = (filas[rr][cc][0], color)


def _teñir_caida_vertical(filas, color):
    """Zigzag entre dos │ (RPC / guarda): el tramo vertical completo, sin el tanque."""
    nfil = len(filas)
    for r, fila in enumerate(filas):
        c = 0
        ncols = len(fila)
        while c < ncols:
            if fila[c][0] not in _ZIGZAG_BLOQUE:
                c += 1
                continue
            ini = c
            while c < ncols and fila[c][0] in _ZIGZAG_BLOQUE:
                c += 1
            izq = fila[ini - 1][0] if ini else " "
            der = fila[c][0] if c < ncols else " "
            if izq in _TRAZOS_BLOQUE or der in _TRAZOS_BLOQUE:
                continue
            stem = None
            for k in range(ini, c):
                arriba = filas[r - 1][k][0] if r and k < len(filas[r - 1]) else ""
                abajo = filas[r + 1][k][0] if r + 1 < nfil and k < len(filas[r + 1]) else ""
                if arriba in "│║" or abajo in "│║":
                    stem = k
                    break
            if stem is None:
                continue
            for k in range(ini, c):
                fila[k] = (fila[k][0], color)
            for hacia in (-1, 1):
                rr = r + hacia
                while 0 <= rr < nfil and stem < len(filas[rr]):
                    g = filas[rr][stem][0]
                    if g not in "│║":
                        break
                    filas[rr][stem] = (g, color)
                    rr += hacia


def _teñir_cables_conexion(
    filas, pintar_tierra=False, pintar_tanque=False, pintar_caja=False,
):
    """Pinta el ramal de LÍNEA, GUARDA y, si aplica, TIERRA o el tanque."""
    rojo, azul, negro = "#FF0000", "#3B82F6", "#000000"
    roles = {"LÍNEA": rojo, "LINEA": rojo, "GUARDA": azul}
    if pintar_tierra or pintar_caja:
        roles["TIERRA"] = negro
    nfil = len(filas)
    ncols = max((len(fila) for fila in filas), default=0)

    def glifo(r, c):
        if r < 0 or c < 0 or r >= nfil or c >= len(filas[r]):
            return ""
        return filas[r][c][0]

    def es_trazo(ch):
        return ch in _TRAZOS_BLOQUE or ch in _ZIGZAG_BLOQUE

    def pintar(r, c, color):
        filas[r][c] = (filas[r][c][0], color)

    cuenta = [0] * ncols
    for fila in filas:
        for c, (ch, _) in enumerate(fila):
            if ch in "│║├┤┬┴┼╠╣╦╩╬╪":
                cuenta[c] += 1
    espina = None
    if ncols:
        mejor = max(range(ncols), key=lambda c: cuenta[c])
        if cuenta[mejor] >= 3:
            espina = mejor

    cajas = []
    ocupadas = []
    for r, fila in enumerate(filas):
        c = 0
        while c < len(fila):
            if fila[c][0] not in "┌╔":
                c += 1
                continue
            cierre = None
            for k in range(c + 1, min(len(fila), c + 18)):
                g = fila[k][0]
                if g in "┐╗":
                    cierre = k
                    break
                if g not in "─┬┴═╦╩┼╬":
                    break
            if cierre is None:
                c += 1
                continue
            abajo = None
            for rr in range(r + 1, min(nfil, r + 8)):
                if c >= len(filas[rr]):
                    break
                g = filas[rr][c][0]
                if g in "└╚":
                    abajo = rr
                    break
                if g not in "│║├┤┼╠╣╬":
                    break
            if (
                abajo is None
                or cierre >= len(filas[abajo])
                or filas[abajo][cierre][0] not in "┘╝"
            ):
                c += 1
                continue
            letras = [
                filas[rr][k][0]
                for rr in range(r + 1, abajo)
                for k in range(c + 1, cierre)
                if k < len(filas[rr])
                and filas[rr][k][0].strip()
                and filas[rr][k][0] not in _TRAZOS_BLOQUE
            ]
            texto = "".join(letras).upper()
            color = next((tono for rol, tono in roles.items() if rol in texto), None)
            if color is not None:
                cajas.append((r, abajo, c, cierre, color))
                ocupadas.append((r, abajo, c, cierre))
            c = cierre + 1

    def dentro(rr, cc):
        return any(
            r0 <= rr <= r1 and c0 <= cc <= c1
            for r0, r1, c0, c1 in ocupadas
        )

    def camino(inicio):
        prev = {inicio: None}
        cola = [inicio]
        meta = None
        while cola and meta is None and len(prev) < 80:
            rr, cc = cola.pop(0)
            for dr, dc in ((0, 1), (0, -1), (1, 0), (-1, 0)):
                nr, nc = rr + dr, cc + dc
                if (nr, nc) in prev or dentro(nr, nc):
                    continue
                ch = glifo(nr, nc)
                if not es_trazo(ch):
                    continue
                if espina is not None and nc == espina:
                    meta = (rr, cc)
                    break
                prev[(nr, nc)] = (rr, cc)
                cola.append((nr, nc))
        if meta is None:
            return None
        celdas = []
        cur = meta
        while cur is not None:
            celdas.append(cur)
            cur = prev[cur]
        return celdas

    bornes = []
    for r, abajo, c, cierre, color in cajas:
        entradas = []
        for rr in range(r, abajo + 1):
            if es_trazo(glifo(rr, c - 1)):
                entradas.append(("w", rr, c))
            if es_trazo(glifo(rr, cierre + 1)):
                entradas.append(("e", rr, cierre))
        if r > 0:
            for cc in range(c, cierre + 1):
                if es_trazo(glifo(r - 1, cc)):
                    entradas.append(("n", r, cc))
        if abajo + 1 < nfil:
            for cc in range(c, cierre + 1):
                if es_trazo(glifo(abajo + 1, cc)):
                    entradas.append(("s", abajo, cc))
        for lado, fila_b, col_b in entradas:
            origen = {
                "w": (fila_b, c - 1),
                "e": (fila_b, cierre + 1),
                "n": (r - 1, col_b),
                "s": (abajo + 1, col_b),
            }[lado]
            celdas = camino(origen)
            if not celdas:
                continue
            for rr, cc in celdas:
                pintar(rr, cc, color)
            bornes.append((lado, fila_b, col_b, color))
            break

    if pintar_tierra:
        for r, fila in enumerate(filas):
            for c, (ch, _) in enumerate(fila):
                if ch != "╧":
                    continue
                pintar(r, c, negro)
                for dc in (-1, 1):
                    cc = c + dc
                    while glifo(r, cc) in "═─":
                        pintar(r, cc, negro)
                        cc += dc
                rr = r - 1
                while glifo(rr, c) in "│║" and not (
                    es_trazo(glifo(rr, c - 1)) or es_trazo(glifo(rr, c + 1))
                ):
                    pintar(rr, c, negro)
                    rr -= 1
                bornes.append(("c", r, c, negro))

    if pintar_tanque and espina is not None:
        reserva = set()
        for r, fila in enumerate(filas):
            for c, (ch, _) in enumerate(fila):
                if ch != "╧":
                    continue
                rr = r - 1
                while glifo(rr, c) in "│║" and not (
                    es_trazo(glifo(rr, c - 1)) or es_trazo(glifo(rr, c + 1))
                ):
                    reserva.add((rr, c))
                    rr -= 1
        for r, fila in enumerate(filas):
            if (
                espina < len(fila)
                and fila[espina][0] in "│║"
                and (r, espina) not in reserva
            ):
                pintar(r, espina, negro)

    def palabras(palabra):
        n = len(palabra)
        for r, fila in enumerate(filas):
            chars = "".join(ch for ch, _ in fila)
            inicio = 0
            while True:
                i = chars.find(palabra, inicio)
                if i < 0:
                    break
                inicio = i + n
                if any(r0 < r < r1 and c0 < i < c1 for r0, r1, c0, c1 in ocupadas):
                    continue
                yield r, i, i + n - 1

    if not any(color == rojo for *_, color in cajas):
        for r, _c0, c1 in palabras("LÍNEA"):
            for cc in list(range(c1 + 1, min(ncols, c1 + 8))) + list(range(c1, max(-1, c1 - 8), -1)):
                if glifo(r, cc) in "│║":
                    pintar(r, cc, rojo)
                    bornes.append(("c", r, cc, rojo))
                    break

    if not any(color == azul for *_, color in cajas):
        for r, _c0, c1 in palabras("GUARDA"):
            col = None
            for cc in range(c1 + 1, min(ncols, c1 + 12)):
                if es_trazo(glifo(r, cc)) and cc != espina:
                    col = cc
                    break
            if col is None:
                continue
            izquierda = col
            while glifo(r, izquierda - 1) in _ZIGZAG_BLOQUE:
                izquierda -= 1
            derecha = col
            while glifo(r, derecha + 1) in _ZIGZAG_BLOQUE:
                derecha += 1
            for cc in range(izquierda, derecha + 1):
                pintar(r, cc, azul)
            for hacia in (-1, 1):
                rr = r + hacia
                while glifo(rr, col) in "│║" or glifo(rr, col) in _ZIGZAG_BLOQUE:
                    if col == espina:
                        break
                    pintar(rr, col, azul)
                    rr += hacia
            bornes.append(("c", r, col, azul))

    return bornes


def _teñir_palabra_bloques(filas, palabra, color):
    n = len(palabra)
    for fila in filas:
        chars = "".join(ch for ch, _ in fila)
        inicio = 0
        while True:
            i = chars.find(palabra, inicio)
            if i < 0:
                break
            for k in range(n):
                fila[i + k] = (fila[i + k][0], color)
            inicio = i + n


def _limpiar_cajas_conexiones(filas):
    """Dentro de una caja con rol (LINEA/TIERRA/GUARDA) borra el texto extra."""
    roles = {"LINEA", "LÍNEA", "TIERRA", "GUARDA"}
    grupos = {}
    for r, fila in enumerate(filas):
        bordes = [
            c for c, (glifo, _color) in enumerate(fila) if glifo in "│║"
        ]
        for k in range(len(bordes) - 1):
            izq, der = bordes[k], bordes[k + 1]
            texto = "".join(
                fila[c][0] for c in range(izq + 1, der)
            ).strip()
            if texto:
                grupos.setdefault((izq, der), []).append((r, texto))
    for (izq, der), miembros in grupos.items():
        if not any(texto in roles for _r, texto in miembros):
            continue
        for r, texto in miembros:
            if texto in roles:
                continue
            if len(texto) == 1 and texto in "HXYPSABCD":
                continue
            fila = filas[r]
            for c in range(izq + 1, der):
                fila[c] = (" ", fila[c][1])


def _recortar_rejilla_bloques(filas):
    filas = [list(fila) for fila in filas]
    while filas and not any(ch.strip() for ch, _ in filas[-1]):
        filas.pop()
    while filas and not any(ch.strip() for ch, _ in filas[0]):
        filas.pop(0)
    return filas


def _cajas_de_rejilla(filas):
    """Cajas ┌─┐ de la rejilla: (fila_ini, fila_fin, col_izq, col_der)."""
    cajas = []
    for r, fila in enumerate(filas):
        chars = "".join(ch for ch, _ in fila)
        i = chars.find("┌")
        while i >= 0:
            j = chars.find("┐", i + 1)
            if j > i:
                cajas.append([r, r, i, j])
            i = chars.find("┌", i + 1)
    for caja in cajas:
        r = caja[0] + 1
        while (
            r < len(filas) and caja[2] < len(filas[r])
            and filas[r][caja[2]][0] in "│║"
        ):
            caja[1] = r
            r += 1
        if (
            r < len(filas) and caja[2] < len(filas[r])
            and filas[r][caja[2]][0] in "└╚"
        ):
            caja[1] = r
    return [tuple(caja) for caja in cajas]


def _insertar_celdas(fila, pos, n):
    if n > 0:
        glifo, color = " ", _TEXTO_BLOQUE
        if 0 < pos <= len(fila) and fila[pos - 1][0] in "─═":
            glifo, color = fila[pos - 1]
        elif pos < len(fila):
            color = fila[pos][1]
        fila[pos:pos] = [(glifo, color)] * n
    elif n < 0:
        del fila[max(0, pos + n):pos]


def _columna_libre_segmento(filas, filas_seg, desde, hacia):
    """Columna en blanco en todas las filas del segmento, buscando desde una."""
    c = desde
    while 0 <= c and filas_seg:
        if all(
            c >= len(filas[r]) or not filas[r][c][0].strip()
            for r in filas_seg
        ):
            return c
        c += hacia
    return desde


def _igualar_cajas_conexiones(filas, cajas_objetivo):
    """Ensacha las cajas de CONEXIONES al ancho de las de MEDICIÓN."""
    propias = _cajas_de_rejilla(filas)
    if not propias or len(propias) != len(cajas_objetivo):
        return
    for indice, ((r0, r1, izq, der), (_m0, _m1, m_izq, m_der)) in enumerate(
        zip(propias, cajas_objetivo)
    ):
        delta = m_der - der
        if not delta:
            continue
        for r in range(r0, r1 + 1):
            _insertar_celdas(filas[r], der, delta)
        if indice + 1 < len(propias):
            seg_fin = propias[indice + 1][0] - 1
        else:
            seg_fin = len(filas) - 1
        cable = None
        for r in range(r1 + 1, min(r1 + 3, len(filas))):
            for c in range(izq + 1, len(filas[r])):
                if filas[r][c][0] in "│║":
                    cable = c
                    break
            if cable is not None:
                break
        centro_objetivo = (m_izq + m_der) // 2
        despl = centro_objetivo - cable if cable is not None else delta // 2
        filas_seg = [
            r for r in range(r1 + 1, seg_fin + 1)
            if any(g.strip() for g, _ in filas[r][izq:])
        ]
        if filas_seg and despl:
            corte1 = _columna_libre_segmento(
                filas, filas_seg, (cable or izq) - 1, -1,
            )
            for r in filas_seg:
                _insertar_celdas(filas[r], corte1, despl)
        if filas_seg and delta - despl:
            corte2 = _columna_libre_segmento(
                filas, filas_seg, der + despl, 1,
            )
            for r in filas_seg:
                _insertar_celdas(filas[r], corte2, delta - despl)
        for r in range(r0, r1 + 1):
            fila = filas[r]
            if der + delta >= len(fila):
                continue
            interior = fila[izq + 1:der + delta]
            if any(
                g in _TRAZOS_BLOQUE or g in _ZIGZAG_BLOQUE
                for g, _ in interior
            ):
                continue
            letras = [(g, col) for g, col in interior if g.strip()]
            if not letras:
                continue
            ancho_int = der + delta - izq - 1
            inicio = izq + 1 + max(0, (ancho_int - len(letras)) // 2)
            for c in range(izq + 1, der + delta):
                fila[c] = (" ", fila[c][1])
            for k, (g, col) in enumerate(letras):
                fila[inicio + k] = (g, col)


def _texto_de_rejilla(filas):
    lineas = []
    for fila in filas:
        partes = []
        actual = None
        for glifo, color in fila:
            col = str(color).lower()
            if col != actual:
                try:
                    r = int(col[1:3], 16)
                    g = int(col[3:5], 16)
                    b = int(col[5:7], 16)
                    partes.append(f"\x1b[38;2;{r};{g};{b}m")
                except (ValueError, IndexError):
                    partes.append("\x1b[0m")
                actual = col
            partes.append(glifo)
        partes.append("\x1b[0m")
        lineas.append("".join(partes))
    return "\n".join(lineas)


def _teñir_palabra_en_caja(filas, palabra, color):
    """Pinta la palabra solo cuando va dentro de una caja de devanado."""
    n = len(palabra)
    for fila in filas:
        chars = "".join(ch for ch, _ in fila)
        inicio = 0
        while True:
            i = chars.find(palabra, inicio)
            if i < 0:
                break
            inicio = i + n
            fin = i + n - 1
            izq = i - 1
            while izq >= 0 and i - izq <= 8 and fila[izq][0] not in "│║":
                izq -= 1
            der = fin + 1
            while der < len(fila) and der - fin <= 8 and fila[der][0] not in "│║":
                der += 1
            if izq < 0 or der >= len(fila):
                continue
            if fila[izq][0] not in "│║" or fila[der][0] not in "│║":
                continue
            for k in range(n):
                fila[i + k] = (fila[i + k][0], color)


def _teñir_palabra_fuera_de_caja(filas, palabra, color):
    """Pinta la palabra solo cuando va fuera de una caja de devanado."""
    n = len(palabra)
    for fila in filas:
        chars = "".join(ch for ch, _ in fila)
        inicio = 0
        while True:
            i = chars.find(palabra, inicio)
            if i < 0:
                break
            inicio = i + n
            fin = i + n - 1
            izq = i - 1
            while izq >= 0 and i - izq <= 8 and fila[izq][0] not in "│║":
                izq -= 1
            der = fin + 1
            while der < len(fila) and der - fin <= 8 and fila[der][0] not in "│║":
                der += 1
            en_caja = (
                izq >= 0 and der < len(fila)
                and fila[izq][0] in "│║" and fila[der][0] in "│║"
            )
            if en_caja:
                continue
            for k in range(n):
                fila[i + k] = (fila[i + k][0], color)


def _columna_pide_tierra(texto):
    """La columna TIERRA pide la tierra: la T suelta (S+T) o la palabra TIERRA."""
    t = (texto or "").strip().upper()
    if not t or t in ("-----", "---", "—"):
        return False
    if "TIERRA" in t:
        return True
    return bool(re.search(r"(?:^|[\s,+])T(?!Q)(?:[\s,+]|$)", t))


def _fp_ground_marca_tanque(texto):
    """La columna GROUND de FP cae en el tanque: Tanque, o la T suelta (S+T, T)."""
    if not texto or str(texto).strip() in ("", "—", "---", "-----"):
        return False
    t = str(texto).upper().replace("*", "")
    if "TANQUE" in t or "TANK" in t:
        return True
    return bool(re.search(r"(?:^|[\s,+])T(?:[\s,+]|$)", t))


def _columna_pide_tanque(texto):
    """La columna pide el tanque solo si dice Tanque o Tq. La T es TIERRA."""
    t = (texto or "").strip().upper()
    if not t or t in ("-----", "---", "—", "TIERRA"):
        return False
    if "TANQUE" in t or "TANK" in t or "CARCASA" in t:
        return True
    return bool(re.search(r"(?:^|[\s,+])TQ(?:[\s,+]|$)", t))


def _sitios_rol_ra(texto, simbolo_tierra=False):
    """H/X/Y/P/S/A/B/C/D, TANQUE y el símbolo TIERRA que marca la columna."""
    t = (texto or "").strip().upper()
    if not t or t in ("-----", "---", "—", "NONE"):
        return set()
    sitios = set()
    # En máquinas rotatorias la carcasa hace de tanque y el rotor es un borne.
    if "ROTOR" in t:
        sitios.add("ROTOR")
        t = t.replace("ROTOR", " ")
    t = t.replace("CARCASA", "TANQUE")
    if (
        "TANQUE" in t
        or "TANK" in t
        or re.search(r"(?:^|[\s,+\-])TQ(?:[\s,+\-]|$)", t)
    ):
        sitios.add("TANQUE")
    if simbolo_tierra and (
        "TIERRA" in t
        or re.search(r"(?:^|[\s,+\-])T(?!Q)(?:[\s,+\-]|$)", t)
    ):
        sitios.add("TIERRA")
    limpio = re.sub(r"TANQUE|TANK|TIERRA|PORCELANA|PORCEL", " ", t)
    limpio = re.sub(r"(?:^|[\s,+\-])TQ(?:[\s,+\-]|$)", " ", limpio)
    if simbolo_tierra:
        limpio = re.sub(r"(?:^|[\s,+\-])T(?!Q)(?:[\s,+\-]|$)", " ", limpio)
    limpio = re.sub(r"([HXYPSABCD])\d+", r"\1", limpio)
    sitios.update(re.findall(r"[HXYPSABCD]", limpio))
    return sitios


_CODIGOS_RESISTENCIA_RA = (
    "RHXY", "RHX", "RHY", "RXY", "RH1", "RH2",
    "RPC", "RPS", "RSC",
    "RAT", "RBT", "RCT", "RRT",
    "RAD", "RAC", "RAB", "RBC", "RCD",
    "RH", "RX", "RY", "RP", "RS",
)
_RE_CODIGO_RESISTENCIA_RA = re.compile("|".join(_CODIGOS_RESISTENCIA_RA))
_RE_ANSI_BLOQUE = re.compile(r"\x1b\[[0-9;]*m")


def _leyenda_resistencias_ra(texto, equipo):
    """Resistencias dibujadas en MEDICIÓN, en el orden del diagrama."""
    plano = _RE_ANSI_BLOQUE.sub("", texto or "")
    equipo = equipo or ""
    es_tc = "TCs" in equipo
    es_auto = "Autotransformadores" in equipo
    es_reactor = "Reactores" in equipo
    descripciones = {
        "RP": (
            "Resistencia del primario (P1-P2)"
            if es_tc else "Resistencia del primario (P)"
        ),
        "RS": "Resistencia del secundario (S)",
        "RPC": "Resistencia del primario a la carcasa (porcelana)",
        "RPS": "Resistencia entre primario y secundario",
        "RSC": "Resistencia del secundario (S1-S2)",
        "RH": (
            "Resistencia del devanado (H)"
            if es_reactor else
            "Resistencia de H–X hacia el tanque"
            if es_auto else
            "Resistencia del devanado de alta (H)"
        ),
        "RX": "Resistencia del devanado de baja (X)",
        "RY": "Resistencia del devanado terciario (Y)",
        "RHX": (
            "Resistencia de H–X hacia el tanque"
            if es_auto else
            "Resistencia entre alta (H) y baja (X)"
        ),
        "RHY": "Resistencia entre alta (H) y terciario (Y)",
        "RXY": "Resistencia entre baja (X) y terciario (Y)",
        "RHXY": "Resistencia entre H–X y el terciario (Y)",
        "RH1": "Resistencia del devanado de alta, sección 1",
        "RH2": "Resistencia del devanado de alta, sección 2",
        "RAT": "Resistencia de la fase A a la carcasa",
        "RBT": "Resistencia de la fase B a la carcasa",
        "RCT": "Resistencia de la fase C a la carcasa",
        "RAD": "Resistencia entre las secciones A y D",
        "RAC": "Resistencia entre las secciones A y C",
        "RAB": "Resistencia entre las secciones A y B",
        "RBC": "Resistencia entre las secciones B y C",
        "RCD": "Resistencia entre las secciones C y D",
    }
    if "Generadores" in equipo:
        descripciones.update({
            "RAB": "Resistencia entre las fases A y B",
            "RBC": "Resistencia entre las fases B y C",
            "RAC": "Resistencia entre las fases A y C",
            "RRT": "Resistencia del rotor a la carcasa",
            "RAT": "Resistencia de la fase A a carcasa",
            "RBT": "Resistencia de la fase B a carcasa",
            "RCT": "Resistencia de la fase C a carcasa",
        })
    vistos = []
    for marca in _RE_CODIGO_RESISTENCIA_RA.finditer(plano):
        codigo = marca.group(0)
        if codigo not in vistos:
            vistos.append(codigo)
    return [
        (codigo, descripciones.get(codigo, "Resistencia de aislamiento"))
        for codigo in vistos
    ]


_CONEXION_VACIA = {"", "-----", "---", "—"}


def _leyenda_conexiones_ra(texto, prueba):
    """LÍNEA, TIERRA y GUARDA de la prueba, con el borne de cada columna."""
    del texto
    prueba = prueba or {}
    linea = str(prueba.get("linea") or "").strip()
    tierra = str(prueba.get("tierra") or "").strip()
    guarda = str(prueba.get("guarda") or "").strip()
    filas = []
    if linea not in _CONEXION_VACIA:
        filas.append((
            "LÍNEA", f"Conexión de línea (+): {linea}", "#DC2626",
        ))
    if tierra not in _CONEXION_VACIA:
        filas.append((
            "TIERRA", f"Conexión de tierra (-): {tierra}", "#111111",
        ))
    if guarda not in _CONEXION_VACIA:
        filas.append((
            "GUARDA", f"Conexión de guarda: {guarda}", "#2563EB",
        ))
    return filas


def _color_celda_bloque(ch, color):
    """Un trazo sin color propio es cable, igual que el resto del circuito."""
    if color == _TEXTO_BLOQUE and (ch in _TRAZOS_BLOQUE or ch in _ZIGZAG_BLOQUE):
        return _COLOR_TRAZO_BLOQUE
    return color


def _rejilla_bloques(texto):
    filas = []
    for linea in (texto or "").split("\n"):
        celdas = []
        color = _COLOR_TRAZO_BLOQUE
        inicio = 0
        for marca in _SGR_BLOQUE.finditer(linea):
            for ch in linea[inicio:marca.start()]:
                celdas.append((ch, _color_celda_bloque(ch, color)))
            numeros = [int(p) for p in marca.group(1).split(";") if p.isdigit()]
            color = _color_sgr_bloque(numeros, color)
            inicio = marca.end()
        for ch in linea[inicio:]:
            celdas.append((ch, _color_celda_bloque(ch, color)))
        filas.append(celdas)
    return filas


def _color_trazo_bloque(color):
    if str(color).lower() in _TRAZO_NEON_BLOQUE:
        return _COLOR_LINEA_BLOQUE
    return color


class _LienzoBloquesNeon(tk.Frame):
    """Diagramas de bloques con resplandor neón real (Matplotlib, canal alfa)."""

    def __init__(self, parent, titulo=""):
        super().__init__(parent, bg=RA_BG)
        self._texto = ""
        self._titulo = titulo
        self._job = None
        self._dibujando = False
        self._ancho = 1
        self._alto = 1
        self._encajando = False 
        self._tierra_en_tanque = False
        self._ground_en_tanque = False
        self._guarda_en_tanque = False
        self._tierra_en_tierra = False 
        self._tierra_en_devanado = False
        self._letras_linea = set()
        self._sitios_linea = set()
        self._sitios_tierra = set()
        self._sitios_guarda = set()
        self._cols_compartidas = 0
        self._filas_compartidas = 0
        self._alto_maximo = 0
        self._plano = False
        self._amarillos = []
        self._puntos_parpadeo = []
        self._turnos = []
        self._grupos = []
        self._fases = []
        self._artistas_medicion = []
        self._artistas_puntos = []
        self._todos_parpadeo = []
        self._fase_parpadeo = 0
        self._oyentes_parpadeo = []
        self._parpadeo = None
        self._parpadeo_on = True
        self._color_medicion = "#F76707"
        self._codigos_parpadeo = set()
        self._es_fp = False
        from matplotlib import font_manager
        if RA_FONT_PATH.is_file():
            self._fuente_titulo = font_manager.FontProperties(
                fname=str(RA_FONT_PATH), size=18, weight="bold",
            )
        else:
            self._fuente_titulo = font_manager.FontProperties(
                family="sans-serif", size=18, weight="bold",
            )
        self.fig = Figure(figsize=(5, 4), dpi=100, facecolor="#000000")
        self.ax = self.fig.add_subplot(111)
        self.fig.subplots_adjust(0, 0, 1, 1)
        from matplotlib.backends.backend_agg import FigureCanvasAgg
        self.canvas_mpl = FigureCanvasAgg(self.fig)
        self._etiqueta = tk.Label(self, bd=0, highlightthickness=0, bg="#FFFFFF")
        self._foto = None
        self.bind("<Destroy>", self._al_cerrar, add="+")

    def cargar(self, texto):
        self._texto = texto or ""
        if self._job is not None:
            try:
                self.after_cancel(self._job)
            except tk.TclError:
                pass
            self._job = None
        self._redibujar()

    def _programar(self, event=None):
        if self._dibujando or self._job is not None:
            return
        self._job = self.after(30, self._redibujar)

    def _volcar_etiqueta(self):
        """Pinta el diagrama en una etiqueta. El canvas de Matplotlib no se ve dentro del recuadro con scroll."""
        from PIL import Image, ImageTk
        self.canvas_mpl.draw()
        rgba = self.canvas_mpl.buffer_rgba()
        alto_px, ancho_px = rgba.shape[:2]
        if ancho_px < 2 or alto_px < 2:
            return
        imagen = Image.frombytes(
            "RGBA", (ancho_px, alto_px), rgba.tobytes(),
        )
        fondo = "#FFFFFF" if self._plano else "#000000"
        self._foto = ImageTk.PhotoImage(imagen)
        self._etiqueta.configure(image=self._foto, text="", bg=fondo)
        self.configure(bg=fondo, width=ancho_px, height=alto_px)
        self.grid_propagate(False)
        self.pack_propagate(False)
        self._etiqueta.place(x=0, y=0, width=ancho_px, height=alto_px)

    def _es_azul(self, color):
        return (
            str(color).lower() in _TRAZO_NEON_BLOQUE
            or str(color).lower() == _AZUL_NEON_SAPE.lower()
        )

    def _es_amarillo_medicion(self, color):
        texto = str(color).lstrip("#")
        if len(texto) != 6:
            return False
        try:
            r, g, b = int(texto[0:2], 16), int(texto[2:4], 16), int(texto[4:6], 16)
        except ValueError:
            return False
        return r > 220 and g > 220 and b < 80

    def _es_negro(self, color):
        texto = str(color).lstrip("#")
        if len(texto) != 6:
            return False
        try:
            r, g, b = int(texto[0:2], 16), int(texto[2:4], 16), int(texto[4:6], 16)
        except ValueError:
            return False
        return r < 40 and g < 40 and b < 40

    def _xy(self, x, y):
        return x / self._ancho, 1.0 - (y / self._alto)

    def _plot_neon(self, coords, color, filo=False):
        xs, ys = [], []
        pares = list(coords)
        for i in range(0, len(pares), 2):
            x, y = self._xy(pares[i], pares[i + 1])
            xs.append(x)
            ys.append(y)
        if len(xs) < 2:
            return None
        if self._plano:
            grosor = 2.4 if self._es_fp else 3.0
            linea, = self.ax.plot(
                xs, ys, color=color, linewidth=grosor,
                solid_capstyle="round",
                solid_joinstyle="miter" if filo else "round",
            )
            return linea
        halo = _AZUL_NEON_SAPE if self._es_azul(color) else color
        nucleo = "#FFFFFF" if self._es_azul(color) else color
        self.ax.plot(
            xs, ys, color=halo, linewidth=8, alpha=0.22,
            solid_capstyle="round", solid_joinstyle="round",
        )
        self.ax.plot(
            xs, ys, color=halo, linewidth=4, alpha=0.55,
            solid_capstyle="round", solid_joinstyle="round",
        )
        linea, = self.ax.plot(
            xs, ys, color=nucleo, linewidth=1.6,
            solid_capstyle="round", solid_joinstyle="round",
        )
        return linea

    def _redibujar(self):
        self._job = None
        self._dibujando = True
        try:
            self._redibujar_cuerpo()
        except Exception:
            import traceback
            self._etiqueta.place_forget()
            self._etiqueta.pack(anchor="nw")
            self._etiqueta.configure(
                image="",
                text=traceback.format_exc()[-800:],
                fg="#FF0000",
                bg="#FFFFFF",
                font=("Consolas", 9),
                justify="left",
            )
            self.grid_propagate(True)
        finally:
            self._dibujando = False

    def _redibujar_cuerpo(self):
        self._detener_parpadeo()
        self._amarillos = []
        self._puntos_parpadeo = []
        self._turnos = []
        self._grupos = []
        self._fases = []
        self._artistas_medicion = []
        self._artistas_puntos = []
        self._todos_parpadeo = []
        self._fase_parpadeo = 0
        self._parpadeo_on = True
        self._plano = (self._titulo or "").strip().upper() in ("CONEXIONES", "MEDICIÓN")
        fondo = "#FFFFFF" if self._plano else "#000000"
        self.fig.patch.set_facecolor(fondo)
        self.configure(bg=fondo)
        self.ax.clear()
        self.ax.set_facecolor(fondo)
        self.ax.set_xlim(0, 1)
        self.ax.set_ylim(0, 1)
        self.ax.axis("off")

        filas = _rejilla_bloques(self._texto)
        while filas and not any(ch.strip() for ch, _ in filas[-1]):
            filas.pop()
        while filas and not any(ch.strip() for ch, _ in filas[0]):
            filas.pop(0)

        if not filas:
            self.canvas_mpl.draw_idle()
            return

        c_izq = None
        c_der = -1
        for fila in filas:
            for c, (glifo, _) in enumerate(fila):
                if glifo.strip():
                    if c_izq is None or c < c_izq:
                        c_izq = c
                    if c > c_der:
                        c_der = c
        if c_izq is None:
            self.canvas_mpl.draw_idle()
            return
        n_cols = c_der - c_izq + 1
        recortadas = []
        for fila in filas:
            trozo = list(fila[c_izq:c_der + 1])
            if len(trozo) < n_cols:
                trozo.extend(
                    [(" ", _COLOR_TRAZO_BLOQUE)] * (n_cols - len(trozo))
                )
            recortadas.append(trozo)
        filas = recortadas
        self._bornes = []
        if self._plano:
            if self._es_fp:
                _estilo_plano_fp(
                    filas,
                    medicion=(
                        (self._titulo or "").strip().upper() == "MEDICIÓN"
                    ),
                    naranja=self._color_medicion,
                    ground_en_tanque=getattr(self, "_ground_en_tanque", False),
                )
            elif (self._titulo or "").strip().upper() == "MEDICIÓN":
                _estilo_plano_medicion(filas, self._color_medicion)
            else:
                _estilo_plano_conexiones(
                    filas, self._tierra_en_tanque, self._guarda_en_tanque,
                    self._tierra_en_tierra, self._letras_linea,
                    self._tierra_en_devanado,
                )
                self._bornes = _teñir_cables_conexion(
                    filas,
                    pintar_tierra=self._tierra_en_tierra,
                    pintar_tanque=self._tierra_en_tanque,
                    pintar_caja=self._tierra_en_devanado,
                )
                for fila in filas:
                    for i, (glifo, _color) in enumerate(fila):
                        if glifo != " ":
                            fila[i] = (glifo, RA_AZUL_MARINO)
                _teñir_roles_junto_a_bus(filas)
                self._bornes = [
                    (ancla, fila_b, col, RA_AZUL_MARINO)
                    for ancla, fila_b, col, _color in self._bornes
                ]

        cols = max(n_cols, self._cols_compartidas)
        nfil = max(len(filas), self._filas_compartidas)

        # Tamaño de celda FIJO: el diagrama siempre mide lo mismo
        cw = 11.0 if self._plano else 12.0
        alto = 16.0 if self._plano else 20.0
        fuente = 9

        dw = cols * cw
        dh = nfil * alto

        pad_x = 20
        pad_y = 8 if self._plano else 24
        reserva_titulo = 0 if self._plano else (34 if self._titulo else 0)
        holgura = 12 if self._plano else 28

        try:
            pantalla_w = self.winfo_screenwidth()
            pantalla_h = self.winfo_screenheight()
        except tk.TclError:
            pantalla_w, pantalla_h = 1920, 1080
        max_w = max(360, pantalla_w - 260 - 220)
        if self._alto_maximo:
            max_h = self._alto_maximo
        else:
            max_h = max(280, pantalla_h - 480)
        natural_w = dw + pad_x * 2 + holgura
        natural_h = dh + pad_y * 2 + reserva_titulo + holgura
        escala = min(1.0, max_w / natural_w, max_h / natural_h)
        if escala < 1:
            cw *= escala
            alto *= escala
            dw = cols * cw
            dh = nfil * alto
            fuente = max(6, min(9, int(alto * 0.42)))

        ox = pad_x + holgura / 2
        oy = reserva_titulo + pad_y + (alto if self._plano else 0)
        ancho_total = int(ox + dw + pad_x + holgura / 2)
        alto_total = int(oy + dh + pad_y + holgura / 2)

        dpi = self.fig.get_dpi()
        self.fig.set_size_inches(ancho_total / dpi, alto_total / dpi)
        self._ancho = ancho_total
        self._alto = alto_total

        if self._titulo and not self._plano:
            self.ax.text(
                0.5, 1.0 - 16 / alto_total, self._titulo,
                color=AMARILLO_BRILLANTE,
                ha="center", va="center",
                fontproperties=self._fuente_titulo,
                transform=self.ax.transAxes,
            )

        self._cajas_redondas = []
        self._preparar_cajas_redondas(filas)
        self._segs = []
        self._sin_trazo = set()
        for r, fila in enumerate(filas):
            self._zigzags(filas, r, ox, oy, cw, alto)
        def tinta_de(color):
            mide_local = (self._titulo or "").strip().upper() == "MEDICIÓN"
            if self._plano:
                if mide_local and self._es_amarillo_medicion(color):
                    return self._color_medicion, 1.0
                if self._es_azul(color):
                    return "#334155", 1.0
                return color, 1.0
            tinta = _AZUL_NEON_SAPE if self._es_azul(color) else color
            alfa = 1.0
            if mide_local:
                if self._es_amarillo_medicion(color):
                    tinta = AMARILLO_BRILLANTE
                else:
                    tinta = _AZUL_NEON_SAPE
                    alfa = 0.38
            elif self._es_negro(color):
                tinta = "#FFFFFF"
            return tinta, alfa

        from matplotlib import font_manager
        ruta_negrita = Path(r"C:\Windows\Fonts\consolab.ttf")
        if ruta_negrita.is_file():
            fuente_diag = font_manager.FontProperties(
                fname=str(ruta_negrita), size=fuente,
            )
        else:
            fuente_diag = font_manager.FontProperties(
                family="Consolas", size=fuente, weight="black",
            )

        for r, fila in enumerate(filas):
            c = 0
            while c < len(fila):
                glifo, color = fila[c]
                if (r, c) in self._sin_trazo or glifo in _ZIGZAG_BLOQUE or glifo == " ":
                    c += 1
                    continue
                if glifo == "○":
                    self._circulo(c, r, ox, oy, cw, alto,
                                  _color_trazo_bloque(color))
                    c += 1
                    continue
                if glifo in _TRAZOS_BLOQUE:
                    self._trazo(
                        glifo, c, r, ox, oy, cw, alto,
                        _color_trazo_bloque(color), filas,
                    )
                    c += 1
                    continue
                fin = c + 1
                while fin < len(fila):
                    siguiente, color_sig = fila[fin]
                    if (
                        (r, fin) in self._sin_trazo
                        or siguiente in _ZIGZAG_BLOQUE
                        or siguiente in (" ", "○")
                        or siguiente in _TRAZOS_BLOQUE
                        or color_sig != color
                    ):
                        break
                    fin += 1
                texto = "".join(fila[i][0] for i in range(c, fin))
                if texto == "LINEA":
                    texto = "LÍNEA"
                if (
                    (self._titulo or "").strip().upper() == "CONEXIONES"
                    and not self._es_fp
                ):
                    caja = self._caja_en(r, c)
                    if caja and self._color_rol(self._sitios_caja(filas, caja)):
                        c = fin
                        continue
                y_px = oy + r * alto + alto / 2
                if texto.strip() in ("TANQUE", "CARCASA"):
                    y_px -= alto
                if (
                    texto.strip() == "TIERRA"
                    and r > 0
                    and any(
                        filas[r - 1][k][0] == "╧"
                        for k in range(
                            max(0, c - 2),
                            min(len(filas[r - 1]), fin + 2),
                        )
                    )
                ):
                    y_px += alto
                if self._rotulo_bajo_zigzag(filas, r, c, fin, texto):
                    y_px += alto * 0.85
                x_px = ox + (c + fin) * cw / 2
                if self._es_fp and texto.strip() in _CAPS_FP:
                    # El rótulo no toca las placas: baja si la capacitancia
                    # está encima y se corre a la derecha si está al lado.
                    arriba = filas[r - 1] if r > 0 else []
                    if any(
                        arriba[k][0] in "┤├"
                        for k in range(max(0, c - 3), min(len(arriba), fin + 3))
                    ):
                        y_px += alto * 0.5
                    elif any(
                        fila[k][0] in "┴┬" for k in range(max(0, c - 6), c)
                    ):
                        x_px += cw * 1.3
                x, y = self._xy(x_px, y_px)
                tinta, alfa = tinta_de(color)
                artista = self.ax.text(
                    x, y, texto, color=tinta, ha="center", va="center",
                    fontproperties=fuente_diag, alpha=alfa,
                )
                if (
                    self._es_fp
                    and texto.strip() in _CAPS_FP
                    and str(color).lower() == str(self._color_medicion).lower()
                ):
                    self._amarillos.append(artista)
                if (
                    self._es_fp
                    and (self._titulo or "").strip().upper() == "CONEXIONES"
                    and texto.strip() in ("HV", "GROUND", "GUARD", "UST")
                ):
                    artista.set_fontweight("black")
                    self._amarillos.append(artista)
                if (
                    (self._titulo or "").strip().upper() == "MEDICIÓN"
                    and not self._es_fp
                    and texto.strip() in self._codigos_parpadeo
                ):
                    self._agregar_turno(texto.strip(), artista)
                self._anotar_conexion(artista, tinta)
                c = fin
        self._volcar_segmentos()
        self._dibujar_cajas_redondas(ox, oy, cw, alto)
        self._dibujar_bornes(ox, oy, cw, alto, filas)
        self._ordenar_turnos()
        if self._grupos:
            self._fase_parpadeo = 0
            self._mostrar_grupo(0)

        self.configure(width=ancho_total, height=alto_total)
        self._volcar_etiqueta()
        self._encajar_ventana()
        if self._grupos or self._amarillos or self._puntos_parpadeo:
            self._parpadeo = self.after(450, self._parpadear_amarillo)

    def _detener_parpadeo(self):
        if self._parpadeo is not None:
            try:
                self.after_cancel(self._parpadeo)
            except tk.TclError:
                pass
            self._parpadeo = None

    def _al_cerrar(self, event):
        if event.widget is self:
            self._detener_parpadeo()

    def _agregar_turno(self, clave, artista, junto=True):
        if junto:
            for turno in self._turnos:
                if turno[0] == clave:
                    turno[1].append(artista)
                    return
        self._turnos.append([clave, [artista]])

    def _ordenar_turnos(self):
        """Medición junta. En conexiones, cada recuadro de color parpadea solo."""
        roles = ("LÍNEA", "TIERRA", "GUARDA")
        por_clave = {}
        medicion = []
        for clave, artistas in self._turnos:
            por_clave.setdefault(clave, []).extend(artistas)
            if clave not in roles:
                medicion.extend(artistas)
        self._por_clave = por_clave
        self._artistas_medicion = medicion
        self._artistas_puntos = [
            artista for rol in roles for artista in por_clave.get(rol, ())
        ]
        if (self._titulo or "").strip().upper() == "CONEXIONES":
            self._todos_parpadeo = self._artistas_puntos
            self._grupos = (
                [("CONEXIONES", self._artistas_puntos)]
                if self._artistas_puntos else []
            )
            self._fases = (
                [("CONEXIONES", False), ("CONEXIONES", True)]
                if self._artistas_puntos else []
            )
        else:
            self._todos_parpadeo = medicion
            self._grupos = [("MEDICION", medicion)] if medicion else []
            self._fases = (
                [("MEDICION", False), ("MEDICION", True)] if medicion else []
            )

    def _avisar_turno(self, clave):
        for oir in self._oyentes_parpadeo:
            oir(clave)

    def _mostrar_grupo(self, indice):
        if self._fases:
            clave, apagado = self._fases[indice % len(self._fases)]
            if clave in ("MEDICION", "CONEXIONES"):
                artistas = (
                    self._artistas_medicion if clave == "MEDICION"
                    else self._artistas_puntos
                )
                for artista in artistas:
                    artista.set_alpha(0.0 if apagado else 1.0)
                if clave == "MEDICION":
                    self._avisar_turno(None if apagado else "MEDICION")
                else:
                    self._avisar_turno("CONEXIONES_OFF" if apagado else "CONEXIONES")
            else:
                for codigo, artistas in self._por_clave.items():
                    alfa = 0.0 if apagado and codigo == clave else 1.0
                    for artista in artistas:
                        artista.set_alpha(alfa)
                self._avisar_turno(clave if apagado else "")
            return
        nombre = None
        for i, (grupo, artistas) in enumerate(self._grupos):
            alfa = 1.0 if i == indice else 0.0
            for artista in artistas:
                artista.set_alpha(alfa)
            if i == indice:
                nombre = grupo
        self._avisar_turno(nombre)

    def _parpadear_amarillo(self):
        self._parpadeo = None
        if not self._grupos and not self._amarillos and not self._puntos_parpadeo:
            return
        try:
            if not self.winfo_exists():
                return
        except tk.TclError:
            return
        if self._fases:
            self._fase_parpadeo = (self._fase_parpadeo + 1) % len(self._fases)
            self._mostrar_grupo(self._fase_parpadeo)
        elif self._grupos:
            self._parpadeo_on = not self._parpadeo_on
            alfa = 1.0 if self._parpadeo_on else 0.0
            for artista in self._grupos[0][1]:
                artista.set_alpha(alfa)
            self._avisar_turno(self._grupos[0][0] if self._parpadeo_on else None)
        else:
            self._parpadeo_on = not self._parpadeo_on
            alfa = 1.0 if self._parpadeo_on else 0.0
            for artista in self._amarillos:
                artista.set_alpha(alfa)
            for punto in self._puntos_parpadeo:
                punto.set_alpha(alfa)
            if self._es_fp:
                # La leyenda de FP parpadea al ritmo del diagrama.
                if (self._titulo or "").strip().upper() == "MEDICIÓN":
                    self._avisar_turno(
                        "MEDICION" if self._parpadeo_on else None,
                    )
                else:
                    self._avisar_turno(
                        "CONEXIONES" if self._parpadeo_on
                        else "CONEXIONES_OFF",
                    )
        self._volcar_etiqueta()
        self._parpadeo = self.after(450, self._parpadear_amarillo)

    def _encajar_ventana(self):
        if self._encajando:
            return
        ventana = self.winfo_toplevel()
        try:
            if not ventana.winfo_exists():
                return
        except tk.TclError:
            return
        panel = self.master
        frame = getattr(self, "_marco_paso", None)
        if frame is None and panel is not None:
            frame = panel.master
        app = ventana.master
        if frame is None or not hasattr(app, "_ajustar_ventana_ra"):
            return
        self._encajando = True
        ancho, alto = int(self._ancho), int(self._alto)

        def _luego(marco=frame, hoja=panel, aw=ancho, al=alto):
            try:
                if app.winfo_exists():
                    app._ajustar_ventana_ra(marco, hoja, aw, al)
            except tk.TclError:
                pass
            self._soltar_encaje()

        # Después de pintar. Si la ventana cambia de tamaño a mitad
        # del armado, el segundo diagrama no llega a crearse.
        self.after(60, _luego)

    def _soltar_encaje(self):
        self._encajando = False

    def _anotar(self, x1, y1, x2, y2, color):
        self._segs.append((x1, y1, x2, y2, color))

    def _unir_tramos(self, tramos):
        orden = sorted(tramos)
        unidos = []
        inicio, fin = orden[0]
        for a, b in orden[1:]:
            if a <= fin + 3:
                fin = max(fin, b)
            else:
                unidos.append((inicio, fin))
                inicio, fin = a, b
        unidos.append((inicio, fin))
        return unidos

    _ROTULOS_CAJA_REDONDA = {
        "ALTA", "BAJA", "TERCIARIO", "LINEA", "LÍNEA", "GUARDA", "TIERRA",
        "H", "X", "Y", "P", "S", "A", "B", "C", "D",
        "H-X", "HX", "H1", "H2", "X1", "X2", "Y1", "Y2",
    }

    def _preparar_cajas_redondas(self, filas):
        """Quita todo marco cuadrado para redibujarlo con puntas redondas."""
        if not self._plano:
            return
        nfil = len(filas)
        for r, fila in enumerate(filas):
            c = 0
            ncols = len(fila)
            while c < ncols:
                if fila[c][0] not in "┌╔":
                    c += 1
                    continue
                cierre = None
                for k in range(c + 1, min(ncols, c + 24)):
                    glifo = fila[k][0]
                    if glifo in "┐╗":
                        cierre = k
                        break
                    if glifo not in "─┬┴═╦╩┼╬":
                        break
                if cierre is None:
                    c += 1
                    continue
                abajo = None
                for rr in range(r + 1, min(nfil, r + 8)):
                    if c >= len(filas[rr]):
                        break
                    glifo = filas[rr][c][0]
                    if glifo in "└╚":
                        abajo = rr
                        break
                    if glifo not in "│║├┤┼╠╣╬":
                        break
                if (
                    abajo is None
                    or cierre >= len(filas[abajo])
                    or filas[abajo][cierre][0] not in "┘╝"
                ):
                    c += 1
                    continue
                color = fila[c][1]
                for k in range(c, cierre + 1):
                    for rr in (r, abajo):
                        if (
                            k < len(filas[rr])
                            and filas[rr][k][0] in _TRAZOS_BLOQUE
                        ):
                            filas[rr][k] = (" ", filas[rr][k][1])
                for rr in range(r + 1, abajo):
                    for k in (c, cierre):
                        if (
                            k < len(filas[rr])
                            and filas[rr][k][0] in _TRAZOS_BLOQUE
                        ):
                            filas[rr][k] = (" ", filas[rr][k][1])
                color_caja = color
                if (
                    self._es_fp
                    and (self._titulo or "").strip().upper() == "CONEXIONES"
                ):
                    texto_caja = "".join(
                        filas[rr][k][0]
                        for rr in range(r, abajo + 1)
                        for k in range(c, cierre + 1)
                        if k < len(filas[rr])
                    )
                    for rol_txt, color_rol in _COLOR_CAJA_ROL_FP:
                        if rol_txt in texto_caja:
                            color_caja = color_rol
                            break
                self._cajas_redondas.append((r, abajo, c, cierre, color_caja))
                c = cierre + 1

    def _es_color_conexion(self, color):
        return self._rol_de_color(color) is not None

    def _rol_de_color(self, color):
        return {
            "#dc2626": "LÍNEA",
            "#111111": "TIERRA",
            "#2563eb": "GUARDA",
        }.get(str(color).lower())

    def _anotar_conexion(self, artista, color):
        rol = self._rol_de_color(color)
        if artista is not None and rol:
            self._agregar_turno(rol, artista)

    def _color_devanado(self, sitio):
        if sitio in getattr(self, "_sitios_linea", ()):
            return "#DC2626"
        if sitio in getattr(self, "_sitios_tierra", ()):
            return "#111111"
        if sitio in getattr(self, "_sitios_guarda", ()):
            return "#2563EB"
        return None

    def _teñir_hacia_vertical(self, filas, fila, col, color):
        """Pinta el cable y la resistencia hacia la izquierda, hasta el bus."""
        c = col - 1
        while c >= 0 and fila < len(filas) and c < len(filas[fila]):
            glifo = filas[fila][c][0]
            if glifo in "│║":
                break
            if glifo not in _TRAZOS_BLOQUE and glifo not in _ZIGZAG_BLOQUE:
                break
            filas[fila][c] = (glifo, color)
            c -= 1

    def _teñir_ramales_conexion(self, filas):
        """Devanado y su resistencia, del color de LÍNEA, TIERRA o GUARDA."""
        if self._es_fp or not filas:
            return
        letras = {"H", "X", "Y"}

        def tono_de(caja):
            for sitio in self._sitios_caja(filas, caja):
                if sitio not in letras:
                    continue
                tono = self._color_devanado(sitio)
                if tono:
                    return tono
            return None

        nuevas = []
        for r, abajo, c, cierre, color in self._cajas_redondas:
            tono = tono_de((r, abajo, c, cierre))
            if tono:
                color = tono
                for rr in range(r, abajo + 1):
                    self._teñir_hacia_vertical(filas, rr, c, tono)
            nuevas.append((r, abajo, c, cierre, color))
        self._cajas_redondas = nuevas

        nfil = len(filas)
        for r, fila in enumerate(filas):
            c = 0
            while c < len(fila):
                if fila[c][0] not in "┌╔":
                    c += 1
                    continue
                cierre = None
                for k in range(c + 1, min(len(fila), c + 18)):
                    glifo = fila[k][0]
                    if glifo in "┐╗":
                        cierre = k
                        break
                    if glifo not in "─┬┴═╦╩┼╬":
                        break
                if cierre is None:
                    c += 1
                    continue
                abajo = None
                for rr in range(r + 1, min(nfil, r + 8)):
                    if c >= len(filas[rr]):
                        break
                    glifo = filas[rr][c][0]
                    if glifo in "└╚":
                        abajo = rr
                        break
                    if glifo not in "│║├┤┼╠╣╬ ":
                        break
                if abajo is None:
                    c += 1
                    continue
                tono = tono_de((r, abajo, c, cierre))
                if tono:
                    for cc in range(c, cierre + 1):
                        for rr in (r, abajo):
                            if (
                                cc < len(filas[rr])
                                and filas[rr][cc][0] in _TRAZOS_BLOQUE
                            ):
                                filas[rr][cc] = (filas[rr][cc][0], tono)
                    for rr in range(r, abajo + 1):
                        for cc in (c, cierre):
                            if (
                                cc < len(filas[rr])
                                and filas[rr][cc][0] in _TRAZOS_BLOQUE
                            ):
                                filas[rr][cc] = (filas[rr][cc][0], tono)
                        self._teñir_hacia_vertical(filas, rr, c, tono)
                c = cierre + 1
        self._teñir_mitad_tanque(filas)

    def _teñir_mitad_tanque(self, filas):
        """TIERRA en el tanque: la vertical negra desde arriba hasta la mitad."""
        if "TANQUE" not in getattr(self, "_sitios_tierra", ()):
            return
        col_bus = None
        fila_ini = None
        for r, fila in enumerate(filas):
            chars = "".join(ch for ch, _ in fila).replace("CARCASA", "TANQUE ")
            i = chars.find("TANQUE")
            if i < 0:
                continue
            centro = i + len("TANQUE") // 2
            for rr in range(r + 1, min(len(filas), r + 8)):
                for dc in range(-8, 9):
                    cc = centro + dc
                    if (
                        0 <= cc < len(filas[rr])
                        and filas[rr][cc][0] in "│║"
                    ):
                        if (
                            col_bus is None
                            or abs(cc - centro) < abs(col_bus - centro)
                        ):
                            col_bus = cc
                if col_bus is not None:
                    fila_ini = rr
                    break
            break
        if col_bus is None:
            return
        tramo = []
        for r in range(fila_ini, len(filas)):
            if col_bus >= len(filas[r]):
                break
            glifo = filas[r][col_bus][0]
            if glifo == "╧":
                break
            if glifo in "│║├┤┼╠╣╬╪╦╩":
                tramo.append(r)
            elif tramo:
                break
        if not tramo:
            return
        for r in tramo[: max(1, (len(tramo) + 1) // 2)]:
            glifo = filas[r][col_bus][0]
            filas[r][col_bus] = (glifo, "#111111")

    def _dibujar_cajas_redondas(self, ox, oy, cw, alto):
        if not self._cajas_redondas:
            return
        radio = min(cw, alto) * 0.42
        for r, abajo, c, cierre, color in self._cajas_redondas:
            x0 = ox + c * cw
            y0 = oy + r * alto
            x1 = ox + (cierre + 1) * cw
            y1 = oy + (abajo + 1) * alto
            curva = min(radio, (x1 - x0) / 2 - 0.4, (y1 - y0) / 2 - 0.4)
            if curva < 1:
                continue
            borde = RA_AZUL_MARINO if self._es_azul(color) else color
            grosor = (
                2.4 if str(borde).lower() in ("#ff0000", "#000000", "#3b82f6")
                else 3.0
            )
            puntos = []
            puntos += self._arco_caja(x1 - curva, y0 + curva, curva, math.pi / 2, 0)
            puntos += self._arco_caja(x1 - curva, y1 - curva, curva, 0, -math.pi / 2)
            puntos += self._arco_caja(x0 + curva, y1 - curva, curva, -math.pi / 2, -math.pi)
            puntos += self._arco_caja(x0 + curva, y0 + curva, curva, math.pi, math.pi / 2)
            xs = [px for px, _py in puntos]
            ys = [py for _px, py in puntos]
            linea, = self.ax.plot(
                xs + [xs[0]], ys + [ys[0]], color=borde, linewidth=grosor,
                solid_capstyle="round", solid_joinstyle="round",
            )
            self._anotar_conexion(linea, borde)

    def _trazo_en(self, filas, r, c):
        if r < 0 or c < 0 or r >= len(filas) or c >= len(filas[r]):
            return False
        return filas[r][c][0] in _TRAZOS_BLOQUE or filas[r][c][0] in _ZIGZAG_BLOQUE

    def _puntos_devanados(self, filas):
        """Punto solo en la entrada izquierda del devanado, donde llega el cable."""
        puntos = []
        vistos = set()

        def agregar(fila, col):
            clave = ("w", fila, col)
            if clave in vistos or not self._trazo_en(filas, fila, col - 1):
                return
            vistos.add(clave)
            puntos.append(("w", fila, col, RA_AZUL_MARINO))

        for r, abajo, c, _cierre, _color in getattr(self, "_cajas_redondas", ()):
            for rr in range(r, abajo + 1):
                agregar(rr, c)

        nfil = len(filas)
        for r, fila in enumerate(filas):
            c = 0
            while c < len(fila):
                if fila[c][0] not in "┌╔":
                    c += 1
                    continue
                cierre = None
                for k in range(c + 1, min(len(fila), c + 18)):
                    glifo = fila[k][0]
                    if glifo in "┐╗":
                        cierre = k
                        break
                    if glifo not in "─┬┴═╦╩┼╬":
                        break
                if cierre is None:
                    c += 1
                    continue
                abajo = None
                for rr in range(r + 1, min(nfil, r + 8)):
                    if c >= len(filas[rr]):
                        break
                    glifo = filas[rr][c][0]
                    if glifo in "└╚":
                        abajo = rr
                        break
                    if glifo not in "│║├┤┼╠╣╬ ":
                        break
                if abajo is None:
                    c += 1
                    continue
                for rr in range(r, abajo + 1):
                    agregar(rr, c)
                c = cierre + 1
        return puntos

    def _puntos_tanque(self, filas):
        """Extremo superior del bus y el símbolo de tierra."""
        puntos = []
        for r, fila in enumerate(filas):
            chars = "".join(ch for ch, _ in fila).replace("CARCASA", "TANQUE ")
            i = chars.find("TANQUE")
            if i < 0:
                continue
            centro = i + len("TANQUE") // 2
            col_bus = None
            for rr in range(r + 1, min(len(filas), r + 6)):
                for dc in range(-8, 9):
                    cc = centro + dc
                    if (
                        0 <= cc < len(filas[rr])
                        and filas[rr][cc][0] in "│║"
                    ):
                        if (
                            col_bus is None
                            or abs(cc - centro) < abs(col_bus - centro)
                        ):
                            col_bus = cc
                if col_bus is not None:
                    puntos.append(("c", rr, col_bus, RA_AZUL_MARINO))
                    break
            break
        for r, fila in enumerate(filas):
            for c, (ch, _color) in enumerate(fila):
                if ch == "╧":
                    puntos.append(("c", r, c, RA_AZUL_MARINO))
        return puntos

    def _caja_del_punto(self, filas, fila, col):
        for r, abajo, c, cierre, _color in getattr(self, "_cajas_redondas", ()):
            if c == col and r <= fila <= abajo:
                return (r, abajo, c, cierre)
        if not filas:
            return None
        nfil = len(filas)
        for r, fila_r in enumerate(filas):
            if col >= len(fila_r) or fila_r[col][0] not in "┌╔":
                continue
            cierre = None
            for k in range(col + 1, min(len(fila_r), col + 18)):
                glifo = fila_r[k][0]
                if glifo in "┐╗":
                    cierre = k
                    break
                if glifo not in "─┬┴═╦╩┼╬":
                    break
            if cierre is None:
                continue
            abajo = None
            for rr in range(r + 1, min(nfil, r + 8)):
                if col >= len(filas[rr]):
                    break
                glifo = filas[rr][col][0]
                if glifo in "└╚":
                    abajo = rr
                    break
                if glifo not in "│║├┤┼╠╣╬ ":
                    break
            if abajo is not None and r <= fila <= abajo:
                return (r, abajo, col, cierre)
        return None

    def _sitios_caja(self, filas, caja):
        r, abajo, c, cierre = caja
        letras = []
        for rr in range(r, abajo + 1):
            if rr >= len(filas):
                break
            for k in range(c, min(cierre + 1, len(filas[rr]))):
                glifo = filas[rr][k][0]
                if glifo.isalpha():
                    letras.append(glifo)
        texto = "".join(letras).upper()
        sitios = []
        for nombre, sitio in (
            ("ROTOR", "ROTOR"),
            ("TERCIARIO", "Y"),
            ("SECUNDARIO", "S"),
            ("PRIMARIO", "P"),
            ("ALTA", "H"),
            ("BAJA", "X"),
        ):
            if nombre in texto:
                sitios.append(sitio)
                texto = texto.replace(nombre, "")
        for glifo in texto:
            if glifo in "HXYPSABCD":
                sitios.append(glifo)
        return list(dict.fromkeys(sitios))

    def _sitios_punto(self, filas, ancla, fila, col):
        if (
            filas is not None
            and 0 <= fila < len(filas)
            and col < len(filas[fila])
            and filas[fila][col][0] == "╧"
        ):
            return ["TIERRA"]
        if ancla == "c":
            return ["TANQUE"]
        if ancla != "w" or filas is None:
            return []
        caja = self._caja_del_punto(filas, fila, col)
        if caja is None:
            return []
        return self._sitios_caja(filas, caja)

    def _color_rol(self, sitios):
        if not sitios:
            return None
        for sitios_rol, color in (
            (getattr(self, "_sitios_linea", ()), "#DC2626"),
            (getattr(self, "_sitios_tierra", ()), "#111111"),
            (getattr(self, "_sitios_guarda", ()), "#2563EB"),
        ):
            if any(sitio in sitios_rol for sitio in sitios):
                return color
        return None

    def _caja_en(self, fila, col):
        for r, abajo, c, cierre, _color in getattr(self, "_cajas_redondas", ()):
            if r <= fila <= abajo and c <= col <= cierre:
                return (r, abajo, c, cierre)
        return None

    def _dibujar_bornes(self, ox, oy, cw, alto, filas=None):
        """En CONEXIONES, el rol queda centrado dentro del devanado y parpadea."""
        if (self._titulo or "").strip().upper() != "CONEXIONES" or not filas:
            return
        nombres = {
            "#DC2626": "LÍNEA",
            "#111111": "TIERRA",
            "#2563EB": "GUARDA",
        }
        tamano = max(7, int(alto * 0.5))
        vistos = set()
        for r, abajo, c, cierre, _color in self._cajas_redondas:
            caja = (r, abajo, c, cierre)
            if caja in vistos:
                continue
            color = self._color_rol(self._sitios_caja(filas, caja))
            nombre = nombres.get(color or "")
            if not nombre:
                continue
            vistos.add(caja)
            x, y = self._xy(
                ox + (c + cierre + 1) * cw / 2,
                oy + (r + abajo + 1) * alto / 2,
            )
            artista = self.ax.text(
                x, y, nombre, color=color, ha="center", va="center",
                fontsize=tamano, fontweight="bold", zorder=8,
            )
            self._agregar_turno(nombre, artista)
        if "TANQUE" in getattr(self, "_sitios_tierra", ()):
            for ancla, fila, col, _color in self._puntos_tanque(filas):
                if not (
                    0 <= fila < len(filas)
                    and col < len(filas[fila])
                    and filas[fila][col][0] in "│║"
                ):
                    continue
                x, y = self._xy(
                    ox + col * cw - cw * 0.35,
                    oy + fila * alto + alto / 2,
                )
                artista = self.ax.text(
                    x, y, "TIERRA", color="#111111", ha="right", va="center",
                    fontsize=tamano, fontweight="bold", zorder=8,
                )
                self._agregar_turno("TIERRA", artista)
                break

    def _arco_caja(self, cx, cy, radio, a0, a1, pasos=6):
        puntos = []
        for i in range(pasos + 1):
            angulo = a0 + (a1 - a0) * i / pasos
            puntos.append(self._xy(
                cx + radio * math.cos(angulo),
                cy - radio * math.sin(angulo),
            ))
        return puntos

    def _volcar_segmentos(self):
        horizontales, verticales = {}, {}
        for x1, y1, x2, y2, color in self._segs:
            if abs(y1 - y2) <= abs(x1 - x2):
                y = round((y1 + y2) / 2, 1)
                a, b = (x1, x2) if x1 <= x2 else (x2, x1)
                horizontales.setdefault((y, color), []).append((a, b))
            else:
                x = round((x1 + x2) / 2, 1)
                a, b = (y1, y2) if y1 <= y2 else (y2, y1)
                verticales.setdefault((x, color), []).append((a, b))
        # FP: los trazos en el color de medición son las placas de la
        # capacitancia medida y parpadean junto con su rótulo.
        placa_medida = (
            self._es_fp
            and (self._titulo or "").strip().upper() == "MEDICIÓN"
        )

        def volcar(coords, color):
            artista = self._plot_neon(coords, color)
            self._anotar_conexion(artista, color)
            if (
                placa_medida and artista is not None
                and str(color).lower() == str(self._color_medicion).lower()
            ):
                self._amarillos.append(artista)

        for (y, color), tramos in horizontales.items():
            for a, b in self._unir_tramos(tramos):
                volcar((a, y, b, y), color)
        for (x, color), tramos in verticales.items():
            for a, b in self._unir_tramos(tramos):
                volcar((x, a, x, b), color)

    def _circulo(self, c, r, ox, oy, cw, ch, color):
        cx = ox + c * cw + cw / 2
        cy = oy + r * ch + ch / 2
        radio = min(cw, ch) * 0.28
        x, y = self._xy(cx, cy)
        rx, ry = radio / self._ancho, radio / self._alto
        if self._plano:
            self.ax.add_patch(patches.Ellipse(
                (x, y), rx * 2, ry * 2, fill=False,
                edgecolor="#334155" if self._es_azul(color) else color,
                linewidth=1.6 if self._es_fp else 2.6,
            ))
            return
        halo = _AZUL_NEON_SAPE if self._es_azul(color) else color
        self.ax.add_patch(patches.Ellipse(
            (x, y), rx * 2.8, ry * 2.8, fill=False,
            edgecolor=halo, linewidth=5, alpha=0.25,
        ))
        self.ax.add_patch(patches.Ellipse(
            (x, y), rx * 2, ry * 2, fill=False,
            edgecolor="#FFFFFF" if self._es_azul(color) else color, linewidth=1.4,
        ))

    def _puente_lado(self, filas, r, c, hacia):
        """Alarga el cable hasta el eje de un │ vecino."""
        cc = c + hacia
        if r < 0 or r >= len(filas) or cc < 0 or cc >= len(filas[r]):
            return False
        spec = _TRAZOS_BLOQUE.get(filas[r][cc][0], "").lower().replace(".", "")
        if not spec:
            return False
        entra = "e" if hacia < 0 else "w"
        return ("n" in spec or "s" in spec) and entra not in spec

    def _puente(self, filas, r, c, hacia):
        rr = r + hacia
        if rr < 0 or rr >= len(filas) or c >= len(filas[rr]):
            return False
        spec = _TRAZOS_BLOQUE.get(filas[rr][c][0], "").lower().replace(".", "")
        if not spec:
            return False
        return ("w" in spec or "e" in spec) and not (("s" if hacia < 0 else "n") in spec)

    def _junto_a_tierra(self, filas, r, c):
        for dc in (-1, 1):
            cc = c + dc
            if 0 <= cc < len(filas[r]) and filas[r][cc][0] == "╧":
                return True
        return False

    def _trazo_fino(self, x1, y1, x2, y2, color):
        ax, ay = self._xy(x1, y1)
        bx, by = self._xy(x2, y2)
        linea, = self.ax.plot(
            [ax, bx], [ay, by], color=color, linewidth=1.6,
            solid_capstyle="butt", zorder=5,
        )
        self._anotar_conexion(linea, color)

    def _simbolo_tierra(self, cx, y0, y1, cw, color):
        """Símbolo de tierra: asta y tres barras separadas, cada una más corta."""
        alto = max(y1 - y0, 8)
        y_barra = y0 + alto * 0.08
        paso = alto * 0.40
        self._trazo_fino(cx, y0, cx, y_barra, color)
        for ancho in (cw * 2.6, cw * 1.7, cw * 0.85):
            self._trazo_fino(
                cx - ancho / 2, y_barra, cx + ancho / 2, y_barra, color,
            )
            y_barra += paso

    def _trazo(self, ch, c, r, ox, oy, cw, chh, color, filas):
        spec = _TRAZOS_BLOQUE.get(ch)
        if not spec:
            return
        cx = ox + c * cw + cw / 2
        cy = oy + r * chh + chh / 2
        x0, x1 = ox + c * cw, ox + (c + 1) * cw
        y0, y1 = oy + r * chh, oy + (r + 1) * chh
        if ch == "╧":
            self._simbolo_tierra(cx, y0, y1, cw, color)
            return
        if ch == "═" and self._junto_a_tierra(filas, r, c):
            return
        lados = {"n": (cx, y0), "s": (cx, y1), "e": (x1, cy), "w": (x0, cy)}
        if "n" in spec.lower() and self._puente(filas, r, c, -1):
            lados["n"] = (cx, oy + (r - 1) * chh + chh / 2)
        if "s" in spec.lower() and self._puente(filas, r, c, 1):
            lados["s"] = (cx, oy + (r + 1) * chh + chh / 2)
        if self._plano and "e" in spec.lower() and self._puente_lado(filas, r, c, 1):
            lados["e"] = (ox + (c + 1) * cw + cw / 2, cy)
        if self._plano and "w" in spec.lower() and self._puente_lado(filas, r, c, -1):
            lados["w"] = (ox + (c - 1) * cw + cw / 2, cy)
        for lado in set(spec.lower()) - {"."}:
            doble = lado.upper() in spec and lado not in spec
            ex, ey = lados[lado]
            if not doble:
                self._anotar(cx, cy, ex, ey, color)
                continue
            sep = max(1.6, chh * 0.08)
            pares = ((0, -sep), (0, sep)) if lado in "we" else ((-sep, 0), (sep, 0))
            for dx, dy in pares:
                self._anotar(cx + dx, cy + dy, ex + dx, ey + dy, color)

    def _zigzags(self, filas, r, ox, oy, cw, ch):
        fila = filas[r]
        c = 0
        while c < len(fila):
            if fila[c][0] not in _ZIGZAG_BLOQUE:
                c += 1
                continue
            ini = c
            while c < len(fila) and fila[c][0] in _ZIGZAG_BLOQUE:
                c += 1
            self._un_zigzag(filas, r, ini, c, ox, oy, cw, ch)

    def _tallo(self, filas, r, c, x, y, oy, ch, color):
        def vertical(rr):
            if rr < 0 or rr >= len(filas) or c >= len(filas[rr]):
                return False
            return filas[rr][c][0] in "│║├┤┼╠╣╬┆┊┴┬╧╪╩╦"

        if vertical(r - 1):
            self._anotar(x, oy + r * ch, x, y, color)
        if vertical(r + 1):
            self._anotar(x, y, x, oy + (r + 1) * ch, color)

    def _es_vertical_en(self, filas, r, c):
        if r < 0 or r >= len(filas) or c < 0 or c >= len(filas[r]):
            return False
        return filas[r][c][0] in "│║"

    def _ancla_vertical(self, filas, r, c, oy, alto, hacia):
        """Une el zigzag al cable horizontal y omite los │ que atraviesa."""
        omit = []
        rr = r
        while True:
            nxt = rr + hacia
            if nxt < 0 or nxt >= len(filas) or c >= len(filas[nxt]):
                break
            g = filas[nxt][c][0]
            if g in "│║":
                omit.append(nxt)
                rr = nxt
                continue
            if g in _ZIGZAG_BLOQUE and omit:
                # Hay otra resistencia en la misma vertical (apartarrayos):
                # cada una toma solo su mitad del cable, para no encimarse.
                omit = omit[:len(omit) // 2]
                rr = omit[-1] if omit else r
                break
            spec = _TRAZOS_BLOQUE.get(g, "").lower().replace(".", "")
            if spec and ("w" in spec or "e" in spec):
                return oy + nxt * alto + alto / 2, omit
            break
        if hacia < 0:
            return oy + rr * alto, omit
        return oy + (rr + 1) * alto, omit

    def _dientes(self, a0, a1, centro, amp, n, vertical):
        """n crestas iguales. Empieza y termina sobre el cable."""
        paso = (a1 - a0) / n
        coords = []
        puntos = [(a0, centro)]
        for i in range(n):
            lado = amp if i % 2 == 0 else -amp
            puntos.append((a0 + paso * (i + 0.5), centro + lado))
        puntos.append((a1, centro))
        for a, b in puntos:
            if vertical:
                coords.extend((b, a))
            else:
                coords.extend((a, b))
        return coords

    def _zigzag_vertical(self, filas, r, c, ox, oy, cw, alto, color):
        x = ox + c * cw + cw / 2
        y_top, arriba = self._ancla_vertical(filas, r, c, oy, alto, -1)
        y_bot, abajo = self._ancla_vertical(filas, r, c, oy, alto, 1)
        for rr in arriba + abajo:
            self._sin_trazo.add((rr, c))
        if y_bot <= y_top:
            return None
        cuerpo = min(alto * 2.4, (y_bot - y_top) * 0.62)
        cuerpo = max(cuerpo, alto * 1.2)
        if cuerpo > y_bot - y_top:
            cuerpo = y_bot - y_top
        y0 = (y_top + y_bot) / 2 - cuerpo / 2
        y1 = y0 + cuerpo
        amp = min(cw * 0.7, cuerpo / 5.5)
        coords = self._dientes(y0, y1, x, amp, 4, True)
        if y0 - y_top > 0.5:
            coords = [x, y_top, *coords]
        if y_bot - y1 > 0.5:
            coords.extend((x, y_bot))
        return self._plot_neon(coords, color, filo=True)

    def _codigo_en_ventana(self, fila, c0, c1):
        if not fila or c1 <= c0:
            return None
        chars = "".join(ch for ch, _ in fila)
        for codigo in _CODIGOS_RESISTENCIA_RA:
            inicio = 0
            while True:
                i = chars.find(codigo, inicio)
                if i < 0:
                    break
                fin = i + len(codigo)
                inicio = fin
                if fin <= c0 or i >= c1:
                    continue
                antes = chars[i - 1] if i else " "
                despues = chars[fin] if fin < len(chars) else " "
                if antes.isalnum() or despues.isalnum():
                    continue
                return codigo
        return None

    def _codigo_junto_a_zigzag(self, filas, r, ini, fin):
        def fila(rr):
            if 0 <= rr < len(filas):
                return filas[rr]
            return None

        hallado = self._codigo_en_ventana(fila(r), fin, fin + 8)
        if hallado:
            return hallado
        hallado = self._codigo_en_ventana(
            fila(r + 1), max(0, ini - 3), fin + 6,
        )
        if hallado:
            return hallado
        hallado = self._codigo_en_ventana(
            fila(r + 2), max(0, ini - 3), fin + 6,
        )
        if hallado:
            return hallado
        hallado = self._codigo_en_ventana(
            fila(r - 1), max(0, ini - 3), fin + 6,
        )
        if hallado:
            return hallado
        return self._codigo_en_ventana(fila(r), max(0, ini - 8), ini)

    def _rotulo_bajo_zigzag(self, filas, r, c0, c1, texto):
        """RH y RX van debajo del zigzag: se bajan sin tocar la caja."""
        titulo = (self._titulo or "").strip().upper()
        if self._es_fp or titulo not in ("MEDICIÓN", "CONEXIONES"):
            return False
        if texto.strip() not in _CODIGOS_RESISTENCIA_RA or r <= 0:
            return False
        fila = filas[r - 1]
        col = c0
        while col < len(fila):
            if fila[col][0] not in _ZIGZAG_BLOQUE:
                col += 1
                continue
            ini = col
            while col < len(fila) and fila[col][0] in _ZIGZAG_BLOQUE:
                col += 1
            izq = fila[ini - 1][0] if ini else " "
            der = fila[col][0] if col < len(fila) else " "
            if izq not in _TRAZOS_BLOQUE and der not in _TRAZOS_BLOQUE:
                continue
            if c1 >= ini - 2 and c0 <= col + 2:
                return True
        return False

    def _zigzag_medido(self, codigo):
        return (
            bool(codigo)
            and not self._es_fp
            and (self._titulo or "").strip().upper() == "MEDICIÓN"
            and codigo in self._codigos_parpadeo
        )

    def _registrar_zigzag_medido(self, linea, codigo):
        if linea is not None and self._zigzag_medido(codigo):
            self._agregar_turno(codigo, linea)

    def _un_zigzag(self, filas, r, ini, fin, ox, oy, cw, alto):
        """Resistencia en diente de sierra, pegada al cable de los dos lados."""
        if not self._plano:
            self._un_zigzag_neon(filas, r, ini, fin, ox, oy, cw, alto)
            return
        fila = filas[r]
        color = _color_trazo_bloque(fila[ini][1])
        codigo = self._codigo_junto_a_zigzag(filas, r, ini, fin)
        if self._zigzag_medido(codigo):
            color = self._color_medicion
        izq = fila[ini - 1][0] if ini else " "
        der = fila[fin][0] if fin < len(fila) else " "
        lateral = izq in _TRAZOS_BLOQUE or der in _TRAZOS_BLOQUE
        if not lateral:
            stem = None
            for k in range(ini, fin):
                if self._es_vertical_en(filas, r - 1, k) or self._es_vertical_en(filas, r + 1, k):
                    stem = k
                    break
            if stem is not None:
                linea = self._zigzag_vertical(
                    filas, r, stem, ox, oy, cw, alto, color,
                )
                self._registrar_zigzag_medido(linea, codigo)
                self._anotar_conexion(linea, color)
                return
        cy = oy + r * alto + alto / 2
        x0 = ox + ini * cw
        x1 = ox + fin * cw
        if x1 <= x0:
            return
        amp = min(alto * 0.46, (x1 - x0) / 7)
        linea = self._plot_neon(
            self._dientes(x0, x1, cy, -amp, 5, False), color, filo=True,
        )
        self._registrar_zigzag_medido(linea, codigo)
        self._anotar_conexion(linea, color)

    def _un_zigzag_neon(self, filas, r, ini, fin, ox, oy, cw, alto):
        """MEDICIÓN: el zigzag sigue los glifos, con halo neón."""
        fila = filas[r]
        cy = oy + r * alto + alto / 2
        amp = alto * 0.34
        izq = fila[ini - 1][0] if ini else ""
        der = fila[fin][0] if fin < len(fila) else ""
        une_izq = izq in _TRAZOS_BLOQUE
        une_der = der in _TRAZOS_BLOQUE
        puntos = []
        for i, (glifo, color) in enumerate(fila[ini:fin]):
            x0 = ox + (ini + i) * cw
            x1 = x0 + cw
            if glifo == "∨":
                puntos.append((x0, cy - amp, color))
                puntos.append((x0 + cw / 2, cy + amp, color))
                puntos.append((x1, cy - amp, color))
                continue
            sube = glifo == "╱"
            y_ini = cy + (amp if sube else -amp)
            y_fin = cy + (-amp if sube else amp)
            if i == 0 and une_izq:
                y_ini = cy
            if i == fin - ini - 1 and une_der:
                y_fin = cy
            puntos.append((x0, y_ini, color))
            puntos.append((x1, y_fin, color))
        if len(puntos) < 2:
            return
        color = _color_trazo_bloque(puntos[0][2])
        coords = []
        for x, y, _col in puntos:
            if coords and coords[-2:] == [x, y]:
                continue
            coords.extend((x, y))
        self._plot_neon(coords, color)
        for i, (glifo, col) in enumerate(fila[ini:fin]):
            x0 = ox + (ini + i) * cw
            if glifo == "∨":
                y = cy + amp
            else:
                sube = glifo == "╱"
                y_ini = cy + (amp if sube else -amp)
                y_fin = cy + (-amp if sube else amp)
                if i == 0 and une_izq:
                    y_ini = cy
                if i == fin - ini - 1 and une_der:
                    y_fin = cy
                y = (y_ini + y_fin) / 2
            self._tallo(
                filas, r, ini + i, x0 + cw / 2, y, oy, alto,
                _color_trazo_bloque(col),
            )



_TEXTO = "#E2E8F0"
_SAPE1_MOD = None
_SAPE1_RUTA = Path(
    r"c:\Users\LapOne MX\Documents\Programacion Modo JEDI\S. A. P. E\SAPE_1.py"
)


def _sape1():
    global _SAPE1_MOD
    if _SAPE1_MOD is not None:
        return _SAPE1_MOD
    cargado = sys.modules.get("SAPE_1")
    if cargado is not None and hasattr(cargado, "_ra_letras_conexion"):
        _SAPE1_MOD = cargado
        return _SAPE1_MOD
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "sape1_diagramas", _SAPE1_RUTA
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    _SAPE1_MOD = mod
    return _SAPE1_MOD


def _descripcion_diagrama(prueba):
    def normalizar(valor):
        texto = (valor or "").strip()
        if texto in ("", "-----", "---", "—"):
            return "-----"
        return texto.replace("Tq", "Tanque")

    return (
        f"Prueba {prueba['prueba']}: "
        f"L={normalizar(prueba['linea'])}, "
        f"T={normalizar(prueba['tierra'])}, "
        f"G={normalizar(prueba['guarda'])}"
    )


def _medicion_diagrama(medicion):
    texto = str(medicion or "").upper().replace(" ", "")
    texto = texto.replace("R(HX)Y", "RHXY").replace("R(HX)", "RH")
    return texto.replace("-", "+")


def _texto_colorizado(sape, lineas, activas, modo, extra):
    crudas = sape._ra_aplicar_simbolo_resistencia(lineas, activas)
    codigos = sorted(extra, key=len, reverse=True)
    encendidas = {item.upper() for item in activas}
    pintadas = []
    for linea in crudas:
        for codigo in codigos:
            color = (
                sape._AMARILLO_MEDICION if codigo in encendidas else sape.GRIS
            )
            linea = re.sub(
                rf"(?<![A-Z0-9])({re.escape(codigo)})(?![A-Z0-9])",
                lambda coincidencia, tinta=color: (
                    f"{tinta}{coincidencia.group(1)}{sape.RESET}"
                ),
                linea,
            )
        pintadas.append(linea)
    contenido = sape._colorizar_cajas_roles_ra([
        sape._ra_colorizar_linea_diagrama(linea, modo=modo)
        for linea in pintadas
    ])
    return sape._texto_diagrama_ra(contenido)


def _lineas_maquina(sape, prueba, modo):
    fase = (prueba["linea"] or "A").strip().upper()[:1] or "A"
    codigo = f"R{fase}T"
    activas = {codigo} if modo == "mide" else set()
    roles = {"TANQUE": "TIERRA"}
    if modo == "conexiones":
        roles["TANQUE_EN_TIERRA"] = True
        roles[fase] = "LINEA"
    lineas = sape._fp_stack_diagrama(
        [("A", "RAT", None), ("B", "RBT", None), ("C", "RCT", None)],
        activas,
        roles=roles,
    )
    return lineas, activas, {"RAT", "RBT", "RCT"}


def _lineas_apartarrayos(sape, prueba, varias, modo):
    terminales = ("A", "B", "C", "D") if varias else ("A", "B")
    nombres = [
        f"R{inicio}{fin}"
        for inicio, fin in zip(terminales, terminales[1:])
    ]
    medicion = str(prueba["medicion"] or "").upper().replace(" ", "")
    if modo != "mide":
        activas = set()
    elif medicion == "RAD":
        activas = set(nombres)
    elif medicion == "RAC":
        activas = {"RAB", "RBC"}
    elif medicion in nombres:
        activas = {medicion}
    else:
        activas = set()
    roles = {}
    if modo == "conexiones":
        linea = (prueba["linea"] or "").strip().upper()[:1]
        tierra = (prueba["tierra"] or "").strip().upper()[:1]
        guarda = (prueba["guarda"] or "").strip().upper()
        if linea in terminales:
            roles[linea] = "LINEA"
        if tierra in terminales:
            roles[tierra] = "TIERRA_DEV"
        if guarda[:1] in terminales and guarda not in ("-----", "---", "—"):
            roles[guarda[:1]] = "GUARDA"
    bus = sape._FP_BUS_COL

    def terminal(letra):
        titulo = sape._fp_titulo_con_rol(letra, roles)
        return max(0, bus - 1 - sape._fp_visible_len(titulo)), titulo

    columna, titulo = terminal(terminales[0])
    lineas = [sape._fp_put([(columna, titulo), (bus, "│")])]
    for indice, nombre in enumerate(nombres):
        lineas.extend(
            sape._fp_rows_cap_h_plates(bus, nombre, set(nombres), 4)
        )
        columna, titulo = terminal(terminales[indice + 1])
        lineas.append(sape._fp_put([(columna, titulo), (bus, "│")]))
    lineas.extend(sape._fp_lineas_tierra({"TANQUE": "TIERRA"}))
    return lineas, activas, set(nombres)


def _lineas_auto_sin_terciario(sape, prueba, modo):
    descripcion = _descripcion_diagrama(prueba)
    roles = {"TANQUE": "TIERRA"}
    if modo == "conexiones":
        roles = sape._ra_mapa_roles_conexion(descripcion)
        roles.setdefault("TANQUE", "TIERRA")
    medicion = _medicion_diagrama(prueba["medicion"])
    activas = {parte for parte in medicion.split("+") if parte}
    titulo = "H-X LINEA" if modo == "conexiones" else "H-X"
    lineas = sape._fp_stack_diagrama(
        [(titulo, "RH", None)], activas, roles=roles,
    )
    return lineas, activas, set()


_RE_ANSI_RA = re.compile(r"\x1b\[[0-9;]*m")


def _etiqueta_diagrama_ra(codigo, activas):
    """Etiqueta de resistencia como la entrega SAPE_1: amarilla si se mide."""
    if codigo in activas:
        return f"\x1b[1m\x1b[38;2;255;255;0m{codigo}\x1b[0m"
    return f"\x1b[90m{codigo}\x1b[0m"


def _fila_diagrama_ra(*piezas):
    """Arma una fila del dibujo: cada pieza es (columna visible, texto)."""
    fila = ""
    visibles = 0
    for columna, texto in sorted(piezas, key=lambda pieza: pieza[0]):
        fila += " " * max(0, columna - visibles) + texto
        visibles = max(visibles, columna) + len(_RE_ANSI_RA.sub("", texto))
    return fila


def _activas_diagrama_ra(prueba, modo):
    if modo == "conexiones":
        return set()
    return set(
        _RE_CODIGO_RESISTENCIA_RA.findall(str(prueba.get("medicion", "")))
    )


def _lineas_generador_ra(prueba, modo):
    """Máquina rotatoria, ST-CT-001 Fig. 10: fases a carcasa y entre fases."""
    activas = _activas_diagrama_ra(prueba, modo)

    def e(codigo):
        return _etiqueta_diagrama_ra(codigo, activas)

    if "ROTOR" in str(prueba.get("linea", "")).upper():
        return [
            "         CARCASA",
            "            │           ┌────────┐",
            "            │───╱╲╱╲╱───│ ROTOR  │",
            f"            │   {e('RRT')}     └────────┘",
            "            │",
            "           ═╧═",
            "         TIERRA",
        ]
    return [
        "         CARCASA",
        "            │           ┌────────┐",
        "            │───╱╲╱╲╱───│   A    │────────┐",
        f"            │   {e('RAT')}     └────────┘        │",
        "            │                │            │",
        f"            │               ╱╲╱ {e('RAB')}       │",
        "            │                │            │",
        "            │           ┌────────┐        │",
        f"            │───╱╲╱╲╱───│   B    │       ╱╲╱ {e('RAC')}",
        f"            │   {e('RBT')}     └────────┘        │",
        "            │                │            │",
        f"            │               ╱╲╱ {e('RBC')}       │",
        "            │                │            │",
        "            │           ┌────────┐        │",
        "            │───╱╲╱╲╱───│   C    │────────┘",
        f"            │   {e('RCT')}     └────────┘",
        "            │",
        "           ═╧═",
        "         TIERRA",
    ]


def _lineas_tc_ra(prueba, modo):
    """TC hermético, ST-CT-001 Fig. 15.

    La pantalla aterrizada separa los devanados: RP y RPC van del primario a
    tierra y RSC del secundario a tierra. No hay resistencia entre devanados.
    """
    activas = _activas_diagrama_ra(prueba, modo)

    def e(codigo):
        return _etiqueta_diagrama_ra(codigo, activas)

    conexiones = modo == "conexiones"
    interior = 8 if conexiones else 12
    primario, secundario = ("P", "S") if conexiones else ("PRIMARIO", "SECUNDARIO")
    bus, caja = 12, 24
    centro = caja + (interior + 2) // 2
    tapa = "┌" + "─" * interior + "┐"
    base = "└" + "─" * interior + "┘"
    tronco = (bus, "│")
    fila_rpc = [tronco, (centro - 1, "╱╲╱ " + e("RPC"))]
    if conexiones and "PORCEL" in str(prueba.get("guarda", "")).upper():
        fila_rpc.append((centro - 8, "GUARDA"))
    f = _fila_diagrama_ra
    return [
        f((9, "TANQUE")),
        f(tronco, (caja, tapa)),
        f((bus, "│───╱╲╱╲╱───"), (caja, "│" + primario.center(interior) + "│")),
        f(tronco, (bus + 5, e("RP")), (caja, base)),
        f(tronco, (centro, "│")),
        f(*fila_rpc),
        f(tronco, (centro, "│")),
        f((bus, "│" + "─" * (centro - bus - 1) + "┤")),
        f(tronco, (centro, "│")),
        f(tronco, (centro - 1, "╱╲╱ " + e("RSC"))),
        f(tronco, (centro, "│")),
        f(tronco, (caja, tapa)),
        f(tronco, (caja, "│" + secundario.center(interior) + "│")),
        f(tronco, (caja, base)),
        f(tronco),
        f((bus - 1, "═╧═")),
        f((9, "TIERRA")),
    ]


def _quitar_terciario_ra(lineas):
    """Autotransformador sin terciario: deja solo el bloque H-X y su RHX."""
    lineas = [str(linea) for linea in lineas]
    limpias = [_RE_ANSI_RA.sub("", linea) for linea in lineas]
    cierre = next((i for i, linea in enumerate(limpias) if "└" in linea), None)
    tierra = next((i for i, linea in enumerate(limpias) if "═╧═" in linea), None)
    if cierre is None or tierra is None or tierra - 1 <= cierre:
        return lineas
    return lineas[:cierre + 1] + lineas[tierra - 1:]


def _textos_diagramas_sape2(equipo, prueba, sin_terciario, varias_secciones):
    sape = _sape1()
    if "Generadores" in equipo:
        construir = lambda modo: _lineas_maquina(sape, prueba, modo)
    elif "Apartarrayos" in equipo:
        construir = lambda modo: _lineas_apartarrayos(
            sape, prueba, varias_secciones, modo
        )
    elif "Autotransformadores" in equipo and sin_terciario:
        construir = lambda modo: _lineas_auto_sin_terciario(
            sape, prueba, modo
        )
    else:
        if "TCs" in equipo:
            tipo = 5
        elif "TPs" in equipo:
            tipo = 6
        elif "3 Devanados" in equipo:
            tipo = 2
        elif "Autotransformadores" in equipo:
            tipo = 3
        elif "Reactores" in equipo:
            tipo = 4
        else:
            tipo = 1
        return sape._textos_diagrama_bloques_ra(
            {"tipo_equipo": tipo},
            _medicion_diagrama(prueba["medicion"]),
            _descripcion_diagrama(prueba),
        )
    salida = []
    for modo in ("mide", "conexiones"):
        lineas, activas, extra = construir(modo)
        salida.append(
            _texto_colorizado(sape, lineas, activas, modo, extra)
        )
    return tuple(salida)



_SGR_ANSI = re.compile(r"\x1b\[([0-9;]*)m")
_FONDO_DIAGRAMA = "#000000"
_COLOR_TRAZO = "#00f0ff"
_COLOR_LINEA_NEON = "#5CFFF6"
_AMARILLO_DIAGRAMA = "#FFFF00"
_TRAZO_A_NEON = {"#00f0ff", "#00f7ff", "#5cfff6"}

# Cada trazo llega al centro de los lados indicados. Doble = dos paralelas.
_TRAZOS = {
    "─": "we", "│": "ns", "┌": "se", "┐": "sw", "└": "ne", "┘": "nw",
    "├": "nse", "┤": "nsw", "┬": "wes", "┴": "wen", "┼": "nsew",
    "═": "WE", "║": "NS",
    "╔": "SE", "╗": "SW", "╚": "NE", "╝": "NW",
    "╠": "NSE", "╣": "NSW", "╦": "WES", "╩": "WEN", "╬": "NSEW",
    "╧": "WEN", "╪": "NSEW",
    "┄": "w.e", "┈": "w.e", "┆": "n.s", "┊": "n.s",
}
_ZIGZAG = set("╱╲∨")


def _color_sgr(numeros, color):
    if not numeros or numeros == [0]:
        return _TEXTO
    i = 0
    while i < len(numeros):
        n = numeros[i]
        if n in (0, 39):
            color = _TEXTO
        elif n == 38 and i + 4 < len(numeros) and numeros[i + 1] == 2:
            r, g, b = numeros[i + 2:i + 5]
            color = f"#{r:02x}{g:02x}{b:02x}"
            i += 4
        elif n == 48 and i + 4 < len(numeros) and numeros[i + 1] == 2:
            i += 4
        i += 1
    return color


def _rejilla_diagrama(texto):
    """Cuadrícula (carácter, color) sin códigos de consola."""
    filas = []
    for linea in (texto or "").split("\n"):
        celdas = []
        color = _COLOR_TRAZO
        inicio = 0
        for marca in _SGR_ANSI.finditer(linea):
            for ch in linea[inicio:marca.start()]:
                celdas.append((ch, color))
            numeros = [int(p) for p in marca.group(1).split(";") if p.isdigit()]
            color = _color_sgr(numeros, color)
            inicio = marca.end()
        for ch in linea[inicio:]:
            celdas.append((ch, color))
        filas.append(celdas)
    return filas


def _color_linea_diagrama(color):
    """Las líneas del diagrama van en azul eléctrico neón."""
    if str(color).lower() in _TRAZO_A_NEON:
        return _COLOR_LINEA_NEON
    return color


def _titulo_diagrama(parent, texto):
    """MEDICIÓN o CONEXIONES: misma letra que CFE, en amarillo neón."""
    fila = ctk.CTkFrame(parent, fg_color="transparent")
    fila.pack(anchor="w", padx=15, pady=12)
    ctk.CTkLabel(
        fila,
        text=str(texto).upper(),
        text_color="#FFFF00",
        font=ctk.CTkFont(family="Courier New", size=36, weight="bold"),
    ).pack(side="left")


def _fuente_diagrama(ancho):
    mejor = 8
    for tam in range(7, 22):
        if tkfont.Font(family="Consolas", size=tam).measure("M") <= ancho:
            mejor = tam
        else:
            break
    return tkfont.Font(family="Consolas", size=mejor)


class _LienzoDiagrama(tk.Canvas):
    """Dibuja el diagrama con líneas continuas, no con caracteres sueltos."""

    def __init__(self, parent):
        super().__init__(
            parent, bg=_FONDO_DIAGRAMA, highlightthickness=0, bd=0,
        )
        self._texto = ""
        self.bind("<Configure>", lambda _e: self._dibujar())

    def cargar(self, texto):
        self._texto = texto or ""
        self._dibujar()

    def _dibujar(self):
        self.delete("all")
        filas = _rejilla_diagrama(self._texto)
        while filas and not any(ch.strip() for ch, _ in filas[-1]):
            filas.pop()
        while filas and not any(ch.strip() for ch, _ in filas[0]):
            filas.pop(0)
        if not filas:
            return
        alto_px = max(self.winfo_height(), 160)
        ancho_px = max(self.winfo_width(), 240)
        cols = max(len(fila) for fila in filas)
        nfil = len(filas)
        alto = min(28, max(12, (alto_px - 28) / nfil))
        cw = min(16, max(8, (ancho_px - 28) / cols))
        if cw > alto * 0.62:
            cw = alto * 0.62
        dw, dh = cols * cw, nfil * alto
        ox = max(12, (ancho_px - dw) / 2)
        oy = max(10, (alto_px - dh) / 2)
        fuente = _fuente_diagrama(cw)
        grosor = max(2, int(round(cw / 7)))
        for r, fila in enumerate(filas):
            self._zigzags(filas, r, ox, oy, cw, alto, grosor)
            for c, (glifo, color) in enumerate(fila):
                if glifo in _ZIGZAG or glifo == " ":
                    continue
                if glifo == "○":
                    self._circulo(
                        c, r, ox, oy, cw, alto, _color_linea_diagrama(color), grosor,
                    )
                    continue
                if glifo in _TRAZOS:
                    self._trazo(
                        glifo, c, r, ox, oy, cw, alto,
                        _color_linea_diagrama(color), grosor, filas,
                    )
                    continue
                self.create_text(
                    ox + c * cw + cw / 2, oy + r * alto + alto / 2,
                    text=glifo, fill=color, font=fuente, anchor="center",
                )

    def _circulo(self, c, r, ox, oy, cw, ch, color, grosor):
        cx = ox + c * cw + cw / 2
        cy = oy + r * ch + ch / 2
        rad = min(cw, ch) * 0.28
        self.create_oval(
            cx - rad, cy - rad, cx + rad, cy + rad,
            outline=color, width=grosor,
        )

    def _puente(self, filas, r, c, hacia):
        """El cable vertical debe llegar al trazo horizontal de la fila vecina."""
        rr = r + hacia
        if rr < 0 or rr >= len(filas) or c >= len(filas[rr]):
            return False
        spec = _TRAZOS.get(filas[rr][c][0], "").lower().replace(".", "")
        if not spec:
            return False
        cruza = "w" in spec or "e" in spec
        sigue = "s" in spec if hacia < 0 else "n" in spec
        return cruza and not sigue 

    def _trazo(self, ch, c, r, ox, oy, cw, chh, color, grosor, filas):
        spec = _TRAZOS.get(ch)
        if not spec:
            return
        cx = ox + c * cw + cw / 2
        cy = oy + r * chh + chh / 2
        x0, x1 = ox + c * cw, ox + (c + 1) * cw
        y0, y1 = oy + r * chh, oy + (r + 1) * chh
        if ch == "╧":
            sep = max(1.4, grosor * 0.7)
            fino = max(1, grosor - 1)
            self.create_line(
                cx, y0, cx, cy - sep, fill=color, width=grosor, capstyle="round",
            )
            self.create_line(
                x0, cy - sep, x1, cy - sep, fill=color, width=fino, capstyle="round",
            )
            self.create_line(
                x0, cy + sep, x1, cy + sep, fill=color, width=fino, capstyle="round",
            )
            return
        lados = {
            "n": (cx, y0), "s": (cx, y1), "e": (x1, cy), "w": (x0, cy),
        }
        if "n" in spec.lower() and self._puente(filas, r, c, -1):
            lados["n"] = (cx, oy + (r - 1) * chh + chh / 2)
        if "s" in spec.lower() and self._puente(filas, r, c, 1):
            lados["s"] = (cx, oy + (r + 1) * chh + chh / 2)
        punteado = "." in spec
        for lado in set(spec.lower()) - {"."}:
            doble = lado.upper() in spec and lado not in spec
            ex, ey = lados[lado] 
            self._segmento(cx, cy, ex, ey, color, grosor, doble, lado, punteado)

    def _segmento(self, x1, y1, x2, y2, color, grosor, doble, lado, punteado):
        dash = (4, 3) if punteado else None
        if not doble:
            self.create_line(
                x1, y1, x2, y2, fill=color, width=grosor,
                capstyle="round", dash=dash,
            )
            return
        sep = max(1.4, grosor * 0.7)
        if lado in "we":
            pares = ((0, -sep), (0, sep))
        else:
            pares = ((-sep, 0), (sep, 0))
        for dx, dy in pares:
            self.create_line(
                x1 + dx, y1 + dy, x2 + dx, y2 + dy,
                fill=color, width=max(1, grosor - 1), capstyle="round",
            )

    def _zigzags(self, filas, r, ox, oy, cw, ch, grosor):
        fila = filas[r]
        c = 0
        n = len(fila)
        while c < n:
            if fila[c][0] not in _ZIGZAG:
                c += 1
                continue
            ini = c
            while c < n and fila[c][0] in _ZIGZAG:
                c += 1
            self._un_zigzag(filas, r, ini, c, ox, oy, cw, ch, grosor)

    def _tallo(self, filas, r, c, x, y, ox, oy, ch, color, grosor):
        """Une el zigzag con el cable vertical de arriba o de abajo."""
        def vertical(rr):
            if rr < 0 or rr >= len(filas) or c >= len(filas[rr]):
                return False
            return filas[rr][c][0] in "│║├┤┼╠╣╬┆┊┴┬╧╪╩╦"

        if vertical(r - 1):
            self.create_line(
                x, oy + r * ch, x, y, fill=color, width=grosor, capstyle="round",
            )
        if vertical(r + 1):
            self.create_line(
                x, y, x, oy + (r + 1) * ch, fill=color, width=grosor, capstyle="round",
            )

    def _un_zigzag(self, filas, r, ini, fin, ox, oy, cw, alto, grosor):
        fila = filas[r]
        cy = oy + r * alto + alto / 2
        amp = alto * 0.34
        izq = fila[ini - 1][0] if ini else ""
        der = fila[fin][0] if fin < len(fila) else ""
        une_izq = izq in _TRAZOS
        une_der = der in _TRAZOS
        puntos = []
        for i, (glifo, color) in enumerate(fila[ini:fin]):
            x0 = ox + (ini + i) * cw
            x1 = x0 + cw
            if glifo == "∨":
                puntos.append((x0, cy - amp, color))
                puntos.append((x0 + cw / 2, cy + amp, color))
                puntos.append((x1, cy - amp, color))
                continue
            sube = glifo == "╱"
            y_ini = cy + (amp if sube else -amp)
            y_fin = cy + (-amp if sube else amp)
            if i == 0 and une_izq:
                y_ini = cy
            if i == fin - ini - 1 and une_der:
                y_fin = cy
            puntos.append((x0, y_ini, color))
            puntos.append((x1, y_fin, color))
        if len(puntos) < 2:
            return
        color = _color_linea_diagrama(puntos[0][2])
        coords = []
        for x, y, _col in puntos:
            if coords and coords[-2:] == [x, y]:
                continue
            coords.extend((x, y))
        self.create_line(
            *coords, fill=color, width=grosor,
            capstyle="round", joinstyle="round",
        )
        for i, (glifo, col) in enumerate(fila[ini:fin]):
            x0 = ox + (ini + i) * cw
            if glifo == "∨":
                y = cy + amp
            else:
                sube = glifo == "╱"
                y_ini = cy + (amp if sube else -amp)
                y_fin = cy + (-amp if sube else amp)
                if i == 0 and une_izq:
                    y_ini = cy
                if i == fin - ini - 1 and une_der:
                    y_fin = cy
                y = (y_ini + y_fin) / 2
            self._tallo(
                filas, r, ini + i, x0 + cw / 2, y, ox, oy, alto,
                _color_linea_diagrama(col), grosor,
            )


def _rgb(valor):
    valor = valor.lstrip("#")
    return tuple(int(valor[i:i + 2], 16) for i in (0, 2, 4))


def _mezcla(origen, destino, parte):
    return tuple(int(origen[i] + (destino[i] - origen[i]) * parte) for i in range(3))


def _degradado_libre(alto, paradas):
    """Degradado vertical con las paradas (posición 0–1, color) que se indiquen."""
    marcas = [(pos, _rgb(color)) for pos, color in paradas]

    def en(posicion):
        if posicion <= marcas[0][0]:
            return marcas[0][1]
        for (inicio, color_a), (fin, color_b) in zip(marcas, marcas[1:]):
            if posicion <= fin:
                tramo = 0 if fin == inicio else (posicion - inicio) / (fin - inicio)
                return _mezcla(color_a, color_b, tramo)
        return marcas[-1][1]

    return [en(y / max(alto - 1, 1)) for y in range(alto)]


def _degradado(alto, paradas):
    colores = [_rgb(color) for color in paradas]
    marcas = ((0.0, colores[0]), (0.5, colores[1]), (1.0, colores[2]))

    def en(posicion):
        if posicion <= 0:
            return marcas[0][1]
        for (inicio, color_a), (fin, color_b) in zip(marcas, marcas[1:]):
            if posicion <= fin:
                tramo = 0 if fin == inicio else (posicion - inicio) / (fin - inicio)
                return _mezcla(color_a, color_b, tramo)
        return marcas[-1][1]

    return [en(y / max(alto - 1, 1)) for y in range(alto)]


def _ancho_boton_ajustado(pares):
    """Ancho del botón más grande, para que el grupo quede parejo."""
    fuente_num = tkfont.Font(family="Segoe UI Black", size=20)
    fuente_txt = tkfont.Font(family="Segoe UI Black", size=8)
    anchos = []
    for marca, texto in pares:
        extra = fuente_num.measure(marca) + 16 if marca else 0
        anchos.append(24 + extra + fuente_txt.measure(texto) + 20)
    return max(anchos)


def _boton_paso_3d(
    panel, fondo_panel, numero, texto, comando, tema="azul", marca=None,
    ajustar=False, ancho=None,
):
    """Paso elegido en relieve. Los demás son teclas. Azul en RA, verde en FP."""
    from PIL import Image, ImageDraw, ImageTk

    temas = {
        "azul": {
            "activo": ("#F2C94C", "#E1AD01", "#C99600"),
            "activo_hundido": ("#C99600", "#A67C00", "#A67C00"),
            "activo_labio": "#7A5C00",
            "inactivo": ("#2C385C", "#1A233D", "#111726"),
            "inactivo_hover": ("#384875", "#222E4F", "#171F33"),
            "inactivo_hundido": ("#111726", "#111726", "#111726"),
            "inactivo_labio": "#070A12",
            "texto": "#55648A",
            "numero": "#FFFFFF",
            "numero_apagado": "#3E4A68",
        },
        "verde": {
            "activo": ("#3DDC9A", "#0E9F6E", "#047857"),
            "activo_hundido": ("#0E9F6E", "#047857", "#047857"),
            "activo_labio": "#064E3B",
            "inactivo": ("#1C4A42", "#12352F", "#0B2420"),
            "inactivo_hover": ("#2A6B5E", "#1A4A42", "#12352F"),
            "inactivo_hundido": ("#0B2420", "#0B2420", "#0B2420"),
            "inactivo_labio": "#041614",
            "texto": "#5C7D76",
            "numero": FP_ROJO_PASTEL,
            "numero_apagado": "#3E5850",
        },
        "morado": {
            "activo": ("#A78BFA", "#7C3AED", "#6D28D9"),
            "activo_hundido": ("#7C3AED", "#6D28D9", "#5B21B6"),
            "activo_labio": "#4C1D95",
            "inactivo": ("#3B2468", "#2A1848", "#1A102E"),
            "inactivo_hover": ("#4C2D86", "#3B2468", "#2A1848"),
            "inactivo_hundido": ("#1A102E", "#1A102E", "#1A102E"),
            "inactivo_labio": "#0E081C",
            "texto": "#6B5B8F",
            "numero": TTR_ROSA,
            "numero_apagado": "#5B4B74",
        },
    }
    paleta = temas[tema]
    fondo_rgb = _rgb(fondo_panel)
    lienzo = tk.Canvas(
        panel, height=72, bg=fondo_panel, highlightthickness=0, bd=0,
        cursor="hand2",
    )
    fuente_num = tkfont.Font(family="Segoe UI Black", size=20)
    fuente_txt = tkfont.Font(family="Segoe UI Semibold", size=8)
    fuente_txt_neg = tkfont.Font(family="Segoe UI Black", size=8)
    fuente_flecha = tkfont.Font(family="Segoe UI", size=16)
    alto_lienzo = 72
    alto_caja = 58
    ancho_fijo = None
    if ajustar:
        visible = f"{numero:02d}" if marca is None else marca
        extra = fuente_num.measure(visible) + 16 if visible else 0
        ancho_fijo = ancho or (24 + extra + fuente_txt_neg.measure(texto) + 20)
        lienzo.configure(width=ancho_fijo)
        lienzo.pack(anchor="w", padx=(16, 8), pady=(0, 2))
    else:
        lienzo.pack(fill="x", padx=8, pady=(0, 2))
    item = {"activo": False, "hover": False, "presionado": False, "foto": None}
    formas = {
        "activo": ("activo", "activo_labio", 6, 4, True, 100),
        "hundido_activo": ("activo_hundido", "activo_labio", 2, 8, False, 0),
        "inactivo": ("inactivo", "inactivo_labio", 4, 8, True, 40),
        "inactivo_hover": ("inactivo_hover", "inactivo_labio", 4, 5, True, 70),
        "hundido_inactivo": ("inactivo_hundido", "inactivo_labio", 1, 11, False, 0),
    }

    def cromado(ancho, modo):
        clave, clave_labio, grosor, arriba, con_sombra, brillo = formas[modo]
        imagen = Image.new("RGBA", (ancho, alto_lienzo), fondo_rgb + (255,))
        radio = 10
        ancho_caja = ancho - 4
        cuerpo = Image.new("RGBA", (ancho_caja, alto_caja), (0, 0, 0, 0))
        lineas = _degradado(alto_caja, paleta[clave])
        labio = _rgb(paleta[clave_labio])
        pixeles = cuerpo.load()
        for y, color in enumerate(lineas):
            tinta = labio if y >= alto_caja - grosor else color
            for x in range(ancho_caja):
                pixeles[x, y] = tinta + (255,)
        mascara = Image.new("L", (ancho_caja, alto_caja), 0)
        ImageDraw.Draw(mascara).rounded_rectangle(
            (0, 0, ancho_caja - 1, alto_caja - 1), radius=radio, fill=255,
        )
        if con_sombra:
            sombra = Image.new("RGBA", (ancho_caja, alto_caja + 16), (0, 0, 0, 0))
            trazo = ImageDraw.Draw(sombra)
            for expansion, alfa in ((7, 40), (4, 60), (1, 80)):
                trazo.rounded_rectangle(
                    (expansion, 8, ancho_caja - 1 - expansion, alto_caja + 9),
                    radius=radio, fill=(0, 0, 0, alfa),
                )
            imagen.paste(sombra, (2, arriba), sombra)
        recorte = Image.new("RGBA", (ancho_caja, alto_caja), (0, 0, 0, 0))
        recorte.paste(cuerpo, (0, 0), mascara)
        if brillo:
            ImageDraw.Draw(recorte).line(
                [(radio, 1), (ancho_caja - radio, 1)],
                fill=(255, 255, 255, brillo),
            )
        imagen.paste(recorte, (2, arriba), recorte)
        return imagen, arriba + (alto_caja - grosor) / 2

    def dibujar():
        ancho = ancho_fijo or max(lienzo.winfo_width(), 40)
        if item["presionado"]:
            modo = "hundido_activo" if item["activo"] else "hundido_inactivo"
        elif item["activo"]:
            modo = "activo"
        elif item["hover"]:
            modo = "inactivo_hover"
        else:
            modo = "inactivo"
        imagen, centro = cromado(ancho, modo)
        foto = ImageTk.PhotoImage(imagen)
        item["foto"] = foto
        lienzo.delete("all")
        lienzo.create_image(0, 0, image=foto, anchor="nw")
        elegido = modo in ("activo", "hundido_activo")
        encendido = elegido or modo == "inactivo_hover"
        if "numero" in paleta:
            color_num = paleta["numero"] if encendido else paleta.get(
                "numero_apagado", paleta["numero"],
            )
            color_txt = "#FFFFFF" if encendido else paleta["texto"]
        elif elegido:
            color_num, color_txt = "#FFD4A8", "#FFFFFF"
        elif modo == "inactivo_hover":
            color_num, color_txt = "#FFAA6E", "#FFFFFF"
        else:
            color_num, color_txt = "#D49A6A", paleta["texto"]
        if tema == "azul" and elegido:
            color_num = RA_TEXTO_MOSTAZA
            color_txt = RA_TEXTO_MOSTAZA
        elif ajustar:
            color_txt = "#FFFFFF"
        marca_visible = f"{numero:02d}" if marca is None else marca
        if marca_visible:
            lienzo.create_text(
                24, centro, text=marca_visible, anchor="w",
                fill=color_num, font=fuente_num,
            )
            inicio_txt = 24 + fuente_num.measure(marca_visible) + 16
        else:
            inicio_txt = 24
        lienzo.create_text(
            inicio_txt, centro, text=texto, anchor="w",
            fill=color_txt,
            font=fuente_txt_neg if elegido or ajustar else fuente_txt,
        )
        if not ajustar and (elegido or modo == "inactivo_hover"):
            if elegido:
                if tema == "morado":
                    color_flecha = TTR_PLATA
                elif tema == "azul":
                    color_flecha = RA_TEXTO_MOSTAZA
                else:
                    color_flecha = "#FFFFFF"
            elif "numero" in paleta:
                color_flecha = paleta["numero"]
            else:
                color_flecha = "#FFAA6E"
            lienzo.create_text(
                ancho - 28, centro, text="➔", anchor="e",
                fill=color_flecha,
                font=fuente_flecha,
            )

    def aplicar(activo):
        item["activo"] = activo
        item["presionado"] = False
        dibujar()

    def al_entrar(_evento=None):
        item["hover"] = True
        dibujar()

    def al_salir(_evento=None):
        item["hover"] = False
        item["presionado"] = False
        dibujar()

    def al_presionar(_evento=None):
        item["presionado"] = True
        dibujar()

    def al_soltar(_evento=None):
        item["presionado"] = False
        comando()
        dibujar()

    item["aplicar"] = aplicar
    lienzo.bind("<Configure>", lambda _evento: dibujar())
    lienzo.bind("<Enter>", al_entrar)
    lienzo.bind("<Leave>", al_salir)
    lienzo.bind("<ButtonPress-1>", al_presionar)
    lienzo.bind("<ButtonRelease-1>", al_soltar)
    return item


def _boton_menu_ra(
    panel, texto, comando, marca="", texto_naranja=False, tema="naranja",
    fondo="#1C2128", ancho=None,
):
    """Tecla en relieve: naranja en RA, verde en FP y neón en TTR."""
    from PIL import Image, ImageDraw, ImageTk

    # Las teclas con letra (A, B, C) son el doble de grandes.
    alto_tecla = 84 if marca else 58
    if marca:
        fondo = "#000000"  # Fondo negro detrás de las teclas A, B y C.
    fondo_rgb = _rgb(fondo)
    lienzo = tk.Canvas(
        panel, height=alto_tecla, bg=fondo,
        highlightthickness=0, bd=0, cursor="hand2",
    )
    if ancho is None:
        lienzo.pack(fill="x", padx=10, pady=(0, 2))
    else:
        lienzo.configure(width=ancho)
        lienzo.pack(anchor="w", padx=(16, 8), pady=(0, 2))
    fuente_num = tkfont.Font(family="Segoe UI", size=16, weight="bold")
    fuente_chip = tkfont.Font(family="Consolas", size=30, weight="bold")
    fuente_chip_numero = tkfont.Font(family="Consolas", size=18, weight="bold")
    fuente_txt = tkfont.Font(family="Segoe UI", size=9, weight="bold")
    fuente_flecha = tkfont.Font(family="Segoe UI", size=14, weight="bold")
    estado = {"activo": False, "hover": False, "presionado": False, "foto": None}
    caras = {
        "inactivo": {
            "paradas": ((0.0, "#2E333F"), (0.15, "#22262F"), (1.0, "#181B21")),
            "labio": "#050608", "grosor": 6, "arriba": 4,
            "filo": "#555C6D", "texto": "#CBD5E1", "numero": "#64748B",
        },
        "hover": {
            "paradas": ((0.0, "#3F4553"), (0.15, "#2E333F"), (1.0, "#22262F")),
            "labio": "#050608", "grosor": 6, "arriba": 1,
            "filo": "#788196", "texto": "#FFFFFF", "numero": "#94A3B8",
        },
        "hundido": {
            "paradas": ((0.0, "#15181E"), (1.0, "#15181E")),
            "labio": "#050608", "grosor": 1, "arriba": 5,
            "filo": "#15181E", "texto": "#CBD5E1", "numero": "#64748B",
        },
        "activo": {
            "paradas": ((0.0, "#F6A84A"), (0.35, "#F08C28"), (1.0, "#E07A1A")),
            "labio": "#9A3412", "grosor": 6, "arriba": 4,
            "filo": "#FFD7A8", "texto": "#FFFFFF", "numero": "#FFFFFF",
        },
        "activo_hundido": {
            "paradas": ((0.0, "#E07A1A"), (1.0, "#C2410C")),
            "labio": "#9A3412", "grosor": 1, "arriba": 5,
            "filo": "#E07A1A", "texto": "#FFFFFF", "numero": "#FFFFFF",
        },
    }
    color_resaltado = RA_VISTA_NARANJA
    if tema == "verde":
        caras["activo"].update(
            paradas=((0.0, "#34D399"), (0.35, "#10B981"), (1.0, "#059669")),
            labio="#064E3B", filo="#A7F3D0",
        )
        caras["activo_hundido"].update(
            paradas=((0.0, "#059669"), (1.0, "#047857")),
            labio="#064E3B", filo="#059669",
        )
        color_resaltado = "#34D399"
    elif tema == "neon":
        caras["activo"].update(
            paradas=((0.0, "#10232A"), (0.35, "#0B1B22"), (1.0, "#081319")),
            labio="#004D5A", filo="#00E5FF",
        )
        caras["activo_hundido"].update(
            paradas=((0.0, "#07141A"), (1.0, "#051015")),
            labio="#004D5A", filo="#00B8CC",
        )
        color_resaltado = "#00E5FF"
    elif tema == "morado":
        caras["activo"].update(
            paradas=((0.0, "#A78BFA"), (0.35, "#7C3AED"), (1.0, "#6D28D9")),
            labio="#4C1D95", filo="#DDD6FE",
        )
        caras["activo_hundido"].update(
            paradas=((0.0, "#7C3AED"), (1.0, "#5B21B6")),
            labio="#4C1D95", filo="#7C3AED",
        )
        color_resaltado = TTR_MORADO_CLARO
    elif tema == "morado_recurso":
        caras["inactivo"].update(
            paradas=((0.0, "#3B2468"), (0.15, "#2A1848"), (1.0, "#1A102E")),
            labio="#0E081C", filo="#7C3AED", texto="#DDD6FE",
        )
        caras["hover"].update(
            paradas=((0.0, "#4C2D86"), (0.15, "#3B2468"), (1.0, "#2A1848")),
            filo="#A78BFA", texto="#FFFFFF",
        )
        color_resaltado = TTR_MORADO_CLARO
    elif tema == "neon_morado":
        color_resaltado = TTR_MORADO_CLARO

    def cara_actual():
        if estado["presionado"] and estado["activo"]:
            return "activo_hundido"
        if estado["presionado"]:
            return "hundido"
        if estado["activo"]:
            return "activo"
        if estado["hover"]:
            return "hover"
        return "inactivo"

    def render(ancho, cara):
        estilo = caras[cara]
        alto_lienzo = alto_tecla
        alto_caja = alto_tecla - 6
        imagen = Image.new("RGBA", (ancho, alto_lienzo), fondo_rgb + (255,))
        radio = 8
        margen = 2
        ancho_caja = ancho - margen * 2
        y0 = estilo["arriba"]
        if estilo["grosor"] > 2:
            sombra = Image.new("RGBA", (ancho_caja, alto_caja + 16), (0, 0, 0, 0))
            trazo = ImageDraw.Draw(sombra)
            trazo.rounded_rectangle(
                (6, 12, ancho_caja - 7, alto_caja + 10),
                radius=radio, fill=(0, 0, 0, 70),
            )
            trazo.rounded_rectangle(
                (2, 8, ancho_caja - 3, alto_caja + 6),
                radius=radio, fill=(0, 0, 0, 110),
            )
            imagen.paste(sombra, (margen, y0), sombra)
        cuerpo = Image.new("RGBA", (ancho_caja, alto_caja), (0, 0, 0, 0))
        lineas = _degradado_libre(alto_caja, estilo["paradas"])
        labio = _rgb(estilo["labio"])
        filo = _rgb(estilo["filo"])
        pixeles = cuerpo.load()
        for y, color in enumerate(lineas):
            if y >= alto_caja - estilo["grosor"]:
                tinta = labio
            elif y == 0:
                tinta = filo
            else:
                tinta = color
            for x in range(ancho_caja):
                pixeles[x, y] = tinta + (255,)
        mascara = Image.new("L", (ancho_caja, alto_caja), 0)
        ImageDraw.Draw(mascara).rounded_rectangle(
            (0, 0, ancho_caja - 1, alto_caja - 1), radius=radio, fill=255,
        )
        recorte = Image.new("RGBA", (ancho_caja, alto_caja), (0, 0, 0, 0))
        recorte.paste(cuerpo, (0, 0), mascara)
        if estilo["grosor"] > 2:
            ImageDraw.Draw(recorte).line(
                [(radio, 1), (ancho_caja - radio, 1)],
                fill=(255, 255, 255, 70 if cara != "activo" else 150),
            )
        imagen.paste(recorte, (margen, y0), recorte)
        return imagen, y0 + (alto_caja - estilo["grosor"]) / 2

    def dibujar(_evento=None):
        ancho = max(lienzo.winfo_width(), 40)
        cara = cara_actual()
        imagen, centro = render(ancho, cara)
        if marca:
            # Teclas con marca (letras o números): sin botón de fondo, solo el cuadro negro con la letra.
            imagen = Image.new("RGBA", (ancho, alto_tecla), fondo_rgb + (255,))
        foto = ImageTk.PhotoImage(imagen)
        estado["foto"] = foto
        lienzo.delete("all")
        lienzo.create_image(0, 0, image=foto, anchor="nw")
        estilo = caras[cara]
        color_txt = estilo["texto"]
        color_num = estilo["numero"]
        if texto_naranja and not estado["activo"]:
            color_txt = color_resaltado
        x_texto = 22
        if False:  # Los números usan ahora el mismo estilo que A, B y C.
            margen_x, margen_y = 6, 5
            ancho_num = int(fuente_chip_numero.measure(marca)) + 16
            alto_num = 32
            chip_w = ancho_num + margen_x * 2
            chip_h = alto_num + margen_y * 2
            if estado["activo"]:
                color_marco = (26, 26, 26)
                color_centro = (5, 5, 5)
                color_digito = (
                    "#00E5FF" if tema in ("neon", "morado") else "#00FFFF"
                )
            else:
                color_marco = (11, 13, 16)
                color_centro = (26, 30, 36)
                color_digito = "#3A4048"
            chip = Image.new("RGBA", (chip_w, chip_h), (0, 0, 0, 0))
            trazo = ImageDraw.Draw(chip)
            trazo.rounded_rectangle(
                (0, 0, chip_w - 1, chip_h - 1), radius=6,
                fill=color_marco + (255,),
            )
            trazo.rounded_rectangle(
                (margen_x, margen_y, margen_x + ancho_num - 1, margen_y + alto_num - 1),
                radius=5, fill=color_centro + (255,),
            )
            if estado["activo"]:
                from PIL import ImageFont, ImageFilter
                fuente_brillo = ImageFont.truetype(
                    r"C:\Windows\Fonts\consolab.ttf", 18,
                )
                brillo = Image.new("RGBA", (chip_w, chip_h), (0, 0, 0, 0))
                ImageDraw.Draw(brillo).text(
                    (chip_w / 2, chip_h / 2), marca,
                    font=fuente_brillo, fill=(0, 229, 255, 230),
                    anchor="mm",
                )
                brillo = brillo.filter(ImageFilter.GaussianBlur(2))
                chip = Image.alpha_composite(chip, brillo)
            foto_chip = ImageTk.PhotoImage(chip)
            estado["foto_chip"] = foto_chip
            chip_x = 14
            lienzo.create_image(
                chip_x, centro - chip_h / 2, image=foto_chip, anchor="nw",
            )
            lienzo.create_text(
                chip_x + chip_w / 2, centro - 1, text=marca,
                fill=color_digito, font=fuente_chip_numero,
            )
            x_texto = chip_x + chip_w + 12
        elif marca:
            # Misma caja y el mismo resplandor cian que el chip de número,
            # nada más que con una letra en vez de un dígito.
            from PIL import ImageFont, ImageFilter
            lw, lh = 190, 76
            color_letra = "#00E5FF" if tema in ("neon", "morado", "neon_morado") else "#00FFFF"
            # Fuente Orbitron (la de la referencia), incluida en la carpeta fonts.
            def _orbitron(tam, estilo):
                ruta = Path(__file__).with_name("fonts") / "Orbitron.ttf"
                try:
                    fuente = ImageFont.truetype(str(ruta), tam)
                    fuente.set_variation_by_name(estilo)
                    return fuente
                except Exception:
                    return ImageFont.truetype(r"C:\Windows\Fonts\consolab.ttf", tam)
            # Tecla 3D neón: esquinas cortadas, borde cian con resplandor y base de profundidad.
            ancho_img, alto_img = lw + 4, lh + 4
            corte = 14

            def _cortado(x0, y0, x1, y1, c=corte):
                return [
                    (x0 + c, y0), (x1 - c, y0), (x1, y0 + c), (x1, y1 - c),
                    (x1 - c, y1), (x0 + c, y1), (x0, y1 - c), (x0, y0 + c),
                ]

            placa = Image.new("RGBA", (ancho_img, alto_img), (0, 0, 0, 0))
            # Base de profundidad, cuerpo oscuro con degradado y líneas de escaneo.
            ImageDraw.Draw(placa).polygon(_cortado(0, 4, lw - 1, lh + 3), fill=(0, 40, 44, 255))
            grad = Image.new("RGBA", placa.size, (0, 0, 0, 255))
            gd = ImageDraw.Draw(grad)
            for yy in range(placa.size[1]):
                f = yy / max(placa.size[1] - 1, 1)
                gd.line([(0, yy), (placa.size[0], yy)],
                        fill=(int(4 + 10 * (1 - f)), int(22 + 16 * (1 - f)), int(24 + 16 * (1 - f)), 255))
            mascara = Image.new("L", placa.size, 0)
            ImageDraw.Draw(mascara).polygon(_cortado(0, 0, lw - 1, lh - 1), fill=255)
            cuerpo = Image.composite(grad, Image.new("RGBA", placa.size, (0, 0, 0, 0)), mascara)
            placa = Image.alpha_composite(placa, cuerpo)
            lineas = Image.new("RGBA", placa.size, (0, 0, 0, 0))
            ld = ImageDraw.Draw(lineas)
            for yy in range(0, placa.size[1], 4):
                ld.line([(0, yy), (placa.size[0], yy)], fill=(0, 255, 255, 16))
            placa = Image.alpha_composite(placa, Image.composite(lineas, Image.new("RGBA", placa.size, (0, 0, 0, 0)), mascara))
            # Luz diagonal en la esquina superior derecha y líneas verticales internas.
            luz = Image.new("RGBA", placa.size, (0, 0, 0, 0))
            ImageDraw.Draw(luz).polygon([(lw - 44, 0), (lw, 0), (lw, 30)], fill=(0, 255, 255, 60))
            placa = Image.alpha_composite(placa, Image.composite(luz, Image.new("RGBA", placa.size, (0, 0, 0, 0)), mascara))
            verticales = Image.new("RGBA", placa.size, (0, 0, 0, 0))
            vd = ImageDraw.Draw(verticales)
            vd.line([(7, 14), (7, lh - 14)], fill=(0, 255, 255, 190), width=1)
            vd.line([(lw - 8, 14), (lw - 8, lh - 14)], fill=(0, 255, 255, 190), width=1)
            placa = Image.alpha_composite(placa, verticales)
            # Resplandor y borde cian.
            puntos_borde = _cortado(0, 0, lw - 1, lh - 1)
            resplandor = Image.new("RGBA", placa.size, (0, 0, 0, 0))
            ImageDraw.Draw(resplandor).line(puntos_borde + [puntos_borde[0]], fill=(0, 255, 255, 255), width=4)
            resplandor = resplandor.filter(ImageFilter.GaussianBlur(4))
            placa = Image.alpha_composite(placa, resplandor)
            borde_img = Image.new("RGBA", placa.size, (0, 0, 0, 0))
            ImageDraw.Draw(borde_img).line(puntos_borde + [puntos_borde[0]], fill=(0, 255, 255, 255), width=2)
            placa = Image.alpha_composite(placa, borde_img)
            fuente_brillo_letra = _orbitron(36, "Bold")
            brillo = Image.new("RGBA", placa.size, (0, 0, 0, 0))
            ImageDraw.Draw(brillo).text(
                (lw / 2, lh / 2 - 12), marca, font=fuente_brillo_letra,
                fill=_rgb(color_letra) + (230,), anchor="mm",
            )
            # Aura de neón alrededor de la letra: tres capas de resplandor.
            # Aura de neón: el resplandor se hace más denso para que se vea como luz.
            def _densa(capa, factor):
                r_, g_, b_, a_ = capa.split()
                a_ = a_.point(lambda v: min(255, int(v * factor)))
                return Image.merge("RGBA", (r_, g_, b_, a_))
            brillo_ancho = brillo.filter(ImageFilter.MaxFilter(5))
            for radio, factor in ((2, 2.5), (6, 4.0), (12, 5.0), (20, 6.0)):
                aura = _densa(brillo_ancho.filter(ImageFilter.GaussianBlur(radio)), factor)
                placa = Image.alpha_composite(placa, aura)
            # Letra y nombre van dentro de la imagen, para que se inclinen con la tecla.
            # Texto en capas transparentes para que no deje cuadros de color detrás.
            capa_texto = Image.new("RGBA", placa.size, (0, 0, 0, 0))
            ImageDraw.Draw(capa_texto).text(
                (lw / 2, lh / 2 - 12), marca, font=fuente_brillo_letra,
                fill=(90, 245, 255, 255), anchor="mm",
            )
            # Nombre con letras espaciadas, en monoespaciada como la referencia.
            fuente_nombre_tecla = ImageFont.truetype(r"C:\Windows\Fonts\consolab.ttf", 12)
            texto_tecla = texto.upper()
            separacion = 2
            ancho_nombre = sum(fuente_nombre_tecla.getlength(ch) for ch in texto_tecla) + separacion * (len(texto_tecla) - 1)
            x_nombre = lw / 2 - ancho_nombre / 2
            for ch in texto_tecla:
                ImageDraw.Draw(capa_texto).text(
                    (x_nombre, lh / 2 + 22), ch, font=fuente_nombre_tecla,
                    fill=(160, 255, 255, 255), anchor="lm",
                )
                x_nombre += fuente_nombre_tecla.getlength(ch) + separacion
            placa = Image.alpha_composite(placa, capa_texto)
            foto_letra = ImageTk.PhotoImage(placa)
            estado["foto_letra"] = foto_letra
            x_placa = 14
            lienzo.create_image(
                x_placa, centro - lh / 2,
                image=foto_letra, anchor="nw",
            )
            x_texto = x_placa + lw + 12
        if not marca:
            lienzo.create_text(
                x_texto, centro, text=texto.upper(), anchor="w",
                fill=color_txt, font=fuente_txt,
            )
        if estado["activo"]:
            lienzo.create_text(
                ancho - 22, centro, text="➔", anchor="e",
                fill="#FFFFFF", font=fuente_flecha,
            )

    def pintar(encendido):
        estado["activo"] = encendido
        estado["presionado"] = False
        dibujar()

    def al_entrar(_evento=None):
        estado["hover"] = True
        dibujar()

    def al_salir(_evento=None):
        estado["hover"] = False
        estado["presionado"] = False
        estado["tilt"] = (0.0, 0.0)
        dibujar()

    def al_mover(evento):
        """El mouse inclina la tecla hacia donde está."""
        ancho_l = max(lienzo.winfo_width(), 1)
        alto_l = max(lienzo.winfo_height(), 1)
        estado["tilt"] = (
            max(-1.0, min(1.0, evento.x / ancho_l * 2 - 1)),
            max(-1.0, min(1.0, evento.y / alto_l * 2 - 1)),
        )
        dibujar()

    def al_presionar(_evento=None):
        estado["presionado"] = True
        dibujar()

    def al_soltar(_evento=None):
        estado["presionado"] = False
        comando()
        dibujar()

    lienzo.bind("<Configure>", dibujar)
    lienzo.bind("<Enter>", al_entrar)
    lienzo.bind("<Leave>", al_salir)
    lienzo.bind("<ButtonPress-1>", al_presionar)
    lienzo.bind("<ButtonRelease-1>", al_soltar)
    return {"aplicar": pintar}


def _boton_relieve_ra(
    padre, texto, comando, ancho=186, modo="naranja", fondo=None,
    alto_caja=44, alto_lienzo=58, fuente_nombre="Segoe UI",
):
    """Botón con el mismo frente y un canto inferior en relieve."""
    from PIL import Image, ImageDraw, ImageTk

    fondo_hex = fondo or RA_VISTA_FONDO
    fondo = _rgb(fondo_hex)
    lienzo = tk.Canvas(
        padre, width=ancho, height=alto_lienzo, bg=fondo_hex,
        highlightthickness=0, bd=0, cursor="hand2", takefocus=1,
    )
    fuente = tkfont.Font(family=fuente_nombre, size=11, weight="bold")
    estado = {"hover": False, "presionado": False, "foco": False, "foto": None}
    caras = {
        "naranja": {
            "reposo": ((0.0, "#F6A84A"), (0.4, "#F08C28"), (1.0, "#E07A1A")),
            "labio": "#9A3412", "texto": "#FFFFFF", "borde": None, "radio": 8,
        },
        "contorno": {
            "reposo": ((0.0, "#FFFFFF"), (0.45, "#F7F5F0"), (1.0, "#EFECE6")),
            "labio": "#1A202C", "texto": "#2D3748", "borde": "#2D3748", "radio": 8,
        },
        "diagnostico": {
            "reposo": ((0.0, "#FFFBEB"), (0.5, "#FEF3C7"), (1.0, "#FDE68A")),
            "labio": "#F59E0B", "texto": "#D97706", "borde": "#FCD34D", "radio": 12,
        },
        # Factor de Potencia: los mismos botones en verde.
        "verde": {
            "reposo": ((0.0, "#34D399"), (0.4, "#10B981"), (1.0, "#059669")),
            "labio": "#064E3B", "texto": "#FFFFFF", "borde": None, "radio": 8,
        },
        "diagnostico_verde": {
            "reposo": ((0.0, "#F0FDF4"), (0.5, "#D1FAE5"), (1.0, "#A7F3D0")),
            "labio": "#10B981", "texto": "#047857", "borde": "#6EE7B7", "radio": 12,
        },
        # Relación de Transformación: los mismos botones en morado.
        "morado": {
            "reposo": ((0.0, "#A78BFA"), (0.4, "#7C3AED"), (1.0, "#6D28D9")),
            "labio": "#4C1D95", "texto": "#FFFFFF", "borde": None, "radio": 8,
        },
        "diagnostico_morado": {
            "reposo": ((0.0, "#F5F3FF"), (0.5, "#EDE9FE"), (1.0, "#DDD6FE")),
            "labio": "#7C3AED", "texto": "#5B21B6", "borde": "#C4B5FD", "radio": 12,
        },
    }
    estilo = caras[modo]

    def render(hundido, elevado):
        grosor = 1 if hundido else (4 if alto_caja <= 32 else 6)
        arriba = 8 if hundido else (1 if elevado else 4)
        imagen = Image.new("RGBA", (ancho, alto_lienzo), fondo + (255,))
        radio = estilo["radio"]
        if not hundido:
            sombra = Image.new("RGBA", (ancho, alto_caja + 14), (0, 0, 0, 0))
            trazo = ImageDraw.Draw(sombra)
            trazo.rounded_rectangle(
                (4, 10, ancho - 5, alto_caja + 8),
                radius=radio, fill=(0, 0, 0, 50),
            )
            imagen.paste(sombra, (0, arriba), sombra)
        cuerpo = Image.new("RGBA", (ancho, alto_caja), (0, 0, 0, 0))
        lineas = _degradado_libre(alto_caja, estilo["reposo"])
        labio = _rgb(estilo["labio"])
        pixeles = cuerpo.load()
        for y, color in enumerate(lineas):
            tinta = labio if y >= alto_caja - grosor else color
            for x in range(ancho):
                pixeles[x, y] = tinta + (255,)
        mascara = Image.new("L", (ancho, alto_caja), 0)
        ImageDraw.Draw(mascara).rounded_rectangle(
            (0, 0, ancho - 1, alto_caja - 1), radius=radio, fill=255,
        )
        recorte = Image.new("RGBA", (ancho, alto_caja), (0, 0, 0, 0))
        recorte.paste(cuerpo, (0, 0), mascara)
        dibujo = ImageDraw.Draw(recorte)
        if grosor > 2:
            dibujo.line(
                [(radio, 1), (ancho - radio, 1)],
                fill=(255, 255, 255, 160),
            )
        if estilo["borde"]:
            dibujo.rounded_rectangle(
                (1, 1, ancho - 2, alto_caja - grosor - 1),
                radius=radio, outline=estilo["borde"], width=2,
            )
        imagen.paste(recorte, (0, arriba), recorte)
        return imagen, arriba + (alto_caja - grosor) / 2

    def dibujar(_evento=None):
        imagen, centro = render(estado["presionado"], estado["hover"])
        foto = ImageTk.PhotoImage(imagen)
        estado["foto"] = foto
        lienzo.delete("all")
        lienzo.create_image(0, 0, image=foto, anchor="nw")
        lienzo.create_text(
            ancho / 2, centro, text=texto, fill=estilo["texto"], font=fuente,
        )
        if estado["foco"]:
            lienzo.create_rectangle(
                2, 2, ancho - 3, alto_lienzo - 8, outline="#1C1917", width=1,
            )

    def marcar(encendido):
        estado["foco"] = encendido
        dibujar()

    def al_entrar(_evento=None):
        estado["hover"] = True
        dibujar()

    def al_salir(_evento=None):
        estado["hover"] = False
        estado["presionado"] = False
        dibujar()

    def al_presionar(_evento=None):
        estado["presionado"] = True
        dibujar()

    def al_soltar(_evento=None):
        estado["presionado"] = False
        comando()
        try:
            if lienzo.winfo_exists():
                dibujar()
        except tk.TclError:
            return

    lienzo.marcar = marcar
    lienzo.invoke = al_soltar
    lienzo.bind("<Enter>", al_entrar)
    lienzo.bind("<Leave>", al_salir)
    lienzo.bind("<ButtonPress-1>", al_presionar)
    lienzo.bind("<ButtonRelease-1>", al_soltar)
    dibujar()
    return lienzo


class AppSAPE(tk.Tk):
    def __init__(self):
        super().__init__()
        _cargar_fuente_ra(self)
        self.option_add("*Font", (RA_FONT, 10))
        estilo = ttk.Style(self)
        estilo.configure("TCombobox", font=(RA_FONT, 10))
        estilo.configure("TEntry", font=(RA_FONT, 10))
        self.title("[ S. A. P. E. ]")
        self.geometry("390x630")
        self.resizable(False, False)
        self.configure(bg=NAVY)
        self.scale_x = 0.5
        self.scale_y = 0.7

        self.iconbitmap(str(APP_ICON_PATH))

        self.canvas = tk.Canvas(self, bg=NAVY, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        
        self.f_cfe = tkfont.Font(family="Consolas", size=7, weight="bold")
        self.f_sub = tkfont.Font(family="Consolas", size=8, weight="bold")
        self.f_sape = tkfont.Font(family="Consolas", size=17, weight="bold")
        self.f_info = tkfont.Font(family="Consolas", size=7)
        self.f_info_bold = tkfont.Font(
            family="Consolas", size=7, weight="bold"
        )
        self.f_ver = tkfont.Font(family="Consolas", size=7, slant="italic")
        self.f_lema = tkfont.Font(family="Consolas", size=8, slant="italic")
        self.f_menu = tkfont.Font(family="Consolas", size=8, weight="bold")

        self.datos_prueba = {
            "tipo_equipo": tk.StringVar(
                self, value=EQUIPOS_AISLAMIENTO[0]
            ),
            "fase": tk.StringVar(self, value="A"),
            "aislamiento": tk.StringVar(self, value="Sumergido en Aceite"),
            "liquido": tk.StringVar(self, value="Aceite mineral"),
            "temp_ambiente": tk.StringVar(self),
            "humedad_relativa": tk.StringVar(self),
            "voltaje_prueba": tk.StringVar(self, value="5000"),
            "lectura_30s": tk.StringVar(self),
            "lectura_1min": tk.StringVar(self),
            "lectura_10min": tk.StringVar(self),
            "temp_devanado": tk.StringVar(self),
            "conexion_L": tk.StringVar(self),
            "conexion_G": tk.StringVar(self),
            "conexion_T": tk.StringVar(self),
            "secciones_apartarrayos": tk.StringVar(
                self, value="Varias secciones"
            ),
            "terciario_autotransformador": tk.StringVar(
                self, value="Con terciario"
            ),
            "configuracion": tk.StringVar(self, value="Trifásico"),
        }
        self.prueba_seleccionada = None
        self._lecturas_anexo_a = _cargar_lecturas_anexo_a()

        self._menu_buttons = []
        self._filas_amarillas = []
        for numero, _texto, _tag in OPCIONES:
            if numero in ("6.", "7.", "8."):
                boton = tk.Label(
                    self.canvas,
                    text="",
                    bg="#0f3460",
                    fg=VERDE_CYAN,
                    font=self.f_menu,
                    anchor="w",
                    padx=10,
                    cursor="hand2",
                    relief="flat",
                    bd=0,
                    highlightthickness=2,
                    highlightbackground="#00F0FF",
                    highlightcolor="#00F0FF",
                )
                boton._amarillo = False
                accion = numero.rstrip(".")

                def al_clic(_evento=None, accion=accion):
                    self.ejecutar_accion(accion)

                def al_mover_fila(_evento=None, b=boton):
                    self._encender_fila_menu(b)

                boton.bind("<Button-1>", al_clic)
                boton.bind("<Enter>", al_mover_fila)
                boton.bind("<Motion>", al_mover_fila)
                self._filas_amarillas.append(boton)
            else:
                boton = tk.Button(
                    self.canvas,
                    text="",
                    bg="#0f3460",
                    fg=GRIS if numero == "9." else VERDE_CYAN,
                    activebackground="#0B4850",
                    activeforeground="white",
                    disabledforeground=GRIS,
                    font=self.f_menu,
                    anchor="w",
                    padx=10,
                    relief="raised",
                    bd=2,
                    cursor="hand2",
                    command=lambda accion=numero.rstrip("."):
                        self.ejecutar_accion(accion),
                )
            self._menu_buttons.append(boton)

        self.canvas.bind("<Button-1>", self._procesar_clic)
        self.canvas.bind("<Motion>", self._mover_menu)
        self.canvas.bind("<Leave>", lambda _evento=None: self._apagar_filas_menu())
        self.after_idle(self._dibujar_todo)

        self.lbl_suterm = tk.Label(
            self,
            text=LOGO_SUTERM,
            font=self.f_cfe,
            fg=ROJO_SUTERM,
            bg=NAVY,
        )

    def _encender_fila_menu(self, boton):
        if getattr(boton, "_amarillo", False):
            return
        self._apagar_filas_menu(excepto=boton)
        boton._amarillo = True
        boton.configure(
            bg="#FFE14A", fg="#111111",
            highlightbackground="#FFE14A", highlightcolor="#FFE14A",
            highlightthickness=3,
        )

    def _apagar_filas_menu(self, excepto=None):
        for boton in getattr(self, "_filas_amarillas", ()):
            if boton is excepto or not getattr(boton, "_amarillo", False):
                continue
            boton._amarillo = False
            try:
                boton.configure(
                    bg="#0f3460", fg=VERDE_CYAN,
                    highlightbackground="#00F0FF", highlightcolor="#00F0FF",
                    highlightthickness=2,
                )
            except tk.TclError:
                pass

    def _mover_menu(self, event):
        try:
            origen_x = self.canvas.winfo_rootx()
            origen_y = self.canvas.winfo_rooty()
        except tk.TclError:
            return
        puntero_x = origen_x + event.x
        puntero_y = origen_y + event.y
        activo = None
        for boton in self._filas_amarillas:
            try:
                x1 = boton.winfo_rootx()
                y1 = boton.winfo_rooty()
                x2 = x1 + boton.winfo_width()
                y2 = y1 + boton.winfo_height()
            except tk.TclError:
                continue
            if x1 <= puntero_x <= x2 and y1 <= puntero_y <= y2:
                activo = boton
                break
        if activo is None:
            self._apagar_filas_menu()
        else:
            self._encender_fila_menu(activo)

    def _dibujar_todo(self, event=None):
        if event is not None and event.widget is not self:
            return

        self.canvas.delete("drawing")
        self.canvas.delete("menu_button_window")
        width = self.winfo_width()
        height = self.winfo_height()
        center_x = width // 2
        tags = ("drawing",)
        sx = self.scale_x
        sy = self.scale_y
        x_pos = lambda value: round(value * sx)
        y_pos = lambda value: round(value * sy)

        for grid_x in range(0, width, 20):
            self.canvas.create_line(
                grid_x, 0, grid_x, height, fill=CUADRI,
                stipple="gray50", tags=tags
            )
        for grid_y in range(0, height, 20):
            self.canvas.create_line(
                0, grid_y, width, grid_y, fill=CUADRI,
                stipple="gray50", tags=tags
            )

        self.canvas.create_rectangle(
            x_pos(8), y_pos(8), width - x_pos(8), height - y_pos(8),
            outline=NAVY, width=8, tags=tags
        )
        self.canvas.create_rectangle(
            x_pos(8), y_pos(8), width - x_pos(8), height - y_pos(8),
            outline=NEON, width=4, tags=tags
        )
        # Relieve 3D: copias desplazadas en verde cada vez más oscuro detrás
        # del texto principal, como si las letras tuvieran grosor.
        for i, color_capa in zip(
            (5, 4, 3, 2, 1),
            ("#06230F", "#0B3A1C", "#115028", "#1A7038", "#248A48"),
        ):
            self.canvas.create_text(
                center_x + i, y_pos(90) + i, text=CFE_ASCII, font=self.f_cfe,
                fill=color_capa, justify="center", tags=tags,
            )
        self.canvas.create_text(
            center_x, y_pos(90), text=CFE_ASCII, font=self.f_cfe,
            fill=VERDE_CLARO, justify="center", tags=tags
        )
        self.canvas.create_text(
            center_x, y_pos(145),
            text="COMISIÓN FEDERAL DE ELECTRICIDAD",
            font=("Consolas", self.f_sub.cget("size") + 2, "bold"),
            fill=TEXTO, tags=tags
        )
        self.canvas.create_text(
            center_x, y_pos(165), text="ZONA DE TRANSMISIÓN JALISCO ORIENTE",
            font=self.f_sub, fill=TEXTO, tags=tags
        )
        self.canvas.create_text(
            center_x, y_pos(185), text="SUBESTACIONES",
            font=self.f_info_bold, fill=TEXTO, tags=tags
        )
        self.canvas.create_text(
            center_x, y_pos(225), text="[ S.A.P.E. ]®",
            font=self.f_sape, fill=VERDE_CLARO, tags=tags
        )
        self.canvas.create_text(
            center_x, y_pos(262),
            text="SISTEMA DE ANÁLISIS DE PRUEBAS ELÉCTRICAS",
            font=("Consolas", self.f_sub.cget("size") + 2, "bold"),
            fill="#FFFFFF", tags=tags
        )
        self.canvas.create_text(
            center_x, y_pos(292), text="VERSIÓN 3.2.0  –  © 2026",
            font=self.f_ver, fill=GRIS, tags=tags
        )
        self.canvas.create_text(
            center_x, y_pos(345),
            text='"Diagnóstico De Transformadores De Potencia\nE Instrumentales"',
            font=self.f_lema, fill=VERDE_CYAN, justify="center", tags=tags
        )

        panel_left = x_pos(30)
        panel_right = width - x_pos(30)
        panel_top = y_pos(405)
        panel_bottom = height - y_pos(30)

        y = 460
        ancho_fila = max(100, panel_right - panel_left - x_pos(16))
        ancho_caracter = max(1, self.f_menu.measure("0"))
        caracteres_fila = max(12, ancho_fila // ancho_caracter - 3)
        for boton, (num, texto, tag) in zip(self._menu_buttons, OPCIONES):
            etiqueta = f"{num} {texto}"
            espacios = max(1, caracteres_fila - len(etiqueta) - len(tag))
            boton.config(text=f"{etiqueta}{' ' * espacios}{tag}")
            self.canvas.create_window(
                center_x, y_pos(y), window=boton,
                width=ancho_fila, height=max(24, y_pos(34)),
                tags=("menu_button_window",),
            )
            y += 42

        self.canvas.create_text(
            center_x, y_pos(840), text="Haga clic en una opción para continuar",
            font=self.f_info_bold, fill=TEXTO, tags=tags
        )

    def _procesar_clic(self, event):
        first_row_y = round(460 * self.scale_y)
        row_step = round(42 * self.scale_y)
        if first_row_y - 18 <= event.y <= first_row_y + row_step * 8 + 18:
            index = round((event.y - first_row_y) / row_step)
            if 0 <= index < len(OPCIONES):
                expected_y = first_row_y + index * row_step
                if abs(event.y - expected_y) <= 18:
                    self.ejecutar_accion(OPCIONES[index][0].rstrip("."))

    def ejecutar_accion(self, num):
        if num == "9":
            self.destroy()
        elif num == "1":
            self.abrir_prueba_aislamiento()
        elif num == "2":
            self.abrir_prueba_factor()
        elif num == "3":
            self.abrir_prueba_ttr()
        elif num == "7":
            self.mostrar_historial()

    def abrir_prueba_aislamiento(self):
        ctk.set_appearance_mode("Light")
        ventana = tk.Toplevel(self)
        ventana.title(
            "[ S. A. P. E. ]  Sistema de Análisis de Pruebas Eléctricas v3.4"
        )
        ventana.iconbitmap(str(APP_ICON_PATH))
        ventana.geometry("1280x840")
        ventana.minsize(1100, 680)
        ventana.configure(bg=RA_VISTA_FONDO)

        barra_superior = tk.Frame(ventana, bg="#12161A", height=50)
        barra_superior.pack(side="top", fill="x")
        barra_superior.pack_propagate(False)

        def logo_neon(
            texto="[ S.A.P.E. ]", fondo=(5, 5, 5), marco=True, tam=16,
        ):
            from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageTk
            fuente = ImageFont.truetype(r"C:\Windows\Fonts\consolab.ttf", tam)
            sonda = ImageDraw.Draw(Image.new("RGB", (1, 1)))
            caja = sonda.textbbox((0, 0), texto, font=fuente)
            ancho = caja[2] - caja[0] + 22
            alto = caja[3] - caja[1] + 14
            imagen = Image.new("RGB", (ancho, alto), fondo)
            halo = Image.new("RGB", (ancho, alto), fondo)
            xy = (11 - caja[0], 7 - caja[1])
            ImageDraw.Draw(halo).text(xy, texto, font=fuente, fill=(0, 255, 255))
            halo = halo.filter(ImageFilter.GaussianBlur(3 * tam / 16))
            imagen = Image.blend(imagen, halo, 0.9)
            dibujo = ImageDraw.Draw(imagen)
            dibujo.text(xy, texto, font=fuente, fill=(0, 255, 255))
            if marco:
                dibujo.rounded_rectangle(
                    (0, 0, ancho - 1, alto - 1), radius=4, outline=(42, 49, 58),
                )
            return ImageTk.PhotoImage(imagen)

        # Barra superior: la clave del procedimiento en neón.
        foto_logo = logo_neon("ST-CT-001")
        ventana._logo_sape = foto_logo
        tk.Label(
            barra_superior, image=foto_logo, bg="#12161A", bd=0,
        ).pack(side="left", padx=(16, 8))
        tk.Label(
            barra_superior,
            text=(
                "PROCEDIMIENTO PARA LA MEDICIÓN DE RESISTENCIA\n"
                "DE AISLAMIENTO EN EQUIPO ELÉCTRICO PRIMARIO"
            ),
            bg="#12161A", fg="#A0AEC0",
            font=("Segoe UI", 8, "bold"), justify="left",
        ).pack(side="left", padx=(8, 0))
        reloj = tk.Label(
            barra_superior, text="", bg="#12161A",
            fg="#A0AEC0", font=("Consolas", 11, "bold"),
        )
        reloj.pack(side="right", padx=(0, 16))
        tk.Label(
            barra_superior, text="CONEXIÓN LÍNEA IEEE-43",
            bg="#12161A", fg="#A0AEC0",
            font=("Segoe UI", 9, "bold"),
        ).pack(side="right")
        tk.Label(
            barra_superior, text="●",
            bg="#12161A", fg="#00FF00",
            font=("Segoe UI", 8),
        ).pack(side="right", padx=(0, 6))

        def marcar_reloj():
            try:
                if not ventana.winfo_exists():
                    return
            except tk.TclError:
                return
            reloj.config(text=datetime.now().strftime("%H:%M:%S"))
            ventana._reloj_ra = ventana.after(1000, marcar_reloj)

        marcar_reloj()

        panel_lateral = tk.Frame(ventana, bg="#000000", width=320)
        panel_lateral.pack(side=tk.LEFT, fill=tk.Y)
        panel_lateral.pack_propagate(False)

        logo = tk.Frame(
            panel_lateral, bg="#12161A",
            highlightbackground="#3B4553", highlightthickness=1,
        )
        logo.pack(fill="x", padx=16, pady=(16, 0))
        # Menú lateral: [ S.A.P.E. ] también en neón, sobre el fondo del marco.
        foto_sape_lateral = logo_neon(
            fondo=(18, 22, 26), marco=False, tam=32,
        )
        ventana._logo_sape_lateral = foto_sape_lateral
        tk.Label(
            logo, image=foto_sape_lateral, bg="#12161A", bd=0,
        ).pack(pady=8)
        tk.Label(
            panel_lateral, text="RESISTENCIA DE AISLAMIENTO",
            bg="#1C2128", fg="#F38B1A",
            font=("Segoe UI", 8, "bold"),
        ).pack(pady=(6, 8))

        pie_lateral = tk.Frame(
            panel_lateral, bg=RA_VISTA_SIDEBAR_OSCURO,
            highlightbackground="#1F2937", highlightthickness=1,
        )
        pie_lateral.pack(side="bottom", fill="x")
        fila_norma = tk.Frame(pie_lateral, bg=RA_VISTA_SIDEBAR_OSCURO)
        fila_norma.pack(fill="x", padx=14, pady=(10, 2))
        tk.Label(
            fila_norma, text="ESTADO NORMA:", bg=RA_VISTA_SIDEBAR_OSCURO,
            fg="#9CA3AF", font=("Consolas", 9),
        ).pack(side="left")
        tk.Label(
            fila_norma, text="IEEE 43-2013", bg=RA_VISTA_SIDEBAR_OSCURO,
            fg="#34D399", font=("Consolas", 9, "bold"),
        ).pack(side="right")
        fila_diag = tk.Frame(pie_lateral, bg=RA_VISTA_SIDEBAR_OSCURO)
        fila_diag.pack(fill="x", padx=14, pady=(0, 10))
        tk.Label(
            fila_diag, text="UNIDAD DE DIAG:", bg=RA_VISTA_SIDEBAR_OSCURO,
            fg="#9CA3AF", font=("Consolas", 9),
        ).pack(side="left")
        tk.Label(
            fila_diag, text="ACTIVA", bg=RA_VISTA_SIDEBAR_OSCURO,
            fg=RA_VISTA_NARANJA, font=("Consolas", 9, "bold"),
        ).pack(side="right")

        menu_lateral = tk.Frame(panel_lateral, bg="#000000")
        menu_lateral.pack(fill="both", expand=True)

        area_principal = tk.Frame(ventana, bg=RA_VISTA_FONDO)
        area_principal.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        marco_scroll = tk.Frame(area_principal, bg=RA_VISTA_FONDO)
        marco_scroll.pack(fill=tk.BOTH, expand=True)
        barra_y_main = tk.Scrollbar(marco_scroll, orient="vertical")
        barra_x_main = tk.Scrollbar(marco_scroll, orient="horizontal")
        puerto_main = tk.Canvas(
            marco_scroll, bg=RA_VISTA_FONDO, highlightthickness=0, bd=0,
            yscrollcommand=barra_y_main.set,
            xscrollcommand=barra_x_main.set,
        )
        barra_y_main.configure(command=puerto_main.yview)
        barra_x_main.configure(command=puerto_main.xview)
        barra_x_main.pack(side="bottom", fill="x")
        barra_y_main.pack(side="right", fill="y")
        puerto_main.pack(side="left", fill="both", expand=True)
        contenedor = tk.Frame(
            puerto_main, bg=RA_VISTA_FONDO, bd=0, highlightthickness=0,
        )
        ventana_contenido = puerto_main.create_window(
            (0, 0), window=contenedor, anchor="nw",
        )

        def ajustar_contenido(_evento=None):
            if getattr(ajustar_contenido, "_ocupado", False):
                return
            ajustar_contenido._ocupado = True
            try:
                if not puerto_main.winfo_exists():
                    return
                req_w = max(contenedor.winfo_reqwidth(), 1)
                req_h = max(contenedor.winfo_reqheight(), 1)
                ancho = max(puerto_main.winfo_width(), req_w)
                alto = max(puerto_main.winfo_height(), req_h)
                puerto_main.itemconfigure(
                    ventana_contenido, width=ancho, height=alto,
                )
                puerto_main.configure(scrollregion=(0, 0, ancho, alto))
            except tk.TclError:
                return
            finally:
                ajustar_contenido._ocupado = False

        contenedor.bind("<Configure>", ajustar_contenido)
        puerto_main.bind("<Configure>", ajustar_contenido)

        def al_rueda_principal(evento):
            if not getattr(evento, "delta", 0):
                return
            try:
                x, y = ventana.winfo_pointerxy()
                destino = ventana.winfo_containing(x, y)
            except tk.TclError:
                return
            if destino is not None and destino.winfo_class() == "Text":
                return
            lienzo = None
            dentro = False
            while destino is not None:
                propio = getattr(destino, "_scroll_propio", None)
                if propio is not None:
                    lienzo = propio
                    break
                if destino is marco_scroll:
                    dentro = True
                    break
                destino = getattr(destino, "master", None)
            if lienzo is None and not dentro:
                return
            objetivo = lienzo or puerto_main
            pasos = int(-evento.delta / 120) or (
                -1 if evento.delta < 0 else 1
            )
            try:
                if evento.state & 0x1:
                    objetivo.xview_scroll(pasos, "units")
                else:
                    objetivo.yview_scroll(pasos, "units")
            except tk.TclError:
                return
            return "break"

        ventana.bind_all("<MouseWheel>", al_rueda_principal)

        def soltar_rueda_principal(_evento):
            if _evento.widget is not ventana:
                return
            try:
                ventana.unbind_all("<MouseWheel>")
            except tk.TclError:
                pass

        ventana.bind("<Destroy>", soltar_rueda_principal)

        paso_actual = tk.IntVar(ventana, value=1)
        botones_paso = []

        def titulo_seccion(texto):
            fila = tk.Frame(menu_lateral, bg="#1C2128")
            fila.pack(fill="x", padx=16, pady=(8, 4))
            tk.Label(
                fila, text=texto, bg="#1C2128", fg="#5C6979",
                font=("Consolas", 9, "bold"),
            ).pack(side="left")
            tk.Frame(fila, bg="#374151", height=1).pack(
                side="left", fill="x", expand=True, padx=(10, 0),
            )

        def crear_boton_paso(numero, texto):
            return _boton_menu_ra(
                menu_lateral, texto,
                lambda n=numero: self._cargar_paso_aislamiento(
                    n, paso_actual, contenedor, botones_paso,
                ),
                marca=f"{numero:02d}",
            )

        titulo_seccion("PROCESO DE PRUEBA")
        for numero_paso, texto_paso in (
            (1, "DATOS DEL EQUIPO"),
            (2, "SELECCIÓN DE PRUEBAS"),
            (3, "DIAGRAMAS DE BLOQUES"),
            (4, "CAPTURA DE LECTURAS"),
        ):
            botones_paso.append(crear_boton_paso(numero_paso, texto_paso))
        titulo_seccion("RECURSOS")
        _boton_menu_ra(
            menu_lateral, "MODOS DE PRUEBA",
            lambda: self.mostrar_modos_prueba_aislamiento(ventana),
            texto_naranja=True,
        )
        _boton_menu_ra(
            menu_lateral, "FORMATOS",
            lambda: self.mostrar_anexo_a_formatos(ventana),
            marca="A",
        )
        _boton_menu_ra(
            menu_lateral, "OPERACIÓN",
            lambda: self.mostrar_anexo_b_operacion(ventana),
            marca="B",
        )
        _boton_menu_ra(
            menu_lateral, "RESUMEN",
            lambda: self.mostrar_anexo_c_resumen(ventana),
            marca="C",
        )
        self._cargar_paso_aislamiento(
            1, paso_actual, contenedor, botones_paso,
        )
        # El menú web abre RA con la ventana principal oculta. Una ventana
        # transient de un padre oculto también queda oculta.
        if self.winfo_viewable():
            ventana.transient(self)
        ventana.update_idletasks()
        ventana.deiconify()
        ventana.lift()
        ventana.focus_force()
        ventana.grab_set()
        return ventana


    def _montar_correccion_ieee(self, padre):
        """Panel de K_T20 y semáforo de aislamiento. Devuelve el refresco."""
        base_ref = self._base_temp_ra()
        panel_kt = tk.Frame(padre, bg=RA_VISTA_PANEL)
        panel_kt.pack(fill="x")
        fila_kt = tk.Frame(panel_kt, bg=RA_VISTA_PANEL)
        fila_kt.pack(fill="x", padx=16, pady=(14, 8))
        tk.Label(
            fila_kt, text="CORRECCIÓN IEEE-43", bg=RA_VISTA_PANEL,
            fg=RA_VISTA_NARANJA, font=("Consolas", 10, "bold"),
        ).pack(side="left")
        tk.Label(
            fila_kt, text=f"Ref: {base_ref:g}°C", bg="#1F2937", fg="#9CA3AF",
            font=("Consolas", 9),
        ).pack(side="right")
        tk.Frame(panel_kt, bg="#374151", height=1).pack(fill="x", padx=16)
        cuerpo_kt = tk.Frame(panel_kt, bg=RA_VISTA_PANEL)
        cuerpo_kt.pack(fill="x", padx=16, pady=(12, 8))
        tk.Label(
            cuerpo_kt, text=f"Factor de Corrección  K_T{base_ref:g}:",
            bg=RA_VISTA_PANEL, fg="#D1D5DB", font=("Segoe UI", 10),
        ).pack(side="left")
        valor_kt = tk.Label(
            cuerpo_kt, text="—", bg=RA_VISTA_PANEL, fg=RA_VISTA_NARANJA,
            font=("Consolas", 28, "bold"),
        )
        valor_kt.pack(side="right")
        caja_ecuacion = tk.Frame(panel_kt, bg="#111827")
        caja_ecuacion.pack(fill="x", padx=16, pady=(0, 8))
        fila_eq = tk.Frame(caja_ecuacion, bg="#111827")
        fila_eq.pack(fill="x", padx=10, pady=(8, 2))
        tk.Label(
            fila_eq, text="Ecuación usada:", bg="#111827", fg="#9CA3AF",
            font=("Consolas", 9),
        ).pack(side="left")
        tk.Label(
            fila_eq, text=f"KT = 0.5^(({base_ref:g}-T)/10)", bg="#111827",
            fg="#E5E7EB", font=("Consolas", 9),
        ).pack(side="right")
        fila_delta = tk.Frame(caja_ecuacion, bg="#111827")
        fila_delta.pack(fill="x", padx=10, pady=(2, 8))
        tk.Label(
            fila_delta, text="Delta temperatura:", bg="#111827",
            fg="#9CA3AF", font=("Consolas", 9),
        ).pack(side="left")
        valor_delta = tk.Label(
            fila_delta, text="—", bg="#111827", fg=RA_VISTA_AMBAR_CLARO,
            font=("Consolas", 9, "bold"),
        )
        valor_delta.pack(side="right")
        aviso_kt = tk.Label(
            panel_kt, text="", bg="#451A03", fg="#FDE68A",
            font=("Segoe UI", 9), justify="left", anchor="nw",
            wraplength=300,
        )
        aviso_kt.pack(fill="x", padx=16, pady=(0, 10))

        panel_estado = tk.Frame(panel_kt, bg=RA_VISTA_PANEL)
        panel_estado.pack(fill="x", padx=16, pady=(4, 16))
        fila_estado = tk.Frame(panel_estado, bg=RA_VISTA_PANEL)
        fila_estado.pack(fill="x", pady=(0, 8))
        tk.Label(
            fila_estado, text="ESTADO DEL AISLAMIENTO",
            bg=RA_VISTA_PANEL, fg=RA_VISTA_NARANJA,
            font=("Consolas", 9, "bold"),
        ).pack(side="left")
        luces = tk.Frame(panel_estado, bg=RA_VISTA_PANEL, height=108)
        luces.pack(fill="x", pady=(0, 10))
        luces.pack_propagate(False)
        def foto_emoji(emoji):
            from PIL import Image, ImageDraw, ImageFont, ImageTk
            fuente = ImageFont.truetype(
                r"C:\Windows\Fonts\seguiemj.ttf", 52,
            )
            sonda = ImageDraw.Draw(Image.new("RGBA", (4, 4)))
            caja = sonda.textbbox(
                (0, 0), emoji, font=fuente, embedded_color=True,
            )
            imagen = Image.new(
                "RGBA",
                (caja[2] - caja[0] + 4, caja[3] - caja[1] + 4),
                (0, 0, 0, 0),
            )
            ImageDraw.Draw(imagen).text(
                (2 - caja[0], 2 - caja[1]),
                emoji, font=fuente, embedded_color=True,
            )
            contenido = imagen.getbbox()
            if contenido:
                imagen = imagen.crop(contenido)
            foto = ImageTk.PhotoImage(imagen)
            vacio = tk.PhotoImage(width=foto.width(), height=foto.height())
            return foto, vacio

        focos = {}
        for indice, (clave, nombre, emoji) in enumerate((
            ("normal", "NORMAL", "✅"),
            ("precaucion", "PRECAUCIÓN", "⚠️"),
            ("alerta", "ALERTA", "❌"),
        )):
            luces.columnconfigure(indice, weight=1, uniform="focos")
            celda = tk.Frame(luces, bg="#1F2937", width=96, height=100)
            celda.grid(row=0, column=indice, sticky="nsew", padx=4)
            celda.grid_propagate(False)
            foto, vacio = foto_emoji(emoji)
            punto = tk.Label(
                celda, image=foto, bg="#1F2937", bd=0,
            )
            punto.pack(pady=(10, 0))
            punto._foto = foto
            punto._vacio = vacio
            punto._emoji = emoji
            nombre_lbl = tk.Label(
                celda, text=nombre, bg="#1F2937", fg="#E5E7EB",
                font=("Segoe UI", 8, "bold"), height=1,
            )
            nombre_lbl.pack(pady=(4, 0))
            focos[clave] = (celda, punto, nombre_lbl)
        luces.rowconfigure(0, weight=1)
        caja_datos = tk.Frame(panel_estado, bg=RA_VISTA_PANEL)
        caja_datos.pack(fill="both", expand=True, pady=(0, 4))
        # Sin barra propia: el cuadro crece con su texto y se recorre con la
        # barra de la ventana.
        datos_ieee = tk.Text(
            caja_datos, bg=RA_VISTA_PANEL, fg="#E5E7EB",
            font=("Segoe UI", 9), wrap="word", height=2, width=40,
            bd=0, highlightthickness=0, padx=2, pady=2, cursor="arrow",
        )
        datos_ieee.pack(side="left", fill="both", expand=True)
        datos_ieee.configure(state="disabled")
        job_foco = getattr(self, "_parpadeo_foco_job", None)
        if job_foco is not None:
            try:
                self.after_cancel(job_foco)
            except tk.TclError:
                pass
            self._parpadeo_foco_job = None
        self._focos_ieee = focos
        self._aviso_ieee = aviso_kt
        self._datos_ieee = datos_ieee
        self._nivel_foco_ieee = None

        def refrescar_kt(_evento=None):
            temp = self._numero_ra(self.datos_prueba["temp_devanado"].get())
            hr = self._numero_ra(self.datos_prueba["humedad_relativa"].get())
            if temp is None:
                valor_kt.config(text="—")
                valor_delta.config(text="—")
                return
            en_aceite = self._en_aceite_ra()
            paso_dup = 10.0 if en_aceite or base_ref == 40.0 else 15.0
            delta = temp - base_ref
            factor = 2.0 ** (delta / paso_dup)
            valor_kt.config(text=f"{factor:.2f}")
            valor_delta.config(
                text=f"{'+' if delta >= 0 else ''}{delta:.1f} °C",
            )
            if temp > 65 or (hr is not None and hr > 80):
                nivel = "alerta"
                aviso_kt.config(
                    bg="#450A0A", fg="#FECACA",
                    text=(
                        "ALERTA CRÍTICA: temperatura excesiva o humedad alta. "
                        "Riesgo de degradación del aislamiento."
                    ),
                )
            elif temp > 40 or (hr is not None and hr > 65):
                nivel = "precaucion"
                aviso_kt.config(
                    bg="#451A03", fg="#FDE68A",
                    text=(
                        f"⚠️ PRECAUCIÓN: temperatura elevada ({temp:g} °C). "
                        f"Se aplica el factor de corrección a {base_ref:g} °C."
                    ),
                )
            else:
                nivel = "normal"
                aviso_kt.config(
                    bg="#052E16", fg="#BBF7D0",
                    text=(
                        "Condiciones dentro del rango de la referencia. "
                        "El ensayo puede continuar."
                    ),
                )
            self._nivel_foco_ieee = nivel
            self._foco_visible = True
            self._pintar_foco_ieee()

        refrescar_kt()
        return refrescar_kt

    def _pintar_foco_ieee(self):
        focos = getattr(self, "_focos_ieee", None)
        if not focos:
            return
        nivel = getattr(self, "_nivel_foco_ieee", None)
        visible = getattr(self, "_foco_visible", True)
        reposo = "#1F2937"
        for clave, (celda, punto, nombre_lbl) in focos.items():
            marca = punto._emoji if clave != nivel or visible else ""
            try:
                punto.configure(
                    image=punto._foto if marca else punto._vacio,
                    bg=reposo,
                )
                nombre_lbl.configure(fg="#E5E7EB", bg=reposo, height=1)
                celda.configure(bg=reposo)
            except tk.TclError:
                return

    def _parpadear_foco_ieee(self):
        self._parpadeo_foco_job = None
        focos = getattr(self, "_focos_ieee", None)
        nivel = getattr(self, "_nivel_foco_ieee", None)
        if not focos or nivel not in focos:
            return
        celda = focos[nivel][0]
        try:
            if not celda.winfo_exists():
                return
        except tk.TclError:
            return
        self._foco_visible = not getattr(self, "_foco_visible", True)
        self._parpadear_marca_ieee()
        self._parpadeo_foco_job = self.after(
            self._ritmo_foco_ieee(), self._parpadear_foco_ieee,
        )

    def _parpadear_marca_ieee(self):
        """Solo muestra u oculta el emoji. El resto del panel no se mueve."""
        focos = getattr(self, "_focos_ieee", None)
        nivel = getattr(self, "_nivel_foco_ieee", None)
        if not focos or nivel not in focos:
            return
        punto = focos[nivel][1]
        visible = getattr(self, "_foco_visible", True)
        try:
            punto.configure(
                image=punto._foto if visible else punto._vacio,
            )
        except tk.TclError:
            return

    def _rotulo_estado(self, estado):
        if estado == "ACEPTADO":
            return "✅ ACEPTADO"
        if estado == "RECHAZADO":
            return "❌ RECHAZADO"
        return estado or "—"

    def _publicar_foco_ieee(self, nivel, texto, rotulo):
        if not getattr(self, "_focos_ieee", None):
            return
        self._nivel_foco_ieee = nivel
        self._foco_visible = True
        estilos = {
            "normal": ("#052E16", "#BBF7D0", "OPERATIVO", "#D1FAE5", "#065F46"),
            "precaucion": ("#451A03", "#FDE68A", "⚠️ PRECAUCIÓN", "#FEF3C7", "#92400E"),
            "alerta": ("#450A0A", "#FECACA", "ALERTA", "#FEE2E2", "#991B1B"),
        }
        fondo_aviso, tinta_aviso, *_resto = estilos[nivel]
        avisos = {
            "normal": "Dictamen aceptado. Los datos del cálculo quedan abajo.",
            "precaucion": "Dictamen: investigar. Los datos del cálculo quedan abajo.",
            "alerta": "Dictamen rechazado. Los datos del cálculo quedan abajo.",
        }
        try:
            self._aviso_ieee.config(
                bg=fondo_aviso, fg=tinta_aviso, text=avisos[nivel],
            )
            previo = self._datos_ieee.get("1.0", "end").strip()
            self._datos_ieee.configure(state="normal")
            self._datos_ieee.delete("1.0", "end")
            self._datos_ieee.insert(
                "1.0",
                (previo + "\n\n" + texto).strip() if previo else texto,
            )
            # El cuadro toma la altura de su texto (no tiene barra propia).
            self._datos_ieee.update_idletasks()
            renglones = self._datos_ieee.count("1.0", "end", "displaylines")
            if isinstance(renglones, tuple):
                renglones = renglones[0]
            self._datos_ieee.configure(
                height=max(2, int(renglones or 0) + 1), state="disabled",
            )
        except tk.TclError:
            return
        self._pintar_foco_ieee()
        job = getattr(self, "_parpadeo_foco_job", None)
        if job is not None:
            try:
                self.after_cancel(job)
            except tk.TclError:
                pass
        self._parpadeo_foco_job = self.after(
            self._ritmo_foco_ieee(), self._parpadear_foco_ieee,
        )

    def _ritmo_foco_ieee(self):
        nivel = getattr(self, "_nivel_foco_ieee", None) 
        if nivel == "alerta":
            return 140
        if nivel == "precaucion":
            return 280
        return 500

    def _cargar_paso_aislamiento(
        self, numero, paso_actual, contenedor, botones_paso,
    ):
        if numero in (3, 4):
            pruebas = self._obtener_pruebas_equipo()
            if not pruebas or not any(
                self.prueba_seleccionada == prueba for prueba in pruebas
            ):
                messagebox.showinfo(
                    "Prueba no disponible",
                    "Seleccione una prueba disponible en el paso 2 antes "
                    "de abrir los diagramas y la medición.",
                    parent=contenedor.winfo_toplevel(),
                )
                return

        paso_actual.set(numero)
        self._medida_diag_ra = (0, 0)
        for indice, boton in enumerate(botones_paso, start=1):
            boton["aplicar"](indice == numero)

        for widget in contenedor.winfo_children():
            widget.destroy()
        fondo = RA_VISTA_FONDO
        frame = ctk.CTkFrame(contenedor, fg_color=fondo, corner_radius=0)
        frame.pack(fill=tk.BOTH, expand=True)

        titulos = {
            1: "01. DATOS DEL EQUIPO",
            2: "02. SELECCIÓN DE PRUEBAS",
            3: "03. DIAGRAMAS DE BLOQUES",
            4: "04. CAPTURA DE LECTURAS",
        }
        fuente_titulo = ctk.CTkFont(family="Segoe UI", size=28, weight="bold")
        fuente_paso = ctk.CTkFont(family="Segoe UI", size=16, weight="bold")
        fuente_campo = ctk.CTkFont(family="Segoe UI", size=14, weight="bold")
        fuente_opcion = ctk.CTkFont(family="Segoe UI", size=14)

        subtitulos = {
            1: "Parámetros de placa y condiciones ambientales del transformador/equipo bajo ensayo.",
            2: "Elija la prueba y revise su esquema de medición y conexión.",
            3: "Diagramas de medición y conexiones del equipo.",
            4: "Captura de lecturas y dictamen de la prueba.",
        }

        def poner_titulos(padre, espacio=16):
            bloque = tk.Frame(padre, bg=fondo)
            bloque.pack(fill="x", pady=(0, espacio))
            fila = tk.Frame(bloque, bg=fondo)
            fila.pack(fill="x")
            izquierda = tk.Frame(fila, bg=fondo)
            izquierda.pack(side="left", fill="x", expand=True)
            fila_titulo = tk.Frame(izquierda, bg=fondo)
            fila_titulo.pack(anchor="w")
            tk.Label(
                fila_titulo, text="Resistencia de Aislamiento",
                bg=fondo, fg="#1A202C", font=("Segoe UI", 26, "bold"),
            ).pack(side="left")
            pastilla = ctk.CTkFrame(
                fila_titulo, fg_color="#FEF3C7", corner_radius=12,
                border_width=1,
                border_color="#FCD34D" if numero == 3 else "#F5D9A8",
            )
            pastilla.pack(side="left", padx=(12, 0))
            ctk.CTkLabel(
                pastilla, text="Modo Diagnóstico",
                text_color=(
                    RA_VISTA_NARANJA if numero == 3 else RA_VISTA_NARANJA_OSCURO
                ),
                fg_color="transparent",
                font=ctk.CTkFont(family="Consolas", size=11, weight="bold"),
            ).pack(padx=10, pady=2)
            equipo_actual = self.datos_prueba["tipo_equipo"].get().strip()
            tk.Label(
                izquierda, text=subtitulos[numero], bg=fondo, fg="#596573",
                font=("Segoe UI", 10), anchor="w",
            ).pack(anchor="w", pady=(4, 0))
            if numero != 1 and equipo_actual:
                tk.Label(
                    izquierda, text=equipo_actual, bg=fondo, fg="#334155",
                    font=("Segoe UI", 18, "bold"), anchor="w",
                ).pack(anchor="w", pady=(2, 0))
            numero_paso, _, resto_paso = titulos[numero].partition(" ")
            insignia = ctk.CTkFrame(
                fila, fg_color=RA_VISTA_NARANJA, corner_radius=10,
            )
            insignia.pack(side="right", anchor="n")
            ctk.CTkLabel(
                insignia, text=numero_paso[:2],
                text_color="#FEF3C7", fg_color=RA_VISTA_NARANJA_OSCURO,
                corner_radius=6,
                font=ctk.CTkFont(family="Consolas", size=20, weight="bold"),
            ).pack(side="left", padx=(10, 8), pady=8)
            ctk.CTkLabel(
                insignia, text=resto_paso,
                text_color="#FFFFFF", fg_color="transparent",
                font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            ).pack(side="left", padx=(0, 14), pady=8)
            if numero in (3, 4):
                barra_paso = tk.Canvas(
                    bloque, height=3, bg=fondo,
                    highlightthickness=0, bd=0,
                )
                barra_paso.pack(fill="x", pady=(12, 0))

                def pintar_barra_paso(_evento=None, lienzo=barra_paso):
                    ancho = max(lienzo.winfo_width(), 4)
                    lienzo.delete("all")
                    paradas = (
                        (0.0, (249, 115, 22)),
                        (0.33, (250, 204, 21)),
                        (0.66, (59, 130, 246)),
                        (1.0, (249, 115, 22)),
                    )
                    for x in range(ancho):
                        t = x / (ancho - 1)
                        for i in range(len(paradas) - 1):
                            t0, c0 = paradas[i]
                            t1, c1 = paradas[i + 1]
                            if t <= t1 or i == len(paradas) - 2:
                                parte = 0 if t1 == t0 else (t - t0) / (t1 - t0)
                                parte = max(0.0, min(1.0, parte))
                                color = tuple(
                                    int(c0[k] + (c1[k] - c0[k]) * parte)
                                    for k in range(3)
                                )
                                lienzo.create_line(
                                    x, 0, x, 3, fill="#%02x%02x%02x" % color,
                                )
                                break

                barra_paso.bind("<Configure>", pintar_barra_paso)
            else:
                tk.Frame(
                    bloque, bg=RA_VISTA_BORDE, height=2,
                ).pack(fill="x", pady=(12, 0))

        if numero == 1:
            formulario = ctk.CTkFrame(frame, fg_color=fondo, corner_radius=0)
            formulario.pack(expand=True, fill="both", padx=28, pady=18)
            poner_titulos(formulario)
            cuerpo = tk.Frame(formulario, bg=fondo)
            cuerpo.pack(fill="both", expand=True)
            tarjeta = ctk.CTkFrame(
                cuerpo, fg_color=RA_VISTA_TARJETA, corner_radius=16,
                border_width=2, border_color=RA_VISTA_BORDE,
            )
            tarjeta.pack(side="left", fill="both", expand=True)
            barra_tarjeta = tk.Canvas(
                tarjeta, height=3, bg=RA_VISTA_TARJETA,
                highlightthickness=0, bd=0,
            )
            barra_tarjeta.pack(fill="x", padx=12, pady=(10, 0))

            def pintar_barra_datos(_evento=None):
                ancho = max(barra_tarjeta.winfo_width(), 4)
                barra_tarjeta.delete("all")
                paradas = (
                    (0.0, (249, 115, 22)),
                    (0.33, (250, 204, 21)),
                    (0.66, (59, 130, 246)),
                    (1.0, (249, 115, 22)),
                )
                for x in range(ancho):
                    t = x / (ancho - 1)
                    for i in range(len(paradas) - 1):
                        t0, c0 = paradas[i]
                        t1, c1 = paradas[i + 1]
                        if t <= t1 or i == len(paradas) - 2:
                            parte = 0 if t1 == t0 else (t - t0) / (t1 - t0)
                            parte = max(0.0, min(1.0, parte))
                            color = tuple(
                                int(c0[k] + (c1[k] - c0[k]) * parte)
                                for k in range(3)
                            )
                            barra_tarjeta.create_line(
                                x, 0, x, 3, fill="#%02x%02x%02x" % color,
                            )
                            break

            barra_tarjeta.bind("<Configure>", pintar_barra_datos)
            rejilla = ctk.CTkFrame(tarjeta, fg_color="transparent")
            rejilla.pack(fill="x", padx=18, pady=(6, 16))

            def campo(texto, fila):
                ctk.CTkLabel(
                    rejilla, text=texto.upper(),
                    font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
                    text_color="#6F6A63", fg_color="transparent",
                ).grid(row=fila, column=0, sticky="e", padx=(8, 18), pady=9)

            campo("Tipo de Equipo:", 0)
            combo_equipo = ctk.CTkComboBox(
                rejilla,
                variable=self.datos_prueba["tipo_equipo"],
                values=EQUIPOS_AISLAMIENTO,
                state="readonly",
                width=380, height=36, corner_radius=8,
                fg_color=RA_VISTA_INPUT, border_color="#C5BCAC", border_width=2,
                button_color="#E4DDD2", button_hover_color="#D5CBBC",   
                text_color="#1C1917", dropdown_fg_color="#FFFCF8",
                font=fuente_opcion, dropdown_font=fuente_opcion,
            )
            combo_equipo.grid(row=0, column=1, sticky="w", pady=9)

            def limitar_a_cuatro(variable):
                if getattr(variable, "_sape_limite_4", False):
                    return

                def cortar(*_args):
                    texto = variable.get()
                    if len(texto) > 4:
                        variable.set(texto[:4])

                variable.trace_add("write", cortar)
                variable._sape_limite_4 = True
                cortar()

            campo("Temp. ambiente (°C):", 3)
            limitar_a_cuatro(self.datos_prueba["temp_ambiente"])
            entrada_ambiente = ctk.CTkEntry(
                rejilla, textvariable=self.datos_prueba["temp_ambiente"],
                width=72, height=36, corner_radius=8,
                fg_color=RA_VISTA_INPUT, border_color="#C5BCAC", border_width=2,
                text_color="#1C1917", font=fuente_opcion,
            )
            entrada_ambiente.grid(row=3, column=1, sticky="w", pady=9)
            campo("Humedad relativa (%):", 4)
            limitar_a_cuatro(self.datos_prueba["humedad_relativa"])
            entrada_humedad = ctk.CTkEntry(
                rejilla, textvariable=self.datos_prueba["humedad_relativa"],
                width=72, height=36, corner_radius=8,
                fg_color=RA_VISTA_INPUT, border_color="#C5BCAC", border_width=2,
                text_color="#1C1917", font=fuente_opcion,
            )
            entrada_humedad.grid(row=4, column=1, sticky="w", pady=9)
            campo("Temp. del devanado (°C):", 5)
            limitar_a_cuatro(self.datos_prueba["temp_devanado"])
            entrada_devanado = ctk.CTkEntry(
                rejilla, textvariable=self.datos_prueba["temp_devanado"],
                width=72, height=36, corner_radius=8,
                fg_color=RA_VISTA_INPUT, border_color="#C5BCAC", border_width=2, 
                text_color="#1C1917", font=fuente_opcion,
            )
            entrada_devanado.grid(row=5, column=1, sticky="w", pady=9)

            campo("Tipo de aislamiento:", 6)
            frame_aislamiento = ctk.CTkFrame(rejilla, fg_color="transparent")
            frame_aislamiento.grid(row=6, column=1, sticky="w", pady=9)
            radios_aislamiento = []
            for texto, valor in (
                ("Sumergido en Aceite", "Sumergido en Aceite"),
                ("Seco (Sólido)", "Seco"),
            ):
                radio = ctk.CTkRadioButton(
                    frame_aislamiento, text=texto,
                    variable=self.datos_prueba["aislamiento"], value=valor,
                    font=fuente_opcion, fg_color=RA_VISTA_NARANJA,
                    hover_color="#CF7422", border_color="#C8C0B4",
                    text_color="#1C1917",
                )
                radio.pack(side="left", padx=(0, 22))
                radios_aislamiento.append(radio)

            etiqueta_config = ctk.CTkLabel(
                rejilla, text="CONFIGURACIÓN:",
                font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
                text_color="#6F6A63", fg_color="transparent",
            )
            frame_config = ctk.CTkFrame(rejilla, fg_color="transparent")
            for texto_cfg in ("Trifásico", "Monofásico"):
                ctk.CTkRadioButton(
                    frame_config, text=texto_cfg,
                    variable=self.datos_prueba["configuracion"],
                    value=texto_cfg, font=fuente_opcion,
                    fg_color=RA_VISTA_NARANJA, hover_color="#CF7422",
                    border_color="#C8C0B4", text_color="#1C1917",
                    command=lambda: actualizar_opciones_equipo(),
                ).pack(side="left", padx=(0, 22))
            etiqueta_fase = ctk.CTkLabel(
                rejilla, text="FASE:",
                font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
                text_color="#6F6A63", fg_color="transparent",
            )
            frame_fase = ctk.CTkFrame(rejilla, fg_color="transparent")
            for letra in ("A", "B", "C"):
                ctk.CTkRadioButton(
                    frame_fase, text=letra,
                    variable=self.datos_prueba["fase"], value=letra,
                    font=fuente_opcion, fg_color=RA_VISTA_NARANJA,
                    hover_color="#CF7422", border_color="#C8C0B4",
                    text_color="#1C1917",
                ).pack(side="left", padx=(0, 16))

            etiqueta_extra = ctk.CTkLabel(
                rejilla, text="", font=fuente_campo,
                text_color="#334155", fg_color="transparent",
            )
            combo_apartarrayos = ctk.CTkComboBox(
                rejilla,
                variable=self.datos_prueba["secciones_apartarrayos"],
                values=("Una sección", "Varias secciones"),
                state="readonly",
                width=350,
                font=fuente_opcion,
                dropdown_font=fuente_opcion,
            )
            combo_autotransformador = ctk.CTkComboBox(
                rejilla,
                variable=self.datos_prueba["terciario_autotransformador"],
                values=("Con terciario", "Sin terciario"),
                state="readonly",
                width=350,
                font=fuente_opcion,
                dropdown_font=fuente_opcion,
            )

            def actualizar_opciones_equipo(_valor=None):
                etiqueta_extra.grid_remove()
                combo_apartarrayos.grid_remove()
                combo_autotransformador.grid_remove()
                etiqueta_fase.grid_remove()
                frame_fase.grid_remove()
                fila_extra = 7
                equipo = self.datos_prueba["tipo_equipo"].get()
                instrumento = any(
                    nombre in equipo for nombre in ("TCs", "TPs", "TPCs")
                )
                if instrumento:
                    etiqueta_config.grid_remove()
                    frame_config.grid_remove()
                    etiqueta_fase.grid(
                        row=1, column=0, sticky="e", padx=(0, 20), pady=15,
                    )
                    frame_fase.grid(row=1, column=1, sticky="w", pady=15)
                else:
                    etiqueta_config.grid(
                        row=1, column=0, sticky="e", padx=(0, 20), pady=15,
                    )
                    frame_config.grid(row=1, column=1, sticky="w", pady=15)
                    if self.datos_prueba["configuracion"].get() == "Monofásico":
                        etiqueta_fase.grid(
                            row=2, column=0, sticky="e", padx=(0, 20), pady=15,
                        )
                        frame_fase.grid(row=2, column=1, sticky="w", pady=15)
                    else:
                        etiqueta_fase.grid_remove()
                        frame_fase.grid_remove()
                # Apartarrayos y máquinas rotatorias no llevan aceite: el
                # aislamiento queda fijo en seco y la opción de aceite se apaga.
                solido = self._solo_aislamiento_solido(equipo)
                if solido:
                    self.datos_prueba["aislamiento"].set("Seco")
                radios_aislamiento[0].configure(
                    state="disabled" if solido else "normal",
                )
                if "Apartarrayos" in equipo:
                    etiqueta_extra.configure(
                        text="Configuración del apartarrayos:",
                    )
                    etiqueta_extra.grid(
                        row=fila_extra, column=0, sticky="e",
                        padx=(0, 20), pady=15,
                    )
                    combo_apartarrayos.grid(
                        row=fila_extra, column=1, sticky="w", pady=15,
                    )
                elif "Autotransformadores" in equipo:
                    etiqueta_extra.configure(text="Devanado terciario:")
                    etiqueta_extra.grid(
                        row=fila_extra, column=0, sticky="e",
                        padx=(0, 20), pady=15,
                    )
                    combo_autotransformador.grid(
                        row=fila_extra, column=1, sticky="w", pady=15,
                    )

            combo_equipo.configure(command=actualizar_opciones_equipo)
            for radio in radios_aislamiento:
                radio.configure(command=actualizar_opciones_equipo)
            actualizar_opciones_equipo()
            rejilla.grid_columnconfigure(1, weight=1)

            tk.Frame(formulario, bg=RA_VISTA_BORDE, height=1).pack(
                fill="x", pady=(16, 10),
            )
            fila_acciones = tk.Frame(formulario, bg=fondo)
            fila_acciones.pack(fill="x")

            boton_siguiente = _boton_relieve_ra(
                fila_acciones, "SIGUIENTE  →",
                lambda: self._cargar_paso_aislamiento(
                    2, paso_actual, contenedor, botones_paso,
                ),
            )
            boton_siguiente.pack(side="right")
            tk.Label(
                formulario,
                text="Ingeniería de pruebas de alta tensión  ·  Subestaciones eléctricas",
                bg=fondo, fg="#596573", font=("Consolas", 9),
            ).pack(side="bottom", anchor="w", pady=(12, 0))
            tk.Label(
                formulario, text="Módulo 01 / 04",
                bg=fondo, fg="#4A5568", font=("Consolas", 9, "bold"),
            ).pack(side="bottom", anchor="e")

            campos_datos = [
                combo_equipo,
                entrada_ambiente,
                entrada_humedad,
                entrada_devanado,
            ]

            def avanzar_campo(indice):
                for campo_siguiente in (
                    campos_datos[indice + 1:] + campos_datos[:indice + 1]
                ):
                    try:
                        if not campo_siguiente.winfo_ismapped():
                            continue
                        campo_siguiente.focus_set()
                    except tk.TclError:
                        continue
                    break
                return "break"

            def enfocar_siguiente(_evento=None):
                boton_siguiente.focus_set()
                return "break"

            def activar_siguiente(_evento=None):
                boton_siguiente.invoke()
                return "break"

            for indice, campo_widget in enumerate(campos_datos):
                al_enter = (
                    enfocar_siguiente
                    if campo_widget is entrada_devanado
                    else (lambda _evento, i=indice: avanzar_campo(i))
                )
                campo_widget.bind("<Return>", al_enter, add="+")
                campo_widget.bind("<KP_Enter>", al_enter, add="+")
            boton_siguiente.bind("<Return>", activar_siguiente, add="+")
            boton_siguiente.bind("<KP_Enter>", activar_siguiente, add="+")

            def marcar_siguiente(_evento=None):
                boton_siguiente.marcar(True)

            def desmarcar_siguiente(_evento=None):
                boton_siguiente.marcar(False)

            boton_siguiente.bind("<FocusIn>", marcar_siguiente, add="+")
            boton_siguiente.bind("<FocusOut>", desmarcar_siguiente, add="+")

        elif numero == 2:
            formulario = ctk.CTkFrame(frame, fg_color=fondo, corner_radius=0)
            formulario.pack(expand=True, fill="both", padx=28, pady=18)
            poner_titulos(formulario)
            zona = tk.Frame(formulario, bg=fondo)
            zona.pack(fill="x")
            zona.grid_columnconfigure(0, weight=1)
            self._crear_tabla_pruebas(zona, row=0)

            tk.Frame(formulario, bg=RA_VISTA_BORDE, height=1).pack(
                fill="x", pady=(16, 10),
            )
            fila_acciones = tk.Frame(formulario, bg=fondo)
            fila_acciones.pack(fill="x")
            boton_siguiente2 = _boton_relieve_ra(
                fila_acciones, "SIGUIENTE  →",
                lambda: self._cargar_paso_aislamiento(
                    3, paso_actual, contenedor, botones_paso,
                ),
            )
            boton_siguiente2.pack(side="right")
            tk.Label(
                formulario,
                text="Ingeniería de pruebas de alta tensión  ·  Subestaciones eléctricas",
                bg=fondo, fg="#596573", font=("Consolas", 9),
            ).pack(side="bottom", anchor="w", pady=(12, 0))
            tk.Label(
                formulario, text="Módulo 02 / 04",
                bg=fondo, fg="#4A5568", font=("Consolas", 9, "bold"),
            ).pack(side="bottom", anchor="e")

            def activar_siguiente2(_evento=None):
                boton_siguiente2.invoke()
                return "break"

            boton_siguiente2.bind("<Return>", activar_siguiente2, add="+")
            boton_siguiente2.bind("<KP_Enter>", activar_siguiente2, add="+")
            boton_siguiente2.bind(
                "<FocusIn>",
                lambda _evento=None: boton_siguiente2.marcar(True),
                add="+",
            )
            boton_siguiente2.bind(
                "<FocusOut>",
                lambda _evento=None: boton_siguiente2.marcar(False),
                add="+",
            )

        else:
            frame.pack_configure(padx=60, pady=40)
            prueba = self.prueba_seleccionada
            if prueba is None:
                cabecera = ctk.CTkFrame(frame, fg_color="transparent")
                cabecera.pack(anchor="w")
                poner_titulos(cabecera, espacio=12)
                tk.Label(
                    frame,
                    text=(
                        "El procedimiento SOM-3531 no especifica una prueba "
                        "de resistencia de aislamiento para este equipo."
                    ),
                    bg=fondo, fg="#334155",
                    font=("Segoe UI", 14, "bold"), wraplength=640,
                    justify="left",
                ).pack(anchor="w")
                return

            frame.pack_configure(padx=0, pady=0)
            contenido = ctk.CTkFrame(frame, fg_color="transparent")
            contenido.pack(
                expand=True, fill="both",
                padx=28 if numero == 3 else 40,
                pady=(12, 8) if numero == 3 else (18, 8),
            )
            poner_titulos(contenido, espacio=8)

            prueba_ra = self.prueba_seleccionada or {}
            textos_diag = {
                "mide": self._texto_bloques_ra("mide"),
                "conexiones": self._texto_bloques_ra("conexiones"),
            }

            def medidas_diag(texto):
                rejilla = _rejilla_bloques(texto)
                while rejilla and not any(
                    ch.strip() for ch, _ in rejilla[-1]
                ):
                    rejilla.pop()
                while rejilla and not any(
                    ch.strip() for ch, _ in rejilla[0]
                ):
                    rejilla.pop(0)
                if not rejilla:
                    return (0, 0)
                ocupadas = [
                    c
                    for fila in rejilla
                    for c, (glifo, _) in enumerate(fila)
                    if glifo.strip()
                ]
                if not ocupadas:
                    return (0, 0)
                return (max(ocupadas) - min(ocupadas) + 1, len(rejilla))

            medidas = (
                medidas_diag(textos_diag["mide"]),
                medidas_diag(textos_diag["conexiones"]),
            )
            cols_compartidas = max(par[0] for par in medidas)
            filas_compartidas = max(par[1] for par in medidas)

            def montar_diagrama(tab, modo):
                fondo_panel = "#FFFFFF"
                panel = tk.Frame(tab, bg=fondo_panel)
                panel.pack(anchor="nw", padx=12, pady=(4, 8))
                panel.grid_columnconfigure(0, weight=0)
                columna = tk.Frame(panel, bg=fondo_panel)
                columna.grid(row=0, column=0, sticky="nw")
                tk.Label(
                    columna,
                    text="MEDICIÓN" if modo == "mide" else "CONEXIONES",
                    bg=fondo_panel, fg=RA_VISTA_NARANJA,
                    font=("Consolas", 22, "bold"), anchor="w",
                ).pack(anchor="nw", padx=6, pady=(0, 4))
                lienzo = _LienzoBloquesNeon(columna)
                lienzo._color_medicion = RA_NARANJA_PASTEL
                lienzo._marco_paso = frame
                lienzo._cols_compartidas = cols_compartidas
                lienzo._filas_compartidas = filas_compartidas
                lienzo._alto_maximo = max(
                    280, lienzo.winfo_screenheight() - 420
                )
                lienzo.pack(anchor="nw")
                leyenda = tk.Frame(panel, bg=fondo_panel)

                def pintar_leyenda(secciones, fondo_leyenda="#FFFFFF"):
                    lienzo._oyentes_parpadeo = []
                    lienzo._orden_badges = []
                    for hijo in leyenda.winfo_children():
                        hijo.destroy()
                    secciones = [
                        (titulo, filas)
                        for titulo, filas in secciones
                        if filas
                    ]
                    if not secciones:
                        leyenda.grid_remove()
                        return
                    leyenda.configure(bg=fondo_leyenda)
                    leyenda.grid(
                        row=0, column=1, sticky="nw", padx=(18, 22), pady=(24, 16),
                    )
                    fila = 0

                    for _titulo, filas in secciones:
                        for codigo, descripcion, color in filas:
                            es_conexion = codigo in ("LÍNEA", "TIERRA", "GUARDA")
                            medida = (
                                modo == "mide"
                                and not es_conexion
                                and codigo in lienzo._codigos_parpadeo
                            )
                            if modo == "mide" and not medida and not es_conexion:
                                color = RA_AZUL_MARINO
                            badge = ctk.CTkLabel(
                                leyenda, text=codigo, fg_color=color,
                                text_color="#FFFFFF", corner_radius=4,
                                width=78, height=26, anchor="center",
                                font=ctk.CTkFont(
                                    family="Consolas", size=12, weight="bold",
                                ),
                            )
                            badge.grid(
                                row=fila, column=0, sticky="w",
                                pady=6, padx=(0, 14),
                            )
                            if es_conexion:
                                lienzo._orden_badges.append(codigo)
                            if medida or es_conexion:
                                def al_fase(
                                    grupo, badge=badge, color=color,
                                    codigo=codigo, es_medida=medida,
                                ):
                                    try:
                                        if not badge.winfo_exists():
                                            return
                                    except tk.TclError:
                                        return
                                    oculto = (
                                        es_medida and grupo is None
                                    ) or (
                                        not es_medida and grupo == "CONEXIONES_OFF"
                                    )
                                    if oculto:
                                        badge.configure(
                                            fg_color="#FFF7ED", text_color=color,
                                        )
                                    else:
                                        badge.configure(
                                            fg_color=color, text_color="#FFFFFF",
                                        )

                                lienzo._oyentes_parpadeo.append(al_fase)
                            tk.Label(
                                leyenda, text=descripcion, bg=fondo_leyenda,
                                fg="#334155", font=("Segoe UI", 11), anchor="w",
                            ).grid(row=fila, column=1, sticky="w", pady=6)
                            fila += 1

                lienzo._titulo = "MEDICIÓN" if modo == "mide" else "CONEXIONES"
                lienzo._codigos_parpadeo = set(
                    _RE_CODIGO_RESISTENCIA_RA.findall(
                        str(prueba_ra.get("medicion", ""))
                    )
                )
                lienzo._tierra_en_tanque = _columna_pide_tanque(
                    prueba_ra.get("tierra", "")
                )
                lienzo._guarda_en_tanque = _columna_pide_tanque(
                    prueba_ra.get("guarda", "")
                )
                lienzo._tierra_en_tierra = _columna_pide_tierra(
                    prueba_ra.get("tierra", "")
                )
                try:
                    lienzo._tierra_en_devanado = bool(
                        set(_sape1()._ra_letras_conexion(
                            prueba_ra.get("tierra", "")
                        )) & set("HXYPSABCD")
                    )
                except Exception:
                    lienzo._tierra_en_devanado = False
                try:
                    lienzo._letras_linea = _sape1()._ra_letras_conexion(
                        prueba_ra.get("linea", "")
                    )
                except Exception:
                    lienzo._letras_linea = set()
                lienzo._sitios_linea = _sitios_rol_ra(prueba_ra.get("linea", ""))
                lienzo._sitios_tierra = _sitios_rol_ra(
                    prueba_ra.get("tierra", ""), simbolo_tierra=True,
                )
                lienzo._sitios_guarda = _sitios_rol_ra(prueba_ra.get("guarda", ""))
                texto = textos_diag[modo]
                if modo == "mide":
                    # Todas las resistencias medidas van en el mismo naranja fuerte.
                    filas_medicion = [
                        (codigo, descripcion, "#EA580C")
                        for codigo, descripcion in _leyenda_resistencias_ra(
                            texto, self.datos_prueba["tipo_equipo"].get(),
                        )
                    ]
                    pintar_leyenda(
                        [("MEDICIÓN", filas_medicion)],
                        fondo_leyenda="#FFFFFF",
                    )
                else:
                    pintar_leyenda(
                        [("CONEXIONES", list(
                            _leyenda_conexiones_ra(texto, prueba_ra)
                        ))],
                        fondo_leyenda="#FFFFFF",
                    )
                lienzo.cargar(texto)

            if numero == 3:
                fila_pie = tk.Frame(contenido, bg="#F6F3EB")
                fila_pie.pack(side="bottom", fill="x", pady=(8, 0))
                area_diagramas = tk.Frame(contenido, bg="#F6F3EB")
                area_diagramas.pack(fill="both", expand=True)
                visor = tk.Frame(
                    area_diagramas, bg="#FFFFFF",
                    highlightbackground="#E5E0D5", highlightthickness=1,
                )
                visor.pack(fill="both", expand=True, pady=(0, 4))
                barra_y = tk.Scrollbar(visor, orient="vertical")
                barra_x = tk.Scrollbar(visor, orient="horizontal")
                puerto = tk.Canvas(
                    visor, bg="#FFFFFF", highlightthickness=0, bd=0,
                    yscrollcommand=barra_y.set,
                    xscrollcommand=barra_x.set,
                )
                barra_y.configure(command=puerto.yview)
                barra_x.configure(command=puerto.xview)
                barra_x.pack(side="bottom", fill="x")
                barra_y.pack(side="right", fill="y")
                puerto.pack(side="left", fill="both", expand=True)
                puerto._scroll_propio = puerto
                seccion = tk.Frame(puerto, bg="#FFFFFF")
                puerto.create_window((0, 0), window=seccion, anchor="nw")

                def ajustar_region(_evento=None, puerto=puerto):
                    puerto.configure(
                        scrollregion=puerto.bbox("all") or (0, 0, 1, 1),
                    )

                seccion.bind("<Configure>", ajustar_region)
                for modo_diag in ("mide", "conexiones"):
                    try:
                        montar_diagrama(seccion, modo_diag)
                    except Exception:
                        import traceback
                        tk.Label(
                            seccion,
                            text=traceback.format_exc()[-900:],
                            bg="#FFFFFF", fg="#B91C1C",
                            font=("Consolas", 9), justify="left", anchor="w",
                        ).pack(anchor="w", padx=12, pady=8)
                seccion.update_idletasks()
                ajustar_region()

                tk.Label(
                    fila_pie, text="Módulo 03 / 04", bg="#F6F3EB",
                    fg="#64748B", font=("Segoe UI", 9, "bold"),
                ).pack(side="left")
                boton_siguiente3 = _boton_relieve_ra(
                    fila_pie, "SIGUIENTE  →",
                    lambda: self._cargar_paso_aislamiento(
                        4, paso_actual, contenedor, botones_paso,
                    ),
                )
                boton_siguiente3.pack(side="right")

                def activar_siguiente3(_evento=None):
                    boton_siguiente3.invoke()
                    return "break"

                boton_siguiente3.bind("<Return>", activar_siguiente3, add="+")
                boton_siguiente3.bind("<KP_Enter>", activar_siguiente3, add="+")
                boton_siguiente3.bind(
                    "<FocusIn>",
                    lambda _evento=None: boton_siguiente3.marcar(True),
                    add="+",
                )
                boton_siguiente3.bind(
                    "<FocusOut>",
                    lambda _evento=None: boton_siguiente3.marcar(False),
                    add="+",
                )
                return

            columna_kt = tk.Frame(contenido, bg=RA_VISTA_PANEL, width=360)
            columna_kt.pack(side="right", fill="both", padx=(18, 0))
            # La columna no lleva barra propia: toma la altura de su contenido
            # y se recorre con la barra de la ventana.
            tk.Frame(columna_kt, bg=RA_VISTA_PANEL, width=346, height=1).pack()
            cuerpo_col = tk.Frame(columna_kt, bg=RA_VISTA_PANEL)
            cuerpo_col.pack(fill="both", expand=True)
            self._montar_correccion_ieee(cuerpo_col)

            tk.Label(
                contenido,
                text=self._nota_criterio_ra(prueba),
                bg="#F8FAFC", fg="#475569",
                font=("Segoe UI", 10),
                justify="left", anchor="w", wraplength=860,
            ).pack(anchor="w", pady=(0, 6))

            barra = ctk.CTkFrame(contenido, fg_color="#F1F5F9", corner_radius=10)
            barra.pack(fill="x", pady=(6, 0))
            self.clave_lectura_ra = (
                "lectura_10min" if prueba["minutos"] == 10
                else "lectura_1min"
            )
            campos_lectura = (
                (("30 s", "lectura_30s"), ("1 min", "lectura_1min"), ("10 min", "lectura_10min"))
                if prueba["minutos"] == 10
                else (("1 min", "lectura_1min"),)
            )
            fila_campos = tk.Frame(barra, bg="#F1F5F9")
            fila_campos.pack(anchor="w", padx=12, pady=(12, 0))
            entradas_lectura = []
            for rotulo, clave in campos_lectura:
                columna_campo = tk.Frame(fila_campos, bg="#F1F5F9")
                columna_campo.pack(side="left", anchor="n", padx=(0, 8))
                ctk.CTkLabel(
                    columna_campo, text=f"{rotulo} (MΩ, GΩ o TΩ):",
                    font=ctk.CTkFont(size=14, weight="bold"),
                    text_color="#334155",
                ).pack(anchor="w")
                entrada_lectura = ctk.CTkEntry(
                    columna_campo, textvariable=self.datos_prueba[clave],
                    placeholder_text="Ingrese valor...",
                    width=150,
                )
                entrada_lectura.pack(anchor="w", pady=(6, 0))
                entradas_lectura.append(entrada_lectura)
            fila_botones = tk.Frame(barra, bg="#F1F5F9")
            fila_botones.pack(anchor="w", padx=12, pady=(8, 12))
            fuente_boton = tkfont.Font(
                family="Consolas", size=11, weight="bold",
            )
            boton_calcular = _boton_relieve_ra(
                fila_botones, "CALCULAR", self.calcular_resultado,
                ancho=fuente_boton.measure("CALCULAR") + 28,
                modo="diagnostico", fondo="#F1F5F9",
                alto_caja=28, alto_lienzo=40, fuente_nombre="Consolas",
            )
            boton_calcular.pack(side="left")
            _boton_relieve_ra(
                fila_botones, "GUARDAR",
                lambda: self._guardar_lectura_anexo_a(barra.winfo_toplevel()),
                ancho=fuente_boton.measure("GUARDAR") + 28,
                modo="diagnostico", fondo="#F1F5F9",
                alto_caja=28, alto_lienzo=40, fuente_nombre="Consolas",
            ).pack(side="left", padx=(8, 0))

            def enfocar_siguiente_lectura(indice):
                def _al_enter(_evento=None):
                    if indice + 1 < len(entradas_lectura):
                        entradas_lectura[indice + 1].focus_set()
                    else:
                        boton_calcular.focus_set()
                    return "break"
                return _al_enter

            for indice, entrada_lec in enumerate(entradas_lectura):
                al_enter_lec = enfocar_siguiente_lectura(indice)
                for widget_lec in (entrada_lec, *entrada_lec.winfo_children()):
                    widget_lec.bind("<Return>", al_enter_lec, add="+")
                    widget_lec.bind("<KP_Enter>", al_enter_lec, add="+")

            def activar_calcular(_evento=None):
                boton_calcular.invoke()
                return "break"

            boton_calcular.bind("<Return>", activar_calcular, add="+")
            boton_calcular.bind("<KP_Enter>", activar_calcular, add="+")
            boton_calcular.bind(
                "<FocusIn>",
                lambda _evento=None: boton_calcular.marcar(True),
                add="+",
            )
            boton_calcular.bind(
                "<FocusOut>",
                lambda _evento=None: boton_calcular.marcar(False),
                add="+",
            )
            panel_dictamen = ctk.CTkFrame(
                contenido, fg_color="#FFFFFF", corner_radius=10,
                border_width=1, border_color="#E2E8F0",
            )
            panel_dictamen.pack(fill="x", pady=(14, 0))
            self._dict_encabezado = tk.Frame(panel_dictamen, bg="#F1F5F9")
            self._dict_encabezado.pack(fill="x")
            self._dict_acento = tk.Frame(
                self._dict_encabezado, bg="#94A3B8", width=6,
            )
            self._dict_acento.pack(side="left", fill="y")
            self._dict_acento.pack_propagate(False)
            self._dict_icono = tk.Label(
                self._dict_encabezado, text="•", bg="#F1F5F9",
                fg="#64748B", font=("Segoe UI", 20, "bold"),
            )
            self._dict_icono.pack(side="left", padx=(14, 10), pady=8)
            self._dict_estado = tk.Label(
                self._dict_encabezado, text="DICTAMEN TÉCNICO",
                bg="#F1F5F9", fg="#334155",
                font=("Segoe UI", 16, "bold"),
            )
            self._dict_estado.pack(side="left", pady=8)
            cuerpo_dictamen = tk.Frame(panel_dictamen, bg="#FFFFFF")
            cuerpo_dictamen.pack(fill="x", padx=16, pady=(12, 12))
            fila_indices = tk.Frame(cuerpo_dictamen, bg="#FFFFFF")
            fila_indices.pack(fill="x", pady=(0, 4))

            def tarjeta_indice(titulo):
                tarjeta = tk.Frame(
                    fila_indices, bg=RA_MANDARINA_CLARO,
                    highlightbackground=RA_NARANJA_PASTEL, highlightthickness=2,
                )
                tarjeta.pack(side="left", padx=(0, 18))
                tk.Label(
                    tarjeta, text=titulo, bg=RA_MANDARINA_CLARO, fg=RA_NARANJA_PASTEL,
                    font=("Segoe UI", 13, "bold"),
                ).pack(anchor="w", padx=16, pady=(12, 0))
                valor = tk.Label(
                    tarjeta, text="——", bg=RA_MANDARINA_CLARO, fg=RA_NARANJA_PASTEL,
                    font=("Segoe UI", 28, "bold"),
                )
                valor.pack(anchor="w", padx=16, pady=(0, 12))
                return valor

            self.lbl_ia_valor = tarjeta_indice("Índice de Absorción (DAR)")
            self.lbl_ip_valor = tarjeta_indice("Índice de Polarización (IP)")
            tk.Frame(
                cuerpo_dictamen, bg="#EEEEEE", height=1,
            ).pack(fill="x", pady=(12, 10))
            tk.Label(
                cuerpo_dictamen, text="OBSERVACIONES TÉCNICAS:",
                bg="#FFFFFF", fg="#4A5568",
                font=("Segoe UI", 10, "bold"),
            ).pack(anchor="w")
            tk.Frame(
                cuerpo_dictamen, bg="#EDF2F7", height=1,
            ).pack(fill="x", pady=(8, 12))
            fila_equipo = tk.Frame(cuerpo_dictamen, bg="#FFFFFF")
            fila_equipo.pack(fill="x")
            self.lbl_equipo_ra = tk.Label(
                fila_equipo, text="——", bg="#FFFFFF", fg="#2D3748",
                font=("Segoe UI", 11, "bold"),
                justify="left", anchor="w", wraplength=640,
            )
            self.lbl_equipo_ra.pack(anchor="w", fill="x")
            self.lbl_aislamiento_ra = tk.Label(
                fila_equipo, text="", bg="#FFFFFF", fg="#2D3748",
                font=("Segoe UI", 11),
                justify="left", anchor="w", wraplength=640,
            )
            self.lbl_aislamiento_ra.pack(anchor="w", fill="x")

            def ajustar_corte_equipo(evento, fila=fila_equipo):
                if evento.widget is not fila:
                    return
                ancho = max(evento.width, 120)
                for etiqueta in (self.lbl_equipo_ra, self.lbl_aislamiento_ra):
                    if int(etiqueta.cget("wraplength")) != ancho:
                        etiqueta.configure(wraplength=ancho)

            fila_equipo.bind("<Configure>", ajustar_corte_equipo)
            self.lbl_amb_ra = tk.Label(
                cuerpo_dictamen, text="•  Ambiente: ——",
                bg="#FFFFFF", fg="#2D3748",
                font=("Segoe UI", 10), anchor="w",
            )
            self.lbl_amb_ra.pack(fill="x", padx=(14, 0), pady=(4, 0))
            self.lbl_dev_ra = tk.Label(
                cuerpo_dictamen, text="•  Devanado: ——",
                bg="#FFFFFF", fg="#2D3748",
                font=("Segoe UI", 10), anchor="w",
            )
            self.lbl_dev_ra.pack(fill="x", padx=(14, 0))
            self.lbl_kt_ra = tk.Label(
                cuerpo_dictamen, text="•  Kt = ——",
                bg="#FFFFFF", fg="#2D3748",
                font=("Segoe UI", 10), anchor="w",
            )
            self.lbl_kt_ra.pack(fill="x", padx=(14, 0), pady=(0, 12))
            rejilla_datos = tk.Frame(cuerpo_dictamen, bg="#FFFFFF")
            rejilla_datos.pack(fill="x", pady=(0, 12))

            def caja_formula(padre, titulo):
                caja = tk.Frame(
                    padre, bg="#F8FAFC",
                    highlightbackground="#E2E8F0", highlightthickness=1,
                )
                caja.pack(
                    side="left", expand=True, fill="both",
                    padx=(0, 10), pady=0, anchor="n",
                )
                tk.Label(
                    caja, text=titulo, bg="#F8FAFC", fg="#1A202C",
                    font=("Segoe UI", 10, "bold"), anchor="w",
                ).pack(fill="x", padx=12, pady=(10, 6))
                etiqueta = tk.Label(
                    caja, text="——", bg="#F8FAFC", fg="#4A5568",
                    font=("Segoe UI", 10), justify="left", wraplength=360,
                    anchor="w",
                )
                etiqueta.pack(fill="x", padx=12, pady=(0, 10))
                return etiqueta

            self.lbl_resistencias_ra = caja_formula(
                rejilla_datos, "Resistencia a 20 °C:"
            )
            self.lbl_calculos_ra = caja_formula(
                rejilla_datos, "Cálculos aplicados:"
            )
            self._marco_conclusion = tk.Frame(
                cuerpo_dictamen, bg="#F8FAFC",
            )
            self._marco_conclusion.pack(fill="x")
            self._dict_acento_conclusion = tk.Frame(
                self._marco_conclusion, bg="#94A3B8", width=4,
            )
            self._dict_acento_conclusion.pack(side="left", fill="y")
            self._dict_acento_conclusion.pack_propagate(False)
            self.lbl_conclusion_ra = tk.Label(
                self._marco_conclusion,
                text="Dictamen: capture la lectura y pulse CALCULAR.",
                bg="#F8FAFC", fg="#334155",
                font=("Segoe UI", 10), justify="left",
                wraplength=800, anchor="w",
            )
            self.lbl_conclusion_ra.pack(
                side="left", fill="both", expand=True,
                padx=(12, 8), pady=10,
            )

        if numero == 2:
            contenedor.after(
                40, lambda f=frame: self._ajustar_ventana_ra(f),
            )

    def _nombre_prueba_ra(self):
        return "Resistencia de Aislamiento"

    def _holgura(self, valor):
        texto = str(valor).replace("{", " ").replace("}", " ").replace(",", " ")
        partes = []
        for pedazo in texto.split():
            try:
                partes.append(int(float(pedazo)))
            except ValueError:
                pass
        if not partes:
            return 0
        if len(partes) == 1:
            return partes[0] * 2
        return partes[0] + partes[1]

    def _eje(self, widget, modo, clave):
        try:
            info = widget.grid_info() if modo == "grid" else widget.pack_info()
        except tk.TclError:
            return 0
        return self._holgura(info.get(clave, 0))

    def _ancho_textos_ra(self):
        """Ancho que ocupan título, pestañas, fases y la fila de lectura."""
        try:
            f_titulo = tkfont.Font(family=RA_FONT, size=14, weight="bold")
            f_btn = tkfont.Font(family=RA_FONT, size=10, weight="bold")
            f_lec = tkfont.Font(family=RA_FONT, size=9)
            f_fase = tkfont.Font(family=RA_FONT, size=12)
        except tk.TclError:
            return 920
        titulo = f_titulo.measure("03. DIAGRAMAS DE BLOQUES") + 32
        pestanas = (
            f_btn.measure("MEDICIÓN") + f_btn.measure("CONEXIONES") + 140
        )
        lectura = (
            f_lec.measure("Lectura a 10 min (MΩ, GΩ o TΩ):")
            + 140 + 180 + 64
        )
        fases = (
            f_fase.measure("Sumergido en Aceite")
            + f_fase.measure("Seco (Sólido)")
            + 260
        )
        return max(titulo, pestanas, lectura, fases, 860)

    def _ajustar_ventana_ra(
        self, contenido, panel_diagrama=None, ancho_diag=0, alto_diag=0,
    ):
        ventana = contenido.winfo_toplevel()
        try:
            if not ventana.winfo_exists():
                return
        except tk.TclError:
            return
        if ancho_diag or alto_diag:
            previa = getattr(self, "_medida_diag_ra", (0, 0))
            ancho_diag = max(previa[0], int(ancho_diag or 0))
            alto_diag = max(previa[1], int(alto_diag or 0))
            self._medida_diag_ra = (ancho_diag, alto_diag)
        if getattr(ventana, "_sape_ajustando", False):
            ventana.after(
                250,
                lambda c=contenido, p=panel_diagrama, aw=ancho_diag, al=alto_diag:
                    self._ajustar_ventana_ra(c, p, aw, al),
            )
            return
        ventana.update_idletasks()

        ancho_interior = self._ancho_textos_ra()
        ancho_interior = max(ancho_interior, getattr(self, "_ancho_tabla_ra", 0))
        if ancho_diag:
            ancho_interior = max(ancho_interior, int(ancho_diag) + 220)
        for hijo in contenido.winfo_children():
            ancho_interior = max(
                ancho_interior,
                hijo.winfo_reqwidth() + self._eje(hijo, "grid", "padx") + 12,
            )

        # Título, pestañas y barra de cálculo, más el diagrama cuando existe.
        alto_interior = 210
        if alto_diag:
            alto_interior += int(alto_diag) + 24
        else:
            for hijo in contenido.winfo_children():
                alto_interior += max(hijo.winfo_reqheight(), 28)
                alto_interior += self._eje(hijo, "grid", "pady")
            alto_interior = max(
                alto_interior,
                getattr(self, "_alto_tabla_ra", 0) + 90,
            )

        # 320 del panel, 24+24 del área y 20+20 del paso.
        ancho = 320 + 48 + 40 + ancho_interior + 24
        alto = max(800, 48 + 36 + alto_interior + 24)
        pantalla_w = max(ventana.winfo_screenwidth() - 16, 800)
        pantalla_h = max(ventana.winfo_screenheight() - 72, 600)
        ancho = min(ancho, pantalla_w)
        alto = min(alto, pantalla_h)
        if (
            abs(ventana.winfo_width() - ancho) < 16
            and abs(ventana.winfo_height() - alto) < 16
        ):
            return
        ventana._sape_ajustando = True
        ventana.minsize(min(ancho, 960), min(alto, 640))
        ventana.geometry(f"{ancho}x{alto}")
        ventana.after(180, lambda: setattr(ventana, "_sape_ajustando", False))

    def _obtener_pruebas_equipo(self):
        equipo = self.datos_prueba["tipo_equipo"].get()
        if "TCs" in equipo:
            pruebas = PRUEBAS_TCS
        elif "TPC" in equipo:
            pruebas = PRUEBAS_TPCS
        elif "TPs" in equipo:
            pruebas = PRUEBAS_TPS
        elif "Autotransformadores" in equipo:
            if (
                self.datos_prueba["terciario_autotransformador"].get()
                == "Sin terciario"
            ):
                pruebas = [PRUEBA_AUTOTRANSFORMADOR_SIN_TERCIARIO]
            else:
                pruebas = PRUEBAS_AUTOTRANSFORMADOR
        elif "Apartarrayos" in equipo:
            if (
                self.datos_prueba["secciones_apartarrayos"].get()
                == "Una sección"
            ):
                pruebas = PRUEBAS_APARTARRAYOS_UNA_SECCION
            else:
                pruebas = PRUEBAS_APARTARRAYOS_VARIAS_SECCIONES
        elif "Generadores" in equipo:
            pruebas = PRUEBAS_MAQUINAS_ROTATIVAS
        elif "Transformadores de 3 Devanados" in equipo:
            pruebas = PRUEBAS_TRANSFORMADORES_3D
        elif "Transformadores de 2 Devanados" in equipo:
            pruebas = PRUEBAS_TRANSFORMADORES_2D
        elif "Reactores" in equipo:
            pruebas = PRUEBAS_REACTOR
        else:
            return []
        return [prueba.copy() for prueba in pruebas]

    def _crear_tabla_pruebas(self, parent, row):
        pruebas = self._obtener_pruebas_equipo()
        if not pruebas:
            self.prueba_seleccionada = None
            tk.Label(
                parent,
                text=(
                    "El procedimiento SOM-3531 no especifica una prueba "
                    "de resistencia de aislamiento para este equipo."
                ),
                bg=RA_VISTA_TARJETA, fg="#3F3A34",
                font=("Segoe UI", 14, "bold"),
                wraplength=620, justify="left",
            ).grid(row=row, column=0, columnspan=4, sticky="w", pady=12)
            return

        job_previo = getattr(self, "_parpadeo_selector", None)
        if job_previo is not None:
            try:
                self.after_cancel(job_previo)
            except tk.TclError:
                pass
            self._parpadeo_selector = None

        columnas = (
            ("selector", ""),
            ("prueba", "PRUEBA"),
            ("kv", "kV CC"),
            ("linea", "LÍNEA (+)"),
            ("tierra", "TIERRA (-)"),
            ("guarda", "GUARDA"),
            ("medicion", "MEDICIÓN"),
        )
        color_th = {
            "prueba": "#334155",
            "kv": "#334155",
            "linea": "#DC2626",
            "tierra": "#334155",
            "guarda": "#2563EB",
            "medicion": "#EA580C",
        }
        # Fondo pastel del color de la columna: (fondo, texto, borde).
        pildoras = {
            "linea": ("#FECACA", "#991B1B", "#FCA5A5"),
            "tierra": ("#E5E7EB", "#111111", "#D1D5DB"),
            "guarda": ("#DBEAFE", "#1E40AF", "#BFDBFE"),
            "medicion": ("#FFEDD5", "#C2410C", "#FED7AA"),
        }
        fuente_th = (
            ("Segoe UI Black", 9)
            if "Segoe UI Black" in tkfont.families()
            else ("Segoe UI", 9, "bold")
        )
        fuente_num = ("Consolas", 12, "bold")
        fuente_kv = ("Consolas", 11)
        fuente_badge = ("Segoe UI", 11, "bold")

        def formatear_voltaje_kv(valor):
            partes = valor.replace("/", "-").split("-")
            formateadas = []
            for parte in partes:
                try:
                    formateadas.append(f"{float(parte) / 1000:g}")
                except ValueError:
                    return valor
            separador = "/" if "/" in valor else "-"
            return separador.join(formateadas)

        def es_vacio(valor):
            return str(valor).strip() in ("", "-----", "---", "—", "-")

        panel = ctk.CTkFrame(
            parent, fg_color="#FFFFFF", corner_radius=10,
            border_width=1, border_color="#E2E8F0",
        )
        panel.grid(row=row, column=0, sticky="ew", pady=(4, 4))

        barra = tk.Canvas(
            panel, height=3, bg="#FFFFFF", highlightthickness=0, bd=0,
        )
        barra.pack(fill="x", padx=10, pady=(8, 0))

        def pintar_degradado(_evento=None):
            ancho = max(barra.winfo_width(), 4)
            barra.delete("all")
            paradas = (
                (0.0, (249, 115, 22)),
                (0.33, (250, 204, 21)),
                (0.66, (59, 130, 246)),
                (1.0, (249, 115, 22)),
            )
            for x in range(ancho):
                t = x / (ancho - 1)
                for i in range(len(paradas) - 1):
                    t0, c0 = paradas[i]
                    t1, c1 = paradas[i + 1]
                    if t <= t1 or i == len(paradas) - 2:
                        parte = 0 if t1 == t0 else (t - t0) / (t1 - t0)
                        parte = max(0.0, min(1.0, parte))
                        color = tuple(
                            int(c0[k] + (c1[k] - c0[k]) * parte) for k in range(3)
                        )
                        barra.create_line(
                            x, 0, x, 3, fill="#%02x%02x%02x" % color,
                        )
                        break

        barra.bind("<Configure>", pintar_degradado)

        tabla = tk.Frame(panel, bg="#FFFFFF")
        tabla.pack(fill="x")
        pesos = (0, 0, 1, 1, 2, 2, 2, 3)
        minimos = (4, 50, 88, 88, 110, 110, 100, 150)
        for indice, (peso, minimo) in enumerate(zip(pesos, minimos)):
            tabla.grid_columnconfigure(indice, weight=peso, minsize=minimo)

        selector = tk.IntVar(value=0)
        filas = []
        punto_visible = {"on": True}

        def dibujar_led(lienzo, encendido, fondo, punto=True):
            lienzo.configure(bg=fondo)
            lienzo.delete("all")
            if encendido:
                lienzo.create_oval(
                    2, 2, 22, 22, outline="#F97316", width=2, fill="#FFFFFF",
                )
                if punto:
                    lienzo.create_oval(7, 7, 17, 17, outline="", fill="#F97316")
            else:
                lienzo.create_oval(
                    2, 2, 22, 22, outline="#94A3B8", width=2, fill="#F8FAFC",
                )

        def pintar_fila(indice):
            fila = filas[indice]
            seleccionado = selector.get() == indice
            fondo = "#FFF7ED" if seleccionado else "#FFFFFF"
            fila["acento"].configure(bg="#F97316" if seleccionado else fondo)
            for marco in fila["marcos"]:
                marco.configure(bg=fondo)
            for etiqueta in fila["etiquetas"]:
                etiqueta.configure(bg=fondo)
            dibujar_led(
                fila["led"], seleccionado, fondo,
                punto_visible["on"] if seleccionado else True,
            )

        def parpadear_punto():
            self._parpadeo_selector = None
            indice = selector.get()
            if not 0 <= indice < len(filas):
                return
            led = filas[indice]["led"]
            try:
                if not led.winfo_exists():
                    return
                punto_visible["on"] = not punto_visible["on"]
                dibujar_led(led, True, "#FFF7ED", punto_visible["on"])
            except tk.TclError:
                return
            self._parpadeo_selector = self.after(420, parpadear_punto)

        def arrancar_parpadeo():
            job = getattr(self, "_parpadeo_selector", None)
            if job is not None:
                try:
                    self.after_cancel(job)
                except tk.TclError:
                    pass
                self._parpadeo_selector = None
            punto_visible["on"] = True
            self._parpadeo_selector = self.after(420, parpadear_punto)

        def seleccionar(indice):
            self.prueba_seleccionada = pruebas[indice]
            selector.set(indice)
            punto_visible["on"] = True
            for i in range(len(filas)):
                pintar_fila(i)
            arrancar_parpadeo()
            if getattr(self, "lbl_nombre_prueba_ra", None) is not None:
                try:
                    self.lbl_nombre_prueba_ra.config(
                        text=self._nombre_prueba_ra(),
                    )
                except tk.TclError:
                    pass
            voltaje = self.prueba_seleccionada["kv"]
            if voltaje.isdigit():
                self.datos_prueba["voltaje_prueba"].set(voltaje)
            else:
                self.datos_prueba["voltaje_prueba"].set("Según procedimiento")

        def celda(fila_grid, columna, alto, fondo, borde, grosor):
            marco = tk.Frame(tabla, bg=fondo, height=alto)
            marco.grid(row=fila_grid, column=columna, sticky="nsew")
            marco.pack_propagate(False)
            tk.Frame(marco, bg=borde, height=grosor).pack(side="bottom", fill="x")
            return marco

        celda(0, 0, 46, "#F1F5F9", "#CBD5E1", 2)
        for indice, (clave, titulo) in enumerate(columnas, start=1):
            marco = celda(0, indice, 46, "#F1F5F9", "#CBD5E1", 2)
            if titulo:
                tk.Label(
                    marco, text=titulo, bg="#F1F5F9", fg=color_th[clave],
                    font=fuente_th,
                ).pack(expand=True)

        for indice_fila, prueba in enumerate(pruebas):
            voltaje = formatear_voltaje_kv(prueba["kv"])
            valores = {
                "prueba": prueba["prueba"],
                "kv": voltaje,
                "linea": prueba["linea"],
                "tierra": prueba["tierra"],
                "guarda": prueba["guarda"],
                "medicion": prueba["medicion"],
            }
            elegir = lambda _evento=None, i=indice_fila: seleccionar(i)
            acento = celda(indice_fila + 1, 0, 48, "#FFFFFF", "#E2E8F0", 1)
            marcos = []
            etiquetas = []
            widgets = {acento, *acento.winfo_children()}
            led = None
            for indice, (clave, _titulo) in enumerate(columnas, start=1):
                marco = celda(
                    indice_fila + 1, indice, 48, "#FFFFFF", "#E2E8F0", 1,
                )
                marcos.append(marco)
                widgets.add(marco)
                widgets.update(marco.winfo_children())
                marco.bind("<Button-1>", elegir)
                if clave == "selector":
                    led = tk.Canvas(
                        marco, width=24, height=24, bg="#FFFFFF",
                        highlightthickness=0, bd=0, cursor="hand2",
                    )
                    led.place(relx=0.5, rely=0.5, anchor="center")
                    led.bind("<Button-1>", elegir)
                    widgets.add(led)
                    continue
                texto = str(valores[clave])
                vacio = es_vacio(texto)
                if clave in pildoras and not vacio:
                    color_f, tinta, borde_badge = pildoras[clave]
                    pastilla = tk.Label(
                        marco, text=texto, bg=color_f, fg=tinta,
                        font=fuente_badge,
                        padx=10, pady=4, cursor="hand2", anchor="center",
                        highlightthickness=1, highlightbackground=borde_badge,
                    )
                    pastilla.place(relx=0.5, rely=0.5, anchor="center")
                    pastilla.bind("<Button-1>", elegir)
                    widgets.add(pastilla)
                    continue
                if clave in pildoras:
                    etiqueta = tk.Label(
                        marco, text="—", bg="#FFFFFF", fg="#94A3B8",
                        font=("Segoe UI", 12, "bold"), cursor="hand2",
                    )
                elif clave == "prueba":
                    etiqueta = tk.Label(
                        marco, text=texto, bg="#FFFFFF", fg="#334155",
                        font=fuente_num, cursor="hand2",
                    )
                else:
                    etiqueta = tk.Label(
                        marco, text=texto, bg="#FFFFFF", fg="#475569",
                        font=fuente_kv, cursor="hand2",
                    )
                etiqueta.place(relx=0.5, rely=0.5, anchor="center")
                etiqueta.bind("<Button-1>", elegir)
                etiquetas.append(etiqueta)
                widgets.add(etiqueta)
            fila = {
                "acento": acento,
                "marcos": marcos,
                "etiquetas": etiquetas,
                "led": led,
                "widgets": widgets,
            }
            filas.append(fila)

            def al_entrar(_evento=None, i=indice_fila):
                if selector.get() != i:
                    filas[i]["acento"].configure(bg="#F8FAFC")
                    for marco in filas[i]["marcos"]:
                        marco.configure(bg="#F8FAFC")
                    for etiqueta in filas[i]["etiquetas"]:
                        etiqueta.configure(bg="#F8FAFC")
                    dibujar_led(filas[i]["led"], False, "#F8FAFC")

            def al_salir(evento, i=indice_fila):
                destino = panel.winfo_containing(evento.x_root, evento.y_root)
                actual = destino
                while actual is not None:
                    if actual in filas[i]["widgets"]:
                        return
                    actual = getattr(actual, "master", None)
                pintar_fila(i)

            for widget in widgets:
                widget.bind("<Enter>", al_entrar)
                widget.bind("<Leave>", al_salir)

        seleccionar(0)

        es_rotativa = "Generadores" in self.datos_prueba["tipo_equipo"].get()
        nota = (
            "Esquema genérico orientativo para máquinas rotativas; "
            "confirme la conexión y tensión con el fabricante."
            if es_rotativa else
            "Elija una prueba para actualizar ambos diagramas. "
            "Las conexiones se muestran según el equipo y el procedimiento "
            "seleccionado."
        )
        tk.Frame(panel, bg="#E2E8F0", height=1).pack(fill="x")
        pie = tk.Frame(panel, bg="#FAFBFC")
        pie.pack(fill="x")
        etiqueta_nota = tk.Label(
            pie, text=nota, bg="#FAFBFC", fg="#64748B",
            font=("Segoe UI", 9, "italic"),
            wraplength=860, justify="left", anchor="w",
        )
        etiqueta_nota.pack(fill="x", padx=24, pady=16)

        def ajustar_nota(_evento=None):
            ancho = panel.winfo_width() - 64
            if ancho > 240:
                etiqueta_nota.configure(wraplength=ancho)

        panel.bind("<Configure>", ajustar_nota, add="+")
        panel.update_idletasks()
        etiqueta_nota.update_idletasks()
        self._ancho_tabla_ra = max(860, panel.winfo_reqwidth())
        self._alto_tabla_ra = panel.winfo_reqheight() + 20


    def _texto_bloques_ra(self, modo):
        prueba = self.prueba_seleccionada
        if prueba is None:
            return "No hay prueba especificada."
        import sys
        ruta = r"c:\Users\LapOne MX\Documents\Programacion Modo JEDI\S. A. P. E"
        if ruta not in sys.path:
            sys.path.insert(0, ruta)
        import SAPE_1 as sape1
        equipo = self.datos_prueba["tipo_equipo"].get()
        if "TCs" in equipo:
            tipo = 5
        elif "TPC" in equipo:
            tipo = 7
        elif "TPs" in equipo:
            tipo = 6
        elif "Autotransformadores" in equipo:
            tipo = 3
        elif "Reactores" in equipo:
            tipo = 4
        elif "3 Devanados" in equipo:
            tipo = 2
        elif "Generadores" in equipo:
            tipo = 8
        elif "Apartarrayos" in equipo:
            tipo = 9
        else:
            tipo = 1
        cfg = {
            "tipo_equipo": tipo,
            "fase_linea": prueba["linea"],
            "linea": prueba["linea"],
            "tierra": prueba["tierra"],
            "guarda": prueba["guarda"],
            "medicion_ra": prueba["medicion"],
            "varias_secciones": (
                self.datos_prueba["secciones_apartarrayos"].get()
                == "Varias secciones"
            ),
        }
        desc = (
            f"Prueba: {prueba['prueba']}  "
            f"L={prueba['linea']} T={prueba['tierra']} G={prueba['guarda']}"
        )
        sin_terciario = tipo == 3 and (
            self.datos_prueba["terciario_autotransformador"].get()
            == "Sin terciario"
        )
        # Dibujos propios de SAPE2, apegados a las figuras de ST-CT-001. Se
        # arman en texto plano y se colorean igual que los de SAPE_1.
        planas = None
        if tipo == 8:
            planas = _lineas_generador_ra(prueba, modo)
        elif tipo == 5:
            planas = _lineas_tc_ra(prueba, modo)
        elif sin_terciario:
            planas = _quitar_terciario_ra(
                sape1._ra_render_diagrama_bloques(
                    cfg, prueba["medicion"], descripcion=desc, modo=modo,
                )
            )
        if planas is not None:
            lineas = sape1._colorizar_cajas_roles_ra(
                [
                    sape1._ra_colorizar_linea_diagrama(linea, modo=modo)
                    for linea in planas
                ],
                modo=modo,
            )
        else:
            lineas = sape1._ra_contenido_diagrama_bloques(
                cfg, prueba["medicion"], desc, modo,
            )
        return "\n".join(lineas)


    def calcular_resultado(self):
        resultado = self._resultado_dictamen_ra()
        if resultado is None:
            return
        if hasattr(self, "lbl_equipo_ra"):
            lineas = resultado["lineas"]
            en_aceite = "Aceite" in resultado["aislamiento"]
            liquido = self.datos_prueba["liquido"].get().strip()
            self.lbl_equipo_ra.config(text=f"{resultado['equipo']}.")
            self.lbl_aislamiento_ra.config(
                text=(
                    f"Aislamiento sumergido en aceite ({liquido or 'Aceite mineral'})."
                    if en_aceite else "Aislamiento seco."
                )
            )
            ambiente = resultado["ambiente"]
            humedad = resultado["hr"]
            self.lbl_amb_ra.config(
                text=(
                    "•  Ambiente: "
                    + (f"{ambiente:g} °C" if ambiente is not None
                       else "sin registrar")
                    + "  |  Humedad relativa: "
                    + (f"{humedad:g} %" if humedad is not None
                       else "sin registrar")
                )
            )
            self.lbl_dev_ra.config(
                text=f"•  Devanado: {resultado['temp']:g} °C"
            )
            self.lbl_kt_ra.config(
                text=(
                    f"•  Kt = {resultado['kt']:.3f} "
                    + (
                        "(IEEE 43, base 40 °C)"
                        if self._base_temp_ra() == 40.0 else
                        f"({'aceite' if en_aceite else 'seco'}, Tabla 1)"
                    )
                )
            )
            resistencias, calculos, conclusion = [], [], []
            for linea in lineas[2:]:
                if linea.startswith(("R a 1 min", "R 1 min", "R 10 min")):
                    resistencias.append(linea)
                elif linea.startswith(("ip =", "ia =", "Tabla 5")):
                    calculos.append(linea)
                else:
                    conclusion.append(linea)
            self.lbl_resistencias_ra.config(
                text="\n".join(resistencias) or "——"
            )
            self.lbl_calculos_ra.config(text="\n".join(calculos) or "——")
            self.lbl_conclusion_ra.config(
                text="Dictamen: " + " ".join(conclusion)
            )
        if hasattr(self, "lbl_ia_valor"):
            datos = self.datos_prueba
            r30 = self._lectura_mohm_ra(datos["lectura_30s"].get())
            r1 = self._lectura_mohm_ra(datos["lectura_1min"].get())
            r10 = self._lectura_mohm_ra(datos["lectura_10min"].get())
            self.lbl_ia_valor.config(
                text=f"{r1 / r30:.2f}" if r30 and r1 else "No aplica"
            )
            self.lbl_ip_valor.config(
                text=f"{r10 / r1:.2f}" if r1 and r10 else "No aplica"
            )
        estilos_estado = {
            "ACEPTADO": ("#D1FAE5", "#10B981", "#065F46", "✅", "#F0FDF4"),
            "INVESTIGAR": ("#FEF3C7", "#F59E0B", "#92400E", "!", "#FFFBEB"),
            "RECHAZADO": ("#FEE2E2", "#EF4444", "#991B1B", "❌", "#FEF2F2"),
        }
        estilo = estilos_estado.get(resultado["estado"])
        encabezado = getattr(self, "_dict_encabezado", None)
        if estilo and encabezado is not None:
            fondo, acento, tinta, icono, suave = estilo
            try:
                encabezado.config(bg=acento)
                self._dict_acento.config(bg=tinta)
                self._dict_icono.config(bg=acento, fg="#FFFFFF", text=icono)
                self._dict_estado.config(
                    bg=acento, fg="#FFFFFF", text=resultado["estado"],
                )
                self._dict_acento_conclusion.config(bg=acento)
                self._marco_conclusion.config(bg=suave)
                self.lbl_conclusion_ra.config(bg=suave, fg=tinta)
            except tk.TclError:
                pass
        banderas = {
            "ACEPTADO": "normal",
            "INVESTIGAR": "precaucion",
            "RECHAZADO": "alerta",
        }
        nivel_foco = banderas.get(resultado["estado"])
        if nivel_foco:
            detalle = "\n".join(resultado["lineas"][2:]) or resultado["estado"]
            self._publicar_foco_ieee(
                nivel_foco, detalle, self._rotulo_estado(resultado["estado"]),
            )
    def _partir_lectura_ra(self, texto):
        """Sin letra: megaohms. Solo vale G/g o T/t al final del número."""
        bruto = (texto or "").strip().replace(",", "")
        if not bruto:
            return None
        unidad = "M"
        if bruto[-1] in "GgTt":
            unidad = bruto[-1].upper()
            bruto = bruto[:-1].strip()
            if not bruto:
                return None
        try:
            valor = float(bruto)
        except ValueError:
            return None
        if not math.isfinite(valor) or valor < 0:
            return None
        return valor, unidad

    def _unidad_lectura_ra(self, texto):
        partes = self._partir_lectura_ra(texto)
        if partes is None:
            return "M"
        return partes[1]

    def _lectura_mohm_ra(self, texto):
        partes = self._partir_lectura_ra(texto)
        if partes is None:
            return None
        valor, unidad = partes
        escala = {"M": 1.0, "G": 1000.0, "T": 1_000_000.0}[unidad]
        return valor * escala

    def _kt_tabla1_ra(self, temp_c, en_aceite):
        """Tabla 1 ST-CT-001. Rc = Rt × Kt, base 20 °C."""
        tabla = (
            (
                (0, 0.25), (5, 0.36), (10, 0.50), (15.6, 0.74), (20, 1.00),
                (25, 1.40), (30, 1.98), (35, 2.80), (40, 3.95), (45, 5.60),
                (50, 7.85), (55, 11.20), (60, 15.85), (65, 22.40),
                (70, 31.75), (75, 44.70),
            )
            if en_aceite else
            (
                (0, 0.40), (5, 0.45), (10, 0.50), (15.6, 0.75), (20, 1.00),
                (25, 1.30), (30, 1.60), (35, 2.05), (40, 2.50), (45, 3.25),
                (50, 4.00), (55, 5.20), (60, 5.40), (65, 8.70),
                (70, 10.00), (75, 13.00),
            )
        )
        if temp_c <= tabla[0][0]:
            return tabla[0][1]
        if temp_c >= tabla[-1][0]:
            return tabla[-1][1]
        for (t0, k0), (t1, k1) in zip(tabla, tabla[1:]):
            if t0 <= temp_c <= t1:
                return k0 + (k1 - k0) * (temp_c - t0) / (t1 - t0)
        return 1.0

    def _solo_aislamiento_solido(self, equipo=None):
        """Apartarrayos y máquinas rotatorias no llevan aceite: siempre son secos."""
        if equipo is None:
            equipo = self.datos_prueba["tipo_equipo"].get()
        return self._familia_ra(equipo) in ("apartarrayos", "rotativa")

    def _en_aceite_ra(self, equipo=None):
        if self._solo_aislamiento_solido(equipo):
            return False
        return "Aceite" in self.datos_prueba["aislamiento"].get()

    def _base_temp_ra(self, equipo=None):
        """Temperatura base de corrección: 40 °C en máquinas rotatorias, 20 °C en el resto."""
        if equipo is None:
            equipo = self.datos_prueba["tipo_equipo"].get()
        return 40.0 if self._familia_ra(equipo) == "rotativa" else 20.0

    def _kt_equipo_ra(self, temp_c, en_aceite, equipo=None):
        """Kt del equipo. Rotatorias: IEEE 43 a 40 °C (ST-CT-001, 3.5.4 y 4.2.5)."""
        if self._base_temp_ra(equipo) == 40.0:
            return 0.5 ** ((40.0 - temp_c) / 10.0)
        return self._kt_tabla1_ra(temp_c, en_aceite)

    def _numero_ra(self, texto):
        bruto = (texto or "").strip().replace("%", "").replace(",", ".")
        if not bruto:
            return None
        try:
            valor = float(bruto)
        except ValueError:
            return None
        if not math.isfinite(valor):
            return None
        return valor

    def _aviso_referencia_20(self, texto):
        """Aviso cuando la temperatura se aleja de la referencia de 20 °C."""
        valor = self._numero_ra(texto)
        if valor is None:
            return "", "#64748B"
        delta = abs(valor - 20.0)
        if delta <= 5:
            return "Cerca de la referencia de 20 °C", "#059669"
        if delta <= 15:
            return "Alejada de 20 °C. Se aplicará Kt.", "#B45309"
        return "Muy alejada de 20 °C. Kt obligatorio.", "#B91C1C"

    def _familia_ra(self, equipo):
        if "TCs" in equipo:
            return "tc"
        if "TPC" in equipo or "TPs" in equipo:
            return "tp"
        if "Apartarrayos" in equipo:
            return "apartarrayos"
        if "Generadores" in equipo:
            return "rotativa"
        return "potencia"

    def _resultado_dictamen_ra(self):
        """Corrección a 20 °C y dictamen ACEPTADO, INVESTIGAR o RECHAZADO."""
        datos = self.datos_prueba
        padre = self.winfo_toplevel()
        equipo = datos["tipo_equipo"].get()
        prueba = self.prueba_seleccionada or {}
        temp = self._numero_ra(datos["temp_devanado"].get())
        if temp is None:
            messagebox.showerror(
                "Falta la temperatura",
                "Escriba la temperatura del devanado en Datos del equipo. "
                "Sin ella no se puede corregir la resistencia a la temperatura base (Rc = Rt × Kt).",
                parent=padre,
            )
            return None
        base = self._base_temp_ra(equipo)
        # Apartarrayos y máquinas rotatorias son de aislamiento sólido.
        en_aceite = self._en_aceite_ra(equipo)
        liquido = datos["liquido"].get().strip()
        kt = self._kt_equipo_ra(temp, en_aceite, equipo)
        r30 = self._lectura_mohm_ra(datos["lectura_30s"].get())
        r1 = self._lectura_mohm_ra(datos["lectura_1min"].get())
        r10 = self._lectura_mohm_ra(datos["lectura_10min"].get())
        u1 = self._unidad_lectura_ra(datos["lectura_1min"].get())
        u10 = self._unidad_lectura_ra(datos["lectura_10min"].get())
        familia = self._familia_ra(equipo)
        minutos = prueba.get("minutos", 1)
        if minutos == 10 and (r1 is None or r10 is None):
            messagebox.showerror(
                "Faltan lecturas",
                "Para el índice de polarización hacen falta la lectura de 1 min y la de 10 min.",
                parent=padre,
            )
            return None
        if minutos != 10 and r1 is None:
            messagebox.showerror(
                "Falta la lectura",
                "Escriba la lectura a 1 min. Sin letra son megaohms. "
                "G o g al final son gigaohms. T o t al final son teraohms.",
                parent=padre,
            )
            return None
        hr = self._numero_ra(datos["humedad_relativa"].get())
        ambiente = self._numero_ra(datos["temp_ambiente"].get())
        aislamiento = (
            f"sumergido en aceite ({liquido or 'Aceite mineral'})"
            if en_aceite else "seco"
        )
        descripcion = [
            f"{equipo}. Aislamiento {aislamiento}.",
            (
                f"Ambiente {ambiente:g} °C. " if ambiente is not None else "Ambiente sin registrar. "
            )
            + (
                f"Humedad relativa {hr:g} %. " if hr is not None else "Humedad relativa sin registrar. "
            )
            + f"Devanado {temp:g} °C. Kt = {kt:.3f} ("
            + (
                "IEEE 43, base 40 °C" if base == 40.0
                else f"{'aceite' if en_aceite else 'seco'}, Tabla 1"
            )
            + ").",
        ]
        if abs(temp - base) > 5:
            descripcion.append(
                f"La temperatura del devanado se aleja de la referencia de {base:g} °C. "
                "La resistencia se corrige con Kt antes del dictamen."
            )
        if minutos == 10 and r30 is not None and r1 is not None and r1 < r30 * 0.99:
            estado = "RECHAZADO"
            descripcion.append(
                "La resistencia baja de 30 s a 1 min. El procedimiento exige que la curva no descienda."
            )
        elif minutos == 10 and r1 is not None and r10 is not None and r10 < r1 * 0.99:
            estado = "RECHAZADO"
            descripcion.append(
                "La resistencia baja de 1 min a 10 min. El procedimiento exige que la curva no descienda."
            )
        elif familia in ("tc", "tp"):
            minimo = 45000 if familia == "tc" else 40000
            nombre = "TC" if familia == "tc" else "TP / TPC"
            rc = r1 * kt
            descripcion.append(
                f"R a 1 min medida {self._fmt_mohm_ra(r1, u1)}. "
                f"Corregida a 20 °C: {self._fmt_mohm_ra(rc, u1)}."
            )
            descripcion.append(
                f"Tabla 5 ST-CT-001, {nombre}: mínimo {minimo:,} MΩ a 1 min y 20 °C.".replace(",", " ")
            )
            if rc >= minimo:
                estado = "ACEPTADO"
                descripcion.append("La resistencia corregida cumple el mínimo. Aislamiento aceptado.")
            else:
                estado = "RECHAZADO"
                descripcion.append("La resistencia corregida queda debajo del mínimo. Aislamiento rechazado.")
        elif minutos == 10 and r1 and r10:
            ip = r10 / r1
            rc1 = r1 * kt
            rc10 = r10 * kt
            descripcion.append(
                f"R 1 min {self._fmt_mohm_ra(r1, u1)} → {self._fmt_mohm_ra(rc1, u1)} a {base:g} °C. "
                f"R 10 min {self._fmt_mohm_ra(r10, u10)} → {self._fmt_mohm_ra(rc10, u10)} a {base:g} °C."
            )
            descripcion.append(f"ip = R10 / R1 = {ip:.2f}. El procedimiento acepta ip ≥ 1.5.")
            if r30 and r30 > 0:
                ia = r1 / r30
                descripcion.append(f"ia = R1 / R30 = {ia:.2f}. La banda es 1.45 ± 25 %.")
                if en_aceite:
                    descripcion.append("En aceite el ia no decide el dictamen.")
            else:
                ia = None
            if ip >= 2.0:
                estado = "ACEPTADO"
                descripcion.append("El índice de polarización está en buen estado.")
            elif ip >= 1.5:
                estado = "INVESTIGAR"
                descripcion.append(
                    "Cumple el mínimo de 1.5, pero queda debajo de 2.0: banda de monitoreo."
                )
            else:
                estado = "RECHAZADO"
                descripcion.append("El índice de polarización queda debajo de 1.5.")
            if (
                estado == "ACEPTADO" and not en_aceite and ia is not None
                and not (1.45 * 0.75 <= ia <= 1.45 * 1.25)
            ):
                estado = "INVESTIGAR"
                descripcion.append("El ia del aislamiento sólido quedó fuera de la banda.")
        else:
            rc = r1 * kt
            descripcion.append(
                f"R a 1 min medida {self._fmt_mohm_ra(r1, u1)}. "
                f"Corregida a {base:g} °C: {self._fmt_mohm_ra(rc, u1)}."
            )
            descripcion.append(
                "Este equipo no tiene mínimo de Tabla 5. La lectura corregida queda para compararla con el fabricante y con pruebas anteriores."
            )
            estado = "INVESTIGAR"
        if hr is not None and hr >= 75 and estado == "ACEPTADO":
            estado = "INVESTIGAR"
            descripcion.append(
                "La humedad relativa es de 75 % o mayor. El procedimiento pide hacer la prueba por debajo de ese valor."
            )
        colores = {
            "ACEPTADO": "#007A33",
            "INVESTIGAR": "#F5C400",
            "RECHAZADO": "#C62828",
        }
        tinta = "#1A1A1A" if estado == "INVESTIGAR" else "#FFFFFF"
        return {
            "estado": estado,
            "color": colores[estado],
            "tinta": tinta,
            "descripcion": " ".join(descripcion),
            "lineas": descripcion,
            "equipo": equipo,
            "aislamiento": (
                datos["aislamiento"].get() if en_aceite else "Seco"
            ),
            "prueba": prueba,
            "ambiente": ambiente,
            "hr": hr,
            "temp": temp,
            "kt": kt,
        }

    def _fmt_mohm_ra(self, valor, unidad="M"):
        if valor is None:
            return "sin lectura"
        unidad = unidad if unidad in ("M", "G", "T") else "M"
        escala = {"M": 1.0, "G": 1000.0, "T": 1_000_000.0}[unidad]
        simbolo = {"M": "MΩ", "G": "GΩ", "T": "TΩ"}[unidad]
        return f"{valor / escala:g} {simbolo}"


    def mostrar_anexo_a_formatos(self, padre):
        visor = tk.Toplevel(padre)
        visor.title("ANEXO A  Formatos de Prueba")
        visor.configure(bg="#F4F6F8")
        visor.geometry("1060x780")
        visor.minsize(920, 640)
        visor.transient(padre)

        barra_sup = tk.Frame(visor, bg="#1E293B")
        barra_sup.pack(fill="x")
        tk.Label(
            barra_sup, text="Formatos de Prueba - Anexo A",
            bg="#1E293B", fg="#FFFFFF", font=("Segoe UI", 15, "bold"),
        ).pack(side="left", padx=20, pady=14)

        contenido = ctk.CTkScrollableFrame(visor, fg_color="#FFFFFF")
        contenido.pack(fill="both", expand=True, padx=18, pady=18)
        kt_var = tk.StringVar(visor, value="Calculado...")
        scratch = {}

        def var_scratch(clave):
            if clave not in scratch:
                scratch[clave] = tk.StringVar(visor)
            return scratch[clave]

        def actualizar_kt(_evento=None):
            temp = self._numero_ra(self.datos_prueba["temp_devanado"].get())
            if temp is None:
                kt_var.set("Calculado...")
                return None
            en_aceite = self._en_aceite_ra()
            kt = self._kt_equipo_ra(temp, en_aceite)
            kt_var.set(f"{kt:.3f}")
            return kt

        def formato_kv(valor):
            partes = str(valor).replace("/", "-").split("-")
            nums = []
            for parte in partes:
                try:
                    nums.append(f"{float(parte) / 1000:g}")
                except ValueError:
                    return str(valor)
            return " - ".join(nums) + " kV"

        def grupo(padre_g, texto, variable, fila, columna, fondo="#FFFFFF"):
            marco = tk.Frame(padre_g, bg=fondo)
            marco.grid(row=fila, column=columna, sticky="ew", padx=8, pady=5)
            tk.Label(
                marco, text=texto, bg=fondo, fg="#64748B",
                font=("Segoe UI", 9, "bold"), anchor="w",
            ).pack(fill="x", pady=(0, 4))
            entrada = ctk.CTkEntry(marco, textvariable=variable, height=30)
            entrada.pack(fill="x")
            return entrada

        def rejilla(padre_g, columnas_n, fondo="#FFFFFF"):
            marco = tk.Frame(padre_g, bg=fondo)
            marco.pack(fill="x", pady=(4, 12))
            for c in range(columnas_n):
                marco.grid_columnconfigure(c, weight=1)
            return marco

        def cabecera_tabla(tabla, columnas):
            for c, (_t, peso) in enumerate(columnas):
                tabla.grid_columnconfigure(c, weight=peso)
            for c, (titulo_c, _peso) in enumerate(columnas):
                tk.Label(
                    tabla, text=titulo_c.upper(), bg="#F1F5F9",
                    fg="#475569", font=("Segoe UI", 8, "bold"),
                    anchor="w", padx=8, pady=8,
                ).grid(row=0, column=c, sticky="ew", padx=(0, 1), pady=(0, 1))

        def dictamen_actual():
            temp = self._numero_ra(self.datos_prueba["temp_devanado"].get())
            prueba_sel = self.prueba_seleccionada or {}
            r1 = self._lectura_mohm_ra(self.datos_prueba["lectura_1min"].get())
            r10 = self._lectura_mohm_ra(
                self.datos_prueba["lectura_10min"].get()
            )
            if (
                temp is None or r1 is None
                or (prueba_sel.get("minutos", 1) == 10 and r10 is None)
            ):
                return None
            return self._resultado_dictamen_ra()

        def caja_resultado(padre_c, texto_izquierdo):
            caja = tk.Frame(padre_c, bg="#F1F5F9")
            caja.pack(fill="x", pady=(14, 6))
            tk.Label(
                caja, text=texto_izquierdo, bg="#F1F5F9", fg="#475569",
                font=("Segoe UI", 9, "bold"), anchor="w", justify="left",
                wraplength=430,
            ).pack(side="left", padx=14, pady=12)
            resultado = dictamen_actual()
            if resultado is None:
                fondo_b, acento_b, tinta_b = "#F1F5F9", "#94A3B8", "#334155"
                icono_b, estado_txt = "•", "DICTAMEN: —"
                sub_txt = "Capture las lecturas en el paso 4."
            else:
                fondo_b, acento_b, tinta_b, icono_b = {
                    "ACEPTADO": ("#D1FAE5", "#10B981", "#065F46", "✅"),
                    "INVESTIGAR": ("#FEF3C7", "#F59E0B", "#92400E", "!"),
                    "RECHAZADO": ("#FEE2E2", "#EF4444", "#991B1B", "❌"),
                }[resultado["estado"]]
                estado_txt = f"DICTAMEN: {resultado['estado']}"
                sub_txt = {
                    "ACEPTADO": "La lectura corregida supera el mínimo.",
                    "INVESTIGAR": "Se requiere revisión y monitoreo.",
                    "RECHAZADO": "La lectura corregida no cumple el mínimo.",
                }[resultado["estado"]]
            banner = tk.Frame(caja, bg=fondo_b)
            banner.pack(side="right", padx=10, pady=8)
            acento = tk.Frame(banner, bg=acento_b, width=6)
            acento.pack(side="left", fill="y")
            acento.pack_propagate(False)
            tk.Label(
                banner, text=icono_b, bg=fondo_b, fg=acento_b,
                font=("Segoe UI", 16, "bold"),
            ).pack(side="left", padx=(10, 6))
            textos_b = tk.Frame(banner, bg=fondo_b)
            textos_b.pack(side="left", padx=(0, 12), pady=6)
            tk.Label(
                textos_b, text=estado_txt, bg=fondo_b, fg=tinta_b,
                font=("Segoe UI", 11, "bold"), anchor="w",
            ).pack(fill="x")
            tk.Label(
                textos_b, text=sub_txt, bg=fondo_b, fg=tinta_b,
                font=("Segoe UI", 8), anchor="w",
            ).pack(fill="x")

        def titulo_formato(texto):
            marco_logo = tk.Frame(contenido, bg="#FFFFFF", height=100)
            marco_logo.pack(fill="x", padx=15, pady=(14, 2))
            marco_logo.pack_propagate(False)
            # Verde oficial CFE: Pantone 136-16 C (#008E60)
            tk.Label(
                marco_logo, text=CFE_ASCII, bg="#FFFFFF", fg="#00573F",
                font=("Consolas", 10, "bold"), anchor="nw",
                justify="left",
            ).place(x=2, y=2)
            tk.Label(
                marco_logo, text=CFE_ASCII, bg="#FFFFFF",
                fg="#008E60", font=("Consolas", 10, "bold"),
                anchor="nw", justify="left",
            ).place(x=0, y=0)
            foto_sape = _imagen_sape_ascii(
                tam=9, fondo="#FFFFFF", color="#1E293B",
            )
            etiqueta_sape = ctk.CTkLabel(
                marco_logo, text="", image=foto_sape, fg_color="#FFFFFF",
            )
            etiqueta_sape._foto_sape = foto_sape
            etiqueta_sape.place(relx=1.0, x=-2, y=0, anchor="ne")
            fila_titulo_ra = tk.Frame(contenido, bg="#FFFFFF")
            fila_titulo_ra.pack(fill="x", padx=15, pady=(2, 10))
            tk.Label(
                fila_titulo_ra, text="ST-CT-001", bg="#FFEDD5",
                fg=RA_VISTA_NARANJA_OSCURO, font=("Consolas", 12, "bold"),
                padx=10, pady=3,
            ).pack(side="left")
            tk.Label(
                fila_titulo_ra, text=texto, bg="#FFFFFF", fg="#1E293B",
                font=("Segoe UI", 14, "bold"), anchor="w",
            ).pack(side="left", padx=(12, 0))

        def subtitulo_seccion(texto):
            tk.Label(
                contenido, text=texto, bg="#FFFFFF", fg="#1E293B",
                font=("Segoe UI", 10, "bold"), anchor="w",
            ).pack(fill="x", padx=15, pady=(12, 2))

        def seccion_identificacion():
            # Datos de placa del formato ST-CT-001 (_ETIQUETAS_ID_RA)
            subtitulo_seccion("DATOS DE IDENTIFICACIÓN")
            rej_id = rejilla(contenido, 4)
            grupo(rej_id, "Gerencia Regional de Transmisión", var_scratch("gerencia"), 0, 0)
            grupo(rej_id, "Zona", var_scratch("subarea"), 0, 1)
            grupo(rej_id, "Nomenclatura", var_scratch("nomenclatura"), 0, 2)
            grupo(rej_id, "Subestación (S.E.)", var_scratch("subestacion"), 0, 3)
            grupo(rej_id, "Marca", var_scratch("marca"), 1, 0)
            grupo(rej_id, "Modelo", var_scratch("modelo"), 1, 1)
            grupo(rej_id, "No. de Serie", var_scratch("serie"), 1, 2)
            grupo(rej_id, "MVA", var_scratch("mva"), 1, 3)
            grupo(rej_id, "Año de Fabricación", var_scratch("fabricacion"), 2, 0)
            grupo(rej_id, "Nivel de Tensión (kV)", var_scratch("nivel"), 2, 1)

        def seccion_condiciones(incluir_devanado=True, incluir_kt=False):
            # Condiciones de prueba del formato ST-CT-001 (_ETIQUETAS_COND_RA)
            subtitulo_seccion("CONDICIONES DE LA PRUEBA")
            campos_cond = [
                ("Voltaje de prueba CD (kV)", var_scratch("voltaje_cd")),
                ("Temp. Aceite (°C)", var_scratch("aceite")),
                ("Temp. Ambiente (°C)", self.datos_prueba["temp_ambiente"]),
                ("Humedad Relativa (% HR)", self.datos_prueba["humedad_relativa"]),
            ]
            if self._solo_aislamiento_solido():
                # Equipo de aislamiento sólido: no hay aceite que medir.
                del campos_cond[1]
            if incluir_devanado:
                campos_cond.append(
                    ("Temp. Devanado (°C)", self.datos_prueba["temp_devanado"])
                )
            rej_cond = rejilla(contenido, 3)
            entrada_dev = None
            for indice_c, (etiqueta_c, variable_c) in enumerate(campos_cond):
                entrada_c = grupo(
                    rej_cond, etiqueta_c, variable_c,
                    indice_c // 3, indice_c % 3,
                )
                if etiqueta_c.startswith("Temp. Devanado"):
                    entrada_dev = entrada_c
            if incluir_kt:
                pos_kt = len(campos_cond)
                grupo_kt = tk.Frame(rej_cond, bg="#FFFFFF")
                grupo_kt.grid(
                    row=pos_kt // 3, column=pos_kt % 3,
                    sticky="ew", padx=8, pady=5,
                )
                tk.Label(
                    grupo_kt, text="Factor Kt a 20°C", bg="#FFFFFF",
                    fg="#64748B", font=("Segoe UI", 9, "bold"), anchor="w",
                ).pack(fill="x", pady=(0, 4))
                ctk.CTkEntry(
                    grupo_kt, textvariable=kt_var, height=30,
                    state="readonly", fg_color="#F8FAFC",
                    text_color="#94A3B8",
                ).pack(fill="x")
            if entrada_dev is not None:
                entrada_dev.bind("<FocusOut>", actualizar_kt, add="+")
                entrada_dev.bind("<Return>", actualizar_kt, add="+")
                actualizar_kt()
            pos_clima = len(campos_cond) + (1 if incluir_kt else 0)
            grupo_clima = tk.Frame(rej_cond, bg="#FFFFFF")
            grupo_clima.grid(
                row=pos_clima // 3, column=pos_clima % 3,
                sticky="ew", padx=8, pady=5,
            )
            tk.Label(
                grupo_clima, text="Clima", bg="#FFFFFF", fg="#64748B",
                font=("Segoe UI", 9, "bold"), anchor="w",
            ).pack(fill="x", pady=(0, 4))
            ctk.CTkComboBox(
                grupo_clima, variable=var_scratch("clima"),
                values=("Soleado", "Nublado", "Brisa", "1/2 nublado", "Lluvia"),
                state="readonly", height=30,
            ).pack(fill="x")

        def seccion_datos_tc():
            subtitulo_seccion("DATOS DEL TC")
            rej_tc = rejilla(contenido, 4)
            grupo(rej_tc, "Relación de transformación", var_scratch("relacion"), 0, 0)
            grupo(rej_tc, "Corriente primaria (A)", var_scratch("i_primaria"), 0, 1)
            grupo(rej_tc, "Corriente secundaria (A)", var_scratch("i_secundaria"), 0, 2)
            grupo(rej_tc, "Clase de exactitud", var_scratch("exactitud"), 0, 3)
            grupo(rej_tc, "Carga / Burden (VA)", var_scratch("burden"), 1, 0)
            grupo(rej_tc, "NBAI (kV)", var_scratch("nbai"), 1, 1)
            grupo(rej_tc, "Frecuencia (Hz)", var_scratch("frecuencia"), 1, 2)

        def seccion_datos_tp():
            subtitulo_seccion("DATOS DEL TP / TPC")
            rej_tp = rejilla(contenido, 4)
            grupo(rej_tp, "Relación de transformación", var_scratch("relacion"), 0, 0)
            grupo(rej_tp, "Tensión primaria (kV)", var_scratch("v_primaria"), 0, 1)
            grupo(rej_tp, "Tensión secundaria (V)", var_scratch("v_secundaria"), 0, 2)
            grupo(rej_tp, "Clase de exactitud", var_scratch("exactitud"), 0, 3)
            grupo(rej_tp, "Carga / Burden (VA)", var_scratch("burden"), 1, 0)
            grupo(rej_tp, "NBAI (kV)", var_scratch("nbai"), 1, 1)
            grupo(rej_tp, "Frecuencia (Hz)", var_scratch("frecuencia"), 1, 2)

        def seccion_datos_maquina():
            subtitulo_seccion("DATOS DE LA MÁQUINA ROTATORIA")
            rej_mq = rejilla(contenido, 4)
            grupo(rej_mq, "Tensión nominal (kV)", var_scratch("v_nominal"), 0, 0)
            grupo(rej_mq, "Corriente nominal (A)", var_scratch("i_nominal"), 0, 1)
            grupo(rej_mq, "Velocidad (RPM)", var_scratch("rpm"), 0, 2)
            grupo(rej_mq, "Factor de potencia", var_scratch("fp_nominal"), 0, 3)
            grupo(rej_mq, "Frecuencia (Hz)", var_scratch("frecuencia"), 1, 0)
            grupo(rej_mq, "Clase de aislamiento", var_scratch("clase_aislamiento"), 1, 1)
            grupo_tipo_mq = tk.Frame(rej_mq, bg="#FFFFFF")
            grupo_tipo_mq.grid(row=1, column=2, sticky="ew", padx=8, pady=5)
            tk.Label(
                grupo_tipo_mq, text="Tipo de máquina", bg="#FFFFFF",
                fg="#64748B", font=("Segoe UI", 9, "bold"), anchor="w",
            ).pack(fill="x", pady=(0, 4))
            ctk.CTkComboBox(
                grupo_tipo_mq, variable=var_scratch("tipo_maquina"),
                values=("Generador", "Motor"), state="readonly", height=30,
            ).pack(fill="x")

        def seccion_datos_reactor():
            subtitulo_seccion("DATOS DEL REACTOR")
            rej_re = rejilla(contenido, 4)
            grupo(rej_re, "Potencia reactiva (MVAr)", var_scratch("mvar"), 0, 0)
            grupo(rej_re, "Tensión nominal (kV)", var_scratch("v_nominal"), 0, 1)
            grupo(rej_re, "Corriente nominal (A)", var_scratch("i_nominal"), 0, 2)
            grupo(rej_re, "Reactancia (%)", var_scratch("reactancia"), 0, 3)
            grupo(rej_re, "Clase de enfriamiento", var_scratch("clase_enf"), 1, 0)

        def seccion_datos_transformador(con_terciario=True):
            # Bloque «Tipo de transformador» del formato oficial
            subtitulo_seccion("DATOS DEL TRANSFORMADOR")
            rej_tr = rejilla(contenido, 4)
            grupo(rej_tr, "Gerencia Regional de Transmisión", var_scratch("gerencia"), 0, 0)
            grupo(rej_tr, "Zona", var_scratch("subarea"), 0, 1)
            grupo_tipo = tk.Frame(rej_tr, bg="#FFFFFF")
            grupo_tipo.grid(row=0, column=2, sticky="ew", padx=8, pady=5)
            tk.Label(
                grupo_tipo, text="Tipo de transformador", bg="#FFFFFF",
                fg="#64748B", font=("Segoe UI", 9, "bold"), anchor="w",
            ).pack(fill="x", pady=(0, 4))
            ctk.CTkComboBox(
                grupo_tipo, variable=self.datos_prueba["configuracion"],
                values=("Trifásico", "Monofásico"), state="readonly",
                height=30,
            ).pack(fill="x")
            grupo(rej_tr, "Clase de enfriamiento", var_scratch("clase_enf"), 0, 3)
            grupo(rej_tr, "Año puesta en servicio", var_scratch("anio_servicio"), 1, 0)
            grupo(rej_tr, "# Taps ± %", var_scratch("taps"), 1, 1)
            grupo(rej_tr, "kV nom A.T.", var_scratch("kv_at"), 1, 2)
            grupo(rej_tr, "kV nom B.T.", var_scratch("kv_bt"), 1, 3)
            if con_terciario:
                grupo(rej_tr, "kV nom Terciario", var_scratch("kv_terc"), 2, 0)
            for fila_z, num_z in enumerate((1, 2, 3), start=3):
                grupo(rej_tr, f"%Z {num_z}", var_scratch(f"z{num_z}"), fila_z, 0)
                grupo(rej_tr, f"a (MVA) {num_z}", var_scratch(f"z{num_z}_mva"), fila_z, 1)
                grupo(rej_tr, f"kV {num_z}", var_scratch(f"z{num_z}_kv"), fila_z, 2)

        def seccion_orden_trabajo():
            subtitulo_seccion("ORDEN DE TRABAJO")
            rej_ot = rejilla(contenido, 3)
            grupo(rej_ot, "O.T.", var_scratch("ot"), 0, 0)
            grupo(rej_ot, "Fecha", var_scratch("fecha"), 0, 1)
            grupo(rej_ot, "Programado", var_scratch("programado"), 0, 2)
            grupo(rej_ot, "Falla", var_scratch("falla"), 1, 1)
            grupo(rej_ot, "RIM", var_scratch("rim"), 1, 2)
            grupo(rej_ot, "RIG", var_scratch("rig"), 2, 0)
            grupo(rej_ot, "No. Licencia", var_scratch("licencia"), 2, 1)
            grupo(rej_ot, "Número de registro", var_scratch("registro"), 2, 2)

        def seccion_equipo_medicion():
            subtitulo_seccion("EQUIPO DE MEDICIÓN UTILIZADO")
            rej_em = rejilla(contenido, 3)
            grupo(rej_em, "Modelo", var_scratch("inst_modelo"), 0, 0)
            grupo(rej_em, "Marca", var_scratch("inst_marca"), 0, 1)
            grupo(rej_em, "No. Serie", var_scratch("inst_serie"), 0, 2)
            grupo(rej_em, "Fecha Calibración", var_scratch("inst_cal"), 1, 0)
            grupo(rej_em, "Fecha Vencimiento", var_scratch("inst_venc"), 1, 1)
            grupo(rej_em, "No. Inv. EIMP", var_scratch("inst_eimp"), 1, 2)

        def seccion_firmas():
            subtitulo_seccion("FIRMAS")
            rej_fir = rejilla(contenido, 3)
            grupo(rej_fir, "Realizó — Nombre y firma", var_scratch("realizo"), 0, 0)
            grupo(rej_fir, "Revisó — Nombre y firma", var_scratch("reviso"), 0, 1)
            grupo(rej_fir, "Aprobó — Nombre y firma", var_scratch("aprobo"), 0, 2)

        def seccion_cierre(con_diagrama=False):
            rej_cierre = rejilla(contenido, 2)
            grupo(
                rej_cierre, "Fecha de la última medición",
                var_scratch("ultima_medicion"), 0, 0,
            )
            if con_diagrama:
                grupo(
                    rej_cierre, "Dibujar diagrama vectorial — Tipo",
                    var_scratch("diagrama_tipo"), 0, 1,
                )

        def formato_1min(equipo, pruebas):
            titulo_formato(f"Medición de Resistencia de Aislamiento — {equipo}")
            seccion_identificacion()
            seccion_condiciones(incluir_kt=True)
            if self._familia_ra(equipo) == "tc":
                seccion_datos_tc()
            else:
                seccion_datos_tp()
            seccion_orden_trabajo()
            seccion_equipo_medicion()
            seccion_cierre()
            if self._familia_ra(equipo) in ("tc", "tp"):
                titulo_prueba = f"Prueba (Fase {self.datos_prueba['fase'].get()})"
            elif self.datos_prueba["configuracion"].get() == "Monofásico":
                titulo_prueba = f"Prueba (Fase {self.datos_prueba['fase'].get()})"
            else:
                titulo_prueba = "Prueba (Trifásico)"
            tabla = tk.Frame(contenido, bg="#FFFFFF")
            tabla.pack(fill="x", padx=15)
            cabecera_tabla(tabla, (
                (titulo_prueba, 34), ("Voltaje Aplicado", 15),
                ("Lectura a 1 min (MΩ)", 18), ("Corregida a 20°C (MΩ)", 18),
            ))
            for indice, prueba in enumerate(pruebas):
                fila_t = indice + 1
                tk.Label(
                    tabla,
                    text=(
                        f"{prueba['medicion']}  (L={prueba['linea']}  "
                        f"T={prueba['tierra']}  G={prueba['guarda']})"
                    ),
                    bg="#FFFFFF", fg="#1E293B",
                    font=("Segoe UI", 9, "bold"), anchor="w", padx=8,
                    pady=7, wraplength=320, justify="left",
                ).grid(row=fila_t, column=0, sticky="ew")
                tk.Label(
                    tabla, text=formato_kv(prueba["kv"]), bg="#FFFFFF",
                    fg="#64748B", font=("Segoe UI", 9), anchor="w", padx=8,
                ).grid(row=fila_t, column=1, sticky="ew")
                var_lec = tk.StringVar(
                    visor,
                    value=self._lectura_guardada_anexo_a(prueba).get(
                        "1 min", "",
                    ),
                )
                entrada_lec = ctk.CTkEntry(
                    tabla, textvariable=var_lec, height=28,
                )
                entrada_lec.grid(
                    row=fila_t, column=2, sticky="ew", padx=6, pady=4,
                )
                etiqueta_corr = tk.Label(
                    tabla, text="Auto-calculado", bg="#F8FAFC",
                    fg="#94A3B8", font=("Segoe UI", 9), anchor="w", padx=8,
                    pady=7,
                )
                etiqueta_corr.grid(
                    row=fila_t, column=3, sticky="ew", padx=(0, 6),
                )

                def corregir(_e=None, var=var_lec, etiqueta=etiqueta_corr):
                    kt = actualizar_kt()
                    valor = self._lectura_mohm_ra(var.get())
                    if kt is None or valor is None:
                        etiqueta.config(text="Auto-calculado", fg="#94A3B8")
                        return "break"
                    etiqueta.config(
                        text=self._fmt_mohm_ra(
                            valor * kt, self._unidad_lectura_ra(var.get()),
                        ),
                        fg="#334155",
                    )
                    return "break"

                entrada_lec.bind("<Return>", corregir, add="+")
                entrada_lec.bind("<FocusOut>", corregir, add="+")
                if var_lec.get().strip():
                    corregir()
            if self._familia_ra(equipo) == "tc":
                _dibujar_diagrama_tc(contenido)
            elif "TPC" in equipo:
                _dibujar_diagrama_tpc(contenido)
            elif "TPs" in equipo:
                _dibujar_diagrama_tp(contenido)
            familia = self._familia_ra(equipo)
            minimo = "45 000 MΩ" if familia == "tc" else "40 000 MΩ"
            caja_resultado(
                contenido,
                f"Valor mínimo (Tabla 5): {minimo} a 1 min y 20 °C.",
            )
            seccion_firmas()

        def formato_10min(equipo, pruebas):
            titulo_formato(f"Medición de Resistencia de Aislamiento — {equipo}")
            seccion_identificacion()
            seccion_condiciones(incluir_kt=True)
            if "Reactores" in equipo:
                seccion_datos_reactor()
            else:
                seccion_datos_transformador(
                    con_terciario=(
                        "3 Devanados" in equipo
                        or "Autotransformadores" in equipo
                    ),
                )
            seccion_orden_trabajo()
            seccion_equipo_medicion()
            seccion_cierre(con_diagrama=True)
            tabla = tk.Frame(contenido, bg="#FFFFFF")
            tabla.pack(fill="x", padx=15)
            cabecera_tabla(tabla, (
                ("Prueba (Conexión)", 36), ("30 seg (MΩ)", 14),
                ("1 min (MΩ)", 14), ("10 min (MΩ)", 14), ("ip", 12),
            ))
            for indice, prueba in enumerate(pruebas):
                fila_t = indice + 1
                tk.Label(
                    tabla,
                    text=(
                        f"{prueba['medicion']}  (L={prueba['linea']}  "
                        f"T={prueba['tierra']}  G={prueba['guarda']})"
                    ),
                    bg="#FFFFFF", fg="#1E293B",
                    font=("Segoe UI", 9, "bold"), anchor="w", padx=8,
                    pady=7, wraplength=330, justify="left",
                ).grid(row=fila_t, column=0, sticky="ew")
                variables = []
                guardadas = self._lectura_guardada_anexo_a(prueba)
                for columna, rotulo in enumerate(
                    ("30 s", "1 min", "10 min"), start=1,
                ):
                    var_t = tk.StringVar(visor, value=guardadas.get(rotulo, ""))
                    variables.append(var_t)
                    entrada_t = ctk.CTkEntry(
                        tabla, textvariable=var_t, height=28,
                    )
                    entrada_t.grid(
                        row=fila_t, column=columna, sticky="ew",
                        padx=4, pady=4,
                    )
                etiqueta_ip = tk.Label(
                    tabla, text="—", bg="#F8FAFC", fg="#94A3B8",
                    font=("Segoe UI", 9, "bold"), anchor="w", padx=8, pady=7,
                )
                etiqueta_ip.grid(
                    row=fila_t, column=4, sticky="ew", padx=(0, 6),
                )

                def calcular_ip(_e=None, vars_t=variables, etiqueta=etiqueta_ip):
                    r30 = self._lectura_mohm_ra(vars_t[0].get())
                    r1 = self._lectura_mohm_ra(vars_t[1].get())
                    r10 = self._lectura_mohm_ra(vars_t[2].get())
                    if r1 and r10:
                        texto_ip = f"ip = {r10 / r1:.2f}"
                        if r30:
                            texto_ip += f"   ia = {r1 / r30:.2f}"
                        etiqueta.config(text=texto_ip, fg="#1A202C")
                    else:
                        etiqueta.config(text="—", fg="#94A3B8")
                    return "break"

                for hijo in tabla.grid_slaves(row=fila_t):
                    if isinstance(hijo, ctk.CTkEntry):
                        hijo.bind("<Return>", calcular_ip, add="+")
                        hijo.bind("<FocusOut>", calcular_ip, add="+")
            if "2 Devanados" in equipo:
                marco_diagrama = tk.Frame(contenido, bg="#FFFFFF")
                marco_diagrama.pack(fill="x")

                def _redibujar_trafo(*_args):
                    for hijo_d in marco_diagrama.winfo_children():
                        hijo_d.destroy()
                    _dibujar_diagrama_transformador_2d(
                        marco_diagrama,
                        monofasico=(
                            self.datos_prueba["configuracion"].get()
                            == "Monofásico"
                        ),
                    )

                _redibujar_trafo()
                self.datos_prueba["configuracion"].trace_add(
                    "write", _redibujar_trafo,
                )
            elif "3 Devanados" in equipo:
                marco_diagrama3 = tk.Frame(contenido, bg="#FFFFFF")
                marco_diagrama3.pack(fill="x")

                def _redibujar_trafo3(*_args):
                    for hijo_d in marco_diagrama3.winfo_children():
                        hijo_d.destroy()
                    if self.datos_prueba["configuracion"].get() != "Monofásico":
                        _dibujar_diagrama_transformador_3d(
                            marco_diagrama3, naranja=RA_NARANJA_PASTEL,
                        )

                _redibujar_trafo3()
                self.datos_prueba["configuracion"].trace_add(
                    "write", _redibujar_trafo3,
                )
            elif "Autotransformadores" in equipo:
                marco_diagrama_auto = tk.Frame(contenido, bg="#FFFFFF")
                marco_diagrama_auto.pack(fill="x")

                def _redibujar_auto(*_args):
                    for hijo_d in marco_diagrama_auto.winfo_children():
                        hijo_d.destroy()
                    _dibujar_diagrama_autotransformador(
                        marco_diagrama_auto,
                        monofasico=(
                            self.datos_prueba["configuracion"].get()
                            == "Monofásico"
                        ),
                        naranja=RA_NARANJA_PASTEL,
                    )

                _redibujar_auto()
                self.datos_prueba["configuracion"].trace_add(
                    "write", _redibujar_auto,
                )
            elif "Reactores" in equipo:
                _dibujar_diagrama_reactor(contenido)
            caja_resultado(
                contenido,
                "Cálculo de ip e ia realizado automáticamente por el "
                "sistema. El procedimiento acepta ip ≥ 1.5.",
            )
            seccion_firmas()

        def formato_generador(equipo, pruebas):
            titulo_formato(f"Medición de Resistencia de Aislamiento — {equipo}")
            seccion_identificacion()
            seccion_condiciones(incluir_devanado=False)
            seccion_datos_maquina()
            rejilla1 = rejilla(contenido, 4)
            entrada_dev = grupo(
                rejilla1, "Temp. Devanado (°C)",
                self.datos_prueba["temp_devanado"], 0, 0,
            )
            grupo_kt = tk.Frame(rejilla1, bg="#FFFFFF")
            grupo_kt.grid(row=0, column=1, sticky="ew", padx=8, pady=5)
            tk.Label(
                grupo_kt, text="Factor Kt a 40°C", bg="#FFFFFF", fg="#64748B",
                font=("Segoe UI", 9, "bold"), anchor="w",
            ).pack(fill="x", pady=(0, 4))
            ctk.CTkEntry(
                grupo_kt, textvariable=kt_var, height=30, state="readonly",
                fg_color="#F8FAFC", text_color="#94A3B8",
            ).pack(fill="x")
            entrada_dev.bind("<FocusOut>", actualizar_kt, add="+")
            entrada_dev.bind("<Return>", actualizar_kt, add="+")
            actualizar_kt()
            for columna, (texto_lim, valor_lim) in enumerate(
                (("Límite ia", "1.45 ± 25%"), ("Límite ip", "≥ 1.5")),
                start=2,
            ):
                grupo_lim = tk.Frame(rejilla1, bg="#FFFFFF")
                grupo_lim.grid(
                    row=0, column=columna, sticky="ew", padx=8, pady=5,
                )
                tk.Label(
                    grupo_lim, text=texto_lim, bg="#FFFFFF", fg="#64748B",
                    font=("Segoe UI", 9, "bold"), anchor="w",
                ).pack(fill="x", pady=(0, 4))
                var_lim = tk.StringVar(visor, value=valor_lim)
                ctk.CTkEntry(
                    grupo_lim, textvariable=var_lim, height=30,
                    state="readonly", fg_color="#F8FAFC",
                    text_color="#94A3B8",
                ).pack(fill="x")
            seccion_orden_trabajo()
            seccion_equipo_medicion()
            seccion_cierre()
            tabla = tk.Frame(contenido, bg="#FFFFFF")
            tabla.pack(fill="x", padx=15)
            # Una columna por prueba del formato SC-CT-001-F (Fig. 10).
            fases = tuple(prueba["prueba"] for prueba in pruebas)
            cabecera_tabla(tabla, (("Tiempo", 12),) + tuple(
                (f"P{prueba['prueba']}: L={prueba['linea']} (MΩ)", 16)
                for prueba in pruebas
            ))
            variables_fase = {}
            for indice, tiempo in enumerate(("30 seg", "1 min", "10 min")):
                fila_t = indice + 1
                tk.Label(
                    tabla, text=tiempo, bg="#FFFFFF", fg="#1E293B",
                    font=("Segoe UI", 9, "bold"), anchor="w", padx=8, pady=7,
                ).grid(row=fila_t, column=0, sticky="ew")
                for columna, fase in enumerate(fases, start=1):
                    var_f = tk.StringVar(visor)
                    variables_fase[(fase, tiempo)] = var_f
                    entrada_f = ctk.CTkEntry(
                        tabla, textvariable=var_f, height=28,
                    )
                    entrada_f.grid(
                        row=fila_t, column=columna, sticky="ew",
                        padx=4, pady=4,
                    )
            etiqueta_indices = tk.Label(
                contenido, text="ia / ip por prueba: —", bg="#FFFFFF",
                fg="#334155", font=("Segoe UI", 10, "bold"), anchor="w",
                justify="left", wraplength=940,
            )
            etiqueta_indices.pack(fill="x", padx=15, pady=(10, 4))

            def calcular_indices(_e=None):
                partes = []
                for fase in fases:
                    r30 = self._lectura_mohm_ra(
                        variables_fase[(fase, "30 seg")].get()
                    )
                    r1 = self._lectura_mohm_ra(
                        variables_fase[(fase, "1 min")].get()
                    )
                    r10 = self._lectura_mohm_ra(
                        variables_fase[(fase, "10 min")].get()
                    )
                    if r30 and r1 and r10:
                        partes.append(
                            f"P{fase}: ia = {r1 / r30:.2f} · "
                            f"ip = {r10 / r1:.2f}"
                        )
                etiqueta_indices.config(
                    text="    ".join(partes) if partes else "ia / ip por prueba: —"
                )
                return "break"

            for hijo in tabla.winfo_children():
                if isinstance(hijo, ctk.CTkEntry):
                    hijo.bind("<Return>", calcular_indices, add="+")
                    hijo.bind("<FocusOut>", calcular_indices, add="+")
            nota = tk.Frame(
                contenido, bg="#F8FAFC",
                highlightbackground="#E2E8F0", highlightthickness=1,
            )
            nota.pack(fill="x", padx=15, pady=(8, 6))
            tk.Label(
                nota,
                text=(
                    "Nota: El sistema calcula automáticamente el ia "
                    "(R1min/R30seg) y el ip (R10min/R1min) para cada prueba. "
                    "Las lecturas se corrigen a 40 °C (ST-CT-001, 4.2.5)."
                ),
                bg="#F8FAFC", fg="#475569", font=("Segoe UI", 9),
                anchor="w", justify="left", wraplength=900,
                ).pack(fill="x", padx=12, pady=10)
            seccion_firmas()

        def formato_apartarrayos(equipo, pruebas):
            titulo_formato(f"Medición de Resistencia de Aislamiento — {equipo}")
            seccion_identificacion()
            seccion_condiciones(incluir_devanado=False)
            subtitulo_seccion("DATOS DEL APARTARRAYOS")
            rejilla1 = rejilla(contenido, 2)
            grupo_sec = tk.Frame(rejilla1, bg="#FFFFFF")
            grupo_sec.grid(row=0, column=0, sticky="ew", padx=8, pady=5)
            tk.Label(
                grupo_sec, text="Número de Secciones", bg="#FFFFFF",
                fg="#64748B", font=("Segoe UI", 9, "bold"), anchor="w",
            ).pack(fill="x", pady=(0, 4))
            ctk.CTkComboBox(
                grupo_sec,
                variable=self.datos_prueba["secciones_apartarrayos"],
                values=("Una sección", "Varias secciones"),
                state="readonly", height=30,
                command=lambda _v=None: construir(),
            ).pack(fill="x")
            voltaje = formato_kv(pruebas[0]["kv"]) if pruebas else "—"
            var_vol = tk.StringVar(visor, value=voltaje)
            grupo_vol = tk.Frame(rejilla1, bg="#FFFFFF")
            grupo_vol.grid(row=0, column=1, sticky="ew", padx=8, pady=5)
            tk.Label(
                grupo_vol, text="Voltaje Aplicado", bg="#FFFFFF",
                fg="#64748B", font=("Segoe UI", 9, "bold"), anchor="w",
            ).pack(fill="x", pady=(0, 4))
            ctk.CTkEntry(
                grupo_vol, textvariable=var_vol, height=30,
                state="readonly", fg_color="#F8FAFC", text_color="#94A3B8",
            ).pack(fill="x")
            grupo(rejilla1, "Tensión de operación continua MCOV (kV)", var_scratch("mcov"), 1, 0)
            grupo(rejilla1, "Corriente de descarga nominal (kA)", var_scratch("descarga"), 1, 1)
            grupo(rejilla1, "Tipo / Clase", var_scratch("tipo_apartarrayos"), 2, 0)
            grupo(rejilla1, "Material", var_scratch("material_ap"), 2, 1)
            seccion_orden_trabajo()
            seccion_equipo_medicion()
            seccion_cierre()
            tabla = tk.Frame(contenido, bg="#FFFFFF")
            tabla.pack(fill="x", padx=15)
            cabecera_tabla(tabla, (
                ("Prueba", 30), ("Lectura a 1 min (MΩ)", 20),
                ("Observación", 34),
            ))
            for indice, prueba in enumerate(pruebas):
                fila_t = indice + 1
                tk.Label(
                    tabla,
                    text=(
                        f"{prueba['medicion']}  (L={prueba['linea']}  "
                        f"T={prueba['tierra']}  G={prueba['guarda']})"
                    ),
                    bg="#FFFFFF", fg="#1E293B",
                    font=("Segoe UI", 9, "bold"), anchor="w", padx=8,
                    pady=7, wraplength=300, justify="left",
                ).grid(row=fila_t, column=0, sticky="ew")
                entrada_lec = ctk.CTkEntry(
                    tabla, textvariable=tk.StringVar(visor), height=28,
                )
                entrada_lec.grid(
                    row=fila_t, column=1, sticky="ew", padx=6, pady=4,
                )
                entrada_obs = ctk.CTkEntry(
                    tabla, textvariable=tk.StringVar(visor), height=28,
                )
                entrada_obs.grid(
                    row=fila_t, column=2, sticky="ew", padx=6, pady=4,
                )
            _dibujar_diagrama_apartarrayos(contenido)
            caja = tk.Frame(contenido, bg="#FEF3C7")
            caja.pack(fill="x", padx=15, pady=(14, 6))
            acento = tk.Frame(caja, bg="#F59E0B", width=6)
            acento.pack(side="left", fill="y")
            acento.pack_propagate(False)
            tk.Label(
                caja,
                text=(
                    "Criterio de Apartarrayos: Los valores varían de 500 "
                    "a 50,000 MΩ. La comparación se hace entre unidades de "
                    "la misma marca. Cualquier desviación notoria "
                    "requiere INVESTIGACIÓN."
                ),
                bg="#FEF3C7", fg="#92400E", font=("Segoe UI", 9),
                anchor="w", justify="left", wraplength=880,
                ).pack(side="left", fill="x", expand=True, padx=12, pady=10)
            seccion_firmas()

        def construir():
            for hijo in contenido.winfo_children():
                hijo.destroy()
            equipo = self.datos_prueba["tipo_equipo"].get().strip()
            pruebas = self._obtener_pruebas_equipo()
            familia = self._familia_ra(equipo)
            if familia in ("tc", "tp"):
                formato_1min(equipo, pruebas)
            elif familia == "rotativa":
                formato_generador(equipo, pruebas)
            elif familia == "apartarrayos":
                formato_apartarrayos(equipo, pruebas)
            else:
                formato_10min(equipo, pruebas)
            contenido._parent_canvas.yview_moveto(0)

        combo_equipo = ctk.CTkComboBox(
            barra_sup, variable=self.datos_prueba["tipo_equipo"],
            values=EQUIPOS_AISLAMIENTO, state="readonly", width=360,
            command=lambda _v=None: construir(),
        )
        combo_equipo.pack(side="right", padx=20, pady=10)
        ctk.CTkButton(
            barra_sup, text="GUARDAR", fg_color="#3B82F6",
            hover_color="#2563EB", text_color="white",
            font=ctk.CTkFont(weight="bold"), width=110, height=34,
            command=lambda: self._guardar_en_historial("Anexo A", visor),
        ).pack(side="right", padx=(10, 0), pady=10)
        ctk.CTkButton(
            barra_sup, text="IMPRIMIR", fg_color="#3B82F6",
            hover_color="#2563EB", text_color="white",
            font=ctk.CTkFont(weight="bold"), width=110, height=34,
            command=lambda: _imprimir_formato_carta(
                contenido, "Anexo A — Resistencia de Aislamiento",
            ),
        ).pack(side="right", padx=(10, 0), pady=10)
        construir()
        visor.focus_force()
        return visor
    def mostrar_anexo_b_operacion(self, padre):
        visor = tk.Toplevel(padre)
        visor.title("ANEXO B  Operación del Equipo")
        visor.configure(bg="#FFFFFF")
        visor.geometry("820x760")
        visor.minsize(700, 560)
        visor.transient(padre)

        encabezado = tk.Frame(visor, bg="#F8FAFC")
        encabezado.pack(fill="x")
        titulo_b = tk.Frame(encabezado, bg="#F8FAFC")
        titulo_b.pack(side="left", padx=30, pady=16)
        tk.Label(
            titulo_b, text="ANEXO B", bg="#F8FAFC", fg="#3B82F6",
            font=("Segoe UI", 15, "bold"),
        ).pack(side="left")
        tk.Label(
            titulo_b, text=" - Operación del Equipo", bg="#F8FAFC",
            fg="#1E293B", font=("Segoe UI", 15, "bold"),
        ).pack(side="left")
        etiqueta_cerrar = tk.Label(
            encabezado, text="✕", bg="#F8FAFC", fg="#94A3B8",
            font=("Segoe UI", 14, "bold"), cursor="hand2",
        )
        etiqueta_cerrar.pack(side="right", padx=20)
        etiqueta_cerrar.bind("<Button-1>", lambda _e=None: visor.destroy())
        etiqueta_cerrar.bind(
            "<Enter>", lambda _e=None: etiqueta_cerrar.config(fg="#EF4444"),
        )
        etiqueta_cerrar.bind(
            "<Leave>", lambda _e=None: etiqueta_cerrar.config(fg="#94A3B8"),
        )
        tk.Frame(visor, bg="#E2E8F0", height=1).pack(fill="x")

        cuerpo = ctk.CTkScrollableFrame(visor, fg_color="#FFFFFF")
        cuerpo.pack(fill="both", expand=True, padx=16, pady=10)

        alerta = tk.Frame(
            cuerpo, bg="#FFFBEB",
            highlightbackground="#FDE68A", highlightthickness=1,
        )
        alerta.pack(fill="x", pady=(6, 4))
        tk.Label(
            alerta,
            text=(
                "Equipo de medición: Megómetro (Megger).  "
                "Norma: ST-CT-001 y PE-D1110 §2.3.1 y §3.1."
            ),
            bg="#FFFBEB", fg="#92400E", font=("Segoe UI", 10),
            anchor="w", justify="left", wraplength=700,
        ).pack(fill="x", padx=14, pady=10)

        def seccion(texto):
            fila = tk.Frame(cuerpo, bg="#FFFFFF")
            fila.pack(fill="x", pady=(18, 6))
            acento = tk.Frame(fila, bg="#3B82F6", width=4)
            acento.pack(side="left", fill="y")
            acento.pack_propagate(False)
            tk.Label(
                fila, text=texto.upper(), bg="#FFFFFF", fg="#0F172A",
                font=("Segoe UI", 11, "bold"),
            ).pack(side="left", padx=(10, 0))

        def numerado(indice, texto):
            tk.Label(
                cuerpo, text=f"{indice}.   {texto}", bg="#FFFFFF",
                fg="#334155", font=("Segoe UI", 10), anchor="w",
                justify="left", wraplength=690,
            ).pack(fill="x", padx=(18, 6), pady=3)

        def vineta(texto, negrita=None):
            fila = tk.Frame(cuerpo, bg="#FFFFFF")
            fila.pack(fill="x", padx=(14, 0), pady=2)
            tk.Label(
                fila, text="•", bg="#FFFFFF", fg="#334155",
                font=("Segoe UI", 10, "bold"),
            ).pack(side="left", anchor="n")
            if negrita:
                tk.Label(
                    fila, text=f"  {negrita}", bg="#FFFFFF",
                    fg="#1E293B", font=("Segoe UI", 10, "bold"),
                ).pack(side="left", anchor="n")
            tk.Label(
                fila, text=f"  {texto}",
                bg="#FFFFFF", fg="#334155", font=("Segoe UI", 10),
                justify="left", wraplength=620, anchor="w",
            ).pack(side="left", fill="x", expand=True)

        seccion("Antes de energizar el megómetro")
        for indice, paso in enumerate((
            "Tramitar la licencia del equipo que está en operación.",
            "Verificar que el equipo está desenergizado y que los "
            "interruptores quedaron abiertos en forma física.",
            "Desconectar las terminales de línea y de barra. "
            "Hacer la inspección previa.",
            "Dejar el tanque o la estructura aterrizados.",
            "Aterrizar el equipo unos 10 minutos antes de la prueba "
            "para drenar la carga capacitiva.",
            "La humedad relativa debe quedar debajo de 75 % cuando "
            "el procedimiento lo pide.",
            "Registrar temperatura del aceite o del devanado, "
            "temperatura ambiente y humedad relativa.",
        ), start=1):
            numerado(indice, paso)

        seccion("Conexión del megómetro")
        vineta("va al devanado o terminal que se mide.", "Línea (+):")
        vineta(
            "va al retorno: tanque, otro devanado o la combinación "
            "que indique el formato.",
            "Tierra (−):",
        )
        vineta(
            "se usa para apartar el devanado o la porcelana que no "
            "se quiere medir.",
            "Guarda:",
        )
        tk.Label(
            cuerpo, text="Consideraciones de conexión:", bg="#FFFFFF",
            fg="#1E293B", font=("Segoe UI", 10, "bold"), anchor="w",
        ).pack(fill="x", padx=(14, 0), pady=(10, 4))
        vineta("En transformadores de corriente la conexión es en serie.")
        vineta(
            "En transformadores de potencial y TPC la conexión es en paralelo."
        )
        vineta(
            "No se rebasan la tensión nominal del equipo ni 5 kV de "
            "corriente directa en esta prueba. PE-D1110 recomienda "
            "2 500 V o 5 000 V, con un mínimo de 1 000 V."
        )

        seccion("Tiempo de la prueba")
        vineta(
            "10 minutos. Se registran 30 s, 1 min y los minutos 2 a 10. "
            "La resistencia no debe bajar con el tiempo (§4.1.3).",
            "Transformadores, autotransformadores y reactores:",
        )
        vineta(
            "1 minuto (§4.3.3).",
            "Transformadores de corriente, de potencial, TPC e instrumentos:",
        )

        seccion("Al terminar")
        for indice, paso in enumerate((
            "Bajar la tensión del megómetro y descargar el equipo a "
            "tierra antes de quitar las conexiones.",
            "Corregir la resistencia a 20 °C con Rc = Rt × Kt "
            "(Tabla 1 ST-CT-001).",
            "Calcular ip = R10 min / R1 min. "
            "El procedimiento acepta ip ≥ 1.5.",
            "El ia = R1 min / R30 s = 1.45 ± 25 % no se toma como "
            "conclusivo en aceite.",
            "En TC y TP/TPC el dictamen es la lectura de 1 minuto a "
            "20 °C contra la Tabla 5, sin ip ni ia.",
        ), start=1):
            numerado(indice, paso)

        tk.Frame(visor, bg="#E2E8F0", height=1).pack(fill="x")
        pie = tk.Frame(visor, bg="#F8FAFC")
        pie.pack(fill="x")
        ctk.CTkButton(
            pie, text="Cerrar", fg_color="#10B981",
            hover_color="#059669", text_color="white",
            font=ctk.CTkFont(size=12, weight="bold"),
            width=110, height=36, command=visor.destroy,
        ).pack(side="right", padx=30, pady=12)
        visor.focus_force()
        return visor
    def mostrar_anexo_c_resumen(self, padre):
        """Anexo C de RA: resumen del procedimiento ST-CT-001, tal como viene en el documento."""
        visor = tk.Toplevel(padre)
        visor.title("ANEXO C  Resumen de procedimiento — ST-CT-001")
        visor.configure(bg="#FFFFFF")
        visor.geometry("860x900")
        visor.transient(padre)
        cuerpo = ctk.CTkScrollableFrame(visor, fg_color="#FFFFFF")
        cuerpo.pack(fill="both", expand=True, padx=12, pady=12)
        tk.Label(
            cuerpo,
            text=(
                "Anexo C Resumen de procedimiento para la medición de resistencia "
                "de aislamiento en equipo eléctrico primario"
            ),
            bg="#FFFFFF", fg="#1E293B", font=("Segoe UI", 12, "bold"),
            anchor="w", justify="left", wraplength=780,
        ).pack(fill="x", pady=(0, 12))
        cabecera_c = tk.Frame(cuerpo, bg="#0F172A")
        cabecera_c.pack(fill="x", pady=(0, 10))
        tk.Label(
            cabecera_c, text="PROCEDIMIENTO ST-CT-001", bg="#0F172A", fg="#FB923C",
            font=("Segoe UI", 9, "bold"), anchor="w", padx=16, pady=10,
        ).pack(fill="x")
        tk.Label(
            cabecera_c,
            text=(
                "Procedimiento para la medición de resistencia de aislamiento en "
                "equipo eléctrico primario"
            ),
            bg="#0F172A", fg="#FFFFFF", font=("Segoe UI", 11, "bold"),
            anchor="w", justify="left", wraplength=760, padx=16, pady=12,
        ).pack(fill="x")
        filas_c = (
            ("En que consiste la medición", (
                "La resistencia de aislamiento se define como la oposición del "
                "aislamiento al paso de la corriente eléctrica al aplicar un voltaje "
                "de corriente directa (CD).",
                "La resistencia del aislamiento está función del tiempo y de la "
                "magnitud del voltaje aplicado y se mide en Megaohms (MΩ). La "
                "resistencia de aislamiento varía directamente con el espesor del "
                "aislamiento e inversamente al área del mismo.",
            )),
            ("Que detecta la medición", (
                "La presencia de humedad con suciedad puede ocasionar una reducción "
                "en los valores de resistencia de aislamiento.",
            )),
            ("Equipo de medición", ("Megóhmetro (Megger).",)),
            ("Valores o límites recomendados", (
                "Índice de polarización mayor o igual a 1.5.",
            )),
            ("Comparación de valores", (
                "Un cambio del 25% en el valor de la resistencia de aislamiento para "
                "esta relación de voltajes, generalmente se debe a la presencia "
                "excesiva de humedad u otros contaminantes.",
                "Analizar la tendencia de los valores obtenidos en las pruebas "
                "periódicas a que se somete el aislamiento (se sugiere realizar "
                "gráficas de tendencias).",
            )),
            ("Correcciones", (
                "Rc = Kt × Ri",
                "Rc = Resistencia de aislamiento corregida a la temperatura base (MΩ).",
                "Kt = Coeficiente de corrección por temperatura.",
                "Ri = Resistencia de aislamiento a la temperatura que efectuó la prueba (MΩ).",
                "20 °C para transformadores, ver tabla 1 Coeficientes de corrección por temperatura",
            )),
            ("Ecuaciones para cálculo", (
                "Cálculo del índice de polarización:  IP = R(AISL) 10 min / R(AISL) 1 min     IP ≥ 1.5",
                "Cálculo índice de absorción:  IA = R(AISL) 1 min / R(AISL) 30 seg     IA = 1.45 ± 25%",
            )),
            ("Recomendaciones", (
                "No es recomendable hacer mediciones del IA en transformadores "
                "inmersos en aceite. Esto se debe a que el concepto del IA se basa en "
                "el comportamiento de las estructuras rígidas de materiales sólidos en "
                "presencia de un campo producido por un voltaje aplicado. Por lo tanto, "
                "este índice no es aplicable en aislamientos líquidos.",
            )),
        )
        for rotulo, textos in filas_c:
            tarjeta_c = tk.Frame(
                cuerpo, bg="#FFFFFF",
                highlightbackground="#E2E8F0", highlightthickness=1,
            )
            tarjeta_c.pack(fill="x", pady=5)
            tk.Frame(tarjeta_c, bg="#EA580C", width=5).pack(side="left", fill="y")
            contenido_c = tk.Frame(tarjeta_c, bg="#FFFFFF")
            contenido_c.pack(side="left", fill="x", expand=True, padx=16, pady=12)
            tk.Label(
                contenido_c, text=rotulo.upper(), bg="#FFFFFF", fg="#9A3412",
                font=("Segoe UI", 9, "bold"), anchor="w",
            ).pack(fill="x", pady=(0, 4))
            for texto_c in textos:
                tk.Label(
                    contenido_c, text=texto_c, bg="#FFFFFF", fg="#0F172A",
                    font=("Segoe UI", 10), anchor="w", justify="left",
                    wraplength=720,
                ).pack(fill="x", pady=2)
        visor.focus_force()
        return visor

    def _visor_anexo_c_anterior(self, padre):
        visor = tk.Toplevel(padre)
        visor.title("ANEXO C  Resumen del Procedimiento")
        visor.configure(bg="#F8FAFC")
        visor.geometry("840x780")
        visor.minsize(740, 560)
        visor.transient(padre)

        encabezado = tk.Frame(visor, bg="#FFFFFF")
        encabezado.pack(fill="x")
        titulo_c = tk.Frame(encabezado, bg="#FFFFFF")
        titulo_c.pack(side="left", padx=30, pady=16)
        tk.Label(
            titulo_c, text="ANEXO C", bg="#FFFFFF", fg="#3B82F6",
            font=("Segoe UI", 15, "bold"),
        ).pack(side="left")
        tk.Label(
            titulo_c, text=" - Resumen del Procedimiento", bg="#FFFFFF",
            fg="#1E293B", font=("Segoe UI", 15, "bold"),
        ).pack(side="left")
        etiqueta_cerrar = tk.Label(
            encabezado, text="✕", bg="#FFFFFF", fg="#94A3B8",
            font=("Segoe UI", 14, "bold"), cursor="hand2",
        )
        etiqueta_cerrar.pack(side="right", padx=20)
        etiqueta_cerrar.bind("<Button-1>", lambda _e=None: visor.destroy())
        etiqueta_cerrar.bind(
            "<Enter>", lambda _e=None: etiqueta_cerrar.config(fg="#EF4444"),
        )
        etiqueta_cerrar.bind(
            "<Leave>", lambda _e=None: etiqueta_cerrar.config(fg="#94A3B8"),
        )
        tk.Frame(visor, bg="#E2E8F0", height=1).pack(fill="x")

        cuerpo = ctk.CTkScrollableFrame(visor, fg_color="#F8FAFC")
        cuerpo.pack(fill="both", expand=True, padx=16, pady=10)

        tk.Label(
            cuerpo,
            text=(
                "Medición de resistencia de aislamiento en equipo "
                "eléctrico primario. (ST-CT-001)"
            ),
            bg="#F8FAFC", fg="#64748B", font=("Segoe UI", 10, "bold"),
            anchor="w", justify="left", wraplength=720,
        ).pack(fill="x", padx=8, pady=(4, 10))

        rejilla = tk.Frame(cuerpo, bg="#F8FAFC")
        rejilla.pack(fill="x", padx=2)
        rejilla.columnconfigure(0, weight=1)
        rejilla.columnconfigure(1, weight=1)

        def tarjeta(fila, columna, titulo, ancho=300, columnas=1):
            tarjeta_f = tk.Frame(
                rejilla, bg="#FFFFFF",
                highlightbackground="#E2E8F0", highlightthickness=1,
            )
            tarjeta_f.grid(
                row=fila, column=columna, columnspan=columnas,
                sticky="nsew", padx=6, pady=6,
            )
            cabecera = tk.Frame(tarjeta_f, bg="#FFFFFF")
            cabecera.pack(fill="x", padx=16, pady=(12, 2))
            tk.Label(
                cabecera, text="●", bg="#FFFFFF", fg="#3B82F6",
                font=("Segoe UI", 8),
            ).pack(side="left")
            tk.Label(
                cabecera, text=titulo.upper(), bg="#FFFFFF",
                fg="#0F172A", font=("Segoe UI", 9, "bold"),
            ).pack(side="left", padx=(8, 0))
            contenido = tk.Frame(tarjeta_f, bg="#FFFFFF")
            contenido.pack(fill="x", padx=16, pady=(4, 12))
            return contenido, ancho

        def parrafo(padre_t, texto, ancho, negrita=None, nota=False):
            fila_p = tk.Frame(padre_t, bg="#FFFFFF")
            fila_p.pack(fill="x", pady=3)
            ancho_txt = ancho
            if negrita:
                tk.Label(
                    fila_p, text=negrita, bg="#FFFFFF", fg="#1E293B",
                    font=("Segoe UI", 10, "bold"),
                ).pack(side="left", anchor="n")
                ancho_txt = max(
                    150,
                    ancho - tkfont.Font(
                        family="Segoe UI", size=10, weight="bold",
                    ).measure(negrita),
                )
            tk.Label(
                fila_p, text=texto, bg="#FFFFFF",
                fg="#64748B" if nota else "#334155",
                font=("Segoe UI", 9 if nota else 10),
                anchor="w", justify="left", wraplength=ancho_txt,
            ).pack(side="left", fill="x", expand=True)

        def caja_formula(padre_t, texto):
            caja = tk.Frame(padre_t, bg="#F1F5F9")
            caja.pack(fill="x", pady=6)
            acento = tk.Frame(caja, bg="#94A3B8", width=3)
            acento.pack(side="left", fill="y")
            acento.pack_propagate(False)
            tk.Label(
                caja, text=texto, bg="#F1F5F9", fg="#0F172A",
                font=("Consolas", 11), anchor="w",
            ).pack(side="left", padx=12, pady=8)

        contenido, ancho = tarjeta(0, 0, "¿En qué consiste?")
        parrafo(
            contenido,
            "al paso de la corriente eléctrica al aplicar un "
            "voltaje de CD.",
            ancho, negrita="Es la oposición del aislamiento ",
        )
        parrafo(
            contenido,
            "Depende del tiempo y el voltaje. Se mide en Megaohms "
            "(MΩ). Aumenta con el espesor y disminuye si crece el área.",
            ancho,
        )

        contenido, ancho = tarjeta(0, 1, "¿Qué detecta?")
        parrafo(
            contenido,
            "Humedad junto con suciedad reducen la resistencia.",
            ancho,
        )
        parrafo(
            contenido,
            "Un cambio del 25% entre dos tensiones de prueba suele "
            "deberse a humedad o contaminantes.",
            ancho,
        )
        parrafo(
            contenido,
            "de las pruebas periódicas.",
            ancho, negrita="Se analiza la tendencia ",
        )

        contenido, ancho = tarjeta(
            1, 0, "Corrección por Temperatura", ancho=680, columnas=2,
        )
        caja_formula(contenido, "Rc = Kt × Rt")
        parrafo(
            contenido, "Resistencia corregida (MΩ).", ancho,
            negrita="Rc:  ",
        )
        parrafo(
            contenido, "Coeficiente de la Tabla 1.", ancho,
            negrita="Kt:  ",
        )
        parrafo(
            contenido,
            "Resistencia medida a la temperatura de prueba (MΩ).",
            ancho, negrita="Rt:  ",
        )
        parrafo(
            contenido,
            "* La base es a 20 °C. Hay columna para sumergido en "
            "aceite y columna para seco.",
            ancho, nota=True,
        )

        contenido, ancho = tarjeta(
            2, 0, "Ecuaciones y Límites", ancho=680, columnas=2,
        )
        columnas_ec = tk.Frame(contenido, bg="#FFFFFF")
        columnas_ec.pack(fill="x")
        columnas_ec.columnconfigure(0, weight=1)
        columnas_ec.columnconfigure(1, weight=1)
        for columna_ec, (nombre, formula, aceptacion) in enumerate((
            (
                "Índice de Polarización (ip)",
                "ip = R 10 min / R 1 min",
                "ip ≥ 1.5",
            ),
            (
                "Índice de Absorción (ia)",
                "ia = R 1 min / R 30 s",
                "ia = 1.45 ± 25 %",
            ),
        )):
            celda = tk.Frame(columnas_ec, bg="#FFFFFF")
            celda.grid(
                row=0, column=columna_ec, sticky="nsew",
                padx=(0, 8) if columna_ec == 0 else (8, 0),
            )
            tk.Label(
                celda, text=nombre, bg="#FFFFFF", fg="#1E293B",
                font=("Segoe UI", 10, "bold"), anchor="w",
            ).pack(fill="x")
            caja_formula(celda, formula)
            fila_a = tk.Frame(celda, bg="#FFFFFF")
            fila_a.pack(fill="x")
            tk.Label(
                fila_a, text="Aceptación: ", bg="#FFFFFF",
                fg="#334155", font=("Segoe UI", 9),
            ).pack(side="left")
            tk.Label(
                fila_a, text=aceptacion, bg="#FFFFFF", fg="#1E293B",
                font=("Segoe UI", 9, "bold"),
            ).pack(side="left")

        alerta = tk.Frame(cuerpo, bg="#FFFBEB")
        alerta.pack(fill="x", padx=8, pady=8)
        acento_a = tk.Frame(alerta, bg="#F59E0B", width=4)
        acento_a.pack(side="left", fill="y")
        acento_a.pack_propagate(False)
        texto_alerta = tk.Frame(alerta, bg="#FFFBEB")
        texto_alerta.pack(side="left", fill="x", expand=True, padx=12, pady=10)
        tk.Label(
            texto_alerta, text="Recomendación importante:",
            bg="#FFFBEB", fg="#92400E", font=("Segoe UI", 10, "bold"),
            anchor="w",
        ).pack(fill="x")
        tk.Label(
            texto_alerta,
            text=(
                "No es recomendable usar el ia en transformadores "
                "sumergidos en aceite. Ese índice describe "
                "aislamientos sólidos dentro de un campo eléctrico, "
                "y no aplica igual en un aislamiento líquido."
            ),
            bg="#FFFBEB", fg="#92400E", font=("Segoe UI", 10),
            anchor="w", justify="left", wraplength=680,
        ).pack(fill="x")

        contenido, ancho = tarjeta(
            3, 0, "Alcance del Procedimiento", ancho=680, columnas=2,
        )
        parrafo(
            contenido,
            "Transformadores y reactores de potencia, "
            "autotransformadores, máquinas rotatorias, "
            "transformadores de instrumento y apartarrayos.",
            ancho,
        )

        tk.Frame(visor, bg="#E2E8F0", height=1).pack(fill="x")
        pie = tk.Frame(visor, bg="#FFFFFF")
        pie.pack(fill="x")
        ctk.CTkButton(
            pie, text="Cerrar", fg_color="#10B981",
            hover_color="#059669", text_color="white",
            font=ctk.CTkFont(size=12, weight="bold"),
            width=110, height=36, command=visor.destroy,
        ).pack(side="right", padx=30, pady=12)
        visor.focus_force()
        return visor
    def _nota_criterio_ra(self, prueba):
        """Criterio que se aplica antes de calcular el dictamen."""
        temp = self._numero_ra(self.datos_prueba["temp_devanado"].get())
        base = self._base_temp_ra()
        en_aceite = self._en_aceite_ra()
        if temp is None:
            kt_txt = (
                f"Corrección automática a {base:g} °C: Rc = Rt × Kt. "
                "Falta la temperatura del devanado para calcular Kt."
            )
        else:
            kt = self._kt_equipo_ra(temp, en_aceite)
            origen = (
                "IEEE 43, base 40 °C" if base == 40.0
                else f"{'aceite' if en_aceite else 'seco'}, Tabla 1"
            )
            kt_txt = (
                f"Corrección automática a {base:g} °C: Rc = Rt × Kt. "
                f"Kt = {kt:.3f} ({origen})."
            )
        if prueba.get("minutos") == 10:
            return (
                kt_txt
                + "  DAR (ia) = R1 min / R30 s.  IP = R10 min / R1 min.  "
                + "IEEE Std 43: IP ≥ 2.0 satisfactorio.  "
                + "Procedimiento: IP ≥ 1.5; entre 1.5 y 2.0 se investiga."
            )
        return kt_txt + f"  La lectura de 1 min se corrige a {base:g} °C antes del dictamen."

    def _exportar_reporte_ra(self, padre=None):
        """Reporte técnico para imprimir o guardar como PDF desde el navegador."""
        resultado = self._resultado_dictamen_ra()
        if resultado is None:
            return
        datos = self.datos_prueba
        r30 = self._lectura_mohm_ra(datos["lectura_30s"].get())
        r1 = self._lectura_mohm_ra(datos["lectura_1min"].get())
        r10 = self._lectura_mohm_ra(datos["lectura_10min"].get())
        prueba = resultado["prueba"] or {}
        ruta = filedialog.asksaveasfilename(
            parent=padre or self.winfo_toplevel(),
            title="Guardar reporte técnico",
            defaultextension=".html",
            filetypes=(("Reporte HTML", "*.html"), ("Todos", "*.*")),
            initialfile="reporte_resistencia_aislamiento.html",
        )
        if not ruta:
            return
        colores = {
            "ACEPTADO": "#007A33",
            "INVESTIGAR": "#B45309",
            "RECHAZADO": "#B91C1C",
        }
        color = colores.get(resultado["estado"], "#334155")

        def esc(texto):
            return (
                str(texto)
                .replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
            )

        def punto(rotulo, valor, unidad="M"):
            if valor is None:
                return f"<tr><td>{rotulo}</td><td>sin lectura</td></tr>"
            return (
                f"<tr><td>{rotulo}</td><td>"
                f"{esc(self._fmt_mohm_ra(valor, unidad))}</td></tr>"
            )

        ia = f"{r1 / r30:.2f}" if r30 and r1 else "No aplica"
        ip = f"{r10 / r1:.2f}" if r1 and r10 else "No aplica"
        ambiente = resultado["ambiente"]
        hr = resultado["hr"]
        lineas = "".join(f"<li>{esc(linea)}</li>" for linea in resultado["lineas"])
        html = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<title>Reporte de resistencia de aislamiento</title>
<style>
  body {{ font-family: Segoe UI, sans-serif; color: #1E293B; margin: 32px; }}
  h1 {{ font-size: 22px; margin-bottom: 0; }}
  .estado {{ display: inline-block; color: white; background: {color};
             padding: 6px 14px; font-weight: 700; margin: 12px 0; }}
  table {{ border-collapse: collapse; margin: 8px 0 18px; }}
  td {{ border: 1px solid #CBD5E1; padding: 6px 12px; }}
  td:first-child {{ background: #F8FAFC; font-weight: 600; }}
  .firma {{ margin-top: 36px; }}
  .linea {{ margin-top: 28px; }}
</style>
</head>
<body>
<h1>S.A.P.E. · Resistencia de aislamiento</h1>
<p>Fecha: {esc(datetime.now().strftime("%d/%m/%Y %H:%M"))}</p>
<p class="estado">{esc(self._rotulo_estado(resultado["estado"]))}</p>
<table>
<tr><td>Equipo</td><td>{esc(resultado["equipo"])}</td></tr>
<tr><td>Fase</td><td>{esc(datos["fase"].get() or "—")}</td></tr>
<tr><td>Configuración</td><td>{esc(datos["configuracion"].get() or "—")}</td></tr>
<tr><td>Aislamiento</td><td>{esc(resultado["aislamiento"])}</td></tr>
<tr><td>Líquido refrigerante</td><td>{esc((datos["liquido"].get() if self._en_aceite_ra() else "") or "—")}</td></tr>
<tr><td>Prueba</td><td>Prueba {esc(prueba.get("prueba", "—"))} · {esc(prueba.get("medicion", "—"))}</td></tr>
<tr><td>Ambiente</td><td>{esc(f"{ambiente:g} °C" if ambiente is not None else "sin registrar")}</td></tr>
<tr><td>Humedad relativa</td><td>{esc(f"{hr:g} %" if hr is not None else "sin registrar")}</td></tr>
<tr><td>Devanado</td><td>{esc(f"{resultado['temp']:g} °C")}</td></tr>
<tr><td>Kt a 20 °C</td><td>{resultado["kt"]:.3f} (Tabla 1)</td></tr>
<tr><td>DAR (ia)</td><td>{esc(ia)}</td></tr>
<tr><td>IP</td><td>{esc(ip)}</td></tr>
</table>
<h2>Puntos de absorción</h2>
<table>
{punto("30 s", r30, self._unidad_lectura_ra(datos["lectura_30s"].get()))}
{punto("1 min", r1, self._unidad_lectura_ra(datos["lectura_1min"].get()))}
{punto("10 min", r10, self._unidad_lectura_ra(datos["lectura_10min"].get()))}
</table>
<h2>Dictamen</h2>
<ul>{lineas}</ul>
<div class="firma">
<p class="linea">Realizó: ________________________________</p>
<p class="linea">Revisó: _________________________________</p>
</div>
</body>
</html>
"""
        try:
            Path(ruta).write_text(html, encoding="utf-8")
        except OSError as error:
            messagebox.showerror(
                "Reporte",
                f"No se pudo guardar el reporte.\n{error}",
                parent=padre or self.winfo_toplevel(),
            )
            return
        messagebox.showinfo(
            "Reporte",
            "Reporte guardado. Ábrelo en el navegador y usa Imprimir para sacarlo en PDF.",
            parent=padre or self.winfo_toplevel(),
        )

    def _clave_prueba_anexo_a(self, prueba):
        datos = self.datos_prueba
        return "|".join((
            datos["tipo_equipo"].get().strip(),
            datos["fase"].get().strip(),
            str(prueba.get("prueba", "")),
            str(prueba.get("medicion", "")),
            str(prueba.get("linea", "")),
            str(prueba.get("tierra", "")),
            str(prueba.get("guarda", "")),
        ))

    def _lectura_guardada_anexo_a(self, prueba):
        if not prueba:
            return {}
        guardada = self._lecturas_anexo_a.get(
            self._clave_prueba_anexo_a(prueba), {},
        )
        return guardada if isinstance(guardada, dict) else {}

    def _guardar_lectura_anexo_a(self, padre=None):
        padre = padre or self.winfo_toplevel()
        prueba = self.prueba_seleccionada
        if not prueba:
            messagebox.showwarning(
                "Anexo A",
                "Selecciona la prueba antes de guardar.",
                parent=padre,
            )
            return
        datos = self.datos_prueba
        lecturas = {}
        for rotulo, clave in (
            ("30 s", "lectura_30s"),
            ("1 min", "lectura_1min"),
            ("10 min", "lectura_10min"),
        ):
            texto = datos[clave].get().strip()
            if texto:
                lecturas[rotulo] = texto
        if not lecturas:
            messagebox.showwarning(
                "Anexo A",
                "Escribe al menos una lectura para guardarla.",
                parent=padre,
            )
            return
        self._lecturas_anexo_a[self._clave_prueba_anexo_a(prueba)] = lecturas
        if not _guardar_lecturas_anexo_a_archivo(self._lecturas_anexo_a):
            messagebox.showerror(
                "Anexo A",
                "No se pudieron guardar las lecturas.",
                parent=padre,
            )
            return
        messagebox.showinfo(
            "Anexo A",
            "Lecturas guardadas en la prueba "
            f"{prueba.get('prueba', '—')} · {prueba.get('medicion', '—')} "
            "del Anexo A.",
            parent=padre,
        )

    def _guardar_en_historial(self, origen, padre=None):
        padre = padre or self.winfo_toplevel()
        resultado = self._resultado_dictamen_ra()
        if resultado is None:
            return
        datos = self.datos_prueba
        r30 = self._lectura_mohm_ra(datos["lectura_30s"].get())
        r1 = self._lectura_mohm_ra(datos["lectura_1min"].get())
        r10 = self._lectura_mohm_ra(datos["lectura_10min"].get())
        lecturas = {}
        for rotulo, clave in (
            ("30 s", "lectura_30s"), ("1 min", "lectura_1min"),
            ("10 min", "lectura_10min"),
        ):
            texto = datos[clave].get().strip()
            if texto:
                lecturas[rotulo] = texto
        prueba = resultado["prueba"] or {}
        registro = {
            "fecha": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "modulo": "Resistencia de Aislamiento",
            "origen": origen,
            "equipo": resultado["equipo"],
            "fase": datos["fase"].get(),
            "prueba": (
                f"Prueba {prueba.get('prueba', '—')} · "
                f"{prueba.get('medicion', '—')} "
                f"(L={prueba.get('linea', '—')} "
                f"T={prueba.get('tierra', '—')} "
                f"G={prueba.get('guarda', '—')})"
            ),
            "lecturas": lecturas,
            "ia": f"{r1 / r30:.2f}" if r30 and r1 else None,
            "ip": f"{r10 / r1:.2f}" if r1 and r10 else None,
            "kt": f"{resultado['kt']:.3f}",
            "liquido": datos["liquido"].get().strip(),
            "estado": resultado["estado"],
            "descripcion": resultado["descripcion"],
        }
        if _agregar_historial(registro):
            messagebox.showinfo(
                "Historial de Análisis",
                "Análisis guardado. Lo encuentras en la opción "
                "7. Historial de Análisis del menú principal.",
                parent=padre,
            )
        else:
            messagebox.showerror(
                "Historial de Análisis",
                "No se pudo guardar el análisis en el historial.",
                parent=padre,
            )

    def mostrar_historial(self, padre=None):
        visor = tk.Toplevel(padre or self)
        visor.title("Historial de Análisis")
        visor.configure(bg="#F4F6F8")
        visor.geometry("900x640")
        visor.minsize(760, 480)
        if padre is not None:
            visor.transient(padre)
        barra = tk.Frame(visor, bg="#1E293B")
        barra.pack(fill="x")
        tk.Label(
            barra, text="Historial de Análisis", bg="#1E293B",
            fg="#FFFFFF", font=("Segoe UI", 15, "bold"),
        ).pack(side="left", padx=20, pady=14)
        tk.Label(
            barra, text="Opción 7 · S.A.P.E.", bg="#1E293B",
            fg="#94A3B8", font=("Segoe UI", 9),
        ).pack(side="right", padx=20)
        contenido = ctk.CTkScrollableFrame(visor, fg_color="#F4F6F8")
        contenido.pack(fill="both", expand=True, padx=14, pady=14)
        pie = tk.Frame(visor, bg="#F4F6F8")
        pie.pack(fill="x", padx=14, pady=(0, 14))

        paleta = {
            "ACEPTADO": ("#D1FAE5", "#065F46"),
            "INVESTIGAR": ("#FEF3C7", "#92400E"),
            "RECHAZADO": ("#FEE2E2", "#991B1B"),
        }

        def pintar():
            for hijo in contenido.winfo_children():
                hijo.destroy()
            registros = _cargar_historial()
            if not registros:
                tk.Label(
                    contenido,
                    text=(
                        "Todavía no hay análisis guardados.\n"
                        "Usa el botón GUARDAR en el Dictamen Técnico "
                        "(paso 4) o en el Anexo A."
                    ),
                    bg="#F4F6F8", fg="#64748B",
                    font=("Segoe UI", 11), justify="center",
                ).pack(pady=40)
                return
            for registro in registros:
                tarjeta = tk.Frame(
                    contenido, bg="#FFFFFF",
                    highlightbackground="#E2E8F0", highlightthickness=1,
                )
                tarjeta.pack(fill="x", pady=(0, 10))
                fila_top = tk.Frame(tarjeta, bg="#FFFFFF")
                fila_top.pack(fill="x", padx=14, pady=(10, 2))
                fondo_e, tinta_e = paleta.get(
                    registro.get("estado", ""),
                    ("#F1F5F9", "#334155"),
                )
                tk.Label(
                    fila_top,
                    text=f"  {self._rotulo_estado(registro.get('estado', ''))}  ",
                    bg=fondo_e, fg=tinta_e,
                    font=("Segoe UI", 9, "bold"), padx=6, pady=2,
                ).pack(side="left")
                tk.Label(
                    fila_top,
                    text=(
                        f"{registro.get('modulo', '')} · "
                        f"{registro.get('origen', '')}"
                    ),
                    bg="#FFFFFF", fg="#64748B", font=("Segoe UI", 9),
                ).pack(side="left", padx=(10, 0))
                tk.Label(
                    fila_top, text=registro.get("fecha", ""),
                    bg="#FFFFFF", fg="#94A3B8", font=("Segoe UI", 9),
                ).pack(side="right")
                tk.Label(
                    tarjeta,
                    text=(
                        f"{registro.get('equipo', '')} · "
                        f"Fase {registro.get('fase', '—')}"
                    ),
                    bg="#FFFFFF", fg="#1E293B",
                    font=("Segoe UI", 11, "bold"), anchor="w",
                ).pack(fill="x", padx=14)
                tk.Label(
                    tarjeta, text=registro.get("prueba", ""),
                    bg="#FFFFFF", fg="#475569", font=("Segoe UI", 9),
                    anchor="w",
                ).pack(fill="x", padx=14)
                detalles = []
                lecturas = registro.get("lecturas") or {}
                if lecturas:
                    detalles.append(
                        "Lecturas: " + ", ".join(
                            f"{k} = {v}" for k, v in lecturas.items()
                        )
                    )
                if registro.get("ia"):
                    detalles.append(f"ia = {registro['ia']}")
                if registro.get("ip"):
                    detalles.append(f"ip = {registro['ip']}")
                if registro.get("fp"):
                    detalles.append(f"%FP = {registro['fp']}")
                if registro.get("fp20"):
                    detalles.append(f"%FP a 20 °C = {registro['fp20']}")
                if registro.get("kt"):
                    detalles.append(f"Kt = {registro['kt']}")
                if detalles:
                    tk.Label(
                        tarjeta, text="   ·   ".join(detalles),
                        bg="#FFFFFF", fg="#334155",
                        font=("Segoe UI", 9, "bold"), anchor="w",
                    ).pack(fill="x", padx=14, pady=(2, 0))
                tk.Label(
                    tarjeta, text=registro.get("descripcion", ""),
                    bg="#FFFFFF", fg="#64748B", font=("Segoe UI", 9),
                    anchor="w", justify="left", wraplength=820,
                ).pack(fill="x", padx=14, pady=(2, 10))

        def borrar():
            if not _cargar_historial():
                return
            if messagebox.askyesno(
                "Historial de Análisis",
                "¿Borrar todo el historial de análisis?",
                parent=visor,
            ):
                try:
                    RUTA_HISTORIAL.write_text("[]", encoding="utf-8")
                except OSError:
                    pass
                pintar()

        ctk.CTkButton(
            pie, text="ACTUALIZAR", fg_color="#3B82F6",
            hover_color="#2563EB", text_color="white",
            font=ctk.CTkFont(weight="bold"), width=130,
            command=pintar,
        ).pack(side="left")
        ctk.CTkButton(
            pie, text="BORRAR HISTORIAL", fg_color="#EF4444",
            hover_color="#DC2626", text_color="white",
            font=ctk.CTkFont(weight="bold"), width=170,
            command=borrar,
        ).pack(side="left", padx=12)
        ctk.CTkButton(
            pie, text="CERRAR", fg_color="#64748B",
            hover_color="#475569", text_color="white",
            font=ctk.CTkFont(weight="bold"), width=110,
            command=visor.destroy,
        ).pack(side="right")
        pintar()
        visor.focus_force()
        return visor

    def mostrar_modos_prueba_aislamiento(self, padre):
        visor = tk.Toplevel(padre)
        visor.title("Guía de Modos de Prueba")
        visor.configure(bg="#FFFFFF")
        visor.geometry("680x760")
        visor.minsize(600, 520)
        visor.transient(padre)

        encabezado = tk.Frame(visor, bg="#FFFFFF")
        encabezado.pack(fill="x")
        titulo_m = tk.Frame(encabezado, bg="#FFFFFF")
        titulo_m.pack(side="left", padx=20, pady=12)
        tk.Label(
            titulo_m, text="ℹ", bg="#FFFFFF", fg="#3B82F6",
            font=("Segoe UI Symbol", 14),
        ).pack(side="left")
        tk.Label(
            titulo_m, text="Guía de Modos de Prueba", bg="#FFFFFF",
            fg="#1E293B", font=("Segoe UI", 12, "bold"),
        ).pack(side="left", padx=(10, 0))
        etiqueta_cerrar = tk.Label(
            encabezado, text="✕", bg="#FFFFFF", fg="#94A3B8",
            font=("Segoe UI", 13, "bold"), cursor="hand2",
        )
        etiqueta_cerrar.pack(side="right", padx=16)
        etiqueta_cerrar.bind("<Button-1>", lambda _e=None: visor.destroy())
        etiqueta_cerrar.bind(
            "<Enter>", lambda _e=None: etiqueta_cerrar.config(fg="#EF4444"),
        )
        etiqueta_cerrar.bind(
            "<Leave>", lambda _e=None: etiqueta_cerrar.config(fg="#94A3B8"),
        )
        tk.Frame(visor, bg="#F1F5F9", height=1).pack(fill="x")

        cuerpo = ctk.CTkScrollableFrame(visor, fg_color="#FFFFFF")
        cuerpo.pack(fill="both", expand=True, padx=10, pady=8)
        tk.Label(
            cuerpo, text="TIPOS DE PRUEBAS (NORMA ST-CT-001)",
            bg="#FFFFFF", fg="#64748B", font=("Segoe UI", 9, "bold"),
            anchor="w",
        ).pack(fill="x", padx=12, pady=(6, 12))

        def tarjeta(insignia, fondo_ins, color_ins, titulo):
            tarjeta_f = tk.Frame(
                cuerpo, bg="#F8FAFC",
                highlightbackground="#E2E8F0", highlightthickness=1,
            )
            tarjeta_f.pack(fill="x", padx=12, pady=(0, 14))
            cabecera = tk.Frame(tarjeta_f, bg="#F8FAFC")
            cabecera.pack(fill="x", padx=14, pady=(12, 8))
            tk.Label(
                cabecera, text=insignia, bg=fondo_ins, fg=color_ins,
                font=("Segoe UI", 8, "bold"), padx=8, pady=3,
            ).pack(side="left")
            tk.Label(
                cabecera, text=titulo, bg="#F8FAFC", fg="#1E293B",
                font=("Segoe UI", 11, "bold"),
            ).pack(side="left", padx=(10, 0))
            tk.Frame(tarjeta_f, bg="#E2E8F0", height=1).pack(
                fill="x", padx=14,
            )
            contenido = tk.Frame(tarjeta_f, bg="#F8FAFC")
            contenido.pack(fill="x", padx=14, pady=(8, 12))
            return contenido

        def vineta(contenido, negrita, texto):
            fila = tk.Frame(contenido, bg="#F8FAFC")
            fila.pack(fill="x", pady=4)
            tk.Label(
                fila, text="•", bg="#F8FAFC", fg="#334155",
                font=("Segoe UI", 11, "bold"),
            ).pack(side="left", anchor="n")
            tk.Label(
                fila, text=f"  {negrita}", bg="#F8FAFC", fg="#0F172A",
                font=("Segoe UI", 10, "bold"),
            ).pack(side="left", anchor="n")
            tk.Label(
                fila, text=texto, bg="#F8FAFC", fg="#334155",
                font=("Segoe UI", 10), anchor="w", justify="left",
                wraplength=360,
            ).pack(side="left", fill="x", expand=True)

        def caja_formula(contenido, texto):
            caja = tk.Frame(
                contenido, bg="#FFFFFF",
                highlightbackground="#CBD5E1", highlightthickness=1,
            )
            caja.pack(anchor="w", padx=(16, 0), pady=5)
            tk.Label(
                caja, text=texto, bg="#FFFFFF", fg="#0F172A",
                font=("Consolas", 10), anchor="w",
            ).pack(padx=12, pady=7)

        def bloque_calculo(contenido, titulo, formula, nota=None):
            tk.Label(
                contenido, text=f"•  {titulo}", bg="#F8FAFC",
                fg="#0F172A", font=("Segoe UI", 10, "bold"), anchor="w",
            ).pack(fill="x", pady=(8, 0))
            caja_formula(contenido, formula)
            if nota:
                tk.Label(
                    contenido, text=nota, bg="#F8FAFC", fg="#64748B",
                    font=("Segoe UI", 8, "italic"), anchor="w",
                ).pack(fill="x", padx=(16, 0))

        contenido = tarjeta(
            "1 MINUTO", "#DBEAFE", "#1E40AF",
            "Prueba IR (Insulation Resistance)",
        )
        vineta(
            contenido, "Aplica para:",
            " TCs, TPs, TPCs, Apartarrayos, Interruptores y "
            "Cables cortos.",
        )
        vineta(
            contenido, "Voltaje:",
            " Primario (2,500 V) / Secundario (500 V).",
        )
        vineta(
            contenido, "Criterio:",
            " Se evalúa contra la Tabla 5. No requiere índices "
            "(ia ni ip).",
        )

        contenido = tarjeta(
            "10 MINUTOS", "#FEF3C7", "#92400E",
            "Pruebas DAR e IP / IRT",
        )
        vineta(
            contenido, "Aplica para:",
            " Transformadores de potencia, autotransformadores, "
            "reactores y generadores.",
        )
        vineta(
            contenido, "Toma de datos:",
            " 30 seg, 1 min, y luego cada minuto hasta el minuto 10.",
        )
        bloque_calculo(
            contenido,
            "Cálculo DAR (Índice de Absorción):",
            "ia = R 1 min / R 30 seg  →  Aceptación: 1.45 ± 25%",
            "* No concluyente en equipos sumergidos en aceite.",
        )
        bloque_calculo(
            contenido,
            "Cálculo IP / IRT (Índice de Polarización):",
            "ip = R 10 min / R 1 min  →  Aceptación: ip ≥ 1.5",
        )

        nota = tk.Frame(cuerpo, bg="#EFF6FF")
        nota.pack(fill="x", padx=12, pady=(2, 10))
        acento_n = tk.Frame(nota, bg="#3B82F6", width=4)
        acento_n.pack(side="left", fill="y")
        acento_n.pack_propagate(False)
        texto_nota = tk.Text(
            nota, bg="#EFF6FF", fg="#1E3A8A", font=("Segoe UI", 9),
            wrap="word", height=3, bd=0, highlightthickness=0,
        )
        texto_nota.pack(side="left", fill="x", expand=True, padx=12, pady=10)
        texto_nota.tag_configure(
            "negrita", font=("Segoe UI", 9, "bold"),
            foreground="#1E3A8A",
        )
        texto_nota.insert(
            "1.0",
            "Al seleccionar un modo, el sistema ajustará "
            "automáticamente las tablas de captura, los voltajes y "
            "los cálculos de corrección a 20°C según el "
            "procedimiento ",
        )
        texto_nota.insert("end", "SOM-3531", "negrita")
        texto_nota.insert("end", ".")
        texto_nota.configure(state="disabled")

        tk.Frame(visor, bg="#F1F5F9", height=1).pack(fill="x")
        pie = tk.Frame(visor, bg="#F8FAFC")
        pie.pack(fill="x")
        ctk.CTkButton(
            pie, text="Entendido", fg_color="#3B82F6",
            hover_color="#2563EB", text_color="white",
            font=ctk.CTkFont(size=12, weight="bold"),
            width=110, height=34, command=visor.destroy,
        ).pack(side="right", padx=20, pady=12)
        visor.deiconify()
        visor.lift()
        visor.focus_force()
        return visor

    def abrir_prueba_ttr(self):
        """Relación de transformación (ST-CT-007). Morado en todo el módulo."""
        ctk.set_appearance_mode("Light")
        ventana = tk.Toplevel(self)
        ventana.title(
            "[ S. A. P. E. ]  Sistema de Análisis de Pruebas Eléctricas"
        )
        ventana.iconbitmap(str(APP_ICON_PATH))
        ventana.geometry("1200x800")
        ventana.minsize(1000, 600)
        ventana.configure(bg="#F8FAFC")
        equipos = (
            "Transformadores de 2 Devanados",
            "Transformadores de 3 Devanados",
            "Autotransformadores",
            "Reactores",
        )
        self.datos_ttr = {
            "tipo_equipo": tk.StringVar(
                ventana, value="Transformadores de 2 Devanados",
            ),
            "configuracion": tk.StringVar(ventana, value="Trifásico"),
            "fase": tk.StringVar(ventana, value="A"),
            "conexion": tk.StringVar(ventana, value="Estrella - Delta"),
            "voltaje_h": tk.StringVar(ventana),
            "voltaje_x": tk.StringVar(ventana),
            "voltaje_y": tk.StringVar(ventana),
            "regulacion_cfe": tk.StringVar(ventana, value="Sí"),
            "tipo_cambiador": tk.StringVar(ventana, value="Sin carga [ 5 TAPs ]"),
            "temp_ambiente": tk.StringVar(ventana),
            "humedad": tk.StringVar(ventana),
            "temp_devanado": tk.StringVar(ventana),
            "medicion_realizar": tk.StringVar(ventana, value="Directa"),
            "polaridad": tk.StringVar(ventana, value="Sustractiva"),
            "tap": tk.StringVar(ventana, value="3"),
            "relacion_teorica_manual": tk.StringVar(ventana),
            "relacion_medida": tk.StringVar(ventana),
        }
        self.prueba_ttr = None
        self._parpadeo_ttr = None

        barra_superior = tk.Frame(ventana, bg="#12161A", height=50)
        barra_superior.pack(side="top", fill="x")
        barra_superior.pack_propagate(False)

        def logo_neon(
            texto="[ S.A.P.E. ]", fondo=(5, 5, 5), marco=True, tam=16,
        ):
            from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageTk
            fuente = ImageFont.truetype(r"C:\Windows\Fonts\consolab.ttf", tam)
            sonda = ImageDraw.Draw(Image.new("RGB", (1, 1)))
            caja = sonda.textbbox((0, 0), texto, font=fuente)
            ancho = caja[2] - caja[0] + 22
            alto = caja[3] - caja[1] + 14
            imagen = Image.new("RGB", (ancho, alto), fondo)
            halo = Image.new("RGB", (ancho, alto), fondo)
            xy = (11 - caja[0], 7 - caja[1])
            ImageDraw.Draw(halo).text(xy, texto, font=fuente, fill=(0, 255, 255))
            halo = halo.filter(ImageFilter.GaussianBlur(3 * tam / 16))
            imagen = Image.blend(imagen, halo, 0.9)
            dibujo = ImageDraw.Draw(imagen)
            dibujo.text(xy, texto, font=fuente, fill=(0, 255, 255))
            if marco:
                dibujo.rounded_rectangle(
                    (0, 0, ancho - 1, alto - 1), radius=4, outline=(42, 49, 58),
                )
            return ImageTk.PhotoImage(imagen)

        foto_logo = logo_neon("ST-CT-007")
        ventana._logo_sape = foto_logo
        tk.Label(
            barra_superior, image=foto_logo, bg="#12161A", bd=0,
        ).pack(side="left", padx=(16, 8))
        tk.Label(
            barra_superior,
            text=(
                "PROCEDIMIENTO PARA LA MEDICIÓN DE RELACIÓN DE\n"
                "TRANSFORMACIÓN (TTR)"
            ),
            bg="#12161A", fg="#A0AEC0",
            font=("Segoe UI", 8, "bold"), justify="left",
        ).pack(side="left", padx=(8, 0))
        reloj = tk.Label(
            barra_superior, text="", bg="#12161A",
            fg="#A0AEC0", font=("Consolas", 11, "bold"),
        )
        reloj.pack(side="right", padx=(0, 16))
        tk.Label(
            barra_superior, text="RELACIÓN H-X · H-Y · X-Y",
            bg="#12161A", fg="#A0AEC0",
            font=("Segoe UI", 9, "bold"),
        ).pack(side="right")
        tk.Label(
            barra_superior, text="●",
            bg="#12161A", fg="#00FF00",
            font=("Segoe UI", 8),
        ).pack(side="right", padx=(0, 6))

        def marcar_reloj_ttr():
            try:
                if not ventana.winfo_exists():
                    return
            except tk.TclError:
                return
            reloj.config(text=datetime.now().strftime("%H:%M:%S"))
            ventana._reloj_ttr = ventana.after(1000, marcar_reloj_ttr)

        marcar_reloj_ttr()

        panel_lateral = ctk.CTkFrame(
            ventana, width=320, corner_radius=0, fg_color="#000000",
        )
        panel_lateral.pack(side=tk.LEFT, fill=tk.Y)
        panel_lateral.pack_propagate(False)
        logo_caja = tk.Frame(
            panel_lateral, bg="#12161A",
            highlightbackground="#3B4553", highlightthickness=1,
        )
        logo_caja.pack(fill="x", padx=16, pady=(16, 0))
        foto_sape_lateral = logo_neon(
            fondo=(18, 22, 26), marco=False, tam=32,
        )
        ventana._logo_sape_lateral = foto_sape_lateral
        tk.Label(
            logo_caja, image=foto_sape_lateral, bg="#12161A", bd=0,
        ).pack(pady=8)
        ctk.CTkLabel(
            panel_lateral, text="RELACIÓN DE TRANSFORMACIÓN (TTR)",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color="#A78BFA", wraplength=280, justify="center",
        ).pack(pady=(8, 14))

        pie_lateral = tk.Frame(
            panel_lateral, bg="#1C2128",
            highlightbackground="#1F2937", highlightthickness=1,
        )
        pie_lateral.pack(side="bottom", fill="x")
        for rotulo, valor, color, relleno in (
            ("ESTADO NORMA:", "ST-CT-007 Rev. 1", TTR_MORADO_CLARO, (10, 2)),
            ("UNIDAD DE DIAG:", "ACTIVA", TTR_MORADO_CLARO, (0, 10)),
        ):
            fila_pie = tk.Frame(pie_lateral, bg="#1C2128")
            fila_pie.pack(fill="x", padx=14, pady=relleno)
            tk.Label(
                fila_pie, text=rotulo, bg="#1C2128",
                fg="#9CA3AF", font=("Consolas", 9),
            ).pack(side="left")
            tk.Label(
                fila_pie, text=valor, bg="#1C2128",
                fg=color, font=("Consolas", 9, "bold"),
            ).pack(side="right")

        area_principal = tk.Frame(ventana, bg=RA_VISTA_FONDO)
        area_principal.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        marco_scroll = tk.Frame(area_principal, bg=RA_VISTA_FONDO)
        marco_scroll.pack(fill=tk.BOTH, expand=True)
        barra_y_main = tk.Scrollbar(marco_scroll, orient="vertical")
        barra_x_main = tk.Scrollbar(marco_scroll, orient="horizontal")
        puerto_main = tk.Canvas(
            marco_scroll, bg=RA_VISTA_FONDO, highlightthickness=0, bd=0,
            yscrollcommand=barra_y_main.set,
            xscrollcommand=barra_x_main.set,
        )
        barra_y_main.configure(command=puerto_main.yview)
        barra_x_main.configure(command=puerto_main.xview)
        barra_x_main.pack(side="bottom", fill="x")
        barra_y_main.pack(side="right", fill="y")
        puerto_main.pack(side="left", fill="both", expand=True)
        contenedor = tk.Frame(
            puerto_main, bg=RA_VISTA_FONDO, bd=0, highlightthickness=0,
        )
        ventana_contenido = puerto_main.create_window(
            (0, 0), window=contenedor, anchor="nw",
        )

        def ajustar_contenido_ttr(_evento=None):
            if getattr(ajustar_contenido_ttr, "_ocupado", False):
                return
            ajustar_contenido_ttr._ocupado = True
            try:
                if not puerto_main.winfo_exists():
                    return
                req_w = max(contenedor.winfo_reqwidth(), 1)
                req_h = max(contenedor.winfo_reqheight(), 1)
                ancho = max(puerto_main.winfo_width(), req_w)
                alto = max(puerto_main.winfo_height(), req_h)
                puerto_main.itemconfigure(
                    ventana_contenido, width=ancho, height=alto,
                )
                puerto_main.configure(scrollregion=(0, 0, ancho, alto))
            except tk.TclError:
                return
            finally:
                ajustar_contenido_ttr._ocupado = False

        contenedor.bind("<Configure>", ajustar_contenido_ttr)
        puerto_main.bind("<Configure>", ajustar_contenido_ttr)
        contenedor._puerto_ttr = puerto_main

        def al_rueda_principal_ttr(evento):
            if not getattr(evento, "delta", 0):
                return
            try:
                x, y = ventana.winfo_pointerxy()
                destino = ventana.winfo_containing(x, y)
            except (tk.TclError, KeyError):
                return
            if destino is not None and destino.winfo_class() == "Text":
                return
            lienzo = None
            dentro = False
            while destino is not None:
                propio = getattr(destino, "_scroll_propio", None)
                if propio is not None:
                    lienzo = propio
                    break
                if destino is marco_scroll:
                    dentro = True
                    break
                destino = getattr(destino, "master", None)
            if lienzo is None and not dentro:
                return
            objetivo = lienzo or puerto_main
            pasos = int(-evento.delta / 120) or (
                -1 if evento.delta < 0 else 1
            )
            try:
                if evento.state & 0x1:
                    objetivo.xview_scroll(pasos, "units")
                else:
                    objetivo.yview_scroll(pasos, "units")
            except tk.TclError:
                return
            return "break"

        ventana.bind_all("<MouseWheel>", al_rueda_principal_ttr)

        def soltar_rueda_principal_ttr(_evento):
            if _evento.widget is not ventana:
                return
            try:
                ventana.unbind_all("<MouseWheel>")
            except tk.TclError:
                pass

        ventana.bind("<Destroy>", soltar_rueda_principal_ttr)

        paso_actual = tk.IntVar(ventana, value=1)
        botones_paso = []
        fondo_lateral = "#000000"

        def titulo_seccion(texto):
            fila = tk.Frame(panel_lateral, bg=fondo_lateral)
            fila.pack(fill="x", padx=25, pady=(16, 10))
            tk.Label(
                fila, text=texto, bg=fondo_lateral, fg=TTR_PLATA,
                font=("Segoe UI", 10, "bold"),
            ).pack(side="left")
            tk.Frame(fila, bg="#334155", height=1).pack(
                side="left", fill="x", expand=True, padx=(10, 0),
            )

        def crear_boton_paso(numero, texto):
            boton = _boton_menu_ra(
                panel_lateral, texto,
                lambda n=numero: self._cargar_paso_ttr(
                    n, paso_actual, contenedor, botones_paso,
                ),
                marca=f"{numero:02d}", tema="morado", fondo=fondo_lateral,
            )
            botones_paso.append(boton)
            return boton

        titulo_seccion("PROCESO DE PRUEBA")
        crear_boton_paso(1, "DATOS DEL EQUIPO")
        crear_boton_paso(2, "SELECCIÓN DE PRUEBAS")
        crear_boton_paso(3, "DIAGRAMA VECTORIAL")
        crear_boton_paso(4, "CAPTURA DE LECTURAS")
        tk.Frame(panel_lateral, bg="#334155", height=1).pack(
            fill="x", padx=25, pady=(14, 2),
        )
        titulo_seccion("RECURSOS")
        _boton_menu_ra(
            panel_lateral, "MODOS DE PRUEBA",
            lambda: self.mostrar_modos_ttr(ventana),
            tema="morado_recurso", fondo=fondo_lateral,
        )
        _boton_menu_ra(
            panel_lateral, "FORMATOS",
            lambda: self.mostrar_anexo_a_ttr(ventana),
            tema="neon_morado", marca="A", fondo=fondo_lateral,
        )
        _boton_menu_ra(
            panel_lateral, "OPERACIÓN",
            lambda: self.mostrar_anexo_b_ttr(ventana),
            tema="neon_morado", marca="B", fondo=fondo_lateral,
        )
        _boton_menu_ra(
            panel_lateral, "RESUMEN",
            lambda: self.mostrar_anexo_c_ttr(ventana),
            tema="neon_morado", marca="C", fondo=fondo_lateral,
        )

        self._cargar_paso_ttr(1, paso_actual, contenedor, botones_paso)
        ventana.focus_force()
        return ventana

    def _visor_guia_ttr(self, padre, titulo, secciones):
        visor = tk.Toplevel(padre)
        visor.title(titulo)
        visor.configure(bg="#FFFFFF")
        visor.geometry("720x700")
        visor.minsize(620, 520)
        visor.transient(padre)
        encabezado = tk.Frame(visor, bg="#FFFFFF")
        encabezado.pack(fill="x")
        tk.Label(
            encabezado, text=titulo, bg="#FFFFFF", fg="#1E293B",
            font=("Segoe UI", 14, "bold"),
        ).pack(side="left", padx=20, pady=14)
        cerrar = tk.Label(
            encabezado, text="✕", bg="#FFFFFF", fg="#94A3B8",
            font=("Segoe UI", 13, "bold"), cursor="hand2",
        )
        cerrar.pack(side="right", padx=16)
        cerrar.bind("<Button-1>", lambda _e=None: visor.destroy())
        tk.Frame(visor, bg="#E9D5FF", height=2).pack(fill="x")
        cuerpo = ctk.CTkScrollableFrame(visor, fg_color="#FFFFFF")
        cuerpo.pack(fill="both", expand=True, padx=12, pady=10)
        tk.Label(
            cuerpo, text="ST-CT-007  ·  Relación de transformación",
            bg="#FFFFFF", fg=TTR_MORADO, font=("Segoe UI", 9, "bold"),
            anchor="w",
        ).pack(fill="x", padx=8, pady=(4, 12))
        for encabezado_sec, parrafos in secciones:
            tk.Label(
                cuerpo, text=encabezado_sec, bg="#FFFFFF", fg="#1E293B",
                font=("Segoe UI", 12, "bold"), anchor="w",
            ).pack(fill="x", padx=8, pady=(8, 4))
            for parrafo in parrafos:
                tk.Label(
                    cuerpo, text=parrafo, bg="#F8FAFC", fg="#334155",
                    font=("Segoe UI", 10), anchor="w", justify="left",
                    wraplength=640, padx=12, pady=8,
                ).pack(fill="x", padx=8, pady=(0, 8))
        visor.focus_force()
        return visor

    def mostrar_modos_ttr(self, padre):
        self._visor_guia_ttr(padre, "Modos de prueba", (
            ("TTR manual James G. Biddle", (
                "Opera con dos transformadores en paralelo. Incluye generador manual de corriente alterna, transformador de referencia ajustable de 0 a 130, selectores S1, S2, S3 y R4, galvanómetro de cero central, voltmetro de excitación y ampermetro de magnetización.",
                "Antes de medir se comprueba el balance, la relación cero y la relación unitaria.",
            )),
            ("Vanguard ATRT-01, ATRT-01B y ATRT-01D", (
                "Equipo digital con pantalla LCD, teclado, conector de alto y bajo voltaje, alimentación 120/240 V y, en el ATRT-01, interfaz RS-232.",
                "Sirve para transformadores monofásicos y trifásicos. Si se capturan los voltajes nominales, muestra el porcentaje de diferencia (%DIFF).",
            )),
            ("Three-Phase TTR Biddle, marca AVO", (
                "Medición trifásica. El procedimiento cubre monofásicos de dos devanados, trifásicos de dos devanados y trifásicos de tres devanados.",
                "Nunca se intercambian las terminales de alto y bajo voltaje: una conexión invertida puede dañar el equipo o el transformador.",
            )),
        ))

    def mostrar_anexo_a_ttr(self, padre):
        """Formato del Anexo A de TTR (ST-CT-007): datos, tabla por tap y firmas."""
        visor = tk.Toplevel(padre)
        visor.title("ANEXO A  Formatos de Prueba — Relación de Transformación")
        visor.configure(bg="#F4F6F8")
        visor.geometry("1180x800")
        visor.minsize(980, 640)
        visor.transient(padre)
        barra_sup = tk.Frame(visor, bg="#1E293B")
        barra_sup.pack(fill="x")
        tk.Label(
            barra_sup, text="Formatos de Prueba - Anexo A",
            bg="#1E293B", fg="#FFFFFF", font=("Segoe UI", 15, "bold"),
        ).pack(side="left", padx=20, pady=14)
        contenido = ctk.CTkScrollableFrame(visor, fg_color="#FFFFFF")
        contenido.pack(fill="both", expand=True, padx=18, pady=18)

        datos = self.datos_ttr
        equipo = datos["tipo_equipo"].get().strip()
        configuracion = datos["configuracion"].get()
        conexion = datos["conexion"].get()
        guardado = _cargar_anexo_ttr().get(equipo, {})
        campos_guardados = guardado.get("campos", {})
        taps_guardados = guardado.get("taps", {})
        prueba = self.prueba_ttr
        n_taps, centro = _taps_ttr(datos["tipo_cambiador"].get())
        mantener = _mantener_nominal_ttr(datos["tipo_cambiador"].get())
        usar_reg = datos["regulacion_cfe"].get() == "Sí"
        nominal = _relacion_nominal_ttr(datos, prueba, equipo, conexion)[0] if prueba else None
        scratch = {}

        def var(clave, inicial=None):
            if clave not in scratch:
                valor = campos_guardados.get(clave, "") if inicial is None else inicial
                scratch[clave] = tk.StringVar(visor, value=valor)
            return scratch[clave]

        def grupo(padre_g, texto, variable, fila, columna):
            marco = tk.Frame(padre_g, bg="#FFFFFF")
            marco.grid(row=fila, column=columna, sticky="ew", padx=8, pady=5)
            tk.Label(
                marco, text=texto, bg="#FFFFFF", fg="#64748B",
                font=("Segoe UI", 9, "bold"), anchor="w",
            ).pack(fill="x", pady=(0, 4))
            ctk.CTkEntry(marco, textvariable=variable, height=30).pack(fill="x")

        def grupo_combo(padre_g, texto, variable, valores, fila, columna):
            marco = tk.Frame(padre_g, bg="#FFFFFF")
            marco.grid(row=fila, column=columna, sticky="ew", padx=8, pady=5)
            tk.Label(
                marco, text=texto, bg="#FFFFFF", fg="#64748B",
                font=("Segoe UI", 9, "bold"), anchor="w",
            ).pack(fill="x", pady=(0, 4))
            ctk.CTkComboBox(
                marco, variable=variable, values=list(valores),
                state="readonly", height=30,
                button_color=TTR_MORADO_OSCURO,
                button_hover_color=TTR_MORADO_HOVER,
            ).pack(fill="x")

        def rejilla(columnas_n):
            marco = tk.Frame(contenido, bg="#FFFFFF")
            marco.pack(fill="x", pady=(4, 12))
            for c in range(columnas_n):
                marco.grid_columnconfigure(c, weight=1)
            return marco

        def subtitulo(texto):
            tk.Label(
                contenido, text=texto, bg="#FFFFFF", fg="#1E293B",
                font=("Segoe UI", 10, "bold"), anchor="w",
            ).pack(fill="x", padx=15, pady=(12, 2))

        marco_logo = tk.Frame(contenido, bg="#FFFFFF", height=100)
        marco_logo.pack(fill="x", padx=15, pady=(14, 2))
        marco_logo.pack_propagate(False)
        # Verde oficial CFE: Pantone 136-16 C (#008E60), igual que en RA y FP.
        tk.Label(
            marco_logo, text=CFE_ASCII, bg="#FFFFFF", fg="#00573F",
            font=("Consolas", 10, "bold"), anchor="nw", justify="left",
        ).place(x=2, y=2)
        tk.Label(
            marco_logo, text=CFE_ASCII, bg="#FFFFFF", fg="#008E60",
            font=("Consolas", 10, "bold"), anchor="nw", justify="left",
        ).place(x=0, y=0)
        foto_sape = _imagen_sape_ascii(tam=9, fondo="#FFFFFF", color="#1E293B")
        etiqueta_sape = ctk.CTkLabel(
            marco_logo, text="", image=foto_sape, fg_color="#FFFFFF",
        )
        etiqueta_sape._foto_sape = foto_sape
        etiqueta_sape.place(relx=1.0, x=-2, y=0, anchor="ne")
        fila_titulo = tk.Frame(contenido, bg="#FFFFFF")
        fila_titulo.pack(fill="x", padx=15, pady=(2, 10))
        tk.Label(
            fila_titulo, text="ST-CT-007", bg=TTR_VISTA_PASTEL,
            fg=TTR_MORADO_OSCURO, font=("Consolas", 12, "bold"), padx=10, pady=3,
        ).pack(side="left")
        tk.Label(
            fila_titulo,
            text=f"Relación de Transformación — {equipo or 'Equipo sin elegir'}",
            bg="#FFFFFF", fg="#1E293B", font=("Segoe UI", 14, "bold"), anchor="w",
        ).pack(side="left", padx=(12, 0))

        subtitulo("DATOS DE IDENTIFICACIÓN")
        rej = rejilla(4)
        for indice, (clave, texto) in enumerate((
            ("gerencia", "Gerencia Regional de Transmisión"), ("subarea", "Zona"),
            ("nomenclatura", "Nomenclatura"), ("subestacion", "Subestación"),
            ("marca", "Marca"), ("modelo", "Modelo / Tipo"),
            ("serie", "No. de Serie"), ("fabricacion", "Año de Fabricación"),
            ("servicio", "Año Puesta en Servicio"),
        )):
            grupo(rej, texto, var(clave), indice // 4, indice % 4)

        subtitulo("ORDEN DE TRABAJO")
        rej = rejilla(4)
        for indice, (clave, texto) in enumerate((
            ("ot", "O.T."), ("fecha", "Fecha"), ("programado", "Programado"),
            ("falla", "Falla"), ("rim", "RIM"), ("rig", "RIG"),
            ("licencia", "No. Licencia"), ("registro", "Número de registro"),
        )):
            grupo(rej, texto, var(clave), indice // 4, indice % 4)

        subtitulo("DATOS DEL EQUIPO")
        rej = rejilla(4)
        for indice, (clave, texto) in enumerate((
            ("mva", "MVA"), ("clase_enf", "Clase de enfriamiento"),
            ("taps", "# Taps"), ("kv_at", "kV nom. A.T."),
            ("kv_bt", "kV nom. B.T."), ("kv_terc", "kV nom. Terciario"),
            ("z", "% Z"),
        )):
            grupo(rej, texto, var(clave), indice // 4, indice % 4)
        for columna, (clave, texto) in enumerate((
            ("con_at", "Tipo de conexión A.T."), ("con_bt", "Tipo de conexión B.T."),
            ("con_te", "Tipo de conexión Terciario"),
        )):
            grupo_combo(rej, texto, var(clave, campos_guardados.get(clave, "Y")), ("Y", "Δ"), 2, columna)

        subtitulo("CONDICIONES: PRUEBA & CLIMATOLÓGICA")
        rej = rejilla(4)
        grupo(rej, "Temp. Ambiente (°C)", datos["temp_ambiente"], 0, 0)
        grupo(rej, "% Hum. Relativa", datos["humedad"], 0, 1)
        grupo(rej, "Temp. Devanado (°C)", datos["temp_devanado"], 0, 2)
        grupo_combo(
            rej, "Clima", var("clima"),
            ("Soleado", "Nublado", "1/2 nublado", "Brisa", "Lluvia"), 1, 0,
        )

        subtitulo("EQUIPO DE MEDICIÓN UTILIZADO")
        rej = rejilla(4)
        for indice, (clave, texto) in enumerate((
            ("inst_marca", "Marca"), ("inst_modelo", "Modelo"),
            ("inst_serie", "Núm. Serie"), ("inst_eimp", "No. Inv. EIMP"),
            ("inst_cal", "Fecha de Calibración"),
        )):
            grupo(rej, texto, var(clave), indice // 4, indice % 4)

        # El diagrama no depende de que se haya elegido una prueba: si no hay, usa la primera.
        clave_vector = _clave_vector_ttr(equipo, configuracion, conexion) if equipo else None
        lista_vector = _filas_ttr(equipo, configuracion, conexion)[0] if clave_vector else []
        prueba_vector = prueba or (lista_vector[0] if lista_vector else None)
        clave_vector = clave_vector if prueba_vector else None
        if clave_vector:
            subtitulo("DIAGRAMA VECTORIAL")
            _margen, _paso, ancho = _medida_vector_ttr(len(_VECTORES_TTR[clave_vector][3]))
            lienzo_vec = tk.Canvas(
                contenido, width=ancho, height=280, bg="#FFFFFF", highlightthickness=0,
            )
            lienzo_vec.pack(anchor="w", padx=15, pady=(2, 8))
            _dibujar_vector_ttr(lienzo_vec, clave_vector, prueba_vector, "mide", anexo=True)

        subtitulo("TABLA POR TAP  ·  RELACIÓN TEÓRICA, PUESTA EN SERVICIO Y MEDIDA")
        if nominal is None:
            tk.Label(
                contenido,
                text="Falta el kV de placa en el paso 01 para la relación teórica.",
                bg="#FFFFFF", fg="#B45309", font=("Segoe UI", 9, "bold"), anchor="w",
            ).pack(fill="x", padx=15)
        tabla = tk.Frame(contenido, bg="#E2E8F0")
        tabla.pack(fill="x", padx=15, pady=(2, 8))
        for c, texto in enumerate(("TAP", "RT TEÓRICA", "RP.S.", "RM", "DIF %", "DICTAMEN")):
            tabla.grid_columnconfigure(c, weight=1)
            tk.Label(
                tabla, text=texto, bg="#F1F5F9", fg="#475569",
                font=("Segoe UI", 8, "bold"), anchor="w", padx=6, pady=8,
            ).grid(row=0, column=c, sticky="nsew", pady=(0, 1))

        def actualizar_tap(t):
            rt = None if nominal is None else _relacion_teorica_tap_ttr(
                nominal, t, centro, usar_reg, mantener,
            )
            rm = _leer_ttr(scratch[f"rm_{t}"].get())
            res = _evaluar_ttr(rt, rm)
            etiquetas[t]["rt"].configure(text="—" if rt is None else f"{rt:.4f}")
            etiquetas[t]["dif"].configure(text="—" if res is None else f"{res['dif']:.3f} %")
            if res is None:
                etiquetas[t]["estado"].configure(text="—", fg="#94A3B8")
            else:
                color = "#059669" if res["estado"] == "ACEPTADO" else "#D97706"
                etiquetas[t]["estado"].configure(text=res["estado"], fg=color)

        etiquetas = {}
        for t in range(1, n_taps + 1):
            guardado_tap = taps_guardados.get(str(t), {})
            var(f"ps_{t}", guardado_tap.get("ps", ""))
            var(f"rm_{t}", guardado_tap.get("rm", ""))
            fondo = "#FEF3C7" if t == centro else "#FFFFFF"
            etiquetas[t] = {}
            tk.Label(
                tabla, text=f"Tap {t}" + (" (central)" if t == centro else ""),
                bg=fondo, fg="#1E293B", font=("Segoe UI", 9, "bold"), anchor="w", padx=6,
            ).grid(row=t, column=0, sticky="nsew", pady=(0, 1))
            etiquetas[t]["rt"] = tk.Label(
                tabla, text="—", bg=fondo, fg="#334155", font=("Consolas", 9), anchor="w", padx=6,
            )
            etiquetas[t]["rt"].grid(row=t, column=1, sticky="nsew", pady=(0, 1))
            for columna, clave in ((2, f"ps_{t}"), (3, f"rm_{t}")):
                celda = tk.Frame(tabla, bg=fondo)
                celda.grid(row=t, column=columna, sticky="nsew", padx=4, pady=2)
                entrada = ctk.CTkEntry(celda, textvariable=scratch[clave], height=28)
                entrada.pack(fill="x")
            scratch[f"rm_{t}"].trace_add("write", lambda *_a, t=t: actualizar_tap(t))
            etiquetas[t]["dif"] = tk.Label(
                tabla, text="—", bg=fondo, fg="#334155", font=("Consolas", 9), anchor="w", padx=6,
            )
            etiquetas[t]["dif"].grid(row=t, column=4, sticky="nsew", pady=(0, 1))
            etiquetas[t]["estado"] = tk.Label(
                tabla, text="—", bg=fondo, fg="#94A3B8", font=("Segoe UI", 9, "bold"),
                anchor="w", padx=6,
            )
            etiquetas[t]["estado"].grid(row=t, column=5, sticky="nsew", pady=(0, 1))
            actualizar_tap(t)
        tk.Label(
            contenido,
            text=(
                "RT = kV de placa con 0.625 % por tap (los taps nominales del cambiador "
                "de 23 taps dan la misma RT). Dif % = 100 × (RT − RM) / RT; "
                "ST-CT-007 acepta hasta 0.5 % en la primera medición."
            ),
            bg="#FFFFFF", fg="#64748B", font=("Segoe UI", 9, "italic"),
            anchor="w", justify="left", wraplength=1040,
        ).pack(fill="x", padx=15, pady=(2, 8))

        subtitulo("OBSERVACIONES Y FIRMAS")
        rej_obs = rejilla(1)
        grupo(rej_obs, "Observaciones", var("observaciones"), 0, 0)
        rej = rejilla(3)
        grupo(rej, "Realizó — Nombre y firma", var("realizo"), 0, 0)
        grupo(rej, "Revisó — Nombre y firma", var("reviso"), 0, 1)
        grupo(rej, "Aprobó — Nombre y firma", var("aprobo"), 0, 2)

        def guardar():
            if not equipo:
                messagebox.showinfo(
                    "Anexo A", "Elija el equipo en el paso 01 antes de guardar.",
                    parent=visor,
                )
                return
            campos = {
                clave: valor.get() for clave, valor in scratch.items()
                if not clave.startswith(("ps_", "rm_"))
            }
            taps = {
                str(t): {"ps": scratch[f"ps_{t}"].get(), "rm": scratch[f"rm_{t}"].get()}
                for t in range(1, n_taps + 1)
            }
            registros = _cargar_anexo_ttr()
            registros[equipo] = {"campos": campos, "taps": taps}
            if not _guardar_anexo_ttr_archivo(registros):
                messagebox.showerror(
                    "Anexo A", "No se pudo guardar el Anexo A de TTR.", parent=visor,
                )
                return
            messagebox.showinfo("Anexo A", "Anexo A de TTR guardado.", parent=visor)

        for texto_boton, comando in (
            ("GUARDAR", guardar),
            (
                "IMPRIMIR",
                lambda: _imprimir_formato_carta(
                    contenido, "Anexo A — Relación de Transformación (TTR)",
                ),
            ),
        ):
            ctk.CTkButton(
                barra_sup, text=texto_boton, fg_color=TTR_MORADO,
                hover_color=TTR_MORADO_OSCURO, text_color="white",
                font=ctk.CTkFont(weight="bold"), width=110, height=34,
                command=comando,
            ).pack(side="right", padx=(12, 24), pady=10)
        visor.focus_force()
        return visor

    def mostrar_anexo_b_ttr(self, padre):
        self._visor_guia_ttr(padre, "Anexo B: Operación", (
            ("TTR manual", (
                "Comprobar balance, relación cero y relación unitaria antes de conectar el equipo bajo prueba.",
                "La polaridad es sustractiva cuando las marcas coinciden, y aditiva cuando la indicación queda a la derecha.",
                "La relación se lee en los selectores después del balance. Si la relación es mayor de 130 se usa un transformador auxiliar o un segundo TTR.",
            )),
            ("Vanguard ATRT", (
                "Conectar alto y bajo voltaje según el modelo. Para ver %DIFF hay que ingresar los voltajes nominales durante la configuración.",
                "En trifásicos se sigue el orden de fases del procedimiento y se confirma el diagrama vectorial antes de conectar un tercer devanado.",
            )),
            ("Precaución", (
                "No intercambiar las terminales de alto y bajo voltaje. Las terminales H0 y X0 que no se usen deben mantenerse alejadas de tierra y del personal, porque pueden energizarse durante la medición.",
            )),
        ))

    def mostrar_anexo_c_ttr(self, padre):
        self._visor_guia_ttr(padre, "Anexo C: Resumen", (
            ("En qué consiste", (
                "Obtiene el número de vueltas de los devanados, la relación entre voltajes primario y secundario, o la relación entre sus corrientes.",
                "a = Vp / Vs    y    a = Is / Ip.",
            )),
            ("Qué detecta", (
                "Terminales, derivaciones y conexiones internas. Polaridad y continuidad. Espiras en corto circuito. Problemas de corrientes circulantes y reparto de carga en transformadores en paralelo.",
            )),
            ("Criterio", (
                "En la primera medición, al entregar el transformador, la diferencia no debe ser mayor de 0.5%.",
                "%DIF = 100 × (RT − RM) / RT, donde RT es la relación teórica y RM la medida.",
                "Con más de dos devanados se hacen mediciones monofásicas y antes hay que interpretar el diagrama vectorial. La fase central puede medir un poco más alta que las fases 1 y 3.",
            )),
        ))

    # ── Pasos 01 a 04, mismo formato que RA y FP ────────────────────────

    def _cargar_paso_ttr(self, numero, paso_actual, contenedor, botones_paso):
        ventana = contenedor.winfo_toplevel()
        job = getattr(self, "_parpadeo_ttr", None)
        if job is not None:
            try:
                self.after_cancel(job)
            except tk.TclError:
                pass
            self._parpadeo_ttr = None
        if numero in (3, 4) and not self.prueba_ttr:
            messagebox.showinfo(
                "Prueba no disponible",
                "Seleccione una prueba disponible en el paso 2 antes "
                "de abrir el diagrama vectorial y la captura.",
                parent=ventana,
            )
            return
        paso_actual.set(numero)
        for indice, boton in enumerate(botones_paso, start=1):
            boton["aplicar"](indice == numero)
        for hijo in contenedor.winfo_children():
            hijo.destroy()
        fondo = RA_VISTA_FONDO
        frame = tk.Frame(contenedor, bg=fondo)
        frame.pack(fill=tk.BOTH, expand=True)
        cuerpo = tk.Frame(frame, bg=fondo)
        cuerpo.pack(
            expand=True, fill="both", padx=28,
            pady=(12, 8) if numero == 3 else 18,
        )
        self._titulos_ttr(cuerpo, numero)

        def ir(destino):
            self._cargar_paso_ttr(
                destino, paso_actual, contenedor, botones_paso,
            )

        if numero == 1:
            self._formulario_ttr(cuerpo, ir)
        elif numero == 2:
            self._tabla_ttr(cuerpo)
            self._pie_paso_ttr(cuerpo, 2, lambda: ir(3))
        elif numero == 3:
            self._vectores_ttr(cuerpo)
            self._pie_paso_ttr(cuerpo, 3, lambda: ir(4))
        else:
            self._captura_ttr(cuerpo)
        puerto = getattr(contenedor, "_puerto_ttr", None)
        if puerto is not None:
            puerto.yview_moveto(0)

    def _titulos_ttr(self, padre, numero):
        fondo = RA_VISTA_FONDO
        titulos = {
            1: "DATOS DEL EQUIPO",
            2: "SELECCIÓN DE PRUEBAS",
            3: "DIAGRAMA VECTORIAL",
            4: "CAPTURA DE LECTURAS",
        }
        subtitulos = {
            1: "Parámetros de placa y condiciones ambientales del transformador bajo prueba.",
            2: "Elija la prueba y revise sus terminales de conexión.",
            3: "Diagrama vectorial y conexiones del equipo de medición.",
            4: "Captura de lecturas y dictamen de la prueba.",
        }
        bloque = tk.Frame(padre, bg=fondo)
        bloque.pack(fill="x", pady=(0, 8 if numero >= 3 else 16))
        fila = tk.Frame(bloque, bg=fondo)
        fila.pack(fill="x")
        izquierda = tk.Frame(fila, bg=fondo)
        izquierda.pack(side="left", fill="x", expand=True)
        fila_titulo = tk.Frame(izquierda, bg=fondo)
        fila_titulo.pack(anchor="w")
        tk.Label(
            fila_titulo, text="Relación de Transformación",
            bg=fondo, fg="#1A202C",
            font=("Segoe UI", 26, "bold"),
        ).pack(side="left")
        pastilla = ctk.CTkFrame(
            fila_titulo, fg_color=TTR_VISTA_PASTEL, corner_radius=12,
            border_width=1, border_color=TTR_VISTA_PASTEL_BORDE,
        )
        pastilla.pack(side="left", padx=(12, 0))
        ctk.CTkLabel(
            pastilla, text="Modo Diagnóstico",
            text_color=TTR_MORADO_OSCURO, fg_color="transparent",
            font=ctk.CTkFont(family="Consolas", size=11, weight="bold"),
        ).pack(padx=10, pady=2)
        equipo_actual = self.datos_ttr["tipo_equipo"].get().strip()
        tk.Label(
            izquierda, text=subtitulos[numero],
            bg=fondo, fg="#596573",
            font=("Segoe UI", 10), anchor="w",
        ).pack(anchor="w", pady=(4, 0))
        if numero != 1 and equipo_actual:
            tk.Label(
                izquierda, text=equipo_actual,
                bg=fondo, fg="#334155",
                font=("Segoe UI", 18, "bold"), anchor="w",
            ).pack(anchor="w", pady=(2, 0))
        insignia = ctk.CTkFrame(
            fila, fg_color=TTR_MORADO, corner_radius=10,
        )
        insignia.pack(side="right", anchor="n")
        ctk.CTkLabel(
            insignia, text=f"{numero:02d}",
            text_color="#F5F3FF", fg_color=TTR_MORADO_OSCURO,
            corner_radius=6,
            font=ctk.CTkFont(family="Consolas", size=20, weight="bold"),
        ).pack(side="left", padx=(10, 8), pady=8)
        ctk.CTkLabel(
            insignia, text=titulos[numero],
            text_color="#FFFFFF", fg_color="transparent",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
        ).pack(side="left", padx=(0, 14), pady=8)
        _barra_degradada_ttr(bloque, fondo, pady=(12, 0))

    def _pie_paso_ttr(self, padre, numero, comando):
        """Botón SIGUIENTE y leyenda del módulo, como en RA y FP."""
        fondo = RA_VISTA_FONDO
        gris = "#596573"
        tk.Frame(padre, bg=RA_VISTA_BORDE, height=1).pack(
            fill="x", pady=(4, 6),
        )
        # El botón va justo debajo del contenido, para que quede a la vista al maximizar.
        fila_acciones = tk.Frame(padre, bg=fondo)
        fila_acciones.pack(fill="x", pady=(10, 6))
        boton = _boton_relieve_ra(
            fila_acciones, "SIGUIENTE  →", comando, modo="morado",
        )
        boton.pack(side="right")
        tk.Label(
            padre,
            text="Ingeniería de pruebas de alta tensión  ·  Subestaciones eléctricas",
            bg=fondo, fg=gris, font=("Consolas", 9),
        ).pack(anchor="w", pady=(4, 0))
        tk.Label(
            padre, text=f"Módulo {numero:02d} / 04",
            bg=fondo, fg="#4A5568", font=("Consolas", 9, "bold"),
        ).pack(anchor="e", padx=(0, 4), pady=(0, 6))

        def activar(_evento=None):
            boton.invoke()
            return "break"

        boton.bind("<Return>", activar, add="+")
        boton.bind("<KP_Enter>", activar, add="+")
        boton.bind("<FocusIn>", lambda _e=None: boton.marcar(True), add="+")
        boton.bind("<FocusOut>", lambda _e=None: boton.marcar(False), add="+")
        return boton

    def _montar_correccion_ttr(self, padre):
        """Panel de relación teórica y semáforo del dictamen, como el de FP."""
        datos = self.datos_ttr
        panel = tk.Frame(padre, bg=RA_VISTA_PANEL)
        panel.pack(fill="x")
        fila_rt = tk.Frame(panel, bg=RA_VISTA_PANEL)
        fila_rt.pack(fill="x", padx=16, pady=(14, 8))
        tk.Label(
            fila_rt, text="CORRECCIÓN ST-CT-007", bg=RA_VISTA_PANEL,
            fg=TTR_MORADO_CLARO, font=("Consolas", 10, "bold"),
        ).pack(side="left")
        ref_tap = tk.Label(
            fila_rt, text="Ref: —", bg="#1F2937", fg="#9CA3AF",
            font=("Consolas", 9),
        )
        ref_tap.pack(side="right")
        tk.Frame(panel, bg="#374151", height=1).pack(fill="x", padx=16)
        cuerpo_rt = tk.Frame(panel, bg=RA_VISTA_PANEL)
        cuerpo_rt.pack(fill="x", padx=16, pady=(12, 8))
        tk.Label(
            cuerpo_rt, text="Relación Teórica  RT:",
            bg=RA_VISTA_PANEL, fg="#D1D5DB", font=("Segoe UI", 10),
        ).pack(side="left")
        valor_rt = tk.Label(
            cuerpo_rt, text="—", bg=RA_VISTA_PANEL, fg=TTR_MORADO_CLARO,
            font=("Consolas", 28, "bold"),
        )
        valor_rt.pack(side="right")
        caja = tk.Frame(panel, bg="#111827")
        caja.pack(fill="x", padx=16, pady=(0, 8))
        filas_caja = {}
        for clave, rotulo, relleno in (
            ("ecuacion", "Ecuación usada:", (8, 2)),
            ("tap", "Tap seleccionado:", (2, 2)),
            ("rm", "Relación medida (RM):", (2, 8)),
        ):
            fila = tk.Frame(caja, bg="#111827")
            fila.pack(fill="x", padx=10, pady=relleno)
            tk.Label(
                fila, text=rotulo, bg="#111827", fg="#9CA3AF",
                font=("Consolas", 9),
            ).pack(side="left")
            valor = tk.Label(
                fila, text="—", bg="#111827", fg="#E5E7EB",
                font=("Consolas", 9, "bold"), wraplength=200, justify="right",
            )
            valor.pack(side="right")
            filas_caja[clave] = valor
        filas_caja["ecuacion"].configure(
            text="%DIF = (RT − RM) / RT × 100", fg="#E5E7EB",
        )
        tabla_taps = tk.Frame(caja, bg="#111827")
        tabla_taps.pack(fill="x", padx=10, pady=(0, 8))

        def mostrar_taps(nominal, n_taps, centro, usar_reg, mantener=0):
            """Lista la relación teórica de cada tap; el tap elegido va resaltado."""
            for hijo in tabla_taps.winfo_children():
                hijo.destroy()
            if nominal is None:
                return
            tap_sel = int(datos["tap"].get())
            tk.Label(
                tabla_taps, text="RT POR TAP", bg="#111827",
                fg=TTR_MORADO_CLARO, font=("Consolas", 9, "bold"),
            ).pack(anchor="w", pady=(2, 4))
            for t in range(1, n_taps + 1):
                rt_t = _relacion_teorica_tap_ttr(nominal, t, centro, usar_reg, mantener)
                sel = t == tap_sel
                color = "#FFFFFF" if sel else "#E5E7EB"
                estilo = "bold" if sel else "normal"
                fila = tk.Frame(tabla_taps, bg="#111827")
                fila.pack(fill="x")
                tk.Label(
                    fila, text=f"Tap {t}" + ("  ◄" if sel else ""),
                    bg="#111827", fg=color, font=("Consolas", 9, estilo),
                ).pack(side="left")
                tk.Label(
                    fila, text="—" if rt_t is None else f"{rt_t:.4f}",
                    bg="#111827", fg=color, font=("Consolas", 9, estilo),
                ).pack(side="right")

        aviso = tk.Label(
            panel, text="", bg="#1F2937", fg="#E5E7EB",
            font=("Segoe UI", 9), justify="left", anchor="nw", wraplength=300,
        )
        aviso.pack(fill="x", padx=16, pady=(0, 10))

        panel_estado = tk.Frame(panel, bg=RA_VISTA_PANEL)
        panel_estado.pack(fill="x", padx=16, pady=(4, 16))
        tk.Label(
            panel_estado, text="ESTADO DEL DICTAMEN",
            bg=RA_VISTA_PANEL, fg=TTR_MORADO_CLARO,
            font=("Consolas", 9, "bold"), anchor="w",
        ).pack(fill="x", pady=(0, 8))
        luces = tk.Frame(panel_estado, bg=RA_VISTA_PANEL, height=108)
        luces.pack(fill="x", pady=(0, 10))
        luces.pack_propagate(False)

        def foto_emoji(emoji):
            from PIL import Image, ImageDraw, ImageFont, ImageTk
            fuente = ImageFont.truetype(r"C:\Windows\Fonts\seguiemj.ttf", 52)
            sonda = ImageDraw.Draw(Image.new("RGBA", (4, 4)))
            caja_e = sonda.textbbox(
                (0, 0), emoji, font=fuente, embedded_color=True,
            )
            imagen = Image.new(
                "RGBA",
                (caja_e[2] - caja_e[0] + 4, caja_e[3] - caja_e[1] + 4),
                (0, 0, 0, 0),
            )
            ImageDraw.Draw(imagen).text(
                (2 - caja_e[0], 2 - caja_e[1]),
                emoji, font=fuente, embedded_color=True,
            )
            contenido = imagen.getbbox()
            if contenido:
                imagen = imagen.crop(contenido)
            foto = ImageTk.PhotoImage(imagen)
            vacio = tk.PhotoImage(width=foto.width(), height=foto.height())
            return foto, vacio

        focos = {}
        for indice, (clave, nombre, emoji) in enumerate((
            ("normal", "NORMAL", "✅"),
            ("precaucion", "PRECAUCIÓN", "⚠️"),
            ("alerta", "ALERTA", "❌"),
        )):
            luces.columnconfigure(indice, weight=1, uniform="focos")
            celda = tk.Frame(luces, bg="#1F2937", width=96, height=100)
            celda.grid(row=0, column=indice, sticky="nsew", padx=4)
            celda.grid_propagate(False)
            foto, vacio = foto_emoji(emoji)
            punto = tk.Label(celda, image=foto, bg="#1F2937", bd=0)
            punto.pack(pady=(10, 0))
            punto._foto = foto
            punto._vacio = vacio
            punto._emoji = emoji
            nombre_lbl = tk.Label(
                celda, text=nombre, bg="#1F2937", fg="#E5E7EB",
                font=("Segoe UI", 8, "bold"), height=1,
            )
            nombre_lbl.pack(pady=(4, 0))
            focos[clave] = (celda, punto, nombre_lbl)
        luces.rowconfigure(0, weight=1)
        datos_txt = tk.Text(
            panel_estado, bg=RA_VISTA_PANEL, fg="#E5E7EB",
            font=("Segoe UI", 9), wrap="word", height=2, width=40,
            bd=0, highlightthickness=0, padx=2, pady=2, cursor="arrow",
        )
        datos_txt.pack(fill="both", expand=True, pady=(0, 4))
        datos_txt.configure(state="disabled")
        self._focos_ieee = focos
        self._aviso_ieee = aviso
        self._datos_ieee = datos_txt
        self._nivel_foco_ieee = None

        def refrescar(_evento=None):
            equipo = datos["tipo_equipo"].get().strip()
            prueba = self.prueba_ttr
            conexion = datos["conexion"].get()
            usar_reg = datos["regulacion_cfe"].get() == "Sí"
            n_taps, centro = _taps_ttr(datos["tipo_cambiador"].get())
            mantener = _mantener_nominal_ttr(datos["tipo_cambiador"].get())
            ref_tap.configure(text=f"Ref: Tap {centro}")
            if not prueba:
                valor_rt.configure(text="—")
                filas_caja["tap"].configure(text="—")
                filas_caja["rm"].configure(text="—")
                aviso.configure(
                    bg="#1F2937", fg="#E5E7EB",
                    text="Elija una prueba en el paso 02.",
                )
                return
            nominal, _par = _relacion_nominal_ttr(datos, prueba, equipo, conexion)
            if datos["tap"].get() not in [str(t) for t in range(1, n_taps + 1)]:
                datos["tap"].set(str(centro))
            tap = int(datos["tap"].get())
            if nominal is not None:
                rt = _relacion_teorica_tap_ttr(nominal, tap, centro, usar_reg, mantener)
            else:
                rt = _leer_ttr(datos["relacion_teorica_manual"].get())
            rm = _leer_ttr(datos["relacion_medida"].get())
            valor_rt.configure(text="—" if rt is None else f"{rt:.4f}")
            filas_caja["tap"].configure(text=f"{tap} de {n_taps}")
            filas_caja["rm"].configure(text="—" if rm is None else f"{rm:.4f}")
            if rt is None:
                aviso.configure(
                    bg="#451A03", fg="#FDE68A",
                    text=(
                        "Falta el kV de placa para la relación teórica; "
                        "escríbala a mano en el paso 04."
                    ),
                )
            elif rm is None:
                aviso.configure(
                    bg="#451A03", fg="#FDE68A",
                    text="Falta la relación medida. Captúrela y pulse CALCULAR.",
                )
            else:
                aviso.configure(
                    bg="#052E16", fg="#BBF7D0",
                    text="Datos listos. Pulse CALCULAR.",
                )

        refrescar()
        refrescar.mostrar_taps = mostrar_taps
        return refrescar

    def _captura_ttr(self, frame):
        datos = self.datos_ttr
        equipo = datos["tipo_equipo"].get().strip()
        prueba = self.prueba_ttr
        if not prueba:
            ctk.CTkLabel(
                frame,
                text="Elija una prueba en el paso 02.",
                font=ctk.CTkFont(family="Segoe UI", size=14),
                text_color="#475569", fg_color="transparent",
            ).pack(anchor="w")
            return

        columna_rt = tk.Frame(frame, bg=RA_VISTA_PANEL, width=360)
        columna_rt.pack(side="right", fill="both", padx=(18, 0))
        tk.Frame(columna_rt, bg=RA_VISTA_PANEL, width=346, height=1).pack()
        refrescar_rt = self._montar_correccion_ttr(columna_rt)

        conexion = datos["conexion"].get()
        usar_reg = datos["regulacion_cfe"].get() == "Sí"
        n_taps, centro = _taps_ttr(datos["tipo_cambiador"].get())
        mantener = _mantener_nominal_ttr(datos["tipo_cambiador"].get())
        if datos["tap"].get() not in [str(t) for t in range(1, n_taps + 1)]:
            datos["tap"].set(str(centro))
        nominal, _par = _relacion_nominal_ttr(datos, prueba, equipo, conexion)

        fuente = ctk.CTkFont(family="Segoe UI", size=14, weight="bold")
        fuente_opcion = ctk.CTkFont(family="Segoe UI", size=14)
        formulario = tk.Frame(frame, bg=RA_VISTA_FONDO)
        formulario.pack(anchor="w", fill="x")

        tk.Label(
            formulario, text="Tap:", bg=RA_VISTA_FONDO, fg="#334155", font=fuente,
        ).grid(row=0, column=0, sticky="e", padx=(0, 20), pady=10)
        combo_tap = ctk.CTkComboBox(
            formulario, variable=datos["tap"],
            values=[str(t) for t in range(1, n_taps + 1)],
            state="readonly", width=120, font=fuente_opcion,
            dropdown_font=fuente_opcion,
            button_color=TTR_MORADO_OSCURO,
            button_hover_color=TTR_MORADO_HOVER,
        )
        combo_tap.grid(row=0, column=1, sticky="w", pady=10)
        tk.Label(
            formulario, text=f"(central: {centro})", bg=RA_VISTA_FONDO,
            fg="#94A3B8", font=fuente_opcion,
        ).grid(row=0, column=2, sticky="w", padx=(10, 0))

        # Relación medida de cada tap: se captura en todos los taps y luego se calcula.
        rm_taps = {str(datos["tap"].get()): datos["relacion_medida"].get()}
        datos["relacion_medida"].trace_add(
            "write",
            lambda *_a: rm_taps.__setitem__(
                str(datos["tap"].get()), datos["relacion_medida"].get(),
            ),
        )

        def rt_del_tap():
            """RT del tap elegido, calculada con los kV de placa del paso 01."""
            if nominal is None:
                return None
            tap = int(datos["tap"].get())
            return _relacion_teorica_tap_ttr(nominal, tap, centro, usar_reg, mantener)

        tk.Label(
            formulario, text="Relación teórica nominal (kV de placa):",
            bg=RA_VISTA_FONDO, fg="#334155", font=fuente,
        ).grid(row=1, column=0, sticky="e", padx=(0, 20), pady=10)
        tk.Label(
            formulario,
            text="—" if nominal is None else f"{nominal:.4f}",
            bg=RA_VISTA_FONDO, fg=TTR_MORADO_OSCURO, font=fuente,
        ).grid(row=1, column=1, sticky="w", pady=10)

        tk.Label(
            formulario,
            text=(
                "Relación teórica en este tap (0.625 %/paso):" if usar_reg
                else "Relación teórica (sin regulación):"
            ),
            bg=RA_VISTA_FONDO, fg="#334155", font=fuente,
        ).grid(row=2, column=0, sticky="e", padx=(0, 20), pady=10)
        etiqueta_rt_valor = tk.Label(
            formulario, text="—", bg=RA_VISTA_FONDO, fg=TTR_MORADO_OSCURO,
            font=fuente,
        )
        etiqueta_rt_valor.grid(row=2, column=1, sticky="w", pady=10)

        def obtener_rt(*_a):
            datos["relacion_medida"].set(rm_taps.get(str(datos["tap"].get()), ""))
            rt = rt_del_tap()
            etiqueta_rt_valor.configure(
                text="—" if rt is None else f"{rt:.4f}",
            )
            refrescar_rt()
            refrescar_rt.mostrar_taps(nominal, n_taps, centro, usar_reg, mantener)

        combo_tap.configure(command=lambda _v=None: obtener_rt())
        fila_botones_ttr = tk.Frame(frame, bg=RA_VISTA_FONDO)
        _boton_relieve_ra(
            fila_botones_ttr, "OBTENER RELACIÓN TEÓRICA", obtener_rt,
            ancho=270, modo="diagnostico_morado", fondo=RA_VISTA_FONDO,
            alto_caja=28, alto_lienzo=40, fuente_nombre="Consolas",
        ).pack(side="left", padx=(0, 12))

        if nominal is None:
            tk.Label(
                formulario, text="Relación teórica manual:",
                bg=RA_VISTA_FONDO, fg="#334155", font=fuente,
            ).grid(row=3, column=0, sticky="e", padx=(0, 20), pady=10)
            ctk.CTkEntry(
                formulario, textvariable=datos["relacion_teorica_manual"],
                width=140, font=fuente_opcion,
            ).grid(row=3, column=1, sticky="w", pady=10)

        tk.Label(
            formulario, text="Relación medida (TTR):", bg=RA_VISTA_FONDO,
            fg="#334155", font=fuente,
        ).grid(row=4, column=0, sticky="e", padx=(0, 20), pady=10)
        entrada_rm = ctk.CTkEntry(
            formulario, textvariable=datos["relacion_medida"],
            width=140, font=fuente_opcion,
        )
        entrada_rm.grid(row=4, column=1, sticky="w", pady=10)
        if nominal is None:
            tk.Label(
                formulario,
                text="Falta el kV de placa de este devanado en el paso 01; "
                     "escriba la relación teórica a mano.",
                bg="#FEF3C7", fg="#92400E", font=fuente_opcion,
                wraplength=420, justify="left", padx=10, pady=6,
            ).grid(row=5, column=0, columnspan=3, sticky="w", pady=(0, 10))

        tk.Label(
            frame,
            text=(
                "%DIF = 100 × (RT − RM) / RT. ST-CT-007 acepta hasta 0.5 % "
                "en la primera medición."
            ),
            bg=RA_VISTA_FONDO, fg="#64748B", font=fuente_opcion, wraplength=600,
            justify="left",
        ).pack(anchor="w", pady=(4, 14))

        tabla_taps_frame = tk.Frame(frame, bg=RA_VISTA_FONDO)
        tabla_taps_frame.pack(anchor="w", fill="x")

        def dibujar_tabla_taps(_evento=None):
            """RELACIÓN POR TAP: se llena al capturar cada RM (Enter) y al calcular."""
            for hijo in tabla_taps_frame.winfo_children():
                hijo.destroy()
            tabla_c = tk.Frame(
                tabla_taps_frame, bg="#FFFFFF",
                highlightbackground="#E2E8F0", highlightthickness=1,
            )
            tabla_c.pack(anchor="w", fill="x", pady=(0, 10))
            tk.Label(
                tabla_c, text="RELACIÓN POR TAP", bg="#FFFFFF", fg=TTR_MORADO_OSCURO,
                font=("Segoe UI", 10, "bold"), anchor="w", padx=14, pady=8,
            ).grid(row=0, column=0, columnspan=5, sticky="ew")
            for columna, encabezado in enumerate(("Tap", "RT teórica", "RM medida", "%DIF", "Dictamen")):
                tk.Label(
                    tabla_c, text=encabezado, bg="#F1F5F9", fg="#475569",
                    font=("Segoe UI", 9, "bold"), anchor="w", padx=10, pady=6,
                ).grid(row=1, column=columna, sticky="ew")
            for t in range(1, n_taps + 1):
                rt_t = None if nominal is None else _relacion_teorica_tap_ttr(
                    nominal, t, centro, usar_reg, mantener,
                )
                rm_t = _leer_ttr(rm_taps.get(str(t), ""))
                res_t = _evaluar_ttr(rt_t, rm_t)
                valores = (
                    f"{t}" + (" (central)" if t == centro else ""),
                    "—" if rt_t is None else f"{rt_t:.4f}",
                    "—" if rm_t is None else f"{rm_t:.4f}",
                    "—" if res_t is None else f"{res_t['dif']:.3f} %",
                    "—" if res_t is None else res_t["estado"],
                )
                color_dictamen = {
                    "ACEPTADO": "#15803D", "INVESTIGAR": "#CA8A04", "RECHAZADO": "#DC2626",
                }
                for columna, texto_t in enumerate(valores):
                    color_t = "#1E293B"
                    if columna == 4 and res_t is not None:
                        color_t = color_dictamen.get(res_t["estado"], "#1E293B")
                    tk.Label(
                        tabla_c, text=texto_t, bg="#FFFFFF", fg=color_t,
                        font=("Consolas", 10, "bold" if columna == 4 else "normal"),
                        anchor="w", padx=10, pady=5,
                    ).grid(row=t + 1, column=columna, sticky="ew")

        def al_capturar_rm(_evento=None):
            """Enter: guarda la RM de este tap, limpia el campo y pasa al siguiente tap."""
            dibujar_tabla_taps()
            siguiente = int(datos["tap"].get()) + 1
            if siguiente <= n_taps:
                datos["tap"].set(str(siguiente))
                obtener_rt()
            dibujar_tabla_taps()

        entrada_rm.bind("<Return>", al_capturar_rm, add="+")
        dibujar_tabla_taps()

        panel_resultado = tk.Frame(frame, bg=RA_VISTA_FONDO)
        panel_resultado.pack(anchor="w", fill="x")

        def calcular():
            for hijo in panel_resultado.winfo_children():
                hijo.destroy()
            refrescar_rt()
            dibujar_tabla_taps()
            if nominal is not None:
                rt = rt_del_tap()
            else:
                rt = _leer_ttr(datos["relacion_teorica_manual"].get())
            rm = _leer_ttr(datos["relacion_medida"].get())
            error = None
            if rt is None:
                error = (
                    "Falta el kV de placa para calcular la relación "
                    "teórica." if nominal is None else
                    "No se pudo calcular la relación teórica."
                )
            elif rm is None:
                error = "Escriba la relación medida con el TTR."
            if error:
                tk.Label(
                    panel_resultado, text=error, bg="#FEF3C7", fg="#92400E",
                    font=fuente_opcion, wraplength=600, justify="left",
                    padx=10, pady=8,
                ).pack(anchor="w")
                return
            resultado = _evaluar_ttr(rt, rm)
            aceptado = resultado["estado"] == "ACEPTADO"
            color_estado = "#007A33" if aceptado else "#F5C400"
            texto_color = "white" if aceptado else "#1A1A1A"
            tarjeta = tk.Frame(
                panel_resultado, bg="#FFFFFF",
                highlightbackground="#E2E8F0", highlightthickness=1,
            )
            tarjeta.pack(anchor="w", fill="x", pady=(0, 10))
            tk.Label(
                tarjeta, text=f"DICTAMEN: {resultado['estado']}",
                bg=color_estado, fg=texto_color,
                font=("Segoe UI", 13, "bold"), anchor="w", padx=14, pady=10,
            ).pack(fill="x")
            cuerpo = tk.Frame(tarjeta, bg="#FFFFFF")
            cuerpo.pack(fill="x", padx=14, pady=12)
            tk.Label(
                cuerpo,
                text=(
                    f"Relación teórica: {resultado['rt']:.4f}   ·   "
                    f"Relación medida: {resultado['rm']:.4f}   ·   "
                    f"%DIF: {resultado['dif']:.3f} %"
                ),
                bg="#FFFFFF", fg="#1E293B", font=("Segoe UI", 13, "bold"),
                anchor="w",
            ).pack(anchor="w", pady=(0, 6))
            tk.Label(
                cuerpo, text=resultado["frase"], bg="#FFFFFF", fg="#334155",
                font=fuente_opcion, wraplength=600, justify="left",
                anchor="w",
            ).pack(anchor="w")
            nivel = "normal" if aceptado else "alerta"
            resumen = (
                f"Relación teórica: {resultado['rt']:.4f}\n"
                f"Relación medida: {resultado['rm']:.4f}\n"
                f"%DIF: {resultado['dif']:.3f} %"
            )
            self._publicar_foco_ieee(nivel, resumen, resultado["estado"])

        _boton_relieve_ra(
            fila_botones_ttr, "CALCULAR RELACIÓN MEDIDA", calcular,
            ancho=280, modo="diagnostico_morado", fondo=RA_VISTA_FONDO,
            alto_caja=28, alto_lienzo=40, fuente_nombre="Consolas",
        ).pack(side="left")
        fila_botones_ttr.pack(anchor="w", pady=(0, 10))

    def _formulario_ttr(self, frame, cargar_paso):
        datos = self.datos_ttr
        formulario = tk.Frame(frame, bg=RA_VISTA_FONDO)
        formulario.pack(anchor="w", fill="x")
        fuente = ctk.CTkFont(family="Segoe UI", size=14, weight="bold")
        fuente_opcion = ctk.CTkFont(family="Segoe UI", size=14)

        def campo(texto, fila):
            ctk.CTkLabel(
                formulario, text=texto, font=fuente,
                text_color="#334155", fg_color="transparent",
            ).grid(row=fila, column=0, sticky="e", padx=(0, 20), pady=6)

        campo("Tipo de equipo:", 0)
        combo_equipo = ctk.CTkComboBox(
            formulario, variable=datos["tipo_equipo"],
            values=(
                "Transformadores de 2 Devanados",
                "Transformadores de 3 Devanados",
                "Autotransformadores",
                "Reactores",
            ),
            state="readonly", width=380, font=fuente_opcion,
            dropdown_font=fuente_opcion,
            button_color=TTR_MORADO_OSCURO,
            button_hover_color=TTR_MORADO_HOVER,
        )
        combo_equipo.grid(row=0, column=1, sticky="w", pady=6)

        campo("Configuración:", 1)
        marco_config = ctk.CTkFrame(formulario, fg_color="transparent")
        marco_config.grid(row=1, column=1, sticky="w", pady=6)
        for texto_cfg in ("Trifásico", "Monofásico"):
            ctk.CTkRadioButton(
                marco_config, text=texto_cfg, variable=datos["configuracion"],
                value=texto_cfg, font=fuente_opcion,
                fg_color=TTR_MORADO, hover_color=TTR_MORADO_HOVER,
                command=lambda: actualizar(),
            ).pack(side="left", padx=(0, 18))

        etiqueta_fase = ctk.CTkLabel(
            formulario, text="Fase:", font=fuente,
            text_color="#334155", fg_color="transparent",
        )
        marco_fase = ctk.CTkFrame(formulario, fg_color="transparent")
        for letra in ("A", "B", "C"):
            ctk.CTkRadioButton(
                marco_fase, text=letra, variable=datos["fase"], value=letra,
                font=fuente_opcion, fg_color=TTR_MORADO,
                hover_color=TTR_MORADO_HOVER,
            ).pack(side="left", padx=(0, 16))

        etiqueta_conexion = ctk.CTkLabel(
            formulario, text="Conexión:", font=fuente,
            text_color="#334155", fg_color="transparent",
        )
        combo_conexion = ctk.CTkComboBox(
            formulario, variable=datos["conexion"],
            values=CONEXIONES_TTR_2D,
            state="readonly", width=320, font=fuente_opcion,
            dropdown_font=fuente_opcion,
            button_color=TTR_MORADO_OSCURO,
            button_hover_color=TTR_MORADO_HOVER,
        )

        etiqueta_voltaje = ctk.CTkLabel(
            formulario, text="Voltaje de placa en kV:", font=fuente,
            text_color="#334155", fg_color="transparent",
        )
        marco_voltaje = ctk.CTkFrame(formulario, fg_color="transparent")
        campos_kv = (
            ("KV PRIMARIO [ H ]:", "voltaje_h", True),
            ("KV SECUNDARIO [ X ]:", "voltaje_x", True),
            ("KV TERCIARIO [ Y ]:", "voltaje_y", False),
        )
        filas_kv = {}
        for i_kv, (titulo_kv, clave_kv, siempre) in enumerate(campos_kv):
            etiqueta_kv = ctk.CTkLabel(
                marco_voltaje, text=titulo_kv, font=fuente_opcion,
                text_color="#334155", fg_color="transparent",
            )
            entrada_kv = ctk.CTkEntry(
                marco_voltaje, textvariable=datos[clave_kv],
                width=90, font=fuente_opcion,
            )
            etiqueta_kv.grid(row=i_kv, column=0, sticky="e", padx=(0, 10), pady=4)
            entrada_kv.grid(row=i_kv, column=1, sticky="w", pady=4)
            filas_kv[clave_kv] = (etiqueta_kv, entrada_kv, siempre)

        etiqueta_reg = ctk.CTkLabel(
            formulario,
            text="¿Usar el estándar CFE de regulación por paso? (0.625%)",
            font=fuente, text_color="#334155", fg_color="transparent",
            wraplength=340, justify="right",
        )
        marco_reg = ctk.CTkFrame(formulario, fg_color="transparent")
        for texto_reg in ("Sí", "No"):
            ctk.CTkRadioButton(
                marco_reg, text=texto_reg, variable=datos["regulacion_cfe"],
                value=texto_reg, font=fuente_opcion,
                fg_color=TTR_MORADO, hover_color=TTR_MORADO_HOVER,
            ).pack(side="left", padx=(0, 18))

        etiqueta_camb = ctk.CTkLabel(
            formulario, text="Seleccione tipo de cambiador:", font=fuente,
            text_color="#334155", fg_color="transparent",
        )
        marco_camb = ctk.CTkFrame(formulario, fg_color="transparent")
        for texto_camb, nota_camb in (
            ("Sin carga [ 5 TAPs ]", ""),
            ("Bajo carga [ 21 TAPs ]", "Nominal Simple"),
            ("Bajo carga [ 23 TAPs ]", "Nominal Triple"),
        ):
            fila_camb = ctk.CTkFrame(marco_camb, fg_color="transparent")
            fila_camb.pack(anchor="w", pady=2)
            ctk.CTkRadioButton(
                fila_camb, text=texto_camb, variable=datos["tipo_cambiador"],
                value=texto_camb, font=fuente_opcion,
                fg_color=TTR_MORADO, hover_color=TTR_MORADO_HOVER,
            ).pack(side="left")
            if nota_camb:
                ctk.CTkLabel(
                    fila_camb, text=nota_camb, font=fuente_opcion,
                    text_color="#334155", fg_color="transparent",
                ).pack(side="left", padx=(14, 0))

        etiqueta_med = ctk.CTkLabel(
            formulario, text="Medición a realizar:", font=fuente,
            text_color="#334155", fg_color="transparent",
        )
        marco_med = ctk.CTkFrame(formulario, fg_color="transparent")
        for opcion in ("Directa", "Inversa", "Ambas"):
            ctk.CTkRadioButton(
                marco_med, text=opcion, variable=datos["medicion_realizar"],
                value=opcion, font=fuente_opcion,
                fg_color=TTR_MORADO, hover_color=TTR_MORADO_HOVER,
            ).pack(side="left", padx=(0, 18))
        etiqueta_med.grid(row=7, column=0, sticky="e", padx=(0, 20), pady=6)
        marco_med.grid(row=7, column=1, sticky="w", pady=6)

        etiqueta_pol = ctk.CTkLabel(
            formulario, text="Polaridad del transformador:", font=fuente,
            text_color="#334155", fg_color="transparent",
        )
        marco_pol = ctk.CTkFrame(formulario, fg_color="transparent")
        for texto_pol, valor_pol in (
            ("Sustractiva  (H1 con X1 — distribución)", "Sustractiva"),
            (
                "Aditiva  (H1 con X2 — transmisión, usual 230/69 kV)",
                "Aditiva",
            ),
        ):
            ctk.CTkRadioButton(
                marco_pol, text=texto_pol, variable=datos["polaridad"],
                value=valor_pol, font=fuente_opcion,
                fg_color=TTR_MORADO, hover_color=TTR_MORADO_HOVER,
            ).pack(anchor="w", pady=3)
        ctk.CTkLabel(
            marco_pol,
            text="Nota: transmisión CFE → casi siempre opción 2.",
            font=fuente_opcion, text_color=TTR_MORADO_OSCURO, fg_color="transparent",
        ).pack(anchor="w", pady=(6, 0))
        etiqueta_pol.grid(row=8, column=0, sticky="ne", padx=(0, 20), pady=6)
        marco_pol.grid(row=8, column=1, sticky="w", pady=6)

        campo("Temp. ambiente (°C):", 9)
        entrada_temp = ctk.CTkEntry(
            formulario, textvariable=datos["temp_ambiente"],
            width=80, font=fuente_opcion,
        )
        entrada_temp.grid(row=9, column=1, sticky="w", pady=6)
        campo("Humedad relativa (%):", 10)
        entrada_hum = ctk.CTkEntry(
            formulario, textvariable=datos["humedad"],
            width=80, font=fuente_opcion,
        )
        entrada_hum.grid(row=10, column=1, sticky="w", pady=6)
        campo("Temp. devanado (°C):", 11)
        entrada_dev = ctk.CTkEntry(
            formulario, textvariable=datos["temp_devanado"],
            width=80, font=fuente_opcion,
        )
        entrada_dev.grid(row=11, column=1, sticky="w", pady=6)

        def mostrar(etiqueta_w, control_w, fila, visible):
            if visible:
                etiqueta_w.grid(
                    row=fila, column=0, sticky="e", padx=(0, 20), pady=6,
                )
                control_w.grid(row=fila, column=1, sticky="w", pady=6)
            else:
                etiqueta_w.grid_remove()
                control_w.grid_remove()

        def actualizar():
            equipo = datos["tipo_equipo"].get()
            mono = datos["configuracion"].get() == "Monofásico"
            opciones = _opciones_conexion_ttr(equipo, datos["configuracion"].get())
            mostrar(etiqueta_fase, marco_fase, 2, mono)
            mostrar(etiqueta_conexion, combo_conexion, 3, bool(opciones))
            mostrar(etiqueta_voltaje, marco_voltaje, 4, True)
            terciario = (
                "3 Devanados" in equipo or "Autotransformadores" in equipo
            )
            etiqueta_y, entrada_y, _siempre = filas_kv["voltaje_y"]
            if terciario:
                etiqueta_y.grid()
                entrada_y.grid()
            else:
                etiqueta_y.grid_remove()
                entrada_y.grid_remove()
            mostrar(etiqueta_reg, marco_reg, 5, True)
            mostrar(etiqueta_camb, marco_camb, 6, True)
            if opciones:
                combo_conexion.configure(values=opciones)
                if datos["conexion"].get() not in opciones:
                    datos["conexion"].set(opciones[0])

        combo_equipo.configure(command=lambda _v=None: actualizar())
        actualizar()
        boton_siguiente = self._pie_paso_ttr(frame, 1, lambda: cargar_paso(2))

        def campos_en_orden():
            terciario = (
                "3 Devanados" in datos["tipo_equipo"].get()
                or "Autotransformadores" in datos["tipo_equipo"].get()
            )
            cadena = [combo_equipo]
            if combo_conexion.winfo_ismapped():
                cadena.append(combo_conexion)
            cadena.append(filas_kv["voltaje_h"][1])
            cadena.append(filas_kv["voltaje_x"][1])
            if terciario:
                cadena.append(filas_kv["voltaje_y"][1])
            cadena.extend([entrada_temp, entrada_hum, entrada_dev, boton_siguiente])
            return cadena

        def al_enter(evento):
            foco = evento.widget
            cadena = campos_en_orden()
            indice = None
            for i, widget in enumerate(cadena):
                interno = getattr(widget, "_entry", None)
                if foco in (widget, interno):
                    indice = i
                    break
            if indice is None:
                return
            destino = cadena[(indice + 1) % len(cadena)]
            destino.focus_set()
            caja = getattr(destino, "_entry", None)
            if caja is not None:
                try:
                    caja.selection_range(0, "end")
                    caja.icursor("end")
                except tk.TclError:
                    pass
            return "break"

        for widget in (
            combo_equipo, combo_conexion,
            filas_kv["voltaje_h"][1], filas_kv["voltaje_x"][1],
            filas_kv["voltaje_y"][1],
            entrada_temp, entrada_hum, entrada_dev,
        ):
            widget.bind("<Return>", al_enter)
            widget.bind("<KP_Enter>", al_enter)

    def _tabla_ttr(self, frame):
        datos = self.datos_ttr
        equipo = datos["tipo_equipo"].get().strip()
        filas, nota = _filas_ttr(
            equipo,
            datos["configuracion"].get(),
            datos["conexion"].get(),
        )
        if not filas:
            ctk.CTkLabel(
                frame, text=nota, font=ctk.CTkFont(family="Segoe UI", size=14),
                text_color="#475569", fg_color="transparent", wraplength=760,
                justify="left",
            ).pack(anchor="w", pady=(0, 14))
            return
        tabla = tk.Frame(
            frame, bg="#FFFFFF",
            highlightbackground="#E2E8F0", highlightthickness=1,
        )
        tabla.pack(fill="x")
        negro = "#111111"
        carmesi = "#DC143C"
        columnas = (
            ("", 4, TTR_MORADO_OSCURO),
            ("PRUEBA", 8, TTR_MORADO_OSCURO),
            ("CN", 14, negro),
            ("CR", 14, carmesi),
            ("GN", 14, negro),
            ("GR", 14, carmesi),
            ("MIDE", 16, _TTR_ROSA_PIE),
        )
        for c, (titulo_c, peso, tinta) in enumerate(columnas):
            tabla.grid_columnconfigure(c, weight=peso)
        for col_ini, col_fin, titulo_g in (
            (2, 3, "TERMINALES DE EXCITACIÓN"),
            (4, 5, "TERMINALES SECUNDARIAS"),
        ):
            tk.Label(
                tabla, text=titulo_g, bg=TTR_MORADO_OSCURO, fg="#FFFFFF",
                font=("Segoe UI", 10, "bold"), anchor="center",
                padx=8, pady=8,
            ).grid(
                row=0, column=col_ini, columnspan=col_fin - col_ini + 1,
                sticky="ew", padx=(0, 1), pady=(0, 1),
            )
        for c, (titulo_c, _peso, tinta) in enumerate(columnas):
            tk.Label(
                tabla, text=titulo_c, bg="#F5F3FF", fg=tinta,
                font=("Segoe UI", 9, "bold"), anchor="center",
                padx=8, pady=10,
            ).grid(row=1, column=c, sticky="ew", padx=(0, 1), pady=(0, 2))
        selector = tk.IntVar(frame, value=-1)
        radios = []
        pildoras = {
            2: (negro, "#E9ECEF"),
            3: (carmesi, "#FFE3E3"),
            4: (negro, "#E9ECEF"),
            5: (carmesi, "#FFE3E3"),
            6: (_TTR_ROSA_PIE, "#FDF2F8"),
        }
        job_previo = getattr(self, "_parpadeo_ttr", None)
        if job_previo is not None:
            try:
                self.after_cancel(job_previo)
            except tk.TclError:
                pass
            self._parpadeo_ttr = None

        def elegir(prueba, indice):
            selector.set(indice)
            self.prueba_ttr = prueba
            self._punto_visible_ttr = True
            for i, radio in enumerate(radios):
                if i == indice:
                    continue
                try:
                    radio.configure(
                        fg_color=TTR_MORADO, border_color="#C4B5FD",
                    )
                except tk.TclError:
                    return

        for i, (numero, cn, cr, gn, gr, mide) in enumerate(filas):
            fondo = "#FAF5FF" if i % 2 else "#FFFFFF"
            fila_t = i + 2
            prueba = {
                "prueba": str(numero), "cn": cn, "cr": cr,
                "gn": gn, "gr": gr, "mide": mide,
            }
            punto = ctk.CTkRadioButton(
                tabla, text="", variable=selector, value=i,
                width=22, height=22,
                radiobutton_width=18, radiobutton_height=18,
                fg_color=TTR_MORADO, hover_color=TTR_MORADO_HOVER,
                border_color="#C4B5FD", bg_color=fondo,
                command=lambda p=prueba, j=i: elegir(p, j),
            )
            punto._fondo_fila = fondo
            punto.grid(row=fila_t, column=0, padx=8, pady=6)
            radios.append(punto)
            for c, valor in enumerate((numero, cn, cr, gn, gr, mide), start=1):
                celda = tk.Frame(tabla, bg=fondo, cursor="hand2")
                celda.grid(row=fila_t, column=c, sticky="nsew")
                elegir_fila = lambda _e, p=prueba, j=i: elegir(p, j)
                celda.bind("<Button-1>", elegir_fila)
                if c == 1:
                    etiqueta = tk.Label(
                        celda, text=str(valor), bg=fondo, fg="#1E293B",
                        font=("Segoe UI", 10, "bold"), cursor="hand2",
                    )
                    etiqueta.pack(expand=True, pady=8)
                    etiqueta.bind("<Button-1>", elegir_fila)
                else:
                    color_t, color_f = pildoras[c]
                    pastilla = tk.Label(
                        celda, text=str(valor), bg=color_f, fg=color_t,
                        font=("Segoe UI", 10, "bold"),
                        padx=12, pady=4, cursor="hand2",
                    )
                    pastilla.pack(expand=True, pady=6)
                    pastilla.bind("<Button-1>", elegir_fila)

        if filas:
            numero, cn, cr, gn, gr, mide = filas[0]
            elegir(
                {
                    "prueba": str(numero), "cn": cn, "cr": cr,
                    "gn": gn, "gr": gr, "mide": mide,
                },
                0,
            )

        self._punto_visible_ttr = True

        def parpadear():
            self._parpadeo_ttr = None
            try:
                if not tabla.winfo_exists():
                    return
            except tk.TclError:
                return
            self._punto_visible_ttr = not self._punto_visible_ttr
            elegido = selector.get()
            if elegido < 0:
                self._parpadeo_ttr = self.after(450, parpadear)
                return
            for i, radio in enumerate(radios):
                if i != elegido:
                    continue
                try:
                    encendido = self._punto_visible_ttr
                    radio.configure(
                        fg_color=TTR_MORADO if encendido else radio._fondo_fila,
                        border_color="#C4B5FD" if encendido else radio._fondo_fila,
                    )
                except tk.TclError:
                    return
            self._parpadeo_ttr = self.after(450, parpadear)

        def al_cerrar_tabla(_evento):
            if _evento.widget is not tabla:
                return
            job = getattr(self, "_parpadeo_ttr", None)
            if job is None:
                return
            try:
                self.after_cancel(job)
            except tk.TclError:
                pass
            self._parpadeo_ttr = None

        tabla.bind("<Destroy>", al_cerrar_tabla)
        self._parpadeo_ttr = self.after(450, parpadear)
        ctk.CTkLabel(
            frame,
            text=(
                "CN y CR son las terminales secundarias del TTR "
                "(H1 negra y H2 roja). GN y GR son la excitación "
                "(X1 negra y X2 roja)."
            ),
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color="#64748B", fg_color="transparent", wraplength=760,
            justify="left",
        ).pack(anchor="w", pady=(16, 8))
        caja = tk.Frame(frame, bg="#F5F3FF")
        caja.pack(fill="x", pady=(16, 0))
        tk.Frame(caja, bg=TTR_MORADO, width=6).pack(side="left", fill="y")
        tk.Label(
            caja,
            text=(
                "Primera medición:  %DIF = (RT − RM) / RT × 100, "
                "máximo 0.5 % contra la relación de placa. "
                "En las siguientes no debe variar; por la precisión "
                "del equipo se acepta 0.05 % (ST-CT-007)."
            ),
            bg="#F5F3FF", fg="#5B21B6", font=("Segoe UI", 10),
            anchor="w", justify="left", wraplength=740,
        ).pack(side="left", fill="x", padx=12, pady=10)

    def _vectores_ttr(self, frame):
        """Paso 03: diagrama fasorial y esquema de conexiones, cada uno con su guía."""
        datos = self.datos_ttr
        clave = _clave_vector_ttr(
            datos["tipo_equipo"].get(),
            datos["configuracion"].get(),
            datos["conexion"].get(),
        )
        if not clave:
            ctk.CTkLabel(
                frame,
                text="ST-CT-007 no publica vectores TTR para reactores.",
                font=ctk.CTkFont(family="Segoe UI", size=14),
                text_color="#475569", fg_color="transparent",
            ).pack(anchor="w")
            return
        n = len(_VECTORES_TTR[clave][3])
        panel = ctk.CTkScrollableFrame(frame, fg_color=RA_VISTA_FONDO)
        panel.pack(fill="both", expand=True)
        prueba = self.prueba_ttr

        def tarjeta(titulo, color):
            caja = tk.Frame(
                panel, bg="#FFFFFF",
                highlightbackground="#E2E8F0", highlightthickness=1,
            )
            caja.pack(fill="x", pady=(0, 12))
            tk.Label(
                caja, text=titulo, bg="#FFFFFF", fg="#FF4A80",
                font=("Consolas", 22, "bold"), anchor="w",
            ).pack(anchor="w", padx=14, pady=(8, 0))
            cuerpo = tk.Frame(caja, bg="#FFFFFF")
            cuerpo.pack(fill="x", padx=6, pady=(0, 8))
            lienzo = tk.Canvas(
                cuerpo, width=520, height=280, bg="#FFFFFF",
                highlightthickness=0,
            )
            lienzo.pack(side="left", anchor="n")
            leyenda = tk.Frame(cuerpo, bg="#FFFFFF")
            leyenda.pack(
                side="left", anchor="n", fill="both", expand=True,
                padx=(8, 16), pady=(18, 8),
            )
            return lienzo, leyenda

        medicion, leyenda_mide = tarjeta("DIAGRAMA FASORIAL", _TTR_ROSA_PIE)
        conexiones, leyenda_cables = tarjeta(
            "ESQUEMA DE CONEXIONES", _TTR_ROSA_PIE,
        )
        modo_med = datos["medicion_realizar"].get()
        polaridad = datos["polaridad"].get()
        _pintar_guia_fasorial_ttr(leyenda_mide, prueba, modo_med, polaridad)
        _pintar_guia_conexiones_ttr(leyenda_cables, prueba, clave, modo_med)

        self._vector_mide_visible = True
        self._seq_vector_ttr = 0
        job_previo = getattr(self, "_parpadeo_vector_ttr", None)
        if job_previo is not None:
            try:
                self.after_cancel(job_previo)
            except tk.TclError:
                pass
            self._parpadeo_vector_ttr = None

        def aplicar_parpadeo():
            linea_visible = self._vector_mide_visible
            tinta = TTR_ROSA_MEDICION if linea_visible else "#FFFFFF"
            fase = "hidden" if linea_visible else "normal"
            try:
                if not medicion.winfo_exists():
                    return False
            except tk.TclError:
                return False
            for item in medicion.find_withtag("parpadeo"):
                if medicion.type(item) == "oval":
                    medicion.itemconfigure(item, fill=tinta, outline=tinta)
                else:
                    medicion.itemconfigure(item, fill=tinta)
            for item in medicion.find_withtag("parpadeo_fase"):
                medicion.itemconfigure(item, state=fase)
            try:
                if not conexiones.winfo_exists():
                    return False
            except tk.TclError:
                return False
            activo = _SECUENCIA_CONEXIONES_TTR[
                self._seq_vector_ttr % len(_SECUENCIA_CONEXIONES_TTR)
            ]
            colores_seq = getattr(conexiones, "_seq_color", {})
            for item in conexiones.find_withtag("seq_todo"):
                tags = conexiones.gettags(item)
                if f"seq_{activo}" in tags:
                    col = colores_seq.get((item, activo), "#000000")
                else:
                    col = "#FFFFFF"
                if conexiones.type(item) == "oval":
                    conexiones.itemconfigure(item, fill=col, outline=col)
                else:
                    conexiones.itemconfigure(item, fill=col)
            return True

        def pintar():
            ficha = _VECTORES_TTR.get(clave)
            n_grupos = len(ficha[3]) if ficha else 1
            _margen, _paso, ancho = _medida_vector_ttr(n_grupos)
            for lienzo, modo in ((medicion, "mide"), (conexiones, "cables")):
                lienzo.configure(width=ancho)
                _dibujar_vector_ttr(lienzo, clave, prueba, modo)
            aplicar_parpadeo()

        def parpadear():
            self._parpadeo_vector_ttr = None
            self._vector_mide_visible = not self._vector_mide_visible
            self._seq_vector_ttr += 1
            if not aplicar_parpadeo():
                return
            self._parpadeo_vector_ttr = self.after(450, parpadear)

        def al_cerrar(evento):
            if evento.widget is not medicion:
                return
            job = getattr(self, "_parpadeo_vector_ttr", None)
            if job is None:
                return
            try:
                self.after_cancel(job)
            except tk.TclError:
                pass
            self._parpadeo_vector_ttr = None

        medicion.bind("<Destroy>", al_cerrar)
        pintar()
        if prueba:
            self._parpadeo_vector_ttr = self.after(450, parpadear)

    def abrir_prueba_factor(self):
        """Factor de potencia al aislamiento (ST-CT-002). Formato de RA, en verde."""
        ctk.set_appearance_mode("Light")
        ventana = tk.Toplevel(self)
        ventana.title(
            "[ S. A. P. E. ]  Sistema de Análisis de Pruebas Eléctricas v3.4"
        )
        ventana.iconbitmap(str(APP_ICON_PATH))
        ventana.geometry("1280x840")
        ventana.minsize(1100, 680)
        ventana.configure(bg=RA_VISTA_FONDO)
        self.datos_fp = {
            "tipo_equipo": tk.StringVar(ventana, value=EQUIPOS_FP[0]),
            "arreglo": tk.StringVar(ventana),
            "configuracion": tk.StringVar(ventana, value="Trifásico"),
            "fase": tk.StringVar(ventana, value="A"),
            "aislamiento": tk.StringVar(ventana, value="Sumergido en Aceite"),
            "preservacion": tk.StringVar(ventana, value=PRESERVACION_FP[0]),
            "estado": tk.StringVar(ventana, value="En operación"),
            "clase_kv": tk.StringVar(ventana, value="Menor de 115 kV"),
            "aislamiento_cable": tk.StringVar(ventana, value=TABLA9_FP[0][0]),
            "temp_aceite": tk.StringVar(ventana),
            "temp_ambiente": tk.StringVar(ventana),
            "humedad": tk.StringVar(ventana),
            "kv": tk.StringVar(ventana, value="10"),
            "ma": tk.StringVar(ventana),
            "watts": tk.StringVar(ventana),
        }
        self.prueba_fp = None
        self._parpadeo_fp = None
        self._ultimo_fp = None
        if not hasattr(self, "_lecturas_fp"):
            self._lecturas_fp = _cargar_lecturas_fp()

        barra_superior = tk.Frame(ventana, bg="#12161A", height=50)
        barra_superior.pack(side="top", fill="x")
        barra_superior.pack_propagate(False)

        def logo_neon(
            texto="[ S.A.P.E. ]", fondo=(5, 5, 5), marco=True, tam=16,
        ):
            from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageTk
            fuente = ImageFont.truetype(r"C:\Windows\Fonts\consolab.ttf", tam)
            sonda = ImageDraw.Draw(Image.new("RGB", (1, 1)))
            caja = sonda.textbbox((0, 0), texto, font=fuente)
            ancho = caja[2] - caja[0] + 22
            alto = caja[3] - caja[1] + 14
            imagen = Image.new("RGB", (ancho, alto), fondo)
            halo = Image.new("RGB", (ancho, alto), fondo)
            xy = (11 - caja[0], 7 - caja[1])
            ImageDraw.Draw(halo).text(xy, texto, font=fuente, fill=(0, 255, 255))
            halo = halo.filter(ImageFilter.GaussianBlur(3 * tam / 16))
            imagen = Image.blend(imagen, halo, 0.9)
            dibujo = ImageDraw.Draw(imagen)
            dibujo.text(xy, texto, font=fuente, fill=(0, 255, 255))
            if marco:
                dibujo.rounded_rectangle(
                    (0, 0, ancho - 1, alto - 1), radius=4, outline=(42, 49, 58),
                )
            return ImageTk.PhotoImage(imagen)

        foto_logo = logo_neon("ST-CT-002")
        ventana._logo_sape = foto_logo
        tk.Label(
            barra_superior, image=foto_logo, bg="#12161A", bd=0,
        ).pack(side="left", padx=(16, 8))
        tk.Label(
            barra_superior,
            text=(
                "PROCEDIMIENTO PARA MEDICIÓN DE FACTOR DE POTENCIA\n"
                "EN AISLAMIENTO DE EQUIPO ELÉCTRICO"
            ),
            bg="#12161A", fg="#A0AEC0",
            font=("Segoe UI", 8, "bold"), justify="left",
        ).pack(side="left", padx=(8, 0))
        reloj = tk.Label(
            barra_superior, text="", bg="#12161A",
            fg="#A0AEC0", font=("Consolas", 11, "bold"),
        )
        reloj.pack(side="right", padx=(0, 16))
        tk.Label(
            barra_superior, text="MODOS GST · GST-G · UST",
            bg="#12161A", fg="#A0AEC0",
            font=("Segoe UI", 9, "bold"),
        ).pack(side="right")
        tk.Label(
            barra_superior, text="●",
            bg="#12161A", fg="#00FF00",
            font=("Segoe UI", 8),
        ).pack(side="right", padx=(0, 6))

        def marcar_reloj():
            try:
                if not ventana.winfo_exists():
                    return
            except tk.TclError:
                return
            reloj.config(text=datetime.now().strftime("%H:%M:%S"))
            ventana._reloj_fp = ventana.after(1000, marcar_reloj)

        marcar_reloj()

        panel_lateral = tk.Frame(ventana, bg="#000000", width=320)
        panel_lateral.pack(side=tk.LEFT, fill=tk.Y)
        panel_lateral.pack_propagate(False)
        logo = tk.Frame(
            panel_lateral, bg="#12161A",
            highlightbackground="#3B4553", highlightthickness=1,
        )
        logo.pack(fill="x", padx=16, pady=(16, 0))
        foto_sape_lateral = logo_neon(
            fondo=(18, 22, 26), marco=False, tam=32,
        )
        ventana._logo_sape_lateral = foto_sape_lateral
        tk.Label(
            logo, image=foto_sape_lateral, bg="#12161A", bd=0,
        ).pack(pady=8)
        tk.Label(
            panel_lateral, text="FACTOR DE POTENCIA AL AISLAMIENTO",
            bg="#1C2128", fg=FP_VISTA_VERDE_CLARO,
            font=("Segoe UI", 8, "bold"),
        ).pack(pady=(6, 8))

        pie_lateral = tk.Frame(
            panel_lateral, bg=RA_VISTA_SIDEBAR_OSCURO,
            highlightbackground="#1F2937", highlightthickness=1,
        )
        pie_lateral.pack(side="bottom", fill="x")
        for rotulo, valor, color, relleno in (
            ("ESTADO NORMA:", "ST-CT-002 Rev. 1", "#34D399", (10, 2)),
            ("UNIDAD DE DIAG:", "ACTIVA", FP_VISTA_VERDE_CLARO, (0, 10)),
        ):
            fila_pie = tk.Frame(pie_lateral, bg=RA_VISTA_SIDEBAR_OSCURO)
            fila_pie.pack(fill="x", padx=14, pady=relleno)
            tk.Label(
                fila_pie, text=rotulo, bg=RA_VISTA_SIDEBAR_OSCURO,
                fg="#9CA3AF", font=("Consolas", 9),
            ).pack(side="left")
            tk.Label(
                fila_pie, text=valor, bg=RA_VISTA_SIDEBAR_OSCURO,
                fg=color, font=("Consolas", 9, "bold"),
            ).pack(side="right")

        menu_lateral = tk.Frame(panel_lateral, bg="#000000")
        menu_lateral.pack(fill="both", expand=True)

        area_principal = tk.Frame(ventana, bg=RA_VISTA_FONDO)
        area_principal.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        marco_scroll = tk.Frame(area_principal, bg=RA_VISTA_FONDO)
        marco_scroll.pack(fill=tk.BOTH, expand=True)
        barra_y_main = tk.Scrollbar(marco_scroll, orient="vertical")
        barra_x_main = tk.Scrollbar(marco_scroll, orient="horizontal")
        puerto_main = tk.Canvas(
            marco_scroll, bg=RA_VISTA_FONDO, highlightthickness=0, bd=0,
            yscrollcommand=barra_y_main.set,
            xscrollcommand=barra_x_main.set,
        )
        barra_y_main.configure(command=puerto_main.yview)
        barra_x_main.configure(command=puerto_main.xview)
        barra_x_main.pack(side="bottom", fill="x")
        barra_y_main.pack(side="right", fill="y")
        puerto_main.pack(side="left", fill="both", expand=True)
        contenedor = tk.Frame(
            puerto_main, bg=RA_VISTA_FONDO, bd=0, highlightthickness=0,
        )
        ventana_contenido = puerto_main.create_window(
            (0, 0), window=contenedor, anchor="nw",
        )

        def ajustar_contenido(_evento=None):
            if getattr(ajustar_contenido, "_ocupado", False):
                return
            ajustar_contenido._ocupado = True
            try:
                if not puerto_main.winfo_exists():
                    return
                req_w = max(contenedor.winfo_reqwidth(), 1)
                req_h = max(contenedor.winfo_reqheight(), 1)
                ancho = max(puerto_main.winfo_width(), req_w)
                alto = max(puerto_main.winfo_height(), req_h)
                puerto_main.itemconfigure(
                    ventana_contenido, width=ancho, height=alto,
                )
                puerto_main.configure(scrollregion=(0, 0, ancho, alto))
            except tk.TclError:
                return
            finally:
                ajustar_contenido._ocupado = False

        contenedor.bind("<Configure>", ajustar_contenido)
        puerto_main.bind("<Configure>", ajustar_contenido)
        contenedor._puerto_fp = puerto_main

        def al_rueda_principal(evento):
            if not getattr(evento, "delta", 0):
                return
            try:
                x, y = ventana.winfo_pointerxy()
                destino = ventana.winfo_containing(x, y)
            except (tk.TclError, KeyError):
                return
            if destino is not None and destino.winfo_class() == "Text":
                return
            lienzo = None
            dentro = False
            while destino is not None:
                propio = getattr(destino, "_scroll_propio", None)
                if propio is not None:
                    lienzo = propio
                    break
                if destino is marco_scroll:
                    dentro = True
                    break
                destino = getattr(destino, "master", None)
            if lienzo is None and not dentro:
                return
            objetivo = lienzo or puerto_main
            pasos = int(-evento.delta / 120) or (
                -1 if evento.delta < 0 else 1
            )
            try:
                if evento.state & 0x1:
                    objetivo.xview_scroll(pasos, "units")
                else:
                    objetivo.yview_scroll(pasos, "units")
            except tk.TclError:
                return
            return "break"

        ventana.bind_all("<MouseWheel>", al_rueda_principal)

        def soltar_rueda_principal(_evento):
            if _evento.widget is not ventana:
                return
            try:
                ventana.unbind_all("<MouseWheel>")
            except tk.TclError:
                pass

        ventana.bind("<Destroy>", soltar_rueda_principal)

        paso_actual = tk.IntVar(ventana, value=1)
        botones_paso = []

        def titulo_seccion(texto):
            fila = tk.Frame(menu_lateral, bg="#1C2128")
            fila.pack(fill="x", padx=16, pady=(8, 4))
            tk.Label(
                fila, text=texto, bg="#1C2128", fg="#5C6979",
                font=("Consolas", 9, "bold"),
            ).pack(side="left")
            tk.Frame(fila, bg="#374151", height=1).pack(
                side="left", fill="x", expand=True, padx=(10, 0),
            )

        titulo_seccion("PROCESO DE PRUEBA")
        for numero_paso, texto_paso in (
            (1, "DATOS DEL EQUIPO"),
            (2, "SELECCIÓN DE PRUEBAS"),
            (3, "DIAGRAMAS DE BLOQUES"),
            (4, "CAPTURA DE LECTURAS"),
        ):
            botones_paso.append(_boton_menu_ra(
                menu_lateral, texto_paso,
                lambda n=numero_paso: self._cargar_paso_fp(
                    n, paso_actual, contenedor, botones_paso,
                ),
                marca=f"{numero_paso:02d}", tema="verde",
            ))
        titulo_seccion("RECURSOS")
        _boton_menu_ra(
            menu_lateral, "MODOS DE PRUEBA",
            lambda: self.mostrar_modos_fp(ventana),
            texto_naranja=True, tema="verde",
        )
        for marca_recurso, texto_recurso, abrir in (
            ("A", "FORMATOS", self.mostrar_anexo_a_fp),
            ("B", "OPERACIÓN", self.mostrar_anexo_b_fp),
            ("C", "RESUMEN", self.mostrar_anexo_c_fp),
        ):
            _boton_menu_ra(
                menu_lateral, texto_recurso,
                lambda abrir=abrir: abrir(ventana),
                marca=marca_recurso, tema="verde",
            )
        self._cargar_paso_fp(1, paso_actual, contenedor, botones_paso)
        # El menú web abre FP con la ventana principal oculta. Una ventana
        # transient de un padre oculto también queda oculta.
        if self.winfo_viewable():
            ventana.transient(self)
        ventana.update_idletasks()
        ventana.deiconify()
        ventana.lift()
        ventana.focus_force()
        ventana.grab_set()
        return ventana

    # ── Datos de la prueba ──────────────────────────────────────────────

    def _arreglo_fp(self):
        """Arreglo vigente. Si el equipo cambió, toma el primero de su lista."""
        equipo = self.datos_fp["tipo_equipo"].get()
        opciones = ARREGLOS_FP.get(equipo, ())
        actual = self.datos_fp["arreglo"].get()
        if actual not in opciones:
            actual = opciones[0] if opciones else ""
            self.datos_fp["arreglo"].set(actual)
        return actual

    def _pruebas_fp(self):
        return _filas_fp(self.datos_fp["tipo_equipo"].get(), self._arreglo_fp())

    def _es_potencia_fp(self, equipo=None):
        equipo = equipo or self.datos_fp["tipo_equipo"].get()
        return any(
            nombre in equipo
            for nombre in ("Devanados", "Autotransformadores", "Reactores")
        )

    def _es_instrumento_fp(self, equipo=None):
        equipo = equipo or self.datos_fp["tipo_equipo"].get()
        return any(nombre in equipo for nombre in ("TCs", "TPs", "TPCs"))

    def _lleva_fase_fp(self, equipo=None):
        equipo = equipo or self.datos_fp["tipo_equipo"].get()
        if "Aceite" in equipo:
            return False
        if self._es_potencia_fp(equipo):
            return self.datos_fp["configuracion"].get() == "Monofásico"
        return True

    def _formato_fp(self):
        """Clave, nombre y figura del formato del Anexo A para el equipo."""
        equipo = self.datos_fp["tipo_equipo"].get()
        clave, nombre, figura = FORMATOS_FP.get(
            equipo, ("ST-CT-002", equipo, ""),
        )
        arreglo = self._arreglo_fp()
        if "TPCs" in equipo and ("Fig. 19" in arreglo or "Fig. 20" in arreglo):
            clave = "ST-CT-002-G"
        if not figura and arreglo:
            hallada = re.search(r"(Fig\. \d+[ab]?|Tabla \d+)", arreglo)
            figura = hallada.group(1) if hallada else ""
        return clave, nombre, figura

    def _nota_tabla_fp(self):
        """Nota del procedimiento que acompaña a la tabla de conexiones."""
        equipo = self.datos_fp["tipo_equipo"].get()
        arreglo = self._arreglo_fp()
        if "2 Devanados" in equipo:
            return (
                "CHX se calcula con la diferencia de mVA y mW de la prueba 1 "
                "menos la 2. Se comprueba con la prueba 3 menos la 4: las dos "
                "diferencias deben ser aproximadamente iguales. Si no lo son, "
                "se hace la prueba en UST (5 o 6)."
            )
        if "3 Devanados" in equipo:
            return (
                "CHX = prueba 1 − 2, CXY = prueba 3 − 4 y CHY = prueba 5 − 6. "
                "La prueba 7 verifica a las pruebas 2, 4 y 6: la suma de sus "
                "mVA y mW debe igualar a la prueba 7."
            )
        if "Autotransformadores" in equipo:
            if arreglo.startswith("Terciario no accesible"):
                return (
                    "Terciario no accesible: se ponen en corto todas las "
                    "boquillas y se hace una sola medición entre ese devanado "
                    "y tierra (prueba 2, sin la conexión del terciario a "
                    "guarda)."
                )
            return (
                "Los devanados interconectados (H+X) se prueban como un solo "
                "devanado y el terciario (Y) como el segundo, igual que un "
                "transformador de dos devanados."
            )
        if "Reactores" in equipo:
            return (
                "El reactor se considera de un solo devanado: una sola "
                "medición entre el devanado y tierra."
            )
        if "TPCs" in equipo:
            return (
                "* Los voltajes de prueba no deben exceder el nominal de la "
                "terminal: no más de 2 kV en B2, y B3 normalmente es de 5 kV "
                "o mayor; consulte el instructivo o al fabricante. Las demás "
                "mediciones se hacen a 2.5 o 10 kV según el equipo de medición."
            )
        if "TPs" in equipo:
            if "Fig. 14" in arreglo:
                return (
                    "Con el neutro del primario aterrizado internamente no se "
                    "puede hacer la prueba completa; solo estas dos mediciones."
                )
            if "Fig. 16" in arreglo:
                return (
                    "Procedimiento alternativo para la prueba completa "
                    "(Overall Test) cuando no se pueden cortocircuitar H1 y H0."
                )
            return (
                "Prueba 1 completa y prueba 2 con el devanado de baja a "
                "guarda. Las pruebas 3 y 4 son cruzadas de comprobación: si "
                "sus lecturas son iguales y el factor de potencia es bajo, el "
                "transformador está en buenas condiciones. Una lectura "
                "negativa indica posible devanado de alta abierto."
            )
        if "TCs" in equipo:
            return (
                "Las dos terminales del devanado de alta se ponen en corto. "
                "El devanado secundario se prueba a una tensión máxima de "
                "500 V."
            )
        if "Apartarrayos" in equipo:
            return (
                "El análisis se basa en las pérdidas: máximo 16 mW a 2.5 kV "
                "o 256 mW (0.256 W) a 10 kV. Se comparan con el historial y "
                "con equipos similares."
            )
        if "Cables" in equipo:
            return (
                "Aplica a longitudes cortas. La medición promedia el factor "
                "de potencia de toda la longitud; se interpreta con la "
                "Tabla 9 según el tipo de aislamiento."
            )
        return (
            "Se purga la válvula de muestreo, se llena la celda y se deja "
            "reposar unos cinco minutos antes de medir (muestreo: ST-CT-006)."
        )

    # ── Pasos 01 a 04 ───────────────────────────────────────────────────

    def _cargar_paso_fp(self, numero, paso_actual, contenedor, botones_paso):
        ventana = contenedor.winfo_toplevel()
        for atributo in ("_parpadeo_fp", "_parpadeo_foco_job"):
            job = getattr(self, atributo, None)
            if job is not None:
                try:
                    self.after_cancel(job)
                except tk.TclError:
                    pass
                setattr(self, atributo, None)
        if numero in (3, 4) and self.prueba_fp not in self._pruebas_fp():
            messagebox.showinfo(
                "Prueba no disponible",
                "Seleccione una prueba disponible en el paso 2 antes "
                "de abrir los diagramas y la medición.",
                parent=ventana,
            )
            return
        paso_actual.set(numero)
        for indice, boton in enumerate(botones_paso, start=1):
            boton["aplicar"](indice == numero)
        for hijo in contenedor.winfo_children():
            hijo.destroy()
        fondo = RA_VISTA_FONDO
        frame = tk.Frame(contenedor, bg=fondo)
        frame.pack(fill=tk.BOTH, expand=True)
        cuerpo = tk.Frame(frame, bg=fondo)
        cuerpo.pack(
            expand=True, fill="both", padx=28,
            pady=(12, 8) if numero == 3 else 18,
        )
        self._titulos_fp(cuerpo, numero)

        def ir(destino):
            self._cargar_paso_fp(
                destino, paso_actual, contenedor, botones_paso,
            )

        if numero == 1:
            self._formulario_fp(cuerpo, ir)
        elif numero == 2:
            self._tabla_fp(cuerpo, ir)
        elif numero == 3:
            self._diagramas_fp(cuerpo, ir)
        else:
            self._captura_fp(cuerpo)
        puerto = getattr(contenedor, "_puerto_fp", None)
        if puerto is not None:
            puerto.yview_moveto(0)

    def _titulos_fp(self, padre, numero):
        fondo = RA_VISTA_FONDO
        titulos = {
            1: "DATOS DEL EQUIPO",
            2: "SELECCIÓN DE PRUEBAS",
            3: "DIAGRAMAS DE BLOQUES",
            4: "CAPTURA DE LECTURAS",
        }
        subtitulos = {
            1: "Parámetros de placa y condiciones ambientales del equipo bajo prueba.",
            2: "Elija la prueba y revise su esquema de medición y conexión.",
            3: "Diagramas de medición y conexiones del equipo.",
            4: "Captura de lecturas y dictamen de la prueba.",
        }
        bloque = tk.Frame(padre, bg=fondo)
        bloque.pack(fill="x", pady=(0, 8 if numero >= 3 else 16))
        fila = tk.Frame(bloque, bg=fondo)
        fila.pack(fill="x")
        izquierda = tk.Frame(fila, bg=fondo)
        izquierda.pack(side="left", fill="x", expand=True)
        fila_titulo = tk.Frame(izquierda, bg=fondo)
        fila_titulo.pack(anchor="w")
        tk.Label(
            fila_titulo, text="Factor de Potencia",
            bg=fondo, fg="#1A202C", font=("Segoe UI", 26, "bold"),
        ).pack(side="left")
        pastilla = ctk.CTkFrame(
            fila_titulo, fg_color=FP_VISTA_PASTEL, corner_radius=12,
            border_width=1, border_color=FP_VISTA_PASTEL_BORDE,
        )
        pastilla.pack(side="left", padx=(12, 0))
        ctk.CTkLabel(
            pastilla, text="Modo Diagnóstico",
            text_color=FP_VISTA_VERDE_OSCURO, fg_color="transparent",
            font=ctk.CTkFont(family="Consolas", size=11, weight="bold"),
        ).pack(padx=10, pady=2)
        equipo_actual = self.datos_fp["tipo_equipo"].get().strip()
        tk.Label(
            izquierda, text=subtitulos[numero], bg=fondo, fg="#596573",
            font=("Segoe UI", 10), anchor="w",
        ).pack(anchor="w", pady=(4, 0))
        if numero != 1 and equipo_actual:
            tk.Label(
                izquierda, text=equipo_actual, bg=fondo, fg="#334155",
                font=("Segoe UI", 18, "bold"), anchor="w",
            ).pack(anchor="w", pady=(2, 0))
        insignia = ctk.CTkFrame(
            fila, fg_color=FP_VISTA_VERDE, corner_radius=10,
        )
        insignia.pack(side="right", anchor="n")
        ctk.CTkLabel(
            insignia, text=f"{numero:02d}",
            text_color="#ECFDF5", fg_color=FP_VISTA_VERDE_OSCURO,
            corner_radius=6,
            font=ctk.CTkFont(family="Consolas", size=20, weight="bold"),
        ).pack(side="left", padx=(10, 8), pady=8)
        ctk.CTkLabel(
            insignia, text=titulos[numero],
            text_color="#FFFFFF", fg_color="transparent",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
        ).pack(side="left", padx=(0, 14), pady=8)
        if numero in (3, 4):
            _barra_degradada_fp(bloque, fondo, pady=(12, 0))
        else:
            tk.Frame(bloque, bg=RA_VISTA_BORDE, height=2).pack(
                fill="x", pady=(12, 0),
            )

    def _pie_paso_fp(self, padre, numero, comando):
        """Botón SIGUIENTE y leyenda del módulo, como en RA."""
        fondo = RA_VISTA_FONDO
        tk.Frame(padre, bg=RA_VISTA_BORDE, height=1).pack(
            fill="x", pady=(16, 10),
        )
        fila_acciones = tk.Frame(padre, bg=fondo)
        fila_acciones.pack(fill="x")
        boton = _boton_relieve_ra(
            fila_acciones, "SIGUIENTE  →", comando, modo="verde",
        )
        boton.pack(side="right")
        tk.Label(
            padre,
            text="Ingeniería de pruebas de alta tensión  ·  Subestaciones eléctricas",
            bg=fondo, fg="#596573", font=("Consolas", 9),
        ).pack(side="bottom", anchor="w", pady=(12, 0))
        tk.Label(
            padre, text=f"Módulo {numero:02d} / 04",
            bg=fondo, fg="#4A5568", font=("Consolas", 9, "bold"),
        ).pack(side="bottom", anchor="e")

        def activar(_evento=None):
            boton.invoke()
            return "break"

        boton.bind("<Return>", activar, add="+")
        boton.bind("<KP_Enter>", activar, add="+")
        boton.bind("<FocusIn>", lambda _e=None: boton.marcar(True), add="+")
        boton.bind("<FocusOut>", lambda _e=None: boton.marcar(False), add="+")
        return boton

    def _formulario_fp(self, cuerpo, ir):
        datos = self.datos_fp
        fuente_opcion = ctk.CTkFont(family="Segoe UI", size=14)
        tarjeta = ctk.CTkFrame(
            cuerpo, fg_color=RA_VISTA_TARJETA, corner_radius=16,
            border_width=2, border_color=RA_VISTA_BORDE,
        )
        tarjeta.pack(fill="both", expand=True)
        _barra_degradada_fp(tarjeta, RA_VISTA_TARJETA, padx=12, pady=(10, 0))
        rejilla = ctk.CTkFrame(tarjeta, fg_color="transparent")
        rejilla.pack(fill="x", padx=18, pady=(6, 16))
        rejilla.grid_columnconfigure(1, weight=1)
        filas = {}

        def poner(clave, fila, texto, control):
            etiqueta = ctk.CTkLabel(
                rejilla, text=texto.upper(),
                font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
                text_color="#6F6A63", fg_color="transparent",
            )
            etiqueta.grid(row=fila, column=0, sticky="e", padx=(8, 18), pady=9)
            control.grid(row=fila, column=1, sticky="w", pady=9)
            filas[clave] = (etiqueta, control)
            return control

        def combo(variable, valores, ancho=380, comando=None):
            return ctk.CTkComboBox(
                rejilla, variable=variable, values=list(valores),
                state="readonly", width=ancho, height=36, corner_radius=8,
                fg_color=RA_VISTA_INPUT, border_color="#C5BCAC",
                border_width=2, button_color="#E4DDD2",
                button_hover_color="#D5CBBC", text_color="#1C1917",
                dropdown_fg_color="#FFFCF8", font=fuente_opcion,
                dropdown_font=fuente_opcion, command=comando,
            )

        def radios(variable, opciones, comando=None):
            marco = ctk.CTkFrame(rejilla, fg_color="transparent")
            marco._radios = []
            for texto, valor in opciones:
                radio = ctk.CTkRadioButton(
                    marco, text=texto, variable=variable, value=valor,
                    font=fuente_opcion, fg_color=FP_VISTA_VERDE,
                    hover_color=FP_VISTA_VERDE_OSCURO,
                    border_color="#C8C0B4", text_color="#1C1917",
                    command=comando,
                )
                radio.pack(side="left", padx=(0, 22))
                marco._radios.append(radio)
            return marco

        def entrada(variable):
            if not getattr(variable, "_sape_limite_5", False):
                def cortar(*_args, v=variable):
                    if len(v.get()) > 5:
                        v.set(v.get()[:5])
                variable.trace_add("write", cortar)
                variable._sape_limite_5 = True
            return ctk.CTkEntry(
                rejilla, textvariable=variable, width=72, height=36,
                corner_radius=8, fg_color=RA_VISTA_INPUT,
                border_color="#C5BCAC", border_width=2,
                text_color="#1C1917", font=fuente_opcion,
            )

        def actualizar(_valor=None):
            equipo = datos["tipo_equipo"].get()
            opciones = ARREGLOS_FP.get(equipo, ())
            combo_arreglo.configure(values=list(opciones))
            self._arreglo_fp()
            potencia = self._es_potencia_fp(equipo)
            instrumento = self._es_instrumento_fp(equipo)
            sin_aceite = "Apartarrayos" in equipo or "Cables" in equipo
            en_aceite = "Aceite" in datos["aislamiento"].get()
            visibles = {
                "arreglo": bool(opciones),
                "configuracion": potencia,
                "fase": self._lleva_fase_fp(equipo),
                "estado": not sin_aceite,
                "clase": "TCs" in equipo,
                "cable": "Cables" in equipo,
                "aislamiento": potencia or instrumento,
                "preservacion": potencia and en_aceite,
                "temp_aceite": not sin_aceite,
            }
            for clave, (etiqueta, control) in filas.items():
                if visibles.get(clave, True):
                    etiqueta.grid()
                    control.grid()
                else:
                    etiqueta.grid_remove()
                    control.grid_remove()

        combo_equipo = poner(
            "equipo", 0, "Tipo de equipo:",
            combo(datos["tipo_equipo"], EQUIPOS_FP, comando=actualizar),
        )
        combo_arreglo = poner(
            "arreglo", 1, "Arreglo de prueba:", combo(datos["arreglo"], ()),
        )
        poner("configuracion", 2, "Configuración:", radios(
            datos["configuracion"],
            (("Trifásico", "Trifásico"), ("Monofásico", "Monofásico")),
            comando=actualizar,
        ))
        poner("fase", 3, "Fase:", radios(
            datos["fase"], tuple((letra, letra) for letra in "ABC"),
        ))
        poner("estado", 4, "Condición:", radios(
            datos["estado"],
            (
                ("Puesta en servicio (nuevo)", "Puesta en servicio"),
                ("En operación", "En operación"),
            ),
        ))
        poner("clase", 5, "Clase del TC:", radios(
            datos["clase_kv"],
            (
                ("Menor de 115 kV", "Menor de 115 kV"),
                ("115 kV o mayor", "115 kV o mayor"),
            ),
        ))
        poner("cable", 6, "Aislamiento del cable:", combo(
            datos["aislamiento_cable"], [nombre for nombre, _ in TABLA9_FP],
        ))
        poner("aislamiento", 7, "Tipo de aislamiento:", radios(
            datos["aislamiento"],
            (
                ("Sumergido en Aceite", "Sumergido en Aceite"),
                ("Seco (Sólido)", "Seco"),
            ),
            comando=actualizar,
        ))
        poner("preservacion", 8, "Preservación (Tabla 4):", combo(
            datos["preservacion"], PRESERVACION_FP,
        ))
        entrada_aceite = poner(
            "temp_aceite", 9, "Temp. del aceite (°C):",
            entrada(datos["temp_aceite"]),
        )
        entrada_ambiente = poner(
            "temp_ambiente", 10, "Temp. ambiente (°C):",
            entrada(datos["temp_ambiente"]),
        )
        entrada_humedad = poner(
            "humedad", 11, "Humedad relativa (%):",
            entrada(datos["humedad"]),
        )
        actualizar()

        boton_siguiente = self._pie_paso_fp(cuerpo, 1, lambda: ir(2))
        campos = [combo_equipo, entrada_aceite, entrada_ambiente, entrada_humedad]

        def avanzar(indice):
            for siguiente in campos[indice + 1:]:
                try:
                    if siguiente.winfo_ismapped():
                        siguiente.focus_set()
                        return "break"
                except tk.TclError:
                    continue
            boton_siguiente.focus_set()
            return "break"

        for indice, campo in enumerate(campos):
            campo.bind("<Return>", lambda _e, i=indice: avanzar(i), add="+")
            campo.bind("<KP_Enter>", lambda _e, i=indice: avanzar(i), add="+")

    def _tabla_fp(self, cuerpo, ir):
        fondo = RA_VISTA_FONDO
        pruebas = self._pruebas_fp()
        previa = self.prueba_fp
        columnas = (
            ("selector", ""), ("prueba", "PRUEBA"), ("kv", "kV"),
            ("modo", "MODO"), ("hv", "ENERGIZAR (HV)"),
            ("ground", "GROUND"), ("guard", "GUARD"), ("ust", "UST"),
            ("medicion", "MIDE"),
        )
        color_th = {
            "prueba": "#334155", "kv": "#334155", "modo": FP_VISTA_VERDE_OSCURO,
            "hv": "#111827", "ground": "#DC2626", "guard": "#2563EB",
            "ust": "#0891B2", "medicion": "#EA580C",
        }
        # Fondo pastel del color de la columna: (fondo, texto, borde).
        pildoras = {
            "hv": ("#E5E7EB", "#111111", "#D1D5DB"),
            "ground": ("#FECACA", "#991B1B", "#FCA5A5"),
            "guard": ("#DBEAFE", "#1E40AF", "#BFDBFE"),
            "ust": ("#CFFAFE", "#155E75", "#A5F3FC"),
            "medicion": ("#FFEDD5", "#C2410C", "#FED7AA"),
        }
        fuente_th = (
            ("Segoe UI Black", 9)
            if "Segoe UI Black" in tkfont.families()
            else ("Segoe UI", 9, "bold")
        )
        panel = ctk.CTkFrame(
            cuerpo, fg_color="#FFFFFF", corner_radius=10,
            border_width=1, border_color="#E2E8F0",
        )
        panel.pack(fill="x", pady=(4, 4))
        _barra_degradada_fp(panel, "#FFFFFF", padx=10, pady=(8, 0))

        tabla = tk.Frame(panel, bg="#FFFFFF")
        tabla.pack(fill="x")
        pesos = (0, 0, 1, 1, 1, 2, 2, 2, 2, 3)
        minimos = (4, 50, 74, 60, 76, 120, 120, 110, 100, 150)
        for indice, (peso, minimo) in enumerate(zip(pesos, minimos)):
            tabla.grid_columnconfigure(indice, weight=peso, minsize=minimo)
        selector = tk.IntVar(value=0)
        filas = []
        punto_visible = {"on": True}
        seleccion = "#ECFDF5"

        def dibujar_led(lienzo, encendido, fondo_led, punto=True):
            lienzo.configure(bg=fondo_led)
            lienzo.delete("all")
            if encendido:
                lienzo.create_oval(
                    2, 2, 22, 22, outline="#10B981", width=2, fill="#FFFFFF",
                )
                if punto:
                    lienzo.create_oval(7, 7, 17, 17, outline="", fill="#10B981")
            else:
                lienzo.create_oval(
                    2, 2, 22, 22, outline="#94A3B8", width=2, fill="#F8FAFC",
                )

        def pintar_fila(indice, sobre=False):
            fila = filas[indice]
            elegido = selector.get() == indice
            fondo_fila = (
                seleccion if elegido else ("#F8FAFC" if sobre else "#FFFFFF")
            )
            fila["acento"].configure(bg="#10B981" if elegido else fondo_fila)
            for marco in fila["marcos"]:
                marco.configure(bg=fondo_fila)
            for etiqueta in fila["etiquetas"]:
                etiqueta.configure(bg=fondo_fila)
            dibujar_led(
                fila["led"], elegido, fondo_fila,
                punto_visible["on"] if elegido else True,
            )

        def parpadear_punto():
            self._parpadeo_fp = None
            indice = selector.get()
            if not 0 <= indice < len(filas):
                return
            led = filas[indice]["led"]
            try:
                if not led.winfo_exists():
                    return
                punto_visible["on"] = not punto_visible["on"]
                dibujar_led(led, True, seleccion, punto_visible["on"])
            except tk.TclError:
                return
            self._parpadeo_fp = self.after(420, parpadear_punto)

        def seleccionar(indice):
            self.prueba_fp = pruebas[indice]
            self.datos_fp["kv"].set(pruebas[indice]["kv"])
            selector.set(indice)
            punto_visible["on"] = True
            for i in range(len(filas)):
                pintar_fila(i)
            job = getattr(self, "_parpadeo_fp", None)
            if job is not None:
                try:
                    self.after_cancel(job)
                except tk.TclError:
                    pass
            self._parpadeo_fp = self.after(420, parpadear_punto)

        def celda(fila_grid, columna, alto, fondo_celda, borde, grosor):
            marco = tk.Frame(tabla, bg=fondo_celda, height=alto)
            marco.grid(row=fila_grid, column=columna, sticky="nsew")
            marco.pack_propagate(False)
            tk.Frame(marco, bg=borde, height=grosor).pack(
                side="bottom", fill="x",
            )
            return marco

        celda(0, 0, 46, "#F1F5F9", "#CBD5E1", 2)
        for indice, (clave, titulo) in enumerate(columnas, start=1):
            marco = celda(0, indice, 46, "#F1F5F9", "#CBD5E1", 2)
            if titulo:
                tk.Label(
                    marco, text=titulo, bg="#F1F5F9", fg=color_th[clave],
                    font=fuente_th,
                ).pack(expand=True)

        for indice_fila, prueba in enumerate(pruebas):
            valores = dict(prueba)
            if prueba.get("flotando"):
                valores["guard"] = f"{prueba['flotando']} flotando"
            elegir = lambda _evento=None, i=indice_fila: seleccionar(i)
            acento = celda(indice_fila + 1, 0, 50, "#FFFFFF", "#E2E8F0", 1)
            marcos, etiquetas = [], []
            widgets = {acento, *acento.winfo_children()}
            led = None
            for indice, (clave, _titulo) in enumerate(columnas, start=1):
                marco = celda(
                    indice_fila + 1, indice, 50, "#FFFFFF", "#E2E8F0", 1,
                )
                marcos.append(marco)
                widgets.add(marco)
                widgets.update(marco.winfo_children())
                marco.bind("<Button-1>", elegir)
                if clave == "selector":
                    led = tk.Canvas(
                        marco, width=24, height=24, bg="#FFFFFF",
                        highlightthickness=0, bd=0, cursor="hand2",
                    )
                    led.place(relx=0.5, rely=0.5, anchor="center")
                    led.bind("<Button-1>", elegir)
                    widgets.add(led)
                    continue
                texto = str(valores[clave])
                vacio = texto.strip() in ("", "-----", "---", "—", "-")
                if clave in pildoras and not vacio:
                    color_f, tinta, borde_badge = pildoras[clave]
                    pastilla = tk.Label(
                        marco, text=texto, bg=color_f, fg=tinta,
                        font=("Segoe UI", 10, "bold"),
                        padx=8, pady=3, cursor="hand2", anchor="center",
                        highlightthickness=1, highlightbackground=borde_badge,
                    )
                    pastilla.place(relx=0.5, rely=0.5, anchor="center")
                    pastilla.bind("<Button-1>", elegir)
                    widgets.add(pastilla)
                    continue
                if clave in pildoras:
                    etiqueta = tk.Label(
                        marco, text="—", bg="#FFFFFF", fg="#94A3B8",
                        font=("Segoe UI", 12, "bold"), cursor="hand2",
                    )
                elif clave == "prueba":
                    etiqueta = tk.Label(
                        marco, text=texto, bg="#FFFFFF", fg="#334155",
                        font=("Consolas", 12, "bold"), cursor="hand2",
                    )
                elif clave == "modo":
                    etiqueta = tk.Label(
                        marco, text=texto, bg="#FFFFFF",
                        fg=FP_VISTA_VERDE_OSCURO,
                        font=("Consolas", 11, "bold"), cursor="hand2",
                    )
                else:
                    etiqueta = tk.Label(
                        marco, text=texto, bg="#FFFFFF", fg="#475569",
                        font=("Consolas", 11), cursor="hand2",
                    )
                etiqueta.place(relx=0.5, rely=0.5, anchor="center")
                etiqueta.bind("<Button-1>", elegir)
                etiquetas.append(etiqueta)
                widgets.add(etiqueta)
            filas.append({
                "acento": acento, "marcos": marcos, "etiquetas": etiquetas,
                "led": led, "widgets": widgets,
            })

            def al_entrar(_evento=None, i=indice_fila):
                if selector.get() != i:
                    pintar_fila(i, sobre=True)

            def al_salir(evento, i=indice_fila):
                try:
                    actual = panel.winfo_containing(
                        evento.x_root, evento.y_root,
                    )
                except (tk.TclError, KeyError):
                    actual = None
                while actual is not None:
                    if actual in filas[i]["widgets"]:
                        return
                    actual = getattr(actual, "master", None)
                pintar_fila(i)

            for widget in widgets:
                widget.bind("<Enter>", al_entrar)
                widget.bind("<Leave>", al_salir)

        inicial = pruebas.index(previa) if previa in pruebas else 0
        if pruebas:
            seleccionar(inicial)

        tk.Frame(panel, bg="#E2E8F0", height=1).pack(fill="x")
        pie = tk.Frame(panel, bg="#FAFBFC")
        pie.pack(fill="x")
        etiqueta_nota = tk.Label(
            pie, text=self._nota_tabla_fp(), bg="#FAFBFC", fg="#64748B",
            font=("Segoe UI", 9, "italic"),
            wraplength=860, justify="left", anchor="w",
        )
        etiqueta_nota.pack(fill="x", padx=24, pady=16)

        def ajustar_nota(_evento=None):
            ancho = panel.winfo_width() - 64
            if ancho > 240:
                etiqueta_nota.configure(wraplength=ancho)

        panel.bind("<Configure>", ajustar_nota, add="+")
        self._pie_paso_fp(cuerpo, 2, lambda: ir(3))

    def _texto_bloques_fp(self, modo):
        """Diagrama de bloques de SAPE_1 para transformadores y reactores."""
        prueba = self.prueba_fp
        if not prueba:
            return "No hay prueba especificada."
        ruta = r"c:\Users\LapOne MX\Documents\Programacion Modo JEDI\S. A. P. E"
        if ruta not in sys.path:
            sys.path.insert(0, ruta)
        import SAPE_1 as sape1
        equipo = self.datos_fp["tipo_equipo"].get()
        if "Autotransformadores" in equipo:
            tipo = 3
        elif "Reactores" in equipo:
            tipo = 4
        elif "3 Devanados" in equipo:
            tipo = 2
        else:
            tipo = 1
        mono = self.datos_fp["configuracion"].get() == "Monofásico"
        cfg = {
            "tipo_equipo": tipo,
            "es_instrumento": False,
            "es_monofasico": mono or tipo == 4,
            "conexion_seleccionada": (
                "Monofásico" if mono or tipo == 4 else "Trifásico"
            ),
            "tpc_formato": "campo",
            "varias_secciones": True,
        }

        def limpio(valor):
            return "" if valor in ("", "-----", "---") else valor

        prueba_proc = (
            prueba["prueba"], limpio(prueba["hv"]), limpio(prueba["ground"]),
            limpio(prueba["guard"]), limpio(prueba["ust"]), prueba["medicion"],
        )
        lineas = sape1._fp_contenido_diagrama_bloques(
            cfg, prueba["medicion"], prueba_proc, modo,
        )
        # Línea más larga entre cada devanado y la capacitancia que los une:
        # un renglón de cable antes de la placa superior y otro después de
        # la inferior.
        alargadas = []
        for linea in lineas:
            plana = _RE_ANSI_BLOQUE.sub("", linea)
            placa = next((g for g in "┴┬" if f"─{g}─" in plana), None)
            libre = (
                placa is not None
                and not any(g in plana for g in "┌└┐┘")
                and plana.count("│") <= 2
            )
            if not libre:
                alargadas.append(linea)
                continue
            columna = plana.index(f"─{placa}─") + 1
            cable = [
                "│" if g == "│" or i == columna else " "
                for i, g in enumerate(plana)
            ]
            cable = "".join(cable).rstrip()
            if placa == "┴":
                alargadas += [cable, linea]
            else:
                alargadas += [linea, cable]
        lineas = alargadas
        texto = "\n".join(lineas)
        if tipo == 3:
            # SAPE_1 rotula CHX y CHXY. ST-CT-002 trata a H+X como un solo
            # devanado: CH a tierra y CHY contra el terciario.
            texto = texto.replace("CHXY", "CHY ").replace("CHX", "CH ")
        # Líneas en el mismo gris pizarra de RA (#334155).
        texto = texto.replace(
            "\x1b[38;2;34;211;238m", "\x1b[38;2;51;65;85m",
        )
        return texto.replace(
            "\x1b[1;38;2;0;80;255m", "\x1b[1;38;2;51;65;85m",
        )

    def _leyenda_fp(self, prueba):
        """Renglones de la leyenda: (medición, conexiones)."""
        equipo = self.datos_fp["tipo_equipo"].get()
        medicion = str(prueba.get("medicion", ""))
        filas_medicion = []
        if self._es_potencia_fp(equipo):
            descripciones = dict(DESCRIPCIONES_FP)
            if "Autotransformadores" in equipo:
                descripciones["CH"] = (
                    "Aislamiento entre los devanados interconectados (H+X) "
                    "y tierra"
                )
                descripciones["CHY"] = (
                    "Aislamiento entre los devanados interconectados (H+X) "
                    "y el terciario (Y)"
                )
            for codigo in medicion.split("+"):
                codigo = codigo.strip()
                filas_medicion.append((
                    codigo,
                    descripciones.get(codigo, "Aislamiento medido"),
                    FP_VISTA_MEDICION,
                ))
        else:
            descripcion = DESCRIPCIONES_FP.get(medicion)
            if descripcion is None:
                if "Apartarrayos" in equipo:
                    descripcion = "Sección o secciones medidas del apartarrayos"
                elif "TPCs" in equipo:
                    descripcion = "Capacitor o terminal medido del TPC"
                elif "Cables" in equipo:
                    descripcion = "Aislamiento del conductor medido"
                elif "Aceite" in equipo:
                    descripcion = "Muestra de aceite dentro de la celda"
                else:
                    descripcion = "Aislamiento medido en esta prueba"
            filas_medicion.append((medicion, descripcion, FP_VISTA_MEDICION))
        filas_conexion = []
        for codigo, campo, texto, color in (
            ("HV", "hv", "Cable de alta tensión; energiza", "#111827"),
            ("GROUND", "ground", "Cable de baja a tierra", "#EF4444"),
            ("GUARD", "guard", "Cable de baja a guarda", "#2563EB"),
            ("UST", "ust", "Cable de baja en UST", "#0891B2"),
            ("FLOTANDO", "flotando", "Terminal sin conectar", "#94A3B8"),
        ):
            valor = str(prueba.get(campo, "")).strip()
            if valor and valor not in ("-----", "---"):
                filas_conexion.append((codigo, f"{texto}: {valor}", color))
        return filas_medicion, filas_conexion

    def _diagramas_fp(self, cuerpo, ir):
        prueba = self.prueba_fp or {}
        equipo = self.datos_fp["tipo_equipo"].get().strip()
        arreglo = self._arreglo_fp()
        topo = _topologia_fp(equipo, arreglo)
        fila_pie = tk.Frame(cuerpo, bg="#F6F3EB")
        fila_pie.pack(side="bottom", fill="x", pady=(8, 0))
        visor = tk.Frame(
            cuerpo, bg="#FFFFFF",
            highlightbackground="#E5E0D5", highlightthickness=1,
        )
        visor.pack(fill="both", expand=True, pady=(0, 4))
        barra_y = tk.Scrollbar(visor, orient="vertical")
        barra_x = tk.Scrollbar(visor, orient="horizontal")
        puerto = tk.Canvas(
            visor, bg="#FFFFFF", highlightthickness=0, bd=0, height=470,
            yscrollcommand=barra_y.set, xscrollcommand=barra_x.set,
        )
        barra_y.configure(command=puerto.yview)
        barra_x.configure(command=puerto.xview)
        barra_x.pack(side="bottom", fill="x")
        barra_y.pack(side="right", fill="y")
        puerto.pack(side="left", fill="both", expand=True)
        puerto._scroll_propio = puerto
        seccion = tk.Frame(puerto, bg="#FFFFFF")
        puerto.create_window((0, 0), window=seccion, anchor="nw")
        seccion.bind(
            "<Configure>",
            lambda _e=None: puerto.configure(
                scrollregion=puerto.bbox("all") or (0, 0, 1, 1),
            ),
        )
        filas_medicion, filas_conexion = self._leyenda_fp(prueba)

        def montar_panel_fp(modo):
            panel = tk.Frame(seccion, bg="#FFFFFF")
            panel.pack(anchor="nw", padx=12, pady=(4, 8))
            columna = tk.Frame(panel, bg="#FFFFFF")
            columna.grid(row=0, column=0, sticky="nw")
            leyenda = tk.Frame(panel, bg="#FFFFFF")
            leyenda.grid(row=0, column=1, sticky="nw", padx=(18, 22), pady=(24, 16))
            # La leyenda parpadea al ritmo del diagrama, como en RA.
            oyentes = []

            def avisar(fase):
                for oir in oyentes:
                    oir(fase)

            tk.Label(
                columna,
                text="MEDICIÓN" if modo == "mide" else "CONEXIONES",
                bg="#FFFFFF", fg="#DC2626",
                font=("Consolas", 22, "bold"), anchor="w",
            ).pack(anchor="nw", padx=6, pady=(0, 4))
            if topo is None:
                lienzo_bloques = _LienzoBloquesNeon(columna)
                lienzo_bloques._oyentes_parpadeo = oyentes
                lienzo_bloques._es_fp = True
                lienzo_bloques._color_medicion = FP_VISTA_MEDICION
                lienzo_bloques._alto_maximo = max(
                    280, lienzo_bloques.winfo_screenheight() - 420,
                )
                lienzo_bloques.pack(anchor="nw")
                lienzo_bloques._titulo = (
                    "MEDICIÓN" if modo == "mide" else "CONEXIONES"
                )
                lienzo_bloques._ground_en_tanque = (
                    modo == "conexiones"
                    and _fp_ground_marca_tanque(prueba.get("ground", ""))
                )
                lienzo_bloques.cargar(self._texto_bloques_fp(modo))
            else:
                avisar("MEDICION" if modo == "mide" else "CONEXIONES")
                _dibujar_esquema_fp(
                    columna, topo, prueba, modo, al_parpadear=avisar,
                ).pack(anchor="nw")

            renglones = filas_medicion if modo == "mide" else filas_conexion
            fila = 0
            for codigo, descripcion, color in renglones:
                badge = ctk.CTkLabel(
                    leyenda, text=codigo, fg_color=color,
                    text_color="#FFFFFF", corner_radius=4,
                    width=max(78, len(codigo) * 9 + 18), height=26,
                    anchor="center",
                    font=ctk.CTkFont(family="Consolas", size=12, weight="bold"),
                )
                badge.grid(row=fila, column=0, sticky="w", pady=6, padx=(0, 14))

                def al_fase(
                    fase, badge=badge, color=color, es_medida=modo == "mide",
                ):
                    try:
                        if not badge.winfo_exists():
                            return
                    except tk.TclError:
                        return
                    apagado = (
                        fase is None if es_medida
                        else fase == "CONEXIONES_OFF"
                    )
                    if apagado:
                        badge.configure(fg_color="#ECFDF5", text_color=color)
                    else:
                        badge.configure(fg_color=color, text_color="#FFFFFF")

                oyentes.append(al_fase)
                tk.Label(
                    leyenda, text=descripcion, bg="#FFFFFF", fg="#334155",
                    font=("Segoe UI", 11), anchor="w", justify="left",
                    wraplength=250,
                ).grid(row=fila, column=1, sticky="w", pady=6)
                fila += 1

        for modo_diag in ("mide", "conexiones"):
            try:
                montar_panel_fp(modo_diag)
            except Exception:
                import traceback
                tk.Label(
                    seccion, text=traceback.format_exc()[-900:],
                    bg="#FFFFFF", fg="#B91C1C", font=("Consolas", 9),
                    justify="left", anchor="w",
                ).pack(anchor="w", padx=12, pady=8)

        tk.Label(
            fila_pie, text="Módulo 03 / 04", bg="#F6F3EB",
            fg="#64748B", font=("Segoe UI", 9, "bold"),
        ).pack(side="left")
        boton = _boton_relieve_ra(
            fila_pie, "SIGUIENTE  →", lambda: ir(4), modo="verde",
        )
        boton.pack(side="right")

        def activar(_evento=None):
            boton.invoke()
            return "break"

        boton.bind("<Return>", activar, add="+")
        boton.bind("<KP_Enter>", activar, add="+")
        boton.bind("<FocusIn>", lambda _e=None: boton.marcar(True), add="+")
        boton.bind("<FocusOut>", lambda _e=None: boton.marcar(False), add="+")

    # ── Cálculo y dictamen ──────────────────────────────────────────────

    def _leer_fp(self, texto):
        bruto = (texto or "").strip().replace(",", ".")
        if not bruto:
            return None
        try:
            valor = float(bruto)
        except ValueError:
            return None
        if not math.isfinite(valor):
            return None
        return valor

    def _kt_fp(self, temp=None):
        """Factor de corrección a 20 °C y la tabla de donde sale."""
        datos = self.datos_fp
        equipo = datos["tipo_equipo"].get()
        if "Apartarrayos" in equipo:
            return 1.0, "sin corrección: se evalúan las pérdidas"
        if "Cables" in equipo:
            return 1.0, "sin corrección: Tabla 9"
        aceite = "Aceite" in equipo
        if not aceite and "Aceite" not in datos["aislamiento"].get():
            return 1.0, "sin corrección: aislamiento seco"
        if temp is None:
            temp = self._leer_fp(datos["temp_aceite"].get())
        if temp is None:
            return None, ""
        if self._es_instrumento_fp(equipo):
            return _interpolar_fp(TABLA6_FP, temp), "Tabla 6"
        columna = 1
        preservacion = datos["preservacion"].get()
        if not aceite and preservacion in PRESERVACION_FP:
            columna = PRESERVACION_FP.index(preservacion) + 1
        return (
            _interpolar_fp(TABLA4_FP, temp, columna),
            f"Tabla 4, columna {columna}",
        )

    def _evaluar_fp(self, kv, ma, watts, temp=None, prueba=None):
        """%FP, corrección a 20 °C y dictamen según ST-CT-002."""
        datos = self.datos_fp
        equipo = datos["tipo_equipo"].get()
        prueba = prueba or self.prueba_fp or {}
        kt, tabla = self._kt_fp(temp)
        if kt is None:
            return None
        va = kv * ma
        fp = 100.0 * watts / va
        fp20 = fp * kt
        mw = watts * 1000.0
        cap = ma * 1_000_000.0 / (2 * math.pi * 60 * kv)
        nuevo = datos["estado"].get() == "Puesta en servicio"
        if "Apartarrayos" in equipo:
            limite = 16.0 * (kv / 2.5) ** 2
            criterio = (
                f"Pérdidas máximas: 16 mW a 2.5 kV y 256 mW a 10 kV. "
                f"A {kv:g} kV el límite es {limite:.0f} mW."
            )
            if mw <= limite:
                estado = "ACEPTADO"
                frase = (
                    "Las pérdidas están dentro del límite. Compárelas con el "
                    "historial y con equipos similares: pérdidas más bajas de "
                    "lo normal indican resistores shunt rotos o circuito "
                    "abierto."
                )
            else:
                estado = "RECHAZADO"
                frase = (
                    "Las pérdidas rebasan el límite: humedad, suciedad, gaps "
                    "corroídos o porcelana quebrada."
                )
        elif "Cables" in equipo:
            nombre = datos["aislamiento_cable"].get()
            limite = dict(TABLA9_FP).get(nombre, 1.0)
            criterio = f"Tabla 9. {nombre}: hasta {limite:g} %."
            if fp20 <= limite:
                estado = "ACEPTADO"
                frase = "El factor de potencia está dentro de la guía de la Tabla 9."
            else:
                estado = "INVESTIGAR"
                frase = (
                    "El factor de potencia rebasa la guía de la Tabla 9. "
                    "Compare con las mediciones iniciales del cable."
                )
        elif "Aceite" in equipo:
            criterio = "Aceite a 20 °C: nuevo hasta 0.05 %, bueno hasta 0.50 %."
            if fp20 <= 0.05:
                estado, frase = "ACEPTADO", "Aceite con valor de aceite nuevo."
            elif fp20 <= 0.5:
                estado, frase = "ACEPTADO", "Aceite en buenas condiciones."
            else:
                estado = "INVESTIGAR"
                frase = (
                    "Arriba de 0.50 %: aceite deteriorado o contaminado. "
                    "Verifique que la muestra sea representativa."
                )
        elif "TCs" in equipo:
            mayor = datos["clase_kv"].get().startswith("115")
            limite = 0.5 if mayor else 1.0
            criterio = (
                f"TC {'de 115 kV o mayor' if mayor else 'menor de 115 kV'}: "
                f"%FP a 20 °C hasta {limite:g} %."
            )
            if fp20 <= limite:
                estado = "ACEPTADO"
                frase = "El factor de potencia corregido cumple el límite del TC."
            else:
                estado = "RECHAZADO"
                frase = (
                    "El factor de potencia corregido rebasa el límite del TC. "
                    "Consulte el historial y los datos del fabricante."
                )
        elif "TPCs" in equipo:
            criterio = (
                "TPC: alrededor de 0.25 % cuando es nuevo; con 0.5 % debe "
                "retirarse del servicio. La capacitancia se compara con la "
                "de placa (Tabla 5)."
            )
            if fp20 >= 0.5:
                estado = "RECHAZADO"
                frase = "Factor de potencia de 0.5 % o mayor: retirar del servicio."
            elif fp20 > 0.25:
                estado = "INVESTIGAR"
                frase = (
                    "Arriba del valor de un TPC nuevo (0.25 %). Vigile la "
                    "tendencia y la variación de la capacitancia."
                )
            else:
                estado = "ACEPTADO"
                frase = "Factor de potencia dentro del valor de un TPC nuevo."
        elif "TPs" in equipo:
            criterio = (
                "TP inductivo: ST-CT-002 no fija un límite numérico. Las "
                "pruebas cruzadas 3 y 4 deben dar lecturas iguales y el "
                "factor de potencia debe ser bajo."
            )
            if watts < 0:
                estado = "INVESTIGAR"
                frase = (
                    "Lectura negativa en la prueba cruzada: posible devanado "
                    "de alta tensión abierto."
                )
            else:
                estado = "REGISTRADO"
                frase = (
                    "Compare esta lectura con la prueba completa, con las "
                    "cruzadas de comprobación y con el historial del equipo."
                )
        else:
            criterio = (
                "Nuevo: menor de 0.5 % a 20 °C. En operación: de 0.5 % a "
                "1.0 %. Arriba de 1.0 % se investiga."
            )
            if fp20 <= 0.5:
                estado = "ACEPTADO"
                frase = "Aislamiento en excelentes condiciones."
            elif fp20 <= 1.0:
                if nuevo:
                    estado = "INVESTIGAR"
                    frase = (
                        "Rebasa el 0.5 % que se acepta en un equipo que "
                        "entra por primera vez en operación."
                    )
                else:
                    estado = "ACEPTADO"
                    frase = "Valor aceptable para un equipo en operación."
            else:
                estado = "INVESTIGAR"
                frase = (
                    "Arriba de 1.0 %: revise el aceite aislante, las "
                    "boquillas y agentes externos, y la estadística de años "
                    "anteriores. Si el valor va en aumento, programe "
                    "mantenimiento mayor."
                )
        return {
            "estado": estado, "frase": frase, "criterio": criterio,
            "fp": fp, "fp20": fp20, "kt": kt, "tabla": tabla,
            "va": va, "mva": va * 1000.0, "mw": mw, "watts": watts,
            "cap": cap, "kv": kv, "ma": ma,
            "ma10": ma * 10.0 / kv, "w10": watts * (10.0 / kv) ** 2,
            "apartarrayos": "Apartarrayos" in equipo,
            "limite_mw": 16.0 * (kv / 2.5) ** 2,
        }

    def _resultado_fp(self, padre=None):
        """Dictamen de las lecturas capturadas en el paso 4."""
        datos = self.datos_fp
        padre = padre or self.winfo_toplevel()
        equipo = datos["tipo_equipo"].get()
        kt, _tabla = self._kt_fp()
        if kt is None:
            messagebox.showerror(
                "Falta la temperatura",
                "Escriba la temperatura del aceite en el paso 1. "
                "Sin ella no se corrige el %FP a 20 °C.",
                parent=padre,
            )
            return None
        kv = self._leer_fp(datos["kv"].get())
        ma = self._leer_fp(datos["ma"].get())
        watts = self._leer_fp(datos["watts"].get())
        if kv is None or kv <= 0 or kv > 12:
            messagebox.showerror(
                "Tensión",
                "La tensión de prueba va de más de 0 hasta 12 kV.",
                parent=padre,
            )
            return None
        if ma is None or ma <= 0 or watts is None:
            messagebox.showerror(
                "Lecturas",
                "Escriba la corriente en mA y las pérdidas en Watts.",
                parent=padre,
            )
            return None
        if watts < 0 and "TPs" not in equipo:
            messagebox.showerror(
                "Lecturas",
                "Las pérdidas no pueden ser negativas en este equipo.",
                parent=padre,
            )
            return None
        resultado = self._evaluar_fp(kv, ma, watts)
        prueba = self.prueba_fp or {}
        identidad = equipo
        arreglo = self._arreglo_fp()
        if arreglo:
            identidad += f". {arreglo}"
        if self._es_potencia_fp(equipo):
            identidad += f". {datos['configuracion'].get()}"
        if self._lleva_fase_fp(equipo):
            identidad += f". Fase {datos['fase'].get()}"
        temp = datos["temp_aceite"].get().strip()
        resultado["descripcion"] = (
            f"{identidad}. Prueba {prueba.get('prueba', '—')} "
            f"({prueba.get('modo', '—')}), mide {prueba.get('medicion', '—')}. "
            + (f"Aceite {temp} °C. " if temp else "")
            + f"Kt = {resultado['kt']:.3f} ({resultado['tabla']}). "
            f"{kv:g} kV, {ma:.3f} mA, {watts:.4f} W. "
            f"%FP medido = {resultado['fp']:.3f} %. "
            f"%FP a 20 °C = {resultado['fp20']:.3f} %. "
            f"Capacitancia ≈ {resultado['cap']:.1f} pF. "
            f"{resultado['criterio']} {resultado['frase']}"
        )
        return resultado

    def _nota_criterio_fp(self):
        """Criterio que se aplica antes de calcular el dictamen."""
        equipo = self.datos_fp["tipo_equipo"].get()
        prueba = self.prueba_fp or {}
        base = (
            f"Prueba {prueba.get('prueba', '—')} · {prueba.get('modo', '')} · "
            f"mide {prueba.get('medicion', '—')}.  "
        )
        if "Apartarrayos" in equipo:
            return base + (
                "Se evalúan las pérdidas: máximo 16 mW a 2.5 kV o 256 mW "
                "a 10 kV."
            )
        if "Cables" in equipo:
            return base + "Se compara el %FP contra la Tabla 9."
        if "Aceite" in equipo:
            return base + "Aceite a 20 °C: nuevo ≤ 0.05 %, bueno ≤ 0.50 %."
        if "TCs" in equipo:
            return base + (
                "TC menor de 115 kV: hasta 1.0 %. De 115 kV o mayor: hasta "
                "0.5 %. Ambos a 20 °C (Tabla 6)."
            )
        if "TPCs" in equipo:
            return base + (
                "TPC nuevo: 0.25 %. Con 0.5 % se retira del servicio "
                "(Tabla 6 y Tabla 5)."
            )
        if "TPs" in equipo:
            return base + (
                "Sin límite numérico: se comparan la prueba completa y las "
                "cruzadas de comprobación (Tabla 6)."
            )
        return base + (
            "Nuevo: menor de 0.5 %. En operación: de 0.5 % a 1.0 %. Arriba "
            "de 1.0 % se investiga. Todo a 20 °C (Tabla 4)."
        )

    def _montar_correccion_fp(self, padre):
        """Panel de Kt y semáforo del aislamiento, como el de RA."""
        datos = self.datos_fp
        panel = tk.Frame(padre, bg=RA_VISTA_PANEL)
        panel.pack(fill="x")
        fila_kt = tk.Frame(panel, bg=RA_VISTA_PANEL)
        fila_kt.pack(fill="x", padx=16, pady=(14, 8))
        tk.Label(
            fila_kt, text="CORRECCIÓN ST-CT-002", bg=RA_VISTA_PANEL,
            fg=FP_VISTA_VERDE_CLARO, font=("Consolas", 10, "bold"),
        ).pack(side="left")
        tk.Label(
            fila_kt, text="Ref: 20°C", bg="#1F2937", fg="#9CA3AF",
            font=("Consolas", 9),
        ).pack(side="right")
        tk.Frame(panel, bg="#374151", height=1).pack(fill="x", padx=16)
        cuerpo_kt = tk.Frame(panel, bg=RA_VISTA_PANEL)
        cuerpo_kt.pack(fill="x", padx=16, pady=(12, 8))
        tk.Label(
            cuerpo_kt, text="Factor de Corrección  Kt:",
            bg=RA_VISTA_PANEL, fg="#D1D5DB", font=("Segoe UI", 10),
        ).pack(side="left")
        kt, tabla = self._kt_fp()
        tk.Label(
            cuerpo_kt, text="—" if kt is None else f"{kt:.2f}",
            bg=RA_VISTA_PANEL, fg=FP_VISTA_VERDE_CLARO,
            font=("Consolas", 28, "bold"),
        ).pack(side="right")
        caja = tk.Frame(panel, bg="#111827")
        caja.pack(fill="x", padx=16, pady=(0, 8))
        temp = datos["temp_aceite"].get().strip()
        for rotulo, valor, color, relleno in (
            ("Ecuación usada:", "%FP20 = %FP × Kt", "#E5E7EB", (8, 2)),
            ("Tabla:", tabla or "—", "#E5E7EB", (2, 2)),
            (
                "Temp. del aceite:", f"{temp} °C" if temp else "—",
                "#FBBF24", (2, 8),
            ),
        ):
            fila = tk.Frame(caja, bg="#111827")
            fila.pack(fill="x", padx=10, pady=relleno)
            tk.Label(
                fila, text=rotulo, bg="#111827", fg="#9CA3AF",
                font=("Consolas", 9),
            ).pack(side="left")
            tk.Label(
                fila, text=valor, bg="#111827", fg=color,
                font=("Consolas", 9, "bold"), wraplength=200, justify="right",
            ).pack(side="right")
        if kt is None:
            fondo_aviso, tinta_aviso = "#451A03", "#FDE68A"
            texto_aviso = (
                "Falta la temperatura del aceite. Captúrela en el paso 1 "
                "para corregir el factor de potencia a 20 °C."
            )
        else:
            fondo_aviso, tinta_aviso = "#052E16", "#BBF7D0"
            texto_aviso = (
                "Condiciones registradas. Capture las lecturas y pulse "
                "CALCULAR."
            )
        aviso = tk.Label(
            panel, text=texto_aviso, bg=fondo_aviso, fg=tinta_aviso,
            font=("Segoe UI", 9), justify="left", anchor="nw", wraplength=300,
        )
        aviso.pack(fill="x", padx=16, pady=(0, 10))

        panel_estado = tk.Frame(panel, bg=RA_VISTA_PANEL)
        panel_estado.pack(fill="x", padx=16, pady=(4, 16))
        tk.Label(
            panel_estado, text="ESTADO DEL AISLAMIENTO",
            bg=RA_VISTA_PANEL, fg=FP_VISTA_VERDE_CLARO,
            font=("Consolas", 9, "bold"), anchor="w",
        ).pack(fill="x", pady=(0, 8))
        luces = tk.Frame(panel_estado, bg=RA_VISTA_PANEL, height=108)
        luces.pack(fill="x", pady=(0, 10))
        luces.pack_propagate(False)

        def foto_emoji(emoji):
            from PIL import Image, ImageDraw, ImageFont, ImageTk
            fuente = ImageFont.truetype(r"C:\Windows\Fonts\seguiemj.ttf", 52)
            sonda = ImageDraw.Draw(Image.new("RGBA", (4, 4)))
            caja_e = sonda.textbbox(
                (0, 0), emoji, font=fuente, embedded_color=True,
            )
            imagen = Image.new(
                "RGBA",
                (caja_e[2] - caja_e[0] + 4, caja_e[3] - caja_e[1] + 4),
                (0, 0, 0, 0),
            )
            ImageDraw.Draw(imagen).text(
                (2 - caja_e[0], 2 - caja_e[1]),
                emoji, font=fuente, embedded_color=True,
            )
            contenido = imagen.getbbox()
            if contenido:
                imagen = imagen.crop(contenido)
            foto = ImageTk.PhotoImage(imagen)
            vacio = tk.PhotoImage(width=foto.width(), height=foto.height())
            return foto, vacio

        focos = {}
        for indice, (clave, nombre, emoji) in enumerate((
            ("normal", "NORMAL", "✅"),
            ("precaucion", "PRECAUCIÓN", "⚠️"),
            ("alerta", "ALERTA", "❌"),
        )):
            luces.columnconfigure(indice, weight=1, uniform="focos")
            celda = tk.Frame(luces, bg="#1F2937", width=96, height=100)
            celda.grid(row=0, column=indice, sticky="nsew", padx=4)
            celda.grid_propagate(False)
            foto, vacio = foto_emoji(emoji)
            punto = tk.Label(celda, image=foto, bg="#1F2937", bd=0)
            punto.pack(pady=(10, 0))
            punto._foto = foto
            punto._vacio = vacio
            punto._emoji = emoji
            nombre_lbl = tk.Label(
                celda, text=nombre, bg="#1F2937", fg="#E5E7EB",
                font=("Segoe UI", 8, "bold"), height=1,
            )
            nombre_lbl.pack(pady=(4, 0))
            focos[clave] = (celda, punto, nombre_lbl)
        luces.rowconfigure(0, weight=1)
        datos_txt = tk.Text(
            panel_estado, bg=RA_VISTA_PANEL, fg="#E5E7EB",
            font=("Segoe UI", 9), wrap="word", height=2, width=40,
            bd=0, highlightthickness=0, padx=2, pady=2, cursor="arrow",
        )
        datos_txt.pack(fill="both", expand=True, pady=(0, 4))
        datos_txt.configure(state="disabled")
        # El semáforo usa el mismo mecanismo de parpadeo que RA.
        self._focos_ieee = focos
        self._aviso_ieee = aviso
        self._datos_ieee = datos_txt
        self._nivel_foco_ieee = None

    def _captura_fp(self, cuerpo):
        ventana = cuerpo.winfo_toplevel()
        datos = self.datos_fp
        equipo = datos["tipo_equipo"].get().strip()
        apartarrayos = "Apartarrayos" in equipo
        columna_kt = tk.Frame(cuerpo, bg=RA_VISTA_PANEL, width=360)
        columna_kt.pack(side="right", fill="both", padx=(18, 0))
        tk.Frame(columna_kt, bg=RA_VISTA_PANEL, width=346, height=1).pack()
        cuerpo_col = tk.Frame(columna_kt, bg=RA_VISTA_PANEL)
        cuerpo_col.pack(fill="both", expand=True)
        self._montar_correccion_fp(cuerpo_col)

        nota_criterio = tk.Label(
            cuerpo, text=self._nota_criterio_fp(),
            bg=RA_VISTA_FONDO, fg="#475569", font=("Segoe UI", 10),
            justify="left", anchor="w", wraplength=500,
        )
        nota_criterio.pack(fill="x", pady=(0, 6))
        nota_criterio.bind(
            "<Configure>",
            lambda evento: nota_criterio.configure(
                wraplength=max(evento.width - 8, 240),
            ),
        )

        barra = ctk.CTkFrame(cuerpo, fg_color="#F1F5F9", corner_radius=10)
        barra.pack(fill="x", pady=(6, 0))
        fila_campos = tk.Frame(barra, bg="#F1F5F9")
        fila_campos.pack(anchor="w", padx=12, pady=(12, 0))
        entradas = []
        for rotulo, clave in (
            ("Tensión (kV):", "kv"),
            ("Corriente (mA):", "ma"),
            ("Pérdidas (W):", "watts"),
        ):
            columna_campo = tk.Frame(fila_campos, bg="#F1F5F9")
            columna_campo.pack(side="left", anchor="n", padx=(0, 8))
            ctk.CTkLabel(
                columna_campo, text=rotulo,
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="#334155",
            ).pack(anchor="w")
            entrada = ctk.CTkEntry(
                columna_campo, textvariable=datos[clave],
                placeholder_text="Ingrese valor...", width=150,
            )
            entrada.pack(anchor="w", pady=(6, 0))
            entradas.append(entrada)
        # Al cambiar de prueba se cargan sus lecturas guardadas (o se limpia).
        clave_actual = self._clave_lectura_fp(self.prueba_fp or {})
        if getattr(self, "_clave_captura_fp", None) != clave_actual:
            self._clave_captura_fp = clave_actual
            guardada = self._lectura_guardada_fp(self.prueba_fp)
            datos["kv"].set(guardada.get("kV") or datos["kv"].get())
            datos["ma"].set(guardada.get("mA", ""))
            datos["watts"].set(guardada.get("W", ""))
        fila_botones = tk.Frame(barra, bg="#F1F5F9")
        fila_botones.pack(anchor="w", padx=12, pady=(8, 12))
        fuente_boton = tkfont.Font(family="Consolas", size=11, weight="bold")
        boton_calcular = _boton_relieve_ra(
            fila_botones, "CALCULAR", lambda: self._calcular_fp(ventana),
            ancho=fuente_boton.measure("CALCULAR") + 28,
            modo="diagnostico_verde", fondo="#F1F5F9",
            alto_caja=28, alto_lienzo=40, fuente_nombre="Consolas",
        )
        boton_calcular.pack(side="left")
        _boton_relieve_ra(
            fila_botones, "GUARDAR", lambda: self._guardar_fp(ventana),
            ancho=fuente_boton.measure("GUARDAR") + 28,
            modo="diagnostico_verde", fondo="#F1F5F9",
            alto_caja=28, alto_lienzo=40, fuente_nombre="Consolas",
        ).pack(side="left", padx=(8, 0))

        def al_enter(indice):
            def _saltar(_evento=None):
                if indice + 1 < len(entradas):
                    entradas[indice + 1].focus_set()
                else:
                    boton_calcular.focus_set()
                return "break"
            return _saltar

        for indice, entrada in enumerate(entradas):
            for widget in (entrada, *entrada.winfo_children()):
                widget.bind("<Return>", al_enter(indice), add="+")
                widget.bind("<KP_Enter>", al_enter(indice), add="+")

        def activar_calcular(_evento=None):
            boton_calcular.invoke()
            return "break"

        boton_calcular.bind("<Return>", activar_calcular, add="+")
        boton_calcular.bind("<KP_Enter>", activar_calcular, add="+")
        boton_calcular.bind(
            "<FocusIn>", lambda _e=None: boton_calcular.marcar(True), add="+",
        )
        boton_calcular.bind(
            "<FocusOut>", lambda _e=None: boton_calcular.marcar(False), add="+",
        )

        panel = ctk.CTkFrame(
            cuerpo, fg_color="#FFFFFF", corner_radius=10,
            border_width=1, border_color="#E2E8F0",
        )
        panel.pack(fill="x", pady=(14, 0))
        self.fp_dict_encabezado = tk.Frame(panel, bg="#F1F5F9")
        self.fp_dict_encabezado.pack(fill="x", padx=2, pady=(2, 0))
        self.fp_dict_acento = tk.Frame(
            self.fp_dict_encabezado, bg="#94A3B8", width=6,
        )
        self.fp_dict_acento.pack(side="left", fill="y")
        self.fp_dict_acento.pack_propagate(False)
        self.fp_dict_icono = tk.Label(
            self.fp_dict_encabezado, text="•", bg="#F1F5F9", fg="#64748B",
            font=("Segoe UI", 20, "bold"),
        )
        self.fp_dict_icono.pack(side="left", padx=(14, 10), pady=8)
        self.fp_lbl_estado = tk.Label(
            self.fp_dict_encabezado, text="DICTAMEN TÉCNICO",
            bg="#F1F5F9", fg="#334155", font=("Segoe UI", 16, "bold"),
        )
        self.fp_lbl_estado.pack(side="left", pady=8)
        cuerpo_dictamen = tk.Frame(panel, bg="#FFFFFF")
        cuerpo_dictamen.pack(fill="x", padx=16, pady=(12, 12))
        fila_indices = tk.Frame(cuerpo_dictamen, bg="#FFFFFF")
        fila_indices.pack(fill="x", pady=(0, 4))
        self.fp_tarjetas = []
        titulos_tarjeta = (
            ("Pérdidas medidas (mW)", "Límite (mW)")
            if apartarrayos else
            ("Factor de Potencia medido", "Factor de Potencia a 20 °C")
        )
        for titulo_tarjeta in titulos_tarjeta:
            tarjeta = tk.Frame(
                fila_indices, bg="#ECFDF5",
                highlightbackground=FP_VISTA_VERDE_CLARO, highlightthickness=2,
            )
            tarjeta.pack(side="left", padx=(0, 18))
            tk.Label(
                tarjeta, text=titulo_tarjeta, bg="#ECFDF5",
                fg=FP_VISTA_VERDE, font=("Segoe UI", 13, "bold"),
            ).pack(anchor="w", padx=16, pady=(12, 0))
            valor = tk.Label(
                tarjeta, text="——", bg="#ECFDF5", fg=FP_VISTA_VERDE,
                font=("Segoe UI", 28, "bold"),
            )
            valor.pack(anchor="w", padx=16, pady=(0, 12))
            self.fp_tarjetas.append(valor)
        tk.Frame(cuerpo_dictamen, bg="#EEEEEE", height=1).pack(
            fill="x", pady=(12, 10),
        )
        tk.Label(
            cuerpo_dictamen, text="OBSERVACIONES TÉCNICAS:",
            bg="#FFFFFF", fg="#4A5568", font=("Segoe UI", 10, "bold"),
        ).pack(anchor="w")
        tk.Frame(cuerpo_dictamen, bg="#EDF2F7", height=1).pack(
            fill="x", pady=(8, 12),
        )
        self.fp_lbl_equipo = tk.Label(
            cuerpo_dictamen, text="——", bg="#FFFFFF", fg="#2D3748",
            font=("Segoe UI", 11, "bold"), justify="left", anchor="w",
            wraplength=640,
        )
        self.fp_lbl_equipo.pack(anchor="w", fill="x")
        self.fp_lbl_amb = tk.Label(
            cuerpo_dictamen, text="•  Ambiente: ——", bg="#FFFFFF",
            fg="#2D3748", font=("Segoe UI", 10), anchor="w",
        )
        self.fp_lbl_amb.pack(fill="x", padx=(14, 0), pady=(4, 0))
        self.fp_lbl_aceite = tk.Label(
            cuerpo_dictamen, text="•  Aceite: ——", bg="#FFFFFF",
            fg="#2D3748", font=("Segoe UI", 10), anchor="w",
        )
        self.fp_lbl_aceite.pack(fill="x", padx=(14, 0))
        self.fp_lbl_kt = tk.Label(
            cuerpo_dictamen, text="•  Kt = ——", bg="#FFFFFF",
            fg="#2D3748", font=("Segoe UI", 10), anchor="w",
        )
        self.fp_lbl_kt.pack(fill="x", padx=(14, 0), pady=(0, 12))
        rejilla_datos = tk.Frame(cuerpo_dictamen, bg="#FFFFFF")
        rejilla_datos.pack(fill="x", pady=(0, 12))

        def caja_formula(titulo):
            caja = tk.Frame(
                rejilla_datos, bg="#F8FAFC",
                highlightbackground="#E2E8F0", highlightthickness=1,
            )
            caja.pack(
                side="left", expand=True, fill="both", padx=(0, 10),
                anchor="n",
            )
            tk.Label(
                caja, text=titulo, bg="#F8FAFC", fg="#1A202C",
                font=("Segoe UI", 10, "bold"), anchor="w",
            ).pack(fill="x", padx=12, pady=(10, 6))
            etiqueta = tk.Label(
                caja, text="——", bg="#F8FAFC", fg="#4A5568",
                font=("Segoe UI", 10), justify="left", wraplength=300,
                anchor="w",
            )
            etiqueta.pack(fill="x", padx=12, pady=(0, 10))
            return etiqueta

        self.fp_lbl_valores = caja_formula("Lecturas equivalentes a 10 kV:")
        self.fp_lbl_calculos = caja_formula("Cálculos aplicados:")
        self.fp_marco_conclusion = tk.Frame(cuerpo_dictamen, bg="#F8FAFC")
        self.fp_marco_conclusion.pack(fill="x")
        self.fp_dict_acento_conclusion = tk.Frame(
            self.fp_marco_conclusion, bg="#94A3B8", width=4,
        )
        self.fp_dict_acento_conclusion.pack(side="left", fill="y")
        self.fp_dict_acento_conclusion.pack_propagate(False)
        self.fp_lbl_conclusion = tk.Label(
            self.fp_marco_conclusion,
            text="Dictamen: capture las lecturas y pulse CALCULAR.",
            bg="#F8FAFC", fg="#334155", font=("Segoe UI", 10),
            justify="left", wraplength=620, anchor="w",
        )
        self.fp_lbl_conclusion.pack(
            side="left", fill="both", expand=True, padx=(12, 8), pady=10,
        )
        tk.Label(
            cuerpo, text="Módulo 04 / 04", bg=RA_VISTA_FONDO,
            fg="#4A5568", font=("Consolas", 9, "bold"),
        ).pack(anchor="e", pady=(12, 0))

    def _calcular_fp(self, padre):
        resultado = self._resultado_fp(padre)
        if resultado is None:
            return
        self._ultimo_fp = resultado
        estilos = {
            "ACEPTADO": ("#10B981", "#065F46", "✅", "#F0FDF4", "normal"),
            "INVESTIGAR": ("#F59E0B", "#92400E", "!", "#FFFBEB", "precaucion"),
            "RECHAZADO": ("#EF4444", "#991B1B", "❌", "#FEF2F2", "alerta"),
            "REGISTRADO": ("#64748B", "#334155", "•", "#F8FAFC", None),
        }
        acento, tinta, icono, suave, nivel = estilos[resultado["estado"]]
        datos = self.datos_fp
        equipo = datos["tipo_equipo"].get()
        try:
            self.fp_dict_encabezado.config(bg=acento)
            self.fp_dict_acento.config(bg=tinta)
            self.fp_dict_icono.config(text=icono, fg="#FFFFFF", bg=acento)
            self.fp_lbl_estado.config(
                text=resultado["estado"], fg="#FFFFFF", bg=acento,
            )
            if resultado["apartarrayos"]:
                valores_tarjeta = (
                    f"{resultado['mw']:.1f}",
                    f"{resultado['limite_mw']:.0f}",
                )
            else:
                valores_tarjeta = (
                    f"{resultado['fp']:.3f} %",
                    f"{resultado['fp20']:.3f} %",
                )
            for etiqueta, valor in zip(self.fp_tarjetas, valores_tarjeta):
                etiqueta.config(text=valor)
            en_aceite = (
                "Aceite" in datos["aislamiento"].get() or "Aceite" in equipo
            ) and not ("Apartarrayos" in equipo or "Cables" in equipo)
            arreglo = self._arreglo_fp()
            self.fp_lbl_equipo.config(
                text=equipo + (f". {arreglo}" if arreglo else "") + ". "
                + (
                    "Aislamiento sumergido en aceite."
                    if en_aceite else "Aislamiento seco."
                )
            )
            self.fp_lbl_amb.config(
                text=(
                    f"•  Ambiente: {datos['temp_ambiente'].get() or '——'} °C"
                    f"  |  Humedad relativa: {datos['humedad'].get() or '——'} %"
                )
            )
            self.fp_lbl_aceite.config(
                text=f"•  Aceite: {datos['temp_aceite'].get() or '——'} °C"
            )
            self.fp_lbl_kt.config(
                text=f"•  Kt = {resultado['kt']:.3f} ({resultado['tabla']})"
            )
            self.fp_lbl_valores.config(
                text=(
                    f"Corriente = {resultado['ma10']:.3f} mA\n"
                    f"Pérdidas = {resultado['w10']:.4f} W "
                    f"({resultado['w10'] * 1000:.1f} mW)\n"
                    f"Capacitancia ≈ {resultado['cap']:.1f} pF"
                )
            )
            self.fp_lbl_calculos.config(
                text=(
                    f"%FP = W × 100 / (kV × mA) = {resultado['fp']:.3f} %\n"
                    f"%FP a 20 °C = %FP × Kt = {resultado['fp20']:.3f} %\n"
                    f"{resultado['criterio']}"
                )
            )
            self.fp_marco_conclusion.config(bg=suave)
            self.fp_dict_acento_conclusion.config(bg=acento)
            self.fp_lbl_conclusion.config(
                text=f"Dictamen: {resultado['frase']}", bg=suave, fg=tinta,
            )
            self._datos_ieee.configure(state="normal")
            self._datos_ieee.delete("1.0", "end")
            self._datos_ieee.configure(state="disabled")
        except (tk.TclError, AttributeError):
            return
        resumen = (
            f"%FP medido: {resultado['fp']:.3f} %\n"
            f"%FP a 20 °C: {resultado['fp20']:.3f} %\n"
            f"Capacitancia: {resultado['cap']:.1f} pF\n"
            f"{resultado['criterio']}"
        )
        if nivel is None:
            self._nivel_foco_ieee = None
            self._pintar_foco_ieee()
            self._aviso_ieee.config(
                bg="#1F2937", fg="#E5E7EB",
                text="Lectura registrada. Este equipo no tiene límite numérico.",
            )
            self._datos_ieee.configure(state="normal")
            self._datos_ieee.insert("1.0", resumen)
            self._datos_ieee.configure(height=7, state="disabled")
        else:
            self._publicar_foco_ieee(nivel, resumen, resultado["estado"])

    # ── Lecturas guardadas (Anexo A) e historial ────────────────────────

    def _clave_lectura_fp(self, prueba):
        datos = self.datos_fp
        equipo = datos["tipo_equipo"].get().strip()
        return "|".join((
            equipo, self._arreglo_fp(),
            datos["fase"].get() if self._lleva_fase_fp(equipo) else "",
            str(prueba.get("prueba", "")), str(prueba.get("medicion", "")),
        ))

    def _lectura_guardada_fp(self, prueba):
        if not prueba:
            return {}
        guardada = getattr(self, "_lecturas_fp", {}).get(
            self._clave_lectura_fp(prueba), {},
        )
        return guardada if isinstance(guardada, dict) else {}

    def _guardar_fp(self, padre):
        """Guarda la lectura en su renglón del Anexo A y en el historial."""
        prueba = self.prueba_fp
        if not prueba:
            messagebox.showwarning(
                "Anexo A", "Selecciona la prueba antes de guardar.",
                parent=padre,
            )
            return
        resultado = self._resultado_fp(padre)
        if resultado is None:
            return
        datos = self.datos_fp
        self._lecturas_fp[self._clave_lectura_fp(prueba)] = {
            "kV": datos["kv"].get().strip(),
            "mA": datos["ma"].get().strip(),
            "W": datos["watts"].get().strip(),
            "temp": datos["temp_aceite"].get().strip(),
        }
        if not _guardar_lecturas_fp(self._lecturas_fp):
            messagebox.showerror(
                "Anexo A", "No se pudieron guardar las lecturas.",
                parent=padre,
            )
            return
        en_historial = self._guardar_en_historial_fp(
            "Dictamen Técnico", padre, resultado=resultado, avisar=False,
        )
        messagebox.showinfo(
            "Anexo A",
            "Lecturas guardadas en la prueba "
            f"{prueba.get('prueba', '—')} · {prueba.get('medicion', '—')} "
            "del Anexo A"
            + (
                " y en el Historial de Análisis."
                if en_historial else
                ". No se pudo escribir en el Historial de Análisis."
            ),
            parent=padre,
        )

    def _guardar_en_historial_fp(
        self, origen, padre=None, resultado=None, avisar=True,
    ):
        padre = padre or self.winfo_toplevel()
        datos = self.datos_fp
        if resultado is None:
            if not all(
                datos[clave].get().strip() for clave in ("kv", "ma", "watts")
            ):
                messagebox.showinfo(
                    "Historial de Análisis",
                    "Primero capture kV, mA y Watts en el paso 4.",
                    parent=padre,
                )
                return False
            resultado = self._resultado_fp(padre)
            if resultado is None:
                return False
        prueba = self.prueba_fp or {}
        equipo = datos["tipo_equipo"].get()
        registro = {
            "fecha": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "modulo": "Factor de Potencia",
            "origen": origen,
            "equipo": equipo,
            "fase": datos["fase"].get() if self._lleva_fase_fp(equipo) else "",
            "prueba": (
                f"Prueba {prueba.get('prueba', '—')} · "
                f"{prueba.get('medicion', '—')} "
                f"({prueba.get('modo', '—')}: HV={prueba.get('hv', '—')} "
                f"GROUND={prueba.get('ground', '—')} "
                f"GUARD={prueba.get('guard', '—')} "
                f"UST={prueba.get('ust', '—')})"
            ),
            "lecturas": {
                "kV": datos["kv"].get().strip(),
                "mA": datos["ma"].get().strip(),
                "W": datos["watts"].get().strip(),
            },
            "fp": f"{resultado['fp']:.3f} %",
            "fp20": f"{resultado['fp20']:.3f} %",
            "kt": f"{resultado['kt']:.3f}",
            "estado": resultado["estado"],
            "descripcion": resultado["descripcion"],
        }
        guardado = bool(_agregar_historial(registro))
        if not avisar:
            return guardado
        if guardado:
            messagebox.showinfo(
                "Historial de Análisis",
                "Análisis guardado. Lo encuentras en la opción "
                "7. Historial de Análisis del menú principal.",
                parent=padre,
            )
        else:
            messagebox.showerror(
                "Historial de Análisis",
                "No se pudo guardar el análisis en el historial.",
                parent=padre,
            )
        return guardado

    # ── Recursos: modos de prueba y anexos ──────────────────────────────

    def _visor_recurso_fp(
        self, padre, resaltado, titulo, medida, fondo="#FFFFFF",
        boton="Cerrar",
    ):
        """Ventana de recurso con encabezado, cuerpo con barra y pie."""
        visor = tk.Toplevel(padre)
        visor.title(f"{resaltado}  {titulo}".strip())
        visor.configure(bg=fondo)
        visor.geometry(medida)
        visor.minsize(640, 520)
        visor.transient(padre)
        encabezado = tk.Frame(visor, bg="#F8FAFC")
        encabezado.pack(fill="x")
        fila_titulo = tk.Frame(encabezado, bg="#F8FAFC")
        fila_titulo.pack(side="left", padx=30, pady=16)
        tk.Label(
            fila_titulo, text=resaltado, bg="#F8FAFC",
            fg=FP_VISTA_VERDE, font=("Segoe UI", 15, "bold"),
        ).pack(side="left")
        tk.Label(
            fila_titulo,
            text=f" - {titulo}" if resaltado.startswith("ANEXO") else f"  {titulo}",
            bg="#F8FAFC", fg="#1E293B", font=("Segoe UI", 15, "bold"),
        ).pack(side="left")
        cerrar = tk.Label(
            encabezado, text="✕", bg="#F8FAFC", fg="#94A3B8",
            font=("Segoe UI", 14, "bold"), cursor="hand2",
        )
        cerrar.pack(side="right", padx=20)
        cerrar.bind("<Button-1>", lambda _e=None: visor.destroy())
        cerrar.bind("<Enter>", lambda _e=None: cerrar.config(fg="#EF4444"))
        cerrar.bind("<Leave>", lambda _e=None: cerrar.config(fg="#94A3B8"))
        tk.Frame(visor, bg="#E2E8F0", height=1).pack(fill="x")
        pie = tk.Frame(visor, bg="#F8FAFC")
        pie.pack(side="bottom", fill="x")
        tk.Frame(visor, bg="#E2E8F0", height=1).pack(side="bottom", fill="x")
        ctk.CTkButton(
            pie, text=boton, fg_color="#10B981", hover_color="#059669",
            text_color="white", font=ctk.CTkFont(size=12, weight="bold"),
            width=110, height=36, command=visor.destroy,
        ).pack(side="right", padx=30, pady=12)
        cuerpo = ctk.CTkScrollableFrame(visor, fg_color=fondo)
        cuerpo.pack(fill="both", expand=True, padx=16, pady=10)
        visor.deiconify()
        visor.lift()
        visor.focus_force()
        return visor, cuerpo

    def mostrar_modos_fp(self, padre):
        visor, cuerpo = self._visor_recurso_fp(
            padre, "ℹ", "Guía de Modos de Prueba", "720x780",
            boton="Entendido",
        )
        tk.Label(
            cuerpo, text="MODOS BÁSICOS DE PRUEBA (ST-CT-002, 3.6)",
            bg="#FFFFFF", fg="#64748B", font=("Segoe UI", 9, "bold"),
            anchor="w",
        ).pack(fill="x", padx=12, pady=(6, 12))

        def tarjeta(insignia, fondo_ins, color_ins, titulo, puntos):
            tarjeta_f = tk.Frame(
                cuerpo, bg="#F8FAFC",
                highlightbackground="#E2E8F0", highlightthickness=1,
            )
            tarjeta_f.pack(fill="x", padx=12, pady=(0, 14))
            cabecera = tk.Frame(tarjeta_f, bg="#F8FAFC")
            cabecera.pack(fill="x", padx=14, pady=(12, 8))
            tk.Label(
                cabecera, text=insignia, bg=fondo_ins, fg=color_ins,
                font=("Segoe UI", 8, "bold"), padx=8, pady=3,
            ).pack(side="left")
            tk.Label(
                cabecera, text=titulo, bg="#F8FAFC", fg="#1E293B",
                font=("Segoe UI", 11, "bold"),
            ).pack(side="left", padx=(10, 0))
            tk.Frame(tarjeta_f, bg="#E2E8F0", height=1).pack(
                fill="x", padx=14,
            )
            for negrita, texto in puntos:
                fila = tk.Frame(tarjeta_f, bg="#F8FAFC")
                fila.pack(fill="x", padx=14, pady=4)
                tk.Label(
                    fila, text="•", bg="#F8FAFC", fg="#334155",
                    font=("Segoe UI", 11, "bold"),
                ).pack(side="left", anchor="n")
                tk.Label(
                    fila, text=f"  {negrita}", bg="#F8FAFC", fg="#0F172A",
                    font=("Segoe UI", 10, "bold"), width=11, anchor="w",
                ).pack(side="left", anchor="n")
                tk.Label(
                    fila, text=texto, bg="#F8FAFC", fg="#334155",
                    font=("Segoe UI", 10), anchor="w", justify="left",
                    wraplength=470,
                ).pack(side="left", fill="x", expand=True)
            tk.Frame(tarjeta_f, bg="#F8FAFC", height=6).pack()

        tarjeta("GST", "#FECACA", "#991B1B", "Grounded Specimen Test", (
            ("Mide:", "toda la corriente entre la fuente de CA y tierra."),
            ("Se usa:", "cuando una terminal del aislamiento está "
             "permanentemente a tierra: el tanque del transformador, la "
             "brida de una boquilla o la carcaza de un equipo aterrizado."),
            ("Cable LV:", "se conecta directamente a tierra o al punto que "
             "se quiere tomar de referencia."),
            ("Ejemplo:", "prueba 1 de un transformador, CH + CHX."),
        ))
        tarjeta("GST-G", "#DBEAFE", "#1E40AF",
                "Grounded Specimen Test with Guard", (
            ("Mide:", "la corriente entre la fuente de CA y tierra, sin la "
             "de la terminal puesta a guarda."),
            ("Se usa:", "para aislar una sección individual del "
             "aislamiento. La corriente de la guarda regresa a la fuente "
             "y no pasa por el circuito de medición."),
            ("Cable LV:", "se conecta al circuito de guarda (Guard)."),
            ("Ejemplo:", "prueba 2 de un transformador, CH; o la medición "
             "de C2 de una boquilla con C1 en guarda."),
        ))
        tarjeta("UST", "#CFFAFE", "#155E75", "Ungrounded Specimen Test", (
            ("Mide:", "solo la corriente entre la fuente y la terminal de "
             "bajo voltaje."),
            ("Se usa:", "con objetos flotados o sin referencia a tierra. "
             "La corriente que va a tierra regresa a la fuente y no se "
             "mide."),
            ("Cable LV:", "se conecta a la terminal contra la que se mide."),
            ("Ejemplo:", "pruebas 5 y 6 de un transformador, CHX directo."),
        ))
        nota = tk.Frame(cuerpo, bg="#ECFDF5")
        nota.pack(fill="x", padx=12, pady=(2, 10))
        acento_n = tk.Frame(nota, bg=FP_VISTA_VERDE, width=4)
        acento_n.pack(side="left", fill="y")
        acento_n.pack_propagate(False)
        tk.Label(
            nota,
            text=(
                "Al elegir una prueba en el paso 2, el sistema muestra su "
                "modo, la tensión, las conexiones del cable de alta (HV) y "
                "del cable de baja (Ground, Guard o UST) y el aislamiento "
                "que mide, según la figura de ST-CT-002."
            ),
            bg="#ECFDF5", fg="#065F46", font=("Segoe UI", 9),
            anchor="w", justify="left", wraplength=600,
        ).pack(side="left", fill="x", expand=True, padx=12, pady=10)
        return visor

    def mostrar_anexo_b_fp(self, padre):
        visor, cuerpo = self._visor_recurso_fp(
            padre, "ANEXO B", "Operación de los Equipos de Medición",
            "860x780",
        )
        alerta = tk.Frame(
            cuerpo, bg="#FFFBEB",
            highlightbackground="#FDE68A", highlightthickness=1,
        )
        alerta.pack(fill="x", pady=(6, 4))
        tk.Label(
            alerta,
            text=(
                "Equipos de medición de factor de potencia: Doble MEU "
                "2.5 kV, Doble M2H 12 kV, Delta-2000 y M4000.  "
                "Norma: ST-CT-002, Anexo B."
            ),
            bg="#FFFBEB", fg="#92400E", font=("Segoe UI", 10),
            anchor="w", justify="left", wraplength=740,
        ).pack(fill="x", padx=14, pady=10)

        def seccion(texto):
            fila = tk.Frame(cuerpo, bg="#FFFFFF")
            fila.pack(fill="x", pady=(18, 6))
            acento = tk.Frame(fila, bg=FP_VISTA_VERDE, width=4)
            acento.pack(side="left", fill="y")
            acento.pack_propagate(False)
            tk.Label(
                fila, text=texto.upper(), bg="#FFFFFF", fg="#0F172A",
                font=("Segoe UI", 11, "bold"),
            ).pack(side="left", padx=(10, 0))

        def numerados(pasos):
            for indice, texto in enumerate(pasos, start=1):
                tk.Label(
                    cuerpo, text=f"{indice}.   {texto}", bg="#FFFFFF",
                    fg="#334155", font=("Segoe UI", 10), anchor="w",
                    justify="left", wraplength=740,
                ).pack(fill="x", padx=(18, 6), pady=3)

        def vineta(texto, negrita=None):
            fila = tk.Frame(cuerpo, bg="#FFFFFF")
            fila.pack(fill="x", padx=(14, 0), pady=2)
            tk.Label(
                fila, text="•", bg="#FFFFFF", fg="#334155",
                font=("Segoe UI", 10, "bold"),
            ).pack(side="left", anchor="n")
            if negrita:
                tk.Label(
                    fila, text=f"  {negrita}", bg="#FFFFFF",
                    fg="#1E293B", font=("Segoe UI", 10, "bold"),
                ).pack(side="left", anchor="n")
            tk.Label(
                fila, text=f"  {texto}", bg="#FFFFFF", fg="#334155",
                font=("Segoe UI", 10), justify="left", wraplength=640,
                anchor="w",
            ).pack(side="left", fill="x", expand=True)

        def formula(texto):
            caja = tk.Frame(cuerpo, bg="#F1F5F9")
            caja.pack(fill="x", padx=(18, 6), pady=6)
            acento = tk.Frame(caja, bg="#94A3B8", width=3)
            acento.pack(side="left", fill="y")
            acento.pack_propagate(False)
            tk.Label(
                caja, text=texto, bg="#F1F5F9", fg="#0F172A",
                font=("Consolas", 11), anchor="w", justify="left",
            ).pack(side="left", padx=12, pady=8)

        seccion("Antes de energizar (todos los equipos)")
        numerados((
            "Asegurar que el equipo a probar esté desenergizado, descargado "
            "y aislado completamente del sistema.",
            "Aterrizar primero el equipo de medición a la red de tierras de "
            "la instalación; esta conexión es la última en retirarse.",
            "Verificar que el equipo bajo prueba esté firmemente aterrizado "
            "a la misma red y que la fuente de 120 V C.A. tenga su neutro "
            "aterrizado.",
            "Conectar el gancho del cable de alta tensión (HV) a la "
            "terminal del equipo a probar.",
            "Conectar el cable o los cables de baja tensión (LV) según la "
            "medición: GROUND, GUARD o UST.",
            "Registrar la temperatura del aceite, la temperatura ambiente "
            "y la humedad relativa.",
        ))

        seccion("Cables de prueba")
        vineta(
            "conductor central que termina en el gancho de la mufa. Lleva "
            "dos blindajes concéntricos: el de guarda termina en el primer "
            "anillo metálico y el de tierra en la base de aluminio.",
            "Cable HV:",
        )
        vineta(
            "va al selector de bajo voltaje del equipo, que permite "
            "aterrizar, guardar o no aterrizar (UST) el espécimen.",
            "Cable LV:",
        )
        vineta(
            "capacitor que usa como dieléctrico el líquido bajo prueba.",
            "Celda de aceite:",
        )

        seccion("B1  Doble tipo MEU 2.5 kV")
        vineta(
            "mide los mVA y las pérdidas en mW hasta 2,500 V. Rango "
            "máximo de 100,000 mVA (40 mA).",
            "Alcance:",
        )
        numerados((
            "Control de voltaje en cero, interruptor en ON, selector en "
            "CHECK, rango en HIGH, multiplicadores de mVA y mW en 2,000 y "
            "selector LV en GROUND.",
            "Cerrar el switch de seguridad del operador y el de la "
            "extensión; se enciende la lámpara roja.",
            "Elevar gradualmente el voltaje a 2.5 kV. Si el interruptor se "
            "dispara antes de 1.25 kV, el equipo bajo prueba está fuera de "
            "rango; entre 1.25 y 2.5 kV, la prueba se hace a voltaje "
            "reducido.",
            "En CHECK y a 2.5 kV, ajustar la aguja a 100 con METER ADJ.",
            "Pasar el selector a mVA y elegir rango y multiplicador hasta "
            "leer en el tercio medio de la escala.",
            "Repetir la lectura con el switch reversible en el otro "
            "extremo y promediar las dos: la diferencia se debe a "
            "interferencia electrostática.",
            "Pasar el selector a mW, sin cambiar el rango de los mVA, y "
            "ajustar a la mínima lectura. Verificar su polaridad: hacia "
            "la izquierda es positiva, hacia la derecha negativa.",
            "Leer mW en las dos posiciones del switch reversible. Si las "
            "dos son positivas se promedian; si una es negativa, se restan "
            "y se divide entre dos.",
            "Regresar el selector a CHECK, el voltaje a cero y abrir los "
            "dos switch de seguridad.",
        ))
        formula(
            "% FP = (mW / mVA) × 100\n"
            "C (pF) = k × mVA     k = 0.425 a 2,500 V"
        )

        seccion("B2  Doble tipo M2H 12 kV")
        vineta(
            "pruebas entre 2 y 12 kV con capacidad máxima de 200 mA. Mide "
            "directamente voltaje, corriente total de carga, pérdidas y "
            "capacitancia. Su circuito de guarda permite medir CH, CL y "
            "CHL sin compensación.",
            "Alcance:",
        )
        numerados((
            "Control de voltaje en cero, interruptor en ON, selector en "
            "CHECK, multiplicador de corriente en 100, multiplicador de "
            "Watts en 1K, ICC en OFF y selector LV en la posición deseada.",
            "Cerrar los interruptores de seguridad (lámparas ámbar y roja) "
            "y elevar gradualmente el voltaje a 10 kV. Si el interruptor se "
            "dispara antes de 2 kV, el equipo está fuera de rango; entre 2 "
            "y 10 kV, se mide a un voltaje menor.",
            "En CHECK, ajustar la aguja a 100 con METER ADJ para las dos "
            "posiciones del switch reversible.",
            "Corriente: bajar el multiplicador hasta leer cerca del centro "
            "de la escala. Leer en las dos polaridades, promediar y "
            "multiplicar por el multiplicador.",
            "Pérdidas: pasar a Watts sin mover el multiplicador de "
            "corriente, llevar WATTS ADJ a la mínima lectura y reducir el "
            "multiplicador. Verificar la polaridad y promediar las dos "
            "lecturas con su signo.",
            "Capacitancia: promedio del contador de pF por el factor de "
            "la casilla CAP MULT.",
            "Regresar el selector a CHECK, el voltaje a cero y abrir los "
            "interruptores de seguridad.",
        ))
        formula(
            "% FP = (Watts × 10) / mA          a 10 kV\n"
            "% FP = (mW / mVA) × 100\n"
            "C (pF) = k × mA      k = 265 a 10,000 V"
        )
        vineta(
            "si se abre el switch local, el voltaje cae a cero y no se "
            "restablece hasta regresar el control de voltaje a cero.",
            "Seguridad M2H:",
        )

        seccion("B3  Medidor Delta-2000")
        numerados((
            "Retirar las tierras de seguridad del objeto bajo prueba y "
            "cerrar el interruptor principal; el equipo hace su "
            "autodiagnóstico.",
            "Capturar el número de identificación y la temperatura antes "
            "de completar las mediciones.",
            "Elegir la configuración de las puntas de bajo voltaje con el "
            "botón UST/GST: UST con medición en rojo, en azul o entre "
            "ambos; GST sin guarda, con guarda azul, con guarda roja o con "
            "ambas en guarda.",
            "Cerrar los interruptores de seguridad, poner el control de "
            "alto voltaje en cero y presionar HV ON.",
            "Ajustar el voltaje de medición y presionar MEASURE.",
            "Al terminar, regresar el voltaje a cero, presionar HIGH "
            "VOLTAGE OFF y descargar las terminales con una pértiga antes "
            "de quitar las puntas.",
        ))
        vineta(
            "0.026 µF a 10 kV y 60 Hz en servicio continuo (100 mA); "
            "0.052 µF con 200 mA durante 15 minutos.",
            "Capacitancia máxima medible:",
        )

        seccion("B4  Medidor M4000")
        numerados((
            "El cable de puesta a tierra es la primera conexión y la "
            "última en retirarse.",
            "Conectar el Controlador y el Instrumento M4000 a la red y "
            "entre sí; después el SAFETY STROBE, el sensor de temperatura "
            "y humedad, los dos pulsadores de seguridad, los cables de "
            "baja tensión (rojo y azul) y el cable de alta tensión.",
            "Encender el Instrumento y luego el Controlador.",
            "Modo Clipboard: una o varias pruebas a elección, hasta 20, "
            "que se muestran en tabla y se pueden guardar o imprimir.",
            "Modo DTA: los resultados se graban en el archivo de prueba "
            "del programa DTA.",
        ))

        seccion("Registro y corrección")
        vineta(
            "tensión de prueba, corriente y pérdidas de cada prueba, con "
            "el multiplicador usado y el modo."
        )
        vineta(
            "el factor de potencia se corrige a 20 °C con la Tabla 4 "
            "(transformadores de potencia y aceite) o la Tabla 6 "
            "(transformadores de instrumento)."
        )
        vineta(
            "en transformadores, las diferencias de la prueba 1 − 2 y de "
            "la 3 − 4 deben coincidir; si no, se comprueba en UST."
        )
        return visor

    def mostrar_anexo_c_fp(self, padre):
        """Anexo C de FP: resumen del procedimiento ST-CT-002, tal como viene en el documento."""
        visor = tk.Toplevel(padre)
        visor.title("ANEXO C  Resumen de procedimiento — ST-CT-002")
        visor.configure(bg="#FFFFFF")
        visor.geometry("860x900")
        visor.transient(padre)
        cuerpo = ctk.CTkScrollableFrame(visor, fg_color="#FFFFFF")
        cuerpo.pack(fill="both", expand=True, padx=12, pady=12)
        tk.Label(
            cuerpo,
            text=(
                "Anexo C Resumen del procedimiento para la medición de factor de "
                "potencia en aislamiento de equipo eléctrico ST-CT-002"
            ),
            bg="#FFFFFF", fg="#1E293B", font=("Segoe UI", 12, "bold"),
            anchor="w", justify="left", wraplength=780,
        ).pack(fill="x", pady=(0, 12))
        cabecera_c = tk.Frame(cuerpo, bg="#052E26")
        cabecera_c.pack(fill="x", pady=(0, 10))
        tk.Label(
            cabecera_c, text="PROCEDIMIENTO ST-CT-002", bg="#052E26", fg="#6EE7B7",
            font=("Segoe UI", 9, "bold"), anchor="w", padx=16, pady=10,
        ).pack(fill="x")
        tk.Label(
            cabecera_c,
            text=(
                "Procedimiento para medición de factor de potencia en aislamiento "
                "de equipo eléctrico"
            ),
            bg="#052E26", fg="#FFFFFF", font=("Segoe UI", 11, "bold"),
            anchor="w", justify="left", wraplength=760, padx=16, pady=12,
        ).pack(fill="x")
        filas_fp = (
            ("En que consiste la medición", (
                "La finalidad de esta medición es la detección de los parámetros "
                "eléctricos de los aislamientos tales como la capacitancia, factor de "
                "potencia y pérdidas dieléctricas. Un incremento apreciable de las "
                "pérdidas dieléctricas en C.A., (mVA) o factor de potencia de un "
                "aislamiento indica deterioro.",
            )),
            ("Que detecta la medición", (
                "Cambios en la capacitancia C del equipo indica cambios en las "
                "propiedades físicas del aislamiento y desplazamientos en los "
                "devanados. El factor de potencia de un dieléctrico es una indicación "
                "de sus pérdidas por unidad de volumen. Este factor se incrementa "
                "debido a las siguientes condiciones: envejecimiento, contaminación, "
                "fallas, esfuerzos eléctricos, degradación, etc.",
            )),
            ("Equipo de medición", ("Equipo de medición de factor de potencia.",)),
            ("Valores o límites recomendados", (
                "Valor límite de FP para transformadores de potencia nuevos es de "
                "0.5%, para transformadores en operación el límite de FP es 1%. Para "
                "valores superiores a 1%, el aislamiento debe investigarse.",
            )),
            ("Comparación de valores", (
                "Cualquier incremento en los valores de capacitancia y FP, indica "
                "deterioro del aislamiento.",
            )),
            ("Correcciones", (
                "Para corregir el FP a 20 °C, el FP medido debe multiplicarse por el "
                "factor de corrección mostrado en la tabla 4 de este procedimiento.",
            )),
            ("Ecuaciones para cálculo", (
                "Factor de potencia:  FP = (pérdidas en Watts)(100) / "
                "(voltaje de prueba)(corriente total)",
                "Factor de disipación:  FD = tan δ = I(R) / I(C)",
                "I(R) = Corriente resistiva (mA)",
                "I(C) = Corriente capacitiva (mA)",
            )),
            ("Recomendaciones", (
                "Para realizar la comparación con mediciones anteriores, los valores de "
                "factor de potencia deben ser corregidos a 20 °C.",
                "En transformadores de potencia, el devanado de bajo voltaje normalmente "
                "no se prueba.",
                "Para realizar la medición en transformadores de potencial, se deben "
                "poner en corto circuito las dos boquillas del devanado de alta tensión "
                "y se aterriza solo una terminal del devanado de baja tensión para evitar "
                "cortos circuitos durante las pruebas cruzadas de comprobación.",
                "Para pruebas de factor de potencia en aceite aislante, se debe tener "
                "especial cuidado de que la muestra sea efectivamente representativa. "
                "Para muestreo, vea el procedimiento ST-CT-006.",
            )),
        )
        for rotulo, textos in filas_fp:
            tarjeta_c = tk.Frame(
                cuerpo, bg="#FFFFFF",
                highlightbackground="#E2E8F0", highlightthickness=1,
            )
            tarjeta_c.pack(fill="x", pady=5)
            tk.Frame(tarjeta_c, bg="#059669", width=5).pack(side="left", fill="y")
            contenido_c = tk.Frame(tarjeta_c, bg="#FFFFFF")
            contenido_c.pack(side="left", fill="x", expand=True, padx=16, pady=12)
            tk.Label(
                contenido_c, text=rotulo.upper(), bg="#FFFFFF", fg="#065F46",
                font=("Segoe UI", 9, "bold"), anchor="w",
            ).pack(fill="x", pady=(0, 4))
            for texto_c in textos:
                tk.Label(
                    contenido_c, text=texto_c, bg="#FFFFFF", fg="#0F172A",
                    font=("Segoe UI", 10), anchor="w", justify="left",
                    wraplength=720,
                ).pack(fill="x", pady=2)
        visor.focus_force()
        return visor

    def _visor_anexo_c_fp_anterior(self, padre):
        visor, cuerpo = self._visor_recurso_fp(
            padre, "ANEXO C", "Resumen del Procedimiento", "860x800",
            fondo="#F8FAFC",
        )
        tk.Label(
            cuerpo,
            text=(
                "Procedimiento para medición de factor de potencia en "
                "aislamiento de equipo eléctrico. (ST-CT-002)"
            ),
            bg="#F8FAFC", fg="#64748B", font=("Segoe UI", 10, "bold"),
            anchor="w", justify="left", wraplength=760,
        ).pack(fill="x", padx=8, pady=(4, 10))
        rejilla = tk.Frame(cuerpo, bg="#F8FAFC")
        rejilla.pack(fill="x", padx=2)
        rejilla.columnconfigure(0, weight=1)
        rejilla.columnconfigure(1, weight=1)

        def tarjeta(fila, columna, titulo, ancho=320, columnas=1):
            tarjeta_f = tk.Frame(
                rejilla, bg="#FFFFFF",
                highlightbackground="#E2E8F0", highlightthickness=1,
            )
            tarjeta_f.grid(
                row=fila, column=columna, columnspan=columnas,
                sticky="nsew", padx=6, pady=6,
            )
            cabecera = tk.Frame(tarjeta_f, bg="#FFFFFF")
            cabecera.pack(fill="x", padx=16, pady=(12, 2))
            tk.Label(
                cabecera, text="●", bg="#FFFFFF", fg=FP_VISTA_VERDE,
                font=("Segoe UI", 8),
            ).pack(side="left")
            tk.Label(
                cabecera, text=titulo.upper(), bg="#FFFFFF",
                fg="#0F172A", font=("Segoe UI", 9, "bold"),
            ).pack(side="left", padx=(8, 0))
            contenido = tk.Frame(tarjeta_f, bg="#FFFFFF")
            contenido.pack(fill="x", padx=16, pady=(4, 12))
            return contenido, ancho

        def parrafo(padre_t, texto, ancho, negrita=None, nota=False):
            fila_p = tk.Frame(padre_t, bg="#FFFFFF")
            fila_p.pack(fill="x", pady=3)
            ancho_txt = ancho
            if negrita:
                tk.Label(
                    fila_p, text=negrita, bg="#FFFFFF", fg="#1E293B",
                    font=("Segoe UI", 10, "bold"),
                ).pack(side="left", anchor="n")
                ancho_txt = max(
                    150,
                    ancho - tkfont.Font(
                        family="Segoe UI", size=10, weight="bold",
                    ).measure(negrita),
                )
            tk.Label(
                fila_p, text=texto, bg="#FFFFFF",
                fg="#64748B" if nota else "#334155",
                font=("Segoe UI", 9 if nota else 10),
                anchor="w", justify="left", wraplength=ancho_txt,
            ).pack(side="left", fill="x", expand=True)

        def caja_formula(padre_t, texto):
            caja = tk.Frame(padre_t, bg="#F1F5F9")
            caja.pack(fill="x", pady=6)
            acento = tk.Frame(caja, bg="#94A3B8", width=3)
            acento.pack(side="left", fill="y")
            acento.pack_propagate(False)
            tk.Label(
                caja, text=texto, bg="#F1F5F9", fg="#0F172A",
                font=("Consolas", 11), anchor="w",
            ).pack(side="left", padx=12, pady=8)

        contenido, ancho = tarjeta(0, 0, "¿En qué consiste la medición?")
        parrafo(
            contenido,
            "de los aislamientos: capacitancia, factor de potencia y "
            "pérdidas dieléctricas.",
            ancho, negrita="Detecta los parámetros eléctricos ",
        )
        parrafo(
            contenido,
            "Un incremento apreciable de las pérdidas dieléctricas en "
            "C.A. (mVA) o del factor de potencia indica deterioro.",
            ancho,
        )
        contenido, ancho = tarjeta(0, 1, "¿Qué detecta la medición?")
        parrafo(
            contenido,
            "Cambios en la capacitancia indican cambios en las "
            "propiedades físicas del aislamiento y desplazamientos en "
            "los devanados.",
            ancho,
        )
        parrafo(
            contenido,
            "El factor de potencia indica las pérdidas por unidad de "
            "volumen. Aumenta con el envejecimiento, la contaminación, "
            "las fallas, los esfuerzos eléctricos y la degradación.",
            ancho,
        )
        contenido, ancho = tarjeta(1, 0, "Equipo de medición")
        parrafo(
            contenido, "Equipo de medición de factor de potencia.", ancho,
        )
        parrafo(
            contenido,
            "Doble MEU 2.5 kV, Doble M2H 12 kV, Delta-2000 o M4000 "
            "(Anexo B).",
            ancho, nota=True,
        )
        contenido, ancho = tarjeta(1, 1, "Comparación de valores")
        parrafo(
            contenido,
            "Cualquier incremento en los valores de capacitancia y de "
            "factor de potencia indica deterioro del aislamiento.",
            ancho,
        )
        contenido, ancho = tarjeta(
            2, 0, "Valores o límites recomendados", ancho=720, columnas=2,
        )
        for negrita, texto in (
            ("Transformadores nuevos:  ", "límite de 0.5 %."),
            ("Transformadores en operación:  ", "límite de 1 %."),
            ("Arriba de 1 %:  ", "el aislamiento debe investigarse."),
        ):
            parrafo(contenido, texto, ancho, negrita=negrita)
        parrafo(
            contenido,
            "TC menor de 115 kV hasta 1 % y de 115 kV o mayor hasta 0.5 %. "
            "TPC nuevo 0.25 %; con 0.5 % se retira. Apartarrayos: 16 mW a "
            "2.5 kV o 256 mW a 10 kV. Cables: Tabla 9.",
            ancho, nota=True,
        )
        contenido, ancho = tarjeta(
            3, 0, "Correcciones", ancho=720, columnas=2,
        )
        caja_formula(contenido, "%FP a 20 °C = %FP medido × Kt")
        parrafo(
            contenido,
            "Factor de corrección por temperatura de la Tabla 4 de este "
            "procedimiento (Tabla 6 en transformadores de instrumento).",
            ancho, negrita="Kt:  ",
        )
        contenido, ancho = tarjeta(
            4, 0, "Ecuaciones para cálculo", ancho=720, columnas=2,
        )
        columnas_ec = tk.Frame(contenido, bg="#FFFFFF")
        columnas_ec.pack(fill="x")
        columnas_ec.columnconfigure(0, weight=1)
        columnas_ec.columnconfigure(1, weight=1)
        for columna_ec, (nombre, formula, detalle) in enumerate((
            (
                "Factor de potencia",
                "FP = (Watts × 100) / (kV × mA)",
                "Pérdidas en Watts entre el voltaje de prueba por la "
                "corriente total.",
            ),
            (
                "Factor de disipación",
                "FD = tan δ = IR / IC",
                "IR: corriente resistiva (mA). IC: corriente capacitiva "
                "(mA).",
            ),
        )):
            celda = tk.Frame(columnas_ec, bg="#FFFFFF")
            celda.grid(
                row=0, column=columna_ec, sticky="nsew",
                padx=(0, 8) if columna_ec == 0 else (8, 0),
            )
            tk.Label(
                celda, text=nombre, bg="#FFFFFF", fg="#1E293B",
                font=("Segoe UI", 10, "bold"), anchor="w",
            ).pack(fill="x")
            caja_formula(celda, formula)
            tk.Label(
                celda, text=detalle, bg="#FFFFFF", fg="#334155",
                font=("Segoe UI", 9), anchor="w", justify="left",
                wraplength=330,
            ).pack(fill="x")
        alerta = tk.Frame(cuerpo, bg="#FFFBEB")
        alerta.pack(fill="x", padx=8, pady=8)
        acento_a = tk.Frame(alerta, bg="#F59E0B", width=4)
        acento_a.pack(side="left", fill="y")
        acento_a.pack_propagate(False)
        texto_alerta = tk.Frame(alerta, bg="#FFFBEB")
        texto_alerta.pack(
            side="left", fill="x", expand=True, padx=12, pady=10,
        )
        tk.Label(
            texto_alerta, text="Recomendaciones:",
            bg="#FFFBEB", fg="#92400E", font=("Segoe UI", 10, "bold"),
            anchor="w",
        ).pack(fill="x")
        for recomendacion in (
            "Para comparar con mediciones anteriores, los valores de "
            "factor de potencia deben corregirse a 20 °C.",
            "En transformadores de potencia, el devanado de bajo voltaje "
            "normalmente no se prueba.",
            "En transformadores de potencial se ponen en corto circuito "
            "las dos boquillas del devanado de alta tensión y se aterriza "
            "solo una terminal del devanado de baja, para evitar cortos "
            "circuitos durante las pruebas cruzadas de comprobación.",
            "En aceite aislante se cuida que la muestra sea efectivamente "
            "representativa. Para el muestreo vea el procedimiento "
            "ST-CT-006.",
        ):
            tk.Label(
                texto_alerta, text=f"•  {recomendacion}",
                bg="#FFFBEB", fg="#92400E", font=("Segoe UI", 10),
                anchor="w", justify="left", wraplength=720,
            ).pack(fill="x", pady=2)
        contenido, ancho = tarjeta(
            5, 0, "Alcance del procedimiento", ancho=720, columnas=2,
        )
        parrafo(
            contenido,
            "Transformadores, autotransformadores, transformadores de "
            "instrumento, apartarrayos, cables y reactores de potencia.",
            ancho,
        )
        return visor

    def mostrar_anexo_a_fp(self, padre):
        visor = tk.Toplevel(padre)
        visor.title("ANEXO A  Formatos de Prueba — Factor de Potencia")
        visor.configure(bg="#F4F6F8")
        visor.geometry("1180x800")
        visor.minsize(980, 640)
        visor.transient(padre)
        barra_sup = tk.Frame(visor, bg="#1E293B")
        barra_sup.pack(fill="x")
        tk.Label(
            barra_sup, text="Formatos de Prueba - Anexo A",
            bg="#1E293B", fg="#FFFFFF", font=("Segoe UI", 15, "bold"),
        ).pack(side="left", padx=20, pady=14)
        contenido = ctk.CTkScrollableFrame(visor, fg_color="#FFFFFF")
        contenido.pack(fill="both", expand=True, padx=18, pady=18)
        scratch = {}

        def var_scratch(clave):
            if clave not in scratch:
                scratch[clave] = tk.StringVar(visor)
            return scratch[clave]

        def grupo(padre_g, texto, variable, fila, columna):
            marco = tk.Frame(padre_g, bg="#FFFFFF")
            marco.grid(row=fila, column=columna, sticky="ew", padx=8, pady=5)
            tk.Label(
                marco, text=texto, bg="#FFFFFF", fg="#64748B",
                font=("Segoe UI", 9, "bold"), anchor="w",
            ).pack(fill="x", pady=(0, 4))
            entrada = ctk.CTkEntry(marco, textvariable=variable, height=30)
            entrada.pack(fill="x")
            return entrada

        def grupo_combo(padre_g, texto, variable, valores, fila, columna):
            marco = tk.Frame(padre_g, bg="#FFFFFF")
            marco.grid(row=fila, column=columna, sticky="ew", padx=8, pady=5)
            tk.Label(
                marco, text=texto, bg="#FFFFFF", fg="#64748B",
                font=("Segoe UI", 9, "bold"), anchor="w",
            ).pack(fill="x", pady=(0, 4))
            ctk.CTkComboBox(
                marco, variable=variable, values=list(valores),
                state="readonly", height=30,
                button_color=FP_VISTA_VERDE,
                button_hover_color=FP_VISTA_VERDE_OSCURO,
            ).pack(fill="x")

        def rejilla(columnas_n):
            marco = tk.Frame(contenido, bg="#FFFFFF")
            marco.pack(fill="x", pady=(4, 12))
            for c in range(columnas_n):
                marco.grid_columnconfigure(c, weight=1)
            return marco

        def subtitulo_seccion(texto):
            tk.Label(
                contenido, text=texto, bg="#FFFFFF", fg="#1E293B",
                font=("Segoe UI", 10, "bold"), anchor="w",
            ).pack(fill="x", padx=15, pady=(12, 2))

        def titulo_formato(texto, clave):
            marco_logo = tk.Frame(contenido, bg="#FFFFFF", height=100)
            marco_logo.pack(fill="x", padx=15, pady=(14, 2))
            marco_logo.pack_propagate(False)
            # Verde oficial CFE: Pantone 136-16 C (#008E60)
            tk.Label(
                marco_logo, text=CFE_ASCII, bg="#FFFFFF", fg="#00573F",
                font=("Consolas", 10, "bold"), anchor="nw", justify="left",
            ).place(x=2, y=2)
            tk.Label(
                marco_logo, text=CFE_ASCII, bg="#FFFFFF", fg="#008E60",
                font=("Consolas", 10, "bold"), anchor="nw", justify="left",
            ).place(x=0, y=0)
            foto_sape = _imagen_sape_ascii(
                tam=9, fondo="#FFFFFF", color="#1E293B",
            )
            etiqueta_sape = ctk.CTkLabel(
                marco_logo, text="", image=foto_sape, fg_color="#FFFFFF",
            )
            etiqueta_sape._foto_sape = foto_sape
            etiqueta_sape.place(relx=1.0, x=-2, y=0, anchor="ne")
            fila_titulo = tk.Frame(contenido, bg="#FFFFFF")
            fila_titulo.pack(fill="x", padx=15, pady=(2, 10))
            tk.Label(
                fila_titulo, text=clave, bg=FP_VISTA_PASTEL,
                fg=FP_VISTA_VERDE_OSCURO, font=("Consolas", 12, "bold"),
                padx=10, pady=3,
            ).pack(side="left")
            tk.Label(
                fila_titulo, text=texto, bg="#FFFFFF", fg="#1E293B",
                font=("Segoe UI", 14, "bold"), anchor="w",
            ).pack(side="left", padx=(12, 0))

        def seccion_identificacion(equipo):
            subtitulo_seccion("DATOS DE IDENTIFICACIÓN")
            rej = rejilla(4)
            grupo(rej, "Gerencia Regional de Transmisión", var_scratch("gerencia"), 0, 0)
            grupo(rej, "Zona", var_scratch("subarea"), 0, 1)
            grupo(rej, "Nomenclatura", var_scratch("nomenclatura"), 0, 2)
            grupo(rej, "Subestación", var_scratch("subestacion"), 0, 3)
            grupo(rej, "Marca", var_scratch("marca"), 1, 0)
            grupo(rej, "Modelo / Tipo", var_scratch("modelo"), 1, 1)
            grupo(rej, "No. de Serie", var_scratch("serie"), 1, 2)
            grupo(rej, "Año de Fabricación", var_scratch("fabricacion"), 1, 3)
            grupo(rej, "Año Puesta en Servicio", var_scratch("servicio"), 2, 0)
            if self._es_potencia_fp(equipo):
                grupo(rej, "MVA", var_scratch("mva"), 2, 1)
                grupo(rej, "Clase de enfriamiento", var_scratch("clase_enf"), 2, 2)
                grupo(rej, "# Taps", var_scratch("taps"), 2, 3)
                grupo(rej, "kV nom. A.T.", var_scratch("kv_at"), 3, 0)
                grupo(rej, "kV nom. B.T.", var_scratch("kv_bt"), 3, 1)
                grupo(rej, "kV nom. Terciario", var_scratch("kv_terc"), 3, 2)
                grupo(rej, "% Z", var_scratch("z"), 3, 3)
                grupo_combo(
                    rej, "Tipo de conexión A.T.", var_scratch("con_at"),
                    ("Y", "Δ"), 4, 0,
                )
                grupo_combo(
                    rej, "Tipo de conexión B.T.", var_scratch("con_bt"),
                    ("Y", "Δ"), 4, 1,
                )
                grupo_combo(
                    rej, "Tipo de conexión Terciario", var_scratch("con_te"),
                    ("Y", "Δ"), 4, 2,
                )
            elif "Apartarrayos" in equipo:
                grupo(rej, "Tensión nominal (kV)", var_scratch("nivel"), 2, 1)
                grupo(rej, "MCOV (kV)", var_scratch("mcov"), 2, 2)
                grupo(rej, "Número de secciones", var_scratch("secciones"), 2, 3)
            elif "Cables" in equipo:
                grupo(rej, "Clase (kV)", var_scratch("nivel"), 2, 1)
                grupo(rej, "Calibre", var_scratch("calibre"), 2, 2)
                grupo(rej, "Longitud (m)", var_scratch("longitud"), 2, 3)
            elif "Corriente" in equipo:
                grupo(rej, "Tensión nominal (kV)", var_scratch("nivel"), 2, 1)
                grupo(rej, "Relación", var_scratch("relacion"), 2, 2)
                grupo(rej, "Clase de exactitud", var_scratch("exactitud"), 2, 3)
                if "TPCs" in equipo:
                    grupo(
                        rej, "Capacitancia de placa (pF)",
                        var_scratch("cap_placa"), 3, 0,
                    )

        def seccion_condiciones():
            subtitulo_seccion("CONDICIONES: PRUEBA & CLIMATOLÓGICA")
            rej = rejilla(4)
            grupo(rej, "Temp. Aceite (°C)", self.datos_fp["temp_aceite"], 0, 0)
            grupo(rej, "Temp. Ambiente (°C)", self.datos_fp["temp_ambiente"], 0, 1)
            grupo(rej, "% Hum. Relativa", self.datos_fp["humedad"], 0, 2)
            grupo(rej, "Temp. Devanado (°C)", var_scratch("temp_devanado"), 0, 3)
            grupo_combo(
                rej, "Clima", var_scratch("clima"),
                ("Soleado", "Nublado", "1/2 nublado", "Brisa", "Lluvia"),
                1, 0,
            )

        def seccion_equipo_medicion():
            subtitulo_seccion("EQUIPO DE MEDICIÓN UTILIZADO")
            rej = rejilla(4)
            grupo(rej, "Marca", var_scratch("inst_marca"), 0, 0)
            grupo(rej, "Modelo", var_scratch("inst_modelo"), 0, 1)
            grupo(rej, "Núm. Serie", var_scratch("inst_serie"), 0, 2)
            grupo(rej, "No. Inv. EIMP", var_scratch("inst_eimp"), 0, 3)
            grupo(rej, "Fecha de Calibración", var_scratch("inst_cal"), 1, 0)

        def seccion_orden_trabajo_fp():
            subtitulo_seccion("ORDEN DE TRABAJO")
            rej = rejilla(4)
            for indice, (clave, texto) in enumerate((
                ("ot", "O.T."), ("fecha", "Fecha"), ("programado", "Programado"),
                ("falla", "Falla"), ("rim", "RIM"), ("rig", "RIG"),
                ("licencia", "No. Licencia"), ("registro", "Número de registro"),
            )):
                grupo(rej, texto, var_scratch(clave), indice // 4, indice % 4)

        def seccion_firmas():
            subtitulo_seccion("OBSERVACIONES Y FIRMAS")
            rej_obs = rejilla(1)
            grupo(rej_obs, "Observaciones", var_scratch("observaciones"), 0, 0)
            rej = rejilla(3)
            grupo(rej, "Realizó — Nombre y firma", var_scratch("realizo"), 0, 0)
            grupo(rej, "Revisó — Nombre y firma", var_scratch("reviso"), 0, 1)
            grupo(rej, "Aprobó — Nombre y firma", var_scratch("aprobo"), 0, 2)

        def lectura_evaluada(prueba):
            """Lectura guardada de la prueba con su %FP ya calculado."""
            guardada = self._lectura_guardada_fp(prueba)
            kv = self._leer_fp(guardada.get("kV", ""))
            ma = self._leer_fp(guardada.get("mA", ""))
            watts = self._leer_fp(guardada.get("W", ""))
            if not kv or not ma or watts is None:
                return None
            temp = self._leer_fp(guardada.get("temp", ""))
            return self._evaluar_fp(kv, ma, watts, temp=temp, prueba=prueba)

        def celda_tabla(tabla, fila, columna, texto, negrita=False, color="#334155", fondo="#FFFFFF"):
            tk.Label(
                tabla, text=texto, bg=fondo, fg=color,
                font=("Segoe UI", 9, "bold" if negrita else "normal"),
                anchor="w", padx=6, pady=7, wraplength=130, justify="left",
            ).grid(row=fila, column=columna, sticky="nsew", pady=(0, 1))

        def tabla_pruebas(equipo):
            subtitulo_seccion("PRUEBA  ·  LECTURAS EQUIVALENTES A 10 kV")
            tabla = tk.Frame(contenido, bg="#E2E8F0")
            tabla.pack(fill="x", padx=15)
            columnas = (
                ("Prueba", 4), ("kV", 4), ("Modo", 5), ("Energizado", 9),
                ("A tierra", 9), ("A guarda", 9), ("UST", 7),
                ("Aislamiento probado", 11), ("mA", 6), ("Watts", 6),
                ("% FP", 6), ("% FP 20 °C", 7), ("C (pF)", 7), ("Cond.", 5),
            )
            for c, (titulo_c, peso) in enumerate(columnas):
                tabla.grid_columnconfigure(c, weight=peso)
                tk.Label(
                    tabla, text=titulo_c.upper(), bg="#F1F5F9",
                    fg="#475569", font=("Segoe UI", 8, "bold"),
                    anchor="w", padx=6, pady=8,
                ).grid(row=0, column=c, sticky="nsew", pady=(0, 1))
            evaluadas = {}
            fila_t = 0
            for prueba in self._pruebas_fp():
                fila_t += 1
                evaluada = lectura_evaluada(prueba)
                evaluadas[prueba["prueba"]] = evaluada
                guard = prueba["guard"]
                if prueba.get("flotando"):
                    guard = f"{prueba['flotando']} flotando"
                fijos = (
                    prueba["prueba"], prueba["kv"], prueba["modo"],
                    prueba["hv"], prueba["ground"], guard, prueba["ust"],
                    prueba["medicion"],
                )
                for c, valor in enumerate(fijos):
                    celda_tabla(
                        tabla, fila_t, c, valor, negrita=c in (0, 7),
                        color="#1E293B" if c in (0, 7) else "#334155",
                    )
                if evaluada is None:
                    medidos = ("—",) * 6
                    color_cond = "#94A3B8"
                else:
                    letra = {
                        "ACEPTADO": "B", "INVESTIGAR": "I",
                        "RECHAZADO": "M", "REGISTRADO": "—",
                    }[evaluada["estado"]]
                    color_cond = {
                        "B": "#059669", "I": "#D97706", "M": "#DC2626",
                    }.get(letra, "#64748B")
                    medidos = (
                        f"{evaluada['ma10']:.3f}", f"{evaluada['w10']:.4f}",
                        f"{evaluada['fp']:.3f}", f"{evaluada['fp20']:.3f}",
                        f"{evaluada['cap']:.1f}", letra,
                    )
                for c, valor in enumerate(medidos, start=8):
                    celda_tabla(
                        tabla, fila_t, c, valor, negrita=c == 13,
                        color=color_cond if c == 13 else "#0F172A",
                    )

            def calculada(nombre, mayor, menor):
                """Renglón de resultados calculados: diferencia de dos pruebas."""
                nonlocal fila_t
                a, b = evaluadas.get(mayor), evaluadas.get(menor)
                fila_t += 1
                celda_tabla(
                    tabla, fila_t, 0, "Calc.", negrita=True,
                    color=FP_VISTA_VERDE_OSCURO, fondo="#F0FDF4",
                )
                for c in range(1, 7):
                    celda_tabla(tabla, fila_t, c, "", fondo="#F0FDF4")
                celda_tabla(
                    tabla, fila_t, 7, f"{nombre} (P{mayor} − P{menor})",
                    negrita=True, color=FP_VISTA_VERDE_OSCURO, fondo="#F0FDF4",
                )
                valores = ("—",) * 6
                if a and b:
                    ma = a["ma10"] - b["ma10"]
                    watts = a["w10"] - b["w10"]
                    if ma > 0:
                        fp = 100.0 * watts / (10.0 * ma)
                        valores = (
                            f"{ma:.3f}", f"{watts:.4f}", f"{fp:.3f}",
                            f"{fp * a['kt']:.3f}",
                            f"{ma * 1_000_000.0 / (2 * math.pi * 60 * 10):.1f}",
                            "",
                        )
                for c, valor in enumerate(valores, start=8):
                    celda_tabla(
                        tabla, fila_t, c, valor, color="#0F172A",
                        fondo="#F0FDF4",
                    )

            if "2 Devanados" in equipo:
                calculada("CHX", "1", "2")
                calculada("CHX", "3", "4")
            elif "3 Devanados" in equipo:
                calculada("CHX", "1", "2")
                calculada("CXY", "3", "4")
                calculada("CHY", "5", "6")
            elif "Autotransformadores" in equipo and len(evaluadas) > 1:
                calculada("CHY", "1", "2")
                calculada("CHY", "3", "4")
            tk.Label(
                contenido,
                text=(
                    "Cond. = condiciones del aislamiento: B = Bueno, "
                    "M = Malo, I = Investigar.  " + self._nota_tabla_fp()
                ),
                bg="#FFFFFF", fg="#64748B", font=("Segoe UI", 9, "italic"),
                anchor="w", justify="left", wraplength=1040,
            ).pack(fill="x", padx=15, pady=(8, 2))

        def tabla_referencia(titulo, encabezados, renglones):
            subtitulo_seccion(titulo)
            tabla = tk.Frame(contenido, bg="#E2E8F0")
            tabla.pack(anchor="w", padx=15, pady=(2, 8))
            for c, texto in enumerate(encabezados):
                tk.Label(
                    tabla, text=texto, bg="#F1F5F9", fg="#475569",
                    font=("Segoe UI", 8, "bold"), padx=8, pady=6,
                ).grid(row=0, column=c, sticky="nsew", padx=(0, 1), pady=(0, 1))
            for r, renglon in enumerate(renglones, start=1):
                for c, texto in enumerate(renglon):
                    tk.Label(
                        tabla, text=texto, bg="#FFFFFF", fg="#334155",
                        font=("Consolas", 9), padx=8, pady=4,
                    ).grid(
                        row=r, column=c, sticky="nsew",
                        padx=(0, 1), pady=(0, 1),
                    )

        def banner_dictamen():
            caja = tk.Frame(contenido, bg="#F1F5F9")
            caja.pack(fill="x", padx=15, pady=(14, 6))
            tk.Label(
                caja, text=self._nota_criterio_fp().split(".  ", 1)[-1],
                bg="#F1F5F9",
                fg="#475569", font=("Segoe UI", 9, "bold"),
                anchor="w", justify="left", wraplength=560,
            ).pack(side="left", padx=14, pady=12)
            estados = [
                evaluada["estado"]
                for evaluada in map(lectura_evaluada, self._pruebas_fp())
                if evaluada
            ]
            if not estados:
                fondo_b, acento_b, tinta_b = "#F1F5F9", "#94A3B8", "#334155"
                icono_b, estado_txt = "•", "CONDICIONES DEL EQUIPO: —"
                sub_txt = "Capture y guarde las lecturas en el paso 4."
            else:
                if "RECHAZADO" in estados:
                    estado = "RECHAZADO"
                elif "INVESTIGAR" in estados:
                    estado = "INVESTIGAR"
                elif "ACEPTADO" in estados:
                    estado = "APROBADO"
                else:
                    estado = "REGISTRADO"
                fondo_b, acento_b, tinta_b, icono_b = {
                    "APROBADO": ("#D1FAE5", "#10B981", "#065F46", "✅"),
                    "INVESTIGAR": ("#FEF3C7", "#F59E0B", "#92400E", "!"),
                    "RECHAZADO": ("#FEE2E2", "#EF4444", "#991B1B", "❌"),
                    "REGISTRADO": ("#F1F5F9", "#94A3B8", "#334155", "•"),
                }[estado]
                estado_txt = f"CONDICIONES DEL EQUIPO: {estado}"
                sub_txt = f"{len(estados)} prueba(s) con lectura guardada."
            banner = tk.Frame(caja, bg=fondo_b)
            banner.pack(side="right", padx=10, pady=8)
            acento = tk.Frame(banner, bg=acento_b, width=6)
            acento.pack(side="left", fill="y")
            acento.pack_propagate(False)
            tk.Label(
                banner, text=icono_b, bg=fondo_b, fg=acento_b,
                font=("Segoe UI", 16, "bold"),
            ).pack(side="left", padx=(10, 6))
            textos_b = tk.Frame(banner, bg=fondo_b)
            textos_b.pack(side="left", padx=(0, 12), pady=6)
            tk.Label(
                textos_b, text=estado_txt, bg=fondo_b, fg=tinta_b,
                font=("Segoe UI", 11, "bold"), anchor="w",
            ).pack(fill="x")
            tk.Label(
                textos_b, text=sub_txt, bg=fondo_b, fg=tinta_b,
                font=("Segoe UI", 8), anchor="w",
            ).pack(fill="x")

        def dibujo_equipo(equipo):
            mono = self.datos_fp["configuracion"].get() == "Monofásico"
            if "Corriente" in equipo:
                _dibujar_diagrama_tc(contenido)
            elif "Capacitivo" in equipo:
                _dibujar_diagrama_tpc(contenido)
            elif "Potencial - TPs" in equipo:
                _dibujar_diagrama_tp(contenido)
            elif "2 Devanados" in equipo:
                _dibujar_diagrama_transformador_2d(contenido, monofasico=mono)
            elif "3 Devanados" in equipo and not mono:
                _dibujar_diagrama_transformador_3d(contenido)
            elif "Autotransformadores" in equipo:
                _dibujar_diagrama_autotransformador(contenido, monofasico=mono)
            elif "Reactores" in equipo:
                _dibujar_diagrama_reactor(contenido)
            elif "Apartarrayos" in equipo:
                _dibujar_diagrama_apartarrayos(contenido)

        def construir(_valor=None):
            for hijo in contenido.winfo_children():
                hijo.destroy()
            equipo = self.datos_fp["tipo_equipo"].get().strip()
            combo_arreglo.configure(values=list(ARREGLOS_FP.get(equipo, ())))
            arreglo = self._arreglo_fp()
            clave, nombre, figura = self._formato_fp()
            titulo_formato(
                f"Factor de Potencia al Aislamiento — {equipo}"
                + (f"  ·  {arreglo}" if arreglo else ""),
                clave,
            )
            seccion_identificacion(equipo)
            seccion_condiciones()
            seccion_orden_trabajo_fp()
            seccion_equipo_medicion()
            tabla_pruebas(equipo)
            if self._es_potencia_fp(equipo) or "Aceite" in equipo:
                tabla_referencia(
                    "FACTOR DE POTENCIA A 20 °C  ·  LÍMITES",
                    ("", "Excelente / Nuevo", "Límite"),
                    (
                        ("Transformador", "0.50 %", "1.00 %"),
                        ("Aceite", "0.05 %", "0.50 %"),
                    ),
                )
            elif "TPCs" in equipo:
                tabla_referencia(
                    "TABLA 5  ·  TOLERANCIA DE CAPACITANCIA",
                    (
                        "Tipo", "Clase", "Módulos", "Bobinas", "Toma C2",
                        "pF por módulo", "± módulo", "pF por aparato",
                        "± aparato",
                    ),
                    [
                        tuple(
                            f"{v:,}" if isinstance(v, int) and v > 999 else str(v)
                            for v in renglon
                        )
                        for renglon in TABLA5_FP
                    ],
                )
            elif "Cables" in equipo:
                tabla_referencia(
                    "TABLA 9  ·  VALORES DE FP PARA CABLES",
                    ("Tipo de aislamiento", "F.P."),
                    [
                        (nombre_c, f"Hasta {limite:g} %")
                        for nombre_c, limite in TABLA9_FP
                    ],
                )
            dibujo_equipo(equipo)
            banner_dictamen()
            seccion_firmas()
            contenido._parent_canvas.yview_moveto(0)

        def guardar():
            if self.prueba_fp not in self._pruebas_fp():
                messagebox.showinfo(
                    "Anexo A",
                    "Elija la prueba en el paso 2 y capture sus lecturas en "
                    "el paso 4 antes de guardar.",
                    parent=visor,
                )
                return
            self._guardar_fp(visor)
            construir()

        for texto_boton, ancho_boton, comando in (
            ("GUARDAR", 110, guardar),
            (
                # Igual que en RA: el formato tal como se ve, en una hoja carta.
                "IMPRIMIR", 110,
                lambda: _imprimir_formato_carta(
                    contenido, "Anexo A — Factor de Potencia al Aislamiento",
                ),
            ),
        ):
            ctk.CTkButton(
                barra_sup, text=texto_boton, fg_color=FP_VERDE,
                hover_color=FP_VERDE_OSCURO, text_color="white",
                font=ctk.CTkFont(weight="bold"), width=ancho_boton, height=34,
                command=comando,
            ).pack(side="right", padx=(10, 0), pady=10)
        # Equipo y arreglo en su propio renglón, bajo el título.
        barra_filtros = tk.Frame(visor, bg="#334155")
        barra_filtros.pack(fill="x", after=barra_sup)
        tk.Label(
            barra_filtros, text="EQUIPO", bg="#334155", fg="#CBD5E1",
            font=("Segoe UI", 9, "bold"),
        ).pack(side="left", padx=(20, 8), pady=8)
        ctk.CTkComboBox(
            barra_filtros, variable=self.datos_fp["tipo_equipo"],
            values=EQUIPOS_FP, state="readonly", width=360,
            button_color=FP_VERDE_OSCURO, button_hover_color=FP_VERDE_HOVER,
            command=construir,
        ).pack(side="left", pady=8)
        tk.Label(
            barra_filtros, text="ARREGLO", bg="#334155", fg="#CBD5E1",
            font=("Segoe UI", 9, "bold"),
        ).pack(side="left", padx=(20, 8), pady=8)
        combo_arreglo = ctk.CTkComboBox(
            barra_filtros, variable=self.datos_fp["arreglo"], values=[],
            state="readonly", width=360,
            button_color=FP_VERDE_OSCURO, button_hover_color=FP_VERDE_HOVER,
            command=construir,
        )
        combo_arreglo.pack(side="left", pady=8)
        construir()
        visor.focus_force()
        return visor


# ═══════════════════════════════════════════════════════════════════════════
# Factor de Potencia al Aislamiento — datos y esquemas de ST-CT-002 Rev. 1
# ═══════════════════════════════════════════════════════════════════════════
# Mismo formato que Resistencia de Aislamiento; aquí manda el verde.
FP_VISTA_VERDE = "#059669"
FP_VISTA_VERDE_OSCURO = "#047857"
FP_VISTA_VERDE_CLARO = "#34D399"
FP_VISTA_PASTEL = "#D1FAE5"
FP_VISTA_PASTEL_BORDE = "#6EE7B7"
FP_VISTA_MEDICION = "#F76707"
RUTA_LECTURAS_FP = Path(__file__).with_name("lecturas_anexo_a_fp.json")

EQUIPOS_FP = [
    "Transformadores de 2 Devanados",
    "Transformadores de 3 Devanados",
    "Autotransformadores",
    "Reactores",
    "Transformadores de Corriente - TCs",
    "Transformadores de Potencial - TPs",
    "Transformadores de Potencial Capacitivo - TPCs",
    "Apartarrayos",
    "Cables de Potencia",
    "Aceite Aislante",
]

# Arreglos de prueba: cada uno es una figura del procedimiento.
ARREGLOS_FP = {
    "Autotransformadores": (
        "Con terciario accesible (Fig. 11)",
        "Terciario no accesible (Fig. 11, nota)",
    ),
    "Transformadores de Corriente - TCs": (
        "Un módulo (Fig. 21)",
        "Dos módulos: módulo superior (Fig. 22a)",
        "Dos módulos: módulo inferior (Fig. 22b)",
    ),
    "Transformadores de Potencial - TPs": (
        "Dos boquillas (Fig. 13)",
        "Una boquilla, neutro aterrizado interno (Fig. 14)",
        "Una boquilla, tierra desconectable (Fig. 15)",
        "Inductivo en cascada (Fig. 16)",
    ),
    "Transformadores de Potencial Capacitivo - TPCs": (
        "Arreglo típico (Fig. 17)",
        "Más de un módulo (Fig. 18)",
        "B2 y B3 comunes (Fig. 19)",
        "Fig. 19 con la línea aterrizada (1A-3A)",
        "Módulos con B1 = T2 (Fig. 20)",
        "Fig. 20 con la línea conectada",
    ),
    "Apartarrayos": (
        "Una sección (Fig. 23)",
        "Dos secciones (Fig. 24)",
        "Tres secciones (Fig. 25)",
        "Cuatro secciones (Tabla 7)",
        "Cinco secciones (Fig. 26)",
    ),
    "Cables de Potencia": (
        "Monofásico (Fig. 27)",
        "Trifásico (Fig. 28)",
    ),
}

# Formato del Anexo A que corresponde a cada equipo.
FORMATOS_FP = {
    "Transformadores de 2 Devanados": (
        "ST-CT-002-A", "Transformador de dos devanados", "Fig. 8",
    ),
    "Transformadores de 3 Devanados": (
        "ST-CT-002-B", "Transformador de tres devanados", "Fig. 10",
    ),
    "Autotransformadores": ("ST-CT-002-C", "Autotransformadores", "Fig. 11"),
    "Reactores": ("ST-CT-002-D", "Reactores", "Fig. 12"),
    "Transformadores de Potencial - TPs": (
        "ST-CT-002-E", "Transformadores de potencial inductivos", "",
    ),
    "Transformadores de Potencial Capacitivo - TPCs": (
        "ST-CT-002-F", "Transformadores de potencial capacitivos", "",
    ),
    "Transformadores de Corriente - TCs": (
        "ST-CT-002-H", "Transformadores de corriente", "",
    ),
    "Apartarrayos": ("ST-CT-002-I", "Apartarrayos", ""),
    "Cables de Potencia": ("ST-CT-002-J", "Cables de potencia", ""),
    "Aceite Aislante": (
        "ST-CT-002", "Aceite aislante (celda de prueba)", "Fig. 29",
    ),
}

# Tabla 4. Factor de corrección por temperatura (°C: tres columnas).
TABLA4_FP = (
    (0, 1.56, 1.57, 0.95), (2, 1.52, 1.50, 0.96), (4, 1.48, 1.44, 0.98),
    (6, 1.45, 1.37, 0.98), (8, 1.43, 1.31, 0.99), (10, 1.38, 1.25, 0.99),
    (12, 1.31, 1.19, 1.00), (14, 1.24, 1.14, 1.01), (16, 1.16, 1.09, 1.01),
    (18, 1.08, 1.05, 1.00), (20, 1.00, 1.00, 1.00), (22, 0.91, 0.96, 0.99),
    (24, 0.83, 0.92, 0.98), (26, 0.76, 0.88, 0.97), (28, 0.70, 0.84, 0.96),
    (30, 0.63, 0.80, 0.95), (32, 0.58, 0.76, 0.94), (34, 0.53, 0.73, 0.93),
    (36, 0.49, 0.70, 0.91), (38, 0.45, 0.67, 0.90), (40, 0.42, 0.65, 0.89),
    (42, 0.38, 0.62, 0.87), (44, 0.36, 0.59, 0.86), (46, 0.33, 0.56, 0.84),
    (48, 0.30, 0.54, 0.83), (50, 0.28, 0.51, 0.81), (52, 0.26, 0.49, 0.79),
    (54, 0.23, 0.47, 0.77), (56, 0.21, 0.45, 0.75), (58, 0.19, 0.43, 0.72),
    (60, 0.17, 0.41, 0.70),
)
PRESERVACION_FP = (
    "Respiración libre / conservador",
    "Sellado o con gas, hasta 161 kV",
    "Sellado o con gas, de 161 a 750 kV",
)
# Tabla 6. Transformadores de instrumento sumergidos en aceite (0 a 44 °C).
TABLA6_FP = (
    (0, 1.67), (2, 1.61), (4, 1.55), (6, 1.49), (8, 1.43), (10, 1.36),
    (12, 1.30), (14, 1.23), (16, 1.16), (18, 1.08), (20, 1.00),
    (22, 0.93), (24, 0.86), (26, 0.80), (28, 0.74), (30, 0.69),
    (32, 0.65), (34, 0.60), (36, 0.56), (38, 0.52), (40, 0.48),
    (42, 0.45), (44, 0.42),
)
# Tabla 9. Valores de FP para cables, según el aislamiento.
TABLA9_FP = (
    ("Butilo hasta 15 kV", 3.0),
    ("Dacrón vidrio 5 kV", 6.0),
    ("Papel y aceite de 34.5 kV", 1.0),
    ("Papel y aceite de 69 a 230 kV", 1.0),
    ("Polietileno hasta 15 kV", 1.0),
    ("Hule 15 kV", 6.0),
    ("Barniz Cambridge hasta 15 kV", 5.0),
)
# Tabla 5. Tolerancia de capacitancia de los TPC:
# (tipo, clase kV, módulos, bobinas, toma C2, pF por módulo, tolerancia por
#  módulo, pF por aparato, tolerancia por aparato)
TABLA5_FP = (
    ("CVA-115", 115, 1, 96, 16, 6000, 128, 6000, 128),
    ("CVB-115", 115, 1, 88, 15, 8800, 205, 8800, 205),
    ("CVC-115", 115, 1, 88, 15, 19700, 458, 19700, 458),
    ("CVA-230", 230, 2, 192, 16, 6000, 63, 3000, 32),
    ("CVB-230", 230, 2, 176, 15, 8800, 101, 4400, 51),
    ("CVC-230", 230, 2, 176, 15, 19700, 226, 9850, 229),
    ("CVC-400", 400, 3, 288, 14, 16800, 117, 5600, 39),
)

DESCRIPCIONES_FP = {
    "CH": "Aislamiento entre el devanado de alta (H) y tierra",
    "CX": "Aislamiento entre el devanado de baja (X) y tierra",
    "CY": "Aislamiento entre el terciario (Y) y tierra",
    "CHX": "Aislamiento entre los devanados de alta y baja",
    "CXY": "Aislamiento entre baja (X) y terciario (Y)",
    "CHY": "Aislamiento entre alta (H) y terciario (Y)",
    "CP": "Aislamiento del devanado primario (P1, P2)",
    "CS": "Aislamiento del devanado secundario",
}


def _interpolar_fp(tabla, temp, columna=1):
    """Factor de corrección a 20 °C; entre renglones se interpola."""
    if temp <= tabla[0][0]:
        return tabla[0][columna]
    if temp >= tabla[-1][0]:
        return tabla[-1][columna]
    for previo, siguiente in zip(tabla, tabla[1:]):
        t0, t1 = previo[0], siguiente[0]
        if t0 <= temp <= t1:
            k0, k1 = previo[columna], siguiente[columna]
            return k0 + (k1 - k0) * (temp - t0) / (t1 - t0)
    return 1.0


def _filas_fp(equipo, arreglo):
    """Tabla de conexiones de la figura de ST-CT-002 para el equipo."""

    def f(n, kv, hv, gnd="", grd="", ust="", mide="", caps=(), flot=""):
        if ust:
            modo = "UST"
        elif grd:
            modo = "GST-G"
        else:
            modo = "GST"
        vacio = "-----"
        return {
            "prueba": str(n), "kv": kv, "modo": modo, "hv": hv,
            "ground": gnd or vacio, "guard": grd or vacio,
            "ust": ust or vacio, "flotando": flot,
            "medicion": mide, "caps": tuple(caps),
        }

    if equipo == "Transformadores de 2 Devanados":
        return [
            f(1, "10", "H", gnd="X", mide="CH+CHX"),
            f(2, "10", "H", grd="X", mide="CH"),
            f(3, "10", "X", gnd="H", mide="CX+CHX"),
            f(4, "10", "X", grd="H", mide="CX"),
            f(5, "10", "H", ust="X", mide="CHX"),
            f(6, "10", "X", ust="H", mide="CHX"),
        ]
    if equipo == "Transformadores de 3 Devanados":
        return [
            f(1, "10", "H", gnd="X", grd="Y", mide="CH+CHX"),
            f(2, "10", "H", grd="X, Y", mide="CH"),
            f(3, "10", "X", gnd="Y", grd="H", mide="CX+CXY"),
            f(4, "10", "X", grd="H, Y", mide="CX"),
            f(5, "10", "Y", gnd="H", grd="X", mide="CY+CHY"),
            f(6, "10", "Y", grd="H, X", mide="CY"),
            f(7, "10", "H, X, Y", mide="CH+CX+CY"),
        ]
    if equipo == "Autotransformadores":
        if arreglo.startswith("Terciario no accesible"):
            return [f(1, "10", "H+X", gnd="Tanque", mide="CH")]
        return [
            f(1, "10", "H+X", gnd="Y", mide="CH+CHY"),
            f(2, "10", "H+X", grd="Y", mide="CH"),
            f(3, "10", "Y", gnd="H+X", mide="CY+CHY"),
            f(4, "10", "Y", grd="H+X", mide="CY"),
            f(5, "10", "H+X", ust="Y", mide="CHY"),
            f(6, "10", "Y", ust="H+X", mide="CHY"),
        ]
    if equipo == "Reactores":
        return [f(1, "10", "H", gnd="Tanque", mide="CH")]
    if equipo == "Transformadores de Corriente - TCs":
        if "22a" in arreglo:
            return [
                f(1, "10", "P1, P2", gnd="S1, S2", mide="CP", caps=("CP",)),
                f(2, "10", "S1, S2", gnd="P1, P2", mide="CS", caps=("CS",)),
            ]
        if "22b" in arreglo:
            return [
                f(1, "10", "P1, P2", gnd="S1, S2", mide="CP", caps=("CP",)),
                f(2, "0.5", "S1, S2", gnd="P1, P2", mide="CS", caps=("CS",)),
            ]
        return [
            f(1, "10", "P1, P2", gnd="S1, S2, S3, S4", mide="CP",
              caps=("CP",)),
            f(2, "0.5", "S1, S2, S3, S4", gnd="P1, P2", mide="CS",
              caps=("CS",)),
        ]
    if equipo == "Transformadores de Potencial - TPs":
        if "Fig. 14" in arreglo:
            return [
                f(1, "10", "H1", gnd="H0", ust="X1, Y1",
                  mide="Aislamiento entre devanados", caps=("CHX",)),
                f(2, "10", "H1", gnd="H0", grd="X1, Y1",
                  mide="Corriente de excitación", caps=("DEVANADO",)),
            ]
        if "Fig. 16" in arreglo:
            return [
                f("1A", "5", "H0", gnd="X1-X3, Y1-Y3", flot="H1",
                  mide="Completa", caps=("C", "DEVANADO")),
            ]
        # Fig. 15: se energiza la terminal de tierra P2; esa boquilla
        # soporta por lo general 5 kV.
        kv = "5" if "Fig. 15" in arreglo else "10"
        return [
            f(1, kv, "H1, H2", gnd="X1", mide="CH+CHX",
              caps=("CH", "CHX")),
            f(2, kv, "H1, H2", grd="X1", mide="CH", caps=("CH",)),
            f(3, kv, "H1", gnd="X1", grd="H2", mide="CH+CHX",
              caps=("CH", "CHX")),
            f(4, kv, "H2", gnd="X1", grd="H1", mide="CH+CHX",
              caps=("CH", "CHX")),
        ]
    if equipo == "Transformadores de Potencial Capacitivo - TPCs":
        c12, c23 = "C(B1-B2)", "C(B2-B3)"
        if "Fig. 17" in arreglo:
            return [
                f(1, "2", "B2*", gnd="B1", mide="C(B2+B1)", caps=(c12,)),
                f(2, "5", "B3*", gnd="B1", grd="B2", mide="C(B3+B1)",
                  caps=(c12, c23)),
                f(3, "5", "B3*", gnd="B1", ust="B2", mide="C(B3+B2)",
                  caps=(c23,)),
                f(4, "2", "B2*", grd="B3", mide="Terminal B2",
                  caps=("Term. B2",)),
                f(5, "5", "B3*", grd="B2", mide="Terminal B3",
                  caps=("Term. B3",)),
            ]
        if "Fig. 18" in arreglo:
            return [
                f("1A", "10", "B1", gnd="T1", grd="B3", mide="C(T1-T2)",
                  caps=("C(T1-T2)",)),
                f("2A", "10", "B1", gnd="T1", ust="B2", mide="C(B1+B2)",
                  caps=(c12,)),
                f("3A", "10", "B1", gnd="T1", ust="B3", mide="C(B1+B3)",
                  caps=(c12, c23)),
                f("4A", "5", "B3*", gnd="T1", ust="B2", mide="C(B3+B2)",
                  caps=(c23,)),
                f("5A", "2", "B2*", grd="B3", mide="Terminal B2",
                  caps=("Term. B2",)),
                f("6A", "5", "B3*", grd="B1, B2", mide="Terminal B3",
                  caps=("Term. B3",)),
            ]
        if arreglo.startswith("Fig. 19"):
            return [
                f("1A", "10", "B1*", gnd="B3", ust="B2", mide="C(B1+B2)",
                  caps=(c12,)),
                f("2A", "2", "B2*", gnd="B3", mide="C(B2+B3)", caps=(c23,)),
                f("3A", "2", "B2*", grd="B1", mide="Terminal B2",
                  caps=("Term. B2",)),
            ]
        if "Fig. 19" in arreglo:
            return [
                f(1, "2", "B2*", gnd="B1", grd="B3", mide="C(B2+B1)",
                  caps=(c12,)),
                f(2, "2", "B2*", gnd="B1", ust="B3", mide="C(B2+B3)",
                  caps=(c23,)),
                f(3, "2", "B2*", grd="B1", mide="Terminal B2",
                  caps=("Term. B2",)),
            ]
        if arreglo.startswith("Fig. 20"):
            return [
                f(1, "10", "B1=T2", gnd="T1, B3", grd="B2",
                  mide="C(T2+T1)", caps=("C(T1-T2)",)),
                f(2, "10", "B1=T2", gnd="T1, B3", ust="B2",
                  mide="C(B1+B2)", caps=(c12,)),
                f(3, "2", "B2*", gnd="T1, B3", grd="B1=T2",
                  mide="C(B2+B3)", caps=(c23,)),
                f(4, "2", "B2*", grd="B1=T2, B3", mide="Terminal B2",
                  caps=("Term. B2",)),
            ]
        return [
            f(1, "10", "B1=T2", gnd="T1", grd="B3", mide="C(T1+T2)",
              caps=("C(T1-T2)",)),
            f(2, "10", "B1=T2", gnd="T1", ust="B2", mide="C(B1+B2)",
              caps=(c12,)),
            f(3, "10", "B1=T2", gnd="T1", ust="B3", mide="C(B1+B3)",
              caps=(c12, c23)),
            f(4, "5", "B3*", gnd="T1", ust="B2", mide="C(B3+B2)",
              caps=(c23,)),
            f(5, "2", "B2*", grd="B3", mide="Terminal B2",
              caps=("Term. B2",)),
            f(6, "5", "B3*", grd="B1=T2, B2", mide="Terminal B3",
              caps=("Term. B3",)),
        ]
    if equipo == "Apartarrayos":
        if "Una" in arreglo:
            return [f(1, "10", "1", gnd="2", mide="C12", caps=("C12",))]
        if "Dos" in arreglo:
            return [
                f(1, "10", "1", gnd="2", mide="A", caps=("A",)),
                f(2, "10", "2", gnd="3", mide="B", caps=("B",)),
                f(3, "10", "1", gnd="3", mide="A+B", caps=("A", "B")),
                f(4, "10", "2", gnd="3", ust="1", mide="A", caps=("A",)),
            ]
        if "Tres" in arreglo:
            return [
                f(1, "10", "1", gnd="2", mide="A", caps=("A",)),
                f(2, "10", "2", gnd="3", mide="B", caps=("B",)),
                f(3, "10", "3", gnd="4", mide="C", caps=("C",)),
                f(4, "10", "1", ust="4", mide="A+B+C",
                  caps=("A", "B", "C")),
            ]
        if "Cuatro" in arreglo:
            return [
                f(1, "10", "1", gnd="2", mide="A", caps=("A",)),
                f(2, "10", "2", gnd="3", mide="B", caps=("B",)),
                f(3, "10", "3", gnd="4", mide="C", caps=("C",)),
                f(4, "10", "4", gnd="5", mide="D", caps=("D",)),
                f(5, "10", "1", gnd="5", mide="A+B+C+D",
                  caps=("A", "B", "C", "D")),
            ]
        return [
            f(1, "10", "2", gnd="1, 6", grd="3", mide="A", caps=("A",)),
            f(2, "10", "3", gnd="1, 2, 6", grd="4", mide="B", caps=("B",)),
            f(3, "10", "3", gnd="1, 2, 6", ust="4", mide="C", caps=("C",)),
            f(4, "10", "5", gnd="1, 6", ust="4", mide="D", caps=("D",)),
            f(5, "10", "5", gnd="1, 6", grd="4", mide="E", caps=("E",)),
        ]
    if equipo == "Cables de Potencia":
        if "Trifásico" in arreglo:
            return [
                f(1, "10", "A", gnd="B+C", mide="A", caps=("A",)),
                f(2, "10", "B", gnd="A+C", mide="B", caps=("B",)),
                f(3, "10", "C", gnd="A+B", mide="C", caps=("C",)),
                f(4, "10", "A+B+C", gnd="Pantalla", mide="A+B+C",
                  caps=("A", "B", "C")),
            ]
        return [
            f(1, "10", "Conductor", gnd="Pantalla", mide="Aislamiento",
              caps=("C",)),
        ]
    if equipo == "Aceite Aislante":
        return [
            f(1, "10", "HV", grd="Guarda", ust="LV", mide="Aceite",
              caps=("ACEITE",)),
        ]
    return []


def _topologia_fp(equipo, arreglo):
    """Esquema propio de SAPE2 para los equipos que SAPE_1 no dibuja.

    None indica que el diagrama de bloques lo arma SAPE_1 (transformadores,
    autotransformadores y reactores).
    """
    if equipo == "Transformadores de Corriente - TCs":
        secundario = (
            ("S1 - S4", ("S1", "S2", "S3", "S4"))
            if "Fig. 21" in arreglo else ("S1 - S2", ("S1", "S2"))
        )
        return {
            "nodos": {
                "P": ("P1 - P2", 1, 0, ("P1", "P2")),
                "S": (secundario[0], 4, 0, secundario[1]),
            },
            "elementos": [
                ("cap", "CP", "P", (1, 2.4)),
                ("cap", "CS", "S", (4, 2.4)),
                ("cable", (1, 2.4), (4, 2.4)),
                ("tierra", (2.5, 2.4)),
            ],
        }
    if equipo == "Transformadores de Potencial - TPs":
        if "Fig. 14" in arreglo:
            return {
                "nodos": {
                    "H1": ("H1", 1, 0, ("H1",)),
                    "H0": ("H0", 1, 3, ("H0",)),
                    "XY": ("X1 - Y1", 3.6, 1.5, ("X1", "Y1")),
                },
                "elementos": [
                    ("bobina", "DEVANADO", "H1", "H0"),
                    ("cap", "CHX", (1, 1.5), "XY"),
                    ("cable", "H0", (1, 4.1)),
                    ("tierra", (1, 4.1)),
                ],
            }
        if "Fig. 16" in arreglo:
            return {
                "nodos": {
                    "H1": ("H1", 1, 0, ("H1",)),
                    "H0": ("H0", 1, 3, ("H0",)),
                    "XY": (
                        "X1-X3 · Y1-Y3", 3.8, 1.5,
                        ("X1-X3", "Y1-Y3", "X1", "X2", "X3", "Y1", "Y2", "Y3"),
                    ),
                },
                "elementos": [
                    ("bobina", "DEVANADO", "H1", "H0"),
                    ("cap", "C", (1, 1.5), "XY"),
                    ("cable", "XY", (3.8, 2.6)),
                    ("tierra", (3.8, 2.6)),
                ],
            }
        return {
            "nodos": {
                "H1": ("H1", 1, 0, ("H1",)),
                "H2": ("H2", 1, 3, ("H2",)),
                "X1": ("X1", 3.6, 1.5, ("X1",)),
            },
            "elementos": [
                ("bobina", "DEVANADO", "H1", "H2"),
                ("cap", "CHX", (1, 1.5), "X1"),
                ("cap", "CH", (1, 1.5), (-0.8, 1.5)),
                ("cable", (-0.8, 1.5), (-0.8, 2.4)),
                ("tierra", (-0.8, 2.4)),
            ],
        }
    if equipo == "Transformadores de Potencial Capacitivo - TPCs":
        if "Fig. 18" in arreglo or "Fig. 20" in arreglo:
            union = (
                ("B1 = T2", ("B1", "T2", "B1=T2"))
                if "Fig. 20" in arreglo else ("B1", ("B1",))
            )
            return {
                "nodos": {
                    "T1": ("T1", 1, 0, ("T1",)),
                    "B1": (union[0], 1, 2, union[1]),
                    "B2": ("B2", 1, 4, ("B2",)),
                    "B3": ("B3", 1, 6, ("B3",)),
                },
                "elementos": [
                    ("cap", "C(T1-T2)", "T1", "B1"),
                    ("cap", "C(B1-B2)", "B1", "B2"),
                    ("cap", "C(B2-B3)", "B2", "B3"),
                    ("cap", "Term. B2", "B2", (3.8, 4)),
                    ("cap", "Term. B3", "B3", (3.8, 6)),
                    ("cable", (3.8, 4), (3.8, 6.9)),
                    ("tierra", (3.8, 6.9)),
                ],
            }
        return {
            "nodos": {
                "B1": ("B1", 1, 0, ("B1",)),
                "B2": ("B2", 1, 2.2, ("B2",)),
                "B3": ("B3", 1, 4.4, ("B3",)),
            },
            "elementos": [
                ("cap", "C(B1-B2)", "B1", "B2"),
                ("cap", "C(B2-B3)", "B2", "B3"),
                ("cap", "Term. B2", "B2", (3.8, 2.2)),
                ("cap", "Term. B3", "B3", (3.8, 4.4)),
                ("cable", (3.8, 2.2), (3.8, 5.3)),
                ("tierra", (3.8, 5.3)),
            ],
        }
    if equipo == "Apartarrayos":
        secciones = 1
        for palabra, numero in (
            ("Dos", 2), ("Tres", 3), ("Cuatro", 4), ("Cinco", 5),
        ):
            if palabra in arreglo:
                secciones = numero
        paso = 1.7
        nodos = {
            str(i + 1): (str(i + 1), 1, i * paso, (str(i + 1),))
            for i in range(secciones + 1)
        }
        elementos = [
            (
                "cap", "C12" if secciones == 1 else "ABCDE"[i],
                str(i + 1), str(i + 2),
            )
            for i in range(secciones)
        ]
        fondo = secciones * paso + 1.0
        elementos += [
            ("cable", str(secciones + 1), (1, fondo)),
            ("tierra", (1, fondo)),
        ]
        return {"nodos": nodos, "elementos": elementos}
    if equipo == "Cables de Potencia":
        if "Trifásico" in arreglo:
            return {
                "nodos": {
                    "A": ("A", 0, 0, ("A",)),
                    "B": ("B", 1.5, 0, ("B",)),
                    "C": ("C", 3, 0, ("C",)),
                    "PANT": ("Pantalla", 4.6, 2.4, ("Pantalla",)),
                },
                "elementos": [
                    ("cap", "A", "A", (0, 2.4)),
                    ("cap", "B", "B", (1.5, 2.4)),
                    ("cap", "C", "C", (3, 2.4)),
                    ("cable", (0, 2.4), "PANT"),
                    ("cable", "PANT", (4.6, 3.4)),
                    ("tierra", (4.6, 3.4)),
                ],
            }
        return {
            "nodos": {
                "COND": ("Conductor", 1, 0, ("Conductor",)),
                "PANT": ("Pantalla", 1, 2.4, ("Pantalla",)),
            },
            "elementos": [
                ("cap", "C", "COND", "PANT"),
                ("cable", "PANT", (1, 3.4)),
                ("tierra", (1, 3.4)),
            ],
        }
    if equipo == "Aceite Aislante":
        return {
            "nodos": {
                "HV": ("Electrodo HV", 0.5, 0, ("HV",)),
                "LV": ("Electrodo LV", 4.5, 0, ("LV",)),
                "G": ("Anillo de guarda", 2.5, 2.0, ("Guarda",)),
            },
            "elementos": [("cap", "ACEITE", "HV", "LV")],
        }
    return None


_COLOR_CAJA_ROL_FP = (
    ("GROUND", "#DC2626"),
    ("HV", "#111827"),
    ("GUARD", "#2563EB"),
    ("UST", "#0891B2"),
)

_ROLES_ESQUEMA_FP = {
    "HV": ("#111827", "#FFFFFF"),
    "GROUND": ("#EF4444", "#FFFFFF"),
    "GUARD": ("#2563EB", "#FFFFFF"),
    "UST": ("#0891B2", "#FFFFFF"),
    "FLOTANDO": ("#94A3B8", "#FFFFFF"),
}


def _terminales_campo_fp(texto):
    """Terminales escritas en una columna de la tabla de conexiones."""
    texto = str(texto or "").replace("*", "")
    if texto.strip() in ("", "-----", "---", "—"):
        return set()
    partes = re.split(r"[,+]|\sy\s", texto)
    return {parte.strip() for parte in partes if parte.strip()}


def _roles_esquema_fp(topo, prueba):
    """Rol de cada nodo en la prueba. El cable de alta manda sobre los demás."""
    roles = {}
    for rol, campo in (
        ("FLOTANDO", "flotando"), ("UST", "ust"), ("GUARD", "guard"),
        ("GROUND", "ground"), ("HV", "hv"),
    ):
        terminales = _terminales_campo_fp(prueba.get(campo, ""))
        for clave, (_etq, _x, _y, propias) in topo["nodos"].items():
            if terminales & set(propias):
                roles[clave] = rol
    return roles


def _dibujar_esquema_fp(
    padre, topo, prueba, modo, fondo="#FFFFFF", al_parpadear=None,
):
    """Esquema de capacitancias de la prueba.

    modo="mide": la capacitancia medida va en naranja y parpadea.
    modo="conexiones": cada terminal toma el color de su cable de prueba.
    """
    paso_x, paso_y, margen_x, margen_y = 72, 62, 64, 78
    nodos = topo["nodos"]

    def coordenada(ref):
        if isinstance(ref, str):
            return nodos[ref][1], nodos[ref][2]
        return ref

    puntos = [(x, y) for _e, x, y, _t in nodos.values()]
    for elemento in topo["elementos"]:
        for ref in elemento[1:]:
            if isinstance(ref, tuple):
                puntos.append(ref)
            elif ref in nodos:
                puntos.append(coordenada(ref))
    min_x = min(p[0] for p in puntos)
    max_x = max(p[0] for p in puntos)
    min_y = min(p[1] for p in puntos)
    max_y = max(p[1] for p in puntos)
    ancho = int((max_x - min_x) * paso_x + margen_x * 2 + 40)
    alto = int((max_y - min_y) * paso_y + margen_y * 2)
    lienzo = tk.Canvas(
        padre, width=ancho, height=alto, bg=fondo,
        highlightthickness=0, bd=0,
    )

    def px(ref):
        x, y = coordenada(ref)
        return (
            margen_x + (x - min_x) * paso_x,
            margen_y + (y - min_y) * paso_y,
        )

    verde = FP_VISTA_VERDE
    medidas = set(prueba.get("caps", ())) if modo == "mide" else set()
    parpadeo = []
    lienzo.create_text(
        18, 22, text="MEDICIÓN" if modo == "mide" else "CONEXIONES",
        anchor="w", fill=FP_VISTA_VERDE_OSCURO,
        font=("Consolas", 14, "bold"),
    )

    def trazo(x1, y1, x2, y2, medido=False, grosor=None):
        item = lienzo.create_line(
            x1, y1, x2, y2,
            fill=FP_VISTA_MEDICION if medido else verde,
            width=grosor or (4 if medido else 2), capstyle="round",
        )
        if medido:
            parpadeo.append(item)
        return item

    for elemento in topo["elementos"]:
        tipo = elemento[0]
        if tipo == "cable":
            (x1, y1), (x2, y2) = px(elemento[1]), px(elemento[2])
            trazo(x1, y1, x2, y2)
        elif tipo == "tierra":
            x, y = px(elemento[1])
            for indice, medio in enumerate((16, 10, 4)):
                lienzo.create_line(
                    x - medio, y + indice * 6, x + medio, y + indice * 6,
                    fill=verde, width=3,
                )
            lienzo.create_text(
                x, y + 26, text="TIERRA", fill=verde,
                font=("Consolas", 9, "bold"),
            )
        elif tipo == "bobina":
            _t, etiqueta, a, b = elemento
            (x1, y1), (x2, y2) = px(a), px(b)
            medido = etiqueta in medidas
            largo = math.hypot(x2 - x1, y2 - y1) or 1.0
            ux, uy = (x2 - x1) / largo, (y2 - y1) / largo
            coords = []
            for k in range(61):
                t = k / 60
                desvio = 8 * math.sin(t * math.pi * 12)
                coords += [
                    x1 + (x2 - x1) * t - uy * desvio,
                    y1 + (y2 - y1) * t + ux * desvio,
                ]
            item = lienzo.create_line(
                *coords, smooth=True,
                fill=FP_VISTA_MEDICION if medido else verde,
                width=4 if medido else 2,
            )
            if medido:
                parpadeo.append(item)
        elif tipo == "cap":
            _t, etiqueta, a, b = elemento
            (x1, y1), (x2, y2) = px(a), px(b)
            medido = etiqueta in medidas
            largo = math.hypot(x2 - x1, y2 - y1) or 1.0
            ux, uy = (x2 - x1) / largo, (y2 - y1) / largo
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            hueco, placa = 5, 14
            trazo(x1, y1, mx - ux * hueco, my - uy * hueco, medido)
            trazo(mx + ux * hueco, my + uy * hueco, x2, y2, medido)
            for signo in (-1, 1):
                cx = mx + signo * ux * hueco
                cy = my + signo * uy * hueco
                trazo(
                    cx + uy * placa, cy - ux * placa,
                    cx - uy * placa, cy + ux * placa,
                    medido, grosor=5 if medido else 3,
                )
            horizontal = abs(ux) > abs(uy)
            texto = lienzo.create_text(
                mx if horizontal else mx + placa + 8,
                my - placa - 10 if horizontal else my,
                text=etiqueta, anchor="s" if horizontal else "w",
                fill=FP_VISTA_MEDICION if medido else verde,
                font=("Consolas", 11, "bold"),
            )
            if medido:
                parpadeo.append(texto)

    roles = _roles_esquema_fp(topo, prueba) if modo == "conexiones" else {}
    fuente_nodo = tkfont.Font(family="Segoe UI", size=10, weight="bold")
    roles_parpadeo = []
    for clave, (etiqueta, _x, _y, _propias) in nodos.items():
        x, y = px(clave)
        rol = roles.get(clave)
        texto = f"{etiqueta}  ·  {rol}" if rol else etiqueta
        medio = max(34, fuente_nodo.measure(texto) // 2 + 12)
        relleno, tinta = _ROLES_ESQUEMA_FP.get(rol, ("#FFFFFF", "#0F172A"))
        caja_nodo = lienzo.create_rectangle(
            x - medio, y - 16, x + medio, y + 16,
            fill=relleno, outline=relleno if rol else verde, width=2,
        )
        rotulo_nodo = lienzo.create_text(
            x, y, text=texto, fill=tinta, font=fuente_nodo,
        )
        if rol:
            roles_parpadeo.append((caja_nodo, rotulo_nodo, relleno))

    estado = {"encendido": True}

    def parpadear():
        try:
            if not lienzo.winfo_exists():
                return
            estado["encendido"] = not estado["encendido"]
            encendido = estado["encendido"]
            # MEDICIÓN: la capacitancia medida se apaga y se enciende.
            for item in parpadeo:
                lienzo.itemconfigure(
                    item, fill=FP_VISTA_MEDICION if encendido else fondo,
                )
            # CONEXIONES: cada terminal con cable alterna relleno y contorno.
            for caja_nodo, rotulo_nodo, color in roles_parpadeo:
                lienzo.itemconfigure(
                    caja_nodo, fill=color if encendido else "#FFFFFF",
                )
                lienzo.itemconfigure(
                    rotulo_nodo, fill="#FFFFFF" if encendido else color,
                )
        except tk.TclError:
            return
        if al_parpadear is not None:
            if modo == "mide":
                al_parpadear("MEDICION" if encendido else None)
            else:
                al_parpadear("CONEXIONES" if encendido else "CONEXIONES_OFF")
        lienzo.after(450, parpadear)

    if parpadeo or roles_parpadeo:
        lienzo.after(450, parpadear)
    return lienzo


def _barra_degradada_fp(padre, fondo, **empaque):
    """Filo de color de las tarjetas: el de RA, con el verde al frente."""
    barra = tk.Canvas(padre, height=3, bg=fondo, highlightthickness=0, bd=0)
    barra.pack(fill="x", **empaque)
    paradas = (
        (0.0, (5, 150, 105)),
        (0.33, (132, 204, 22)),
        (0.66, (59, 130, 246)),
        (1.0, (5, 150, 105)),
    )

    def pintar(_evento=None):
        ancho = max(barra.winfo_width(), 4)
        barra.delete("all")
        for x in range(0, ancho, 2):
            t = x / (ancho - 1)
            for i in range(len(paradas) - 1):
                t0, c0 = paradas[i]
                t1, c1 = paradas[i + 1]
                if t <= t1 or i == len(paradas) - 2:
                    parte = max(0.0, min(1.0, (t - t0) / (t1 - t0)))
                    color = tuple(
                        int(c0[k] + (c1[k] - c0[k]) * parte) for k in range(3)
                    )
                    barra.create_line(
                        x, 0, x, 3, fill="#%02x%02x%02x" % color, width=2,
                    )
                    break

    barra.bind("<Configure>", pintar)
    return barra


def _barra_degradada_ttr(padre, fondo, **empaque):
    """Espectro de TTR: morado al inicio y rosa al final."""
    barra = tk.Canvas(padre, height=3, bg=fondo, highlightthickness=0, bd=0)
    barra.pack(fill="x", **empaque)
    paradas = (
        (0.0, (124, 58, 237)),
        (0.14, (75, 0, 130)),
        (0.28, (0, 0, 255)),
        (0.42, (0, 191, 255)),
        (0.56, (0, 200, 83)),
        (0.70, (255, 255, 0)),
        (0.82, (255, 127, 0)),
        (0.92, (255, 0, 0)),
        (1.0, (255, 77, 255)),
    )

    def pintar(_evento=None):
        ancho = max(barra.winfo_width(), 4)
        barra.delete("all")
        for x in range(0, ancho, 2):
            t = x / (ancho - 1)
            for i in range(len(paradas) - 1):
                t0, c0 = paradas[i]
                t1, c1 = paradas[i + 1]
                if t <= t1 or i == len(paradas) - 2:
                    parte = max(0.0, min(1.0, (t - t0) / (t1 - t0)))
                    color = tuple(
                        int(c0[k] + (c1[k] - c0[k]) * parte) for k in range(3)
                    )
                    barra.create_line(
                        x, 0, x, 3, fill="#%02x%02x%02x" % color, width=2,
                    )
                    break

    barra.bind("<Configure>", pintar)
    return barra


def _cargar_lecturas_fp():
    try:
        datos = json.loads(RUTA_LECTURAS_FP.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return datos if isinstance(datos, dict) else {}


def _guardar_lecturas_fp(lecturas):
    try:
        RUTA_LECTURAS_FP.write_text(
            json.dumps(lecturas, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    except OSError:
        return False
    return True


class API:
    """Puente entre el menú web y las funciones de SAPE2."""

    def __init__(self):
        self._window = None
        self._ra_process = None
        self._fp_process = None
        self._ttr_process = None
        self._historial_process = None

    def _lanzar_modulo(self, atributo, bandera):
        proceso = getattr(self, atributo)
        if proceso is not None and proceso.poll() is None:
            return True
        script = Path(__file__).resolve()
        pythonw = Path(sys.executable).with_name("pythonw.exe")
        ejecutable = pythonw if pythonw.is_file() else Path(sys.executable)
        flags = (
            getattr(subprocess, "CREATE_NO_WINDOW", 0)
            if ejecutable == Path(sys.executable)
            else 0
        )
        setattr(self, atributo, subprocess.Popen(
            [str(ejecutable), str(script), bandera],
            cwd=str(script.parent),
            creationflags=flags,
        ))
        return True

    def seleccionar_opcion(self, num, nombre):
        print(f"[SAPE2] Opción seleccionada: {num}. {nombre}")
        if str(num) == "1":
            return self._lanzar_modulo("_ra_process", "--ra")
        if str(num) == "2":
            return self._lanzar_modulo("_fp_process", "--fp")
        if str(num) == "3":
            return self._lanzar_modulo("_ttr_process", "--ttr")
        if str(num) == "7":
            return self._lanzar_modulo("_historial_process", "--historial")
        elif str(num) == "9":
            self.cerrar_app()
        return True

    def cerrar_app(self):
        print("[SAPE2] Cerrando aplicación...")
        if self._window is not None:
            self._window.destroy()

def main():
    if (
        "--ra" in sys.argv[1:] or "--fp" in sys.argv[1:]
        or "--ttr" in sys.argv[1:] or "--historial" in sys.argv[1:]
    ):
        app = AppSAPE()
        app.withdraw()
        if "--fp" in sys.argv[1:]:
            ventana_mod = app.abrir_prueba_factor()
        elif "--ttr" in sys.argv[1:]:
            ventana_mod = app.abrir_prueba_ttr()
        elif "--historial" in sys.argv[1:]:
            ventana_mod = app.mostrar_historial()
        else:
            ventana_mod = app.abrir_prueba_aislamiento()
        ventana_mod.bind(
            "<Destroy>",
            lambda event: app.destroy() if event.widget is ventana_mod else None,
            add="+",
        )
        app.mainloop()
        return

    api = API()
    # pywebview, en modo privado, guarda WebView2 en un TemporaryDirectory
    # que se borra al instante. El control queda del color de fondo y el
    # menú no se pinta. Esta carpeta vive mientras la ventana está abierta.
    datos_menu = tempfile.mkdtemp(prefix="sape-menu-")
    menu_archivo = Path(__file__).with_name("SAPE2_menu.html")
    try:
        ventana = webview.create_window(
            title="[ S.A.P.E. ] - Sistema de Análisis de Pruebas Eléctricas",
            url=str(menu_archivo),
            width=500,
            height=960,
            resizable=False,
            background_color="#050505",
            js_api=api,
        )
        api._window = ventana
        ventana.events.shown += lambda: _aplicar_icono_webview(ventana)
        webview.start(debug=False, storage_path=datos_menu, http_server=True)
    except Exception:
        if (
            api._ra_process is not None
            and api._ra_process.poll() is None
        ):
            api._ra_process.terminate()
        raise


if __name__ == "__main__":
    main()
