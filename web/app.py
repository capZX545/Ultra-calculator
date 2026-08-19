"""Flask entry for the web calculator. Independent of the desktop package."""

from __future__ import annotations

from flask import Flask, jsonify, render_template, request

import chemtools
import core
from strings import UI, ui_text

app = Flask(__name__)


@app.get("/")
def home():
    return render_template("index.html")


@app.get("/api/meta")
def meta():
    lang = request.args.get("lang", "en")
    cats, _, _ = core.catalog()
    labeled = []
    for key, names in sorted(cats.items()):
        labeled.append({"id": key, "label": names.get(lang) or names.get("en")})
    return jsonify({"strings": UI.get(lang) or UI["en"], "categories": labeled, "languages": ["en", "fa", "fi"]})


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
        )
    )


@app.post("/api/poly")
def api_poly():
    body = request.get_json(silent=True) or {}
    return jsonify(core.poly_work(body.get("coeffs") or [0] * 7, body.get("x"), bool(body.get("eng"))))


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
    if kind == "integral":
        return jsonify(core.n_integral(func, a, b, eng))
    if kind == "deriv":
        return jsonify(core.n_deriv(func, a, eng))
    if kind == "ode":
        return jsonify(core.n_ode(func, a, y0, b, steps, eng))
    return jsonify(core.n_root(func, a, b, eng))


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
    return jsonify(chemtools.balance_equation(body.get("eq", "")))


@app.post("/api/molar")
def api_molar():
    body = request.get_json(silent=True) or {}
    return jsonify(chemtools.molar_mass(body.get("formula", "")))


def main():
    app.run(host="0.0.0.0", port=5000, debug=False)


if __name__ == "__main__":
    main()
