// Logo "CFE" en 3D (Three.js, "Plasma Solar") para el menú principal del
// móvil. Vive dentro de #logo-cfe-3d, con el tamaño de ese contenedor (no
// pantalla completa). Si no hay internet para bajar Three.js o el celular
// no soporta WebGL, se queda el logo de texto de respaldo del contenedor.
"use strict";

const _CFE3D_FUENTE = "https://unpkg.com/three@0.160.0/examples/fonts/helvetiker_bold.typeface.json";

let _cfe3dModulo = null;
let _cfe3dActivo = null;

async function _cargarThree() {
  if (_cfe3dModulo) return _cfe3dModulo;
  const [THREE, controles, fuentes, geometriaTexto, composer, renderPass, bloom] = await Promise.all([
    import("three"),
    import("three/addons/controls/OrbitControls.js"),
    import("three/addons/loaders/FontLoader.js"),
    import("three/addons/geometries/TextGeometry.js"),
    import("three/addons/postprocessing/EffectComposer.js"),
    import("three/addons/postprocessing/RenderPass.js"),
    import("three/addons/postprocessing/UnrealBloomPass.js"),
  ]);
  _cfe3dModulo = {
    THREE,
    OrbitControls: controles.OrbitControls,
    FontLoader: fuentes.FontLoader,
    TextGeometry: geometriaTexto.TextGeometry,
    EffectComposer: composer.EffectComposer,
    RenderPass: renderPass.RenderPass,
    UnrealBloomPass: bloom.UnrealBloomPass,
  };
  return _cfe3dModulo;
}

function detenerCfe3D() {
  if (!_cfe3dActivo) return;
  const act = _cfe3dActivo;
  _cfe3dActivo = null;
  act.vivo = false;
  if (act.raf) cancelAnimationFrame(act.raf);
  if (act.resize) window.removeEventListener("resize", act.resize);
  if (act.renderer) {
    act.renderer.dispose();
    const lienzo = act.renderer.domElement;
    if (lienzo && lienzo.parentNode) lienzo.parentNode.removeChild(lienzo);
  }
}

function _inclinar(THREE, geometria) {
  geometria.center();
  const matriz = new THREE.Matrix4();
  matriz.set(1, 0.25, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1);
  geometria.applyMatrix4(matriz);
  return geometria;
}

// Nube de puntos esparcidos sobre una esfera de radio [radioMin, radioMin+extra].
function _campoEstrellas(THREE, escena, cuenta, color, tamano, velocidad, radioMin, extra) {
  const geometria = new THREE.BufferGeometry();
  const posiciones = new Float32Array(cuenta * 3);
  for (let i = 0; i < cuenta; i++) {
    const r = radioMin + Math.random() * extra;
    const theta = Math.random() * Math.PI * 2;
    const phi = Math.acos((Math.random() * 2) - 1);
    posiciones[i * 3] = r * Math.sin(phi) * Math.cos(theta);
    posiciones[i * 3 + 1] = r * Math.sin(phi) * Math.sin(theta);
    posiciones[i * 3 + 2] = r * Math.cos(phi);
  }
  geometria.setAttribute("position", new THREE.BufferAttribute(posiciones, 3));
  const material = new THREE.PointsMaterial({
    size: tamano, color, transparent: true, opacity: 0.9,
    blending: THREE.AdditiveBlending, depthWrite: false,
  });
  const estrellas = new THREE.Points(geometria, material);
  estrellas.userData = { velocidad };
  escena.add(estrellas);
  return estrellas;
}

// Nube de puntos esparcidos en un cubo de lado `extension`.
function _particulasPlasma(THREE, escena, cuenta, color, tamano, extension, opacidad) {
  const geometria = new THREE.BufferGeometry();
  const posiciones = new Float32Array(cuenta * 3);
  for (let i = 0; i < cuenta * 3; i++) {
    posiciones[i] = (Math.random() - 0.5) * extension;
  }
  geometria.setAttribute("position", new THREE.BufferAttribute(posiciones, 3));
  const material = new THREE.PointsMaterial({
    size: tamano, color, transparent: true, opacity: opacidad ?? 0.8,
    blending: THREE.AdditiveBlending, depthWrite: false,
  });
  const particulas = new THREE.Points(geometria, material);
  escena.add(particulas);
  return particulas;
}

async function iniciarCfe3D(contenedor) {
  detenerCfe3D();
  if (!contenedor || typeof WebGLRenderingContext === "undefined") return;
  let mod;
  try {
    mod = await _cargarThree();
  } catch (_e) {
    return; // Sin internet: se queda el logo de texto de respaldo.
  }
  if (!contenedor.isConnected) return; // El usuario ya cambió de pantalla.
  const {
    THREE, OrbitControls, FontLoader, TextGeometry,
    EffectComposer, RenderPass, UnrealBloomPass,
  } = mod;

  const ancho = () => contenedor.clientWidth || 320;
  const alto = () => contenedor.clientHeight || 200;

  const escena = new THREE.Scene();
  escena.background = new THREE.Color(0x010a08);
  escena.fog = new THREE.FogExp2(0x010a08, 0.03);
  const camara = new THREE.PerspectiveCamera(45, ancho() / alto(), 0.1, 1000);
  camara.position.set(0, 0, 22);

  let renderer;
  try {
    renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
  } catch (_e) {
    return; // Celular sin WebGL.
  }
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.setSize(ancho(), alto());
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));

  const estadoLocal = { vivo: true, raf: 0, renderer, plasma: null };
  _cfe3dActivo = estadoLocal;
  contenedor.innerHTML = "";
  contenedor.appendChild(renderer.domElement);

  const controles = new OrbitControls(camara, renderer.domElement);
  controles.enableDamping = true;
  controles.enableZoom = false;
  controles.enablePan = false;
  controles.enableRotate = false;
  controles.autoRotate = true;
  controles.autoRotateSpeed = 1.5;

  new FontLoader().load(_CFE3D_FUENTE, (fuente) => {
    if (!estadoLocal.vivo) return;
    const matVerde = new THREE.MeshStandardMaterial({
      color: 0x008e60, emissive: 0x00ff88, emissiveIntensity: 2.0,
      roughness: 0.1, metalness: 0.8,
    });
    const matBlanco = new THREE.MeshStandardMaterial({
      color: 0xffffff, emissive: 0xffffff, emissiveIntensity: 1.0,
      roughness: 0.2, metalness: 0.2,
    });
    const matVerdeOscuro = new THREE.MeshStandardMaterial({
      color: 0x001a12, emissive: 0x003322, emissiveIntensity: 0.2,
      roughness: 0.4, metalness: 0.3,
    });

    const geoExterior = _inclinar(THREE, new TextGeometry("CFE", {
      font: fuente, size: 7, height: 1.0, curveSegments: 32,
      bevelEnabled: true, bevelThickness: 0.1, bevelSize: 0.25, bevelSegments: 6,
    }));
    escena.add(new THREE.Mesh(geoExterior, matVerde));

    const geoBlanco = _inclinar(THREE, new TextGeometry("CFE", {
      font: fuente, size: 7, height: 1.1, curveSegments: 32,
      bevelEnabled: true, bevelThickness: 0.1, bevelSize: 0.1, bevelSegments: 6,
    }));
    escena.add(new THREE.Mesh(geoBlanco, matBlanco));

    const geoCentral = _inclinar(THREE, new TextGeometry("CFE", {
      font: fuente, size: 7, height: 1.15, curveSegments: 32,
      bevelEnabled: true, bevelThickness: 0.1, bevelSize: 0.0, bevelSegments: 4,
    }));
    escena.add(new THREE.Mesh(geoCentral, matVerdeOscuro));

    // Aura de plasma: una capa un poco más grande con un shader que agita
    // ruido entre dos colores y le suma un brillo de borde (fresnel).
    const geoAura = _inclinar(THREE, new TextGeometry("CFE", {
      font: fuente, size: 7.3, height: 1.0, curveSegments: 32,
      bevelEnabled: true, bevelThickness: 0.1, bevelSize: 0.3, bevelSegments: 6,
    }));
    const matPlasma = new THREE.ShaderMaterial({
      uniforms: {
        time: { value: 0 },
        color1: { value: new THREE.Color(0x00ff88) },
        color2: { value: new THREE.Color(0xffaa00) },
      },
      vertexShader: `
        varying vec3 vNormal;
        varying vec3 vPosition;
        void main() {
          vNormal = normalize(normalMatrix * normal);
          vPosition = position;
          gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
        }
      `,
      fragmentShader: `
        uniform float time;
        uniform vec3 color1;
        uniform vec3 color2;
        varying vec3 vNormal;
        varying vec3 vPosition;
        float noise(vec3 p) {
          return fract(sin(dot(p, vec3(12.9898, 78.233, 45.164))) * 43758.5453);
        }
        void main() {
          float n = noise(vPosition * 0.5 + time * 2.0);
          vec3 finalColor = mix(color1, color2, n * 0.3);
          float fresnel = pow(1.0 - abs(dot(vNormal, vec3(0.0, 0.0, 1.0))), 3.0);
          finalColor += vec3(0.0, 1.0, 0.5) * fresnel * 1.5;
          gl_FragColor = vec4(finalColor, 0.6 + (n * 0.4));
        }
      `,
      transparent: true,
      blending: THREE.AdditiveBlending,
      depthWrite: false,
    });
    escena.add(new THREE.Mesh(geoAura, matPlasma));
    estadoLocal.plasma = matPlasma;
  });

  escena.add(new THREE.AmbientLight(0xffffff, 0.2));
  const luzDir = new THREE.DirectionalLight(0x00ff88, 2);
  luzDir.position.set(5, 10, 7);
  escena.add(luzDir);
  const luz1 = new THREE.PointLight(0x00ff88, 100, 50);
  luz1.position.set(10, 5, 10);
  escena.add(luz1);

  const estrellasAzules = _campoEstrellas(THREE, escena, 500, 0x88aaff, 0.25, 0.02, 30, 20);
  const estrellasBlancas = _campoEstrellas(THREE, escena, 400, 0xffffff, 0.2, 0.015, 30, 20);
  const estrellasAmarillas = _campoEstrellas(THREE, escena, 300, 0xffdd55, 0.3, 0.01, 30, 20);

  const particulasAzules = _particulasPlasma(THREE, escena, 400, 0x0088ff, 0.15, 40);
  const particulasBlancas = _particulasPlasma(THREE, escena, 400, 0xffffff, 0.12, 40);
  const particulasRojas = _particulasPlasma(THREE, escena, 400, 0xff3333, 0.18, 40);
  const particulasMoradas = _particulasPlasma(THREE, escena, 300, 0xaa00ff, 0.2, 40);
  const particulasAmarillas = _particulasPlasma(THREE, escena, 300, 0xffff00, 0.15, 40);
  const polvoRosa = _particulasPlasma(THREE, escena, 200, 0xff69b4, 0.5, 60, 0.4);

  const composer = new EffectComposer(renderer);
  composer.addPass(new RenderPass(escena, camara));
  composer.addPass(new UnrealBloomPass(
    new THREE.Vector2(ancho(), alto()), 1.5, 0.6, 0.1,
  ));

  const redimensionar = () => {
    if (!contenedor.isConnected) return;
    const a = ancho(), h = alto();
    camara.aspect = a / h;
    camara.updateProjectionMatrix();
    renderer.setSize(a, h);
    composer.setSize(a, h);
  };
  window.addEventListener("resize", redimensionar);
  estadoLocal.resize = redimensionar;

  const reloj = new THREE.Clock();
  const animar = () => {
    if (!estadoLocal.vivo || !contenedor.isConnected) {
      detenerCfe3D();
      return;
    }
    estadoLocal.raf = requestAnimationFrame(animar);
    const t = reloj.getElapsedTime();
    controles.update();
    if (estadoLocal.plasma) estadoLocal.plasma.uniforms.time.value = t;

    estrellasAzules.rotation.y = t * estrellasAzules.userData.velocidad;
    estrellasBlancas.rotation.y = t * estrellasBlancas.userData.velocidad;
    estrellasBlancas.rotation.x = t * estrellasBlancas.userData.velocidad * 0.5;
    estrellasAmarillas.rotation.y = t * estrellasAmarillas.userData.velocidad;
    estrellasAmarillas.rotation.z = t * estrellasAmarillas.userData.velocidad * 0.5;

    particulasAzules.rotation.y = t * 0.05;
    particulasAzules.rotation.x = t * 0.02;
    particulasBlancas.rotation.y = t * -0.04;
    particulasBlancas.rotation.z = t * 0.03;
    particulasRojas.rotation.y = t * 0.06;
    particulasRojas.rotation.x = t * -0.03;
    particulasMoradas.rotation.x = t * 0.04;
    particulasMoradas.rotation.z = t * 0.05;
    particulasAmarillas.rotation.y = t * -0.03;
    particulasAmarillas.rotation.z = t * -0.04;
    polvoRosa.rotation.y = t * 0.01;
    polvoRosa.rotation.x = t * 0.005;

    composer.render();
  };
  animar();
}
