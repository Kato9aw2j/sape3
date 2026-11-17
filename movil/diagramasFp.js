// Diagrama de bloques para Factor de Potencia (ST-CT-002), estilo igual al
// de Resistencia de Aislamiento (diagramas.js): un esquema real, no solo
// chips de texto. Un solo layout genérico que se adapta a cualquier equipo,
// porque ST-CT-002 cubre demasiadas topologías (transformadores, TCs, TPs,
// TPCs, apartarrayos, cables, aceite) para dibujar cada una a mano aquí.
"use strict";

const COLOR_FP = {
  hv: "#DC2626",
  gnd: "#111111",
  guard: "#2563EB",
  ust: "#7C3AED",
  cable: "#059669",
  medido: "#EA580C",
  texto: "#065F46",
};

function dibujarDiagramaFp(equipoNombre, pr, modo) {
  const conexiones = modo === "conexiones";
  const medido = !conexiones;
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
      `font-size="${o.tam || 11}" font-weight="${o.peso || 700}" class="${o.clase || ""}">${String(t).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")}</text>`
    );
  };
  const punto = (x, y, color, r) =>
    partes.push(`<circle cx="${x}" cy="${y}" r="${r || 4}" fill="${color}"/>`);
  const puntoHueco = (x, y, color) =>
    partes.push(`<circle cx="${x}" cy="${y}" r="4.5" fill="#FFFFFF" stroke="${color}" stroke-width="2.5"/>`);

  const cx = 175, cyBox = 112, bw = 118, bh = 56;
  const bx0 = cx - bw / 2, bx1 = cx + bw / 2, by0 = cyBox - bh / 2, by1 = cyBox + bh / 2;

  const llevaGnd = pr.ground && pr.ground !== "-----";
  const llevaGuard = pr.guard && pr.guard !== "-----";
  const llevaUst = pr.ust && pr.ust !== "-----";

  // Equipo bajo prueba.
  partes.push(`<rect x="${bx0}" y="${by0}" width="${bw}" height="${bh}" rx="8" fill="#FFFFFF" stroke="${COLOR_FP.cable}" stroke-width="2.5"/>`);
  texto(cx, cyBox - 4, equipoNombre.length > 26 ? equipoNombre.slice(0, 24) + "…" : equipoNombre, { tam: 10, color: "#334155", peso: 700 });
  texto(cx, cyBox + 13, pr.medicion || "—", { tam: 11, color: COLOR_FP.texto });

  // Generador / equipo de prueba (arriba-izquierda), conectado a HV.
  const gx = 36, gy = 34, gw = 70, gh = 30;
  partes.push(`<rect x="${gx}" y="${gy}" width="${gw}" height="${gh}" rx="6" fill="#111827" />`);
  texto(gx + gw / 2, gy + 13, "GENERADOR", { tam: 8, color: "#D1FAE5", peso: 700 });
  texto(gx + gw / 2, gy + 24, pr.modo || "—", { tam: 9, color: "#6EE7B7", peso: 700 });

  // HV: del generador al punto de excitación arriba del equipo.
  const hvMide = medido;
  linea(`M${gx + gw} ${gy + gh / 2} H${cx} V${by0}`, hvMide ? COLOR_FP.medido : COLOR_FP.hv, hvMide ? 4 : 3);
  punto(cx, by0, hvMide ? COLOR_FP.medido : COLOR_FP.hv);
  texto(cx + 10, by0 - 10, `HV ${pr.hv || "—"}`, { ancla: "start", color: COLOR_FP.hv, tam: 10, clase: hvMide ? "pulso" : "" });

  // GND: abajo del equipo, con símbolo de tierra.
  if (llevaGnd) {
    const gndMide = medido;
    const yFondo = by1 + 42;
    linea(`M${cx} ${by1} V${yFondo}`, gndMide ? COLOR_FP.medido : COLOR_FP.gnd, gndMide ? 4 : 3, "butt");
    linea(`M${cx - 14} ${yFondo} H${cx + 14} M${cx - 9} ${yFondo + 6} H${cx + 9} M${cx - 4} ${yFondo + 12} H${cx + 4}`, gndMide ? COLOR_FP.medido : COLOR_FP.gnd, 2.5);
    texto(cx, yFondo + 28, `TIERRA ${pr.ground}`, { tam: 10, color: COLOR_FP.gnd, clase: gndMide ? "pulso" : "" });
  }

  // GUARD: a la derecha, línea punteada (excluye esa parte de la medición).
  if (llevaGuard) {
    const gxp = bx1 + 60, gyp = cyBox;
    linea(`M${bx1} ${cyBox} H${gxp}`, COLOR_FP.guard, 2.5, "round", "2,4");
    puntoHueco(gxp, gyp, COLOR_FP.guard);
    texto(gxp, gyp - 12, "GUARDA", { color: COLOR_FP.guard, tam: 9 });
    texto(gxp, gyp + 18, pr.guard, { color: COLOR_FP.guard, tam: 10 });
  }

  // UST: debajo a la izquierda, terminal flotante (sin conexión).
  if (llevaUst) {
    const uxp = bx0 - 60, uyp = by1 + 10;
    linea(`M${bx0} ${by1 - 8} L${uxp} ${uyp}`, COLOR_FP.ust, 2.5, "round", "1,5");
    puntoHueco(uxp, uyp, COLOR_FP.ust);
    texto(uxp, uyp + 16, "UST", { color: COLOR_FP.ust, tam: 9 });
    texto(uxp, uyp + 32, pr.ust, { color: COLOR_FP.ust, tam: 10 });
  }

  // Flotando (autotransformadores con un devanado sin conectar).
  if (pr.flotando) {
    texto(cx, by0 - 26, `FLOTA: ${pr.flotando}`, { color: "#B45309", tam: 9 });
  }

  const alto = Math.max(260, (llevaGnd ? by1 + 90 : by1 + 40));
  return `<svg viewBox="0 0 350 ${alto}" xmlns="http://www.w3.org/2000/svg" font-family="Consolas, 'Courier New', monospace">${partes.join("")}</svg>`;
}
