// SAPE móvil: Resistencia de Aislamiento en cuatro pasos.
"use strict";

const CLAVE_ESTADO = "sape-movil-estado";
const CLAVE_HISTORIAL = "sape-movil-historial";
const CLAVE_ANEXO_A = "sape-movil-anexo-a";

const estado = {
  vista: "inicio", // inicio | ra | fp | historial
  paso: 1,
  modo: "mide",
  datos: {
    equipo: "2d", configuracion: "Trifásico", fase: "A", terciario: "con",
    secciones: "varias", tempAmbiente: "", humedad: "", tempDevanado: "",
    aislamiento: "aceite",
  },
  prueba: 0,
  lecturas: { r30: "", r1: "", r10: "" },
  resultado: null,
  // Factor de Potencia al Aislamiento (ST-CT-002)
  pasoFp: 1,
  datosFp: {
    equipo: EQUIPOS_FP[0], arreglo: "", configuracion: "Trifásico", fase: "A",
    aislamiento: "Sumergido en Aceite", preservacion: PRESERVACION_FP[0],
    estado: "En operación", claseKv: "Menor de 115 kV",
    aislamientoCable: TABLA9_FP[0][0],
    tempAceite: "", tempAmbiente: "", humedad: "",
  },
  pruebaFp: 0,
  lecturasFp: { kv: "10", ma: "", watts: "" },
  resultadoFp: null,
  modoFp: "mide",
  // Relación de Transformación / TTR (ST-CT-007)
  pasoTtr: 1,
  datosTtr: {
    equipo: EQUIPOS_TTR[0], configuracion: "Trifásico", fase: "A",
    conexion: "Estrella - Delta", voltajeH: "", voltajeX: "", voltajeY: "",
    regulacionCfe: "Sí", tipoCambiador: CAMBIADORES_TTR[0].valor,
    medicionRealizar: "Directa", polaridad: "Sustractiva",
    tempAmbiente: "", humedad: "", tempDevanado: "",
  },
  pruebaTtr: 0,
  tapTtr: null,
  lecturasTtr: { relacionTeoricaManual: "", relacionMedida: "" },
  resultadoTtr: null,
  // Anexo A — Formatos de Prueba (captura de todas las pruebas del equipo,
  // igual que el Anexo A de PC: identificación, condiciones, datos propios
  // del equipo, orden de trabajo, equipo de medición y firmas).
  lecturasAnexoRa: {},
  datosAnexoRa: {},
  lecturasAnexoFp: {},
  datosAnexoFp: {},
  anexoEstado: "",
};

function leer(clave, respaldo) {
  try {
    const crudo = localStorage.getItem(clave);
    return crudo ? JSON.parse(crudo) : respaldo;
  } catch (_e) {
    return respaldo;
  }
}

function guardar(clave, valor) {
  try {
    localStorage.setItem(clave, JSON.stringify(valor));
  } catch (_e) {
    // Sin almacenamiento (modo privado): la app sigue funcionando.
  }
}

function recordar() {
  guardar(CLAVE_ESTADO, {
    datos: estado.datos, prueba: estado.prueba, lecturas: estado.lecturas,
    datosFp: estado.datosFp, pruebaFp: estado.pruebaFp, lecturasFp: estado.lecturasFp,
    datosTtr: estado.datosTtr, pasoTtr: estado.pasoTtr, pruebaTtr: estado.pruebaTtr,
    tapTtr: estado.tapTtr, lecturasTtr: estado.lecturasTtr,
    lecturasAnexoRa: estado.lecturasAnexoRa, datosAnexoRa: estado.datosAnexoRa,
    lecturasAnexoFp: estado.lecturasAnexoFp, datosAnexoFp: estado.datosAnexoFp,
  });
}

const previo = leer(CLAVE_ESTADO, null);
if (previo && previo.datos) {
  Object.assign(estado.datos, previo.datos);
  estado.prueba = previo.prueba || 0;
  Object.assign(estado.lecturas, previo.lecturas || {});
}
if (previo && previo.datosFp) {
  Object.assign(estado.datosFp, previo.datosFp);
  estado.pruebaFp = previo.pruebaFp || 0;
  Object.assign(estado.lecturasFp, previo.lecturasFp || {});
}
if (previo && previo.datosTtr) {
  Object.assign(estado.datosTtr, previo.datosTtr);
  estado.pruebaTtr = previo.pruebaTtr || 0;
  estado.tapTtr = previo.tapTtr || null;
  Object.assign(estado.lecturasTtr, previo.lecturasTtr || {});
}
if (previo) {
  Object.assign(estado.lecturasAnexoRa, previo.lecturasAnexoRa || {});
  Object.assign(estado.datosAnexoRa, previo.datosAnexoRa || {});
  Object.assign(estado.lecturasAnexoFp, previo.lecturasAnexoFp || {});
  Object.assign(estado.datosAnexoFp, previo.datosAnexoFp || {});
}

const esc = (texto) =>
  String(texto).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

function formatoKv(valor) {
  const partes = String(valor).replace("/", "-").split("-");
  const nums = partes.map((parte) => Number(parte));
  if (nums.some((n) => !Number.isFinite(n))) return String(valor);
  return nums.map((n) => String(n / 1000)).join(" - ") + " kV";
}

function pruebaActual() {
  const lista = pruebasDe(estado.datos);
  if (estado.prueba >= lista.length) estado.prueba = 0;
  return lista[estado.prueba];
}

const MENU = [
  ["1", "Resistencia de Aislamiento", "R.A.Ω", "ra"],
  ["2", "Factor de Potencia al Aislamiento", "%F.P.", "fp"],
  ["3", "Relación de Transformación", "T.T.R.", "ttr"],
  ["4", "Corriente de Excitación", "I.EXC", null],
  ["5", "Resistencia Óhmica de Devanados", "R.O.Ω", null],
  ["6", "Normativa y Procedimientos", "CFE-IEEE", null],
  ["7", "Historial de Análisis", "", "historial"],
];

function vistaInicio() {
  const filas = MENU.map(([num, nombre, marca, destino]) => `
    <button class="menu-item ${destino === "ra" ? "menu-item-ra" : ""} ${destino === "fp" ? "menu-item-fp" : ""} ${destino === "ttr" ? "menu-item-ttr" : ""}" ${destino ? `data-ir="${destino}"` : "disabled"}>
      <span>${num}. ${esc(nombre)}</span>
      <span class="marca">${destino ? (marca ? `[ ${esc(marca)} ]` : "›") : "Próximamente"}</span>
    </button>`).join("");
  return `
    <main class="inicio">
      <div class="logo-cfe-3d" id="logo-cfe-3d"><div class="logo-cfe">CFE</div></div>
      <p class="org">COMISIÓN FEDERAL DE ELECTRICIDAD<br>ZONA DE TRANSMISIÓN JALISCO ORIENTE<br>SUBESTACIONES</p>
      <h1 class="logo-sape">[ S.A.P.E. ]</h1>
      <p class="sub">SISTEMA DE ANÁLISIS DE PRUEBAS ELÉCTRICAS<br>VERSIÓN MÓVIL 1.0</p>
      <nav class="menu">${filas}</nav>
      <p class="pie">ST-CT-001 · ST-CT-002 · Funciona sin conexión</p>
    </main>`;
}

const PASOS = ["Datos del equipo", "Selección de pruebas", "Diagramas de bloques", "Captura de lecturas"];

function barraPasos() {
  return `<ol class="pasos">${PASOS.map((nombre, i) => `
    <li><button data-paso="${i + 1}" class="${estado.paso === i + 1 ? "activo" : ""}" aria-label="${esc(nombre)}">
      <b>0${i + 1}</b></button></li>`).join("")}</ol>`;
}

function campo(etiqueta, clave, extra) {
  return `<label class="campo"><span>${esc(etiqueta)}</span>
    <input inputmode="decimal" data-dato="${clave}" value="${esc(estado.datos[clave])}" ${extra || ""}></label>`;
}

function opciones(clave, pares, bloqueada) {
  return `<div class="segmentos">${pares.map(([valor, texto]) => `
    <button data-dato="${clave}" data-valor="${valor}"
      class="${estado.datos[clave] === valor ? "activo" : ""}"
      ${bloqueada === valor ? "disabled" : ""}>${esc(texto)}</button>`).join("")}</div>`;
}

function paso1() {
  const d = estado.datos;
  const solido = soloSolido(d.equipo);
  if (solido) d.aislamiento = "seco";
  const instrumento = ["tc", "tp", "tpc"].includes(d.equipo);
  let extra = "";
  if (instrumento) {
    extra = `<div class="campo"><span>Fase</span>${opciones("fase", [["A", "A"], ["B", "B"], ["C", "C"]])}</div>`;
  } else {
    extra = `<div class="campo"><span>Configuración</span>${opciones("configuracion", [["Trifásico", "Trifásico"], ["Monofásico", "Monofásico"]])}</div>`;
  }
  if (d.equipo === "apart") {
    extra += `<div class="campo"><span>Configuración del apartarrayos</span>${opciones("secciones", [["una", "Una sección"], ["varias", "Varias secciones"]])}</div>`;
  }
  if (d.equipo === "auto") {
    extra += `<div class="campo"><span>Devanado terciario</span>${opciones("terciario", [["con", "Con terciario"], ["sin", "Sin terciario"]])}</div>`;
  }
  return `
    <h2>01. Datos del equipo</h2>
    <p class="nota">Parámetros de placa y condiciones ambientales del equipo bajo ensayo.</p>
    <label class="campo"><span>Tipo de equipo</span>
      <select data-dato="equipo">${EQUIPOS.map((e) =>
        `<option value="${e.id}" ${e.id === d.equipo ? "selected" : ""}>${esc(e.nombre)}</option>`).join("")}
      </select></label>
    ${extra}
    <div class="rejilla">
      ${campo("Temp. ambiente (°C)", "tempAmbiente")}
      ${campo("Humedad relativa (%)", "humedad")}
      ${campo("Temp. del devanado (°C)", "tempDevanado")}
    </div>
    <div class="campo"><span>Tipo de aislamiento</span>
      ${opciones("aislamiento", [["aceite", "Sumergido en aceite"], ["seco", "Seco (sólido)"]], solido ? "aceite" : null)}
      ${solido ? `<small>Este equipo es de aislamiento sólido: no lleva aceite.</small>` : ""}
    </div>`;
}

function chips(prueba) {
  const par = (rol, valor) =>
    VACIO.has(valor) ? "" : `<span class="chip ${rol}"><b>${rol[0]}</b> ${esc(valor)}</span>`;
  return par("LINEA", prueba.linea) + par("TIERRA", prueba.tierra) + par("GUARDA", prueba.guarda);
}

// Celda de tabla de pruebas: pastilla de color si hay valor, "—" si no la
// hay. Igual que las columnas de _crear_tabla_pruebas / _tabla_fp en PC.
function celdaPildora(valor, clase) {
  return !valor || VACIO.has(valor)
    ? `<td class="vacia">—</td>`
    : `<td><span class="pildora ${clase}">${esc(valor)}</span></td>`;
}

function paso2() {
  const lista = pruebasDe(estado.datos);
  const actual = pruebaActual();
  return `
    <h2>02. Selección de pruebas</h2>
    <p class="nota">${esc(equipoDe(estado.datos.equipo).nombre)}. Elija la prueba a realizar.</p>
    <div class="tabla-pruebas"><table>
      <thead><tr>
        <th></th><th>Prueba</th><th>kV CC</th>
        <th class="th-linea">Línea (+)</th><th class="th-tierra">Tierra (−)</th>
        <th class="th-guarda">Guarda</th><th class="th-medicion">Medición</th>
      </tr></thead>
      <tbody>${lista.map((prueba, i) => `
        <tr class="${i === estado.prueba ? "activa" : ""}" data-prueba="${i}">
          <td class="led"><span class="punto ${i === estado.prueba ? "on" : ""}"></span></td>
          <td class="num">${esc(prueba.prueba)}</td>
          <td>${esc(formatoKv(prueba.kv))}</td>
          ${celdaPildora(prueba.linea, "linea")}
          ${celdaPildora(prueba.tierra, "tierra")}
          ${celdaPildora(prueba.guarda, "guarda")}
          ${celdaPildora(prueba.medicion, "medicion")}
        </tr>`).join("")}</tbody>
    </table></div>
    <p class="nota">Prueba ${esc(actual.prueba)} · ${esc(actual.medicion)} · ${actual.minutos} min</p>`;
}

function paso3() {
  const prueba = pruebaActual();
  const medicion = leyendaMedicion(estado.datos, prueba);
  const conexiones = leyendaConexiones(prueba);
  return `
    <h2>03. Diagramas de bloques</h2>
    <p class="nota">Prueba ${esc(prueba.prueba)} · ${esc(prueba.medicion)}</p>
    <div class="segmentos vista">
      <button data-modo="mide" class="${estado.modo === "mide" ? "activo" : ""}">Medición</button>
      <button data-modo="conexiones" class="${estado.modo === "conexiones" ? "activo" : ""}">Conexiones</button>
    </div>
    <div class="diagrama">${dibujarDiagrama(estado.datos, prueba, estado.modo)}</div>
    <h3>Medición</h3>
    <ul class="leyenda">${medicion.map((fila) => `
      <li><span class="badge ${fila.medido ? "medido" : ""}">${fila.codigo}</span>${esc(fila.texto)}</li>`).join("")}</ul>
    <h3>Conexiones</h3>
    <ul class="leyenda">${conexiones.map((fila) => `
      <li><span class="badge ${fila.rol}">${ROTULO[fila.rol]}</span>${esc(fila.texto)}</li>`).join("")}</ul>`;
}

function tarjetaDictamen(res) {
  if (!res) return "";
  if (res.error) return `<div class="aviso">${esc(res.error)}</div>`;
  const indices = [
    res.ia != null ? `<div><small>Índice de absorción (ia)</small><b>${res.ia.toFixed(2)}</b></div>` : "",
    res.ip != null ? `<div><small>Índice de polarización (ip)</small><b>${res.ip.toFixed(2)}</b></div>` : "",
  ].join("");
  return `
    <section class="dictamen ${res.estado}">
      <header>DICTAMEN: ${res.estado}</header>
      ${indices ? `<div class="indices">${indices}</div>` : ""}
      <ul>${res.lineas.map((linea) => `<li>${esc(linea)}</li>`).join("")}</ul>
    </section>
    <div class="acciones">
      <button class="secundario" data-accion="guardar">Guardar en historial</button>
      ${navigator.share ? `<button class="secundario" data-accion="compartir">Compartir</button>` : ""}
    </div>`;
}

function paso4() {
  const prueba = pruebaActual();
  const d = estado.datos;
  const temp = numero(d.tempDevanado);
  const base = baseTemp(d.equipo);
  const kt = temp == null ? null : ktEquipo(temp, d);
  const origen = base === 40 ? "IEEE 43" : `Tabla 1, ${enAceite(d) ? "aceite" : "seco"}`;
  const entrada = (clave, etiqueta) => `
    <label class="campo"><span>${etiqueta}</span>
      <input inputmode="decimal" data-lectura="${clave}" value="${esc(estado.lecturas[clave])}" placeholder="MΩ"></label>`;
  return `
    <h2>04. Captura de lecturas</h2>
    <p class="nota">Prueba ${esc(prueba.prueba)} · ${esc(prueba.medicion)} · ${esc(formatoKv(prueba.kv))}</p>
    <div class="kt">
      <div><small>Factor de corrección a ${base} °C (${origen})</small>
        <b>${kt == null ? "—" : kt.toFixed(3)}</b></div>
      <div><small>Temp. del devanado</small><b>${temp == null ? "—" : `${temp} °C`}</b></div>
    </div>
    ${temp == null ? `<div class="aviso">Falta la temperatura del devanado. Captúrela en el paso 01.</div>` : ""}
    <div class="rejilla">
      ${prueba.minutos === 10 ? entrada("r30", "30 s") : ""}
      ${entrada("r1", "1 min")}
      ${prueba.minutos === 10 ? entrada("r10", "10 min") : ""}
    </div>
    <p class="nota">Sin letra son MΩ. Agregue G para gigaohms o T para teraohms (ej. 2.5G).</p>
    <button class="primario" data-accion="calcular">Calcular dictamen</button>
    <div id="dictamen">${tarjetaDictamen(estado.resultado)}</div>`;
}

function vistaRa() {
  const cuerpo = [paso1, paso2, paso3, paso4][estado.paso - 1]();
  return `
    <header class="barra">
      <button class="atras" data-ir="inicio" aria-label="Volver al menú">‹</button>
      <div><b>Resistencia de Aislamiento</b><small>ST-CT-001</small></div>
      <button class="anexo" data-ir="anexoA">Anexo A</button>
    </header>
    ${barraPasos()}
    <main class="contenido">${cuerpo}</main>
    <footer class="pie-pasos">
      <button class="secundario" data-paso="${Math.max(1, estado.paso - 1)}" ${estado.paso === 1 ? "disabled" : ""}>‹ Anterior</button>
      <button class="primario" data-paso="${Math.min(4, estado.paso + 1)}" ${estado.paso === 4 ? "disabled" : ""}>Siguiente ›</button>
    </footer>`;
}

// ---------- Factor de Potencia al Aislamiento (ST-CT-002) ----------

function campoFp(etiqueta, clave, extra) {
  return `<label class="campo"><span>${esc(etiqueta)}</span>
    <input inputmode="decimal" data-datofp="${clave}" value="${esc(estado.datosFp[clave])}" ${extra || ""}></label>`;
}

function opcionesFp(clave, pares, bloqueada) {
  return `<div class="segmentos">${pares.map(([valor, texto]) => `
    <button data-datofp="${clave}" data-valor="${valor}"
      class="${estado.datosFp[clave] === valor ? "activo" : ""}"
      ${bloqueada === valor ? "disabled" : ""}>${esc(texto)}</button>`).join("")}</div>`;
}

function pasoFp1() {
  const d = estado.datosFp;
  const potencia = esPotenciaFp(d.equipo);
  const esTc = d.equipo === "Transformadores de Corriente - TCs";
  const esCable = d.equipo === "Cables de Potencia";
  const aceiteEquipo = d.equipo.includes("Aceite");
  const arreglos = ARREGLOS_FP[d.equipo] || [];
  if (arreglos.length) d.arreglo = arregloFp(d.equipo, d.arreglo);
  const fase = llevaFaseFp(d.equipo, d.configuracion);
  const necesitaAislamiento = !d.equipo.includes("Apartarrayos") && !esCable && !aceiteEquipo;
  const seco = necesitaAislamiento && !String(d.aislamiento).includes("Aceite");
  const necesitaTemp = aceiteEquipo || (necesitaAislamiento && !seco);

  let extra = "";
  if (potencia) {
    extra += `<div class="campo"><span>Configuración</span>${opcionesFp("configuracion", [["Trifásico", "Trifásico"], ["Monofásico", "Monofásico"]])}</div>`;
  }
  if (fase) {
    extra += `<div class="campo"><span>Fase</span>${opcionesFp("fase", [["A", "A"], ["B", "B"], ["C", "C"]])}</div>`;
  }
  if (arreglos.length) {
    extra += `<label class="campo"><span>Arreglo de prueba</span>
      <select data-datofp="arreglo">${arreglos.map((a) =>
        `<option value="${esc(a)}" ${a === d.arreglo ? "selected" : ""}>${esc(a)}</option>`).join("")}
      </select></label>`;
  }
  if (esTc) {
    extra += `<div class="campo"><span>Clase del TC</span>${opcionesFp("claseKv", [["Menor de 115 kV", "< 115 kV"], ["115 kV o mayor", "≥ 115 kV"]])}</div>`;
  }
  if (esCable) {
    extra += `<label class="campo"><span>Aislamiento del cable (Tabla 9)</span>
      <select data-datofp="aislamientoCable">${TABLA9_FP.map(([n]) =>
        `<option value="${esc(n)}" ${n === d.aislamientoCable ? "selected" : ""}>${esc(n)}</option>`).join("")}
      </select></label>`;
  }
  if (potencia) {
    extra += `<div class="campo"><span>Estado del equipo</span>${opcionesFp("estado", [["En operación", "En operación"], ["Puesta en servicio", "Puesta en servicio"]])}</div>`;
  }
  if (necesitaAislamiento) {
    extra += `<div class="campo"><span>Tipo de aislamiento</span>
      ${opcionesFp("aislamiento", [["Sumergido en Aceite", "Sumergido en aceite"], ["Seco", "Seco"]])}</div>`;
  }
  if (potencia && !seco) {
    extra += `<label class="campo"><span>Preservación del aceite</span>
      <select data-datofp="preservacion">${PRESERVACION_FP.map((p) =>
        `<option value="${esc(p)}" ${p === d.preservacion ? "selected" : ""}>${esc(p)}</option>`).join("")}
      </select></label>`;
  }
  return `
    <h2>01. Datos del equipo</h2>
    <p class="nota">Parámetros del equipo y condiciones ambientales. Procedimiento ST-CT-002.</p>
    <label class="campo"><span>Tipo de equipo</span>
      <select data-datofp="equipo">${EQUIPOS_FP.map((e) =>
        `<option value="${esc(e)}" ${e === d.equipo ? "selected" : ""}>${esc(e)}</option>`).join("")}
      </select></label>
    ${extra}
    <div class="rejilla">
      ${campoFp("Temp. ambiente (°C)", "tempAmbiente")}
      ${campoFp("Humedad relativa (%)", "humedad")}
      ${necesitaTemp ? campoFp("Temp. del aceite (°C)", "tempAceite") : ""}
    </div>
    ${necesitaTemp ? "" : `<p class="nota">Este equipo no necesita la temperatura del aceite para corregir el %FP.</p>`}`;
}

function pasoFp2() {
  const d = estado.datosFp;
  const lista = filasFp(d.equipo, d.arreglo);
  if (estado.pruebaFp >= lista.length) estado.pruebaFp = 0;
  if (!lista.length) {
    return `
      <h2>02. Selección de prueba</h2>
      <p class="nota">${esc(d.equipo)}${d.arreglo ? " · " + esc(d.arreglo) : ""}.</p>
      <p class="aviso">No hay pruebas definidas para este equipo.</p>`;
  }
  const actual = lista[estado.pruebaFp];
  return `
    <h2>02. Selección de prueba</h2>
    <p class="nota">${esc(d.equipo)}${d.arreglo ? " · " + esc(d.arreglo) : ""}. Elija la prueba a realizar.</p>
    <div class="tabla-pruebas"><table>
      <thead><tr>
        <th></th><th>Prueba</th><th>kV</th><th>Modo</th>
        <th class="th-hv">Energizar (HV)</th><th class="th-ground">Ground</th>
        <th class="th-guard">Guard</th><th class="th-ust">UST</th><th class="th-medicion">Mide</th>
      </tr></thead>
      <tbody>${lista.map((pr, i) => {
        const guard = pr.flotando ? `${pr.flotando} flotando` : pr.guard;
        return `
        <tr class="${i === estado.pruebaFp ? "activa" : ""}" data-pruebafp="${i}">
          <td class="led"><span class="punto ${i === estado.pruebaFp ? "on" : ""}"></span></td>
          <td class="num">${esc(pr.prueba)}</td>
          <td>${esc(pr.kv)}</td>
          <td>${esc(pr.modo)}</td>
          ${celdaPildora(pr.hv, "hv")}
          ${celdaPildora(pr.ground, "ground")}
          ${celdaPildora(guard, "guard")}
          ${celdaPildora(pr.ust, "ust")}
          ${celdaPildora(pr.medicion, "medicion")}
        </tr>`;
      }).join("")}</tbody>
    </table></div>
    <p class="nota">Prueba ${esc(actual.prueba)} · ${esc(actual.medicion || actual.modo)}</p>`;
}

function chipFp(rol, clase, valor) {
  return (!valor || valor === "-----") ? "" : `<span class="chip ${clase}"><b>${esc(rol)}</b> ${esc(valor)}</span>`;
}

function pasoFp3() {
  const d = estado.datosFp;
  const lista = filasFp(d.equipo, d.arreglo);
  const pr = lista[estado.pruebaFp] || lista[0] || {};
  return `
    <h2>03. Diagramas de bloques</h2>
    <p class="nota">Prueba ${esc(pr.prueba || "—")} · ${esc(pr.medicion || "—")} · ${esc(pr.kv || "—")} kV · ${esc(pr.modo || "—")}</p>
    <div class="segmentos vista">
      <button data-modofp="mide" class="${estado.modoFp === "conexiones" ? "" : "activo"}">Medición</button>
      <button data-modofp="conexiones" class="${estado.modoFp === "conexiones" ? "activo" : ""}">Conexiones</button>
    </div>
    <div class="diagrama">${dibujarDiagramaFp(d, pr, estado.modoFp)}</div>
    <h3>Conexiones de esta prueba</h3>
    <div class="chips" style="justify-content:center;margin-bottom:6px;">
      ${chipFp("HV", "LINEA", pr.hv)}
      ${chipFp("TIERRA", "TIERRA", pr.ground)}
      ${chipFp("GUARDA", "GUARDA", pr.guard)}
      ${chipFp("UST", "UST", pr.ust)}
      ${pr.flotando ? `<span class="chip UST"><b>FLOTA</b> ${esc(pr.flotando)}</span>` : ""}
    </div>
    <p class="nota">Modo del equipo de prueba: <b>${esc(pr.modo || "—")}</b>. Se energiza ${esc(pr.hv || "—")}; TIERRA se conecta al retorno del instrumento; GUARDA excluye esa parte de la medición; UST la deja flotando y fuera del cálculo.</p>
    <h3>Qué mide esta prueba</h3>
    <ul class="leyenda"><li><span class="badge medido">${esc(pr.prueba || "—")}</span>${esc(pr.medicion || "Sin definir")}</li></ul>`;
}

function tarjetaDictamenFp(res) {
  if (!res) return "";
  if (res.error) return `<div class="aviso">${esc(res.error)}</div>`;
  return `
    <section class="dictamen ${res.estado}">
      <header>DICTAMEN: ${res.estado}</header>
      <div class="indices">
        <div><small>%FP medido</small><b>${res.fp.toFixed(3)}</b></div>
        <div><small>%FP a 20 °C</small><b>${res.fp20.toFixed(3)}</b></div>
      </div>
      <ul>
        <li>Kt = ${res.kt.toFixed(3)} (${esc(res.tabla)}).</li>
        <li>Potencia aparente: ${res.va.toFixed(2)} VA. Pérdidas: ${res.watts.toFixed(4)} W${res.apartarrayos ? ` (${res.mw.toFixed(1)} mW)` : ""}.</li>
        <li>Capacitancia ≈ ${res.cap.toFixed(1)} pF.</li>
        <li>${esc(res.criterio)}</li>
        <li>${esc(res.frase)}</li>
      </ul>
    </section>
    <div class="acciones">
      <button class="secundario" data-accionfp="guardar">Guardar en historial</button>
      ${navigator.share ? `<button class="secundario" data-accionfp="compartir">Compartir</button>` : ""}
    </div>`;
}

function pasoFp4() {
  const d = estado.datosFp;
  const lista = filasFp(d.equipo, d.arreglo);
  const pr = lista[estado.pruebaFp] || lista[0] || {};
  const l = estado.lecturasFp;
  const kt = ktFp(d);
  return `
    <h2>04. Captura de lecturas</h2>
    <p class="nota">Prueba ${esc(pr.prueba || "—")} · ${esc(pr.medicion || "—")}</p>
    <div class="kt">
      <div><small>Factor de corrección (${esc(kt.tabla || "—")})</small>
        <b>${kt.kt == null ? "—" : kt.kt.toFixed(3)}</b></div>
      <div><small>Temp. del aceite</small><b>${d.tempAceite ? `${esc(d.tempAceite)} °C` : "—"}</b></div>
    </div>
    ${kt.kt == null ? `<div class="aviso">Falta la temperatura del aceite. Captúrela en el paso 01.</div>` : ""}
    <div class="rejilla">
      <label class="campo"><span>Tensión de prueba (kV)</span>
        <input inputmode="decimal" data-lecturafp="kv" value="${esc(l.kv)}"></label>
      <label class="campo"><span>Corriente (mA)</span>
        <input inputmode="decimal" data-lecturafp="ma" value="${esc(l.ma)}"></label>
      <label class="campo"><span>Pérdidas (W)</span>
        <input inputmode="decimal" data-lecturafp="watts" value="${esc(l.watts)}"></label>
    </div>
    <p class="nota">La tensión de prueba va de más de 0 hasta 12 kV.</p>
    <button class="primario" data-accionfp="calcular">Calcular dictamen</button>
    <div id="dictamenfp">${tarjetaDictamenFp(estado.resultadoFp)}</div>`;
}

function calcularFp() {
  const d = estado.datosFp;
  const l = estado.lecturasFp;
  const kv = numero(l.kv);
  const ma = numero(l.ma);
  const watts = numero(l.watts);
  if (kv == null || kv <= 0 || kv > 12) {
    return { error: "La tensión de prueba va de más de 0 hasta 12 kV." };
  }
  if (ma == null || ma <= 0 || watts == null) {
    return { error: "Escriba la corriente en mA y las pérdidas en Watts." };
  }
  if (watts < 0 && !d.equipo.includes("TPs")) {
    return { error: "Las pérdidas no pueden ser negativas en este equipo." };
  }
  const res = evaluarFp(d, kv, ma, watts);
  if (!res) return { error: "Falta la temperatura del aceite. Captúrela en el paso 01." };
  return res;
}

const PASOS_FP = ["Datos del equipo", "Selección de prueba", "Diagramas de bloques", "Captura de lecturas"];

function vistaFp() {
  const cuerpo = [pasoFp1, pasoFp2, pasoFp3, pasoFp4][estado.pasoFp - 1]();
  return `
    <header class="barra">
      <button class="atras" data-ir="inicio" aria-label="Volver al menú">‹</button>
      <div><b>Factor de Potencia al Aislamiento</b><small>ST-CT-002</small></div>
      <button class="anexo" data-ir="anexoAFp">Anexo A</button>
    </header>
    <ol class="pasos">${PASOS_FP.map((nombre, i) => `
      <li><button data-pasofp="${i + 1}" class="${estado.pasoFp === i + 1 ? "activo" : ""}" aria-label="${esc(nombre)}">
        <b>0${i + 1}</b></button></li>`).join("")}</ol>
    <main class="contenido">${cuerpo}</main>
    <footer class="pie-pasos">
      <button class="secundario" data-pasofp="${Math.max(1, estado.pasoFp - 1)}" ${estado.pasoFp === 1 ? "disabled" : ""}>‹ Anterior</button>
      <button class="primario" data-pasofp="${Math.min(4, estado.pasoFp + 1)}" ${estado.pasoFp === 4 ? "disabled" : ""}>Siguiente ›</button>
    </footer>`;
}

// ---------- Relación de Transformación / TTR (ST-CT-007) ----------

function campoTtr(etiqueta, clave, extra) {
  return `<label class="campo"><span>${esc(etiqueta)}</span>
    <input inputmode="decimal" data-datottr="${clave}" value="${esc(estado.datosTtr[clave])}" ${extra || ""}></label>`;
}

function opcionesTtr(clave, pares) {
  return `<div class="segmentos">${pares.map(([valor, texto]) => `
    <button data-datottr="${clave}" data-valor="${valor}"
      class="${estado.datosTtr[clave] === valor ? "activo" : ""}">${esc(texto)}</button>`).join("")}</div>`;
}

function pasoTtr1() {
  const d = estado.datosTtr;
  const mono = d.configuracion === "Monofásico";
  const opcionesConexion = opcionesConexionTtr(d.equipo, d.configuracion);
  if (opcionesConexion.length && !opcionesConexion.includes(d.conexion)) {
    d.conexion = opcionesConexion[0];
  }
  const terciario = llevaTerciarioTtr(d.equipo);
  const esReactor = d.equipo.includes("Reactores");

  let extra = "";
  if (!esReactor) {
    extra += `<div class="campo"><span>Configuración</span>${opcionesTtr("configuracion", [["Trifásico", "Trifásico"], ["Monofásico", "Monofásico"]])}</div>`;
    if (mono) {
      extra += `<div class="campo"><span>Fase</span>${opcionesTtr("fase", [["A", "A"], ["B", "B"], ["C", "C"]])}</div>`;
    }
    if (opcionesConexion.length) {
      extra += `<label class="campo"><span>Conexión</span>
        <select data-datottr="conexion">${opcionesConexion.map((c) =>
          `<option value="${esc(c)}" ${c === d.conexion ? "selected" : ""}>${esc(c)}</option>`).join("")}
        </select></label>`;
    }
    extra += `<div class="rejilla">
      ${campoTtr("kV primario (H)", "voltajeH")}
      ${campoTtr("kV secundario (X)", "voltajeX")}
      ${terciario ? campoTtr("kV terciario (Y)", "voltajeY") : ""}
    </div>`;
    extra += `<div class="campo"><span>¿Usar el estándar CFE de regulación por paso? (0.625 %)</span>
      ${opcionesTtr("regulacionCfe", [["Sí", "Sí"], ["No", "No"]])}</div>`;
    extra += `<div class="campo"><span>Tipo de cambiador</span>
      <div class="segmentos vertical">${CAMBIADORES_TTR.map(({ valor, nota }) => `
        <button data-datottr="tipoCambiador" data-valor="${esc(valor)}"
          class="${d.tipoCambiador === valor ? "activo" : ""}">${esc(valor)}${nota ? ` · ${esc(nota)}` : ""}</button>`).join("")}</div>
    </div>`;
    extra += `<div class="campo"><span>Medición a realizar</span>${opcionesTtr("medicionRealizar", [["Directa", "Directa"], ["Inversa", "Inversa"], ["Ambas", "Ambas"]])}</div>`;
    extra += `<div class="campo"><span>Polaridad del transformador</span>
      <div class="segmentos vertical">
        <button data-datottr="polaridad" data-valor="Sustractiva" class="${d.polaridad === "Sustractiva" ? "activo" : ""}">Sustractiva (H1 con X1 — distribución)</button>
        <button data-datottr="polaridad" data-valor="Aditiva" class="${d.polaridad === "Aditiva" ? "activo" : ""}">Aditiva (H1 con X2 — transmisión, usual 230/69 kV)</button>
      </div>
      <small>Nota: transmisión CFE → casi siempre "Aditiva".</small>
    </div>`;
  }
  return `
    <h2>01. Datos del equipo</h2>
    <p class="nota">Parámetros del equipo y condiciones ambientales. Procedimiento ST-CT-007.</p>
    <label class="campo"><span>Tipo de equipo</span>
      <select data-datottr="equipo">${EQUIPOS_TTR.map((e) =>
        `<option value="${esc(e)}" ${e === d.equipo ? "selected" : ""}>${esc(e)}</option>`).join("")}
      </select></label>
    ${esReactor ? `<p class="aviso">ST-CT-007 no publica conexiones TTR para reactores.</p>` : extra}
    <div class="rejilla">
      ${campoTtr("Temp. ambiente (°C)", "tempAmbiente")}
      ${campoTtr("Humedad relativa (%)", "humedad")}
      ${campoTtr("Temp. del devanado (°C)", "tempDevanado")}
    </div>`;
}

function chipTtr(rol, valor) {
  return (!valor || valor === "-----") ? "" : `<span class="chip ${rol}"><b>${esc(rol)}</b> ${esc(valor)}</span>`;
}

function pasoTtr2() {
  const d = estado.datosTtr;
  const [lista, nota] = filasTtr(d.equipo, d.configuracion, d.conexion);
  if (estado.pruebaTtr >= lista.length) estado.pruebaTtr = 0;
  if (!lista.length) {
    return `
      <h2>02. Selección de pruebas</h2>
      <p class="nota">${esc(d.equipo)}</p>
      <div class="aviso">${esc(nota)}</div>`;
  }
  const actual = lista[estado.pruebaTtr];
  return `
    <h2>02. Selección de pruebas</h2>
    <p class="nota">${esc(d.equipo)}${d.configuracion === "Monofásico" ? " · Monofásico" : ""}. ${esc(nota)}</p>
    <div class="tabla-pruebas"><table>
      <thead>
        <tr>
          <th></th><th>Prueba</th>
          <th class="th-cn" colspan="2">Terminales de excitación</th>
          <th class="th-gn" colspan="2">Terminales secundarias</th>
          <th class="th-mide">Mide</th>
        </tr>
        <tr>
          <th></th><th></th>
          <th class="th-cn">CN</th><th class="th-cr">CR</th>
          <th class="th-cn">GN</th><th class="th-cr">GR</th>
          <th></th>
        </tr>
      </thead>
      <tbody>${lista.map((pr, i) => `
        <tr class="${i === estado.pruebaTtr ? "activa" : ""}" data-pruebattr="${i}">
          <td class="led"><span class="punto ${i === estado.pruebaTtr ? "on" : ""}"></span></td>
          <td class="num">${esc(pr.prueba)}</td>
          ${celdaPildora(pr.cn, "cn")}
          ${celdaPildora(pr.cr, "cr")}
          ${celdaPildora(pr.gn, "cn")}
          ${celdaPildora(pr.gr, "cr")}
          ${celdaPildora(pr.mide, "mide")}
        </tr>`).join("")}</tbody>
    </table></div>
    <p class="nota">Prueba ${esc(actual.prueba)} · ${esc(actual.mide)}</p>`;
}

function pasoTtr3() {
  const d = estado.datosTtr;
  const [lista, nota] = filasTtr(d.equipo, d.configuracion, d.conexion);
  if (estado.pruebaTtr >= lista.length) estado.pruebaTtr = 0;
  const prueba = lista[estado.pruebaTtr];
  const clave = claveVectorTtr(d.equipo, d.configuracion, d.conexion);
  const ficha = clave ? VECTORES_TTR[clave] : null;
  if (!prueba || !ficha) {
    return `
      <h2>03. Diagrama vectorial</h2>
      <p class="nota">${esc(d.equipo)}</p>
      <div class="aviso">${esc(nota)}</div>`;
  }
  return `
    <h2>03. Diagrama vectorial</h2>
    <p class="nota">${esc(ficha[0])} · ${esc(ficha[1])} · Desplazamiento ${esc(ficha[2])} · Prueba ${esc(prueba.prueba)} (${esc(prueba.mide)})</p>
    <div class="diagrama">${svgVectorTtr(clave, prueba)}</div>
    <h3>Conexiones de esta prueba</h3>
    <ul class="leyenda">
      <li><span class="badge CN">CN</span>${esc(prueba.cn)}</li>
      <li><span class="badge CR">CR</span>${esc(prueba.cr)}</li>
      <li><span class="badge GN">GN</span>${esc(prueba.gn)}</li>
      <li><span class="badge GR">GR</span>${esc(prueba.gr)}</li>
    </ul>`;
}

function tarjetaDictamenTtr(res) {
  if (!res) return "";
  return `
    <section class="dictamen ${res.estado}">
      <header>DICTAMEN: ${res.estado}</header>
      <div class="indices">
        <div><small>Relación teórica</small><b>${res.rt.toFixed(4)}</b></div>
        <div><small>%DIF</small><b>${res.dif.toFixed(3)}</b></div>
      </div>
      <ul>
        <li>Relación medida: ${res.rm.toFixed(4)}.</li>
        <li>%DIF = 100 × (RT − RM) / RT.</li>
        <li>${esc(res.frase)}</li>
      </ul>
    </section>
    <div class="acciones">
      <button class="secundario" data-accionttr="guardar">Guardar en historial</button>
      ${navigator.share ? `<button class="secundario" data-accionttr="compartir">Compartir</button>` : ""}
    </div>`;
}

function calcularTtr() {
  const d = estado.datosTtr;
  const [lista] = filasTtr(d.equipo, d.configuracion, d.conexion);
  const prueba = lista[estado.pruebaTtr];
  if (!prueba) return { error: "Elija una prueba en el paso 02." };
  const { rt: nominal } = relacionNominalTtr(d, prueba);
  const { n, centro } = tapsTtr(d.tipoCambiador);
  const tap = estado.tapTtr || centro;
  const usarReg = d.regulacionCfe === "Sí";
  const l = estado.lecturasTtr;
  let rt;
  if (usarReg) {
    rt = relacionTeoricaTapTtr(nominal, tap, centro, true);
  } else {
    rt = numero(l.relacionTeoricaManual);
  }
  if (rt == null) {
    return { error: usarReg
      ? "Falta el kV de placa de ese devanado en el paso 01 para calcular la relación teórica."
      : "Escriba la relación teórica de este tap." };
  }
  const rm = numero(l.relacionMedida);
  if (rm == null) return { error: "Escriba la relación medida con el TTR." };
  const res = evaluarTtr(rt, rm);
  if (!res) return { error: "No se pudo calcular: revise los valores." };
  return res;
}

function pasoTtr4() {
  const d = estado.datosTtr;
  const [lista, nota] = filasTtr(d.equipo, d.configuracion, d.conexion);
  if (estado.pruebaTtr >= lista.length) estado.pruebaTtr = 0;
  const prueba = lista[estado.pruebaTtr];
  if (!prueba) {
    return `
      <h2>04. Captura de lecturas</h2>
      <p class="nota">${esc(d.equipo)}</p>
      <div class="aviso">${esc(nota)}</div>`;
  }
  const { n, centro } = tapsTtr(d.tipoCambiador);
  if (!estado.tapTtr) estado.tapTtr = centro;
  const { rt: nominal, par } = relacionNominalTtr(d, prueba);
  const usarReg = d.regulacionCfe === "Sí";
  const rtTap = usarReg ? relacionTeoricaTapTtr(nominal, estado.tapTtr, centro, true) : null;
  const l = estado.lecturasTtr;
  const taps = Array.from({ length: n }, (_, i) => i + 1);
  return `
    <h2>04. Captura de lecturas</h2>
    <p class="nota">Prueba ${esc(prueba.prueba)} · ${esc(prueba.mide)} · mide ${esc(par)}</p>
    <label class="campo"><span>Tap</span>
      <select data-datottr="__tap">${taps.map((t) =>
        `<option value="${t}" ${t === estado.tapTtr ? "selected" : ""}>${t}${t === centro ? " (central)" : ""}</option>`).join("")}
      </select></label>
    ${usarReg
      ? `<div class="kt">
          <div><small>Relación teórica nominal</small><b>${nominal == null ? "—" : nominal.toFixed(4)}</b></div>
          <div><small>Relación teórica en este tap (0.625 %/paso)</small><b>${rtTap == null ? "—" : rtTap.toFixed(4)}</b></div>
        </div>
        ${nominal == null ? `<div class="aviso">Falta el kV de placa de este devanado en el paso 01.</div>` : ""}`
      : `<label class="campo"><span>Relación teórica de este tap</span>
          <input inputmode="decimal" data-lecturattr="relacionTeoricaManual" value="${esc(l.relacionTeoricaManual)}"></label>`}
    <label class="campo"><span>Relación medida (TTR)</span>
      <input inputmode="decimal" data-lecturattr="relacionMedida" value="${esc(l.relacionMedida)}"></label>
    <p class="nota">%DIF = 100 × (RT − RM) / RT. ST-CT-007 acepta hasta 0.5 % en la primera medición.</p>
    <button class="primario" data-accionttr="calcular">Calcular dictamen</button>
    <div id="dictamenttr">${estado.resultadoTtr && estado.resultadoTtr.error
      ? `<div class="aviso">${esc(estado.resultadoTtr.error)}</div>`
      : tarjetaDictamenTtr(estado.resultadoTtr)}</div>`;
}

function pasoTtrProximamente(titulo) {
  return `
    <h2>${esc(titulo)}</h2>
    <p class="nota">Este paso de Relación de Transformación está en construcción. Por ahora, los pasos 01 y 02 ya están listos.</p>
    <div class="aviso">Próximamente en una actualización de la app.</div>`;
}

const PASOS_TTR = ["Datos del equipo", "Selección de pruebas", "Diagrama vectorial", "Captura de lecturas"];

function vistaTtr() {
  const pasos = { 1: pasoTtr1, 2: pasoTtr2, 3: pasoTtr3, 4: pasoTtr4 };
  const cuerpo = pasos[estado.pasoTtr]
    ? pasos[estado.pasoTtr]()
    : pasoTtrProximamente(`0${estado.pasoTtr}. ${PASOS_TTR[estado.pasoTtr - 1]}`);
  return `
    <header class="barra">
      <button class="atras" data-ir="inicio" aria-label="Volver al menú">‹</button>
      <div><b>Relación de Transformación (TTR)</b><small>ST-CT-007</small></div>
    </header>
    <ol class="pasos">${PASOS_TTR.map((nombre, i) => `
      <li><button data-pasottr="${i + 1}" class="${estado.pasoTtr === i + 1 ? "activo" : ""}" aria-label="${esc(nombre)}">
        <b>0${i + 1}</b></button></li>`).join("")}</ol>
    <main class="contenido">${cuerpo}</main>
    <footer class="pie-pasos">
      <button class="secundario" data-pasottr="${Math.max(1, estado.pasoTtr - 1)}" ${estado.pasoTtr === 1 ? "disabled" : ""}>‹ Anterior</button>
      <button class="primario" data-pasottr="${Math.min(4, estado.pasoTtr + 1)}" ${estado.pasoTtr === 4 ? "disabled" : ""}>Siguiente ›</button>
    </footer>`;
}

// ---------- Anexo A — Formatos de Prueba (captura en una sola pantalla) ----------
// Mismos campos que mostrar_anexo_a_formatos / mostrar_anexo_a_fp en SAPE2.py:
// identificación, condiciones, datos propios del equipo, orden de trabajo,
// equipo de medición y firmas — no solo las lecturas.

const CAMPOS_ANEXO_RA = {
  identificacion: [
    ["nomenclatura", "Nomenclatura"], ["subestacion", "Subestación (S.E.)"],
    ["marca", "Marca"], ["modelo", "Modelo"], ["serie", "No. de Serie"],
    ["mva", "MVA"], ["fabricacion", "Año de Fabricación"],
    ["nivel", "Nivel de Tensión (kV)"],
  ],
  condiciones: [
    ["voltajeCd", "Voltaje de prueba CD (kV)"],
    ["aceiteTemp", "Temp. Aceite (°C)"], ["clima", "Clima"],
  ],
  tc: [
    ["relacion", "Relación de transformación"],
    ["iPrimaria", "Corriente primaria (A)"],
    ["iSecundaria", "Corriente secundaria (A)"],
    ["exactitud", "Clase de exactitud"], ["burden", "Carga / Burden (VA)"],
    ["nbai", "NBAI (kV)"], ["frecuencia", "Frecuencia (Hz)"],
  ],
  tp: [
    ["relacion", "Relación de transformación"],
    ["vPrimaria", "Tensión primaria (kV)"],
    ["vSecundaria", "Tensión secundaria (V)"],
    ["exactitud", "Clase de exactitud"], ["burden", "Carga / Burden (VA)"],
    ["nbai", "NBAI (kV)"], ["frecuencia", "Frecuencia (Hz)"],
  ],
  rotativa: [
    ["vNominal", "Tensión nominal (kV)"], ["iNominal", "Corriente nominal (A)"],
    ["rpm", "Velocidad (RPM)"], ["fpNominal", "Factor de potencia"],
    ["frecuencia", "Frecuencia (Hz)"],
    ["claseAislamiento", "Clase de aislamiento"],
    ["tipoMaquina", "Tipo de máquina (Generador/Motor)"],
  ],
  reactor: [
    ["gerencia", "Gerencia Regional de Transmisión"], ["subarea", "SubÁrea"],
    ["mvar", "Potencia reactiva (MVAr)"],
    ["vNominal", "Tensión nominal (kV)"], ["iNominal", "Corriente nominal (A)"],
    ["reactancia", "Reactancia (%)"], ["claseEnf", "Clase de enfriamiento"],
  ],
  transformador: [
    ["gerencia", "Gerencia Regional de Transmisión"], ["subarea", "SubÁrea"],
    ["claseEnf", "Clase de enfriamiento"],
    ["anioServicio", "Año puesta en servicio"], ["taps", "# Taps ± %"],
    ["kvAt", "kV nom A.T."], ["kvBt", "kV nom B.T."],
    ["kvTerc", "kV nom Terciario"],
    ["z1", "%Z 1"], ["z1Mva", "a (MVA) 1"], ["z1Kv", "kV 1"],
    ["z2", "%Z 2"], ["z2Mva", "a (MVA) 2"], ["z2Kv", "kV 2"],
    ["z3", "%Z 3"], ["z3Mva", "a (MVA) 3"], ["z3Kv", "kV 3"],
  ],
  orden: [
    ["ot", "O.T."], ["fecha", "Fecha"], ["programado", "Programado"],
    ["ps", "P.S."], ["falla", "Falla"],
  ],
  medicion: [
    ["instModelo", "Modelo"], ["instMarca", "Marca"],
    ["instSerie", "No. Serie"], ["instCal", "Fecha Calibración"],
    ["instVenc", "Fecha Vencimiento"], ["instEimp", "No. Inv. EIMP"],
  ],
  cierre: [["ultimaMedicion", "Fecha de la última medición"]],
  firmas: [
    ["realizo", "Realizó — Nombre y firma"],
    ["reviso", "Revisó — Nombre y firma"],
    ["aprobo", "Aprobó — Nombre y firma"],
  ],
};

const CAMPOS_ANEXO_FP = {
  identificacion: [
    ["gerencia", "Gerencia Regional de Transmisión"], ["subarea", "SubÁrea"],
    ["subestacion", "Subestación"], ["nomenclatura", "Nomenclatura"],
    ["marca", "Marca"], ["modelo", "Modelo / Tipo"],
    ["serie", "No. de Serie"], ["fabricacion", "Año de Fabricación"],
    ["servicio", "Año Puesta en Servicio"],
  ],
  potencia: [
    ["mva", "MVA"], ["claseEnf", "Clase de enfriamiento"], ["taps", "# Taps"],
    ["kvAt", "kV nom. A.T."], ["kvBt", "kV nom. B.T."],
    ["kvTerc", "kV nom. Terciario"], ["z", "% Z"],
    ["conAt", "Tipo de conexión A.T. (Y/Δ)"],
    ["conBt", "Tipo de conexión B.T. (Y/Δ)"],
    ["conTe", "Tipo de conexión Terciario (Y/Δ)"],
  ],
  apartarrayos: [
    ["nivel", "Tensión nominal (kV)"], ["mcov", "MCOV (kV)"],
    ["secciones", "Número de secciones"],
  ],
  cables: [
    ["nivel", "Clase (kV)"], ["calibre", "Calibre"], ["longitud", "Longitud (m)"],
  ],
  instrumento: [
    ["nivel", "Tensión nominal (kV)"], ["relacion", "Relación"],
    ["exactitud", "Clase de exactitud"],
    ["capPlaca", "Capacitancia de placa (pF) — solo TPCs"],
  ],
  condiciones: [
    ["tempDevanado", "Temp. Devanado (°C)"], ["clima", "Clima"],
    ["motivo", "Motivo de la prueba"], ["ot", "Orden de Trabajo (O.T.)"],
    ["fecha", "Fecha"],
  ],
  medicion: [
    ["instMarca", "Marca"], ["instModelo", "Modelo"],
    ["instSerie", "Núm. Serie"], ["instEimp", "No. Inv. EIMP"],
    ["instCal", "Fecha de Calibración"], ["instVenc", "Fecha Vencimiento"],
    ["ultimaPrueba", "Fecha última prueba"],
  ],
  firmas: [
    ["observaciones", "Observaciones"],
    ["realizo", "Realizó — Nombre y firma"],
    ["reviso", "Revisó — Nombre y firma"],
    ["aprobo", "Aprobó — Nombre y firma"],
  ],
};

function badgeEstadoAnexo(res) {
  if (!res || res.error) return `<span class="badge-anexo">—</span>`;
  return `<span class="badge-anexo ${res.estado}">${esc(res.estado)}</span>`;
}

function campoAnexo(clave, etiqueta, valores) {
  return `<label class="campo"><span>${esc(etiqueta)}</span>
    <input data-anexodato="${clave}" value="${esc(valores[clave] || "")}"></label>`;
}

function seccionAnexo(titulo, lista, valores) {
  if (!lista || !lista.length) return "";
  return `<h3>${esc(titulo)}</h3>
    <div class="rejilla">${lista.map(([clave, etiqueta]) => campoAnexo(clave, etiqueta, valores)).join("")}</div>`;
}

function bloqueIdentificacionRa(familia) {
  if (familia === "tc") return CAMPOS_ANEXO_RA.tc;
  if (familia === "tp") return CAMPOS_ANEXO_RA.tp;
  if (familia === "rotativa") return CAMPOS_ANEXO_RA.rotativa;
  return null;
}

function vistaAnexoA() {
  const d = estado.datos;
  const eq = equipoDe(d.equipo);
  const lista = pruebasDe(d);
  const lec = estado.lecturasAnexoRa;
  const v = estado.datosAnexoRa;
  const filas = lista.map((pr, i) => {
    const l = lec[i] || (lec[i] = { r30: "", r1: "", r10: "" });
    const res = dictamen(d, pr, l);
    return `
      <tr>
        <td>${esc(pr.prueba)}<br><small>${esc(pr.medicion)}</small></td>
        <td>${pr.minutos === 10
          ? `<input inputmode="decimal" data-anexora="${i}:r30" value="${esc(l.r30)}">`
          : "—"}</td>
        <td><input inputmode="decimal" data-anexora="${i}:r1" value="${esc(l.r1)}"></td>
        <td>${pr.minutos === 10
          ? `<input inputmode="decimal" data-anexora="${i}:r10" value="${esc(l.r10)}">`
          : "—"}</td>
        <td>${badgeEstadoAnexo(res)}</td>
      </tr>`;
  }).join("");
  const esReactor = d.equipo === "reactor";
  const datosEquipo = esReactor
    ? CAMPOS_ANEXO_RA.reactor
    : (eq.familia === "potencia" ? CAMPOS_ANEXO_RA.transformador : bloqueIdentificacionRa(eq.familia));
  return `
    <header class="barra">
      <button class="atras" data-ir="ra" aria-label="Volver">‹</button>
      <div><b>Anexo A · Formatos de Prueba</b><small>${esc(eq.nombre)}</small></div>
    </header>
    <main class="contenido anexo-a">
      ${seccionAnexo("Datos de identificación", CAMPOS_ANEXO_RA.identificacion, v)}
      <h3>Condiciones de la prueba</h3>
      <div class="rejilla">
        <div class="dato"><small>Temp. ambiente</small><b>${esc(d.tempAmbiente) || "—"} °C</b></div>
        <div class="dato"><small>Humedad relativa</small><b>${esc(d.humedad) || "—"} %</b></div>
        <div class="dato"><small>Temp. del devanado</small><b>${esc(d.tempDevanado) || "—"} °C</b></div>
        ${CAMPOS_ANEXO_RA.condiciones.map(([clave, etiqueta]) => campoAnexo(clave, etiqueta, v)).join("")}
      </div>
      ${seccionAnexo(
        eq.familia === "rotativa" ? "Datos de la máquina rotatoria"
          : esReactor ? "Datos del reactor"
          : eq.familia === "potencia" ? "Datos del transformador"
          : eq.familia === "tc" ? "Datos del TC" : "Datos del TP / TPC",
        datosEquipo, v,
      )}
      ${seccionAnexo("Orden de trabajo", CAMPOS_ANEXO_RA.orden, v)}
      ${seccionAnexo("Equipo de medición utilizado", CAMPOS_ANEXO_RA.medicion, v)}
      ${diagramaAnexoRa(d.equipo, d) ? `<h3>Diagrama del equipo</h3><div class="diagrama">${diagramaAnexoRa(d.equipo, d)}</div>` : ""}
      <h3>Lecturas (MΩ) — todas las pruebas de este equipo</h3>
      <p class="nota">Sin letra son MΩ. Agregue G para gigaohms o T para teraohms.</p>
      <div class="tabla-anexo"><table>
        <thead><tr><th>Prueba</th><th>30 s</th><th>1 min</th><th>10 min</th><th>Dictamen</th></tr></thead>
        <tbody>${filas}</tbody>
      </table></div>
      ${seccionAnexo("Cierre", CAMPOS_ANEXO_RA.cierre, v)}
      ${seccionAnexo("Firmas", CAMPOS_ANEXO_RA.firmas, v)}
      <button class="primario" data-accion="guardar-anexo-a">Guardar Anexo A</button>
      <p class="nota">${esc(estado.anexoEstado)}</p>
    </main>`;
}

function bloqueIdentificacionFp(equipo) {
  if (esPotenciaFp(equipo)) return CAMPOS_ANEXO_FP.potencia;
  if (equipo.includes("Apartarrayos")) return CAMPOS_ANEXO_FP.apartarrayos;
  if (equipo.includes("Cables")) return CAMPOS_ANEXO_FP.cables;
  if (!equipo.includes("Aceite")) return CAMPOS_ANEXO_FP.instrumento;
  return null;
}

function vistaAnexoAFp() {
  const d = estado.datosFp;
  const lista = filasFp(d.equipo, d.arreglo);
  const lec = estado.lecturasAnexoFp;
  const v = estado.datosAnexoFp;
  const filas = lista.map((pr, i) => {
    const l = lec[i] || (lec[i] = { kv: "10", ma: "", watts: "" });
    const res = numero(l.kv) && numero(l.ma) != null && numero(l.watts) != null
      ? evaluarFp(d, numero(l.kv), numero(l.ma), numero(l.watts))
      : null;
    return `
      <tr>
        <td>${esc(pr.prueba)}<br><small>${esc(pr.medicion || pr.modo)}</small></td>
        <td><input inputmode="decimal" data-anexofp="${i}:kv" value="${esc(l.kv)}"></td>
        <td><input inputmode="decimal" data-anexofp="${i}:ma" value="${esc(l.ma)}"></td>
        <td><input inputmode="decimal" data-anexofp="${i}:watts" value="${esc(l.watts)}"></td>
        <td>${badgeEstadoAnexo(res)}</td>
      </tr>`;
  }).join("");
  return `
    <header class="barra">
      <button class="atras" data-ir="fp" aria-label="Volver">‹</button>
      <div><b>Anexo A · Formatos de Prueba</b><small>${esc(d.equipo)}</small></div>
    </header>
    <main class="contenido anexo-a">
      ${seccionAnexo("Datos de identificación", CAMPOS_ANEXO_FP.identificacion, v)}
      ${seccionAnexo("Datos propios del equipo", bloqueIdentificacionFp(d.equipo), v)}
      <h3>Condiciones: prueba &amp; climatológica</h3>
      <div class="rejilla">
        <div class="dato"><small>Temp. ambiente</small><b>${esc(d.tempAmbiente) || "—"} °C</b></div>
        <div class="dato"><small>Humedad relativa</small><b>${esc(d.humedad) || "—"} %</b></div>
        <div class="dato"><small>Temp. del aceite</small><b>${esc(d.tempAceite) || "—"} °C</b></div>
        ${CAMPOS_ANEXO_FP.condiciones.map(([clave, etiqueta]) => campoAnexo(clave, etiqueta, v)).join("")}
      </div>
      ${seccionAnexo("Equipo de medición utilizado", CAMPOS_ANEXO_FP.medicion, v)}
      ${diagramaAnexoFp(d.equipo, d) ? `<h3>Diagrama del equipo</h3><div class="diagrama">${diagramaAnexoFp(d.equipo, d)}</div>` : ""}
      <h3>Lecturas — todas las pruebas de este equipo</h3>
      <div class="tabla-anexo"><table>
        <thead><tr><th>Prueba</th><th>kV</th><th>mA</th><th>W</th><th>Dictamen</th></tr></thead>
        <tbody>${filas}</tbody>
      </table></div>
      ${seccionAnexo("Observaciones y firmas", CAMPOS_ANEXO_FP.firmas, v)}
      <button class="primario" data-accion="guardar-anexo-a-fp">Guardar Anexo A</button>
      <p class="nota">${esc(estado.anexoEstado)}</p>
    </main>`;
}

function vistaHistorial() {
  const lista = leer(CLAVE_HISTORIAL, []);
  const filas = lista.length
    ? lista.map((reg) => `
      <li class="registro ${reg.estado}">
        <div><b>${esc(reg.equipo)}</b><span class="badge-estado">${reg.estado}</span></div>
        <small>${esc(reg.fecha)} · Prueba ${esc(reg.prueba)} · ${esc(reg.medicion)}</small>
        <small>${esc(reg.resumen)}</small>
      </li>`).join("")
    : `<li class="vacio">Aún no hay análisis guardados.</li>`;
  return `
    <header class="barra">
      <button class="atras" data-ir="inicio" aria-label="Volver al menú">‹</button>
      <div><b>Historial de Análisis</b><small>${lista.length} registro(s) en este celular</small></div>
    </header>
    <main class="contenido"><ul class="historial">${filas}</ul>
      ${lista.length ? `<button class="secundario" data-accion="borrar-historial">Borrar historial</button>` : ""}
    </main>`;
}

const raiz = document.getElementById("app");

function pintar() {
  raiz.innerHTML = {
    inicio: vistaInicio, ra: vistaRa, fp: vistaFp, ttr: vistaTtr,
    anexoA: vistaAnexoA, anexoAFp: vistaAnexoAFp, historial: vistaHistorial,
  }[estado.vista]();
  raiz.className = { anexoA: "ra", anexoAFp: "fp" }[estado.vista] || estado.vista;
  if (estado.vista === "inicio" && typeof iniciarCfe3D === "function") {
    iniciarCfe3D(document.getElementById("logo-cfe-3d"));
  } else if (typeof detenerCfe3D === "function") {
    detenerCfe3D();
  }
}

function resumenResultado(res) {
  const partes = [];
  if (res.ip != null) partes.push(`ip ${res.ip.toFixed(2)}`);
  if (res.ia != null) partes.push(`ia ${res.ia.toFixed(2)}`);
  partes.push(`Kt ${res.kt.toFixed(3)} a ${res.base} °C`);
  return partes.join(" · ");
}

function avisar(texto) {
  const aviso = document.createElement("div");
  aviso.className = "toast";
  aviso.textContent = texto;
  document.body.appendChild(aviso);
  setTimeout(() => aviso.remove(), 2200);
}

// Guarda el Anexo A en este celular y lo manda al servidor de la PC (si hay
// conexión), para que SAPE2.py lo pueda importar desde "Anexo A → Importar
// del celular". Un registro por módulo+equipo (el último capturado manda).
function guardarAnexoA(modulo, equipo, cuerpo) {
  const registro = {
    modulo, equipo, ...cuerpo,
    fecha: new Date().toISOString(),
    fechaTexto: new Date().toLocaleString("es-MX", { dateStyle: "short", timeStyle: "short" }),
  };
  const lista = leer(CLAVE_ANEXO_A, []).filter(
    (r) => !(r.modulo === modulo && r.equipo === equipo),
  );
  lista.unshift(registro);
  guardar(CLAVE_ANEXO_A, lista.slice(0, 50));
  estado.anexoEstado = "Guardado en este celular…";
  fetch("/api/anexo-a", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(registro),
  }).then((r) => {
    estado.anexoEstado = r.ok
      ? "Guardado en el celular y enviado a la PC."
      : "Guardado en el celular. La PC no pudo recibirlo (reintente).";
    pintarEstadoAnexo();
  }).catch(() => {
    estado.anexoEstado = "Guardado en el celular. Sin conexión con la PC — ábralo en el mismo WiFi que la PC para sincronizar.";
    pintarEstadoAnexo();
  });
  avisar("Guardando Anexo A…");
}

function pintarEstadoAnexo() {
  if (estado.vista !== "anexoA" && estado.vista !== "anexoAFp") return;
  const p = raiz.querySelector(".anexo-a .nota:last-of-type");
  if (p) p.textContent = estado.anexoEstado;
}

raiz.addEventListener("click", (evento) => {
  const boton = evento.target.closest(
    "button, tr[data-prueba], tr[data-pruebafp], tr[data-pruebattr]",
  );
  if (!boton || boton.disabled) return;
  const d = boton.dataset;
  if (d.ir) {
    estado.vista = d.ir;
    if (d.ir === "ra") estado.paso = 1;
    if (d.ir === "fp") estado.pasoFp = 1;
    if (d.ir === "ttr") estado.pasoTtr = 1;
  } else if (d.paso) {
    estado.paso = Number(d.paso);
    window.scrollTo(0, 0);
  } else if (d.pasofp) {
    estado.pasoFp = Number(d.pasofp);
    window.scrollTo(0, 0);
  } else if (d.pasottr) {
    estado.pasoTtr = Number(d.pasottr);
    window.scrollTo(0, 0);
  } else if (d.dato) {
    estado.datos[d.dato] = d.valor;
    estado.resultado = null;
    if (["secciones", "terciario"].includes(d.dato)) estado.prueba = 0;
  } else if (d.datofp) {
    estado.datosFp[d.datofp] = d.valor;
    estado.resultadoFp = null;
    if (["configuracion", "estado"].includes(d.datofp)) estado.pruebaFp = 0;
  } else if (d.datottr) {
    estado.datosTtr[d.datottr] = d.valor;
    estado.resultadoTtr = null;
  } else if (d.pruebattr) {
    estado.pruebaTtr = Number(d.pruebattr);
    estado.resultadoTtr = null;
  } else if (d.prueba) {
    estado.prueba = Number(d.prueba);
    estado.resultado = null;
  } else if (d.pruebafp) {
    estado.pruebaFp = Number(d.pruebafp);
    estado.resultadoFp = null;
  } else if (d.modofp) {
    estado.modoFp = d.modofp;
  } else if (d.modo) {
    estado.modo = d.modo;
  } else if (d.accion === "calcular") {
    estado.resultado = dictamen(estado.datos, pruebaActual(), estado.lecturas);
  } else if (d.accionfp === "calcular") {
    estado.resultadoFp = calcularFp();
  } else if (d.accionttr === "calcular") {
    estado.resultadoTtr = calcularTtr();
  } else if (d.accion === "guardar" && estado.resultado && !estado.resultado.error) {
    const prueba = pruebaActual();
    const lista = leer(CLAVE_HISTORIAL, []);
    lista.unshift({
      fecha: new Date().toLocaleString("es-MX", { dateStyle: "short", timeStyle: "short" }),
      equipo: equipoDe(estado.datos.equipo).nombre,
      prueba: prueba.prueba, medicion: prueba.medicion,
      estado: estado.resultado.estado, resumen: resumenResultado(estado.resultado),
    });
    guardar(CLAVE_HISTORIAL, lista.slice(0, 200));
    avisar("Guardado en el historial");
    return;
  } else if (d.accionfp === "guardar" && estado.resultadoFp && !estado.resultadoFp.error) {
    const dd = estado.datosFp;
    const pr = filasFp(dd.equipo, dd.arreglo)[estado.pruebaFp] || {};
    const lista = leer(CLAVE_HISTORIAL, []);
    lista.unshift({
      fecha: new Date().toLocaleString("es-MX", { dateStyle: "short", timeStyle: "short" }),
      equipo: `F.P. · ${dd.equipo}`,
      prueba: pr.prueba || "—", medicion: pr.medicion || "—",
      estado: estado.resultadoFp.estado,
      resumen: `%FP20 ${estado.resultadoFp.fp20.toFixed(3)} % · Kt ${estado.resultadoFp.kt.toFixed(3)}`,
    });
    guardar(CLAVE_HISTORIAL, lista.slice(0, 200));
    avisar("Guardado en el historial");
    return;
  } else if (d.accion === "compartir" && estado.resultado) {
    const prueba = pruebaActual();
    navigator.share({
      title: "SAPE — Resistencia de Aislamiento",
      text: [
        `${equipoDe(estado.datos.equipo).nombre} · Prueba ${prueba.prueba} (${prueba.medicion})`,
        `DICTAMEN: ${estado.resultado.estado}`,
        ...estado.resultado.lineas,
      ].join("\n"),
    }).catch(() => {});
    return;
  } else if (d.accionttr === "guardar" && estado.resultadoTtr && !estado.resultadoTtr.error) {
    const dd = estado.datosTtr;
    const [lista] = filasTtr(dd.equipo, dd.configuracion, dd.conexion);
    const pr = lista[estado.pruebaTtr] || {};
    const lista2 = leer(CLAVE_HISTORIAL, []);
    lista2.unshift({
      fecha: new Date().toLocaleString("es-MX", { dateStyle: "short", timeStyle: "short" }),
      equipo: `T.T.R. · ${dd.equipo}`,
      prueba: pr.prueba || "—", medicion: pr.mide || "—",
      estado: estado.resultadoTtr.estado,
      resumen: `%DIF ${estado.resultadoTtr.dif.toFixed(3)} % · Tap ${estado.tapTtr}`,
    });
    guardar(CLAVE_HISTORIAL, lista2.slice(0, 200));
    avisar("Guardado en el historial");
    return;
  } else if (d.accionttr === "compartir" && estado.resultadoTtr && !estado.resultadoTtr.error) {
    const dd = estado.datosTtr;
    const [lista] = filasTtr(dd.equipo, dd.configuracion, dd.conexion);
    const pr = lista[estado.pruebaTtr] || {};
    navigator.share({
      title: "SAPE — Relación de Transformación (TTR)",
      text: [
        `${dd.equipo} · Prueba ${pr.prueba || "—"} (${pr.mide || "—"}) · Tap ${estado.tapTtr}`,
        `DICTAMEN: ${estado.resultadoTtr.estado}`,
        `Relación teórica: ${estado.resultadoTtr.rt.toFixed(4)}`,
        `Relación medida: ${estado.resultadoTtr.rm.toFixed(4)}`,
        `%DIF: ${estado.resultadoTtr.dif.toFixed(3)} %`,
        estado.resultadoTtr.frase,
      ].join("\n"),
    }).catch(() => {});
    return;
  } else if (d.accionfp === "compartir" && estado.resultadoFp) {
    const dd = estado.datosFp;
    const pr = filasFp(dd.equipo, dd.arreglo)[estado.pruebaFp] || {};
    navigator.share({
      title: "SAPE — Factor de Potencia al Aislamiento",
      text: [
        `${dd.equipo} · Prueba ${pr.prueba || "—"} (${pr.medicion || "—"})`,
        `DICTAMEN: ${estado.resultadoFp.estado}`,
        `%FP medido: ${estado.resultadoFp.fp.toFixed(3)} %`,
        `%FP a 20 °C: ${estado.resultadoFp.fp20.toFixed(3)} %`,
        estado.resultadoFp.criterio, estado.resultadoFp.frase,
      ].join("\n"),
    }).catch(() => {});
    return;
  } else if (d.accion === "borrar-historial") {
    if (!confirm("¿Borrar todo el historial de este celular?")) return;
    guardar(CLAVE_HISTORIAL, []);
  } else if (d.accion === "guardar-anexo-a") {
    guardarAnexoA("RA", equipoDe(estado.datos.equipo).nombre, {
      datos: estado.datos, lecturas: estado.lecturasAnexoRa,
      datosAnexo: estado.datosAnexoRa,
    });
  } else if (d.accion === "guardar-anexo-a-fp") {
    guardarAnexoA("FP", estado.datosFp.equipo, {
      datos: estado.datosFp, lecturas: estado.lecturasAnexoFp,
      datosAnexo: estado.datosAnexoFp,
    });
  } else {
    return;
  }
  recordar();
  pintar();
});

// Los campos de texto se guardan al escribir, sin repintar (no se pierde el foco).
raiz.addEventListener("input", (evento) => {
  const el = evento.target;
  if (el.dataset.lectura) {
    estado.lecturas[el.dataset.lectura] = el.value;
    estado.resultado = null;
  } else if (el.dataset.lecturafp) {
    estado.lecturasFp[el.dataset.lecturafp] = el.value;
    estado.resultadoFp = null;
  } else if (el.dataset.dato && el.tagName === "INPUT") {
    estado.datos[el.dataset.dato] = el.value;
    estado.resultado = null;
  } else if (el.dataset.datofp && el.tagName === "INPUT") {
    estado.datosFp[el.dataset.datofp] = el.value;
    estado.resultadoFp = null;
  } else if (el.dataset.datottr && el.tagName === "INPUT") {
    estado.datosTtr[el.dataset.datottr] = el.value;
  } else if (el.dataset.lecturattr) {
    estado.lecturasTtr[el.dataset.lecturattr] = el.value;
    estado.resultadoTtr = null;
  } else if (el.dataset.anexora) {
    const [indice, campo] = el.dataset.anexora.split(":");
    (estado.lecturasAnexoRa[indice] ||= { r30: "", r1: "", r10: "" })[campo] = el.value;
  } else if (el.dataset.anexofp) {
    const [indice, campo] = el.dataset.anexofp.split(":");
    (estado.lecturasAnexoFp[indice] ||= { kv: "10", ma: "", watts: "" })[campo] = el.value;
  } else if (el.dataset.anexodato) {
    const destino = estado.vista === "anexoAFp" ? estado.datosAnexoFp : estado.datosAnexoRa;
    destino[el.dataset.anexodato] = el.value;
  } else {
    return;
  }
  recordar();
});

raiz.addEventListener("change", (evento) => {
  const el = evento.target;
  if (el.tagName !== "SELECT") return;
  if (el.dataset.dato) {
    estado.datos[el.dataset.dato] = el.value;
    estado.prueba = 0;
    estado.resultado = null;
  } else if (el.dataset.datofp) {
    estado.datosFp[el.dataset.datofp] = el.value;
    estado.pruebaFp = 0;
    estado.resultadoFp = null;
    if (el.dataset.datofp === "equipo") estado.datosFp.arreglo = "";
  } else if (el.dataset.datottr === "__tap") {
    estado.tapTtr = Number(el.value);
    estado.resultadoTtr = null;
  } else if (el.dataset.datottr) {
    estado.datosTtr[el.dataset.datottr] = el.value;
    estado.resultadoTtr = null;
  } else {
    return;
  }
  recordar();
  pintar();
});

pintar();

if ("serviceWorker" in navigator) {
  window.addEventListener("load", () => {
    navigator.serviceWorker.register("sw.js").catch(() => {});
  });
}
