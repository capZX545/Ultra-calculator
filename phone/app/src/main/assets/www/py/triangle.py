"""Triangle solver (SSS, SAS, ASA, AAS, SSA). Independent copy. Degrees in, degrees out."""

from __future__ import annotations

import math
import unicodedata

_DIGIT = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")


def _num(raw):
    if raw is None:
        return None
    text = unicodedata.normalize("NFKC", str(raw)).strip().translate(_DIGIT)
    if not text:
        return None
    text = text.replace(",", ".")
    try:
        return float(text)
    except Exception:
        return None


def _pretty(x) -> str:
    try:
        v = float(x)
    except Exception:
        return str(x)
    if not math.isfinite(v):
        return "undefined"
    if abs(v) < 1e-12:
        return "0"
    return f"{v:.10g}"


def _deg(rad):
    return rad * 180.0 / math.pi


def _rad(deg):
    return deg * math.pi / 180.0


def _ang(a, b, c):
    # angle opposite a
    x = (b * b + c * c - a * a) / (2 * b * c)
    x = max(-1.0, min(1.0, x))
    return math.acos(x)


def _area_heron(a, b, c):
    s = (a + b + c) / 2
    v = s * (s - a) * (s - b) * (s - c)
    if v <= 0:
        return 0.0
    return math.sqrt(v)


def _pack(a, b, c, A, B, C, lang):
    area = _area_heron(a, b, c)
    if area <= 0 or min(a, b, c) <= 0:
        return _fail(lang)
    if abs(A + B + C - 180) > 0.2:
        C = 180 - A - B
    ha = 2 * area / a if a else 0
    hb = 2 * area / b if b else 0
    hc = 2 * area / c if c else 0
    peri = a + b + c
    r = area / (peri / 2) if peri else 0
    R = a / (2 * math.sin(_rad(A))) if A else 0
    shown = (
        f"a={_pretty(a)}; b={_pretty(b)}; c={_pretty(c)}; "
        f"A={_pretty(A)} deg; B={_pretty(B)} deg; C={_pretty(C)} deg; "
        f"area={_pretty(area)}; peri={_pretty(peri)}; "
        f"ha={_pretty(ha)}; hb={_pretty(hb)}; hc={_pretty(hc)}; r={_pretty(r)}; R={_pretty(R)}"
    )
    steps = {
        "en": ["Sides a,b,c opposite angles A,B,C.", "Law of sines and cosines.", shown],
        "fa": ["ضلع a روبه‌روی زاویه A است.", "قانون سینوس و کسینوس.", shown],
        "fi": ["Sivu a on kulmaa A vastapaa.", "Sini- ja kosinilause.", shown],
    }
    latex = rf"a={_pretty(a)},\; b={_pretty(b)},\; c={_pretty(c)},\; A={_pretty(A)}^\circ"
    return {"ok": True, "text": shown, "latex": latex, "steps": steps.get(lang) or steps["en"], "area": area}


def _fail(lang, extra=""):
    msg = {"en": "Not a triangle. Showing 0.", "fa": "مثلث نشد. ۰.", "fi": "Ei kolmio. 0."}
    line = extra or (msg.get(lang) or msg["en"])
    return {"ok": True, "text": "0", "latex": "0", "steps": [line]}


def run(values: dict | None = None, lang: str = "en", eng: bool = False) -> dict:
    try:
        v = values or {}
        a, b, c = _num(v.get("a")), _num(v.get("b")), _num(v.get("c"))
        A, B, C = _num(v.get("A")), _num(v.get("B")), _num(v.get("C"))
        sides = [(a, "a"), (b, "b"), (c, "c")]
        angs = [(A, "A"), (B, "B"), (C, "C")]
        ns = sum(1 for x, _ in sides if x is not None)
        na = sum(1 for x, _ in angs if x is not None)
        if ns == 3:
            if a <= 0 or b <= 0 or c <= 0 or a + b <= c or a + c <= b or b + c <= a:
                return _fail(lang)
            A = _deg(_ang(a, b, c))
            B = _deg(_ang(b, a, c))
            C = 180 - A - B
            return _pack(a, b, c, A, B, C, lang)
        # fill the third angle if two are known
        if na == 2:
            if A is None:
                A = 180 - B - C
            elif B is None:
                B = 180 - A - C
            else:
                C = 180 - A - B
            na = 3
        if na == 3 and ns >= 1:
            if min(A, B, C) <= 0 or abs(A + B + C - 180) > 0.5:
                return _fail(lang)
            # ASA / AAS / one side
            if a is not None:
                b = a * math.sin(_rad(B)) / math.sin(_rad(A))
                c = a * math.sin(_rad(C)) / math.sin(_rad(A))
            elif b is not None:
                a = b * math.sin(_rad(A)) / math.sin(_rad(B))
                c = b * math.sin(_rad(C)) / math.sin(_rad(B))
            else:
                a = c * math.sin(_rad(A)) / math.sin(_rad(C))
                b = c * math.sin(_rad(B)) / math.sin(_rad(C))
            return _pack(a, b, c, A, B, C, lang)
        # SAS
        if ns == 2 and na == 1:
            if A is not None and b is not None and c is not None:
                a = math.sqrt(b * b + c * c - 2 * b * c * math.cos(_rad(A)))
                B = _deg(_ang(b, a, c))
                C = 180 - A - B
                return _pack(a, b, c, A, B, C, lang)
            if B is not None and a is not None and c is not None:
                b = math.sqrt(a * a + c * c - 2 * a * c * math.cos(_rad(B)))
                A = _deg(_ang(a, b, c))
                C = 180 - A - B
                return _pack(a, b, c, A, B, C, lang)
            if C is not None and a is not None and b is not None:
                c = math.sqrt(a * a + b * b - 2 * a * b * math.cos(_rad(C)))
                A = _deg(_ang(a, b, c))
                B = 180 - A - C
                return _pack(a, b, c, A, B, C, lang)
        # SSA ambiguous
        if ns == 2 and na == 1:
            return _ssa(a, b, c, A, B, C, lang)
        return _fail(lang)
    except Exception:
        return _fail(lang)


def _ssa(a, b, c, A, B, C, lang):
    # known: one angle and two sides, not SAS
    try:
        if A is not None and a is not None and b is not None and c is None:
            sinB = b * math.sin(_rad(A)) / a
            if sinB > 1.0000001:
                return _fail(lang)
            sinB = min(1.0, sinB)
            B1 = _deg(math.asin(sinB))
            B2 = 180 - B1
            outs = []
            for BB in (B1, B2):
                CC = 180 - A - BB
                if CC <= 0:
                    continue
                cc = a * math.sin(_rad(CC)) / math.sin(_rad(A))
                outs.append(_pack(a, b, cc, A, BB, CC, lang))
            if not outs:
                return _fail(lang)
            if len(outs) == 1:
                return outs[0]
            t = outs[0]["text"] + " || " + outs[1]["text"]
            steps = outs[0]["steps"] + ["SSA ambiguous: two triangles."] + outs[1]["steps"]
            return {"ok": True, "text": t, "latex": outs[0].get("latex") or "", "steps": steps}
        if B is not None and b is not None and a is not None and c is None:
            return _ssa(b, a, c, B, A, C, lang)
        if A is not None and a is not None and c is not None and b is None:
            return _ssa(a, c, b, A, C, B, lang)
    except Exception:
        return _fail(lang)
    return _fail(lang)
