# Status and provenance (2026-11-13)

## Verified available and imported
- GitHub repository `kawaho3/motion-effect` (public, previously empty)
- Original editable ZIP `Flower_Friends_Editable_Project.zip` in the ChatGPT Library
- Original source scripts `render_cinematic.py`, `generate_speech.py`, `setup_audio_models.py`, `improve_audio.py`
- Python dependencies `requirements.txt`
- Original phoneme timeline, dialogue script, subtitles
- Original archive's README and separate developer handoff
- Optimized versions of the original 1672×941 artwork in `assets/*.jpg` and compressed soundtrack `work/audio.mp3`; renderer has PNG/WAV fallback and the JPEG/MP3 mode has passed a local still-frame smoke test

## Not yet committed at original quality (binary / media assets)
- `assets/Garden_Base.png` (1672×941), `assets/Garden_Ah_Blink.png`, `assets/Garden_Oh.png`
- `assets/DejaVuSans-Bold.ttf` and `assets/DejaVu_Font_License.txt`
- `work/audio.wav`, individual `work/neural_raw_*.wav`
- `work/audio_report.json`, `work/encoded_audio_qa.json`

## Original rendered deliverables outside ZIP
- `Flower_Friends_30_Seconds.mp4`
- `Flower_Friends_Improved_Audio.wav`
- `Flower_Friends_Preview.jpg`

## Confirmed limitations
- The 30-second video was produced in an earlier project session, not reconstructed or visually audited during this repository transfer.
- The original project's README notes the result is limited 2D facial compositing, not true head/body animation or a full 3D rig.
- Repository source does not imply all binaries or all historical ChatGPT workspace state have been committed; check `git ls-files` against the list above.
- Certain exact dependency versions may not yet be installable across all platforms; validate before promoting to stable.

## Next acceptance tests
1. Fresh clone in clean environment; dependency installation.
2. Confirm included JPEG artwork and MP3 audio exist; optionally supply original PNG plates, font and WAV master.
3. Run `python render_cinematic.py --stills` and inspect patched visemes/eyeblinks (already succeeded locally for optimized mode on 2026-11-13).
4. Full 900-frame render, check final MP4 audio and subtitles.
5. Iterate based on user's original visual-quality feedback.

This is an audit record. Don't label an untested workflow as passing.

## 2026-11-14: Vegetable Shop upgrade

A second, independent 120-second episode source and Kokoro-only audio pipeline are now tracked at `episodes/vegetable_shop/`; it preserves all 44 lines from the earlier poor-quality eSpeak draft. Seven offline unit tests passed locally. The new concept image is tracked as `Scene_Concept.jpg`. Three aligned expression plates plus calibrated `rig.json` are **not** committed; the upgraded audio, video, and GitHub Actions run have **not** yet been remotely verified. No enhanced finished video is claimed. Full rendering is opt-in only.

## 2026-11-14: Successful neural voice and local two-minute render

GitHub Actions [run 43499211402](https://github.com/kawaho3/motion-effect/actions/runs/43499211402) produced 120s neural speech with no clipping, 44 timed lines, and no music. Local image-compositing then produced a 120s 1280×720 30fps MP4; `scripts/check_episode.py` passed duration/FPS/audio checks. The derived JPEG expressions and rig are committed as **preview-grade** reference assets. They are not visually endorsed as exact likeness to the requested reference video. Full video GitHub Actions validation remains pending until the `render-video` job completes.