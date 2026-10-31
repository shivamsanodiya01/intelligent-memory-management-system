"""First-order page-to-page transition probabilities."""

from collections import defaultdict


class TransitionModel:
    """Count observed (previous_page -> next_page) pairs."""

    def __init__(self):
        self._counts = defaultdict(lambda: defaultdict(int))
        self._totals = defaultdict(int)

    def record(self, previous_page, next_page) -> None:
        """Store one observed transition."""
        self._counts[previous_page][next_page] += 1
        self._totals[previous_page] += 1

    def probability(self, previous_page, next_page) -> float:
        """
        P(next_page | previous_page).

        Returns 0.0 when that previous page has never been seen as a source.
        """
        total = self._totals.get(previous_page, 0)
        if total == 0:
            return 0.0
        return self._counts[previous_page].get(next_page, 0) / total

    def transition_scores(self, previous_page, pages: list) -> dict:
        """Probability of each candidate page following previous_page."""
        return {page: self.probability(previous_page, page) for page in pages}
