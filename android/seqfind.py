"""Identify sequence types and return their formulas. Independent copy."""

from __future__ import annotations

import math
import re


def _nm(en, fa, fi):
    return {"en": en, "fa": fa, "fi": fi}


TYPES = [
    {
        "id": "arith",
        "name": _nm("Arithmetic", "حسابی (خطی)", "Aritmeettinen"),
        "formula": "a_n = a1 + (n - 1)*d",
        "note": _nm("Constant difference d.", "اختلاف مشترک d ثابت است.", "Vakioerotus d."),
    },
    {
        "id": "geo",
        "name": _nm("Geometric", "هندسی", "Geometrinen"),
        "formula": "a_n = a1 * r**(n - 1)",
        "note": _nm("Constant ratio r.", "نسبت مشترک r ثابت است.", "Vakiosuhde r."),
    },
    {
        "id": "harm",
        "name": _nm("Harmonic", "همساز", "Harmoninen"),
        "formula": "1/a_n = 1/a1 + (n - 1)*d",
        "note": _nm("Reciprocals form an arithmetic sequence.", "معکوس جمله‌ها حسابی است.", "Kaanteisluvut muodostavat aritmeettisen jonon."),
    },
    {
        "id": "quad",
        "name": _nm("Quadratic", "درجه دو", "Toisen asteen"),
        "formula": "a_n = p*n**2 + q*n + r0",
        "note": _nm("Second differences are constant.", "اختلاف دوم ثابت است.", "Toiset erotukset ovat vakiot."),
    },
    {
        "id": "cubic",
        "name": _nm("Cubic", "درجه سه", "Kolmannen asteen"),
        "formula": "a_n = A*n**3 + B*n**2 + C*n + D",
        "note": _nm("Third differences are constant.", "اختلاف سوم ثابت است.", "Kolmannet erotukset ovat vakiot."),
    },
    {
        "id": "fib",
        "name": _nm("Fibonacci-like", "شبیه فیبوناچی", "Fibonaccin kaltainen"),
        "formula": "a_n = a_(n-1) + a_(n-2)",
        "note": _nm("Each term is the sum of the two before it.", "هر جمله جمع دو جملهٔ قبلی است.", "Jokainen termi on kahden edellisen summa."),
    },
    {
        "id": "recur2",
        "name": _nm("Linear recurrence order 2", "بازگشتی خطی مرتبه ۲", "Lineaarinen rekursio, jarjestys 2"),
        "formula": "a_n = p*a_(n-1) + q*a_(n-2)",
        "note": _nm("Constant coefficients p, q.", "ضریب‌های p و q ثابت‌اند.", "Vakiokertoimet p, q."),
    },
    {
        "id": "const",
        "name": _nm("Constant", "ثابت", "Vakio"),
        "formula": "a_n = c",
        "note": _nm("Every term is the same.", "همهٔ جمله‌ها یکی‌اند.", "Kaikki termit ovat samat."),
    },
    {
        "id": "square",
        "name": _nm("Square numbers", "مربع کامل", "Nelioluvut"),
        "formula": "a_n = n**2",
        "note": _nm("1, 4, 9, 16, …", "۱، ۴، ۹، ۱۶، …", "1, 4, 9, 16, …"),
    },
    {
        "id": "cube",
        "name": _nm("Cubes", "مکعب کامل", "Kuutioluvut"),
        "formula": "a_n = n**3",
        "note": _nm("1, 8, 27, 64, …", "۱، ۸، ۲۷، ۶۴، …", "1, 8, 27, 64, …"),
    },
    {
        "id": "tri",
        "name": _nm("Triangular", "مثلثی", "Kolmioluvut"),
        "formula": "a_n = n*(n + 1)/2",
        "note": _nm("1, 3, 6, 10, 15, …", "۱، ۳، ۶، ۱۰، ۱۵، …", "1, 3, 6, 10, 15, …"),
    },
    {
        "id": "fact",
        "name": _nm("Factorial", "فاکتوریل", "Kertoma"),
        "formula": "a_n = n!",
        "note": _nm("1, 2, 6, 24, 120, …", "۱، ۲، ۶، ۲۴، ۱۲۰، …", "1, 2, 6, 24, 120, …"),
    },
    {
        "id": "power",
        "name": _nm("Powers of a base", "توان‌های یک پایه", "Kannan potenssit"),
        "formula": "a_n = b**n   or   a_n = a1 * b**(n-1)",
        "note": _nm("Same as geometric with integer ratio.", "همان هندسی با نسبت درست است.", "Sama kuin geometrinen kokonaislukusuhteella."),
    },
]


def list_types(lang: str = "en"):
    out = []
    for t in TYPES:
        out.append(
            {
                "id": t["id"],
                "name": t["name"].get(lang) or t["name"]["en"],
                "formula": t["formula"],
                "note": t["note"].get(lang) or t["note"]["en"],
            }
        )
    return out


_PERSIAN = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")


def _pretty(x):
    try:
        v = float(x)
    except Exception:
        return str(x)
    if not math.isfinite(v):
        return "undefined"
    if abs(v) < 1e-12:
        return "0"
    if abs(v - round(v)) < 1e-10:
        return str(int(round(v)))
    if abs(v) >= 1e7 or (abs(v) < 1e-4 and v != 0):
        return f"{v:.8g}"
    return f"{v:.12g}"


def _num(tok):
    t = str(tok).strip().translate(_PERSIAN).replace("×", "*").replace("−", "-").replace("–", "-")
    t = t.replace(" ", "")
    if not t:
        return None
    t = t.replace(",", ".")
    if "/" in t and t.count("/") == 1:
        a, b = t.split("/")
        try:
            den = float(b)
            if abs(den) < 1e-15:
                return None
            return float(a) / den
        except Exception:
            return None
    try:
        return float(t)
    except Exception:
        return None


def parse_terms(text: str):
    raw = (text or "").strip().translate(_PERSIAN)
    if not raw:
        return []
    raw = raw.replace("،", " ").replace(";", " ").replace("|", " ").replace("\t", " ")
    raw = raw.replace("−", "-").replace("–", "-")
    parts = re.split(r"[\s,]+", raw)
    out = []
    for p in parts:
        v = _num(p)
        if v is None:
            continue
        out.append(v)
    return out


def _close(a, b, tol=1e-8):
    if a is None or b is None:
        return False
    try:
        a = float(a)
        b = float(b)
    except Exception:
        return False
    if not (math.isfinite(a) and math.isfinite(b)):
        return False
    scale = max(1.0, abs(a), abs(b))
    return abs(a - b) <= tol * scale


def _const_diff(vals):
    if len(vals) < 2:
        return None
    d = vals[1] - vals[0]
    for i in range(2, len(vals)):
        if not _close(vals[i] - vals[i - 1], d):
            return None
    return d


def _const_ratio(vals):
    if len(vals) < 2:
        return None
    if any(abs(v) < 1e-15 for v in vals[:-1]) and not all(abs(v) < 1e-15 for v in vals):
        # zero then nonzero is not geometric
        if abs(vals[0]) < 1e-15:
            return None
    if abs(vals[0]) < 1e-15:
        return None
    r = vals[1] / vals[0]
    for i in range(2, len(vals)):
        if abs(vals[i - 1]) < 1e-15:
            if abs(vals[i]) > 1e-15:
                return None
            continue
        if not _close(vals[i] / vals[i - 1], r):
            return None
    return r


def _poly_from_diffs(vals, degree):
    """Newton forward differences, nodes 1..n, return coeffs of p(n) in monomials if exact."""
    n = len(vals)
    if n < degree + 1:
        return None
    table = [list(vals)]
    for k in range(1, degree + 1):
        prev = table[-1]
        nxt = [prev[i + 1] - prev[i] for i in range(len(prev) - 1)]
        table.append(nxt)
    # remaining first diffs of last row must be ~0
    last = table[-1]
    lead = last[0]
    for x in last[1:]:
        if not _close(x, lead):
            return None
    # Newton basis: f(1+s) = c0 + C(s,1)c1 + C(s,2)c2 + ...
    # s = n-1
    # convert to monomials in n
    # Use evaluation fit on 1..degree+1
    m = degree + 1
    A = []
    b = []
    for i in range(m):
        ni = i + 1
        A.append([ni**p for p in range(m)])
        b.append(vals[i])
    coef = _solve_lin(A, b)
    if coef is None:
        return None
    # verify rest
    for i, v in enumerate(vals):
        ni = i + 1
        pred = 0.0
        for p, c in enumerate(coef):
            pred += c * (ni**p)
        if not _close(pred, v):
            return None
    return coef


def _solve_lin(A, b):
    n = len(A)
    M = [A[i][:] + [b[i]] for i in range(n)]
    for i in range(n):
        piv = i
        for r in range(i + 1, n):
            if abs(M[r][i]) > abs(M[piv][i]):
                piv = r
        if abs(M[piv][i]) < 1e-12:
            return None
        M[i], M[piv] = M[piv], M[i]
        fac = M[i][i]
        for c in range(i, n + 1):
            M[i][c] /= fac
        for r in range(n):
            if r == i:
                continue
            f = M[r][i]
            for c in range(i, n + 1):
                M[r][c] -= f * M[i][c]
    return [M[i][n] for i in range(n)]


def _eval_poly(coef, n):
    s = 0.0
    for p, c in enumerate(coef):
        s += c * (n**p)
    return s


def _poly_formula(coef):
    parts = []
    for p in range(len(coef) - 1, -1, -1):
        c = coef[p]
        if abs(c) < 1e-10:
            continue
        cs = _pretty(c)
        if p == 0:
            parts.append(cs)
        elif p == 1:
            if _close(c, 1):
                parts.append("n")
            elif _close(c, -1):
                parts.append("-n")
            else:
                parts.append(cs + "*n")
        else:
            if _close(c, 1):
                parts.append("n**" + str(p))
            elif _close(c, -1):
                parts.append("-n**" + str(p))
            else:
                parts.append(cs + "*n**" + str(p))
    if not parts:
        return "0"
    out = parts[0]
    for p in parts[1:]:
        if p.startswith("-"):
            out += " - " + p[1:]
        else:
            out += " + " + p
    return "a_n = " + out


def _next_from(fn, start, k, already):
    out = []
    n = start
    while len(out) < k:
        out.append(fn(n))
        n += 1
    return out


def _T(lang):
    if lang == "fa":
        return {
            "need": "حداقل دو عدد بنویس، مثلاً ۲ ۵ ۸ ۱۱ یا ۳، ۶، ۱۲، ۲۴.",
            "none": "با این جمله‌ها نوع مشخصی پیدا نشد.",
            "type": "نوع",
            "formula": "فرمول",
            "params": "پارامترها",
            "next": "جمله‌های بعدی",
            "given": "جمله‌های داده‌شده",
            "d": "اختلاف مشترک d",
            "r": "نسبت مشترک r",
            "a1": "جمله اول a1",
            "sum": "جمع n جملهٔ اول",
        }
    if lang == "fi":
        return {
            "need": "Kirjoita vahintaan kaksi lukua, esim. 2 5 8 11.",
            "none": "Tunnistettavaa jonoa ei loytynyt.",
            "type": "Tyyppi",
            "formula": "Kaava",
            "params": "Parametrit",
            "next": "Seuraavat termit",
            "given": "Annetut termit",
            "d": "Erotus d",
            "r": "Suhde r",
            "a1": "Ensimmainen termi a1",
            "sum": "n ensimmaisen summa",
        }
    return {
        "need": "Enter at least two numbers, e.g. 2 5 8 11 or 3, 6, 12, 24.",
        "none": "No standard sequence type matched these terms.",
        "type": "Type",
        "formula": "Formula",
        "params": "Parameters",
        "next": "Next terms",
        "given": "Given terms",
        "d": "Common difference d",
        "r": "Common ratio r",
        "a1": "First term a1",
        "sum": "Sum of the first n terms",
    }


def _hit(tid, lang, formula, params, nxt, steps, extra=None):
    meta = next((t for t in TYPES if t["id"] == tid), None)
    name = (meta["name"].get(lang) or meta["name"]["en"]) if meta else tid
    row = {
        "id": tid,
        "name": name,
        "formula": formula,
        "params": params,
        "next": nxt,
        "steps": steps,
    }
    if extra:
        row.update(extra)
    return row


def identify(vals, lang="en", n_next=5):
    T = _T(lang)
    hits = []
    n_next = max(1, min(int(n_next or 5), 20))
    k = len(vals)
    if k < 2:
        return hits

    # constant
    if all(_close(v, vals[0]) for v in vals):
        c = vals[0]
        hits.append(
            _hit(
                "const",
                lang,
                "a_n = " + _pretty(c),
                {"c": _pretty(c)},
                [_pretty(c)] * n_next,
                [T["type"] + ": constant", "a_n = " + _pretty(c)],
            )
        )

    # arithmetic
    d = _const_diff(vals)
    if d is not None and not all(_close(v, vals[0]) for v in vals):
        a1 = vals[0]
        nxt = [a1 + (k + i) * d for i in range(n_next)]
        steps = [
            f"a1 = {_pretty(a1)}",
            f"d = {_pretty(d)}",
            "a_n = a1 + (n - 1)*d",
        ]
        extra = {}
        # sum of first n given terms
        s = k * (2 * a1 + (k - 1) * d) / 2
        extra["sum_given"] = _pretty(s)
        extra["sum_formula"] = "S_n = n*(2*a1 + (n-1)*d)/2"
        hits.append(_hit("arith", lang, "a_n = a1 + (n - 1)*d", {"a1": _pretty(a1), "d": _pretty(d)}, [_pretty(x) for x in nxt], steps, extra))

    # geometric
    r = _const_ratio(vals)
    if r is not None and not all(_close(v, vals[0]) for v in vals):
        a1 = vals[0]
        nxt = [a1 * (r ** (k + i)) for i in range(n_next)]
        steps = [f"a1 = {_pretty(a1)}", f"r = {_pretty(r)}", "a_n = a1 * r**(n - 1)"]
        extra = {"sum_formula": "S_n = a1*(r**n - 1)/(r - 1)   (r != 1)"}
        if abs(r - 1) < 1e-15:
            extra["sum_given"] = _pretty(k * a1)
        else:
            extra["sum_given"] = _pretty(a1 * (r**k - 1) / (r - 1))
        hits.append(
            _hit(
                "geo",
                lang,
                "a_n = a1 * r**(n - 1)",
                {"a1": _pretty(a1), "r": _pretty(r)},
                [_pretty(x) for x in nxt],
                steps,
                extra,
            )
        )

    # harmonic
    if all(abs(v) > 1e-15 for v in vals):
        inv = [1.0 / v for v in vals]
        dh = _const_diff(inv)
        if dh is not None and not all(_close(v, inv[0]) for v in inv):
            a1 = vals[0]
            nxt = []
            for i in range(n_next):
                den = inv[0] + (k + i) * dh
                nxt.append("undefined" if abs(den) < 1e-15 else _pretty(1.0 / den))
            steps = ["1/a_n arithmetic", f"1/a1 = {_pretty(inv[0])}", f"d = {_pretty(dh)}"]
            hits.append(_hit("harm", lang, "1/a_n = 1/a1 + (n - 1)*d", {"a1": _pretty(a1), "d": _pretty(dh)}, nxt, steps))

    # squares / cubes / triangular / factorial — only if they match from n=1
    if k >= 3:
        if all(_close(vals[i], (i + 1) ** 2) for i in range(k)):
            nxt = [_pretty((k + i + 1) ** 2) for i in range(n_next)]
            hits.append(_hit("square", lang, "a_n = n**2", {"start": "n = 1"}, nxt, ["a_n = n**2"]))
        if all(_close(vals[i], (i + 1) ** 3) for i in range(k)):
            nxt = [_pretty((k + i + 1) ** 3) for i in range(n_next)]
            hits.append(_hit("cube", lang, "a_n = n**3", {"start": "n = 1"}, nxt, ["a_n = n**3"]))
        if all(_close(vals[i], (i + 1) * (i + 2) / 2) for i in range(k)):
            nxt = [_pretty((k + i + 1) * (k + i + 2) / 2) for i in range(n_next)]
            hits.append(_hit("tri", lang, "a_n = n*(n + 1)/2", {"start": "n = 1"}, nxt, ["a_n = n*(n + 1)/2"]))
        facts = []
        f = 1
        for i in range(1, k + 1 + n_next + 2):
            f *= i
            facts.append(f)
        if all(_close(vals[i], facts[i]) for i in range(k)):
            nxt = [_pretty(facts[k + i]) for i in range(n_next)]
            hits.append(_hit("fact", lang, "a_n = n!", {"start": "n = 1"}, nxt, ["a_n = n!"]))

    simple = {h["id"] for h in hits}
    # quadratic / cubic via finite differences (need one extra term so it is not just interpolation)
    if k >= 4 and not simple.intersection({"arith", "const", "geo", "square", "tri"}):
        coef = _poly_from_diffs(vals, 2)
        if coef is not None:
            nxt = [_pretty(_eval_poly(coef, k + i + 1)) for i in range(n_next)]
            params = {
                "r0": _pretty(coef[0]),
                "q": _pretty(coef[1]) if len(coef) > 1 else "0",
                "p": _pretty(coef[2]) if len(coef) > 2 else "0",
            }
            hits.append(_hit("quad", lang, _poly_formula(coef), params, nxt, ["second differences constant", _poly_formula(coef)]))
    if k >= 5 and not {h["id"] for h in hits}.intersection({"arith", "const", "geo", "quad", "cube", "square", "tri", "fact"}):
        coef = _poly_from_diffs(vals, 3)
        if coef is not None:
            nxt = [_pretty(_eval_poly(coef, k + i + 1)) for i in range(n_next)]
            hits.append(
                _hit(
                    "cubic",
                    lang,
                    _poly_formula(coef),
                    {"D": _pretty(coef[0]), "C": _pretty(coef[1]), "B": _pretty(coef[2]), "A": _pretty(coef[3])},
                    nxt,
                    ["third differences constant", _poly_formula(coef)],
                )
            )

    # Fibonacci-like
    if k >= 3:
        ok = True
        for i in range(2, k):
            if not _close(vals[i], vals[i - 1] + vals[i - 2]):
                ok = False
                break
        if ok:
            nxt = []
            a, b = vals[-2], vals[-1]
            for _ in range(n_next):
                a, b = b, a + b
                nxt.append(_pretty(b))
            hits.append(_hit("fib", lang, "a_n = a_(n-1) + a_(n-2)", {"a1": _pretty(vals[0]), "a2": _pretty(vals[1])}, nxt, ["a_n = a_(n-1) + a_(n-2)"]))

    # order-2 recurrence a_n = p a_{n-1} + q a_{n-2}
    if k >= 5 and not {h["id"] for h in hits}.intersection({"fib", "arith", "geo", "const", "harm"}):
        # from first 4: a3 = p a2 + q a1, a4 = p a3 + q a2
        a1, a2, a3, a4 = vals[0], vals[1], vals[2], vals[3]
        det = a2 * a2 - a3 * a1
        if abs(det) > 1e-12:
            p = (a3 * a2 - a4 * a1) / det
            q = (a2 * a4 - a3 * a3) / det
            ok = True
            for i in range(2, k):
                if not _close(vals[i], p * vals[i - 1] + q * vals[i - 2]):
                    ok = False
                    break
            if ok and not (_close(p, 1) and _close(q, 1)):
                nxt = []
                x, y = vals[-2], vals[-1]
                for _ in range(n_next):
                    x, y = y, p * y + q * x
                    nxt.append(_pretty(y))
                hits.append(
                    _hit(
                        "recur2",
                        lang,
                        "a_n = p*a_(n-1) + q*a_(n-2)",
                        {"p": _pretty(p), "q": _pretty(q), "a1": _pretty(vals[0]), "a2": _pretty(vals[1])},
                        nxt,
                        [f"p = {_pretty(p)}", f"q = {_pretty(q)}", "a_n = p*a_(n-1) + q*a_(n-2)"],
                    )
                )

    # unique by id, prefer more specific first
    seen = set()
    uniq = []
    for h in hits:
        if h["id"] in seen:
            continue
        seen.add(h["id"])
        uniq.append(h)
    return uniq


def run(text="", lang="en", n_next=5):
    try:
        T = _T(lang)
        vals = parse_terms(text)
        types = list_types(lang)
        if len(vals) < 2:
            return {
                "ok": True,
                "text": T["need"],
                "hits": [],
                "terms": [],
                "types": types,
                "steps": [T["need"]],
            }
        hits = identify(vals, lang, n_next)
        if not hits:
            shown = ", ".join(_pretty(v) for v in vals)
            return {
                "ok": True,
                "text": T["none"],
                "hits": [],
                "terms": [_pretty(v) for v in vals],
                "types": types,
                "steps": [T["given"] + ": " + shown, T["none"]],
            }
        lines = [T["given"] + ": " + ", ".join(_pretty(v) for v in vals)]
        for h in hits:
            lines.append(T["type"] + ": " + h["name"])
            lines.append(T["formula"] + ": " + h["formula"])
            if h.get("params"):
                bits = [f"{k} = {v}" for k, v in h["params"].items()]
                lines.append(T["params"] + ": " + ", ".join(bits))
            if h.get("next"):
                lines.append(T["next"] + ": " + ", ".join(str(x) for x in h["next"]))
            if h.get("sum_formula"):
                lines.append(T["sum"] + ": " + h["sum_formula"])
            lines.append("")
        text_out = "\n".join(lines).strip()
        return {
            "ok": True,
            "text": text_out,
            "hits": hits,
            "terms": [_pretty(v) for v in vals],
            "types": types,
            "steps": lines,
        }
    except Exception:
        return {"ok": True, "text": "0", "hits": [], "terms": [], "types": list_types(lang), "steps": []}
