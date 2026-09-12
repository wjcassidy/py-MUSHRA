from __future__ import annotations

import logging

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.audio_engine import AudioEngine
from backend.config import Config
from backend.session import REFERENCE_LETTER, Session, StimuliError

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("py_mushra.main")

app = FastAPI(title="py-MUSHRA")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.state.session = None
app.state.engine = None
app.state.startup_error = None


@app.on_event("startup")
def startup() -> None:
    try:
        config = Config.load()
        session = Session.build(config)
        engine = AudioEngine(config)
        engine.startup(session.current_page.reference_path)
        engine.reset_page()
        app.state.session = session
        app.state.engine = engine
    except StimuliError as exc:
        logger.error("Stimuli setup error: %s", exc)
        app.state.startup_error = str(exc)
    except Exception as exc:  # pragma: no cover - defensive, surfaced to the UI
        logger.exception("Failed to start py-MUSHRA")
        app.state.startup_error = str(exc)


def _session() -> Session:
    if app.state.startup_error:
        raise HTTPException(status_code=503, detail=app.state.startup_error)
    return app.state.session


def _engine() -> AudioEngine:
    if app.state.startup_error:
        raise HTTPException(status_code=503, detail=app.state.startup_error)
    return app.state.engine


class SelectRequest(BaseModel):
    letter: str


class DeviceRequest(BaseModel):
    index: int | None = None


class RatingsRequest(BaseModel):
    ratings: dict[str, float]


@app.get("/api/session")
def get_session():
    session = _session()
    if session.is_finished:
        return {"done": True}
    return {"done": False, **session.public_page_state()}


@app.post("/api/select")
def select(body: SelectRequest):
    session = _session()
    engine = _engine()
    page = session.current_page
    if body.letter != REFERENCE_LETTER and body.letter not in page.eval_letters:
        raise HTTPException(status_code=400, detail=f"Unknown letter '{body.letter}' for current page")
    engine.select(page.path_for_letter(body.letter))
    return {"ok": True}


@app.post("/api/play")
def play():
    _engine().play()
    return {"ok": True}


@app.post("/api/pause")
def pause():
    _engine().pause()
    return {"ok": True}


@app.get("/api/audio-devices")
def audio_devices():
    return {"devices": _engine().list_output_devices()}


@app.post("/api/audio-device")
def set_audio_device(body: DeviceRequest):
    _engine().set_output_device(body.index)
    return {"ok": True}


@app.post("/api/ratings")
def submit_ratings(body: RatingsRequest):
    session = _session()
    engine = _engine()
    try:
        result = session.record_ratings(body.ratings)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    engine.reset_page()
    return result
