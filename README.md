# Motion Effect — Flower Friends

A reproducible local Python pipeline for a 30-second illustrated flower lesson using still-image facial animation, timed dialogue, subtitles and post-processed audio.

> **Project status:** The original editable Flower Friends project has been recovered from the ChatGPT project Library. This repository is being assembled from those files; see `docs/PROJECT_STATUS.md` for verified and pending items.

## Quick start

Install Python, FFmpeg and the dependencies:

```bash
python -m pip install -r requirements.txt
python render_cinematic.py
```

This render uses the checked-in artwork, processed audio and timing data; no model download or paid API call is needed.

To synthesize new dialogue locally, edit `SCRIPT` in `generate_speech.py`, then run:

```bash
python setup_audio_models.py
python generate_speech.py
python render_cinematic.py
```

See `docs/DEVELOPER_HANDOFF.md` for architecture, setup, editing instructions, testing and exact asset expectations.
