"""Input cleanup for the desktop calculator. Never raises to the caller."""

from __future__ import annotations

import re
import unicodedata


_DIGIT_MAP = str.maketrans(
    "۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩",
    "01234567890123456789",
)

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
    "φ": "phi",
    "θ": "theta",
    "ω": "omega",
    "λ": "lambda",
    "μ": "mu",
    "ρ": "rho",
    "σ": "sigma",
    "Δ": "Delta",
    "δ": "delta",
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
    text = re.sub(r"(\d)\s*([a-zA-Z_(])", r"\1*\2", text)
    text = re.sub(r"(\))\s*(\d)", r"\1*\2", text)
    text = re.sub(r"(\))\s*([a-zA-Z_(])", r"\1*\2", text)
    text = re.sub(r"([a-zA-Z_])(\d)", r"\1*\2", text)
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
    text = text.replace("−", "-").replace("–", "-")
    if text.endswith("%"):
        try:
            return float(text[:-1]) / 100.0
        except ValueError:
            return default
    try:
        return float(text)
    except ValueError:
        try:
            from ast import literal_eval

            value = literal_eval(text)
            if isinstance(value, (int, float)):
                return float(value)
        except Exception:
            pass
    return default


def clean_expression(raw: str) -> str:
    if raw is None:
        return "0"
    text = unicodedata.normalize("NFKC", str(raw)).strip()
    if not text:
        return "0"
    text = text.translate(_DIGIT_MAP)
    for src, dst in _OP_MAP.items():
        text = text.replace(src, dst)
    text = text.replace(",", ".")
    text = re.sub(r"\s+", "", text)
    text = text.replace("**", "^")
    text = text.replace("^", "**")
    text = re.sub(r"[^0-9a-zA-Z_+\-*/().=<>!]", "", text)
    text = _implicit_mul(text)
    text = re.sub(r"\+\+", "+", text)
    text = re.sub(r"--", "+", text)
    text = re.sub(r"\+\-", "-", text)
    text = re.sub(r"\-\+", "-", text)
    text = _close_parens(text)
    if not text:
        return "0"
    return text
