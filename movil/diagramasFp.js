// Diagrama de bloques para Factor de Potencia (ST-CT-002).
// Misma estructura que Resistencia de Aislamiento (diagramas.js): bus vertical
// a tierra con cajas de devanados apiladas — RA y FP comparten la topología
// real (SAPE_1._fp_generar_diagrama_* alimenta también el diagrama RA de estos
// equipos vía _ra_aplicar_simbolo_resistencia); la única diferencia es el
// símbolo entre bus/cajas: aquí capacitor en vez de resistencia en zigzag.
"use strict";

const COLOR_FP = {
  cable: "#059669",
  medido: "#EA580C",
  texto: "#065F46",
  LINEA: "#DC2626",
  TIERRA: "#DC2626",
  GUARDA: "#2563EB",
  UST: "#7C3AED",
};
const ROTULO_FP = { LINEA: "HV", TIERRA: "GROUND", GUARDA: "GUARDA", UST: "UST" };

function _escFp(t) {
  return String(t).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

// Bornes mencionados en un campo de la prueba ("H", "H+X", "S1, S2"...).
function _terminalesFp(texto) {
  if (!texto || texto === "-----" || texto === "—") return new Set();
  return new Set(
    String(texto).split(/[,+]|\sy\s/).map((t) => t.trim()).filter(Boolean),
  );
}

// Modelo de devanados apilados por equipo (ST-CT-002, familia de potencia):
// cajas + capacitores de bus (caja↔bus), entre (caja↔caja) y puente (bypass).
function _modeloPilaFp(equipoNombre, arreglo) {
  const caja = (titulo, id, sitios) => ({ titulo, id, sitios });
  if (equipoNombre === "Transformadores de 2 Devanados") {
    return {
      cajas: [caja("ALTA", "H", ["H"]), caja("BAJA", "X", ["X"])],
      bus: ["CH", "CX"], entre: ["CHX"],
    };
  }
  if (equipoNombre === "Transformadores de 3 Devanados") {
    return {
      cajas: [
        caja("ALTA", "H", ["H"]), caja("BAJA", "X", ["X"]),
        caja("TERCIARIO", "Y", ["Y"]),
      ],
      bus: ["CH", "CX", "CY"], entre: ["CHX", "CXY"], puente: "CHY",
    };
  }
  if (equipoNombre === "Autotransformadores") {
    if ((arreglo || "").startsWith("Terciario no accesible")) {
      return { cajas: [caja("ALTA-BAJA", "H+X", ["H", "X"])], bus: ["CH"], entre: [] };
    }
    return {
      cajas: [caja("ALTA-BAJA", "H+X", ["H", "X"]), caja("TERCIARIO", "Y", ["Y"])],
      bus: ["CH", "CY"], entre: ["CHY"],
    };
  }
  if (equipoNombre === "Reactores") {
    return { cajas: [caja("DEVANADO", "H", ["H"])], bus: ["CH"], entre: [] };
  }
  return null;
}

function _rolDeFp(sitios, roles) {
  for (const rol of ["LINEA", "TIERRA", "GUARDA", "UST"]) {
    if (sitios.some((s) => roles[rol].has(s))) return rol;
  }
  return null;
}

// Dibuja los devanados en cajas apiladas, bus vertical y tierra al fondo —
// transformadores, autotransformadores y reactores.
function _dibujarPilaFp(equipoNombre, arreglo, pr, modo) {
  const m = _modeloPilaFp(equipoNombre, arreglo);
  const conexiones = modo === "conexiones";
  const medidos = conexiones ? new Set() : _terminalesFp(pr.medicion);
  const roles = {
    LINEA: _terminalesFp(pr.hv), TIERRA: _terminalesFp(pr.ground),
    GUARDA: _terminalesFp(pr.guard), UST: _terminalesFp(pr.ust),
  };
  const rolDe = (sitios) => (conexiones ? _rolDeFp(sitios, roles) : null);

  const partes = [];
  const linea = (d, color, ancho, cap) =>
    partes.push(
      `<path d="${d}" fill="none" stroke="${color || COLOR_FP.cable}" stroke-width="${ancho || 3}" ` +
      `stroke-linecap="${cap || "round"}" stroke-linejoin="round"/>`
    );
  const texto = (x, y, t, o) => {
    o = o || {};
    partes.push(
      `<text x="${x}" y="${y}" text-anchor="${o.ancla || "middle"}" fill="${o.color || COLOR_FP.texto}" ` +
      `font-size="${o.tam || 12}" font-weight="700" class="${o.clase || ""}">${_escFp(t)}</text>`
    );
  };
  const tierra = (x, y) => {
    linea(`M${x - 14} ${y} H${x + 14} M${x - 9} ${y + 6} H${x + 9} M${x - 4} ${y + 12} H${x + 4}`, COLOR_FP.cable, 2.5);
    texto(x, y + 30, "GROUND", { color: "#DC2626" });
  };
  const rotuloTanque = (x) => {
    texto(x, 16, "TANQUE", { ancla: "middle" });
    if (!conexiones) return;
    if (roles.TIERRA.has("Tanque") || roles.TIERRA.has("TANQUE")) {
      texto(x + 36, 16, ROTULO_FP.TIERRA, { ancla: "start", color: "#DC2626", clase: "pulso" });
    }
  };
  // Capacitor con sus dos tramos de cable (con hueco real entre placas,
  // igual que el símbolo "cap" de _dibujarEsquemaFp); parpadea si se mide.
  const capacitor = (codigo, x0, y0, x1, y1, etiqueta) => {
    const medido = medidos.has(codigo);
    const color = medido ? COLOR_FP.medido : COLOR_FP.cable;
    const horizontal = y0 === y1;
    const largo = Math.hypot(x1 - x0, y1 - y0) || 1;
    const ux = (x1 - x0) / largo, uy = (y1 - y0) / largo;
    const mx = (x0 + x1) / 2, my = (y0 + y1) / 2;
    const hueco = 5, placa = 9;
    const cables = (
      `M${x0} ${y0} L${mx - ux * hueco} ${my - uy * hueco} ` +
      `M${mx + ux * hueco} ${my + uy * hueco} L${x1} ${y1}`
    );
    const placas = horizontal
      ? `M${mx - hueco} ${my - placa} V${my + placa} M${mx + hueco} ${my - placa} V${my + placa}`
      : `M${mx - placa} ${my - hueco} H${mx + placa} M${mx - placa} ${my + hueco} H${mx + placa}`;
    partes.push(
      `<g class="${medido ? "pulso" : ""}">` +
      `<path d="${cables}" fill="none" stroke="${color}" stroke-width="3" stroke-linecap="round"/>` +
      `<path d="${placas}" stroke="${color}" stroke-width="3" fill="none"/>` +
      `<text x="${etiqueta.x}" y="${etiqueta.y}" text-anchor="${etiqueta.ancla || "middle"}" fill="${color}" font-size="11" font-weight="700">${_escFp(codigo)}</text>` +
      `</g>`
    );
  };
  const cajaSvg = (c, x, y, w, h) => {
    const rol = rolDe(c.sitios);
    const color = rol ? COLOR_FP[rol] : COLOR_FP.cable;
    partes.push(`<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="7" fill="#FFFFFF" stroke="${color}" stroke-width="3"/>`);
    if (rol) {
      texto(x + w / 2, y + h / 2 - 3, c.id, { tam: 10, color: "#64748B" });
      texto(x + w / 2, y + h / 2 + 12, ROTULO_FP[rol], { color: rol === "LINEA" ? "#111827" : color, clase: "pulso" });
    } else {
      texto(x + w / 2, y + h / 2 + 4, c.titulo);
    }
  };

  const BUS = 46, CX = 150, CW = 120, CH = 46, PASO = 104, Y0 = 34;
  const n = m.cajas.length;
  const fondo = Y0 + (n - 1) * PASO + CH + 34;
  let ancho = 300;

  rotuloTanque(BUS);
  linea(`M${BUS} 26 V${fondo}`, COLOR_FP.cable, 3.5, "butt");
  tierra(BUS, fondo);
  m.cajas.forEach((c, i) => {
    const y = Y0 + i * PASO;
    const cy = y + CH / 2;
    capacitor(m.bus[i], BUS, cy, CX, cy, { x: (BUS + CX) / 2, y: cy + 22 });
    if (i < n - 1) {
      capacitor(
        m.entre[i], CX + CW / 2, y + CH, CX + CW / 2, y + PASO,
        { x: CX + CW / 2 + 14, y: y + CH + (PASO - CH) / 2 + 4, ancla: "start" },
      );
    }
  });
  if (m.puente) {
    const px = CX + CW + 56;
    const y1 = Y0 + CH / 2;
    const y2 = Y0 + (n - 1) * PASO + CH / 2;
    linea(`M${CX + CW} ${y1} H${px} M${CX + CW} ${y2} H${px}`);
    capacitor(m.puente, px, y1, px, y2, { x: px + 12, y: (y1 + y2) / 2 + 4, ancla: "start" });
    ancho = px + 56;
  }
  m.cajas.forEach((c, i) => cajaSvg(c, CX, Y0 + i * PASO, CW, CH));
  const alto = fondo + 40;

  return (
    `<svg viewBox="0 0 ${ancho} ${alto}" xmlns="http://www.w3.org/2000/svg" role="img" ` +
    `aria-label="Diagrama de ${conexiones ? "conexiones" : "medición"}" ` +
    `style="max-height:${Math.round(alto * 1.25)}px">${partes.join("")}</svg>`
  );
}

// Esquema propio de capacitancias — calco exacto de SAPE2._topologia_fp /
// _dibujar_esquema_fp (el que usa el programa de PC para TCs, TPs, TPCs,
// Apartarrayos, Cables y Aceite: no tienen devanados apilados, van en un
// esquema de nodos y capacitores con sus propias coordenadas).
const COLOR_ROL_FP = {
  HV: ["#111827", "#FFFFFF"],
  GROUND: ["#EF4444", "#FFFFFF"],
  GUARD: ["#2563EB", "#FFFFFF"],
  UST: ["#0891B2", "#FFFFFF"],
  FLOTANDO: ["#94A3B8", "#FFFFFF"],
};

function _topologiaFp(equipo, arreglo) {
  arreglo = arreglo || "";
  const nodo = (etiqueta, x, y, propias) => [etiqueta, x, y, propias];

  if (equipo === "Transformadores de Corriente - TCs") {
    const secundario = arreglo.includes("Fig. 21")
      ? ["S1 - S4", ["S1", "S2", "S3", "S4"]]
      : ["S1 - S2", ["S1", "S2"]];
    return {
      nodos: { P: nodo("P1 - P2", 1, 0, ["P1", "P2"]), S: nodo(secundario[0], 4, 0, secundario[1]) },
      elementos: [
        ["cap", "CP", "P", [1, 2.4]],
        ["cap", "CS", "S", [4, 2.4]],
        ["cable", [1, 2.4], [4, 2.4]],
        ["tierra", [2.5, 2.4]],
      ],
    };
  }
  if (equipo === "Transformadores de Potencial - TPs") {
    if (arreglo.includes("Fig. 14")) {
      return {
        nodos: { H1: nodo("H1", 1, 0, ["H1"]), H0: nodo("H0", 1, 3, ["H0"]), XY: nodo("X1 - Y1", 3.6, 1.5, ["X1", "Y1"]) },
        elementos: [
          ["bobina", "DEVANADO", "H1", "H0"],
          ["cap", "CHX", [1, 1.5], "XY"],
          ["cable", "H0", [1, 4.1]],
          ["tierra", [1, 4.1]],
        ],
      };
    }
    if (arreglo.includes("Fig. 16")) {
      return {
        nodos: {
          H1: nodo("H1", 1, 0, ["H1"]), H0: nodo("H0", 1, 3, ["H0"]),
          XY: nodo("X1-X3 · Y1-Y3", 3.8, 1.5, ["X1-X3", "Y1-Y3", "X1", "X2", "X3", "Y1", "Y2", "Y3"]),
        },
        elementos: [
          ["bobina", "DEVANADO", "H1", "H0"],
          ["cap", "C", [1, 1.5], "XY"],
          ["cable", "XY", [3.8, 2.6]],
          ["tierra", [3.8, 2.6]],
        ],
      };
    }
    return {
      nodos: { H1: nodo("H1", 1, 0, ["H1"]), H2: nodo("H2", 1, 3, ["H2"]), X1: nodo("X1", 3.6, 1.5, ["X1"]) },
      elementos: [
        ["bobina", "DEVANADO", "H1", "H2"],
        ["cap", "CHX", [1, 1.5], "X1"],
        ["cap", "CH", [1, 1.5], [-0.8, 1.5]],
        ["cable", [-0.8, 1.5], [-0.8, 2.4]],
        ["tierra", [-0.8, 2.4]],
      ],
    };
  }
  if (equipo === "Transformadores de Potencial Capacitivo - TPCs") {
    if (arreglo.includes("Fig. 18") || arreglo.includes("Fig. 20")) {
      const union = arreglo.includes("Fig. 20")
        ? ["B1 = T2", ["B1", "T2", "B1=T2"]]
        : ["B1", ["B1"]];
      return {
        nodos: {
          T1: nodo("T1", 1, 0, ["T1"]), B1: nodo(union[0], 1, 2, union[1]),
          B2: nodo("B2", 1, 4, ["B2"]), B3: nodo("B3", 1, 6, ["B3"]),
        },
        elementos: [
          ["cap", "C(T1-T2)", "T1", "B1"],
          ["cap", "C(B1-B2)", "B1", "B2"],
          ["cap", "C(B2-B3)", "B2", "B3"],
          ["cap", "Term. B2", "B2", [3.8, 4]],
          ["cap", "Term. B3", "B3", [3.8, 6]],
          ["cable", [3.8, 4], [3.8, 6.9]],
          ["tierra", [3.8, 6.9]],
        ],
      };
    }
    return {
      nodos: { B1: nodo("B1", 1, 0, ["B1"]), B2: nodo("B2", 1, 2.2, ["B2"]), B3: nodo("B3", 1, 4.4, ["B3"]) },
      elementos: [
        ["cap", "C(B1-B2)", "B1", "B2"],
        ["cap", "C(B2-B3)", "B2", "B3"],
        ["cap", "Term. B2", "B2", [3.8, 2.2]],
        ["cap", "Term. B3", "B3", [3.8, 4.4]],
        ["cable", [3.8, 2.2], [3.8, 5.3]],
        ["tierra", [3.8, 5.3]],
      ],
    };
  }
  if (equipo === "Apartarrayos") {
    let secciones = 1;
    for (const [palabra, numero] of [["Dos", 2], ["Tres", 3], ["Cuatro", 4], ["Cinco", 5]]) {
      if (arreglo.includes(palabra)) secciones = numero;
    }
    const paso = 1.7;
    const nodos = {};
    for (let i = 0; i <= secciones; i++) {
      nodos[String(i + 1)] = nodo(String(i + 1), 1, i * paso, [String(i + 1)]);
    }
    const letras = "ABCDE";
    const elementos = [];
    for (let i = 0; i < secciones; i++) {
      elementos.push(["cap", secciones === 1 ? "C12" : letras[i], String(i + 1), String(i + 2)]);
    }
    const fondo = secciones * paso + 1.0;
    elementos.push(["cable", String(secciones + 1), [1, fondo]], ["tierra", [1, fondo]]);
    return { nodos, elementos };
  }
  if (equipo === "Cables de Potencia") {
    if (arreglo.includes("Trifásico")) {
      return {
        nodos: {
          A: nodo("A", 0, 0, ["A"]), B: nodo("B", 1.5, 0, ["B"]), C: nodo("C", 3, 0, ["C"]),
          PANT: nodo("Pantalla", 4.6, 2.4, ["Pantalla"]),
        },
        elementos: [
          ["cap", "A", "A", [0, 2.4]],
          ["cap", "B", "B", [1.5, 2.4]],
          ["cap", "C", "C", [3, 2.4]],
          ["cable", [0, 2.4], "PANT"],
          ["cable", "PANT", [4.6, 3.4]],
          ["tierra", [4.6, 3.4]],
        ],
      };
    }
    return {
      nodos: { COND: nodo("Conductor", 1, 0, ["Conductor"]), PANT: nodo("Pantalla", 1, 2.4, ["Pantalla"]) },
      elementos: [
        ["cap", "C", "COND", "PANT"],
        ["cable", "PANT", [1, 3.4]],
        ["tierra", [1, 3.4]],
      ],
    };
  }
  if (equipo === "Aceite Aislante") {
    return {
      nodos: {
        HV: nodo("Electrodo HV", 0.5, 0, ["HV"]), LV: nodo("Electrodo LV", 4.5, 0, ["LV"]),
        G: nodo("Anillo de guarda", 2.5, 2.0, ["Guarda"]),
      },
      elementos: [["cap", "ACEITE", "HV", "LV"]],
    };
  }
  return null;
}

// Rol de cada nodo en la prueba; el cable de alta manda sobre los demás.
function _rolesEsquemaFp(topo, pr) {
  const roles = {};
  for (const [rol, campo] of [
    ["FLOTANDO", "flotando"], ["UST", "ust"], ["GUARD", "guard"],
    ["GROUND", "ground"], ["HV", "hv"],
  ]) {
    const terminales = _terminalesFp(pr[campo]);
    for (const clave of Object.keys(topo.nodos)) {
      const propias = topo.nodos[clave][3];
      if (propias.some((t) => terminales.has(t))) roles[clave] = rol;
    }
  }
  return roles;
}

// Esquema de capacitancias de la prueba: cable, tierra, bobina (devanado) y
// capacitor, con los nodos como cajas, igual que en SAPE2 (_dibujar_esquema_fp).
function _dibujarEsquemaFp(topo, pr, modo) {
  const conexiones = modo === "conexiones";
  const pasoX = 72, pasoY = 62, margenX = 64, margenY = 56;
  const nodos = topo.nodos;
  const coord = (ref) => (typeof ref === "string" ? [nodos[ref][1], nodos[ref][2]] : ref);

  const puntos = Object.values(nodos).map((n) => [n[1], n[2]]);
  topo.elementos.forEach((el) => {
    for (let i = 1; i < el.length; i++) {
      const ref = el[i];
      if (Array.isArray(ref)) puntos.push(ref);
      else if (nodos[ref]) puntos.push(coord(ref));
    }
  });
  const minX = Math.min(...puntos.map((p) => p[0]));
  const maxX = Math.max(...puntos.map((p) => p[0]));
  const minY = Math.min(...puntos.map((p) => p[1]));
  const maxY = Math.max(...puntos.map((p) => p[1]));
  const ancho = (maxX - minX) * pasoX + margenX * 2 + 40;
  const alto = (maxY - minY) * pasoY + margenY * 2;
  const px = (ref) => {
    const [x, y] = coord(ref);
    return [margenX + (x - minX) * pasoX, margenY + (y - minY) * pasoY];
  };

  const medidasRaw = conexiones ? new Set() : _terminalesFp(pr.medicion);
  const medidas = { has: (etiqueta) => medidasRaw.has(etiqueta) || [...medidasRaw].some((m) => m.toUpperCase() === String(etiqueta).toUpperCase()) };
  const partes = [];
  const texto = (x, y, t, o) => {
    o = o || {};
    partes.push(
      `<text x="${x}" y="${y}" text-anchor="${o.ancla || "middle"}" fill="${o.color || COLOR_FP.cable}" ` +
      `font-size="${o.tam || 11}" font-weight="700" class="${o.clase || ""}">${_escFp(t)}</text>`
    );
  };
  const trazo = (x1, y1, x2, y2, medido, grosor) => {
    const color = medido ? COLOR_FP.medido : COLOR_FP.cable;
    const g = `<path d="M${x1} ${y1} L${x2} ${y2}" fill="none" stroke="${color}" stroke-width="${grosor || (medido ? 4 : 2)}" stroke-linecap="round"/>`;
    partes.push(medido ? `<g class="pulso">${g}</g>` : g);
  };

  texto(18, 16, conexiones ? "CONEXIONES" : "MEDICIÓN", { ancla: "start", color: "#047857", tam: 13 });

  topo.elementos.forEach((el) => {
    const tipo = el[0];
    if (tipo === "cable") {
      const [[x1, y1], [x2, y2]] = [px(el[1]), px(el[2])];
      trazo(x1, y1, x2, y2);
    } else if (tipo === "tierra") {
      const [x, y] = px(el[1]);
      [16, 10, 4].forEach((medio, i) => {
        partes.push(`<path d="M${x - medio} ${y + i * 6} H${x + medio}" stroke="${COLOR_FP.cable}" stroke-width="3" fill="none"/>`);
      });
      texto(x, y + 30, "GROUND", { tam: 9, color: "#DC2626" });
    } else if (tipo === "bobina") {
      const [, etiqueta, a, b] = el;
      const [[x1, y1], [x2, y2]] = [px(a), px(b)];
      const medido = medidas.has(etiqueta);
      const largo = Math.hypot(x2 - x1, y2 - y1) || 1;
      const ux = (x2 - x1) / largo, uy = (y2 - y1) / largo;
      let d = `M${x1} ${y1}`;
      for (let k = 1; k <= 60; k++) {
        const t = k / 60;
        const desvio = 8 * Math.sin(t * Math.PI * 12);
        d += ` L${x1 + (x2 - x1) * t - uy * desvio} ${y1 + (y2 - y1) * t + ux * desvio}`;
      }
      const color = medido ? COLOR_FP.medido : COLOR_FP.cable;
      const g = `<path d="${d}" fill="none" stroke="${color}" stroke-width="${medido ? 4 : 2}" stroke-linejoin="round"/>`;
      partes.push(medido ? `<g class="pulso">${g}</g>` : g);
    } else if (tipo === "cap") {
      const [, etiqueta, a, b] = el;
      const [[x1, y1], [x2, y2]] = [px(a), px(b)];
      const medido = medidas.has(etiqueta);
      const largo = Math.hypot(x2 - x1, y2 - y1) || 1;
      const ux = (x2 - x1) / largo, uy = (y2 - y1) / largo;
      const mx = (x1 + x2) / 2, my = (y1 + y2) / 2;
      const hueco = 5, placa = 14;
      const trozos = [];
      trozos.push(`M${x1} ${y1} L${mx - ux * hueco} ${my - uy * hueco}`);
      trozos.push(`M${mx + ux * hueco} ${my + uy * hueco} L${x2} ${y2}`);
      for (const signo of [-1, 1]) {
        const cx = mx + signo * ux * hueco, cy = my + signo * uy * hueco;
        trozos.push(`M${cx + uy * placa} ${cy - ux * placa} L${cx - uy * placa} ${cy + ux * placa}`);
      }
      const color = medido ? COLOR_FP.medido : COLOR_FP.cable;
      const g = (
        `<path d="${trozos[0]} ${trozos[1]}" fill="none" stroke="${color}" stroke-width="${medido ? 4 : 2}" stroke-linecap="round"/>` +
        `<path d="${trozos[2]} ${trozos[3]}" fill="none" stroke="${color}" stroke-width="${medido ? 5 : 3}" stroke-linecap="round"/>`
      );
      const horizontal = Math.abs(ux) > Math.abs(uy);
      const lblX = horizontal ? mx : mx + placa + 8;
      const lblY = horizontal ? my - placa - 10 : my + 4;
      const lbl = `<text x="${lblX}" y="${lblY}" text-anchor="${horizontal ? "middle" : "start"}" fill="${color}" font-size="11" font-weight="700">${_escFp(etiqueta)}</text>`;
      partes.push(medido ? `<g class="pulso">${g}${lbl}</g>` : `${g}${lbl}`);
    }
  });

  const roles = conexiones ? _rolesEsquemaFp(topo, pr) : {};
  Object.keys(nodos).forEach((clave) => {
    const [etiqueta] = nodos[clave];
    const [x, y] = px(clave);
    const rol = roles[clave];
    const texto2 = rol ? `${etiqueta}  ·  ${ROTULO_FP[rol] || rol}` : etiqueta;
    const medio = Math.max(34, texto2.length * 3.4 + 12);
    const [relleno, tinta] = rol ? (COLOR_ROL_FP[rol] || ["#FFFFFF", "#0F172A"]) : ["#FFFFFF", "#0F172A"];
    const borde = rol ? relleno : COLOR_FP.cable;
    const caja = (
      `<rect x="${x - medio}" y="${y - 16}" width="${medio * 2}" height="32" rx="7" fill="${relleno}" stroke="${borde}" stroke-width="2"/>` +
      `<text x="${x}" y="${y + 4}" text-anchor="middle" fill="${tinta}" font-size="10" font-weight="700">${_escFp(texto2)}</text>`
    );
    partes.push(rol ? `<g class="pulso">${caja}</g>` : caja);
  });

  return (
    `<svg viewBox="0 0 ${ancho} ${alto}" xmlns="http://www.w3.org/2000/svg" font-family="Consolas, 'Courier New', monospace">${partes.join("")}</svg>`
  );
}

// Diagrama genérico (una caja) — respaldo si un equipo no tiene topología
// de devanados apilados ni esquema propio definido arriba.
function _dibujarGenericoFp(equipoNombre, pr) {
  const partes = [];
  const linea = (d, color, ancho, cap, punteada) =>
    partes.push(
      `<path d="${d}" fill="none" stroke="${color}" stroke-width="${ancho || 2.5}" ` +
      `stroke-linecap="${cap || "round"}" stroke-linejoin="round"${punteada ? ` stroke-dasharray="${punteada}"` : ""}/>`
    );
  const texto = (x, y, t, o) => {
    o = o || {};
    partes.push(
      `<text x="${x}" y="${y}" text-anchor="${o.ancla || "middle"}" fill="${o.color || "#1E293B"}" ` +
      `font-size="${o.tam || 11}" font-weight="${o.peso || 700}" class="${o.clase || ""}">${_escFp(t)}</text>`
    );
  };
  const punto = (x, y, color, r) => partes.push(`<circle cx="${x}" cy="${y}" r="${r || 4}" fill="${color}"/>`);
  const puntoHueco = (x, y, color) => partes.push(`<circle cx="${x}" cy="${y}" r="4.5" fill="#FFFFFF" stroke="${color}" stroke-width="2.5"/>`);

  const cx = 175, cyBox = 112, bw = 118, bh = 56;
  const bx0 = cx - bw / 2, bx1 = cx + bw / 2, by0 = cyBox - bh / 2, by1 = cyBox + bh / 2;
  const llevaGnd = pr.ground && pr.ground !== "-----";
  const llevaGuard = pr.guard && pr.guard !== "-----";
  const llevaUst = pr.ust && pr.ust !== "-----";

  partes.push(`<rect x="${bx0}" y="${by0}" width="${bw}" height="${bh}" rx="8" fill="#FFFFFF" stroke="${COLOR_FP.cable}" stroke-width="2.5"/>`);
  texto(cx, cyBox - 4, equipoNombre.length > 26 ? equipoNombre.slice(0, 24) + "…" : equipoNombre, { tam: 10, color: "#334155" });
  texto(cx, cyBox + 13, pr.medicion || "—", { tam: 11, color: COLOR_FP.texto });

  const gx = 36, gy = 34, gw = 70, gh = 30;
  partes.push(`<rect x="${gx}" y="${gy}" width="${gw}" height="${gh}" rx="6" fill="#111827"/>`);
  texto(gx + gw / 2, gy + 13, "GENERADOR", { tam: 8, color: "#D1FAE5" });
  texto(gx + gw / 2, gy + 24, pr.modo || "—", { tam: 9, color: "#6EE7B7" });

  linea(`M${gx + gw} ${gy + gh / 2} H${cx} V${by0}`, COLOR_FP.medido, 4);
  punto(cx, by0, COLOR_FP.medido);
  texto(cx + 10, by0 - 10, `HV ${pr.hv || "—"}`, { ancla: "start", color: "#111827", tam: 10, clase: "pulso" });

  if (llevaGnd) {
    const yFondo = by1 + 42;
    linea(`M${cx} ${by1} V${yFondo}`, COLOR_FP.medido, 4, "butt");
    linea(`M${cx - 14} ${yFondo} H${cx + 14} M${cx - 9} ${yFondo + 6} H${cx + 9} M${cx - 4} ${yFondo + 12} H${cx + 4}`, COLOR_FP.TIERRA, 2.5);
    texto(cx, yFondo + 28, `GROUND ${pr.ground}`, { tam: 10, color: "#DC2626", clase: "pulso" });
  }
  if (llevaGuard) {
    const gxp = bx1 + 60, gyp = cyBox;
    linea(`M${bx1} ${cyBox} H${gxp}`, COLOR_FP.GUARDA, 2.5, "round", "2,4");
    puntoHueco(gxp, gyp, COLOR_FP.GUARDA);
    texto(gxp, gyp - 12, "GUARDA", { color: COLOR_FP.GUARDA, tam: 9 });
    texto(gxp, gyp + 18, pr.guard, { color: COLOR_FP.GUARDA, tam: 10 });
  }
  if (llevaUst) {
    const uxp = bx0 - 60, uyp = by1 + 10;
    linea(`M${bx0} ${by1 - 8} L${uxp} ${uyp}`, COLOR_FP.UST, 2.5, "round", "1,5");
    puntoHueco(uxp, uyp, COLOR_FP.UST);
    texto(uxp, uyp + 16, "UST", { color: COLOR_FP.UST, tam: 9 });
    texto(uxp, uyp + 32, pr.ust, { color: COLOR_FP.UST, tam: 10 });
  }
  if (pr.flotando) texto(cx, by0 - 26, `FLOTA: ${pr.flotando}`, { color: "#B45309", tam: 9 });

  const alto = Math.max(260, llevaGnd ? by1 + 90 : by1 + 40);
  return `<svg viewBox="0 0 350 ${alto}" xmlns="http://www.w3.org/2000/svg" font-family="Consolas, 'Courier New', monospace">${partes.join("")}</svg>`;
}

function dibujarDiagramaFp(d, pr, modo) {
  const pila = _modeloPilaFp(d.equipo, d.arreglo);
  if (pila) return _dibujarPilaFp(d.equipo, d.arreglo, pr, modo);
  const topo = _topologiaFp(d.equipo, d.arreglo);
  if (topo) return _dibujarEsquemaFp(topo, pr, modo);
  return _dibujarGenericoFp(d.equipo, pr);
}
