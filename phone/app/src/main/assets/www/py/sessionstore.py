"""Save and load a session file on disk (desktop / kivy). Independent copy."""

from __future__ import annotations

import json
from pathlib import Path


def path() -> Path:
    return Path.home() / ".ultra-calculator" / "session.json"


def load() -> dict:
    try:
        p = path()
        if p.is_file():
            data = json.loads(p.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                return data
    except Exception:
        pass
    return {}


def save(data: dict) -> dict:
    try:
        p = path()
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(data or {}, ensure_ascii=False, indent=2), encoding="utf-8")
        return {"ok": True, "text": str(p)}
    except Exception:
        return {"ok": True, "text": "0"}
