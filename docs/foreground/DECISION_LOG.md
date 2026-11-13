> Historical documentation imported from `kawaho3/background` on 2026-11-13. Any original repository references below are historical; use `motion-effect` root README and `docs/PROJECT_GUIDE.md` for current instructions.

# Decision log

| Date | Decision | Why | Next follow-up |
| --- | --- | --- | --- |
| 2026-11-11 | Goal defined as full-character foreground motion with no background and no sound | Original user request | Validate as RGBA export, not backdrop substitution |
| 2026-11-13 | Make `kawaho3/background` the public documentation and development hub | New contributors need independence from previous chats | Keep README and reproducible examples current |
| 2026-11-13 | Prefer free local Python/FFmpeg/model inference; avoid paid APIs/plugins | Owner's credit constraint | Measure local performance and document model license |
| 2026-11-13 | Do not describe rembg baseline as the recovered production pipeline | Original historical code is unavailable | Add temporal matting and regression benchmark |
| 2026-11-13 | Use ProRes 4444 as default alpha MOV encoding | Recovered historical MOV is ProRes with alpha | Verify editor support across target OS |
| 2026-11-13 | Add a fully synthetic source and reference movie generator | Public repo cannot safely depend on original clip | Add rights-cleared integrated quality test |
| 2026-11-13 | Hold original source and large renders from public Git pending rights review | Original clip/characters and asset licenses unverified; MOV >100MB | Owner to decide licenses and asset distribution |

## Open decisions

- Intended legal license for this repository's code and contributions.
- Can historical media be redistributed to external developers publicly?
- First target OS/editor and minimum acceptable visual quality.
- Preferred temporal matting model after local benchmarking and license audit.
- Approved storage path and cost ceiling for large output artifacts.

No decision in this table implies that a planned feature is already implemented.