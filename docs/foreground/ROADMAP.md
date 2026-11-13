> Historical documentation imported from `kawaho3/background` on 2026-11-13. Any original repository references below are historical; use `motion-effect` root README and `docs/PROJECT_GUIDE.md` for current instructions.

# Roadmap for contributors

## P0 — Make a reproducible vertical slice
- [x] Consolidate objective, status, original references and missing assets.
- [x] Add baseline local foreground isolation script and metadata-free unit checks.
- [ ] End-to-end test on a legal clip and capture alpha/video/audio metadata.
- [x] Add a local generator for a rights-cleared synthetic input and transparent reference (source code, no binary upload needed).
- [ ] Add fully automatic integration-test comparison against the synthetic reference.
- [ ] Validate Windows and Linux installation, FFmpeg and model download.
- [ ] Add a machine-readable FFprobe report for alpha, frame count, duration and silence.

## P1 — Production quality extraction
- [ ] Implement **temporal video matting** instead of frame-independent masks.
- [ ] Handle fast moving hands, hair strands, shadows, accessories and motion blur.
- [ ] Provide manual correction of problem frames and temporal propagation.
- [ ] Preserve true original timestamps for VFR input.
- [ ] Implement resumable renders with verified intermediate frames.

## P2 — Product features
- [ ] RGBA PNG export option, compositing preview, flexible alpha codecs.
- [ ] Batch processing, queue, logging and configurable quality.
- [ ] Cross-platform GUI; optional GPU support and CPU fallback.
- [ ] Benchmark resource costs, speed and quality.

## P3 — Open contribution readiness
- [ ] Agree on code/asset/model licensing.
- [ ] Provide legally distributable demo inputs and outputs.
- [ ] Add opt-in CI after owner checks credit and compute budgets.
- [ ] Publish release instructions with exact versions and provenance.
