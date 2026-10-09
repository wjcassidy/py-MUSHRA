# py-MUSHRA

A local MUSHRA-style listening test: a React UI drives a Python backend that
plays Ambisonic `.wav` stimuli in realtime and records ratings to a
timestamped CSV. All audio is rendered by the Python process straight to the
selected output device; the browser never plays audio itself.

Python sends the raw Ambisonic channels (`num_channels`
in `config.yaml`, 25 for 4th order) to the output device, and an external Max/MSP
decoder renders them to the loudspeakers.

<img width="864" height="543" alt="Screenshot 2026-10-09 at 09 03 34" src="https://github.com/user-attachments/assets/b218f375-2fbf-4033-9b1c-26842ab36a3b" />

## Quick-Start Guide

### Install packages and set up virtual devices

1. **Backend**:
   ```
   python3 -m venv .venv
   ./.venv/bin/pip install -r requirements.txt
   ```
2. **Frontend**:
   ```
   source .venv/bin/activate
   nodeenv -p --node=lts
   cd frontend && npm install
   ```
   Activate `.venv` first: `nodeenv -p` installs into whichever venv is
   currently active. If it fails with `CERTIFICATE_VERIFY_FAILED` (python.org
   Python on macOS), run `/Applications/Python 3.x/Install Certificates.command`
   and retry. If you already have Node.js 20+ installed system-wide, you can
   skip the `nodeenv` line.
3. **Virtual audio device**: Any multichannel loopback device works, e.g.
   Pro Tools Audio Bridge 64 or
   [BlackHole 64ch](https://existential.audio/blackhole/). Select it as the
   output device in the test UI.
4. **External decoder**: Only required if you want live decoding (you can render the decoding into the stimulus files and skip this step). In `backend/decoder.maxpat` (Max/MSP 8 or 9) set the input device to the loopback device and the output device
   to the loudspeaker interface.

### Add your stimulus files 

Put `.wav` files in `stimuli/`, named `<prefix>_<suffix>.wav`. Files sharing
a prefix form one test page. Exactly one file per item must use the
suffix `target` (the reference); every other suffix is an anonymous
test condition. A hidden reference is automatically added to
each page and randomised among the lettered
 conditions.

Place any `.wav` files into `familiarisation/` to be presented to the participant
before the main test. They must listen to all of these before continuing.

### Running

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
source .venv/bin/activate && cd frontend && npm run dev
```
