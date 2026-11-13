> Historical documentation imported from `kawaho3/background` on 2026-11-13. Any original repository references below are historical; use `motion-effect` root README and `docs/PROJECT_GUIDE.md` for current instructions.

# Test criteria and validation

## Foreground quality
- Character (face, hands, feet, hair and moving clothing) remains complete every frame.
- Empty scene behind and between arms/legs is transparent; alpha channel is real.
- Scrub fast motion and compare consecutive frames for flicker, outline/halo and disappearing pieces.
- Composite over both solid white and solid black to detect contamination.
- Overlay source and output time-aligned frames to verify movement and speed.

## Sound and metadata
~~~bash
ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1 output.webm
ffprobe -v error -select_streams a -show_entries stream=index -of csv=p=0 output.webm
ffprobe -v error -select_streams v -show_entries stream=codec_name,pix_fmt,avg_frame_rate -of json output.webm
~~~
The audio-stream query should return **no rows**. Some alpha-capable VP9 files can report a normal-looking pixel format to FFprobe or lose alpha in unsupported decoders; test in a compatible editor with a contrasting background. A checkerboard visible in ordinary pixels is **not** transparent.

## Local tests
~~~bash
python -m unittest discover -s tests -v
python scripts/extract_character.py source.mp4 output.webm
python scripts/extract_character.py source.mp4 output.mov
~~~

A successful command and three passing unit tests do **not** prove visual quality; capture actual output and a QC report before changing STATUS.md.
