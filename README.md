# Ultra Calculator

This repository is three calculators that do the same job. One opens as a desktop window. One runs in a browser. One is a phone app for Android. I wrote them as separate programs on purpose. None of the folders import each other. Each one has its own engine, its own formula file, its own periodic table, and its own translation files. The formula IDs are the same in all three, so if something solves on the desktop it also solves in the browser and on the phone.

- `desktop` — window app (tkinter)
- `web` — browser app (Flask)
- `phone` — Android app. Install `UltraCalculator.apk`. You do not need Pydroid.
- `android` — Kivy copy of the same engine, if you want to pack it another way

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

There is also a real Android app. Install `UltraCalculator.apk` on the phone. You do not need Pydroid. Numpy and sympy are already inside the APK.

The project that builds that APK is in `phone/`.

---

## What the programs can do

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

Here is the count for every category. Desktop and web have the same numbers. They add up to 5196.

**Math (771)**

| Category | Formulas |
|---|---:|
| Geometry | 143 |
| Financial math | 113 |
| Statistics | 101 |
| Algebra | 96 |
| Calculus | 61 |
| Trigonometry | 54 |
| Probability | 53 |
| Linear algebra | 43 |
| Combinatorics | 19 |
| Complex numbers | 19 |
| Number theory | 18 |
| Finite series | 16 |
| Coordinate geometry | 15 |
| Sequences and series | 13 |
| Measurement uncertainty | 7 |

**Engineering math (62)**

| Category | Formulas |
|---|---:|
| Numerical methods | 21 |
| Ordinary differential equations | 11 |
| Laplace transform | 10 |
| Vector calculus | 10 |
| Fourier analysis | 6 |
| Partial differential equations | 3 |
| Complex analysis | 1 |

**Special functions (154)**

| Category | Formulas |
|---|---:|
| Elementary functions | 51 |
| Gamma, beta, erf | 28 |
| Bessel-type functions | 17 |
| Hypergeometric functions | 12 |
| Named constants | 10 |
| DLMF extra identities | 10 |
| Zeta and polylog | 7 |
| Orthogonal polynomials | 5 |
| Elliptic integrals | 3 |
| Complex components | 3 |
| Elliptic functions | 2 |
| Generalized functions | 2 |
| Mathieu functions | 2 |
| Integer functions | 1 |
| Number theory functions | 1 |

**Physics (489)**

| Category | Formulas |
|---|---:|
| Thermodynamics | 45 |
| Circuits | 44 |
| Optics | 39 |
| Dynamics | 36 |
| Modern physics | 32 |
| Kinematics | 29 |
| Work and energy | 28 |
| Fluids | 28 |
| Waves | 23 |
| Rotation | 22 |
| Physical constants | 22 |
| Astronomy | 20 |
| Electrostatics | 20 |
| Magnetism | 20 |
| Gravitation | 14 |
| Acoustics | 14 |
| Nuclear | 13 |
| Oscillations | 12 |
| More EM / quantum | 12 |
| Semiconductors | 6 |
| Applied optics | 5 |
| Radiation dose | 5 |

**Chemistry (207)**

| Category | Formulas |
|---|---:|
| Solutions | 27 |
| Acids and bases | 25 |
| Gases | 22 |
| Kinetics | 22 |
| More chemical thermo | 20 |
| Stoichiometry | 17 |
| Equilibrium extra | 17 |
| Organic calculations | 14 |
| Electrochemistry | 13 |
| Stoichiometry extra | 11 |
| Colligative properties | 8 |
| Buffers and titration | 4 |
| Spectroscopy | 4 |
| Chemical thermodynamics | 3 |

**Biology (126)**

| Category | Formulas |
|---|---:|
| Ecology | 36 |
| Physiology | 34 |
| Genetics | 25 |
| Lab and biotech | 21 |
| Enzymes | 7 |
| Plant physiology | 3 |

**Medicine and health (90)**

| Category | Formulas |
|---|---:|
| Fitness and nutrition | 40 |
| Clinical formulas | 33 |
| Pharmacokinetics | 16 |
| Lab medicine | 1 |

**Engineering (433)**

| Category | Formulas |
|---|---:|
| HVAC | 82 |
| Electrical engineering | 44 |
| Machine design | 33 |
| Heat transfer extra | 31 |
| Pipes and pumps | 29 |
| Electric power | 28 |
| Aerospace | 20 |
| Engineering fluids | 19 |
| Steel design | 19 |
| Control | 16 |
| Civil / structures | 15 |
| Signals | 15 |
| Statics and strength | 15 |
| Chemical engineering | 14 |
| Manufacturing | 9 |
| Industrial operations | 7 |
| Heat transfer | 6 |
| Psychrometrics | 6 |
| Materials | 6 |
| Motors and machines | 6 |
| Surveying | 6 |
| Concrete | 4 |
| Welding | 3 |

**Economics and finance (95)**

| Category | Formulas |
|---|---:|
| Investment | 23 |
| Market formulas | 21 |
| Interest and loans | 19 |
| Macroeconomics | 18 |
| Microeconomics | 14 |

**Earth and environment (78)**

| Category | Formulas |
|---|---:|
| Earth and climate | 39 |
| Geotechnics | 22 |
| Water and environment | 9 |
| Weather and climate | 8 |

**Other applied (175)**

| Category | Formulas |
|---|---:|
| Everyday quantities | 67 |
| Computing formulas | 24 |
| Psychophysics | 20 |
| Musical acoustics | 17 |
| Quantum computing | 15 |
| Travel and navigation | 10 |
| Demography | 9 |
| Agriculture | 5 |
| Photography exposure | 5 |
| Networks and info | 3 |

**Unit conversions (2516)**

Length, mass, time, force, energy, power, pressure, volume, area, speed, angle, frequency, data, activity, dose, and related pairs. This is the largest category because each pair is a working formula, not a note.

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

Android is a third copy in `phone/`. Install `UltraCalculator.apk` on the phone. Same 5196 formulas, balancer, periodic table, algorithms, lookup, and teacher steps.

---

## What this is not

I did not copy 307,409 identities from the Wolfram Functions Site, 10,000 MathWorld articles, CRC handbook pages, Equation Encyclopedia’s copyrighted pages, or arXiv papers. Those sources are used as a map of subjects and as engines (SymPy, SciPy, public CODATA). The 5196 named formulas here are ones the program can actually solve.
