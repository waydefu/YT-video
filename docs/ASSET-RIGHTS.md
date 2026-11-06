# Media/source rights and provenance

No reference-image pixels have been placed in the Blender scene. User-supplied screenshots/images are visual direction only and are **not redistributed** in this repository.

| Asset | Location | Origin | License/rights status | Use |
| --- | --- | --- | --- | --- |
| Stylized marble bust geometry | `blender/scene.py` | Original mesh assembled by procedural primitives/curved drapery in this repo | Original project source | Rendered hero and final trio |
| Film smoke | `blender/scene.py` | Generated volumetric 4-D noise shader | Original procedural effect; not stock footage | Cycles volume scattering |
| Dust / fracture fragments | `blender/scene.py` | Deterministic procedural 3-D particles | Original procedural effect | Fracture/transition blockout |
| Spotlights, light rays, studio floor | `blender/scene.py` | Generated 3-D scene nodes and geometry | Original project source | Keyframe reveal |
| Sound effect score | `scripts/soundtrack.py` | Generated waveforms/noise, seeded; no samples | Original procedural audio | Exported soundtrack |
| Brand/title text | `blender/scene.py` | Original wording; default system DejaVu Serif or Liberation Serif font | Third-party bundled OS fonts; review font license when redistributing font file. **Do not commit font binaries.** | Render text only |
| Research- documents | `docs/TECH-REUSE.md` | URLs/link references only | Source author permissions unchanged | Engineering study, not copied code/assets |
| Marble Bust 01 (V4) | `scripts/fetch_cc0_bust.py` → `assets/external/` (not committed) | Rico Cilliers via Poly Haven, CC0; SHA-256 pinned, see `docs/V4-ASSETS.md` | CC0, commercial use allowed | V4 hero sculpture |
| Anatomy official sample screenshots | Downloaded in CI from pinned upstream commit `1482e8469b0a9e0d8cc18ea2740a01423d29ae80`; **not committed** | `wheresryan22/anatomy`, MIT, Copyright (c) 2026 Ryan | MIT: upstream LICENSE text must travel with every artifact (embedded in speaker notes + uploaded) | `docs/ANATOMY-SPIKE-QA.md` spike deck only |
| Living Scene character, hills, sunburst, sign | `scripts/build_living_scene.py` | Original procedural vector geometry in this repo | Original project source; **no third-party art**; artistic quality is spike-level | `docs/PPTX-LIVE-MOTION.md` spike deck |
| Reference video (Canva playback phone recording) | Outside repository | User-provided | **Unknown distribution status**; frames are never committed | Quality benchmark only |
| User reference art | Outside repository, conversational reference | User-provided | **Unknown distribution status** | Direction only; never include without explicit rights confirmation |

Original geometry does **not** by itself guarantee aesthetic quality. High-detail replacement meshes are allowed only with individually verified provenance and distribution/commercial rights. Log actual source URL, license, access date, SHA and approvals before import.
