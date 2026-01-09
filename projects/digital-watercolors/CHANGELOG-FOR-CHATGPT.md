# Implementation Complete — v1.3.0 (Seal Stamp Menu)

Replaced drawer with seal-anchored stamp menu per ChatGPT spec.

---

## What Changed

| Before | After |
|--------|-------|
| Top sheet drawer with box/border | **4 bold text lines** rising from seal |
| Close button, header, backdrop | **None** — just text with shadows |
| Invisible hotspot on seal | **Larger hotspot moved UP** (thumb zone) |

---

## New Mobile Menu

### HTML
```html
<button id="sealHotspot" class="seal-hotspot" aria-label="Open menu"></button>

<nav id="sealMenu" class="seal-menu" aria-hidden="true">
  <a class="seal-menu__item" href="scenes/">Living Scenes</a>
  <a class="seal-menu__item" href="gallery/">Pixel Sliders</a>
  <a class="seal-menu__item" href="...">Color Lab</a>
  <a class="seal-menu__item" href="https://haslun.studio">Haslun.studio</a>
</nav>
```

### CSS Approach
- **No boxes, no borders** — just text + shadow
- **Hotspot moved UP** so it's in thumb zone (not too low)
- **Menu appears beside seal** (rising upward)
- **Faint radial mist** emanates from seal area
- **Very light glass** background on items (0.18 opacity)

### Positioning
```css
.seal-hotspot {
  bottom: max(92px, calc(env(safe-area-inset-bottom) + 58px));
  /* Lifted into thumb zone */
}

.seal-menu {
  left: calc(max(14px, env(safe-area-inset-left)) + 70px);
  /* Right of seal */
  bottom: max(92px, calc(env(safe-area-inset-bottom) + 62px));
  /* Aligned with seal */
}
```

### Item Styling
```css
.seal-menu__item {
  font-weight: 700;
  color: rgba(255, 255, 255, 0.96);
  text-shadow:
    0 2px 0 rgba(0, 0, 0, 0.85),
    0 0 10px rgba(0, 0, 0, 0.35);
  background: rgba(22, 12, 6, 0.18);
  backdrop-filter: blur(1.5px);
}
```

---

## Removed

- ❌ `menu-drawer` and all drawer styles
- ❌ `menu-backdrop`
- ❌ Drawer parallax / tilt code
- ❌ Close button
- ❌ Header with title/subtitle

---

## Kept

- ✅ Nameplate at top ("Haslun Studio")
- ✅ Desktop HUD unchanged (>900px)
- ✅ Tap outside to close
- ✅ ESC to close
- ✅ Reduced motion support

---

## Mobile UX Flow

1. Painting visible with nameplate at top
2. **Tap above the seal** (larger invisible hotspot)
3. **4 text links rise beside the seal** with subtle animation
4. Tap a link or tap outside → closes
5. No overlay, no box — painting stays hero

---

## Files Updated

1. **`index.html`**
   - Replaced drawer HTML with seal hotspot + seal menu
   - Simplified JS (no parallax, no backdrop)

2. **`assets/css/hub-peacocks.css`**
   - Removed all drawer styles
   - Added seal-hotspot and seal-menu styles
   - Updated focus-visible selectors

---

## File Placement

```
digital-watercolors/
├── index.html              ← Replace
└── assets/css/
    └── hub-peacocks.css    ← Replace
```

**Stamp menu rising from seal!** 🔏
