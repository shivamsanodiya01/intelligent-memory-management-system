"""Recency scores from how recently each page was last used."""

import numpy as np


def recency_scores(last_used: dict, pages: list, current_time: int) -> dict:
    """
    Return a 0-1 score for each page.

    More recently used pages get higher scores. Age is (current_time - last_used).
    The newest resident page scores 1.0 and the oldest scores 0.0 after
    normalization. If every page has the same age, all scores are 1.0.
    """
    if not pages:
        return {}

    ages = np.array(
        [max(current_time - last_used.get(page, 0), 0) for page in pages],
        dtype=float,
    )
    max_age = float(np.max(ages))
    min_age = float(np.min(ages))
    span = max_age - min_age
    if span == 0:
        return {page: 1.0 for page in pages}

    # Smaller age => higher recency.
    normalized = 1.0 - ((ages - min_age) / span)
    return {page: float(score) for page, score in zip(pages, normalized)}
