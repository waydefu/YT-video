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
Presentations: follow `docs/WORKFLOW-EXPLAINER-DECK.md` (P0–P9, including the misreading check at G0); the deliverable is a formal science-explainer PPT with seamless Morph camera transitions (not character animation); read `docs/PPTX-SEAMLESS-EXPLAINER.md`, `docs/PPTX-CINEMATIC-MORPH.md` and, for optional ambient loops, `docs/PPTX-LIVE-MOTION.md`; never claim Live2D equivalence for PowerPoint rigid 2D loops; PowerPoint playback (layer C) stays BLOCKED/NOT RUN until actually observed.
Test statements must say whether checked in CI, locally, or not run.

## Governance and source-of-truth precedence

- Review [`docs/GOVERNANCE-STATUS.md`](docs/GOVERNANCE-STATUS.md) for the *current* production lane and historical alternatives. This inventory is dated, not a real-time source of PR/CI status.
- **Current BROKE TRIO creative direction is [`docs/SHOTLIST.md`](docs/SHOTLIST.md)**. It requires two independent sequential lights, **low-bass switching sounds only**, **dust only (no fracture, stone chunks or broken-stone audio)**, and reverse-time assembly of the floor dust into the brand logo.
- The old V3 storyboard [`docs/archive/SHOTLIST-V3-LEGACY.md`](docs/archive/SHOTLIST-V3-LEGACY.md), V3 config and earlier V4 experiments are **historical / implementation candidates**, not the current creative contract. When current shotlist differs from code, report it as an explicit blocker rather than claiming compliance.
- All PRs should run `governance / docs-and-policy` in addition to applicable media-specific tests; only a GitHub repo admin can make the check *required* via branch rules. Do not claim branch protection exists until the settings are actually verified.
- Governance / document changes are not artistic approval, and must not automatically alter, merge, delete branches or publish media.

