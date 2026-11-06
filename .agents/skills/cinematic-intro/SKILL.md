---
name: cinematic-intro
description: Use when editing or rendering the original BROKE TRIO Blender intro, including fog, sequential lighting, camera, fracture and video delivery quality gates.
---

# BROKE TRIO 3-D cinematic scene skill

1. Read `AGENTS.md`, `config/production.json`, `docs/SHOTLIST.md` and `docs/ASSET-RIGHTS.md`. Do not assume third-party reference art is reusable.
2. Identify which shot is being changed. Change one property family (geometry, light, camera, fog, motion, audio or title) per iteration where possible.
3. Preserve true independent left and right spot sources and non-overlapping energy keyframes; no statue emergence before second light fully fades.
4. Keep the principal statue geometry and fracture shards in 3-D Blender objects, not a 2-D screenshot collage.
5. Prioritize close-up face detail, camera composition, visible physical continuity and motion timing over extra bloom or fast transitions.
6. Use `bash scripts/render.sh smoke` before expensive preview/final render; `bash scripts/render.sh preview` and `bash scripts/render.sh final` require Blender and FFmpeg.
7. Verify the exported MP4 with `python3 scripts/validate_media.py <path>`; render at least six representative frames. Resolution-only checks **cannot** prove there is no title overlap or anatomy crop.
8. Report exact limits: the current scene has procedural stylized geometry, volume shader smoke and keyed fracture particles; it is **not** yet a high-detail scan, Mantaflow simulation or rigid-body baked fracture.
9. A successful smoke render proves the scene loads and samples render. Only a full render + image/audio inspection + user approval can qualify as Final.
10. Never upload, merge or publish without user authorization.
