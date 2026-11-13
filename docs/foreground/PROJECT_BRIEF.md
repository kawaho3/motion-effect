> Historical documentation imported from `kawaho3/background` on 2026-11-13. Any original repository references below are historical; use `motion-effect` root README and `docs/PROJECT_GUIDE.md` for current instructions.

# Product brief

## Primary user request

From the supplied animated video (original example: viggle-d6d871ba-48aa-4575-b0d0-b6b6ecbb3542.mp4), **extract the complete character and all movement as video, with no background and no sound**.

### Definition of done
1. Retain complete subject, body motion, poses and timeline; no cropping of limbs or accessories.
2. All background and empty spaces become true alpha, not a colored substitute or baked checkerboard.
3. Stable hair/fingers/motion-blurred edges, no distracting halos or flicker.
4. Silent transparent .webm and/or .mov output, plus optional RGBA PNG sequence.
5. Verify output composites correctly against white AND black backgrounds and contains no audio stream.
6. Every reproduction has command, dependency list, sample permission, test results and known limitations.

### Constraints
Use available local/open tools, Python and FFmpeg. No paid plugins, APIs or recurring credit use; download a free model once if needed. Produce practical scripts and instructions that another developer can run independently. Prefer accuracy over attractive mockups. A lightweight preview must never be mislabeled final-quality extraction.

### Potential future product
Reliable temporal video matting, manual frame fixes, preservation of variable timestamps, batch processing, resume/recovery, editor-friendly exports, cross-platform GUI and optional GPU acceleration. These are **planned**, not implemented.
