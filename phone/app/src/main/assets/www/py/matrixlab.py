"""Matrix calculator. Independent copy."""

from __future__ import annotations

import math
import re
import unicodedata

_DIGIT = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")


def _pretty(x, eng=False) -> str:
    if isinstance(x, complex):
        if abs(x.imag) < 1e-12:
            return _pretty(x.real, eng)
        sign = "+" if x.imag >= 0 else "-"
        return f"{_pretty(x.real, eng)} {sign} {_pretty(abs(x.imag), eng)}i"
    try:
        v = float(x)
    except Exception:
        return str(x)
    if not math.isfinite(v):
        return "undefined"
    if abs(v) < 1e-15:
        return "0"
    if eng and v != 0:
        exp = int(math.floor(math.log10(abs(v)) / 3) * 3)
        return f"{v / (10 ** exp):.8g}e{exp:+d}"
    return f"{v:.12g}"


def parse_mat(text: str):
    s = unicodedata.normalize("NFKC", str(text or "")).translate(_DIGIT).strip()
    if not s:
        return None
    rows = []
    for line in s.replace(";", "\n").splitlines():
        line = line.strip()
        if not line:
            continue
        line = line.replace(",", " ")
        row = []
        for p in line.split():
            p = p.replace("i", "j") if re.fullmatch(r"[+\-0-9.eE]*[+\-]?[0-9.eE]*j", p.replace("i", "j")) else p
            try:
                if "j" in p:
                    row.append(complex(p))
                else:
                    row.append(float(p))
            except Exception:
                continue
        if row:
            rows.append(row)
    if not rows:
        return None
    w = max(len(r) for r in rows)
    rows = [r + [0.0] * (w - len(r)) for r in rows]
    return rows


def _sym(rows):
    import sympy as sp

    return sp.Matrix(rows)


def _show(M, eng=False) -> str:
    try:
        rows = M.tolist()
    except Exception:
        return str(M)
    lines = []
    for row in rows:
        lines.append(", ".join(_pretty(complex(x) if isinstance(x, complex) else x, eng) for x in row))
    return "; ".join(lines)


def run(op: str, a: str, b: str = "", eng: bool = False, lang: str = "en") -> dict:
    try:
        import sympy as sp

        A = parse_mat(a)
        if A is None:
            return _fail(lang)
        MA = _sym(A)
        kind = (op or "det").lower()
        latex = ""
        detail = ""
        if kind in {"det", "determinant"}:
            val = MA.det()
            text = _pretty(complex(sp.N(val)), eng)
            latex = sp.latex(val)
            steps = _steps(lang, "det", text=text)
        elif kind in {"inv", "inverse"}:
            try:
                MI = MA.inv()
            except Exception:
                return _fail(lang)
            text = _show(MI.applyfunc(lambda z: sp.N(z)), eng)
            latex = sp.latex(MI)
            steps = _steps(lang, "inv", text=text)
        elif kind in {"t", "trans", "transpose"}:
            MT = MA.T
            text = _show(MT, eng)
            latex = sp.latex(MT)
            steps = _steps(lang, "t", text=text)
        elif kind in {"trace"}:
            val = MA.trace()
            text = _pretty(complex(sp.N(val)), eng)
            latex = sp.latex(val)
            steps = _steps(lang, "trace", text=text)
        elif kind in {"rank"}:
            text = str(int(MA.rank()))
            latex = text
            steps = _steps(lang, "rank", text=text)
        elif kind in {"rref"}:
            R, piv = MA.rref()
            text = _show(R, eng)
            detail = "pivots " + ", ".join(str(int(p) + 1) for p in piv)
            latex = sp.latex(R)
            steps = _steps(lang, "rref", text=text)
        elif kind in {"eig", "eigen"}:
            vals = MA.eigenvals()
            bits = []
            for val, mul in vals.items():
                bits.append(_pretty(complex(sp.N(val)), eng) + (f" (x{int(mul)})" if int(mul) != 1 else ""))
            text = ", ".join(bits) or "0"
            latex = ", ".join(sp.latex(v) for v in vals)
            steps = _steps(lang, "eig", text=text)
        elif kind in {"char", "charpoly"}:
            x = sp.Symbol("lam")
            p = MA.charpoly(x).as_expr()
            text = str(p)
            latex = sp.latex(p)
            steps = _steps(lang, "char", text=text)
        elif kind in {"mul", "prod"}:
            B = parse_mat(b)
            if B is None:
                return _fail(lang)
            MB = _sym(B)
            MP = MA * MB
            text = _show(MP.applyfunc(lambda z: sp.N(z)), eng)
            latex = sp.latex(MP)
            steps = _steps(lang, "mul", text=text)
        elif kind in {"add"}:
            B = parse_mat(b)
            if B is None:
                return _fail(lang)
            MP = MA + _sym(B)
            text = _show(MP.applyfunc(lambda z: sp.N(z)), eng)
            latex = sp.latex(MP)
            steps = _steps(lang, "add", text=text)
        elif kind in {"solve"}:
            B = parse_mat(b)
            if B is None:
                return _fail(lang)
            bb = _sym(B)
            if bb.shape[1] == 1:
                vec = bb
            else:
                vec = bb.T if bb.shape[0] == 1 else bb
            try:
                sol = MA.solve(vec)
                text = _show(sol.applyfunc(lambda z: sp.N(z)), eng)
                latex = sp.latex(sol)
            except Exception:
                try:
                    sol = MA.gauss_jordan_solve(vec)[0]
                    text = _show(sol.applyfunc(lambda z: sp.N(z)), eng)
                    latex = sp.latex(sol)
                except Exception:
                    return _fail(lang)
            steps = _steps(lang, "solve", text=text)
        else:
            return _fail(lang)
        return {"ok": True, "text": text, "detail": detail, "latex": latex, "steps": steps}
    except Exception:
        return _fail(lang)


def _fail(lang: str) -> dict:
    msg = {"en": "Could not do that matrix. Showing 0.", "fa": "ماتریس حل نشد. ۰.", "fi": "Matriisia ei voitu kasitella. 0."}
    return {"ok": True, "text": "0", "detail": "", "latex": "0", "steps": [msg.get(lang) or msg["en"]]}


def _steps(lang, kind, **kw):
    packs = {
        "en": {
            "det": "det(A) = {text}",
            "inv": "A inverse = {text}",
            "t": "A^T = {text}",
            "trace": "tr(A) = {text}",
            "rank": "rank(A) = {text}",
            "rref": "RREF = {text}",
            "eig": "Eigenvalues: {text}",
            "char": "Characteristic polynomial: {text}",
            "mul": "A B = {text}",
            "add": "A + B = {text}",
            "solve": "x = {text}",
        },
        "fa": {
            "det": "دترمینان = {text}",
            "inv": "وارون = {text}",
            "t": "ترانهاده = {text}",
            "trace": "اثر = {text}",
            "rank": "رتبه = {text}",
            "rref": "صورت پلکانی = {text}",
            "eig": "ویژه مقدار: {text}",
            "char": "چندجمله‌ای مشخصه: {text}",
            "mul": "A B = {text}",
            "add": "A + B = {text}",
            "solve": "x = {text}",
        },
        "fi": {
            "det": "det(A) = {text}",
            "inv": "A^{-1} = {text}",
            "t": "A^T = {text}",
            "trace": "tr(A) = {text}",
            "rank": "aste(A) = {text}",
            "rref": "RREF = {text}",
            "eig": "Ominaisarvot: {text}",
            "char": "Karakteristinen polynomi: {text}",
            "mul": "A B = {text}",
            "add": "A + B = {text}",
            "solve": "x = {text}",
        },
    }
    pack = packs.get(lang) or packs["en"]
    try:
        return [pack.get(kind, "{text}").format(**kw)]
    except Exception:
        return [str(kw.get("text") or "0")]
