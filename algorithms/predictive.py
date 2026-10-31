"""Rule-based predictive page replacement."""

from algorithms.common import (
    build_result,
    empty_result,
    error_result,
    make_step,
    validate_simulation_input,
)
from prediction.frequency import frequency_scores
from prediction.recency import recency_scores
from prediction.transition import TransitionModel


DEFAULT_WEIGHTS = {"alpha": 0.4, "beta": 0.4, "gamma": 0.2}


def _normalize_weights(alpha: float, beta: float, gamma: float) -> tuple[float, float, float]:
    """Keep relative weights, but scale them so they sum to 1 when possible."""
    total = alpha + beta + gamma
    if total <= 0:
        return 1.0 / 3.0, 1.0 / 3.0, 1.0 / 3.0
    return alpha / total, beta / total, gamma / total


def _prediction_score(freq: float, recency: float, transition: float, weights: tuple[float, float, float]) -> float:
    alpha, beta, gamma = weights
    return alpha * freq + beta * recency + gamma * transition


def _choose_victim(frames: list, scores: dict) -> object:
    """
    Replace the resident page with the lowest prediction score.

    Lower score = less likely to be needed soon.
    Ties are broken by the left-most frame so the choice is deterministic.
    """
    resident_pages = [page for page in frames if page is not None]
    return min(resident_pages, key=lambda page: (scores[page], frames.index(page)))


def predictive(reference_string: list, frame_count: int, weights: dict | None = None) -> dict:
    """
    Predict which loaded page is least likely to be needed soon.

    The score uses only history seen so far (no future references):
        score = alpha * frequency + beta * recency + gamma * P(page | previous page)

    This is a deterministic rule-based predictor, not machine learning.
    It can beat FIFO/LRU on some strings and lose on others. Optimal remains
    the theoretical lower bound on faults because it can see the future.
    """
    error = validate_simulation_input(reference_string, frame_count)
    if error:
        return error_result("Predictive", frame_count, reference_string or [], error)
    if not reference_string:
        return empty_result("Predictive", frame_count, reference_string)

    raw = {**DEFAULT_WEIGHTS, **(weights or {})}
    norm_weights = _normalize_weights(float(raw["alpha"]), float(raw["beta"]), float(raw["gamma"]))

    frames = [None] * frame_count
    page_counts = {}
    last_used = {}
    transitions = TransitionModel()
    previous_page = None
    steps = []

    for index, page in enumerate(reference_string, start=1):
        extra = {"prediction": "-"}

        if page in frames:
            steps.append(make_step(index, page, frames, "Hit", extra=extra))
        else:
            replaced = None
            if None in frames:
                empty_slot = frames.index(None)
                frames[empty_slot] = page
            else:
                resident_pages = [p for p in frames if p is not None]
                freq = frequency_scores(page_counts, resident_pages)
                recency = recency_scores(last_used, resident_pages, index)
                trans = transitions.transition_scores(previous_page, resident_pages)
                scores = {
                    p: _prediction_score(freq[p], recency[p], trans[p], norm_weights)
                    for p in resident_pages
                }
                replaced = _choose_victim(frames, scores)
                frames[frames.index(replaced)] = page

                extra["prediction"] = (
                    f"Victim {replaced} (lowest score {scores[replaced]:.3f}). "
                    + "; ".join(
                        f"{p}: F={freq[p]:.2f} R={recency[p]:.2f} T={trans[p]:.2f} S={scores[p]:.3f}"
                        for p in resident_pages
                    )
                )

            steps.append(make_step(index, page, frames, "Fault", replaced, extra))

        # Update history after the decision so the current request is not leaked.
        page_counts[page] = page_counts.get(page, 0) + 1
        last_used[page] = index
        if previous_page is not None:
            transitions.record(previous_page, page)
        previous_page = page

    result = build_result("Predictive", reference_string, frame_count, steps)
    result["weights"] = {
        "alpha": norm_weights[0],
        "beta": norm_weights[1],
        "gamma": norm_weights[2],
        "raw": {"alpha": float(raw["alpha"]), "beta": float(raw["beta"]), "gamma": float(raw["gamma"])},
    }
    return result
