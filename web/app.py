"""Flask entry for the web calculator. Independent of the desktop package."""

from __future__ import annotations

import json
from pathlib import Path

from flask import Flask, jsonify, render_template, request

import algorithms
import chemtools
import core
import lookup
import teach
from strings import UI, ui_text

app = Flask(__name__)


@app.after_request
def _no_store(resp):
    resp.headers["Cache-Control"] = "no-store"
    return resp


@app.get("/")
def home():
    return render_template("index.html")


@app.get("/api/meta")
def meta():
    lang = request.args.get("lang", "en")
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
    return jsonify(
        {
            "strings": UI.get(lang) or UI["en"],
            "categories": labeled,
            "total": len(rows),
            "languages": ["en", "fa", "fi"],
        }
    )


@app.get("/api/formulas")
def formulas():
    lang = request.args.get("lang", "en")
    query = request.args.get("q", "")
    category = request.args.get("category") or None
    return jsonify(core.list_formulas(query, lang, category))


@app.post("/api/eval")
def api_eval():
    body = request.get_json(silent=True) or {}
    return jsonify(
        core.eval_line(
            body.get("expr", "0"),
            angle=body.get("angle", "DEG"),
            eng=bool(body.get("eng")),
            ans=body.get("ans", 0),
            lang=body.get("lang", "en"),
        )
    )


@app.post("/api/solve")
def api_solve():
    body = request.get_json(silent=True) or {}
    return jsonify(
        core.solve_named(
            body.get("id"),
            body.get("values") or {},
            unknown=body.get("unknown"),
            eng=bool(body.get("eng")),
            lang=body.get("lang", "en"),
        )
    )


@app.post("/api/system")
def api_system():
    body = request.get_json(silent=True) or {}
    return jsonify(
        core.solve_many(
            body.get("equations") or ["x=0"],
            body.get("unknowns") or ["x"],
            eng=bool(body.get("eng")),
            lang=body.get("lang", "en"),
        )
    )


@app.post("/api/poly")
def api_poly():
    body = request.get_json(silent=True) or {}
    out = core.poly_work(body.get("coeffs") or [0] * 7, body.get("x"), bool(body.get("eng")))
    lang = body.get("lang", "en")
    if body.get("x") is None:
        out["steps"] = teach.steps_poly(lang, "roots", None, "", out.get("degree"), out.get("roots") or [])
    else:
        out["steps"] = teach.steps_poly(lang, "eval", body.get("x"), out.get("value_text") or "0", out.get("degree"), None)
    return jsonify(out)


@app.post("/api/numeric")
def api_numeric():
    body = request.get_json(silent=True) or {}
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
        return jsonify(out)
    if kind == "deriv":
        out = core.n_deriv(func, a, eng)
        out["steps"] = teach.steps_numeric(lang, "deriv", a, None, None, out.get("text") or "0")
        return jsonify(out)
    if kind == "ode":
        out = core.n_ode(func, a, y0, b, steps, eng)
        out["steps"] = teach.steps_numeric(lang, "ode", a, b, y0, out.get("text") or "0")
        return jsonify(out)
    out = core.n_root(func, a, b, eng)
    out["steps"] = teach.steps_numeric(lang, "root", a, b, None, out.get("text") or "0")
    return jsonify(out)


@app.get("/api/elements")
def api_elements():
    q = request.args.get("q", "")
    lang = request.args.get("lang", "en")
    rows = []
    for el in chemtools.list_elements(q):
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
    return jsonify(rows)


@app.get("/api/element")
def api_element():
    el = chemtools.find_element(request.args.get("q", ""))
    if not el:
        return jsonify({})
    return jsonify(el)


@app.post("/api/balance")
def api_balance():
    body = request.get_json(silent=True) or {}
    out = chemtools.balance_equation(body.get("eq", ""))
    out["steps"] = teach.steps_chem(body.get("lang", "en"), body.get("eq", ""), out.get("text") or "", False)
    return jsonify(out)


@app.post("/api/molar")
def api_molar():
    body = request.get_json(silent=True) or {}
    out = chemtools.molar_mass(body.get("formula", ""))
    out["steps"] = teach.steps_chem(body.get("lang", "en"), body.get("formula", ""), out.get("text") or "0", True)
    return jsonify(out)


@app.get("/api/algos")
def api_algos():
    lang = request.args.get("lang", "en")
    query = request.args.get("q", "")
    category = request.args.get("category") or None
    cats, items, _ = algorithms.catalog()
    counts = {}
    for row in items:
        key = row.get("category") or ""
        counts[key] = counts.get(key, 0) + 1
    labeled = [
        {
            "id": key,
            "label": names.get(lang) or names.get("en"),
            "count": int(counts.get(key, 0)),
        }
        for key, names in sorted(cats.items())
    ]
    return jsonify(
        {
            "categories": labeled,
            "total": len(items),
            "items": algorithms.list_algos(query, lang, category),
        }
    )


@app.post("/api/algo")
def api_algo():
    body = request.get_json(silent=True) or {}
    return jsonify(algorithms.run_algo(body.get("id"), body.get("values") or {}, eng=bool(body.get("eng"))))


@app.get("/api/lookup")
def api_lookup():
    q = request.args.get("q", "")
    lang = request.args.get("lang", "en")
    return jsonify(lookup.lookup(q, lang))


@app.get("/api/sources")
def api_sources():
    path = Path(__file__).with_name("sources.json")
    return jsonify(json.loads(path.read_text(encoding="utf-8")))


def main():
    app.run(host="0.0.0.0", port=5000, debug=False)


if __name__ == "__main__":
    main()
