#!/usr/bin/env python3
"""
Digital Watercolors Scene Manager v1.0
Local web interface for managing your animated watercolor scenes.

SETUP:
    pip install flask pillow

USAGE:
    python scene-manager.py
    Open http://localhost:5002

Features:
- Create new scenes with folder structure
- Upload animation frames (auto-renamed to frame-000.png, etc.)
- Upload ambient audio files
- Preview scenes before publishing
- Update scenes.js automatically
- Commit and push to GitHub
"""

import os
import re
import subprocess
import json
import shutil
from datetime import datetime
from pathlib import Path

from flask import Flask, render_template_string, request, redirect, url_for, flash, send_from_directory

app = Flask(__name__)
app.secret_key = 'digital-watercolors-2025'

PROJECT_ROOT = Path(__file__).parent.resolve()
SCENES_DIR = PROJECT_ROOT / "scenes"
SCENES_JS = PROJECT_ROOT / "scenes.js"
HUB_FRAMES_DIR = PROJECT_ROOT / "hub-frames"

# =============================================================================
# SCENE DATA MANAGEMENT
# =============================================================================

def load_scenes_config():
    """Load scenes from scenes.js."""
    if not SCENES_JS.exists():
        return []
    
    with open(SCENES_JS, 'r', encoding='utf-8') as f:
        content = f.read()
    
    scenes = []
    # Match each scene object
    for match in re.finditer(r'\{\s*id:\s*"([^"]+)",\s*label:\s*"([^"]+)",\s*ready:\s*(true|false)', content):
        scenes.append({
            'id': match.group(1),
            'label': match.group(2),
            'ready': match.group(3) == 'true'
        })
    
    return scenes


def save_scenes_config(scenes):
    """Save scenes to scenes.js."""
    lines = [
        '// ============================================',
        '// SCENES CONFIG - Edit this to add/remove scenes',
        '// ============================================',
        '// Each scene needs:',
        '//   id: folder name in scenes/',
        '//   label: what shows on the menu button',
        '//   ready: set to true when frames are added',
        '// ============================================',
        '',
        'const SCENES = ['
    ]
    
    for i, scene in enumerate(scenes):
        ready_str = 'true' if scene['ready'] else 'false'
        comma = ',' if i < len(scenes) - 1 else ''
        lines.append(f'  {{')
        lines.append(f'    id: "{scene["id"]}",')
        lines.append(f'    label: "{scene["label"]}",')
        lines.append(f'    ready: {ready_str}')
        lines.append(f'  }}{comma}')
    
    lines.append('];')
    
    with open(SCENES_JS, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')


def get_scene_details(scene_id):
    """Get detailed info about a scene (frame count, audio files, etc.)."""
    scene_dir = SCENES_DIR / scene_id
    frames_dir = scene_dir / "frames"
    audio_dir = scene_dir / "audio"
    
    details = {
        'id': scene_id,
        'exists': scene_dir.exists(),
        'frame_count': 0,
        'frames': [],
        'audio_files': [],
        'has_index': (scene_dir / "index.html").exists()
    }
    
    if frames_dir.exists():
        frames = sorted([f.name for f in frames_dir.glob("frame-*.png")])
        details['frames'] = frames
        details['frame_count'] = len(frames)
    
    if audio_dir.exists():
        audio_files = [f.name for f in audio_dir.glob("*.mp3")]
        details['audio_files'] = audio_files
    
    return details


def slugify(text):
    """Convert text to URL-friendly slug."""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text)
    text = re.sub(r'^-+|-+$', '', text)
    return text


def create_scene_folder(scene_id):
    """Create the folder structure for a new scene."""
    scene_dir = SCENES_DIR / scene_id
    (scene_dir / "frames").mkdir(parents=True, exist_ok=True)
    (scene_dir / "audio").mkdir(parents=True, exist_ok=True)
    return scene_dir


def create_scene_html(scene_id, title, subtitle):
    """Create the index.html for a scene from template."""
    template_path = SCENES_DIR / "mister-softee" / "index.html"
    
    if template_path.exists():
        with open(template_path, 'r', encoding='utf-8') as f:
            html = f.read()
        
        # Update title tag
        html = re.sub(r'<title>.*?</title>', f'<title>{title} — Digital Watercolors</title>', html)
        
        # Update scene title
        html = re.sub(
            r'<div class="scene-title"[^>]*>.*?</div>',
            f'''<div class="scene-title" id="scene-title">
    <h1>{title}</h1>
    <p>{subtitle}</p>
  </div>''',
            html,
            flags=re.DOTALL
        )
        
        # Update emoji favicon based on scene
        emoji_map = {
            'ice-cream': '🍦', 'softee': '🍦', 'food': '🍕', 
            'subway': '🚇', 'train': '🚂',
            'park': '🌳', 'central': '🌳',
            'museum': '🏛️', 'building': '🏢',
            'default': '🎨'
        }
        emoji = '🎨'
        for key, val in emoji_map.items():
            if key in scene_id.lower() or key in title.lower():
                emoji = val
                break
        html = re.sub(r"<text y='.9em' font-size='90'>.</text>", f"<text y='.9em' font-size='90'>{emoji}</text>", html)
        
    else:
        # Fallback: create minimal template
        html = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title} — Digital Watercolors</title>
  <style>
    body {{ background: #1a1a1a; color: #f5f5f5; font-family: sans-serif; display: flex; align-items: center; justify-content: center; min-height: 100vh; margin: 0; }}
    .message {{ text-align: center; }}
    a {{ color: #c4703f; }}
  </style>
</head>
<body>
  <div class="message">
    <h1>{title}</h1>
    <p>{subtitle}</p>
    <p>Scene template needed. Copy from mister-softee.</p>
    <p><a href="../../">← Back to hub</a></p>
  </div>
</body>
</html>'''
    
    scene_dir = SCENES_DIR / scene_id
    with open(scene_dir / "index.html", 'w', encoding='utf-8') as f:
        f.write(html)


# =============================================================================
# GIT OPERATIONS
# =============================================================================

def git_status():
    """Get current git status."""
    try:
        result = subprocess.run(
            ['git', 'status', '--porcelain'],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True
        )
        return result.stdout.strip().split('\n') if result.stdout.strip() else []
    except:
        return []


def git_commit_and_push(message):
    """Stage all changes, commit, and push."""
    try:
        # Stage all changes
        subprocess.run(['git', 'add', '-A'], cwd=PROJECT_ROOT, check=True)
        
        # Commit
        result = subprocess.run(
            ['git', 'commit', '-m', message],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0 and 'nothing to commit' in result.stdout:
            return True, "Nothing to commit - already up to date"
        
        # Push
        result = subprocess.run(
            ['git', 'push'],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            return True, "Deployed successfully!"
        else:
            return False, f"Push failed: {result.stderr}"
            
    except Exception as e:
        return False, f"Error: {e}"


# =============================================================================
# HTML TEMPLATE
# =============================================================================

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Scene Manager — Digital Watercolors</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg: #1a1a1a;
            --bg-card: #242424;
            --bg-input: #2a2a2a;
            --text: #f5f5f5;
            --text-muted: #888;
            --terracotta: #c4703f;
            --terracotta-light: #d4845a;
            --green: #4a9f4a;
            --red: #c44a4a;
            --border: #3a3a3a;
        }
        
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'DM Sans', sans-serif;
            background: var(--bg);
            color: var(--text);
            min-height: 100vh;
            padding: 2rem;
        }
        
        .container {
            max-width: 1000px;
            margin: 0 auto;
        }
        
        header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 2rem;
            padding-bottom: 1rem;
            border-bottom: 1px solid var(--border);
        }
        
        h1 {
            font-size: 1.5rem;
            font-weight: 500;
        }
        
        h1 span { color: var(--terracotta); }
        
        .header-links a {
            color: var(--text-muted);
            text-decoration: none;
            margin-left: 1.5rem;
            font-size: 0.9rem;
        }
        
        .header-links a:hover { color: var(--terracotta); }
        
        .tabs {
            display: flex;
            gap: 0.5rem;
            margin-bottom: 2rem;
        }
        
        .tab {
            padding: 0.75rem 1.5rem;
            background: var(--bg-card);
            border: none;
            color: var(--text-muted);
            cursor: pointer;
            font-family: inherit;
            font-size: 0.9rem;
            border-radius: 4px 4px 0 0;
            transition: all 0.2s;
        }
        
        .tab:hover { color: var(--text); }
        .tab.active { background: var(--terracotta); color: white; }
        
        .tab-content { display: none; }
        .tab-content.active { display: block; }
        
        .card {
            background: var(--bg-card);
            border-radius: 8px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
        }
        
        .card h2 {
            font-size: 1.1rem;
            font-weight: 500;
            margin-bottom: 1rem;
            color: var(--terracotta);
        }
        
        .form-group {
            margin-bottom: 1rem;
        }
        
        .form-group label {
            display: block;
            font-size: 0.85rem;
            color: var(--text-muted);
            margin-bottom: 0.4rem;
        }
        
        input[type="text"], input[type="file"], select, textarea {
            width: 100%;
            padding: 0.75rem;
            background: var(--bg-input);
            border: 1px solid var(--border);
            border-radius: 4px;
            color: var(--text);
            font-family: inherit;
            font-size: 0.95rem;
        }
        
        input:focus, select:focus, textarea:focus {
            outline: none;
            border-color: var(--terracotta);
        }
        
        .btn {
            padding: 0.75rem 1.5rem;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-family: inherit;
            font-size: 0.9rem;
            font-weight: 500;
            transition: all 0.2s;
        }
        
        .btn-primary {
            background: var(--terracotta);
            color: white;
        }
        
        .btn-primary:hover { background: var(--terracotta-light); }
        
        .btn-secondary {
            background: var(--bg-input);
            color: var(--text);
            border: 1px solid var(--border);
        }
        
        .btn-secondary:hover { border-color: var(--terracotta); }
        
        .btn-danger {
            background: var(--red);
            color: white;
        }
        
        .btn-small {
            padding: 0.4rem 0.8rem;
            font-size: 0.8rem;
        }
        
        .message {
            padding: 1rem;
            border-radius: 4px;
            margin-bottom: 1.5rem;
        }
        
        .message.success { background: rgba(74, 159, 74, 0.2); border: 1px solid var(--green); }
        .message.error { background: rgba(196, 74, 74, 0.2); border: 1px solid var(--red); }
        
        .scene-list {
            display: grid;
            gap: 1rem;
        }
        
        .scene-item {
            display: flex;
            align-items: center;
            gap: 1rem;
            padding: 1rem;
            background: var(--bg-input);
            border-radius: 6px;
        }
        
        .scene-status {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            flex-shrink: 0;
        }
        
        .scene-status.ready { background: var(--green); }
        .scene-status.draft { background: var(--text-muted); }
        
        .scene-info { flex: 1; }
        .scene-info h3 { font-size: 1rem; font-weight: 500; margin-bottom: 0.25rem; }
        .scene-info p { font-size: 0.85rem; color: var(--text-muted); }
        
        .scene-meta {
            text-align: right;
            font-size: 0.8rem;
            color: var(--text-muted);
        }
        
        .scene-actions {
            display: flex;
            gap: 0.5rem;
        }
        
        .help-text {
            font-size: 0.8rem;
            color: var(--text-muted);
            margin-top: 0.4rem;
        }
        
        .file-list {
            margin-top: 0.5rem;
            padding: 0.75rem;
            background: var(--bg);
            border-radius: 4px;
            font-size: 0.85rem;
        }
        
        .file-list code {
            display: block;
            color: var(--text-muted);
            margin: 0.2rem 0;
        }
        
        .inline-form {
            display: flex;
            gap: 0.5rem;
            align-items: end;
        }
        
        .inline-form .form-group { flex: 1; margin-bottom: 0; }
        
        .git-changes {
            font-family: monospace;
            font-size: 0.8rem;
            background: var(--bg);
            padding: 1rem;
            border-radius: 4px;
            max-height: 200px;
            overflow-y: auto;
        }
        
        .git-changes .added { color: var(--green); }
        .git-changes .modified { color: var(--terracotta); }
        .git-changes .deleted { color: var(--red); }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1><span>Digital Watercolors</span> Scene Manager</h1>
            <div class="header-links">
                <a href="./" target="_blank">Preview Hub</a>
                <a href="https://haslun.me/projects/digital-watercolors" target="_blank">Live Site</a>
            </div>
        </header>
        
        {% if message %}
        <div class="message {{ 'success' if success == 'true' else 'error' }}">
            {{ message }}
        </div>
        {% endif %}
        
        <div class="tabs">
            <button class="tab {{ 'active' if tab == 'scenes' }}" onclick="showTab('scenes')">Scenes</button>
            <button class="tab {{ 'active' if tab == 'new' }}" onclick="showTab('new')">New Scene</button>
            <button class="tab {{ 'active' if tab == 'upload' }}" onclick="showTab('upload')">Upload</button>
            <button class="tab {{ 'active' if tab == 'deploy' }}" onclick="showTab('deploy')">Deploy</button>
        </div>
        
        <!-- SCENES TAB -->
        <div id="tab-scenes" class="tab-content {{ 'active' if tab == 'scenes' }}">
            <div class="card">
                <h2>Current Scenes</h2>
                <div class="scene-list">
                    {% for scene in scenes %}
                    <div class="scene-item">
                        <div class="scene-status {{ 'ready' if scene.ready else 'draft' }}"></div>
                        <div class="scene-info">
                            <h3>{{ scene.label }}</h3>
                            <p>scenes/{{ scene.id }}/</p>
                        </div>
                        <div class="scene-meta">
                            {% set details = scene_details.get(scene.id, {}) %}
                            {{ details.get('frame_count', 0) }} frames<br>
                            {{ details.get('audio_files', [])|length }} audio
                        </div>
                        <div class="scene-actions">
                            <a href="scenes/{{ scene.id }}/" target="_blank" class="btn btn-secondary btn-small">Preview</a>
                            <form action="/toggle-ready" method="POST" style="display:inline;">
                                <input type="hidden" name="id" value="{{ scene.id }}">
                                <button type="submit" class="btn btn-small {{ 'btn-primary' if not scene.ready else 'btn-secondary' }}">
                                    {{ 'Publish' if not scene.ready else 'Unpublish' }}
                                </button>
                            </form>
                            <form action="/delete-scene" method="POST" style="display:inline;" onsubmit="return confirm('Delete this scene?');">
                                <input type="hidden" name="id" value="{{ scene.id }}">
                                <button type="submit" class="btn btn-danger btn-small">Delete</button>
                            </form>
                        </div>
                    </div>
                    {% else %}
                    <p style="color: var(--text-muted);">No scenes yet. Create one in the "New Scene" tab.</p>
                    {% endfor %}
                </div>
            </div>
            
            <div class="card">
                <h2>Hub Animation</h2>
                <p style="color: var(--text-muted); margin-bottom: 1rem;">
                    The breathing peacocks background. {{ hub_frame_count }} frames in hub-frames/.
                </p>
                <a href="./" target="_blank" class="btn btn-secondary btn-small">Preview Hub</a>
            </div>
        </div>
        
        <!-- NEW SCENE TAB -->
        <div id="tab-new" class="tab-content {{ 'active' if tab == 'new' }}">
            <div class="card">
                <h2>Create New Scene</h2>
                <form action="/create-scene" method="POST">
                    <div class="form-group">
                        <label>Scene ID (folder name)</label>
                        <input type="text" name="scene_id" placeholder="e.g., subway-72nd" required pattern="[a-z0-9-]+">
                        <p class="help-text">Lowercase letters, numbers, and hyphens only</p>
                    </div>
                    <div class="form-group">
                        <label>Menu Label</label>
                        <input type="text" name="label" placeholder="e.g., Catch the train?" required>
                        <p class="help-text">What visitors see on the hub menu</p>
                    </div>
                    <div class="form-group">
                        <label>Scene Title</label>
                        <input type="text" name="title" placeholder="e.g., 72nd Street Subway" required>
                        <p class="help-text">Shown when entering the scene</p>
                    </div>
                    <div class="form-group">
                        <label>Subtitle</label>
                        <input type="text" name="subtitle" placeholder="e.g., Upper West Side, Morning" required>
                    </div>
                    <button type="submit" class="btn btn-primary">Create Scene</button>
                </form>
            </div>
        </div>
        
        <!-- UPLOAD TAB -->
        <div id="tab-upload" class="tab-content {{ 'active' if tab == 'upload' }}">
            <div class="card">
                <h2>Upload Animation Frames</h2>
                <form action="/upload-frames" method="POST" enctype="multipart/form-data">
                    <div class="form-group">
                        <label>Scene</label>
                        <select name="scene_id" required>
                            <option value="">Select a scene...</option>
                            {% for scene in scenes %}
                            <option value="{{ scene.id }}">{{ scene.label }} ({{ scene.id }})</option>
                            {% endfor %}
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Frames (PNG files)</label>
                        <input type="file" name="frames" multiple accept=".png" required>
                        <p class="help-text">Select all frames. They will be auto-renamed to frame-000.png, frame-001.png, etc.</p>
                    </div>
                    <button type="submit" class="btn btn-primary">Upload Frames</button>
                </form>
            </div>
            
            <div class="card">
                <h2>Upload Audio</h2>
                <form action="/upload-audio" method="POST" enctype="multipart/form-data">
                    <div class="form-group">
                        <label>Scene</label>
                        <select name="scene_id" required>
                            <option value="">Select a scene...</option>
                            {% for scene in scenes %}
                            <option value="{{ scene.id }}">{{ scene.label }} ({{ scene.id }})</option>
                            {% endfor %}
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Audio File (MP3)</label>
                        <input type="file" name="audio" accept=".mp3" required>
                        <p class="help-text">Ambient sound for the scene. Keep it subtle and loopable.</p>
                    </div>
                    <button type="submit" class="btn btn-primary">Upload Audio</button>
                </form>
            </div>
        </div>
        
        <!-- DEPLOY TAB -->
        <div id="tab-deploy" class="tab-content {{ 'active' if tab == 'deploy' }}">
            <div class="card">
                <h2>Pending Changes</h2>
                <div class="git-changes">
                    {% if git_changes %}
                        {% for change in git_changes %}
                        <div class="{{ 'added' if change.startswith('A') or change.startswith('?') else 'modified' if change.startswith('M') else 'deleted' if change.startswith('D') else '' }}">{{ change }}</div>
                        {% endfor %}
                    {% else %}
                        <p style="color: var(--text-muted);">No changes to deploy.</p>
                    {% endif %}
                </div>
            </div>
            
            <div class="card">
                <h2>Deploy to GitHub</h2>
                <form action="/deploy" method="POST">
                    <div class="form-group">
                        <label>Commit Message</label>
                        <input type="text" name="commit_message" value="Update digital watercolors" required>
                    </div>
                    <button type="submit" class="btn btn-primary" {{ 'disabled' if not git_changes }}>
                        Commit & Push
                    </button>
                </form>
            </div>
        </div>
    </div>
    
    <script>
        function showTab(tabName) {
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            document.querySelector(`.tab-content#tab-${tabName}`).classList.add('active');
            event.target.classList.add('active');
            history.replaceState(null, '', `?tab=${tabName}`);
        }
    </script>
</body>
</html>
'''


# =============================================================================
# ROUTES
# =============================================================================

@app.route('/')
def index():
    tab = request.args.get('tab', 'scenes')
    message = request.args.get('message')
    success = request.args.get('success', 'true')
    
    scenes = load_scenes_config()
    scene_details = {s['id']: get_scene_details(s['id']) for s in scenes}
    
    hub_frame_count = len(list(HUB_FRAMES_DIR.glob("frame-*.png"))) if HUB_FRAMES_DIR.exists() else 0
    
    return render_template_string(
        HTML_TEMPLATE,
        tab=tab,
        message=message,
        success=success,
        scenes=scenes,
        scene_details=scene_details,
        hub_frame_count=hub_frame_count,
        git_changes=git_status()
    )


@app.route('/create-scene', methods=['POST'])
def create_scene():
    try:
        scene_id = slugify(request.form.get('scene_id', ''))
        label = request.form.get('label', '')
        title = request.form.get('title', '')
        subtitle = request.form.get('subtitle', '')
        
        if not scene_id or not label:
            return redirect(url_for('index', tab='new', message='Scene ID and label required', success='false'))
        
        # Check if exists
        if (SCENES_DIR / scene_id).exists():
            return redirect(url_for('index', tab='new', message=f'Scene "{scene_id}" already exists', success='false'))
        
        # Create folder structure
        create_scene_folder(scene_id)
        
        # Create HTML
        create_scene_html(scene_id, title, subtitle)
        
        # Add to scenes.js
        scenes = load_scenes_config()
        scenes.append({
            'id': scene_id,
            'label': label,
            'ready': False
        })
        save_scenes_config(scenes)
        
        return redirect(url_for('index', tab='scenes', message=f'Created scene "{label}"', success='true'))
        
    except Exception as e:
        return redirect(url_for('index', tab='new', message=f'Error: {e}', success='false'))


@app.route('/upload-frames', methods=['POST'])
def upload_frames():
    try:
        scene_id = request.form.get('scene_id')
        files = request.files.getlist('frames')
        
        if not scene_id or not files:
            return redirect(url_for('index', tab='upload', message='Scene and files required', success='false'))
        
        frames_dir = SCENES_DIR / scene_id / "frames"
        if not frames_dir.exists():
            return redirect(url_for('index', tab='upload', message=f'Scene "{scene_id}" not found', success='false'))
        
        # Clear existing frames
        for old_frame in frames_dir.glob("frame-*.png"):
            old_frame.unlink()
        
        # Sort files by name and save with proper naming
        sorted_files = sorted(files, key=lambda f: f.filename)
        
        for i, file in enumerate(sorted_files):
            if file.filename.endswith('.png'):
                new_name = f"frame-{i:03d}.png"
                file.save(frames_dir / new_name)
        
        # Update frame count in scene's index.html
        update_scene_frame_count(scene_id, len(sorted_files))
        
        return redirect(url_for('index', tab='scenes', message=f'Uploaded {len(sorted_files)} frames to {scene_id}', success='true'))
        
    except Exception as e:
        return redirect(url_for('index', tab='upload', message=f'Error: {e}', success='false'))


def update_scene_frame_count(scene_id, count):
    """Update the frameCount in a scene's index.html."""
    html_path = SCENES_DIR / scene_id / "index.html"
    if html_path.exists():
        with open(html_path, 'r', encoding='utf-8') as f:
            html = f.read()
        
        html = re.sub(r'frameCount:\s*\d+', f'frameCount: {count}', html)
        
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html)


@app.route('/upload-audio', methods=['POST'])
def upload_audio():
    try:
        scene_id = request.form.get('scene_id')
        file = request.files.get('audio')
        
        if not scene_id or not file:
            return redirect(url_for('index', tab='upload', message='Scene and file required', success='false'))
        
        audio_dir = SCENES_DIR / scene_id / "audio"
        if not audio_dir.exists():
            return redirect(url_for('index', tab='upload', message=f'Scene "{scene_id}" not found', success='false'))
        
        # Save the audio file
        filename = file.filename.replace(' ', '-').lower()
        file.save(audio_dir / filename)
        
        return redirect(url_for('index', tab='scenes', message=f'Uploaded {filename} to {scene_id}', success='true'))
        
    except Exception as e:
        return redirect(url_for('index', tab='upload', message=f'Error: {e}', success='false'))


@app.route('/toggle-ready', methods=['POST'])
def toggle_ready():
    try:
        scene_id = request.form.get('id')
        
        scenes = load_scenes_config()
        for scene in scenes:
            if scene['id'] == scene_id:
                scene['ready'] = not scene['ready']
                status = 'published' if scene['ready'] else 'unpublished'
                break
        
        save_scenes_config(scenes)
        
        return redirect(url_for('index', tab='scenes', message=f'Scene {status}', success='true'))
        
    except Exception as e:
        return redirect(url_for('index', tab='scenes', message=f'Error: {e}', success='false'))


@app.route('/delete-scene', methods=['POST'])
def delete_scene():
    try:
        scene_id = request.form.get('id')
        
        # Remove folder
        scene_dir = SCENES_DIR / scene_id
        if scene_dir.exists():
            shutil.rmtree(scene_dir)
        
        # Remove from config
        scenes = load_scenes_config()
        scenes = [s for s in scenes if s['id'] != scene_id]
        save_scenes_config(scenes)
        
        return redirect(url_for('index', tab='scenes', message=f'Deleted scene "{scene_id}"', success='true'))
        
    except Exception as e:
        return redirect(url_for('index', tab='scenes', message=f'Error: {e}', success='false'))


@app.route('/deploy', methods=['POST'])
def deploy():
    message = request.form.get('commit_message', 'Update digital watercolors')
    success, result = git_commit_and_push(message)
    return redirect(url_for('index', tab='deploy', message=result, success=str(success).lower()))


# =============================================================================
# MAIN
# =============================================================================

if __name__ == '__main__':
    print(f"""
{'='*60}
  Digital Watercolors Scene Manager v1.0
{'='*60}

  Project:  {PROJECT_ROOT}
  Scenes:   {SCENES_DIR}
  
  Open: http://localhost:5002

{'='*60}
""")
    app.run(debug=True, port=5002)
