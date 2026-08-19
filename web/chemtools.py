"""Chemistry tools for the web app. Independent of the desktop tree."""

from __future__ import annotations

import json
import re
from fractions import Fraction
from functools import reduce
from math import gcd
from pathlib import Path


def _load_table():
    path = Path(__file__).with_name("elements.json")
    data = json.loads(path.read_text(encoding="utf-8"))
    by_sym = {el["symbol"]: el for el in data["elements"]}
    by_z = {el["Z"]: el for el in data["elements"]}
    by_name = {}
    for el in data["elements"]:
        for lang, name in el["name"].items():
            by_name[name.lower()] = el
        by_name[el["symbol"].lower()] = el
    return data["elements"], by_sym, by_z, by_name


ELEMENTS, BY_SYM, BY_Z, BY_NAME = _load_table()


def find_element(query: str):
    q = (query or "").strip()
    if not q:
        return None
    if q.isdigit():
        return BY_Z.get(int(q))
    if q in BY_SYM:
        return BY_SYM[q]
    return BY_NAME.get(q.lower())


def list_elements(query: str = ""):
    q = (query or "").strip().lower()
    out = []
    for el in ELEMENTS:
        blob = " ".join([el["symbol"], str(el["Z"]), el["name"]["en"], el["name"]["fa"], el["name"]["fi"]]).lower()
        if not q or q in blob:
            out.append(el)
    return out


_TOKEN = re.compile(r"([A-Z][a-z]?|\(|\)|\d+)")


def parse_formula(formula: str) -> dict[str, int]:
    text = (formula or "").strip().replace("[", "(").replace("]", ")")
    text = re.sub(r"\s+", "", text)
    if not text:
        return {}
    tokens = _TOKEN.findall(text)
    stack = [ {} ]

    def merge(dest, src, mult=1):
        for k, v in src.items():
            dest[k] = dest.get(k, 0) + v * mult

    i = 0
    while i < len(tokens):
        tok = tokens[i]
        if tok == "(":
            stack.append({})
            i += 1
        elif tok == ")":
            group = stack.pop()
            if not stack:
                stack = [{}]
            i += 1
            mult = 1
            if i < len(tokens) and tokens[i].isdigit():
                mult = int(tokens[i])
                i += 1
            merge(stack[-1], group, mult)
        elif tok[0].isalpha():
            i += 1
            mult = 1
            if i < len(tokens) and tokens[i].isdigit():
                mult = int(tokens[i])
                i += 1
            stack[-1][tok] = stack[-1].get(tok, 0) + mult
        else:
            i += 1
    return stack[0]


def molar_mass(formula: str) -> dict:
    try:
        counts = parse_formula(formula)
        if not counts:
            return {"ok": True, "mass": 0.0, "text": "0", "detail": {}}
        total = 0.0
        detail = {}
        for sym, n in counts.items():
            el = BY_SYM.get(sym)
            if not el:
                return {"ok": True, "mass": 0.0, "text": "0", "detail": {"unknown": sym}}
            piece = el["mass"] * n
            total += piece
            detail[sym] = {"count": n, "mass": el["mass"], "contrib": piece}
        return {"ok": True, "mass": total, "text": f"{total:.5g}", "detail": detail, "counts": counts}
    except Exception:
        return {"ok": True, "mass": 0.0, "text": "0", "detail": {}}


def _split_side(side: str):
    parts = re.split(r"\+", side)
    return [p.strip() for p in parts if p.strip()]


def balance_equation(raw: str) -> dict:
    try:
        text = (raw or "").replace("→", "=").replace("->", "=").replace("=>", "=")
        if "=" not in text:
            return {"ok": True, "text": raw or "", "coeffs": []}
        left_s, right_s = text.split("=", 1)
        left = _split_side(left_s)
        right = _split_side(right_s)
        species = left + right
        if not species:
            return {"ok": True, "text": "", "coeffs": []}
        parsed = [parse_formula(s) for s in species]
        elems = sorted({e for p in parsed for e in p})
        n = len(species)
        m = len(elems)
        if m == 0 or n == 0:
            return {"ok": True, "text": " + ".join(left) + " = " + " + ".join(right), "coeffs": [1] * n}
        # rows elements, cols species; products negative
        A = []
        for e in elems:
            row = []
            for i, p in enumerate(parsed):
                sign = 1 if i < len(left) else -1
                row.append(sign * p.get(e, 0))
            A.append(row)
        # integer null space via Fraction Gaussian
        mat = [[Fraction(A[r][c]) for c in range(n)] for r in range(m)]
        # augment with identity for kernel extraction: solve A x = 0
        # RREF
        rows, cols = m, n
        r = 0
        pivot_cols = []
        for c in range(cols):
            piv = None
            for i in range(r, rows):
                if mat[i][c] != 0:
                    piv = i
                    break
            if piv is None:
                continue
            mat[r], mat[piv] = mat[piv], mat[r]
            div = mat[r][c]
            mat[r] = [x / div for x in mat[r]]
            for i in range(rows):
                if i == r:
                    continue
                fac = mat[i][c]
                if fac != 0:
                    mat[i] = [mat[i][j] - fac * mat[r][j] for j in range(cols)]
            pivot_cols.append(c)
            r += 1
            if r == rows:
                break
        free = [c for c in range(cols) if c not in pivot_cols]
        if not free:
            free = [cols - 1]
        vec = [Fraction(0)] * cols
        vec[free[0]] = Fraction(1)
        # back-sub from RREF: for each pivot row, x_p = -sum a_free * x_free
        for i, pc in enumerate(pivot_cols):
            s = Fraction(0)
            for c in range(cols):
                if c != pc:
                    s += mat[i][c] * vec[c]
            vec[pc] = -s
        # if all zero, ones
        if all(x == 0 for x in vec):
            vec = [Fraction(1)] * cols
        # make positive if possible
        if sum(1 for x in vec if x < 0) > sum(1 for x in vec if x > 0):
            vec = [-x for x in vec]
        dens = [x.denominator for x in vec]
        lcm = reduce(lambda a, b: a * b // gcd(a, b), dens, 1)
        ints = [int(x * lcm) for x in vec]
        g = reduce(gcd, (abs(k) for k in ints if k), 1) or 1
        ints = [k // g for k in ints]
        if any(k <= 0 for k in ints):
            ints = [abs(k) or 1 for k in ints]
        def fmt(names, coeffs):
            bits = []
            for name, c in zip(names, coeffs):
                bits.append(name if c == 1 else f"{c} {name}")
            return " + ".join(bits)
        out = fmt(left, ints[: len(left)]) + " = " + fmt(right, ints[len(left) :])
        return {"ok": True, "text": out, "coeffs": ints, "species": species}
    except Exception:
        return {"ok": True, "text": raw or "", "coeffs": []}
