"""Read-only progress checks. No provider calls, dependencies or PPT backend."""

import argparse
import json
from pathlib import Path, PurePosixPath, PureWindowsPath
from outline_state import outline_errors

STATUSES = {"planned", "reference-ready", "reconstructed", "rendered",
            "awaiting-review", "needs-revision", "approved", "blocked"}
READY = {"rendered", "awaiting-review", "approved"}


def integer(value, minimum=0):
    return type(value) is int and value >= minimum


def safe_path(value):
    return (isinstance(value, str) and bool(value)
            and not PureWindowsPath(value).drive
            and not PureWindowsPath(value).root
            and not PurePosixPath(value).is_absolute()
            and ".." not in PurePosixPath(value.replace("\\", "/")).parts
            and ":" not in value)


def validate(state, root=None):
    errors = []
    if not isinstance(state, dict):
        return ["state must be an object"]
    if type(state.get("schema_version")) is not int or state.get("schema_version") != 1 or not isinstance(state.get("project_id"), str) or not state["project_id"].strip():
        errors.append("schema_version=1 and project_id are required")
    slides = state.get("slides")
    if not isinstance(slides, list) or not slides:
        return errors + ["slides must be a nonempty array"]
    if state.get("mode") not in ("single", "multi"):
        errors.append("mode must be single or multi")
    if (not integer(state.get("total_slides"), 1)
            or state["total_slides"] != len(slides)
            or (state.get("mode") == "single" and len(slides) != 1)):
        errors.append("slide count does not match mode/ordered slides")
    errors.extend(outline_errors(state))
    ids, earlier_unapproved = set(), False
    for slide in slides:
        if not isinstance(slide, dict):
            errors.append("each slide must be an object")
            continue
        sid = slide.get("id")
        if not isinstance(sid, str) or not sid or sid in ids:
            errors.append("slide IDs must be nonempty unique strings")
            continue
        ids.add(sid)
        status = slide.get("status")
        if not isinstance(status, str):
            errors.append(f"{sid}: status must be a string")
            continue
        if status not in STATUSES or not integer(slide.get("revision"), 1):
            errors.append(f"{sid}: invalid status or revision")
        artifacts, checks = slide.get("artifacts", {}), slide.get("checks", {})
        if not isinstance(artifacts, dict) or not isinstance(checks, dict):
            errors.append(f"{sid}: artifacts/checks must be objects")
            continue
        for value in artifacts.values():
            if not safe_path(value):
                errors.append(f"{sid}: artifact paths must stay within project")
            elif root is not None:
                target = (root / value).resolve()
                if not target.is_relative_to(root.resolve()) or not target.is_file():
                    errors.append(f"{sid}: missing or out-of-project artifact {value}")
        if status in READY:
            if not artifacts.get("pptx") or not artifacts.get("preview"):
                errors.append(f"{sid}: ready status requires PPTX and preview")
            if checks.get("native") is not True or checks.get("render") is not True:
                errors.append(f"{sid}: ready status requires native/render checks")
        approval = slide.get("approval")
        if status == "approved":
            if (not isinstance(approval, dict)
                    or approval.get("revision") != slide.get("revision")
                    or not approval.get("evidence") or not approval.get("user_text")):
                errors.append(f"{sid}: missing approval for this revision")
        elif approval is not None:
            errors.append(f"{sid}: clear stale approval after revision")
        if (earlier_unapproved and status not in {"planned", "approved"}):
            errors.append(f"{sid}: later unapproved production crossed review gate")
        earlier_unapproved |= status != "approved"
    generation = state.get("generation")
    if not isinstance(generation, dict):
        return errors + ["generation budget required, use zero limits for no generation"]
    for field in ("planned_images", "max_calls_per_slide", "max_calls_total"):
        if not integer(generation.get(field)):
            errors.append(f"generation.{field} must be a nonnegative integer")
    attempts = generation.get("attempts")
    if not isinstance(attempts, list):
        return errors + ["attempts must be an array"]
    attempt_ids, counts = set(), {}
    ordered = [s for s in slides if isinstance(s, dict) and isinstance(s.get("id"), str)]
    first_unapproved = next((i for i, s in enumerate(ordered) if s.get("status") != "approved"), len(ordered))
    future_unapproved = {s["id"] for s in ordered[first_unapproved + 1:] if s.get("status") != "approved"}
    for attempt in attempts:
        if not isinstance(attempt, dict):
            errors.append("each attempt must be an object")
            continue
        aid, sid = attempt.get("id"), attempt.get("slide_id")
        if not isinstance(aid, str) or not aid or aid in attempt_ids:
            errors.append("attempt IDs must be unique nonempty strings")
        else:
            attempt_ids.add(aid)
        if not isinstance(sid, str) or sid not in ids:
            errors.append("attempt references unknown slide")
            continue
        counts[sid] = counts.get(sid, 0) + 1
        if sid in future_unapproved:
            errors.append(f"{sid}: generation attempt crossed review gate")
        if attempt.get("outcome") not in ("requested", "succeeded", "failed", "unknown"):
            errors.append(f"{sid}: invalid attempt outcome")
    if integer(generation.get("max_calls_total")) and len(attempts) > generation["max_calls_total"]:
        errors.append("project call cap exceeded")
    if integer(generation.get("max_calls_per_slide")):
        if any(n > generation["max_calls_per_slide"] for n in counts.values()):
            errors.append("per-slide call cap exceeded")
    return errors


def production_errors(state, slide_id):
    errors = validate(state)
    if errors:
        return errors
    if state.get("mode") == "multi" and state["outline"]["status"] != "approved":
        return ["confirm the outline and each page's content before any page production"]
    current = next((s for s in state["slides"] if s["status"] != "approved"), None)
    if current is None or current["id"] != slide_id:
        return ["production allowed only for the current unapproved page"]
    if current["status"] == "awaiting-review":
        return ["current page awaits user review"]
    return []


def generation_errors(state, slide_id, purpose="reference", root=None):
    errors = production_errors(state, slide_id)
    if errors:
        return errors
    current = next(s for s in state["slides"] if s["id"] == slide_id)
    if purpose == "artwork":
        if root is None:
            return ["artwork extraction requires project root and approved design"]
        from workflow import reconstruction_errors
        errors = reconstruction_errors(state, slide_id, root)
        if errors:
            return errors
    if current["status"] not in {"planned", "needs-revision", "reference-ready", "blocked"}:
        return ["page is already built or awaiting review; no speculative generation"]
    gen = state["generation"]
    attempts = [a for a in gen["attempts"] if a["slide_id"] == slide_id]
    if len(gen["attempts"]) >= gen["max_calls_total"] or len(attempts) >= gen["max_calls_per_slide"]:
        errors.append("generation call budget exhausted")
    if any(a["outcome"] in {"requested", "unknown"} for a in attempts):
        errors.append("reconcile existing request before submitting again")
    if purpose != "artwork" and current["status"] != "needs-revision" and any(a.get("usable") is True for a in attempts):
        errors.append("usable image exists; stop retries")
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("state", type=Path)
    parser.add_argument("--check-files", action="store_true")
    parser.add_argument("--allow-generate", metavar="SLIDE_ID")
    parser.add_argument("--allow-produce", metavar="SLIDE_ID")
    parser.add_argument("--purpose", choices=("reference", "artwork"), default="reference")
    args = parser.parse_args()
    try:
        state = json.loads(args.state.read_text(encoding="utf-8-sig"))
        errors = validate(state, args.state.parent if args.check_files else None)
        if not errors and args.allow_produce:
            from workflow import reconstruction_errors
            errors = reconstruction_errors(state, args.allow_produce, args.state.parent)
        if not errors and args.allow_generate:
            errors = generation_errors(state, args.allow_generate, args.purpose, args.state.parent)
    except (OSError, ValueError, TypeError) as exc:
        errors = [str(exc)]
    print(json.dumps({"valid": not errors, "errors": errors}, ensure_ascii=False, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
