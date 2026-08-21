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

- **Calculator** — engineering keypad, degrees or radians, ENG, memory, history. The screen is a text field. Type with the keyboard. Enter calculates, Esc clears. After Enter, teacher-style steps appear under the screen. The screen also accepts `diff`, `integrate`, `summation`, `product`, `limit`, `series`, `factor`, `expand`, `simplify`, `apart`, `together`, `cancel`, `solveeq`.
- **Formulas** — 5196 formulas in 126 categories. Solve shows the steps. One unknown, or several equations
- **Polynomial** — up to degree 6, value, roots, derivative, integral
- **Numerical** — root, integral, derivative, first-order ODE
- **Algorithms** — 130 named methods
- **Chemistry** — balancer and molar mass
- **Elements** — full periodic table with isotopes
- **Sources** — links and notes
- **Problems** — type an equation and solve it, or find the inverse function / inverse at a value / inverse of a matrix
- **Circuits** — read a netlist or a shortcut and compute voltages and currents

## Keyboard and lookup

Alt+1 to Alt+9 switch pages. Alt+L opens lookup. `/` does the same when you are not already in a field. Type `H2O`, `Fe-56`, or `R` in the lookup bar and insert the number into the last field you clicked.

Languages: en / fa / fi. Persian is right-to-left. Bad input does not crash the program.
