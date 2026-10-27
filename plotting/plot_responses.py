"""Plot every individual rating for each passive/target combination (e.g. R1T5)
in the MUSHRA results CSVs, as jittered points per condition with a median line.

Defaults are set in the settings block below; command-line arguments override them.

Usage:
    python plotting/plot_responses.py [--results-dir DIR] [--[no-]include-repeats]
                                      [--[no-]split-signals]
"""

import argparse

import matplotlib.pyplot as plt
import numpy as np

from common import (
    CONDITION_COLOURS, CONDITION_MARKERS, DEFAULT_RESULTS_DIR, GRID_COLOUR,
    add_common_args, load_ratings, plot_layout, style_axis,
)
from exclusion_criteria import included_results

# Settings (defaults for the command-line arguments)
RESULTS_DIR = DEFAULT_RESULTS_DIR             # Folder containing the results CSVs
INCLUDE_REPEATS = False                       # Include repeated trials (repeat=1)
SPLIT_SIGNALS = False                          # One panel per excitation signal; False pools all signals


def plot(ratings):
    signals, combinations, conditions = plot_layout(ratings)

    x = np.arange(len(combinations))
    offset_step = 0.2
    offsets = (np.arange(len(conditions)) - (len(conditions) - 1) / 2) * offset_step
    jitter_width = 0.06
    median_half_width = 0.08
    # Fixed seed so the jitter is the same every time the plot is regenerated
    rng = np.random.default_rng(0)

    fig, axes = plt.subplots(
        len(signals), 1, sharex=True, squeeze=False,
        figsize=(max(8, 0.9 * len(combinations) + 2), 3.2 * len(signals) + 0.8),
    )
    axes = axes[:, 0]
    for ax, signal in zip(axes, signals):
        for condition, offset in zip(conditions, offsets):
            colour = CONDITION_COLOURS.get(condition)
            xs, ys = [], []
            for i, combination in enumerate(combinations):
                values = ratings[signal][combination].get(condition)
                if not values:
                    continue
                centre = x[i] + offset
                xs.extend(centre + rng.uniform(-jitter_width, jitter_width, len(values)))
                ys.extend(values)
                median = np.median(values)
                ax.plot([centre - median_half_width, centre + median_half_width], [median, median],
                        color=colour, linewidth=2, zorder=3)
            ax.scatter(
                xs, ys,
                marker=CONDITION_MARKERS.get(condition, "o"),
                color=colour, alpha=0.55, s=18, linewidths=0,
                label=condition, zorder=2,
            )

        for boundary in x[:-1] + 0.5:
            ax.axvline(boundary, color=GRID_COLOUR, linewidth=0.8, zorder=0)

        style_axis(ax, signal, "Rating (line = median)")

    axes[-1].set_xticks(x)
    axes[-1].set_xticklabels(combinations)
    axes[-1].set_xlim(-0.5, len(combinations) - 0.5)
    axes[-1].set_xlabel("Passive/target combination")
    legend = axes[0].legend(title="Condition", loc="upper left", bbox_to_anchor=(1.01, 1), frameon=False)
    for handle in legend.legend_handles:
        handle.set_alpha(1)

    fig.tight_layout()
    plt.show()


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    add_common_args(parser, RESULTS_DIR, INCLUDE_REPEATS, SPLIT_SIGNALS)
    args = parser.parse_args()

    results = included_results(args.results_dir)
    ratings = load_ratings(results, args.include_repeats, args.split_signals)
    if not ratings:
        raise SystemExit(f"No results found in {args.results_dir}")
    plot(ratings)


if __name__ == "__main__":
    main()
