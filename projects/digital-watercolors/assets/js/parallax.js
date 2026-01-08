/**
 * Parallax System
 * Handles multi-layer parallax with smooth rAF interpolation
 * Supports both static and animated layers
 * 
 * Uses time-based smoothing for consistent feel across refresh rates
 */

const Parallax = {
  viewport: null,
  layers: [],
  maxShift: 15,
  
  // Smooth interpolation state (time-based)
  targetX: 0.5,
  targetY: 0.5,
  currentX: 0.5,
  currentY: 0.5,
  _lastTimestamp: 0,
  
  // Time constants (in seconds) - higher = floatier
  tau: {
    mouse: 0.14,
    touch: 0.10,
    orientation: 0.08
  },
  _currentTau: 0.14, // default to mouse
  
  // Animation state for animated layers
  animatedLayers: [],
  frameIndex: 0,
  frameDirection: 1,
  frameDelay: 120,
  lastFrameTime: 0,
  
  // Atmosphere (optional, set by atmosphere.js)
  atmosphereColor: '#4a5568',
  
  // Track if initialized (prevent double-init)
  _initialized: false,
  
  init(options = {}) {
    if (this._initialized) return;
    this._initialized = true;
    
    this.viewport = document.getElementById('viewport');
    this.layers = Array.from(document.querySelectorAll('.parallax-layer'));
    
    // Allow customization
    if (options.tau) this.tau = { ...this.tau, ...options.tau };
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
        
        // Preload all frames and keep references
        const frames = [];
        const frameImages = [];
        for (let i = 0; i < frameCount; i++) {
          const frameSrc = `${folder}/frame-${String(i).padStart(3, '0')}.png`;
          const frameImg = new Image();
          frameImg.src = frameSrc;
          frames.push(frameSrc);
          frameImages.push(frameImg); // Keep reference to avoid GC
        }
        
        this.animatedLayers.push({
          element: layer,
          img: img,
          frames: frames,
          frameImages: frameImages, // Keep loaded images in memory
          frameCount: frameCount
        });
      }
    });
  },
  
  loop(timestamp = 0) {
    // Time-based smoothing (consistent across refresh rates)
    const dt = Math.min(0.05, (timestamp - (this._lastTimestamp || timestamp)) / 1000);
    this._lastTimestamp = timestamp;
    
    // Exponential smoothing with time constant
    const a = dt > 0 ? 1 - Math.exp(-dt / this._currentTau) : 0.08;
    
    this.currentX += (this.targetX - this.currentX) * a;
    this.currentY += (this.targetY - this.currentY) * a;
    
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
    
    this._rafId = requestAnimationFrame((t) => this.loop(t));
  },
  
  setupListeners() {
    // Store handlers for cleanup
    this._handlers = {
      resize: () => this.onResize(),
      mousemove: (e) => {
        this._currentTau = this.tau.mouse;
        this.targetX = e.clientX / window.innerWidth;
        this.targetY = e.clientY / window.innerHeight;
      },
      touchmove: (e) => {
        this._currentTau = this.tau.touch;
        const touch = e.touches[0];
        this.targetX = touch.clientX / window.innerWidth;
        this.targetY = touch.clientY / window.innerHeight;
      }
    };
    
    // Attach handlers
    window.addEventListener('resize', this._handlers.resize, { passive: true });
    window.addEventListener('mousemove', this._handlers.mousemove, { passive: true });
    window.addEventListener('touchmove', this._handlers.touchmove, { passive: true });
    
    // Device orientation (setup separately, snappiest tau)
    this.setupDeviceOrientation();
  },
  
  setupDeviceOrientation() {
    if (!('DeviceOrientationEvent' in window)) return;
    
    this._handlers.orientation = (e) => {
      if (e.gamma === null) return;
      this._currentTau = this.tau.orientation; // Snappiest for tilt
      this.targetX = Math.min(1, Math.max(0, (e.gamma + 45) / 90));
      this.targetY = Math.min(1, Math.max(0, (e.beta - 30) / 60));
    };
    
    if (typeof DeviceOrientationEvent.requestPermission === 'function') {
      // iOS 13+ - permission requested via PixelMode toggle or explicit button
      this._orientationEnabled = false;
    } else {
      window.addEventListener('deviceorientation', this._handlers.orientation, { passive: true });
      this._orientationEnabled = true;
    }
  },
  
  // Call this from a user gesture (button click, etc.)
  requestMotionPermission() {
    if (this._orientationEnabled) return Promise.resolve(true);
    
    if (typeof DeviceOrientationEvent.requestPermission === 'function') {
      return DeviceOrientationEvent.requestPermission()
        .then(permission => {
          if (permission === 'granted' && this._handlers.orientation) {
            window.addEventListener('deviceorientation', this._handlers.orientation, { passive: true });
            this._orientationEnabled = true;
            return true;
          }
          return false;
        })
        .catch(() => false);
    }
    return Promise.resolve(true); // Already enabled on non-iOS
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
  },
  
  // Cleanup (for SPA navigation)
  destroy() {
    // Cancel animation loop
    if (this._rafId) {
      cancelAnimationFrame(this._rafId);
      this._rafId = null;
    }
    
    // Remove event listeners
    if (this._handlers) {
      window.removeEventListener('resize', this._handlers.resize);
      window.removeEventListener('mousemove', this._handlers.mousemove);
      window.removeEventListener('touchmove', this._handlers.touchmove);
      if (this._handlers.orientation) {
        window.removeEventListener('deviceorientation', this._handlers.orientation);
      }
      this._handlers = null;
    }
    
    // Reset state
    this._initialized = false;
    this._orientationEnabled = false;
    this.layers = [];
    this.animatedLayers = [];
  }
};

// Export for module use or attach to window
if (typeof module !== 'undefined' && module.exports) {
  module.exports = Parallax;
} else {
  window.Parallax = Parallax;
}
