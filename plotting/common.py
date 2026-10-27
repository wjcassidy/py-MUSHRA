"""Shared loading and styling for the MUSHRA results plotting scripts."""

import argparse
import csv
import re
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy import stats

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_RESULTS_DIR = REPO_ROOT / "results"

FILENAME_RE = re.compile(r"^(R\d+T\d+)_([^_]+)_([^_]+)\.wav$")

# Panel title used when ratings are pooled across excitation signals
ALL_SIGNALS = "All signals"
# Display names for the excitation signal names used in the stimulus filenames
SIGNAL_NAMES = {"Beet": "Classical", "Hand": "Handclaps", "Slow": "Pop"}

CONDITIONS = ["target", "fulloptim", "geq", "passive"]
# Sampled from matplotlib's magma colormap at np.linspace(0.15, 0.8, 4)
CONDITION_COLOURS = {
    "target": "#251255",
    "fulloptim": "#7e2482",
    "geq": "#d8456c",
    "passive": "#fe9f6d",
}
CONDITION_MARKERS = {"target": "o", "fulloptim": "s", "geq": "D", "passive": "^"}
GRID_COLOUR = "#e5e4df"


def load_ratings(paths, include_repeats, split_signals=True):
    """Return {signal: {combination: {condition: [ratings]}}} pooled over the given results CSVs.

    If split_signals is False, all excitation signals are pooled under ALL_SIGNALS.
    """
    ratings = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    for path in paths:
        with open(path, newline="") as f:
            for row in csv.DictReader(f):
                if not include_repeats and row["repeat"] == "1":
                    continue
                match = FILENAME_RE.match(row["filename"])
                if match is None:
                    print(f"Skipping unrecognised filename {row['filename']} in {path.name}")
                    continue
                combination, signal, condition = match.groups()
                key = signal if split_signals else ALL_SIGNALS
                ratings[key][combination][condition].append(float(row["rating"]))
    return ratings


def mean_ci95(values):
    values = np.asarray(values)
    mean = values.mean()
    if len(values) < 2:
        return mean, 0.0
    half_width = stats.t.ppf(0.975, len(values) - 1) * stats.sem(values)
    return mean, half_width


def combination_sort_key(combination):
    r, t = map(int, re.findall(r"\d+", combination))
    return r, t


def plot_layout(ratings):
    """Return (signals, combinations, conditions) in display order."""
    signals = sorted(ratings)
    combinations = sorted({k for s in signals for k in ratings[s]}, key=combination_sort_key)
    present = {c for s in signals for k in ratings[s] for c in ratings[s][k]}
    conditions = [c for c in CONDITIONS if c in present] + sorted(present - set(CONDITIONS))
    return signals, combinations, conditions


def style_axis(ax, signal, ylabel):
    ax.set_title(SIGNAL_NAMES.get(signal, signal), loc="left", fontsize=11)
    # Leave headroom so points/CIs at the ends of the 0-100 scale aren't clipped
    ax.set_ylim(-10, 110)
    ax.set_yticks(range(0, 101, 20))
    ax.set_ylabel(ylabel)
    ax.yaxis.grid(True, color=GRID_COLOUR, linewidth=0.8)
    ax.set_axisbelow(True)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)


def add_common_args(parser, results_dir, include_repeats, split_signals):
    """Add the arguments shared by all plotting scripts, using the given defaults."""
    parser.add_argument("--results-dir", default=str(results_dir),
                        help="Folder containing the results CSVs (default: %(default)s)")
    parser.add_argument("--include-repeats", default=include_repeats, action=argparse.BooleanOptionalAction,
                        help="Include repeated trials (repeat=1) (default: %(default)s)")
    parser.add_argument("--split-signals", default=split_signals, action=argparse.BooleanOptionalAction,
                        help="One panel per excitation signal; otherwise all signals are pooled "
                             "into a single panel (default: %(default)s)")
