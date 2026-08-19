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
- after Enter, a short teacher-style walkthrough appears under the screen
- the screen is a real text field. Type the expression with the keyboard. Enter calculates, Esc clears. You do not have to click the keypad.
- Alt+1 to Alt+8 switch pages. Alt+L or `/` (when you are not already in a field) opens the lookup bar. Enter also runs solve / balance / polynomial evaluate / algorithm run in those pages.

### Algorithms

A separate page runs named methods, not just formula rearrangement.

- number theory: gcd, lcm, extended gcd, modular inverse and power, primes, factorization, totient, divisors, Chinese remainder
- combinatorics and sequences: binomial, permutations, factorial, Catalan, Bell, Stirling, partitions, Fibonacci, Lucas, harmonic, arithmetic and geometric sums
- linear algebra: determinant, inverse, product, solve Ax=b, eigenvalues, rank, trace, Frobenius norm. Type a matrix as `1, 2; 3, 4`
- root finding: bisection, Newton, secant, Brent
- integration: trapezoid, Simpson, Romberg, adaptive quadrature
- ODE: Euler, Heun, RK4, RK45
- interpolation and minimization
- statistics: mean, median, variance, stdev, geometric mean, RMS, percentile, linear regression, correlation
- 20 probability distributions, each with PDF, CDF, and quantile
- FFT magnitudes, discrete convolution
- geometry helpers: 2D/3D distance, shoelace area, Heron, haversine
- integer base conversion

There are 130 of these. Each one computes. They are not a list of names.

The ordinary calculator screen also runs computer-algebra operations:

- `summation(k, k, 1, 100)`
- `product(k, k, 1, 5)`
- `diff(x**3, x)`
- `integrate(x**2, x, 0, 1)`
- `limit(sin(x)/x, x, 0)`
- `factor(x**2-1)`
- `expand((x+1)**3)`
- `solveeq(x**2-4, x)`

I did not paste 50,000 encyclopedia pages into the program. That would be a dump, and most of those lines would not be mine to copy. The engine uses SymPy and SciPy, so it can evaluate a very large set of functions and methods. The named formula list is still the 2031 solvable equations. The new Algorithms page is for the methods themselves.

### Formulas

There are **5196 named formulas** in **126 categories**. These are not a list of names. They compute the missing value. After you solve, the program writes the steps like a teacher: the equation, what is unknown, what you already know, the substitution, then the number.

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

### Keyboard

Both programs are meant to be used from the keyboard. You do not have to click every number.

- Click the calculator screen, or just start typing when that page is open. The screen is a normal text field. `sin(30)+sqrt(16)` is a valid thing to type.
- Enter calculates. Esc clears. Backspace deletes. `^` is treated as `**`.
- After a result, a digit starts a new expression. `+`, `-`, `*`, `/` continue from that result.
- Alt+1 Calculator, Alt+2 Formulas, Alt+3 Polynomial, Alt+4 Numerical, Alt+5 Algorithms, Alt+6 Chemistry, Alt+7 Elements, Alt+8 Sources. The desktop app also accepts Ctrl+1 to Ctrl+8.
- Alt+L focuses the lookup bar. If you are not already in a text field, `/` does the same.
- In Formulas, type in the search box and press Enter to open the first match. Enter in a value field solves. Enter on a chemistry equation balances it. Enter on polynomial coefficients evaluates.

### Quick lookup

A small field sits under the top buttons on both programs. Type `H2O`, `Fe`, `Fe-56`, `Ca(OH)2`, or a constant name such as `R` or `g`. The matching molar mass, element mass, isotope mass, or stored constant appears at once. Click a result, or press Insert, and that number is written into the last field you clicked — a formula unknown, a chemistry box, a polynomial coefficient, wherever you need it. If no field is selected, the calculator screen gets the number.

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
- Algorithms page — SymPy / SciPy methods that run. Not a dump of 50,000 copied identities.

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
