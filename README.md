# py-MUSHRA

A local MUSHRA-style listening test: a React UI drives a Python backend that
plays Ambisonic `.wav` stimuli in realtime and records ratings to a
timestamped CSV. All audio is rendered by the Python process straight to the
selected output device -- the browser never plays audio itself.

Python does not decode: it sends the raw Ambisonic channels (`num_channels`
in `config.yaml`, 25 for 4th order) to the output device, and an external
decoder renders them to the loudspeakers. (Hosting the IEM VST3s in Python via
dawdreamer/pedalboard left them stuck on a 4-in/4-out bus, so decoding moved
out of the app.)

## One-time setup

1. **Virtual audio device**. Any multichannel loopback device works, e.g.
   Pro Tools Audio Bridge 64 (installed with Pro Tools) or
   [BlackHole 64ch](https://existential.audio/blackhole/). Select it as the
   output device in the test UI.
2. **External decoder**. In Max, build a patcher that reads the Ambisonic
   channels from the loopback device and decodes them to the loudspeaker interface, e.g.
   `mc.adc~ 1-25` → `mcs.vst~ 25 25 SceneRotator` → `mcs.vst~ 25 48 AllRADecoder`
   → `mc.dac~ 1-48`. Set Max's input device to the loopback device and its output device
   to the loudspeaker interface (or use an Aggregate Device with drift
   correction). Check with meters that every loudspeaker receives signal.
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
