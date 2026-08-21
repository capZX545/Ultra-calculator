# Ultra Calculator

Four Python programs that solve the same things. A tkinter window, a Flask site, a Kivy tree, and an Android APK. They do not import each other. Each tree has its own engine, its own `formulas.json`, its own periodic table, and its own translation files. Formula IDs are identical across copies, so a solve that works in `desktop/` is the same solve in `web/` and on the phone.

I kept the copies separate on purpose. A shared package would have been shorter. It would also mean one import bug takes everything down. If the web app is broken I still want `python3 desktop/run.py` to open.

| Path | What it is |
|---|---|
| `desktop/` | Window app. tkinter. `python3 run.py` |
| `web/` | Browser app. Flask on `0.0.0.0:5000` |
| `phone/` | Android Gradle project. Install `UltraCalculator.apk` |
| `android/` | Kivy copy of the same engine, if I pack it another way |

UI languages are English, Persian, and Finnish. Strings come from translation files (`desktop/calc/i18n.py`, `web/strings.py`, and the copies under `android/` and `phone/`). Formula names follow the language too. Persian is right-to-left in the web and phone WebView.

Bad input is swallowed. You get `0` and a short note. No traceback in the UI.

Python 3.10+. Desktop: numpy, scipy, sympy. Web: those plus Flask. The APK already contains numpy and sympy. You do not install Pydroid or pip on the phone.

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

Then open port 5000. The APK is `UltraCalculator.apk` at the repo root (same file under `phone/`). Package `org.capzx545.ultracalculator`, minSdk 24, versionName 1.3, versionCode 4. Uninstall an older build first if the installer complains.

---

## How the solver works

The keypad and the named-formula page are not two programs glued together. Both go through a SymPy parse, then either `N` or `solve`.

Formula parse uses `standard_transformations` only. Implicit multiplication is off there. `I` and `E` are not bound to the imaginary unit and `exp(1)`, because those letters are variable names in a lot of textbook equations (current, energy, field, …). Calc mode is looser: implicit multiplication is allowed, and `pi` / `e` / `j` are constants.

A few rules I had to lock in after they bit me:

- Comma becomes a decimal point only when the whole string has no letters. `2,5` is `2.5`. `x, y` is not.
- Digit followed by `(` is not implicit multiplication in calc mode. `log10(100)` must stay a call.
- If the formula is already `y = f(...)` and `y` is the unknown, the right-hand side is evaluated with the knowns substituted. I do not call `solve` for that case.
- One unknown is the default. System mode is opt-in. You add and remove equations and unknowns yourself.
- Identifiers I avoid as parameter names: `I`, `E`, `pi`, `re`, `rf`, `beta`, `gamma`, `yn`, `def`, `in`, `lambda`. Those collide with SymPy or Python.

`core.catalog()` is cached (`lru_cache`). After you edit `formulas.json` or `core.py`, restart Flask.

Teacher steps are written after a successful solve, in the language you picked. They say what you typed, what is unknown, whether the unknown was already isolated, the substitution, and the number with its unit. They are a walkthrough, not a derivation of every identity.

---

## Pages

Fourteen pages. Alt+1 … Alt+9 and Alt+0 switch the first ten. Alt+G graph, Alt+M matrix, Alt+D stats, Alt+T triangle. Desktop also takes Ctrl+1 … Ctrl+0. Alt+L (or `/` when you are not in a field) focuses lookup.

### Calculator

Engineering keypad. DEG/RAD, ENG notation, MC/MR/M+/M−, history, Ans. The screen is a real text field. Type `sin(30)+sqrt(16)` and press Enter. `^` is `**`. After a result, a digit starts a new line; `+` `−` `*` `/` continue from Ans.

If the line has exactly one `=`, it is treated as an equation in `x`.

The same screen runs CAS calls. These are evaluated, not printed as text:

```
summation(k, k, 1, 100)
product(k, k, 1, 5)
diff(x**3, x)
integrate(x**2, x, 0, 1)
limit(sin(x)/x, x, 0)
series(exp(x), x, 0, 5)
factor(x**2-1)
expand((x+1)**3)
simplify(...)
apart(...)  together(...)  cancel(...)
solveeq(x**2-4, x)
```

Units are first-class on this screen. `12 V / 2 kohm` is `6 mA`. `5 km / 30 min` is `2.777… m/s`. `100 W * 2 s` is `200 J`. SI base dimensions are tracked as a 7-tuple (L, M, T, I, Θ, N, J). Prefixes: `f p n u µ m c d k M G T` and `meg`. A bare `2k` after a voltage is treated as 2 kΩ. Implementation is in `units.py` (copied into each tree). It does not use Pint.

### Formulas

5196 named equations, 126 categories. Each row is a solvable identity, not a caption. Desktop and web `formulas.json` are the same file (~3.75 MB).

Default: fill knowns, leave one blank or pick the unknown, Solve. Isolated-LHS formulas skip `solve` and evaluate the right-hand side. Otherwise SymPy solves for that symbol, with `nsolve` as a fallback.

System mode: several equations, several unknowns. Add / remove both.

Search matches id, category, name (all three languages), and the expression string.

Counts by group, they add to 5196:

| Group | n |
|---|---:|
| Math | 771 |
| Engineering math | 62 |
| Special functions | 154 |
| Physics | 489 |
| Chemistry | 207 |
| Biology | 126 |
| Medicine and health | 90 |
| Engineering | 433 |
| Economics and finance | 95 |
| Earth and environment | 78 |
| Other applied | 175 |
| Unit conversions | 2516 |

Unit conversions are the large block because each pair is a working formula (length, mass, time, force, energy, power, pressure, volume, area, speed, angle, frequency, data, activity, dose).

**Math (771)**

| Category | n |
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

| Category | n |
|---|---:|
| Numerical methods | 21 |
| Ordinary differential equations | 11 |
| Laplace transform | 10 |
| Vector calculus | 10 |
| Fourier analysis | 6 |
| Partial differential equations | 3 |
| Complex analysis | 1 |

**Special functions (154)**

| Category | n |
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

| Category | n |
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

| Category | n |
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

**Biology (126)** — Ecology 36, Physiology 34, Genetics 25, Lab and biotech 21, Enzymes 7, Plant physiology 3.

**Medicine and health (90)** — Fitness and nutrition 40, Clinical 33, Pharmacokinetics 16, Lab medicine 1.

**Engineering (433)**

| Category | n |
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

**Economics and finance (95)** — Investment 23, Market 21, Interest and loans 19, Macro 18, Micro 14.

**Earth and environment (78)** — Earth and climate 39, Geotechnics 22, Water and environment 9, Weather and climate 8.

**Other applied (175)** — Everyday 67, Computing 24, Psychophysics 20, Musical acoustics 17, Quantum computing 15, Travel 10, Demography 9, Agriculture 5, Photography 5, Networks 3.

CODATA / NIST constants (c, h, e, k, N_A, R, g, G, ε0, μ0, …) are stored as formulas you can solve, not as a decoration list.

### Problems

Free-form equation, not a catalog row.

- `2*x+3=11` → `4`. `x**2-5*x+6=0` → `2, 3`. Persian digits: `۲x+۳=۱۱`.
- Systems: `x+y=5; x-y=1` or separate lines.
- Inverse: `2*x+3` → `x/2 - 3/2`. Fill **at** with `11` and it evaluates the inverse there.
- `x**3` inverse is the cube root, every branch SymPy returns.
- Matrix inverse: `1, 2; 3, 4`.

API: `POST /api/problem` with `{text, mode, unknown, at, lang, eng}`.

### Circuits

Text netlist. There is no schematic editor. Node `0` (also `gnd`, `ground`, `g`, `earth`) is the reference.

```
V1 1 0 12
R1 1 2 1k
R2 2 0 2k
```

That divider gives `V(2)=8 V`, `I=4 mA`.

The linear solver is modified nodal analysis. The dense system is factored with a small Gaussian-elimination routine that accepts complex entries (`_ge` in `circuits.py`). SciPy is not required for MNA. That matters on the phone.

Passive and independent sources: `R`, `C`, `L`, `V`, `I`. Suffixes: `t g meg k m u µ n p f`. `meg` is 1e6. Lowercase `m` is 1e-3.

Controlled sources, SPICE order:

- `Ename n+ n- nc+ nc- gain` — VCVS
- `Gname n+ n- nc+ nc- gm` — VCCS
- `Fname n+ n- Vctrl gain` — CCCS
- `Hname n+ n- Vctrl r` — CCVS

Nonlinear DC uses Newton–Raphson on the same MNA stamps:

- `Dname n+ n- [Is] [n]` — Shockley diode, `Vt = 0.026 n`, `Vd` clamped
- `Qname C B E [npn|pnp] [beta]` — simplified Gummel / hybrid-π
- `Mname D G S [nmos|pmos] [Kp] [Vt]` — square-law MOSFET, triode and saturation

These are textbook companion models, not BSIM or Ebers–Moll with Early effect. Fine for homework operating points. Do not treat the numbers as a lab measurement.

AC: fill **f (Hz)** or write `.ac 50`. C and L become `jωC` and `1/(jωL)`.

Transient: `.tran tstep tstop`. Capacitors and inductors use backward-Euler companions. Nonlinear devices are re-linearized each step. Output is the last operating point plus a short time table. It is not a full SPICE transient (no trapezoidal, no LTE control).

Thevenin: `.thevenin a b` → Voc, Isc, Rth.

Inverse: put `?` on one element and `.eq V(2)=4` or `I(R1)=3m`. One unknown, log-space grid then ternary search. Not a general nonlinear OP solver.

Shortcuts when you do not want a netlist: `series 1k 2k 3k`, `parallel 1k 1k`, `divider 12 1k 2k`, `V=12 R=1k`, `R=1k C=1u` (τ and fc).

API: `POST /api/circuit` `{text, mode, freq, lang, eng}`.

### Polynomials

Coefficients `a6` … `a0`. Value at `x`, roots (`numpy.roots`), derivative and integral coefficient lists.

### Numerical

- Root on `[a, b]` (Brent, Newton fallback)
- Definite integral. Closed form from SymPy when it exists, otherwise quadrature
- Derivative at a point
- `y' = f(x, y)`, RK4
- `y'' = f(x, y, yp)`, RK4 on the first-order reduction
- First-order system: `y1'=…; y2'=…`, initial vector in `y0` as `1, 0`

Phone APK has no SciPy. Root and integral fall back inside `android/core.py` / the phone copy.

### Algorithms

130 runnable methods, 14 categories. Not titles.

Number theory, combinatorics, sequences, dense linear algebra (`1, 2; 3, 4`), scalar roots, quadrature, ODE (Euler / Heun / RK4 / RK45), interpolation and two scalar minimizers, descriptive stats, 20 distributions (PDF, CDF, quantile), rFFT magnitudes, discrete convolution, 2D/3D distance, shoelace, Heron, haversine, integer base conversion.

### Graph

`y = f(x)`, one function per line. Parametric `x(t), y(t)`. Scatter from pasted `x y` pairs. Bode: paste a netlist, pick a node, log-frequency sweep of `|V|` in dB. The plot is an SVG built in Python (`graphs.py`). Web and the phone WebView display it. tkinter cannot load SVG as a `PhotoImage`, so the desktop page shows the numbers and a fallback string. I have not wired a rasterizer there yet.

### Matrix

`A` as `1, 2; 3, 4` or one row per line. det, inverse, transpose, eigenvalues, characteristic polynomial, RREF, rank, trace, `A B`, `Ax = b`. SymPy `Matrix`, so fractions stay exact until they are printed.

### Stats

Paste a column, or one line of numbers. n, mean, median, min, max, sample variance and stdev, quartiles, IQR, RMS, histogram SVG. Two columns: slope, intercept, Pearson r.

### Triangle

Sides `a,b,c` opposite angles `A,B,C` in degrees. SSS, SAS, ASA, AAS, SSA (both triangles when the ambiguous case is real). Area, perimeter, altitudes, inradius, circumradius.

### Chemistry and elements

Balancer (`H2+O2=H2O` → `2 H2 + O2 = 2 H2O`) and molar mass with parentheses. Separate from the named-formula list.

118 elements, H through Og. Z, symbol, name in three languages, atomic mass, group, isotopes (A, mass, abundance when known).

### Lookup, save, LaTeX

Lookup under the tabs. `H2O`, `Fe`, `Fe-56`, `R`, `g`, a page name, a CAS command, a circuit shortcut. Click or Insert writes the number into the last focused field. Right-click a hit to star it. Favorites live in `localStorage` (web / phone) or `~/.ultra-calculator/session.json` (desktop / Kivy).

Save / Load keep language, circuit netlist, problem text, graph input, matrix A, stats data, history, favorites.

LaTeX copies the last result (`sympy.latex` when the string parses).

---

## Keyboard

| Key | Action |
|---|---|
| Enter | evaluate / solve / run, depending on the page |
| Esc | clear the calculator |
| `^` | `**` |
| Alt+1 … Alt+9 | first nine pages |
| Alt+0 | Circuits |
| Alt+G / M / D / T | Graph / Matrix / Stats / Triangle |
| Alt+L, Ctrl+L, `/` | lookup |

Enter in a formula value field solves. Enter on a chemistry line balances. Enter on polynomial coefficients evaluates.

---

## Android APK

`phone/` is a WebView (`file:///android_asset/www/index.html`) that boots Pyodide 0.26.4 (CPython 3.12.1, abi `2024_0`) from assets. Wheels inside the APK: numpy 1.26.4, sympy 1.12, mpmath, packaging, micropip. This numpy build has empty `depends`, so there is no separate OpenBLAS wheel. Total `pyodide/` directory is about 42 MB. The signed APK is about 45 MB.

`boot.js` writes the `py/*.py` and JSON files into the Pyodide FS, then `import bridge`. The UI is shown immediately (`window.startApp` at the end of `ui.js`, `_appStarted` guard). `/api/eval` has a small JS fallback until Pyodide is ready. `WebAssembly.instantiateStreaming` is patched to fall back to `arrayBuffer` because `file://` often breaks streaming in Android WebView. `MainActivity` serves asset MIME types (`application/wasm`, `application/zip` for `.whl` / `.zip`). `android:largeHeap="true"`. `aaptOptions { noCompress "wasm", "whl", "zip" }`.

Build, if you have the SDK:

```
cd phone
# sdk.dir in local.properties, not committed
# AGP 7.4.2, Gradle 7.6.3, compileSdk 33, build-tools 33.0.2, JDK 17
gradle :app:assembleDebug
```

The APK in the repo is debug-signed (`androiddebugkey`). Uninstall a previous install if the signature or versionCode fights you.

I do not ship SciPy in the APK. Anything that needed it has a fallback.

---

## Layout

```
desktop/calc/     engine, UI, formulas.json, circuits, problems, units, …
web/              Flask app.py, same modules as flat files, static/, templates/
android/          Kivy main.py + the same modules
phone/app/src/main/assets/www/
                  index.html, ui.js, boot.js, py/, pyodide/
```

Web APIs are ordinary JSON POST/GET: `/api/eval`, `/api/solve`, `/api/system`, `/api/poly`, `/api/numeric`, `/api/problem`, `/api/circuit`, `/api/graph`, `/api/matrix`, `/api/stats`, `/api/triangle`, `/api/search`, `/api/latex`, `/api/session`, plus formulas, algorithms, chemistry, elements, lookup, sources. The phone WebView calls the same paths through `bridge.handle`.

---

## Coverage matrix

| | Desktop | Web | Phone APK |
|---|---|---|---|
| Keypad + CAS | yes | yes | yes |
| Units on the keypad | yes | yes | yes |
| 5196 formulas / systems | yes | yes | yes |
| Teacher steps | yes | yes | yes |
| Polynomials ≤ 6 | yes | yes | yes |
| Numerical, RK4, ODE 2, system | yes | yes | yes (no SciPy) |
| 130 algorithms | yes | yes | yes |
| Chemistry + 118 elements | yes | yes | yes |
| Problems / inverse | yes | yes | yes |
| Circuits (MNA, AC, Thevenin, NL, .tran) | yes | yes | yes |
| Graph SVG | fallback | yes | yes |
| Matrix / stats / triangle | yes | yes | yes |
| Save / lookup / LaTeX | yes | yes | yes |
| en / fa / fi | yes | yes | yes |
| Persian RTL | — | yes | yes |

---

## Sources, and what I did not copy

The Sources tab lists the maps I used. I did not scrape or paste:

- Wolfram Functions Site identity dump (on the order of 3×10⁵ lines)
- MathWorld article text
- CRC handbook pages
- Equation Encyclopedia’s copyrighted pages, games, or problem sets
- arXiv TeX

Named special functions are evaluated with SymPy / SciPy. Constants are public CODATA. The 5196 rows are textbook equations the program can actually solve. That is the point of the catalog. A dump of other people’s pages would be larger and mostly not mine to ship.

---

## Limits I am not pretending are done

- Circuit inverse is one numeric unknown. Not a general nonlinear OP.
- No schematic drawing. Netlist only.
- Diode / BJT / MOSFET models are the simple stamps described above.
- Transient is backward Euler, fixed step, short table.
- Teacher steps explain the solve that ran. They do not invent a Photomath-style derivation for every identity.
- A few named special-function rows (`struveh`, `struvel`, `mathieuc`, `mathieus`) still parse poorly. Some identities evaluate to 0 at parse. I have not finished those.
- Desktop graph does not rasterize the SVG yet.
- APK is debug-signed.
- No iOS tree.

If you change `formulas.json` or `core.py`, restart the Flask process. Do not commit `phone/local.properties`, `.gradle`, or `app/build`.
