# Ultra Calculator

This repo is two programs that do the same job: they calculate. One opens as a desktop window. The other runs in a browser. The two codebases are not linked. Neither folder imports the other. Each one has its own engine, its own formula file, its own periodic table, and its own translation files. The formula list is the same. If a formula is here, it is in both programs.

- `desktop` — window app (tkinter)
- `web` — browser app (Flask)

The interface is English, Persian, and Finnish. Menus, buttons, messages, and formula names come from translation files. They are not hardcoded. Persian is right-to-left in the web app.

Bad input does not crash the program. Errors are caught and a usable result is shown. The user never sees a stack trace.

---

## What it does

### Engineering calculator

This is a normal engineering keypad, not just the four operations.

- degrees or radians
- engineering notation (ENG)
- memory: MC, MR, M+, M−
- history
- Ans
- trig, hyperbolic, log, exp, roots, absolute value, factorial
- if you type one equation with a single `=`, it solves for `x`

### Formulas

There are **2031 named formulas** in **101 categories**. These are not a list of names. They compute the missing value.

The default is one unknown. Fill the known fields, leave one empty or pick the unknown, press solve. If the formula is `y = f(...)` and `y` is the unknown, the right-hand side is evaluated directly. Otherwise the equation is solved for that unknown.

If you need several equations and several unknowns, switch to system mode. You can add or remove equations and unknowns.

Search looks at the name, the id, the category, and the expression itself. Formula names follow the interface language.

Subjects covered:

- Math: algebra, geometry, coordinate geometry, trigonometry, calculus, linear algebra, statistics, probability, combinatorics, sequences and series, complex numbers, number theory, measurement uncertainty
- Engineering math: ordinary and partial differential equations, Laplace, Fourier, vector calculus, numerical methods, complex analysis
- Special functions: gamma, beta, error function, Bessel, hypergeometric, elliptic integrals and functions, zeta and polylog, orthogonal polynomials, Mathieu, named constants
- Physics: kinematics, dynamics, work and energy, rotation, gravity, oscillations, waves, fluids, thermodynamics, circuits, electrostatics, magnetism, optics, modern physics, nuclear, astronomy, acoustics
- Chemistry: stoichiometry, solutions, gases, acids and bases, kinetics, equilibrium, chemical thermodynamics, electrochemistry, colligative properties, organic calculations, CODATA constants
- Biology: genetics, ecology, physiology, enzymes, lab work, plants
- Medicine: clinical formulas, pharmacokinetics, fitness and nutrition
- Engineering: statics and strength, civil, machine design, fluids, heat transfer, electrical, control, signals, manufacturing, aerospace, chemical engineering
- Economics and finance: micro, macro, interest and loans, investment, markets
- Earth: climate and earth science, geotechnics
- Computing, demography, psychophysics, musical acoustics, quantum computing, everyday quantities

Standard physical constants (speed of light, Planck, elementary charge, Boltzmann, Avogadro, R, g, G, ε0, μ0, and the rest) are also stored as usable formulas.

### Polynomials

You enter coefficients `a6` … `a0`, so up to degree 6.

- value at a given `x`
- roots
- derivative (coefficients)
- integral (coefficients)

### Numerical

- root on an interval
- definite integral (closed form is shown when it exists)
- derivative at a point
- first-order ODE `y' = f(x, y)` with RK4, from an initial condition to a final `x`

### Chemistry

This is separate from the named formula list.

- Equation balancer. Example: `H2+O2=H2O` becomes `2 H2 + O2 = 2 H2O`. Iron rusting and combustion work the same way.
- Molar mass. Example: water is 18.015, `Ca(OH)2` is about 74.092. Parentheses and subscripts are handled.

Reactions that are only a chemical equation belong here. They do not need a separate named formula.

### Elements

All 118 elements:

- atomic number
- symbol
- name (three languages)
- atomic mass
- group
- important isotopes, with mass number, mass, and abundance when it is known

Search works on name and symbol.

### Sources

One tab explains where the formulas come from and what was not copied. The links are:

- Equation Encyclopedia — subject map and standard textbook equations in those subjects, not a copy of their pages or practice problems
- Wolfram MathWorld — named functions are evaluated; the articles were not copied
- NIST DLMF — drives the special-function engine
- Public CODATA / NIST constants instead of copying CRC handbook pages
- Equations taught by PhET-style labs
- arXiv as a paper archive only, not scraped
- Wolfram Functions Site — families are evaluated with SymPy and SciPy, not stored as 300,000 identity lines

---

## Two programs, same coverage

I wrote two separate codebases on purpose. If one breaks, the other still has the same formulas.

| | Desktop | Web |
|---|---|---|
| Start | `cd desktop` then `python3 run.py` | `cd web` then `python3 run.py`, open port 5000 |
| UI | tkinter window | Flask + HTML |
| Calculator | yes | yes |
| Formulas / systems | yes | yes |
| Polynomials to degree 6 | yes | yes |
| Numerical + RK4 | yes | yes |
| Balance and molar mass | yes | yes |
| Periodic table | yes | yes |
| Sources | yes | yes |
| en / fa / fi | yes | yes |

Desktop depends on `numpy`, `scipy`, `sympy`. Python 3.10 or newer.

Web needs those plus `flask`.

```
cd desktop
pip install -r requirements.txt
python3 run.py
```

```
cd web
pip install -r requirements.txt
python3 run.py
```

The web server listens on `0.0.0.0:5000`.
