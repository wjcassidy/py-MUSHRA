from __future__ import annotations

import logging
import threading
import datetime

logger = logging.getLogger("py_mushra.researcher_call")

ALERT_MESSAGE = (
    "\n\033[93m********************************** ALERT **********************************\n\n"
    "{time} - Participant has requested assistance; press enter to acknowledge.\n\n"
    "***************************************************************************\n\x1b[37m"
)


class ResearcherCall:
    """Participant-raised call for the researcher, acknowledged by pressing Enter
    in the terminal running the backend."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self.active = False
        self.acknowledged = False
        self.listening = False

    def start_listening(self) -> None:
        # Read Enter from the controlling terminal rather than stdin, which is
        # often redirected (e.g. to /dev/null for background jobs). A daemon
        # thread blocks on it for the lifetime of the process; lines entered
        # while no call is active are discarded.
        try:
            tty = open("/dev/tty")
        except OSError as exc:
            logger.warning(
                "No terminal available (%s) -- 'Call researcher' alerts can't be acknowledged with Enter. "
                "Start the backend with ./run_test from a terminal window.",
                exc,
            )
            return
        self.listening = True
        threading.Thread(target=self._read_tty, args=(tty,), name="researcher-call-tty", daemon=True).start()

    def state(self) -> dict:
        with self._lock:
            return {"active": self.active, "acknowledged": self.acknowledged}

    def set_active(self, active: bool) -> dict:
        with self._lock:
            if active and not self.active:
                print(ALERT_MESSAGE.format(time=datetime.datetime.now().strftime("%H:%M")), end="", flush=True)
                if not self.listening:
                    print("(not listening for Enter -- no terminal available)\n", flush=True)
            elif not active and self.active:
                if not self.acknowledged:
                    print()  # end the unanswered prompt line
                print(f"{self.get_time_string()} - Participant cancelled the call.\n", flush=True)
            self.active = active
            self.acknowledged = False
        return self.state()

    def acknowledge(self, source: str) -> dict:
        with self._lock:
            if self.active and not self.acknowledged:
                self.acknowledged = True
                if source != "terminal":
                    print()  # Enter wasn't typed here, so end the prompt line ourselves
                print(
                    f"{self.get_time_string()} - Acknowledged from {source}; participant has been notified.\n",
                    flush=True,
                )
        return self.state()

    def _read_tty(self, tty) -> None:
        for _ in tty:
            self.acknowledge("terminal")
        self.listening = False
        logger.warning(f"\n{self.get_time_string()} - Terminal closed; 'Call researcher' alerts can no longer be acknowledged")

    def get_time_string(self):
        return f"{datetime.datetime.now().strftime('%H:%M')}"
