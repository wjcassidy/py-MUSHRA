"""Plot mean ratings with 95% confidence intervals for each passive/target
combination (e.g. R1T5) in the MUSHRA results CSVs.

Defaults are set in the settings block below; command-line arguments override them.

Usage:
    python plotting/plot_means_and_confidence.py [--results-dir DIR] [--[no-]include-repeats]
                                                 [--[no-]split-signals] [--[no-]error-bars]
"""

import argparse

import matplotlib.pyplot as plt
import numpy as np

from common import (
    CONDITION_COLOURS, CONDITION_MARKERS, DEFAULT_RESULTS_DIR, GRID_COLOUR,
    add_common_args, load_ratings, mean_ci95, plot_layout, style_axis,
)
from exclusion_criteria import included_results

# Settings (defaults for the command-line arguments)
RESULTS_DIR = DEFAULT_RESULTS_DIR             # Folder containing the results CSVs
INCLUDE_REPEATS = False                       # Include repeated trials (repeat=1)
SPLIT_SIGNALS = False                          # One panel per excitation signal; False pools all signals
SHOW_ERROR_BARS = True                        # Draw 95% confidence interval error bars around the means


def plot(ratings, show_error_bars=True):
    signals, combinations, conditions = plot_layout(ratings)

    x = np.arange(len(combinations))
    offset_step = 0.18
    offsets = (np.arange(len(conditions)) - (len(conditions) - 1) / 2) * offset_step

    fig, axes = plt.subplots(
        len(signals), 1, sharex=True, squeeze=False,
        figsize=(max(8, 0.9 * len(combinations) + 2), 3.2 * len(signals) + 0.8),
    )
    axes = axes[:, 0]
    for ax, signal in zip(axes, signals):
        for condition, offset in zip(conditions, offsets):
            means, errors, xs = [], [], []
            for i, combination in enumerate(combinations):
                values = ratings[signal][combination].get(condition)
                if not values:
                    continue
                mean, half_width = mean_ci95(values)
                xs.append(x[i] + offset)
                means.append(mean)
                errors.append(half_width)
            ax.errorbar(
                xs, means, yerr=errors if show_error_bars else None,
                fmt=CONDITION_MARKERS.get(condition, "o"),
                color=CONDITION_COLOURS.get(condition),
                markersize=6, capsize=3, elinewidth=1.5, capthick=1.5,
                label=condition,
            )

        for boundary in x[:-1] + 0.5:
            ax.axvline(boundary, color=GRID_COLOUR, linewidth=0.8, zorder=0)

        style_axis(ax, signal, "Rating (mean ± 95% CI)" if show_error_bars else "Rating (mean)")

    axes[-1].set_xticks(x)
    axes[-1].set_xticklabels(combinations)
    axes[-1].set_xlim(-0.5, len(combinations) - 0.5)
    axes[-1].set_xlabel("Passive/target combination")
    axes[0].legend(title="Condition", loc="upper left", bbox_to_anchor=(1.01, 1), frameon=False)

    fig.tight_layout()
    plt.show()


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    add_common_args(parser, RESULTS_DIR, INCLUDE_REPEATS, SPLIT_SIGNALS)
    parser.add_argument("--error-bars", dest="show_error_bars", default=SHOW_ERROR_BARS,
                        action=argparse.BooleanOptionalAction,
                        help="Draw 95%% confidence interval error bars around the means (default: %(default)s)")
    args = parser.parse_args()

    results = included_results(args.results_dir)
    ratings = load_ratings(results, args.include_repeats, args.split_signals)
    if not ratings:
        raise SystemExit(f"No results found in {args.results_dir}")
    plot(ratings, args.show_error_bars)


if __name__ == "__main__":
    main()
