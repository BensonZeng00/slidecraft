"""Validate the discussed deck outline independently from page approval."""
import hashlib
import json


def outline_fingerprint(outline):
    payload = {k: v for k, v in outline.items() if k not in {"approval", "status"}}
    encoded = json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def outline_errors(state):
    if state.get("mode") != "multi":
        return []
    outline = state.get("outline")
    if not isinstance(outline, dict):
        return ["multi-slide outline required; recover or request approval before production"]
    errors = []
    revision = outline.get("revision")
    if type(revision) is not int or revision < 1:
        errors.append("outline revision must be a positive integer")
    if outline.get("status") not in ("draft", "awaiting-review", "needs-revision", "approved"):
        errors.append("invalid outline status")
    pages = outline.get("pages")
    if not isinstance(pages, list) or not pages:
        return errors + ["outline must include per-page content"]
    mappings = []
    for page in pages:
        if not isinstance(page, dict):
            errors.append("outline pages must be objects")
            continue
        mappings.append((page.get("id"), page.get("title")))
        points = page.get("key_points")
        if (not isinstance(page.get("title"), str) or not page["title"].strip()
                or not isinstance(points, list) or not points
                or any(not isinstance(p, str) or not p.strip() for p in points)):
            errors.append("each outline page needs title and substantive key_points")
    expected = [(s.get("id"), s.get("title")) for s in state.get("slides", []) if isinstance(s, dict)]
    if mappings != expected:
        errors.append("outline page order/IDs/titles must match slides")
    approval = outline.get("approval")
    if outline.get("status") == "approved":
        if (not isinstance(approval, dict) or approval.get("revision") != revision
                or not approval.get("evidence") or not approval.get("user_text")
                or approval.get("content_sha256") != outline_fingerprint(outline)):
            errors.append("outline approval missing or does not match current content")
    elif approval is not None:
        errors.append("clear stale outline approval when plan changes")
    return errors
