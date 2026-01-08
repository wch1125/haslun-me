# Haslun Projects

Interactive web experiences built with watercolor aesthetics.

---

## Quick Reference

| Action | Command/URL |
|--------|-------------|
| **Card Maker** (visual tool) | `/projects/cards/_maker/` |
| Create new card (CLI) | `python tools/haslun.py new-page cards birthday-jane --title "Happy Birthday"` |
| Create new template category | `python tools/haslun.py new-template posters --from cards` |
| List all projects | `python tools/haslun.py list` |

**Share a card:** `/projects/cards/birthday-jane/?to=Jane&from=Will&msg=Happy%20Birthday!`

**Preview modes:** Add `?mode=pixel` or `?mode=glass` to any card URL

---

## Architecture Overview

```
projects/
├── shared/                  # Platform modules (single source of truth)
│   ├── assets/
│   │   ├── css/base.css    # Reset + design tokens
│   │   └── js/
│   │       ├── boot.js     # Early init, FOUC prevention
│   │       ├── loader.js   # DOM/canvas loaders
│   │       ├── parallax.js # rAF parallax with proper destroy()
│   │       ├── atmosphere.js # Visibility-aware pigment washes
│   │       └── pixel-mode.js # Glass/pixel toggle
│   ├── ui/                  # Opt-in UI components
│   └── watercolor-engine/   # Pigment mixing engine
│
├── digital-watercolors/     # Main gallery (uses local assets/)
├── cards/                   # Greeting cards
│   ├── _template/          # Copy to create new cards
│   └── index.json          # Category registry
├── invites/                 # Wedding invitation demos
│   ├── _template/
│   └── index.json
├── menus/                   # Restaurant menu demos
│   ├── _template/
│   └── index.json
│
├── tools/
│   └── haslun.py           # Scaffolder CLI
└── registry.json            # Master project index
```

---

## Creating New Content

### Quick Start: New Card

```bash
# 1. Create from template
python tools/haslun.py new-page cards birthday-jane --title "Happy Birthday, Jane"

# 2. Edit the new card
code projects/cards/birthday-jane/index.html

# 3. Add custom art
# Copy images to projects/cards/birthday-jane/assets/img/

# 4. Test locally
# Open projects/cards/birthday-jane/index.html in browser

# 5. Share
# URL: /projects/cards/birthday-jane/?to=Jane&from=Will
```

### Creating a New Template Category

```bash
# Copy from existing template
python tools/haslun.py new-template posters --from cards

# Or create minimal skeleton
python tools/haslun.py new-template storybooks
```

---

## What to Touch vs. Never Touch

### ✅ Touch (your app folder)

| File | Purpose |
|------|---------|
| `app.json` | Title, mode, loader, OG tags, atmosphere settings |
| `index.html` | Layout, content, per-page scripts |
| `assets/*` | Images, audio, custom CSS/JS |
| `og.png` | Link preview image |

### ❌ Never Touch (shared platform)

| Location | Why |
|----------|-----|
| `/projects/shared/*` | Changes affect ALL apps |
| `_template/` folders | Keep as "gold master" |

**Exception:** Edit shared code when fixing bugs or adding features that should apply everywhere.

---

## URL Conventions

| Type | Pattern | Example |
|------|---------|---------|
| Gallery | `/projects/{name}/` | `/projects/digital-watercolors/` |
| Card | `/projects/cards/{slug}/` | `/projects/cards/birthday-jane/` |
| Invite | `/projects/invites/{slug}/` | `/projects/invites/smith-jones/` |
| Menu | `/projects/menus/{slug}/` | `/projects/menus/ramen-bar/` |

### URL Parameters

Cards and invites support personalization via URL:

```
/projects/cards/template/?to=Jane&from=Will&msg=Happy%20Birthday!
```

| Parameter | Max Length | Description |
|-----------|------------|-------------|
| `to` | 40 chars | Recipient name |
| `from` | 40 chars | Sender name |
| `msg` | 240 chars | Custom message |

---

## App Configuration (`app.json`)

```json
{
  "id": "cards:birthday-jane",
  "title": "Happy Birthday, Jane",
  "type": "card",
  "modeDefault": "glass",
  "loader": "dom",
  "atmosphere": {
    "livingWashes": true,
    "dailyAccent": false
  },
  "share": {
    "ogTitle": "You've received a card!",
    "ogImage": "og.png",
    "noIndex": true
  },
  "created": "2025-01-08"
}
```

| Key | Options | Default |
|-----|---------|---------|
| `modeDefault` | `"glass"`, `"pixel"` | `"glass"` |
| `loader` | `"dom"`, `"canvas"` | `"dom"` |
| `atmosphere.livingWashes` | `true`, `false` | `true` |
| `share.noIndex` | `true`, `false` | `true` |

---

## Boot Sequence

All templates use the standard boot sequence:

```javascript
// 1. Early boot (in <head>) - prevents FOUC
<script src="../../shared/assets/js/boot.js"></script>
<script>HaslunBoot.early();</script>

// 2. Full boot (after DOM ready)
const ctx = await HaslunBoot.boot({ configUrl: './app.json' });

// 3. Preload and init modules
await ctx.preloadAndInit(imagesToLoad);

// 4. App-specific logic
applyMyCustomStuff();
```

**Why this matters:** Consistent boot order means you can add new shared modules (audio, analytics, etc.) by updating `boot.js` once.

---

## LocalStorage Keys

All keys are namespaced to avoid collisions:

| Key | Description |
|-----|-------------|
| `haslun:pixelMode` | Pixel/glass mode preference |
| `haslun:lastApp` | Last visited app ID |
| `haslun:motionPermission` | iOS motion permission granted |

---

## Privacy & Sharing

### Cards and Invites

- Set to `noindex` by default (search engines won't index)
- OG tags configured for nice link previews
- URL is the only way to access

### Sensitive Content

For wedding invites with private info:
- Consider "token mode" (future): `?t=abc123` loads `./data/abc123.json`
- Avoid putting sensitive text in URL query strings

---

## Testing Checklist

Before sharing a page:

- [ ] Works in glass mode
- [ ] Works in pixel mode (toggle button bottom-right)
- [ ] Mobile responsive
- [ ] Link preview looks good (test OG tags)
- [ ] Reduced motion works (`prefers-reduced-motion`)
- [ ] URL parameters work (if applicable)

---

## Development

### Running Locally

```bash
# Simple HTTP server
python -m http.server 8000
# Visit http://localhost:8000/projects/
```

### Project Structure Rules

1. **One source of truth per project**
2. **Templates are read-only** (copy, don't modify)
3. **Shared code = platform code** (affects everyone)
4. **App code = content code** (affects only that app)

---

## Version History

### v1.0.1 — Card Maker & Storage (2025-01-08)

**New Features:**
- **Card Maker tool** at `/projects/cards/_maker/`
- **Mode query param** (`?mode=pixel|glass`) for previews
- **App-specific storage** via `ctx.storageKey()`, `ctx.getStorage()`, `ctx.setStorage()`
- **Split boot helpers** (`ctx.preload()`, `ctx.initModules()`)

**Files:**
- `cards/_maker/index.html` — New visual card creation tool
- `shared/assets/js/boot.js` — Enhanced with storage & mode support
- `cards/README.md` — Updated with Card Maker documentation

### v1.0.0 — Multi-Project Architecture (2025-01-08)

**Architecture:**
- Created `/projects/shared/` platform with reusable modules
- Templates for cards, invites, menus
- Scaffolder CLI (`tools/haslun.py`)
- Category-level `index.json` registries

**Platform Improvements (per ChatGPT review):**
- `HaslunBoot.boot()` for consistent initialization
- Fixed URL param double-decode bug + length caps
- Font readiness for canvas loader
- `_washesStarted` guard in atmosphere.js
- Proper `destroy()` in parallax.js with stored handlers
- Configurable canvas loader font

**Files:**
- `shared/assets/js/boot.js` — New
- `tools/haslun.py` — New
- `*/index.json` — New category registries
- All templates updated to use `HaslunBoot.boot()`

---

## Credits

**Design & Development:** Will Haslun  
**Website:** [haslun.studio](https://haslun.studio)

