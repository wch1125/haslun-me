/**
 * Parallax System
 * Handles multi-layer parallax with smooth rAF interpolation
 * Supports both static and animated layers
 */

const Parallax = {
  viewport: null,
  layers: [],
  maxShift: 15,
  
  // Smooth interpolation state
  targetX: 0.5,
  targetY: 0.5,
  currentX: 0.5,
  currentY: 0.5,
  smoothing: 0.08, // Lower = floatier, higher = snappier
  
  // Animation state for animated layers
  animatedLayers: [],
  frameIndex: 0,
  frameDirection: 1,
  frameDelay: 120,
  lastFrameTime: 0,
  
  // Atmosphere (optional, set by atmosphere.js)
  atmosphereColor: '#4a5568',
  
  init(options = {}) {
    this.viewport = document.getElementById('viewport');
    this.layers = Array.from(document.querySelectorAll('.parallax-layer'));
    
    // Allow customization
    if (options.smoothing) this.smoothing = options.smoothing;
    if (options.maxShift) this.maxShift = options.maxShift;
    if (options.frameDelay) this.frameDelay = options.frameDelay;
    
    this.onResize();
    this.setupAnimatedLayers();
    this.setupListeners();
    
    // Start the single rAF loop
    this.loop();
  },
  
  onResize() {
    const w = window.innerWidth;
    this.maxShift = w <= 480 ? 8 : w <= 768 ? 12 : 15;
  },
  
  setupAnimatedLayers() {
    this.layers.forEach(layer => {
      if (layer.dataset.animated === 'true') {
        const frameCount = parseInt(layer.dataset.frames) || 20;
        const folder = layer.dataset.folder;
        const img = layer.querySelector('img');
        
        // Preload all frames
        const frames = [];
        for (let i = 0; i < frameCount; i++) {
          const frameSrc = `${folder}/frame-${String(i).padStart(3, '0')}.png`;
          const frameImg = new Image();
          frameImg.src = frameSrc;
          frames.push(frameSrc);
        }
        
        this.animatedLayers.push({
          element: layer,
          img: img,
          frames: frames,
          frameCount: frameCount
        });
      }
    });
  },
  
  loop(timestamp = 0) {
    // Smooth interpolation toward target
    this.currentX += (this.targetX - this.currentX) * this.smoothing;
    this.currentY += (this.targetY - this.currentY) * this.smoothing;
    
    // Apply parallax transforms (GPU-accelerated with translate3d)
    const xNorm = this.currentX;
    const yNorm = this.currentY;
    
    for (const layer of this.layers) {
      const p = parseFloat(layer.dataset.parallax) || 0;
      const shiftX = (xNorm - 0.5) * this.maxShift * p;
      const shiftY = (yNorm - 0.5) * this.maxShift * p * 0.5;
      layer.style.transform = `translate3d(${shiftX}px, ${shiftY}px, 0)`;
    }
    
    // Update animated layers (ping-pong)
    if (this.animatedLayers.length > 0 && timestamp - this.lastFrameTime >= this.frameDelay) {
      this.lastFrameTime = timestamp;
      
      this.animatedLayers.forEach(layer => {
        const frameIdx = this.frameIndex % layer.frameCount;
        layer.img.src = layer.frames[frameIdx];
      });
      
      const maxFrames = Math.max(...this.animatedLayers.map(l => l.frameCount));
      this.frameIndex += this.frameDirection;
      if (this.frameIndex >= maxFrames - 1) this.frameDirection = -1;
      if (this.frameIndex <= 0) this.frameDirection = 1;
    }
    
    requestAnimationFrame((t) => this.loop(t));
  },
  
  setupListeners() {
    // Resize handler
    window.addEventListener('resize', () => this.onResize(), { passive: true });
    
    // Mouse
    window.addEventListener('mousemove', (e) => {
      this.targetX = e.clientX / window.innerWidth;
      this.targetY = e.clientY / window.innerHeight;
    }, { passive: true });
    
    // Touch
    window.addEventListener('touchmove', (e) => {
      const touch = e.touches[0];
      this.targetX = touch.clientX / window.innerWidth;
      this.targetY = touch.clientY / window.innerHeight;
    }, { passive: true });
    
    // Device orientation
    this.setupDeviceOrientation();
  },
  
  setupDeviceOrientation() {
    if (!('DeviceOrientationEvent' in window)) return;
    
    const handleOrientation = (e) => {
      if (e.gamma === null) return;
      this.targetX = Math.min(1, Math.max(0, (e.gamma + 45) / 90));
      this.targetY = Math.min(1, Math.max(0, (e.beta - 30) / 60));
    };
    
    if (typeof DeviceOrientationEvent.requestPermission === 'function') {
      // iOS 13+ requires explicit permission
      const requestOnce = () => {
        DeviceOrientationEvent.requestPermission()
          .then(permission => {
            if (permission === 'granted') {
              window.addEventListener('deviceorientation', handleOrientation, { passive: true });
            }
          })
          .catch(console.warn);
        document.removeEventListener('click', requestOnce);
      };
      document.addEventListener('click', requestOnce);
    } else {
      window.addEventListener('deviceorientation', handleOrientation, { passive: true });
    }
  },
  
  // Apply atmospheric haze to layers based on depth
  applyAtmosphere(color) {
    if (color) this.atmosphereColor = color;
    
    this.layers.forEach(layer => {
      const opacity = parseFloat(layer.dataset.atmosphere) || 0;
      if (opacity > 0) {
        // Check if overlay already exists
        let overlay = layer.querySelector('.layer-atmosphere');
        if (!overlay) {
          overlay = document.createElement('div');
          overlay.className = 'layer-atmosphere';
          layer.appendChild(overlay);
        }
        overlay.style.backgroundColor = this.atmosphereColor;
        overlay.style.opacity = opacity;
      }
    });
  }
};

// Export for module use or attach to window
if (typeof module !== 'undefined' && module.exports) {
  module.exports = Parallax;
} else {
  window.Parallax = Parallax;
}
