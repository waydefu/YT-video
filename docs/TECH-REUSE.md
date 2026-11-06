# Reuse assessment from waydefu/Research-

Reviewed source: [waydefu/Research-](https://github.com/waydefu/Research-), 2026-11-06. Research is evidence and candidate documentation, not authority to import code/media. Preserve original links; avoid copying implementation and third-party artwork.

| Research source | Relevance | YT-video decision |
| --- | --- | --- |
| [09 Video automation](https://github.com/waydefu/Research-/blob/main/research/2026-10-retrospective/09-video-automation.md) | OpenFilm / Remotion / FFmpeg / YouTube API | **ADOPT FFmpeg** for encode/verification; **CANDIDATE Remotion/OpenFilm** for future infographics, NOT the primary 3D scene engine |
| [11 Motion graphics/rendering](https://github.com/waydefu/Research-/blob/main/research/2026-11-universal-web-engine/11-motion-graphics-and-rendering.md) | volumetric light, fog, camera DoF, compositing and color space | **ADOPT principles** in Blender Cycles; do not port website WebGPU renderer |
| [28 Advanced shader pipeline](https://github.com/waydefu/Research-/blob/main/research/2026-11-universal-web-engine/28-advanced-shader-pipeline-and-hd2d-recipes.md) | noise density, volumetrics, tone mapping, frame graph | **ADOPT principles** with different Blender nodes; source itself labels recipes untested |
| [30 VIPER 11 cinematic rendering](https://github.com/waydefu/Research-/blob/main/research/2026-11-universal-web-engine/30-viper11-clouds-terrain-cinematic-rendering.md) | volumetric haze, controlled exposure, optics, judicious bloom | **REFERENCE ONLY**: no game assets or shaders copied |
| [07 Audio DSP](https://github.com/waydefu/Research-/blob/main/research/2026-10-retrospective/07-audio-dsp.md) | RMS/peak/LUFS monitoring, phase and distortion | **ADOPT measurement discipline**; dedicated loudness stage remains a follow-up |
| [05 Web motion/3D](https://github.com/waydefu/Research-/blob/main/research/2026-10-retrospective/05-web-motion-3d.md) | true geometry vs flattened effects, source rights | **ADOPT geometry/QA separation**, not Three.js runtime |
| [24 Polyfork](https://github.com/waydefu/Research-/blob/main/research/2026-11-universal-web-engine/24-polyfork-agent-native-3d-assets.md) | editable parametric asset-as-code | **REFERENCE ONLY**: license is custom; no asset imported |
| [33 UniForge3D](https://github.com/waydefu/Research-/blob/main/research/2026-11-universal-web-engine/33-uniforge3d-anchor-guided-multiview-3d-reconstruction.md) | high-quality geometry from multiview data | **DO NOT ADOPT** for commercial video by default: model/checkpoint and background remover licensing restrictions, CUDA cost |
| [Research evidence skill](https://github.com/waydefu/Research-/blob/main/.agents/skills/research-evidence/SKILL.md) | fresh citations, precise source locations | **ADAPT** source-register and traceability discipline |
| [Research governance skill](https://github.com/waydefu/Research-/blob/main/.agents/skills/research-governance/SKILL.md) | scope/permission/CI evidence gates | **ADAPT** branch and PR pattern, not wholesale EAG-100 framework |
| [Asset rights register](https://github.com/waydefu/Research-/blob/main/site/P1-ASSET-RIGHTS-REGISTER.md) | asset provenance and rights status | **ADAPT** at `docs/ASSET-RIGHTS.md` |

## Preferred focused pipeline

Blender authored scene/geometry -> Cycles offline lighting/fog/fracture -> numbered PNG frames -> original generated PCM audio -> FFmpeg H.264/AAC -> ffprobe validity -> representative stills/visual acceptance -> manually approved release.

**Not integrated**: full Three.js, WebGPU, Polyfork assets, UniForge3D checkpoints, external music tracks, paid Runway tools. No browser rendering stack is necessary for an offline movie intro.
