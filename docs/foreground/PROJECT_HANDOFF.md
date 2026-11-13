> Historical documentation imported from `kawaho3/background` on 2026-11-13. Any original repository references below are historical; use `motion-effect` root README and `docs/PROJECT_GUIDE.md` for current instructions.

# Complete developer handoff — Background

**Last reviewed:** 2026-11-13. **Primary repo:** https://github.com/kawaho3/background.

This handoff is written for a developer who has never seen any ChatGPT conversation. Read it before altering the project.

## 1. What the owner asked us to build

The owner provided an animated character video and asked: **"extract this character and all movement as a video, no background, no sound."** The output must preserve the on-screen character and animation while removing background and stripping audio. A transparent foreground movie should be reusable in videos, editors, and animations. The initial example was a portrait Viggle-generated MP4 named `viggle-d6d871ba-48aa-4575-b0d0-b6b6ecbb3542.mp4`.

**Do not confuse the goal with a background replacement**: a solid green, white or checkerboard background is NOT transparency. Do not invent new gestures, delete body parts, distort timing, or mute audio while still carrying a silent audio track. The export should have an actual alpha channel and no audio streams.

## 2. Non-negotiable constraints and preferences

- **Free/local-first:** Avoid paid third-party services, plug-ins, API calls or credit consumption. Open-source models downloaded once and run locally are acceptable.
- **Preserve motion:** The goal is foreground isolation, NOT retiming, restyling or creating a new animation.
- **Practical, reproducible delivery:** Provide code, dependencies, commands, tests, metadata, quality checks, and failures in GitHub. Another developer should be able to start from a clone and generated fixture.
- **Work efficiently:** Favor a direct, working baseline over vague plans. Quality and end-to-end validation are still required for claims of completion.
- **Public repo safety:** Do not upload media with unknown redistribution permission, private/signed CDN URLs, model weights under restrictive terms, credentials or unlicensed fonts.

## 3. What has already happened

1. The user supplied the Viggle example MP4 in a previous conversation.
2. An earlier session produced silent transparent WebM and MOV files. Those bytes have since been recovered and analyzed; see `VERIFIED_MEDIA.md` for exact stream metadata and SHA-256 values.
3. **The original segmentation/matting source code used for those exports was not recovered**. We cannot honestly claim to reproduce the same result using the current code.
4. This repo's first handoff added a new independently written `scripts/extract_character.py` (rembg + FFmpeg), documentation, and related 2D animation text sources.
5. This follow-on handoff adds a no-API synthetic test clip generator, alpha/audio verification, records of the historical exports, updated ProRes MOV encoding, more tests and detailed onboarding.

## 4. Project components and boundaries

### Primary deliverable: Background extractor

The core CLI is `scripts/extract_character.py`. Its current implementation does **independent single-frame person matting** using rembg, then encodes into transparent VP9 WebM or ProRes 4444 MOV. This is a local baseline, not a robust video-aware model. It does not guarantee perfect hands/hair, alpha, occlusion, edge stability, or correct variable-frame-rate timings.

### Auxiliary scripts and evidence

- `scripts/make_demo.py`: **fully synthetic, redistributable** short animated character and its true transparent reference. Does not need model downloads.
- `scripts/verify_export.py`: validates streams, SHA-256, sample-frame alpha, and audio absence using FFmpeg. Does not prove visual quality.
- `docs/VERIFIED_MEDIA.md`: independently recorded technical characteristics of the recovered historical input and outputs.
- `docs/ROADMAP.md` and `docs/RELEASE_CHECKLIST.md`: outstanding work and release gates.

### Related but separate experiments

Earlier work on motion effects tried subtle eye/lip movement and image switching, with a 30-second flower-teaching video, neural local speech, custom DSP, subtitles and photo-like character images. Some user feedback rejected an earlier low-quality style, motivating improved aligned art and voice quality. Those *source text files* are preserved in `examples/flower-friends/`. The full editable ZIP remains outside Git and is not needed for the core extractor. Another larger Blender "Reed House" series project is separate: do not present its prototypes as finished extraction features.

## 5. If you are a new contributor, do this first

1. Clone the repo, install Python, FFmpeg/ffprobe, and `requirements.txt` in an isolated environment.
2. Run `python -m unittest discover -s tests -v`.
3. Run `python scripts/make_demo.py` and then `python scripts/verify_export.py output/synthetic-demo/synthetic_reference_alpha.mov --strict`.
4. Inspect the synthetic source MP4 and expected alpha reference in an editor; see `QUALITY.md`.
5. **Optional expensive experiment:** run `python scripts/extract_character.py output/synthetic-demo/synthetic_source.mp4 output/from_rembg.webm` (downloads a free segmentation model once). Observe segmentation quality; there is no expectation it perfectly matches the synthetic reference.
6. Choose a P0/P1 issue and include actual evidence and failure cases in a pull request.

## 6. Missing assets and work (not in repository)

The original input and prior WebM/MOV output were recovered for analysis but **not redistributed** in this public Git repository. Their exact hashes are in `VERIFIED_MEDIA.md`; ask the owner for approved rights-cleared access if needed. The old extraction script is absent. The flower-art render assets / model data / font are also absent (see `ASSET_MANIFEST.md`). A fresh checkout **does not yet reproduce the historical original Viggle extraction**, and the new pipeline does not yet handle temporal matte instability.

## 7. Success means

A free, reproducible pipeline that preserves full foreground motion and timing, produces real transparent silent media, passes metadata and visual checks on approved sample clips, has clear cross-platform instructions, and distinguishes measured facts from goals. **No prior chat context is needed to understand or start the work.**