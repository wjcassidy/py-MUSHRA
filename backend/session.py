from __future__ import annotations

import csv
import logging
import random
import secrets
import string
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from backend.config import Config

logger = logging.getLogger("py_mushra.session")

REFERENCE_LETTER = "R"
TARGET_SUFFIX = "target"


class StimuliError(Exception):
    pass


@dataclass
class Item:
    prefix: str
    target_path: Path
    condition_paths: list[Path]


@dataclass
class Page:
    prefix: str
    reference_path: Path
    # ordered list of (letter, path, is_hidden_reference)
    slots: list[tuple[str, Path, bool]]

    @property
    def eval_letters(self) -> list[str]:
        return [letter for letter, _, _ in self.slots]

    def path_for_letter(self, letter: str) -> Path:
        if letter == REFERENCE_LETTER:
            return self.reference_path
        for l, path, _ in self.slots:
            if l == letter:
                return path
        raise KeyError(letter)


@dataclass
class RatingRow:
    order: int
    page_index: int
    filename: str
    rating: float


def discover_items(stimuli_dir: Path) -> list[Item]:
    groups: dict[str, dict[str, Path]] = {}
    for wav_path in sorted(stimuli_dir.glob("*.wav")):
        stem = wav_path.stem
        if "_" not in stem:
            raise StimuliError(
                f"Stimulus file '{wav_path.name}' does not match the "
                f"'<prefix>_<suffix>.wav' naming convention."
            )
        prefix, suffix = stem.rsplit("_", 1)
        groups.setdefault(prefix, {})[suffix] = wav_path

    if not groups:
        raise StimuliError(f"No .wav files found in {stimuli_dir}")

    items: list[Item] = []
    bad_prefixes: list[str] = []
    for prefix, suffixes in groups.items():
        target = suffixes.pop(TARGET_SUFFIX, None)
        if target is None or not suffixes:
            bad_prefixes.append(prefix)
            continue
        items.append(Item(prefix=prefix, target_path=target, condition_paths=list(suffixes.values())))

    if bad_prefixes:
        raise StimuliError(
            "Each stimulus item needs exactly one '_target.wav' file plus at "
            f"least one other condition file. Offending item prefixes: {bad_prefixes}"
        )

    return items


def _build_half(items: list[Item], rng: random.Random) -> list[Page]:
    shuffled_items = items[:]
    rng.shuffle(shuffled_items)

    pages: list[Page] = []
    for item in shuffled_items:
        candidates = list(item.condition_paths) + [item.target_path]  # hidden reference copy
        rng.shuffle(candidates)
        letters = list(string.ascii_uppercase[: len(candidates)])
        slots = [
            (letter, path, path == item.target_path)
            for letter, path in zip(letters, candidates)
        ]
        pages.append(Page(prefix=item.prefix, reference_path=item.target_path, slots=slots))
    return pages


@dataclass
class Session:
    pages: list[Page]
    results_dir: Path
    seed: int
    page_index: int = 0
    _rows: list[RatingRow] = field(default_factory=list)
    _order_counter: int = 0

    @classmethod
    def build(cls, config: Config) -> "Session":
        seed = secrets.randbits(32)
        rng = random.Random(seed)
        logger.info("py-MUSHRA session random seed: %s", seed)

        items = discover_items(config.stimuli_dir)
        pages = _build_half(items, rng) + _build_half(items, rng)
        logger.info(
            "Discovered %d item(s), built %d page(s) across two halves", len(items), len(pages)
        )
        return cls(pages=pages, results_dir=config.results_dir, seed=seed)

    @property
    def total_pages(self) -> int:
        return len(self.pages)

    @property
    def is_finished(self) -> bool:
        return self.page_index >= self.total_pages

    @property
    def current_page(self) -> Page:
        if self.is_finished:
            raise IndexError("Session already finished")
        return self.pages[self.page_index]

    def public_page_state(self) -> dict:
        page = self.current_page
        return {
            "page_index": self.page_index,
            "total_pages": self.total_pages,
            "reference_letter": REFERENCE_LETTER,
            "letters": [REFERENCE_LETTER] + page.eval_letters,
        }

    def record_ratings(self, ratings: dict[str, float]) -> dict:
        page = self.current_page
        expected = set(page.eval_letters)
        got = set(ratings.keys())
        if got != expected:
            raise ValueError(f"Expected ratings for letters {sorted(expected)}, got {sorted(got)}")

        for letter, path, _ in page.slots:
            self._order_counter += 1
            self._rows.append(
                RatingRow(
                    order=self._order_counter,
                    page_index=self.page_index,
                    filename=path.name,
                    rating=ratings[letter],
                )
            )

        self.page_index += 1

        if self.is_finished:
            csv_filename = self._write_csv()
            return {"done": True, "csv_filename": csv_filename}
        return {"done": False, "page": self.public_page_state()}

    def _write_csv(self) -> str:
        self.results_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}.csv"
        out_path = self.results_dir / filename
        with out_path.open("w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["order", "page", "filename", "rating"])
            for row in self._rows:
                writer.writerow([row.order, row.page_index, row.filename, row.rating])
        logger.info("Wrote results to %s", out_path)
        return filename
