# Ultra Calculator — Android app

This is a normal Android app. Install the APK. Numpy, sympy, and the formula engine are already inside that file. You do not install Pydroid, pip, numpy, or sympy yourself.

## Install

1. Put `UltraCalculator.apk` on the phone (from the repo root, or from this folder after you build).
2. Open the file and allow installs from this source if Android asks.
3. Open Ultra Calculator from the app list.

The keypad opens at once. The math engine (numpy / sympy) loads in the background from files already inside the APK. No internet is required to start.

## Build

Needs JDK 17 and the Android SDK.

```
cd phone
# set sdk.dir in local.properties
gradle :app:assembleDebug
```

Output: `app/build/outputs/apk/debug/app-debug.apk`
