/**
 * Atmosphere System
 * Handles pigment-based color washes using the Watercolor Engine
 * Visibility-aware: pauses when tab is hidden
 */

const Atmosphere = {
  engine: null,
  washOverlay: null,
  transitionWash: null,
  glazingPigments: [],
  _washTimer: null,
  _initialized: false,
  _visibilityHandler: null,
  
  // Configuration
  washInterval: 30000,
  initialDelay: 4000,
  resumeDelay: 5000,
  
  init(options = {}) {
    // Prevent double-init
    if (this._initialized) return this.getAtmosphereColor();
    
    if (typeof WatercolorEngine === 'undefined') {
      console.warn('Atmosphere: WatercolorEngine not found');
      return null;
    }
    
    this.engine = new WatercolorEngine();
    this.washOverlay = document.getElementById('wash-overlay');
    this.transitionWash = document.getElementById('transition-wash');
    this.glazingPigments = this.engine.getGlazingPigments();
    
    // Apply options
    if (options.washInterval) this.washInterval = options.washInterval;
    if (options.initialDelay) this.initialDelay = options.initialDelay;
    
    // Start after initial delay
    setTimeout(() => this.startLivingWashes(), this.initialDelay);
    
    this._initialized = true;
    
    // Return atmosphere color for parallax integration
    return this.getAtmosphereColor();
  },
  
  getAtmosphereColor(pigmentName = "Payne's Grey") {
    if (!this.engine) return '#4a5568';
    const pigment = this.engine.findPigment(pigmentName);
    return pigment ? this.engine.glaze(this.engine.paperWhite, pigment) : '#4a5568';
  },
  
  startLivingWashes() {
    if (!this.washOverlay || this.glazingPigments.length === 0) return;
    
    const tick = () => {
      if (document.hidden) return; // Don't run when tab is hidden
      this.applyWash();
      this._washTimer = setTimeout(tick, this.washInterval);
    };
    
    // Initial wash
    this.applyWash();
    this._washTimer = setTimeout(tick, this.washInterval);
    
    // Visibility change handler (stored for cleanup)
    this._visibilityHandler = () => {
      if (document.hidden) {
        // Clear timer when hidden
        clearTimeout(this._washTimer);
        this._washTimer = null;
      } else {
        // Resume when visible
        clearTimeout(this._washTimer);
        this._washTimer = setTimeout(tick, this.resumeDelay);
      }
    };
    
    document.addEventListener('visibilitychange', this._visibilityHandler);
  },
  
  applyWash() {
    if (!this.washOverlay || !this.engine) return;
    
    const count = 1 + Math.floor(Math.random() * 2);
    const pigments = [];
    for (let i = 0; i < count; i++) {
      pigments.push(this.glazingPigments[Math.floor(Math.random() * this.glazingPigments.length)]);
    }
    
    const washColor = this.engine.glazeMultiple(pigments);
    this.washOverlay.style.backgroundColor = washColor;
    this.washOverlay.classList.add('active');
  },
  
  // Transition palettes for scene navigation
  transitionPalettes: {
    warm: ['Indian Yellow', 'Yellow Ochre', 'Orange'],
    cool: ['Ultramarine', 'Prussian Blue', "Payne's Grey"],
    earth: ['Burnt Umber', 'Sepia', 'Yellow Ochre'],
    neutral: ["Payne's Grey", 'Sepia']
  },
  
  async transitionTo(url, mood = 'neutral') {
    if (!this.transitionWash || !this.engine) {
      window.location.href = url;
      return;
    }
    
    const palette = this.transitionPalettes[mood] || this.transitionPalettes.neutral;
    const pigment = this.engine.findPigment(palette[Math.floor(Math.random() * palette.length)]);
    
    if (pigment) {
      this.transitionWash.style.backgroundColor = this.engine.glaze(this.engine.paperWhite, pigment);
    }
    
    this.transitionWash.classList.add('entering');
    await new Promise(r => setTimeout(r, 350));
    window.location.href = url;
  },
  
  // Generate daily accent color (date-seeded)
  getDailyAccent() {
    if (!this.engine) return null;
    
    const today = new Date();
    const seed = today.getFullYear() * 10000 + (today.getMonth() + 1) * 100 + today.getDate();
    const seededRandom = (s) => {
      const x = Math.sin(s) * 10000;
      return x - Math.floor(x);
    };
    
    const idx = Math.floor(seededRandom(seed) * this.glazingPigments.length);
    return this.glazingPigments[idx];
  },
  
  // Stop washes and cleanup (for SPA navigation)
  stop() {
    clearTimeout(this._washTimer);
    this._washTimer = null;
    
    if (this._visibilityHandler) {
      document.removeEventListener('visibilitychange', this._visibilityHandler);
      this._visibilityHandler = null;
    }
    
    this._initialized = false;
  }
};

// Export for module use or attach to window
if (typeof module !== 'undefined' && module.exports) {
  module.exports = Atmosphere;
} else {
  window.Atmosphere = Atmosphere;
}
