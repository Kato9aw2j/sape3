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
  TIERRA: "#111111",
  GUARDA: "#2563EB",
  UST: "#7C3AED",
};
const ROTULO_FP = { LINEA: "HV", TIERRA: "TIERRA", GUARDA: "GUARDA", UST: "UST" };

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
    texto(x, y + 30, "TIERRA");
  };
  const rotuloTanque = (x) => {
    texto(x, 16, "TANQUE", { ancla: "middle" });
    if (!conexiones) return;
    if (roles.TIERRA.has("Tanque") || roles.TIERRA.has("TANQUE")) {
      texto(x + 36, 16, ROTULO_FP.TIERRA, { ancla: "start", color: COLOR_FP.TIERRA, clase: "pulso" });
    }
  };
  // Capacitor con sus dos tramos de cable; parpadea si es el que se mide.
  const capacitor = (codigo, x0, y0, x1, y1, etiqueta) => {
    const medido = medidos.has(codigo);
    const color = medido ? COLOR_FP.medido : COLOR_FP.cable;
    const horizontal = y0 === y1;
    const mx = (x0 + x1) / 2, my = (y0 + y1) / 2;
    const placas = horizontal
      ? `M${mx - 4} ${my - 9} V${my + 9} M${mx + 4} ${my - 9} V${my + 9}`
      : `M${mx - 9} ${my - 4} H${mx + 9} M${mx - 9} ${my + 4} H${mx + 9}`;
    partes.push(
      `<g class="${medido ? "pulso" : ""}">` +
      `<path d="M${x0} ${y0} L${x1} ${y1}" fill="none" stroke="${color}" stroke-width="3" stroke-linecap="round"/>` +
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
      texto(x + w / 2, y + h / 2 + 12, ROTULO_FP[rol], { color, clase: "pulso" });
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

// Diagrama genérico (una caja) para los equipos sin topología de devanados
// apilados: TCs, TPs, TPCs, apartarrayos, cables, aceite.
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
  texto(cx + 10, by0 - 10, `HV ${pr.hv || "—"}`, { ancla: "start", color: COLOR_FP.LINEA, tam: 10, clase: "pulso" });

  if (llevaGnd) {
    const yFondo = by1 + 42;
    linea(`M${cx} ${by1} V${yFondo}`, COLOR_FP.medido, 4, "butt");
    linea(`M${cx - 14} ${yFondo} H${cx + 14} M${cx - 9} ${yFondo + 6} H${cx + 9} M${cx - 4} ${yFondo + 12} H${cx + 4}`, COLOR_FP.TIERRA, 2.5);
    texto(cx, yFondo + 28, `TIERRA ${pr.ground}`, { tam: 10, color: COLOR_FP.TIERRA, clase: "pulso" });
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
  return _dibujarGenericoFp(d.equipo, pr);
}
