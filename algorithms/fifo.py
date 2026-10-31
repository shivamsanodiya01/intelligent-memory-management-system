"""FIFO (First-In First-Out) page replacement."""

from algorithms.common import (
    build_result,
    empty_result,
    error_result,
    make_step,
    validate_simulation_input,
)


def fifo(reference_string: list, frame_count: int) -> dict:
    """
    Replace the page that has been in memory for the longest time.

    New pages are inserted into the oldest frame slot. This is simple and
    fair, but it ignores whether an old page is still being used.
    """
    error = validate_simulation_input(reference_string, frame_count)
    if error:
        return error_result("FIFO", frame_count, reference_string or [], error)
    if not reference_string:
        return empty_result("FIFO", frame_count, reference_string)

    frames = [None] * frame_count
    insertion_order = []  # pages currently in memory, oldest first
    steps = []

    for index, page in enumerate(reference_string, start=1):
        if page in frames:
            steps.append(make_step(index, page, frames, "Hit"))
            continue

        replaced = None
        if None in frames:
            empty_slot = frames.index(None)
            frames[empty_slot] = page
            insertion_order.append(page)
        else:
            replaced = insertion_order.pop(0)
            victim_slot = frames.index(replaced)
            frames[victim_slot] = page
            insertion_order.append(page)

        steps.append(make_step(index, page, frames, "Fault", replaced))

    return build_result("FIFO", reference_string, frame_count, steps)
