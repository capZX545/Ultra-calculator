"""API used by the phone WebView. Independent of desktop and web servers."""

from __future__ import annotations

import json

import algorithms
import chemtools
import core
import lookup
import circuits
import circguide
import seqfind
import problems
import graphs
import matrixlab
import statsdata
import triangle
import searchall
import sessionstore
import latexout
import strings
import teach


def handle(raw: str) -> str:
    try:
        req = json.loads(raw or "{}")
    except Exception:
        return json.dumps({})
    path = req.get("path") or ""
    query = req.get("query") or {}
    body = req.get("body") or {}
    try:
        out = _route(path, query, body)
    except Exception:
        out = {"ok": True, "text": "0"}
    return json.dumps(out)


def _q(query, key, default=""):
    v = query.get(key, default)
    if isinstance(v, list):
        return v[0] if v else default
    return v if v is not None else default


def _route(path, query, body):
    if path == "/api/meta":
        lang = _q(query, "lang", "en")
        cats, rows, _ = core.catalog()
        counts = {}
        for row in rows:
            key = row.get("category") or ""
            counts[key] = counts.get(key, 0) + 1
        labeled = []
        for key, names in sorted(cats.items()):
            labeled.append(
                {
                    "id": key,
                    "label": names.get(lang) or names.get("en"),
                    "count": int(counts.get(key, 0)),
                }
            )
        return {
            "strings": strings.UI.get(lang) or strings.UI["en"],
            "categories": labeled,
            "total": len(rows),
            "languages": ["en", "fa", "fi"],
        }
    if path == "/api/formulas":
        return core.list_formulas(_q(query, "q"), _q(query, "lang", "en"), _q(query, "category") or None)
    if path == "/api/eval":
        return core.eval_line(
            body.get("expr", "0"),
            angle=body.get("angle", "DEG"),
            eng=bool(body.get("eng")),
            ans=body.get("ans", 0),
            lang=body.get("lang", "en"),
        )
    if path == "/api/solve":
        return core.solve_named(
            body.get("id"),
            body.get("values") or {},
            unknown=body.get("unknown"),
            eng=bool(body.get("eng")),
            lang=body.get("lang", "en"),
        )
    if path == "/api/system":
        return core.solve_many(
            body.get("equations") or ["x=0"],
            body.get("unknowns") or ["x"],
            eng=bool(body.get("eng")),
            lang=body.get("lang", "en"),
        )
    if path == "/api/poly":
        out = core.poly_work(body.get("coeffs") or [0] * 7, body.get("x"), bool(body.get("eng")))
        lang = body.get("lang", "en")
        if body.get("x") is None:
            out["steps"] = teach.steps_poly(lang, "roots", None, "", out.get("degree"), out.get("roots") or [])
        else:
            out["steps"] = teach.steps_poly(lang, "eval", body.get("x"), out.get("value_text") or "0", out.get("degree"), None)
        return out
    if path == "/api/numeric":
        kind = body.get("kind", "root")
        func = body.get("func", "x")
        a = float(body.get("a") or 0)
        b = float(body.get("b") or 1)
        y0 = float(body.get("y0") or 0)
        steps = int(body.get("steps") or 40)
        eng = bool(body.get("eng"))
        lang = body.get("lang", "en")
        if kind == "integral":
            out = core.n_integral(func, a, b, eng)
            out["steps"] = teach.steps_numeric(lang, "integral", a, b, None, out.get("text") or "0")
            return out
        if kind == "deriv":
            out = core.n_deriv(func, a, eng)
            out["steps"] = teach.steps_numeric(lang, "deriv", a, None, None, out.get("text") or "0")
            return out
        if kind == "ode":
            out = core.n_ode(func, a, y0, b, steps, eng)
            out["steps"] = teach.steps_numeric(lang, "ode", a, b, y0, out.get("text") or "0")
            return out
        out = core.n_root(func, a, b, eng)
        out["steps"] = teach.steps_numeric(lang, "root", a, b, None, out.get("text") or "0")
        return out
    if path == "/api/elements":
        lang = _q(query, "lang", "en")
        rows = []
        for el in chemtools.list_elements(_q(query, "q")):
            rows.append(
                {
                    "Z": el["Z"],
                    "symbol": el["symbol"],
                    "name": el["name"].get(lang) or el["name"]["en"],
                    "mass": el["mass"],
                    "group": el["group"],
                    "isotopes": el["isotopes"],
                    "names": el["name"],
                }
            )
        return rows
    if path == "/api/balance":
        out = chemtools.balance_equation(body.get("eq", ""))
        out["steps"] = teach.steps_chem(body.get("lang", "en"), body.get("eq", ""), out.get("text") or "", False)
        return out
    if path == "/api/molar":
        out = chemtools.molar_mass(body.get("formula", ""))
        out["steps"] = teach.steps_chem(body.get("lang", "en"), body.get("formula", ""), out.get("text") or "0", True)
        return out
    if path == "/api/algos":
        lang = _q(query, "lang", "en")
        cats, items, _ = algorithms.catalog()
        counts = {}
        for row in items:
            key = row.get("category") or ""
            counts[key] = counts.get(key, 0) + 1
        labeled = [
            {"id": key, "label": names.get(lang) or names.get("en"), "count": int(counts.get(key, 0))}
            for key, names in sorted(cats.items())
        ]
        return {
            "categories": labeled,
            "total": len(items),
            "items": algorithms.list_algos(_q(query, "q"), lang, _q(query, "category") or None),
        }
    if path == "/api/algo":
        return algorithms.run_algo(body.get("id"), body.get("values") or {}, eng=bool(body.get("eng")))
    if path == "/api/lookup":
        return lookup.lookup(_q(query, "q"), _q(query, "lang", "en"))
    if path == "/api/sources":
        from pathlib import Path

        return json.loads(Path("sources.json").read_text(encoding="utf-8"))
    if path == "/api/problem":
        return problems.run(
            body.get("text") or "",
            mode=body.get("mode") or "solve",
            unknown=body.get("unknown") or "x",
            at=body.get("at") or "",
            lang=body.get("lang") or "en",
            eng=bool(body.get("eng")),
        )
    if path == "/api/circguide":
        return circguide.run(body)
    if path == "/api/seqfind":
        return seqfind.run(body.get("text") or "", lang=body.get("lang") or "en", n_next=body.get("n_next") or 5)
    if path == "/api/circuit":
        return circuits.run(
            body.get("text") or "",
            mode=body.get("mode") or "solve",
            freq=body.get("freq") or "",
            lang=body.get("lang") or "en",
            eng=bool(body.get("eng")),
        )
    if path == "/api/graph":
        return graphs.run(
            kind=body.get("kind") or "func",
            funcs=body.get("funcs") or body.get("text") or "sin(x)",
            xmin=str(body.get("xmin") or "-10"),
            xmax=str(body.get("xmax") or "10"),
            tmin=str(body.get("tmin") or "0"),
            tmax=str(body.get("tmax") or "6.2832"),
            data=body.get("data") or "",
            circuit=body.get("circuit") or "",
            node=str(body.get("node") or "2"),
            fmin=str(body.get("fmin") or "1"),
            fmax=str(body.get("fmax") or "1e5"),
            n=str(body.get("n") or "200"),
            lang=body.get("lang") or "en",
            eng=bool(body.get("eng")),
        )
    if path == "/api/matrix":
        return matrixlab.run(body.get("op") or "det", body.get("a") or "", body.get("b") or "", eng=bool(body.get("eng")), lang=body.get("lang") or "en")
    if path == "/api/stats":
        return statsdata.run(body.get("text") or "", eng=bool(body.get("eng")), lang=body.get("lang") or "en")
    if path == "/api/triangle":
        return triangle.run(body.get("values") or {}, lang=body.get("lang") or "en", eng=bool(body.get("eng")))
    if path == "/api/search":
        q = _q(query, "q")
        lang = _q(query, "lang", "en")
        fav = _q(query, "fav")
        favorites = [{"kind": p.split(":", 1)[0], "id": p.split(":", 1)[1]} for p in fav.split(",") if ":" in p]
        return searchall.search(q, lang, favorites)
    if path == "/api/latex":
        shown = latexout.of_result(body.get("text") or "", body.get("exact") or "")
        return {"ok": True, "text": shown, "latex": shown}
    if path == "/api/session":
        if body:
            return sessionstore.save(body)
        return sessionstore.load()
    return {}
