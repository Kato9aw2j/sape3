// Datos y cálculos de Resistencia de Aislamiento (ST-CT-001).
// Deben coincidir con SAPE2.py: si cambia una prueba allá, cambia aquí.
"use strict";

const EQUIPOS = [
  { id: "2d", nombre: "Transformadores de 2 Devanados", familia: "potencia" },
  { id: "3d", nombre: "Transformadores de 3 Devanados", familia: "potencia" },
  { id: "auto", nombre: "Autotransformadores", familia: "potencia" },
  { id: "reactor", nombre: "Reactores", familia: "potencia" },
  { id: "gen", nombre: "Generadores / Máquinas Rotatorias", familia: "rotativa" },
  { id: "tc", nombre: "Transformadores de Corriente - TCs", familia: "tc" },
  { id: "tp", nombre: "Transformadores de Potencial - TPs", familia: "tp" },
  { id: "tpc", nombre: "Transformadores de Potencial Capacitivo - TPCs", familia: "tp" },
  { id: "apart", nombre: "Apartarrayos", familia: "apartarrayos" },
];

function p(prueba, kv, linea, tierra, guarda, medicion, minutos) {
  return { prueba: String(prueba), kv, linea, tierra, guarda, medicion, minutos };
}

const V = "-----";
const KV_POT = "2500-5000";

const PRUEBAS = {
  "2d": [
    p(1, KV_POT, "H", "Tq", "X", "RH", 10),
    p(2, KV_POT, "X", "Tq", "H", "RX", 10),
    p(3, KV_POT, "X", "H", V, "RHX", 10),
    p(4, KV_POT, "H", "X+Tq", V, "RH + RHX", 10),
    p(5, KV_POT, "X", "H+Tq", V, "RX + RHX", 10),
  ],
  "3d": [
    p(1, KV_POT, "H", "Tq", "X+Y", "RH", 10),
    p(2, KV_POT, "X", "Tq", "H+Y", "RX", 10),
    p(3, KV_POT, "Y", "Tq", "H+X", "RY", 10),
    p(4, KV_POT, "H", "X", "Y+Tq", "RHX", 10),
    p(5, KV_POT, "H", "Y", "X+Tq", "RHY", 10),
    p(6, KV_POT, "X", "Y", "H+Tq", "RXY", 10),
    p(7, KV_POT, "H+X+Y", "Tq", V, "RH + RX + RY", 10),
    p(8, KV_POT, "H", "X+Y+Tq", V, "RH + RHY + RHX", 10),
    p(9, KV_POT, "X", "H+Y+Tq", V, "RX + RXY + RHX", 10),
    p(10, KV_POT, "Y", "H+X+Tq", V, "RY + RHY + RXY", 10),
  ],
  auto: [
    p(1, KV_POT, "H-X", "Y+Tq", V, "RHX + RHXY", 10),
    p(2, KV_POT, "H-X", "Tq", "Y", "RHX", 10),
    p(3, KV_POT, "H-X", "Y", "Tq", "RHXY", 10),
    p(4, KV_POT, "Y", "H-X+Tq", V, "RY + RHXY", 10),
    p(5, KV_POT, "Y", "Tq", "H-X", "RY", 10),
  ],
  auto_sin: [p(1, KV_POT, "H-X", "Tq", V, "RHX", 10)],
  reactor: [p(1, KV_POT, "H", "Tq", V, "RH", 10)],
  // Fig. 10 y formato SC-CT-001-F: 10 minutos, corrección a 40 °C.
  gen: [
    p(1, "Según Tabla 2", "A", "B+C+Carcasa", V, "RAT + RAB + RAC", 10),
    p(2, "Según Tabla 2", "B", "A+C+Carcasa", V, "RBT + RAB + RBC", 10),
    p(3, "Según Tabla 2", "C", "A+B+Carcasa", V, "RCT + RAC + RBC", 10),
    p(4, "Según Tabla 2", "A+B+C", "Carcasa", V, "RAT + RBT + RCT", 10),
    p(5, "500", "Rotor", "Carcasa", V, "RRT", 10),
  ],
  tc: [
    p(1, "5000", "P1, P2", "S1, S2, S3, S4", "Porcelana", "RP + RPC", 1),
    p(2, "500", "S1, S2, S3, S4", "P1, P2", V, "RSC", 1),
  ],
  // Fig. 16 y formato SC-CT-001-H.
  tp: [
    p(1, "5000", "P", "Tq", "S", "RP", 1),
    p(2, "5000", "P", "S", "Tq", "RPS + RP", 1),
    p(3, "500", "S", "Tq", "P", "RS", 1),
  ],
  apart_una: [p(1, "2500/5000", "A", "B", V, "RAB", 1)],
  // Fig. 17 b): tres secciones, sin guarda.
  apart_varias: [
    p(1, "5000", "A", "B+C+D", V, "RAB", 1),
    p(2, "5000", "B", "C+D", V, "RBC", 1),
    p(3, "5000", "C", "D", V, "RCD", 1),
    p(4, "5000", "A", "D", V, "RAD", 1),
  ],
};
PRUEBAS.tpc = PRUEBAS.tp;

function pruebasDe(datos) {
  if (datos.equipo === "auto") {
    return datos.terciario === "sin" ? PRUEBAS.auto_sin : PRUEBAS.auto;
  }
  if (datos.equipo === "apart") {
    return datos.secciones === "una" ? PRUEBAS.apart_una : PRUEBAS.apart_varias;
  }
  return PRUEBAS[datos.equipo] || [];
}

function equipoDe(id) {
  return EQUIPOS.find((e) => e.id === id) || EQUIPOS[0];
}

// Apartarrayos y máquinas rotatorias son de aislamiento sólido: nunca aceite.
function soloSolido(id) {
  const familia = equipoDe(id).familia;
  return familia === "apartarrayos" || familia === "rotativa";
}

function enAceite(datos) {
  return !soloSolido(datos.equipo) && datos.aislamiento === "aceite";
}

function baseTemp(id) {
  return equipoDe(id).familia === "rotativa" ? 40 : 20;
}

// Tabla 1 del ST-CT-001 (base 20 °C).
const KT_ACEITE = [
  [0, 0.25], [5, 0.36], [10, 0.5], [15.6, 0.74], [20, 1.0], [25, 1.4],
  [30, 1.98], [35, 2.8], [40, 3.95], [45, 5.6], [50, 7.85], [55, 11.2],
  [60, 15.85], [65, 22.4], [70, 31.75], [75, 44.7],
];
const KT_SECO = [
  [0, 0.4], [5, 0.45], [10, 0.5], [15.6, 0.75], [20, 1.0], [25, 1.3],
  [30, 1.6], [35, 2.05], [40, 2.5], [45, 3.25], [50, 4.0], [55, 5.2],
  [60, 5.4], [65, 8.7], [70, 10.0], [75, 13.0],
];

function ktTabla1(temp, aceite) {
  const tabla = aceite ? KT_ACEITE : KT_SECO;
  if (temp <= tabla[0][0]) return tabla[0][1];
  if (temp >= tabla[tabla.length - 1][0]) return tabla[tabla.length - 1][1];
  for (let i = 0; i < tabla.length - 1; i++) {
    const [t0, k0] = tabla[i];
    const [t1, k1] = tabla[i + 1];
    if (temp >= t0 && temp <= t1) return k0 + ((k1 - k0) * (temp - t0)) / (t1 - t0);
  }
  return 1;
}

// Rotatorias: IEEE 43 a 40 °C (ST-CT-001, 3.5.4 y 4.2.5).
function ktEquipo(temp, datos) {
  if (baseTemp(datos.equipo) === 40) return Math.pow(0.5, (40 - temp) / 10);
  return ktTabla1(temp, enAceite(datos));
}

function numero(texto) {
  const bruto = String(texto == null ? "" : texto).trim().replace("%", "").replace(",", ".");
  if (!bruto) return null;
  const valor = Number(bruto);
  return Number.isFinite(valor) ? valor : null;
}

// Lectura en megaohms. Sin letra son MΩ; G = gigaohms; T = teraohms.
function lectura(texto) {
  const m = String(texto == null ? "" : texto).trim().replace(",", ".")
    .match(/^(\d+(?:\.\d+)?)\s*([mgt])?/i);
  if (!m) return null;
  const unidad = (m[2] || "M").toUpperCase();
  const escala = { M: 1, G: 1000, T: 1000000 }[unidad];
  return { valor: Number(m[1]) * escala, unidad };
}

function fmtMohm(valor, unidad) {
  if (valor == null) return "sin lectura";
  const u = { M: [1, "MΩ"], G: [1000, "GΩ"], T: [1000000, "TΩ"] }[unidad] || [1, "MΩ"];
  return `${Number((valor / u[0]).toPrecision(6))} ${u[1]}`;
}

// Mismo criterio que _resultado_dictamen_ra de SAPE2.py.
function dictamen(datos, prueba, lecturas) {
  const eq = equipoDe(datos.equipo);
  const temp = numero(datos.tempDevanado);
  if (temp == null) {
    return { error: "Falta la temperatura del devanado. Sin ella no se puede corregir la resistencia a la temperatura base (Rc = Rt × Kt)." };
  }
  const base = baseTemp(datos.equipo);
  const aceite = enAceite(datos);
  const kt = ktEquipo(temp, datos);
  const l30 = lectura(lecturas.r30);
  const l1 = lectura(lecturas.r1);
  const l10 = lectura(lecturas.r10);
  const r30 = l30 && l30.valor;
  const r1 = l1 && l1.valor;
  const r10 = l10 && l10.valor;
  const u1 = l1 ? l1.unidad : "M";
  const u10 = l10 ? l10.unidad : "M";
  const minutos = prueba.minutos;
  if (minutos === 10 && (r1 == null || r10 == null)) {
    return { error: "Para el índice de polarización hacen falta la lectura de 1 min y la de 10 min." };
  }
  if (minutos !== 10 && r1 == null) {
    return { error: "Escriba la lectura a 1 min. Sin letra son megaohms; G al final son gigaohms y T teraohms." };
  }
  const hr = numero(datos.humedad);
  const ambiente = numero(datos.tempAmbiente);
  const lineas = [];
  const origen = base === 40 ? "IEEE 43, base 40 °C" : `${aceite ? "aceite" : "seco"}, Tabla 1`;
  lineas.push(`${eq.nombre}. Aislamiento ${aceite ? "sumergido en aceite" : "seco"}.`);
  lineas.push(
    (ambiente != null ? `Ambiente ${ambiente} °C. ` : "Ambiente sin registrar. ") +
    (hr != null ? `Humedad relativa ${hr} %. ` : "Humedad relativa sin registrar. ") +
    `Devanado ${temp} °C. Kt = ${kt.toFixed(3)} (${origen}).`
  );
  if (Math.abs(temp - base) > 5) {
    lineas.push(`La temperatura del devanado se aleja de la referencia de ${base} °C. La resistencia se corrige con Kt antes del dictamen.`);
  }
  let estado;
  let ip = null;
  let ia = null;
  if (minutos === 10 && r30 != null && r1 < r30 * 0.99) {
    estado = "RECHAZADO";
    lineas.push("La resistencia baja de 30 s a 1 min. El procedimiento exige que la curva no descienda.");
  } else if (minutos === 10 && r10 < r1 * 0.99) {
    estado = "RECHAZADO";
    lineas.push("La resistencia baja de 1 min a 10 min. El procedimiento exige que la curva no descienda.");
  } else if (eq.familia === "tc" || eq.familia === "tp") {
    const minimo = eq.familia === "tc" ? 45000 : 40000;
    const nombre = eq.familia === "tc" ? "TC" : "TP / TPC";
    const rc = r1 * kt;
    lineas.push(`R a 1 min medida ${fmtMohm(r1, u1)}. Corregida a 20 °C: ${fmtMohm(rc, u1)}.`);
    lineas.push(`Tabla 5 ST-CT-001, ${nombre}: mínimo ${minimo.toLocaleString("es-MX")} MΩ a 1 min y 20 °C.`);
    if (rc >= minimo) {
      estado = "ACEPTADO";
      lineas.push("La resistencia corregida cumple el mínimo. Aislamiento aceptado.");
    } else {
      estado = "RECHAZADO";
      lineas.push("La resistencia corregida queda debajo del mínimo. Aislamiento rechazado.");
    }
  } else if (minutos === 10) {
    ip = r10 / r1;
    lineas.push(
      `R 1 min ${fmtMohm(r1, u1)} → ${fmtMohm(r1 * kt, u1)} a ${base} °C. ` +
      `R 10 min ${fmtMohm(r10, u10)} → ${fmtMohm(r10 * kt, u10)} a ${base} °C.`
    );
    lineas.push(`ip = R10 / R1 = ${ip.toFixed(2)}. El procedimiento acepta ip ≥ 1.5.`);
    if (r30) {
      ia = r1 / r30;
      lineas.push(`ia = R1 / R30 = ${ia.toFixed(2)}. La banda es 1.45 ± 25 %.`);
      if (aceite) lineas.push("En aceite el ia no decide el dictamen.");
    }
    if (ip >= 2) {
      estado = "ACEPTADO";
      lineas.push("El índice de polarización está en buen estado.");
    } else if (ip >= 1.5) {
      estado = "INVESTIGAR";
      lineas.push("Cumple el mínimo de 1.5, pero queda debajo de 2.0: banda de monitoreo.");
    } else {
      estado = "RECHAZADO";
      lineas.push("El índice de polarización queda debajo de 1.5.");
    }
    if (estado === "ACEPTADO" && !aceite && ia != null && !(ia >= 1.45 * 0.75 && ia <= 1.45 * 1.25)) {
      estado = "INVESTIGAR";
      lineas.push("El ia del aislamiento sólido quedó fuera de la banda.");
    }
  } else {
    const rc = r1 * kt;
    lineas.push(`R a 1 min medida ${fmtMohm(r1, u1)}. Corregida a ${base} °C: ${fmtMohm(rc, u1)}.`);
    lineas.push("Este equipo no tiene mínimo de Tabla 5. La lectura corregida queda para compararla con el fabricante y con pruebas anteriores.");
    estado = "INVESTIGAR";
  }
  if (hr != null && hr >= 75 && estado === "ACEPTADO") {
    estado = "INVESTIGAR";
    lineas.push("La humedad relativa es de 75 % o mayor. El procedimiento pide hacer la prueba por debajo de ese valor.");
  }
  return { estado, lineas, kt, base, ip, ia, temp };
}

const CODIGOS = [
  "RHXY", "RHX", "RHY", "RXY", "RPC", "RPS", "RSC", "RAT", "RBT", "RCT", "RRT",
  "RAD", "RAC", "RAB", "RBC", "RCD", "RH", "RX", "RY", "RP", "RS",
];
const RE_CODIGO = new RegExp(CODIGOS.join("|"), "g");

function codigosMedidos(prueba) {
  const hallados = new Set(String(prueba.medicion).match(RE_CODIGO) || []);
  // RAD cubre los tres tramos en serie del apartarrayos.
  if (hallados.has("RAD")) ["RAB", "RBC", "RCD"].forEach((c) => hallados.add(c));
  return hallados;
}

function descripcionCodigo(codigo, equipo) {
  const auto = equipo === "auto";
  const tabla = {
    RP: equipo === "tc" ? "Resistencia del primario (P1-P2)" : "Resistencia del primario (P)",
    RS: "Resistencia del secundario (S)",
    RPC: "Resistencia del primario a la carcasa (porcelana)",
    RPS: "Resistencia entre primario y secundario",
    RSC: "Resistencia del secundario (S1-S2)",
    RH: equipo === "reactor" ? "Resistencia del devanado (H)" : "Resistencia del devanado de alta (H)",
    RX: "Resistencia del devanado de baja (X)",
    RY: "Resistencia del devanado terciario (Y)",
    RHX: auto ? "Resistencia de H–X hacia el tanque" : "Resistencia entre alta (H) y baja (X)",
    RHY: "Resistencia entre alta (H) y terciario (Y)",
    RXY: "Resistencia entre baja (X) y terciario (Y)",
    RHXY: "Resistencia entre H–X y el terciario (Y)",
    RAT: "Resistencia de la fase A a carcasa",
    RBT: "Resistencia de la fase B a carcasa",
    RCT: "Resistencia de la fase C a carcasa",
    RRT: "Resistencia del rotor a la carcasa",
    RAB: equipo === "gen" ? "Resistencia entre las fases A y B" : "Resistencia entre las secciones A y B",
    RBC: equipo === "gen" ? "Resistencia entre las fases B y C" : "Resistencia entre las secciones B y C",
    RAC: "Resistencia entre las fases A y C",
    RCD: "Resistencia entre las secciones C y D",
  };
  return tabla[codigo] || "Resistencia de aislamiento";
}

// Bornes que marca una columna: letras, TANQUE (Tq / Carcasa) y ROTOR.
function sitios(texto) {
  let t = String(texto || "").trim().toUpperCase();
  const fuera = new Set();
  if (!t || t === "-----" || t === "---" || t === "—") return fuera;
  if (t.includes("ROTOR")) {
    fuera.add("ROTOR");
    t = t.replace("ROTOR", " ");
  }
  if (/PORCEL/.test(t)) {
    fuera.add("PORCELANA");
    t = t.replace(/PORCELANA|PORCEL/g, " ");
  }
  if (/CARCASA|TANQUE|(^|[\s,+\-])TQ([\s,+\-]|$)/.test(t)) fuera.add("TANQUE");
  t = t.replace(/CARCASA|TANQUE/g, " ").replace(/(^|[\s,+\-])TQ(?=[\s,+\-]|$)/g, " ");
  t = t.replace(/([HXYPSABCD])\d+/g, "$1");
  (t.match(/[HXYPSABCD]/g) || []).forEach((letra) => fuera.add(letra));
  return fuera;
}

const VACIO = new Set(["", "-----", "---", "—"]);
