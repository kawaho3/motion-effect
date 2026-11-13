# Why the vegetable-shop prototype was rejected and what changed

## Incident review

The previous 120-second render used eSpeak at a high speech rate rather than the repository's neural Kokoro engine. Lip motion was generated from approximated rhythms and painted shapes, with imprecise character silhouettes. It rendered source animation at 12 fps then duplicated frames to export 24 fps. These issues explain robotic dialogue and an artificial look. A simple EQ pass cannot make that prior speech genuinely human-like.

## Changes

- Added an **explicit Kokoro-only** speech path with original syllable/phoneme timing instead of crude eSpeak timing.
- Added a true 30-fps image-plate animation path; mouth and eye regions are taken from aligned source art, not re-painted ellipses.
- Added a 120-second timeline planner that **rejects** overlong/underlong speech instead of severely resampling speech.
- Reused `improve_audio.py` loudness and true-peak protection and disabled music by default. Added machine-readable audio report and strict FFprobe export metadata checks.
- Kept original vegetable dialogue and added a reproducible manual workflow plus low-cost automatic tests.
- Made quality prerequisites explicit: the three aligned expression plates and exact face regions **still need to be provided and visually accepted**.

## Acceptance gate

1. Listen to beginning/middle/end of neural dialogue for pronunciation, pacing, noise, voice consistency and level.
2. Check each character's aligned mouth plates for seams, wrong speaker, teeth and eyes; review jokes at frame level.
3. Verify 120s, 30 fps, 1280×720, a real audio stream, subtitles and no unintended silence/clipping.
4. Compare against the owner's reference video visually; obtain explicit artistic approval before calling the output similar.
5. Store large MP4/WAV as workflow artifacts or an approved release, not a routine source commit.

**Status:** Source code and offline tests exist; neural output not verified in this transfer environment because model/runtime assets are absent. The renderer intentionally will not fabricate expression plates. The GitHub Actions workflow is configured but a successful remote run has not yet been confirmed.

## GitHub Actions validation note

The first manual-audio branch run failed at dependency installation: NumPy 2.5.4 is incompatible with Python 3.11. The audio workflow was changed to Python 3.13; installation and synthesis still require a new successful run before claiming completion.

## First neural render result (2026-11-14)

The second neural-audio GitHub Actions workflow **succeeded** with exactly 120.0 seconds, -16.56 LUFS integrated loudness, -1.50 dBTP, zero clipped samples, no backing track, and phoneme timelines for all 44 shortened lines. The new local 1280×720 30fps video was rendered with scene-aligned **procedurally derived preview** mouth/blink JPEGs. `scripts/check_episode.py` confirmed 120.0s, 30fps, 1280×720 and one audio stream. This is a verified technical prototype, NOT a confirmed visual match to the reference; artist-grade facial plates are still needed.