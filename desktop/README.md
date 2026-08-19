# Ultra Calculator — دسکتاپ

برنامهٔ پنجره‌ای. از پوشهٔ `web` چیزی برنمی‌دارد. همهٔ فرمول‌ها و قابلیت‌هایی که وب دارد این‌جا هم هست.

## اجرا

پایتون ۳٫۱۰ یا جدیدتر.

```
cd desktop
pip install -r requirements.txt
python3 run.py
```

نیاز: numpy، scipy، sympy.

## بخش‌ها

- **ماشین حساب** — صفحه کلید مهندسی، حافظه، درجه یا رادیان، نماد مهندسی، تاریخچه
- **فرمول‌ها** — ۲۰۳۱ فرمول در ۱۰۱ دسته. پیش‌فرض یک مجهول. می‌شود دستگاه معادلات ساخت و معادله یا مجهول اضافه یا کم کرد
- **چندجمله‌ای** — ضریب‌های a6 تا a0، مقدار، ریشه، مشتق، انتگرال
- **عددی** — ریشه، انتگرال، مشتق، معادلهٔ دیفرانسیل مرتبهٔ اول با RK4
- **شیمی** — موازنهٔ معادله و جرم مولی
- **عنصرها** — ۱۱۸ عنصر، عدد اتمی، جرم، ایزوتوپ‌های مهم
- **منبع‌ها** — از کجا آمده و از کجا کپی نشده

زبان رابط: انگلیسی، فارسی، فنلاندی. ورودی خراب برنامه را نمی‌خواباند.

---

Standalone desktop program. It does not import the `web` folder.

```
cd desktop
pip install -r requirements.txt
python3 run.py
```

Python 3.10+, numpy, scipy, sympy.

Modes: engineering calculator, 2031 formulas in 101 categories (one unknown or a system), polynomials to degree 6, numerical root / integral / derivative / RK4 ODE, chemistry balancer and molar mass, periodic table (118 elements with isotopes), sources. Languages: English, Persian, Finnish.
