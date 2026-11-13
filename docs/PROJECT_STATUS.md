# Status and provenance (2026-11-13)

## Verified available and imported
- GitHub repository `kawaho3/motion-effect` (public, previously empty)
- Original editable ZIP `Flower_Friends_Editable_Project.zip` in the ChatGPT Library
- Original source scripts `render_cinematic.py`, `generate_speech.py`, `setup_audio_models.py`, `improve_audio.py`
- Python dependencies `requirements.txt`
- Original phoneme timeline, dialogue script, subtitles
- Original archive's README and separate developer handoff

## In the recovered ZIP (binary / media assets)
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
2. Confirm required artwork, font and master WAV exist.
3. Run `python render_cinematic.py --stills` and inspect patched visemes/eyeblinks.
4. Full 900-frame render, check final MP4 audio and subtitles.
5. Iterate based on user's original visual-quality feedback.

This is an audit record. Don't label an untested workflow as passing.
