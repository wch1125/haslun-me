/**
 * Pixel Mode Toggle
 * Switches between glass (elegant) and pixel (retro) UI aesthetics
 * Uses namespaced localStorage key: haslun:pixelMode
 */

const PixelMode = {
  enabled: false,
  storageKey: 'haslun:pixelMode', // Namespaced key
  toggleBtn: null,
  _initialized: false,
  
  init() {
    if (this._initialized) return this.enabled;
    this._initialized = true;
    
    // Load saved preference
    try {
      const saved = localStorage.getItem(this.storageKey);
      this.enabled = saved === 'true';
    } catch {
      this.enabled = false;
    }
    
    // Ensure classes are applied (boot.js may have done this early)
    if (this.enabled) {
      document.documentElement.classList.add('pixel-mode');
      document.body?.classList.add('pixel-mode');
    }
    
    // Create toggle button
    this.createToggle();
    
    return this.enabled;
  },
  
  createToggle() {
    this.toggleBtn = document.getElementById('pixel-toggle');
    
    if (!this.toggleBtn) {
      this.toggleBtn = document.createElement('button');
      this.toggleBtn.id = 'pixel-toggle';
      this.toggleBtn.className = 'pixel-toggle';
      this.toggleBtn.setAttribute('aria-label', 'Toggle pixel mode');
      document.body.appendChild(this.toggleBtn);
    }
    
    this.updateToggleIcon();
    this.toggleBtn.addEventListener('click', () => this.toggle());
  },
  
  updateToggleIcon() {
    if (!this.toggleBtn) return;
    this.toggleBtn.textContent = this.enabled ? '◼' : '◻';
    this.toggleBtn.title = this.enabled ? 'Switch to glass mode' : 'Switch to pixel mode';
  },
  
  toggle() {
    this.enabled = !this.enabled;
    
    try {
      localStorage.setItem(this.storageKey, this.enabled);
    } catch {}
    
    if (this.enabled) {
      document.documentElement.classList.add('pixel-mode');
      document.body.classList.add('pixel-mode');
    } else {
      document.documentElement.classList.remove('pixel-mode');
      document.body.classList.remove('pixel-mode');
    }
    
    this.updateToggleIcon();
    
    // Request motion permission on iOS (piggyback on user gesture)
    if (typeof Parallax !== 'undefined' && Parallax.requestMotionPermission) {
      Parallax.requestMotionPermission();
    }
    
    // Dispatch event
    window.dispatchEvent(new CustomEvent('pixelmodechange', { 
      detail: { enabled: this.enabled } 
    }));
    
    return this.enabled;
  },
  
  isEnabled() {
    return this.enabled;
  },
  
  destroy() {
    if (this.toggleBtn?.parentNode) {
      this.toggleBtn.parentNode.removeChild(this.toggleBtn);
    }
    this.toggleBtn = null;
    this._initialized = false;
  }
};

if (typeof module !== 'undefined' && module.exports) {
  module.exports = PixelMode;
} else {
  window.PixelMode = PixelMode;
}
