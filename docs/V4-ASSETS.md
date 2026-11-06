# V4-A/B | Existing commercial-safe sculpture first

## Selected model
- Asset: [Marble Bust 01](https://polyhaven.com/a/marble_bust_01)
- Original creator: **Rico Cilliers**, distributed by Poly Haven
- License: **CC0** on [official original asset](https://polyhaven.com/a/marble_bust_01) and [Poly Haven terms](https://polyhaven.com/license). Commercial rendering/editing allowed.
- Asset type: real 3D modeled/scanned sculpture, PBR materials; **not** generated from the chat reference images.
- Downloaded as 1.9 MB self-contained GLB from [Innerscene mirror](https://www.innerscene.com/tools/library/3d-parts/marble-bust-f5604fc9), which identifies the original Poly Haven author/source and CC0.
- Use `python3 scripts/fetch_cc0_bust.py` on GitHub Actions to get the binary, then import into Blender. Keep external mesh out of git initially.
- Pin content SHA-256 after first successful CI retrieval and human review. Never silently replace a CC0 mesh with a different model if the network fails.

## Why we changed
The V3 geometry was procedural spheres and deformed cylinders; smoke CI passed but it visually resembled a toy, not a classical bust. V4 uses high-quality existing third-party asset with an explicit commercial-safe license instead of pretending we can invent the anatomy.

## Locked shot A/B sequence
| Timeline | Output |
| --- | --- |
| 0.0–0.74s | Subtle 3-D fog in black space, no sculpture |
| 0.74–1.94s | LEFT spotlight rises and fully fades |
| 1.94–2.12s | Dark interval; both spots zero |
| 2.12–3.12s | RIGHT spotlight rises and fully fades |
| 3.12–3.38s | Dark interval, no sculpture |
| 3.38–6.25s | High-quality imported marble bust emerges *through* volume, while camera advances; portrait light and rim activate **only after** sequential opening spots end |

This PR does **not** include breakup, reassembly or text; these come after the user approves an actual 3-D keyframe review.

## Format and review
- Movie master 1920×1080 / 16:9 / square pixels / 24 fps.
- Preview frames are 960×540 in **exactly the same composition**.
- Human review needed for: correct face orientation, complete head and shoulders, no horizon line, smoke density, volumetric beam distinctness, portrait proportions and black levels.
- A green GitHub workflow means Blender generated 5 true-3-D frames, **not** that composition is artistically accepted.

## References / ownership
The user's reference collage and original BROKE TRIO logo remain only private creative direction. No unlicensed image from that collage is packaged into the V4 3D project. Third-party creator attribution is retained in docs even though CC0 does not require it.
