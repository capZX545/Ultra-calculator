# Ultra Calculator — desktop

Standalone window program. It does not import anything from the `web` folder. It has the same formulas and the same features as the web program.

## Run

Python 3.10 or newer.

```
cd desktop
pip install -r requirements.txt
python3 run.py
```

Needs numpy, scipy, sympy.

## Modes

- **Calculator** — engineering keypad, memory, degrees or radians, engineering notation, history. The screen is a text field. Type with the keyboard. Enter calculates, Esc clears. After Enter, teacher-style steps appear under the screen. The screen also accepts `diff`, `integrate`, `summation`, `product`, `limit`, `series`, `factor`, `expand`, `simplify`, `apart`, `together`, `cancel`, `solveeq`.
- **Formulas** — 5196 formulas in 126 categories. Solve shows the steps. Default is one unknown. You can build a system and add or remove equations and unknowns.
- **Polynomial** — coefficients a6 to a0, value, roots, derivative, integral
- **Numerical** — root, integral, derivative, first-order ODE with RK4
- **Algorithms** — 130 named methods (number theory, combinatorics, sequences, linear algebra, roots, integrals, ODE, interpolation, statistics, distributions, FFT, geometry, base conversion)
- **Chemistry** — balance an equation and compute molar mass
- **Elements** — all 118 elements, atomic number, mass, important isotopes
- **Sources** — where the formulas come from, and what was not copied

## Keyboard and lookup

Alt+1 to Alt+8 switch pages (also Ctrl+1 to Ctrl+8). Alt+L or Ctrl+L opens lookup. `/` does the same when you are not already in a field. Type `H2O`, `Fe-56`, or `R` in the lookup bar and insert the number into the last field you clicked.

Interface languages: English, Persian, Finnish. Bad input does not crash the program.
