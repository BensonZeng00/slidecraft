# Stage 2 — approved design to editable PPT

Read after explicit design confirmation, or a request to reconstruct an identified supplied source. For that source route, inspect it, freeze its brief and record the actual request as approval for the exact file; no new image is needed. Use [design-stage.md](design-stage.md) only if the approval record schema is not already known. Missing approval returns to stage 1; never fabricate retrospective approval from a completed PPT.

First record the selected-image inventory and identical reconstruction plan using the [fidelity contract](fidelity-contract.md). This is read-only source inspection and needs no additional user confirmation. Legacy projects need this inventory, not invented approval or an output-derived baseline. Before extraction or authoring run:

```text
python scripts/workflow.py reconstruct-check project-state.json --slide page-intro
```

The gate checks outline/page progression, design revision, image/brief hashes, approval fields, the locked source inventory and unauthorized plan changes. The existing `validate_state.py --allow-produce` CLI delegates to it. Without Python perform equivalent host checks. Failed/stale approval stops dependent work. Missing fidelity records require source inspection; they do not justify re-asking approval for an unchanged source. Design approval is not rendered-quality or change-authorization evidence.

## Load in execution order

1. Read [runtime-adaptation.md](runtime-adaptation.md). Respect explicit provider choice; otherwise reuse a verified project integration, then suitable installed PPT skills/plugins, then exposed native tools. Read selected backend instructions before invoking it. Only missing capability routes to [platform-installation.md](platform-installation.md); failed/unavailable installation means notify and pause, not a generic-library fallback.
2. Read [design-and-cli.md](design-and-cli.md) for deterministic construction, text preflight and stress edits, and [native-pptx.md](native-pptx.md) for faithful mapping. Preserve approved composition using native text/shapes/connectors and disclosed artwork. Read [svg.md](svg.md) only for SVG-specific work; SVG is not a mandatory bridge.
3. At export, read [artifact-checks.md](artifact-checks.md) and [delivery-evidence.md](delivery-evidence.md). Expected content comes from the scene, never the output as its own answer key. Inspect actual PPT renders and bind review/checks to file hashes. Changed PPT invalidates checks; missing rendering means an explicitly unverified draft.

Keep native/render checks separate from user approval. Deliver PPT, actual preview and generated reference clearly labeled; disclose image-only artwork and editing limits. Keep build logs/scenes private unless requested. For decks, obtain finished-page approval before any next-page work, then assemble one ordered final deck after all pages are approved.
