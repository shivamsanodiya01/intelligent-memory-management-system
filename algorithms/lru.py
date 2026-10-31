"""LRU (Least Recently Used) page replacement."""

from algorithms.common import (
    build_result,
    empty_result,
    error_result,
    make_step,
    validate_simulation_input,
)


def lru(reference_string: list, frame_count: int) -> dict:
    """
    Replace the page that has not been used for the longest time.

    LRU uses temporal locality: a page used recently is more likely to be
    used again soon than a page that has been idle.
    """
    error = validate_simulation_input(reference_string, frame_count)
    if error:
        return error_result("LRU", frame_count, reference_string or [], error)
    if not reference_string:
        return empty_result("LRU", frame_count, reference_string)

    frames = [None] * frame_count
    last_used = {}  # page -> last reference step number
    steps = []

    for index, page in enumerate(reference_string, start=1):
        if page in frames:
            last_used[page] = index
            steps.append(make_step(index, page, frames, "Hit"))
            continue

        replaced = None
        if None in frames:
            empty_slot = frames.index(None)
            frames[empty_slot] = page
        else:
            # Resident page with the oldest last-use time is the victim.
            resident_pages = [p for p in frames if p is not None]
            replaced = min(resident_pages, key=lambda p: last_used[p])
            victim_slot = frames.index(replaced)
            frames[victim_slot] = page

        last_used[page] = index
        steps.append(make_step(index, page, frames, "Fault", replaced))

    return build_result("LRU", reference_string, frame_count, steps)
