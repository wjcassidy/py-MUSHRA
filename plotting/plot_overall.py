"""Plot the overall comparison of conditions, pooling the ratings over all
passive/target combinations (e.g. R1T5) in the MUSHRA results CSVs.

Shows a violin plot of the rating distribution for each condition, with the mean
(and optionally the 95% confidence interval) marked, grouped by excitation signal.

Defaults are set in the settings block below; command-line arguments override them.

Usage:
    python plotting/plot_overall.py [--results-dir DIR] [--[no-]include-repeats]
                                    [--[no-]split-signals] [--[no-]error-bars]
"""

import argparse

import matplotlib.pyplot as plt
import numpy as np

from common import (
    CONDITION_COLOURS, CONDITION_MARKERS, DEFAULT_RESULTS_DIR, GRID_COLOUR, SIGNAL_NAMES,
    add_common_args, load_ratings, mean_ci95, plot_layout, style_axis,
)
from exclusion_criteria import included_results

# Settings (defaults for the command-line arguments)
RESULTS_DIR = DEFAULT_RESULTS_DIR             # Folder containing the results CSVs
INCLUDE_REPEATS = False                       # Include repeated trials (repeat=1)
SPLIT_SIGNALS = True                          # One group per excitation signal; False pools all signals
SHOW_ERROR_BARS = True                        # Draw 95% confidence interval error bars around the means


def plot(ratings, show_error_bars=True):
    signals, combinations, conditions = plot_layout(ratings)

    x = np.arange(len(signals))
    offset_step = 0.2
    offsets = (np.arange(len(conditions)) - (len(conditions) - 1) / 2) * offset_step
    violin_width = 0.18

    fig, ax = plt.subplots(figsize=(max(5, 2.2 * len(signals) + 2.5), 4.5))
    for condition, offset in zip(conditions, offsets):
        colour = CONDITION_COLOURS.get(condition)
        marker = CONDITION_MARKERS.get(condition, "o")
        means, errors, xs = [], [], []
        for i, signal in enumerate(signals):
            values = [v for combination in combinations
                      for v in ratings[signal][combination].get(condition, [])]
            if not values:
                continue
            centre = x[i] + offset
            if np.ptp(values) > 0:
                violin = ax.violinplot(values, positions=[centre], widths=violin_width, showextrema=False)
                for body in violin["bodies"]:
                    body.set_facecolor(colour)
                    body.set_edgecolor(colour)
                    body.set_alpha(0.35)
                    body.set_zorder(1)
            else:
                # The density estimate is undefined when every rating is identical, so draw a flat line
                ax.plot([centre - violin_width / 2, centre + violin_width / 2], [values[0], values[0]],
                        color=colour, alpha=0.6, linewidth=2, zorder=1)
            mean, half_width = mean_ci95(values)
            xs.append(centre)
            means.append(mean)
            errors.append(half_width)
        ax.errorbar(
            xs, means, yerr=errors if show_error_bars else None,
            fmt=marker, color=colour, markeredgecolor="white", markeredgewidth=0.8,
            markersize=7, capsize=3, elinewidth=1.6, capthick=1.6,
            label=condition, zorder=3,
        )

    for boundary in x[:-1] + 0.5:
        ax.axvline(boundary, color=GRID_COLOUR, linewidth=0.8, zorder=0)

    style_axis(ax, "All passive/target combinations",
               "Rating (violin, mean ± 95% CI)" if show_error_bars else "Rating (violin, mean)")
    ax.set_xticks(x)
    ax.set_xticklabels([SIGNAL_NAMES.get(s, s) for s in signals])
    ax.set_xlim(-0.5, len(signals) - 0.5)
    ax.set_xlabel("Excitation signal")
    ax.legend(title="Condition", loc="upper left", bbox_to_anchor=(1.01, 1), frameon=False)

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
