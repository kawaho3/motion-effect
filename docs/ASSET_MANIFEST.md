# Original file inventory and reproducibility

The original `Flower_Friends_Editable_Project.zip` included 29 entries under `Flower_Friends_Project/`. Important inputs:

| Path | Purpose |
|---|---|
| `assets/Garden_Base.png` | Base aligned image, 1672×941 |
| `assets/Garden_Ah_Blink.png` | Open-mouth blink aligned image |
| `assets/Garden_Oh.png` | Rounded-mouth aligned image |
| `assets/DejaVuSans-Bold.ttf` | Caption font |
| `assets/DejaVu_Font_License.txt` | Font license |
| `work/audio.wav` | 30-second mixed audio |
| `work/timeline.json` | Dialogue and phoneme timing |
| `work/neural_raw_00.wav` .. `work/neural_raw_11.wav` | Per-line synthesized speech |
| `work/audio_report.json` | Source-run audio measurements |
| `work/encoded_audio_qa.json` | Final encoded audio measurements |
| `deliverables/Flower_Friends_Script.txt` | Script |
| `deliverables/Flower_Friends_Cinematic_Subtitles.srt` | Captions |

The repository already includes smaller JPEG keyframes and an MP3 voice track for direct rendering. To use original quality, or if required binary assets are absent from your clone, extract the original ZIP into your working tree, keeping the path names above. Avoid committing large encoded final MP4 artifacts directly to Git; use GitHub Releases or Git LFS if repository policy allows.

## Reusing character assets
The facial region rectangles in `render_cinematic.py` assume exact 1672×941 coordinates; new art demands updated ROI bounding boxes. The three expression plates should all be generated from the *same* base scene so every pixel except the mouth/eye region remains aligned.

## Voice and model licences
The project uses Kokoro ONNX with external model assets downloaded by `setup_audio_models.py`; check the upstream project's current license terms before distribution. Included DejaVu font is subject to its accompanying license; always preserve that file when distributing the font.
