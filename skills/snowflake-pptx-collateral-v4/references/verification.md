---
name: pptx-verification
description: verify_slide() and verify_deck() functions — automated quality checks for every slide.
---

# PPTX Verification Reference — Post-Slide and Deck-Level Checks

> **This file is a reference companion to SKILL.md.**
> Copy `verify_slide()` and `verify_deck()` into every generated script.
> Call `verify_slide()` after populating each slide, `verify_deck()` before saving.

## 23. Post-Slide Verification (MANDATORY)

After creating each slide, call `verify_slide()` to catch problems BEFORE they
become visual defects. This is the **single most important quality gate**.

```python
def verify_slide(slide, prs, slide_num):
    """Verify a slide for common defects. Call after populating every slide.
    Prints warnings and returns list of issues found.
    """
    issues = []
    slide_w = prs.slide_width / 914400   # 10.00"
    slide_h = prs.slide_height / 914400  # 5.63"
    safe_bottom = 5.10
    safe_left = 0.40
    safe_right = 9.50

    # --- Check 0: Empty title/subtitle ---
    for shape in slide.placeholders:
        idx = shape.placeholder_format.idx
        if idx in (0, 1) and shape.has_text_frame:
            text = shape.text_frame.text.strip()
            if not text:
                label = "TITLE" if idx == 0 else "SUBTITLE"
                issues.append(f"  EMPTY {label}: PH[{idx}] has no text — every content slide needs both title and subtitle")

    for shape in slide.shapes:
        l = (shape.left or 0) / 914400
        t = (shape.top or 0) / 914400
        w = (shape.width or 0) / 914400
        h = (shape.height or 0) / 914400
        bot = t + h
        right = l + w

        # --- Check 1: Below safe zone ---
        if not shape.is_placeholder and bot > safe_bottom and w > 0.5:
            issues.append(f"  OVERFLOW: shape at ({l:.2f}\",{t:.2f}\") bottom={bot:.2f}\" exceeds safe zone {safe_bottom}\"")

        # --- Check 1b: Above safe zone (custom shapes overlapping title/subtitle) ---
        if not shape.is_placeholder and t < 1.22 and w > 0.3 and h > 0.1:
            issues.append(f"  HEADER OVERLAP: shape at ({l:.2f}\",{t:.2f}\") starts above 1.22\" safe start — overlaps title/subtitle area")

        # --- Check 1c: Shape past right or bottom safe zone ---
        if not shape.is_placeholder and w > 0.3:
            if l + w > 9.55:
                issues.append(f"  RIGHT OVERFLOW: shape at ({l:.2f}\",{t:.2f}\") right edge={l+w:.2f}\" > 9.50\" — will bleed into slide margin")
            if t + h > 5.15:
                issues.append(f"  BOTTOM OVERFLOW: shape at ({l:.2f}\",{t:.2f}\") bottom={t+h:.2f}\" > 5.10\" — will bleed into slide footer")

        # --- Check 2: Table row count ---
        if shape.has_table:
            tbl = shape.table
            n_rows = len(tbl.rows)
            max_height = safe_bottom - t
            row_h = h / n_rows if n_rows > 0 else 0.40
            max_rows = int(max_height / row_h)
            if bot > safe_bottom:
                issues.append(f"  TABLE OVERFLOW: {n_rows} rows, bottom={bot:.2f}\". Max {max_rows} rows for this position.")

        # --- Check 3: Custom shape text density ---
        if not shape.is_placeholder and shape.has_text_frame and not shape.has_table:
            tf = shape.text_frame
            total_chars = sum(len(p.text) for p in tf.paragraphs)
            if total_chars > 0 and w > 0.5 and h > 0.40:  # skip tiny textboxes (bullets)
                max_chars = int(w * 9) * max(int(h / 0.18), 1)
                if total_chars > max_chars * 1.2:
                    issues.append(f"  TEXT DENSE: shape ({w:.1f}\"x{h:.1f}\") has {total_chars} chars, max ~{max_chars}")

        # --- Check 3b2: Font too large for circles/ovals ---
        if not shape.is_placeholder and shape.has_text_frame:
            st = shape.shape_type
            is_oval = (st and st == 9)  # MSO_SHAPE.OVAL
            is_small_shape = w < 2.0 and h < 2.0
            if is_oval or is_small_shape:
                max_fs = 0
                for para in shape.text_frame.paragraphs:
                    for run in para.runs:
                        if run.font.size:
                            fs = run.font.size.pt
                            if fs > max_fs:
                                max_fs = fs
                    # Also check paragraph-level font
                    if para.font.size:
                        fs = para.font.size.pt
                        if fs > max_fs:
                            max_fs = fs
                if is_oval:
                    diameter = min(w, h)
                    # Minimum circle size check
                    if diameter < 0.54:
                        issues.append(f"  CIRCLE TOO SMALL: {diameter:.2f}\" diameter (min 0.55\"). Text won't fit. Increase to ≥0.55\".")
                if max_fs > 0 and is_oval:
                    # Circle font limits from Section 12.1
                    diameter = min(w, h)
                    if diameter <= 0.60 and max_fs > 14:
                        issues.append(f"  CIRCLE FONT TOO LARGE: {max_fs:.0f}pt in {diameter:.2f}\" circle (max 14pt). Use smaller font or larger circle.")
                    elif diameter <= 0.80 and max_fs > 14:
                        issues.append(f"  CIRCLE FONT TOO LARGE: {max_fs:.0f}pt in {diameter:.2f}\" circle (max 14pt). Use smaller font or larger circle.")
                    elif diameter <= 1.00 and max_fs > 10:
                        issues.append(f"  CIRCLE FONT TOO LARGE: {max_fs:.0f}pt in {diameter:.2f}\" circle (max 10pt). Use smaller font or larger circle.")
                    elif diameter <= 1.50 and max_fs > 11:
                        issues.append(f"  CIRCLE FONT TOO LARGE: {max_fs:.0f}pt in {diameter:.2f}\" circle (max 11pt). Use smaller font or larger circle.")
                # Check auto_size is set on shapes (not textboxes)
                if hasattr(shape, 'shape_type') and shape.shape_type and shape.shape_type != 17:  # 17 = TEXTBOX
                    auto = shape.text_frame.auto_size
                    if auto is None or auto == 0:  # MSO_AUTO_SIZE.NONE = 0
                        has_text = any(p.text.strip() for p in shape.text_frame.paragraphs)
                        if has_text:
                            issues.append(f"  NO AUTO-FIT: shape \"{shape.name}\" ({w:.2f}\"x{h:.2f}\") has text but no TEXT_TO_FIT_SHAPE — text may overflow")

    # --- Check 3a2: Multi-category content dumped in single placeholder ---
    for shape in slide.shapes:
        if not shape.is_placeholder or not shape.has_text_frame:
            continue
        t = (shape.top or 0) / 914400
        if t <= 1.20:  # skip title/subtitle area
            continue
        tf = shape.text_frame
        paras = tf.paragraphs
        # Count bold headings (short bold text followed by non-bold body)
        bold_heading_count = 0
        for pi, para in enumerate(paras):
            txt = para.text.strip()
            if not txt or len(txt) > 50:
                continue
            # Check if paragraph is bold (run-level or paragraph-level)
            is_bold = False
            if para.runs:
                is_bold = any(r.font.bold for r in para.runs if r.font.bold is True)
            if is_bold and pi + 1 < len(paras):
                next_txt = paras[pi + 1].text.strip()
                if next_txt and len(next_txt) > len(txt):
                    bold_heading_count += 1
        if bold_heading_count >= 3:
            idx = shape.placeholder_format.idx
            issues.append(f"  WALL OF TEXT: PH[{idx}] has {bold_heading_count} bold-header sections in one placeholder. Split into separate columns (Layout 7) or callout boxes via add_shape_text(). See slide-patterns.md Section 12.8.")

    # --- Check 3a2b: Dense single-placeholder detection (≥10 non-empty lines + no visuals) ---
    has_visual = any(
        s.shape_type in (MSO_SHAPE_TYPE.AUTO_SHAPE, MSO_SHAPE_TYPE.FREEFORM, MSO_SHAPE_TYPE.TABLE)
        for s in slide.shapes if not s.is_placeholder
    )
    if not has_visual:
        for shape in slide.shapes:
            if not shape.is_placeholder or not shape.has_text_frame:
                continue
            t = (shape.top or 0) / 914400
            if t <= 1.20:
                continue
            non_empty = [p for p in shape.text_frame.paragraphs if p.text.strip()]
            if len(non_empty) >= 10:
                idx = shape.placeholder_format.idx
                issues.append(f"  DENSE PLACEHOLDER: PH[{idx}] has {len(non_empty)} lines with NO visual elements on slide. Use Layout 7 (3-col), add_shape_text() boxes, or a table instead of a bullet wall.")

    # --- Check 3a3: Auto size None on body placeholders ---
    for shape in slide.shapes:
        if not shape.is_placeholder or not shape.has_text_frame:
            continue
        t = (shape.top or 0) / 914400
        if t <= 1.20:  # skip title/subtitle
            continue
        tf = shape.text_frame
        total_chars = sum(len(p.text) for p in tf.paragraphs)
        if total_chars > 100:  # only flag substantial content
            auto = tf.auto_size
            if auto is None or auto == 0:
                idx = shape.placeholder_format.idx
                issues.append(f"  NO AUTO-FIT PH: PH[{idx}] has {total_chars} chars but Auto size is None — text may overflow. Set auto_size = TEXT_TO_FIT_SHAPE.")

    # --- Check 3b: Colour violations in custom shapes ---
    # FULL palette: theme colours + extended utility colours + structural greys
    PALETTE = {
        (0x26,0x26,0x26), (0xFF,0xFF,0xFF), (0x11,0x56,0x7F), (0x29,0xB5,0xE8),
        (0x71,0xD3,0xDC), (0xFF,0x9F,0x36), (0x7D,0x44,0xCF), (0xD4,0x5B,0x90),
        (0x5B,0x5B,0x5B), (0x71,0x71,0x71), (0x92,0x92,0x92), (0xBF,0xBF,0xBF),
        (0xF5,0xF5,0xF5), (0xC8,0xC8,0xC8), (0xA2,0x00,0x00), (0xEF,0xEF,0xEF),
        (0xDD,0xDD,0xDD),  # GRID_LINE — cell borders, grid lines
        (0xCC,0xCC,0xCC),  # CONN_LINE — connector lines between shapes
        (0x00,0x00,0x00),  # pure black (rare but valid for lines)
    }
    SFBLUE_RGB = (0x29,0xB5,0xE8)
    ACCENT_FILL_ONLY = {(0x71,0xD3,0xDC), (0xFF,0x9F,0x36), (0x7D,0x44,0xCF), (0xD4,0x5B,0x90)}
    for shape in slide.shapes:
        if shape.is_placeholder or not shape.has_text_frame:
            continue
        for para in shape.text_frame.paragraphs:
            # Colour can be on individual runs OR on the paragraph font.
            # Check both: run-level first (most skill patterns use this),
            # then paragraph-level for text set via p.font.color.rgb.
            sources = []
            for run in para.runs:
                c = run.font.color
                try:
                    if c and c.type is not None:
                        sources.append((c.rgb, run.font.size, run.text))
                except AttributeError:
                    pass
            # Also check paragraph-level font colour
            try:
                pc = para.font.color
                if pc and pc.type is not None:
                    sz = para.font.size or (para.runs[0].font.size if para.runs else None)
                    sources.append((pc.rgb, sz, para.text))
            except (AttributeError, IndexError):
                pass

            for rgb, sz, txt in sources:
                if rgb is None:
                    continue
                rgb_tuple = (rgb[0], rgb[1], rgb[2])
                sz_pt = sz / 12700 if sz else 0
                # Allow ±10 tolerance for near-palette colors (e.g. 1A,1A,1A ≈ black)
                in_palette = rgb_tuple in PALETTE
                if not in_palette:
                    in_palette = any(all(abs(a-b) <= 10 for a, b in zip(rgb_tuple, pc)) for pc in PALETTE)
                if not in_palette:
                    issues.append(f"  NON-PALETTE COLOR: #{rgb} on \"{txt[:20]}\"")
                if rgb_tuple in ACCENT_FILL_ONLY:
                    issues.append(f"  ACCENT AS TEXT: #{rgb} on \"{txt[:20]}\" — only for fills")
                if rgb_tuple == SFBLUE_RGB and sz_pt > 0 and sz_pt < 28:
                    issues.append(f"  SF_BLUE UNDERSIZED: {sz_pt:.0f}pt on \"{txt[:20]}\" (min 28pt)")

    # --- Check 3c: Fill colour violations (catch off-brand shape fills) ---
    FILL_PALETTE = PALETTE  # same palette applies to fills and text
    for shape in slide.shapes:
        if shape.is_placeholder:
            continue
        try:
            fill = shape.fill
            if fill and fill.type is not None and fill.type == 1:  # solid fill
                fc = fill.fore_color
                if fc and fc.type is not None and fc.rgb:
                    rgb = fc.rgb
                    rgb_tuple = (rgb[0], rgb[1], rgb[2])
                    in_palette = rgb_tuple in FILL_PALETTE
                    if not in_palette:
                        in_palette = any(all(abs(a-b) <= 10 for a, b in zip(rgb_tuple, pc)) for pc in FILL_PALETTE)
                    if not in_palette:
                        issues.append(f"  NON-PALETTE FILL: #{rgb} on shape \"{shape.name}\" — use only Snowflake palette colours for fills")
        except (AttributeError, TypeError):
            pass

    # --- Check 3d: Font name violations (MUST be Arial everywhere) ---
    for shape in slide.shapes:
        if not shape.has_text_frame:
            continue
        for para in shape.text_frame.paragraphs:
            for run in para.runs:
                if run.font.name and run.font.name != "Arial":
                    issues.append(f"  WRONG FONT: \"{run.font.name}\" on \"{run.text[:25]}\" — MUST be Arial")
            # Also check paragraph-level font
            try:
                if para.font.name and para.font.name != "Arial":
                    issues.append(f"  WRONG FONT: \"{para.font.name}\" on \"{para.text[:25]}\" — MUST be Arial")
            except AttributeError:
                pass

    # --- Check 3e: Font size range (catch absurdly small or large text) ---
    for shape in slide.shapes:
        if not shape.has_text_frame:
            continue
        for para in shape.text_frame.paragraphs:
            if not para.text.strip():
                continue
            for run in para.runs:
                if run.font.size:
                    sz = run.font.size.pt
                    if sz < 7:
                        issues.append(f"  FONT TOO SMALL: {sz:.0f}pt on \"{run.text[:25]}\" — minimum 7pt for readability")
                    elif sz > 32 and not shape.is_placeholder:
                        issues.append(f"  FONT TOO LARGE: {sz:.0f}pt on \"{run.text[:25]}\" — maximum 32pt for custom shapes")
            try:
                if para.font.size:
                    sz = para.font.size.pt
                    if sz < 7:
                        issues.append(f"  FONT TOO SMALL: {sz:.0f}pt on \"{para.text[:25]}\" — minimum 7pt for readability")
                    elif sz > 32 and not shape.is_placeholder:
                        issues.append(f"  FONT TOO LARGE: {sz:.0f}pt on \"{para.text[:25]}\" — maximum 32pt for custom shapes")
            except AttributeError:
                pass

    # --- Check 3f: Content quality (flag generic placeholder text) ---
    GENERIC_PATTERNS = [
        "item 1", "item 2", "item 3", "lorem ipsum", "placeholder",
        "text here", "enter text", "your text", "todo", "tbd",
        "description here", "add content", "insert text", "sample text",
    ]
    for shape in slide.shapes:
        if not shape.has_text_frame:
            continue
        for para in shape.text_frame.paragraphs:
            txt = para.text.strip().lower()
            if not txt or len(txt) < 3:
                continue
            for gp in GENERIC_PATTERNS:
                if gp in txt:
                    issues.append(f"  GENERIC TEXT: \"{para.text.strip()[:40]}\" — replace with specific, meaningful content")
                    break
            # Flag single-word body bullets (too terse for consulting quality)
            if not shape.is_placeholder:
                continue
            t = (shape.top or 0) / 914400
            if t > 1.20 and len(txt.split()) == 1 and len(txt) > 2 and para.level >= 0:
                issues.append(f"  TERSE BULLET: \"{para.text.strip()}\" — single-word bullets lack substance. Add context (15+ chars)")

    # --- Check 3f2: Fill→Text CONTRAST violations (TEAL/ORANGE + WHITE = unreadable) ---
    CONTRAST_BAD = {
        # (fill_rgb_tuple, text_rgb_tuple): description
    }
    TEAL_RGB  = (0x71, 0xD3, 0xDC)
    ORANGE_RGB = (0xFF, 0x9F, 0x36)
    WHITE_RGB  = (0xFF, 0xFF, 0xFF)
    for shape in slide.shapes:
        if shape.is_placeholder or not shape.has_text_frame:
            continue
        try:
            fill = shape.fill
            if fill and fill.type is not None and fill.type == 1:
                fc = fill.fore_color
                if fc and fc.type is not None and fc.rgb:
                    fill_t = (fc.rgb[0], fc.rgb[1], fc.rgb[2])
                    for para in shape.text_frame.paragraphs:
                        for run in para.runs:
                            try:
                                tc = run.font.color
                                if tc and tc.type is not None and tc.rgb:
                                    text_t = (tc.rgb[0], tc.rgb[1], tc.rgb[2])
                                    if fill_t == TEAL_RGB and text_t == WHITE_RGB:
                                        issues.append(f"  BAD CONTRAST: TEAL fill + WHITE text on \"{para.text[:30]}\" — use DK1 (#262626) instead of WHITE")
                                    if fill_t == ORANGE_RGB and text_t == WHITE_RGB:
                                        issues.append(f"  BAD CONTRAST: ORANGE fill + WHITE text on \"{para.text[:30]}\" — use DK1 (#262626) instead of WHITE")
                            except AttributeError:
                                pass
        except (AttributeError, TypeError):
            pass

    # --- Check 3f3: Shape OUTLINE check (custom shapes should have no visible outline) ---
    for shape in slide.shapes:
        if shape.is_placeholder:
            continue
        if not shape.has_text_frame:
            continue
        try:
            line = shape.line
            if line.fill.type is not None and line.fill.type == 1:
                txt = shape.text_frame.text[:30] if shape.text_frame.text else shape.name
                issues.append(f"  VISIBLE OUTLINE: shape \"{txt}\" has a stroke — use shape.line.fill.background() or add_shape_text()")
        except (AttributeError, TypeError):
            pass

    # --- Check 3g: Multi-run text concatenation (runs without spaces/newlines) ---
    for shape in slide.shapes:
        if shape.is_placeholder or not shape.has_text_frame:
            continue
        for para in shape.text_frame.paragraphs:
            if len(para.runs) > 1:
                combined = "".join(r.text for r in para.runs)
                spaced = " ".join(r.text for r in para.runs)
                # If runs concat without spaces and each run is a word, flag it
                if combined != spaced and not any(c in combined for c in [' ', '\n']):
                    issues.append(f"  MERGED RUNS: \"{combined}\" — multiple runs in one paragraph with no spaces. Use \\n in a single string instead of separate runs")

    # --- Check 4: Shape-shape overlap (smart — ignores vertical stacking) ---
    custom = [(s, (s.left or 0)/914400, (s.top or 0)/914400,
               (s.width or 0)/914400, (s.height or 0)/914400)
              for s in slide.shapes if not s.is_placeholder and (s.width or 0)/914400 > 0.5]
    reported = set()
    for i, (s1, l1, t1, w1, h1) in enumerate(custom):
        for j, (s2, l2, t2, w2, h2) in enumerate(custom):
            if j <= i or (i, j) in reported:
                continue
            r1, b1, r2, b2 = l1+w1, t1+h1, l2+w2, t2+h2
            if l1 < r2 and r1 > l2 and t1 < b2 and b1 > t2:
                ov_w = min(r1, r2) - max(l1, l2)
                ov_h = min(b1, b2) - max(t1, t2)
                # Skip vertically stacked shapes in the same column
                # (label below a circle, description below a title, etc.)
                centres_same_col = abs((l1+w1/2) - (l2+w2/2)) < max(w1, w2) * 0.6
                # Only flag substantial side-by-side overlaps
                if ov_w > 0.25 and ov_h > 0.25 and not centres_same_col:
                    issues.append(f"  OVERLAP: shapes at ({l1:.1f}\",{t1:.1f}\") and ({l2:.1f}\",{t2:.1f}\") overlap {ov_w:.1f}\"x{ov_h:.1f}\"")
                    reported.add((i, j))

    # --- Check 5: Placeholder heading/body hierarchy ---
    for shape in slide.shapes:
        if shape.is_placeholder and shape.has_text_frame:
            tf = shape.text_frame
            idx = shape.placeholder_format.idx
            t = (shape.top or 0) / 914400
            paras = tf.paragraphs

            # Check 5a: Title length (prevent expansion into subtitle)
            if t < 0.50:  # Title placeholder
                title_text = " ".join(p.text for p in paras)
                if len(title_text) > 50:
                    issues.append(f"  TITLE TOO LONG: {len(title_text)} chars (max 50) — will overflow into subtitle. \"{title_text[:40]}...\"")

            # Check 5b: Subtitle length (65 chars = 1 line at 14pt in 9.1")
            if 0.60 < t < 1.20:  # Subtitle placeholder
                sub_text = " ".join(p.text for p in paras)
                if len(sub_text) > 65:
                    issues.append(f"  SUBTITLE TOO LONG: {len(sub_text)} chars (max 65) — will wrap to 2 lines. Trim to one sentence.")

            for pi, para in enumerate(paras):
                txt = para.text.strip()
                if not txt:
                    continue
                # Detect heading-like text (short) followed by longer body text
                if (len(txt) < 40 and pi + 1 < len(paras)):
                    next_txt = paras[pi + 1].text.strip()
                    if len(next_txt) > 40 and para.level == paras[pi + 1].level:
                        # Check if heading has bold
                        has_bold = any(r.font.bold for r in para.runs if r.font.bold)
                        if not has_bold:
                            issues.append(f"  FLAT TEXT: PH heading \"{txt[:30]}\" not bold/differentiated from body")

            # Check 5b2: Empty paragraph spacers (banned — use set_ph_sections instead)
            if t > 1.20:
                empty_count = sum(1 for p in paras if not p.text.strip())
                if empty_count > 0:
                    issues.append(f"  EMPTY SPACERS: PH{idx} has {empty_count} empty paragraph(s) used as spacers. Use set_ph_sections() for heading/body hierarchy instead of blank lines.")

            # Check 5b3: All-L0 flat text in body (no hierarchy)
            if t > 1.20:
                content_paras = [p for p in paras if p.text.strip()]
                if len(content_paras) > 3:
                    levels = set(p.level for p in content_paras)
                    if levels == {0}:
                        issues.append(f"  FLAT HIERARCHY: PH{idx} has {len(content_paras)} paragraphs all at Level 0. Use set_ph_sections() (L0 headings + L1 body) for proper visual hierarchy.")

            # Check 5c: Body placeholder content density (too much text for height)
            if t > 1.20:  # Body content placeholder
                total_chars = sum(len(p.text) for p in paras)
                w = (shape.width or 0) / 914400
                if total_chars > 0 and w > 2.0:
                    # At 10pt, ~9 chars/inch width, ~5.5 lines/inch height
                    max_lines = int(h / 0.18)
                    max_chars = int(w * 9) * max_lines
                    if total_chars > max_chars:
                        issues.append(f"  CONTENT DENSE: PH at ({l:.1f}\",{t:.1f}\") has {total_chars} chars, max ~{max_chars} for {w:.1f}\"x{h:.1f}\". Split across slides.")

            # Check 5d: Right edge past safe zone
            if l + w > 9.55:
                issues.append(f"  RIGHT OVERFLOW: PH at ({l:.2f}\",{t:.2f}\") right edge={l+w:.2f}\" > 9.50\"")

    # --- Check 6: Concatenated text detection (missing spaces/newlines) ---
    import re
    for shape in slide.shapes:
        if not shape.has_text_frame:
            continue
        for para in shape.text_frame.paragraphs:
            txt = para.text.strip()
            if len(txt) < 6:
                continue
            # Find runs of 10+ lowercase-uppercase transitions with no space
            # e.g. "THECHALLENGE", "DocumentAI", "HorizonGovernance"
            merged = re.findall(r'[a-z][A-Z]', txt)
            if len(merged) >= 1 and ' ' not in txt and '\n' not in txt and len(txt) > 8:
                issues.append(f"  MERGED TEXT: \"{txt[:40]}\" — missing space or \\n between words. Use \"word1\\nword2\" or \"word1 word2\".")
            # Also catch ALL-CAPS merged words: "THECHALLENGE" = "THE" + "CHALLENGE"
            # Skip single valid words (e.g. "APPLICATIONS", "ARCHITECTURE") — only flag
            # strings with obvious word boundaries (3+ consonants in a row mid-word is rare
            # in English but common in merged words like "THECHALLENGE" → "ECH")
            if txt.isupper() and len(txt) > 12 and ' ' not in txt:
                # Heuristic: real single words rarely have 4+ consonants in sequence
                import re as _re
                consonant_clusters = _re.findall(r'[^AEIOU]{4,}', txt)
                if consonant_clusters:
                    issues.append(f"  MERGED CAPS: \"{txt[:40]}\" — appears to be concatenated ALL-CAPS words missing spaces or \\n.")

    if issues:
        print(f"⚠ SLIDE {slide_num} issues:")
        for iss in issues:
            print(iss)
    else:
        print(f"✓ SLIDE {slide_num} OK")
    return issues
```

### How to Use

Call `verify_slide()` immediately after populating each slide:

```python
# After creating and populating a slide:
slide = prs.slides.add_slide(prs.slide_layouts[5])
set_ph(slide, 0, "SLIDE TITLE")
set_ph_sections(slide, 1, [("Heading", ["Body text"])])
verify_slide(slide, prs, slide_num=1)  # ← ALWAYS call this
```

### Deck-Level Verification

After all slides are created, call `verify_deck()` to check deck-wide rules that individual slide checks can't enforce:

```python
def verify_deck(prs):
    """Verify deck-level rules: visual variety, consecutive text slides, feature tags.
    Call once after all slides are generated, before saving.
    """
    issues = []
    content_slides = 0
    visual_pattern_slides = 0
    consecutive_text = 0
    max_consecutive_text = 0

    for si, slide in enumerate(prs.slides):
        sn = si + 1
        is_cover = False; is_divider = False; is_thankyou = False; is_content = False
        has_custom_shapes = False

        for shape in slide.shapes:
            if shape.is_placeholder:
                t = (shape.top or 0) / 914400
                # Detect covers (layout with big title > 1.00" top)
                if t > 1.20 and hasattr(shape, 'placeholder_format'):
                    idx = shape.placeholder_format.idx
                    if idx == 3:  # Cover title PH
                        is_cover = True
            else:
                w = (shape.width or 0) / 914400
                h = (shape.height or 0) / 914400
                if w > 0.5 and h > 0.3:
                    has_custom_shapes = True

        # Detect chapter dividers (DK2 background, no custom shapes)
        layout_idx = None
        try:
            layout_name = slide.slide_layout.name
            if "Quote" in layout_name and "Violet" in layout_name and "_1_1" in layout_name and not has_custom_shapes:
                is_divider = True
            if "Thank" in layout_name:
                is_thankyou = True
        except:
            pass

        if not is_cover and not is_divider and not is_thankyou:
            content_slides += 1
            if has_custom_shapes:
                visual_pattern_slides += 1
                consecutive_text = 0
            else:
                consecutive_text += 1
                max_consecutive_text = max(max_consecutive_text, consecutive_text)

    # Rule 28: Visual variety — HARD ENFORCEMENT
    # ≥40% of content slides must have visual elements (shapes, diagrams, tables)
    if content_slides > 0:
        visual_ratio = visual_pattern_slides / content_slides
        required_pct = 0.40
        required_count = max(1, int(content_slides * required_pct))
        if visual_pattern_slides < required_count:
            issues.append(f"  LOW VISUAL DENSITY: Only {visual_pattern_slides}/{content_slides} content slides ({visual_ratio:.0%}) have visual elements — need ≥{required_count} ({required_pct:.0%}). Add diagrams (chevrons, hub-spoke, stat callouts, timelines) from patterns-enterprise.md. Bullet-only decks are REJECTED.")
    if max_consecutive_text > 2:
        issues.append(f"  CONSECUTIVE TEXT: {max_consecutive_text} bullet-only slides in a row (max 2). Insert a visual pattern slide (diagram, table, stat callout) to break monotony.")

    # Also count tables as visual elements (they were counted above via has_custom_shapes)
    # but recount to be thorough — tables also break monotony
    table_slides = 0
    for slide in prs.slides:
        for shape in slide.shapes:
            if shape.has_table:
                table_slides += 1
                break

    # Deck size check
    total = len(prs.slides)
    if total < 3:
        issues.append(f"  TOO SHORT: Only {total} slides — minimum for a professional deck is 5-6")
    if total > 30:
        issues.append(f"  TOO LONG: {total} slides — consider splitting into multiple decks or cutting content")

    # --- Deck-level brand consistency: aggregate font/colour violations ---
    non_arial_count = 0
    off_palette_count = 0
    generic_text_count = 0
    GENERIC_PATTERNS = [
        "item 1", "item 2", "item 3", "lorem ipsum", "placeholder",
        "text here", "enter text", "your text", "todo", "tbd",
        "description here", "add content", "insert text", "sample text",
    ]
    PALETTE = {
        (0x26,0x26,0x26), (0xFF,0xFF,0xFF), (0x11,0x56,0x7F), (0x29,0xB5,0xE8),
        (0x71,0xD3,0xDC), (0xFF,0x9F,0x36), (0x7D,0x44,0xCF), (0xD4,0x5B,0x90),
        (0x5B,0x5B,0x5B), (0x71,0x71,0x71), (0x92,0x92,0x92), (0xBF,0xBF,0xBF),
        (0xF5,0xF5,0xF5), (0xC8,0xC8,0xC8), (0xA2,0x00,0x00), (0xEF,0xEF,0xEF),
        (0xDD,0xDD,0xDD), (0xCC,0xCC,0xCC), (0x00,0x00,0x00),
    }
    for slide in prs.slides:
        for shape in slide.shapes:
            if not shape.has_text_frame:
                continue
            for para in shape.text_frame.paragraphs:
                txt = para.text.strip().lower()
                if txt:
                    for gp in GENERIC_PATTERNS:
                        if gp in txt:
                            generic_text_count += 1
                            break
                for run in para.runs:
                    if run.font.name and run.font.name != "Arial":
                        non_arial_count += 1
                    try:
                        c = run.font.color
                        if c and c.type is not None and c.rgb:
                            rgb = c.rgb
                            t = (rgb[0], rgb[1], rgb[2])
                            in_p = t in PALETTE or any(all(abs(a-b) <= 10 for a, b in zip(t, pc)) for pc in PALETTE)
                            if not in_p:
                                off_palette_count += 1
                    except (AttributeError, TypeError):
                        pass
    if non_arial_count > 0:
        issues.append(f"  BRAND: {non_arial_count} text run(s) using non-Arial font — MUST be Arial everywhere")
    if off_palette_count > 0:
        issues.append(f"  BRAND: {off_palette_count} text run(s) using off-palette colours — only Snowflake palette allowed")
    if generic_text_count > 0:
        issues.append(f"  CONTENT: {generic_text_count} instance(s) of generic placeholder text — replace with specific content")

    # --- Word choice quality heuristic ---
    weak_words = 0
    WEAK_STARTS = ["we will", "we can", "things", "stuff", "various", "some of the"]
    for slide in prs.slides:
        for shape in slide.shapes:
            if not shape.has_text_frame:
                continue
            for para in shape.text_frame.paragraphs:
                txt = para.text.strip().lower()
                if len(txt) < 10:
                    continue
                for ws in WEAK_STARTS:
                    if txt.startswith(ws):
                        weak_words += 1
                        break
    if weak_words > 3:
        issues.append(f"  WORD CHOICE: {weak_words} bullet(s) start with weak/vague phrasing ('We will...', 'Various...', 'Things...') — use direct, outcome-focused language")

    if issues:
        print(f"⚠ DECK-LEVEL issues ({len(issues)}):")
        for iss in issues:
            print(iss)
    else:
        print(f"✓ DECK OK: {len(prs.slides)} slides, {visual_pattern_slides}/{content_slides} visual patterns, max {max_consecutive_text} consecutive text")
    return issues
```

**Call once at the end, before `prs.save()`:**

```python
# After all slides created and individually verified:
verify_deck(prs)
prs.save(output_path)
```

### What It Catches

| Check | What It Detects | How to Fix |
|-------|----------------|------------|
| OVERFLOW | Shape/table extends below 5.10" | Reduce rows, split to next slide, or shrink font |
| TABLE OVERFLOW | Table rows exceed available height | Paginate: max 8 data rows per slide |
| TEXT DENSE | Too much text for shape dimensions | Enlarge shape, reduce text, or split content |
| OVERLAP | Two custom shapes overlap each other | Add 0.15"+ gap, recalculate positions |
| FLAT TEXT | Heading paragraph not differentiated from body | Use `set_ph_sections()` or manually bold+DK2 the heading |
| EMPTY SPACERS | Empty paragraphs used as spacing hacks in body | Remove blank lines; use `set_ph_sections()` for heading/body gaps |
| FLAT HIERARCHY | 4+ body paragraphs all at Level 0, no differentiation | Use `set_ph_sections()` (L0 heading + L1 body) or `set_ph_bold_keywords()` |
| HEADER OVERLAP | Custom shape starts above 1.22" | Move shape down to ≥ 1.30" |
| RIGHT OVERFLOW | Shape right edge > 9.50" | Reduce width or shift left |
| BOTTOM OVERFLOW | Shape bottom edge > 5.10" | Reduce height, move up, or split to next slide |
| TITLE TOO LONG | Title > 50 chars | Shorten to a punchy headline |
| SUBTITLE TOO LONG | Subtitle > 65 chars (wraps to 2 lines) | Trim to one sentence ≤ 65 chars |
| CONTENT DENSE | Body PH text exceeds capacity | Split content across slides or reduce text |
| NON-PALETTE COLOR | Text RGB value not in Section 4 palette | Replace with nearest palette colour |
| NON-PALETTE FILL | Shape fill colour not in Section 4 palette | Replace with nearest palette colour for fills |
| ACCENT AS TEXT | TEAL/ORANGE/VIOLET/PINK used as text colour | Use DK1 or DK2 for text; accent colours for fills only |
| SF_BLUE UNDERSIZED | SF_BLUE text below 28pt | Use DK2 instead, or increase font to 28pt+ |
| WRONG FONT | Non-Arial font detected on any text | Change to `p.font.name = "Arial"` — mandatory across all shapes |
| FONT TOO SMALL | Font size below 7pt | Increase to at least 7pt for readability |
| FONT TOO LARGE | Font size above 32pt on custom shapes | Reduce to 32pt max (titles in placeholders can be larger) |
| GENERIC TEXT | Placeholder text like "Item 1", "Lorem ipsum", "TBD" | Replace with specific, meaningful, consulting-grade content |
| TERSE BULLET | Single-word bullet in a body placeholder | Add context — bullets should be 15+ characters with substance |
| CIRCLE FONT TOO LARGE | Font exceeds max for circle diameter (Section 12.1) | Reduce font size or increase circle diameter |
| NO AUTO-FIT | Custom shape has text but no TEXT_TO_FIT_SHAPE | Add `tf.auto_size = MSO_AUTO_SIZE.TEXT_TO_FIT_SHAPE` (Rule 39) |
| MERGED TEXT | camelCase-like text without spaces (e.g. "DocumentAI") | Add space or `\n` between words (Section 12.6) |
| MERGED CAPS | ALL-CAPS string 10+ chars with no spaces (e.g. "THECHALLENGE") | Add space or `\n` between words (Section 12.6) |
| MERGED RUNS | Multiple runs in one paragraph concat without spaces (e.g. "EHRSYSTEMS") | Use `\n` in single string via `add_shape_text()` (Section 12.7) |
| WALL OF TEXT | 3+ bold-header sections in one body placeholder | Split into Layout 7 (3-col), callout boxes, or multi-column sections. See `slide-patterns.md` Section 12.8. |
| NO AUTO-FIT PH | Body placeholder with 100+ chars and Auto size None | Set `auto_size = MSO_AUTO_SIZE.TEXT_TO_FIT_SHAPE` on the text frame |
| EMPTY TITLE | PH[0] has no text | Every content slide needs a title via `set_ph(slide, 0, ...)` |
| EMPTY SUBTITLE | PH[1] has no text | Every content slide needs a subtitle via `set_ph(slide, 1, ...)` |
| TIGHT FIT | Long text crammed into narrow shape (<1.5" wide) | Move description to separate text box below shape, or shorten text |
| LOW VISUAL DENSITY | Less than 40% of content slides have visual elements (shapes/diagrams/tables) | Add chevrons, hub-spoke, stat callouts, timelines from `patterns-enterprise.md`. Bullet-only decks REJECTED. |
| CONSECUTIVE TEXT | More than 2 bullet-only slides in a row | Insert a visual pattern slide (diagram, table, stat callout) between text slides |

---

