// SAPE móvil: Resistencia de Aislamiento en cuatro pasos.
"use strict";

const CLAVE_ESTADO = "sape-movil-estado";
const CLAVE_HISTORIAL = "sape-movil-historial";

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
    <button class="menu-item ${destino === "fp" ? "menu-item-fp" : ""} ${destino === "ttr" ? "menu-item-ttr" : ""}" ${destino ? `data-ir="${destino}"` : "disabled"}>
      <span>${num}. ${esc(nombre)}</span>
      <span class="marca">${destino ? (marca ? `[ ${esc(marca)} ]` : "›") : "Próximamente"}</span>
    </button>`).join("");
  return `
    <main class="inicio">
      <div class="logo-cfe">CFE</div>
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

function paso2() {
  const lista = pruebasDe(estado.datos);
  pruebaActual();
  return `
    <h2>02. Selección de pruebas</h2>
    <p class="nota">${esc(equipoDe(estado.datos.equipo).nombre)}. Elija la prueba a realizar.</p>
    <div class="pruebas">${lista.map((prueba, i) => `
      <button class="prueba ${i === estado.prueba ? "activo" : ""}" data-prueba="${i}">
        <span class="num">${esc(prueba.prueba)}</span>
        <span class="cuerpo">
          <b>${esc(prueba.medicion)}</b>
          <span class="chips">${chips(prueba)}</span>
          <small>${esc(formatoKv(prueba.kv))} · ${prueba.minutos} min</small>
        </span>
      </button>`).join("")}</div>`;
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
  return `
    <h2>02. Selección de prueba</h2>
    <p class="nota">${esc(d.equipo)}${d.arreglo ? " · " + esc(d.arreglo) : ""}. Elija la prueba a realizar.</p>
    <div class="pruebas">${lista.map((pr, i) => `
      <button class="prueba ${i === estado.pruebaFp ? "activo" : ""}" data-pruebafp="${i}">
        <span class="num">${esc(pr.prueba)}</span>
        <span class="cuerpo">
          <b>${esc(pr.medicion || pr.modo)}</b>
          <small>${esc(pr.kv)} kV · ${esc(pr.modo)}</small>
        </span>
      </button>`).join("")}
      ${!lista.length ? `<p class="aviso">No hay pruebas definidas para este equipo.</p>` : ""}
    </div>`;
}

function chipFp(rol, clase, valor) {
  return (!valor || valor === "-----") ? "" : `<span class="chip ${clase}"><b>${esc(rol)}</b> ${esc(valor)}</span>`;
}

function pasoFp3() {
  const d = estado.datosFp;
  const lista = filasFp(d.equipo, d.arreglo);
  const pr = lista[estado.pruebaFp] || lista[0] || {};
  return `
    <h2>03. Conexión de prueba</h2>
    <p class="nota">Prueba ${esc(pr.prueba || "—")} · ${esc(pr.medicion || "—")} · ${esc(pr.kv || "—")} kV · ${esc(pr.modo || "—")}</p>
    <div class="diagrama">
      <div class="chips" style="justify-content:center;margin-bottom:10px;">
        ${chipFp("HV", "LINEA", pr.hv)}
        ${chipFp("TIERRA", "TIERRA", pr.ground)}
        ${chipFp("GUARDA", "GUARDA", pr.guard)}
        ${chipFp("UST", "UST", pr.ust)}
        ${pr.flotando ? `<span class="chip UST"><b>FLOTA</b> ${esc(pr.flotando)}</span>` : ""}
      </div>
      <p class="nota" style="margin:0;">Modo del equipo de prueba: <b>${esc(pr.modo || "—")}</b>. Se energiza ${esc(pr.hv || "—")}; TIERRA se conecta al retorno del instrumento; GUARDA excluye esa parte de la medición; UST la deja flotando y fuera del cálculo.</p>
    </div>
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

const PASOS_FP = ["Datos del equipo", "Selección de prueba", "Conexión de prueba", "Captura de lecturas"];

function vistaFp() {
  const cuerpo = [pasoFp1, pasoFp2, pasoFp3, pasoFp4][estado.pasoFp - 1]();
  return `
    <header class="barra">
      <button class="atras" data-ir="inicio" aria-label="Volver al menú">‹</button>
      <div><b>Factor de Potencia al Aislamiento</b><small>ST-CT-002</small></div>
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
  return `
    <h2>02. Selección de pruebas</h2>
    <p class="nota">${esc(d.equipo)}${d.configuracion === "Monofásico" ? " · Monofásico" : ""}. ${esc(nota)}</p>
    <div class="pruebas">${lista.map((pr, i) => `
      <button class="prueba ${i === estado.pruebaTtr ? "activo" : ""}" data-pruebattr="${i}">
        <span class="num">${esc(pr.prueba)}</span>
        <span class="cuerpo">
          <b>${esc(pr.mide)}</b>
          <span class="chips">${chipTtr("CN", pr.cn)}${chipTtr("CR", pr.cr)}${chipTtr("GN", pr.gn)}${chipTtr("GR", pr.gr)}</span>
        </span>
      </button>`).join("")}</div>`;
}

function pasoTtrProximamente(titulo) {
  return `
    <h2>${esc(titulo)}</h2>
    <p class="nota">Este paso de Relación de Transformación está en construcción. Por ahora, los pasos 01 y 02 ya están listos.</p>
    <div class="aviso">Próximamente en una actualización de la app.</div>`;
}

const PASOS_TTR = ["Datos del equipo", "Selección de pruebas", "Diagrama vectorial", "Captura de lecturas"];

function vistaTtr() {
  const cuerpo = { 1: pasoTtr1, 2: pasoTtr2 }[estado.pasoTtr]
    ? { 1: pasoTtr1, 2: pasoTtr2 }[estado.pasoTtr]()
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
  raiz.innerHTML = { inicio: vistaInicio, ra: vistaRa, fp: vistaFp, ttr: vistaTtr, historial: vistaHistorial }[estado.vista]();
  raiz.className = estado.vista;
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

raiz.addEventListener("click", (evento) => {
  const boton = evento.target.closest("button");
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
  } else if (d.pruebattr) {
    estado.pruebaTtr = Number(d.pruebattr);
  } else if (d.prueba) {
    estado.prueba = Number(d.prueba);
    estado.resultado = null;
  } else if (d.pruebafp) {
    estado.pruebaFp = Number(d.pruebafp);
    estado.resultadoFp = null;
  } else if (d.modo) {
    estado.modo = d.modo;
  } else if (d.accion === "calcular") {
    estado.resultado = dictamen(estado.datos, pruebaActual(), estado.lecturas);
  } else if (d.accionfp === "calcular") {
    estado.resultadoFp = calcularFp();
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
  } else if (el.dataset.datottr) {
    estado.datosTtr[el.dataset.datottr] = el.value;
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
