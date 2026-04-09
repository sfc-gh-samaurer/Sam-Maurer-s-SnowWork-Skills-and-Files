---
name: pptx-html-to-pptx-conversion
description: Python Playwright conversion pipeline — screenshots HTML slides at 960×540 (2× retina) and assembles them as full-bleed images into a PPTX file. The PPTX contains no editable shapes or text — every slide is a PNG image.
---

# HTML → PPTX Conversion Pipeline

## Overview

Each slide is a standalone `.html` file (960×540 CSS pixels). Playwright renders each file in a headless Chromium browser at 2× device pixel ratio (1920×1080 actual pixels), takes a full-viewport screenshot, and `python-pptx` assembles the PNGs into a 10"×5.625" PPTX slide deck. The result is pixel-perfect, design-first slides that look identical to the HTML originals.

---

## Conversion Rules (NON-NEGOTIABLE)

These rules govern every PPTX produced by this skill. They must never be violated.

1. **Image-only slides.** Every PPTX slide contains exactly one shape: a full-bleed PNG image that fills the entire 10"×5.625" slide area. `prs.slide_layouts[6]` (blank) is always used.

2. **No python-pptx drawing on top of images.** After `slide.shapes.add_picture(...)`, nothing else is added to that slide — no text boxes, no shapes, no titles, no footers, no slide number placeholders.

3. **HTML/CSS is the source of truth.** All design, layout, typography, color, and branding live in the `.html` source files. The PPTX assembly step is purely mechanical — screenshot → image → slide.

4. **Never patch the PPTX to fix design issues.** If something looks wrong, fix the `.html` file and reconvert. Do not try to overlay corrections in python-pptx.

5. **Exact slide dimensions.** PPTX deck must be set to exactly `Inches(10) × Inches(5.625)` — the standard Snowflake 16:9 template size. The PNG is inserted at `left=0, top=0, width=slide_width, height=slide_height`.

6. **File order is deck order.** HTML files are sorted by filename before conversion. Always use zero-padded names (`slide_01_`, `slide_02_`, …) to guarantee correct sort order.

---

## Dependencies

```bash
pip install python-pptx playwright
playwright install chromium
```

---

## Conversion Script

Save as `convert_to_pptx.py` alongside the `slides/` directory:

```python
#!/usr/bin/env python3
"""Convert a directory of HTML slide files into a Snowflake PPTX deck."""

import os
import sys
import glob
from io import BytesIO
from pathlib import Path

from pptx import Presentation
from pptx.util import Inches
from playwright.sync_api import sync_playwright

SLIDE_W_CSS = 960    # CSS pixels — matches 10" at 96dpi
SLIDE_H_CSS = 540    # CSS pixels — matches 5.625" at 96dpi
DEVICE_SCALE = 2     # 2× = 1920×1080 actual PNG pixels (retina quality)


def html_slides_to_pptx(html_files: list, output_path: str) -> None:
    prs = Presentation()
    prs.slide_width  = Inches(10)
    prs.slide_height = Inches(5.625)
    blank = prs.slide_layouts[6]  # blank layout

    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        for html_file in html_files:
            abs_path = Path(html_file).resolve()
            page = browser.new_page(
                viewport={"width": SLIDE_W_CSS, "height": SLIDE_H_CSS},
                device_scale_factor=DEVICE_SCALE,
            )
            page.goto(f"file://{abs_path}")
            page.wait_for_load_state("networkidle")

            img_bytes = page.screenshot(
                type="png",
                clip={"x": 0, "y": 0, "width": SLIDE_W_CSS, "height": SLIDE_H_CSS},
            )
            page.close()

            slide = prs.slides.add_slide(blank)
            slide.shapes.add_picture(
                BytesIO(img_bytes), 0, 0, prs.slide_width, prs.slide_height
            )

        browser.close()

    prs.save(output_path)
    print(f"Deck saved: {output_path}  ({len(html_files)} slides)")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python convert_to_pptx.py OUTPUT.pptx slides/slide_*.html")
        sys.exit(1)

    output  = sys.argv[1]
    pattern = sys.argv[2]

    # Support glob patterns or explicit file lists
    if any(c in pattern for c in ["*", "?"]):
        files = sorted(glob.glob(pattern))
    else:
        files = sys.argv[2:]

    if not files:
        print(f"No HTML files matched: {pattern}")
        sys.exit(1)

    html_slides_to_pptx(files, output)
```

---

## Usage

```bash
# Assumes slides are in a slides/ directory named slide_01_*.html, slide_02_*.html, etc.
python convert_to_pptx.py "MyDeck.pptx" "slides/slide_*.html"

# Or list files explicitly:
python convert_to_pptx.py "MyDeck.pptx" slides/slide_01_cover.html slides/slide_02_agenda.html
```

---

## File Naming Convention

Name slide files with zero-padded numbers so glob sorting matches deck order:

```
slides/
  slide_01_cover.html
  slide_02_agenda.html
  slide_03_chapter_about_us.html
  slide_04_our_team.html
  slide_05_chapter_context.html
  ...
```

---

## Dimension Verification (MANDATORY before batch conversion)

Before running the full conversion, open one HTML slide in a browser and verify it renders at exactly 960×540 with no scrollbars. Every HTML file **must** include:

```css
html, body {
  width: 960px;
  height: 540px;
  overflow: hidden;
  margin: 0;
  padding: 0;
}
.slide {
  width: 960px;
  height: 540px;
  overflow: hidden;
  position: relative;
}
```

If content overflows, Playwright will still clip to 960×540 — but layout will appear cut off. Fix any overflow in the HTML before converting.

---

## Integration in Build Script

For decks with many slides, wrap generation + conversion in a single Python script:

```python
import subprocess, glob, os

def build_deck(slide_dir: str, output_path: str):
    """Generate all HTML slides then convert to PPTX."""
    # 1. [agent writes slide HTML files here]
    
    # 2. Convert
    files = sorted(glob.glob(os.path.join(slide_dir, "slide_*.html")))
    from convert_to_pptx import html_slides_to_pptx
    html_slides_to_pptx(files, output_path)
```
