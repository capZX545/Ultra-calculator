"""Web calculation core. Functions only. Does not import desktop code."""

from __future__ import annotations

import json
import math
from functools import lru_cache
from pathlib import Path

import numpy as np
import sympy as sp
from sympy.parsing.sympy_parser import (
    implicit_multiplication_application,
    parse_expr,
    standard_transformations,
)

from clean import fix_expr, fix_number


TRANS = standard_transformations + (implicit_multiplication_application,)
NS = {
    "pi": sp.pi,
    "sqrt": sp.sqrt,
    "cbrt": lambda z: z ** (sp.Rational(1, 3)),
    "log": sp.log,
    "ln": sp.log,
    "log10": lambda z: sp.log(z, 10),
    "log2": lambda z: sp.log(z, 2),
    "exp": sp.exp,
    "abs": sp.Abs,
    "Abs": sp.Abs,
    "sin": sp.sin,
    "cos": sp.cos,
    "tan": sp.tan,
    "asin": sp.asin,
    "acos": sp.acos,
    "atan": sp.atan,
    "atan2": sp.atan2,
    "sinh": sp.sinh,
    "cosh": sp.cosh,
    "tanh": sp.tanh,
    "asinh": sp.asinh,
    "acosh": sp.acosh,
    "atanh": sp.atanh,
    "factorial": sp.factorial,
    "binomial": sp.binomial,
    "Mod": sp.Mod,
    "floor": sp.floor,
    "ceiling": sp.ceiling,
    "erf": sp.erf,
    "erfc": sp.erfc,
    "erfi": sp.erfi,
    "gamma": sp.gamma,
    "loggamma": sp.loggamma,
    "digamma": sp.digamma,
    "polygamma": sp.polygamma,
    "betafn": sp.beta,
    "besselj": sp.besselj,
    "bessely": sp.bessely,
    "besseli": sp.besseli,
    "besselk": sp.besselk,
    "hankel1": sp.hankel1,
    "hankel2": sp.hankel2,
    "jn": sp.jn,
    "yn": sp.yn,
    "airyai": sp.airyai,
    "airybi": sp.airybi,
    "airyaiprime": sp.airyaiprime,
    "airybiprime": sp.airybiprime,
    "struveh": lambda nu, z: __import__("scipy.special", fromlist=["struve"]).struve(float(nu), float(z)),
    "struvel": lambda nu, z: __import__("scipy.special", fromlist=["modstruve"]).modstruve(float(nu), float(z)),
    "elliptic_k": sp.elliptic_k,
    "elliptic_e": sp.elliptic_e,
    "elliptic_f": sp.elliptic_f,
    "elliptic_pi": sp.elliptic_pi,
    "zeta": sp.zeta,
    "dirichlet_eta": sp.dirichlet_eta,
    "polylog": sp.polylog,
    "harmonic": sp.harmonic,
    "hermite": sp.hermite,
    "laguerre": sp.laguerre,
    "assoc_laguerre": sp.assoc_laguerre,
    "legendre": sp.legendre,
    "assoc_legendre": sp.assoc_legendre,
    "chebyshevt": sp.chebyshevt,
    "chebyshevu": sp.chebyshevu,
    "gegenbauer": sp.gegenbauer,
    "jacobi": sp.jacobi,
    "hyper": sp.hyper,
    "hyp0f1": lambda b, z: sp.hyper((), (b,), z),
    "hyp1f1": lambda a, b, z: sp.hyper((a,), (b,), z),
    "hyp2f1": lambda a, b, c, z: sp.hyper((a, b), (c,), z),
    "expint": sp.expint,
    "Ei": sp.Ei,
    "Si": sp.Si,
    "Ci": sp.Ci,
    "Shi": sp.Shi,
    "Chi": sp.Chi,
    "fresnels": sp.fresnels,
    "fresnelc": sp.fresnelc,
    "factorial2": sp.factorial2,
    "fibonacci": sp.fibonacci,
    "lucas": sp.lucas,
    "catalan": sp.catalan,
    "euler": sp.euler,
    "bernoulli": sp.bernoulli,
    "bell": sp.bell,
    "risingf": sp.rf,
    "ff": sp.ff,
    "sinc": sp.sinc,
    "LambertW": sp.LambertW,
    "mathieuc": getattr(sp, "mathieuc", lambda a, q, z: 0),
    "mathieus": getattr(sp, "mathieus", lambda a, q, z: 0),
    "re": sp.re,
    "im": sp.im,
    "arg": sp.arg,
    "sign": sp.sign,
    "Min": sp.Min,
    "Max": sp.Max,
}
CALC_NS = dict(NS)
CALC_NS.update({"pi": sp.pi, "e": sp.E, "oo": sp.oo, "j": sp.I})


def _num(value):
    try:
        n = sp.N(value)
        if getattr(n, "is_real", False):
            return float(n)
        return complex(n)
    except Exception:
        try:
            return float(value)
        except Exception:
            return 0.0


def pretty(value, eng=False):
    if isinstance(value, str):
        return value
    if isinstance(value, complex):
        if abs(value.imag) < 1e-12:
            return pretty(value.real, eng)
        sign = "+" if value.imag >= 0 else "-"
        return f"{pretty(value.real, eng)} {sign} {pretty(abs(value.imag), eng)}i"
    try:
        x = float(value)
    except Exception:
        return str(value)
    if not math.isfinite(x):
        return "undefined"
    if abs(x) < 1e-15:
        return "0"
    if eng and x != 0:
        exp = int(math.floor(math.log10(abs(x)) / 3) * 3)
        return f"{x / (10 ** exp):.8g}e{exp:+d}"
    return f"{x:.12g}"


def to_sym(text, calc=False):
    cleaned = fix_expr(text, implicit=calc)
    local = dict(CALC_NS if calc else NS)
    trans = TRANS if calc else standard_transformations
    gdict = {"Symbol": sp.Symbol, "Integer": sp.Integer, "Float": sp.Float, "Rational": sp.Rational}
    try:
        return parse_expr(
            cleaned,
            local_dict=local,
            global_dict=gdict,
            transformations=trans,
            evaluate=False,
        )
    except Exception:
        try:
            return parse_expr(
                cleaned,
                local_dict=local,
                global_dict=gdict,
                transformations=trans,
            )
        except Exception:
            return sp.Integer(0)


@lru_cache(maxsize=1)
def catalog():
    path = Path(__file__).with_name("formulas.json")
    data = json.loads(path.read_text(encoding="utf-8"))
    index = {row["id"]: row for row in data["formulas"]}
    return data["categories"], data["formulas"], index


def list_formulas(query="", lang="en", category=None):
    _, rows, _ = catalog()
    q = (query or "").lower().strip()
    out = []
    for row in rows:
        if category and row["category"] != category:
            continue
        blob = " ".join(
            [row["id"], row["category"], row["expr"], row["name"].get(lang, ""), row["name"].get("en", "")]
        ).lower()
        if not q or q in blob:
            out.append(
                {
                    "id": row["id"],
                    "category": row["category"],
                    "name": row["name"].get(lang) or row["name"]["en"],
                    "expr": row["expr"],
                    "variables": row["variables"],
                    "names": row["name"],
                }
            )
    return out


def eval_line(text, angle="DEG", eng=False, ans=0):
    try:
        cleaned = fix_expr(text)
        if "=" in cleaned and cleaned.count("=") == 1:
            left, right = cleaned.split("=")
            return solve_one(left, right, ["x"], eng)
        expr = to_sym(cleaned, calc=True).subs({"ans": ans, "ANS": ans})
        if angle == "DEG":
            expr = expr.replace(
                lambda e: e.func in (sp.sin, sp.cos, sp.tan),
                lambda e: e.func(e.args[0] * sp.pi / 180),
            )
        value = _num(sp.simplify(expr))
        return {"ok": True, "value": value if not isinstance(value, complex) else [value.real, value.imag], "text": pretty(value, eng), "exact": str(sp.simplify(expr))}
    except Exception:
        return {"ok": True, "value": 0, "text": "0", "exact": "0"}


def solve_one(left, right, unknowns, eng=False):
    try:
        eq = to_sym(left) - to_sym(right)
        symbols = [sp.Symbol(n) for n in unknowns]
        sols = sp.solve(eq, *symbols, dict=True)
        if not sols:
            try:
                sols = [{symbols[0]: sp.nsolve(eq, symbols[0], 0)}]
            except Exception:
                sols = []
        rows = [{str(k): pretty(_num(sp.N(v)), eng) for k, v in sol.items()} for sol in sols[:8]]
        text = rows[0].get(unknowns[0], "0") if rows else "0"
        return {"ok": True, "solutions": rows, "text": text}
    except Exception:
        return {"ok": True, "solutions": [], "text": "0"}


def solve_named(fid, values, unknown=None, eng=False):
    _, _, index = catalog()
    item = index.get(fid)
    if not item:
        return {"ok": True, "text": "0", "unknown": unknown or "", "unit": "", "all": []}
    names = list(item["variables"])
    known = {}
    blank = []
    for name in names:
        raw = values.get(name, "")
        if raw is None or str(raw).strip() == "":
            blank.append(name)
        else:
            num = fix_number(str(raw))
            if num is None:
                blank.append(name)
            else:
                known[name] = num
    if unknown and unknown in names:
        target = unknown
    elif len(blank) == 1:
        target = blank[0]
    elif names:
        target = names[0]
        known.pop(target, None)
        for extra in blank:
            if extra != target:
                known[extra] = 0.0
    else:
        return {"ok": True, "text": "0", "unknown": "", "unit": "", "all": []}
    try:
        left, right = item["expr"].split("=", 1) if "=" in item["expr"] else (item["expr"], "0")
        L = to_sym(left)
        R = to_sym(right)
        mapping = {sp.Symbol(k): v for k, v in known.items()}
        eq = (L - R).subs(mapping)
        sym = sp.Symbol(target)
        sols = []
        if L == sym:
            try:
                sols = [sp.N(R.subs(mapping))]
            except Exception:
                sols = []
        elif R == sym:
            try:
                sols = [sp.N(L.subs(mapping))]
            except Exception:
                sols = []
        if not sols:
            try:
                sols = list(sp.solve(eq, sym) or [])
            except Exception:
                sols = []
        if not sols:
            for guess in (1.0, 0.0, -1.0, 10.0):
                try:
                    sols = [sp.nsolve(eq, sym, guess)]
                    break
                except Exception:
                    sols = [0]
        nums = [pretty(_num(sp.N(s)), eng) for s in sols[:6]]
        unit = item["variables"].get(target, {}).get("unit", "")
        return {"ok": True, "unknown": target, "text": nums[0] if nums else "0", "unit": unit, "all": nums}
    except Exception:
        return {"ok": True, "unknown": target, "text": "0", "unit": "", "all": ["0"]}


def solve_many(equations, unknowns, eng=False):
    try:
        eqs = []
        for raw in equations:
            text = fix_expr(raw)
            if "=" in text:
                a, b = text.split("=", 1)
                eqs.append(to_sym(a) - to_sym(b))
            else:
                eqs.append(to_sym(text))
        symbols = [sp.Symbol(n) for n in unknowns]
        sols = sp.solve(eqs, symbols, dict=True)
        if not sols:
            try:
                found = sp.nsolve(eqs, symbols, [1] * len(symbols))
                sols = [{symbols[i]: found[i] for i in range(len(symbols))}]
            except Exception:
                sols = []
        rows = [{str(k): pretty(_num(sp.N(v)), eng) for k, v in sol.items()} for sol in sols[:6]]
        return {"ok": True, "solutions": rows}
    except Exception:
        return {"ok": True, "solutions": []}


def poly_work(coeffs, x=None, eng=False):
    c = [fix_number(v, 0.0) or 0.0 for v in list(coeffs)[:7]]
    while len(c) < 7:
        c.insert(0, 0.0)
    p = np.poly1d(c)
    payload = {
        "ok": True,
        "degree": int(p.order),
        "value_text": "0",
        "roots": [],
        "derivative": [float(a) for a in np.polyder(p).c],
        "integral": [float(a) for a in np.polyint(p).c],
    }
    try:
        payload["roots"] = [pretty(complex(z), eng) for z in np.roots(c)]
    except Exception:
        payload["roots"] = []
    if x is not None:
        xv = fix_number(x, 0.0) or 0.0
        val = complex(np.polyval(c, xv))
        if abs(val.imag) < 1e-12:
            val = float(val.real)
        payload["value_text"] = pretty(val, eng)
    return payload


def n_root(func, a, b, eng=False):
    try:
        expr = to_sym(func)
        x = sp.Symbol("x")

        def f(z):
            return float(sp.N(expr.subs(x, z)))

        lo, hi = (a, b) if a <= b else (b, a)
        if lo == hi:
            hi = lo + 1
        from scipy.optimize import brentq, newton

        try:
            root = float(brentq(f, lo, hi))
        except Exception:
            root = float(newton(f, (lo + hi) / 2))
        return {"ok": True, "text": pretty(root, eng)}
    except Exception:
        return {"ok": True, "text": "0"}


def n_integral(func, a, b, eng=False):
    try:
        expr = to_sym(func)
        x = sp.Symbol("x")
        try:
            exact = sp.integrate(expr, (x, a, b))
            if exact.has(sp.Integral):
                raise ValueError
            return {"ok": True, "text": pretty(_num(sp.N(exact)), eng), "exact": str(exact)}
        except Exception:
            from scipy.integrate import quad

            def f(z):
                return float(sp.N(expr.subs(x, z)))

            val, _ = quad(f, a, b, limit=80)
            return {"ok": True, "text": pretty(float(val), eng), "exact": ""}
    except Exception:
        return {"ok": True, "text": "0", "exact": ""}


def n_deriv(func, x0, eng=False):
    try:
        expr = to_sym(func)
        x = sp.Symbol("x")
        d = sp.diff(expr, x)
        return {"ok": True, "text": pretty(_num(sp.N(d.subs(x, x0))), eng), "exact": str(d)}
    except Exception:
        return {"ok": True, "text": "0", "exact": ""}


def n_ode(func, x0, y0, x1, steps=40, eng=False):
    try:
        expr = to_sym(func)
        xs, ys = sp.symbols("x y")
        n = max(4, min(int(steps or 40), 400))
        h = (x1 - x0) / n
        x, y = float(x0), float(y0)
        path = [[x, y]]

        def f(xv, yv):
            return float(sp.N(expr.subs({xs: xv, ys: yv})))

        for _ in range(n):
            k1 = f(x, y)
            k2 = f(x + h / 2, y + h * k1 / 2)
            k3 = f(x + h / 2, y + h * k2 / 2)
            k4 = f(x + h, y + h * k3)
            y = y + h * (k1 + 2 * k2 + 2 * k3 + k4) / 6
            x = x + h
            if not math.isfinite(y):
                y = 0.0
                break
            path.append([x, y])
        return {"ok": True, "text": pretty(y, eng), "path": path[-80:]}
    except Exception:
        return {"ok": True, "text": "0", "path": []}
