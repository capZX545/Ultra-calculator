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

- **Calculator** — engineering keypad, memory, degrees or radians, engineering notation, history
- **Formulas** — 2031 formulas in 101 categories. Default is one unknown. You can build a system and add or remove equations and unknowns
- **Polynomial** — coefficients a6 to a0, value, roots, derivative, integral
- **Numerical** — root, integral, derivative, first-order ODE with RK4
- **Chemistry** — balance an equation and compute molar mass
- **Elements** — all 118 elements, atomic number, mass, important isotopes
- **Sources** — where the formulas come from, and what was not copied

Interface languages: English, Persian, Finnish. Bad input does not crash the program.
