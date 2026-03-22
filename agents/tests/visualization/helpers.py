"""Pure functions for visualization tests (importable without pytest fixture magic)."""

from __future__ import annotations

import base64
import json
from typing import Any


def assert_valid_png_base64(b64: str) -> bytes:
    assert b64, "image_base64 must be non-empty"
    raw = base64.standard_b64decode(b64)
    assert raw[:8] == b"\x89PNG\r\n\x1a\n", "decoded payload must be a PNG"
    assert len(raw) > 200, "PNG should have non-trivial payload"
    return raw


def json_dumps_model(model: Any) -> str:
    return json.dumps(model.model_dump(), default=str)
