# Faithful reconstruction contract

Use during production after a design is selected. The CLI compares recorded source and plan data; it cannot discover omitted image elements, authenticate user intent or judge pixel similarity. An actual source-to-render visual comparison remains required. Do not lower fidelity to increase native-object counts.

## Inventory and lock

Inspect the selected image, not only the prompt. Save `design/page-01-source.json` with `image_sha256`, the source-pixel `canvas` (`width`, `height`) and `elements`. Include background, all visible text (also secondary/generated captions and text inside artwork), connectors, illustrations, decoration and effects. Each element has a stable `id`, a `kind` (`text`, `connector`, `artwork`, `background`, `shape`) and `properties`:

- All elements: source-pixel `bounds: [x,y,width,height]`. Record additional visible properties needed to preserve appearance: colors, typography, line breaks, proportions, layer order, texture and effects.
- Text: exact `text`, including original line breaks. Do not substitute the pre-generation copy. Record unreadable source text as unresolved rather than guessing.
- Connectors: `from` and `to` are inventory element IDs; `route` records the visible straight/curved path or control points; `arrowheads` records the visible ends. Free endpoints may use inventoried anchor shapes. Record apparent source mistakes as observations, not fixes.
- Artwork/background: describe the exact source region and appearance. A detail can remain a replaceable image if clean native reproduction is impractical.

Create `work/page-01-plan.json` by copying the inventory's `canvas` and `elements` unchanged, then add `source_sha256` and `changes: []`. This records the intended appearance, not backend coordinates: keep source pixels here and convert only in the builder. Keep output object IDs and actual asset paths in a separate mapping, so native/raster implementation choices do not look like design changes.

Add to the slide's project state:

```json
{"reconstruction":{"source":"design/page-01-source.json","source_sha256":"<actual SHA-256 of that file>","plan":"work/page-01-plan.json"}}
```

This source lock is not a user approval. Do not ask for another confirmation just to record an already selected source. Freeze it before authoring; do not rewrite it to match the produced slide. For an actual transcription mistake in the inventory, re-inspect the image, record the correction evidence and relock/recheck the plan. An intentional source-design change uses the scoped authorization below or a newly selected source.

## Explicit changes only

Default `changes` is empty. “Yes”, “continue”, “optimize” and approving the design are not instructions to apply an assistant's proposed corrections. Do not infer authorization from commentary or a source concern. An explicit user instruction, or confirmation of an exact displayed before/after change, can authorize only that change. Record its real message and exact scope:

```json
{"element_id":"caption","before":{"id":"caption","kind":"text","properties":{"bounds":[20,20,300,40],"text":"原文"}},"after":{"id":"caption","kind":"text","properties":{"bounds":[20,20,300,40],"text":"用户指定的新文字"}},"authorization":{"kind":"explicit_change_request","user_text":"把‘原文’改为‘用户指定的新文字’","evidence":"actual user message ID or timestamp"}}
```

For deletion, `after` is null; for addition, `before` is null. Preserve every other property. Changes never inherit the design approval. Never fill an explicit-change record merely to bypass the CLI. Source observations belong in work notes and do not block faithful copying.

```text
python scripts/workflow.py fidelity-check project-state.json --slide page-intro
python scripts/workflow.py reconstruct-check project-state.json --slide page-intro
```

The standalone check prints source/image/plan fingerprints. Both commands reject missing/stale inventories, lost backgrounds, changed wording, geometry, arrow routes or decorations without exact scoped change records. This is declaration checking, not automatic image understanding.

## Delivery comparison

Compare the actual exported PPT render with the selected source, element by element. Check text, paths, relative sizes, layout, artwork details, background and decoration. Restore unintended differences; do not relabel them “optimizations”. Preserve visible features as artwork when needed and disclose editing limits.

Alongside each existing page `visual_review`, record a separate `source_comparison` with `status: "passed"`, the three fingerprints returned by `fidelity-check`, that actual `preview_sha256`, `reviewer`, `reviewed_at` and concrete comparison `evidence`. Do not mark passed for “looks good” or successful rendering alone. Any changed source, plan or PPT/preview requires a fresh comparison.

```text
python scripts/check_delivery.py output.pptx --requirements required-text.json --scene scene.json --state project-state.json --evidence render-evidence.json
```

The delivery CLI requires state for the delivered slides in the same order, rechecks fidelity, checks source-plan text against native paragraphs and requires a source-bound comparison record. A legacy delivery missing these records is a draft, not evidence of source fidelity. No bypass flag generates a comparison or grants approval.
