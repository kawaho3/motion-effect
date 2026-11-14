# Motion Effect — Flower Friends

**Reproducible illustrated-character video pipeline.** A pair of illustrated characters teach **rose**, **sunflower**, and **tulip** in a 30-second humorous dialogue. The animation uses facial keyframe patches, phoneme-timed mouth shapes, blinks, gentle head drift, dynamic close-ups, captions and audio post-processing.


## Current video: Vegetable Adventure (12 places, upgraded face animation)

The newest two-minute episode is [episodes/vegetable_shop/journey.py](episodes/vegetable_shop/journey.py): **12 different locations, exactly 10 seconds each**, same standing Max/Mia, gentle joke motion, phoneme-driven lip shapes, eye gaze and eased blinks. Existing **Kokoro ONNX** voices are retained, not eSpeak. Production files and asset provenance are tracked; large MP4/WAV exports are generated locally or via the manual-only [Vegetable Adventure GitHub Actions](.github/workflows/render-vegetable-journey.yml).

Detailed developer text guides: [Sound / Kokoro / mixing](docs/SOUND_GUIDE_KOKORO.txt), [Animation and scene rendering](docs/ANIMATION_GUIDE_JOURNEY.txt), [12-stop timing](docs/SCENE_PLAN_VEGETABLES.txt), plus [episode README](episodes/vegetable_shop/README.md).

```bash
python -m pip install -r requirements.txt -r requirements-journey.txt
python setup_audio_models.py
python episodes/vegetable_shop/build.py --audio
python episodes/vegetable_shop/journey.py --contact-sheet
python episodes/vegetable_shop/journey.py
python scripts/check_vegetable_journey.py episodes/vegetable_shop/output/Vegetable_Adventure_2_Minutes.mp4
```

**Quality status:** local MP4 passed 120.0 s, 3600 frames at 30 fps, 1280x720, one AAC audio track, subtitles and 12 unique scene comparisons. These technical checks do not certify visual similarity to the external video reference; eye/blink and scenery artwork remain preview-grade pending human review.

## Direct MP4 downloads (no ZIP required)

If ChatGPT attachments fail with "This action couldn't be completed" or Chrome blocks the zipped GitHub Actions artifact, use the public [Vegetable Adventure v3 GitHub Release](https://github.com/kawaho3/motion-effect/releases/tag/vegetable-adventure-v3). It includes two individually downloadable MP4 videos and the TXT developer guides, plus SHA256 checksums:

- [Smaller MP4 (5.5 MB)](https://github.com/kawaho3/motion-effect/releases/download/vegetable-adventure-v3/Vegetable_Adventure_Lighter.mp4)
- [HD MP4 (34.5 MB)](https://github.com/kawaho3/motion-effect/releases/download/vegetable-adventure-v3/Vegetable_Adventure_2_Minutes_HD.mp4)
- [Kokoro sound guide TXT](https://github.com/kawaho3/motion-effect/releases/download/vegetable-adventure-v3/SOUND_GUIDE_KOKORO.txt)

These are GitHub **Release assets**, not expiring GitHub Actions ZIP artifacts. If a security program flags any file, investigate rather than overriding its warning. The reproducible manual publishing workflow is in `.github/workflows/publish-vegetable-direct.yml`.


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

The old eSpeak-based demo was rejected for robotic voices and artificial facial movement. The source-controlled replacement lives in [episodes/vegetable_shop](episodes/vegetable_shop/README.md), with the original 44 dialogue lines, an offline **Kokoro timed-phoneme** audio pipeline, spatially aligned face-plate renderer, and quality checks. A [new scene concept](episodes/vegetable_shop/assets/Scene_Concept.jpg), **three derived preview facial expression plates**, and an example calibrated `rig.json` are now included. The 120-second 720p/30fps neural draft passed local FFprobe checks. These procedurally edited facial poses are **not artist-approved or an exact visual reference match**; refine them before a quality release.

[Automated lightweight tests](.github/workflows/ci.yml) run on push/PR. The [manual-only neural audio/video workflow](.github/workflows/render-vegetable-shop.yml) uploads outputs as GitHub Actions artifacts; choose **audio** for speech only or **video** to render the current 30fps *preview-quality* facial plates. The `render-video` branch supports an intentional one-off video test. See [postmortem and acceptance checks](docs/VEGETABLE_SHOP_UPGRADE.md).

### Verified hosted render (2026-11-14)

[GitHub Actions run 43516290455](https://github.com/kawaho3/motion-effect/actions/runs/43516290455) completed successfully on the opt-in `render-journey` branch. The hosted runner generated a 120.0-second, 3600-frame, 30fps HD H.264/AAC video and verified all 12 scene comparisons. [Download its GitHub artifact](https://github.com/kawaho3/motion-effect/actions/runs/43516290455/artifacts/14080498610) (7-day retention; scheduled expiration November 20, 2026). Rendered media are **not permanent Git-tracked binaries**. Visual/reference quality and listening review remain separate human acceptance tasks.
