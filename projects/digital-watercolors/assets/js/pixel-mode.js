/**
 * Pixel Mode Toggle
 * Switches between glass (elegant) and pixel (retro) UI aesthetics
 * Persists preference to localStorage
 */

const PixelMode = {
  enabled: false,
  storageKey: 'pixelMode',
  toggleBtn: null,
  
  init() {
    // Load saved preference
    const saved = localStorage.getItem(this.storageKey);
    this.enabled = saved === 'true';
    
    // Apply initial state
    if (this.enabled) {
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
      document.body.classList.add('pixel-mode');
    } else {
      document.body.classList.remove('pixel-mode');
    }
    
    this.updateToggleIcon();
    
    // Dispatch event for other components to react
    window.dispatchEvent(new CustomEvent('pixelmodechange', { 
      detail: { enabled: this.enabled } 
    }));
    
    return this.enabled;
  },
  
  isEnabled() {
    return this.enabled;
  }
};

// Export for module use or attach to window
if (typeof module !== 'undefined' && module.exports) {
  module.exports = PixelMode;
} else {
  window.PixelMode = PixelMode;
}
