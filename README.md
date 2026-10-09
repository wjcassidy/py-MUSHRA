# py-MUSHRA

A local MUSHRA-style listening test: a React UI drives a Python backend that plays Ambisonic `.wav` stimuli in realtime and records ratings to a timestamped CSV. All audio is rendered by the Python process straight to the selected output device; the browser never plays audio itself.

Python sends the raw Ambisonic channels (`num_channels` in `config.yaml`, 25 for 4th order) to the output device, and an external Max/MSP decoder renders them to the loudspeakers.

<img width="864" height="543" alt="Screenshot 2026-10-09 at 09 03 34" src="https://github.com/user-attachments/assets/b218f375-2fbf-4033-9b1c-26842ab36a3b" />

## Quick-Start Guide

### Set up virtual environment and install packages

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
   cd ../
   ```
   Activate `.venv` first: `nodeenv -p` installs into whichever venv is currently active. If it fails with `CERTIFICATE_VERIFY_FAILED` (python.org Python on macOS), run `/Applications/Python 3.x/Install Certificates.command` and retry. If you already have Node.js 20+ installed system-wide, you can skip the `nodeenv` line.

### Optional: Set up live Ambisonics decoding
If you render the loudspeaker decoding into the stimulus files, you can skip these steps.
1. **Virtual audio device**: Any multichannel loopback device works, e.g. Pro Tools Audio Bridge 64 or [BlackHole 64ch](https://existential.audio/blackhole/). This will be selected as the output device in the test UI.
2. **External decoder**: In `backend/decoder.maxpat` (Max/MSP 8 or 9) set the input device to the loopback device and the output device to the loudspeaker interface.

### Add your stimulus files 

1. Create the folders `stimuli` and `familiarisation` on the top level.

2. Put `.wav` files in `stimuli/`, named `<prefix>_[...]_<suffix>.wav`. Files sharing a prefix form one test page. Exactly one file per item must use the suffix `target` (the reference); every other suffix is an anonymous test condition. A hidden reference is automatically added to each page and randomised among the lettered conditions.

3. Place any `.wav` files into `familiarisation/` to be presented to the participant before the main test. They'll need to listen to all of these before continuing.

### Running the test

1. Run `./run_test` from the repo root. It stops any previous instance, starts the backend and frontend, and opens the browser automatically. Use Ctrl+C to stop both servers.

2. Select your output device (use loopback device if decoding with Max, otherwise select your loudspeaker interface). The volume slider can be adjusted during the familiarisation but will lock for the main test.

In this example, I've set up an aggregate device called "py-MUSHRA" which applies drift correction to the Pro Tools bridge.
<img width="864" height="52" alt="Screenshot 2026-10-09 at 10 58 07" src="https://github.com/user-attachments/assets/d69b7b44-0f31-4cfc-a88a-67084d0baec4" />

3. If using the live decoder, ensure Max has its input set to the loopback device and its output set to the loudspeaker interface, then enable audio output. Play a familiarisation stimulus from the test and check the multichannel meters in Max.

Restart the backend for each participant. This renews the random seed (logged on startup) and reshuffles item order and condition/hidden-reference letter assignment. Results are written to `results/<timestamp>.csv` when a test session finishes.

To run the servers manually instead, in separate terminals:

```
./.venv/bin/uvicorn backend.main:app --port 8000
```

```
source .venv/bin/activate && cd frontend && npm run dev
```
