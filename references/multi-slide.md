# Multi-slide presentation mode

Use for a topic or outline that needs a complete presentation, several source images to combine as a deck, or an explicit request to split one dense source across slides. Reuse the main skill's platform discovery/install route and stopping rule. Do not add a standalone PPT backend merely to obtain multi-slide support.

Recommend single-slide mode (one prompt produces one editable slide) for focused quality control. When the user selects a multi-slide deck, respect that choice and use sequential, user-confirmed production. Overall planning may cover all pages; actual image generation, slide construction, and rendering must be limited to the current page until it is approved.

## Establish the deck contract

Determine the audience, purpose, language, required topics, total slide count, source order, canvas, and visual direction. A request for N slides means N total, including covers and closing pages. Add a cover, agenda, summary, or appendix only when it serves the request and fits the total; none is mandatory.

If the user requests multiple pages without a count, propose a content-appropriate count for discussion. Respect a requested presentation duration when estimating density. All multi-slide requests require the outline confirmation below before page production; having a specified count or a supplied outline does not remove this gate.

## Discuss and confirm the outline first

1. Reuse known requirements and ask only about meaningful gaps: audience, purpose, essential content, source order, length and requested style. Offer a concrete draft so the user can revise it instead of starting with an unnecessary questionnaire.
2. Present the total page count and an ordered page-by-page outline. For every page include its title, purpose/takeaway and substantive content or key points; list needed facts/materials and source-image mapping where relevant. Headings alone are insufficient. Discuss the shared visual direction without fixing unnecessary geometry or restricting the image model's composition. Explain planned reference-image count and retry allowance before spending on generation.
3. Invite changes, revise the draft, then ask for explicit confirmation of the displayed outline and each page's content. For example: "以上是 6 页大纲及每页内容，请确认或提出修改；确认后我再制作第 1 页。" Stop at this gate. Read-only source inspection, capability discovery and plan edits may continue, but no page images, PPT objects, rendering or delegated production starts before confirmation.
4. Record approval for the reviewed plan revision. User edits without approval, silence, resuming the task, tool success and the original deck request are not approval. If the user supplied and explicitly approved this exact detailed plan already, reuse that evidence rather than asking repeatedly. Never invent or infer approval of a plan the user has not seen.
5. After plan approval, generate and show page 1's design image, then wait for explicit design approval. Only then reconstruct its editable PPT and render it. Obtain finished-page approval before page 2. Outline, design and finished-PPT approvals are separate.
6. A material change to count, order, page topic, essential content or source mapping returns the outline to review before dependent production continues. Present the changed outline and preserve unaffected work. A purely visual correction within approved content only needs current-page review. Keep plan approval and page approval separate on resume.

These rules apply equally to prompt-based decks, multiple source images, split-source and mixed decks. For supplied images, the discussion can be concise: confirm source order and what each page contains without inventing a redesign.

For source-based work:

- Several content images default to one slide per source, following explicit order, then attachment order or meaningful filename order. Record the chosen mapping. Ask if order is important and cannot be inferred. Style references are not content slides.
- If the requested count differs from the number of sources, do not silently drop or duplicate images. When the user authorizes restructuring, create and explain an explicit split/merge mapping; otherwise resolve the conflicting requirement before dependent work.
- A single source is split only when requested. Inventory all substantive text and relationships, assign each to a page, and use brief carry-over labels where needed to preserve cross-page relationships. Do not mechanically slice an image through text or turn cropped strips into allegedly editable slides.
- If source proportions differ, use the user's canvas or the first content source's aspect ratio as the deck canvas, stating that choice. Fit other sources proportionally and preserve readable content; do not stretch them. Recompose only within the requested fidelity/optimization scope. Ask if a fixed common canvas cannot preserve essential content legibly.

Verify the selected platform integration can produce and deliver a multi-slide PPTX. If it only produces one slide at a time, use its supported append/merge operation when it preserves native objects, fonts, media, and slide order. Do not concatenate PPTX ZIP entries or rasterize slides to simulate merging. If multi-slide composition cannot be made available through an appropriate platform skill/plugin, notify the user and pause.

## Save a deck plan

Read [project-state.md](project-state.md) and reuse its lightweight progress template or map it into the backend's existing manifest. Check revision-bound approval, artifact availability and remaining generation calls before advancing. Do not mistake the state validator for a user approval mechanism.

Use one shared scene or manifest that the selected authoring workflow can consume. Keep it backend-independent and include:

- Deck title, requested and planned total count, language, canvas, and shared style.
- Ordered slides with stable IDs, title, purpose, required content, chosen layout, and source mappings.
- Per-slide exact wording, facts and units, element IDs, assets, and relationship endpoints. For split sources, record relationships that cross page boundaries.
- Per-slide production status: planned, reference-ready, reconstructed, rendered, awaiting-review, needs-revision, approved, or blocked; asset locations and specific errors when applicable. Keep technical verification separate from user approval. Record the reviewed revision and the user's explicit approval so an older approval cannot be attached to a changed slide.

Stable slide IDs should survive insertion or reordering; display page numbers follow the current order. Keep the manifest, output file, and previews synchronized. It is a working artifact, not extra material to include in the public delivery by default.

## Design the set before individual pages

Define the palette, typography hierarchy, margins, illustration style, arrow/icon treatment, and optional page numbering once. Adapt layout to each slide's function: timeline, process, comparison, relationship diagram, or another structure that explains the content. Consistency does not require identical layouts or repeated decorative panels.

Give each slide a clear purpose. Avoid repeating the full title or identical introductory copy on every page. Ensure the ordered pages cover the requested subject without contradictions, missing sections, invented evidence, or filler. Preserve user-supplied content when faithful reconstruction is requested.

For mixed sources, preserve explicitly requested individual designs. Do not force all references into a new visual style merely to standardize them. Shared canvas and navigation can be consistent without redesigning source artwork.

## Produce each slide

Follow the current stage selected in the main skill. For prompt pages show the design and stop for approval before extraction or reconstruction. Save image/brief hashes and real approval evidence. An explicitly selected supplied source can use its reconstruction request as design approval. Outline approval does not approve unseen images.

For new content use [design-stage.md](design-stage.md) for the current page only; after design confirmation use [production-stage.md](production-stage.md). Do not preload production manuals during design. Preserve shared style and current-page content; never assume unsupported reference-image APIs or reuse one infographic as every page's background.

For supplied content images/SVGs, inspect and reconstruct those sources directly using [native-pptx.md](native-pptx.md); no new image generation is required. A mixed deck can contain both directly reconstructed pages and newly generated pages according to the manifest.

Build all pages into one presentation using the selected platform tool's multi-slide authoring workflow. Keep text, simple shapes, and required diagrams native on each slide. Share reusable builders and styles, and retain independent image assets for complex illustrations. Keep paragraphs editable as paragraphs, not dozens of per-line boxes.

Persist page progress and output locations after meaningful work. On interruption, resume the current unfinished or awaiting-review page from the saved manifest and reuse successful images rather than regenerating every page. Do not treat resuming the task as approving an unreviewed page. For a change to one slide, update its scene and dependent references; regenerate other pages only when a shared style or content dependency requires it. Changed approved pages require review again before continuing. Provider retries apply per failing page and remain bounded by any overall user budget. Repeated failures or exhausted limits are reported, not hidden by reducing the promised slide count.

## Confirm each page before the next

1. Complete the current page through native reconstruction, export, rendering, and content/editability checks. Do not ask the user to approve only a generated reference image as if it were the finished editable slide.
2. Provide the rendered page preview and a usable editable draft (a clearly labeled current-page or cumulative approved-pages-plus-current-page PPTX). State the current page number out of the agreed total and any material image-only limitations. Do not include placeholder pages as completed work.
3. Ask a concise confirmation question, for example: "第 2/8 页已完成，请确认这一页；确认后我再制作第 3 页。" Use the host's supported user-input mechanism or end the turn with the question. The waiting state is an intentional review gate, not a tool failure.
4. Wait for explicit approval of the displayed revision. "这页可以，继续" counts; silence, timeout, unrelated conversation, download activity, or a previous request to make the full deck does not. Do not generate later-page assets, start later-page code, or delegate later-page work while waiting. Saving the current state and checking the current page are allowed.
5. If the user requests changes, revise the current page, rerender, and present it for approval again. Only after approval mark this revision approved and begin the next page. If the user changes the outline or shared style, identify affected pages and renew approval for materially changed content.
6. After approval of the last page, assemble/finalize the complete deck and verify it as below. Do not call a deck fully approved while any page is awaiting review. Single-slide mode can deliver its verified page directly without this multi-page progression gate.

## Verify the whole exported deck

1. Export one PPTX and reopen or import that exact file with available tooling. Check actual slide count and slide order against the deck manifest, not against the number of generated images.
2. Compare every slide's required text, shapes, assets, and relationships with its content inventory. Confirm native editability on every relevant slide, not only the first slide. Detect empty pages, duplicated/missing pages, placeholders, and broken media or cross-slide references.
3. Render every exported slide and inspect it individually at readable resolution for wrapping, collisions, clipping, fonts, contrast, and connectors. A montage supports checking consistency and story flow but cannot replace per-slide inspection.
4. Check shared canvas, title hierarchy, margins, optional page numbers, and page-to-page terminology. Check multi-page narrative continuity and source coverage.
5. After a repair, export a new final filename, rerun whole-deck structural/count checks, and render the final deck. Inspect changed slides closely and scan unaffected slides for unintended changes. Use the selected platform's required finalization workflow.

If any required page remains blocked, missing, unverified, or awaiting approval, do not claim the complete deck is finished. Preserve useful work and identify the exact affected slide IDs/numbers and next action. Label any delivered partial file as a draft; do not silently omit failed pages or insert placeholders into a claimed final deck. Assembly should preserve approved content and appearance; if final rendering reveals a material change that needs repair, present the affected page for renewed confirmation.

## Delivery

After all pages are approved, return one final editable PPTX with the agreed number of slides. Provide ordered previews or a montage and the generated reference images for prompt-based pages, using a folder or ZIP when helpful. Use clear zero-padded display filenames such as `slide-01.png`, and distinguish generated references from renders of the final PPTX. Current-page PPTX drafts may be delivered for required reviews; the completed deliverable is one consolidated deck. Deliver an extra PDF or a separate final PPTX per page only when requested. Note image-only artwork or material limitations without exposing internal build/validation files.
