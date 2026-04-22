"""Sprite sheet generator for the Texas Energy GIS Map.

Writes 5 semantic icons into `sprite/` at repo root:
  sprite.png + sprite.json       (1x, 48 px tall)
  sprite@2x.png + sprite@2x.json (2x, 96 px tall)

Icons: solar, wind, battery, plant, well.
Rasterized from inline SVG strings via cairosvg. Self-contained; no external assets.

Called from build.py main() before the layer loop. Idempotent (overwrites).
Also copied from ROOT/sprite/ → DIST/sprite/ at build time so Netlify serves them.
"""

import io
import json
from pathlib import Path

import cairosvg
from PIL import Image

ICON_SIZE = 48  # 1x px

# White ring baked into each icon at the border for readability on any basemap.
# Icons are 48x48; content lives within a 44x44 inner box, 2 px ring.

SVGS = {
    'solar': '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48">
  <circle cx="24" cy="24" r="22" fill="#ffffff"/>
  <g stroke="#eab308" stroke-width="3.5" stroke-linecap="round">
    <line x1="24" y1="6"  x2="24" y2="11"/>
    <line x1="24" y1="37" x2="24" y2="42"/>
    <line x1="6"  y1="24" x2="11" y2="24"/>
    <line x1="37" y1="24" x2="42" y2="24"/>
    <line x1="11.3" y1="11.3" x2="14.9" y2="14.9"/>
    <line x1="33.1" y1="33.1" x2="36.7" y2="36.7"/>
    <line x1="11.3" y1="36.7" x2="14.9" y2="33.1"/>
    <line x1="33.1" y1="14.9" x2="36.7" y2="11.3"/>
  </g>
  <circle cx="24" cy="24" r="8.5" fill="#eab308" stroke="#a16207" stroke-width="1"/>
</svg>''',

    'wind': '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48">
  <circle cx="24" cy="24" r="22" fill="#ffffff"/>
  <!-- tower -->
  <path d="M22.5 42 L25.5 42 L24.7 24 L23.3 24 Z" fill="#166534"/>
  <!-- hub -->
  <circle cx="24" cy="24" r="2.4" fill="#166534"/>
  <!-- three blades at 90°, 210°, 330° -->
  <path d="M24 24 L24 8 L26.4 9.5 Z" fill="#166534"/>
  <path d="M24 24 L10.14 32 L9.85 28.9 Z" fill="#166534"/>
  <path d="M24 24 L37.86 32 L38.15 28.9 Z" fill="#166534"/>
</svg>''',

    'battery': '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48">
  <circle cx="24" cy="24" r="22" fill="#ffffff"/>
  <!-- body -->
  <rect x="8" y="17" width="30" height="14" rx="1.5" fill="none" stroke="#991b1b" stroke-width="2.2"/>
  <!-- terminal -->
  <rect x="38" y="21" width="3" height="6" fill="#991b1b"/>
  <!-- charge bars -->
  <rect x="11"   y="20" width="6" height="8" fill="#dc2626"/>
  <rect x="18.5" y="20" width="6" height="8" fill="#dc2626"/>
  <rect x="26"   y="20" width="6" height="8" fill="#dc2626"/>
</svg>''',

    'plant': '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48">
  <circle cx="24" cy="24" r="22" fill="#ffffff"/>
  <!-- factory body + two stacks -->
  <path d="M8 38 L8 24 L16 24 L16 18 L22 24 L28 18 L28 24 L40 24 L40 38 Z"
        fill="#9a3412" stroke="#7c2d12" stroke-width="1"/>
  <!-- tall stack -->
  <rect x="30" y="14" width="5" height="12" fill="#9a3412" stroke="#7c2d12" stroke-width="1"/>
  <!-- windows -->
  <rect x="11" y="30" width="3" height="4" fill="#ffffff"/>
  <rect x="18" y="30" width="3" height="4" fill="#ffffff"/>
  <rect x="25" y="30" width="3" height="4" fill="#ffffff"/>
  <rect x="32" y="30" width="3" height="4" fill="#ffffff"/>
</svg>''',

    'well': '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48">
  <circle cx="24" cy="24" r="22" fill="#ffffff"/>
  <!-- water drop: cubic curves forming teardrop -->
  <path d="M24 8
           C24 8, 12 22, 12 30
           C12 36.6, 17.4 42, 24 42
           C30.6 42, 36 36.6, 36 30
           C36 22, 24 8, 24 8 Z"
        fill="#7c3aed" stroke="#5b21b6" stroke-width="1.2"/>
  <!-- highlight -->
  <ellipse cx="20" cy="28" rx="2.6" ry="4.5" fill="#ffffff" fill-opacity="0.35"/>
</svg>''',
}

ICON_ORDER = ['solar', 'wind', 'battery', 'plant', 'well']


def _svg_to_png_bytes(svg_str, px):
    """Render SVG string to PNG bytes at `px` × `px`."""
    return cairosvg.svg2png(bytestring=svg_str.encode('utf-8'),
                            output_width=px, output_height=px)


def _build_at_scale(out_dir, scale):
    """Write sprite@{scale}x.png + .json. scale=1 → suffix '', scale=2 → '@2x'."""
    px = ICON_SIZE * scale
    suffix = '' if scale == 1 else '@2x'
    sheet = Image.new('RGBA', (px * len(ICON_ORDER), px), (0, 0, 0, 0))
    manifest = {}
    for i, name in enumerate(ICON_ORDER):
        png = _svg_to_png_bytes(SVGS[name], px)
        icon = Image.open(io.BytesIO(png)).convert('RGBA')
        x = i * px
        sheet.paste(icon, (x, 0), icon)
        manifest[name] = {
            'x': x,
            'y': 0,
            'width': px,
            'height': px,
            'pixelRatio': scale,
        }
    sheet.save(out_dir / f'sprite{suffix}.png', optimize=True)
    (out_dir / f'sprite{suffix}.json').write_text(json.dumps(manifest, indent=2) + '\n')


def build_sprite_sheet(out_dir):
    """Generate 1x and 2x sprite assets into `out_dir`. Idempotent."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    _build_at_scale(out_dir, 1)
    _build_at_scale(out_dir, 2)
    return len(ICON_ORDER)


if __name__ == '__main__':
    import sys
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent / 'sprite'
    n = build_sprite_sheet(target)
    print(f'wrote {n} icons × 2 scales to {target}/')
