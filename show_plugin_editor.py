#!/usr/bin/env python3
"""Loads the AllRADecoder plugin + preset from config.yaml and opens its native
editor window, so the loudspeaker layout/decoder state can be checked visually.
Close the window to exit."""

from __future__ import annotations

import pedalboard

from backend.config import Config


def main() -> None:
    config = Config.load()
    if not config.plugin_path:
        raise SystemExit("config.yaml has no plugin_path set.")

    plugin = pedalboard.load_plugin(str(config.plugin_path))
    print(f"Loaded plugin: {plugin.name}")

    if config.plugin_preset_path and config.plugin_preset_path.exists():
        plugin.load_preset(str(config.plugin_preset_path))
        print(f"Loaded preset: {config.plugin_preset_path}")
    else:
        print("No plugin_preset_path configured (or file missing) -- showing plugin defaults.")

    plugin.show_editor()


if __name__ == "__main__":
    main()
