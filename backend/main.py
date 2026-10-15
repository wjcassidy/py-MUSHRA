from __future__ import annotations

import logging
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.audio_engine import VOLUME_MAX_DB, VOLUME_MIN_DB, AudioDeviceError, AudioEngine
from backend.config import Config
from backend.researcher_call import ResearcherCall
from backend.session import REFERENCE_LETTER, Session, StimuliError

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("py_mushra.main")


class _HideResearcherCallAccessLog(logging.Filter):
    # The frontend polls /api/call-researcher every second while a call is
    # active; keep those requests from burying the terminal prompt.
    def filter(self, record: logging.LogRecord) -> bool:
        return "/api/call-researcher" not in record.getMessage()


logging.getLogger("uvicorn.access").addFilter(_HideResearcherCallAccessLog())

app = FastAPI(title="py-MUSHRA")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.state.session = None
app.state.engine = None
app.state.config = None
app.state.startup_error = None
# Volume is fixed once familiarisation is finished, so every test page is heard
# at the level the listener chose.
app.state.volume_locked = False
app.state.researcher_call = ResearcherCall()


@app.on_event("startup")
def startup() -> None:
    app.state.researcher_call.start_listening()
    try:
        config = Config.load()
        session = Session.build(config)
        engine = AudioEngine(config)
        engine.startup(session.current_page.reference_path)
        engine.reset_page()
        # Preload page 1 while the listener is on the welcome/familiarisation pages.
        engine.set_page_stimuli(session.current_page.stimulus_paths)
        app.state.session = session
        app.state.engine = engine
        app.state.config = config
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


def _config() -> Config:
    if app.state.startup_error:
        raise HTTPException(status_code=503, detail=app.state.startup_error)
    return app.state.config


class SelectRequest(BaseModel):
    letter: str


class DeviceRequest(BaseModel):
    index: Optional[int] = None  # not `int | None`: Pydantic evaluates this at runtime (Python 3.9)


class RatingsRequest(BaseModel):
    ratings: dict[str, float]


class FamiliarisationSelectRequest(BaseModel):
    filename: str


class VolumeRequest(BaseModel):
    volume_db: float


class ResearcherCallRequest(BaseModel):
    active: bool


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
    engine = _engine()
    return {
        "devices": engine.list_output_devices(),
        **engine.channel_status(),
    }


@app.post("/api/audio-device")
def set_audio_device(body: DeviceRequest):
    engine = _engine()
    try:
        engine.set_output_device(body.index)
    except AudioDeviceError:
        pass  # engine.channel_status() below reports the resulting device_error
    return {"ok": engine.device_error is None, **engine.channel_status()}


def _volume_state(engine: AudioEngine) -> dict:
    return {
        "volume_db": engine.volume_db,
        "min_db": VOLUME_MIN_DB,
        "max_db": VOLUME_MAX_DB,
        "locked": app.state.volume_locked,
        "hidden": _config().hide_volume,
    }


@app.get("/api/volume")
def get_volume():
    return _volume_state(_engine())


@app.post("/api/volume")
def set_volume(body: VolumeRequest):
    engine = _engine()
    if app.state.volume_locked:
        raise HTTPException(status_code=409, detail="Volume is locked once familiarisation is finished")
    engine.set_volume_db(body.volume_db)
    return _volume_state(engine)


@app.get("/api/familiarisation-stimuli")
def familiarisation_stimuli():
    config = _config()
    return {"stimuli": sorted(p.name for p in config.familiarisation_dir.glob("*.wav"))}


@app.post("/api/familiarisation-select")
def familiarisation_select(body: FamiliarisationSelectRequest):
    config = _config()
    engine = _engine()
    familiarisation_dir = config.familiarisation_dir.resolve()
    path = (familiarisation_dir / body.filename).resolve()
    if path.parent != familiarisation_dir or not path.is_file():
        raise HTTPException(
            status_code=400, detail=f"Unknown familiarisation stimulus '{body.filename}'"
        )
    engine.select(path)
    return {"ok": True}


@app.post("/api/familiarisation-finish")
def familiarisation_finish():
    # Familiarisation and the main test share engine.select(), which can leave a
    # crossfade queued from the last familiarisation clip into the first real
    # stimulus -- clear that transport state before the test's own audio begins.
    engine = _engine()
    session = _session()
    engine.reset_page()
    # Releases the familiarisation clips; page 1 was already preloaded at startup.
    engine.set_page_stimuli(session.current_page.stimulus_paths)
    app.state.volume_locked = True
    session.log_current_page()
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
    engine.set_page_stimuli([] if session.is_finished else session.current_page.stimulus_paths)
    session.log_current_page()
    return result


@app.get("/api/call-researcher")
def get_researcher_call():
    return app.state.researcher_call.state()


@app.post("/api/call-researcher")
def set_researcher_call(body: ResearcherCallRequest):
    return app.state.researcher_call.set_active(body.active)


@app.post("/api/call-researcher/acknowledge")
def acknowledge_researcher_call():
    return app.state.researcher_call.acknowledge("web UI")
