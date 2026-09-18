# Native slide reconstruction

## Source of truth

Before reconstruction, run the image-bound approval gate in [design-and-cli.md](design-and-cli.md). Reuse supported CLI operations for measured text preflight, building and verification; visual inspection remains required. Do not prepare a speculative PPT before the user confirms the design.

For prompt-generated infographics, use the saved pre-generation content for exact wording, values, units, and relationships. Use the inspected generated image for composition, color, hierarchy, and artwork. Correct generated text errors and wrong arrows in the shared scene before export. Track required element IDs through the scene and native slide objects so verification can detect missing content, not only count objects.

For supplied images or SVGs, derive that content inventory from the actual source. When a broken-import screenshot and original SVG are both supplied, recover content from the original and locate visual failures using the screenshot.

## Element mapping

| Source component | Preferred slide object | Required behavior |
| --- | --- | --- |
| Titles, body, metrics, labels | Native text boxes | Direct text editing; explicit font size and position |
| Panels, roof, borders, simple geometry | Native preset or freeform shapes | Independently movable; editable fill and outline |
| Relationship and process arrows | Native connectors or arrow shapes | Preserve direction and endpoint relationship |
| Complex icons, logos, maps | Separate vector image when supported, otherwise isolated raster asset | Move, resize, replace; disclose image-only editability |
| Tables or quantitative charts | Native tables/charts when present and supported | Preserve actual source values and units |

Use native shapes for the requested diagram, not to invent decorative illustrations. Never cover a full-slide screenshot with a handful of text boxes and describe the entire diagram as editable.

SVG paths and cropped pixel traces do not automatically become useful slide objects. Do not turn thousands of scanline paths into thousands of slide shapes. If the user requires every icon to be editable, use a clean native reconstruction or simplified contour geometry and disclose fidelity tradeoffs. Do not rasterize that requirement away.

## Typography and positioning

- Keep a complete editable paragraph in one text box where practical; use intentional line breaks or wrapping rather than one box per rendered line. Separate boxes when the source has genuinely independent labels or distinct positions. Use meaningful object names, and group related components where the backend supports grouping without flattening content.
- Confirm that the chosen font exists and supports the source language. An SVG CSS fallback stack is not a slide font declaration. Set fonts explicitly for native text, including non-Latin text where the library supports it.
- Track source pixels, points, and the library's coordinate units explicitly. Convert once at the rendering boundary. In a 96-DPI CSS coordinate system, 1 px = 0.75 pt = 9525 EMU; verify the authoring API's units rather than assuming all APIs use pixels.
- SVG `y` generally positions a baseline; native text boxes use a rectangular frame with margins. Account for baseline, line height, box insets, and vertical alignment. Do not copy the baseline directly into the box top.
- Translate `text-anchor` into box position plus alignment. Centered text needs a deliberate box width, not only a centered paragraph setting.
- Allocate room for actual wording, bold width, and the target font. Prefer resizing a frame or adding intentional line breaks to shrinking important text until it becomes unreadable.
- Use explicit sizes and sensible overflow settings. Avoid automatic text fitting that produces inconsistent hierarchy. For an optimization request, adjust spacing and alignment without deleting substantive labels or metrics.

## Arrows and effects

Preserve flow direction, including feedback loops and bidirectional relationships. When the authoring library supports attached connectors, use them for relationships expected to remain connected after a user moves a node. Otherwise disclose that independent arrows may need repositioning.

Verify the visible arrow tip against the saved source-to-target relationship after export. Provider names such as head/tail/start/end need not correspond to the intended semantic destination. A structurally valid, attached connector can still point backwards; correct its visible direction and recheck without swapping the intended relationship.

Gradients, shadows, SVG filters, clipping, and `<use>` references have different representations across formats. Translate simple effects natively; simplify nonessential effects when optimizing. Preserve meaningful artwork in an independent asset if its effect cannot be reproduced reliably. Do not promise that flattening references or outlining text guarantees successful SVG-to-shape conversion.

## Compatibility repairs preserve appearance

Ordinary editable PPT means native text/useful diagram objects plus independently replaceable artwork; it does not require zero images. If an icon or illustration fails in the actual exported-PPTX render, inspect the asset and embedding before attributing it to an application version. Record the observed combination of writer, embedding and renderer. Do not infer universal SVG support from a version string alone.

Prefer the selected integration's supported compatible vector embedding or fallback. Otherwise convert the isolated source asset to a transparent PNG at sufficient resolution for its final display size, preserving aspect ratio, silhouette, colors and placement; keep the original. Use an available supported converter, with no automatic installation or extra image-generation request. Cache conversions by source hash, conversion settings and converter version. Rebuild through the selected integration and inspect the new actual PPTX render.

Do not replace semantic icons with numbers, remove arrows or redesign artwork merely to raise native-object counts or pass lint. Full internal editability must be explicitly requested before accepting the associated simplification tradeoff. If no faithful compatible route is available, disclose the limitation instead of calling a degraded design equivalent.

## Verification

Inspect isolated artwork at normal and enlarged view: no opaque crop seams, duplicated text baked into an asset, accidental background patches or clipped meaningful edges. Prefer an existing clean asset, supported mask/transparent extraction or authorized image editing; do not automatically buy another generation or silently simplify required artwork. Preserve original sources and disclose material visual compromises.

Check the final exported artifact, not just the in-memory scene. Use [artifact-checks.md](artifact-checks.md) for reusable package/text checks; a passing report is structural evidence only. Bind render and visual-review evidence to the exact PPTX hash. A successful render command is not a visual pass, and any PPTX change invalidates prior evidence. Follow [delivery-evidence.md](delivery-evidence.md) before final wording; align scene artwork declarations with intentional exported assets:


1. Reopen or import the exported PPTX with available tooling and render every slide. Inspect at readable resolution for overflow, collisions, unwanted wrapping, missing glyphs, broken images, and connectors.
2. Inspect the package or object model. Verify required words exist in native text objects (`a:t` inside shape text bodies in OOXML), with separate shape objects for layout. Counts alone do not prove coverage: compare the reconstructed content with the source inventory.
3. Confirm that no full-slide picture is substituting for required editable content, and that the image-only elements match the declared exceptions.
4. Validate the package and slide dimensions using the available authoring workflow. If actual presentation-app access is available, test opening and a representative text edit in a disposable copy. Otherwise describe only the checks actually performed.
5. Keep original sources unchanged. Use a new final filename for revisions, and do not deliver an unvalidated intermediate as the finished result.

For a newly adopted backend, test a longer paragraph replacement, node move, and save/reopen in a disposable copy when application access is available; verify wrapping and connector attachment after reopening. Otherwise inspect paragraph grouping and encoded connector endpoints without claiming application testing. See [release-checks.md](release-checks.md) for the detailed acceptance procedure. Distinguish source typos from our transcription errors; do not silently rewrite readable supplied content in a faithful reconstruction.

No guarantee of identical rendering on an untested system: disclose specific known font or renderer differences when they affect use, rather than adding generic warnings.
