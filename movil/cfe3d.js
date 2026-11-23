// Logo "CFE" en 3D (Three.js) para el menú principal del móvil. Vive dentro
// de #logo-cfe-3d, con el tamaño de ese contenedor (no pantalla completa).
// Si no hay internet para bajar Three.js o el celular no soporta WebGL, se
// queda el logo de texto de respaldo que ya trae el contenedor.
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
  escena.background = new THREE.Color(0x050b14); // mismo fondo oscuro de la app.
  const camara = new THREE.PerspectiveCamera(45, ancho() / alto(), 0.1, 1000);
  camara.position.set(0, 0, 20);

  let renderer;
  try {
    renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
  } catch (_e) {
    return; // Celular sin WebGL.
  }
  renderer.setSize(ancho(), alto());
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));

  const estadoLocal = { vivo: true, raf: 0, renderer };
  _cfe3dActivo = estadoLocal;
  contenedor.innerHTML = "";
  contenedor.appendChild(renderer.domElement);

  const controles = new OrbitControls(camara, renderer.domElement);
  controles.enableDamping = true;
  controles.enableZoom = false;
  controles.enablePan = false;
  controles.enableRotate = false;
  controles.autoRotate = true;
  controles.autoRotateSpeed = 2.4;

  new FontLoader().load(_CFE3D_FUENTE, (fuente) => {
    if (!estadoLocal.vivo) return;
    const matVerde = new THREE.MeshStandardMaterial({
      color: 0x008e60, emissive: 0x00b378, emissiveIntensity: 1.5,
      roughness: 0.2, metalness: 0.1,
    });
    const matBlanco = new THREE.MeshStandardMaterial({
      color: 0xffffff, emissive: 0xffffff, emissiveIntensity: 1.2, roughness: 0.2,
    });
    const geoExterior = _inclinar(THREE, new TextGeometry("CFE", {
      font: fuente, size: 7, height: 1.0, curveSegments: 24,
      bevelEnabled: true, bevelThickness: 0.1, bevelSize: 0.25, bevelSegments: 4,
    }));
    escena.add(new THREE.Mesh(geoExterior, matVerde));
    const geoInterior = _inclinar(THREE, new TextGeometry("CFE", {
      font: fuente, size: 7, height: 1.05, curveSegments: 24,
      bevelEnabled: true, bevelThickness: 0.1, bevelSize: 0.1, bevelSegments: 4,
    }));
    escena.add(new THREE.Mesh(geoInterior, [matVerde, matBlanco]));
  });

  escena.add(new THREE.AmbientLight(0xffffff, 0.5));
  const luz1 = new THREE.PointLight(0x008e60, 60, 50);
  luz1.position.set(10, 10, 10);
  escena.add(luz1);
  const luz2 = new THREE.PointLight(0x008e60, 40, 50);
  luz2.position.set(-10, -5, 5);
  escena.add(luz2);

  const composer = new EffectComposer(renderer);
  composer.addPass(new RenderPass(escena, camara));
  composer.addPass(new UnrealBloomPass(
    new THREE.Vector2(ancho(), alto()), 0.8, 0.4, 0.7,
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

  const animar = () => {
    if (!estadoLocal.vivo || !contenedor.isConnected) {
      detenerCfe3D();
      return;
    }
    estadoLocal.raf = requestAnimationFrame(animar);
    controles.update();
    composer.render();
  };
  animar();
}
