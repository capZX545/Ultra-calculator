"""Statistics from pasted numbers. Independent copy."""

from __future__ import annotations

import math
import re
import unicodedata

_DIGIT = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")


def _pretty(x) -> str:
    try:
        v = float(x)
    except Exception:
        return str(x)
    if not math.isfinite(v):
        return "undefined"
    if abs(v) < 1e-15:
        return "0"
    return f"{v:.12g}"


def parse_table(text: str):
    s = unicodedata.normalize("NFKC", str(text or "")).translate(_DIGIT)
    rows = []
    for line in s.replace(";", "\n").splitlines():
        line = line.strip()
        if not line:
            continue
        line = line.replace(",", " ")
        nums = []
        for p in line.split():
            try:
                nums.append(float(p))
            except Exception:
                continue
        if nums:
            rows.append(nums)
    if not rows:
        # one blob of numbers
        nums = []
        for m in re.finditer(r"[+\-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+\-]?[0-9]+)?", s):
            nums.append(float(m.group(0)))
        if nums:
            rows = [[x] for x in nums]
    return rows


def _mean(xs):
    return sum(xs) / len(xs) if xs else 0.0


def _var(xs, ddof=1):
    n = len(xs)
    if n <= ddof:
        return 0.0
    m = _mean(xs)
    return sum((x - m) ** 2 for x in xs) / (n - ddof)


def _pct(xs, p):
    if not xs:
        return 0.0
    ys = sorted(xs)
    k = (len(ys) - 1) * p / 100.0
    f = int(math.floor(k))
    c = int(math.ceil(k))
    if f == c:
        return ys[f]
    return ys[f] * (c - k) + ys[c] * (k - f)


def _hist(xs, bins=8):
    if not xs:
        return []
    lo, hi = min(xs), max(xs)
    if hi == lo:
        return [(lo, hi, len(xs))]
    n = max(4, min(int(bins or 8), 24))
    w = (hi - lo) / n
    counts = [0] * n
    for x in xs:
        i = int((x - lo) / w)
        if i >= n:
            i = n - 1
        if i < 0:
            i = 0
        counts[i] += 1
    out = []
    for i, c in enumerate(counts):
        out.append((lo + i * w, lo + (i + 1) * w, c))
    return out


def _svg_hist(bins, w=640, h=220):
    if not bins:
        return ""
    mx = max(c for _, _, c in bins) or 1
    pad = 36
    iw, ih = w - 2 * pad, h - 2 * pad
    bw = iw / len(bins)
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">']
    parts.append(f'<rect width="{w}" height="{h}" fill="#11141a"/>')
    parts.append(f'<line x1="{pad}" y1="{h-pad}" x2="{w-pad}" y2="{h-pad}" stroke="#9aa3ad"/>')
    for i, (a, b, c) in enumerate(bins):
        bh = ih * (c / mx)
        x = pad + i * bw + 2
        y = h - pad - bh
        parts.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw-4:.1f}" height="{bh:.1f}" fill="#c4a35a"/>')
    parts.append("</svg>")
    return "".join(parts)


def run(text: str, eng: bool = False, lang: str = "en") -> dict:
    try:
        rows = parse_table(text)
        if not rows:
            return _fail(lang)
        if len(rows) == 1 and len(rows[0]) > 2:
            rows = [[x] for x in rows[0]]
        cols = max(len(r) for r in rows)
        xs = [r[0] for r in rows]
        n = len(xs)
        m = _mean(xs)
        med = _pct(xs, 50)
        v = _var(xs, 1)
        s = math.sqrt(v) if v >= 0 else 0.0
        q1, q3 = _pct(xs, 25), _pct(xs, 75)
        bits = [
            f"n={n}",
            f"mean={_pretty(m)}",
            f"median={_pretty(med)}",
            f"min={_pretty(min(xs))}",
            f"max={_pretty(max(xs))}",
            f"stdev={_pretty(s)}",
            f"var={_pretty(v)}",
            f"q1={_pretty(q1)}",
            f"q3={_pretty(q3)}",
            f"iqr={_pretty(q3 - q1)}",
        ]
        if n:
            rms = math.sqrt(sum(x * x for x in xs) / n)
            bits.append(f"rms={_pretty(rms)}")
        extra = ""
        if cols >= 2:
            ys = [r[1] if len(r) > 1 else 0.0 for r in rows]
            if n >= 2:
                mx, my = _mean(xs), _mean(ys)
                den = sum((x - mx) ** 2 for x in xs)
                if den:
                    slope = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / den
                    intercept = my - slope * mx
                    bits.append(f"slope={_pretty(slope)}")
                    bits.append(f"intercept={_pretty(intercept)}")
                    extra = f"y = {_pretty(slope)} x + {_pretty(intercept)}"
                    sx = math.sqrt(_var(xs, 1)) if n > 1 else 0
                    sy = math.sqrt(_var(ys, 1)) if n > 1 else 0
                    if sx and sy:
                        cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / (n - 1)
                        bits.append(f"r={_pretty(cov / (sx * sy))}")
        shown = "; ".join(bits)
        hist = _hist(xs)
        svg = _svg_hist(hist)
        steps = {
            "en": [f"Read {n} numbers.", shown],
            "fa": [f"{n} عدد خوانده شد.", shown],
            "fi": [f"Luettu {n} lukua.", shown],
        }
        return {
            "ok": True,
            "text": shown + ((" | " + extra) if extra else ""),
            "detail": extra,
            "svg": svg,
            "latex": extra.replace(" ", "") if extra else rf"\bar x = {_pretty(m)}",
            "steps": steps.get(lang) or steps["en"],
        }
    except Exception:
        return _fail(lang)


def _fail(lang: str) -> dict:
    msg = {"en": "No numbers found. Showing 0.", "fa": "عددی پیدا نشد. ۰.", "fi": "Lukuja ei loytynyt. 0."}
    return {"ok": True, "text": "0", "detail": "", "svg": "", "latex": "0", "steps": [msg.get(lang) or msg["en"]]}
