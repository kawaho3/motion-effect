> Historical documentation imported from `kawaho3/background` on 2026-11-13. Any original repository references below are historical; use `motion-effect` root README and `docs/PROJECT_GUIDE.md` for current instructions.

# Historical media: independently verified stream evidence

Inspection date: 2026-11-13. This is factual metadata from files recovered from the project Library, **not a claim that those files were uploaded to GitHub or recreated by the baseline extractor**.

| Source/output | File bytes | SHA-256 | Video | FPS / frames | Duration | Audio |
| --- | ---: | --- | --- | --- | --- | --- |
| Original `viggle-d6d871ba-48aa-4575-b0d0-b6b6ecbb3542.mp4` | 4,382,229 | `cff35b1301a90f5d02f337c9949ce9fad13836ce003ab3c4a54ffc9c90aee5c3` | H.264, 576×1024, yuv420p | 25 / 485 | 19.4 s | AAC present |
| `Character_Transparent_Silent.webm` | 41,829,950 | `da5f103ab524ab6e8886276d029fccb2c8826e776bc1e41c0a4bbed11d482474` | VP9, 576×1024, `ALPHA_MODE=1` | 25 / 485 | 19.4 s | None |
| `Character_Transparent_Silent.mov` | 125,601,383 | `fd7402d13ba364fec0e3b40adfd53e68d59ff4d528691b784d62a812eef8187d` | ProRes 4444 with alpha, 576×1024, `yuva444p12le` decoded | 25 / 485 | 19.4 s | None |

## Verified transparency

Using FFmpeg to decode **three RGBA frames per output** at approximately 0 s, 9.7 s, and 19.32 s showed alpha values spanning **0–255** for both exported videos.

| Output | 0 s: fraction of pixels not fully opaque | 9.7 s | ~19.32 s |
| --- | ---: | ---: | ---: |
| WebM | 0.877540 | 0.810106 | 0.768960 |
| MOV | 0.877540 | 0.810106 | 0.768960 |

Both exports have **0 audio streams**. `ffprobe -count_frames` confirmed 485 video frames in the original and each output. This is strong evidence that the existing files are genuinely silent and alpha-bearing and share nominal duration, dimensions and frame counts. **It does not prove perfect matting on all frames or the exact similarity of all gestures**; visual frame-by-frame review is still required. The full original frames are not embedded here.

## Repeat these checks locally

~~~bash
python scripts/verify_export.py Character_Transparent_Silent.webm Character_Transparent_Silent.mov --strict --json output/historical_checks.json
ffprobe -v error -select_streams v:0 -count_frames -show_entries stream=nb_read_frames -of csv=p=0 Character_Transparent_Silent.mov
~~~

The `--strict` mode checks sampled-frame alpha and stream silence. It does NOT create the missing historical matting algorithm.

## Reproducing the same MOV format with the new code

Use `python scripts/extract_character.py source.mp4 output.mov` (default `--mov-codec prores`). This chooses ProRes 4444 alpha encoding, but **the matte is still generated with a different baseline model**. Exact visual equivalence has not been established.

## Provenance / licensing

These binaries were supplied or created in private project work. Permission to **view/process for this project** is not proof of permission to **redistribute publicly**. Do not put them in GitHub Releases, Git LFS or commits until distribution rights are confirmed. The MOV is >100 MB and is not a normal GitHub contents-file candidate regardless.