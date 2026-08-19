"""Quick lookup for the web app. Does not import the desktop tree."""

from __future__ import annotations

import json
import re
from pathlib import Path

from chemtools import find_element, molar_mass

_FORMULAS = None


def _formulas():
    global _FORMULAS
    if _FORMULAS is None:
        path = Path(__file__).with_name("formulas.json")
        data = json.loads(path.read_text(encoding="utf-8"))
        _FORMULAS = data.get("formulas") or []
    return _FORMULAS


def _num_text(value) -> str:
    try:
        x = float(value)
    except Exception:
        return str(value)
    if abs(x) >= 1e7 or (abs(x) < 1e-4 and x != 0):
        return f"{x:.8g}"
    return f"{x:.8g}"


def _const_rhs(expr: str):
    if "=" not in expr:
        return None
    rhs = expr.split("=", 1)[1].strip()
    if re.fullmatch(r"[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?", rhs):
        try:
            return float(rhs)
        except Exception:
            return None
    return None


def lookup(query: str, lang: str = "en") -> list[dict]:
    q = (query or "").strip()
    if not q:
        return []
    out: list[dict] = []
    seen = set()

    def add(kind, label, text, unit="", extra="", insert=None):
        key = (kind, text, label)
        if key in seen:
            return
        seen.add(key)
        out.append(
            {
                "kind": kind,
                "label": label,
                "text": text,
                "unit": unit,
                "extra": extra,
                "insert": insert if insert is not None else text,
            }
        )

    iso = re.fullmatch(r"([A-Za-z]{1,2})[- ]?(\d{1,3})", q)
    if iso:
        el = find_element(iso.group(1))
        if el:
            a = int(iso.group(2))
            for item in el.get("isotopes") or []:
                if int(item.get("A") or 0) == a:
                    add(
                        "isotope",
                        f"{el['symbol']}-{a}",
                        _num_text(item.get("mass")),
                        "u",
                        item.get("note") or "",
                    )
                    break

    el = find_element(q)
    if el:
        name = el["name"].get(lang) or el["name"]["en"]
        add("element", f"{el['symbol']}  {name}", _num_text(el["mass"]), "g/mol", f"Z = {el['Z']}")
        for item in (el.get("isotopes") or [])[:4]:
            ab = item.get("abundance")
            extra = f"{ab} %" if ab is not None else (item.get("note") or "")
            add(
                "isotope",
                f"{el['symbol']}-{item.get('A')}",
                _num_text(item.get("mass")),
                "u",
                extra,
            )

    if re.search(r"[A-Z]", q) and not q.isdigit() and "-" not in q:
        formula = q.split("=")[0].split("+")[0].strip()
        mw = molar_mass(formula)
        mass = mw.get("mass") or 0
        if mass > 0:
            bits = []
            for sym, info in (mw.get("detail") or {}).items():
                if isinstance(info, dict) and "count" in info:
                    bits.append(f"{sym}{info['count']}")
            add("molar", formula, mw.get("text") or _num_text(mass), "g/mol", " ".join(bits))

    ql = q.lower()
    scored = []
    for item in _formulas():
        name = (item.get("name") or {}).get(lang) or (item.get("name") or {}).get("en") or ""
        blob = " ".join([item.get("id", ""), item.get("category", ""), name, item.get("expr", "")]).lower()
        expr = item.get("expr") or ""
        ident = item.get("id", "").lower()
        namel = name.lower()
        if len(ql) <= 2:
            left = expr.split("=", 1)[0].strip().lower()
            id_ok = ident == ql or ident.startswith(ql + "_") or ident.endswith("_" + ql)
            name_ok = namel == ql or namel.split()[0] == ql
            expr_ok = left == ql
            if not (id_ok or name_ok or expr_ok):
                continue
        elif ql not in blob:
            continue
        score = 0
        if ident == ql:
            score += 50
        if namel == ql:
            score += 40
        if item.get("category", "").startswith("const."):
            score += 20
        if ql in ident:
            score += 8
        scored.append((score, item, name))
    scored.sort(key=lambda row: -row[0])
    for score, item, name in scored[:8]:
        val = _const_rhs(item.get("expr") or "")
        if val is None:
            continue
        unit = ""
        variables = item.get("variables") or {}
        if variables:
            first = next(iter(variables.values()))
            unit = first.get("unit") or ""
        add("const", name, _num_text(val), unit, item.get("expr") or "")

    return out[:12]
