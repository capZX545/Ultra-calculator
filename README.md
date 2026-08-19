# Ultra Calculator

این مخزن دو برنامهٔ جدا است که یک کار را می‌کنند: حساب کردن. یکی روی میزکار باز می‌شود، یکی توی مرورگر. کدشان به هم وصل نیست. هیچ‌کدام از پوشهٔ دیگری چیزی import نمی‌کند. هر کدام موتور خودش، فایل فرمول خودش، جدول تناوبی خودش و ترجمهٔ خودش را دارد. فهرست فرمول‌ها یکی است؛ اگر فرمولی این‌جا باشد، توی هر دو هست.

- `desktop` — برنامهٔ پنجره‌ای با tkinter
- `web` — برنامهٔ مرورگر با Flask

زبان رابط: انگلیسی، فارسی، فنلاندی. منوها، دکمه‌ها، پیام‌ها و اسم فرمول‌ها از فایل ترجمه می‌آیند، توی کد سخت نشده‌اند. فارسی توی وب راست‌چین است.

ورودی خراب برنامه را نمی‌خواباند. خطا را می‌گیرد و یک نتیجهٔ قابل نمایش می‌دهد؛ stack trace به کاربر نشان داده نمی‌شود.

---

## چه کارهایی می‌کند

### ماشین حساب مهندسی

صفحه کلید معمولی مهندسی است، نه فقط چهار عمل اصلی.

- درجه یا رادیان
- نماد مهندسی (ENG)
- حافظه: MC، MR، M+، M−
- تاریخچه
- Ans
- توابع مثلثاتی، هذلولوی، لگاریتم، نمایی، ریشه، قدر مطلق، فاکتوریل
- اگر یک معادله با یک مساوی بنویسی، برای `x` حل می‌کند

### فرمول‌ها

الان **۲۰۳۱ فرمول نام‌دار** توی **۱۰۱ دسته** است. این‌ها فقط اسم نیستند؛ مقدار مجهول را حساب می‌کنند.

پیش‌فرض یک مجهول است. خانه‌های معلوم را پر می‌کنی، یکی را خالی می‌گذاری یا مجهول را انتخاب می‌کنی، دکمهٔ حل را می‌زنی. اگر معادله از نوع `y = f(...)` باشد و `y` مجهول باشد، طرف راست مستقیم حساب می‌شود. وگرنه معادله برای همان مجهول حل می‌شود.

اگر چند معادله با چند مجهول لازم داری، حالت دستگاه را روشن کن. معادله و مجهول را می‌شود اضافه یا کم کرد.

جستجو روی اسم، شناسه، دسته و خود عبارت کار می‌کند. زبان اسم فرمول با زبان رابط عوض می‌شود.

موضوع‌هایی که پوشش داده شده:

- ریاضی: جبر، هندسه، هندسهٔ مختصاتی، مثلثات، حسابان، جبر خطی، آمار، احتمال، ترکیبیات، دنباله و سری، اعداد مختلط، نظریهٔ اعداد، عدم قطعیت اندازه‌گیری
- ریاضی مهندسی: معادلهٔ دیفرانسیل معمولی و جزئی، لاپلاس، فوریه، حساب برداری، روش عددی، آنالیز مختلط
- توابع خاص: گاما، بتا، خطا، بسل، فوق‌هندسی، انتگرال و تابع بیضوی، زتا و پلی‌لگاریتم، چندجمله‌ای متعامد، ماتیو، ثابت‌های نام‌دار
- فیزیک: سینماتیک، دینامیک، کار و انرژی، دوران، گرانش، نوسان، امواج، سیالات، ترمودینامیک، مدار، الکتروستاتیک، مغناطیس، اپتیک، فیزیک مدرن، هسته‌ای، نجوم، آکوستیک
- شیمی: استوکیومتری، محلول، گاز، اسید و باز، سینتیک، تعادل، ترمودینامیک شیمیایی، الکتروشیمی، خواص کولیگاتیو، محاسبهٔ آلی، ثابت‌های CODATA
- زیست: ژنتیک، بوم‌شناسی، فیزیولوژی، آنزیم، آزمایشگاه، گیاه
- پزشکی و دارو: فرمول بالینی، فارماکوکینتیک، تناسب و تغذیه
- مهندسی: استاتیک و مقاومت، عمران، طراحی ماشین، سیالات، انتقال حرارت، برق، کنترل، سیگنال، ساخت، هوافضا، مهندسی شیمی
- اقتصاد و مالی: خرد، کلان، بهره و وام، سرمایه‌گذاری، بازار
- زمین: اقلیم و زمین، ژئوتکنیک
- رایانه، جمعیت‌شناسی، روان‌فیزیک، آکوستیک موسیقی، رایانش کوانتومی، مقدارهای روزمره

ثابت‌های فیزیکی استاندارد (نور، پلانک، بار الکترون، بولتزمن، آووگادرو، R، g، G، ε0، μ0 و بقیه) هم به‌صورت فرمول قابل استفاده‌اند.

### چندجمله‌ای

ضریب‌های `a6` تا `a0` را می‌دهی، یعنی تا درجهٔ ۶.

- مقدار در یک `x`
- ریشه‌ها
- مشتق (ضریب‌ها)
- انتگرال (ضریب‌ها)

### عددی

- پیدا کردن ریشه توی یک بازه
- انتگرال عددی (اگر فرم بسته باشد همان را هم می‌دهد)
- مشتق در یک نقطه
- معادلهٔ دیفرانسیل مرتبهٔ اول `y' = f(x, y)` با روش RK4، از یک شرط اولیه تا یک `x` نهایی

### شیمی

جدا از فهرست فرمول‌ها است.

- موازنهٔ معادله. مثال: `H2+O2=H2O` می‌شود `2 H2 + O2 = 2 H2O`. برای `Fe+O2=Fe2O3` و سوختن هم کار می‌کند.
- جرم مولی. مثال: آب ۱۸٫۰۱۵، `Ca(OH)2` حدود ۷۴٫۰۹۲. پرانتز و ضریب را می‌فهمد.

واکنش‌هایی که فقط شکل شیمیایی دارند همین‌جا موازنه می‌شوند؛ لازم نیست برای هر واکنش یک فرمول جدا باشد.

### عنصرها

هر ۱۱۸ عنصر:

- عدد اتمی
- نماد
- اسم (سه زبان)
- جرم اتمی
- گروه
- ایزوتوپ‌های مهم با عدد جرمی، جرم و فراوانی (اگر معلوم باشد)

جستجو روی اسم و نماد کار می‌کند.

### منبع‌ها

یک زبانه توضیح می‌دهد این فرمول‌ها از کجا آمده‌اند و از کجا نیامده‌اند. لینک‌ها این‌ها هستند:

- Equation Encyclopedia — نقشهٔ موضوعی و معادله‌های استاندارد همان سرفصل‌ها، نه کپی متن و تمرین آن برنامه
- Wolfram MathWorld — توابع نام‌دار حساب می‌شوند؛ مقاله‌ها کپی نشده
- NIST DLMF — موتور توابع خاص
- ثابت‌های عمومی CODATA / NIST به‌جای رونویسی CRC
- معادله‌هایی که آزمایشگاه‌های PhET درس می‌دهند
- arXiv فقط به‌عنوان آرشیو مقاله، استخراج نشده
- سایت توابع ولفرام — خانواده‌ها با SymPy و SciPy حساب می‌شوند، نه ذخیرهٔ سیصد هزار خط اتحاد

---

## دو برنامه، یک پوشش

عمداً دو کد جدا نوشتم. اگر یکی خراب شود، آن یکی همان فرمول‌ها را دارد.

| | دسکتاپ | وب |
|---|---|---|
| ورود | `cd desktop` بعد `python3 run.py` | `cd web` بعد `python3 run.py` بعد مرورگر روی پورت ۵۰۰۰ |
| ظاهر | پنجرهٔ tkinter | Flask + HTML |
| ماشین حساب | هست | هست |
| فرمول / دستگاه معادلات | هست | هست |
| چندجمله‌ای تا درجه ۶ | هست | هست |
| عددی و RK4 | هست | هست |
| موازنه و جرم مولی | هست | هست |
| جدول تناوبی | هست | هست |
| منبع‌ها | هست | هست |
| en / fa / fi | هست | هست |

وابستگی دسکتاپ: `numpy`، `scipy`، `sympy`. پایتون ۳٫۱۰ به بالا.

وابستگی وب: همان‌ها به‌اضافهٔ `flask`.

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

وب روی `0.0.0.0:5000` گوش می‌دهد.

---

## English

Two separate programs that do the same job. They do not import each other. Each folder has its own engine, its own formula file, its own periodic table, and its own translations. Formula IDs match.

- `desktop` — tkinter window
- `web` — Flask in the browser

Interface languages: English, Persian, Finnish. Labels come from translation files. Persian is right-to-left on the web.

Bad input does not crash the program. The user does not see a stack trace.

### What it does

**Engineering calculator.** Degrees or radians, engineering notation, memory, history, Ans, the usual scientific functions. A single `=` equation is solved for `x`.

**Formulas.** 2031 named formulas in 101 categories. They compute. Default is one unknown: fill the known fields, leave one empty or pick the unknown, press solve. You can switch to a system, then add or remove equations and unknowns. Search uses the name, id, category, and expression.

Coverage includes algebra, geometry, trigonometry, calculus, linear algebra, statistics, probability, combinatorics, sequences, complex numbers, number theory, measurement uncertainty, ODE/PDE, Laplace, Fourier, vector calculus, numerical methods, special functions (gamma, Bessel, hypergeometric, elliptic, zeta, orthogonal polynomials), most of introductory and engineering physics, chemistry, biology, clinical and pharmacokinetic formulas, fitness, civil / mechanical / electrical / chemical / aerospace engineering, heat transfer, control, signals, manufacturing, finance, economics, earth science, geotechnics, computing, demography, psychophysics, musical acoustics, quantum computing, everyday unit conversions, and CODATA constants.

**Polynomials** through degree 6: value, roots, derivative, integral.

**Numerical:** root on an interval, definite integral, derivative at a point, first-order ODE with RK4.

**Chemistry tab:** balance equations (`H2+O2=H2O` → `2 H2 + O2 = 2 H2O`) and molar mass (`H2O` → 18.015). Word-only reaction schemes belong here, not in the named list.

**Elements:** all 118, with Z, mass, and important isotopes.

**Sources tab:** subject map and public constants. Not a dump of Equation Encyclopedia, MathWorld, DLMF, CRC, PhET, arXiv, or the Wolfram Functions Site.

### Run

Python 3.10+. Desktop needs numpy, scipy, sympy. Web needs those plus Flask.

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

Web listens on `0.0.0.0:5000`.
