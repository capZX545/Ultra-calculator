"""Desktop calculation engine. Self-contained. Does not import from the web app."""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import sympy as sp
from sympy.parsing.sympy_parser import (
    implicit_multiplication_application,
    parse_expr,
    standard_transformations,
)

from .sanitize import clean_expression, clean_number


_TRANSFORMS = standard_transformations + (implicit_multiplication_application,)
_FUNCS = {
    "pi": sp.pi,
    "sqrt": sp.sqrt,
    "cbrt": lambda z: z ** (sp.Integer(1) / 3),
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
    "meijerg": sp.meijerg,
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
    "re": sp.re,
    "im": sp.im,
    "arg": sp.arg,
    "sign": sp.sign,
    "min": sp.Min,
    "max": sp.Max,
    "Min": sp.Min,
    "Max": sp.Max,
}
_CALC_CONST = {"pi": sp.pi, "e": sp.E, "oo": sp.oo, "j": sp.I}


def _as_float(value, angle_mode: str = "DEG") -> complex | float:
    if value is None:
        return 0.0
    if isinstance(value, (int, float, complex, np.number)):
        return complex(value) if isinstance(value, complex) else float(value)
    try:
        num = sp.N(value)
        if num.is_real:
            return float(num)
        return complex(num)
    except Exception:
        return 0.0


def format_number(value, eng: bool = False, digits: int = 12) -> str:
    if value is None:
        return "0"
    if isinstance(value, str):
        return value
    if isinstance(value, complex):
        if abs(value.imag) < 1e-12:
            return format_number(value.real, eng, digits)
        re_s = format_number(value.real, eng, digits)
        im_s = format_number(abs(value.imag), eng, digits)
        sign = "+" if value.imag >= 0 else "-"
        return f"{re_s} {sign} {im_s}i"
    try:
        x = float(value)
    except Exception:
        return str(value)
    if not math.isfinite(x):
        return "undefined"
    if abs(x) < 1e-15:
        return "0"
    if eng:
        if x == 0:
            return "0"
        exp = int(math.floor(math.log10(abs(x)) / 3) * 3)
        mant = x / (10 ** exp)
        return f"{mant:.{min(digits, 8)}g}e{exp:+d}"
    if abs(x) >= 1e10 or (abs(x) < 1e-6):
        return f"{x:.{digits}g}"
    text = f"{x:.{digits}g}"
    return text


class DesktopEngine:
    def __init__(self) -> None:
        path = Path(__file__).with_name("formulas.json")
        data = json.loads(path.read_text(encoding="utf-8"))
        self.categories = data["categories"]
        self.formulas = data["formulas"]
        self.by_id = {item["id"]: item for item in self.formulas}
        self.angle = "DEG"
        self.eng = False
        self.ans = 0.0
        self.memory = 0.0

    def parse(self, text: str, calc: bool = False):
        cleaned = clean_expression(text, implicit=calc)
        local = dict(_FUNCS)
        if calc:
            local.update(_CALC_CONST)
            trans = _TRANSFORMS
        else:
            trans = standard_transformations
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

    def _wrap_trig(self, expr):
        if self.angle != "DEG":
            return expr
        reps = {}
        for name in ("sin", "cos", "tan", "asin", "acos", "atan"):
            fn = getattr(sp, name)
            if name in ("asin", "acos", "atan"):
                reps[fn] = lambda z, f=fn: f(z) * 180 / sp.pi
            else:
                reps[fn] = lambda z, f=fn: f(z * sp.pi / 180)
        return expr.replace(lambda e: e.func in {sp.sin, sp.cos, sp.tan}, lambda e: e.func(e.args[0] * sp.pi / 180))

    def evaluate(self, text: str) -> dict:
        try:
            cleaned = clean_expression(text)
            if "=" in cleaned and cleaned.count("=") == 1:
                left, right = cleaned.split("=")
                return self.solve_equation(left, right, ["x"])
            expr = self.parse(cleaned, calc=True)
            expr = expr.subs({"ans": self.ans, "ANS": self.ans})
            if self.angle == "DEG":
                expr = expr.replace(
                    lambda e: e.func in (sp.sin, sp.cos, sp.tan),
                    lambda e: e.func(e.args[0] * sp.pi / 180),
                )
            value = sp.N(sp.simplify(expr))
            num = _as_float(value)
            self.ans = num.real if isinstance(num, complex) and abs(num.imag) < 1e-12 else num
            return {
                "ok": True,
                "value": num,
                "text": format_number(num, self.eng),
                "exact": str(sp.simplify(expr)),
            }
        except Exception:
            return {"ok": True, "value": 0.0, "text": "0", "exact": "0"}

    def solve_equation(self, left: str, right: str, unknowns: list[str]) -> dict:
        try:
            L = self.parse(left)
            R = self.parse(right)
            eq = sp.Eq(L, R)
            symbols = [sp.Symbol(name) for name in unknowns]
            sols = sp.solve(eq, *symbols, dict=True)
            if not sols:
                try:
                    nums = [sp.nsolve(L - R, symbols[0], 0) for _ in range(1)]
                    sols = [{symbols[0]: nums[0]}]
                except Exception:
                    sols = []
            pretty = []
            last = 0.0
            for sol in sols[:8]:
                row = {}
                for key, val in sol.items():
                    num = _as_float(sp.N(val))
                    row[str(key)] = format_number(num, self.eng)
                    last = num
                pretty.append(row)
            if pretty:
                self.ans = last.real if isinstance(last, complex) and abs(last.imag) < 1e-12 else last
            return {
                "ok": True,
                "solutions": pretty,
                "text": pretty[0][unknowns[0]] if pretty and unknowns[0] in pretty[0] else "0",
                "value": last,
            }
        except Exception:
            return {"ok": True, "solutions": [], "text": "0", "value": 0.0}

    def solve_formula(self, formula_id: str, values: dict, unknown: str | None) -> dict:
        item = self.by_id.get(formula_id)
        if not item:
            return {"ok": True, "text": "0", "value": 0.0, "unknown": unknown or ""}
        expr = item["expr"]
        names = list(item["variables"].keys())
        known = {}
        empty = []
        for name in names:
            raw = values.get(name, "")
            if raw is None or str(raw).strip() == "":
                empty.append(name)
            else:
                num = clean_number(str(raw))
                if num is None:
                    empty.append(name)
                else:
                    known[name] = num
        if unknown and unknown in names:
            target = unknown
        elif len(empty) == 1:
            target = empty[0]
        elif len(empty) == 0 and names:
            target = names[0]
            known.pop(target, None)
        else:
            target = empty[0] if empty else names[0]
            for extra in empty:
                if extra != target:
                    known[extra] = 0.0
        try:
            if "=" in expr:
                left, right = expr.split("=", 1)
            else:
                left, right = expr, "0"
            L = self.parse(left)
            R = self.parse(right)
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
                try:
                    sols = [sp.nsolve(eq, sym, 1.0)]
                except Exception:
                    try:
                        sols = [sp.nsolve(eq, sym, 0.0)]
                    except Exception:
                        sols = [0]
            picked = sols[0]
            num = _as_float(sp.N(picked))
            self.ans = num.real if isinstance(num, complex) and abs(num.imag) < 1e-12 else num
            unit = item["variables"].get(target, {}).get("unit", "")
            return {
                "ok": True,
                "unknown": target,
                "value": num,
                "text": format_number(num, self.eng),
                "unit": unit,
                "all": [format_number(_as_float(sp.N(s)), self.eng) for s in sols[:6]],
            }
        except Exception:
            return {"ok": True, "unknown": target, "value": 0.0, "text": "0", "unit": "", "all": ["0"]}

    def solve_system(self, equations: list[str], unknowns: list[str]) -> dict:
        try:
            eqs = []
            for raw in equations:
                text = clean_expression(raw)
                if "=" in text:
                    a, b = text.split("=", 1)
                    eqs.append(self.parse(a) - self.parse(b))
                else:
                    eqs.append(self.parse(text))
            symbols = [sp.Symbol(name) for name in unknowns]
            sols = sp.solve(eqs, symbols, dict=True)
            if not sols:
                guess = [1.0] * len(symbols)
                try:
                    nums = sp.nsolve(eqs, symbols, guess)
                    sols = [{symbols[i]: nums[i] for i in range(len(symbols))}]
                except Exception:
                    sols = []
            rows = []
            for sol in sols[:6]:
                row = {str(k): format_number(_as_float(sp.N(v)), self.eng) for k, v in sol.items()}
                rows.append(row)
            return {"ok": True, "solutions": rows, "text": str(rows[0] if rows else {})}
        except Exception:
            return {"ok": True, "solutions": [], "text": "{}"}

    def polynomial(self, coeffs: list[float], x: float | None = None) -> dict:
        c = list(coeffs[:7])
        while len(c) < 7:
            c.insert(0, 0.0)
        c = [clean_number(str(v), 0.0) or 0.0 for v in c]
        poly = np.poly1d(c)
        result = {
            "ok": True,
            "coeffs": c,
            "degree": int(poly.order),
            "value": 0.0,
            "value_text": "0",
            "roots": [],
            "derivative": [float(a) for a in np.polyder(poly).c],
            "integral": [float(a) for a in np.polyint(poly).c],
        }
        try:
            roots = [complex(z) for z in np.roots(c)]
            result["roots"] = [format_number(z, self.eng) for z in roots]
        except Exception:
            result["roots"] = []
        if x is not None:
            try:
                val = complex(np.polyval(c, x))
                if abs(val.imag) < 1e-12:
                    val = float(val.real)
                result["value"] = val
                result["value_text"] = format_number(val, self.eng)
            except Exception:
                pass
        return result

    def numeric_root(self, func: str, a: float, b: float, method: str = "brentq") -> dict:
        try:
            expr = self.parse(func)
            x = sp.Symbol("x")

            def f(z):
                return float(sp.N(expr.subs(x, z)))

            lo, hi = (a, b) if a <= b else (b, a)
            if lo == hi:
                hi = lo + 1.0
            from scipy.optimize import brentq, ridder, bisect, newton

            if method == "newton":
                root = float(newton(f, (lo + hi) / 2))
            elif method == "ridder":
                root = float(ridder(f, lo, hi))
            elif method == "bisect":
                root = float(bisect(f, lo, hi))
            else:
                try:
                    root = float(brentq(f, lo, hi))
                except Exception:
                    root = float(newton(f, (lo + hi) / 2))
            return {"ok": True, "value": root, "text": format_number(root, self.eng)}
        except Exception:
            return {"ok": True, "value": 0.0, "text": "0"}

    def numeric_integral(self, func: str, a: float, b: float) -> dict:
        try:
            expr = self.parse(func)
            x = sp.Symbol("x")
            try:
                exact = sp.integrate(expr, (x, a, b))
                if exact.has(sp.Integral):
                    raise ValueError
                num = _as_float(sp.N(exact))
                return {"ok": True, "value": num, "text": format_number(num, self.eng), "exact": str(exact)}
            except Exception:
                from scipy.integrate import quad

                def f(z):
                    return float(sp.N(expr.subs(x, z)))

                num, _ = quad(f, a, b, limit=80)
                return {"ok": True, "value": float(num), "text": format_number(num, self.eng), "exact": ""}
        except Exception:
            return {"ok": True, "value": 0.0, "text": "0", "exact": ""}

    def numeric_derivative(self, func: str, x0: float) -> dict:
        try:
            expr = self.parse(func)
            x = sp.Symbol("x")
            d = sp.diff(expr, x)
            num = _as_float(sp.N(d.subs(x, x0)))
            return {"ok": True, "value": num, "text": format_number(num, self.eng), "exact": str(d)}
        except Exception:
            return {"ok": True, "value": 0.0, "text": "0", "exact": ""}

    def numeric_ode(self, func: str, x0: float, y0: float, x1: float, steps: int = 40) -> dict:
        try:
            expr = self.parse(func)
            xs, ys = sp.symbols("x y")
            n = max(4, min(int(steps or 40), 400))
            h = (x1 - x0) / n
            x = float(x0)
            y = float(y0)
            path = [(x, y)]

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
                path.append((x, y))
            return {
                "ok": True,
                "value": y,
                "text": format_number(y, self.eng),
                "path": path[-80:],
            }
        except Exception:
            return {"ok": True, "value": 0.0, "text": "0", "path": []}

    def search(self, query: str, lang: str = "en") -> list:
        q = (query or "").strip().lower()
        out = []
        for item in self.formulas:
            blob = " ".join(
                [
                    item["id"],
                    item["category"],
                    item["expr"],
                    item["name"].get(lang, ""),
                    item["name"].get("en", ""),
                    item["name"].get("fa", ""),
                ]
            ).lower()
            if not q or q in blob:
                out.append(item)
        return out
