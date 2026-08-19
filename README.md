# Ultra Calculator

This repository is two calculators that do the same job. One opens as a desktop window. The other runs in a browser. I wrote them as two separate programs on purpose. Neither folder imports the other. Each one has its own engine, its own formula file, its own periodic table, and its own translation files. The formula IDs are the same in both, so if something solves on the desktop it also solves in the browser.

- `desktop` — window app (tkinter)
- `web` — browser app (Flask)

The interface is English, Persian, and Finnish. Menus, buttons, messages, and formula names come from translation files. They are not hardcoded. Persian is right-to-left in the web app.

Bad input does not crash the program. Errors are caught and a usable message is shown. You never see a stack trace.

---

## How to run it

Python 3.10 or newer.

Desktop needs numpy, scipy, and sympy:

```
cd desktop
pip install -r requirements.txt
python3 run.py
```

Web needs those plus Flask:

```
cd web
pip install -r requirements.txt
python3 run.py
```

The web server listens on `0.0.0.0:5000`. Open that port in a browser.

---

## What both programs can do

There are eight pages: Calculator, Formulas, Polynomial, Numerical, Algorithms, Chemistry, Elements, and Sources.

### Calculator

This is a normal engineering keypad, not just plus and minus.

- degrees or radians
- engineering notation (ENG)
- memory: MC, MR, M+, M−
- history (double-click or Enter on a line to reuse it)
- Ans
- trig, hyperbolic, log, exp, roots, absolute value, factorial
- if you type one equation with a single `=`, it solves for `x`
- the screen is a real text field. Type the expression with the keyboard. You do not have to click the keypad. `sin(30)+sqrt(16)` is a valid thing to type.
- Enter calculates. Esc clears. Backspace deletes. `^` is treated as `**`.
- after a result, a digit starts a new expression. `+`, `-`, `*`, `/` continue from that result.

### Step by step, like a teacher

After you press Enter or Solve, a short walkthrough appears under the result. It is written in the language you picked (English, Persian, or Finnish).

It shows the equation, what is unknown, what you already typed, whether the unknown was already alone on one side or had to be rearranged, the substitution, and the number with its unit when there is one. Extra roots are listed if they exist.

This is not only for the keypad. Named formulas, systems of equations, polynomials, numerical work, and chemistry balancing also write steps.

### Computer algebra on the same screen

You can type these on the calculator screen and they actually run:

- `summation(k, k, 1, 100)`
- `product(k, k, 1, 5)`
- `diff(x**3, x)`
- `integrate(x**2, x, 0, 1)`
- `limit(sin(x)/x, x, 0)`
- `series(exp(x), x, 0, 5)`
- `factor(x**2-1)`
- `expand((x+1)**3)`
- `simplify(...)`
- `apart(...)`, `together(...)`, `cancel(...)`
- `solveeq(x**2-4, x)`

### Formulas

There are **5196 named formulas** in **126 categories**. These are not a list of names. Each one computes the missing value.

The default is one unknown. Fill the known fields, leave one empty or pick the unknown, press solve. If the formula is already written as `y = f(...)` and `y` is the unknown, the right-hand side is evaluated directly. Otherwise the equation is solved for that unknown.

If you need several equations and several unknowns, switch to system mode. You can add or remove equations and unknowns.

Search looks at the name, the id, the category, and the expression itself. Formula names follow the interface language.

Subjects in the catalog:

- Math: algebra, geometry, coordinate geometry, trigonometry, calculus, linear algebra, statistics, probability, combinatorics, sequences and series, finite series, complex numbers, number theory, measurement uncertainty, financial math
- Engineering math: ordinary and partial differential equations, Laplace, Fourier, vector calculus, numerical methods, complex analysis
- Special functions: elementary functions, gamma / beta / erf, Bessel, hypergeometric, elliptic integrals and functions, zeta and polylog, orthogonal polynomials, Mathieu, integer and number-theory functions, named constants, complex components
- Physics: kinematics, dynamics, work and energy, rotation, gravity, oscillations, waves, fluids, thermodynamics, circuits, electrostatics, magnetism, optics, applied optics, modern physics, nuclear, astronomy, acoustics, semiconductors, radiation dose
- Chemistry: stoichiometry, solutions, gases, acids and bases, buffers and titration, kinetics, equilibrium, chemical thermodynamics, electrochemistry, colligative properties, organic calculations, spectroscopy, CODATA constants
- Biology: genetics, ecology, physiology, enzymes, lab work, plants
- Medicine: clinical formulas, pharmacokinetics, lab medicine, fitness and nutrition
- Engineering: statics and strength, civil, steel, concrete, surveying, machine design, materials, welding, fluids, pipes and pumps, heat transfer, HVAC and psychrometrics, electrical, motors, electric power, control, signals, manufacturing, aerospace, chemical engineering, industrial operations
- Economics and finance: micro, macro, interest and loans, investment, markets
- Earth and environment: climate, geotechnics, water, weather
- Other applied: computing, networks, demography, psychophysics, musical acoustics, quantum computing, travel and navigation, photography exposure, agriculture, everyday quantities
- Unit conversions: length, mass, time, force, energy, power, pressure, volume, area, speed, angle, frequency, data, activity, dose, and related pairs

Standard physical constants (speed of light, Planck, elementary charge, Boltzmann, Avogadro, R, g, G, ε0, μ0, and the rest) are stored as usable formulas, not as decoration.

### Polynomials

You enter coefficients `a6` … `a0`, so up to degree 6.

- value at a given `x`
- roots
- derivative (coefficients)
- integral (coefficients)

### Numerical

- root on an interval
- definite integral (a closed form is shown when it exists)
- derivative at a point
- first-order ODE `y' = f(x, y)` with RK4, from an initial condition to a final `x`

### Algorithms

A separate page runs named methods. They compute. They are not a list of titles.

There are 130 of them:

- number theory: gcd, lcm, extended gcd, modular inverse and power, primality, next and previous prime, factorization, Euler totient, divisors, divisor sigma, integer nth root, Chinese remainder
- combinatorics: binomial, permutations, factorial, Catalan, Bell, Stirling second kind, integer partitions
- sequences: Fibonacci, Lucas, harmonic numbers, arithmetic and geometric term and sum
- linear algebra: determinant, inverse, transpose, product, solve Ax=b, eigenvalues, rank, trace, Frobenius norm. Type a matrix as `1, 2; 3, 4`
- root finding: bisection, Newton, secant, Brent
- integration: trapezoid, Simpson, Romberg, adaptive quadrature
- ODE: Euler, Heun, RK4, RK45
- interpolation and minimization: linear interpolate, Lagrange, golden section, Nelder–Mead
- statistics: mean, median, variance, stdev, geometric mean, RMS, percentile, linear regression, correlation
- 20 probability distributions, each with PDF, CDF, and quantile
- FFT magnitudes, discrete convolution
- geometry: 2D and 3D distance, shoelace area, Heron, haversine
- integer base conversion

I did not paste 50,000 encyclopedia pages into the program. That would be a dump, and most of those lines would not be mine to copy. The engine uses SymPy and SciPy, so it can evaluate a large set of functions and methods. The named formula list is the 5196 solvable equations. This page is for the methods themselves.

### Keyboard

Both programs are meant to be used from the keyboard. You do not have to click every number.

- Click the calculator screen, or just start typing when that page is open.
- Enter calculates. Esc clears.
- Alt+1 Calculator, Alt+2 Formulas, Alt+3 Polynomial, Alt+4 Numerical, Alt+5 Algorithms, Alt+6 Chemistry, Alt+7 Elements, Alt+8 Sources. The desktop app also accepts Ctrl+1 to Ctrl+8.
- Alt+L focuses the lookup bar. If you are not already in a text field, `/` does the same. Desktop also accepts Ctrl+L.
- In Formulas, type in the search box and press Enter to open the first match. Enter in a value field solves. Enter on a chemistry equation balances it. Enter on polynomial coefficients evaluates. Enter on an algorithm runs it.

### Quick lookup

A small field sits under the top buttons on both programs. Type `H2O`, `Fe`, `Fe-56`, `Ca(OH)2`, or a constant name such as `R` or `g`. The matching molar mass, element mass, isotope mass, or stored constant appears at once.

Click a result, or press Insert, and that number is written into the last field you clicked — a formula unknown, a chemistry box, a polynomial coefficient, wherever you need it. If no field is selected, the calculator screen gets the number.

### Chemistry

This is separate from the named formula list.

- Equation balancer. Example: `H2+O2=H2O` becomes `2 H2 + O2 = 2 H2O`. Iron rusting and combustion work the same way.
- Molar mass. Example: water is 18.015, `Ca(OH)2` is about 74.092. Parentheses and subscripts are handled.

Reactions that are only a chemical equation belong here. They do not need a separate named formula.

### Elements

All 118 elements, hydrogen through oganesson:

- atomic number
- symbol
- name (three languages)
- atomic mass
- group
- important isotopes, with mass number, mass, and abundance when it is known

Search works on name and symbol.

### Sources

One tab explains where the formulas come from and what was not copied. The links are:

- Equation Encyclopedia — subject map and standard textbook equations in those subjects, not a copy of their pages, games, or practice problems
- Wolfram MathWorld — named functions are evaluated; the articles were not copied
- NIST DLMF — drives the special-function engine
- Public CODATA / NIST constants instead of copying CRC handbook pages
- Equations taught by PhET-style labs
- arXiv as a paper archive only, not scraped
- Wolfram Functions Site — families are evaluated with SymPy and SciPy, not stored as 300,000 identity lines
- Algorithms page — SymPy / SciPy methods that run. Not a dump of 50,000 copied identities
- Common syllabus formulas from standard STEM textbooks

---

## Two programs, same coverage

If one breaks, the other still has the same formulas.

| | Desktop | Web |
|---|---|---|
| Start | `cd desktop` then `python3 run.py` | `cd web` then `python3 run.py`, open port 5000 |
| UI | tkinter window | Flask + HTML |
| Calculator | yes | yes |
| Teacher steps | yes | yes |
| Computer algebra on the screen | yes | yes |
| Formulas / systems | yes | yes |
| Polynomials to degree 6 | yes | yes |
| Numerical + RK4 | yes | yes |
| Algorithms (130 methods) | yes | yes |
| Keyboard shortcuts | yes | yes |
| Quick lookup / insert | yes | yes |
| Balance and molar mass | yes | yes |
| Periodic table | yes | yes |
| Sources | yes | yes |
| en / fa / fi | yes | yes |
| Persian right-to-left | — | yes |

---

## What this is not

I did not copy 307,409 identities from the Wolfram Functions Site, 10,000 MathWorld articles, CRC handbook pages, Equation Encyclopedia’s copyrighted pages, or arXiv papers. Those sources are used as a map of subjects and as engines (SymPy, SciPy, public CODATA). The 5196 named formulas here are ones the program can actually solve.
