"""Turn a result into LaTeX. Independent copy."""

from __future__ import annotations

import re


def from_expr(text: str) -> str:
    raw = (text or "").strip()
    if not raw:
        return ""
    try:
        import sympy as sp
        from sympy.parsing.sympy_parser import parse_expr, standard_transformations

        local = {
            "sin": sp.sin, "cos": sp.cos, "tan": sp.tan, "exp": sp.exp,
            "log": sp.log, "ln": sp.log, "sqrt": sp.sqrt, "pi": sp.pi, "e": sp.E,
            "I": sp.I, "oo": sp.oo,
        }
        expr = parse_expr(raw.replace("^", "**"), local_dict=local, transformations=standard_transformations)
        return sp.latex(expr)
    except Exception:
        s = raw.replace("*", r" \cdot ").replace("**", "^")
        s = re.sub(r"sqrt\(([^)]+)\)", r"\\sqrt{\1}", s)
        return s


def wrap(text: str) -> str:
    body = from_expr(text)
    if not body:
        return ""
    return r"\(" + body + r"\)"


def of_result(text: str, exact: str = "") -> str:
    src = exact or text or ""
    # skip if it is already a long prose line
    if len(src) > 240 or "\n" in src:
        src = (text or "")[:240]
    return from_expr(src)
