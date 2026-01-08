# Watercolor Engine

Color mixing and glazing calculations based on real pigment data from Schmincke AKADEMIE Aquarell watercolors.

## What's Here

```
watercolor-engine/
├── pigments.json           # Raw pigment data (24 colors)
├── watercolor-engine.js    # JavaScript engine (browser + Node)
├── README.md               # This file
└── demo.html               # Interactive demo
```

## Quick Start

### Browser

```html
<script src="watercolor-engine.js"></script>
<script>
  const engine = new WatercolorEngine();
  
  // Find a pigment
  const indianYellow = engine.findPigment('Indian Yellow');
  
  // Glaze it over paper
  const onPaper = engine.glaze('#FCFAF5', indianYellow);
  
  // Layer two colors
  const glazed = engine.glazeMultiple(['Indian Yellow', 'Ultramarine']);
</script>
```

### Node.js

```javascript
const { WatercolorEngine } = require('./watercolor-engine.js');
const engine = new WatercolorEngine();
```

## Core Concepts

### Glazing

Watercolor glazing simulates how transparent pigment layers filter light:
- Light passes through top layer → hits paper → reflects back through layers
- Transparent colors let more underlayer show through
- Opaque colors cover more of the base

```javascript
// Order matters!
const { aOverB, bOverA } = engine.compareLayerOrders('Indian Yellow', 'Ultramarine');
// aOverB !== bOverA (different results based on which is on top)
```

### Transparency Levels

| Level | Opacity | Effect |
|-------|---------|--------|
| transparent | 0.45 | Light passes through easily |
| semi-transparent | 0.55 | Partial coverage |
| semi-opaque | 0.70 | Mostly covers |
| opaque | 0.85 | Blocks underlayer |

## API Reference

### Pigment Queries

```javascript
engine.getAllPigments()                    // All 24 pigments
engine.findPigment('Indian Yellow')        // By name/ID
engine.getByFamily('earth')                // By color family
engine.getByTransparency('transparent')    // By transparency
engine.getGlazingPigments()               // Best for layering
```

### Glazing Operations

```javascript
// Single glaze
engine.glaze('#FCFAF5', 'Indian Yellow')

// Multiple layers (bottom to top)
engine.glazeMultiple(['Indian Yellow', 'Ultramarine', 'Burnt Umber'])

// Dilution gradient
engine.getDilutionGradient('Carmine', 5)  // 5 steps, light to saturated

// Compare layer orders
engine.compareLayerOrders('Indian Yellow', 'Prussian Blue')
// Returns { aOverB: '#...', bOverA: '#...' }
```

### Palette Generation

```javascript
// Harmonious palettes based on color theory
engine.generatePalette('Ultramarine', 'complementary')  // Opposite on wheel
engine.generatePalette('Indian Yellow', 'analogous')    // Adjacent colors
engine.generatePalette('Carmine', 'triadic')           // 120° apart
engine.generatePalette('May Green', 'split')           // Split complementary

// The Haslun Studio signature palette
engine.getHaslunPalette()
```

### Utility Methods

```javascript
engine.lerp('#FF0000', '#0000FF', 0.5)    // Interpolate colors
engine.isLight('#F5D328')                  // true/false
engine.getTextColor('#1A3050')             // '#FFFFFF' or '#000000'
engine.hexToRgb('#F5D328')                 // [245, 211, 40]
engine.rgbToHex(245, 211, 40)              // '#F5D328'
```

## Pigment Data

24 colors from the Schmincke AKADEMIE Aquarell line:

| Family | Pigments |
|--------|----------|
| White | Opaque White |
| Yellow | Lemon Yellow, Cadmium Yellow, Indian Yellow, Naples Yellow |
| Orange | Orange |
| Red | Cadmium Red, Carmine, Magenta |
| Violet | Violet |
| Blue | Indigo, Ultramarine, Prussian Blue, Cyan |
| Green | Brilliant Green, May Green, Permanent Green, Olive Green |
| Earth | Yellow Ochre, Burnt Umber, Sepia, English Red |
| Neutral | Payne's Grey, Black |

Each pigment includes:
- Schmincke ID (e.g., '225')
- German name
- English name
- Hex color
- Pigment codes (e.g., 'PY110')
- Transparency level
- Color family

## Use Cases

### Digital Watercolors Project

```javascript
// Generate scene-appropriate palette
const warmPalette = engine.getByFamily('earth')
  .concat(engine.getByFamily('yellow'))
  .filter(p => p.transparency !== 'opaque');

// Create ambient color for scene
const baseColor = engine.glazeMultiple(['Yellow Ochre', 'Burnt Umber']);
```

### Pixel Art Color Picking

```javascript
// Get dilution gradient for shading
const shades = engine.getDilutionGradient('Prussian Blue', 8);
// Returns 8 colors from light wash to full saturation
```

### Procedural Art

```javascript
// Generate random harmonious palette
const allPigments = engine.getAllPigments();
const seed = allPigments[Math.floor(Math.random() * allPigments.length)];
const palette = engine.generatePalette(seed, 'triadic');
```

## Direct Utility Access

For low-level operations without the class:

```javascript
const { 
  hexToRgb, 
  rgbToHex, 
  glazeColors, 
  lerpColor,
  PIGMENTS,
  PAPER_WHITE 
} = WatercolorUtils;

// Direct glazing calculation
const result = glazeColors('#FCFAF5', PIGMENTS[3]);
```

## License

Pigment data extracted from publicly available Schmincke documentation for educational purposes. Engine code is free to use.

---

*Part of Haslun Studio's digital watercolor toolkit*
