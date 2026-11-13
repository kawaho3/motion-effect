> Historical documentation imported from `kawaho3/background` on 2026-11-13. Any original repository references below are historical; use `motion-effect` root README and `docs/PROJECT_GUIDE.md` for current instructions.

# Release quality gate

Every checked item must have a reproducible command, sample hash, and evidence. Passing the current small unit tests alone is not enough.

## Reproducibility
- [ ] A fresh-clone developer can reproduce examples using documented local tools.
- [ ] Python versions, dependencies, FFmpeg build, model name/checksum, OS and hardware recorded.
- [ ] Model downloads are documented; no paid credit, cloud inference or hidden credentials.
- [ ] Rights-cleared inputs and expected outputs available with hashes.

## Media correctness
- [ ] Complete target character visible throughout every frame; no missing hands, feet, hair or face.
- [ ] Actual alpha verified across multiple frames and in target editing software.
- [ ] Output contains **zero** audio streams.
- [ ] All output frames correspond to input motion and source timing (including VFR if supported).
- [ ] Correct duration, dimensions, orientation, color and aspect ratio.
- [ ] Stress scenes with fast movement, blurred hands, thin hair and partial occlusions evaluated.
- [ ] Background contamination, flicker, edge halos and temporal stability measured and reviewed.

## Project integrity
- [ ] Open-source/model and asset licenses confirmed and recorded.
- [ ] Never publicly redistribute uncertain copyrighted or private videos.
- [ ] README, setup, roadmap, tests, usage and errors match shipped code.
- [ ] Baseline limitation disclosure remains visible; claims have real test evidence.
- [ ] Releases tagged with changelog and minimal artifact checksums.

## Current gate

Historical exports are confirmed to have real alpha and no audio. The **new extraction baseline has not been tested end-to-end on the original Viggle clip**, and the original historical segmentation algorithm has not been recovered. Not release-ready for production-quality matting.