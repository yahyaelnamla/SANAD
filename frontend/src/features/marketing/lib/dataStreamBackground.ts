/**
 * Islamic-FinTech Neural Network Background
 *
 * Procedural GLSL: Arabic calligraphy, Rub el Hizb stars, crypto glyphs,
 * and live market data segments — single InstancedMesh + grid shaders.
 * Midnight FinTech palette with center masking for text readability.
 */

import * as THREE from "three";

export type DataStreamTheme = "dark" | "gold";

interface ThemePalette {
  bgColor: number;
  gridColor: number;
  primaryColor: number;
  secondaryColor: number;
  fogDensity: number;
  baseOpacity: number;
}

const THEMES: Record<DataStreamTheme, ThemePalette> = {
  dark: {
    bgColor: 0x020617,
    gridColor: 0x1e293b,
    primaryColor: 0x00f2ff,
    secondaryColor: 0xd4af37,
    fogDensity: 0.05,
    baseOpacity: 0.06,
  },
  gold: {
    bgColor: 0x050505,
    gridColor: 0x2a2a2a,
    primaryColor: 0xd4af37,
    secondaryColor: 0xffd700,
    fogDensity: 0.045,
    baseOpacity: 0.07,
  },
};

interface InstanceData {
  position: THREE.Vector3;
  speed: number;
  noiseOffset: number;
  rotSpeed: number;
  baseScale: number;
  glitchSeed: number;
}

export class DataStreamBackground {
  private container: HTMLElement;
  private scene: THREE.Scene;
  private camera: THREE.PerspectiveCamera;
  private renderer: THREE.WebGLRenderer;
  private mouse: THREE.Vector2;
  private targetMouse: THREE.Vector2;
  private clock: THREE.Clock;
  private theme: DataStreamTheme;
  private params: {
    elementCount: number;
    bgColor: THREE.Color;
    gridColor: THREE.Color;
    primaryColor: THREE.Color;
    secondaryColor: THREE.Color;
    baseOpacity: number;
    fogDensity: number;
  };
  private gridMaterial: THREE.ShaderMaterial | null = null;
  private networkMaterial: THREE.ShaderMaterial | null = null;
  private instancedMesh: THREE.InstancedMesh | null = null;
  private instanceData: InstanceData[] = [];
  private animationId: number | null = null;
  private disposed = false;
  private readonly onMouseMoveBound: (e: MouseEvent) => void;
  private readonly onResizeBound: () => void;
  private readonly dummy = new THREE.Object3D();

  constructor(container: HTMLElement, theme: DataStreamTheme = "dark") {
    this.container = container;
    this.theme = theme;
    this.scene = new THREE.Scene();
    this.camera = new THREE.PerspectiveCamera(68, 1, 0.1, 1000);
    this.renderer = new THREE.WebGLRenderer({
      alpha: true,
      antialias: true,
      powerPreference: "high-performance",
    });

    this.mouse = new THREE.Vector2(0, 0);
    this.targetMouse = new THREE.Vector2(0, 0);
    this.clock = new THREE.Clock();

    const palette = THEMES[theme];
    this.params = {
      elementCount: 400,
      bgColor: new THREE.Color(palette.bgColor),
      gridColor: new THREE.Color(palette.gridColor),
      primaryColor: new THREE.Color(palette.primaryColor),
      secondaryColor: new THREE.Color(palette.secondaryColor),
      baseOpacity: palette.baseOpacity,
      fogDensity: palette.fogDensity,
    };

    this.onMouseMoveBound = (e) => this.onMouseMove(e);
    this.onResizeBound = () => this.onResize();

    this.init();
  }

  setTheme(mode: DataStreamTheme) {
    if (mode === this.theme) return;
    this.theme = mode;
    const palette = THEMES[mode];
    this.params.bgColor.set(palette.bgColor);
    this.params.gridColor.set(palette.gridColor);
    this.params.primaryColor.set(palette.primaryColor);
    this.params.secondaryColor.set(palette.secondaryColor);
    this.params.baseOpacity = palette.baseOpacity;
    this.params.fogDensity = palette.fogDensity;

    if (this.scene.fog) {
      (this.scene.fog as THREE.FogExp2).color.copy(this.params.bgColor);
      (this.scene.fog as THREE.FogExp2).density = palette.fogDensity;
    }

    if (this.gridMaterial) {
      this.gridMaterial.uniforms.uGridColor.value.copy(this.params.gridColor);
      this.gridMaterial.uniforms.uGlowColor.value.copy(this.params.primaryColor);
      this.gridMaterial.uniforms.uOpacity.value = palette.baseOpacity;
    }

    if (this.networkMaterial) {
      this.networkMaterial.uniforms.uPrimaryColor.value.copy(this.params.primaryColor);
      this.networkMaterial.uniforms.uSecondaryColor.value.copy(this.params.secondaryColor);
      this.networkMaterial.uniforms.uBaseOpacity.value = palette.baseOpacity;
    }
  }

  private init() {
    const width = this.container.clientWidth || window.innerWidth;
    const height = this.container.clientHeight || window.innerHeight;

    this.renderer.setSize(width, height, false);
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    this.renderer.domElement.style.display = "block";
    this.renderer.domElement.style.width = "100%";
    this.renderer.domElement.style.height = "100%";
    this.container.appendChild(this.renderer.domElement);

    this.camera.aspect = width / height;
    this.camera.updateProjectionMatrix();
    this.camera.position.set(0, 2, 12);

    this.scene.fog = new THREE.FogExp2(this.params.bgColor.getHex(), this.params.fogDensity);

    this.createBackdrop();
    this.createGrid();
    this.createNeuralNetwork();

    window.addEventListener("mousemove", this.onMouseMoveBound);
    window.addEventListener("resize", this.onResizeBound);

    this.animate();
  }

  private createBackdrop() {
    const geometry = new THREE.PlaneGeometry(200, 200);
    const material = new THREE.ShaderMaterial({
      uniforms: {
        uBgInner: { value: new THREE.Color(0x0f172a) },
        uBgOuter: { value: this.params.bgColor.clone() },
      },
      vertexShader: `
        varying vec2 vUv;
        void main() {
          vUv = uv;
          gl_Position = vec4(position.xy, 0.999, 1.0);
        }
      `,
      fragmentShader: `
        varying vec2 vUv;
        uniform vec3 uBgInner;
        uniform vec3 uBgOuter;
        void main() {
          float d = length(vUv - 0.5) * 1.4;
          vec3 color = mix(uBgInner, uBgOuter, smoothstep(0.0, 1.0, d));
          gl_FragColor = vec4(color, 1.0);
        }
      `,
      depthWrite: false,
      depthTest: false,
    });

    const backdrop = new THREE.Mesh(geometry, material);
    this.scene.add(backdrop);
  }

  private createGrid() {
    const geometry = new THREE.PlaneGeometry(120, 120, 60, 60);
    geometry.rotateX(-Math.PI / 2);

    this.gridMaterial = new THREE.ShaderMaterial({
      transparent: true,
      depthWrite: false,
      uniforms: {
        uTime: { value: 0 },
        uMouse: { value: new THREE.Vector3(0, 0, 0) },
        uGridColor: { value: this.params.gridColor.clone() },
        uGlowColor: { value: this.params.primaryColor.clone() },
        uOpacity: { value: this.params.baseOpacity },
      },
      vertexShader: `
        varying vec3 vPosition;
        void main() {
          vPosition = position;
          gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
        }
      `,
      fragmentShader: `
        varying vec3 vPosition;
        uniform float uTime;
        uniform vec3 uMouse;
        uniform vec3 uGridColor;
        uniform vec3 uGlowColor;
        uniform float uOpacity;

        void main() {
          float lineX = step(0.98, fract(vPosition.x * 0.5));
          float lineZ = step(0.98, fract(vPosition.z * 0.5));
          float grid = max(lineX, lineZ);
          if (grid < 0.1) discard;

          float dist = distance(vPosition.xz, uMouse.xz);
          float glow = exp(-dist * 0.38);

          float centerDist = length(vPosition.xz);
          float centerMask = smoothstep(0.0, 18.0, centerDist);

          vec3 finalColor = mix(uGridColor, uGlowColor, glow * 0.85);
          float alpha = grid * uOpacity * (0.35 + glow * 2.5) * (0.55 + centerMask * 0.45);

          gl_FragColor = vec4(finalColor, alpha);
        }
      `,
    });

    const grid = new THREE.Mesh(geometry, this.gridMaterial);
    grid.position.y = -4;
    this.scene.add(grid);
  }

  private createNeuralNetwork() {
    const geometry = new THREE.PlaneGeometry(1, 1);

    this.networkMaterial = new THREE.ShaderMaterial({
      transparent: true,
      depthWrite: false,
      blending: THREE.AdditiveBlending,
      uniforms: {
        uTime: { value: 0 },
        uPrimaryColor: { value: this.params.primaryColor.clone() },
        uSecondaryColor: { value: this.params.secondaryColor.clone() },
        uBaseOpacity: { value: this.params.baseOpacity },
      },
      vertexShader: `
        varying vec2 vUv;
        varying float vInstanceId;
        varying vec3 vViewPosition;
        void main() {
          vUv = uv;
          vInstanceId = float(gl_InstanceID);
          vec4 mvPosition = modelViewMatrix * instanceMatrix * vec4(position, 1.0);
          vViewPosition = -mvPosition.xyz;
          gl_Position = projectionMatrix * mvPosition;
        }
      `,
      fragmentShader: `
        varying vec2 vUv;
        varying float vInstanceId;
        varying vec3 vViewPosition;
        uniform float uTime;
        uniform vec3 uPrimaryColor;
        uniform vec3 uSecondaryColor;
        uniform float uBaseOpacity;

        float hash(float n) { return fract(sin(n) * 43758.5453123); }

        float sdStar8(vec2 p, float r) {
          const vec2 s = vec2(0.9238, 0.3826);
          p = abs(p);
          p -= 2.0 * min(dot(s, p), 0.0) * s;
          s.xy = s.yx;
          p -= 2.0 * min(dot(s, p), 0.0) * s;
          return max(p.x - r, p.y - r);
        }

        void main() {
          vec2 uv = vUv * 2.0 - 1.0;
          float id = vInstanceId;
          float type = mod(id, 4.0);
          float shape = 0.0;
          vec3 color = uPrimaryColor;

          float glitchPulse = step(0.94, hash(floor(uTime * 6.0 + id * 0.17)));

          if (type < 1.0) {
            float wave = sin(uv.x * 3.5 + uTime * 0.6 + id) * 0.35;
            float curve = abs(uv.y - wave);
            shape = smoothstep(0.08, 0.0, curve) * smoothstep(1.0, 0.15, abs(uv.x));
            float stroke2 = abs(uv.y + uv.x * 0.4 - 0.1);
            shape = max(shape, smoothstep(0.06, 0.0, stroke2) * smoothstep(0.8, 0.0, abs(uv.x)));
            float dots = smoothstep(0.06, 0.0, length(uv - vec2(0.45, 0.25)))
              + smoothstep(0.05, 0.0, length(uv - vec2(-0.35, -0.3)));
            shape = max(shape, dots);
          } else if (type < 2.0) {
            shape = smoothstep(0.04, 0.0, abs(sdStar8(uv, 0.48)));
            shape += smoothstep(0.55, 0.5, length(uv)) * 0.25;
            color = uSecondaryColor;
            shape *= 0.7 + 0.3 * glitchPulse * 2.0;
          } else if (type < 3.0) {
            float ring = abs(length(uv) - 0.55);
            shape = smoothstep(0.04, 0.0, ring);
            float barTop = smoothstep(0.12, 0.08, abs(uv.x)) * step(abs(uv.y), 0.75) * step(0.15, abs(uv.x));
            float barBot = smoothstep(0.08, 0.04, abs(uv.x + 0.15)) * step(abs(uv.y), 0.5);
            shape = max(shape, barTop * 0.6 + barBot * 0.4);
          } else {
            float chart = abs(uv.y - (sin(uv.x * 4.0 + id) * 0.35 + hash(id) * 0.2));
            shape = smoothstep(0.09, 0.0, chart) * step(abs(uv.x), 0.75);
            float candle = step(0.04, abs(uv.x - 0.3)) * step(abs(uv.y), 0.5) * step(0.08, abs(uv.x - 0.3));
            shape = max(shape, candle * 0.5);
            shape *= 0.5 + 0.5 * sin(uTime * 5.0 + id) + glitchPulse * 0.4;
          }

          float viewDist = length(vViewPosition.xy);
          float depthFade = smoothstep(0.0, 35.0, vViewPosition.z);
          float centerMask = smoothstep(0.0, 2.8, viewDist * 0.12 + depthFade * 0.3);

          float alpha = shape * uBaseOpacity * centerMask;
          if (alpha < 0.001) discard;

          gl_FragColor = vec4(color, alpha);
        }
      `,
    });

    this.instancedMesh = new THREE.InstancedMesh(
      geometry,
      this.networkMaterial,
      this.params.elementCount,
    );

    this.instanceData = [];

    for (let i = 0; i < this.params.elementCount; i++) {
      const x = (Math.random() - 0.5) * 50;
      const y = (Math.random() - 0.5) * 28;
      const z = (Math.random() - 0.5) * 40;

      this.dummy.position.set(x, y, z);
      this.dummy.rotation.set(Math.random() * Math.PI, Math.random() * Math.PI, 0);
      const scale = 0.25 + Math.random() * 1.0;
      this.dummy.scale.setScalar(scale);
      this.dummy.updateMatrix();
      this.instancedMesh.setMatrixAt(i, this.dummy.matrix);

      this.instanceData.push({
        position: new THREE.Vector3(x, y, z),
        speed: 0.015 + Math.random() * 0.04,
        noiseOffset: Math.random() * 100,
        rotSpeed: (Math.random() - 0.5) * 0.008,
        baseScale: scale,
        glitchSeed: Math.random(),
      });
    }

    this.scene.add(this.instancedMesh);
  }

  private onMouseMove(e: MouseEvent) {
    const rect = this.container.getBoundingClientRect();
    const x = (e.clientX - rect.left) / rect.width;
    const y = (e.clientY - rect.top) / rect.height;
    this.targetMouse.x = x * 2 - 1;
    this.targetMouse.y = -(y * 2 - 1);
  }

  private onResize() {
    const width = this.container.clientWidth || window.innerWidth;
    const height = this.container.clientHeight || window.innerHeight;

    this.camera.aspect = width / height;
    this.camera.updateProjectionMatrix();
    this.renderer.setSize(width, height, false);
  }

  private animate() {
    if (this.disposed) return;

    this.animationId = window.requestAnimationFrame(() => this.animate());

    const elapsed = this.clock.getElapsedTime();
    this.mouse.lerp(this.targetMouse, 0.06);

    if (this.gridMaterial) {
      this.gridMaterial.uniforms.uTime.value = elapsed;
      this.gridMaterial.uniforms.uMouse.value.set(this.mouse.x * 28, 0, -this.mouse.y * 28);
    }

    if (this.instancedMesh && this.networkMaterial) {
      this.networkMaterial.uniforms.uTime.value = elapsed;

      for (let i = 0; i < this.params.elementCount; i++) {
        const data = this.instanceData[i];
        const noiseT = elapsed * 0.25 + data.noiseOffset;

        data.position.z += data.speed;
        data.position.x += Math.sin(noiseT) * 0.018 + Math.sin(noiseT * 0.37) * 0.008;
        data.position.y += Math.cos(noiseT * 0.9) * 0.015 + Math.sin(noiseT * 0.23) * 0.006;

        if (data.position.z > 22) data.position.z = -22;

        const depthFactor = (data.position.z + 22) / 44;
        const parallaxStrength = 0.08 + depthFactor * 0.22;
        const glitch =
          Math.sin(elapsed * 12 + data.glitchSeed * 50) > 0.97 ? 0.04 : 0;

        this.dummy.position.copy(data.position);
        this.dummy.position.x += this.mouse.x * parallaxStrength * 8 + glitch;
        this.dummy.position.y += this.mouse.y * parallaxStrength * 5;

        this.dummy.rotation.z += data.rotSpeed;
        this.dummy.scale.setScalar(data.baseScale);
        this.dummy.updateMatrix();
        this.instancedMesh.setMatrixAt(i, this.dummy.matrix);
      }
      this.instancedMesh.instanceMatrix.needsUpdate = true;
    }

    this.camera.position.x += (this.mouse.x * 3 - this.camera.position.x) * 0.012;
    this.camera.position.y += (2 + this.mouse.y * 1.8 - this.camera.position.y) * 0.012;
    this.camera.lookAt(0, 0, 0);

    this.renderer.render(this.scene, this.camera);
  }

  dispose() {
    this.disposed = true;

    if (this.animationId !== null) {
      window.cancelAnimationFrame(this.animationId);
      this.animationId = null;
    }

    window.removeEventListener("mousemove", this.onMouseMoveBound);
    window.removeEventListener("resize", this.onResizeBound);

    this.scene.traverse((object) => {
      if (object instanceof THREE.Mesh) {
        object.geometry.dispose();
        const material = object.material;
        if (Array.isArray(material)) {
          material.forEach((m) => m.dispose());
        } else {
          material.dispose();
        }
      }
    });

    this.renderer.dispose();

    if (this.container.contains(this.renderer.domElement)) {
      this.container.removeChild(this.renderer.domElement);
    }
  }
}
