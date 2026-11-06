# BROKE TRIO — 2026-11-06 cinematic visual benchmark (user-shared Gemini video)

## Intent and rights
The user supplied an approximately **10.03-second, 1280×720, 24 FPS MP4** as a **quality and shot-sequencing reference**. Use it to identify target techniques, timing, and framing. **Do not commit the uploaded binary, reproduce its frames, or assert permission to redistribute**. Retain the original user-supplied reference in the conversation only unless the user separately authorizes import. This note is an independent analysis, not a claim that the V4 Blender scene matches it.

## Visual beats observed in the actual clip

| Approx time (s) | What is actually visible | How to adopt / improve |
|---|---|---|
| 0.0–0.8 | Black background, visible drifting smoke, bright left-side diagonal beam | Build true 3-D scattering and softer graduated edge. Avoid geometry visible before entrance |
| ~0.9–1.8 | Second diagonal light from upper right becomes active; **both lights visibly coexist** | **DO NOT COPY** this: user specified the first lamp must shut off *before* the second turns on, then the second shuts off before statue emerges |
| 1.8–3.2 | Full-body muscular statue emerges from smoke/bright circular splash, dynamic pose and dramatic chiaroscuro | Current V4 bust on pedestal looks small and static. Investigate CC0 full-body sculpture scan from official museums and face camera. Always check license and hash |
| 3.2–4.5 | Camera pushes into detailed classical marble face, a damaged / fractured side is gradually visible | Preserve one subject's anatomical continuity and realistic sculptural material, even through camera movement |
| 4.5–5.7 | Face fractures and dissolves into tendril-like powder; high motion coherence | Make fracture begin on one side, shards have depth, mass and gravity. The reference favors smooth fluid morph rather than verified stone rigid-body mechanics |
| 5.7–7.5 | Flowing dust/smoke vortex transforms into three separate busts | User wants dust **falling** into the next scene and reconstructing 3D busts; add visible physical trajectory and avoid a purely swirling smoke cut |
| 7.5–10.0 | Three classical busts, radial halo, large centered BROKE TRIO typography with tagline | Long legible final ident, preserve 16:9; title and tagline clear within 15%-85% safe area. Avoid overlap and shrinking title in mobile view |

## Comparison to current Blender V4 opening

- **What works:** true CC0 3-D mesh, honest volumetric spotlights, independent animation timing, 16:9 master, working Blender → MP4 + AAC pipeline.
- **What fails artistically:** current bust is much too small, motion understated, fog flat/noisy, no full figure entrance, weak cinematic framing. The user-supplied AI-generated example is a significantly stronger **visual target**.
- **Critical difference:** the reference shows two beams overlapping; the written user requirement overrides the reference on sequencing. A/B acceptance must enforce left ends *strictly before* right begins and sculpture emerges only after second light extinguishes.
- **Creative target:** monochrome marble/ivory-black editorial finish with high contrast and beautifully controlled light, not cartoony 3D, grainy smoke wedge, or slide deck effects.
- **Missing from V4:** genuine close-up → physical fracture → gravity dust → three-figure reform → typography. This is a separate V4-C/D production phase, not silently "done".

## Prioritized technical fixes

1. Establish original-vs-reference visual QA at exact timestamps. Stage a full-sized high-resolution full-body statue, preferably rights-verified CC0 museum scanning. Keep the branded final trio separate from the hero stage.
2. Restore strong cinematic *scale*: subject-height goal >55% of shot height after emergence; do not crop head, arms, or pedestal accidentally. Verify in render and on mobile.
3. Preserve correctly timed independently illuminated smoke volumes; improve softness with unbiased Cycles volume integration, no visible tube/cone silhouettes. Keep black at genuinely black except subtle local haze.
4. Add image-space camera trajectory, time-continuous motion and motion blur; eliminate sudden statue pop-in.
5. For fracture, prefer well-supported Blender Cell Fracture/Rigid Body or Geometry Nodes with bake and actual visible debris movement; explicitly mark approximation when physically simulated behavior is not implemented.
6. Sound: original restrained low drone, separated light cues, one debris impact, a rising transition and a final restrained studio-logo sting; check actual playback and loudness.
7. QA: export real 24fps h264+aac, review every 0.5 seconds and critical transition frames; ensure 1920×1080 master, 16:9 and safe titles. CI PASS alone is not a visual PASS.

## Source and provenance
User-uploaded `gemini_generated_video_29299afa.mp4` examined **privately** in ChatGPT on 2026-11-06. No reference imagery copied to this repository. This document contains only shot-level analysis and actionable requirements.
