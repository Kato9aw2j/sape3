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
