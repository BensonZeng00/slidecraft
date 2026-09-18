# Backend-neutral artifact checks

Use these helpers when Python 3.11+ is available. Use the actual host interpreter (including the user's configured environment); no third-party dependencies or PPT backend are needed. Otherwise perform the equivalent checks with available tooling. Scripts neither build nor render PPTX and do not call image providers or alter project approval state.

```text
python scripts/check_pptx.py /project/output.pptx --requirements /project/required-text.json --output /project/native-check.json
python scripts/check_pptx.py /project/output.pptx --check-report /project/native-check.json
```

The inventory follows actual presentation order, one entry per slide:

```json
{"slides": [{"required_text": ["AI 发展史", "图灵测试（1950）"]}]}
```

Generate the inventory from the saved content plan, not by extracting the produced PPTX and using it as its own expected result. Each required string must occur within one native paragraph; split runs are joined, unrelated paragraphs are not. Express intentional paragraph breaks as separate strings. Tables with native text bodies are included; text inside images or chart caches does not count as editable slide text. This checks presence, not factual accuracy, occurrence counts or exact element-ID mapping. Review those against the scene separately.

The JSON report includes ordered slides, native paragraphs, shape/picture counts, dimensions, missing text/relationship targets, SVG inventory and exact PPTX hash. A structural pass is NOT full OOXML validation, usable-editing proof or a visual pass. External resources are reported, never fetched. SVG presence is a warning to inspect rendering, not a verdict on compatibility. No full-slide flattening claim is inferred from object counts.

`--check-report` only checks whether the input PPTX matches the saved hash. It does not authenticate the report, inspect previews, prove human approval or check whether the content plan changed. When the scene changes rerun with the new inventory; when the PPTX changes, rerun both structural and actual rendering/visual checks. Keep preview hashes and renderer evidence in project state separately. The helper always reports `visual_verified: false`.

Exit codes: 0 = selected check passed; 1 = structural/content failure or changed PPTX; 2 = invalid inputs or unreadable package. Without `--requirements`, `coverage_checked` is false: inspection alone is not content verification. Reports are UTF-8. Output paths must differ from inputs. Source PPTX remains unchanged.

For read-only renderer discovery, scene/artwork reconciliation and file-bound delivery evidence, follow [delivery-evidence.md](delivery-evidence.md). `check_delivery.py` reruns the structural check with the current inventory instead of trusting stale reports.

Keep backend-specific authoring, lint and rendering in the chosen PPT skill/plugin. Reuse these checks and `validate_state.py` instead of writing task-specific ZIP/text scripts. Asset conversion uses an available supported converter; this helper does not install one, rasterize a slide or replace semantic artwork.
