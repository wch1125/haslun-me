# Haslun Studio Projects

Interactive web experiences built with watercolor aesthetics.

## Structure

```
projects/
├── shared/                  # Platform modules (CSS, JS, engine)
├── digital-watercolors/     # Main gallery site
├── cards/                   # Shareable greeting cards
├── invites/                 # Wedding invitation demos
├── menus/                   # Restaurant menu demos
└── registry.json            # Project index
```

## Quick Start

### Creating a New Card

```bash
cd projects/cards
cp -r _template/ my-card/
# Edit my-card/index.html and app.json
```

Share via: `/projects/cards/my-card/?to=Jane&from=Will`

### Creating a New Invite Demo

```bash
cd projects/invites
cp -r _template/ smith-jones/
# Customize for the client
```

### Creating a New Menu Demo

```bash
cd projects/menus
cp -r _template/ ramen-bar/
# Add menu items and styling
```

## App Configuration

Each project has an `app.json`:

```json
{
  "id": "my-app",
  "title": "My App",
  "type": "card",
  "modeDefault": "glass",
  "loader": "dom",
  "atmosphere": {
    "livingWashes": true
  },
  "share": {
    "ogImage": "og.png",
    "noIndex": true
  }
}
```

## Shared Platform

All projects can use shared modules from `/shared/`:

- **boot.js** — Early initialization, FOUC prevention
- **loader.js** — DOM and pixel canvas loaders
- **parallax.js** — Time-based parallax with animation
- **atmosphere.js** — Pigment-based color washes
- **pixel-mode.js** — Glass/pixel UI toggle
- **watercolor-engine.js** — Pigment mixing and glazing

## URL Conventions

| Type | Pattern | Example |
|------|---------|---------|
| Gallery | `/projects/{name}/` | `/projects/digital-watercolors/` |
| Card | `/projects/cards/{slug}/` | `/projects/cards/birthday-jane/` |
| Invite | `/projects/invites/{client}/{slug}/` | `/projects/invites/smith-jones/preview/` |
| Menu | `/projects/menus/{client}/{slug}/` | `/projects/menus/ramen-bar/spring/` |

## Privacy

- Cards and invites are `noindex` by default
- OG tags for nice link previews
- No sensitive data in query strings (use tokens if needed)

## Project Registry

`registry.json` lists all projects for potential hub/index pages:

```json
{
  "projects": [
    {
      "id": "digital-watercolors",
      "title": "Digital Watercolors",
      "path": "/projects/digital-watercolors/",
      "category": "gallery",
      "status": "live"
    }
  ]
}
```

## Development

### Running Locally

Projects are static HTML—just open in a browser or use a local server:

```bash
python -m http.server 8000
# Visit http://localhost:8000/projects/
```

### Testing Both Modes

Click the pixel toggle (◻/◼) in the bottom-right to switch between glass and pixel modes.

## Credits

**Design & Development:** Will Haslun  
**Website:** [haslun.studio](https://haslun.studio)
