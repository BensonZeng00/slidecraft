# Prompt to infographic workflow

Optional detailed reference for complex prompt composition, not the normal entry point. Use [design-stage.md](design-stage.md) for routine design tasks. Defer reconstruction/delivery instructions below until design approval and stage 2.

This is the per-slide workflow. In multi-slide mode, read [multi-slide.md](multi-slide.md) first to establish the deck plan and shared design, then apply this workflow only to the current page. Complete its editable PPT and preview, obtain explicit user confirmation, and only then begin the next page. Do not batch-generate future pages, compress a planned deck into one generated image, or deliver a contact sheet as the presentation.

## Plan accurate content

Extract the subject, audience, intended takeaway, required wording, visual style, canvas, and editing requirements. Infer routine design choices; ask only when missing information prevents faithful content or changes the user's scope materially.

Save a compact scene description in the working project, in a format the presentation generator can reuse. Include:

- Canvas aspect ratio, language, and design intent.
- Stable element IDs, element type, exact text, and hierarchy.
- Supplied or verified numbers, units, and source references when applicable.
- Relationship endpoints by element ID, direction, and labels.
- Planned image-only assets and any full-editability requirement.

Use the user's supplied facts accurately. Verify claims when current or specialist facts require research. Do not invent statistics to make a chart attractive. If the topic does not require quantitative evidence, use a qualitative diagram. Clearly identify illustrative values when the user requests examples.

Choose the information relationship that explains the content (such as chronology or comparison), but let image generation propose the visual composition unless the user supplies a layout. Do not prescribe coordinates, a fixed card grid, alternating node positions, flat styling, or bans on backgrounds/hero imagery merely to simplify coding. Preserve substantive wording when condensing and respect requested page count. An exact-layout request or full internal editability can justify tighter geometry constraints; ordinary editable PPT does not.

## Generate the image

Before the first generation call, state expected reference-image count, current-page scope, and the retry ceiling. Default to one candidate per slide with at most three calls per page including the initial request. Track calls using [project-state.md](project-state.md), obey lower user limits and pause at the first exhausted per-page or project cap. Extra artwork, variants and edits count too. Reconcile an uncertain job before resubmitting; polling is not a new generation. Stop after a usable result. Do not quote actual cost without provider evidence.

Use the image-generation implementation selected through [runtime-adaptation.md](runtime-adaptation.md). Read its matching skill or tool documentation when available. The user requested an actual generated infographic before slide reconstruction. Describe the task as an infographic or educational diagram; `infographic-diagram` below is a prompt label, not a required provider API value.

Use a concise, visual-first brief. Keep factual/content requirements distinct from aesthetic freedom. Apply the visual direction of a user-liked reference without copying its factual mistakes. A PPT backend's generic design preferences must not override image generation or the user's chosen style. Include only relevant fields:

```text
Use case: infographic-diagram
Asset type: complete infographic for a presentation
Topic and audience: <user intent>
Canvas: <aspect ratio and orientation>
Visual goal: compelling integrated design, clear hierarchy, readable text
Information relationship: <chronology, comparison, process, etc.>
Art direction: <user's preferences/reference if provided; otherwise let
  the image model choose composition, palette, illustration and effects>
Text (verbatim): <exact title, labels, body, values and units>
Relationships: <node names, directions, connection labels>
Content constraints: preserve accurate wording and relationships;
  no invented facts, duplicate content or unreadable/overlapping labels.
Do not include implementation coordinates or library constraints.
```

Do not impose flat styling by default. Complex backgrounds, atmospheric light, large subject illustrations and coherent panels are valid when they serve the subject and preserve readability. After inspecting the chosen image, decide which objects are native and which artwork remains image-only. Explain the tradeoff before production. Only when every illustration's internal geometry must be editable, use a cleaner geometric style or resolve the tradeoff with the user. Do not sacrifice visual quality merely to maximize native-object counts.

For example, a short topic can become: "制作一张关于{主题}的中文信息图，用于一页16:9演示文稿。兼顾视觉吸引力、信息层次与文字可读性，自主选择适合主题的构图、插画和视觉风格。准确呈现以下内容与关系：{内容计划}。" Add art direction only when supported by the user or context, not a long list of arbitrary prohibitions.

Generate one coherent candidate per planned slide by default. Carry the shared deck style into every prompt, but include only the current slide's content. Use only actual tool arguments supported in the session; an aspect-ratio instruction is not evidence that the tool returned that exact ratio. Persist the selected generated asset in the project using its returned location and supported handling. Inspect actual image dimensions before mapping positions. Do not stretch a mismatched image; preserve proportions and adjust the slide composition to the requested canvas.

## Review, confirm, then map

Apply [design-stage.md](design-stage.md) to every prompt slide. Show the inspected design and proposed corrections, freeze image and brief, ask for confirmation and end the turn. No extraction, PPT authoring or rendering before approval. Changed designs need renewed confirmation.

Inspect the generated image itself. Compare every planned text block and relationship with the content plan. Separate visual problems from content errors:

- Typos, inaccurate numbers, or an isolated wrong arrow: use the correct planned content when reconstructing the PPTX. Report meaningful differences between the reference image and final PPTX.
- Major missing sections or an unusable composition: revise the generation prompt or edit the image before reconstructing. Prefer targeted changes and preserve the correct content.
- Repeated generation failure: after an initial attempt and up to two targeted retries by default, report the remaining limitation. Do not loop indefinitely or silently omit required sections. Honor an explicit user retry budget.

Add observed layout bounds, colors, font intent, and assets to the scene. Use normalized coordinates or a documented canvas coordinate system, converting to the authoring library's units at the export boundary. OCR can aid transcription, but does not override planned wording or substitute for visual inspection.

Only after approval and a successful `workflow.py reconstruct-check`, reconstruct with the native PPTX workflow and compare the rendered slide with the approved brief and image. Exact pixel identity is not the goal; disclose approved corrections and preserve substantive meaning. Unsupported CLI checks require equivalent host checks, not silently skipping confirmation.

## Completion

Deliver the PPTX, generated reference image(s), and final slide preview(s) with clear labels and matching page order. For multi-slide work, use the delivery and completion checks in [multi-slide.md](multi-slide.md). Briefly identify editable object types and any image-only assets. Keep the final generation prompts available in the working files and follow any reporting requirements of the selected provider. Distinguish generation success, rendering verification, and actual PowerPoint-app testing; claim only the checks performed.
