"""Optional terminal QR-code renderer.

Requires the ``qrcode`` package (install with ``pip install trafikverket-client[qr]``).
"""

from __future__ import annotations

import hashlib
import hmac
import logging
import sys
import time
from enum import Enum, auto
from typing import TextIO

logger = logging.getLogger(__name__)

try:
    import qrcode as _qrcode

    HAS_QRCODE = True
except ImportError:
    _qrcode = None  # type: ignore[assignment]
    HAS_QRCODE = False

_UPPER_HALF = "\u2580"  # ▀
_LOWER_HALF = "\u2584"  # ▄
_FULL = "\u2588"  # █


class ShowQr(Enum):
    """Controls QR code rendering in the terminal during BankID login."""

    AUTO = auto()
    """Show the QR code if the ``qrcode`` package is installed (default)."""
    ALWAYS = auto()
    """Always show the QR code; raise if ``qrcode`` is not installed."""
    NEVER = auto()
    """Never show the QR code."""


class QrRenderer:
    """Renders QR codes to the terminal, overwriting the previous frame."""

    def __init__(self, *, border: int = 1, file: TextIO = sys.stdout) -> None:
        self._border = border
        self._file = file
        self._printed_lines = 0

    def render(self, data: str) -> str:
        """Return a compact Unicode string representing *data* as a QR code."""
        assert _qrcode is not None
        qr = _qrcode.QRCode(border=self._border)
        qr.add_data(data)
        qr.make(fit=True)
        matrix = qr.get_matrix()

        lines: list[str] = []
        for y in range(0, len(matrix), 2):
            row_top = matrix[y]
            row_bot = matrix[y + 1] if y + 1 < len(matrix) else [False] * len(row_top)
            chars: list[str] = []
            for top, bot in zip(row_top, row_bot):
                if top and bot:
                    chars.append(" ")
                elif top:
                    chars.append(_LOWER_HALF)
                elif bot:
                    chars.append(_UPPER_HALF)
                else:
                    chars.append(_FULL)
            lines.append("".join(chars))
        return "\n".join(lines)

    def update(self, data: str) -> None:
        """Clear the previous QR (if any) and print a new one."""
        self.clear()
        text = self.render(data)
        print(text, file=self._file, flush=True)
        self._printed_lines = text.count("\n") + 1

    def clear(self) -> None:
        """Erase the last printed QR code from the terminal."""
        for _ in range(self._printed_lines):
            self._file.write("\033[A\033[2K")
        self._file.flush()
        self._printed_lines = 0


class NoopQrRenderer(QrRenderer):
    """No-op renderer used when QR display is disabled or unavailable."""

    def __init__(self) -> None:
        self._printed_lines = 0

    def render(self, data: str) -> str:
        return ""

    def update(self, data: str) -> None:
        pass

    def clear(self) -> None:
        pass


def make_qr_renderer(show_qr: ShowQr) -> QrRenderer:
    """Create the appropriate renderer based on the *show_qr* setting."""
    if show_qr is ShowQr.ALWAYS and not HAS_QRCODE:
        raise ImportError(
            "show_qr is ALWAYS but the 'qrcode' package is not installed. "
            "Install with: pip install trafikverket-client[qr]"
        )
    if show_qr is ShowQr.ALWAYS or (show_qr is ShowQr.AUTO and HAS_QRCODE):
        return QrRenderer()
    return NoopQrRenderer()


def make_bankid_qr_payload(
    qr_start_token: str,
    qr_start_secret: str,
    qr_start_time: int,
    now: int | None = None,
) -> str:
    """Build the animated BankID QR payload for the current second."""
    current_time = int(time.time()) if now is None else now
    elapsed = max(0, current_time - qr_start_time)
    auth_code = hmac.new(
        qr_start_secret.encode("utf-8"),
        str(elapsed).encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return f"bankid.{qr_start_token}.{elapsed}.{auth_code}"
