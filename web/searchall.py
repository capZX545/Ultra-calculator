"""Global search across pages, formulas, algorithms, elements, CAS, circuits. Independent copy."""

from __future__ import annotations


PAGES = [
    {"id": "calc", "go": "calc", "en": "Calculator", "fa": "ماشین حساب", "fi": "Laskin", "keys": "keypad eng deg ans history units"},
    {"id": "formulas", "go": "formulas", "en": "Formulas", "fa": "فرمول ها", "fi": "Kaavat", "keys": "formula named equation"},
    {"id": "poly", "go": "poly", "en": "Polynomial", "fa": "چندجمله ای", "fi": "Polynomi", "keys": "roots derivative integral degree"},
    {"id": "numeric", "go": "numeric", "en": "Numerical", "fa": "عددی", "fi": "Numeerinen", "keys": "root integral derivative ode rk4 system"},
    {"id": "algo", "go": "algo", "en": "Algorithms", "fa": "الگوریتم ها", "fi": "Algoritmit", "keys": "gcd fft matrix prime"},
    {"id": "chem", "go": "chem", "en": "Chemistry", "fa": "شیمی", "fi": "Kemia", "keys": "balance molar mass reaction"},
    {"id": "elements", "go": "elements", "en": "Elements", "fa": "عنصرها", "fi": "Alkuaineet", "keys": "periodic isotope"},
    {"id": "sources", "go": "sources", "en": "Sources", "fa": "منبع ها", "fi": "Lahteet", "keys": "nist dlmf"},
    {"id": "problems", "go": "problems", "en": "Problems", "fa": "مسائل", "fi": "Tehtavat", "keys": "solve inverse equation matrix"},
    {"id": "circuits", "go": "circuits", "en": "Circuits", "fa": "مدارها", "fi": "Piirit", "keys": "netlist thevenin diode transistor ac tran spice"},
    {"id": "graph", "go": "graph", "en": "Graph", "fa": "نمودار", "fi": "Kuvaaja", "keys": "plot bode parametric chart"},
    {"id": "matrix", "go": "matrix", "en": "Matrix", "fa": "ماتریس", "fi": "Matriisi", "keys": "det inverse eigenvalues rref solve"},
    {"id": "stats", "go": "stats", "en": "Stats", "fa": "آمار", "fi": "Tilastot", "keys": "mean stdev regression histogram data"},
    {"id": "triangle", "go": "triangle", "en": "Triangle", "fa": "مثلث", "fi": "Kolmio", "keys": "sss sas asa heron sine cosine"},
]

CAS = [
    {"id": "summation", "en": "summation(k, k, 1, n)", "keys": "sum series"},
    {"id": "product", "en": "product(k, k, 1, n)", "keys": "product"},
    {"id": "diff", "en": "diff(f, x)", "keys": "derivative"},
    {"id": "integrate", "en": "integrate(f, x, a, b)", "keys": "integral"},
    {"id": "limit", "en": "limit(f, x, a)", "keys": "limit"},
    {"id": "series", "en": "series(f, x, 0, n)", "keys": "taylor series"},
    {"id": "factor", "en": "factor(expr)", "keys": "factor"},
    {"id": "expand", "en": "expand(expr)", "keys": "expand"},
    {"id": "simplify", "en": "simplify(expr)", "keys": "simplify"},
    {"id": "solveeq", "en": "solveeq(expr, x)", "keys": "solve"},
]

CIR = [
    {"id": "series", "en": "series 1k 2k 3k", "keys": "series resistor"},
    {"id": "parallel", "en": "parallel 1k 1k", "keys": "parallel"},
    {"id": "divider", "en": "divider 12 1k 2k", "keys": "divider"},
    {"id": "thevenin", "en": ".thevenin 2 0", "keys": "thevenin voc rth"},
    {"id": "ac", "en": ".ac 50", "keys": "ac frequency"},
    {"id": "tran", "en": ".tran 1u 2m", "keys": "transient time"},
    {"id": "diode", "en": "D1 1 0", "keys": "diode shockley"},
    {"id": "bjt", "en": "Q1 3 2 0 npn", "keys": "transistor bjt npn"},
    {"id": "mos", "en": "M1 3 2 0 nmos", "keys": "mosfet nmos"},
    {"id": "vcvs", "en": "E1 3 0 1 0 2", "keys": "vcvs opamp"},
]


def _algs():
    try:
        import algorithms
        return algorithms.list_algos("", "en", None)
    except Exception:
        try:
            from . import algorithms
            return algorithms.list_algos("", "en", None)
        except Exception:
            return []


def _forms():
    try:
        import core
        _, rows, _ = core.catalog()
        return rows
    except Exception:
        try:
            from .engine import DesktopEngine
            return DesktopEngine().formulas
        except Exception:
            return []


def _els(q: str):
    try:
        import chemtools
        return chemtools.list_elements(q)[:8]
    except Exception:
        try:
            from .chemtools import list_elements
            return list_elements(q)[:8]
        except Exception:
            return []


def search(query: str, lang: str = "en", favorites: list | None = None) -> dict:
    q = (query or "").strip().lower()
    fav = set()
    for item in favorites or []:
        if isinstance(item, dict):
            fav.add((item.get("kind"), item.get("id")))
        else:
            fav.add(("fav", str(item)))
    hits = []

    def add(kind, iid, title, go, extra=""):
        starred = (kind, iid) in fav
        hits.append({"kind": kind, "id": iid, "title": title, "go": go, "extra": extra, "star": starred})

    if not q:
        for p in PAGES:
            add("page", p["id"], p.get(lang) or p["en"], p["go"])
        return {"ok": True, "hits": hits}

    for p in PAGES:
        blob = " ".join([p["id"], p["en"], p["fa"], p["fi"], p["keys"]]).lower()
        if q in blob:
            add("page", p["id"], p.get(lang) or p["en"], p["go"])
    for c in CAS:
        if q in (c["id"] + " " + c["en"] + " " + c["keys"]).lower():
            add("cas", c["id"], c["en"], "calc", c["en"])
    for c in CIR:
        if q in (c["id"] + " " + c["en"] + " " + c["keys"]).lower():
            add("circuit", c["id"], c["en"], "circuits", c["en"])
    try:
        for el in _els(query):
            name = (el.get("name") or {}).get(lang) or (el.get("name") or {}).get("en") or el.get("symbol")
            add("element", el.get("symbol"), f"{el.get('Z')}  {el.get('symbol')}  {name}", "elements", str(el.get("mass")))
    except Exception:
        pass
    try:
        for row in _algs():
            name = row.get("name") or ""
            blob = " ".join([row.get("id") or "", name, row.get("category") or ""]).lower()
            if q in blob:
                add("algo", row.get("id"), name, "algo")
                if sum(1 for h in hits if h["kind"] == "algo") >= 8:
                    break
    except Exception:
        pass
    try:
        nform = 0
        for row in _forms():
            name = (row.get("name") or {}).get(lang) or (row.get("name") or {}).get("en") or ""
            blob = " ".join([row.get("id") or "", row.get("category") or "", name, row.get("expr") or ""]).lower()
            if q in blob:
                add("formula", row.get("id"), name, "formulas", row.get("expr") or "")
                nform += 1
                if nform >= 12:
                    break
    except Exception:
        pass
    # favorites on top
    hits.sort(key=lambda h: (0 if h.get("star") else 1))
    return {"ok": True, "hits": hits[:40]}
