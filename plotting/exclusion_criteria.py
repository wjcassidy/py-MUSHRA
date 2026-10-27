"""Decide which subjects' results are included in the analysis.

Every plotting script calls included_results() to get the results CSVs that pass
the criteria below. Run this script on its own to see how many subjects are
included and excluded with the current settings, and why.

Current criteria:
  - Hidden reference: a rating of the hidden reference ("target" condition) below
    HIDDEN_REF_MIN_RATING counts as a miss; subjects with more than
    HIDDEN_REF_MAX_MISSES misses are excluded.

Usage:
    python plotting/exclusion_criteria.py [--results-dir DIR]
"""

import argparse
import csv
from pathlib import Path

from common import DEFAULT_RESULTS_DIR, FILENAME_RE

# Settings
HIDDEN_REF_CONDITION = "target"               # Condition name of the hidden reference
HIDDEN_REF_MIN_RATING = 90                   # Hidden reference ratings below this count as a miss
HIDDEN_REF_MAX_MISSES = 5                  # Exclude subjects with more misses than this
HIDDEN_REF_INCLUDE_REPEATS = True             # Count misses on repeated trials (repeat=1) as well


def hidden_reference_misses(rows):
    """Return the hidden reference ratings below HIDDEN_REF_MIN_RATING."""
    misses = []
    for row in rows:
        if not HIDDEN_REF_INCLUDE_REPEATS and row["repeat"] == "1":
            continue
        match = FILENAME_RE.match(row["filename"])
        if match is None or match.group(3) != HIDDEN_REF_CONDITION:
            continue
        rating = float(row["rating"])
        if rating < HIDDEN_REF_MIN_RATING:
            misses.append(rating)
    return misses


def exclusion_reasons(rows):
    """Return a list of reasons for excluding a subject (empty if included)."""
    reasons = []
    misses = hidden_reference_misses(rows)
    if len(misses) > HIDDEN_REF_MAX_MISSES:
        reasons.append(f"{len(misses)} hidden reference ratings < {HIDDEN_REF_MIN_RATING} "
                       f"(max {HIDDEN_REF_MAX_MISSES})")
    return reasons


def evaluate(results_dir):
    """Return {path: [exclusion reasons]} for every results CSV in results_dir."""
    evaluation = {}
    for path in sorted(Path(results_dir).glob("*.csv")):
        with open(path, newline="") as f:
            evaluation[path] = exclusion_reasons(list(csv.DictReader(f)))
    return evaluation


def included_results(results_dir, verbose=True):
    """Return the results CSVs of the subjects that pass the exclusion criteria."""
    evaluation = evaluate(results_dir)
    included = [path for path, reasons in evaluation.items() if not reasons]
    if verbose:
        print(f"Exclusion criteria: {len(included)} subjects included, "
              f"{len(evaluation) - len(included)} excluded")
    return included


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--results-dir", default=str(DEFAULT_RESULTS_DIR),
                        help="Folder containing the results CSVs (default: %(default)s)")
    args = parser.parse_args()

    evaluation = evaluate(args.results_dir)
    if not evaluation:
        raise SystemExit(f"No results found in {args.results_dir}")

    for path, reasons in evaluation.items():
        status = "EXCLUDED" if reasons else "included"
        print(f"{path.stem}: {status}" + (f" ({'; '.join(reasons)})" if reasons else ""))

    excluded = sum(1 for reasons in evaluation.values() if reasons)
    print(f"\n{len(evaluation) - excluded} subjects included, {excluded} excluded "
          f"(of {len(evaluation)})")


if __name__ == "__main__":
    main()
