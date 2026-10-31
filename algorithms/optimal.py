"""Optimal page replacement (Belady's algorithm)."""

from algorithms.common import (
    build_result,
    empty_result,
    error_result,
    make_step,
    validate_simulation_input,
)


def _next_use_distance(page, future_references: list) -> int:
    """How far ahead this page is used again. Larger means used later."""
    try:
        return future_references.index(page)
    except ValueError:
        return float("inf")


def optimal(reference_string: list, frame_count: int) -> dict:
    """
    Replace the page that will not be needed for the longest time in the future.

    Optimal needs the full future reference string, so it is a theoretical
    benchmark, not a practical OS algorithm. Real systems cannot see future
    page requests.
    """
    error = validate_simulation_input(reference_string, frame_count)
    if error:
        return error_result("Optimal", frame_count, reference_string or [], error)
    if not reference_string:
        return empty_result("Optimal", frame_count, reference_string)

    frames = [None] * frame_count
    steps = []

    for index, page in enumerate(reference_string, start=1):
        if page in frames:
            steps.append(make_step(index, page, frames, "Hit"))
            continue

        replaced = None
        if None in frames:
            empty_slot = frames.index(None)
            frames[empty_slot] = page
        else:
            future = reference_string[index:]
            resident_pages = [p for p in frames if p is not None]
            # Farthest next use wins. If two pages are never used again,
            # the left-most frame is chosen so the result is deterministic.
            replaced = max(
                resident_pages,
                key=lambda p: (_next_use_distance(p, future), -frames.index(p)),
            )
            victim_slot = frames.index(replaced)
            frames[victim_slot] = page

        steps.append(make_step(index, page, frames, "Fault", replaced))

    return build_result("Optimal", reference_string, frame_count, steps)
