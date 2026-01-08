# Greeting Cards

Digital greeting cards that can be shared via URL.

## Usage

1. **Duplicate** `_template/` to create a new card
2. **Rename** the folder to your card's slug (e.g., `happy-birthday-will/`)
3. **Customize** `app.json` and `index.html`
4. **Add art** to the `assets/` folder
5. **Share** the URL

## URL Parameters

Cards support URL parameters for personalization:

```
/projects/cards/birthday/?to=Jane&from=Will&msg=Happy%20Birthday!
```

| Parameter | Description |
|-----------|-------------|
| `to` | Recipient name |
| `from` | Sender name |
| `msg` | Custom message (URL encoded) |

## Creating a New Card

### Quick Start

```bash
# Copy template
cp -r _template/ my-new-card/

# Edit the config
nano my-new-card/app.json
```

### Customizing

1. **Change the art**: Replace the emoji in `.card-art` with an `<img>` tag
2. **Update colors**: Override CSS variables in the `<style>` block
3. **Add animation**: Include parallax layers or animated frames

### Privacy

Cards are set to `noindex` by default to keep them private. The URL is the only way to access them.

## Folder Structure

```
cards/
├── _template/           # Base template (don't modify)
│   ├── app.json
│   ├── index.html
│   └── assets/
│
├── birthday-jane/       # Example card
│   ├── app.json
│   ├── index.html
│   ├── og.png           # Open Graph preview image
│   └── assets/
│       └── flower.png
│
└── README.md
```

## OG Image

For nice link previews, add an `og.png` (1200x630px recommended) to each card folder and update the `<meta property="og:image">` tag.

## Tips

- Keep messages short for URL sharing
- Test the card in both glass and pixel modes
- Use the atmosphere system for subtle animation
- Consider adding a "reveal" animation on load
