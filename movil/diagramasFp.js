// Diagrama de bloques para Factor de Potencia (ST-CT-002), con el mismo
// lenguaje visual que Resistencia de Aislamiento (diagramas.js): devanados
// en cajas apiladas sobre un bus a tierra, no una sola caja genérica.
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

// Rol de un devanado (por su id, p.ej. "H", "H+X") en la prueba actual.
// HV manda sobre los demás, igual que en SAPE2 (_roles_esquema_fp).
function _rolDevanadoFp(id, pr) {
  const en = (campo) => _terminalesFp(pr[campo]).has(id);
  if (en("hv")) return "hv";
  if (en("ground")) return "gnd";
  if (en("guard")) return "guard";
  if (en("ust")) return "ust";
  return null;
}

// Configuración de devanados por equipo (ST-CT-002, familia de potencia).
function _devanadosFp(equipoNombre, arreglo) {
  if (equipoNombre === "Transformadores de 2 Devanados") {
    return [{ id: "H", nombre: "ALTA" }, { id: "X", nombre: "BAJA" }];
  }
  if (equipoNombre === "Transformadores de 3 Devanados") {
    return [
      { id: "H", nombre: "ALTA" }, { id: "X", nombre: "BAJA" },
      { id: "Y", nombre: "TERCIARIO" },
    ];
  }
  if (equipoNombre === "Autotransformadores") {
    const lista = [{ id: "H+X", nombre: "ALTA-BAJA" }];
    if (!(arreglo || "").startsWith("Terciario no accesible")) {
      lista.push({ id: "Y", nombre: "TERCIARIO" });
    }
    return lista;
  }
  if (equipoNombre === "Reactores") {
    return [{ id: "H", nombre: "DEVANADO" }];
  }
  return null;
}

// Dibuja los devanados en cajas apiladas, bus vertical y tierra al fondo —
// transformadores, autotransformadores y reactores.
function _dibujarPilaFp(equipoNombre, arreglo, pr) {
  const devanados = _devanadosFp(equipoNombre, arreglo);
  const BUS = 150, CW = 118, CH = 48, PASO = 84, Y0 = 36;
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
      `font-size="${o.tam || 10}" font-weight="${o.peso || 700}" class="${o.clase || ""}">${_escFp(t)}</text>`
    );
  };
  const capacitor = (x, y, color, vertical) => {
    // Dos placas paralelas cortas: símbolo de capacitor sobre el bus.
    if (vertical) {
      partes.push(`<path d="M${x - 9} ${y - 4} H${x + 9} M${x - 9} ${y + 4} H${x + 9}" stroke="${color}" stroke-width="2.5" fill="none"/>`);
    } else {
      partes.push(`<path d="M${x - 4} ${y - 9} V${y + 9} M${x + 4} ${y - 9} V${y + 9}" stroke="${color}" stroke-width="2.5" fill="none"/>`);
    }
  };

  const fondo = Y0 + (devanados.length - 1) * PASO + CH + 60;
  // Bus vertical de arriba (generador) hasta el tanque/tierra.
  const yTop = 20;
  linea(`M${BUS} ${yTop} V${fondo}`, COLOR_FP.cable, 3, "butt");

  // Generador arriba.
  const gx = BUS - 40, gy = yTop - 34, gw = 80, gh = 26;
  partes.push(`<rect x="${gx}" y="${gy}" width="${gw}" height="${gh}" rx="6" fill="#111827"/>`);
  texto(gx + gw / 2, gy + 11, "GENERADOR", { tam: 7.5, color: "#D1FAE5" });
  texto(gx + gw / 2, gy + 21, pr.modo || "—", { tam: 8.5, color: "#6EE7B7" });

  let yHv = null, yGnd = fondo;
  devanados.forEach((dev, i) => {
    const y = Y0 + i * PASO + CH / 2;
    const rol = _rolDevanadoFp(dev.id, pr);
    if (rol === "hv") yHv = y;
    if (rol === "gnd") yGnd = Math.min(yGnd, y);

    const colorBorde = rol === "hv" ? COLOR_FP.hv
      : rol === "gnd" ? COLOR_FP.gnd
      : rol === "guard" ? COLOR_FP.guard
      : rol === "ust" ? COLOR_FP.ust
      : "#94A3B8";
    const bx0 = BUS + 46, bx1 = bx0 + CW;
    // Caja del devanado.
    partes.push(`<rect x="${bx0}" y="${y - CH / 2}" width="${CW}" height="${CH}" rx="7" fill="#FFFFFF" stroke="${colorBorde}" stroke-width="2.5"/>`);
    texto(bx0 + CW / 2, y - 3, dev.nombre, { tam: 9, color: "#334155" });
    texto(bx0 + CW / 2, y + 12, dev.id, { tam: 11, color: colorBorde });

    if (rol === "guard" || rol === "ust") {
      // Rama aparte: excluida (guarda) o flotando (UST), no toca el bus.
      const color = rol === "guard" ? COLOR_FP.guard : COLOR_FP.ust;
      linea(`M${BUS + 10} ${y} H${bx0 - 14}`, color, 2.5, "round", rol === "guard" ? "2,4" : "1,5");
      partes.push(`<circle cx="${BUS + 10}" cy="${y}" r="4.5" fill="#FFFFFF" stroke="${color}" stroke-width="2.5"/>`);
      texto(BUS + 10, y - 10, rol === "guard" ? "GUARDA" : "UST", { ancla: "middle", color, tam: 8 });
    } else {
      // HV o GND: conectado al bus con el capacitor de esa interfase.
      linea(`M${BUS} ${y} H${bx0}`, colorBorde, 2.5);
      capacitor(BUS + 23, y, colorBorde, true);
    }
  });

  // Segmento del bus que representa la trayectoria medida: del devanado
  // energizado hasta el punto de tierra (otro devanado o el tanque).
  if (yHv !== null) {
    linea(`M${BUS} ${yHv} V${yGnd}`, COLOR_FP.medido, 4, "butt");
    partes.push(`<g class="pulso">${partes.pop()}</g>`);
  }

  // Tanque / tierra al fondo del bus (si nadie más marcó tierra arriba).
  linea(`M${BUS - 14} ${fondo} H${BUS + 14} M${BUS - 9} ${fondo + 6} H${BUS + 9} M${BUS - 4} ${fondo + 12} H${BUS + 4}`, COLOR_FP.gnd, 2.5);
  texto(BUS, fondo + 28, "TANQUE", { tam: 9, color: COLOR_FP.gnd });

  const ancho = BUS + 46 + CW + 20;
  return `<svg viewBox="0 0 ${ancho} ${fondo + 44}" xmlns="http://www.w3.org/2000/svg" font-family="Consolas, 'Courier New', monospace">${partes.join("")}</svg>`;
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

  const hvMide = true;
  linea(`M${gx + gw} ${gy + gh / 2} H${cx} V${by0}`, COLOR_FP.medido, 4);
  punto(cx, by0, COLOR_FP.medido);
  texto(cx + 10, by0 - 10, `HV ${pr.hv || "—"}`, { ancla: "start", color: COLOR_FP.hv, tam: 10, clase: "pulso" });

  if (llevaGnd) {
    const yFondo = by1 + 42;
    linea(`M${cx} ${by1} V${yFondo}`, COLOR_FP.medido, 4, "butt");
    linea(`M${cx - 14} ${yFondo} H${cx + 14} M${cx - 9} ${yFondo + 6} H${cx + 9} M${cx - 4} ${yFondo + 12} H${cx + 4}`, COLOR_FP.gnd, 2.5);
    texto(cx, yFondo + 28, `TIERRA ${pr.ground}`, { tam: 10, color: COLOR_FP.gnd, clase: "pulso" });
  }
  if (llevaGuard) {
    const gxp = bx1 + 60, gyp = cyBox;
    linea(`M${bx1} ${cyBox} H${gxp}`, COLOR_FP.guard, 2.5, "round", "2,4");
    puntoHueco(gxp, gyp, COLOR_FP.guard);
    texto(gxp, gyp - 12, "GUARDA", { color: COLOR_FP.guard, tam: 9 });
    texto(gxp, gyp + 18, pr.guard, { color: COLOR_FP.guard, tam: 10 });
  }
  if (llevaUst) {
    const uxp = bx0 - 60, uyp = by1 + 10;
    linea(`M${bx0} ${by1 - 8} L${uxp} ${uyp}`, COLOR_FP.ust, 2.5, "round", "1,5");
    puntoHueco(uxp, uyp, COLOR_FP.ust);
    texto(uxp, uyp + 16, "UST", { color: COLOR_FP.ust, tam: 9 });
    texto(uxp, uyp + 32, pr.ust, { color: COLOR_FP.ust, tam: 10 });
  }
  if (pr.flotando) texto(cx, by0 - 26, `FLOTA: ${pr.flotando}`, { color: "#B45309", tam: 9 });

  const alto = Math.max(260, llevaGnd ? by1 + 90 : by1 + 40);
  return `<svg viewBox="0 0 350 ${alto}" xmlns="http://www.w3.org/2000/svg" font-family="Consolas, 'Courier New', monospace">${partes.join("")}</svg>`;
}

function dibujarDiagramaFp(d, pr, modo) {
  const pila = _devanadosFp(d.equipo, d.arreglo);
  if (pila) return _dibujarPilaFp(d.equipo, d.arreglo, pr);
  return _dibujarGenericoFp(d.equipo, pr);
}
