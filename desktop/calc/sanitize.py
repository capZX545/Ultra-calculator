"""Input cleanup for the desktop calculator. Never raises to the caller."""

from __future__ import annotations

import re
import unicodedata


_DIGIT_MAP = str.maketrans(
    "۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩",
    "01234567890123456789",
)

_TEN_E = re.compile(r"(?<![\d.])10(?:\.0+)?[eE]([+-]?\d+)")


def rewrite_ten_e(text: str) -> str:
    return _TEN_E.sub(r"1e\1", text or "")


_OP_MAP = {
    "×": "*",
    "∙": "*",
    "·": "*",
    "÷": "/",
    "−": "-",
    "–": "-",
    "—": "-",
    "√": "sqrt",
    "π": "pi",
    "Π": "pi",
    "∞": "oo",
    "≤": "<=",
    "≥": ">=",
    "≠": "!=",
    "^": "**",
}


def _close_parens(text: str) -> str:
    opens = text.count("(")
    closes = text.count(")")
    if opens > closes:
        text = text + (")" * (opens - closes))
    elif closes > opens:
        text = ("(" * (closes - opens)) + text
    return text


def _implicit_mul(text: str) -> str:
    text = re.sub(r"(\d)([A-Za-df-zA-DF-Z_])", r"\1*\2", text)
    text = re.sub(r"(\d)([eE])(?![+-]?\d)", r"\1*\2", text)
    text = re.sub(r"(\))(\d)", r"\1*\2", text)
    text = re.sub(r"(\))([A-Za-z_(])", r"\1*\2", text)
    return text


def clean_number(raw: str, default: float | None = None) -> float | None:
    if raw is None:
        return default
    text = unicodedata.normalize("NFKC", str(raw)).strip()
    if not text:
        return default
    text = text.translate(_DIGIT_MAP)
    text = text.replace(" ", "")
    if text.count(",") == 1 and "." not in text:
        text = text.replace(",", ".")
    else:
        text = text.replace(",", "")
    text = text.replace("−", "-").replace("–", "-").replace("^", "**")
    text = rewrite_ten_e(text)
    if text.endswith("%"):
        try:
            return float(text[:-1]) / 100.0
        except ValueError:
            return default
    try:
        return float(text)
    except ValueError:
        pass
    m = re.fullmatch(r"10(?:\*\*)\(?([+-]?\d+)\)?", text)
    if m:
        try:
            return 10.0 ** int(m.group(1))
        except Exception:
            return default
    return default


def clean_expression(raw: str, implicit: bool = False) -> str:
    if raw is None:
        return "0"
    text = unicodedata.normalize("NFKC", str(raw)).strip()
    if not text:
        return "0"
    text = text.translate(_DIGIT_MAP)
    for src, dst in _OP_MAP.items():
        text = text.replace(src, dst)
    text = re.sub(r"\s+", "", text)
    if text.count(",") == 1 and not re.search(r"[A-Za-z_]", text):
        text = text.replace(",", ".")
    text = text.replace("**", "^").replace("^", "**")
    text = rewrite_ten_e(text)
    text = re.sub(r"[^0-9A-Za-z_+\-*/().,=<>!]", "", text)
    if implicit:
        text = _implicit_mul(text)
    text = re.sub(r"\+\+", "+", text)
    text = re.sub(r"--", "+", text)
    text = re.sub(r"\+\-", "-", text)
    text = re.sub(r"\-\+", "-", text)
    text = _close_parens(text)
    return text or "0"
