/**
 * Boot System
 * Handles early initialization to prevent FOUC and consistent module loading
 * 
 * Usage:
 *   import { boot } from "/shared/assets/js/boot.js";
 *   boot({ configUrl: "./app.json" });
 * 
 * Or inline in <head> for earliest possible execution:
 *   <script src="/shared/assets/js/boot.js"></script>
 *   <script>HaslunBoot.early();</script>
 */

const HaslunBoot = {
  // Namespaced storage keys
  KEYS: {
    pixelMode: 'haslun:pixelMode',
    lastApp: 'haslun:lastApp',
    motionPermission: 'haslun:motionPermission'
  },
  
  config: null,
  _earlyRan: false,
  
  /**
   * Run as early as possible (in <head>) to prevent FOUC
   * Sets pixel-mode class on <html> before first paint
   */
  early() {
    if (this._earlyRan) return;
    this._earlyRan = true;
    
    try {
      const isPixelMode = localStorage.getItem(this.KEYS.pixelMode) === 'true';
      if (isPixelMode) {
        document.documentElement.classList.add('pixel-mode');
      }
      window.__haslunBoot = { pixelMode: isPixelMode };
    } catch (e) {
      window.__haslunBoot = { pixelMode: false };
    }
  },
  
  /**
   * Full boot sequence - call after DOM is ready
   * @param {Object} options
   * @param {string} options.configUrl - Path to app.json
   * @param {Object} options.config - Inline config (alternative to configUrl)
   * @param {Function} options.onReady - Callback when boot complete
   */
  async boot(options = {}) {
    // Ensure early() ran
    this.early();
    
    // Load config
    if (options.configUrl) {
      try {
        const res = await fetch(options.configUrl);
        this.config = await res.json();
      } catch (e) {
        console.warn('Boot: Could not load config from', options.configUrl);
        this.config = {};
      }
    } else {
      this.config = options.config || {};
    }
    
    // Apply config defaults
    const config = {
      title: document.title,
      modeDefault: 'glass',
      loader: 'dom',
      atmosphere: { livingWashes: true },
      ...this.config
    };
    
    // Determine pixel mode (saved preference > config default)
    const savedMode = localStorage.getItem(this.KEYS.pixelMode);
    const isPixelMode = savedMode !== null 
      ? savedMode === 'true' 
      : config.modeDefault === 'pixel';
    
    // Apply pixel mode to body (html already done in early())
    if (isPixelMode) {
      document.documentElement.classList.add('pixel-mode');
      document.body?.classList.add('pixel-mode');
    }
    
    // Initialize modules in order
    const modules = {
      loader: null,
      parallax: null,
      atmosphere: null,
      pixelMode: null
    };
    
    // Loader
    if (typeof Loader !== 'undefined') {
      Loader.init(isPixelMode ? 'canvas' : config.loader);
      modules.loader = Loader;
    }
    
    // Track last app visited
    if (config.id) {
      localStorage.setItem(this.KEYS.lastApp, config.id);
    }
    
    // Return boot context for further initialization
    return {
      config,
      isPixelMode,
      modules,
      
      // Helper to preload and then init remaining modules
      async preloadAndInit(images = []) {
        // Preload images
        if (modules.loader && images.length > 0) {
          await modules.loader.preloadImages(images);
        } else if (modules.loader) {
          await modules.loader.hide(100);
        }
        
        // Init parallax
        if (typeof Parallax !== 'undefined') {
          Parallax.init();
          modules.parallax = Parallax;
        }
        
        // Init atmosphere
        if (typeof Atmosphere !== 'undefined' && config.atmosphere?.livingWashes !== false) {
          const color = Atmosphere.init();
          if (color && modules.parallax) {
            modules.parallax.applyAtmosphere(color);
          }
          modules.atmosphere = Atmosphere;
        }
        
        // Init pixel mode toggle
        if (typeof PixelMode !== 'undefined') {
          PixelMode.init();
          modules.pixelMode = PixelMode;
        }
        
        return modules;
      }
    };
  },
  
  /**
   * Get a namespaced storage key
   * @param {string} key - Base key name
   * @param {string} namespace - Optional additional namespace (e.g., app id)
   */
  storageKey(key, namespace = null) {
    const base = this.KEYS[key] || `haslun:${key}`;
    return namespace ? `${base}:${namespace}` : base;
  },
  
  /**
   * Safe localStorage get with namespace
   */
  getStorage(key, namespace = null) {
    try {
      return localStorage.getItem(this.storageKey(key, namespace));
    } catch {
      return null;
    }
  },
  
  /**
   * Safe localStorage set with namespace
   */
  setStorage(key, value, namespace = null) {
    try {
      localStorage.setItem(this.storageKey(key, namespace), value);
      return true;
    } catch {
      return false;
    }
  }
};

// Auto-run early() if this script is in <head>
if (document.readyState === 'loading') {
  HaslunBoot.early();
}

// Export
if (typeof module !== 'undefined' && module.exports) {
  module.exports = HaslunBoot;
} else {
  window.HaslunBoot = HaslunBoot;
  // Convenience alias
  window.boot = (opts) => HaslunBoot.boot(opts);
}
