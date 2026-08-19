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

- **Calculator** — engineering keypad, degrees or radians, ENG, memory, history. The screen is a text field. Type with the keyboard. Enter calculates, Esc clears. Alt+1–7 switch pages, Alt+L opens lookup.
- **Formulas** — 5196 formulas in 126 categories. Solve shows the steps. One unknown, or several equations
- **Polynomial** — up to degree 6, value, roots, derivative, integral
- **Numerical** — root, integral, derivative, first-order ODE
- **Algorithms** — 130 named methods. The screen also accepts `diff`, `integrate`, `summation`, `limit`, `factor`, `solveeq`
- **Chemistry** — balancer and molar mass
- **Elements** — full periodic table with isotopes
- **Sources** — links and notes

Languages: en / fa / fi. Persian is right-to-left.
