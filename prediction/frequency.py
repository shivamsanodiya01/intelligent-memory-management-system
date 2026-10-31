"""Frequency scores from how often each page has appeared so far."""

import numpy as np


def frequency_scores(page_counts: dict, pages: list) -> dict:
    """
    Return a 0-1 score for each page.

    A page that appeared more often in the history gets a higher score.
    Scores are divided by the maximum count among the given pages so they
    stay in a comparable range.
    """
    if not pages:
        return {}
    counts = np.array([page_counts.get(page, 0) for page in pages], dtype=float)
    max_count = float(np.max(counts)) if counts.size else 0.0
    if max_count == 0:
        return {page: 0.0 for page in pages}
    return {page: float(count / max_count) for page, count in zip(pages, counts)}
