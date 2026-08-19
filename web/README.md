# Ultra Calculator — وب

برنامهٔ مرورگر. از پوشهٔ `desktop` چیزی برنمی‌دارد. پوشش فرمول و قابلیت‌ها با دسکتاپ یکی است.

## اجرا

```
cd web
pip install -r requirements.txt
python3 run.py
```

بعد برو به `http://127.0.0.1:5000`. سرور روی `0.0.0.0:5000` گوش می‌دهد.

نیاز: Flask، numpy، scipy، sympy.

## بخش‌ها

- **ماشین حساب** — صفحه کلید مهندسی، درجه یا رادیان، ENG، حافظه، تاریخچه
- **فرمول‌ها** — ۲۰۳۱ فرمول در ۱۰۱ دسته. یک مجهول یا چند معادله
- **چندجمله‌ای** — تا درجهٔ ۶، مقدار و ریشه و مشتق و انتگرال
- **عددی** — ریشه، انتگرال، مشتق، ODE مرتبهٔ اول
- **شیمی** — موازنه و جرم مولی
- **عنصرها** — جدول تناوبی کامل با ایزوتوپ
- **منبع‌ها** — لینک و توضیح منبع‌ها

زبان: en / fa / fi. فارسی راست‌چین است.

---

Standalone web program. It does not import the `desktop` folder.

```
cd web
pip install -r requirements.txt
python3 run.py
```

Open `http://127.0.0.1:5000`. Same coverage as the desktop program: calculator, 2031 formulas in 101 categories, polynomials to degree 6, numerical methods, chemistry balancer, periodic table, sources. English, Persian, Finnish.
