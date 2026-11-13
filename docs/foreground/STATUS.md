> Historical documentation imported from `kawaho3/background` on 2026-11-13. Any original repository references below are historical; use `motion-effect` root README and `docs/PROJECT_GUIDE.md` for current instructions.

# What exists vs what remains (13 November 2026)

## Historical outputs reported from earlier conversation

- Original Viggle-like input: viggle-d6d871ba-48aa-4575-b0d0-b6b6ecbb3542.mp4 (~4.4 MB).
- Character_Transparent_Silent.webm: previously produced, ~41.8 MB.
- Character_Transparent_Silent.mov: previously produced, ~125.6 MB.
- Reported ~19.4 sec, 485 frames, silent transparent foreground. The original executable pipeline is not available in this repository.

## Committed now

- [x] Project goals, dependencies, developer onboarding and acceptance criteria.
- [x] New local rembg + FFmpeg baseline script.
- [x] Local standard-library unit tests (3 tests passed).
- [x] Prior Flower Friends animation/render/voice processing **source text**, timing JSON, script and subtitles.
- [x] Media inventory and transparent-video testing procedure.

## NOT completed / NOT claimed

- [ ] End-to-end testing of *new baseline* with original input and output.
- [ ] Robust temporal video matting and validated visual quality.
- [ ] Accurate VFR preservation and frame-level motion QA.
- [ ] Reproduction of existing 19.4-sec historical output by new code.
- [ ] Uploading original/binary source video, prior MOV/WebM, finished Flower Friends video/audio or original PNGs.
- [ ] Approved public rights-cleared benchmark assets.
- [ ] License decision for project code, videos, art and third-party models.

The historical MOV exceeds ordinary GitHub's single-file 100 MB limit and is NOT part of this public repo. Ask owner for licensed sample or an approved Git LFS/release mechanism.

## Additional verified handoff (13 November 2026)

- [x] Recovered the actual historical input and two outputs for local metadata inspection (not committed as public assets).
- [x] FFprobe independently confirmed 485 frames and 19.4 seconds for input, WebM and MOV; outputs contain no audio streams.
- [x] Decoded first/middle/near-final frames in both formats and confirmed real varying alpha values 0–255; see [VERIFIED_MEDIA.md](VERIFIED_MEDIA.md).
- [x] Replaced the new baseline's default MOV encoding with ProRes alpha, matching the historical MOV *codec family* (not original extraction model).
- [x] Added local synthetic clip generator and reference alpha output, tested with FFmpeg.
- [x] Added export verification tool, 6 local unit checks plus 1 FFmpeg-based synthetic integration test and a restore helper for an owner-supplied original Flower Friends archive.
- [ ] New rembg model evaluated on the original Viggle clip end-to-end with quality report.
- [ ] Rights confirmed and original binary media legally distributed to external contributors.

Start with [PROJECT_HANDOFF.md](PROJECT_HANDOFF.md) and [DEVELOPER_SETUP.md](DEVELOPER_SETUP.md).
