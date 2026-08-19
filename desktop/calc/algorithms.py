"""Named algorithms for the desktop app. Independent of the web copy."""

from __future__ import annotations

import math
from functools import lru_cache

import numpy as np
import sympy as sp

from .sanitize import clean_number


def _nm(en: str, fa: str, fi: str) -> dict:
    return {"en": en, "fa": fa, "fi": fi}


def _p(default: str, en: str, fa: str = "", fi: str = "") -> dict:
    return {"default": default, "name": _nm(en, fa or en, fi or en)}


CATS = {
    "algo.numth": _nm("Number theory", "نظریه اعداد", "Lukuteoria"),
    "algo.combo": _nm("Combinatorics", "ترکیبیات", "Kombinatoriikka"),
    "algo.seq": _nm("Sequences", "دنباله ها", "Jonot"),
    "algo.linalg": _nm("Linear algebra", "جبر خطی", "Lineaarialgebra"),
    "algo.root": _nm("Root finding", "ریشه یابی", "Juuren haku"),
    "algo.integ": _nm("Integration", "انتگرال", "Integrointi"),
    "algo.ode": _nm("Differential equations", "معادلات دیفرانسیل", "Differentiaaliyhtalot"),
    "algo.interp": _nm("Interpolation", "درونیابی", "Interpolointi"),
    "algo.opt": _nm("Optimization", "بهینه سازی", "Optimointi"),
    "algo.stat": _nm("Statistics", "آمار", "Tilastot"),
    "algo.dist": _nm("Distributions", "توزیع ها", "Jakaumat"),
    "algo.signal": _nm("Signals", "سیگنال", "Signaalit"),
    "algo.geo": _nm("Geometry algorithms", "هندسه الگوریتمی", "Geometria-algoritmit"),
    "algo.convert": _nm("Conversion", "تبدیل", "Muunnos"),
}


def _pretty(value, eng: bool = False) -> str:
    if value is None:
        return "0"
    if isinstance(value, str):
        return value
    if isinstance(value, (list, tuple)):
        return ", ".join(_pretty(v, eng) for v in value)
    if isinstance(value, dict):
        return "  ".join(f"{k}={_pretty(v, eng)}" for k, v in value.items())
    if isinstance(value, complex):
        if abs(value.imag) < 1e-12:
            return _pretty(value.real, eng)
        sign = "+" if value.imag >= 0 else "-"
        return f"{_pretty(value.real, eng)} {sign} {_pretty(abs(value.imag), eng)}i"
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


def _num(values: dict, key: str, default: float = 0.0) -> float:
    raw = values.get(key, "")
    got = clean_number(str(raw), default)
    return default if got is None else float(got)


def _int(values: dict, key: str, default: int = 0) -> int:
    try:
        return int(round(_num(values, key, float(default))))
    except Exception:
        return default


def _text(values: dict, key: str, default: str = "") -> str:
    raw = values.get(key)
    if raw is None:
        return default
    text = str(raw).strip()
    return text if text else default


def _vec(raw: str) -> np.ndarray:
    text = (raw or "").replace(";", ",").replace("\n", ",")
    parts = [p.strip() for p in text.split(",") if p.strip()]
    out = []
    for p in parts:
        n = clean_number(p)
        if n is not None:
            out.append(float(n))
    return np.array(out, dtype=float)


def _mat(raw: str) -> np.ndarray:
    text = (raw or "").strip()
    rows = []
    for line in text.replace(";", "\n").splitlines():
        line = line.strip()
        if not line:
            continue
        row = []
        for p in line.replace(",", " ").split():
            n = clean_number(p)
            if n is not None:
                row.append(float(n))
        if row:
            rows.append(row)
    if not rows:
        return np.array([[0.0]])
    width = max(len(r) for r in rows)
    padded = [r + [0.0] * (width - len(r)) for r in rows]
    return np.array(padded, dtype=float)


def _ok(text, detail: str = "") -> dict:
    return {"ok": True, "text": str(text), "detail": detail}


def _fail() -> dict:
    return {"ok": True, "text": "0", "detail": ""}


def _parse_fx(func: str):
    from sympy.parsing.sympy_parser import parse_expr, standard_transformations

    local = {
        "sin": sp.sin,
        "cos": sp.cos,
        "tan": sp.tan,
        "exp": sp.exp,
        "log": sp.log,
        "ln": sp.log,
        "sqrt": sp.sqrt,
        "abs": sp.Abs,
        "pi": sp.pi,
        "e": sp.E,
    }
    try:
        return parse_expr(func.replace("^", "**"), local_dict=local, transformations=standard_transformations)
    except Exception:
        return sp.Integer(0)


def _f1(func: str):
    expr = _parse_fx(func)
    x = sp.Symbol("x")

    def f(z):
        try:
            return float(sp.N(expr.subs(x, z)))
        except Exception:
            return 0.0

    return f


def _f2(func: str):
    expr = _parse_fx(func)
    xs, ys = sp.symbols("x y")

    def f(xv, yv):
        try:
            return float(sp.N(expr.subs({xs: xv, ys: yv})))
        except Exception:
            return 0.0

    return f


def _r_gcd(v, eng):
    a, b = _int(v, "a"), _int(v, "b")
    return _ok(math.gcd(a, b))


def _r_lcm(v, eng):
    a, b = _int(v, "a"), _int(v, "b")
    if a == 0 or b == 0:
        return _ok(0)
    return _ok(abs(a // math.gcd(a, b) * b))


def _r_egcd(v, eng):
    a, b = _int(v, "a"), _int(v, "b")
    g, x, y = sp.gcdex(a, b)
    return _ok(int(g), f"x = {int(x)}   y = {int(y)}   {a}*x + {b}*y = {int(g)}")


def _r_invmod(v, eng):
    a, m = _int(v, "a"), _int(v, "m")
    try:
        return _ok(int(pow(a, -1, m)))
    except Exception:
        return _fail()


def _r_powmod(v, eng):
    a, b, m = _int(v, "a"), _int(v, "b"), _int(v, "m")
    if m == 0:
        return _fail()
    return _ok(int(pow(a, b, m)))


def _r_isprime(v, eng):
    n = _int(v, "n")
    return _ok(1 if sp.isprime(n) else 0, "prime" if sp.isprime(n) else "not prime")


def _r_nextprime(v, eng):
    return _ok(int(sp.nextprime(_int(v, "n"))))


def _r_prevprime(v, eng):
    n = _int(v, "n")
    if n <= 2:
        return _ok(0)
    return _ok(int(sp.prevprime(n)))


def _r_factor(v, eng):
    n = abs(_int(v, "n"))
    if n < 2:
        return _ok(str(n))
    fac = sp.factorint(n)
    parts = [str(p) if e == 1 else f"{p}^{e}" for p, e in sorted(fac.items())]
    return _ok(" * ".join(parts), str(dict((int(p), int(e)) for p, e in fac.items())))


def _r_totient(v, eng):
    return _ok(int(sp.totient(_int(v, "n"))))


def _r_divisors(v, eng):
    n = abs(_int(v, "n"))
    if n == 0:
        return _fail()
    divs = sp.divisors(n)
    return _ok(len(divs), " ".join(str(int(d)) for d in divs))


def _r_sigma(v, eng):
    return _ok(int(sp.divisor_sigma(_int(v, "n"), _int(v, "k", 1))))


def _r_nthroot(v, eng):
    n, k = abs(_int(v, "n")), max(1, _int(v, "k", 2))
    root, exact = sp.integer_nthroot(n, k)
    return _ok(int(root), "exact" if exact else "floor")


def _r_crt(v, eng):
    a1, n1, a2, n2 = _int(v, "a1"), _int(v, "n1"), _int(v, "a2"), _int(v, "n2")
    try:
        from sympy.ntheory.modular import solve_congruence

        out = solve_congruence((a1, n1), (a2, n2))
        if not out:
            return _fail()
        x, mod = out
        return _ok(int(x), f"mod {int(mod)}")
    except Exception:
        return _fail()


def _r_binom(v, eng):
    n, k = _int(v, "n"), _int(v, "k")
    try:
        return _ok(int(sp.binomial(n, k)))
    except Exception:
        return _fail()


def _r_perm(v, eng):
    n, k = _int(v, "n"), _int(v, "k")
    if k < 0 or n < 0 or k > n:
        return _ok(0)
    return _ok(int(sp.factorial(n) // sp.factorial(n - k)))


def _r_fact(v, eng):
    n = _int(v, "n")
    if n < 0 or n > 500:
        return _fail()
    return _ok(int(sp.factorial(n)))


def _r_catalan(v, eng):
    n = _int(v, "n")
    if n < 0 or n > 200:
        return _fail()
    return _ok(int(sp.catalan(n)))


def _r_bell(v, eng):
    n = _int(v, "n")
    if n < 0 or n > 60:
        return _fail()
    return _ok(int(sp.bell(n)))


def _r_stir2(v, eng):
    n, k = _int(v, "n"), _int(v, "k")
    try:
        return _ok(int(sp.stirling(n, k, kind=2)))
    except Exception:
        return _fail()


def _r_part(v, eng):
    n = _int(v, "n")
    if n < 0 or n > 200:
        return _fail()
    return _ok(int(sp.partition(n)))


def _r_fib(v, eng):
    return _ok(int(sp.fibonacci(_int(v, "n"))))


def _r_lucas(v, eng):
    return _ok(int(sp.lucas(_int(v, "n"))))


def _r_harm(v, eng):
    n = _int(v, "n")
    if n < 1:
        return _fail()
    return _ok(_pretty(float(sp.N(sp.harmonic(n))), eng), str(sp.harmonic(n)))


def _r_arith_nth(v, eng):
    a, d, n = _num(v, "a"), _num(v, "d"), _int(v, "n", 1)
    return _ok(_pretty(a + (n - 1) * d, eng))


def _r_arith_sum(v, eng):
    a, d, n = _num(v, "a"), _num(v, "d"), _int(v, "n", 1)
    return _ok(_pretty(n / 2 * (2 * a + (n - 1) * d), eng))


def _r_geom_nth(v, eng):
    a, r, n = _num(v, "a"), _num(v, "r"), _int(v, "n", 1)
    return _ok(_pretty(a * (r ** (n - 1)), eng))


def _r_geom_sum(v, eng):
    a, r, n = _num(v, "a"), _num(v, "r"), _int(v, "n", 1)
    if abs(r - 1) < 1e-15:
        return _ok(_pretty(a * n, eng))
    return _ok(_pretty(a * (1 - r**n) / (1 - r), eng))


def _r_det(v, eng):
    m = _mat(_text(v, "m", "1, 0; 0, 1"))
    if m.shape[0] != m.shape[1]:
        return _fail()
    return _ok(_pretty(float(np.linalg.det(m)), eng))


def _r_inv(v, eng):
    m = _mat(_text(v, "m", "1, 0; 0, 1"))
    try:
        inv = np.linalg.inv(m)
        rows = [", ".join(_pretty(x, eng) for x in row) for row in inv]
        return _ok("; ".join(rows))
    except Exception:
        return _fail()


def _r_trans(v, eng):
    m = _mat(_text(v, "m", "1, 2; 3, 4"))
    rows = [", ".join(_pretty(x, eng) for x in row) for row in m.T]
    return _ok("; ".join(rows))


def _r_trace(v, eng):
    m = _mat(_text(v, "m", "1, 0; 0, 1"))
    return _ok(_pretty(float(np.trace(m)), eng))


def _r_rank(v, eng):
    m = _mat(_text(v, "m", "1, 0; 0, 1"))
    return _ok(int(np.linalg.matrix_rank(m)))


def _r_mul(v, eng):
    a = _mat(_text(v, "a", "1, 0; 0, 1"))
    b = _mat(_text(v, "b", "1, 0; 0, 1"))
    try:
        p = a @ b
        rows = [", ".join(_pretty(x, eng) for x in row) for row in p]
        return _ok("; ".join(rows))
    except Exception:
        return _fail()


def _r_linsolve(v, eng):
    a = _mat(_text(v, "a", "1, 0; 0, 1"))
    b = _vec(_text(v, "b", "1, 1"))
    try:
        x = np.linalg.solve(a, b)
        return _ok(", ".join(_pretty(float(t), eng) for t in x))
    except Exception:
        return _fail()


def _r_eig(v, eng):
    m = _mat(_text(v, "m", "1, 0; 0, 2"))
    try:
        w = np.linalg.eigvals(m)
        return _ok(", ".join(_pretty(complex(z), eng) for z in w))
    except Exception:
        return _fail()


def _r_fnorm(v, eng):
    m = _mat(_text(v, "m", "1, 2; 3, 4"))
    return _ok(_pretty(float(np.linalg.norm(m)), eng))


def _r_bisect(v, eng):
    f = _f1(_text(v, "f", "x**2-2"))
    a, b = _num(v, "a", 0), _num(v, "b", 2)
    try:
        from scipy.optimize import bisect

        return _ok(_pretty(float(bisect(f, a, b)), eng))
    except Exception:
        return _fail()


def _r_newton(v, eng):
    f = _f1(_text(v, "f", "x**2-2"))
    x0 = _num(v, "x0", 1)
    try:
        from scipy.optimize import newton

        return _ok(_pretty(float(newton(f, x0)), eng))
    except Exception:
        return _fail()


def _r_secant(v, eng):
    f = _f1(_text(v, "f", "x**2-2"))
    x0, x1 = _num(v, "x0", 1), _num(v, "x1", 2)
    try:
        from scipy.optimize import newton

        return _ok(_pretty(float(newton(f, x0, x1=x1)), eng))
    except Exception:
        return _fail()


def _r_brent(v, eng):
    f = _f1(_text(v, "f", "x**2-2"))
    a, b = _num(v, "a", 0), _num(v, "b", 2)
    try:
        from scipy.optimize import brentq

        return _ok(_pretty(float(brentq(f, a, b)), eng))
    except Exception:
        return _fail()


def _r_trap(v, eng):
    f = _f1(_text(v, "f", "x**2"))
    a, b, n = _num(v, "a", 0), _num(v, "b", 1), max(2, _int(v, "n", 40))
    xs = np.linspace(a, b, n + 1)
    ys = np.array([f(x) for x in xs])
    trap = getattr(np, "trapezoid", None) or getattr(np, "trapz")
    return _ok(_pretty(float(trap(ys, xs)), eng))


def _r_simpson(v, eng):
    f = _f1(_text(v, "f", "x**2"))
    a, b, n = _num(v, "a", 0), _num(v, "b", 1), max(2, _int(v, "n", 40))
    if n % 2:
        n += 1
    h = (b - a) / n
    s = f(a) + f(b)
    for i in range(1, n):
        s += (4 if i % 2 else 2) * f(a + i * h)
    return _ok(_pretty(s * h / 3, eng))


def _r_romberg(v, eng):
    f = _f1(_text(v, "f", "x**2"))
    a, b = _num(v, "a", 0), _num(v, "b", 1)
    try:
        from scipy.integrate import romberg

        return _ok(_pretty(float(romberg(f, a, b, show=False)), eng))
    except Exception:
        try:
            from scipy.integrate import quad

            val, _ = quad(f, a, b)
            return _ok(_pretty(float(val), eng))
        except Exception:
            return _fail()


def _r_quad(v, eng):
    f = _f1(_text(v, "f", "x**2"))
    a, b = _num(v, "a", 0), _num(v, "b", 1)
    try:
        from scipy.integrate import quad

        val, err = quad(f, a, b)
        return _ok(_pretty(float(val), eng), f"est. error {err:.3g}")
    except Exception:
        return _fail()


def _step_ode(method: str, v, eng):
    f = _f2(_text(v, "f", "y"))
    x0, y0, x1 = _num(v, "x0", 0), _num(v, "y0", 1), _num(v, "x1", 1)
    n = max(4, min(_int(v, "steps", 40), 800))
    h = (x1 - x0) / n
    x, y = float(x0), float(y0)
    for _ in range(n):
        if method == "euler":
            y = y + h * f(x, y)
        elif method == "heun":
            k1 = f(x, y)
            k2 = f(x + h, y + h * k1)
            y = y + h * (k1 + k2) / 2
        else:
            k1 = f(x, y)
            k2 = f(x + h / 2, y + h * k1 / 2)
            k3 = f(x + h / 2, y + h * k2 / 2)
            k4 = f(x + h, y + h * k3)
            y = y + h * (k1 + 2 * k2 + 2 * k3 + k4) / 6
        x = x + h
        if not math.isfinite(y):
            return _fail()
    return _ok(_pretty(y, eng))


def _r_euler(v, eng):
    return _step_ode("euler", v, eng)


def _r_heun(v, eng):
    return _step_ode("heun", v, eng)


def _r_rk4(v, eng):
    return _step_ode("rk4", v, eng)


def _r_rk45(v, eng):
    f = _f2(_text(v, "f", "y"))
    x0, y0, x1 = _num(v, "x0", 0), _num(v, "y0", 1), _num(v, "x1", 1)

    def rhs(t, z):
        return [f(float(t), float(z[0]))]

    try:
        from scipy.integrate import solve_ivp

        sol = solve_ivp(rhs, (x0, x1), [y0], rtol=1e-6, atol=1e-8)
        if not sol.success:
            return _fail()
        return _ok(_pretty(float(sol.y[0, -1]), eng))
    except Exception:
        return _fail()


def _r_lerp(v, eng):
    x0, y0, x1, y1, x = _num(v, "x0"), _num(v, "y0"), _num(v, "x1", 1), _num(v, "y1", 1), _num(v, "x", 0.5)
    if abs(x1 - x0) < 1e-15:
        return _fail()
    return _ok(_pretty(y0 + (y1 - y0) * (x - x0) / (x1 - x0), eng))


def _r_lagrange(v, eng):
    xs = _vec(_text(v, "xs", "0, 1, 2"))
    ys = _vec(_text(v, "ys", "1, 2, 5"))
    x = _num(v, "x", 1.5)
    if len(xs) == 0 or len(xs) != len(ys):
        return _fail()
    total = 0.0
    for i, yi in enumerate(ys):
        li = 1.0
        for j, xj in enumerate(xs):
            if i == j:
                continue
            den = xs[i] - xj
            if abs(den) < 1e-15:
                return _fail()
            li *= (x - xj) / den
        total += yi * li
    return _ok(_pretty(total, eng))


def _r_golden(v, eng):
    f = _f1(_text(v, "f", "(x-2)**2"))
    a, b = _num(v, "a", 0), _num(v, "b", 4)
    try:
        from scipy.optimize import minimize_scalar

        out = minimize_scalar(f, bounds=(a, b), method="bounded")
        return _ok(_pretty(float(out.x), eng), f"f = {_pretty(float(out.fun), eng)}")
    except Exception:
        return _fail()


def _r_nelder(v, eng):
    f = _f1(_text(v, "f", "(x-2)**2"))
    x0 = _num(v, "x0", 0)

    def obj(z):
        return f(float(z[0]))

    try:
        from scipy.optimize import minimize

        out = minimize(obj, [x0], method="Nelder-Mead")
        return _ok(_pretty(float(out.x[0]), eng), f"f = {_pretty(float(out.fun), eng)}")
    except Exception:
        return _fail()


def _data(v) -> np.ndarray:
    return _vec(_text(v, "data", "1, 2, 3, 4, 5"))


def _r_mean(v, eng):
    d = _data(v)
    return _ok(_pretty(float(np.mean(d)), eng)) if d.size else _fail()


def _r_median(v, eng):
    d = _data(v)
    return _ok(_pretty(float(np.median(d)), eng)) if d.size else _fail()


def _r_var(v, eng):
    d = _data(v)
    return _ok(_pretty(float(np.var(d, ddof=1 if d.size > 1 else 0)), eng)) if d.size else _fail()


def _r_std(v, eng):
    d = _data(v)
    return _ok(_pretty(float(np.std(d, ddof=1 if d.size > 1 else 0)), eng)) if d.size else _fail()


def _r_geomean(v, eng):
    d = _data(v)
    if d.size == 0 or np.any(d <= 0):
        return _fail()
    return _ok(_pretty(float(np.exp(np.mean(np.log(d)))), eng))


def _r_rms(v, eng):
    d = _data(v)
    return _ok(_pretty(float(np.sqrt(np.mean(d * d))), eng)) if d.size else _fail()


def _r_pct(v, eng):
    d = _data(v)
    p = _num(v, "p", 50)
    return _ok(_pretty(float(np.percentile(d, p)), eng)) if d.size else _fail()


def _r_linreg(v, eng):
    xs = _vec(_text(v, "xs", "1, 2, 3, 4"))
    ys = _vec(_text(v, "ys", "2, 3, 5, 6"))
    if xs.size < 2 or xs.size != ys.size:
        return _fail()
    slope, intercept = np.polyfit(xs, ys, 1)
    return _ok(_pretty(float(slope), eng), f"intercept = {_pretty(float(intercept), eng)}")


def _r_corr(v, eng):
    xs = _vec(_text(v, "xs", "1, 2, 3, 4"))
    ys = _vec(_text(v, "ys", "2, 3, 5, 6"))
    if xs.size < 2 or xs.size != ys.size:
        return _fail()
    return _ok(_pretty(float(np.corrcoef(xs, ys)[0, 1]), eng))


def _dist(name: str):
    import scipy.stats as st

    return getattr(st, name)


def _r_pdf(name):
    def run(v, eng):
        try:
            dist = _dist(name)
            x = _num(v, "x", 0)
            kw = {}
            for key in ("loc", "scale", "a", "b", "c", "s", "df", "dfn", "dfd", "n", "p", "mu"):
                if key in v and str(v.get(key, "")).strip() != "":
                    kw[key] = _num(v, key, 0 if key != "scale" else 1)
            return _ok(_pretty(float(dist.pdf(x, **kw)), eng))
        except Exception:
            try:
                dist = _dist(name)
                x = _num(v, "x", 0)
                return _ok(_pretty(float(dist.pmf(x)), eng))
            except Exception:
                return _fail()

    return run


def _r_cdf(name):
    def run(v, eng):
        try:
            dist = _dist(name)
            x = _num(v, "x", 0)
            kw = {}
            for key in ("loc", "scale", "a", "b", "c", "s", "df", "dfn", "dfd", "n", "p", "mu"):
                if key in v and str(v.get(key, "")).strip() != "":
                    kw[key] = _num(v, key, 0 if key != "scale" else 1)
            return _ok(_pretty(float(dist.cdf(x, **kw)), eng))
        except Exception:
            return _fail()

    return run


def _r_ppf(name):
    def run(v, eng):
        try:
            dist = _dist(name)
            q = _num(v, "q", 0.5)
            kw = {}
            for key in ("loc", "scale", "a", "b", "c", "s", "df", "dfn", "dfd", "n", "p", "mu"):
                if key in v and str(v.get(key, "")).strip() != "":
                    kw[key] = _num(v, key, 0 if key != "scale" else 1)
            return _ok(_pretty(float(dist.ppf(q, **kw)), eng))
        except Exception:
            return _fail()

    return run


def _r_fft(v, eng):
    d = _vec(_text(v, "data", "1, 0, -1, 0"))
    if d.size == 0:
        return _fail()
    mag = np.abs(np.fft.rfft(d))
    return _ok(", ".join(_pretty(float(x), eng) for x in mag))


def _r_conv(v, eng):
    a = _vec(_text(v, "a", "1, 2, 3"))
    b = _vec(_text(v, "b", "0, 1, 0.5"))
    if a.size == 0 or b.size == 0:
        return _fail()
    c = np.convolve(a, b)
    return _ok(", ".join(_pretty(float(x), eng) for x in c))


def _r_dist2(v, eng):
    return _ok(
        _pretty(
            math.hypot(_num(v, "x2") - _num(v, "x1"), _num(v, "y2") - _num(v, "y1")),
            eng,
        )
    )


def _r_dist3(v, eng):
    dx = _num(v, "x2") - _num(v, "x1")
    dy = _num(v, "y2") - _num(v, "y1")
    dz = _num(v, "z2") - _num(v, "z1")
    return _ok(_pretty(math.sqrt(dx * dx + dy * dy + dz * dz), eng))


def _r_shoelace(v, eng):
    pts = _text(v, "pts", "0,0; 1,0; 0,1")
    m = _mat(pts)
    if m.shape[0] < 3 or m.shape[1] < 2:
        return _fail()
    x, y = m[:, 0], m[:, 1]
    s = 0.0
    n = len(x)
    for i in range(n):
        j = (i + 1) % n
        s += x[i] * y[j] - x[j] * y[i]
    return _ok(_pretty(abs(s) / 2, eng))


def _r_heron(v, eng):
    a, b, c = _num(v, "a", 3), _num(v, "b", 4), _num(v, "c", 5)
    s = (a + b + c) / 2
    val = s * (s - a) * (s - b) * (s - c)
    if val < 0:
        return _fail()
    return _ok(_pretty(math.sqrt(val), eng))


def _r_haversine(v, eng):
    lat1, lon1 = math.radians(_num(v, "lat1")), math.radians(_num(v, "lon1"))
    lat2, lon2 = math.radians(_num(v, "lat2")), math.radians(_num(v, "lon2"))
    r = _num(v, "r", 6371)
    dlat, dlon = lat2 - lat1, lon2 - lon1
    h = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return _ok(_pretty(2 * r * math.asin(min(1.0, math.sqrt(h))), eng))


def _r_base(v, eng):
    raw = _text(v, "n", "255")
    frm, to = max(2, min(36, _int(v, "frm", 10))), max(2, min(36, _int(v, "to", 16)))
    try:
        value = int(raw, frm)
        if to == 10:
            return _ok(str(value))
        digits = "0123456789abcdefghijklmnopqrstuvwxyz"
        if value == 0:
            return _ok("0")
        sign = "-" if value < 0 else ""
        value = abs(value)
        out = []
        while value:
            value, rem = divmod(value, to)
            out.append(digits[rem])
        return _ok(sign + "".join(reversed(out)))
    except Exception:
        return _fail()


RUN = {
    "alg_gcd": _r_gcd,
    "alg_lcm": _r_lcm,
    "alg_egcd": _r_egcd,
    "alg_invmod": _r_invmod,
    "alg_powmod": _r_powmod,
    "alg_isprime": _r_isprime,
    "alg_nextprime": _r_nextprime,
    "alg_prevprime": _r_prevprime,
    "alg_factor": _r_factor,
    "alg_totient": _r_totient,
    "alg_divisors": _r_divisors,
    "alg_sigma": _r_sigma,
    "alg_nthroot": _r_nthroot,
    "alg_crt": _r_crt,
    "alg_binom": _r_binom,
    "alg_perm": _r_perm,
    "alg_fact": _r_fact,
    "alg_catalan": _r_catalan,
    "alg_bell": _r_bell,
    "alg_stir2": _r_stir2,
    "alg_part": _r_part,
    "alg_fib": _r_fib,
    "alg_lucas": _r_lucas,
    "alg_harm": _r_harm,
    "alg_arith_nth": _r_arith_nth,
    "alg_arith_sum": _r_arith_sum,
    "alg_geom_nth": _r_geom_nth,
    "alg_geom_sum": _r_geom_sum,
    "alg_det": _r_det,
    "alg_inv": _r_inv,
    "alg_trans": _r_trans,
    "alg_trace": _r_trace,
    "alg_rank": _r_rank,
    "alg_mul": _r_mul,
    "alg_linsolve": _r_linsolve,
    "alg_eig": _r_eig,
    "alg_fnorm": _r_fnorm,
    "alg_bisect": _r_bisect,
    "alg_newton": _r_newton,
    "alg_secant": _r_secant,
    "alg_brent": _r_brent,
    "alg_trap": _r_trap,
    "alg_simpson": _r_simpson,
    "alg_romberg": _r_romberg,
    "alg_quad": _r_quad,
    "alg_euler": _r_euler,
    "alg_heun": _r_heun,
    "alg_rk4": _r_rk4,
    "alg_rk45": _r_rk45,
    "alg_lerp": _r_lerp,
    "alg_lagrange": _r_lagrange,
    "alg_golden": _r_golden,
    "alg_nelder": _r_nelder,
    "alg_mean": _r_mean,
    "alg_median": _r_median,
    "alg_var": _r_var,
    "alg_std": _r_std,
    "alg_geomean": _r_geomean,
    "alg_rms": _r_rms,
    "alg_pct": _r_pct,
    "alg_linreg": _r_linreg,
    "alg_corr": _r_corr,
    "alg_fft": _r_fft,
    "alg_conv": _r_conv,
    "alg_dist2": _r_dist2,
    "alg_dist3": _r_dist3,
    "alg_shoelace": _r_shoelace,
    "alg_heron": _r_heron,
    "alg_haversine": _r_haversine,
    "alg_base": _r_base,
}

DISTS = [
    ("norm", "Normal", "نرمال", "Normaali", {"loc": "0", "scale": "1"}),
    ("expon", "Exponential", "نمایی", "Eksponentiaalinen", {"loc": "0", "scale": "1"}),
    ("uniform", "Uniform", "یکنواخت", "Tasainen", {"loc": "0", "scale": "1"}),
    ("t", "Student t", "تی استیودنت", "Studentin t", {"df": "10", "loc": "0", "scale": "1"}),
    ("chi2", "Chi-square", "کای دو", "Khiin neliö", {"df": "4"}),
    ("f", "F", "اف", "F", {"dfn": "5", "dfd": "10"}),
    ("gamma", "Gamma", "گاما", "Gamma", {"a": "2", "loc": "0", "scale": "1"}),
    ("beta", "Beta", "بتا", "Beeta", {"a": "2", "b": "5"}),
    ("lognorm", "Log-normal", "لگ نرمال", "Lognormaali", {"s": "0.5", "loc": "0", "scale": "1"}),
    ("weibull_min", "Weibull", "وایبل", "Weibull", {"c": "1.5", "loc": "0", "scale": "1"}),
    ("cauchy", "Cauchy", "کوشی", "Cauchy", {"loc": "0", "scale": "1"}),
    ("laplace", "Laplace", "لاپلاس", "Laplace", {"loc": "0", "scale": "1"}),
    ("logistic", "Logistic", "لجستیک", "Logistinen", {"loc": "0", "scale": "1"}),
    ("rayleigh", "Rayleigh", "ریلی", "Rayleigh", {"loc": "0", "scale": "1"}),
    ("pareto", "Pareto", "پارتو", "Pareto", {"b": "2", "loc": "0", "scale": "1"}),
    ("gumbel_r", "Gumbel", "گامبل", "Gumbel", {"loc": "0", "scale": "1"}),
    ("poisson", "Poisson", "پواسون", "Poisson", {"mu": "3"}),
    ("binom", "Binomial", "دوجمله ای", "Binomi", {"n": "10", "p": "0.5"}),
    ("geom", "Geometric", "هندسی", "Geometrinen", {"p": "0.3"}),
    ("nbinom", "Negative binomial", "دوجمله ای منفی", "Negatiivinen binomi", {"n": "5", "p": "0.4"}),
]


def _core_items() -> list[dict]:
    ab = {"a": _p("12", "a"), "b": _p("18", "b")}
    items = [
        ("alg_gcd", "algo.numth", "GCD", "ب.م.م", "GCD", ab),
        ("alg_lcm", "algo.numth", "LCM", "ک.م.م", "SKM", ab),
        ("alg_egcd", "algo.numth", "Extended GCD", "ب.م.م گسترش یافته", "Laajennettu GCD", ab),
        ("alg_invmod", "algo.numth", "Modular inverse", "وارون پیمانه ای", "Modulaarinen kaanne", {"a": _p("3", "a"), "m": _p("11", "modulus")}),
        ("alg_powmod", "algo.numth", "Modular power", "توان پیمانه ای", "Modulaarinen potenssi", {"a": _p("3", "base"), "b": _p("5", "exp"), "m": _p("7", "modulus")}),
        ("alg_isprime", "algo.numth", "Primality", "اول بودن", "Alkuluku?", {"n": _p("97", "n")}),
        ("alg_nextprime", "algo.numth", "Next prime", "عدد اول بعدی", "Seuraava alkuluku", {"n": _p("100", "n")}),
        ("alg_prevprime", "algo.numth", "Previous prime", "عدد اول قبلی", "Edellinen alkuluku", {"n": _p("100", "n")}),
        ("alg_factor", "algo.numth", "Integer factorization", "تجزیه عدد", "Tekijoihin jako", {"n": _p("360", "n")}),
        ("alg_totient", "algo.numth", "Euler totient", "فی اویلر", "Eulerin totientti", {"n": _p("36", "n")}),
        ("alg_divisors", "algo.numth", "Divisors", "مقسوم علیه ها", "Tekijat", {"n": _p("60", "n")}),
        ("alg_sigma", "algo.numth", "Divisor sigma", "سیگما مقسوم علیه", "Tekijasumma", {"n": _p("12", "n"), "k": _p("1", "power k")}),
        ("alg_nthroot", "algo.numth", "Integer nth root", "ریشه صحیح", "Kokonaisjuuri", {"n": _p("81", "n"), "k": _p("4", "k")}),
        ("alg_crt", "algo.numth", "Chinese remainder", "باقیمانده چینی", "Kiinalainen jaannoslause", {"a1": _p("2", "a1"), "n1": _p("3", "n1"), "a2": _p("3", "a2"), "n2": _p("5", "n2")}),
        ("alg_binom", "algo.combo", "Binomial C(n,k)", "ترکیب", "Binomikerroin", {"n": _p("10", "n"), "k": _p("3", "k")}),
        ("alg_perm", "algo.combo", "Permutation P(n,k)", "جایگشت", "Permutaatio", {"n": _p("10", "n"), "k": _p("3", "k")}),
        ("alg_fact", "algo.combo", "Factorial", "فاکتوریل", "Kertoma", {"n": _p("10", "n")}),
        ("alg_catalan", "algo.combo", "Catalan number", "عدد کاتالان", "Catalanin luku", {"n": _p("8", "n")}),
        ("alg_bell", "algo.combo", "Bell number", "عدد بل", "Bellin luku", {"n": _p("8", "n")}),
        ("alg_stir2", "algo.combo", "Stirling 2nd kind", "استرلینگ نوع ۲", "Stirling 2", {"n": _p("6", "n"), "k": _p("3", "k")}),
        ("alg_part", "algo.combo", "Integer partitions", "افراز عدد", "Osiin jako", {"n": _p("10", "n")}),
        ("alg_fib", "algo.seq", "Fibonacci", "فیبوناچی", "Fibonacci", {"n": _p("12", "n")}),
        ("alg_lucas", "algo.seq", "Lucas", "لوکاس", "Lucas", {"n": _p("10", "n")}),
        ("alg_harm", "algo.seq", "Harmonic number", "عدد همساز", "Harmoninen luku", {"n": _p("10", "n")}),
        ("alg_arith_nth", "algo.seq", "Arithmetic term", "جمله حسابی", "Aritmeettinen termi", {"a": _p("2", "first"), "d": _p("3", "diff"), "n": _p("10", "n")}),
        ("alg_arith_sum", "algo.seq", "Arithmetic sum", "جمع حسابی", "Aritmeettinen summa", {"a": _p("2", "first"), "d": _p("3", "diff"), "n": _p("10", "n")}),
        ("alg_geom_nth", "algo.seq", "Geometric term", "جمله هندسی", "Geometrinen termi", {"a": _p("2", "first"), "r": _p("3", "ratio"), "n": _p("6", "n")}),
        ("alg_geom_sum", "algo.seq", "Geometric sum", "جمع هندسی", "Geometrinen summa", {"a": _p("2", "first"), "r": _p("3", "ratio"), "n": _p("6", "n")}),
        ("alg_det", "algo.linalg", "Determinant", "دترمینان", "Determinantti", {"m": _p("1, 2; 3, 4", "matrix")}),
        ("alg_inv", "algo.linalg", "Matrix inverse", "وارون ماتریس", "Kaanteismatriisi", {"m": _p("1, 2; 3, 4", "matrix")}),
        ("alg_trans", "algo.linalg", "Transpose", "ترانهاده", "Transpoosi", {"m": _p("1, 2; 3, 4", "matrix")}),
        ("alg_trace", "algo.linalg", "Trace", "اثر", "Jalki", {"m": _p("1, 2; 3, 4", "matrix")}),
        ("alg_rank", "algo.linalg", "Rank", "رتبه", "Aste", {"m": _p("1, 2; 2, 4", "matrix")}),
        ("alg_mul", "algo.linalg", "Matrix product", "ضرب ماتریس", "Matriisitulo", {"a": _p("1, 2; 3, 4", "A"), "b": _p("0, 1; 1, 0", "B")}),
        ("alg_linsolve", "algo.linalg", "Linear solve Ax=b", "حل Ax=b", "Lineaarinen ratkaisu", {"a": _p("2, 1; 1, 2", "A"), "b": _p("5, 4", "b")}),
        ("alg_eig", "algo.linalg", "Eigenvalues", "مقادیر ویژه", "Ominaisarvot", {"m": _p("2, 1; 1, 2", "matrix")}),
        ("alg_fnorm", "algo.linalg", "Frobenius norm", "نرم فروبینیوس", "Frobenius-normi", {"m": _p("1, 2; 3, 4", "matrix")}),
        ("alg_bisect", "algo.root", "Bisection", "نصف کردن", "Puolitus", {"f": _p("x**2-2", "f(x)"), "a": _p("0", "a"), "b": _p("2", "b")}),
        ("alg_newton", "algo.root", "Newton", "نیوتن", "Newton", {"f": _p("x**2-2", "f(x)"), "x0": _p("1", "x0")}),
        ("alg_secant", "algo.root", "Secant", "قاطع", "Sivustaja", {"f": _p("x**2-2", "f(x)"), "x0": _p("1", "x0"), "x1": _p("2", "x1")}),
        ("alg_brent", "algo.root", "Brent", "برنت", "Brent", {"f": _p("x**2-2", "f(x)"), "a": _p("0", "a"), "b": _p("2", "b")}),
        ("alg_trap", "algo.integ", "Trapezoid integral", "ذوزنقه", "Puolisuunnikas", {"f": _p("x**2", "f(x)"), "a": _p("0", "a"), "b": _p("1", "b"), "n": _p("40", "n")}),
        ("alg_simpson", "algo.integ", "Simpson integral", "سیمپسون", "Simpson", {"f": _p("x**2", "f(x)"), "a": _p("0", "a"), "b": _p("1", "b"), "n": _p("40", "n")}),
        ("alg_romberg", "algo.integ", "Romberg integral", "رامبرگ", "Romberg", {"f": _p("x**2", "f(x)"), "a": _p("0", "a"), "b": _p("1", "b")}),
        ("alg_quad", "algo.integ", "Adaptive quadrature", "کوادراتور وقتی", "Adaptiivinen kvadratuuri", {"f": _p("x**2", "f(x)"), "a": _p("0", "a"), "b": _p("1", "b")}),
        ("alg_euler", "algo.ode", "Euler ODE", "اویلر", "Euler", {"f": _p("-y", "f(x,y)"), "x0": _p("0", "x0"), "y0": _p("1", "y0"), "x1": _p("1", "x1"), "steps": _p("40", "steps")}),
        ("alg_heun", "algo.ode", "Heun ODE", "هوین", "Heun", {"f": _p("-y", "f(x,y)"), "x0": _p("0", "x0"), "y0": _p("1", "y0"), "x1": _p("1", "x1"), "steps": _p("40", "steps")}),
        ("alg_rk4", "algo.ode", "RK4 ODE", "رانگ کوتا ۴", "RK4", {"f": _p("-y", "f(x,y)"), "x0": _p("0", "x0"), "y0": _p("1", "y0"), "x1": _p("1", "x1"), "steps": _p("40", "steps")}),
        ("alg_rk45", "algo.ode", "RK45 ODE", "رانگ کوتا ۴۵", "RK45", {"f": _p("-y", "f(x,y)"), "x0": _p("0", "x0"), "y0": _p("1", "y0"), "x1": _p("1", "x1")}),
        ("alg_lerp", "algo.interp", "Linear interpolation", "درونیابی خطی", "Lineaarinen interpolointi", {"x0": _p("0", "x0"), "y0": _p("1", "y0"), "x1": _p("2", "x1"), "y1": _p("5", "y1"), "x": _p("1", "x")}),
        ("alg_lagrange", "algo.interp", "Lagrange interpolation", "لاگرانژ", "Lagrange", {"xs": _p("0, 1, 2", "x values"), "ys": _p("1, 2, 5", "y values"), "x": _p("1.5", "x")}),
        ("alg_golden", "algo.opt", "Bounded scalar min", "کمینه روی بازه", "Raja-arvoinen minimi", {"f": _p("(x-2)**2", "f(x)"), "a": _p("0", "a"), "b": _p("4", "b")}),
        ("alg_nelder", "algo.opt", "Nelder-Mead min", "نلدر مید", "Nelder-Mead", {"f": _p("(x-2)**2", "f(x)"), "x0": _p("0", "x0")}),
        ("alg_mean", "algo.stat", "Mean", "میانگین", "Keskiarvo", {"data": _p("1, 2, 3, 4, 5", "data")}),
        ("alg_median", "algo.stat", "Median", "میانه", "Mediaani", {"data": _p("1, 2, 3, 4, 5", "data")}),
        ("alg_var", "algo.stat", "Sample variance", "واریانس نمونه", "Otosvarianssi", {"data": _p("1, 2, 3, 4, 5", "data")}),
        ("alg_std", "algo.stat", "Sample stdev", "انحراف معیار", "Keskihajonta", {"data": _p("1, 2, 3, 4, 5", "data")}),
        ("alg_geomean", "algo.stat", "Geometric mean", "میانگین هندسی", "Geometrinen keskiarvo", {"data": _p("1, 2, 4, 8", "data")}),
        ("alg_rms", "algo.stat", "RMS", "جذر میانگین مربع", "RMS", {"data": _p("3, 4", "data")}),
        ("alg_pct", "algo.stat", "Percentile", "صدک", "Persentiili", {"data": _p("1, 2, 3, 4, 5", "data"), "p": _p("75", "p")}),
        ("alg_linreg", "algo.stat", "Linear regression", "رگرسیون خطی", "Lineaarinen regressio", {"xs": _p("1, 2, 3, 4", "x"), "ys": _p("2, 3, 5, 6", "y")}),
        ("alg_corr", "algo.stat", "Pearson correlation", "همبستگی پیرسون", "Pearson-korrelaatio", {"xs": _p("1, 2, 3, 4", "x"), "ys": _p("2, 3, 5, 6", "y")}),
        ("alg_fft", "algo.signal", "FFT magnitudes", "اندازه تبدیل فوریه", "FFT-suuruudet", {"data": _p("1, 0, -1, 0", "samples")}),
        ("alg_conv", "algo.signal", "Discrete convolution", "پیچش گسسته", "Konvoluutio", {"a": _p("1, 2, 3", "a"), "b": _p("0, 1, 0.5", "b")}),
        ("alg_dist2", "algo.geo", "2D distance", "فاصله دوبعدی", "2D-etaisyys", {"x1": _p("0", "x1"), "y1": _p("0", "y1"), "x2": _p("3", "x2"), "y2": _p("4", "y2")}),
        ("alg_dist3", "algo.geo", "3D distance", "فاصله سه بعدی", "3D-etaisyys", {"x1": _p("0", "x1"), "y1": _p("0", "y1"), "z1": _p("0", "z1"), "x2": _p("1", "x2"), "y2": _p("2", "y2"), "z2": _p("2", "z2")}),
        ("alg_shoelace", "algo.geo", "Shoelace area", "مساحت چندضلعی", "Kenkanauha-ala", {"pts": _p("0,0; 4,0; 4,3; 0,3", "points")}),
        ("alg_heron", "algo.geo", "Heron area", "هرون", "Heron", {"a": _p("3", "a"), "b": _p("4", "b"), "c": _p("5", "c")}),
        ("alg_haversine", "algo.geo", "Haversine distance", "هاورساین", "Haversine", {"lat1": _p("60.17", "lat1"), "lon1": _p("24.94", "lon1"), "lat2": _p("59.33", "lat2"), "lon2": _p("18.07", "lon2"), "r": _p("6371", "R km")}),
        ("alg_base", "algo.convert", "Integer base convert", "تبدیل مبنا", "Kantamuunnos", {"n": _p("255", "digits"), "frm": _p("10", "from base"), "to": _p("16", "to base")}),
    ]
    out = []
    for aid, cat, en, fa, fi, params in items:
        out.append({"id": aid, "category": cat, "name": _nm(en, fa, fi), "params": params})
    return out


def _dist_items() -> list[dict]:
    rows = []
    ops = [
        ("pdf", "PDF", "چگالی", "tiheys", "x", "0"),
        ("cdf", "CDF", "تابع توزیع", "kertymä".replace("ä", "a"), "x", "0"),
        ("ppf", "Quantile PPF", "چندک", "kvantiili", "q", "0.5"),
    ]
    for key, en, fa, fi, extra in DISTS:
        params = {k: _p(val, k) for k, val in extra.items()}
        for op, oen, ofa, ofi, pk, pd in ops:
            p = dict(params)
            p[pk] = _p(pd, pk)
            aid = f"alg_{key}_{op}"
            rows.append(
                {
                    "id": aid,
                    "category": "algo.dist",
                    "name": _nm(f"{en} {oen}", f"{fa} {ofa}", f"{fi} {ofi}"),
                    "params": p,
                    "dist": key,
                    "op": op,
                }
            )
            if op == "pdf":
                RUN[aid] = _r_pdf(key)
            elif op == "cdf":
                RUN[aid] = _r_cdf(key)
            else:
                RUN[aid] = _r_ppf(key)
    return rows


@lru_cache(maxsize=1)
def catalog() -> tuple[dict, list[dict], dict]:
    items = _core_items() + _dist_items()
    index = {row["id"]: row for row in items}
    return CATS, items, index


def list_algos(query: str = "", lang: str = "en", category: str | None = None) -> list[dict]:
    _, rows, _ = catalog()
    q = (query or "").lower().strip()
    out = []
    for row in rows:
        if category and row["category"] != category:
            continue
        blob = " ".join(
            [row["id"], row["category"], row["name"].get(lang, ""), row["name"].get("en", ""), row["name"].get("fa", "")]
        ).lower()
        if not q or q in blob:
            out.append(
                {
                    "id": row["id"],
                    "category": row["category"],
                    "name": row["name"].get(lang) or row["name"]["en"],
                    "params": row["params"],
                    "names": row["name"],
                }
            )
    return out


catalog()


def run_algo(aid: str, values: dict | None = None, eng: bool = False) -> dict:
    try:
        fn = RUN.get(aid)
        if not fn:
            _, _, index = catalog()
            item = index.get(aid)
            if not item:
                return _fail()
            fn = RUN.get(aid)
            if not fn:
                return _fail()
        return fn(values or {}, eng)
    except Exception:
        return _fail()
