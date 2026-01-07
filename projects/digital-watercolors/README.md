# Digital Watercolors

Watercolor paintings that breathe. An interactive sketchbook.

## Structure

```
digital-watercolors/
├── index.html          ← Hub page (breathing peacocks + menu)
├── scenes.js           ← Edit this to add/remove scenes from menu
├── hub-frames/         ← Peacock animation frames
└── scenes/
    └── mister-softee/  ← Each scene is a folder
        ├── index.html  ← Scene page (copy from template)
        ├── frames/     ← Your animation frames (frame-000.png, etc.)
        └── audio/      ← Ambient sounds (.mp3)
```

## Adding a New Scene

### 1. Create the folder
```
scenes/your-scene-name/
├── frames/
└── audio/
```

### 2. Copy the template
Copy `scenes/mister-softee/index.html` to your new scene folder.

### 3. Edit the scene config (in the HTML)
```javascript
const sceneConfig = {
  frameCount: 20,           // How many frames you exported
  framePath: 'frames/frame-',
  frameExtension: '.png',
  frameDelay: 120,          // Speed (lower = faster)
  pingPong: true,           // Breathe back and forth

  audio: [
    { src: 'audio/ambient.mp3', volume: 0.4, loop: true }
  ]
};
```

### 4. Update the title (in the HTML)
```html
<title>Your Scene — Digital Watercolors</title>

<div class="scene-title">
  <h1>Your Scene Name</h1>
  <p>Location, Season</p>
</div>
```

### 5. Add frames from Aseprite
Export your animation as PNG sequence:
- File → Export Sprite Sheet → PNG Files
- Name: `frame-{frame000}.png`
- Drop in `scenes/your-scene-name/frames/`

### 6. Add to the hub menu
Edit `scenes.js`:
```javascript
const SCENES = [
  {
    id: "mister-softee",
    label: "Hungry for ice cream?",
    ready: true
  },
  {
    id: "your-scene-name",        // Must match folder name
    label: "Menu text here",
    ready: true                    // Set to true when frames are ready
  }
];
```

## Audio Tips

- Keep ambient loops subtle (volume 0.3–0.5)
- Layer 2-3 sounds for depth (e.g., traffic + birds + distant voices)
- Use .mp3 for browser compatibility
- Sound starts muted; visitor clicks to enable

## Frame Naming

Aseprite export: `frame-{frame000}.png`  
Result: `frame-000.png`, `frame-001.png`, etc.

## Workflow Summary

1. Paint watercolor
2. Photograph/scan
3. Pixelate in Photoshop (256px width, Nearest Neighbor)
4. Animate in Aseprite (layer-based breathing)
5. Export PNG sequence to `scenes/your-scene/frames/`
6. Find/record ambient audio
7. Edit `scenes.js` to add to menu
8. Push to GitHub
