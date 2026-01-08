# AI-README.md — Watercolor Engine

**Purpose:** This folder contains a reusable JavaScript library for watercolor color mixing calculations, extracted from the Haslun Studio Watercolor Lab tool.

**When to use this:**
- User asks for color palette generation
- User wants procedural/generative art with watercolor aesthetics
- User needs glazing calculations (layering transparent colors)
- User wants colors that match the Haslun Studio brand
- Any project involving realistic watercolor color theory

**When NOT to use this:**
- Simple hex color manipulation (just use basic RGB math)
- Non-watercolor art styles
- Projects that don't need pigment-accurate colors

---

## Quick Reference

### Load the engine
```javascript
// Browser
<script src="watercolor-engine.js"></script>
const engine = new WatercolorEngine();

// Node.js
const { WatercolorEngine } = require('./watercolor-engine.js');
```

### Most useful methods

```javascript
// GLAZING - simulate transparent layers
engine.glaze('#FCFAF5', 'Indian Yellow')  // pigment over paper
engine.glazeMultiple(['Indian Yellow', 'Ultramarine', 'Burnt Umber'])  // stack

// COMPARE LAYER ORDERS - order matters in watercolor!
const { aOverB, bOverA } = engine.compareLayerOrders('Yellow Ochre', 'Prussian Blue');

// GET PIGMENTS
engine.findPigment('Indian Yellow')       // by name
engine.getByFamily('earth')               // by family: yellow, red, blue, green, earth, neutral
engine.getGlazingPigments()               // transparent/semi-transparent only

// PALETTES
engine.generatePalette('Ultramarine', 'complementary')  // color theory harmonies
engine.getHaslunPalette()                 // Will's signature colors

// GRADIENTS
engine.getDilutionGradient('Carmine', 5)  // light wash → full saturation

// UTILITIES
engine.lerp('#FF0000', '#0000FF', 0.5)    // interpolate
engine.getTextColor('#1A3050')            // returns white or black for contrast
```

---

## Key Data

**24 pigments** from Schmincke AKADEMIE Aquarell line, each with:
- `id`: Schmincke product code (e.g., '225')
- `name`: German name
- `nameEn`: English name
- `hex`: Color value
- `transparency`: 'transparent' | 'semi-transparent' | 'semi-opaque' | 'opaque'
- `family`: 'yellow' | 'red' | 'blue' | 'green' | 'earth' | 'neutral' | etc.
- `pigments`: Array of pigment codes (e.g., ['PY110', 'PY154'])

**Transparency affects glazing math:**
- transparent: 0.45 opacity
- semi-transparent: 0.55
- semi-opaque: 0.70
- opaque: 0.85

**Paper white:** `#FCFAF5` (warm white, simulates watercolor paper)

---

## Files in this folder

| File | What it is | When to read it |
|------|------------|-----------------|
| `watercolor-engine.js` | The library | Include in projects |
| `pigments.json` | Raw pigment data | If you need data without the JS |
| `README.md` | Human documentation | For detailed API reference |
| `demo.html` | Interactive playground | To test/demonstrate features |
| `AI-README.md` | This file | You're reading it |

---

## Example: Generate scene-appropriate palette

```javascript
const engine = new WatercolorEngine();

// For a warm sunset scene
const warmColors = engine.getByFamily('earth')
  .concat(engine.getByFamily('orange'))
  .filter(p => p.transparency !== 'opaque');

// For a cool night scene  
const coolColors = engine.getByFamily('blue')
  .concat([engine.findPigment("Payne's Grey")])
  .filter(Boolean);

// Generate CSS variables
const palette = engine.getHaslunPalette();
const cssVars = palette.map((p, i) => `--color-${i + 1}: ${p.hex};`).join('\n');
```

---

## Integration with Digital Watercolors project

This engine lives in `/shared/watercolor-engine/` and can be referenced by:
- `haslun.studio/watercolor-lab.html` (origin of this code)
- `haslun.me/projects/digital-watercolors/` (breathing paintings)
- Any future Haslun projects needing color calculations

The glazing math here models real physics: light passes through transparent pigment layers, hits paper, reflects back. That's why layer order matters — Yellow over Blue ≠ Blue over Yellow.

---

## Brand colors (Haslun Studio)

```javascript
const haslun = {
  terracotta: '#c4703f',
  terracottaLight: '#d4845a', 
  gold: '#b8986b',
  sage: '#8b9a7d',
  forest: '#5a7247',
  parchment: '#f4e4c1',
  inkDark: '#1a1a1a'
};
```

These appear across haslun.studio, digital-watercolors, and related projects.

---

**Last updated:** January 2025
**Origin:** Extracted from haslun.studio/watercolor-lab.html
**Maintainer:** Will Haslun / Haslun Studio
