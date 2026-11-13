> Historical documentation imported from `kawaho3/background` on 2026-11-13. Any original repository references below are historical; use `motion-effect` root README and `docs/PROJECT_GUIDE.md` for current instructions.

# Asset provenance and getting a complete working copy

**What is in Git:** source Python, unit tests, a generator for a redistributable synthetic fixture, verification scripts, documentation, and recovered *text source* for the Flower Friends example.

**What is not in Git:** the original Viggle reference, historical transparent WebM and MOV, the completed Flower Friends MP4/WAV, aligned art PNGs, original voice WAV clips, fonts, external model files and the editable ZIP. Their hashes and filenames are documented in `VERIFIED_MEDIA.md` and `ASSET_MANIFEST.md`.

## Why binaries are not automatically public

The repository is **public**. User-provided source and Viggle-generated character footage may incorporate characters, likenesses, or third-party rights we have not audited. The owner authorized a technical handoff, but media redistribution rights remain unverified. Even if rights are cleared, the historical transparent MOV is over 100 MB. GitHub does not accept that through ordinary file contents commits; LFS and Release assets have quota/cost/permission considerations.

The Flower Friends editable ZIP contains an open-font binary and generated art/voices. This repo does not distribute font binaries or the full archive; developers can reconstruct it from the owner's archive using `examples/flower-friends/restore_assets.py`, after any needed permissions check. The original ZIP hash is recorded here for integrity:

`Flower_Friends_Editable_Project.zip` (17,963,654 bytes)
SHA-256: `0b814dd830d5e37e2c898dd5283e137504c2b4b0599b6f14cc56b0c5c0adbcbe`

## Developer with no chat history

1. Build and test the synthetic demo locally: `python scripts/make_demo.py`; no external original needed.
2. For the specific historical clip, request **licensed access** from repository maintainers, then compare `sha256sum` (or Windows `Get-FileHash`) against `VERIFIED_MEDIA.md`.
3. Keep all non-released binaries under `input/`, `output/` or other ignored directories.
4. Only after the rights audit and owner selection of an artifact storage method, publish the appropriate assets with checksums and documented limits.
5. If inspecting the Flower Friends archive, use the optional restore helper in the example directory and keep the complete archive private.

## Recovery conditions

No original foreground extractor implementation was found in the available source files. The current repo includes a **new, independent** script. Do not claim to reproduce the historical exact result without an end-to-end comparison.