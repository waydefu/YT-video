---
name: canva-cinematic
description: Use when researching, planning, building or reviewing cinematic Canva presentations and YouTube educational video transitions, especially Match & Move, layered camera-like motion, timing and export QA.
---

# Canva cinematic presentation skill

1. Read `AGENTS.md`, `docs/CANVA-CINEMATIC-MOTION.md`, `docs/CANVA-TECHNIQUE-INDEX.md`, `docs/CANVA-REFERENCE-RECIPE.md`, `docs/CANVA-QA.md` and `docs/ASSET-RIGHTS.md`. For edits to the Blender title sequence also read `docs/SHOTLIST.md`, `config/production.json`, `docs/TECH-REUSE.md`.
2. Confirm the deliverable is **native Canva presentation**, **Canva video edit**, **editable PPTX**, or **rendered MP4**. Never claim all Canva animations survive PowerPoint export.
3. Research current Canva capability through its official Help Center / Design School. Label each statement **officially documented**, **design recommendation**, **hands-on verified**, or **unverified**; distinguish plan and rollout limitations.
4. Start from story beats and visual anchors. Plan transitions as spatial continuity (same subject and shared background across adjacent states), not unrelated page effects. For Match & Move, duplicate the page and modify the same retained elements.
5. For explanatory content show both benefits and limitations, installation, practical usage, who should / should not use it. Demonstration output and factual statements must be source-backed; never invent a successful test.
6. Keep copy readable in Traditional Chinese with a strong title hierarchy, restrained movement, 16:9 composition, 10% subject / 15% title safe zones.
7. Keep reference media private and out of the repo. Each final asset needs provenance and commercial-use rights. Canva content and stock music have separate licenses; Popular Music is not generally usable for monetized YouTube.
8. Perform preview → transition-boundary frame inspection → export → `ffprobe` verification → desktop and mobile visual / audio review. Do not claim Canva direct FPS control unless verified; re-encoding to 24 FPS does not repair stutter.
9. Never claim that a docs-only change validates motion quality, renders a Canva video, or produces a finished presentation. Distinguish CI checks from manual acceptance.
10. Work on a topic branch and open a PR, **do not merge / publish without separate authorization**. Log untested UI behaviors and risks in the PR.
