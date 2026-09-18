# Runtime adaptation

This skill is a portable workflow, not a bundled image model, API client, or presentation engine. Automatic adaptation means selecting and invoking capabilities the current host actually exposes. A model's advertised image or coding ability alone does not establish tool access. Do not claim cross-platform compatibility solely because these instructions are provider-neutral.

## Discover capabilities before production

Use the host's tool catalog/search, skill catalog, and runtime discovery mechanisms. Identify the host application separately from the model: the same model may run in a desktop agent, a consumer chat app, or an API wrapper with different tools. When shell access is available, perform focused read-only checks for relevant installed libraries, renderers, and fonts. Do not search unrelated files or secrets. Do not assume another session's paths, OS, credentials, or packages exist. If the host cannot be identified, use capability-based discovery and the generic route in [platform-installation.md](platform-installation.md).

Keep a brief working record of the selected implementations, supported operations, and evidence of availability:

| Capability | Required evidence | When required |
| --- | --- | --- |
| Image inspection | Can display and inspect the input or generated image | All image reconstruction and image review |
| Image generation | Callable tool accepts a text prompt and returns a retrievable image or supported asset handle | Prompt-to-infographic mode |
| Native PPTX authoring | Can create editable text, shapes, and images and export a real PPTX file | All PPTX outputs |
| Multi-slide composition | Can append or safely merge native slides into one ordered PPTX with a common canvas | Multi-slide mode |
| Artifact rendering | Can render the exported PPTX directly, or reimport it and render every slide | Verified final delivery |
| File delivery | Can persist the actual outputs and return usable files or supported artifact links | All deliverables |

Distinguish image generation, image editing, and image inspection. Support for one does not imply the others. A tool that generates slide pictures does not satisfy native PPTX authoring. Package inspection proves native object structure but cannot replace visual rendering.

## Select implementations

Select eligible PPT integrations in this order:

1. The user's explicit skill, plugin, provider or tool choice. If unavailable, explain the specific limitation; do not silently substitute another provider.
2. The integration already used and verified for the current project, if it still meets the request.
3. Installed, callable dedicated PPT skills or plugins. Read their instructions before invoking underlying engines.
4. Directly exposed native PPT tools when no suitable skill/plugin is available.
5. Authorized platform discovery/installation if no existing route is usable; otherwise report the blocker.

Within one tier, compare required editable objects and exports first, then a verified actual-PPTX rendering path (a separate renderer is valid), successful evidence in this environment, and fewer dependencies/conversions. A known incompatible integration is not eligible just because it ranks higher. Missing rendering means only draft capability; prefer a suitable route with rendering for verified delivery. Skills named `pptx` and vendor-named PPT skills compete on capabilities, not spelling or host ownership. Do not automatically choose the host vendor's engine or a low-level CLI before checking installed PPT skills/plugins.

Keep a compact selection record: relevant candidates, availability evidence, unmet requirements, selected integration and renderer, and reason. Announce the choice briefly; no routine selection question. Continue with a suitable working integration rather than repeatedly comparing alternatives. Reassess after a material capability failure, preserving content plans and source assets. Never switch silently to a new paid service or one requiring additional permissions.

For missing PPT authoring capability, exhaust the eligible existing routes in the priority order above; discover and attempt an authorized platform-supported PPT skill/plugin installation; pause PPT production and notify the user if neither route yields a usable integration. Consult [platform-installation.md](platform-installation.md) for installation. An unavailable installer, a user prohibition, an incompatible candidate, or a blocked connection is a reason to report the actual blocker, not to switch automatically to a general-purpose library. Do not treat this order as a reason to replace a working integration.

For image generation:

- Record the actual chosen image tool, provider and exposed model name (unknown when not exposed), returned job/asset identity and request outcome; never infer them from branding or filenames. Briefly name the selected tool before generation.
- Use a host's native image tool when suitable, regardless of its name. `imagegen` is one integration, not a mandatory dependency.
- A configured image-generation connector or API can be used when permitted and within the user's authorization. If switching involves a new service, credentials, or additional authorization, explain the missing requirement instead of switching silently.
- Translate the shared prompt into the real provider schema. Check supported dimensions, reference-image handling, asynchronous job results, and file retrieval. Do not send fields copied from an unrelated provider.
- Retrieve or reference results only through mechanisms supported by the host. Never invent a filesystem path for an inline image, asset handle, or remote URL. If the result cannot be inspected or consumed by the authoring environment, state that bridge limitation.

For PowerPoint authoring:

- A compatible installed presentation skill is the preferred guide when available. Its vendor-specific libraries and finalizers are not required in hosts where it is absent.
- If no suitable native tool or installed skill exists, try the platform skill/plugin route first. After that route is exhausted or inapplicable, notify the user and pause PPT production. Do not automatically install or use a standalone library, even if code execution is available. This does not prevent an already selected, working platform skill from using its documented libraries internally.
- Select a renderer separately if necessary. An available presentation application, LibreOffice-based conversion, or a validated import-and-render service may provide it. Do not assume the writer can render slides.
- Apply the same object mapping and final-artifact checks from [native-pptx.md](native-pptx.md) with the available tooling. No specific finalizer script or absolute skill path is required by this skill.

## Execution preflight and bounded recovery

Before production, use the selected integration's documented discovery/help operations to confirm its callable entry, runtime and rendering path. For local renderers, use the read-only probe in [delivery-evidence.md](delivery-evidence.md) when available. Distinguish not detected, detected but untested, invocation failure and permission blocking; failed PATH lookup or one failed command cannot establish that an application is not installed. Reuse a version-scoped record within the project; refresh when a path, version or capability changes. Do not search unrelated directories. Do not assume a preview is a render of the exported PPTX.

Prefer supported tool APIs. Where the integration documents subprocess invocation, use explicit executable paths and argument arrays without shell interpolation. Keep vendor launchers and backend-specific fixes in that integration, not in slidecraft. Do not cycle through shells with unchanged inputs. Capture exit code, stdout, stderr and structured diagnostics; stderr warnings alone are not failure. Empty output alone is not success. Confirm the expected output artifact.

Classify a failure before retrying: missing runtime/entry, content or layout diagnostics, transient rendering failure, unsupported asset, or permission/authentication. Correct deterministic inputs before repeating. Allow at most one targeted launch recovery and one transient render retry per unchanged revision unless the integration specifies a stricter limit; repeated identical failures stop that route. This is separate from image-generation budgets. Follow supported job reconciliation before retrying uncertain external calls.

Layout diagnostics identify a rule and element, not necessarily a design defect. Distinguish intended decorative bleed from clipped content; fix within supported backend rules while preserving composition. Do not suppress all lint checks or move all out-of-bounds artwork indiscriminately. For asset failures use the fidelity-preserving fallback in [native-pptx.md](native-pptx.md).

On cancellation stop and retain successful outputs. On user-requested resume, reconcile existing state and rerun only invalidated or incomplete steps. Cleanup may affect only processes created by this task, never all running presentation applications.

## Missing capabilities and failures

- Image supplied, no image generation: proceed with direct reconstruction; generation is unnecessary.
- Prompt supplied, no image generation: finish useful content planning, report the missing generation capability, and offer direct native-slide creation as a distinct alternative. Do not claim that the requested generated infographic exists.
- No presentation skill, but a suitable native authoring tool and rendering available: proceed using those implementations without installing a duplicate. If only a general-purpose library is available and the platform installation route cannot provide a suitable integration, pause and notify the user rather than creating a new backend.
- No native PPTX export: provide useful planning or image results where available, state the blocker, and do not label a picture as an editable presentation.
- Multi-slide request but no supported multi-slide composition: attempt a suitable platform PPT skill/plugin route, then notify the user and pause if still unsupported. Do not replace the requested deck with a montage or silently reduce it to one slide.
- No renderer: preserve any produced PPTX as an unverified draft and explain which visual checks remain incomplete. Do not claim verified completion.
- Selected tool fails: use its supported retry behavior within the task's retry budget. Reassess suitable platform tools or skills when the failure changes availability. If no such integration remains usable, notify the user rather than switching automatically to a standalone library.

## User notification when PPT capability is unavailable

State which capability is missing, which relevant discovery or installation attempt failed, and the specific next action the user can take (for example install the verified package, enable it, complete a connection, or start a new session). Provide verified installation steps or the host's install card where available. Distinguish an unsupported host from a transient install failure and from a pending user action. Preserve completed planning and assets, but stop dependent PPT production and do not present them as a finished presentation. A generic code-based implementation becomes a separate option only if the user explicitly requests it; do not push it as an automatic fallback.

## Cross-environment verification

For a newly selected backend, inspect its first real output: exported native text and shapes, image proportions, Chinese or other required fonts, geometry units, connector behavior, and readable rendering. Record only actual compatibility evidence. At release time, exercise the prompt route, supplied-image route, and missing-capability cases in each environment advertised as supported.

Keep the content plan and asset roles independent of the backend. Adapt schema, coordinates, asynchronous job status, asset retrieval, and delivery links to the chosen tools. A platform's PPT marketing page does not establish that its internal tools can be invoked by this skill or that its output satisfies native editability requirements.
