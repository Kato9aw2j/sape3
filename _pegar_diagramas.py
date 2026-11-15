# -*- coding: utf-8 -*-
from pathlib import Path

src = Path(
    r"c:\Users\LapOne MX\Documents\Programacion Modo JEDI\S. A. P. E\sape_ra_ui.py"
).read_text(encoding="utf-8").splitlines()
lienzo = "\n".join(src[821:1122])
dest = Path(r"c:\Users\LapOne MX\Documents\Programacion PYTHON\SAPE 2\SAPE2.py")
text = dest.read_text(encoding="utf-8")
if "_LienzoDiagrama" in text:
    raise SystemExit("ya insertado")

helpers = r'''
_TEXTO = "#E2E8F0"
_SAPE1_MOD = None
_SAPE1_RUTA = Path(
    r"c:\Users\LapOne MX\Documents\Programacion Modo JEDI\S. A. P. E\SAPE_1.py"
)


def _sape1():
    global _SAPE1_MOD
    if _SAPE1_MOD is None:
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


'''

needle = "class AppSAPE(tk.Tk):"
text = text.replace(needle, helpers + "\n" + lienzo + "\n\n\n" + needle, 1)
dest.write_text(text, encoding="utf-8")
print("insertado", dest.stat().st_size)
