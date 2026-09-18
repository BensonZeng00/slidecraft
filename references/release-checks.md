# Release and new-backend acceptance

Read for release review or first adoption of an authoring backend, not for every ordinary slide. Record date, skill version, host/OS, integration version, test input, artifact locations, observations and remaining limits. Distinguish static inspection, simulated scenarios, actual provider execution, renderer verification and real presentation-application interaction.

## Required cases

For beta.6 and later, real prompt cases must show the design image and stop for actual user confirmation before reconstruction, including single slides. Test image/brief changes invalidating design approval and restart at the waiting gate. Old completed examples establish rendering/editing evidence only, not evidence of this newly introduced human review flow. Synthetic tests cannot replace it. Follow the fixed stress-edit inputs in [design-and-cli.md](design-and-cli.md); do not weaken a failing long-text test to obtain a pass.

1. Prompt to one infographic to native PPTX: save exact input and generation prompt, inspect generated image, export/reimport/render final PPTX, match required text and relationships. Test Chinese paragraph wrapping. Keep reference and final render distinct.
2. Supplied image: retain all required content; simple geometry is native, complex isolated assets have clean boundaries and no duplicate baked-in labels. Review real output for crop seams, opaque rectangles, mismatched background, font substitution, collisions and clipping. Preserve source typos unless correction is authorized.
3. Three-page real workflow: discuss and present the complete outline and each page's substantive content, then stop without generating or constructing page 1. Revise the plan on feedback and obtain explicit plan approval. Only then make page 1 draft and preview, stop; user requests a revision, revise and stop again; user approves, only then produce page 2. Interrupt and resume at an awaiting-review page; do not treat resume as approval. Test that material plan changes require renewed outline approval and that outline approval does not approve page outputs. After all three page approvals, consolidate and verify exactly three native slides in order. Synthetic approval records only test state logic and never count as this human review test.
4. Disposable application edit: open the exported PPTX in the target presentation application, replace a paragraph with longer content, move a connected node, resize/replace a separate image when present, save to a new file and reopen. Check text editability, wrapping and connector attachment after reopening. If application control is unavailable, document structural/import checks separately and leave app editing pending.
5. Environment routing: existing working PPT integration (no duplicate install); missing integration with successful authorized install and first output; installation unavailable/failed/pending (notify and stop, no generic library fallback). Injected fixtures are simulations, not real installation tests. Never uninstall a user's working skill or break permissions just to create a failure case.
6. Resource limits: success stops retries; failures stop at the per-slide and project caps; timeout reuses the same job; extra candidates need agreement; approval and budget both checked before generation. Never call a paid provider merely to test rejection when a local negative test suffices.

## Compatibility labels

- `tested`: name the exact tested capability, host/version and evidence. A single-slide success does not prove deck assembly, application editing or installation.
- `unverified`: provider-neutral adaptation documented but no end-to-end evidence. Do not advertise as supported.
- `unavailable-in-this-session`: observed missing capability in this environment only; do not generalize to an entire vendor or model.
- `blocked`: known issue with reproducible evidence and the needed next action.

## Publication package

Keep SKILL.md concise with conditional references. Validate frontmatter and relative links; run supplied state tests. Archive one skill-root folder, exclude caches, node_modules, private runtime paths, credentials and private test outputs. Validate archive paths and hashes against staged files. Retain a recoverable old version before installation; provide one active skill folder, not several renamed duplicates.

Include author/source provenance and an explicit owner-selected distribution license before public release. Do not infer an open-source license from user authorship, a public repository or a dependency's manifest. Keep third-party integrations separate. Real examples must have publication permission; disclose generated references. A package can be prepared for private testing while public licensing or external platform tests remain pending.

Use a dated test report: pass / failed / pending / simulated, with evidence. Structural validation is not an end-to-end pass. Claim only the compatibility actually tested. Never turn pending user confirmation, missing software access or a license decision into a green release check.
