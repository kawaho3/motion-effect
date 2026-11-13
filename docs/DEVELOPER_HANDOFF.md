# Developer handoff — Motion Effect

## 1. Goal
Create a 30-second illustrated two-character flower lesson with a funny conversation, attractive cinematic still artwork, speech-synchronized mouth/eye effects, gentle camera moves, subtitles, and clean audio. The requested target aesthetic is inspired by the user's reference video, not an exact reproduction. A future developer should preserve the design fidelity and improve expression animation, not substitute flat cartoons.

## 2. Current implementation
- `render_cinematic.py` — 30 fps, 1280×720, 900-frame offline PIL/SciPy facial compositing; mouth phoneme poses; eyelid blinks; gentle head micro-warp; camera shots; captions; FFmpeg H.264/AAC final render.
- `generate_speech.py` — on-device voice generation and phoneme/segment timeline with Kokoro ONNX, plus audio processing.
- `setup_audio_models.py` — one-time model download and SHA256 validation.
- `improve_audio.py` — custom DSP filtering, EQ, de-essing, compression, LUFS control, mixing and peak protection.
- `work/timeline.json` — segment and phoneme timings for original lesson.
- `deliverables/*` — original dialogue and SRT subtitles.

## 3. Developer environment
Python 3.11+ is a good starting point, but original pinned package versions may require an up-to-date Python. Install FFmpeg separately and ensure `ffmpeg` is on PATH. A compatible CPU can render without a hosted GPU. On Windows use PowerShell; on macOS/Linux use a terminal.

```bash
git clone https://github.com/kawaho3/motion-effect.git
cd motion-effect
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
ffmpeg -version
```

## 4. Input and output contract
The renderer assumes 1672×941 aligned source artwork and uses hardcoded ROI coordinates in `render_cinematic.py`. All three frames **must have exactly aligned facial landmarks**, not merely similar poses:
- `assets/Garden_Base.png` — eyes open, mouths resting
- `assets/Garden_Ah_Blink.png` — blink plus open 'ah' mouth
- `assets/Garden_Oh.png` — eyes open, rounded 'oh' mouth
- `assets/DejaVuSans-Bold.ttf` — font, with its license
- `work/audio.wav` — finished 48kHz stereo master
- `work/timeline.json` — dialogue row start/end/phones
- `deliverables/Flower_Friends_Cinematic_Subtitles.srt`

The original art and audio are inside the project archive `Flower_Friends_Editable_Project.zip` recovered from the project's ChatGPT Library. Large source media may need to be copied into this working tree if not checked into Git. See `docs/PROJECT_STATUS.md`.

```bash
python render_cinematic.py --stills  # fast smoke test, writes work/still_*.jpg
python render_cinematic.py           # ~30-sec, 900-frame video
```

The video is written to `deliverables/Flower_Friends_30_Seconds.mp4`.

## 5. Create new episode
1. Write a 30-second dialogue script, retaining two speaker labels (Max and Mia), and edit `SCRIPT` in `generate_speech.py`.
2. Run `python setup_audio_models.py` once. This downloads model assets (~192 MB in original project).
3. Run `python generate_speech.py` to generate `work/audio.wav` and `work/timeline.json`.
4. Align new character keyframe art and update facial ROIs, shot intervals and phoneme mapping if facial anatomy or spoken phrase count differs.
5. Run `python render_cinematic.py --stills`, inspect mouths, blinks, framing and captions.
6. Run the complete render and verify sound levels, black frames, subtitles, A/V sync, duration and visual artifacts.

**Important**: `render_cinematic.py` currently hardcodes `SHOTS` indices (e.g. timeline row 10), and lists of per-character blink times. When changing script row counts, revise these parts.

## 6. Architecture
```text
Dialogue SCRIPT -> Kokoro ONNX -> work/neural_raw_*.wav
                          |-> phoneme durations -> work/timeline.json
                          v
                     improve_audio.py -> work/audio.wav
Assets keyframes + timeline -> render_cinematic.py -> RGB frames
RGB frames + audio + SRT -> FFmpeg -> deliverables/*.mp4
```

No paid plugin or hosted generation API is needed for this local rendering pipeline; the first-time neural model download needs network access.

## 7. Known limitations and recommendations
The current renderer uses blended still-image facial patches, not full rigged 2D or 3D animation. Mouth masks may reveal seams; hardcoded facial ROIs depend on fixed dimensions; expression interpolation is limited; shot changes are index-based. Future work: landmark-assisted facial positioning, smoother phoneme-to-viseme timing, per-character masks, automated short-form scene format, audio QA tests, a configuration file for ROI/shot control and simple CI smoke tests. Treat rendered output as a prototype pending visual approval.

## 8. Recovery / handoff
Keep all content-addressed original assets with hashes; do not commit secrets or third-party video references. Document external reference sources and licensing. For support, start with `README.md`, this document, `docs/PROJECT_STATUS.md`, and source comments. Commit changes in small increments and preserve working samples.
