# Digital Watercolors - AI Collaboration Guide

## Legend
```
✅ INCLUDE  - Always send to Claude
⚠️ SELECTIVE - Send only when relevant
❌ EXCLUDE  - Never send (animation frames, audio)
```

---

## Directory Tree with AI Inclusion Markers

```
DIGITAL-WATERCOLORS/
│
├── index.html                          ✅ INCLUDE (hub page)
├── scenes.js                           ✅ INCLUDE (scene config)
├── scene-manager.py                    ✅ INCLUDE (management tool)
├── README.md                           ✅ INCLUDE
│
├───hub-frames/                         ❌ EXCLUDE (5MB+ of PNGs)
│   └── frame-*.png                     ❌ EXCLUDE
│
└───scenes/
    └───{scene-name}/
        ├── index.html                  ✅ INCLUDE (scene template)
        ├───frames/                     ❌ EXCLUDE (animation PNGs)
        │   └── frame-*.png             ❌ EXCLUDE
        └───audio/                      ❌ EXCLUDE (ambient MP3s)
            └── *.mp3                   ❌ EXCLUDE
```

---

## Quick Reference: What to Zip for Claude

### 🎯 LITE ZIP (Recommended)
Best for: Bug fixes, UI changes, adding features
```
index.html
scenes.js
README.md
scenes/*/index.html    (scene HTML templates only)
```
**Approximate size: ~30KB**

### 📦 STANDARD ZIP (With tools)
Best for: Full project work, manager updates
```
Everything in LITE, plus:
scene-manager.py
```
**Approximate size: ~50KB**

### 🚫 NEVER INCLUDE
```
hub-frames/              (5MB+ of animation frames)
scenes/*/frames/         (animation frames per scene)
scenes/*/audio/          (ambient audio files)
.git/                    (version control)
```

---

## File Size Reference

| File/Folder | Size | Include? |
|-------------|------|----------|
| `hub-frames/` | ~5MB | ❌ Never |
| `scenes/*/frames/` | ~1-5MB each | ❌ Never |
| `scenes/*/audio/` | ~1-10MB each | ❌ Never |
| `index.html` | ~8KB | ✅ Always |
| `scenes.js` | ~1KB | ✅ Always |
| `scene-manager.py` | ~20KB | ✅ When relevant |
| Scene index.html | ~8KB each | ✅ Always |

---

## Usage

```bash
# Create lite package (recommended)
ai-package.bat

# Create standard package (includes scene-manager.py)
ai-package.bat standard
```

---

## Scene Structure Reference

When discussing scenes, note that each scene folder contains:
- `index.html` - The scene page (include this)
- `frames/` - Animation PNG sequence (exclude)
- `audio/` - Ambient sound MP3s (exclude)

The `sceneConfig` object in each scene's index.html defines:
```javascript
const sceneConfig = {
  frameCount: 20,           // Number of frames
  framePath: 'frames/frame-',
  frameExtension: '.png',
  frameDelay: 120,          // ms between frames
  pingPong: true,           // Breathe animation
  audio: [
    { src: 'audio/ambient.mp3', volume: 0.4, loop: true }
  ]
};
```
