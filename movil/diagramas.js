// Diagramas de bloques en SVG, según las figuras del ST-CT-001.
"use strict";

const COLOR = {
  cable: "#1D5FC4",
  medido: "#EA580C",
  texto: "#1E3A8A",
  LINEA: "#DC2626",
  TIERRA: "#111111",
  GUARDA: "#2563EB",
};
const ROTULO = { LINEA: "LÍNEA", TIERRA: "TIERRA", GUARDA: "GUARDA" };

function modeloDiagrama(datos, prueba) {
  const caja = (mide, conex, donde) => ({ mide, conex, sitios: donde });
  switch (datos.equipo) {
    case "2d":
      return {
        tipo: "pila", tanque: "TANQUE",
        cajas: [caja("ALTA", "H", ["H"]), caja("BAJA", "X", ["X"])],
        bus: ["RH", "RX"], entre: ["RHX"],
      };
    case "3d":
      return {
        tipo: "pila", tanque: "TANQUE",
        cajas: [caja("ALTA", "H", ["H"]), caja("BAJA", "X", ["X"]), caja("TERCIARIO", "Y", ["Y"])],
        bus: ["RH", "RX", "RY"], entre: ["RHX", "RXY"], puente: "RHY",
      };
    case "auto":
      if (datos.terciario === "sin") {
        return {
          tipo: "pila", tanque: "TANQUE",
          cajas: [caja("ALTA-BAJA", "H-X", ["H", "X"])], bus: ["RHX"], entre: [],
        };
      }
      return {
        tipo: "pila", tanque: "TANQUE",
        cajas: [caja("ALTA-BAJA", "H-X", ["H", "X"]), caja("TERCIARIO", "Y", ["Y"])],
        bus: ["RHX", "RY"], entre: ["RHXY"],
      };
    case "reactor":
      return {
        tipo: "pila", tanque: "TANQUE",
        cajas: [caja("DEVANADO", "H", ["H"])], bus: ["RH"], entre: [],
      };
    case "gen":
      if (/rotor/i.test(prueba.linea)) {
        return {
          tipo: "pila", tanque: "CARCASA",
          cajas: [caja("ROTOR", "ROTOR", ["ROTOR"])], bus: ["RRT"], entre: [],
        };
      }
      return {
        tipo: "pila", tanque: "CARCASA",
        cajas: [caja("A", "A", ["A"]), caja("B", "B", ["B"]), caja("C", "C", ["C"])],
        bus: ["RAT", "RBT", "RCT"], entre: ["RAB", "RBC"], puente: "RAC",
      };
    case "tp":
    case "tpc":
      return {
        tipo: "pila", tanque: "TANQUE",
        cajas: [caja("PRIMARIO", "P", ["P"]), caja("SECUNDARIO", "S", ["S"])],
        bus: ["RP", "RS"], entre: ["RPS"],
      };
    case "tc":
      return { tipo: "tc", tanque: "TANQUE" };
    default:
      return { tipo: "cadena", bornes: datos.secciones === "una" ? ["A", "B"] : ["A", "B", "C", "D"] };
  }
}

// Tramos " L…" del diente de sierra, partiendo de (x0, y0) hasta (x1, y1).
function zigzag(x0, y0, x1, y1, dientes, amp) {
  const horizontal = y0 === y1;
  const largo = horizontal ? x1 - x0 : y1 - y0;
  const paso = largo / dientes;
  let d = "";
  for (let i = 0; i < dientes; i++) {
    const lado = i % 2 === 0 ? -amp : amp;
    const medio = (i + 0.5) * paso;
    d += horizontal ? ` L${x0 + medio} ${y0 + lado}` : ` L${x0 + lado} ${y0 + medio}`;
  }
  return d + ` L${x1} ${y1}`;
}

function dibujarDiagrama(datos, prueba, modo) {
  const m = modeloDiagrama(datos, prueba);
  const conexiones = modo === "conexiones";
  const medidos = conexiones ? new Set() : codigosMedidos(prueba);
  const roles = { LINEA: sitios(prueba.linea), TIERRA: sitios(prueba.tierra), GUARDA: sitios(prueba.guarda) };
  const rolDe = (donde) => {
    if (!conexiones) return null;
    for (const rol of ["LINEA", "TIERRA", "GUARDA"]) {
      if (donde.some((s) => roles[rol].has(s))) return rol;
    }
    return null;
  };
  const partes = [];
  const linea = (d, color, ancho, cap) =>
    partes.push(`<path d="${d}" fill="none" stroke="${color || COLOR.cable}" stroke-width="${ancho || 3}" stroke-linecap="${cap || "round"}" stroke-linejoin="round"/>`);
  const texto = (x, y, t, o) => {
    o = o || {};
    partes.push(
      `<text x="${x}" y="${y}" text-anchor="${o.ancla || "middle"}" fill="${o.color || COLOR.texto}" ` +
      `font-size="${o.tam || 12}" font-weight="700" class="${o.clase || ""}">${t}</text>`
    );
  };
  // Resistencia con sus dos tramos de cable. Parpadea si es la que se mide.
  const resistencia = (codigo, x0, y0, x1, y1, etiqueta) => {
    const medido = medidos.has(codigo);
    const color = medido ? COLOR.medido : COLOR.cable;
    const horizontal = y0 === y1;
    const largo = horizontal ? x1 - x0 : y1 - y0;
    const cuerpo = Math.min(largo - 12, horizontal ? 56 : 42);
    const ini = (largo - cuerpo) / 2;
    const [zx0, zy0, zx1, zy1] = horizontal
      ? [x0 + ini, y0, x0 + ini + cuerpo, y0]
      : [x0, y0 + ini, x0, y0 + ini + cuerpo];
    partes.push(
      `<g class="${medido ? "pulso" : ""}">` +
      `<path d="M${x0} ${y0} L${zx0} ${zy0}${zigzag(zx0, zy0, zx1, zy1, 5, 7)} L${x1} ${y1}" ` +
      `fill="none" stroke="${color}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>` +
      `<text x="${etiqueta.x}" y="${etiqueta.y}" text-anchor="${etiqueta.ancla || "middle"}" fill="${color}" font-size="11" font-weight="700">${codigo}</text>` +
      `</g>`
    );
  };
  const tierra = (x, y) => {
    linea(`M${x - 14} ${y} H${x + 14} M${x - 9} ${y + 6} H${x + 9} M${x - 4} ${y + 12} H${x + 4}`, COLOR.cable, 2.5);
    texto(x, y + 30, "TIERRA");
  };
  const rotuloTanque = (nombre, x) => {
    texto(x, 16, nombre, { ancla: "middle" });
    if (!conexiones) return;
    const rol = roles.TIERRA.has("TANQUE") ? "TIERRA" : roles.GUARDA.has("TANQUE") ? "GUARDA" : null;
    if (rol) texto(x + 36, 16, ROTULO[rol], { ancla: "start", color: COLOR[rol], clase: "pulso" });
  };
  const cajaSvg = (c, x, y, w, h) => {
    const rol = rolDe(c.sitios);
    const color = rol ? COLOR[rol] : COLOR.cable;
    partes.push(`<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="7" fill="#FFFFFF" stroke="${color}" stroke-width="3"/>`);
    if (rol) {
      texto(x + w / 2, y + h / 2 - 3, c.conex, { tam: 10, color: "#64748B" });
      texto(x + w / 2, y + h / 2 + 12, ROTULO[rol], { color, clase: "pulso" });
    } else {
      texto(x + w / 2, y + h / 2 + 4, conexiones ? c.conex : c.mide);
    }
  };

  let ancho = 300;
  let alto = 200;
  const BUS = 46;
  const CX = 150;
  const CW = 120;
  const CH = 46;
  const PASO = 104;
  const Y0 = 34;

  if (m.tipo === "pila") {
    const n = m.cajas.length;
    const fondo = Y0 + (n - 1) * PASO + CH + 34;
    rotuloTanque(m.tanque, BUS);
    linea(`M${BUS} 26 V${fondo}`, COLOR.cable, 3.5, "butt");
    tierra(BUS, fondo);
    m.cajas.forEach((c, i) => {
      const y = Y0 + i * PASO;
      const cy = y + CH / 2;
      resistencia(m.bus[i], BUS, cy, CX, cy, { x: (BUS + CX) / 2, y: cy + 22 });
      if (i < n - 1) {
        resistencia(m.entre[i], CX + CW / 2, y + CH, CX + CW / 2, y + PASO, { x: CX + CW / 2 + 14, y: y + CH + (PASO - CH) / 2 + 4, ancla: "start" });
      }
    });
    if (m.puente) {
      const px = CX + CW + 56;
      const y1 = Y0 + CH / 2;
      const y2 = Y0 + (n - 1) * PASO + CH / 2;
      linea(`M${CX + CW} ${y1} H${px} M${CX + CW} ${y2} H${px}`);
      resistencia(m.puente, px, y1, px, y2, { x: px + 12, y: (y1 + y2) / 2 + 4, ancla: "start" });
      ancho = px + 56;
    }
    m.cajas.forEach((c, i) => cajaSvg(c, CX, Y0 + i * PASO, CW, CH));
    alto = fondo + 40;
  } else if (m.tipo === "tc") {
    // Fig. 15: la pantalla aterrizada separa los devanados.
    const yP = Y0;
    const union = yP + CH + 68;
    const yS = union + 68;
    const fondo = yS + CH + 34;
    const cxm = CX + CW / 2;
    rotuloTanque("TANQUE", BUS);
    linea(`M${BUS} 26 V${fondo}`, COLOR.cable, 3.5, "butt");
    tierra(BUS, fondo);
    resistencia("RP", BUS, yP + CH / 2, CX, yP + CH / 2, { x: (BUS + CX) / 2, y: yP + CH / 2 + 22 });
    resistencia("RPC", cxm, yP + CH, cxm, union, { x: cxm + 14, y: yP + CH + 38, ancla: "start" });
    linea(`M${BUS} ${union} H${cxm}`);
    resistencia("RSC", cxm, union, cxm, yS, { x: cxm + 14, y: union + 38, ancla: "start" });
    if (conexiones && roles.GUARDA.has("PORCELANA")) {
      texto(cxm - 14, yP + CH + 38, "GUARDA", { ancla: "end", color: COLOR.GUARDA, clase: "pulso" });
    }
    cajaSvg({ mide: "PRIMARIO", conex: "P", sitios: ["P"] }, CX, yP, CW, CH);
    cajaSvg({ mide: "SECUNDARIO", conex: "S", sitios: ["S"] }, CX, yS, CW, CH);
    alto = fondo + 40;
  } else {
    // Apartarrayos: secciones en serie.
    const x = 130;
    const paso = 88;
    const y0 = 26;
    const n = m.bornes.length;
    const fondo = y0 + (n - 1) * paso + 22;
    m.bornes.forEach((borne, i) => {
      const y = y0 + i * paso;
      const rol = rolDe([borne]);
      if (rol) {
        texto(x - 16, y + 4, ROTULO[rol], { ancla: "end", color: COLOR[rol], clase: "pulso" });
        texto(x - 16, y - 10, borne, { ancla: "end", tam: 10, color: "#64748B" });
      } else {
        texto(x - 16, y + 4, borne, { ancla: "end" });
      }
      partes.push(`<circle cx="${x}" cy="${y}" r="4" fill="${rol ? COLOR[rol] : COLOR.cable}"/>`);
      if (i < n - 1) {
        const codigo = `R${borne}${m.bornes[i + 1]}`;
        resistencia(codigo, x, y, x, y + paso, { x: x + 18, y: y + paso / 2 + 4, ancla: "start" });
      }
    });
    linea(`M${x} ${y0 + (n - 1) * paso} V${fondo}`, COLOR.cable, 3.5, "butt");
    tierra(x, fondo);
    ancho = 260;
    alto = fondo + 40;
  }
  return (
    `<svg viewBox="0 0 ${ancho} ${alto}" xmlns="http://www.w3.org/2000/svg" role="img" ` +
    `aria-label="Diagrama de ${conexiones ? "conexiones" : "medición"}" ` +
    `style="max-height:${Math.round(alto * 1.25)}px">${partes.join("")}</svg>`
  );
}

function leyendaMedicion(datos, prueba) {
  const m = modeloDiagrama(datos, prueba);
  let codigos;
  if (m.tipo === "pila") {
    codigos = [];
    m.cajas.forEach((_, i) => {
      codigos.push(m.bus[i]);
      if (m.entre[i]) codigos.push(m.entre[i]);
    });
    if (m.puente) codigos.splice(2, 0, m.puente);
  } else if (m.tipo === "tc") {
    codigos = ["RP", "RPC", "RSC"];
  } else {
    codigos = m.bornes.slice(0, -1).map((b, i) => `R${b}${m.bornes[i + 1]}`);
  }
  const medidos = codigosMedidos(prueba);
  return codigos.map((codigo) => ({
    codigo, medido: medidos.has(codigo), texto: descripcionCodigo(codigo, datos.equipo),
  }));
}

function leyendaConexiones(prueba) {
  const filas = [];
  if (!VACIO.has(prueba.linea)) filas.push({ rol: "LINEA", texto: `Conexión de línea (+): ${prueba.linea}` });
  if (!VACIO.has(prueba.tierra)) filas.push({ rol: "TIERRA", texto: `Conexión de tierra (−): ${prueba.tierra}` });
  if (!VACIO.has(prueba.guarda)) filas.push({ rol: "GUARDA", texto: `Conexión de guarda: ${prueba.guarda}` });
  return filas;
}
