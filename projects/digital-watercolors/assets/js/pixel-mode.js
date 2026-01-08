/**
 * Pixel Mode Toggle
 * Switches between glass (elegant) and pixel (retro) UI aesthetics
 * Persists preference to localStorage
 * Also handles iOS motion permission request (piggybacks on user gesture)
 */

const PixelMode = {
  enabled: false,
  storageKey: 'pixelMode',
  toggleBtn: null,
  _initialized: false,
  
  init() {
    if (this._initialized) return this.enabled;
    this._initialized = true;
    
    // Load saved preference (should already be applied by boot script)
    const saved = localStorage.getItem(this.storageKey);
    this.enabled = saved === 'true';
    
    // Ensure class is applied (in case boot script didn't run)
    if (this.enabled) {
      document.documentElement.classList.add('pixel-mode');
      document.body.classList.add('pixel-mode');
    }
    
    // Create toggle button if it doesn't exist
    this.createToggle();
    
    return this.enabled;
  },
  
  createToggle() {
    // Check if toggle already exists
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
    // Use text icons for simplicity (no external dependencies)
    this.toggleBtn.textContent = this.enabled ? '◼' : '◻';
    this.toggleBtn.title = this.enabled ? 'Switch to glass mode' : 'Switch to pixel mode';
  },
  
  toggle() {
    this.enabled = !this.enabled;
    localStorage.setItem(this.storageKey, this.enabled);
    
    if (this.enabled) {
      document.documentElement.classList.add('pixel-mode');
      document.body.classList.add('pixel-mode');
    } else {
      document.documentElement.classList.remove('pixel-mode');
      document.body.classList.remove('pixel-mode');
    }
    
    this.updateToggleIcon();
    
    // Piggyback on this user gesture to request motion permission (iOS)
    if (typeof Parallax !== 'undefined' && Parallax.requestMotionPermission) {
      Parallax.requestMotionPermission();
    }
    
    // Dispatch event for other components to react
    window.dispatchEvent(new CustomEvent('pixelmodechange', { 
      detail: { enabled: this.enabled } 
    }));
    
    return this.enabled;
  },
  
  isEnabled() {
    return this.enabled;
  },
  
  // Cleanup (for SPA navigation)
  destroy() {
    if (this.toggleBtn && this.toggleBtn.parentNode) {
      this.toggleBtn.parentNode.removeChild(this.toggleBtn);
    }
    this.toggleBtn = null;
    this._initialized = false;
  }
};

// Export for module use or attach to window
if (typeof module !== 'undefined' && module.exports) {
  module.exports = PixelMode;
} else {
  window.PixelMode = PixelMode;
}
