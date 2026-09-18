"""Compact read-only design gate and measured text preflight. No PPT engine."""
import argparse
import hashlib
import json
import math
from pathlib import Path
from validate_state import production_errors, safe_path, validate


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def digest_file(root, value):
    if not safe_path(value):
        raise ValueError("design paths must be project-relative")
    target = (root / value).resolve()
    if not target.is_relative_to(root.resolve()) or not target.is_file():
        raise ValueError("design file missing or outside project")
    with target.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def design_fingerprint(state, slide_id, root):
    slide = next((s for s in state["slides"] if s["id"] == slide_id), None)
    if slide is None:
        raise ValueError("unknown slide")
    design = slide.get("design")
    if not isinstance(design, dict) or type(design.get("revision")) is not int or design["revision"] < 1:
        raise ValueError("positive design revision required")
    return {"revision": design["revision"],
            "image_sha256": digest_file(root, design.get("image")),
            "brief_sha256": digest_file(root, design.get("brief"))}


def reconstruction_errors(state, slide_id, root):
    errors = validate(state, root)
    if not errors:
        errors = production_errors(state, slide_id)
    if errors:
        return errors
    try:
        fingerprint = design_fingerprint(state, slide_id, root)
        slide = next(s for s in state["slides"] if s["id"] == slide_id)
        approval = slide["design"].get("approval")
        if not isinstance(approval, dict):
            return ["show the design and wait for explicit user confirmation"]
        if any(approval.get(key) != value for key, value in fingerprint.items()):
            errors.append("design approval is stale: image, brief or revision changed")
        for key in ("user_text", "evidence"):
            if not isinstance(approval.get(key), str) or not approval[key].strip():
                errors.append(f"actual user approval {key} required")
    except (ValueError, OSError) as exc:
        errors.append(str(exc))
    return errors


def number(value):
    return type(value) in (int, float) and math.isfinite(value)


def preflight(data):
    if not isinstance(data, dict):
        raise ValueError("metrics must be an object")
    canvas, texts = data.get("canvas", {}), data.get("texts")
    if not isinstance(canvas, dict) or not all(number(canvas.get(k)) and canvas[k] > 0 for k in ("width", "height")):
        raise ValueError("positive canvas width and height required")
    source = data.get("measurement_source")
    if not isinstance(source, str) or not source.strip() or not isinstance(texts, list) or not texts:
        raise ValueError("actual measurement source and nonempty texts required")
    errors, ids = [], set()
    for item in texts:
        if not isinstance(item, dict):
            raise ValueError("text metrics must be objects")
        sid, box = item.get("id"), item.get("box")
        if not isinstance(sid, str) or not sid or sid in ids:
            raise ValueError("unique text IDs required")
        ids.add(sid)
        if not isinstance(box, list) or len(box) != 4 or not all(number(v) for v in box):
            raise ValueError(f"{sid}: finite four-value box required")
        x, y, w, h = box
        if w <= 0 or h <= 0 or x < 0 or y < 0 or x+w > canvas["width"] or y+h > canvas["height"]:
            errors.append(f"{sid}: invalid or out-of-canvas text box")
        for key, capacity in (("measured_width", w), ("measured_height", h)):
            value = item.get(key)
            if not number(value) or value < 0:
                raise ValueError(f"{sid}: actual nonnegative {key} required")
            if value > capacity:
                errors.append(f"{sid}: {key} overflows by {value-capacity:g}")
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("fingerprint", "reconstruct-check", "preflight"))
    parser.add_argument("input", type=Path)
    parser.add_argument("--slide")
    args = parser.parse_args()
    try:
        data = read_json(args.input)
        result = {}
        if args.command == "preflight":
            errors = preflight(data)
        else:
            errors = validate(data, args.input.parent)
            if not args.slide:
                raise ValueError("--slide is required")
            if not errors and args.command == "fingerprint":
                result["fingerprint"] = design_fingerprint(data, args.slide, args.input.parent)
            elif not errors:
                errors = reconstruction_errors(data, args.slide, args.input.parent)
        result.update(ok=not errors, errors=errors)
        code = 1 if errors else 0
    except (ValueError, OSError, TypeError, KeyError) as exc:
        result, code = {"ok": False, "errors": [str(exc)]}, 2
    print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
