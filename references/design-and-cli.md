# Production CLI and editability checks

Load in stage 2 only, after the design gate described in [production-stage.md](production-stage.md). Normal design-stage tasks do not need this file.

## CLI entry point

Use the host's actual Python 3.11+ path. These standard-library commands are read-only, print compact JSON and return 0 on pass, 1 on a blocked/check failure, 2 on invalid input:

```text
python scripts/workflow.py fingerprint project-state.json --slide page-intro
python scripts/workflow.py reconstruct-check project-state.json --slide page-intro
python scripts/workflow.py preflight layout-metrics.json
```

`fingerprint` supplies the current design hashes, not an approval. `reconstruct-check` combines existing outline/current-page checks, file existence, design approval and hashes; run it immediately before dependent reconstruction. The existing `validate_state.py --allow-produce` CLI now delegates to the same design gate. Budget checks still use `validate_state.py --allow-generate`. After an approved design, necessary artwork extraction may use `--purpose artwork` with `--allow-generate`; it requires a valid design and remains counted under the same cap. Default reference generation still stops at the first usable image. Do not use artwork extraction to redesign the approved composition without asking again.

For `preflight`, export measured geometry from the selected backend/renderer to this contract:

```json
{"measurement_source":"actual backend/font measurer and version", "canvas":{"width":1600,"height":900}, "texts":[{"id":"title","box":[40,30,1000,130],"measured_width":900,"measured_height":110}]}
```

Use consistent units, the actual fonts, wrapping and insets; box dimensions mean usable text bounds. Do not label character-count estimates as measured results. Every planned text object must be included. Missing metrics mean preflight unavailable, not a pass. This helper detects measured overflow and out-of-canvas text only, not contrast, line-break quality, collisions or unreported objects. Inspect those visually. Protect names, dates and terms from awkward wrapping with supported no-break controls or intentional breaks.

## Deterministic work, not deterministic art

- Reuse the selected PPT skill's supported CLI/builders. Maintain one per-project build entry accepting a saved scene; do not invent a replacement PPT engine or promise a universal cross-platform renderer.
- Prefer CLI for inventory, hashing, crop coordinates, supported native operations, validation and packaging. Group safe native operations into one application session. Use UI only when needed. Image generation still uses the available authorized image tool; CLI preference does not authorize a paid API switch or new credentials.
- Persist inputs, asset hashes, canvas, fonts and backend version. Cache exact dependencies and rerun only invalidated stages. Never reuse verification after a changed input/PPT hash. Image generation and renderer output are not guaranteed byte-identical; no unsupported token-saving percentages.
- Keep `work/` candidates distinct from `delivery/`; promote only after the existing finalizer, render and evidence checks pass. On failure preserve logs and the last good deliverable. Compact summaries go to conversation; full reports stay in files. Do not repeatedly dump the same source or large tool output.
- Prefer background plus genuinely isolated illustrations. If artwork is merely cropped from a shared source, describe it as separately cropped regions, not isolated objects. Avoid seams or baked-in duplicate text; extraction calls count toward budget.
- Group related labels/nodes where supported and test connector behavior after grouping. Use semantic names. Do not claim label movement follows a node unless verified.
- In a disposable app copy, test longer title, roughly 30% longer body, longer numeric values and a node move; save/reopen and inspect wrapping and attachments. Do not shorten a failing test to make it green. Fix frames or supported fitting, or disclose limits. Fitting adjustments must not change facts or silently make text tiny. Preserve the tested inputs/results. If app access is unavailable, leave these checks pending.
- Check historical/technical imagery for misleading implications, not just text accuracy. Distinguish sourced fact from visual metaphor; label synthetic scenes and revise material misrepresentations before design approval.
