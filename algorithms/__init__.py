from algorithms.fifo import fifo
from algorithms.lru import lru
from algorithms.optimal import optimal
from algorithms.predictive import DEFAULT_WEIGHTS, predictive

ALGORITHMS = {
    "FIFO": fifo,
    "LRU": lru,
    "Optimal": optimal,
    "Predictive": predictive,
}

__all__ = ["fifo", "lru", "optimal", "predictive", "ALGORITHMS", "DEFAULT_WEIGHTS"]
