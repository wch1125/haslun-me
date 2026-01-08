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
 * 
 * Query params supported:
 *   ?mode=pixel - Force pixel mode for this session
 *   ?mode=glass - Force glass mode for this session
 */

const HaslunBoot = {
  // Namespaced storage keys
  KEYS: {
    pixelMode: 'haslun:pixelMode',
    lastApp: 'haslun:lastApp',
    motionPermission: 'haslun:motionPermission'
  },
  
  config: null,
  appId: null,
  _earlyRan: false,
  
  /**
   * Run as early as possible (in <head>) to prevent FOUC
   * Sets pixel-mode class on <html> before first paint
   * Respects ?mode=pixel|glass query param for preview/testing
   */
  early() {
    if (this._earlyRan) return;
    this._earlyRan = true;
    
    try {
      // Check for mode override in URL (for previews/testing)
      const urlParams = new URLSearchParams(window.location.search);
      const modeOverride = urlParams.get('mode');
      
      let isPixelMode;
      if (modeOverride === 'pixel') {
        isPixelMode = true;
      } else if (modeOverride === 'glass') {
        isPixelMode = false;
      } else {
        isPixelMode = localStorage.getItem(this.KEYS.pixelMode) === 'true';
      }
      
      if (isPixelMode) {
        document.documentElement.classList.add('pixel-mode');
      }
      window.__haslunBoot = { pixelMode: isPixelMode, modeOverride: modeOverride };
    } catch (e) {
      window.__haslunBoot = { pixelMode: false, modeOverride: null };
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
    
    // Store app ID for namespacing
    this.appId = config.id || location.pathname.replace(/\//g, '-').replace(/^-|-$/g, '') || 'default';
    
    // Determine pixel mode (URL override > saved preference > config default)
    const modeOverride = window.__haslunBoot?.modeOverride;
    const savedMode = localStorage.getItem(this.KEYS.pixelMode);
    
    let isPixelMode;
    if (modeOverride === 'pixel') {
      isPixelMode = true;
    } else if (modeOverride === 'glass') {
      isPixelMode = false;
    } else if (savedMode !== null) {
      isPixelMode = savedMode === 'true';
    } else {
      isPixelMode = config.modeDefault === 'pixel';
    }
    
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
    
    // Create context with helpers
    const ctx = {
      config,
      appId: this.appId,
      isPixelMode,
      modules,
      
      /**
       * Get app-specific storage key
       * @param {string} key - Base key name
       * @returns {string} Namespaced key like "haslun:cards:birthday:seenIntro"
       */
      storageKey: (key) => `haslun:${this.appId}:${key}`,
      
      /**
       * Get value from app-specific storage
       */
      getStorage: (key) => {
        try {
          return localStorage.getItem(`haslun:${this.appId}:${key}`);
        } catch {
          return null;
        }
      },
      
      /**
       * Set value in app-specific storage
       */
      setStorage: (key, value) => {
        try {
          localStorage.setItem(`haslun:${this.appId}:${key}`, value);
          return true;
        } catch {
          return false;
        }
      },
      
      /**
       * Preload images with progress
       */
      async preload(images = []) {
        if (modules.loader && images.length > 0) {
          await modules.loader.preloadImages(images);
        } else if (modules.loader) {
          await modules.loader.hide(100);
        }
      },
      
      /**
       * Initialize remaining modules (parallax, atmosphere, pixel toggle)
       */
      initModules() {
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
      },
      
      /**
       * Convenience: preload images then init modules
       */
      async preloadAndInit(images = []) {
        await ctx.preload(images);
        return ctx.initModules();
      }
    };
    
    return ctx;
  },
  
  /**
   * Get a namespaced storage key (global, not app-specific)
   * @param {string} key - Base key name
   * @param {string} namespace - Optional additional namespace
   */
  storageKey(key, namespace = null) {
    const base = this.KEYS[key] || `haslun:${key}`;
    return namespace ? `${base}:${namespace}` : base;
  },
  
  /**
   * Safe localStorage get with namespace (global)
   */
  getStorage(key, namespace = null) {
    try {
      return localStorage.getItem(this.storageKey(key, namespace));
    } catch {
      return null;
    }
  },
  
  /**
   * Safe localStorage set with namespace (global)
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
