---
name: powerpoint-cinematic
description: Use for native editable PowerPoint (.pptx) presentations with cinematic camera-like Morph transitions, stable object pairing, licensed asset layers, motion continuity and OOXML / visual QA.
---

# Cinematic native PowerPoint agent skill

1. Read `AGENTS.md`, `docs/PPTX-CINEMATIC-MORPH.md`, `docs/ASSET-RIGHTS.md`, `docs/TECH-REUSE.md` and `config/production.json`. Any change to the Blender ident also requires `docs/SHOTLIST.md`.
2. Define the output as **editable PPTX with native Morph**. An MP4 preview, Keynote, static slide export, or HTML animation is **not an acceptable substitute**. Distinguish a native slide transition from animated footage inserted into a slide.
3. Choose a storyboard with one visual anchor that survives between adjacent slides. Reuse *the same media object* or matching `!!` named shapes, changing transforms as a camera move: macro → pullback → pan → inset detail → reveal.
4. Use PptxGenJS to make native slide layout, captions, captions source notes, original graphic shapes and optional locally licensed images. Never promise every bitmap pixel remains separately editable.
5. Add `altText: '!!PERSISTENT_NAME'` to every visual object that must Morph across slides. Apply `scripts/pptx_morph_patch.py` after creating the draft. Check exact `<mc:AlternateContent>` + `<p159:morph option="byObject"/>` + fallback.
6. Rename `p:cNvPr@name` only for unique matching elements per slide; duplicate names or a different underlying image can create unexpected matches. Use the XML validator and visual QA.
7. Research facts from official primary sources. Product / skill reviews must cover installation, usage, benefits, costs and limits, suitable / unsuitable users. No unverified benchmark or fake output screenshots.
8. Keep 16:9, legible Traditional Chinese and technical command typography (mono font). Preserve original source images / SVG / scripts and rights register. Never redistribute a font binary or copyrighted example without recording licenses.
9. Inspect static PNGs, verify slide count and XML, check deliberate off-canvas world images separately from accidental text overflow. **Do not claim successful native Morph playback without Microsoft PowerPoint render / manual review.** LibreOffice static previews are not playback evidence.
10. Source facts and rights; do not merge PR, publish a deck as final, or upload a YouTube video without user approval. Show what was executed locally vs in CI vs not tested.

## Minimal reproduction

```bash
npm install --no-save pptxgenjs
node scripts/build_morph_example.js
python3 scripts/pptx_morph_patch.py morph-draft.pptx morph-native.pptx --duration 1350 --hold 4700
python3 -m unittest discover -s tests -v
```

PowerPoint: open `morph-native.pptx` → Slide Show → confirm camera-like motion for every adjacent slide → desktop/mobile text and audio checks → approve or iterate.

## Known caveat

- Different PowerPoint editions support Morph at different levels; test in a compatible Microsoft app.
- The `mc:AlternateContent` namespace must remain correctly scoped, with a fade fallback.
- Large panorama images intentionally extend beyond slide bounds, and this is not necessarily a layout bug.
- A working deck containing 13 Morph tags has only passed **OOXML structural verification** until actual playback is reviewed.
