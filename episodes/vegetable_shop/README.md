# Vegetable Shop — neural-quality two-minute episode

This project supersedes the **previous low-quality eSpeak vegetable demo**. Its 44 original dialogue lines remain editable in `script.json`. The target is a **120-second, 1280×720, real 30 fps** two-character conversation with a friendly shop setting, small joke reactions, and speech-timed lips. It uses the repository's **Kokoro ONNX** offline voices (`af_heart`/`am_puck`) and custom `improve_audio.py` DSP. No paid voice API, plugin, or synthetic eSpeak fallback is used.

## What is included

- `build.py`: validates script, generates neural voices, alignments, `.srt`, audio quality report; renders an illustrated clip with aligned facial plates.
- `script.json`: 44 Max/Mia lines including vegetables and jokes (preserved from the prior editable project).
- Two GitHub Actions: lightweight unit tests on push/PR; **manual-only** neural audio or full render; final media are downloadable workflow artifacts rather than binary Git commits.

## Build high-quality dialogue locally

Install Python 3.11, FFmpeg, root `requirements.txt`, and once run `python setup_audio_models.py` from repository root. This downloads and verifies Kokoro model weights; it does **not** use a hosted voice service.

```sh
python episodes/vegetable_shop/build.py --check-script
python episodes/vegetable_shop/build.py --audio
```

The output directory is `episodes/vegetable_shop/output/`. Generated files include 48 kHz 24-bit stereo audio, timeline with phone timings, an SRT file and a technical audio report. Music is OFF by default because the old backing track obscured poor voice quality. To supply a licensed bed, pass `--music path/to/music.wav` with `--audio`.

## Full video requires artwork assets — quality gate

Place the **same** 1672×941 (or other identical dimension) scene in three accurately registered files under `episodes/vegetable_shop/assets/`:

1. `Scene_Base.png`: Max and Mia standing together, smiling, lips at rest, eyes open.
2. `Scene_Ah_Blink.png`: same scene pixel-aligned except controlled mouth openings and closed eyes.
3. `Scene_Oh.png`: same scene pixel-aligned except rounded speaking mouths; eyes open.

Also provide `rig.json`, e.g.:

```json
{
  "Max": {"mouth": [0.36, 0.20, 0.40, 0.25], "eyes": [[0.34, 0.13, 0.37, 0.17], [0.38, 0.13, 0.41, 0.17]]},
  "Mia": {"mouth": [0.59, 0.22, 0.62, 0.27], "eyes": [[0.57, 0.15, 0.59, 0.19], [0.62, 0.15, 0.64, 0.19]]}
}
```

**These coordinates are examples, not calibrated values.** Use a real frame inspection to set them. A single unaligned reference scene is insufficient for realistic lips. The renderer deliberately stops with a clear error rather than fabricating mouth ellipses and calling it lip sync. `python episodes/vegetable_shop/build.py --render` creates the MP4 when these files and the audio timeline exist.

## GitHub Actions usage

Use **Actions → Vegetable Shop - neural audio and video → Run workflow → audio** to generate a high-quality voice draft; download the audio and SRT from the workflow's Artifacts section. Select `video` only after all four art files are added and calibrated. **No automatic heavy render runs on the main branch**, respecting usage limits. A dedicated `render-audio` branch can trigger a one-off neural-audio test upon push. GitHub-hosted runners may still consume GitHub Actions minutes depending on repository/plan settings.

## Limitations

Kokoro speech sounds more natural than eSpeak but still needs **human listening review**. Phoneme durations drive image-based mouth visemes; this is not full-face neural motion tracking. The workflow can prove technical media properties but **cannot certify that the look matches a YouTube reference** without visual comparison and approval. The original reference is not reproduced exactly. New artwork, manual facial registration, actual listening review, and a full successful render are required before calling this a final-quality replacement.