> Historical documentation imported from `kawaho3/background` on 2026-11-13. Any original repository references below are historical; use `motion-effect` root README and `docs/PROJECT_GUIDE.md` for current instructions.

# Technical architecture

## Current baseline (new code, not original historical pipeline)

~~~text
Video source -> FFprobe rate -> FFmpeg RGB PNG frames
       -> rembg / local U2Net image segmentation on each frame
       -> RGBA PNG frame sequence
       -> FFmpeg VP9 yuva420p .webm OR qtrle argb .mov, -an (silent)
~~~

Entry point: scripts/extract_character.py. It creates frames in a temporary directory; --keep-frames stores RGBA PNGs. First use downloads a segmentation model. Everything after installation runs locally. Video is reassembled at the nominal average frame rate; **VFR timestamps are not fully preserved**. Independent matting may flicker and miss hair or fast limbs. No full end-to-end validation on the historic sample yet.

~~~bash
python scripts/extract_character.py source.mp4 output.webm --model u2net
python scripts/extract_character.py source.mp4 output.mov --keep-frames output/rgba
~~~

## Planned architecture (not built)

1. Decode with timestamp/color metadata and user target selection.
2. Segment person/character with a video-aware temporal model, not independent frames.
3. Track foreground and recover detail across motion, fast limbs and occlusions.
4. Allow manually corrected keyframes with propagation and caching.
5. Encode truly transparent silent WebM/MOV/PNG with verified source timing.
6. Run quality gates for frame count, duration, audio count, alpha, edge stability and cross-editor support.
7. Add a GUI, optional GPU acceleration and batch/recovery with safe logs.

Keep model downloads and large frame/video artifacts outside the repository.
