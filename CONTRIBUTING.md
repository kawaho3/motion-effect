# Contributing

## Project orientation

The main product must **isolate an animated character**, preserve that character's original movement, and export **real transparency with zero audio**, using local/free tools. Read docs/foreground/PROJECT_BRIEF.md, docs/foreground/ARCHITECTURE.md, docs/foreground/STATUS.md and docs/foreground/ROADMAP.md before coding. Never equate a historical finished export with code in this repository.

## Developer setup

- Install Python and FFmpeg/ffprobe; run python -m pip install -r requirements-extraction.txt for foreground extraction (or requirements.txt for neural speech) in a virtual environment.
- Run python -m unittest discover -s tests -v and python -m py_compile scripts/extract_character.py.
- For a real video change, test with a rights-cleared clip in WebM and MOV and document environment, duration, FPS and known visual problems.
- Check true alpha against black and white backgrounds, no sound tracks, no missing body parts and appropriate timing.
- Open a focused GitHub issue or pull request with reproducer, command, evidence, limitations, licensing of dependencies and tests.

## Technical and collaboration rules

- Prefer free local code/models; **do not require paid API calls or plugins**.
- Keep the decode, matte, temporal refinement, encode and quality-check stages separate as the project grows.
- No private links, credentials, user-uploaded media, copyrighted sample video, paid model weights or giant renders in regular Git commits.
- Clearly mark proposed features vs code tested end-to-end. Document licenses of every imported model and asset.
- Lightweight GitHub Actions CI runs Python tests on push/PR; full neural voice/video rendering is **manual-only** to limit usage. Still run tests locally.
- Project-wide licensing remains an owner decision. Do not presume third-party media can be re-licensed.

## Good first contributions

A rights-cleared synthetic video integration test; FFprobe alpha/audio verification; Windows installation docs; handling variable frame rate; frame-by-frame corrections; temporal matting benchmarks and resumable frame processing.

## Ready-to-run synthetic test (no previous chat or private source needed)

```sh
python scripts/make_demo.py
python scripts/verify_export.py output/synthetic-demo/synthetic_reference_alpha.mov --strict
python -m unittest discover -s tests -v
```

Read [the complete handoff](docs/foreground/PROJECT_HANDOFF.md) and [the evidence record](docs/foreground/VERIFIED_MEDIA.md) before claiming parity with prior outputs. ProRes 4444 is the default MOV export; the original source video, licensed footage and its exact extraction script are NOT in this public repo.

## Vegetable Shop episode

Start with [episodes/vegetable_shop/README.md](episodes/vegetable_shop/README.md). The image concept and script are checked in; high-quality aligned facial plates and rig calibration are still required. Do not publish the previous eSpeak render as the upgraded neural episode.
