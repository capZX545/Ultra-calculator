"""Flask entry for the web calculator. Independent of the desktop package."""

from __future__ import annotations

import json
from pathlib import Path

from flask import Flask, jsonify, render_template, request

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
    if kind == "ode2":
        y0 = float(body.get("y0") or 0)
        yp0 = float(body.get("yp0") or 0)
        out = core.n_ode2(func, a, y0, yp0, b, steps, eng)
        out["steps"] = teach.steps_numeric(lang, "ode", a, b, y0, out.get("text") or "0")
        return jsonify(out)
    if kind == "odesys":
        out = core.n_odesys(func, a, body.get("y0") or "1, 0", b, steps, eng)
        out["steps"] = teach.steps_numeric(lang, "ode", a, b, body.get("y0"), out.get("text") or "0")
        return jsonify(out)
    if kind == "ode":
        y0 = float(body.get("y0") or 0)
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


@app.post("/api/circuit")
def api_circuit():
    body = request.get_json(silent=True) or {}
    return jsonify(
        circuits.run(
            body.get("text") or "",
            mode=body.get("mode") or "solve",
            freq=body.get("freq") or "",
            lang=body.get("lang") or "en",
            eng=bool(body.get("eng")),
        )
    )


@app.post("/api/circguide")
def api_circguide():
    body = request.get_json(silent=True) or {}
    return jsonify(circguide.run(body))


@app.post("/api/seqfind")
def api_seqfind():
    body = request.get_json(silent=True) or {}
    return jsonify(seqfind.run(body.get("text") or "", lang=body.get("lang") or "en", n_next=body.get("n_next") or 5))


@app.post("/api/graph")
def api_graph():
    body = request.get_json(silent=True) or {}
    return jsonify(
        graphs.run(
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
    )


@app.post("/api/matrix")
def api_matrix():
    body = request.get_json(silent=True) or {}
    return jsonify(
        matrixlab.run(
            body.get("op") or "det",
            body.get("a") or "",
            body.get("b") or "",
            eng=bool(body.get("eng")),
            lang=body.get("lang") or "en",
        )
    )


@app.post("/api/stats")
def api_stats():
    body = request.get_json(silent=True) or {}
    return jsonify(statsdata.run(body.get("text") or "", eng=bool(body.get("eng")), lang=body.get("lang") or "en"))


@app.post("/api/triangle")
def api_triangle():
    body = request.get_json(silent=True) or {}
    return jsonify(triangle.run(body.get("values") or {}, lang=body.get("lang") or "en", eng=bool(body.get("eng"))))


@app.get("/api/search")
def api_search():
    q = request.args.get("q", "")
    lang = request.args.get("lang", "en")
    fav = request.args.get("fav", "")
    favorites = [{"kind": p.split(":", 1)[0], "id": p.split(":", 1)[1]} for p in fav.split(",") if ":" in p]
    return jsonify(searchall.search(q, lang, favorites))


@app.post("/api/latex")
def api_latex():
    body = request.get_json(silent=True) or {}
    shown = latexout.of_result(body.get("text") or "", body.get("exact") or "")
    return jsonify({"ok": True, "text": shown, "latex": shown})


@app.get("/api/session")
def api_session_get():
    return jsonify(sessionstore.load())


@app.post("/api/session")
def api_session_post():
    body = request.get_json(silent=True) or {}
    return jsonify(sessionstore.save(body))


@app.post("/api/problem")
def api_problem():
    body = request.get_json(silent=True) or {}
    return jsonify(
        problems.run(
            body.get("text") or "",
            mode=body.get("mode") or "solve",
            unknown=body.get("unknown") or "x",
            at=body.get("at") or "",
            lang=body.get("lang") or "en",
            eng=bool(body.get("eng")),
        )
    )


def main():
    app.run(host="0.0.0.0", port=5000, debug=False)


if __name__ == "__main__":
    main()
