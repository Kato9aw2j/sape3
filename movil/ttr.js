// Datos de Relación de Transformación / TTR (ST-CT-007).
// Debe coincidir con SAPE2.py (datos_ttr, _opciones_conexion_ttr): si cambia
// algo allá, cambia aquí también. Por ahora cubre el paso 01 (Datos del
// equipo); los pasos 02-04 se agregan en una siguiente actualización.
"use strict";

const EQUIPOS_TTR = [
  "Transformadores de 2 Devanados",
  "Transformadores de 3 Devanados",
  "Autotransformadores",
  "Reactores",
];

const CONEXIONES_TTR_2D = [
  "Delta - Estrella",
  "Estrella - Delta",
  "Delta - Delta",
  "Estrella - Estrella",
];

const CONEXIONES_TTR_AUTO = [
  "Estrella - Estrella",
  "Estrella - Estrella - Delta",
];

const CAMBIADORES_TTR = [
  { valor: "Sin carga [ 5 TAPs ]", nota: "" },
  { valor: "Bajo carga [ 21 TAPs ]", nota: "Nominal Simple" },
  { valor: "Bajo carga [ 23 TAPs ]", nota: "Nominal Triple" },
];

// Conexiones que se preguntan según el tipo de equipo (igual que
// _opciones_conexion_ttr en SAPE2.py).
function opcionesConexionTtr(equipo, configuracion) {
  if (equipo.includes("2 Devanados")) return CONEXIONES_TTR_2D;
  if (equipo.includes("Autotransformadores") && configuracion !== "Monofásico") return CONEXIONES_TTR_AUTO;
  return [];
}

// Tablas de pruebas (ST-CT-007, figuras 5 a 9). Cada fila: número, CN, CR,
// GN, GR, qué mide. Mismos datos que PRUEBAS_TTR_* en SAPE2.py.
function filaTtr(n, cn, cr, gn, gr, mide) {
  return { prueba: String(n), cn, cr, gn, gr, mide };
}

const PRUEBAS_TTR_YD = [
  filaTtr(1, "H1", "H0", "X1", "X2", "H – X φ1"),
  filaTtr(2, "H2", "H0", "X2", "X3", "H – X φ2"),
  filaTtr(3, "H3", "H0", "X3", "X1", "H – X φ3"),
];
const PRUEBAS_TTR_DY = [
  filaTtr(1, "H1", "H2", "X0", "X2", "H – X φ1"),
  filaTtr(2, "H2", "H3", "X0", "X3", "H – X φ2"),
  filaTtr(3, "H3", "H1", "X0", "X1", "H – X φ3"),
];
const PRUEBAS_TTR_YY = [
  filaTtr(1, "H1", "H0", "X1", "X0", "H – X φ1"),
  filaTtr(2, "H2", "H0", "X2", "X0", "H – X φ2"),
  filaTtr(3, "H3", "H0", "X3", "X0", "H – X φ3"),
];
const PRUEBAS_TTR_DD = [
  filaTtr(1, "H1", "H2", "X1", "X2", "H – X φ1"),
  filaTtr(2, "H2", "H3", "X2", "X3", "H – X φ2"),
  filaTtr(3, "H3", "H1", "X3", "X1", "H – X φ3"),
];
const PRUEBAS_TTR_YYD = [
  filaTtr(1, "H1", "H0", "X1", "X0", "H – X φ1"),
  filaTtr(2, "H2", "H0", "X2", "X0", "H – X φ2"),
  filaTtr(3, "H3", "H0", "X3", "X0", "H – X φ3"),
  filaTtr(4, "H1", "H0", "Y1", "Y2", "H – Y φ1"),
  filaTtr(5, "H2", "H0", "Y2", "Y3", "H – Y φ2"),
  filaTtr(6, "H3", "H0", "Y3", "Y1", "H – Y φ3"),
  filaTtr(7, "X1", "X0", "Y1", "Y2", "X – Y φ1"),
  filaTtr(8, "X2", "X0", "Y2", "Y3", "X – Y φ2"),
  filaTtr(9, "X3", "X0", "Y3", "Y1", "X – Y φ3"),
];
const PRUEBAS_TTR_YYD_MONO = [
  filaTtr(1, "H1", "H0", "X1", "X0", "H – X"),
  filaTtr(2, "H1", "H0", "Y1", "Y2", "H – Y"),
  filaTtr(3, "X1", "X0", "Y1", "Y2", "X – Y"),
];
const PRUEBAS_TTR_AUTO_TRIF = [
  filaTtr(1, "H1", "H0-X0", "X1", "H0-X0", "H – X φ1"),
  filaTtr(2, "H2", "H0-X0", "X2", "H0-X0", "H – X φ2"),
  filaTtr(3, "H3", "H0-X0", "X3", "H0-X0", "H – X φ3"),
  filaTtr(4, "H1", "H0-X0", "Y1", "H0-X0", "H – Y φ1"),
  filaTtr(5, "H2", "H0-X0", "Y2", "H0-X0", "H – Y φ2"),
  filaTtr(6, "H3", "H0-X0", "Y3", "H0-X0", "H – Y φ3"),
  filaTtr(7, "X1", "H0-X0", "Y1", "H0-X0", "X – Y φ1"),
  filaTtr(8, "X2", "H0-X0", "Y2", "H0-X0", "X – Y φ2"),
  filaTtr(9, "X3", "H0-X0", "Y3", "H0-X0", "X – Y φ3"),
];
const PRUEBAS_TTR_AUTO_MONO = [
  filaTtr(1, "H1", "H0-X0", "Y1", "H0-X0", "H – X"),
  filaTtr(2, "H1", "H0-X0", "Y1", "Y2", "H – Y"),
  filaTtr(3, "X1", "H0-X0", "Y1", "Y2", "X – Y"),
];
const PRUEBAS_TTR_MONO_2D = [
  filaTtr(1, "H1", "H0", "X1", "X2", "H – X"),
];

const _NOTAS_TTR_2D = {
  "Estrella - Delta": "Figura 5 — Estrella-Delta (Y-D), 30°.",
  "Delta - Estrella": "Figura 6 — Delta-Estrella (D-Y), 30°.",
  "Estrella - Estrella": "Estrella-Estrella (Y-Y), desplazamiento 0°.",
  "Delta - Delta": "Delta-Delta (D-D), desplazamiento 0°.",
};
const _FILAS_TTR_2D = {
  "Estrella - Delta": PRUEBAS_TTR_YD,
  "Delta - Estrella": PRUEBAS_TTR_DY,
  "Estrella - Estrella": PRUEBAS_TTR_YY,
  "Delta - Delta": PRUEBAS_TTR_DD,
};

// Diagramas vectoriales (ST-CT-007, figuras 5 a 9). Mismos datos que
// _VECTORES_TTR en SAPE2.py: nombre, figura, desplazamiento angular y los
// grupos (devanados) a dibujar. Cada grupo: [forma, lado, tipo, ...bornes].
const VECTORES_TTR = {
  "Y-D": ["Estrella-Delta Y-D", "Fig. 5", "30°", [
    ["estrella", "ALTA", "ESTRELLA", "H1", "H3", "H0", "H2"],
    ["delta", "BAJA", "DELTA", "X2", "X1", "X3"],
  ]],
  "D-Y": ["Delta-Estrella D-Y", "Fig. 6", "30°", [
    ["delta", "ALTA", "DELTA", "H2", "H3", "H1"],
    ["estrella", "BAJA", "ESTRELLA", "X2", "X1", "X0", "X3"],
  ]],
  "Y-Y": ["Estrella-Estrella Y-Y", "—", "0°", [
    ["estrella", "ALTA", "ESTRELLA", "H1", "H3", "H0", "H2"],
    ["estrella", "BAJA", "ESTRELLA", "X2", "X1", "X0", "X3"],
  ]],
  "D-D": ["Delta-Delta D-D", "—", "0°", [
    ["delta", "ALTA", "DELTA", "H2", "H3", "H1"],
    ["delta", "BAJA", "DELTA", "X2", "X3", "X1"],
  ]],
  "Y-Y-D": ["Estrella-Estrella-Delta Y-Y-D", "Fig. 7", "0° / 30°", [
    ["estrella", "ALTA", "ESTRELLA", "H1", "H3", "H0", "H2"],
    ["estrella", "BAJA", "ESTRELLA", "X2", "X1", "X0", "X3"],
    ["delta", "TERCIARIO", "DELTA", "Y2", "Y3", "Y1"],
  ]],
  "Y-Y-D_MONO": ["Estrella-Estrella-Delta Y-Y-D monofásico", "Fig. 7", "H1-H0 / X1-X0 / Y1-Y2", [
    ["vertical", "ALTA", "ESTRELLA", "H1", "H0"],
    ["vertical", "BAJA", "ESTRELLA", "X1", "X0"],
    ["horizontal", "TERCIARIO", "DELTA", "Y1", "Y2"],
  ]],
  "AUTO_YY": ["Autotransformador Y-Y", "Fig. 8", "0°", [
    ["cruz", "ALTA-BAJA", "ESTRELLA-ESTRELLA", "H2·X2", "H1·X1", "H3·X3", "H0·X0"],
  ]],
  "AUTO_YYD": ["Autotransformador Y-Y-D", "Fig. 8", "0° / 30°", [
    ["cruz", "ALTA-BAJA", "ESTRELLA-ESTRELLA", "H2·X2", "H1·X1", "H3·X3", "H0/X0"],
    ["delta", "TERCIARIO", "DELTA", "Y2", "Y3", "Y1"],
  ]],
  "AUTO_MONO": ["Autotransformador monofásico", "Fig. 9", "Ie por par H·X·Y", [
    ["vertical3", "ALTA-BAJA", "ESTRELLA-ESTRELLA", "H1", "H0/X0", "X1"],
    ["vertical", "TERCIARIO", "DELTA", "Y2", "Y1"],
  ]],
  "MONO_2D": ["Monofásico 2 devanados", "Anexo A", "Ie H–X", [
    ["vertical", "ALTA", "ESTRELLA", "H1", "H0"],
    ["vertical", "BAJA", "DELTA", "X1", "X2"],
  ]],
};

// Misma clave que _clave_vector_ttr en SAPE2.py.
function claveVectorTtr(equipo, configuracion, conexion) {
  const mono = configuracion === "Monofásico";
  if (equipo.includes("Reactores")) return null;
  if (equipo.includes("Autotransformadores")) {
    if (mono) return "AUTO_MONO";
    if (conexion.includes("Delta")) return "AUTO_YYD";
    return "AUTO_YY";
  }
  if (equipo.includes("3 Devanados")) return mono ? "Y-Y-D_MONO" : "Y-Y-D";
  if (mono) return "MONO_2D";
  return {
    "Estrella - Delta": "Y-D",
    "Delta - Estrella": "D-Y",
    "Estrella - Estrella": "Y-Y",
    "Delta - Delta": "D-D",
  }[conexion] || "Y-D";
}

// Bornes que representa un campo de prueba (expande "H0-X0" en H0 y X0, y
// junta alias con guion/diagonal/punto). Igual que _expandir_campo_ttr.
function _expandirCampoTtr(valor) {
  if (!valor || valor === "—" || valor === "-----") return [];
  const tokens = [];
  for (let parte of String(valor).split(/[,;]+/)) {
    parte = parte.trim();
    if (!parte) continue;
    tokens.push(parte);
    if (parte.includes("H0-X0") || parte.includes("H0/X0") || parte.includes("H0·X0")) {
      tokens.push("H0", "X0");
    }
    const m = parte.match(/[HXY]\d/gi) || [];
    m.forEach((t) => tokens.push(t.toUpperCase()));
  }
  return [...new Set(tokens)];
}

// Colores de los bornes según la prueba elegida: CN/GN negro, CR/GR rojo.
function coloresVectorTtr(prueba) {
  const colores = {};
  if (!prueba) return colores;
  const campos = [["cn", "#000000"], ["gn", "#000000"], ["cr", "#FF0000"], ["gr", "#FF0000"]];
  for (const [campo, color] of campos) {
    for (const tok of _expandirCampoTtr(prueba[campo])) colores[tok] = color;
  }
  if (colores.H0 || colores.X0) {
    const c = colores.H0 || colores.X0;
    ["H0-X0", "H0/X0", "H0·X0"].forEach((alias) => { if (!colores[alias]) colores[alias] = c; });
  }
  return colores;
}

function colorBorneTtr(texto, colores) {
  if (colores[texto]) return colores[texto];
  const tokens = (texto.match(/[HXY]\d/gi) || []).map((t) => t.toUpperCase());
  for (const tok of tokens) if (colores[tok]) return colores[tok];
  return "#7C3AED"; // morado libre (sin rol en esta prueba)
}

// Ancho del lienzo según cuántos devanados (grupos) se dibujan. Igual que
// _medida_vector_ttr en SAPE2.py.
function medidaVectorTtr(n) {
  const paso = n >= 3 ? 200 : 230;
  const margen = n === 1 ? 190 : 140;
  const ancho = margen + Math.max(0, n - 1) * paso + 165;
  return { margen, paso, ancho };
}

// Dibuja el diagrama vectorial (SVG) de la prueba elegida: un panel por
// devanado (estrella, delta, vertical, cruz...), con los bornes CN/CR en
// negro/rojo y GN/GR en negro/rojo, igual que en SAPE2.py (modo "cables").
function svgVectorTtr(clave, prueba) {
  const ficha = VECTORES_TTR[clave];
  if (!ficha) return "";
  const grupos = ficha[3];
  const n = grupos.length;
  const colores = coloresVectorTtr(prueba);
  const { margen, paso, ancho } = medidaVectorTtr(n);
  const alto = 280;
  const lineas = [];
  const nodos = [];
  const labels = [];

  const colorBorne = (b) => colorBorneTtr(b, colores);
  function linea(x1, y1, x2, y2, a, b) {
    const ca = colorBorne(a), cb = colorBorne(b);
    lineas.push([x1, y1, x2, y2, ca, cb]);
    nodos.push([x1, y1, ca], [x2, y2, cb]);
  }
  function borne(x, y, texto, anchor) {
    labels.push([x, y, texto, colorBorne(texto), anchor]);
  }

  grupos.forEach((grupo, i) => {
    const cx = margen + i * paso;
    const kind = grupo[0];
    const pie = `${grupo[1]} · ${grupo[2]}`;
    const bornes = grupo.slice(3);
    const brazo = n === 1 ? 108 : 58;
    if (kind === "estrella") {
      const [arriba, izq, centro, der] = bornes;
      const largo = n > 1 ? 78 : 96;
      const cy = 128;
      const xIzq = cx - largo, yIzq = cy;
      const xArr = cx + largo * 0.5, yArr = cy - largo * 0.866;
      const xDer = cx + largo * 0.5, yDer = cy + largo * 0.866;
      linea(xIzq, yIzq, cx, cy, izq, centro);
      linea(xArr, yArr, cx, cy, arriba, centro);
      linea(xDer, yDer, cx, cy, der, centro);
      borne(xIzq - 12, yIzq, izq, "end");
      borne(xArr + 8, yArr - 6, arriba, "start");
      borne(xDer + 8, yDer + 6, der, "start");
      borne(cx + 28, cy, centro, "start");
    } else if (kind === "delta") {
      const [apex, izq, der] = bornes;
      const medio = n === 1 ? 46 : 40;
      linea(cx, 96, cx - medio, 176, apex, izq);
      linea(cx, 96, cx + medio, 176, apex, der);
      linea(cx - medio, 176, cx + medio, 176, izq, der);
      borne(cx, 80, apex, "middle");
      borne(cx - medio, 190, izq, "middle");
      borne(cx + medio, 190, der, "middle");
    } else if (kind === "cruz") {
      const [arriba, izq, der, abajo] = bornes;
      linea(cx, 56, cx, 124, arriba, arriba);
      linea(cx, 124, cx, 196, abajo, abajo);
      linea(cx - brazo, 124, cx, 124, izq, izq);
      linea(cx, 124, cx + brazo, 124, der, der);
      borne(cx, 40, arriba, "middle");
      borne(cx - brazo - 16, 124, izq, "end");
      borne(cx + brazo + 16, 124, der, "start");
      borne(cx, 212, abajo, "middle");
    } else if (kind === "vertical3") {
      const [arriba, medioB, abajo] = bornes;
      linea(cx, 64, cx, 128, arriba, medioB);
      linea(cx, 128, cx, 196, medioB, abajo);
      borne(cx, 46, arriba, "middle");
      borne(cx + 14, 128, medioB, "start");
      borne(cx, 214, abajo, "middle");
    } else if (kind === "horizontal") {
      const [izq, der] = bornes;
      linea(cx - brazo, 128, cx + brazo, 128, izq, der);
      borne(cx - brazo - 16, 128, izq, "end");
      borne(cx + brazo + 16, 128, der, "start");
    } else {
      const [arriba, abajo] = bornes;
      linea(cx, 78, cx, 186, arriba, abajo);
      borne(cx, 60, arriba, "middle");
      borne(cx, 204, abajo, "middle");
    }
    labels.push([cx, 262, pie, "#DB2777", "middle"]);
  });

  let svg = `<svg viewBox="0 0 ${ancho} ${alto}" xmlns="http://www.w3.org/2000/svg">`;
  for (const [x1, y1, x2, y2, ca, cb] of lineas) {
    if (ca === cb) {
      svg += `<line x1="${x1.toFixed(1)}" y1="${y1.toFixed(1)}" x2="${x2.toFixed(1)}" y2="${y2.toFixed(1)}" stroke="${ca}" stroke-width="4" stroke-linecap="round"/>`;
    } else {
      const mx = (x1 + x2) / 2, my = (y1 + y2) / 2;
      svg += `<line x1="${x1.toFixed(1)}" y1="${y1.toFixed(1)}" x2="${mx.toFixed(1)}" y2="${my.toFixed(1)}" stroke="${ca}" stroke-width="4" stroke-linecap="round"/>`;
      svg += `<line x1="${mx.toFixed(1)}" y1="${my.toFixed(1)}" x2="${x2.toFixed(1)}" y2="${y2.toFixed(1)}" stroke="${cb}" stroke-width="4" stroke-linecap="round"/>`;
    }
  }
  for (const [x, y, color] of nodos) {
    svg += `<circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="4.5" fill="${color}"/>`;
  }
  for (const [x, y, texto, color, anchor] of labels) {
    const esc_ = String(texto).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
    const tamano = color === "#DB2777" ? 12 : 13;
    svg += `<text x="${x.toFixed(1)}" y="${(y + 4).toFixed(1)}" text-anchor="${anchor}" fill="${color}" font-family="Consolas, monospace" font-size="${tamano}" font-weight="bold">${esc_}</text>`;
  }
  svg += `</svg>`;
  return svg;
}

// Misma selección que _filas_ttr en SAPE2.py (obtener_tabla_conexiones_ttr).
function filasTtr(equipo, configuracion, conexion) {
  const mono = configuracion === "Monofásico";
  if (equipo.includes("Reactores")) {
    return [[], "ST-CT-007 no publica conexiones TTR para reactores."];
  }
  if (equipo.includes("3 Devanados") && mono) {
    return [PRUEBAS_TTR_YYD_MONO, "Tres devanados monofásico — Alta H1-H0, Baja X1-X0, Terciario Y1-Y2."];
  }
  if (equipo.includes("3 Devanados")) {
    return [PRUEBAS_TTR_YYD, "Figura 7 — Estrella-Estrella-Delta (Y-Y-D), 0° / 30°."];
  }
  if (equipo.includes("Autotransformadores") && mono) {
    return [PRUEBAS_TTR_AUTO_MONO, "Figura 9 — Autotransformador monofásico."];
  }
  if (equipo.includes("Autotransformadores")) {
    const nota = conexion === "Estrella - Estrella"
      ? "Figura 8 — Autotransformador estrella-estrella (Y-Y)."
      : "Figura 8 — Autotransformador estrella-estrella-delta (Y-Y-D).";
    return [PRUEBAS_TTR_AUTO_TRIF, nota];
  }
  if (mono) {
    return [PRUEBAS_TTR_MONO_2D, "Anexo A — Monofásico de dos devanados."];
  }
  const filas = _FILAS_TTR_2D[conexion] || PRUEBAS_TTR_YD;
  const nota = _NOTAS_TTR_2D[conexion] || _NOTAS_TTR_2D["Estrella - Delta"];
  return [filas, nota];
}

function llevaTerciarioTtr(equipo) {
  return equipo.includes("3 Devanados") || equipo.includes("Autotransformadores");
}

function llevaFaseTtr(configuracion) {
  return configuracion === "Monofásico";
}

// ---------- Captura y dictamen (paso 04) ----------
// Nota: el escritorio (SAPE2.py) todavía no trae esta parte programada —
// paso 04 solo mostraba la prueba elegida. Este cálculo se arma a partir
// del procedimiento ST-CT-007 (relación teórica Tabla 1, %DIF ecuación 14).

// Cuántos taps tiene el cambiador y cuál es el central (neutro).
function tapsTtr(tipoCambiador) {
  if ((tipoCambiador || "").includes("21")) return { n: 21, centro: 11 };
  if ((tipoCambiador || "").includes("23")) return { n: 23, centro: 12 };
  return { n: 5, centro: 3 };
}

// Qué par de devanados mide la prueba (para elegir los kV de placa).
function parMideTtr(mide) {
  const t = (mide || "").replace("–", "-").replace("—", "-");
  if (t.includes("X") && t.includes("Y") && !t.includes("H")) return "X-Y";
  if (t.includes("H") && t.includes("Y") && !t.includes("X")) return "H-Y";
  return "H-X";
}

// Relación teórica nominal (tap central), Tabla 1 del ST-CT-007: el factor
// √3 solo aplica entre devanados Delta-Estrella de un transformador de 2
// devanados; en los demás casos se usa la relación directa de los kV de
// placa del par que mide la prueba.
function relacionNominalTtr(d, prueba) {
  const par = parMideTtr(prueba.mide);
  const campoP = par === "X-Y" ? "voltajeX" : "voltajeH";
  const campoS = par === "H-X" ? "voltajeX" : "voltajeY";
  const vp = numero(d[campoP]);
  const vs = numero(d[campoS]);
  if (vp == null || vs == null || vs === 0) return { rt: null, par };
  let factor = 1;
  if (par === "H-X" && d.equipo.includes("2 Devanados")) {
    if (d.conexion === "Delta - Estrella") factor = 1.73;
    else if (d.conexion === "Estrella - Delta") factor = 1 / 1.73;
  }
  return { rt: (vp / vs) * factor, par };
}

// Regulación CFE: 0.625 % por paso de tap, a partir del tap central.
function relacionTeoricaTapTtr(nominal, tap, centro, usarRegulacion) {
  if (nominal == null) return null;
  if (!usarRegulacion) return nominal;
  return nominal * (1 + 0.00625 * (tap - centro));
}

// %DIF = 100 × (RT − RM) / RT (ecuación 14, ST-CT-007).
function evaluarTtr(rt, rm) {
  if (rt == null || rt === 0 || rm == null) return null;
  const dif = (100 * (rt - rm)) / rt;
  const absDif = Math.abs(dif);
  let estado, frase;
  if (absDif <= 0.5) {
    estado = "ACEPTADO";
    frase = "La diferencia está dentro del 0.5 % que exige ST-CT-007 para la primera medición (puesta en servicio contra la relación teórica de placa).";
  } else {
    estado = "INVESTIGAR";
    frase = "La diferencia rebasa el 0.5 %: revise el equipo de medición y las conexiones, la ejecución de la prueba, la calibración del TTR y, si nada de eso explica la diferencia, investigue espiras en corto en el transformador.";
  }
  return { dif, absDif, estado, frase, rt, rm };
}
