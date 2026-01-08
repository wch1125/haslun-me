/**
 * Loader System
 * Supports two modes:
 * 1. DOM loader (minimal, glass-style)
 * 2. Pixel canvas loader (retro, chunky)
 */

const Loader = {
  mode: 'dom', // 'dom' or 'canvas'
  container: null,
  canvas: null,
  ctx: null,
  progress: 0,
  
  // DOM elements
  loadingEl: null,
  loadingFill: null,
  
  // Canvas settings
  canvasWidth: 320,
  canvasHeight: 180,
  pixelScale: 1,
  palette: {
    bg: '#1a1816',
    bar: '#c9a86c',
    barBg: '#2a2826',
    text: '#f8f6f1',
    border: '#3a3836',
    font: '8px monospace' // Configurable font
  },
  
  init(mode = 'dom', options = {}) {
    this.mode = mode;
    
    if (options.palette) {
      this.palette = { ...this.palette, ...options.palette };
    }
    
    if (mode === 'canvas') {
      this.initCanvas(options);
    } else {
      this.initDOM();
    }
  },
  
  initDOM() {
    this.loadingEl = document.getElementById('loading');
    this.loadingFill = document.getElementById('loading-fill');
  },
  
  initCanvas(options = {}) {
    this.container = document.getElementById('loading');
    if (!this.container) return;
    
    // Create canvas
    this.canvas = document.createElement('canvas');
    this.canvas.width = this.canvasWidth;
    this.canvas.height = this.canvasHeight;
    this.canvas.style.cssText = `
      image-rendering: pixelated;
      image-rendering: crisp-edges;
      width: 100%;
      max-width: 640px;
      height: auto;
    `;
    
    // Clear container and add canvas
    this.container.innerHTML = '';
    this.container.style.cssText = `
      position: fixed;
      inset: 0;
      display: flex;
      align-items: center;
      justify-content: center;
      background: ${this.palette.bg};
      z-index: 100;
    `;
    this.container.appendChild(this.canvas);
    
    this.ctx = this.canvas.getContext('2d');
    this.ctx.imageSmoothingEnabled = false;
    
    // Wait for fonts to load before first draw (prevents fallback font flash)
    const draw = () => this.drawCanvas();
    if (document.fonts?.ready) {
      document.fonts.ready.then(draw);
    } else {
      draw();
    }
  },
  
  drawCanvas() {
    if (!this.ctx) return;
    
    const ctx = this.ctx;
    const w = this.canvasWidth;
    const h = this.canvasHeight;
    
    // Clear
    ctx.fillStyle = this.palette.bg;
    ctx.fillRect(0, 0, w, h);
    
    // Dithered background pattern
    ctx.fillStyle = this.palette.border;
    for (let y = 0; y < h; y += 4) {
      for (let x = (y % 8 === 0 ? 0 : 2); x < w; x += 4) {
        ctx.fillRect(x, y, 1, 1);
      }
    }
    
    // Loading bar background
    const barX = 60;
    const barY = 100;
    const barW = 200;
    const barH = 12;
    
    // Border
    ctx.fillStyle = this.palette.border;
    ctx.fillRect(barX - 2, barY - 2, barW + 4, barH + 4);
    
    // Background
    ctx.fillStyle = this.palette.barBg;
    ctx.fillRect(barX, barY, barW, barH);
    
    // Progress fill (chunky steps)
    const steps = 20;
    const filledSteps = Math.floor(this.progress * steps);
    const stepWidth = barW / steps;
    
    ctx.fillStyle = this.palette.bar;
    for (let i = 0; i < filledSteps; i++) {
      ctx.fillRect(barX + i * stepWidth + 1, barY + 1, stepWidth - 2, barH - 2);
    }
    
    // Loading text
    ctx.fillStyle = this.palette.text;
    ctx.font = this.palette.font;
    ctx.textAlign = 'center';
    ctx.fillText('loading...', w / 2, barY - 10);
    
    // Percentage
    ctx.fillText(`${Math.floor(this.progress * 100)}%`, w / 2, barY + barH + 16);
  },
  
  setProgress(value) {
    this.progress = Math.min(1, Math.max(0, value));
    
    if (this.mode === 'canvas') {
      this.drawCanvas();
    } else if (this.loadingFill) {
      // Stepped progress for DOM mode
      const steps = 10;
      const snapped = Math.round(this.progress * steps) / steps;
      this.loadingFill.style.width = `${snapped * 100}%`;
    }
  },
  
  hide(delay = 300) {
    return new Promise(resolve => {
      setTimeout(() => {
        if (this.mode === 'canvas' && this.container) {
          this.container.style.opacity = '0';
          this.container.style.transition = 'opacity 0.4s ease';
          setTimeout(() => {
            this.container.style.display = 'none';
            resolve();
          }, 400);
        } else if (this.loadingEl) {
          this.loadingEl.classList.add('hidden');
          setTimeout(resolve, 400);
        } else {
          resolve();
        }
      }, delay);
    });
  },
  
  // Preload images with progress tracking
  async preloadImages(images) {
    let loaded = 0;
    const total = images.length;
    
    if (total === 0) {
      await this.hide();
      return;
    }
    
    return new Promise(resolve => {
      images.forEach(src => {
        const img = new Image();
        img.onload = img.onerror = () => {
          loaded++;
          this.setProgress(loaded / total);
          
          if (loaded === total) {
            this.hide().then(resolve);
          }
        };
        img.src = src;
      });
    });
  }
};

// Export for module use or attach to window
if (typeof module !== 'undefined' && module.exports) {
  module.exports = Loader;
} else {
  window.Loader = Loader;
}
