#!/usr/bin/env python3
"""
Digital Watercolors — Scene Builder
====================================
A simple GUI tool for creating layered scenes.

Usage:
    python scene-builder.py

Or double-click scene-builder.py on Windows/Mac.
"""

import os
import sys
import json
import shutil
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from datetime import datetime

# ============================================
# PIGMENT DATA (from watercolor engine)
# ============================================
PIGMENTS = [
    # Yellows
    {"name": "Lemon Yellow", "id": "lemon-yellow", "family": "yellow"},
    {"name": "Indian Yellow", "id": "indian-yellow", "family": "yellow"},
    {"name": "Yellow Ochre", "id": "yellow-ochre", "family": "earth"},
    {"name": "Orange", "id": "orange", "family": "orange"},
    
    # Reds
    {"name": "Vermilion", "id": "vermilion", "family": "red"},
    {"name": "Carmine", "id": "carmine", "family": "red"},
    {"name": "Magenta", "id": "magenta", "family": "red"},
    
    # Blues
    {"name": "Ultramarine", "id": "ultramarine", "family": "blue"},
    {"name": "Prussian Blue", "id": "prussian-blue", "family": "blue"},
    {"name": "Cyan", "id": "cyan", "family": "blue"},
    
    # Greens
    {"name": "Permanent Green", "id": "permanent-green", "family": "green"},
    {"name": "Brilliant Green", "id": "brilliant-green", "family": "green"},
    {"name": "Olive Green", "id": "olive-green", "family": "green"},
    
    # Earth tones
    {"name": "Burnt Sienna", "id": "burnt-sienna", "family": "earth"},
    {"name": "Burnt Umber", "id": "burnt-umber", "family": "earth"},
    {"name": "Sepia", "id": "sepia", "family": "earth"},
    
    # Neutrals
    {"name": "Payne's Grey", "id": "paynes-grey", "family": "neutral"},
    {"name": "Ivory Black", "id": "ivory-black", "family": "neutral"},
]

PIGMENT_NAMES = [p["name"] for p in PIGMENTS]

# Default atmosphere choices (good for depth haze)
ATMOSPHERE_PIGMENTS = ["Payne's Grey", "Ultramarine", "Prussian Blue", "Sepia", "None"]

# ============================================
# SCENE BUILDER GUI
# ============================================
class SceneBuilder:
    def __init__(self, root):
        self.root = root
        self.root.title("Digital Watercolors — Scene Builder")
        self.root.geometry("700x800")
        self.root.configure(bg="#1a1a1c")
        
        # Scene data
        self.layers = []  # List of layer dicts
        self.output_dir = None
        
        self.create_ui()
    
    def create_ui(self):
        # Style
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TLabel", background="#1a1a1c", foreground="#f5f5f5", font=("Segoe UI", 10))
        style.configure("TButton", font=("Segoe UI", 10))
        style.configure("TEntry", font=("Segoe UI", 10))
        style.configure("Header.TLabel", font=("Segoe UI", 14, "bold"), foreground="#c9a86c")
        style.configure("Section.TLabel", font=("Segoe UI", 11, "bold"), foreground="#e8d8b8")
        
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # ---- Header ----
        ttk.Label(main_frame, text="Scene Builder", style="Header.TLabel").pack(anchor="w")
        ttk.Label(main_frame, text="Create layered scenes with parallax and atmospheric depth").pack(anchor="w", pady=(0, 15))
        
        # ---- Scene Info ----
        info_frame = ttk.LabelFrame(main_frame, text="Scene Info", padding=10)
        info_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Scene ID
        row1 = ttk.Frame(info_frame)
        row1.pack(fill=tk.X, pady=2)
        ttk.Label(row1, text="Scene ID:", width=12).pack(side=tk.LEFT)
        self.scene_id_var = tk.StringVar(value="my-scene")
        ttk.Entry(row1, textvariable=self.scene_id_var, width=30).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Label(row1, text="(folder name, lowercase, hyphens)", foreground="#888").pack(side=tk.LEFT)
        
        # Title
        row2 = ttk.Frame(info_frame)
        row2.pack(fill=tk.X, pady=2)
        ttk.Label(row2, text="Title:", width=12).pack(side=tk.LEFT)
        self.title_var = tk.StringVar(value="My Scene")
        ttk.Entry(row2, textvariable=self.title_var, width=30).pack(side=tk.LEFT)
        
        # Subtitle
        row3 = ttk.Frame(info_frame)
        row3.pack(fill=tk.X, pady=2)
        ttk.Label(row3, text="Subtitle:", width=12).pack(side=tk.LEFT)
        self.subtitle_var = tk.StringVar(value="Location, Season")
        ttk.Entry(row3, textvariable=self.subtitle_var, width=30).pack(side=tk.LEFT)
        
        # ---- Palette ----
        palette_frame = ttk.LabelFrame(main_frame, text="Color Palette (from your painting)", padding=10)
        palette_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Primary pigment
        p1_row = ttk.Frame(palette_frame)
        p1_row.pack(fill=tk.X, pady=2)
        ttk.Label(p1_row, text="Primary:", width=12).pack(side=tk.LEFT)
        self.pigment1_var = tk.StringVar(value="Indian Yellow")
        ttk.Combobox(p1_row, textvariable=self.pigment1_var, values=PIGMENT_NAMES, width=25).pack(side=tk.LEFT)
        
        # Secondary pigment
        p2_row = ttk.Frame(palette_frame)
        p2_row.pack(fill=tk.X, pady=2)
        ttk.Label(p2_row, text="Secondary:", width=12).pack(side=tk.LEFT)
        self.pigment2_var = tk.StringVar(value="Permanent Green")
        ttk.Combobox(p2_row, textvariable=self.pigment2_var, values=PIGMENT_NAMES, width=25).pack(side=tk.LEFT)
        
        # Atmosphere pigment
        atm_row = ttk.Frame(palette_frame)
        atm_row.pack(fill=tk.X, pady=2)
        ttk.Label(atm_row, text="Atmosphere:", width=12).pack(side=tk.LEFT)
        self.atmosphere_var = tk.StringVar(value="Payne's Grey")
        ttk.Combobox(atm_row, textvariable=self.atmosphere_var, values=ATMOSPHERE_PIGMENTS, width=25).pack(side=tk.LEFT)
        ttk.Label(atm_row, text="(depth haze color)", foreground="#888").pack(side=tk.LEFT, padx=5)
        
        # ---- Layers ----
        layers_frame = ttk.LabelFrame(main_frame, text="Layers (back to front)", padding=10)
        layers_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Layer list
        self.layer_listbox = tk.Listbox(layers_frame, height=8, bg="#242424", fg="#f5f5f5", 
                                         selectmode=tk.SINGLE, font=("Consolas", 10))
        self.layer_listbox.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Layer buttons
        btn_row = ttk.Frame(layers_frame)
        btn_row.pack(fill=tk.X)
        
        ttk.Button(btn_row, text="+ Add Static Layer", command=self.add_static_layer).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_row, text="+ Add Animated Layer", command=self.add_animated_layer).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_row, text="Remove", command=self.remove_layer).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_row, text="↑ Move Up", command=self.move_layer_up).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_row, text="↓ Move Down", command=self.move_layer_down).pack(side=tk.LEFT)
        
        # Layer info
        ttk.Label(layers_frame, text="Layer order = depth order. First layer = farthest (background).", 
                  foreground="#888").pack(anchor="w", pady=(10, 0))
        
        # ---- Animation Settings ----
        anim_frame = ttk.LabelFrame(main_frame, text="Animation Settings", padding=10)
        anim_frame.pack(fill=tk.X, pady=(0, 15))
        
        anim_row = ttk.Frame(anim_frame)
        anim_row.pack(fill=tk.X)
        
        ttk.Label(anim_row, text="Frame delay (ms):", width=15).pack(side=tk.LEFT)
        self.frame_delay_var = tk.StringVar(value="120")
        ttk.Entry(anim_row, textvariable=self.frame_delay_var, width=8).pack(side=tk.LEFT, padx=(0, 20))
        
        self.pingpong_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(anim_row, text="Ping-pong animation", variable=self.pingpong_var).pack(side=tk.LEFT)
        
        # ---- Output ----
        output_frame = ttk.LabelFrame(main_frame, text="Output", padding=10)
        output_frame.pack(fill=tk.X, pady=(0, 15))
        
        out_row = ttk.Frame(output_frame)
        out_row.pack(fill=tk.X)
        
        ttk.Label(out_row, text="Output folder:").pack(side=tk.LEFT)
        self.output_label = ttk.Label(out_row, text="(not selected)", foreground="#888")
        self.output_label.pack(side=tk.LEFT, padx=10)
        ttk.Button(out_row, text="Browse...", command=self.select_output_dir).pack(side=tk.LEFT)
        
        # ---- Generate Button ----
        ttk.Button(main_frame, text="Generate Scene", command=self.generate_scene).pack(pady=10)
        
        # ---- Status ----
        self.status_var = tk.StringVar(value="Ready. Add layers and configure your scene.")
        ttk.Label(main_frame, textvariable=self.status_var, foreground="#888").pack(anchor="w")
    
    def add_static_layer(self):
        filepath = filedialog.askopenfilename(
            title="Select static layer PNG",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
        )
        if filepath:
            name = self.prompt_layer_name(Path(filepath).stem)
            if name:
                self.layers.append({
                    "name": name,
                    "type": "static",
                    "source": filepath
                })
                self.update_layer_list()
    
    def add_animated_layer(self):
        folder = filedialog.askdirectory(title="Select folder containing animation frames")
        if folder:
            # Count PNG frames
            frames = sorted(Path(folder).glob("*.png"))
            if not frames:
                messagebox.showerror("Error", "No PNG files found in selected folder.")
                return
            
            name = self.prompt_layer_name(Path(folder).name)
            if name:
                self.layers.append({
                    "name": name,
                    "type": "animated",
                    "source": folder,
                    "frame_count": len(frames)
                })
                self.update_layer_list()
    
    def prompt_layer_name(self, default):
        """Simple dialog to get layer name."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Layer Name")
        dialog.geometry("300x100")
        dialog.transient(self.root)
        dialog.grab_set()
        
        result = [None]
        
        ttk.Label(dialog, text="Layer name:").pack(pady=(15, 5))
        name_var = tk.StringVar(value=default)
        entry = ttk.Entry(dialog, textvariable=name_var, width=30)
        entry.pack()
        entry.select_range(0, tk.END)
        entry.focus()
        
        def confirm():
            result[0] = name_var.get().strip().lower().replace(" ", "-")
            dialog.destroy()
        
        entry.bind("<Return>", lambda e: confirm())
        ttk.Button(dialog, text="OK", command=confirm).pack(pady=10)
        
        self.root.wait_window(dialog)
        return result[0]
    
    def remove_layer(self):
        sel = self.layer_listbox.curselection()
        if sel:
            del self.layers[sel[0]]
            self.update_layer_list()
    
    def move_layer_up(self):
        sel = self.layer_listbox.curselection()
        if sel and sel[0] > 0:
            idx = sel[0]
            self.layers[idx], self.layers[idx-1] = self.layers[idx-1], self.layers[idx]
            self.update_layer_list()
            self.layer_listbox.select_set(idx - 1)
    
    def move_layer_down(self):
        sel = self.layer_listbox.curselection()
        if sel and sel[0] < len(self.layers) - 1:
            idx = sel[0]
            self.layers[idx], self.layers[idx+1] = self.layers[idx+1], self.layers[idx]
            self.update_layer_list()
            self.layer_listbox.select_set(idx + 1)
    
    def update_layer_list(self):
        self.layer_listbox.delete(0, tk.END)
        for i, layer in enumerate(self.layers):
            depth_label = ["(farthest)", "(far)", "(mid)", "(nearest)"]
            depth = depth_label[min(i, 3)]
            if layer["type"] == "static":
                text = f"{i}: {layer['name']} — static PNG {depth}"
            else:
                text = f"{i}: {layer['name']} — {layer['frame_count']} frames {depth}"
            self.layer_listbox.insert(tk.END, text)
    
    def select_output_dir(self):
        folder = filedialog.askdirectory(title="Select output folder (e.g., digital-watercolors/scenes)")
        if folder:
            self.output_dir = folder
            self.output_label.config(text=folder)
    
    def generate_scene(self):
        # Validate
        scene_id = self.scene_id_var.get().strip().lower().replace(" ", "-")
        if not scene_id:
            messagebox.showerror("Error", "Scene ID is required.")
            return
        
        if not self.layers:
            messagebox.showerror("Error", "Add at least one layer.")
            return
        
        if not self.output_dir:
            messagebox.showerror("Error", "Select an output folder.")
            return
        
        try:
            # Create scene folder
            scene_path = Path(self.output_dir) / scene_id
            layers_path = scene_path / "layers"
            audio_path = scene_path / "audio"
            
            scene_path.mkdir(parents=True, exist_ok=True)
            layers_path.mkdir(exist_ok=True)
            audio_path.mkdir(exist_ok=True)
            
            # Build scene.json
            scene_config = {
                "title": self.title_var.get(),
                "subtitle": self.subtitle_var.get(),
                "palette": {
                    "primary": self.pigment1_var.get(),
                    "secondary": self.pigment2_var.get(),
                    "atmosphere": self.atmosphere_var.get() if self.atmosphere_var.get() != "None" else None
                },
                "layers": [],
                "animation": {
                    "frameDelay": int(self.frame_delay_var.get()),
                    "pingPong": self.pingpong_var.get()
                },
                "audio": [],
                "_generated": datetime.now().isoformat(),
                "_generator": "scene-builder.py"
            }
            
            # Process layers
            for i, layer in enumerate(self.layers):
                # Calculate parallax based on depth (0=far, 1=near)
                normalized_depth = i / max(1, len(self.layers) - 1) if len(self.layers) > 1 else 0
                parallax = 0.1 + (normalized_depth * 0.9)  # 0.1 to 1.0
                
                # Calculate atmosphere opacity (far = more haze)
                atmo_opacity = max(0, 0.1 - (normalized_depth * 0.1))  # 0.1 to 0
                
                layer_config = {
                    "id": layer["name"],
                    "depth": i,
                    "parallax": round(parallax, 2),
                    "atmosphereOpacity": round(atmo_opacity, 3)
                }
                
                if layer["type"] == "static":
                    # Copy file
                    src = Path(layer["source"])
                    dst = layers_path / f"{layer['name']}.png"
                    shutil.copy2(src, dst)
                    layer_config["file"] = f"layers/{layer['name']}.png"
                    layer_config["animated"] = False
                else:
                    # Copy animated frames
                    frame_folder = layers_path / layer["name"]
                    frame_folder.mkdir(exist_ok=True)
                    
                    src_folder = Path(layer["source"])
                    frames = sorted(src_folder.glob("*.png"))
                    
                    for j, frame in enumerate(frames):
                        dst = frame_folder / f"frame-{j:03d}.png"
                        shutil.copy2(frame, dst)
                    
                    layer_config["file"] = f"layers/{layer['name']}/frame-{{000}}.png"
                    layer_config["animated"] = True
                    layer_config["frameCount"] = len(frames)
                
                scene_config["layers"].append(layer_config)
            
            # Write scene.json
            with open(scene_path / "scene.json", "w") as f:
                json.dump(scene_config, f, indent=2)
            
            # Copy template HTML (placeholder for now)
            self.create_scene_html(scene_path, scene_config)
            
            self.status_var.set(f"✓ Scene created: {scene_path}")
            messagebox.showinfo("Success", f"Scene created at:\n{scene_path}\n\nFiles:\n- scene.json\n- index.html\n- layers/")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate scene:\n{e}")
            self.status_var.set(f"Error: {e}")
    
    def create_scene_html(self, scene_path, config):
        """Generate the scene HTML file."""
        html = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{config["title"]} — Digital Watercolors</title>
  
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,600;1,400&family=DM+Sans:wght@400;500&family=Press+Start+2P&display=swap" rel="stylesheet">
  
  <style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    
    :root {{
      --scene-primary: var(--pigment-{config["palette"]["primary"].lower().replace(" ", "-").replace("'", "")}, #c9a86c);
      --scene-secondary: var(--pigment-{config["palette"]["secondary"].lower().replace(" ", "-").replace("'", "")}, #5a7247);
    }}
    
    body {{
      background: #0a0a0a;
      color: #f5f5f5;
      font-family: 'DM Sans', sans-serif;
      min-height: 100vh;
      overflow: hidden;
    }}
    
    /* Scene container */
    .scene-container {{
      position: fixed;
      inset: 0;
      display: flex;
      align-items: center;
      justify-content: center;
    }}
    
    .scene-viewport {{
      position: relative;
      width: 100%;
      max-width: 960px;
      aspect-ratio: 16/10;
    }}
    
    /* Layers */
    .layer {{
      position: absolute;
      inset: 0;
      background-size: contain;
      background-position: center;
      background-repeat: no-repeat;
      will-change: transform;
      transition: transform 0.1s ease-out;
    }}
    
    .layer img {{
      width: 100%;
      height: 100%;
      object-fit: contain;
      image-rendering: pixelated;
      image-rendering: crisp-edges;
    }}
    
    /* Atmosphere overlay */
    .layer-atmosphere {{
      position: absolute;
      inset: 0;
      pointer-events: none;
      mix-blend-mode: multiply;
    }}
    
    /* Scene info */
    .scene-info {{
      position: fixed;
      bottom: 2rem;
      left: 50%;
      transform: translateX(-50%);
      text-align: center;
      z-index: 100;
    }}
    
    .scene-title {{
      font-family: 'Cormorant Garamond', serif;
      font-size: 1.5rem;
      font-weight: 600;
      color: #f4e4c1;
      text-shadow: 2px 2px 4px rgba(0,0,0,0.8);
    }}
    
    .scene-subtitle {{
      font-family: 'Cormorant Garamond', serif;
      font-style: italic;
      font-size: 0.9rem;
      color: #a0a0a0;
      margin-top: 0.25rem;
    }}
    
    /* Back button */
    .back-btn {{
      position: fixed;
      top: 1rem;
      left: 1rem;
      font-family: 'DM Sans', sans-serif;
      font-size: 0.8rem;
      color: #888;
      text-decoration: none;
      padding: 0.5rem 1rem;
      border: 2px solid #333;
      background: rgba(0,0,0,0.5);
      z-index: 100;
    }}
    
    .back-btn:hover {{
      color: #c9a86c;
      border-color: #c9a86c;
    }}
    
    /* Sound toggle */
    .sound-toggle {{
      position: fixed;
      top: 1rem;
      right: 1rem;
      font-size: 1.5rem;
      background: none;
      border: none;
      cursor: pointer;
      opacity: 0.6;
      z-index: 100;
    }}
    
    .sound-toggle:hover {{
      opacity: 1;
    }}
  </style>
</head>
<body>

  <a href="../../" class="back-btn">← Back</a>
  
  <button class="sound-toggle" id="sound-toggle" aria-label="Toggle sound">🔇</button>
  
  <div class="scene-container">
    <div class="scene-viewport" id="viewport">
      <!-- Layers injected by JS -->
    </div>
  </div>
  
  <div class="scene-info">
    <h1 class="scene-title">{config["title"]}</h1>
    <p class="scene-subtitle">{config["subtitle"]}</p>
  </div>

  <script src="../../watercolor-engine/watercolor-engine.js"></script>
  <script>
    // Scene configuration (from scene.json)
    const sceneConfig = {json.dumps(config, indent=2)};
    
    // ========================================
    // LAYERED SCENE RENDERER
    // ========================================
    const Scene = {{
      viewport: null,
      layers: [],
      engine: null,
      frameIndex: 0,
      frameDirection: 1,
      lastFrameTime: 0,
      
      async init() {{
        this.viewport = document.getElementById('viewport');
        
        // Initialize watercolor engine
        if (typeof WatercolorEngine !== 'undefined') {{
          this.engine = new WatercolorEngine();
        }}
        
        // Create layer elements
        await this.createLayers();
        
        // Start animation
        this.animate();
        
        // Setup parallax
        this.setupParallax();
      }},
      
      async createLayers() {{
        for (const layerConfig of sceneConfig.layers) {{
          const layerEl = document.createElement('div');
          layerEl.className = 'layer';
          layerEl.dataset.parallax = layerConfig.parallax;
          layerEl.style.zIndex = layerConfig.depth;
          
          const img = document.createElement('img');
          
          if (layerConfig.animated) {{
            // Load all frames
            const frames = [];
            for (let i = 0; i < layerConfig.frameCount; i++) {{
              const framePath = layerConfig.file.replace('{{000}}', String(i).padStart(3, '0'));
              frames.push(framePath);
            }}
            layerEl.dataset.frames = JSON.stringify(frames);
            layerEl.dataset.animated = 'true';
            img.src = frames[0];
          }} else {{
            img.src = layerConfig.file;
          }}
          
          img.alt = layerConfig.id;
          layerEl.appendChild(img);
          
          // Add atmosphere overlay if needed
          if (layerConfig.atmosphereOpacity > 0 && this.engine && sceneConfig.palette.atmosphere) {{
            const atmospherePigment = this.engine.findPigment(sceneConfig.palette.atmosphere);
            if (atmospherePigment) {{
              const glazeColor = this.engine.glaze(this.engine.paperWhite, atmospherePigment);
              const overlay = document.createElement('div');
              overlay.className = 'layer-atmosphere';
              overlay.style.backgroundColor = glazeColor;
              overlay.style.opacity = layerConfig.atmosphereOpacity;
              layerEl.appendChild(overlay);
            }}
          }}
          
          this.viewport.appendChild(layerEl);
          this.layers.push({{ el: layerEl, config: layerConfig }});
        }}
      }},
      
      setupParallax() {{
        const maxShift = 30;
        
        const applyParallax = (xNorm, yNorm) => {{
          this.layers.forEach(layer => {{
            const parallax = parseFloat(layer.el.dataset.parallax);
            const shiftX = (xNorm - 0.5) * maxShift * parallax;
            const shiftY = (yNorm - 0.5) * maxShift * parallax * 0.5;
            layer.el.style.transform = `translate(${{shiftX}}px, ${{shiftY}}px)`;
          }});
        }};
        
        // Mouse
        window.addEventListener('mousemove', (e) => {{
          const xNorm = e.clientX / window.innerWidth;
          const yNorm = e.clientY / window.innerHeight;
          applyParallax(xNorm, yNorm);
        }});
        
        // Device orientation
        if ('DeviceOrientationEvent' in window) {{
          const setupOrientation = () => {{
            window.addEventListener('deviceorientation', (e) => {{
              if (e.gamma === null) return;
              const xNorm = (e.gamma + 45) / 90;
              const yNorm = (e.beta - 30) / 60;
              applyParallax(
                Math.min(1, Math.max(0, xNorm)),
                Math.min(1, Math.max(0, yNorm))
              );
            }}, {{ passive: true }});
          }};
          
          if (typeof DeviceOrientationEvent.requestPermission === 'function') {{
            // iOS - need user gesture
            document.addEventListener('click', () => {{
              DeviceOrientationEvent.requestPermission().then(p => {{
                if (p === 'granted') setupOrientation();
              }});
            }}, {{ once: true }});
          }} else {{
            setupOrientation();
          }}
        }}
      }},
      
      animate(timestamp = 0) {{
        // Update animated layers
        if (timestamp - this.lastFrameTime >= sceneConfig.animation.frameDelay) {{
          this.lastFrameTime = timestamp;
          
          this.layers.forEach(layer => {{
            if (layer.el.dataset.animated === 'true') {{
              const frames = JSON.parse(layer.el.dataset.frames);
              const img = layer.el.querySelector('img');
              img.src = frames[this.frameIndex % frames.length];
            }}
          }});
          
          // Update frame index
          const maxFrames = Math.max(...this.layers
            .filter(l => l.config.animated)
            .map(l => l.config.frameCount), 1);
          
          if (sceneConfig.animation.pingPong) {{
            this.frameIndex += this.frameDirection;
            if (this.frameIndex >= maxFrames - 1) this.frameDirection = -1;
            if (this.frameIndex <= 0) this.frameDirection = 1;
          }} else {{
            this.frameIndex = (this.frameIndex + 1) % maxFrames;
          }}
        }}
        
        requestAnimationFrame((t) => this.animate(t));
      }}
    }};
    
    // Initialize
    Scene.init();
  </script>

</body>
</html>
'''
        
        with open(scene_path / "index.html", "w") as f:
            f.write(html)


# ============================================
# MAIN
# ============================================
if __name__ == "__main__":
    root = tk.Tk()
    app = SceneBuilder(root)
    root.mainloop()
