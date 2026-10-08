"""Vendor detection over all handlers."""

from __future__ import annotations

from scrapling.core._types import List, Optional
from scrapling.core.utils import log
from scrapling.engines.antibot import registry
from scrapling.engines.antibot.base import Detection, Signal

__all__ = ["detect", "detect_all"]


def detect_all(s: Signal) -> List[Detection]:
    """Every handler's detection for ``s``, in detection order (see :mod:`scrapling.engines.antibot.registry`).

    More than one result means vendors are layered (for example Imperva in front of DataDome): after the first one
    is solved, detect again on the new page. A handler that raises is skipped, so a detector bug never breaks a
    fetch.
    """
    found: List[Detection] = []
    for handler in registry.HANDLERS:
        try:
            det = handler.detect(s)
        except Exception as error:  # pragma: no cover - a detector bug
            log.debug(f"anti-bot detector {handler.vendor} failed: {error}")
            continue
        if det is not None:
            if det.signal is None:
                det.signal = s
            found.append(det)
    return found


def detect(s: Signal) -> Optional[Detection]:
    """The first vendor detection for ``s`` in the fixed detection order, or ``None`` for a page with no challenge,
    captcha or block on it. The detection keeps ``s`` as its :attr:`~Detection.signal`."""
    for handler in registry.HANDLERS:
        try:
            det = handler.detect(s)
        except Exception as error:  # pragma: no cover - a detector bug
            log.debug(f"anti-bot detector {handler.vendor} failed: {error}")
            continue
        if det is not None:
            if det.signal is None:
                det.signal = s
            return det
    return None
