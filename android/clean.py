"""Input cleanup for the Android app. Independent copy."""
import re
import unicodedata


DIGITS = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")
OPS = str.maketrans({"×": "*", "÷": "/", "−": "-", "–": "-", "—": "-", "∙": "*", "·": "*"})


def fix_number(raw, fallback=None):
    if raw is None:
        return fallback
    text = unicodedata.normalize("NFKC", str(raw)).strip().translate(DIGITS)
    if not text:
        return fallback
    text = text.replace(" ", "")
    if text.endswith("%"):
        try:
            return float(text[:-1]) / 100.0
        except ValueError:
            return fallback
    if text.count(",") == 1 and "." not in text:
        text = text.replace(",", ".")
    else:
        text = text.replace(",", "")
    try:
        return float(text)
    except ValueError:
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
    text = re.sub(r"[^0-9A-Za-z_+\-*/().,=<>!]", "", text)
    if implicit:
        text = re.sub(r"(\d)([A-Za-z_])", r"\1*\2", text)
        text = re.sub(r"(\))(\d|[A-Za-z_(])", r"\1*\2", text)
    opens, closes = text.count("("), text.count(")")
    if opens > closes:
        text += ")" * (opens - closes)
    elif closes > opens:
        text = "(" * (closes - opens) + text
    return text or "0"
