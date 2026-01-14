# ChatGPT Review Request: Haslun Projects v1.0.0

## Context

We've implemented the multi-project architecture you recommended, including your second-pass refinements. This document summarizes what was done.

---

## Second-Pass Implementations (Per Your Review)

### A) App-Specific Storage Namespacing ✅

**boot.js now provides:**
```javascript
const ctx = await HaslunBoot.boot({ configUrl: './app.json' });

// App-specific storage (uses config.id or pathname)
ctx.storageKey('seenIntro');     // → "haslun:cards:birthday:seenIntro"
ctx.getStorage('seenIntro');     // Get from app-specific key
ctx.setStorage('seenIntro', '1'); // Set in app-specific key
```

The `appId` is computed from `config.id` or the URL pathname.

### B) Mode Query Param for Preview/Testing ✅

**Now supports:**
```
?mode=pixel  → Force pixel mode for this session
?mode=glass  → Force glass mode for this session
```

This works in `early()` so it applies before first paint, and doesn't persist to localStorage (preview-only).

### C) Card Maker Tool Created ✅

**Location:** `/projects/cards/_maker/`

Features:
- Template selector (populated from `index.json`)
- To/From/Message fields with character counters
- Live iframe preview
- Glass/Pixel mode toggle for preview
- "Copy Link" button with toast notification
- "Open in New Tab" button
- URL display showing the shareable link

### D) Split `preloadAndInit()` into Separate Helpers ✅

**boot.js context now has:**
```javascript
ctx.preload(images)      // Just preload, don't init modules
ctx.initModules()        // Just init modules, no preload
ctx.preloadAndInit(images) // Convenience: both in sequence
```

This allows custom preloading workflows.

---

## First-Pass Implementations (Already Done)

### 1. Templates Now Use `HaslunBoot.boot()` Consistently ✅

**Before:**
```javascript
Loader.init(...)
await Loader.hide(...)
Atmosphere.init(...)
PixelMode.init()
```

**After:**
```javascript
const ctx = await HaslunBoot.boot({ configUrl: './app.json' });
await ctx.preloadAndInit([]);
```

All three templates (cards, invites, menus) now use this pattern. App-specific logic runs after boot.

---

### 2. URL Param Bug Fixed + Length Caps Added ✅

**Before:**
```javascript
params.get('msg')  // already decoded
decodeURIComponent(params.msg) // double-decode — broken!
```

**After:**
```javascript
const clampText = (s, max) => (s || '').slice(0, max);

return {
  to: clampText(params.get('to'), 40),
  from: clampText(params.get('from'), 40),
  msg: clampText(params.get('msg'), 240)
};
```

No double-decode, and length caps prevent layout issues from malformed URLs.

---

### 3. Font Readiness + Configurable Canvas Font ✅

**loader.js now:**
```javascript
palette: {
  // ...
  font: '8px monospace' // Configurable
},

initCanvas() {
  // Wait for fonts before first draw
  const draw = () => this.drawCanvas();
  if (document.fonts?.ready) {
    document.fonts.ready.then(draw);
  } else {
    draw();
  }
}
```

Can now pass custom pixel font: `Loader.init('canvas', { palette: { font: '8px "Press Start 2P"' } })`

---

### 4. Atmosphere: `_washesStarted` Guard Added ✅

**atmosphere.js:**
```javascript
startLivingWashes() {
  if (!this.washOverlay || this.glazingPigments.length === 0) return;
  if (this._washesStarted) return; // NEW: Prevent duplicate listeners
  this._washesStarted = true;
  // ...
}

stop() {
  // ...
  this._washesStarted = false; // Reset on stop
}
```

Now safe to call `startLivingWashes()` multiple times.

---

### 5. Parallax: Real `destroy()` Implemented ✅

**parallax.js now:**
```javascript
setupListeners() {
  // Store handlers for cleanup
  this._handlers = {
    resize: () => this.onResize(),
    mousemove: (e) => { /* ... */ },
    touchmove: (e) => { /* ... */ }
  };
  
  window.addEventListener('resize', this._handlers.resize, { passive: true });
  // etc.
}

destroy() {
  // Cancel animation loop
  if (this._rafId) {
    cancelAnimationFrame(this._rafId);
    this._rafId = null;
  }
  
  // Remove all event listeners
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
```

Now safe for SPA navigation or iframe embedding.

---

### 6. Scaffolder CLI Created ✅

**tools/haslun.py:**
```bash
# Create new template category
python tools/haslun.py new-template posters --from cards

# Create new page from template
python tools/haslun.py new-page cards birthday-jane --title "Happy Birthday, Jane"

# List all projects
python tools/haslun.py list
```

Features:
- Copies template folder
- Updates `app.json` with new ID, title, created date
- Updates `<title>` and `og:title` in HTML
- Updates category `index.json`
- Updates main `registry.json`

---

### 7. Category-Level `index.json` Files Created ✅

Each category now has its own registry:

**cards/index.json:**
```json
{
  "category": "cards",
  "title": "Greeting Cards",
  "description": "Shareable digital greeting cards with URL parameters",
  "pages": []
}
```

The scaffolder automatically adds new pages to these indexes.

---

## Current File Structure

```
projects/
├── shared/
│   ├── assets/
│   │   ├── css/base.css
│   │   └── js/
│   │       ├── boot.js          # Early init + module orchestration
│   │       ├── loader.js        # Font readiness, configurable font
│   │       ├── parallax.js      # Stored handlers, real destroy()
│   │       ├── atmosphere.js    # _washesStarted guard
│   │       └── pixel-mode.js    # Namespaced storage
│   ├── ui/
│   │   ├── loader.css
│   │   ├── parallax.css
│   │   ├── glass-overlay.css
│   │   └── pixel-overlay.css
│   └── watercolor-engine/
│
├── digital-watercolors/         # Uses local assets/ (synced copies)
│   ├── app.json
│   ├── index.html
│   └── assets/js/               # Updated with same fixes
│
├── cards/
│   ├── _template/
│   │   ├── app.json
│   │   └── index.html           # Uses HaslunBoot.boot()
│   ├── index.json               # Category registry
│   └── README.md
│
├── invites/
│   ├── _template/
│   │   ├── app.json
│   │   └── index.html           # Uses HaslunBoot.boot()
│   └── index.json
│
├── menus/
│   ├── _template/
│   │   ├── app.json
│   │   └── index.html           # Uses HaslunBoot.boot()
│   └── index.json
│
├── tools/
│   └── haslun.py                # Scaffolder CLI
│
├── registry.json                # Master index
└── README.md                    # Comprehensive docs
```

---

## What Was NOT Implemented (Deferred)

Per your advice, these were noted but deferred:

1. **Token mode for invites** (`?t=abc123` loads `./data/abc123.json`)
   - Architecture supports it via `ctx.getStorage()`
   - Will add when first real client invite is created

2. **`build-registry` CLI command**
   - Would regenerate `registry.json` from category `index.json` files
   - Not necessary yet, manual sync is fine at current scale

3. **Broader HASLUN-DOMAINS reorganization**
   - `packages/` folder (authoritative shared code)
   - `sandbox/` folder (experiments)
   - `archive/snapshots/` (dated bundles)
   - *Will do manually per your advice*

---

## Current File Structure

```
projects/
├── shared/
│   └── assets/js/
│       └── boot.js          # Now with app storage + mode param support
│
├── cards/
│   ├── _maker/              # NEW: Card Maker tool
│   │   └── index.html
│   ├── _template/
│   ├── index.json
│   └── README.md            # Updated with Card Maker docs
│
├── invites/_template/
├── menus/_template/
├── tools/haslun.py
└── registry.json
```

---

## Testing Checklist (Before Deploy)

- [ ] Card Maker loads at `/projects/cards/_maker/`
- [ ] Live preview updates as you type
- [ ] `?mode=pixel` and `?mode=glass` work in card templates
- [ ] Copy Link produces correct URL
- [ ] Card template renders URL params correctly
- [ ] Pixel toggle persists across reload (but not when `?mode=` is set)
- [ ] iOS Safari: no surprise motion permission prompts

---

## Questions Resolved

| Question | Answer |
|----------|--------|
| `boot.js` structure | Keep it, split helpers added |
| Template inheritance | Copy-and-customize is correct |
| Dual registry | Good separation, add `build-registry` CLI later |
| Digital-watercolors migration | Keep self-contained |
| Per-app storage | Added `ctx.storageKey()` etc |

---

## Ready for Deploy

All critical items from your review are implemented:
- ✅ App-specific storage namespacing
- ✅ Mode query param for previews
- ✅ Card Maker tool
- ✅ Split boot helpers

The architecture is now ready for creating real cards and client demos.
