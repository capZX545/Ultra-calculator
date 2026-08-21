"""Plot functions, parametric curves, data, and Bode. Independent copy. Returns SVG."""

from __future__ import annotations

import math
import re
import unicodedata

_DIGIT = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")
_COLORS = ["#c4a35a", "#6db3c8", "#c86d6d", "#7dba6d", "#b07cc8"]


def _num(raw, default=None):
    if raw is None or str(raw).strip() == "":
        return default
    text = unicodedata.normalize("NFKC", str(raw)).translate(_DIGIT).replace(",", ".")
    try:
        return float(text)
    except Exception:
        return default


def _parse_fx(func: str):
    import sympy as sp
    from sympy.parsing.sympy_parser import parse_expr, standard_transformations

    local = {
        "sin": sp.sin, "cos": sp.cos, "tan": sp.tan, "asin": sp.asin, "acos": sp.acos, "atan": sp.atan,
        "sinh": sp.sinh, "cosh": sp.cosh, "tanh": sp.tanh, "exp": sp.exp, "log": sp.log, "ln": sp.log,
        "log10": lambda z: sp.log(z, 10), "log2": lambda z: sp.log(z, 2), "sqrt": sp.sqrt, "abs": sp.Abs,
        "pi": sp.pi, "e": sp.E, "sec": lambda z: 1 / sp.cos(z), "csc": lambda z: 1 / sp.sin(z),
    }
    text = (func or "x").replace("^", "**")
    try:
        return parse_expr(text, local_dict=local, transformations=standard_transformations)
    except Exception:
        return sp.Integer(0)


def _sample(expr, var, lo, hi, n=200):
    import sympy as sp

    n = max(20, min(int(n or 200), 800))
    xs, ys = [], []
    if hi == lo:
        hi = lo + 1
    for i in range(n + 1):
        x = lo + (hi - lo) * i / n
        try:
            y = complex(sp.N(expr.subs(var, x)))
            if abs(y.imag) > 1e-8:
                continue
            yv = float(y.real)
            if not math.isfinite(yv) or abs(yv) > 1e8:
                xs.append(x)
                ys.append(None)
            else:
                xs.append(x)
                ys.append(yv)
        except Exception:
            xs.append(x)
            ys.append(None)
    return xs, ys


def _svg(series, xmin, xmax, ymin, ymax, w=640, h=400, xlabel="x", ylabel="y"):
    if xmax == xmin:
        xmax = xmin + 1
    if ymax == ymin:
        ymax = ymin + 1
    pad_l, pad_r, pad_t, pad_b = 48, 16, 16, 36
    iw, ih = w - pad_l - pad_r, h - pad_t - pad_b

    def X(x):
        return pad_l + (x - xmin) / (xmax - xmin) * iw

    def Y(y):
        return pad_t + (ymax - y) / (ymax - ymin) * ih

    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">']
    parts.append(f'<rect width="{w}" height="{h}" fill="#11141a"/>')
    parts.append(f'<rect x="{pad_l}" y="{pad_t}" width="{iw}" height="{ih}" fill="#1c1f24" stroke="#333"/>')
    # axes
    if xmin < 0 < xmax:
        x0 = X(0)
        parts.append(f'<line x1="{x0:.1f}" y1="{pad_t}" x2="{x0:.1f}" y2="{pad_t+ih}" stroke="#3d4654"/>')
    if ymin < 0 < ymax:
        y0 = Y(0)
        parts.append(f'<line x1="{pad_l}" y1="{y0:.1f}" x2="{pad_l+iw}" y2="{y0:.1f}" stroke="#3d4654"/>')
    for s in series:
        color = s.get("color") or "#c4a35a"
        xs, ys = s.get("xs") or [], s.get("ys") or []
        seg = []
        chunks = []
        for x, y in zip(xs, ys):
            if y is None or not math.isfinite(y):
                if seg:
                    chunks.append(seg)
                    seg = []
                continue
            seg.append(f"{X(x):.2f},{Y(y):.2f}")
        if seg:
            chunks.append(seg)
        for ch in chunks:
            parts.append(f'<polyline fill="none" stroke="{color}" stroke-width="1.8" points="{" ".join(ch)}"/>')
        # scatter
        if s.get("scatter"):
            for x, y in zip(xs, ys):
                if y is None:
                    continue
                parts.append(f'<circle cx="{X(x):.1f}" cy="{Y(y):.1f}" r="3" fill="{color}"/>')
    parts.append(f'<text x="{pad_l}" y="{h-8}" fill="#9aa3ad" font-size="12">{xmin:g}</text>')
    parts.append(f'<text x="{w-pad_r-40}" y="{h-8}" fill="#9aa3ad" font-size="12">{xmax:g}</text>')
    parts.append(f'<text x="6" y="{pad_t+12}" fill="#9aa3ad" font-size="12">{ymax:g}</text>')
    parts.append(f'<text x="6" y="{h-pad_b}" fill="#9aa3ad" font-size="12">{ymin:g}</text>')
    legend_y = 18
    for i, s in enumerate(series):
        name = s.get("name") or ""
        if not name:
            continue
        parts.append(f'<rect x="{pad_l+8}" y="{legend_y-8}" width="10" height="10" fill="{s.get("color") or "#c4a35a"}"/>')
        parts.append(f'<text x="{pad_l+22}" y="{legend_y}" fill="#e8eaed" font-size="12">{name}</text>')
        legend_y += 16
    parts.append("</svg>")
    return "".join(parts)


def _bounds(series):
    xs, ys = [], []
    for s in series:
        for x, y in zip(s.get("xs") or [], s.get("ys") or []):
            if y is None or not math.isfinite(y):
                continue
            xs.append(x)
            ys.append(y)
    if not xs:
        return -1, 1, -1, 1
    xmin, xmax = min(xs), max(xs)
    ymin, ymax = min(ys), max(ys)
    if xmax == xmin:
        xmax += 1
        xmin -= 1
    if ymax == ymin:
        ymax += 1
        ymin -= 1
    dy = (ymax - ymin) * 0.08
    return xmin, xmax, ymin - dy, ymax + dy


def run(kind: str = "func", funcs: str = "sin(x)", xmin: str = "-10", xmax: str = "10",
        tmin: str = "0", tmax: str = "6.2832", data: str = "", circuit: str = "",
        node: str = "2", fmin: str = "1", fmax: str = "1e5", n: str = "200",
        lang: str = "en", eng: bool = False) -> dict:
    try:
        kind = (kind or "func").lower()
        import sympy as sp

        series = []
        if kind in {"func", "plot", "xy", ""}:
            x = sp.Symbol("x")
            lo, hi = _num(xmin, -10.0), _num(xmax, 10.0)
            lines = [ln.strip() for ln in str(funcs or "sin(x)").splitlines() if ln.strip()]
            if not lines:
                lines = ["sin(x)"]
            for i, line in enumerate(lines[:5]):
                expr = _parse_fx(line)
                xs, ys = _sample(expr, x, lo, hi, _num(n, 200))
                series.append({"name": line, "xs": xs, "ys": ys, "color": _COLORS[i % len(_COLORS)]})
            xmin_b, xmax_b = lo, hi
            _, _, ymin, ymax = _bounds(series)
            svg = _svg(series, xmin_b, xmax_b, ymin, ymax)
        elif kind in {"param", "parametric"}:
            t = sp.Symbol("t")
            lo, hi = _num(tmin, 0.0), _num(tmax, 2 * math.pi)
            lines = [ln.strip() for ln in str(funcs or "cos(t), sin(t)").splitlines() if ln.strip()]
            line = lines[0] if lines else "cos(t), sin(t)"
            if "," in line:
                xs_s, ys_s = line.split(",", 1)
            elif ";" in line:
                xs_s, ys_s = line.split(";", 1)
            else:
                xs_s, ys_s = "cos(t)", line
            xe, ye = _parse_fx(xs_s), _parse_fx(ys_s)
            ts, xs = _sample(xe, t, lo, hi, _num(n, 300))
            _, ys = _sample(ye, t, lo, hi, _num(n, 300))
            series = [{"name": line, "xs": xs, "ys": ys, "color": _COLORS[0]}]
            xmin_b, xmax_b, ymin, ymax = _bounds(series)
            svg = _svg(series, xmin_b, xmax_b, ymin, ymax, xlabel="x", ylabel="y")
        elif kind in {"data", "scatter"}:
            xs, ys = [], []
            blob = unicodedata.normalize("NFKC", str(data or funcs or "")).translate(_DIGIT)
            for line in blob.replace(";", "\n").splitlines():
                line = line.strip().replace(",", " ")
                parts = [p for p in line.split() if p]
                if len(parts) >= 2:
                    try:
                        xs.append(float(parts[0]))
                        ys.append(float(parts[1]))
                    except Exception:
                        continue
            series = [{"name": "data", "xs": xs, "ys": ys, "color": _COLORS[0], "scatter": True}]
            xmin_b, xmax_b, ymin, ymax = _bounds(series)
            svg = _svg(series, xmin_b, xmax_b, ymin, ymax)
        elif kind in {"bode"}:
            svg, text, series = _bode(circuit, node, fmin, fmax, n, lang)
            steps = _steps(lang, "bode", text=text)
            return {"ok": True, "text": text, "svg": svg, "series": _ser_out(series), "steps": steps, "latex": ""}
        else:
            return _fail(lang)
        npts = sum(1 for s in series for y in (s.get("ys") or []) if y is not None)
        text = f"{len(series)} curve(s), {npts} points"
        steps = _steps(lang, "plot", text=text)
        return {"ok": True, "text": text, "svg": svg, "series": _ser_out(series), "steps": steps, "latex": ""}
    except Exception:
        return _fail(lang)


def _ser_out(series):
    out = []
    for s in series:
        xs = s.get("xs") or []
        ys = s.get("ys") or []
        out.append({"name": s.get("name") or "", "n": len(xs), "color": s.get("color")})
    return out


def _bode(circuit, node, fmin, fmax, n, lang):
    try:
        import circuits
    except Exception:
        try:
            from . import circuits
        except Exception:
            return "", "0", []
    lo = max(_num(fmin, 1.0) or 1.0, 1e-6)
    hi = max(_num(fmax, 1e5) or 1e5, lo * 10)
    pts = max(20, min(int(_num(n, 40) or 40), 120))
    freqs, mag, phase = [], [], []
    node = str(node or "2").strip()
    for i in range(pts):
        f = lo * (hi / lo) ** (i / (pts - 1))
        out = circuits.run(circuit or "", mode="solve", freq=str(f), lang="en", eng=False)
        val = _extract_v(out.get("text") or "", node)
        freqs.append(f)
        if val is None:
            mag.append(None)
            phase.append(None)
        else:
            mag.append(20 * math.log10(abs(val) + 1e-18))
            phase.append(math.degrees(math.atan2(val.imag, val.real)))
    series = [
        {"name": f"|V({node})| dB", "xs": [math.log10(f) for f in freqs], "ys": mag, "color": _COLORS[0]},
    ]
    xmin_b, xmax_b, ymin, ymax = _bounds(series)
    svg = _svg(series, xmin_b, xmax_b, ymin, ymax, xlabel="log10 f", ylabel="dB")
    finite = [m for m in mag if m is not None]
    text = f"Bode V({node})  {lo:g}–{hi:g} Hz" + (f"  mag {min(finite):.3g} … {max(finite):.3g} dB" if finite else "")
    return svg, text, series


def _extract_v(text: str, node: str):
    m = re.search(rf"V\(\s*{re.escape(node)}\s*\)\s*=\s*([^;|]+)", text)
    if not m:
        return None
    blob = m.group(1).strip()
    # "8 V" or "0.7 + j0.1"
    blob = blob.replace("V", "").replace("A", "").strip()
    blob = blob.replace(" ", "")
    try:
        if "j" in blob:
            blob = blob.replace("+j", "+") if False else blob
            # 0.7+j0.1 or 0.7 + j0.1 already stripped
            blob = blob.replace("j", "") if blob.startswith("j") else blob
            m2 = re.match(r"([+\-]?[0-9.eE]+)([+\-][0-9.eE]*)i?", blob.replace("j", ""))
            # simpler:  a + j b
        parts = re.findall(r"[+\-]?[0-9.eE]+", blob.replace("j", " "))
        if not parts:
            return None
        re_v = float(parts[0])
        im_v = float(parts[1]) if len(parts) > 1 and "j" in m.group(1) else 0.0
        if "-" in m.group(1) and len(parts) > 1 and re.search(r"-\s*j", m.group(1)):
            im_v = -abs(im_v)
        return complex(re_v, im_v)
    except Exception:
        try:
            return complex(float(re.findall(r"[+\-]?[0-9.eE]+", blob)[0]))
        except Exception:
            return None


def _fail(lang):
    msg = {"en": "Could not plot. Showing 0.", "fa": "نمودار نشد. ۰.", "fi": "Kuvaajaa ei saatu. 0."}
    return {"ok": True, "text": "0", "svg": "", "series": [], "steps": [msg.get(lang) or msg["en"]], "latex": ""}


def _steps(lang, kind, **kw):
    packs = {
        "en": {"plot": "Plotted {text}.", "bode": "Frequency sweep: {text}."},
        "fa": {"plot": "رسم شد: {text}.", "bode": "جاروب فرکانس: {text}."},
        "fi": {"plot": "Piirretty {text}.", "bode": "Taajuuspyyhkäisy: {text}."},
    }
    pack = packs.get(lang) or packs["en"]
    try:
        return [pack.get(kind, "{text}").format(**kw)]
    except Exception:
        return [str(kw.get("text") or "0")]
