from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent


@dataclass
class Config:
    stimuli_dir: Path
    results_dir: Path
    plugin_path: Path | None
    plugin_preset_path: Path | None
    num_output_channels: int | None
    sample_rate: int
    block_size: int

    @classmethod
    def load(cls, path: Path = REPO_ROOT / "config.yaml") -> "Config":
        raw = yaml.safe_load(path.read_text())

        def resolve(value: str | None) -> Path | None:
            if not value:
                return None
            p = Path(value)
            return p if p.is_absolute() else REPO_ROOT / p

        return cls(
            stimuli_dir=resolve(raw["stimuli_dir"]),
            results_dir=resolve(raw["results_dir"]),
            plugin_path=resolve(raw.get("plugin_path")),
            plugin_preset_path=resolve(raw.get("plugin_preset_path")),
            num_output_channels=raw.get("num_output_channels"),
            sample_rate=int(raw["sample_rate"]),
            block_size=int(raw["block_size"]),
        )
