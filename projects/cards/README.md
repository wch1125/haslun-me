# Greeting Cards

Digital greeting cards that can be shared via URL.

---

## Quick Start: Card Maker

**Use the visual Card Maker tool:**
```
/projects/cards/_maker/
```

The Card Maker lets you:
- Fill in recipient, sender, and message
- Preview in glass or pixel mode
- Copy the shareable URL with one click

---

## Usage

### Creating Cards with URL Parameters

Cards support personalization via URL query parameters:

```
/projects/cards/template/?to=Jane&from=Will&msg=Happy%20Birthday!
```

| Parameter | Max Length | Description |
|-----------|------------|-------------|
| `to` | 40 chars | Recipient name |
| `from` | 40 chars | Sender name |
| `msg` | 240 chars | Custom message |

### Preview Mode

Add `?mode=pixel` or `?mode=glass` to force a specific visual mode:

```
/projects/cards/template/?to=Jane&mode=pixel
```

---

## Creating New Card Templates

### Using the CLI

```bash
python tools/haslun.py new-page cards birthday --title "Happy Birthday"
```

### Manual Method

1. Copy `_template/` to a new folder (e.g., `birthday/`)
2. Edit `app.json` with new title and settings
3. Customize `index.html` layout and styling
4. Add images to `assets/img/`
5. Update `og.png` for link previews

---

## Folder Structure

```
cards/
├── _maker/              # Card Maker tool (don't modify)
│   └── index.html
│
├── _template/           # Base template (copy to create new cards)
│   ├── app.json
│   ├── index.html
│   └── assets/
│
├── birthday-jane/       # Example custom card
│   ├── app.json
│   ├── index.html
│   ├── og.png
│   └── assets/
│       └── flower.png
│
├── index.json           # Category registry
└── README.md
```

---

## Customizing Card Appearance

### Per-Card CSS

Add custom styles in the card's `index.html`:

```html
<style>
  :root {
    --card-ink: #1a1a1a;
    --card-accent: #c9a86c;
  }
  
  html.pixel-mode {
    --card-ink: #f5f5f0;
  }
</style>
```

### Using Watercolor Engine Colors

```javascript
// Get readable text color for a background
const textColor = WatercolorEngine.getTextColor('#1a1a1a');
```

---

## Privacy

- Cards are `noindex` by default
- OG tags configured for nice link previews
- URL is the only way to access

For sensitive content, consider "token mode" (future feature):
- `?t=abc123` loads `./data/abc123.json`
- Keeps personal info out of URLs

---

## Tips

- Keep messages short for clean URLs
- Test in both glass and pixel modes
- Add meaningful `og.png` for link previews
- Use the Card Maker for quick prototyping
