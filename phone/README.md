# Ultra Calculator — phone app

This is a real Android app. You install the APK and open it from the home screen. You do not install Pydroid or any other Python program.

The first launch needs internet so the math engine can load. After that, formulas, balancer, periodic table, and the keypad work on the phone.

## Install

1. Copy `UltraCalculator.apk` to the phone (from this folder after a build, or from GitHub Releases if you uploaded it).
2. Open the file. Android may ask you to allow installing from this source. Allow it.
3. Tap Ultra Calculator.

## Build the APK on a computer

Needs JDK 17 and the Android SDK.

```
cd phone
# sdk.dir in local.properties must point at your Android SDK
gradle :app:assembleDebug
```

The APK is:

`app/build/outputs/apk/debug/app-debug.apk`

Rename it to `UltraCalculator.apk` if you want.

This folder does not import `desktop`, `web`, or the Kivy `android` folder. It ships its own Python files and the same 5196 formulas.
