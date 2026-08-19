# Ultra Calculator — web

Standalone browser program. It does not import anything from the `desktop` folder. Formula coverage and features match the desktop program.

## Run

```
cd web
pip install -r requirements.txt
python3 run.py
```

Then open `http://127.0.0.1:5000`. The server listens on `0.0.0.0:5000`.

Needs Flask, numpy, scipy, sympy.

## Modes

- **Calculator** — engineering keypad, degrees or radians, ENG, memory, history
- **Formulas** — 2031 formulas in 101 categories. One unknown, or several equations
- **Polynomial** — up to degree 6, value, roots, derivative, integral
- **Numerical** — root, integral, derivative, first-order ODE
- **Chemistry** — balancer and molar mass
- **Elements** — full periodic table with isotopes
- **Sources** — links and notes

Languages: en / fa / fi. Persian is right-to-left.
