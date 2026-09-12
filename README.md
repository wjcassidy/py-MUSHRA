# py-MUSHRA

A local MUSHRA-style listening test: a React UI drives a Python backend that
loads Ambisonic `.wav` stimuli, decodes them in realtime through the IEM
AllRADecoder plugin to a loudspeaker array, and records ratings to a
timestamped CSV. All audio is rendered by the Python process straight to the
selected output device -- the browser never plays audio itself.

## One-time setup

1. **IEM AllRADecoder (VST3/AU)**. `pedalboard` (the Python VST host used
   here) only loads VST3 or Audio Unit plugins, not legacy VST2. Install a
   current [IEM Plug-in Suite](https://plugins.iem.at/) release (ships VST3 +
   AU on macOS), then set `plugin_path` in `config.yaml` to the installed
   `AllRADecoder.vst3` (or `.component`) path.
2. **Decoder / loudspeaker layout config**. Once you have an AllRADecoder
   configuration for your array, set `plugin_preset_path` in `config.yaml` to
   it (a `.vstpreset` export). Until then the engine runs with the plugin's
   default state, or in a passthrough fallback if no plugin is configured at
   all.
3. **Backend**:
   ```
   python3 -m venv .venv
   ./.venv/bin/pip install -r requirements.txt
   ```
4. **Frontend**:
   ```
   cd frontend && npm install
   ```

## Stimuli

Put `.wav` files in `Stimuli/`, named `<prefix>_<suffix>.wav`. Files sharing
a prefix form one MUSHRA page/item. Exactly one file per item must use the
suffix `target` (the true reference); every other suffix is an anonymous
test condition. A hidden copy of the reference is automatically added to
each page and randomized among the lettered conditions.

## Running

Run `./run_test` from the repo root. It stops any previous instance,
starts the backend and frontend, and opens the browser automatically.
Press Ctrl+C to stop both servers.

Run it again before each participant: restarting the backend picks a fresh
random seed (logged on startup) and reshuffles item order and
condition/hidden-reference letter assignment, which is how the test resets
for the next participant. Results are written to `results/<timestamp>.csv`
when a test session finishes.

To run the servers manually instead, in separate terminals:

```
./.venv/bin/uvicorn backend.main:app --port 8000
```

```
cd frontend && npm run dev
```
