# YT-video Production Instructions

## Mandatory quality-first delivery workflow

Before any significant visual, animation, presentation, video or interactive deliverable, **read `docs/QUALITY-GATED-WORKFLOW.md` and `.agents/skills/quality-gated-production/SKILL.md`** and follow its G0–G5 quality gates:

1. **G0 contract** — preserve the user's exact native medium, visual benchmark and non-negotiable behaviors; do not silently substitute an MP4 for native Canva/PowerPoint animation.
2. **G1 source and direction** — verify assets and rights; select a visual direction that can plausibly meet the benchmark.
3. **G2 minimum proof** — implement and test the riskiest real effect in a short sample before creating a full deliverable.
4. **G3 self-QA** — separately check file structure, static visuals, **native playback/interaction in the intended tool**, desktop/mobile experience, content accuracy and asset rights. Inspect the artifact yourself before asking the user to be its first tester.
5. **G3 FAIL = redo**, not extra decoration or more pages. **G3 BLOCKED / NOT RUN = unverified**, not complete. CI, OOXML, static renders and generated files do not prove final visual/animation quality.
6. **G4/G5** — only expand after the minimum proof passes; report actual evidence, unresolved gaps, and `RESEARCH/SPIKE/PREVIEW/CANDIDATE/FINAL-APPROVED` status before PR or handoff.

For docs-only or nonvisual edits, apply proportional meaningful checks; don't require a cinematic render where the PR makes no visual-quality claim. No project or work item is `FINAL-APPROVED` until its essential quality gates and user acceptance are satisfied. **Never automatically merge or publish.**


Work on an explicit topic branch and open a PR; never merge or publish automatically.
Keep user references separate from footage. Only original/properly licensed media may ship.
Prefer pre-existing high-quality, provenance-verifiable, commercially permitted 3D assets over procedural anatomical modelling; use original geometry only when visual review shows it meets the brief.
No borrowed screenshots, reference images, meshes, music, fonts, or external assets without a rights record.
Never represent keyframed particle approximations as true rigid-body or fluid simulations.
Never call an image sequence or composited poster a 3-D animation without actual spatial geometry.
Preserve source project files, explicit output labels (smoke test, preview, final), and reproducibility.
Before changing a shot, read `docs/SHOTLIST.md`, `config/production.json`, `docs/TECH-REUSE.md`.
Render at 1920×1080 16:9, 24 fps, square pixels; ensure title and subject fit in 10% edge-safe area and 15% text-safe area.
Do not treat automated resolution tests as proof of acceptable framing. Review frames on desktop and mobile.
Lighting contract: LEFT completes and turns off BEFORE RIGHT starts; BOTH off before statue enters smoke.
User review required for imagery, motion, audio levels, factual statements and final YouTube publication.
Never silently upgrade scope, enable services, download external binaries, or use credentials based on research documents.
Test statements must say whether checked in CI, locally, or not run.
