"""Matplotlib charts for algorithm comparison."""

import matplotlib.pyplot as plt


ALGORITHM_COLORS = {
    "FIFO": "#10B981",
    "LRU": "#34D399",
    "Optimal": "#6EE7B7",
    "Predictive": "#059669",
}


def comparison_figures(results: list[dict]):
    """
    Build page-fault, hits-versus-faults, and frame-utilization charts.

    results: list of algorithm result dictionaries (invalid ones are skipped).
    """
    valid = [item for item in results if item and not item.get("error")]
    names = [item["algorithm"] for item in valid]
    faults = [item["page_faults"] for item in valid]
    hits = [item["page_hits"] for item in valid]
    colors = [ALGORITHM_COLORS.get(name, "#10B981") for name in names]

    fault_fig, fault_ax = plt.subplots(figsize=(7.5, 3.8))
    bars = fault_ax.bar(names, faults, color=colors)
    fault_ax.set_title("Page Faults (lower is better)")
    fault_ax.set_ylabel("Faults")
    fault_ax.bar_label(bars, padding=3)
    fault_fig.tight_layout()

    hit_fault_fig, hit_fault_ax = plt.subplots(figsize=(7.5, 3.8))
    positions = list(range(len(names)))
    bar_width = 0.36
    hit_bars = hit_fault_ax.bar(
        [position - bar_width / 2 for position in positions],
        hits,
        bar_width,
        label="Page hits",
        color="#10B981",
    )
    fault_bars = hit_fault_ax.bar(
        [position + bar_width / 2 for position in positions],
        faults,
        bar_width,
        label="Page faults",
        color="#52635A",
    )
    hit_fault_ax.set_title("Page Hits vs. Page Faults")
    hit_fault_ax.set_ylabel("References")
    hit_fault_ax.set_xticks(positions, names)
    hit_fault_ax.legend(frameon=False)
    hit_fault_ax.bar_label(hit_bars, padding=3)
    hit_fault_ax.bar_label(fault_bars, padding=3)
    hit_fault_fig.tight_layout()

    utilization = []
    for result in valid:
        steps = result.get("steps", [])
        frame_count = result.get("frame_count", 0)
        total_slots = len(steps) * frame_count
        occupied_slots = sum(
            sum(frame != "-" for frame in step["frames"])
            for step in steps
        )
        utilization.append(occupied_slots / total_slots * 100 if total_slots else 0)

    utilization_fig, utilization_ax = plt.subplots(figsize=(7.5, 3.4))
    utilization_bars = utilization_ax.bar(names, utilization, color=colors)
    utilization_ax.set_title("Average Memory Frame Utilization")
    utilization_ax.set_ylabel("Utilization (%)")
    utilization_ax.set_ylim(0, 100)
    utilization_ax.bar_label(utilization_bars, fmt="%.1f%%", padding=3)
    utilization_fig.tight_layout()

    return fault_fig, hit_fault_fig, utilization_fig
