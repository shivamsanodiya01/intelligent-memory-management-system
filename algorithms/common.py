"""Shared helpers for page-replacement simulations."""

from typing import Any


def empty_result(algorithm: str, frame_count: int, reference_string: list) -> dict[str, Any]:
    """Return a consistent result when there is nothing to simulate."""
    return {
        "algorithm": algorithm,
        "frame_count": frame_count,
        "reference_string": list(reference_string),
        "page_faults": 0,
        "page_hits": 0,
        "hit_ratio": 0.0,
        "fault_ratio": 0.0,
        "steps": [],
        "error": None,
    }


def error_result(algorithm: str, frame_count: int, reference_string: list, message: str) -> dict[str, Any]:
    """Return a consistent result when input is invalid."""
    result = empty_result(algorithm, frame_count, reference_string)
    result["error"] = message
    return result


def validate_simulation_input(reference_string: list, frame_count: int) -> str | None:
    """Return an error message, or None if input is usable."""
    if frame_count is None or int(frame_count) <= 0:
        return "Number of frames must be greater than 0."
    if not reference_string:
        return "Reference string is empty. Enter at least one page number."
    return None


def format_frames(frames: list) -> list:
    """Convert empty frame slots to '-' for display."""
    return ["-" if page is None else page for page in frames]


def build_result(algorithm: str, reference_string: list, frame_count: int, steps: list[dict]) -> dict[str, Any]:
    """Build the common result dictionary used by every algorithm."""
    total = len(steps)
    page_faults = sum(1 for step in steps if step["status"] == "Fault")
    page_hits = total - page_faults
    hit_ratio = (page_hits / total) if total else 0.0
    fault_ratio = (page_faults / total) if total else 0.0
    return {
        "algorithm": algorithm,
        "frame_count": frame_count,
        "reference_string": list(reference_string),
        "page_faults": page_faults,
        "page_hits": page_hits,
        "hit_ratio": hit_ratio,
        "fault_ratio": fault_ratio,
        "steps": steps,
        "error": None,
    }


def make_step(
    step_number: int,
    page: Any,
    frames: list,
    status: str,
    replaced: Any = None,
    extra: dict | None = None,
) -> dict[str, Any]:
    """Create one simulation-table row."""
    step = {
        "step": step_number,
        "page": page,
        "frames": format_frames(frames),
        "status": status,
        "replaced": replaced if replaced is not None else "-",
    }
    if extra:
        step.update(extra)
    return step
