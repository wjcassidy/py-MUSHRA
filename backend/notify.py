from __future__ import annotations

import logging
import ssl
import threading
import urllib.request

import certifi

logger = logging.getLogger("py_mushra.notify")


def send_mobile_notification(topic: str | None, message: str, title: str = "py-MUSHRA") -> None:
    """Push `message` to the ntfy.sh `topic` (subscribe to it in the ntfy app).

    Sent from a daemon thread so a slow or unreachable ntfy server never holds
    up the request that raised the alert. Does nothing if no topic is configured.
    """
    if not topic:
        return
    threading.Thread(target=_send, args=(topic, message, title), name="ntfy", daemon=True).start()


def _send(topic: str, message: str, title: str) -> None:
    # certifi's root certificates, as python.org builds on macOS ship without any.
    context = ssl.create_default_context(cafile=certifi.where())
    request = urllib.request.Request(
        f"https://ntfy.sh/{topic}",
        data=message.encode("utf-8"),
        method="POST",
        # UTF-8-encode rather than leaving this a str: http.client otherwise
        # latin-1-encodes str header values, which fails outside that range.
        headers={"Title": title.encode("utf-8"), "Priority": "high", "Tags": "rotating_light"},
    )
    try:
        urllib.request.urlopen(request, context=context, timeout=10).close()
    except Exception as exc:
        logger.warning("Failed to send ntfy notification: %s", exc)
