// Datos y cálculos de Factor de Potencia al Aislamiento (ST-CT-002).
// Debe coincidir con SAPE2.py (_evaluar_fp, _kt_fp, _filas_fp): si cambia
// algo allá, cambia aquí también.
"use strict";

const EQUIPOS_FP = [
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
];

const ARREGLOS_FP = {
  "Autotransformadores": [
    "Con terciario accesible (Fig. 11)",
    "Terciario no accesible (Fig. 11, nota)",
  ],
  "Transformadores de Corriente - TCs": [
    "Un módulo (Fig. 21)",
    "Dos módulos: módulo superior (Fig. 22a)",
    "Dos módulos: módulo inferior (Fig. 22b)",
  ],
  "Transformadores de Potencial - TPs": [
    "Dos boquillas (Fig. 13)",
    "Una boquilla, neutro aterrizado interno (Fig. 14)",
    "Una boquilla, tierra desconectable (Fig. 15)",
    "Inductivo en cascada (Fig. 16)",
  ],
  "Transformadores de Potencial Capacitivo - TPCs": [
    "Arreglo típico (Fig. 17)",
    "Más de un módulo (Fig. 18)",
    "B2 y B3 comunes (Fig. 19)",
    "Fig. 19 con la línea aterrizada (1A-3A)",
    "Módulos con B1 = T2 (Fig. 20)",
    "Fig. 20 con la línea conectada",
  ],
  "Apartarrayos": [
    "Una sección (Fig. 23)",
    "Dos secciones (Fig. 24)",
    "Tres secciones (Fig. 25)",
    "Cuatro secciones (Tabla 7)",
    "Cinco secciones (Fig. 26)",
  ],
  "Cables de Potencia": [
    "Monofásico (Fig. 27)",
    "Trifásico (Fig. 28)",
  ],
};

const PRESERVACION_FP = [
  "Respiración libre / conservador",
  "Sellado o con gas, hasta 161 kV",
  "Sellado o con gas, de 161 a 750 kV",
];

// Tabla 4. Factor de corrección por temperatura (tres columnas de preservación).
const TABLA4_FP = [
  [0, 1.56, 1.57, 0.95], [2, 1.52, 1.50, 0.96], [4, 1.48, 1.44, 0.98],
  [6, 1.45, 1.37, 0.98], [8, 1.43, 1.31, 0.99], [10, 1.38, 1.25, 0.99],
  [12, 1.31, 1.19, 1.00], [14, 1.24, 1.14, 1.01], [16, 1.16, 1.09, 1.01],
  [18, 1.08, 1.05, 1.00], [20, 1.00, 1.00, 1.00], [22, 0.91, 0.96, 0.99],
  [24, 0.83, 0.92, 0.98], [26, 0.76, 0.88, 0.97], [28, 0.70, 0.84, 0.96],
  [30, 0.63, 0.80, 0.95], [32, 0.58, 0.76, 0.94], [34, 0.53, 0.73, 0.93],
  [36, 0.49, 0.70, 0.91], [38, 0.45, 0.67, 0.90], [40, 0.42, 0.65, 0.89],
  [42, 0.38, 0.62, 0.87], [44, 0.36, 0.59, 0.86], [46, 0.33, 0.56, 0.84],
  [48, 0.30, 0.54, 0.83], [50, 0.28, 0.51, 0.81], [52, 0.26, 0.49, 0.79],
  [54, 0.23, 0.47, 0.77], [56, 0.21, 0.45, 0.75], [58, 0.19, 0.43, 0.72],
  [60, 0.17, 0.41, 0.70],
];

// Tabla 6. Transformadores de instrumento sumergidos en aceite (0 a 44 °C).
const TABLA6_FP = [
  [0, 1.67], [2, 1.61], [4, 1.55], [6, 1.49], [8, 1.43], [10, 1.36],
  [12, 1.30], [14, 1.23], [16, 1.16], [18, 1.08], [20, 1.00],
  [22, 0.93], [24, 0.86], [26, 0.80], [28, 0.74], [30, 0.69],
  [32, 0.65], [34, 0.60], [36, 0.56], [38, 0.52], [40, 0.48],
  [42, 0.45], [44, 0.42],
];

// Tabla 9. Valores de FP para cables, según el aislamiento.
const TABLA9_FP = [
  ["Butilo hasta 15 kV", 3.0],
  ["Dacrón vidrio 5 kV", 6.0],
  ["Papel y aceite de 34.5 kV", 1.0],
  ["Papel y aceite de 69 a 230 kV", 1.0],
  ["Polietileno hasta 15 kV", 1.0],
  ["Hule 15 kV", 6.0],
  ["Barniz Cambridge hasta 15 kV", 5.0],
];

function interpolarFp(tabla, temp, columna) {
  columna = columna || 1;
  if (temp <= tabla[0][0]) return tabla[0][columna];
  if (temp >= tabla[tabla.length - 1][0]) return tabla[tabla.length - 1][columna];
  for (let i = 0; i < tabla.length - 1; i++) {
    const previo = tabla[i], siguiente = tabla[i + 1];
    const t0 = previo[0], t1 = siguiente[0];
    if (temp >= t0 && temp <= t1) {
      const k0 = previo[columna], k1 = siguiente[columna];
      return k0 + ((k1 - k0) * (temp - t0)) / (t1 - t0);
    }
  }
  return 1.0;
}

function esPotenciaFp(equipo) {
  return ["Devanados", "Autotransformadores", "Reactores"].some((n) => equipo.includes(n));
}
function esInstrumentoFp(equipo) {
  return ["TCs", "TPs", "TPCs"].some((n) => equipo.includes(n));
}
function llevaFaseFp(equipo, configuracion) {
  if (equipo.includes("Aceite")) return false;
  if (esPotenciaFp(equipo)) return configuracion === "Monofásico";
  return true;
}
function arregloFp(equipo, actual) {
  const opciones = ARREGLOS_FP[equipo] || [];
  if (!opciones.length) return "";
  return opciones.includes(actual) ? actual : opciones[0];
}

// Factor de corrección a 20 °C y la tabla de donde sale.
function ktFp(d) {
  const equipo = d.equipo;
  if (equipo.includes("Apartarrayos")) return { kt: 1.0, tabla: "sin corrección: se evalúan las pérdidas" };
  if (equipo.includes("Cables")) return { kt: 1.0, tabla: "sin corrección: Tabla 9" };
  const aceiteEquipo = equipo.includes("Aceite");
  if (!aceiteEquipo && !String(d.aislamiento).includes("Aceite")) {
    return { kt: 1.0, tabla: "sin corrección: aislamiento seco" };
  }
  const temp = numero(d.tempAceite);
  if (temp == null) return { kt: null, tabla: "" };
  if (esInstrumentoFp(equipo)) return { kt: interpolarFp(TABLA6_FP, temp, 1), tabla: "Tabla 6" };
  let columna = 1;
  if (!aceiteEquipo && PRESERVACION_FP.includes(d.preservacion)) {
    columna = PRESERVACION_FP.indexOf(d.preservacion) + 1;
  }
  return { kt: interpolarFp(TABLA4_FP, temp, columna), tabla: `Tabla 4, columna ${columna}` };
}

// %FP, corrección a 20 °C y dictamen según ST-CT-002. Mismo criterio que
// SAPE2.py _evaluar_fp.
function evaluarFp(d, kv, ma, watts) {
  const equipo = d.equipo;
  const { kt, tabla } = ktFp(d);
  if (kt == null) return null;
  const va = kv * ma;
  const fp = (100.0 * watts) / va;
  const fp20 = fp * kt;
  const mw = watts * 1000.0;
  const cap = (ma * 1000000.0) / (2 * Math.PI * 60 * kv);
  const nuevo = d.estado === "Puesta en servicio";
  let estado, frase, criterio, limite;

  if (equipo.includes("Apartarrayos")) {
    limite = 16.0 * Math.pow(kv / 2.5, 2);
    criterio = `Pérdidas máximas: 16 mW a 2.5 kV y 256 mW a 10 kV. A ${kv} kV el límite es ${limite.toFixed(0)} mW.`;
    if (mw <= limite) {
      estado = "ACEPTADO";
      frase = "Las pérdidas están dentro del límite. Compárelas con el historial y con equipos similares: pérdidas más bajas de lo normal indican resistores shunt rotos o circuito abierto.";
    } else {
      estado = "RECHAZADO";
      frase = "Las pérdidas rebasan el límite: humedad, suciedad, gaps corroídos o porcelana quebrada.";
    }
  } else if (equipo.includes("Cables")) {
    const nombre = d.aislamientoCable;
    const fila = TABLA9_FP.find(([n]) => n === nombre);
    limite = fila ? fila[1] : 1.0;
    criterio = `Tabla 9. ${nombre}: hasta ${limite} %.`;
    if (fp20 <= limite) {
      estado = "ACEPTADO";
      frase = "El factor de potencia está dentro de la guía de la Tabla 9.";
    } else {
      estado = "INVESTIGAR";
      frase = "El factor de potencia rebasa la guía de la Tabla 9. Compare con las mediciones iniciales del cable.";
    }
  } else if (equipo.includes("Aceite")) {
    criterio = "Aceite a 20 °C: nuevo hasta 0.05 %, bueno hasta 0.50 %.";
    if (fp20 <= 0.05) { estado = "ACEPTADO"; frase = "Aceite con valor de aceite nuevo."; }
    else if (fp20 <= 0.5) { estado = "ACEPTADO"; frase = "Aceite en buenas condiciones."; }
    else {
      estado = "INVESTIGAR";
      frase = "Arriba de 0.50 %: aceite deteriorado o contaminado. Verifique que la muestra sea representativa.";
    }
  } else if (equipo.includes("TCs")) {
    const mayor = d.claseKv === "115 kV o mayor";
    limite = mayor ? 0.5 : 1.0;
    criterio = `TC ${mayor ? "de 115 kV o mayor" : "menor de 115 kV"}: %FP a 20 °C hasta ${limite} %.`;
    if (fp20 <= limite) { estado = "ACEPTADO"; frase = "El factor de potencia corregido cumple el límite del TC."; }
    else {
      estado = "RECHAZADO";
      frase = "El factor de potencia corregido rebasa el límite del TC. Consulte el historial y los datos del fabricante.";
    }
  } else if (equipo.includes("TPCs")) {
    criterio = "TPC: alrededor de 0.25 % cuando es nuevo; con 0.5 % debe retirarse del servicio. La capacitancia se compara con la de placa (Tabla 5).";
    if (fp20 >= 0.5) { estado = "RECHAZADO"; frase = "Factor de potencia de 0.5 % o mayor: retirar del servicio."; }
    else if (fp20 > 0.25) {
      estado = "INVESTIGAR";
      frase = "Arriba del valor de un TPC nuevo (0.25 %). Vigile la tendencia y la variación de la capacitancia.";
    } else { estado = "ACEPTADO"; frase = "Factor de potencia dentro del valor de un TPC nuevo."; }
  } else if (equipo.includes("TPs")) {
    criterio = "TP inductivo: ST-CT-002 no fija un límite numérico. Las pruebas cruzadas 3 y 4 deben dar lecturas iguales y el factor de potencia debe ser bajo.";
    if (watts < 0) {
      estado = "INVESTIGAR";
      frase = "Lectura negativa en la prueba cruzada: posible devanado de alta tensión abierto.";
    } else {
      estado = "REGISTRADO";
      frase = "Compare esta lectura con la prueba completa, con las cruzadas de comprobación y con el historial del equipo.";
    }
  } else {
    criterio = "Nuevo: menor de 0.5 % a 20 °C. En operación: de 0.5 % a 1.0 %. Arriba de 1.0 % se investiga.";
    if (fp20 <= 0.5) { estado = "ACEPTADO"; frase = "Aislamiento en excelentes condiciones."; }
    else if (fp20 <= 1.0) {
      if (nuevo) {
        estado = "INVESTIGAR";
        frase = "Rebasa el 0.5 % que se acepta en un equipo que entra por primera vez en operación.";
      } else { estado = "ACEPTADO"; frase = "Valor aceptable para un equipo en operación."; }
    } else {
      estado = "INVESTIGAR";
      frase = "Arriba de 1.0 %: revise el aceite aislante, las boquillas y agentes externos, y la estadística de años anteriores. Si el valor va en aumento, programe mantenimiento mayor.";
    }
  }

  return {
    estado, frase, criterio, fp, fp20, kt, tabla,
    va, mva: va * 1000.0, mw, watts, cap, kv, ma,
    ma10: (ma * 10.0) / kv, w10: watts * Math.pow(10.0 / kv, 2),
    apartarrayos: equipo.includes("Apartarrayos"),
  };
}

// Tabla de conexiones de la figura de ST-CT-002 para el equipo (paso 03).
function filasFp(equipo, arreglo) {
  const V = "-----";
  function f(n, kv, hv, opts) {
    opts = opts || {};
    const gnd = opts.gnd || "", grd = opts.grd || "", ust = opts.ust || "";
    const modo = ust ? "UST" : (grd ? "GST-G" : "GST");
    return {
      prueba: String(n), kv, modo, hv,
      ground: gnd || V, guard: grd || V, ust: ust || V,
      flotando: opts.flot || "", medicion: opts.mide || "",
    };
  }

  if (equipo === "Transformadores de 2 Devanados") {
    return [
      f(1, "10", "H", { gnd: "X", mide: "CH+CHX" }),
      f(2, "10", "H", { grd: "X", mide: "CH" }),
      f(3, "10", "X", { gnd: "H", mide: "CX+CHX" }),
      f(4, "10", "X", { grd: "H", mide: "CX" }),
      f(5, "10", "H", { ust: "X", mide: "CHX" }),
      f(6, "10", "X", { ust: "H", mide: "CHX" }),
    ];
  }
  if (equipo === "Transformadores de 3 Devanados") {
    return [
      f(1, "10", "H", { gnd: "X", grd: "Y", mide: "CH+CHX" }),
      f(2, "10", "H", { grd: "X, Y", mide: "CH" }),
      f(3, "10", "X", { gnd: "Y", grd: "H", mide: "CX+CXY" }),
      f(4, "10", "X", { grd: "H, Y", mide: "CX" }),
      f(5, "10", "Y", { gnd: "H", grd: "X", mide: "CY+CHY" }),
      f(6, "10", "Y", { grd: "H, X", mide: "CY" }),
      f(7, "10", "H, X, Y", { mide: "CH+CX+CY" }),
    ];
  }
  if (equipo === "Autotransformadores") {
    if (arreglo.startsWith("Terciario no accesible")) {
      return [f(1, "10", "H+X", { gnd: "Tanque", mide: "CH" })];
    }
    return [
      f(1, "10", "H+X", { gnd: "Y", mide: "CH+CHY" }),
      f(2, "10", "H+X", { grd: "Y", mide: "CH" }),
      f(3, "10", "Y", { gnd: "H+X", mide: "CY+CHY" }),
      f(4, "10", "Y", { grd: "H+X", mide: "CY" }),
      f(5, "10", "H+X", { ust: "Y", mide: "CHY" }),
      f(6, "10", "Y", { ust: "H+X", mide: "CHY" }),
    ];
  }
  if (equipo === "Reactores") {
    return [f(1, "10", "H", { gnd: "Tanque", mide: "CH" })];
  }
  if (equipo === "Transformadores de Corriente - TCs") {
    if (arreglo.includes("22a")) {
      return [
        f(1, "10", "P1, P2", { gnd: "S1, S2", mide: "CP" }),
        f(2, "10", "S1, S2", { gnd: "P1, P2", mide: "CS" }),
      ];
    }
    if (arreglo.includes("22b")) {
      return [
        f(1, "10", "P1, P2", { gnd: "S1, S2", mide: "CP" }),
        f(2, "0.5", "S1, S2", { gnd: "P1, P2", mide: "CS" }),
      ];
    }
    return [
      f(1, "10", "P1, P2", { gnd: "S1, S2, S3, S4", mide: "CP" }),
      f(2, "0.5", "S1, S2, S3, S4", { gnd: "P1, P2", mide: "CS" }),
    ];
  }
  if (equipo === "Transformadores de Potencial - TPs") {
    if (arreglo.includes("Fig. 14")) {
      return [
        f(1, "10", "H1", { gnd: "H0", ust: "X1, Y1", mide: "Aislamiento entre devanados" }),
        f(2, "10", "H1", { gnd: "H0", grd: "X1, Y1", mide: "Corriente de excitación" }),
      ];
    }
    if (arreglo.includes("Fig. 16")) {
      return [f("1A", "5", "H0", { gnd: "X1-X3, Y1-Y3", flot: "H1", mide: "Completa" })];
    }
    const kv = arreglo.includes("Fig. 15") ? "5" : "10";
    return [
      f(1, kv, "H1, H2", { gnd: "X1", mide: "CH+CHX" }),
      f(2, kv, "H1, H2", { grd: "X1", mide: "CH" }),
      f(3, kv, "H1", { gnd: "X1", grd: "H2", mide: "CH+CHX" }),
      f(4, kv, "H2", { gnd: "X1", grd: "H1", mide: "CH+CHX" }),
    ];
  }
  if (equipo === "Transformadores de Potencial Capacitivo - TPCs") {
    const c12 = "C(B1-B2)", c23 = "C(B2-B3)";
    if (arreglo.includes("Fig. 17")) {
      return [
        f(1, "2", "B2*", { gnd: "B1", mide: "C(B2+B1)" }),
        f(2, "5", "B3*", { gnd: "B1", grd: "B2", mide: "C(B3+B1)" }),
        f(3, "5", "B3*", { gnd: "B1", ust: "B2", mide: "C(B3+B2)" }),
        f(4, "2", "B2*", { grd: "B3", mide: "Terminal B2" }),
        f(5, "5", "B3*", { grd: "B2", mide: "Terminal B3" }),
      ];
    }
    if (arreglo.includes("Fig. 18")) {
      return [
        f("1A", "10", "B1", { gnd: "T1", grd: "B3", mide: `C(T1-T2)` }),
        f("2A", "10", "B1", { gnd: "T1", ust: "B2", mide: c12 }),
        f("3A", "10", "B1", { gnd: "T1", ust: "B3", mide: `${c12} + ${c23}` }),
        f("4A", "5", "B3*", { gnd: "T1", ust: "B2", mide: "C(B3+B2)" }),
        f("5A", "2", "B2*", { grd: "B3", mide: "Terminal B2" }),
        f("6A", "5", "B3*", { grd: "B1, B2", mide: "Terminal B3" }),
      ];
    }
    if (arreglo.startsWith("Fig. 19 con")) {
      return [
        f("1A", "10", "B1*", { gnd: "B3", ust: "B2", mide: "C(B1+B2)" }),
        f("2A", "2", "B2*", { gnd: "B3", mide: "C(B2+B3)" }),
        f("3A", "2", "B2*", { grd: "B1", mide: "Terminal B2" }),
      ];
    }
    if (arreglo.includes("Fig. 19")) {
      return [
        f(1, "2", "B2*", { gnd: "B1", grd: "B3", mide: "C(B2+B1)" }),
        f(2, "2", "B2*", { gnd: "B1", ust: "B3", mide: "C(B2+B3)" }),
        f(3, "2", "B2*", { grd: "B1", mide: "Terminal B2" }),
      ];
    }
    if (arreglo.startsWith("Fig. 20 con")) {
      return [
        f(1, "10", "B1=T2", { gnd: "T1, B3", grd: "B2", mide: "C(T2+T1)" }),
        f(2, "10", "B1=T2", { gnd: "T1, B3", ust: "B2", mide: c12 }),
        f(3, "2", "B2*", { gnd: "T1, B3", grd: "B1=T2", mide: "C(B2+B3)" }),
        f(4, "2", "B2*", { grd: "B1=T2, B3", mide: "Terminal B2" }),
      ];
    }
    return [
      f(1, "10", "B1=T2", { gnd: "T1", grd: "B3", mide: "C(T1+T2)" }),
      f(2, "10", "B1=T2", { gnd: "T1", ust: "B2", mide: c12 }),
      f(3, "10", "B1=T2", { gnd: "T1", ust: "B3", mide: `${c12} + ${c23}` }),
      f(4, "5", "B3*", { gnd: "T1", ust: "B2", mide: "C(B3+B2)" }),
      f(5, "2", "B2*", { grd: "B3", mide: "Terminal B2" }),
      f(6, "5", "B3*", { grd: "B1=T2, B2", mide: "Terminal B3" }),
    ];
  }
  if (equipo === "Apartarrayos") {
    if (arreglo.includes("Una")) {
      return [f(1, "10", "1", { gnd: "2", mide: "C12" })];
    }
    if (arreglo.includes("Dos")) {
      return [
        f(1, "10", "1", { gnd: "2", mide: "A" }),
        f(2, "10", "2", { gnd: "3", mide: "B" }),
        f(3, "10", "1", { gnd: "3", mide: "A+B" }),
        f(4, "10", "2", { gnd: "3", ust: "1", mide: "A" }),
      ];
    }
    if (arreglo.includes("Tres")) {
      return [
        f(1, "10", "1", { gnd: "2", mide: "A" }),
        f(2, "10", "2", { gnd: "3", mide: "B" }),
        f(3, "10", "3", { gnd: "4", mide: "C" }),
        f(4, "10", "1", { ust: "4", mide: "A+B+C" }),
      ];
    }
    if (arreglo.includes("Cuatro")) {
      return [
        f(1, "10", "1", { gnd: "2", mide: "A" }),
        f(2, "10", "2", { gnd: "3", mide: "B" }),
        f(3, "10", "3", { gnd: "4", mide: "C" }),
        f(4, "10", "4", { gnd: "5", mide: "D" }),
        f(5, "10", "1", { gnd: "5", mide: "A+B+C+D" }),
      ];
    }
    return [
      f(1, "10", "2", { gnd: "1, 6", grd: "3", mide: "A" }),
      f(2, "10", "3", { gnd: "1, 2, 6", grd: "4", mide: "B" }),
      f(3, "10", "3", { gnd: "1, 2, 6", ust: "4", mide: "C" }),
      f(4, "10", "5", { gnd: "1, 6", ust: "4", mide: "D" }),
      f(5, "10", "5", { gnd: "1, 6", grd: "4", mide: "E" }),
    ];
  }
  if (equipo === "Cables de Potencia") {
    if (arreglo.includes("Trifásico")) {
      return [
        f(1, "10", "A", { gnd: "B+C", mide: "A" }),
        f(2, "10", "B", { gnd: "A+C", mide: "B" }),
        f(3, "10", "C", { gnd: "A+B", mide: "C" }),
        f(4, "10", "A+B+C", { gnd: "Pantalla", mide: "A+B+C" }),
      ];
    }
    return [f(1, "10", "Conductor", { gnd: "Pantalla", mide: "Aislamiento" })];
  }
  if (equipo === "Aceite Aislante") {
    return [f(1, "10", "HV", { grd: "Guarda", ust: "LV", mide: "Aceite" })];
  }
  return [];
}
