---
name: quality-gated-production
description: Use on every new or significantly revised YT-video visual, animated presentation, Blender/3D, interactive site or audiovisual deliverable. Enforce sample-first workflow, self-review, real-playback evidence and truthful completion reporting before scaling or delivery.
---

# Quality-gated production

**Mandatory first read**: `AGENTS.md` and `docs/QUALITY-GATED-WORKFLOW.md`, followed by medium-specific documents (`docs/SHOTLIST.md`, `config/production.json`, `docs/ASSET-RIGHTS.md`, Canva or PPTX guides).

1. **G0 — Contract**: Pin exact output format and native behavior; include user benchmark. Do not substitute an MP4 for native Canva or PPTX Morph animation.
2. **G1 — Direction and rights**: Prove quality and licensing of chosen source visual assets; prioritize high-quality authorized references over low-fidelity procedural approximations.
3. **G2 — Minimum proof**: Implement the riskiest required effect on a small usable sample first. For cinematic slides, begin with 10–15 seconds (2–4 camera poses) and continuous scene anchors.
4. **G3 — Verify personally**: A) file structure, B) representative static frames, C) **actual playback or interaction in the target app**, D) desktop/mobile readability, E) factual/asset-rights review. Record evidence for each.
5. **Stop conditions**: If B/C/D fails benchmark, **redo the visual direction**; don't expand scope or hide flaws with more features. If C can't run, label `BLOCKED/NOT RUN`, not `PASS`.
6. **G4 — Expand only after proof**: Extend the full sequence in batches and repeat G3 after every substantial revision.
7. **G5 — Handoff**: Deliver editable source, preview, licenses, executed tests, limitations, stage and evidence. Draft PRs/CI never prove aesthetic quality. Do not merge or publish without authorization.
8. Use meaningful smoke tests for small docs/code changes. Do not demand a video review for a docs-only PR; do not make claims about improved animation without actually testing animation.

Decision rule: **source of truth is the intended user experience, not the mere existence of code, slides, tests, or an export**.

Every report must specify `RESEARCH/SPIKE/PREVIEW/CANDIDATE/FINAL-APPROVED` and separate `PASS/FAIL/BLOCKED/NOT RUN` for structure, visual, native playback, device and rights.
