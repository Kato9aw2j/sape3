// Diagramas de ingeniería del Anexo A (vista de planta / alzado de cada
// equipo), calco de SAPE2.py: _dibujar_diagrama_tc, _dibujar_diagrama_tpc,
// _dibujar_diagrama_tp, _dibujar_diagrama_transformador_2d/3d,
// _dibujar_diagrama_autotransformador, _dibujar_diagrama_reactor,
// _dibujar_diagrama_apartarrayos. Mismas coordenadas y colores; el canvas de
// tkinter se reemplaza por un <svg> con el mismo sistema X(x)=ox+x*s,
// Y(y)=oy+y*s.
"use strict";

function _escAnexoDiag(t) {
  return String(t).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

// Mismo lienzo de 640px de ancho que usa SAPE2.py para cada diagrama;
// anchoBase/altoBase son las unidades de dibujo (antes de aplicar s).
function _anexoLienzo(anchoBase, altoBase, s) {
  const anchoCanvas = 640;
  const altoCanvas = Math.floor(altoBase * s) + 14;
  const ox = (anchoCanvas - anchoBase * s) / 2;
  const oy = 6;
  const X = (x) => ox + x * s;
  const Y = (y) => oy + y * s;
  const partes = [];

  const atributos = (o) => {
    let a = ` fill="${o.fill || "none"}" stroke="${o.outline || "none"}" stroke-width="${o.width || 1}"`;
    if (o.dash) a += ` stroke-dasharray="${o.dash[0]},${o.dash[1]}"`;
    return a;
  };

  const rect = (x, y, ancho, alto, o = {}) => {
    partes.push(
      `<rect x="${X(x).toFixed(1)}" y="${Y(y).toFixed(1)}" width="${(ancho * s).toFixed(1)}" height="${(alto * s).toFixed(1)}"${atributos(o)}/>`,
    );
  };
  const ovalo = (cx, cy, r, o = {}) => {
    partes.push(
      `<circle cx="${X(cx).toFixed(1)}" cy="${Y(cy).toFixed(1)}" r="${Math.max(0.5, r * s).toFixed(1)}"${atributos(o)}/>`,
    );
  };
  const linea = (x1, y1, x2, y2, o = {}) => {
    let a = ` stroke="${o.fill || "#000000"}" stroke-width="${o.width || 1}"`;
    if (o.dash) a += ` stroke-dasharray="${o.dash[0]},${o.dash[1]}"`;
    if (o.cap) a += ` stroke-linecap="${o.cap}"`;
    partes.push(
      `<line x1="${X(x1).toFixed(1)}" y1="${Y(y1).toFixed(1)}" x2="${X(x2).toFixed(1)}" y2="${Y(y2).toFixed(1)}"${a}/>`,
    );
  };
  const poligono = (puntos, o = {}) => {
    const pts = puntos.map(([x, y]) => `${X(x).toFixed(1)},${Y(y).toFixed(1)}`).join(" ");
    partes.push(`<polygon points="${pts}"${atributos(o)}/>`);
  };
  const texto = (x, y, txt, tam, color = "#333333", negrita = true, ancla = "w") => {
    const anchorMap = { w: "start", e: "end", center: "middle" };
    const tamFuente = Math.max(8, Math.round(tam * s));
    partes.push(
      `<text x="${X(x).toFixed(1)}" y="${Y(y).toFixed(1)}" text-anchor="${anchorMap[ancla] || "start"}" ` +
      `dominant-baseline="central" fill="${color}" font-family="Arial, sans-serif" ` +
      `font-size="${tamFuente}" font-weight="${negrita ? 700 : 400}">${_escAnexoDiag(txt)}</text>`,
    );
  };
  const rango = (inicio, fin, paso) => {
    const r = [];
    for (let v = inicio; v <= fin; v += paso) r.push(v);
    return r;
  };

  return {
    rect, ovalo, linea, poligono, texto, rango,
    svg() {
      return (
        `<svg viewBox="0 0 ${anchoCanvas} ${altoCanvas}" xmlns="http://www.w3.org/2000/svg" ` +
        `style="background:#FFFFFF;border:1px solid #E2E8F0;max-width:100%;height:auto;display:block">` +
        `${partes.join("")}</svg>`
      );
    },
  };
}

const _ROJO_DIAG = "#CC0000";
const _AZUL_DIAG = "#0055AA";

function dibujarDiagramaTc() {
  const s = 0.8;
  const { rect, ovalo, linea, poligono, texto, svg } = _anexoLienzo(600, 820, s);
  const rojo = _ROJO_DIAG, azul = _AZUL_DIAG;
  texto(30, 80, "PRIMARIO", 22, rojo);
  texto(30, 105, "(Línea de AT)", 15, rojo, false);
  linea(180, 90, 210, 90, { fill: rojo, width: 2, dash: [4, 4] });
  texto(410, 670, "SECUNDARIO", 22, azul);
  texto(410, 695, "(Instrumentos)", 15, azul, false);
  linea(380, 680, 400, 680, { fill: azul, width: 2, dash: [4, 4] });
  rect(200, 80, 200, 140, { fill: "#E0E0E0", outline: "#333333", width: 2 });
  rect(220, 90, 160, 120, { fill: "#D0D0D0", outline: "#333333", width: 1 });
  for (const [cx, cy] of [[215, 95], [385, 95], [215, 205], [385, 205]]) {
    ovalo(cx, cy, 4, { fill: "#666666", outline: "#666666" });
  }
  linea(150, 150, 250, 150, { fill: rojo, width: 5 });
  ovalo(150, 150, 8, { fill: rojo, outline: rojo });
  texto(100, 156, "P1", 20, rojo);
  linea(350, 150, 450, 150, { fill: rojo, width: 5 });
  ovalo(450, 150, 8, { fill: rojo, outline: rojo });
  texto(470, 156, "P2", 20, rojo);
  rect(250, 140, 100, 20, { fill: rojo, outline: "#800000", width: 2 });
  rect(230, 220, 140, 15, { fill: "#A0A0A0", outline: "#333333", width: 2 });
  rect(275, 235, 50, 380, { fill: "#F9F9F9", outline: "#888888", width: 1 });
  for (let i = 0; i < 12; i++) {
    rect(235, 245 + 30 * i, 130, 18, { fill: "#EEEEEE", outline: "#555555", width: 1 });
  }
  rect(230, 615, 140, 15, { fill: "#A0A0A0", outline: "#333333", width: 2 });
  poligono([[210, 630], [390, 630], [410, 750], [190, 750]], { fill: "#B0B0B0", outline: "#333333", width: 2 });
  rect(200, 630, 200, 10, { fill: "#909090", outline: "#333333", width: 2 });
  rect(210, 660, 180, 70, { fill: "#DCDCDC", outline: "#333333", width: 2 });
  linea(210, 695, 390, 695, { fill: "#999999", width: 1, dash: [2, 2] });
  for (const [bx, nombre] of [[250, "S1"], [350, "S2"]]) {
    ovalo(bx, 680, 5, { fill: azul, outline: azul });
    texto(bx - 35, 685, nombre, 16, azul);
  }
  for (const [bx, nombre] of [[250, "S3"], [350, "S4"]]) {
    ovalo(bx, 715, 5, { fill: azul, outline: azul });
    texto(bx - 35, 720, nombre, 16, azul);
  }
  linea(355, 715, 420, 715, { fill: "green", width: 3 });
  linea(420, 715, 420, 770, { fill: "green", width: 3 });
  linea(400, 770, 440, 770, { fill: "green", width: 4 });
  linea(408, 778, 432, 778, { fill: "green", width: 4 });
  linea(416, 786, 424, 786, { fill: "green", width: 4 });
  texto(450, 780, "Tierra", 14, "green");
  return svg();
}

function dibujarDiagramaTpc() {
  const s = 0.72;
  const { rect, ovalo, linea, texto, svg } = _anexoLienzo(850, 1050, s);
  const rojo = _ROJO_DIAG, azul = _AZUL_DIAG;
  texto(50, 80, "PRIMARIO", 20, rojo);
  texto(50, 105, "(Alta Tensión)", 14, rojo, false);
  linea(170, 90, 210, 90, { fill: rojo, width: 2, dash: [4, 4] });
  linea(350, 30, 350, 60, { fill: rojo, width: 5 });
  ovalo(350, 30, 8, { fill: rojo, outline: rojo });
  texto(365, 38, "H1", 20, rojo);
  rect(275, 60, 150, 40, { fill: "#D0D0D0", outline: "#333333", width: 2 });
  rect(285, 70, 130, 20, { fill: "#B0B0B0", outline: "#333333", width: 1 });
  rect(200, 120, 300, 450, { fill: "#FAFAFA", outline: azul, width: 2, dash: [8, 4] });
  rect(210, 105, 280, 30, { fill: azul, outline: azul });
  texto(350, 125, "PARTE CAPACITIVA (DIVISOR)", 12, "#FFFFFF", true, "center");
  linea(350, 140, 350, 550, { fill: "#333333", width: 3 });
  for (const [yC, nombre] of [[160, "C1A"], [230, "C1B"], [300, "C1C"], [470, "C2"]]) {
    linea(300, yC, 400, yC, { fill: "#333333", width: 4 });
    linea(300, yC + 10, 400, yC + 10, { fill: "#333333", width: 4 });
    texto(410, yC + 10, nombre, 18, azul);
  }
  ovalo(350, 390, 7, { fill: "#333333", outline: "#333333" });
  texto(350, 420, "Toma intermedia", 14, "#333333", true, "center");
  linea(350, 480, 350, 540, { fill: "#333333", width: 3 });
  linea(330, 540, 370, 540, { fill: "green", width: 4 });
  linea(338, 548, 362, 548, { fill: "green", width: 4 });
  linea(346, 556, 354, 556, { fill: "green", width: 4 });
  texto(40, 385, "CD", 20, rojo);
  texto(40, 405, "(Cap. Total)", 12, rojo, false);
  linea(92, 390, 330, 390, { fill: rojo, width: 2, dash: [4, 4] });
  rect(500, 365, 180, 50, { fill: "#FFF0F0", outline: rojo, width: 2 });
  texto(590, 385, "CD = (C1 × C2)", 14, "#333333", true, "center");
  texto(590, 405, "/ (C1 + C2)", 14, "#333333", true, "center");
  rect(260, 590, 180, 20, { fill: "#A0A0A0", outline: "#333333", width: 2 });
  rect(230, 610, 240, 260, { fill: "#C0C0C0", outline: "#333333", width: 2 });
  rect(250, 630, 200, 70, { fill: "#B0B0B0", outline: "#555555", width: 1 });
  texto(350, 660, "Transformador", 15, "#333333", true, "center");
  texto(350, 680, "Electromagnético", 15, "#333333", true, "center");
  rect(250, 720, 80, 60, { fill: "#A0A0A0", outline: "#555555", width: 1 });
  for (const yR of [735, 745, 755, 765]) {
    linea(260, yR, 320, yR, { fill: "#333333", width: 2 });
  }
  texto(290, 800, "Reactor", 13, "#333333", true, "center");
  rect(360, 720, 140, 120, { fill: "#DCDCDC", outline: "#333333", width: 2 });
  texto(430, 730, "Caja de Bornes", 11, "#333333", true, "center");
  for (const [bx, nombre] of [[385, "X1"], [430, "X2"], [475, "X3"]]) {
    ovalo(bx, 745, 5, { fill: azul, outline: azul });
    texto(bx, 765, nombre, 14, azul, true, "center");
  }
  for (const [bx, nombre] of [[385, "Y1"], [430, "Y2"], [475, "Y3"]]) {
    ovalo(bx, 805, 5, { fill: azul, outline: azul });
    texto(bx, 825, nombre, 14, azul, true, "center");
  }
  linea(370, 780, 490, 780, { fill: "green", width: 2 });
  linea(490, 780, 490, 830, { fill: "green", width: 2 });
  ovalo(430, 745, 7, { outline: "green", width: 2 });
  linea(430, 745, 430, 780, { fill: "green", width: 3 });
  ovalo(430, 805, 7, { outline: "green", width: 2 });
  linea(430, 805, 430, 780, { fill: "green", width: 3 });
  linea(500, 715, 525, 715, { fill: azul, width: 2, dash: [4, 4] });
  texto(535, 710, "SECUNDARIO", 18, azul);
  texto(535, 730, "(Instrumentos)", 12, azul, false);
  linea(500, 780, 525, 780, { fill: "green", width: 2, dash: [4, 4] });
  texto(535, 775, "PUESTA A TIERRA", 12, "green");
  texto(535, 792, "del secundario", 10, "green", false);
  linea(260, 870, 260, 920, { fill: rojo, width: 3 });
  ovalo(260, 920, 6, { fill: rojo, outline: rojo });
  texto(272, 905, "H2", 20, rojo);
  linea(240, 955, 280, 955, { fill: "green", width: 4 });
  linea(248, 963, 272, 963, { fill: "green", width: 4 });
  linea(256, 971, 264, 971, { fill: "green", width: 4 });
  texto(290, 965, "Tierra Tanque", 12, "green");
  linea(490, 830, 490, 920, { fill: "green", width: 2 });
  linea(470, 920, 510, 920, { fill: "green", width: 4 });
  linea(478, 928, 502, 928, { fill: "green", width: 4 });
  linea(486, 936, 494, 936, { fill: "green", width: 4 });
  texto(520, 930, "Tierra Secundario", 12, "green");
  return svg();
}

function dibujarDiagramaTp() {
  const s = 0.8;
  const { rect, ovalo, linea, poligono, texto, svg } = _anexoLienzo(600, 850, s);
  const rojo = _ROJO_DIAG, azul = _AZUL_DIAG;
  texto(20, 80, "PRIMARIO", 22, rojo);
  texto(20, 105, "(Alta Tensión)", 15, rojo, false);
  linea(154, 90, 196, 90, { fill: rojo, width: 2, dash: [4, 4] });
  texto(420, 680, "SECUNDARIO", 22, azul);
  texto(420, 705, "(Baja Tensión)", 15, azul, false);
  linea(400, 690, 416, 690, { fill: azul, width: 2, dash: [4, 4] });
  linea(300, 10, 300, 40, { fill: rojo, width: 4 });
  ovalo(300, 10, 7, { fill: rojo, outline: rojo });
  texto(315, 8, "H1", 20, rojo);
  rect(200, 40, 200, 80, { fill: "#E0E0E0", outline: "#333333", width: 2 });
  rect(220, 50, 160, 60, { fill: "#D0D0D0", outline: "#333333", width: 1 });
  rect(230, 25, 140, 15, { fill: "#B0B0B0", outline: "#333333", width: 2 });
  ovalo(300, 70, 12, { fill: "#FFFFFF", outline: "#333333", width: 2 });
  ovalo(300, 70, 6, { fill: "#ADD8E6", outline: "#ADD8E6" });
  texto(412, 75, "Indicador nivel", 12, "#333333", false);
  rect(230, 120, 140, 15, { fill: "#A0A0A0", outline: "#333333", width: 2 });
  rect(275, 135, 50, 510, { fill: "#F9F9F9", outline: "#888888", width: 1 });
  for (let i = 0; i < 17; i++) {
    rect(235, 145 + 30 * i, 130, 18, { fill: "#EEEEEE", outline: "#555555", width: 1 });
  }
  rect(230, 645, 140, 15, { fill: "#A0A0A0", outline: "#333333", width: 2 });
  poligono([[210, 660], [390, 660], [410, 780], [190, 780]], { fill: "#B0B0B0", outline: "#333333", width: 2 });
  rect(200, 660, 200, 10, { fill: "#909090", outline: "#333333", width: 2 });
  rect(365, 700, 20, 30, { fill: "#909090", outline: "#333333", width: 1 });
  ovalo(375, 715, 5, { fill: "#333333", outline: "#333333" });
  texto(412, 728, "Toma de", 11, "#333333", false);
  texto(412, 743, "muestras", 11, "#333333", false);
  linea(140, 760, 140, 790, { fill: rojo, width: 4 });
  ovalo(140, 790, 7, { fill: rojo, outline: rojo });
  texto(155, 772, "H2", 20, rojo);
  linea(120, 805, 160, 805, { fill: "green", width: 4 });
  linea(128, 813, 152, 813, { fill: "green", width: 4 });
  linea(136, 821, 144, 821, { fill: "green", width: 4 });
  texto(180, 720, "Caja de Bornes", 13, "#333333", true, "e");
  rect(220, 680, 120, 80, { fill: "#DCDCDC", outline: "#333333", width: 2 });
  for (const [bx, nombre] of [[245, "X1"], [280, "X2"], [315, "X3"]]) {
    ovalo(bx, 705, 5, { fill: azul, outline: azul });
    texto(bx - 10, 695, nombre, 14, azul);
  }
  for (const [bx, nombre] of [[245, "Y1"], [280, "Y2"], [315, "Y3"]]) {
    ovalo(bx, 740, 5, { fill: azul, outline: azul });
    texto(bx - 10, 755, nombre, 14, azul);
  }
  return svg();
}

// Conexiones de prueba (CN/CR/GN/GR) sobre los bujes del dibujo de planta:
// aro negro (CN/GN) o rojo (CR/GR) y el rol encima del buje.
function marcarConexionesPlanta(ovalo, texto, marcas, roles) {
  for (const [nombre, cx, cy, radio] of marcas) {
    const rs = ["CN", "CR", "GN", "GR"].filter((r) => (roles[nombre] || []).includes(r));
    if (!rs.length) continue;
    const color = rs.some((r) => r === "CR" || r === "GR") ? "#FF0000" : "#000000";
    ovalo(cx, cy, radio + 7, { outline: color, width: 3 });
    texto(cx, cy - radio - 16, rs.join("/"), 11, color, true, "center");
  }
}

function dibujarDiagramaTransformador(tresDevanados, monofasico, roles = null) {
  const s = 0.62;
  const { rect, ovalo, linea, texto, svg } = _anexoLienzo(950, 700, s);
  const rojo = _ROJO_DIAG, azul = _AZUL_DIAG, naranja = "#FF8C00";
  if (!tresDevanados) {
    rect(240, 140, 520, 320, { outline: "#222222", width: 2 });
    rect(255, 155, 490, 290, { outline: "#222222", width: 1, dash: [4, 4] });
    for (let xT = 270; xT <= 720; xT += 50) {
      ovalo(xT, 150, 2, { fill: "#222222", outline: "#222222" });
      ovalo(xT, 450, 2, { fill: "#222222", outline: "#222222" });
    }
    for (let yT = 180; yT <= 430; yT += 50) {
      ovalo(250, yT, 2, { fill: "#222222", outline: "#222222" });
      ovalo(740, yT, 2, { fill: "#222222", outline: "#222222" });
    }
    rect(330, 60, 340, 80, { outline: "#222222", width: 1 });
    rect(330, 460, 340, 80, { outline: "#222222", width: 1 });
    for (let xR = 335; xR <= 665; xR += 15) {
      linea(xR, 60, xR, 140, { fill: "#222222", width: 1 });
      linea(xR, 460, xR, 540, { fill: "#222222", width: 1 });
    }
    rect(160, 220, 80, 160, { outline: "#222222", width: 1 });
    rect(760, 220, 80, 160, { outline: "#222222", width: 1 });
    for (let yR = 225; yR <= 375; yR += 15) {
      linea(160, yR, 240, yR, { fill: "#222222", width: 1 });
      linea(760, yR, 840, yR, { fill: "#222222", width: 1 });
    }
    for (const [xU, yU] of [[420, 140], [580, 140], [420, 440], [580, 440]]) {
      linea(xU, yU, xU, yU + 20, { fill: "#222222", width: 2 });
    }
    linea(240, 260, 260, 260, { fill: "#222222", width: 2 });
    linea(240, 340, 260, 340, { fill: "#222222", width: 2 });
    linea(740, 260, 760, 260, { fill: "#222222", width: 2 });
    linea(740, 340, 760, 340, { fill: "#222222", width: 2 });
    const bujesAt = monofasico ? [[420, "H1"], [580, "H2"]] : [[390, "H1"], [500, "H2"], [610, "H3"], [700, "H0"]];
    for (const [cx, nombre] of bujesAt) {
      ovalo(cx, 210, 20, { fill: "#FFFFFF", outline: "#333333", width: 2 });
      ovalo(cx, 210, 12, { outline: "#333333", width: 1 });
      ovalo(cx, 210, 5, { fill: "#333333", outline: "#333333" });
      linea(cx, 230, cx, 300, { fill: "#222222", width: 1, dash: [3, 3] });
      texto(cx, 260, nombre, 14, "#333333", true, "center");
    }
    const bujesBt = monofasico
      ? [[470, "X1"], [530, "X2"]]
      : [[420, "X1"], [475, "X2"], [530, "X3"], [585, "X0"]];
    for (const [cx, nombre] of bujesBt) {
      ovalo(cx, 360, 14, { fill: "#FFFFFF", outline: "#333333", width: 2 });
      ovalo(cx, 360, 7, { outline: "#333333", width: 1 });
      ovalo(cx, 360, 3, { fill: "#333333", outline: "#333333" });
      texto(cx, 395, nombre, 14, "#333333", true, "center");
    }
    if (roles) {
      marcarConexionesPlanta(ovalo, texto, [
        ...bujesAt.map(([c, n]) => [n, c, 210, 20]),
        ...bujesBt.map(([c, n]) => [n, c, 360, 14]),
      ], roles);
    }
    for (const cx of [290, 710]) {
      ovalo(cx, 390, 12, { outline: "#222222", width: 1 });
      linea(cx - 12, 390, cx + 12, 390, { fill: "#222222", width: 1 });
      linea(cx, 378, cx, 402, { fill: "#222222", width: 1 });
    }
    for (const [xA, yA] of [[270, 250], [714, 250], [270, 350], [714, 350]]) {
      rect(xA, yA, 16, 8, { outline: "#222222", width: 1 });
    }
    const etiquetasLat = [
      [205, "ALTA TENSIÓN", monofasico ? "(H1, H2)" : "(H1, H2, H3)", rojo],
      [415, "BAJA TENSIÓN", monofasico ? "(X1, X2)" : "(X1, X2, X3, X0)", azul],
    ];
    for (const [yEt, tituloEt, subEt, colorEt] of etiquetasLat) {
      rect(2, yEt - 16, 146, 44, { fill: "#FFFFFF" });
      texto(8, yEt, tituloEt, 12, colorEt);
      texto(8, yEt + 19, subEt, 10, colorEt, false);
    }
    texto(475, 610, monofasico ? "TRANSFORMADOR DE POTENCIA MONOFÁSICO" : "TRANSFORMADOR DE POTENCIA TRIFÁSICO", 20, "#222222", true, "center");
    texto(475, 635, "2 DEVANADOS (VISTA DE PLANTA)", 16, "#222222", true, "center");
    texto(475, 665, monofasico ? "Devanado Primario: Fases H1, H2" : "Devanado Primario: Conexión Estrella (H1, H2, H3)", 14, "#555555", false, "center");
    texto(475, 685, monofasico ? "Devanado Secundario: Fases X1, X2" : "Devanado Secundario: Conexión Estrella con Neutro (X1, X2, X3, X0)", 14, "#555555", false, "center");
    return svg();
  }
  rect(220, 140, 560, 320, { outline: "#222222", width: 2 });
  rect(235, 155, 530, 290, { outline: "#222222", width: 1, dash: [4, 4] });
  for (let xT = 250; xT <= 750; xT += 50) {
    ovalo(xT, 150, 2, { fill: "#222222", outline: "#222222" });
    ovalo(xT, 450, 2, { fill: "#222222", outline: "#222222" });
  }
  for (let yT = 180; yT <= 430; yT += 50) {
    ovalo(230, yT, 2, { fill: "#222222", outline: "#222222" });
    ovalo(770, yT, 2, { fill: "#222222", outline: "#222222" });
  }
  rect(320, 60, 360, 80, { outline: "#222222", width: 1 });
  rect(320, 460, 360, 80, { outline: "#222222", width: 1 });
  for (let xR = 325; xR <= 670; xR += 15) {
    linea(xR, 60, xR, 140, { fill: "#222222", width: 1 });
    linea(xR, 460, xR, 540, { fill: "#222222", width: 1 });
  }
  rect(140, 220, 80, 160, { outline: "#222222", width: 1 });
  rect(780, 220, 80, 160, { outline: "#222222", width: 1 });
  for (let yR = 225; yR <= 375; yR += 15) {
    linea(140, yR, 220, yR, { fill: "#222222", width: 1 });
    linea(780, yR, 860, yR, { fill: "#222222", width: 1 });
  }
  for (const [xU, yU] of [[420, 140], [580, 140], [420, 440], [580, 440]]) {
    linea(xU, yU, xU, yU + 20, { fill: "#222222", width: 2 });
  }
  linea(220, 260, 240, 260, { fill: "#222222", width: 2 });
  linea(220, 340, 240, 340, { fill: "#222222", width: 2 });
  linea(760, 260, 780, 260, { fill: "#222222", width: 2 });
  linea(760, 340, 780, 340, { fill: "#222222", width: 2 });
  for (const [cx, nombre] of [[380, "H1"], [500, "H2"], [620, "H3"], [740, "H0"]]) {
    ovalo(cx, 200, 16, { fill: "#FFFFFF", outline: "#333333", width: 2 });
    ovalo(cx, 200, 9, { outline: "#333333", width: 1 });
    ovalo(cx, 200, 4, { fill: "#333333", outline: "#333333" });
    texto(cx, 240, nombre, 12, "#333333", true, "center");
  }
  for (const [cx, nombre] of [[320, "Y1"], [380, "Y2"], [440, "Y3"]]) {
    ovalo(cx, 360, 14, { fill: "#FFFFFF", outline: "#333333", width: 2 });
    ovalo(cx, 360, 7, { outline: "#333333", width: 1 });
    ovalo(cx, 360, 3, { fill: "#333333", outline: "#333333" });
    texto(cx, 395, nombre, 12, "#333333", true, "center");
  }
  for (const [cx, nombre] of [[540, "X1"], [590, "X2"], [640, "X3"], [690, "X0"]]) {
    ovalo(cx, 360, 12, { fill: "#FFFFFF", outline: "#333333", width: 2 });
    ovalo(cx, 360, 6, { outline: "#333333", width: 1 });
    ovalo(cx, 360, 2, { fill: "#333333", outline: "#333333" });
    texto(cx, 390, nombre, 12, "#333333", true, "center");
  }
  if (roles) {
    marcarConexionesPlanta(ovalo, texto, [
      ["H1", 380, 200, 16], ["H2", 500, 200, 16], ["H3", 620, 200, 16], ["H0", 740, 200, 16],
      ["Y1", 320, 360, 14], ["Y2", 380, 360, 14], ["Y3", 440, 360, 14],
      ["X1", 540, 360, 12], ["X2", 590, 360, 12], ["X3", 640, 360, 12], ["X0", 690, 360, 12],
    ], roles);
  }
  for (const cx of [270, 730]) {
    ovalo(cx, 400, 10, { outline: "#222222", width: 1 });
    linea(cx - 10, 400, cx + 10, 400, { fill: "#222222", width: 1 });
    linea(cx, 390, cx, 410, { fill: "#222222", width: 1 });
  }
  for (const xA of [250, 736]) {
    rect(xA, 250, 14, 6, { outline: "#222222", width: 1 });
  }
  const etiquetasLat3 = [
    [175, "ALTA TENSIÓN", "(H0, H1, H2, H3)", rojo],
    [375, "TERCIARIO", "(Y1, Y2, Y3)", naranja],
    [475, "BAJA TENSIÓN", "(X1, X2, X3, X0)", azul],
  ];
  for (const [yEt, tituloEt, subEt, colorEt] of etiquetasLat3) {
    rect(2, yEt - 16, 136, 44, { fill: "#FFFFFF" });
    texto(8, yEt, tituloEt, 12, colorEt);
    texto(8, yEt + 19, subEt, 10, colorEt, false);
  }
  texto(475, 610, "TRANSFORMADOR DE POTENCIA TRIFÁSICO", 20, "#222222", true, "center");
  texto(475, 635, "3 DEVANADOS (VISTA DE PLANTA)", 16, "#222222", true, "center");
  texto(475, 665, "Primario: H1, H2, H3 | Terciario: Y1, Y2, Y3 | Secundario: X1, X2, X3, X0", 14, "#555555", false, "center");
  return svg();
}

function dibujarDiagramaAutotransformador(monofasico) {
  const s = 0.62;
  const { rect, ovalo, linea, texto, svg } = _anexoLienzo(950, 750, s);
  const rojo = _ROJO_DIAG, azul = _AZUL_DIAG, naranja = "#FF8C00", gris = "#333333";
  rect(220, 140, 560, 340, { outline: "#222222", width: 2 });
  rect(235, 155, 530, 310, { outline: "#222222", width: 1, dash: [4, 4] });
  for (let xT = 250; xT <= 750; xT += 50) {
    ovalo(xT, 150, 2, { fill: "#222222", outline: "#222222" });
    ovalo(xT, 470, 2, { fill: "#222222", outline: "#222222" });
  }
  for (let yT = 180; yT <= 430; yT += 50) {
    ovalo(230, yT, 2, { fill: "#222222", outline: "#222222" });
    ovalo(770, yT, 2, { fill: "#222222", outline: "#222222" });
  }
  rect(320, 60, 360, 80, { outline: "#222222", width: 1 });
  rect(320, 480, 360, 80, { outline: "#222222", width: 1 });
  for (let xR = 325; xR <= 670; xR += 15) {
    linea(xR, 60, xR, 140, { fill: "#222222", width: 1 });
    linea(xR, 480, xR, 560, { fill: "#222222", width: 1 });
  }
  rect(140, 220, 80, 160, { outline: "#222222", width: 1 });
  rect(780, 220, 80, 160, { outline: "#222222", width: 1 });
  for (let yR = 225; yR <= 375; yR += 15) {
    linea(140, yR, 220, yR, { fill: "#222222", width: 1 });
    linea(780, yR, 860, yR, { fill: "#222222", width: 1 });
  }
  for (const [xU, yU] of [[420, 140], [580, 140], [420, 460], [580, 460]]) {
    linea(xU, yU, xU, yU + 20, { fill: "#222222", width: 2 });
  }
  linea(220, 260, 240, 260, { fill: "#222222", width: 2 });
  linea(220, 340, 240, 340, { fill: "#222222", width: 2 });
  linea(760, 260, 780, 260, { fill: "#222222", width: 2 });
  linea(760, 340, 780, 340, { fill: "#222222", width: 2 });
  const bujesY = monofasico
    ? [[320, 280, "Y1"], [320, 360, "Y2"]]
    : [[300, 250, "Y1"], [300, 330, "Y2"], [300, 410, "Y3"]];
  const [radioY, radioY2, radioY3] = monofasico ? [14, 7, 3] : [12, 6, 2];
  for (const [cxY, cyY, nombre] of bujesY) {
    ovalo(cxY, cyY, radioY, { fill: "#FFFFFF", outline: naranja, width: 2 });
    ovalo(cxY, cyY, radioY2, { outline: naranja, width: 1 });
    ovalo(cxY, cyY, radioY3, { fill: naranja, outline: naranja });
    texto(cxY, cyY + 35, nombre, 12, naranja, true, "center");
  }
  const paresHx = monofasico
    ? [[480, 250, 340, "H1", "X1"]]
    : [[420, 220, 300, "H1", "X1"], [530, 220, 300, "H2", "X2"], [640, 220, 300, "H3", "X3"]];
  for (const [cx, cyH, cyX, nomH, nomX] of paresHx) {
    ovalo(cx, cyH, 16, { fill: "#FFFFFF", outline: rojo, width: 2 });
    ovalo(cx, cyH, 9, { outline: rojo, width: 1 });
    ovalo(cx, cyH, 4, { fill: rojo, outline: rojo });
    texto(cx, cyH + 35, nomH, 12, rojo, true, "center");
    ovalo(cx, cyX, 14, { fill: "#FFFFFF", outline: azul, width: 2 });
    ovalo(cx, cyX, 7, { outline: azul, width: 1 });
    ovalo(cx, cyX, 3, { fill: azul, outline: azul });
    texto(cx, cyX + 35, nomX, 12, azul, true, "center");
  }
  const [nx, ny, radioN, radioN2] = monofasico ? [640, 290, 20, 12] : [530, 400, 18, 11];
  ovalo(nx, ny, radioN, { fill: "#FFFFFF", outline: gris, width: 2 });
  ovalo(nx, ny, radioN2, { outline: gris, width: 1 });
  ovalo(nx, ny, 5, { fill: gris, outline: gris });
  texto(nx - 32, ny + 2, "H0 / X0", 14, gris, true, "e");
  texto(nx - 32, ny + 18, "(Neutro)", 11, gris, false, "e");
  ovalo(730, 400, 10, { outline: "#222222", width: 1 });
  linea(720, 400, 740, 400, { fill: "#222222", width: 1 });
  linea(730, 390, 730, 410, { fill: "#222222", width: 1 });
  rect(736, monofasico ? 220 : 250, 14, 6, { outline: "#222222", width: 1 });
  rect(250, 250, 14, 6, { outline: "#222222", width: 1 });
  const etiquetasLat = [
    [180, "PRIMARIO (H)", monofasico ? "(H1)" : "(H1, H2, H3)", rojo],
    [240, "SECUNDARIO (X)", monofasico ? "(X1)" : "(X1, X2, X3)", azul],
    [380, "TERCIARIO (Y)", monofasico ? "(Y1, Y2)" : "(Y1, Y2, Y3 - Delta)", naranja],
    [500, "NEUTRO COMÚN", "(H0 / X0)", gris],
  ];
  for (const [yEt, tituloEt, subEt, colorEt] of etiquetasLat) {
    rect(2, yEt - 16, 136, 44, { fill: "#FFFFFF" });
    texto(-8, yEt, tituloEt, 12, colorEt);
    texto(-8, yEt + 20, subEt, 10, colorEt, false);
  }
  texto(475, 630, monofasico ? "AUTOTRANSFORMADOR DE POTENCIA MONOFÁSICO" : "AUTOTRANSFORMADOR DE POTENCIA TRIFÁSICO", 20, "#222222", true, "center");
  texto(475, 655, "CON TERCIARIO Y NEUTRO COMÚN (VISTA DE PLANTA)", 16, "#222222", true, "center");
  texto(475, 685, monofasico ? "Terciario (Izquierda): Y1, Y2" : "Terciario (Izquierda): Y1, Y2, Y3 (Delta)", 14, "#555555", false, "center");
  texto(475, 705, monofasico ? "Devanado Compartido (Centro): H1 - X1" : "Devanados Compartidos: H1-X1 | H2-X2 | H3-X3", 14, "#555555", false, "center");
  texto(475, 725, monofasico ? "Punto Neutro Común (Derecha): H0 / X0" : "Punto Neutro Común (Centro): H0 / X0", 14, "#555555", false, "center");
  return svg();
}

function dibujarDiagramaReactor() {
  const s = 0.62;
  const { rect, ovalo, linea, texto, svg } = _anexoLienzo(950, 750, s);
  const rojo = _ROJO_DIAG, gris = "#333333";
  rect(220, 140, 560, 320, { outline: "#222222", width: 2 });
  rect(235, 155, 530, 290, { outline: "#222222", width: 1, dash: [4, 4] });
  for (let xT = 250; xT <= 750; xT += 50) {
    ovalo(xT, 150, 2, { fill: "#222222", outline: "#222222" });
    ovalo(xT, 450, 2, { fill: "#222222", outline: "#222222" });
  }
  for (let yT = 180; yT <= 430; yT += 50) {
    ovalo(230, yT, 2, { fill: "#222222", outline: "#222222" });
    ovalo(770, yT, 2, { fill: "#222222", outline: "#222222" });
  }
  rect(320, 60, 360, 80, { outline: "#222222", width: 1 });
  rect(320, 460, 360, 80, { outline: "#222222", width: 1 });
  for (let xR = 325; xR <= 670; xR += 15) {
    linea(xR, 60, xR, 140, { fill: "#222222", width: 1 });
    linea(xR, 460, xR, 540, { fill: "#222222", width: 1 });
  }
  rect(140, 220, 80, 160, { outline: "#222222", width: 1 });
  rect(780, 220, 80, 160, { outline: "#222222", width: 1 });
  for (let yR = 225; yR <= 375; yR += 15) {
    linea(140, yR, 220, yR, { fill: "#222222", width: 1 });
    linea(780, yR, 860, yR, { fill: "#222222", width: 1 });
  }
  for (const [xU, yU] of [[420, 140], [580, 140], [420, 440], [580, 440]]) {
    linea(xU, yU, xU, yU + 20, { fill: "#222222", width: 2 });
  }
  linea(220, 260, 240, 260, { fill: "#222222", width: 2 });
  linea(220, 340, 240, 340, { fill: "#222222", width: 2 });
  linea(760, 260, 780, 260, { fill: "#222222", width: 2 });
  linea(760, 340, 780, 340, { fill: "#222222", width: 2 });
  ovalo(420, 210, 18, { fill: "#FFFFFF", outline: rojo, width: 2 });
  ovalo(420, 210, 10, { outline: rojo, width: 1 });
  ovalo(420, 210, 5, { fill: rojo, outline: rojo });
  texto(420, 245, "H1", 14, rojo, true, "center");
  ovalo(580, 210, 18, { fill: "#FFFFFF", outline: gris, width: 2 });
  ovalo(580, 210, 10, { outline: gris, width: 1 });
  ovalo(580, 210, 5, { fill: gris, outline: gris });
  texto(580, 245, "H0", 14, gris, true, "center");
  for (const cx of [290, 710]) {
    ovalo(cx, 390, 12, { outline: "#222222", width: 1 });
    linea(cx - 12, 390, cx + 12, 390, { fill: "#222222", width: 1 });
    linea(cx, 378, cx, 402, { fill: "#222222", width: 1 });
  }
  for (const [yEt, tituloEt, subEt, colorEt] of [
    [195, "ALTA TENSIÓN", "(Fase - H1)", rojo],
    [495, "NEUTRO", "(H0)", gris],
  ]) {
    rect(2, yEt - 16, 136, 44, { fill: "#FFFFFF" });
    texto(8, yEt, tituloEt, 12, colorEt);
    texto(8, yEt + 19, subEt, 10, colorEt, false);
  }
  texto(475, 610, "REACTOR DE POTENCIA MONOFÁSICO", 20, "#222222", true, "center");
  texto(475, 635, "VISTA DE PLANTA", 16, "#222222", true, "center");
  texto(475, 665, "Conexión de Fase (Alta Tensión): H1", 14, "#555555", false, "center");
  texto(475, 685, "Conexión de Neutro: H0", 14, "#555555", false, "center");
  return svg();
}

function dibujarDiagramaApartarrayos() {
  const s = 0.62;
  const { rect, ovalo, linea, poligono, texto, svg } = _anexoLienzo(950, 850, s);
  const rojo = _ROJO_DIAG, verde = "#005500";
  linea(475, 40, 475, 90, { fill: rojo, width: 4 });
  ovalo(475, 40, 8, { fill: rojo, outline: rojo });
  texto(495, 50, "H1", 18, rojo);
  rect(425, 90, 100, 20, { fill: "#A0A0A0", outline: "#333333", width: 2 });
  rect(435, 110, 80, 15, { fill: "#909090", outline: "#333333", width: 1 });
  rect(460, 125, 30, 480, { fill: "#F9F9F9", outline: "#888888", width: 1 });
  const secciones = [
    [130, 5, "#EEEEEE", "Sección 4", 200],
    [305, 5, "#F4F4F4", "Sección 3", 375],
    [480, 3, "#EEEEEE", "Sección 2", 525],
    [595, 2, "#F4F4F4", "Sección 1", 625],
  ];
  for (const [y0, cantidad, relleno, nombre, yNombre] of secciones) {
    for (let i = 0; i < cantidad; i++) {
      rect(405, y0 + 30 * i, 140, 20, { fill: relleno, outline: "#555555", width: 1 });
    }
    texto(560, yNombre, nombre, 14, "#333333");
  }
  for (const yBrida of [280, 455, 570]) {
    rect(435, yBrida, 80, 15, { fill: "#A0A0A0", outline: "#333333", width: 2 });
  }
  rect(425, 655, 100, 20, { fill: "#A0A0A0", outline: "#333333", width: 2 });
  poligono([[380, 675], [570, 675], [590, 750], [360, 750]], { fill: "#B0B0B0", outline: "#333333", width: 2 });
  rect(370, 675, 210, 10, { fill: "#909090", outline: "#333333", width: 2 });
  linea(380, 720, 300, 720, { fill: verde, width: 3 });
  ovalo(380, 720, 6, { fill: verde, outline: verde });
  texto(380, 700, "T", 16, verde, true, "center");
  linea(260, 720, 300, 720, { fill: verde, width: 3 });
  linea(268, 730, 292, 730, { fill: verde, width: 3 });
  linea(276, 740, 284, 740, { fill: verde, width: 3 });
  for (const [yEt, tituloEt, subEt, colorEt] of [
    [80, "ALTA TENSIÓN", "(Fase - H1)", rojo],
    [650, "PUESTA A TIERRA", "(Base Metálica - T)", verde],
  ]) {
    rect(2, yEt - 18, 228, 50, { fill: "#FFFFFF" });
    texto(8, yEt, tituloEt, 14, colorEt);
    texto(8, yEt + 22, subEt, 11, colorEt, false);
  }
  texto(475, 800, "APARTARRAYOS DE ÓXIDO DE ZINC (ZnO) DE 4 SECCIONES", 16, "#222222", true, "center");
  texto(475, 825, "VISTA DE ALZADO (LATERAL)", 14, "#222222", true, "center");
  return svg();
}

// Elige el diagrama según el tipo de equipo (mismo criterio que
// dibujo_equipo en el Anexo A de FP y los formato_* de RA).
function diagramaAnexoRa(equipoId, datos) {
  const mono = datos && datos.configuracion === "Monofásico";
  if (equipoId === "tc") return dibujarDiagramaTc();
  if (equipoId === "tp" || equipoId === "tpc") return dibujarDiagramaTp();
  if (equipoId === "2d") return dibujarDiagramaTransformador(false, mono);
  if (equipoId === "3d") return dibujarDiagramaTransformador(true, false);
  if (equipoId === "auto") return dibujarDiagramaAutotransformador(mono);
  if (equipoId === "reactor") return dibujarDiagramaReactor();
  if (equipoId === "apart") return dibujarDiagramaApartarrayos();
  return "";
}

function diagramaAnexoFp(equipo, datos, roles = null) {
  const mono = datos && datos.configuracion === "Monofásico";
  if (equipo.includes("Corriente")) return dibujarDiagramaTc();
  if (equipo.includes("Capacitivo")) return dibujarDiagramaTpc();
  if (equipo.includes("Potencial - TPs")) return dibujarDiagramaTp();
  if (equipo.includes("2 Devanados")) return dibujarDiagramaTransformador(false, mono, roles);
  if (equipo.includes("3 Devanados") && !mono) return dibujarDiagramaTransformador(true, false, roles);
  if (equipo.includes("Autotransformadores")) return dibujarDiagramaAutotransformador(mono);
  if (equipo.includes("Reactores")) return dibujarDiagramaReactor();
  if (equipo.includes("Apartarrayos")) return dibujarDiagramaApartarrayos();
  return "";
}
