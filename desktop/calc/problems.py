"""Problem solver and inverse solver for the desktop app. Independent copy."""

from __future__ import annotations

import re
import unicodedata

import sympy as sp
from sympy.matrices import Matrix
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application

from .sanitize import clean_expression


_TRANS = standard_transformations + (implicit_multiplication_application,)
_DIGIT = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")

_NS = {
    "sin": sp.sin, "cos": sp.cos, "tan": sp.tan,
    "asin": sp.asin, "acos": sp.acos, "atan": sp.atan,
    "sinh": sp.sinh, "cosh": sp.cosh, "tanh": sp.tanh,
    "exp": sp.exp, "log": sp.log, "ln": sp.log,
    "log10": lambda z: sp.log(z, 10), "sqrt": sp.sqrt, "abs": sp.Abs,
    "pi": sp.pi, "e": sp.E, "I": sp.I,
    "factorial": sp.factorial, "gamma": sp.gamma,
}


def _pretty(value, eng: bool = False) -> str:
    if value is None:
        return "0"
    if isinstance(value, (list, tuple)):
        return ", ".join(_pretty(v, eng) for v in value)
    try:
        if isinstance(value, sp.Basic):
            if value.free_symbols:
                return str(sp.simplify(value))
            value = sp.N(value)
    except Exception:
        pass
    if isinstance(value, complex):
        if abs(value.imag) < 1e-12:
            return _pretty(value.real, eng)
        sign = "+" if value.imag >= 0 else "-"
        return f"{_pretty(value.real, eng)} {sign} {_pretty(abs(value.imag), eng)}i"
    try:
        x = float(value)
    except Exception:
        return str(value)
    if abs(x) < 1e-15:
        return "0"
    if eng and x != 0:
        import math
        exp = int(math.floor(math.log10(abs(x)) / 3) * 3)
        return f"{x / (10 ** exp):.8g}e{exp:+d}"
    text = f"{x:.12g}"
    return text


def _prep(raw: str) -> str:
    text = unicodedata.normalize("NFKC", str(raw or "")).strip()
    text = text.translate(_DIGIT)
    text = text.replace("×", "*").replace("÷", "/").replace("−", "-").replace("–", "-")
    text = text.replace("^", "**").replace("π", "pi")
    text = re.sub(r"^f\s*\(\s*x\s*\)\s*=", "", text, flags=re.I)
    text = re.sub(r"^y\s*=", "", text, flags=re.I)
    text = re.sub(r"^(solve|find|calculate|compute)\s+(for\s+[A-Za-z]\s*:?\s*)?", "", text, flags=re.I)
    return text.strip()


def _parse(text: str):
    cleaned = clean_expression(text, implicit=True)
    try:
        return parse_expr(cleaned, local_dict=dict(_NS), transformations=_TRANS, evaluate=False)
    except Exception:
        try:
            return parse_expr(cleaned, local_dict=dict(_NS), transformations=_TRANS)
        except Exception:
            return None


def _steps(lang: str, kind: str, **kw) -> list[str]:
    packs = {
        "en": {
            "typed": "Problem: {raw}",
            "eq": "Equation: {eq}",
            "unk": "Unknown: {u}",
            "sol": "Solution: {text}",
            "many": "Solutions: {text}",
            "inv_fun": "Find the inverse of {fun}.",
            "inv_out": "Inverse: {text}",
            "inv_at": "Evaluate the inverse at {at}.",
            "mat": "Invert the matrix.",
            "none": "No closed inverse. Showing 0.",
            "fail": "No closed form. Showing 0.",
            "ineq": "Inequality: {eq}",
        },
        "fa": {
            "typed": "مسئله: {raw}",
            "eq": "معادله: {eq}",
            "unk": "مجهول: {u}",
            "sol": "جواب: {text}",
            "many": "جواب‌ها: {text}",
            "inv_fun": "وارون {fun} را پیدا می‌کنیم.",
            "inv_out": "وارون: {text}",
            "inv_at": "وارون را در {at} حساب می‌کنیم.",
            "mat": "وارون ماتریس.",
            "none": "وارون بسته پیدا نشد. ۰.",
            "fail": "فرم بسته پیدا نشد. ۰.",
            "ineq": "نامساوی: {eq}",
        },
        "fi": {
            "typed": "Tehtava: {raw}",
            "eq": "Yhtalo: {eq}",
            "unk": "Tuntematon: {u}",
            "sol": "Ratkaisu: {text}",
            "many": "Ratkaisut: {text}",
            "inv_fun": "Kaanteisfunktio funktiolle {fun}.",
            "inv_out": "Kaanteinen: {text}",
            "inv_at": "Laske kaanteinen kohdassa {at}.",
            "mat": "Kaanteismatriisi.",
            "none": "Ei suljettua kaanteista. 0.",
            "fail": "Ei suljettua muotoa. 0.",
            "ineq": "Epayhtalo: {eq}",
        },
    }
    pack = packs.get(lang) or packs["en"]
    key = kind if kind in pack else "sol"
    try:
        return [pack[key].format(**kw)]
    except Exception:
        return [pack.get("sol", "0")]


def _fail(lang: str, kind: str = "fail") -> dict:
    return {"ok": True, "kind": "none", "text": "0", "solutions": [], "steps": _steps(lang, kind)}


def _matrix(raw: str):
    text = raw.replace("[[", "").replace("]]", "")
    rows = []
    for line in re.split(r"[;\n]", text):
        line = line.strip().strip("[]")
        if not line:
            continue
        parts = [p.strip() for p in re.split(r"[,\s]+", line) if p.strip()]
        nums = []
        for p in parts:
            try:
                nums.append(float(p))
            except Exception:
                return None
        if nums:
            rows.append(nums)
    if not rows:
        return None
    w = max(len(r) for r in rows)
    rows = [r + [0.0] * (w - len(r)) for r in rows]
    try:
        return Matrix(rows)
    except Exception:
        return None


def solve_problem(raw: str, lang: str = "en", unknown: str = "x", eng: bool = False) -> dict:
    try:
        text = _prep(raw)
        if not text:
            return _fail(lang)
        u = (unknown or "x").strip() or "x"
        parts = [p.strip() for p in re.split(r"[;\n]+", text) if p.strip() and "=" in p]
        if len(parts) >= 2:
            eqs = []
            symbols = set()
            for p in parts:
                a, b = p.split("=", 1)
                L, R = _parse(a), _parse(b)
                if L is None or R is None:
                    continue
                eqs.append(sp.Eq(L, R))
                symbols |= L.free_symbols | R.free_symbols
            if not eqs:
                return _fail(lang)
            names = sorted(str(s) for s in symbols) or [u]
            sols = sp.solve(eqs, [sp.Symbol(n) for n in names], dict=True) or []
            rows = []
            for sol in sols[:6]:
                rows.append({str(k): _pretty(v, eng) for k, v in sol.items()})
            shown = " ; ".join("  ".join(f"{k} = {v}" for k, v in row.items()) for row in rows) or "0"
            steps = _steps(lang, "typed", raw=raw) + _steps(lang, "many", text=shown)
            return {"ok": True, "kind": "system", "text": shown, "solutions": rows, "steps": steps}
        ineq = re.search(r"(<=|>=|<|>)", text)
        if ineq and "=" not in text.replace("<=", "").replace(">=", ""):
            expr = _parse(text)
            if expr is None:
                return _fail(lang)
            rel = sp.solve_univariate_inequality(expr, sp.Symbol(u), relational=False) if hasattr(sp, "solve_univariate_inequality") else expr
            shown = str(rel)
            steps = _steps(lang, "typed", raw=raw) + _steps(lang, "ineq", eq=text) + _steps(lang, "sol", text=shown)
            return {"ok": True, "kind": "ineq", "text": shown, "solutions": [shown], "steps": steps}
        if "=" in text:
            a, b = text.split("=", 1)
            L, R = _parse(a), _parse(b)
            if L is None or R is None:
                return _fail(lang)
            eq = sp.Eq(L, R)
            sym = sp.Symbol(u)
            if sym not in eq.free_symbols and eq.free_symbols:
                sym = sorted(eq.free_symbols, key=str)[0]
            sols = list(sp.solve(eq, sym) or [])
            if not sols:
                try:
                    sols = [sp.nsolve(L - R, sym, 0)]
                except Exception:
                    sols = []
            pretty = [_pretty(s, eng) for s in sols[:8]]
            shown = ", ".join(pretty) if pretty else "0"
            steps = (
                _steps(lang, "typed", raw=raw)
                + _steps(lang, "eq", eq=f"{a} = {b}")
                + _steps(lang, "unk", u=str(sym))
                + _steps(lang, "many" if len(pretty) > 1 else "sol", text=shown)
            )
            return {"ok": True, "kind": "equation", "text": shown, "solutions": pretty, "unknown": str(sym), "steps": steps}
        expr = _parse(text)
        if expr is None:
            return _fail(lang)
        if expr.free_symbols:
            sym = sp.Symbol(u) if sp.Symbol(u) in expr.free_symbols else sorted(expr.free_symbols, key=str)[0]
            sols = list(sp.solve(expr, sym) or [])
            pretty = [_pretty(s, eng) for s in sols[:8]]
            shown = ", ".join(pretty) if pretty else "0"
            steps = _steps(lang, "typed", raw=raw) + _steps(lang, "eq", eq=f"{text} = 0") + _steps(lang, "sol", text=shown)
            return {"ok": True, "kind": "roots", "text": shown, "solutions": pretty, "steps": steps}
        val = _pretty(sp.N(expr), eng)
        steps = _steps(lang, "typed", raw=raw) + _steps(lang, "sol", text=val)
        return {"ok": True, "kind": "value", "text": val, "solutions": [val], "steps": steps}
    except Exception:
        return _fail(lang)


def inverse_problem(raw: str, lang: str = "en", unknown: str = "x", at: str = "", eng: bool = False) -> dict:
    try:
        text = _prep(raw)
        if not text:
            return _fail(lang, "none")
        u = (unknown or "x").strip() or "x"
        mat = _matrix(text)
        if mat is not None and mat.rows == mat.cols and mat.rows >= 2:
            try:
                inv = mat.inv()
                rows = [", ".join(_pretty(inv[i, j], eng) for j in range(inv.cols)) for i in range(inv.rows)]
                shown = "; ".join(rows)
                steps = _steps(lang, "typed", raw=raw) + _steps(lang, "mat") + _steps(lang, "inv_out", text=shown)
                return {"ok": True, "kind": "matrix", "text": shown, "solutions": [shown], "steps": steps}
            except Exception:
                return _fail(lang, "none")
        if "=" in text:
            left, right = text.split("=", 1)
            if re.fullmatch(r"[A-Za-z]\(\s*[A-Za-z]\s*\)", left.strip()) or left.strip() in {u, "y", "f"}:
                text = right.strip()
            else:
                expr_l, expr_r = _parse(left), _parse(right)
                if expr_l is not None and expr_r is not None:
                    if expr_l.free_symbols and not expr_r.free_symbols:
                        text = left.strip()
                        if not str(at or "").strip():
                            at = right.strip()
                    elif expr_r.free_symbols and not expr_l.free_symbols:
                        text = right.strip()
                        if not str(at or "").strip():
                            at = left.strip()
                    elif sp.Symbol(u) in expr_l.free_symbols:
                        text = left.strip()
                    else:
                        text = right.strip() if expr_r.free_symbols else left.strip()
        expr = _parse(text)
        if expr is None:
            return _fail(lang, "none")
        if not expr.free_symbols:
            try:
                val = float(sp.N(expr))
                if abs(val) < 1e-15:
                    return _fail(lang, "none")
                shown = _pretty(1.0 / val, eng)
                steps = _steps(lang, "typed", raw=raw) + _steps(lang, "inv_out", text=shown)
                return {"ok": True, "kind": "reciprocal", "text": shown, "solutions": [shown], "steps": steps}
            except Exception:
                return _fail(lang, "none")
        x = sp.Symbol(u) if sp.Symbol(u) in expr.free_symbols else sorted(expr.free_symbols, key=str)[0]
        y = sp.Dummy("y")
        sols = list(sp.solve(sp.Eq(y, expr), x) or [])
        if not sols:
            return _fail(lang, "none")
        invs = [s.subs(y, x) for s in sols]
        shown_fun = ", ".join(str(sp.simplify(s)) for s in invs)
        steps = _steps(lang, "typed", raw=raw) + _steps(lang, "inv_fun", fun=str(expr)) + _steps(lang, "inv_out", text=shown_fun)
        at_text = str(at or "").strip()
        if at_text:
            at_expr = _parse(at_text)
            if at_expr is not None:
                vals = [_pretty(s.subs(x, at_expr), eng) for s in invs]
                shown_at = ", ".join(vals)
                steps = steps + _steps(lang, "inv_at", at=at_text) + _steps(lang, "sol", text=shown_at)
                return {
                    "ok": True,
                    "kind": "inverse_at",
                    "text": shown_at,
                    "inverse": shown_fun,
                    "solutions": vals,
                    "steps": steps,
                }
        return {"ok": True, "kind": "inverse", "text": shown_fun, "solutions": [str(sp.simplify(s)) for s in invs], "steps": steps}
    except Exception:
        return _fail(lang, "none")


def run(raw: str, mode: str = "solve", unknown: str = "x", at: str = "", lang: str = "en", eng: bool = False) -> dict:
    try:
        if (mode or "solve").lower().startswith("inv"):
            return inverse_problem(raw, lang=lang, unknown=unknown, at=at, eng=eng)
        try:
            try:
                from wordprob import try_solve
            except Exception:
                from .wordprob import try_solve
            hit = try_solve(raw, lang=lang, eng=eng)
            if hit:
                return hit
        except Exception:
            pass
        return solve_problem(raw, lang=lang, unknown=unknown, eng=eng)
    except Exception:
        return _fail(lang)
