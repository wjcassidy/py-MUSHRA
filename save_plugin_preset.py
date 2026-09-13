#!/usr/bin/env python3
"""Opens the AllRADecoder plugin's native editor so its loudspeaker layout can be
configured by hand, then writes the resulting state out as a .vstpreset file once
the editor window is closed.

Usage:
    .venv/bin/python3 save_plugin_preset.py <output.vstpreset> [--preset <existing.vstpreset>]

The plugin itself has no "save preset" option in its UI, but pedalboard can read
back the plugin's internal state (in .vstpreset format) after you've configured it
in the editor -- this script does that read-back and write for you.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pedalboard

from backend.config import Config


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("output", type=Path, help="Path to write the resulting .vstpreset file to.")
    parser.add_argument(
        "--preset",
        type=Path,
        default=None,
        help="Existing .vstpreset file to load into the editor as a starting point.",
    )
    args = parser.parse_args()

    config = Config.load()
    if not config.plugin_path:
        raise SystemExit("config.yaml has no plugin_path set.")

    plugin = pedalboard.load_plugin(str(config.plugin_path))
    print(f"Loaded plugin: {plugin.name}")

    if args.preset:
        if not args.preset.exists():
            raise SystemExit(f"--preset file not found: {args.preset}")
        plugin.load_preset(str(args.preset))
        print(f"Loaded starting preset: {args.preset}")

    print("Opening editor -- configure the loudspeaker layout, then close the window to save.")
    plugin.show_editor()

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(plugin.preset_data)
    print(f"Saved preset to: {args.output}")


if __name__ == "__main__":
    main()
