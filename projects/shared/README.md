# Shared Platform

Reusable modules for all Haslun Studio projects.

## Structure

```
shared/
├── assets/
│   ├── css/
│   │   └── base.css         # Reset + CSS tokens
│   │
│   └── js/
│       ├── boot.js          # Early init + module loader
│       ├── loader.js        # DOM/canvas loader
│       ├── parallax.js      # rAF parallax system
│       ├── atmosphere.js    # Pigment washes
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

## Usage

### In a Project

```html
<!-- Early boot (in <head>) -->
<script src="../../shared/assets/js/boot.js"></script>
<script>HaslunBoot.early();</script>

<!-- Styles -->
<link rel="stylesheet" href="../../shared/assets/css/base.css">
<link rel="stylesheet" href="../../shared/ui/loader.css">
<link rel="stylesheet" href="../../shared/ui/glass-overlay.css">
<link rel="stylesheet" href="../../shared/ui/pixel-overlay.css">

<!-- Scripts (before </body>) -->
<script src="../../shared/watercolor-engine/watercolor-engine.js"></script>
<script src="../../shared/assets/js/loader.js"></script>
<script src="../../shared/assets/js/atmosphere.js"></script>
<script src="../../shared/assets/js/pixel-mode.js"></script>
```

### With Boot.js

```javascript
const ctx = await HaslunBoot.boot({ configUrl: './app.json' });
const modules = await ctx.preloadAndInit(imagesToLoad);
```

## LocalStorage Keys

All storage keys are namespaced to avoid collisions:

| Key | Description |
|-----|-------------|
| `haslun:pixelMode` | Pixel/glass mode preference |
| `haslun:lastApp` | Last visited app ID |
| `haslun:motionPermission` | iOS motion permission granted |

## CSS Tokens

Available in `base.css`:

```css
/* Colors */
--glass-bg, --glass-border, --glass-highlight
--pixel-bg, --pixel-border, --pixel-accent
--text-primary, --text-secondary, --text-muted
--accent, --accent-warm, --accent-soft
--bg-dark, --bg-card

/* Typography */
--font-display    /* Cormorant Garamond */
--font-body       /* DM Sans */
--font-pixel      /* Press Start 2P */

/* Spacing */
--space-xs, --space-sm, --space-md, --space-lg, --space-xl, --space-2xl

/* Z-index */
--z-base, --z-overlay, --z-modal, --z-toast
```

## Adding New Modules

1. Create the module in the appropriate folder
2. Export to `window` for browser use
3. Document in this README
4. Test with existing projects
