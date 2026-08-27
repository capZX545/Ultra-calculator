# Ultra Calculator — desktop

Standalone tkinter program. It does not import `web/`, `android/`, or `phone/`. Same formula IDs as the other copies.

## Install (no Python)

From [Releases](https://github.com/capZX545/Ultra-calculator/releases):

- Windows: `UltraCalculator-Setup-1.8.0.exe` (user install, optional desktop shortcut). Portable zip: unzip and run `UltraCalculator.exe`.
- Android: `UltraCalculator-1.8.0.apk` on the same release. Uninstall an older build first if the phone refuses it.
- Linux: unpack `UltraCalculator-Linux.tar.gz` and run `./install.sh`, or run `./UltraCalculator` in place.
- macOS: unzip and run `UltraCalculator`.

## Run from source

```
cd desktop
pip install -r requirements.txt
python3 run.py
```

Python 3.10+, numpy, scipy, sympy.

## Freeze it yourself

From the repo root:

```
pip install pyinstaller numpy scipy sympy
pyinstaller desktop/packaging/UltraCalculator.spec --noconfirm --clean
```

Windows installer: Inno Setup on `desktop/packaging/windows/setup.iss`. Linux: copy `desktop/packaging/linux/install.sh` next to the frozen binary.

Fourteen pages: Calculator (CAS + units on the line), Formulas, Polynomial ≤ 6, Numerical, Algorithms, Chemistry, Elements, Sources, Problems, Circuits (two parts then series/parallel, plus netlist), Sequences, Graph, Matrix, Stats, Triangle.

Alt+1–9 and Alt+0 switch the first ten pages. Alt+S is Sequences. Alt+G / M / D / T are Graph / Matrix / Stats / Triangle. Ctrl+1–0 also work. Alt+L or `/` is lookup.

tkinter cannot display the SVG the graph page builds. You still get the sampled values. The browser copy shows the drawing.

en / fa / fi. Bad input does not crash.
