# Motion Effect — Flower Friends

**Reproducible illustrated-character video pipeline.** A pair of illustrated characters teach **rose**, **sunflower**, and **tulip** in a 30-second humorous dialogue. The animation uses facial keyframe patches, phoneme-timed mouth shapes, blinks, gentle head drift, dynamic close-ups, captions and audio post-processing.

## What is in this repository

- **Original source:** `render_cinematic.py`, `generate_speech.py`, `improve_audio.py`, `setup_audio_models.py`, `requirements.txt`.
- **Ready-to-render light assets:** three aligned 1672×941 JPEG keyframes in `assets/` and a 30-second MP3 dialogue track in `work/`.
- **Timing and text:** `work/timeline.json`, `deliverables/Flower_Friends_Script.txt`, `deliverables/Flower_Friends_Cinematic_Subtitles.srt`.
- **Documentation:** [Developer handoff](docs/DEVELOPER_HANDOFF.md), [asset manifest](docs/ASSET_MANIFEST.md), [project status](docs/PROJECT_STATUS.md), [original README](docs/ORIGINAL_PROJECT_README.md).

The JPEG/MP3 assets are compressed copies for a smaller Git checkout. **For the highest available quality**, replace them with the original three PNG expression plates and `work/audio.wav` from `Flower_Friends_Editable_Project.zip` in the project's ChatGPT Library. The renderer automatically prefers PNG/WAV files if present.

## Quick start (render only)

Install Python, FFmpeg and the small rendering dependency set:

```bash
git clone https://github.com/kawaho3/motion-effect.git
cd motion-effect
python -m pip install -r requirements-render.txt
ffmpeg -version
python render_cinematic.py --stills
python render_cinematic.py
```

The rendered 1280×720, 30 fps movie appears at `deliverables/Flower_Friends_30_Seconds.mp4`. The stills go to `work/`.

**Smoke-test status:** a local test of the light-asset mode rendered still frames successfully on 2026-11-13. A complete fresh-clone 900-frame movie render has **not** been certified here.

## Generate new spoken dialogue (optional)

The original neural-audio path is CPU-capable and does not use paid APIs, but it downloads Kokoro model files once.

```bash
python -m pip install -r requirements.txt
python setup_audio_models.py
# Edit the SCRIPT declaration in generate_speech.py
python generate_speech.py
python render_cinematic.py
```

The included `improve_audio.py` can also process an existing voice recording:

```bash
python improve_audio.py input.wav output.wav
```

## For developers and Codex

**Start with [docs/DEVELOPER_HANDOFF.md](docs/DEVELOPER_HANDOFF.md).** It explains the architecture, assets, inputs, outputs, assumptions, acceptance tests, and known limitations. The project's [status ledger](docs/PROJECT_STATUS.md) separates confirmed work from missing or untested pieces.

The project does **not** contain a 3D rig or automated full-body motion system. It is illustrated 2D compositing with speech-oriented expression changes. The existing prototype is intended for further improvement, particularly more natural faces and audio.

### Core file tree

```text
motion-effect/
  README.md
  requirements-render.txt
  requirements.txt
  render_cinematic.py
  generate_speech.py
  improve_audio.py
  setup_audio_models.py
  assets/
    Garden_Base.jpg
    Garden_Ah_Blink.jpg
    Garden_Oh.jpg
  work/
    audio.mp3
    timeline.json
  deliverables/
    Flower_Friends_Script.txt
    Flower_Friends_Cinematic_Subtitles.srt
  docs/
    DEVELOPER_HANDOFF.md
    PROJECT_STATUS.md
    ASSET_MANIFEST.md
    ORIGINAL_PROJECT_README.md
```

## New: Vegetable Shop (2-minute neural episode)

The old eSpeak-based demo was rejected for robotic voices and artificial facial movement. The source-controlled replacement lives in [episodes/vegetable_shop](episodes/vegetable_shop/README.md), with the original 44 dialogue lines, an offline **Kokoro timed-phoneme** audio pipeline, spatially aligned face-plate renderer, and quality checks. A [new scene concept](episodes/vegetable_shop/assets/Scene_Concept.jpg) is included, but **aligned expression plates and a calibrated facial rig are not yet supplied**. Do not claim a finished 2-minute neural video exists until those assets and a verified render are available.

[Automated lightweight tests](.github/workflows/ci.yml) run on push/PR. The [manual-only neural audio/video workflow](.github/workflows/render-vegetable-shop.yml) uploads outputs as GitHub Actions artifacts; choose **audio** first and **video** only when the three aligned plates and rig.json have been added. See [postmortem and acceptance checks](docs/VEGETABLE_SHOP_UPGRADE.md).
