# Digital Watercolors

**Watercolor paintings that breathe.**

An interactive art experience by [Haslun Studio](https://haslun.studio). Hand-painted watercolors are photographed, pixelated, and animated to create living scenes. The site uses a custom pigment engine to ensure all colors are derived from real watercolor data, creating visual coherence throughout.

**Live site:** [haslun.me/projects/digital-watercolors](https://haslun.me/projects/digital-watercolors/)

---

## Project Vision

The goal is to build an interactive sketchbook where paintings feel alive. Each scene is a watercolor that breathes — subtle movements, ambient sounds, and an atmosphere that shifts with real pigment data. The aesthetic blends pixel art UI (chunky borders, dithered fills, stepped animations) with painterly backgrounds.

**Design principles:**
- Pixels define form, pigments define atmosphere
- The engine should be felt, not announced
- Every color comes from real pigment data
- Paintings are the stars; UI supports, never competes

---

## What's Been Built

### Core Experience
- **Hub page** — Animated peacock painting with parallax menu
- **Pixel-panel UI** — Chunky borders, dithered fills, stepped animations
- **Scene framework** — Template system for adding new animated paintings
- **Loading screen** — Branded loader with progress bar

### Atmosphere System (Pigment Engine Integration)
- **Daily generative swatch** — Date-seeded palette that changes each day
- **Living background washes** — Subtle glazed overlays that shift every 25-40 seconds
- **Transition washes** — Scene navigation uses pigment-based color washes
- **CSS custom properties** — `--daily-accent`, `--daily-accent-light`, `--daily-wash`

### Watercolor Engine
- **24 Schmincke AKADEMIE pigments** with real transparency data
- **Glazing calculations** — Order-sensitive layer mixing
- **Palette generation** — Complementary, analogous, triadic, split harmonies
- **Dilution gradients** — Wash strength simulation

### Accessibility & Performance
- **iOS motion permission** — Proper `DeviceOrientationEvent.requestPermission()` handling
- **Reduced motion support** — Respects `prefers-reduced-motion`
- **Mobile optimization** — No backdrop-filter blur on small screens

---

## Directory Structure

```
digital-watercolors/
│
├── index.html                 # Landing page (parallax peacocks + glass menu)
├── scenes.js                  # Scene registry (edit to add scenes)
├── README.md                  # This file
│
├── layers/                    # Parallax background layers
│   ├── Layer_0.png            # Full art (base/safety)
│   ├── Layer_1.png            # Background
│   ├── Layer_2.png            # Far branch
│   ├── Layer_3.png            # Near branch
│   ├── Layer_4.png            # Left peacock
│   └── Layer_5.png            # Right peacock (nearest)
│
├── gallery/                   # Painting gallery with comparison sliders
│   ├── index.html             # Gallery page
│   ├── *-hd.webp              # High-resolution originals
│   └── *.png                  # Pixelated versions
│
├── scenes/                    # Individual scene folders
│   └── mister-softee/         # Example scene
│       ├── index.html         # Scene page
│       ├── scene.json         # Scene metadata
│       ├── layers/            # Depth-separated layers
│       └── audio/             # Ambient sounds
│
├── watercolor-engine/         # Pigment data and mixing logic
│   ├── watercolor-engine.js   # Core engine
│   ├── pigments.json          # Schmincke AKADEMIE pigment data
│   └── demo.html              # Interactive demo
│
├── legacy/                    # Previous designs (archived)
│   ├── index-pixel.html       # Pixel-themed hub (v0.1-0.6)
│   └── hub-frames/            # Animated peacock frames
│
└── tools/                     # Build utilities
    └── scene-builder.py       # GUI for creating layered scenes
```

---

## Technical Architecture

### Hub Page (`index.html`)

The hub is a single HTML file containing:

1. **Loading screen** — Animated drops + progress bar
2. **Background animation** — Canvas-based PNG sequence player (ping-pong)
3. **Wash overlay** — Pigment engine applies subtle glazed colors
4. **Hero window** — Pixel-panel menu with parallax effect
5. **Atmosphere system** — Silent color infrastructure

### Atmosphere System

```javascript
const Atmosphere = {
  // Daily swatch (deterministic by date)
  setDailyAccent()      // Seeds PRNG with date, picks 2-3 pigments
  
  // Living washes (ambient)
  startLivingWashes()   // Cycles glazed overlays every 25-40s
  applyNextWash()       // Picks transparent pigments, applies multiply blend
  
  // Transitions (navigation)
  transitionTo(url, mood)  // Wash screen with mood-appropriate pigment
  transitionIn()           // Fade out wash on page load
}
```

**Mood palettes for transitions:**
- `warm` — Indian Yellow, Yellow Ochre, Orange
- `cool` — Ultramarine, Prussian Blue, Payne's Grey
- `earth` — Burnt Umber, Sepia, Yellow Ochre
- `vibrant` — Magenta, Cyan, Brilliant Green
- `neutral` — Payne's Grey, Sepia

### Scene Configuration (`scenes.js`)

```javascript
const SCENES = [
  {
    id: "mister-softee",       // Folder name in scenes/
    label: "Hungry for ice cream?",  // Menu button text
    ready: false,              // Set true when frames exist
    mood: "warm"               // Transition wash mood
  }
];
```

### Watercolor Engine API

```javascript
const engine = new WatercolorEngine();

// Glazing
engine.glaze(baseHex, pigment)           // Single glaze
engine.glazeMultiple([pigments], paper)  // Stack glazes
engine.compareLayerOrders(a, b)          // See order matters

// Queries
engine.findPigment('Indian Yellow')      // By name/ID
engine.getByFamily('earth')              // By color family
engine.getGlazingPigments()              // Transparent only

// Palettes
engine.generatePalette(seed, 'analogous')
engine.getDilutionGradient(pigment, steps)
engine.getHaslunPalette()                // Signature colors
```

---

## Creating Layered Scenes

### The Scene Builder Tool

Run `python scene-builder.py` to open the GUI:

```
┌─────────────────────────────────────────────────────────────┐
│  Scene Builder                                               │
├─────────────────────────────────────────────────────────────┤
│  Scene ID:    [mister-softee_______]  (folder name)         │
│  Title:       [Mister Softee________]                       │
│  Subtitle:    [Central Park, Summer_]                       │
├─────────────────────────────────────────────────────────────┤
│  PALETTE                                                     │
│  Primary:     [Indian Yellow     ▼]                         │
│  Secondary:   [Permanent Green   ▼]                         │
│  Atmosphere:  [Payne's Grey      ▼]  (depth haze)           │
├─────────────────────────────────────────────────────────────┤
│  LAYERS (back to front)                                      │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ 0: bg         — static PNG (farthest)               │    │
│  │ 1: trees      — static PNG (far)                    │    │
│  │ 2: truck      — 20 frames (mid)                     │    │
│  │ 3: figures    — static PNG (nearest)                │    │
│  └─────────────────────────────────────────────────────┘    │
│  [+ Static] [+ Animated] [Remove] [↑ Up] [↓ Down]           │
├─────────────────────────────────────────────────────────────┤
│  Output: /path/to/digital-watercolors/scenes   [Browse]     │
│                                                              │
│                    [ Generate Scene ]                        │
└─────────────────────────────────────────────────────────────┘
```

### Your Workflow

```
1. PAINT                    2. PHOTOGRAPH              3. SEPARATE LAYERS
   Watercolor on paper  →      Scan at high res    →     Photoshop lasso tool
                                                          isolate depth layers

4. PIXELATE                 5. ANIMATE (optional)      6. RUN SCENE BUILDER
   Each layer separately →     Aseprite for any    →     Pick pigments,
   256px, nearest neighbor     breathing layers          add layers, generate

                            ↓

7. OUTPUT: Ready-to-use scene folder with:
   - scene.json (auto-configured)
   - index.html (parallax + atmosphere)
   - layers/ (your PNGs, organized)
```

### Photoshop Layer Separation Tips

1. **Start with background**: Select everything behind main subject (sky, distant buildings)
2. **Work forward**: Far trees → main subject → foreground figures
3. **Feather selections**: 1-2px feather prevents hard edges
4. **Export with transparency**: PNG-24 for all layers except solid background
5. **Keep consistent canvas size**: All layers should be same dimensions

### What the Scene Builder Does Automatically

| Task | How It Works |
|------|--------------|
| **Parallax values** | Calculated from layer order (far=0.1, near=1.0) |
| **Atmosphere opacity** | Far layers get haze, near layers stay crisp |
| **Folder structure** | Creates `layers/`, `audio/`, organized files |
| **Frame naming** | Renames your frames to `frame-000.png` format |
| **scene.json** | Full config with all settings |
| **index.html** | Working scene page with parallax + engine |

### Scene.json Schema

```json
{
  "title": "Mister Softee",
  "subtitle": "Central Park, Summer",
  "palette": {
    "primary": "Indian Yellow",
    "secondary": "Permanent Green", 
    "atmosphere": "Payne's Grey"
  },
  "layers": [
    {
      "id": "bg",
      "file": "layers/bg.png",
      "depth": 0,
      "parallax": 0.1,
      "atmosphereOpacity": 0.08,
      "animated": false
    },
    {
      "id": "truck",
      "file": "layers/truck/frame-{000}.png",
      "depth": 2,
      "parallax": 0.6,
      "atmosphereOpacity": 0.02,
      "animated": true,
      "frameCount": 20
    }
  ],
  "animation": {
    "frameDelay": 120,
    "pingPong": true
  }
}
```

---

## Adding a New Scene (Simple Method)

### 1. Create folder structure
```
scenes/your-scene-name/
├── frames/
├── audio/
├── index.html    (copy from mister-softee)
└── scene.json
```

### 2. Configure scene.json
```json
{
  "title": "Scene Name",
  "subtitle": "Location, Season",
  "emoji": "🎨",
  "animation": {
    "frameCount": 20,
    "frameDelay": 120,
    "pingPong": true
  },
  "audio": [
    { "src": "audio/ambient.mp3", "volume": 0.4, "loop": true }
  ]
}
```

### 3. Export frames from Aseprite
- File → Export Sprite Sheet → PNG Files
- Naming: `frame-{frame000}.png`
- Result: `frame-000.png`, `frame-001.png`, etc.

### 4. Register in scenes.js
```javascript
{
  id: "your-scene-name",
  label: "Menu text",
  ready: true,
  mood: "warm"  // or cool, earth, vibrant, neutral
}
```

---

## Development Workflow

### Painting → Pixel Art → Animation

1. **Paint** watercolor on paper
2. **Scan/photograph** at high resolution
3. **Pixelate** in Photoshop (Image Size → 256px width → Nearest Neighbor)
4. **Animate** in Aseprite (layer-based breathing, 10-30 frames)
5. **Export** PNG sequence to `scenes/[name]/frames/`
6. **Add audio** (ambient .mp3 files)
7. **Register** in `scenes.js`

### Sharing with AI

Use the included `ai-package.bat` or `tools/Create-AIPackage.ps1` to create a zip file optimized for AI context windows:
- Includes all source files
- Excludes large frame images
- Preserves folder structure

---

## Browser Support

Tested in:
- Chrome 90+
- Firefox 88+
- Safari 14+ (including iOS motion permission)
- Edge 90+

**APIs used:**
- Canvas 2D
- CSS Custom Properties
- requestAnimationFrame
- DeviceOrientationEvent (with permission handling)

---

## Version History

### v0.7.0 — Parallax Landing Page (2025-01-08)
**Added:**
- New landing page with parallax peacock layers (6 depth layers)
- Glass overlay menu (semi-transparent, backdrop blur)
- Smooth parallax on mouse move and device tilt
- Atmospheric depth haze using pigment engine
- Elegant loading screen with progress bar

**Changed:**
- Moved pixel-themed hub to `legacy/index-pixel.html`
- Moved hub-frames to `legacy/` folder
- New design uses `layers/` folder for parallax images

**Design Philosophy:**
- Clean, sophisticated glass overlay instead of pixel panels
- Parallax creates depth without competing with menu
- Atmosphere system still runs (subtle background washes)

**Files added:** `index.html` (new), `layers/Layer_0-5.png`
**Files moved:** `legacy/index-pixel.html`, `legacy/hub-frames/`

---

### v0.6.0 — Scene Builder & Layered Scenes (2025-01-07)
**Added:**
- `scene-builder.py` — GUI tool for creating layered scenes
- Layered scene template with:
  - Depth-based parallax (mouse/tilt)
  - Atmospheric glazing from pigment engine
  - Multi-layer animation support
  - Auto-calculated parallax values
- Photoshop workflow documentation

**Scene Builder Features:**
- Pigment picker (24 Schmincke colors)
- Atmosphere selector for depth haze
- Static + animated layer support
- Auto-generates scene.json and index.html
- Organizes files into proper folder structure

**Files added:** `scene-builder.py`
**Files modified:** `README.md`

---

### v0.5.0 — Gallery & Pixel Mode Toggle (2025-01-07)
**Added:**
- **Gallery page** with comparison sliders (HD ↔ pixel)
- **Pixel mode toggle** in bottom-right corner (persists via localStorage)
- Press Start 2P font for pixel mode
- Four paintings with HD/pixel pairs:
  - Mister Softee
  - Natural History Museum
  - Grand Central Terminal
  - Autumn Stroll (Central Park Mall)

**How comparison slider works:**
- GPU-accelerated via `clip-path` (no re-rendering)
- Touch and mouse drag support
- Click to jump to position

**Files added:** `gallery/index.html`, `gallery/*.webp`, `gallery/*.png`
**Files modified:** `index.html`

---

### v0.4.0 — Pixel Canvas Loader (2025-01-07)
**Added:**
- Canvas-based loading screen rendered at 320×180, scaled up pixelated
- Dithered background using Bayer 4×4 matrix
- Animated palette pills with stepped bob timing
- Chunky pixel progress bar with palette gradient fill
- Blinking "loading..." text
- Integration with watercolor engine for palette colors

**Changed:**
- Loading screen now uses `PixelLoader` object instead of DOM elements
- Progress updates via `PixelLoader.setProgress()` instead of CSS width
- Hide transition uses `steps()` timing for game-y feel

**Files modified:** `index.html`

---

### v0.3.0 — Atmosphere System (2025-01-07)
**Added:**
- Watercolor engine integration in hub page
- Daily generative swatch (date-seeded palette)
- Living background washes (subtle glazed overlays)
- Scene transition washes with mood palettes
- CSS custom properties for pigment-derived colors

**Changed:**
- Scene links now use `Atmosphere.transitionTo()` for pigment washes
- `scenes.js` now supports `mood` property per scene

**Files modified:** `index.html`, `scenes.js`

---

### v0.2.0 — Pixel Panel UI (2025-01-07)
**Added:**
- Pixel-native panel styling (dithered fills, chunky borders)
- Stepped animations (`steps()` timing functions)
- Arrow indicator on menu hover with `pixelBob` animation
- Block shadows and pixel corner accents
- `pixelOpen` entrance animation for hero window

**Changed:**
- Removed glass/blur aesthetic in favor of solid pixel panels
- Menu items now have chunky box-shadow borders
- Footer restyled to match pixel aesthetic

**Files modified:** `index.html`

---

### v0.1.1 — Mobile & Accessibility Fixes (2025-01-07)
**Added:**
- iOS 13+ motion permission handling (`DeviceOrientationEvent.requestPermission`)
- `prefers-reduced-motion` support (disables parallax and animations)
- Mobile performance fallback (no backdrop-filter blur on small screens)

**Fixed:**
- Parallax now works on iOS Safari
- Motion-sensitive users see static UI

**Files modified:** `index.html`

---

### v0.1.0 — Initial Release (2025-01-07)
**Added:**
- Hub page with animated peacock background
- Pixel-art styled menu with parallax effect
- Scene framework with template system
- Loading screen with progress bar
- Watercolor engine with 24 Schmincke pigments
- Engine demo page

**Files included:** All initial files

---

## Future Roadmap

### Tier 1 — Ready to Build
- [ ] Wire `--daily-accent` to UI elements (borders, hover states)
- [ ] Complete mister-softee scene with full animation frames
- [ ] Add ambient audio to first scene

### Tier 2 — Studio Features (Behind "Lab" Door)
- [ ] Pigment compendium page
- [ ] Layer-by-layer reveal for select paintings
- [ ] Photo → palette translator

### Tier 3 — Deferred
- [ ] Match-this-mix challenge game
- [ ] Audio-reactive glazing
- [ ] Progression/unlock system

---

## Credits

**Art & Direction:** Will Haslun / [Haslun Studio](https://haslun.studio)  
**Development:** Claude (Anthropic) + Will Haslun  
**Pigment Data:** Schmincke AKADEMIE Aquarell (educational use)

---

## License

Paintings and artwork © Will Haslun / Haslun Studio. All rights reserved.

Code is available for reference and educational purposes.
