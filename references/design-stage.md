# Stage 1 — design, then stop

This is the normal single-slide design route. No PPT construction manuals are needed yet. Confirm exposed image generation, inspection and file delivery; read the selected image tool's instructions. Record tool/provider, model (unknown if not exposed), job/asset IDs and outcomes. Disclose a known PPT capability gap before spending; detailed PPT selection belongs to stage 2. Do not promise unavailable export. If generation is unavailable, report it; native-only creation is a different workflow requiring user agreement.

## Prepare and generate

Save exact words, values/units, sources and relationship endpoints in a brief. Verify specialist/current claims; distinguish facts from visual metaphors. Infer routine design choices, asking only about material gaps. Use the user's language, Chinese if unspecified; no invented statistics. Explain that complex illustrations normally remain replaceable images, not internally editable geometry.

### Choose and announce the visual style before generation

Read the user's prompt, supplied materials/reference images and conversation context to choose a visual direction before calling image generation. Consider the topic, audience, intended use, tone, information density and content relationships together; do not map a topic keyword mechanically to a preset (for example, technology need not mean neon blue).

Honor explicit style requests and brand constraints first, then user-selected visual references and an established deck style. Infer unspecified choices from the communication goal. A reference supplied for content alone is not automatically a style reference. When context is sparse, choose a restrained, readable direction suited to the available content and label it as your choice, not a stated user preference. Ask only when conflicting requirements or a material gap prevents a useful decision.

Before the first generation call, tell the user in their language, in one or two sentences: the chosen style, the input/context that supports it, and concrete visual traits such as palette, typography/hierarchy, illustration treatment and information density. For example: “根据你提到的‘面向管理层汇报’和这页的对比数据，我会采用简洁的商务信息图风格：浅底、深色标题、单一强调色，以对比图表突出结论。” Tailor the explanation to the actual request rather than repeating this example. This is an announcement, not a new approval gate; proceed unless clarification is necessary or the user requested approval first.

Record the chosen direction and its basis in the working brief, and include the same art direction in the image-generation prompt. Let the image model explore composition, illustration details and effects within that direction unless the user specifies them. For later deck pages, reuse the shared style and briefly state the current page's treatment; announce any changed direction before generating a revision. When resuming an unchanged, already-generated design, present it without regenerating merely to satisfy this step.

Do not force a template, coordinates or flat styling merely to ease reconstruction. A short prompt needs topic, audience, canvas, exact content, relationships, the announced art direction and readable text. Generate an actual infographic, not a coded placeholder.

### Generate within the page budget

Announce one expected reference and at most three calls per page including edits/extraction, or the user's lower cap. Stop after a usable reference. Extra scope/budget requires agreement; do not infer costs. In a deck, release calls only for the current page after outline and previous-page approval.

Use one project state based on [the template](../assets/project-state.example.json), not duplicate manifests. Before each request run with the host's Python when available:

```text
python scripts/validate_state.py project-state.json --allow-generate page-intro
```

Keep one writer; persist state atomically. Record unique attempt ID, slide ID and `outcome: requested` before calling; then save job ID and `succeeded`, `failed` or `unknown`, plus whether usable. Unknown requests still consume budget: reconcile/poll the existing job, never blindly resubmit. Preserve attempts across revisions. Artwork extraction also counts but cannot start before design approval.

## Inspect, save, ask

Inspect the returned image and actual dimensions: required content, arrows, legibility and misleading imagery. Preserve proportions. Correct an unusable design within budget; stop on exhausted limits/repeated permission failure. Explain small corrections planned for editable text instead of unnecessarily regenerating.

Save a versioned image and frozen reviewed brief within the project. The brief includes content, chosen design and proposed corrections; mutable build metadata stays elsewhere. On the existing slide set `status: reference-ready` and:

```json
{"design":{"revision":1,"image":"design/page-01-v1.png","brief":"design/page-01-v1.json","approval":null}}
```

Show the image as a design preview, not an editable PPT, identify corrections and ask: “这是设计图 v1，确认后我再复刻为可编辑 PPT；需要修改哪里？” **End the turn.** No extraction, PPT authoring/rendering or future-page production while waiting.

After explicit approval, obtain current hashes:

```text
python scripts/workflow.py fingerprint project-state.json --slide page-intro
```

Set `design.approval` to returned `revision`, `image_sha256`, `brief_sha256` plus actual `user_text` and message ID/time in `evidence`. Never fabricate approval. Ambiguous “continue” requires clarification; explicit approval of the displayed version needs no extra question. Changing image/brief invalidates approval. Then load stage 2 through the main router, not before.

On normal resume, verify saved files/hashes, reconcile jobs and present the waiting design. For contradictory/missing state or multi-page recovery only, read [project-state.md](project-state.md); never auto-approve legacy work. For unusually complex prompt composition only, consult [prompt-to-infographic.md](prompt-to-infographic.md). These are conditional, not mandatory preloads. Without Python use equivalent host checks, preserving the same gates and budget.
