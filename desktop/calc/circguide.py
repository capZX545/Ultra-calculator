"""Step-by-step circuit builder. Independent copy.

Asks what the two parts are, then asks series or parallel.
Never asks "how many in parallel".
"""

from __future__ import annotations

import math
import re
import unicodedata

_DIGIT = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")

_SUF = {
    "t": 1e12,
    "g": 1e9,
    "meg": 1e6,
    "k": 1e3,
    "m": 1e-3,
    "u": 1e-6,
    "µ": 1e-6,
    "n": 1e-9,
    "p": 1e-12,
    "f": 1e-15,
}

_KINDS = ("R", "C", "L")

_KIND_META = {
    "R": {
        "en": "resistor",
        "fa": "مقاومت",
        "fi": "vastus",
        "unit": "ohm",
        "symbol": "R",
    },
    "C": {
        "en": "capacitor",
        "fa": "خازن",
        "fi": "kondensaattori",
        "unit": "F",
        "symbol": "C",
    },
    "L": {
        "en": "inductor",
        "fa": "سلف",
        "fi": "kela",
        "unit": "H",
        "symbol": "L",
    },
}

_T = {
    "en": {
        "ask_a": "What is the first circuit?",
        "ask_b": "What is the second circuit?",
        "ask_conn": "How are those two circuits connected?",
        "ask_freq": "The two parts are different kinds. What is the frequency?",
        "pick_kind": "Pick the type, then type its value.",
        "need_val": "Type the value first.",
        "need_kind": "Pick the type first.",
        "bad_val": "That value was not read. Try 4.7k or 10u or 2.2.",
        "series": "Series",
        "parallel": "Parallel",
        "next": "Next",
        "add": "Add another part",
        "reset": "Start over",
        "back": "Back",
        "a_is": "First circuit: {text}",
        "b_is": "Second circuit: {text}",
        "conn_is": "Connection: {text}",
        "eq_was": "Equivalent so far: {text}",
        "formula": "Formula: {text}",
        "result": "Equivalent = {text}",
        "step_read": "Circuit 1 is {a}. Circuit 2 is {b}.",
        "step_conn": "They are connected in {conn}.",
        "step_plug": "Substitute: {text}",
        "step_out": "So the equivalent is {text}.",
        "step_mixed": "Different kinds. Use impedance at f = {f}.",
        "z_series": "Zeq = Z1 + Z2",
        "z_par": "Zeq = Z1 Z2 / (Z1 + Z2)",
        "r_series": "Req = R1 + R2",
        "r_par": "Req = R1 R2 / (R1 + R2)",
        "c_series": "Ceq = C1 C2 / (C1 + C2)",
        "c_par": "Ceq = C1 + C2",
        "l_series": "Leq = L1 + L2",
        "l_par": "Leq = L1 L2 / (L1 + L2)",
        "fail": "Could not combine those two. Showing 0.",
        "hint": "First say what the two circuits are. Then say series or parallel. You can add another part after that.",
        "freq_hint": "Hz  (50, 60, 1k)",
        "val_hint": {
            "R": "ohm   e.g. 1k  4.7k  10",
            "C": "farad  e.g. 10u  100n  47p",
            "L": "henry  e.g. 10m  100u  1",
        },
    },
    "fa": {
        "ask_a": "مدار اول چیست؟",
        "ask_b": "مدار دوم چیست؟",
        "ask_conn": "این دو مدار چطور به هم وصل شده‌اند؟",
        "ask_freq": "جنس این دو تا فرق دارد. فرکانس چند است؟",
        "pick_kind": "اول نوع را بزن، بعد مقدار را بنویس.",
        "need_val": "اول مقدار را بنویس.",
        "need_kind": "اول نوع را انتخاب کن.",
        "bad_val": "مقدار خوانده نشد. مثلاً ۴.۷k یا ۱۰u یا ۲.۲",
        "series": "سری",
        "parallel": "موازی",
        "next": "بعدی",
        "add": "یک قطعه دیگر اضافه کن",
        "reset": "از اول",
        "back": "برگشت",
        "a_is": "مدار اول: {text}",
        "b_is": "مدار دوم: {text}",
        "conn_is": "اتصال: {text}",
        "eq_was": "معادل تا اینجا: {text}",
        "formula": "فرمول: {text}",
        "result": "معادل = {text}",
        "step_read": "مدار ۱ {a} است. مدار ۲ {b} است.",
        "step_conn": "اتصال {conn} است.",
        "step_plug": "جایگذاری: {text}",
        "step_out": "پس معادل می‌شود {text}.",
        "step_mixed": "جنس‌ها فرق دارند. امپدانس در f = {f}.",
        "z_series": "Zeq = Z1 + Z2",
        "z_par": "Zeq = Z1 Z2 / (Z1 + Z2)",
        "r_series": "Req = R1 + R2",
        "r_par": "Req = R1 R2 / (R1 + R2)",
        "c_series": "Ceq = C1 C2 / (C1 + C2)",
        "c_par": "Ceq = C1 + C2",
        "l_series": "Leq = L1 + L2",
        "l_par": "Leq = L1 L2 / (L1 + L2)",
        "fail": "این دو تا ترکیب نشد. ۰.",
        "hint": "اول بگو دو تا مدار چی هستند. بعد بگو سری‌اند یا موازی. بعد از جواب می‌توانی قطعه بعدی را اضافه کنی.",
        "freq_hint": "هرتز  (۵۰، ۶۰، ۱k)",
        "val_hint": {
            "R": "اهم   مثلاً 1k  4.7k  10",
            "C": "فاراد  مثلاً 10u  100n  47p",
            "L": "هانری  مثلاً 10m  100u  1",
        },
    },
    "fi": {
        "ask_a": "Mika on ensimmainen piiri?",
        "ask_b": "Mika on toinen piiri?",
        "ask_conn": "Miten nuo kaksi piiria on kytketty?",
        "ask_freq": "Osat ovat eri tyyppia. Mika on taajuus?",
        "pick_kind": "Valitse tyyppi ja kirjoita arvo.",
        "need_val": "Kirjoita arvo ensin.",
        "need_kind": "Valitse tyyppi ensin.",
        "bad_val": "Arvoa ei voitu lukea. Kokeile 4.7k tai 10u.",
        "series": "Sarjaan",
        "parallel": "Rinnan",
        "next": "Seuraava",
        "add": "Lisaa seuraava osa",
        "reset": "Alusta",
        "back": "Takaisin",
        "a_is": "Ensimmainen piiri: {text}",
        "b_is": "Toinen piiri: {text}",
        "conn_is": "Kytkenta: {text}",
        "eq_was": "Ekvivalentti tahan asti: {text}",
        "formula": "Kaava: {text}",
        "result": "Ekvivalentti = {text}",
        "step_read": "Piiri 1 on {a}. Piiri 2 on {b}.",
        "step_conn": "Kytkenta on {conn}.",
        "step_plug": "Sijoitus: {text}",
        "step_out": "Ekvivalentti on siis {text}.",
        "step_mixed": "Eri tyypit. Impedanssi taajuudella f = {f}.",
        "z_series": "Zeq = Z1 + Z2",
        "z_par": "Zeq = Z1 Z2 / (Z1 + Z2)",
        "r_series": "Req = R1 + R2",
        "r_par": "Req = R1 R2 / (R1 + R2)",
        "c_series": "Ceq = C1 C2 / (C1 + C2)",
        "c_par": "Ceq = C1 + C2",
        "l_series": "Leq = L1 + L2",
        "l_par": "Leq = L1 L2 / (L1 + L2)",
        "fail": "Yhdistaminen ei onnistunut. 0.",
        "hint": "Kerro ensin kaksi piiria. Sitten sarja tai rinnan.",
        "freq_hint": "Hz  (50, 60, 1k)",
        "val_hint": {
            "R": "ohm   esim. 1k  4.7k  10",
            "C": "faradi  esim. 10u  100n  47p",
            "L": "henry  esim. 10m  100u  1",
        },
    },
}


def _pack(lang: str) -> dict:
    return _T.get(lang) or _T["en"]


def _kind_name(kind: str, lang: str) -> str:
    meta = _KIND_META.get(kind) or _KIND_META["R"]
    return meta.get(lang) or meta["en"]


def _num(raw, default=None):
    if raw is None:
        return default
    text = unicodedata.normalize("NFKC", str(raw)).strip().translate(_DIGIT)
    if not text or text in {"?", "x", "X", "unknown"}:
        return default
    text = text.replace(" ", "").replace("ω", "").replace("Ω", "")
    text = text.replace("×", "*").replace(",", ".")
    low = text.lower()
    for word in ("ohm", "ohms", "farad", "henry", "hz", "hertz"):
        if low.endswith(word):
            text = text[: -len(word)]
            low = text.lower()
            break
    # People write 10e-2 for 10^(-2) = 0.01. Ordinary 2e-3 stays 0.002.
    special = re.fullmatch(r"10[eE]([+\-]?\d+)", text)
    if special:
        try:
            return float(10.0 ** int(special.group(1)))
        except Exception:
            pass
    m = re.fullmatch(r"([+\-]?\d*\.?\d+(?:[eE][+\-]?\d+)?)([a-zA-Zµ]*)", text)
    if not m:
        try:
            return float(text)
        except Exception:
            return default
    try:
        val = float(m.group(1))
    except Exception:
        return default
    suf = (m.group(2) or "").lower()
    if suf in {"a", "v", "w", "hz", "s", "h", "f"}:
        suf = ""
    if suf == "meg":
        return val * 1e6
    if suf in _SUF:
        return val * _SUF[suf]
    return val


def _pretty(x, unit: str = "", eng: bool = True) -> str:
    try:
        if isinstance(x, complex):
            if abs(x.imag) < 1e-12:
                return _pretty(x.real, unit, eng)
            sign = "+" if x.imag >= 0 else "-"
            return f"{_pretty(x.real, '', eng)} {sign} j{_pretty(abs(x.imag), '', eng)}" + (
                f" {unit}" if unit else ""
            )
        v = float(x)
    except Exception:
        return str(x)
    if not math.isfinite(v):
        return "undefined"
    if abs(v) < 1e-18:
        return "0" + (f" {unit}" if unit else "")
    ax = abs(v)
    prefixes = [
        (1e12, "T"),
        (1e9, "G"),
        (1e6, "M"),
        (1e3, "k"),
        (1, ""),
        (1e-3, "m"),
        (1e-6, "u"),
        (1e-9, "n"),
        (1e-12, "p"),
    ]
    pref = ""
    shown = v
    if eng or unit:
        for scale, name in prefixes:
            if ax >= scale * 0.999:
                shown = v / scale
                pref = name
                break
        else:
            shown = v / 1e-12
            pref = "p"
    text = f"{shown:.8g}"
    return f"{text} {pref}{unit}".strip()


def _blank_state() -> dict:
    return {
        "phase": "a",
        "a": {},
        "b": {},
        "conn": "",
        "freq": None,
        "eq": {},
        "hist": [],
        "picked": "",
    }


def _copy_state(state) -> dict:
    src = state if isinstance(state, dict) else {}
    out = _blank_state()
    out["phase"] = str(src.get("phase") or "a")
    for key in ("a", "b", "eq"):
        val = src.get(key)
        out[key] = dict(val) if isinstance(val, dict) else {}
    out["conn"] = str(src.get("conn") or "")
    out["freq"] = src.get("freq")
    hist = src.get("hist")
    out["hist"] = list(hist) if isinstance(hist, list) else []
    out["picked"] = str(src.get("picked") or "")
    return out


def _part_text(part: dict, lang: str, eng: bool) -> str:
    if not part or not part.get("kind"):
        return "—"
    kind = str(part.get("kind") or "R")
    name = _kind_name(kind, lang)
    unit = (_KIND_META.get(kind) or {}).get("unit") or ""
    if part.get("val") is None:
        return name
    return f"{name} {_pretty(part.get('val'), unit, eng)}"


def _kind_choices(lang: str) -> list:
    return [{"id": k, "label": _kind_name(k, lang)} for k in _KINDS]


def _conn_choices(lang: str) -> list:
    p = _pack(lang)
    return [
        {"id": "series", "label": p["series"]},
        {"id": "parallel", "label": p["parallel"]},
    ]


def _actions(lang: str, phase: str) -> list:
    p = _pack(lang)
    rows = []
    if phase != "a":
        rows.append({"id": "back", "label": p["back"]})
    if phase == "done":
        rows = [
            {"id": "add", "label": p["add"]},
            {"id": "reset", "label": p["reset"]},
        ]
    return rows


def _impedance(kind: str, val: float, freq: float):
    w = 2 * math.pi * float(freq or 0.0)
    if kind == "R":
        return complex(float(val), 0.0)
    if kind == "C":
        if abs(w * val) < 1e-30:
            return None
        return 1.0 / (1j * w * val)
    if kind == "L":
        return 1j * w * float(val)
    return None


def _combine(a: dict, b: dict, conn: str, freq, lang: str, eng: bool) -> dict:
    p = _pack(lang)
    ka = str(a.get("kind") or "")
    kb = str(b.get("kind") or "")
    try:
        va = float(a.get("val"))
        vb = float(b.get("val"))
    except Exception:
        return {"ok": False, "text": "0", "formula": "", "eq": {}, "steps": [p["fail"]]}
    conn = "parallel" if str(conn).lower().startswith("p") or str(conn) in {"موازی", "rinnan"} else "series"
    conn_name = p["parallel"] if conn == "parallel" else p["series"]
    steps = [
        p["step_read"].format(a=_part_text(a, lang, eng), b=_part_text(b, lang, eng)),
        p["step_conn"].format(conn=conn_name),
    ]

    if ka == kb == "R":
        formula = p["r_par"] if conn == "parallel" else p["r_series"]
        if conn == "series":
            eqv = va + vb
            plug = f"{_pretty(va, 'ohm', eng)} + {_pretty(vb, 'ohm', eng)}"
        else:
            den = va + vb
            eqv = (va * vb / den) if abs(den) > 1e-18 else 0.0
            plug = f"{_pretty(va, 'ohm', eng)} || {_pretty(vb, 'ohm', eng)}"
        shown = _pretty(eqv, "ohm", eng)
        steps.append(p["formula"].format(text=formula))
        steps.append(p["step_plug"].format(text=plug))
        steps.append(p["step_out"].format(text=shown))
        return {
            "ok": True,
            "text": shown,
            "formula": formula,
            "eq": {"kind": "R", "val": eqv},
            "steps": steps,
        }

    if ka == kb == "C":
        formula = p["c_par"] if conn == "parallel" else p["c_series"]
        if conn == "parallel":
            eqv = va + vb
            plug = f"{_pretty(va, 'F', eng)} + {_pretty(vb, 'F', eng)}"
        else:
            den = va + vb
            eqv = (va * vb / den) if abs(den) > 1e-18 else 0.0
            plug = f"{_pretty(va, 'F', eng)} series {_pretty(vb, 'F', eng)}"
        shown = _pretty(eqv, "F", eng)
        steps.append(p["formula"].format(text=formula))
        steps.append(p["step_plug"].format(text=plug))
        steps.append(p["step_out"].format(text=shown))
        return {
            "ok": True,
            "text": shown,
            "formula": formula,
            "eq": {"kind": "C", "val": eqv},
            "steps": steps,
        }

    if ka == kb == "L":
        formula = p["l_par"] if conn == "parallel" else p["l_series"]
        if conn == "series":
            eqv = va + vb
            plug = f"{_pretty(va, 'H', eng)} + {_pretty(vb, 'H', eng)}"
        else:
            den = va + vb
            eqv = (va * vb / den) if abs(den) > 1e-18 else 0.0
            plug = f"{_pretty(va, 'H', eng)} || {_pretty(vb, 'H', eng)}"
        shown = _pretty(eqv, "H", eng)
        steps.append(p["formula"].format(text=formula))
        steps.append(p["step_plug"].format(text=plug))
        steps.append(p["step_out"].format(text=shown))
        return {
            "ok": True,
            "text": shown,
            "formula": formula,
            "eq": {"kind": "L", "val": eqv},
            "steps": steps,
        }

    f = _num(freq, None)
    if f is None or f <= 0:
        return {"need_freq": True}

    z1 = _impedance(ka, va, f)
    z2 = _impedance(kb, vb, f)
    if z1 is None or z2 is None:
        return {"ok": False, "text": "0", "formula": "", "eq": {}, "steps": [p["fail"]]}
    formula = p["z_par"] if conn == "parallel" else p["z_series"]
    if conn == "series":
        zeq = z1 + z2
    else:
        den = z1 + z2
        zeq = (z1 * z2 / den) if abs(den) > 1e-18 else 0j
    shown = _pretty(zeq, "ohm", eng)
    steps.append(p["step_mixed"].format(f=_pretty(f, "Hz", eng)))
    steps.append(p["formula"].format(text=formula))
    steps.append(p["step_plug"].format(text=f"Z1={_pretty(z1, 'ohm', eng)}; Z2={_pretty(z2, 'ohm', eng)}"))
    steps.append(p["step_out"].format(text=shown))
    # Keep the equivalent as a resistor-like impedance magnitude for further R-only adds
    # but mark kind as mixed R so next same-kind combine is not forced.
    mag = abs(zeq)
    return {
        "ok": True,
        "text": shown,
        "formula": formula,
        "eq": {"kind": "R", "val": mag, "z": [zeq.real, zeq.imag], "mixed": True},
        "steps": steps,
    }


def _view(state: dict, lang: str, eng: bool, note: str = "") -> dict:
    p = _pack(lang)
    phase = state.get("phase") or "a"
    prompt = p["ask_a"]
    choices = _kind_choices(lang)
    need_value = True
    value_hint = p["val_hint"]["R"]
    if phase == "a":
        prompt = p["ask_a"]
        picked = state.get("picked") or (state.get("a") or {}).get("kind") or ""
        if picked in _KINDS:
            value_hint = p["val_hint"][picked]
    elif phase == "b":
        prompt = p["ask_b"]
        picked = state.get("picked") or (state.get("b") or {}).get("kind") or ""
        if picked in _KINDS:
            value_hint = p["val_hint"][picked]
    elif phase == "conn":
        prompt = p["ask_conn"]
        choices = _conn_choices(lang)
        need_value = False
        value_hint = ""
    elif phase == "freq":
        prompt = p["ask_freq"]
        choices = []
        need_value = True
        value_hint = p["freq_hint"]
    elif phase == "done":
        prompt = p["result"].format(text=state.get("text") or "0")
        choices = []
        need_value = False
        value_hint = ""
    else:
        phase = "a"
        state["phase"] = "a"

    story = []
    if (state.get("hist") or []) and phase in {"b", "conn", "freq", "done"}:
        last = state["hist"][-1] if state["hist"] else ""
        if last:
            story.append(str(last))
    if state.get("a"):
        story.append(p["a_is"].format(text=_part_text(state["a"], lang, eng)))
    if state.get("b") and phase in {"conn", "freq", "done"}:
        story.append(p["b_is"].format(text=_part_text(state["b"], lang, eng)))
    if state.get("conn") and phase in {"freq", "done"}:
        cname = p["parallel"] if state["conn"] == "parallel" else p["series"]
        story.append(p["conn_is"].format(text=cname))
    if note:
        story.append(note)

    return {
        "ok": True,
        "phase": phase,
        "prompt": prompt,
        "hint": p["hint"],
        "choices": choices,
        "need_value": need_value,
        "value_hint": value_hint,
        "picked": state.get("picked") or "",
        "next_label": p["next"],
        "story": story,
        "text": state.get("text") or "",
        "formula": state.get("formula") or "",
        "steps": list(state.get("steps") or []),
        "actions": _actions(lang, phase),
        "state": {
            "phase": state.get("phase") or "a",
            "a": dict(state.get("a") or {}),
            "b": dict(state.get("b") or {}),
            "conn": state.get("conn") or "",
            "freq": state.get("freq"),
            "eq": dict(state.get("eq") or {}),
            "hist": list(state.get("hist") or []),
            "picked": state.get("picked") or "",
            "text": state.get("text") or "",
            "formula": state.get("formula") or "",
            "steps": list(state.get("steps") or []),
        },
    }


def _fill_part(state: dict, which: str, kind: str, value, lang: str) -> str:
    p = _pack(lang)
    part = dict(state.get(which) or {})
    k = str(kind or state.get("picked") or part.get("kind") or "").upper()
    if k in {"SERIES", "PARALLEL"}:
        k = ""
    if k and k not in _KINDS:
        aliases = {
            "resistor": "R",
            "resistance": "R",
            "مقاومت": "R",
            "vastus": "R",
            "capacitor": "C",
            "خازن": "C",
            "kondensaattori": "C",
            "inductor": "L",
            "سلف": "L",
            "kela": "L",
        }
        k = aliases.get(str(kind).lower(), k)
    if k in _KINDS:
        part["kind"] = k
        state["picked"] = k
    if value is not None and str(value).strip() != "":
        parsed = _num(value, None)
        if parsed is None:
            state[which] = part
            return p["bad_val"]
        if parsed < 0:
            parsed = abs(parsed)
        part["val"] = parsed
    state[which] = part
    return ""


def run(body=None, **kwargs) -> dict:
    try:
        data = {}
        if isinstance(body, dict):
            data.update(body)
        data.update(kwargs)
        lang = str(data.get("lang") or "en")
        if lang not in _T:
            lang = "en"
        eng = bool(data.get("eng", True))
        action = str(data.get("action") or "start").lower().strip()
        state = _copy_state(data.get("state"))
        kind = data.get("kind") or data.get("choice") or ""
        value = data.get("value")
        conn = data.get("conn") or ""
        p = _pack(lang)

        if action in {"start", "reset", ""}:
            return _view(_blank_state(), lang, eng)

        if action == "back":
            phase = state.get("phase") or "a"
            if phase == "b":
                state["phase"] = "a"
                state["b"] = {}
                state["picked"] = (state.get("a") or {}).get("kind") or ""
            elif phase == "conn":
                state["phase"] = "b"
                state["conn"] = ""
                state["picked"] = (state.get("b") or {}).get("kind") or ""
            elif phase == "freq":
                state["phase"] = "conn"
            elif phase == "done":
                state["phase"] = "conn"
                state["text"] = ""
                state["formula"] = ""
                state["steps"] = []
            else:
                state = _blank_state()
            return _view(state, lang, eng)

        if action == "add":
            eq = state.get("eq") or {}
            if not eq.get("kind") or eq.get("val") is None:
                return _view(_blank_state(), lang, eng)
            nxt = _blank_state()
            nxt["a"] = {"kind": eq.get("kind"), "val": eq.get("val")}
            nxt["phase"] = "b"
            shown = _part_text(nxt["a"], lang, eng)
            nxt["hist"] = list(state.get("hist") or []) + [p["eq_was"].format(text=shown)]
            return _view(nxt, lang, eng)

        if action == "pick":
            k = str(kind or "").upper()
            if k in {"SERIES", "S", "SERI", "سری"} or str(kind) in {p["series"], "series"}:
                state["conn"] = "series"
                state["phase"] = "freq" if _needs_freq(state) else "done"
                if state["phase"] == "done":
                    return _finish(state, lang, eng)
                return _view(state, lang, eng)
            if k in {"PARALLEL", "P", "PAR", "موازی"} or str(kind) in {p["parallel"], "parallel"}:
                state["conn"] = "parallel"
                state["phase"] = "freq" if _needs_freq(state) else "done"
                if state["phase"] == "done":
                    return _finish(state, lang, eng)
                return _view(state, lang, eng)
            if k not in _KINDS:
                aliases = {
                    "resistor": "R",
                    "مقاومت": "R",
                    "vastus": "R",
                    "capacitor": "C",
                    "خازن": "C",
                    "kondensaattori": "C",
                    "inductor": "L",
                    "سلف": "L",
                    "kela": "L",
                }
                k = aliases.get(str(kind).lower(), "")
            if k not in _KINDS:
                return _view(state, lang, eng, note=p["need_kind"])
            state["picked"] = k
            which = "a" if state.get("phase") in {"a", ""} else "b"
            if state.get("phase") == "conn":
                return _view(state, lang, eng)
            part = dict(state.get(which) or {})
            part["kind"] = k
            state[which] = part
            return _view(state, lang, eng)

        if action in {"next", "value", "set"}:
            phase = state.get("phase") or "a"
            if phase == "freq":
                parsed = _num(value, None)
                if parsed is None or parsed <= 0:
                    return _view(state, lang, eng, note=p["bad_val"])
                state["freq"] = parsed
                return _finish(state, lang, eng)
            if phase == "conn":
                raw = str(conn or kind or value or "").lower()
                if raw in {"series", "seri", "s", "سری"} or raw == p["series"].lower():
                    state["conn"] = "series"
                elif raw in {"parallel", "par", "p", "موازی"} or raw == p["parallel"].lower():
                    state["conn"] = "parallel"
                else:
                    return _view(state, lang, eng, note=p["need_kind"])
                if _needs_freq(state):
                    state["phase"] = "freq"
                    return _view(state, lang, eng)
                return _finish(state, lang, eng)
            which = "a" if phase == "a" else "b"
            err = _fill_part(state, which, kind or state.get("picked") or "", value, lang)
            if err:
                return _view(state, lang, eng, note=err)
            part = state.get(which) or {}
            if not part.get("kind"):
                return _view(state, lang, eng, note=p["need_kind"])
            if part.get("val") is None:
                return _view(state, lang, eng, note=p["need_val"])
            if phase == "a":
                state["phase"] = "b"
                state["picked"] = ""
                return _view(state, lang, eng)
            state["phase"] = "conn"
            state["picked"] = ""
            return _view(state, lang, eng)

        if action == "connect":
            raw = str(conn or kind or "").lower()
            if raw in {"series", "seri", "s", "سری"} or raw == p["series"].lower():
                state["conn"] = "series"
            elif raw in {"parallel", "par", "p", "موازی"} or raw == p["parallel"].lower():
                state["conn"] = "parallel"
            else:
                state["phase"] = "conn"
                return _view(state, lang, eng, note=p["need_kind"])
            if _needs_freq(state):
                state["phase"] = "freq"
                return _view(state, lang, eng)
            return _finish(state, lang, eng)

        return _view(state, lang, eng)
    except Exception:
        st = _blank_state()
        lang = "en"
        try:
            lang = str((body or {}).get("lang") or kwargs.get("lang") or "en")
        except Exception:
            lang = "en"
        out = _view(st, lang if lang in _T else "en", True)
        out["text"] = "0"
        out["steps"] = [_pack(lang if lang in _T else "en")["fail"]]
        return out


def _needs_freq(state: dict) -> bool:
    a = state.get("a") or {}
    b = state.get("b") or {}
    ka, kb = a.get("kind"), b.get("kind")
    if not ka or not kb:
        return False
    return ka != kb


def _finish(state: dict, lang: str, eng: bool) -> dict:
    p = _pack(lang)
    a = state.get("a") or {}
    b = state.get("b") or {}
    if not a.get("kind") or a.get("val") is None:
        state["phase"] = "a"
        return _view(state, lang, eng, note=p["need_val"])
    if not b.get("kind") or b.get("val") is None:
        state["phase"] = "b"
        return _view(state, lang, eng, note=p["need_val"])
    if not state.get("conn"):
        state["phase"] = "conn"
        return _view(state, lang, eng)
    out = _combine(a, b, state.get("conn") or "series", state.get("freq"), lang, eng)
    if out.get("need_freq"):
        state["phase"] = "freq"
        return _view(state, lang, eng)
    if not out.get("ok"):
        state["phase"] = "done"
        state["text"] = "0"
        state["formula"] = ""
        state["steps"] = out.get("steps") or [p["fail"]]
        state["eq"] = {}
        return _view(state, lang, eng)
    state["phase"] = "done"
    state["text"] = out.get("text") or "0"
    state["formula"] = out.get("formula") or ""
    state["steps"] = out.get("steps") or []
    state["eq"] = out.get("eq") or {}
    return _view(state, lang, eng)
