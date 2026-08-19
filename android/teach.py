"""Teacher-style steps for the Android app. Independent copy."""
from __future__ import annotations


def _p(lang: str) -> dict:
    packs = {
        "en": {
            "typed": "You typed {raw}.",
            "clean": "After cleanup that is {cleaned}.",
            "deg": "Trigonometry is using degrees, so sin(x) means sin(x · π/180).",
            "rad": "Trigonometry is using radians.",
            "cas": "This is an algebra command, so the exact form is kept.",
            "exact": "The exact form is {exact}.",
            "number": "As a number that is {text}.",
            "eq_typed": "You typed the equation {left} = {right}.",
            "solve_for": "We solve for {who}.",
            "sols": "The solution is {text}.",
            "no_sol": "No solution came out. The program shows 0 instead of crashing.",
            "eq": "The formula is {eq}.",
            "want": "We want {u}.",
            "known": "What we already have: {bits}.",
            "alone_l": "{u} is already alone on the left, so we only compute the right-hand side.",
            "alone_r": "{u} is already alone on the right, so we only compute the left-hand side.",
            "plug": "Put the known numbers in: {expr}.",
            "rearr": "Move things so {u} is alone. That gives {u} = {sym}.",
            "numeric": "Now compute it: {u} = {text} {unit}.",
            "more": "There is more than one value: {all}.",
            "sys_eq": "The equations are:",
            "sys_u": "The unknowns are {who}.",
            "sys_one": "One solution is {row}.",
            "sys_none": "The system did not give a solution. Showing 0.",
            "poly_val": "Evaluate the polynomial at x = {x}.",
            "poly_out": "p(x) = {text}. Degree {deg}.",
            "poly_roots": "The roots of this polynomial are {roots}.",
            "n_root": "Find x where f(x) = 0 on [{a}, {b}].",
            "n_int": "Integrate f(x) from {a} to {b}.",
            "n_der": "Differentiate f(x) and evaluate at x = {a}.",
            "n_ode": "Step y' = f(x,y) from x = {a}, y = {y0} to x = {b}.",
            "got": "The result is {text}.",
            "chem_in": "The input was {raw}.",
            "chem_out": "After balancing: {text}.",
            "molar_out": "Molar mass is {text} g/mol.",
        },
        "fa": {
            "typed": "نوشتی {raw}.",
            "clean": "بعد از پاکسازی می‌شود {cleaned}.",
            "deg": "مثلثات روی درجه است، یعنی sin(x) یعنی sin(x · π/180).",
            "rad": "مثلثات روی رادیان است.",
            "cas": "این یک دستور جبری است، پس شکل دقیق نگه داشته می‌شود.",
            "exact": "شکل دقیق: {exact}.",
            "number": "مقدار عددی: {text}.",
            "eq_typed": "معادله‌ای که نوشتی: {left} = {right}.",
            "solve_for": "مجهول {who} است.",
            "sols": "جواب: {text}.",
            "no_sol": "جوابی درنیامد. به‌جای قفل شدن برنامه، ۰ نشان داده شد.",
            "eq": "فرمول این است: {eq}.",
            "want": "دنبال {u} هستیم.",
            "known": "چیزهایی که داریم: {bits}.",
            "alone_l": "{u} همین حالا سمت چپ تنهاست. فقط سمت راست را حساب می‌کنیم.",
            "alone_r": "{u} همین حالا سمت راست تنهاست. فقط سمت چپ را حساب می‌کنیم.",
            "plug": "عددها را می‌گذاریم داخل فرمول: {expr}.",
            "rearr": "چیزها را جابه‌جا می‌کنیم تا {u} تنها بماند: {u} = {sym}.",
            "numeric": "حالا حساب می‌کنیم: {u} = {text} {unit}.",
            "more": "بیش از یک جواب هست: {all}.",
            "sys_eq": "معادله‌ها این‌ها هستند:",
            "sys_u": "مجهول‌ها: {who}.",
            "sys_one": "یک جواب: {row}.",
            "sys_none": "دستگاه جواب نداد. ۰ نشان داده شد.",
            "poly_val": "چندجمله‌ای را در x = {x} حساب می‌کنیم.",
            "poly_out": "p(x) = {text}. درجه {deg}.",
            "poly_roots": "ریشه‌ها: {roots}.",
            "n_root": "x را پیدا کن که f(x) = 0 روی [{a}, {b}].",
            "n_int": "انتگرال f(x) از {a} تا {b}.",
            "n_der": "مشتق f(x) در x = {a}.",
            "n_ode": "y' = f(x,y) را از x = {a}، y = {y0} تا x = {b} جلو می‌بریم.",
            "got": "نتیجه: {text}.",
            "chem_in": "ورودی: {raw}.",
            "chem_out": "بعد از موازنه: {text}.",
            "molar_out": "جرم مولی {text} گرم بر مول است.",
        },
        "fi": {
            "typed": "Kirjoitit {raw}.",
            "clean": "Siivouksen jalkeen: {cleaned}.",
            "deg": "Trigonometria kayttaa asteita, eli sin(x) on sin(x · π/180).",
            "rad": "Trigonometria kayttaa radiaaneja.",
            "cas": "Tama on algebra-komento, joten tarkka muoto sailytetaan.",
            "exact": "Tarkka muoto: {exact}.",
            "number": "Lukuna: {text}.",
            "eq_typed": "Yhtalo oli {left} = {right}.",
            "solve_for": "Ratkaistaan {who}.",
            "sols": "Ratkaisu: {text}.",
            "no_sol": "Ratkaisua ei tullut. Naytetaan 0.",
            "eq": "Kaava on {eq}.",
            "want": "Etsitaan {u}.",
            "known": "Tunnetut: {bits}.",
            "alone_l": "{u} on jo yksin vasemmalla. Lasketaan vain oikea puoli.",
            "alone_r": "{u} on jo yksin oikealla. Lasketaan vain vasen puoli.",
            "plug": "Sijoitetaan tunnetut: {expr}.",
            "rearr": "Siirretaan termit niin etta {u} on yksin: {u} = {sym}.",
            "numeric": "Lasketaan: {u} = {text} {unit}.",
            "more": "Arvoja on useita: {all}.",
            "sys_eq": "Yhtalot:",
            "sys_u": "Tuntemattomat: {who}.",
            "sys_one": "Yksi ratkaisu: {row}.",
            "sys_none": "Ryhma ei antanut ratkaisua. Naytetaan 0.",
            "poly_val": "Lasketaan polynomi kohdassa x = {x}.",
            "poly_out": "p(x) = {text}. Aste {deg}.",
            "poly_roots": "Juuret: {roots}.",
            "n_root": "Etsi x jolla f(x) = 0 valilla [{a}, {b}].",
            "n_int": "Integroi f(x) valilla {a} … {b}.",
            "n_der": "Derivoi f(x) ja laske kohdassa x = {a}.",
            "n_ode": "Askella y' = f(x,y) alkaen x = {a}, y = {y0} arvoon x = {b}.",
            "got": "Tulos: {text}.",
            "chem_in": "Syote: {raw}.",
            "chem_out": "Tasapainotuksen jalkeen: {text}.",
            "molar_out": "Moolimassa on {text} g/mol.",
        },
    }
    return packs.get(lang) or packs["en"]


def _t(lang: str, key: str, **kw) -> str:
    text = _p(lang).get(key) or _p("en").get(key, key)
    try:
        return text.format(**kw)
    except Exception:
        return text


def format_steps(lines: list[str]) -> str:
    out = []
    n = 1
    for line in lines:
        if not line:
            continue
        if line.endswith(":"):
            out.append(f"{n}) {line}")
        else:
            out.append(f"{n}) {line}")
        n += 1
    return "\n".join(out)


def steps_eval(lang: str, raw: str, cleaned: str, exact: str, text: str, angle: str, cas: bool = False) -> list[str]:
    lines = [_t(lang, "typed", raw=raw or "0")]
    if cleaned and cleaned != (raw or "").replace(" ", ""):
        lines.append(_t(lang, "clean", cleaned=cleaned))
    trig = any(name in (cleaned or "") for name in ("sin", "cos", "tan", "asin", "acos", "atan"))
    if trig:
        lines.append(_t(lang, "deg" if angle == "DEG" else "rad"))
    if cas:
        lines.append(_t(lang, "cas"))
    if exact:
        lines.append(_t(lang, "exact", exact=exact))
    if text and text != exact:
        lines.append(_t(lang, "number", text=text))
    return lines


def steps_equation(lang: str, left: str, right: str, who: str, text: str, found: bool) -> list[str]:
    lines = [
        _t(lang, "eq_typed", left=left, right=right),
        _t(lang, "solve_for", who=", ".join(who) if isinstance(who, (list, tuple)) else who),
    ]
    if found:
        lines.append(_t(lang, "sols", text=text))
    else:
        lines.append(_t(lang, "no_sol"))
    return lines


def steps_formula(
    lang: str,
    eq: str,
    target: str,
    known: dict,
    mode: str,
    plugged: str,
    symbolic: str,
    text: str,
    unit: str,
    allsols: list[str] | None = None,
) -> list[str]:
    bits = ", ".join(f"{k} = {v}" for k, v in known.items()) or "—"
    lines = [
        _t(lang, "eq", eq=eq),
        _t(lang, "want", u=target),
        _t(lang, "known", bits=bits),
    ]
    if mode == "left":
        lines.append(_t(lang, "alone_l", u=target))
    elif mode == "right":
        lines.append(_t(lang, "alone_r", u=target))
    else:
        if symbolic:
            lines.append(_t(lang, "rearr", u=target, sym=symbolic))
    if plugged:
        lines.append(_t(lang, "plug", expr=plugged))
    lines.append(_t(lang, "numeric", u=target, text=text, unit=unit or ""))
    if allsols and len(allsols) > 1:
        lines.append(_t(lang, "more", all=", ".join(allsols)))
    return lines


def steps_system(lang: str, eqs: list[str], unknowns: list[str], rows: list[dict]) -> list[str]:
    lines = [_t(lang, "sys_eq")]
    for eq in eqs:
        lines.append("    " + eq)
    lines.append(_t(lang, "sys_u", who=", ".join(unknowns)))
    if not rows:
        lines.append(_t(lang, "sys_none"))
        return lines
    for row in rows:
        bits = "   ".join(f"{k} = {v}" for k, v in row.items())
        lines.append(_t(lang, "sys_one", row=bits))
    return lines


def steps_poly(lang: str, kind: str, x, text: str, deg, roots) -> list[str]:
    if kind == "roots":
        return [_t(lang, "poly_roots", roots=", ".join(roots or []) or "0")]
    return [
        _t(lang, "poly_val", x=x),
        _t(lang, "poly_out", text=text, deg=deg),
    ]


def steps_numeric(lang: str, kind: str, a, b, y0, text: str) -> list[str]:
    key = {"root": "n_root", "integral": "n_int", "deriv": "n_der", "ode": "n_ode"}.get(kind, "got")
    lines = [_t(lang, key, a=a, b=b, y0=y0)]
    lines.append(_t(lang, "got", text=text))
    return lines


def steps_chem(lang: str, raw: str, text: str, molar: bool = False) -> list[str]:
    if molar:
        return [_t(lang, "chem_in", raw=raw), _t(lang, "molar_out", text=text)]
    return [_t(lang, "chem_in", raw=raw), _t(lang, "chem_out", text=text)]
