# Flower Friends — cinematic revision

This replaces the rejected flat cartoon with detailed, warmly lit, 3D-looking still artwork. Two friends in a greenhouse teach **rose**, **sunflower**, and **tulip** through a 30-second conversation.

## What changed

- Three aligned, detailed image keyframes supply the original scene, speaking lips, and closed eyelids. The artwork was created with the built-in image tool using the uploaded reference as a visual-style reference.
- Local Python compositing supplies speech-timed mouth changes, quick blinks, very small head drift, a slow camera push, and conversational close-ups.
- White subtitles with dark outlines follow the reference's presentation.
- The old Flite voices were replaced with Kokoro neural voices: `af_heart` for Mia and `am_puck` for Max, generated locally on CPU.
- A new custom Python DSP pipeline improves voice balance and mixing. No external speech-generation or video-generation API is used.

This remains limited facial animation over a still scene. It does not reproduce full 3D head turns, hand gestures, or every motion in the reference. The voice model is an existing open model; the audio processing, timing, mixing, and animation scripts are custom code.

## Audio processing

`improve_audio.py` is a reusable standalone script. It performs DC removal, a gentle low-frequency cut, small parametric-EQ corrections, adaptive sibilance reduction, soft-knee compression, loudness matching, click-prevention fades, speech-driven music ducking, and a four-times-oversampled peak check. It preserves speech duration and does not use pitch-shifting to imitate character voices.

The finished 48 kHz stereo master measures −16.5 LUFS integrated and approximately −1.60 dBTP, with zero clipped samples before AAC encoding. The audio report is included under `work/`.

```sh
python -m pip install -r requirements.txt
python improve_audio.py input_voice.wav polished_voice.wav
python improve_audio.py input_voice.wav polished_mix.wav --music background.wav
```

Improving EQ or loudness cannot turn a poor synthetic voice into a natural human performance. The replacement neural synthesis is the primary improvement; the custom processing polishes it. Clean synthetic speech is not subjected to destructive noise reduction.

## Re-render the exact video

The archive includes the finished audio, phoneme timings, image assets, subtitles, and font. Install the Python requirements and have FFmpeg available on `PATH`, then run:

```sh
python render_cinematic.py
```

For newly generated dialogue, edit `SCRIPT` in `generate_speech.py`. Download the models once (about 192 MB combined), then synthesize and render:

```sh
python setup_audio_models.py
python generate_speech.py
python render_cinematic.py
```

The model files are not duplicated in this archive. Their download URLs and verified SHA-256 hashes are in `setup_audio_models.py`. The original generated voice clips are included in `work/` for inspection or further processing. No API key is required for local speech inference.

## Sources and dependencies

- Kokoro ONNX: https://github.com/thewh1teagle/kokoro-onnx
- Model release: https://github.com/thewh1teagle/kokoro-onnx/releases/tag/model-files-v1.1
- Voice descriptions: https://huggingface.co/hexgrad/Kokoro-82M/blob/main/VOICES.md
- Kokoro model: Apache 2.0. Kokoro ONNX wrapper: MIT. The included DejaVu font license is beside the font.

## Image-generation directions used

Base scene: a warm cinematic animated-film still in a lush florist greenhouse, with a dark-haired young adult man on the left in a cream hoodie and a chestnut-haired young adult woman on the right in a sage cardigan. Both have richly shaded faces, clear eyes and lips, detailed hair and fabric, and closed-mouth smiles. Three separate pots contain a red rose, a yellow sunflower, and a pink tulip. Use the supplied video frame as a style reference; no text or panels.

Expression edit 1: keep the image aligned and unchanged except for both characters' naturally closed blinking eyes and subtly open 'ah' mouths.

Expression edit 2: keep the image aligned and unchanged except for small rounded 'oo/oh' lips, with eyes open.

Full rendered videos and the original reference footage are not duplicated in the project archive.