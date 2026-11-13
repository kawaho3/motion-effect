> Historical documentation imported from `kawaho3/background` on 2026-11-13. Any original repository references below are historical; use `motion-effect` root README and `docs/PROJECT_GUIDE.md` for current instructions.

# Developer setup — new machine / no previous chat needed

## Dependencies

- Git, Python and a virtual environment. Use a currently supported Python version compatible with the installed rembg release.
- `ffmpeg` and `ffprobe` available on `PATH` (on Windows, test both in PowerShell).
- Internet **only for installing dependencies and first free model download**. No paid API, cloud account or plugin required.

## Clone and smoke-test without a model download

~~~bash
git clone https://github.com/kawaho3/background.git
cd background
python -m venv .venv
# Windows PowerShell: .\.venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python scripts/make_demo.py --output-dir output/synthetic-demo
python scripts/verify_export.py output/synthetic-demo/synthetic_reference_alpha.mov --strict
~~~

The synthetic test draws simple shapes, creates a moving character over a synthetic background, exports a source MP4 and a transparent reference MOV, and then probes the reference. **No original Viggle clip or private asset is necessary.**

## Try the extraction baseline

~~~bash
python scripts/extract_character.py output/synthetic-demo/synthetic_source.mp4 output/from_model.webm
python scripts/verify_export.py output/from_model.webm --strict --json output/model_check.json
python scripts/extract_character.py output/synthetic-demo/synthetic_source.mp4 output/from_model.mov
python scripts/verify_export.py output/from_model.mov --strict
~~~

The first extraction command may download the open model once. This is a **qualitative baseline**, not a benchmark of flawless segmentation. The synthetic ground truth is for inspection and comparison.

## Windows troubleshooting

- `python` may be `py`; use `py -m venv .venv` if necessary.
- If `Activate.ps1` is blocked by policy, use `cmd.exe` activation (`.venv\Scripts\activate.bat`) or run `.venv\Scripts\python.exe` directly.
- Install FFmpeg via your standard package manager, then restart the terminal and run `ffmpeg -version` and `ffprobe -version`.
- Run scripts from repository root so file paths are predictable.
- File names with spaces are safe when shell-quoted.
- Close editors before overwriting output MOV/WebM files.

## Technical caveats

- VP9 alpha can be hidden in players without alpha-aware decoders; inspect against contrasting layers in an editor or use ProRes MOV.
- ProRes alpha MOVs can be large. Estimate disk space before running on long clips.
- Current baseline reassembles at nominal average FPS, not exact timestamp-aware VFR timing.
- The first model may be CPU-intensive and slow; do not publish a performance number without recording hardware.
- Font files, original artwork, speech models, and the large flower-project archive are not prerequisites for character extraction.