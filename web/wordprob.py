"""Textbook word-problem solver. Independent copy. No desktop/web/phone imports."""

from __future__ import annotations

import math
import re
import unicodedata


_DIGIT = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")
K_VAC = 8.9875517923e9

_CHARGE_UNIT = {
    "c": 1.0,
    "mc": 1e-3,
    "uc": 1e-6,
    "μc": 1e-6,
    "µc": 1e-6,
    "nc": 1e-9,
    "pc": 1e-12,
}
_LEN_UNIT = {
    "m": 1.0,
    "cm": 0.01,
    "mm": 0.001,
    "km": 1000.0,
    "nm": 1e-9,
}


def _clean(raw: str) -> str:
    text = unicodedata.normalize("NFKC", str(raw or ""))
    text = text.translate(_DIGIT)
    text = text.replace("\u200c", " ").replace("\u200b", "").replace("\u2060", "")
    text = text.replace("−", "-").replace("–", "-").replace("—", "-")
    text = text.replace("μ", "u").replace("µ", "u")
    text = re.sub(r"([+-]?\d+(?:\.\d+)?)\s*[×xX*]\s*109\b", r"\1e9", text)
    text = re.sub(r"([+-]?\d+(?:\.\d+)?)\s*[×xX*]\s*10\s*\^?\s*([89])\b", r"\1e\2", text)
    text = text.replace("×", "*").replace("·", "*").replace("⋅", "*")
    text = re.sub(r"\*+", "", text)
    text = re.sub(r"_+", "", text)
    text = re.sub(r"[\u0332\u20d2\u20e8\u20e3]", "", text)
    text = re.sub(r"q\s*([123])\s*=", r" q\1=", text, flags=re.I)
    text = re.sub(r"10\s*\^\s*([+-]?\d+)", r"e\1", text)
    text = re.sub(r"10\s*\*\*\s*([+-]?\d+)", r"e\1", text)
    text = re.sub(r"(\d)\s*\*\s*10\s*([+-]?\d+)", r"\1e\2", text)
    text = re.sub(r"(\d)\s*e\s*\+?\s*(\d+)", r"\1e\2", text)
    text = re.sub(r"(\d)\s+e\s*(\d+)", r"\1e\2", text)
    return text


def _num(token: str):
    token = (token or "").strip().replace(" ", "")
    token = token.replace(",", ".")
    if not token:
        return None
    try:
        return float(token)
    except Exception:
        return None


def _looks_word(text: str) -> bool:
    if re.search(r"[\u0600-\u06FF]", text):
        return True
    keys = (
        "charge", "field", "coulomb", "force", "distance", "vacuum",
        "ohm", "current", "voltage", "resistor", "velocity", "acceleration",
        "بار", "میدان", "فاصله", "نیرو", "کولن", "خلاء", "خلا", "نقطه",
        "شتاب", "سرعت", "مقاومت", "ولتاژ", "جریان",
    )
    low = text.lower()
    return any(k in low or k in text for k in keys)


def _find_k(text: str) -> float:
    m = re.search(r"\bk\s*=\s*([+-]?\d+(?:\.\d+)?)(?:e([+-]?\d+))?", text, re.I)
    if m:
        base = float(m.group(1))
        if m.group(2):
            return base * (10 ** int(m.group(2)))
        after = text[m.end() : m.end() + 12]
        m2 = re.search(r"^\s*(?:e|\*?\s*10)?\s*([+-]?\d{1,2})\b", after, re.I)
        # k=9 then 109 nearby (9×109 written as 9 109 after cleanup)
        nearby = text[m.start() : m.start() + 40]
        m3 = re.search(r"k\s*=\s*([+-]?\d+(?:\.\d+)?)\s*(?:e|x|\*)?\s*10?\s*([89]|10)\b", nearby, re.I)
        if m3 and not m.group(2):
            exp = int(m3.group(2))
            if exp in (8, 9, 10):
                return float(m3.group(1)) * (10 ** exp)
        if m2 and not m.group(2):
            exp = int(m2.group(1))
            if 7 <= abs(exp) <= 12:
                return base * (10 ** exp)
        if abs(base) >= 1e7:
            return base
        # 9 followed by 109 in the original "9×109"
        m4 = re.search(r"k\s*=\s*([+-]?\d+(?:\.\d+)?)\s*109\b", nearby, re.I)
        if m4:
            return float(m4.group(1)) * 1e9
    m = re.search(r"k\s*=\s*([+-]?\d+(?:\.\d+)?)\s*\*?\s*10\s*\*?\s*([89])\b", text, re.I)
    if m:
        return float(m.group(1)) * (10 ** int(m.group(2)))
    return K_VAC


def _charges(text: str):
    out = {}
    pat = re.compile(
        r"q\s*([123])\s*=\s*([+-]?\d+(?:\.\d+)?(?:e[+-]?\d+)?)\s*(u?c|μc|µc|nc|pc|mc|c)?",
        re.I,
    )
    for m in pat.finditer(text):
        val = _num(m.group(2))
        if val is None:
            continue
        unit = (m.group(3) or "c").lower().replace("μ", "u").replace("µ", "u")
        if unit == "c" and abs(val) > 1:
            # bare 4 next to uC that was split; look ahead
            nxt = text[m.end() : m.end() + 8].lower()
            if re.search(r"u?c", nxt):
                unit = "uc"
        scale = _CHARGE_UNIT.get(unit, 1.0)
        if unit == "c" and 0 < abs(val) <= 1000 and "uc" in text.lower():
            # q1=+4 with μC later in the same token cluster
            window = text[max(0, m.start() - 4) : m.end() + 8].lower()
            if "uc" in window or "μc" in window:
                scale = 1e-6
        out[int(m.group(1))] = val * scale
    if len(out) < 2:
        # "بار ... +4uC و ... -9uC"
        found = []
        for m in re.finditer(
            r"([+-]\d+(?:\.\d+)?(?:e[+-]?\d+)?)\s*(uc|nc|pc|mc|c)\b",
            text,
            re.I,
        ):
            val = _num(m.group(1))
            if val is None:
                continue
            unit = m.group(2).lower()
            found.append(val * _CHARGE_UNIT.get(unit, 1.0))
        for i, v in enumerate(found[:3], start=1):
            out.setdefault(i, v)
    return out


def _distance_m(text: str):
    # 50 cm / 50 سانت / 0.5 m / فاصله ۵۰ سانتی‌متری
    unit_re = r"(سانتی[\s‌-]*متر[یي]?|سانت(?:ی)?|cm|میلی[\s‌-]*متر[یي]?|mm|کیلو[\s‌-]*متر[یي]?|km|متر[یي]?|m)\b"
    m = re.search(
        rf"(?:فاصله|distance|d)\s*(?:[=:]|)\s*([+-]?\d+(?:\.\d+)?(?:e[+-]?\d+)?)\s*{unit_re}",
        text,
        re.I,
    )
    if not m:
        m = re.search(rf"([+-]?\d+(?:\.\d+)?)\s*{unit_re}", text, re.I)
    if not m:
        return None
    val = _num(m.group(1))
    if val is None:
        return None
    unit = re.sub(r"[\s‌-]+", "", m.group(2).lower())
    if unit.startswith("سانت") or unit == "cm":
        return val * 0.01
    if unit.startswith("میلی") or unit == "mm":
        return val * 0.001
    if unit.startswith("کیلو") or unit == "km":
        return val * 1000.0
    return val


def _pretty(x, eng=False, unit=""):
    try:
        v = float(x)
    except Exception:
        return str(x)
    if not math.isfinite(v):
        return "0"
    if abs(v) < 1e-15:
        shown = "0"
    elif eng and v != 0:
        exp = int(math.floor(math.log10(abs(v)) / 3) * 3)
        shown = f"{v / (10 ** exp):.8g}e{exp:+d}"
    else:
        shown = f"{v:.12g}"
    return (shown + (" " + unit if unit else "")).strip()


def _T(lang: str) -> dict:
    if lang == "fa":
        return {
            "typed": "صورت مسئله خوانده شد.",
            "q": "بارها: q1 = {q1} C ، q2 = {q2} C{q3}",
            "q3extra": " ، q3 = {q3} C",
            "d": "فاصلهٔ دو بار: d = {d} m",
            "k": "k = {k} N·m²/C²",
            "signs_opp": "علامت دو بار مخالف است. بین دو بار، میدان‌ها هم‌جهت‌اند و صفر نمی‌شوند.",
            "signs_same": "علامت دو بار یکسان است. نقطهٔ صفر بین آن‌هاست.",
            "side": "نقطهٔ صفر بیرون از بازه و در سمت بار کوچک‌تر از نظر مقدار است.",
            "region": "بار کوچک‌تر q{who} است. نقطه را در سمت همان بار، بیرون از فاصله، می‌گذاریم.",
            "eq": "شرط E1 = E2 : k |q1| / r1² = k |q2| / r2²",
            "pos": "نقطهٔ صفر {pos} متر از q1 فاصله دارد ({side}).",
            "left": "سمت چپ q1، دور از q2",
            "right": "سمت راست q2، دور از q1",
            "between": "بین دو بار، از q1 به اندازهٔ {x} متر",
            "force0": "در نقطه‌ای که میدان خالص صفر است، F = q3 E = 0.",
            "force": "نیروی خالص روی q3 : {f} N",
            "ans_a": "الف) {ans}",
            "ans_b": "ب) نیروی خالص = {f} N",
            "coul": "نیروی کولن: F = k |q1 q2| / r² = {f} N",
            "efield": "میدان بار نقطه‌ای: E = k |q| / r² = {e} N/C",
            "ohm": "V = I R → {ans}",
            "kin": "حرکت: {ans}",
        }
    if lang == "fi":
        return {
            "typed": "Luettu tehtavananto.",
            "q": "Varaukset: q1 = {q1} C, q2 = {q2} C{q3}",
            "q3extra": ", q3 = {q3} C",
            "d": "Etaisyys: d = {d} m",
            "k": "k = {k} N·m²/C²",
            "signs_opp": "Vastakkaiset merkit. Kentat eivat nollaudu varausten valissa.",
            "signs_same": "Sama merkki. Nollakohta on valissa.",
            "side": "Nollakohta on pienemman |q| puolella, janan ulkopuolella.",
            "region": "Pienempi on q{who}. Nollakohta sen puolella.",
            "eq": "Ehto E1 = E2 : k |q1| / r1² = k |q2| / r2²",
            "pos": "Nollakohta on {pos} m paassa q1:sta ({side}).",
            "left": "q1:n vasemmalla, poispain q2:sta",
            "right": "q2:n oikealla, poispain q1:sta",
            "between": "valissa, {x} m q1:sta",
            "force0": "Kun E = 0, F = q3 E = 0.",
            "force": "Nettovoima q3:een: {f} N",
            "ans_a": "a) {ans}",
            "ans_b": "b) Nettovoima = {f} N",
            "coul": "Coulomb: F = k |q1 q2| / r² = {f} N",
            "efield": "Pistvaraus: E = k |q| / r² = {e} N/C",
            "ohm": "V = I R → {ans}",
            "kin": "Liike: {ans}",
        }
    return {
        "typed": "Read the problem statement.",
        "q": "Charges: q1 = {q1} C, q2 = {q2} C{q3}",
        "q3extra": ", q3 = {q3} C",
        "d": "Separation: d = {d} m",
        "k": "k = {k} N·m²/C²",
        "signs_opp": "Opposite signs. Between the charges the fields point the same way, so they cannot cancel.",
        "signs_same": "Same sign. The null point lies between them.",
        "side": "The null point is outside the segment, on the side of the smaller |q|.",
        "region": "The smaller magnitude is q{who}. Put the point outside, on that side.",
        "eq": "Set E1 = E2: k |q1| / r1² = k |q2| / r2²",
        "pos": "The null point is {pos} m from q1 ({side}).",
        "left": "to the left of q1, away from q2",
        "right": "to the right of q2, away from q1",
        "between": "between them, {x} m from q1",
        "force0": "Where the net field is zero, F = q3 E = 0.",
        "force": "Net force on q3: {f} N",
        "ans_a": "a) {ans}",
        "ans_b": "b) Net force = {f} N",
        "coul": "Coulomb force: F = k |q1 q2| / r² = {f} N",
        "efield": "Point-charge field: E = k |q| / r² = {e} N/C",
        "ohm": "V = I R → {ans}",
        "kin": "Motion: {ans}",
    }


def _zero_field_point(q1: float, q2: float, d: float):
    """q1 at 0, q2 at d. Return (x_from_q1, region, r1, r2). region: left/right/between."""
    a1, a2 = abs(q1), abs(q2)
    if a1 <= 0 or a2 <= 0 or d <= 0:
        return None
    same = (q1 > 0 and q2 > 0) or (q1 < 0 and q2 < 0)
    s1, s2 = math.sqrt(a1), math.sqrt(a2)
    if same:
        # between: s1 / x = s2 / (d-x)
        # s1 (d-x) = s2 x  => s1 d = x (s1+s2) => x = s1 d / (s1+s2)
        x = s1 * d / (s1 + s2)
        if 0 < x < d:
            return (x, "between", x, d - x)
        return None
    # opposite: outside, nearer smaller charge
    if a1 < a2:
        # left of q1: s1 / x = s2 / (x+d)  with x = distance to q1 > 0
        # s1 (x+d) = s2 x => s1 d = x (s2-s1) => x = s1 d / (s2-s1)
        if s2 == s1:
            return None
        x = s1 * d / (s2 - s1)
        if x > 0:
            return (-x, "left", x, x + d)
    else:
        # right of q2: s2 / y = s1 / (y+d), y distance from q2
        if s1 == s2:
            return None
        y = s2 * d / (s1 - s2)
        if y > 0:
            return (d + y, "right", d + y, y)
    return None


def _electrostatics(text: str, lang: str, eng: bool):
    qs = _charges(text)
    d = _distance_m(text)
    if 1 not in qs or 2 not in qs or not d:
        return None
    low = text.lower()
    wants_zero = any(
        k in text or k in low
        for k in (
            "صفر", "برآیند", "برایند", "میدان", "null", "zero", "cancel",
            "field", "e = 0", "e=0", "net field",
        )
    )
    wants_force = any(k in text or k in low for k in ("نیرو", "force", "نیوتن", "newton", "q3"))
    if not wants_zero and not wants_force and 3 not in qs:
        # still allow if two charges + distance and electrostatic words
        if not any(k in text or k in low for k in ("بار", "charge", "کولن", "coulomb", "الکتر")):
            return None
    k = _find_k(text)
    q1, q2 = qs[1], qs[2]
    q3 = qs.get(3)
    T = _T(lang)
    steps = [T["typed"]]
    extra = T["q3extra"].format(q3=_pretty(q3, eng)) if q3 is not None else ""
    steps.append(T["q"].format(q1=_pretty(q1, eng), q2=_pretty(q2, eng), q3=extra))
    steps.append(T["d"].format(d=_pretty(d, eng)))
    steps.append(T["k"].format(k=_pretty(k, eng)))
    same = (q1 > 0 and q2 > 0) or (q1 < 0 and q2 < 0)
    steps.append(T["signs_same"] if same else T["signs_opp"])
    if not same:
        steps.append(T["side"])
    hit = _zero_field_point(q1, q2, d)
    if not hit:
        return None
    x, region, r1, r2 = hit
    who = 1 if abs(q1) <= abs(q2) else 2
    steps.append(T["region"].format(who=who))
    steps.append(T["eq"])
    if region == "left":
        side = T["left"]
        pos = r1
        ans_a = T["pos"].format(pos=_pretty(r1, eng), side=side)
    elif region == "right":
        side = T["right"]
        pos = r1
        ans_a = T["pos"].format(pos=_pretty(r1, eng), side=side)
    else:
        side = T["between"].format(x=_pretty(x, eng))
        pos = x
        ans_a = T["pos"].format(pos=_pretty(x, eng), side=side)
    steps.append(T["ans_a"].format(ans=ans_a))
    parts = [ans_a]
    f_text = None
    if q3 is not None or wants_force:
        steps.append(T["force0"])
        f_text = _pretty(0.0, eng, "N")
        steps.append(T["ans_b"].format(f="0"))
        parts.append(T["force"].format(f="0"))
    shown = "  |  ".join(parts)
    return {
        "ok": True,
        "kind": "word.electro.e0",
        "text": shown,
        "solutions": parts,
        "detail": {
            "q1": q1,
            "q2": q2,
            "q3": q3,
            "d": d,
            "x_from_q1": x,
            "r1": r1,
            "r2": r2,
            "region": region,
            "force_N": 0.0 if (q3 is not None or wants_force) else None,
        },
        "steps": steps,
    }


def _coulomb_only(text: str, lang: str, eng: bool):
    qs = _charges(text)
    d = _distance_m(text)
    if 1 not in qs or 2 not in qs or not d:
        return None
    low = text.lower()
    if not any(k in text or k in low for k in ("نیرو", "force", "کولن", "coulomb")):
        return None
    if any(k in text or k in low for k in ("صفر", "میدان", "field", "zero")):
        return None
    k = _find_k(text)
    f = k * qs[1] * qs[2] / (d ** 2)
    T = _T(lang)
    shown = T["coul"].format(f=_pretty(abs(f), eng))
    attr = "attractive" if f < 0 else "repulsive"
    if lang == "fa":
        attr = "ربایشی" if f < 0 else "رانشی"
    return {
        "ok": True,
        "kind": "word.electro.coulomb",
        "text": shown + " (" + attr + ")",
        "solutions": [shown],
        "steps": [T["typed"], T["q"].format(q1=_pretty(qs[1], eng), q2=_pretty(qs[2], eng), q3=""), T["d"].format(d=_pretty(d, eng)), shown],
    }


def _one_field(text: str, lang: str, eng: bool):
    qs = _charges(text)
    d = _distance_m(text)
    if len(qs) != 1 or not d:
        return None
    low = text.lower()
    if not any(k in text or k in low for k in ("میدان", "field", "E")):
        return None
    q = next(iter(qs.values()))
    k = _find_k(text)
    e = k * abs(q) / (d ** 2)
    T = _T(lang)
    shown = T["efield"].format(e=_pretty(e, eng))
    return {"ok": True, "kind": "word.electro.e", "text": shown, "solutions": [shown], "steps": [T["typed"], shown]}


def _ohm_word(text: str, lang: str, eng: bool):
    low = text.lower()
    if not any(k in text or k in low for k in ("مقاومت", "ولتاژ", "جریان", "ohm", "volt", "ampere", "amp")):
        return None
    if any(k in text or k in low for k in ("بار", "میدان", "charge", "field")):
        return None

    def grab(names, scale=1.0):
        for n in names:
            m = re.search(rf"(?:{n})\s*=\s*([+-]?\d+(?:\.\d+)?(?:e[+-]?\d+)?)", text, re.I)
            if m:
                v = _num(m.group(1))
                if v is not None:
                    return v * scale
        return None

    V = grab(["V", "ولت", "ولتاژ", "voltage"])
    I = grab(["I", "جریان", "amp", "ampere"])
    R = grab(["R", "مقاومت", "ohm"])
    # units in text
    m = re.search(r"([+-]?\d+(?:\.\d+)?)\s*(mA|A|kΩ|kohm|ohm|Ω|V)\b", text, re.I)
    # fill missing from first matching numbers with units
    for m in re.finditer(r"([+-]?\d+(?:\.\d+)?)\s*(ma|a|kω|kohm|ohm|ω|v)\b", text, re.I):
        val = _num(m.group(1))
        u = m.group(2).lower()
        if val is None:
            continue
        if u in ("v",) and V is None:
            V = val
        elif u == "ma" and I is None:
            I = val * 1e-3
        elif u == "a" and I is None:
            I = val
        elif u in ("kω", "kohm") and R is None:
            R = val * 1e3
        elif u in ("ohm", "ω") and R is None:
            R = val
    known = sum(x is not None for x in (V, I, R))
    if known < 2:
        return None
    if V is None:
        ans, name = I * R, "V"
    elif I is None:
        if abs(R or 0) < 1e-18:
            return None
        ans, name = V / R, "I"
    else:
        if abs(I or 0) < 1e-18:
            return None
        ans, name = V / I, "R"
    T = _T(lang)
    shown = T["ohm"].format(ans=f"{name} = {_pretty(ans, eng)}")
    return {"ok": True, "kind": "word.ohm", "text": shown, "solutions": [shown], "steps": [T["typed"], shown]}


def _kinematics(text: str, lang: str, eng: bool):
    low = text.lower()
    if not any(k in text or k in low for k in ("شتاب", "سرعت", "ثانیه", "acceleration", "velocity", "m/s")):
        return None
    if any(k in text or k in low for k in ("بار", "میدان", "charge", "field")):
        return None

    def grab(pats):
        for p in pats:
            m = re.search(p, text, re.I)
            if m:
                return _num(m.group(1))
        return None

    v0 = grab([r"v0\s*=\s*([+-]?\d+(?:\.\d+)?)", r"سرعت\s*اولیه[^\d]*([+-]?\d+(?:\.\d+)?)"])
    v = grab([r"(?<!v)\bv\s*=\s*([+-]?\d+(?:\.\d+)?)", r"سرعت\s*(?:نهایی|ثانویه)?[^\d]*([+-]?\d+(?:\.\d+)?)"])
    a = grab([r"\ba\s*=\s*([+-]?\d+(?:\.\d+)?)", r"شتاب[^\d]*([+-]?\d+(?:\.\d+)?)"] )
    t = grab([r"\bt\s*=\s*([+-]?\d+(?:\.\d+)?)", r"زمان[^\d]*([+-]?\d+(?:\.\d+)?)", r"([+-]?\d+(?:\.\d+)?)\s*(?:s|ثانیه)\b"])
    x = grab([r"\b(?:x|s)\s*=\s*([+-]?\d+(?:\.\d+)?)", r"جابجایی[^\d]*([+-]?\d+(?:\.\d+)?)"] )
    T = _T(lang)
    # v = v0 + a t
    if v is None and v0 is not None and a is not None and t is not None:
        ans = v0 + a * t
        shown = T["kin"].format(ans=f"v = {_pretty(ans, eng)} m/s")
        return {"ok": True, "kind": "word.kin", "text": shown, "solutions": [shown], "steps": [T["typed"], "v = v0 + a t", shown]}
    if x is None and v0 is not None and a is not None and t is not None:
        ans = v0 * t + 0.5 * a * t * t
        shown = T["kin"].format(ans=f"x = {_pretty(ans, eng)} m")
        return {"ok": True, "kind": "word.kin", "text": shown, "solutions": [shown], "steps": [T["typed"], "x = v0 t + ½ a t²", shown]}
    if t is None and v0 is not None and v is not None and a is not None and abs(a) > 1e-18:
        ans = (v - v0) / a
        shown = T["kin"].format(ans=f"t = {_pretty(ans, eng)} s")
        return {"ok": True, "kind": "word.kin", "text": shown, "solutions": [shown], "steps": [T["typed"], "t = (v - v0)/a", shown]}
    return None


def try_solve(raw: str, lang: str = "en", eng: bool = False):
    """Return a problem dict or None if this is not a handled word problem."""
    try:
        text = _clean(raw)
        if not text.strip() or not _looks_word(text):
            return None
        for fn in (_electrostatics, _coulomb_only, _one_field, _ohm_word, _kinematics):
            try:
                hit = fn(text, lang, eng)
            except Exception:
                hit = None
            if hit:
                return hit
        return None
    except Exception:
        return None
