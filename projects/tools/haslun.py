#!/usr/bin/env python3
"""
Haslun Projects Scaffolder

Creates new templates and pages for the Haslun projects ecosystem.

Usage:
    python tools/haslun.py new-template posters --from cards
    python tools/haslun.py new-page cards birthday-jane --title "Happy Birthday, Jane"
    python tools/haslun.py list
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
from pathlib import Path
from datetime import date

# Resolve paths relative to this script
ROOT = Path(__file__).resolve().parents[1]  # projects/ folder
REGISTRY = ROOT / "registry.json"


def slugify(s: str) -> str:
    """Convert a string to a URL-safe slug."""
    s = s.strip().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = re.sub(r"-{2,}", "-", s).strip("-")
    return s or "untitled"


def ensure_projects_root():
    """Verify we're running from the correct location."""
    if not ROOT.exists():
        raise SystemExit(f"Expected {ROOT} to exist. Are you running from repo root?")


def load_registry() -> dict:
    """Load the project registry."""
    if REGISTRY.exists():
        return json.loads(REGISTRY.read_text(encoding="utf-8"))
    return {"projects": [], "categories": {}}


def save_registry(reg: dict):
    """Save the project registry."""
    REGISTRY.write_text(json.dumps(reg, indent=2), encoding="utf-8")


def load_category_index(category: str) -> dict:
    """Load a category's index.json."""
    index_path = ROOT / category / "index.json"
    if index_path.exists():
        return json.loads(index_path.read_text(encoding="utf-8"))
    return {"category": category, "pages": []}


def save_category_index(category: str, data: dict):
    """Save a category's index.json."""
    index_path = ROOT / category / "index.json"
    index_path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def add_category_if_missing(reg: dict, category: str):
    """Add a category to the registry if it doesn't exist."""
    if category not in reg.get("categories", {}):
        reg.setdefault("categories", {})[category] = {
            "label": category.replace("-", " ").title(),
            "icon": "📄",
            "status": "active"
        }


def new_template(category: str, from_category: str | None):
    """Create a new template category."""
    ensure_projects_root()
    category = slugify(category)
    dst = ROOT / category / "_template"

    if dst.exists():
        raise SystemExit(f"Template already exists: {dst}")

    dst.parent.mkdir(parents=True, exist_ok=True)

    if from_category:
        src = ROOT / slugify(from_category) / "_template"
        if not src.exists():
            raise SystemExit(f"Source template not found: {src}")
        shutil.copytree(src, dst)
        print(f"✅ Copied template from {from_category}")
    else:
        # Create minimal skeleton
        dst.mkdir(parents=True, exist_ok=True)
        (dst / "assets").mkdir(exist_ok=True)
        (dst / "assets" / "css").mkdir(parents=True, exist_ok=True)
        (dst / "assets" / "js").mkdir(parents=True, exist_ok=True)
        (dst / "assets" / "img").mkdir(parents=True, exist_ok=True)
        
        # Create app.json
        (dst / "app.json").write_text(json.dumps({
            "id": f"{category}-template",
            "title": f"{category.title()} Template",
            "type": category,
            "modeDefault": "glass",
            "loader": "dom",
            "share": {"noIndex": True, "ogImage": "og.png"},
            "atmosphere": {"livingWashes": True}
        }, indent=2), encoding="utf-8")
        
        # Create minimal index.html
        (dst / "index.html").write_text(f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="robots" content="noindex, nofollow">
  <title>{category.title()} Template</title>
  <meta property="og:title" content="{category.title()} Template">
  <meta property="og:image" content="./og.png">
  
  <!-- Early boot -->
  <script src="../../shared/assets/js/boot.js"></script>
  <script>HaslunBoot.early();</script>
  
  <!-- Styles -->
  <link rel="stylesheet" href="../../shared/assets/css/base.css">
  <link rel="stylesheet" href="../../shared/ui/loader.css">
  <link rel="stylesheet" href="../../shared/ui/glass-overlay.css">
  <link rel="stylesheet" href="../../shared/ui/pixel-overlay.css">
</head>
<body>
  <div class="loading" id="loading">
    <div class="loading-content">
      <p class="loading-text">loading...</p>
      <div class="loading-bar">
        <div class="loading-bar-fill" id="loading-fill"></div>
      </div>
    </div>
  </div>

  <main>
    <h1>{category.title()} Template</h1>
    <p>Edit this template to create your {category}.</p>
  </main>

  <script src="../../shared/watercolor-engine/watercolor-engine.js"></script>
  <script src="../../shared/assets/js/loader.js"></script>
  <script src="../../shared/assets/js/atmosphere.js"></script>
  <script src="../../shared/assets/js/pixel-mode.js"></script>
  
  <script>
    async function init() {{
      const ctx = await HaslunBoot.boot({{ configUrl: './app.json' }});
      await ctx.preloadAndInit([]);
    }}
    init();
  </script>
</body>
</html>
''', encoding="utf-8")

    # Create category index.json
    save_category_index(category, {
        "category": category,
        "title": category.replace("-", " ").title(),
        "pages": []
    })

    # Update main registry
    reg = load_registry()
    add_category_if_missing(reg, category)
    
    # Add to projects list if not there
    project_entry = {
        "id": category,
        "title": category.replace("-", " ").title(),
        "path": f"/projects/{category}/",
        "category": category,
        "status": "template"
    }
    if not any(p["id"] == category for p in reg.get("projects", [])):
        reg.setdefault("projects", []).append(project_entry)
    
    save_registry(reg)
    print(f"✅ Created template: {dst}")


def new_page(category: str, slug: str, title: str | None):
    """Create a new page from a template."""
    ensure_projects_root()
    category = slugify(category)
    slug = slugify(slug)
    tmpl = ROOT / category / "_template"
    
    if not tmpl.exists():
        raise SystemExit(f"Template not found: {tmpl}")

    dst = ROOT / category / slug
    if dst.exists():
        raise SystemExit(f"Destination already exists: {dst}")

    shutil.copytree(tmpl, dst)

    # Update app.json
    app_json = dst / "app.json"
    if app_json.exists():
        data = json.loads(app_json.read_text(encoding="utf-8"))
        data["id"] = f"{category}:{slug}"
        if title:
            data["title"] = title
        data["created"] = str(date.today())
        app_json.write_text(json.dumps(data, indent=2), encoding="utf-8")

    # Update <title> and og:title in index.html
    if title:
        index = dst / "index.html"
        if index.exists():
            html = index.read_text(encoding="utf-8")
            html = re.sub(r"<title>.*?</title>", f"<title>{title}</title>", html, flags=re.DOTALL)
            html = re.sub(r'property="og:title"\s+content=".*?"', f'property="og:title" content="{title}"', html)
            index.write_text(html, encoding="utf-8")

    # Update category index
    cat_index = load_category_index(category)
    cat_index["pages"].append({
        "slug": slug,
        "title": title or slug.replace("-", " ").title(),
        "created": str(date.today()),
        "status": "draft"
    })
    save_category_index(category, cat_index)

    print(f"✅ Created page: {dst}")
    print(f"🔗 URL: /projects/{category}/{slug}/")


def list_projects():
    """List all projects and categories."""
    ensure_projects_root()
    reg = load_registry()
    
    print("\n📁 Categories:")
    for cat_id, cat_data in reg.get("categories", {}).items():
        icon = cat_data.get("icon", "📄")
        label = cat_data.get("label", cat_id)
        print(f"  {icon} {label} ({cat_id})")
    
    print("\n📄 Projects:")
    for proj in reg.get("projects", []):
        status = proj.get("status", "unknown")
        emoji = "✅" if status == "live" else "📝" if status == "template" else "⏳"
        print(f"  {emoji} {proj['title']} → {proj['path']}")
    
    print()


def main():
    p = argparse.ArgumentParser(
        prog="haslun",
        description="Haslun Projects Scaffolder"
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    # new-template command
    t = sub.add_parser("new-template", help="Create a new template category")
    t.add_argument("category", help="Category name (e.g., 'posters')")
    t.add_argument("--from", dest="from_category", default=None,
                   help="Copy from existing category template")

    # new-page command
    n = sub.add_parser("new-page", help="Create a new page from a template")
    n.add_argument("category", help="Category (e.g., 'cards')")
    n.add_argument("slug", help="Page slug (e.g., 'birthday-jane')")
    n.add_argument("--title", default=None, help="Page title")

    # list command
    sub.add_parser("list", help="List all projects and categories")

    args = p.parse_args()

    if args.cmd == "new-template":
        new_template(args.category, args.from_category)
    elif args.cmd == "new-page":
        new_page(args.category, args.slug, args.title)
    elif args.cmd == "list":
        list_projects()


if __name__ == "__main__":
    main()
