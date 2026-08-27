# Ultra Calculator — Android app

Install `UltraCalculator.apk` (also attached to every GitHub release next to the desktop installer). Numpy, sympy, the formula catalog, circuits, sequences, and the algorithms are already inside that file. You do not install Pydroid or pip, and the app does not download the engine from the internet.

versionName 1.8.0, versionCode 9, `org.capzx545.ultracalculator`, minSdk 24. The APK is debug-signed. Uninstall an older build if the installer refuses it.

The keypad opens at once. Pyodide 0.26.4 plus the numpy / sympy wheels load from assets in the background. No network is required to start.

Same pages as desktop and web. The WebView can show the graph SVG.

## Build

JDK 17, Android SDK, AGP 7.4.2, Gradle 7.6.3, compileSdk 33.

```
cd phone
# sdk.dir in local.properties — do not commit that file
gradle :app:assembleDebug
```

`aaptOptions { noCompress "wasm", "whl", "zip" }`.
