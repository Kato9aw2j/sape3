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

function llevaTerciarioTtr(equipo) {
  return equipo.includes("3 Devanados") || equipo.includes("Autotransformadores");
}

function llevaFaseTtr(configuracion) {
  return configuracion === "Monofásico";
}
