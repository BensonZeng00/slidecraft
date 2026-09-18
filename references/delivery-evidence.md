# Discovery and delivery evidence

Use these standard-library Python 3.11+ helpers with the host's configured interpreter. They do not install software, invoke a vendor backend, render slides, or inspect images. A host-only environment applies the same checks through available tools.

## Renderer discovery

```text
python scripts/renderer_probe.py
python scripts/renderer_probe.py --candidate /known/path/to/renderer
```

Windows checks PowerPoint COM registration in both registry views and targeted executable paths; macOS checks application paths; all platforms check LibreOffice command discovery and explicit candidate files. It never starts applications. Results are `detected_not_tested` or `not_detected`, with evidence. The search is bounded and cannot prove absence. Host render services are discovered separately through their tools/skills.

Do not say "not installed" because PATH search, one CLI command or COM activation failed. Record actual later invocation results as `succeeded`, `failed` or `permission_blocked`, with the error. Registered/present is different from callable. Historical successful renders justify a focused recheck, not an assumption of present availability. If one renderer fails, assess an already available supported alternative within the existing retry budget. Do not modify the host SDK or silently install another renderer.

## Reconcile artwork and evidence

After export, update the scene's `image_only_assets` from the real object mapping, preserving semantic roles. Each embedded source/fallback part is listed once per slide; one SVG plus its PNG fallback needs two part records, not a claim of two separate visible icons:

```json
{"image_only_assets": [{"slide": 1, "part": "ppt/media/image1.svg", "role": "timeline direction arrow"}]}
```

Use the package paths reported in `media_parts` by `check_pptx.py`. Preserve other scene fields. An empty array declares no embedded artwork. Do not silently change the declared design to match an erroneous export: repair the export or explain the intentional asset change first. This comparison checks image references, not semantic equivalence or artwork visibility. Images inherited from masters, external resources and complex unsupported object types still need actual visual inspection. Content verification uses the scene-derived required-text inventory; do not derive expected text from the output itself.

Record actual render operations and actual visual review in `render-evidence.json`. Never fill this template with invented observations or mark review passed merely to unlock delivery:

```json
{
  "pptx_sha256": "<hash of the exported PPTX actually rendered>",
  "renderer": {"name": "<actual renderer>", "version": "<reported version or unknown>", "operation_evidence": "<actual export log/tool result reference>"},
  "pages": [{
    "slide": 1,
    "render_status": "succeeded",
    "preview": "render/slide-01.png",
    "preview_sha256": "<actual preview hash>",
    "visual_review": {"status": "passed", "preview_sha256": "<same inspected preview hash>", "reviewer": "<agent or user>", "reviewed_at": "<actual time>", "evidence": "<actual viewing tool result or user message and observations>"}
  }]
}
```

Preview paths are relative to the evidence file's directory and must stay within it. Record all slides. Missing review remains missing or pending; failed render remains failed. Preserve actual errors and existing useful files. User page approval is separate from an agent visual-review record and still follows the multi-slide gate.

```text
python scripts/check_delivery.py /project/output.pptx --requirements /project/required-text.json --scene /project/scene.json --state /project/project-state.json --evidence /project/render-evidence.json
```

Also record each page's `source_comparison` as defined in [fidelity-contract.md](fidelity-contract.md). A successful render and generic visual review do not establish source fidelity. `--state` is required, with the same ordered pages as the delivered PPTX. It binds the selected images, locked inventories and planned changes to the actual comparison records, and checks exact native text and duplicate/additional labels against the source-derived plan.

Omit `--evidence` when none exists: the command reports `draft`. It rechecks the current PPTX and content inventory instead of trusting an old structural report, compares scene artwork, checks matching PPTX/preview hashes and per-page render/review records. Exit codes: 0 = evidence consistent and complete; 1 = draft with issues; 2 = invalid input. JSON always goes to stdout; the command does not modify inputs or project state. Legacy evidence remains historical until the missing source comparison is actually performed; never manufacture it.

`evidence_complete` means records are consistent, not that this script viewed images or authenticated claims. It cannot prove that a preview was actually rendered from that PPTX: the producing agent must record the real operation faithfully. A byte-identical PPTX may still require re-review after a meaningful content-plan change. Never fabricate records to silence a check.

## Delivery language

- When evidence is missing, stale or failed: lead with "Editable draft; visual verification incomplete" and state the specific remaining check. Do not lead with "completed/verified" and retract it in a disclaimer.
- When records are complete AND actual agent visual inspection passed: deliver the checked PPTX and its actual previews, accurately describing the checks performed.
- Use actual object/artwork findings. Embedded artwork means "native text and shapes plus independently replaceable artwork", not "all native/zero images". Absence of image parts alone does not prove every object internally editable.
- A host preview counts only if the agent actually inspects it and establishes that it represents this exported PPTX, not the source DSL or reference image. Asking the user to inspect a preview is a handoff of remaining work, not completed agent verification.
