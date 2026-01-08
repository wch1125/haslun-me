# Shared Platform

Reusable modules for all Haslun Studio projects.

---

## Quick Start

```html
<!-- In <head> - MUST be first -->
<script src="/projects/shared/assets/js/boot.js"></script>
<script>HaslunBoot.early();</script>

<!-- Styles -->
<link rel="stylesheet" href="/projects/shared/assets/css/base.css">
<link rel="stylesheet" href="/projects/shared/ui/loader.css">
<link rel="stylesheet" href="/projects/shared/ui/glass-overlay.css">
<link rel="stylesheet" href="/projects/shared/ui/pixel-overlay.css">

<!-- Before </body> -->
<script src="/projects/shared/watercolor-engine/watercolor-engine.js"></script>
<script src="/projects/shared/assets/js/loader.js"></script>
<script src="/projects/shared/assets/js/atmosphere.js"></script>
<script src="/projects/shared/assets/js/pixel-mode.js"></script>

<script>
  async function init() {
    const ctx = await HaslunBoot.boot({ configUrl: './app.json' });
    await ctx.preloadAndInit(imagesToLoad);
    // Your app code here
  }
  init();
</script>
```

---

## Structure

```
shared/
├── assets/
│   ├── css/
│   │   └── base.css         # Reset + CSS tokens only
│   │
│   └── js/
│       ├── boot.js          # Early init + module orchestration
│       ├── loader.js        # DOM/canvas loader with font readiness
│       ├── parallax.js      # rAF parallax with proper destroy()
│       ├── atmosphere.js    # Visibility-aware pigment washes
│       └── pixel-mode.js    # Glass/pixel toggle
│
├── ui/
│   ├── loader.css           # Loader styles
│   ├── parallax.css         # Parallax layer styles
│   ├── glass-overlay.css    # Glass panel UI
│   └── pixel-overlay.css    # Pixel panel UI
│
└── watercolor-engine/
    ├── watercolor-engine.js # Pigment mixing engine
    └── pigments.json        # Schmincke AKADEMIE data
```

---

## Module Reference

### boot.js

Handles early initialization and module orchestration.

```javascript
// In <head> - prevents FOUC
HaslunBoot.early();

// After DOM ready - full boot
const ctx = await HaslunBoot.boot({ configUrl: './app.json' });

// Preload images and init modules (convenience)
await ctx.preloadAndInit(['img/hero.png']);

// OR separate steps for custom workflows
await ctx.preload(['img/hero.png']);
ctx.initModules();
```

**App-Specific Storage:**
```javascript
// Get namespaced key: "haslun:<appId>:seenIntro"
const key = ctx.storageKey('seenIntro');

// Read/write app-specific values
const seen = ctx.getStorage('seenIntro');
ctx.setStorage('seenIntro', 'true');
```

**Mode Query Param (for previews):**
```
?mode=pixel  → Force pixel mode (doesn't persist)
?mode=glass  → Force glass mode (doesn't persist)
```

**Namespaced Storage Keys:**
| Key | Description |
|-----|-------------|
| `haslun:pixelMode` | Global pixel/glass preference |
| `haslun:lastApp` | Last visited app ID |
| `haslun:<appId>:*` | App-specific storage |

### loader.js

DOM or canvas-based loading screen.

```javascript
// DOM mode (default)
Loader.init('dom');

// Canvas mode with custom font
Loader.init('canvas', {
  palette: {
    font: '8px "Press Start 2P", monospace'
  }
});

// Preload with progress
await Loader.preloadImages(['a.png', 'b.png']);

// Manual hide
await Loader.hide(300);
```

### parallax.js

Time-based parallax with smooth interpolation.

```javascript
Parallax.init({
  tau: { mouse: 0.14, touch: 0.10, orientation: 0.08 },
  maxShift: 15,
  frameDelay: 120
});

// Apply atmosphere color
Parallax.applyAtmosphere('#4a5568');

// Request iOS motion permission (call from user gesture)
await Parallax.requestMotionPermission();

// Cleanup (for SPA navigation)
Parallax.destroy();
```

### atmosphere.js

Pigment-based color washes using WatercolorEngine.

```javascript
const color = Atmosphere.init({
  washInterval: 30000,
  initialDelay: 4000
});

// Get daily accent color
const accent = Atmosphere.getDailyAccent();

// Scene transitions
await Atmosphere.transitionTo('/next-scene/', 'warm');

// Cleanup
Atmosphere.stop();
```

### pixel-mode.js

Glass/pixel UI toggle with localStorage persistence.

```javascript
PixelMode.init();

// Check current state
if (PixelMode.isEnabled()) { /* ... */ }

// Toggle programmatically
PixelMode.toggle();

// Cleanup
PixelMode.destroy();
```

---

## CSS Tokens

Available in `base.css`:

```css
/* Colors - Glass theme */
--glass-bg: rgba(12, 10, 8, 0.45);
--glass-border: rgba(255, 255, 255, 0.12);

/* Colors - Pixel theme */
--pixel-bg: #1a1816;
--pixel-border: #3a3836;
--pixel-accent: #c9a86c;

/* Text */
--text-primary: #f8f6f1;
--text-secondary: #b8b4a8;
--text-muted: rgba(255, 255, 255, 0.5);

/* Accent */
--accent: #c9a86c;

/* Typography */
--font-display: 'Cormorant Garamond', Georgia, serif;
--font-body: 'DM Sans', sans-serif;
--font-pixel: 'Press Start 2P', monospace;

/* Spacing */
--space-xs: 0.25rem;
--space-sm: 0.5rem;
--space-md: 1rem;
--space-lg: 1.5rem;
--space-xl: 2rem;
--space-2xl: 3rem;

/* Z-index */
--z-base: 0;
--z-overlay: 50;
--z-modal: 100;
--z-toast: 150;
```

---

## When to Edit Shared Code

**DO edit shared code when:**
- Fixing bugs that affect multiple apps
- Adding features that should apply everywhere
- Improving performance/accessibility globally

**DON'T edit shared code when:**
- Making changes for a single app
- Experimenting with new features
- Customizing layout/content

**Rule of thumb:** If it's specific to one card/invite/menu, put it in that app's folder.

---

## Version History

### v1.0.1 (2025-01-08)
- App-specific storage: `ctx.storageKey()`, `ctx.getStorage()`, `ctx.setStorage()`
- Mode query param: `?mode=pixel|glass` for previews
- Split helpers: `ctx.preload()`, `ctx.initModules()`, `ctx.preloadAndInit()`

### v1.0.0 (2025-01-08)
- `boot.js` for consistent initialization
- `_washesStarted` guard in atmosphere.js
- Proper `destroy()` in parallax.js
- Font readiness + configurable font in loader.js
- Namespaced localStorage keys
