# Ultra Calculator — desktop

Standalone tkinter program. It does not import `web/`, `android/`, or `phone/`. Same formula IDs as the other copies.

```
cd desktop
pip install -r requirements.txt
python3 run.py
```

Python 3.10+, numpy, scipy, sympy.

Fourteen pages: Calculator (CAS + units on the line), Formulas (7531 / 139), Polynomial ≤ 6, Numerical (root, integral, derivative, RK4, second-order ODE, first-order system), Algorithms (130), Chemistry, Elements (118), Sources, Problems, Circuits (MNA, AC, Thevenin, diode / BJT / MOSFET, `.tran`), Graph, Matrix, Stats, Triangle.

Alt+1–9 and Alt+0 switch the first ten pages. Alt+G / M / D / T are Graph / Matrix / Stats / Triangle. Ctrl+1–0 also work. Alt+L or `/` is lookup.

tkinter cannot display the SVG the graph page builds. You still get the sampled values. The browser copy shows the drawing.

en / fa / fi. Bad input does not crash.
