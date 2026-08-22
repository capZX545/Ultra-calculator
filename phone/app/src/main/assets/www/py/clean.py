"""Input cleanup for the Android app. Independent copy."""
import re
import unicodedata


DIGITS = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")
OPS = str.maketrans({"×": "*", "÷": "/", "−": "-", "–": "-", "—": "-", "∙": "*", "·": "*"})

# Students write 10e-2 for 10^(-2) = 0.01, not 10*10^(-2) = 0.1.
_TEN_E = re.compile(r"(?<![\d.])10(?:\.0+)?[eE]([+-]?\d+)")


def rewrite_ten_e(text: str) -> str:
    return _TEN_E.sub(r"1e\1", text or "")


def fix_number(raw, fallback=None):
    if raw is None:
        return fallback
    text = unicodedata.normalize("NFKC", str(raw)).strip().translate(DIGITS)
    if not text:
        return fallback
    text = text.replace(" ", "").replace("×", "*").replace("^", "**")
    if text.endswith("%"):
        try:
            return float(text[:-1]) / 100.0
        except ValueError:
            return fallback
    if text.count(",") == 1 and "." not in text:
        text = text.replace(",", ".")
    else:
        text = text.replace(",", "")
    text = rewrite_ten_e(text)
    try:
        return float(text)
    except ValueError:
        pass
    m = re.fullmatch(r"10(?:\*\*)\(?([+-]?\d+)\)?", text)
    if m:
        try:
            return 10.0 ** int(m.group(1))
        except Exception:
            return fallback
    return fallback


def fix_expr(raw, implicit=False):
    if raw is None:
        return "0"
    text = unicodedata.normalize("NFKC", str(raw)).strip()
    if not text:
        return "0"
    text = text.translate(DIGITS).translate(OPS)
    text = text.replace("π", "pi").replace("√", "sqrt").replace("^", "**")
    text = re.sub(r"\s+", "", text)
    if text.count(",") == 1 and not re.search(r"[A-Za-z_]", text):
        text = text.replace(",", ".")
    text = rewrite_ten_e(text)
    text = re.sub(r"[^0-9A-Za-z_+\-*/().,=<>!]", "", text)
    if implicit:
        text = re.sub(r"(\d)([A-Za-df-zA-DF-Z_])", r"\1*\2", text)
        text = re.sub(r"(\d)([eE])(?![+-]?\d)", r"\1*\2", text)
        text = re.sub(r"(\))(\d|[A-Za-z_(])", r"\1*\2", text)
    opens, closes = text.count("("), text.count(")")
    if opens > closes:
        text += ")" * (opens - closes)
    elif closes > opens:
        text = "(" * (closes - opens) + text
    return text or "0"
