# Ultra Calculator — Android

Standalone phone program. It does not import anything from the `desktop` or `web` folders. Formula IDs and coverage match the other two programs: 5196 named formulas, chemistry balancer, periodic table, algorithms, teacher steps, lookup, English / Persian / Finnish.

This is a Kivy app. On a computer it opens a tall phone-sized window. On Android you can run it in Pydroid 3, or pack an APK with Buildozer.

## Run on a computer (to try the phone layout)

Python 3.10 or newer.

```
cd android
pip install -r requirements.txt
python3 run.py
```

## Run on an Android phone without building an APK

1. Install [Pydroid 3](https://play.google.com/store/apps/details?id=ru.iiec.pydroid3) from Play Store.
2. In Pydroid, open Pip and install `kivy`, `numpy`, `sympy`. `scipy` is optional; without it a few numerical methods still run using a built-in fallback.
3. Copy this `android` folder onto the phone.
4. Open `run.py` (or `main.py`) in Pydroid and press the play button.

The phone keyboard types into the calculator screen. Pages are the buttons along the top: Calculator, Formulas, Polynomial, Numerical, Algorithms, Chemistry, Elements, Sources.

## Build an APK (Buildozer)

Do this on Linux. Install Buildozer once, then:

```
cd android
pip install buildozer
buildozer android debug
```

The APK lands in `bin/`. Copy it to the phone and install it. The first build downloads the Android NDK/SDK and takes a long time.

`scipy` is left out of the default APK recipe on purpose. The named formulas, balancer, polynomials, RK4, and most algorithms still run. If you need SciPy inside the APK, add `scipy` to `requirements` in `buildozer.spec` and expect a harder build.

## What is on each page

- **Calculator** — keypad plus the phone keyboard. DEG/RAD, ENG. After `=` a short teacher walkthrough. You can type `diff(x**3,x)` and the other computer-algebra commands.
- **Formulas** — 5196 formulas. Each category shows how many it has. Tap a name, fill knowns, solve. Steps appear under the answer.
- **Polynomial** — degree 6, value, roots.
- **Numerical** — root, integral, derivative, RK4 ODE.
- **Algorithms** — 130 named methods, with counts on the categories.
- **Chemistry** — balance and molar mass.
- **Elements** — all 118, with isotopes.
- **Sources** — where the formulas come from.

Lookup sits under the top buttons. Type `H2O` or `Fe-56` or `g` and Insert puts the number into the last field you tapped.
