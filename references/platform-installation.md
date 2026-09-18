# Platform PPT skill and plugin discovery

Read when suitable native PPT authoring is missing, or the user asks to install/select a platform PPT integration. This reference guides discovery and installation, not redistribution of vendor code. Platform names below are discovery hints, not claims of tested compatibility. Recheck current official documentation and the actual host catalog before relying on an installation command or package identifier.

## Installation workflow

1. Identify the host and required operation. Confirm whether a native PPT tool, installed skill, or pending install already exists. Distinguish native editable PPTX from HTML-only presentations or image-only slide exports.
2. Search the host's supported skill/plugin catalog for `pptx`, `PowerPoint`, `presentation`, or the equivalent localized terms. Prefer a relevant official or platform-maintained integration; otherwise evaluate a reputable compatible candidate. If no catalog search is available, use current official documentation or an official repository. A search result or a familiar package name alone is not sufficient evidence.
3. Inspect the exact candidate, provenance, supported operations, dependencies, permissions, and installation method. Use the smallest suitable install scope. Avoid adding an unrelated bundle when a dedicated option works; explain any unavoidable broader document bundle.
4. Attempt installation through the host's documented installer or permitted local skill mechanism when authorized. Do not stop at recommending installation when an allowed installation action can complete it. Reuse prior user authorization and avoid asking the same question again. Announce the selected package and purpose before the mutation. This workflow does not itself override platform approval requirements or authorize charges, credentials, account connections, or unrelated system changes.
5. If the host only offers a user-click installation card, present it through the supported mechanism. If only a manual route exists, provide the verified steps. Continue content planning and other independent work; do not claim installation or connection is complete while it is pending. Do not invent tool IDs, execute chat slash commands in a shell, or bypass a missing installer by copying protected runtime directories.
6. Verify the installer result and refresh tool/skill discovery. Read the installed skill entrypoint, check dependencies and actual native export support. If a new session is required, say so; do not pretend a newly installed capability is callable in the current session. Continue only through a suitable usable platform integration, or notify the user and leave a precise handoff if the task is blocked. Do not automatically create a standalone backend.
7. Use the first task output to verify text editability and rendering. An installed label alone does not establish working PPT export. Record the selected integration, version when exposed, and any untested features in the working record.

Bound installation discovery to the task: try the best verified candidate, and one suitable alternative if the first fails for a candidate-specific reason. Follow the installer's documented transient retry rules. Stop repeating attempts for the same permission, authentication, or host restriction. When no suitable integration can be made usable, pause PPT production and explain the user action required; do not switch automatically to a general-purpose library. Do not install across several unrelated platforms in one user's environment.

## Host routing hints

### Codex or another host with a skill/plugin catalog

Inspect installed presentation skills/plugins before directly exposed native tools, following the explicit priority and tie-break rules in [runtime-adaptation.md](runtime-adaptation.md). Reuse a suitable working project integration unless the user specifies otherwise. Otherwise follow the current host's catalog discovery and installation facilities, including any restrictions on which packages can be suggested or installed. Do not hard-code local cache paths, copy a bundled proprietary runtime, or assume a plugin listed elsewhere is installable here.

### Claude Code

Claude Code supports filesystem skills and plugin installation. Its built-in skill list is distinct from Claude's hosted document tools. Anthropic's skills repository documents a `document-skills` plugin containing document workflows, including PPTX. Recheck the repository and exact package contents before installation.

The repository documents these commands inside Claude Code's command interface:

```text
/plugin marketplace add anthropics/skills
/plugin install document-skills@anthropic-agent-skills
```

Use them only if still documented and available in the actual host. They are not shell commands. Prefer a documented automation/CLI installer when the host exposes one; otherwise present these verified interactive steps. Inspect any document skill's own license and dependencies; a public repository is not automatic permission to rebundle its contents.

Sources: [Claude Code skills](https://code.claude.com/docs/en/skills), [Anthropic skills repository](https://github.com/anthropics/skills), [cross-surface availability](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview).

### Claude web, desktop, or API

Discover document capabilities exposed in that surface and account. A hosted `pptx` capability, if available, is a candidate backend; do not assume Claude Code's plugin commands work here. Use the surface's actual skill upload or configuration path when needed and permitted. API execution environments may restrict network access and dependency installation, so prefer provided capabilities and report missing ones accurately.

### WorkBuddy

Use its Skills Market and installed-skills list. Compare installed `pptx`, vendor PPT skills and other presentation plugins using [runtime-adaptation.md](runtime-adaptation.md); host ownership alone does not give a vendor skill priority. Read the selected skill before using its underlying CLI. Keep launcher fixes in the selected integration; this skill does not depend on any vendor CLI. Official documentation describes searching, installing, and importing local skill packages, and lists PPT creation as a skill use case. Discover the actual package and available installation operation in the current product; do not invent a fixed official PPT package ID or assume every edition ships with it. Verify the selected backend can follow the supplied layout and export native editable content.

Sources: [WorkBuddy skill management](https://www.codebuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Skills-Market), [WorkBuddy skill package structure](https://open.workbuddy.cn/en/docs/skill).

### Qianwen / Qwen and Doubao

Determine whether this is the consumer app, a desktop work mode, a coding agent, or a model API. Consumer app descriptions advertise PPT generation, but this does not prove that custom skills can invoke the internal PPT engine. A model API alone does not inherit the consumer app's Office tools.

Inspect current help and the exposed skills/plugins/tools. Use a supported PPT workflow or installation mechanism if actually present. If the consumer app offers only an interactive PPT button, explain the limitation; do not claim this ZIP can unlock internal APIs. Where no custom skill loader is exposed, the user may use the workflow instructions manually, but do not describe that as an installed or automatically integrated skill. In a coding-agent host, use that host's generic discovery/install route instead of assuming consumer app capabilities.

Feature references, not installation APIs: [Qianwen developer-provided app listing](https://apps.apple.com/cn/app/id6466733523), [Doubao developer-provided app listing](https://apps.apple.com/cn/app/id6459478672).

### Other Agent Skills hosts and custom agent environments

Discover the host's documented SKILL.md support, compatible package format, catalog, and installer. Some hosts support skills but not plugins, slash commands, or cross-skill invocation. Use only the features actually available. Let the agent follow a matching installed skill directly when supported; do not require a universal skill-to-skill API.

Keep skill paths relative to the package, and runtime paths derived from the actual environment. Windows, macOS, and Linux routes should differ only where the host or runtime requires it. If an API wrapper has neither a suitable PPT tool nor an installer, report that limitation using the notification rule in [runtime-adaptation.md](runtime-adaptation.md), even if code execution is exposed.

## Packaging boundary

Distribute this workflow's own files. External skills, plugins, fonts, templates, and libraries retain their own licenses and installation processes. Installing a dependency for a user is distinct from copying it into a public release. Do not bundle another vendor's runtime or promise offline/self-contained execution merely because a skill installation succeeded.
