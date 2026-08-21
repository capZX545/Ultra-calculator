# Ultra Calculator — web

Standalone Flask program. It does not import `desktop/`. Same formula IDs as the other copies.

```
cd web
pip install -r requirements.txt
python3 run.py
```

Listens on `0.0.0.0:5000`. Flask, numpy, scipy, sympy.

After you edit `formulas.json` or `core.py`, restart the process. `core.catalog()` is cached.

Same fourteen pages as the desktop copy. Persian is right-to-left. Lookup, Save / Load, and LaTeX sit on the bar under the tabs.

JSON routes live in `app.py`: `/api/eval`, `/api/solve`, `/api/system`, `/api/poly`, `/api/numeric`, `/api/problem`, `/api/circuit`, `/api/graph`, `/api/matrix`, `/api/stats`, `/api/triangle`, `/api/search`, `/api/latex`, `/api/session`, plus formulas, algorithms, chemistry, elements, lookup, sources.

en / fa / fi. Bad input does not crash.
