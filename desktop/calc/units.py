"""Unit-aware evaluation. Independent copy. No pint."""

from __future__ import annotations

import ast
import math
import re
import unicodedata

_DIGIT = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")

# L M T I Theta N J
_L, _M, _T, _I, _TH, _N, _J = range(7)
ZERO = (0, 0, 0, 0, 0, 0, 0)


def _d(*pairs):
    v = [0] * 7
    for i, e in pairs:
        v[i] = e
    return tuple(v)


# name -> (si_factor, dimension, print_symbol)
_UNITS = {
    "m": (1.0, _d((_L, 1)), "m"),
    "meter": (1.0, _d((_L, 1)), "m"),
    "metre": (1.0, _d((_L, 1)), "m"),
    "inch": (0.0254, _d((_L, 1)), "m"),
    "in": (0.0254, _d((_L, 1)), "m"),
    "ft": (0.3048, _d((_L, 1)), "m"),
    "foot": (0.3048, _d((_L, 1)), "m"),
    "yard": (0.9144, _d((_L, 1)), "m"),
    "mile": (1609.344, _d((_L, 1)), "m"),
    "mi": (1609.344, _d((_L, 1)), "m"),
    "angstrom": (1e-10, _d((_L, 1)), "m"),
    "kg": (1.0, _d((_M, 1)), "kg"),
    "g": (0.001, _d((_M, 1)), "kg"),
    "lb": (0.45359237, _d((_M, 1)), "kg"),
    "lbm": (0.45359237, _d((_M, 1)), "kg"),
    "slug": (14.593903, _d((_M, 1)), "kg"),
    "s": (1.0, _d((_T, 1)), "s"),
    "sec": (1.0, _d((_T, 1)), "s"),
    "min": (60.0, _d((_T, 1)), "s"),
    "minute": (60.0, _d((_T, 1)), "s"),
    "hr": (3600.0, _d((_T, 1)), "s"),
    "hour": (3600.0, _d((_T, 1)), "s"),
    "hours": (3600.0, _d((_T, 1)), "s"),
    "day": (86400.0, _d((_T, 1)), "s"),
    "a": (1.0, _d((_I, 1)), "A"),
    "amp": (1.0, _d((_I, 1)), "A"),
    "ampere": (1.0, _d((_I, 1)), "A"),
    "kelvin": (1.0, _d((_TH, 1)), "K"),
    "mol": (1.0, _d((_N, 1)), "mol"),
    "mole": (1.0, _d((_N, 1)), "mol"),
    "cd": (1.0, _d((_J, 1)), "cd"),
    "n": (1.0, _d((_M, 1), (_L, 1), (_T, -2)), "N"),
    "newton": (1.0, _d((_M, 1), (_L, 1), (_T, -2)), "N"),
    "lbf": (4.4482216152605, _d((_M, 1), (_L, 1), (_T, -2)), "N"),
    "pa": (1.0, _d((_M, 1), (_L, -1), (_T, -2)), "Pa"),
    "pascal": (1.0, _d((_M, 1), (_L, -1), (_T, -2)), "Pa"),
    "bar": (1e5, _d((_M, 1), (_L, -1), (_T, -2)), "Pa"),
    "atm": (101325.0, _d((_M, 1), (_L, -1), (_T, -2)), "Pa"),
    "psi": (6894.757293168, _d((_M, 1), (_L, -1), (_T, -2)), "Pa"),
    "torr": (133.322368, _d((_M, 1), (_L, -1), (_T, -2)), "Pa"),
    "mmhg": (133.322368, _d((_M, 1), (_L, -1), (_T, -2)), "Pa"),
    "j": (1.0, _d((_M, 1), (_L, 2), (_T, -2)), "J"),
    "joule": (1.0, _d((_M, 1), (_L, 2), (_T, -2)), "J"),
    "cal": (4.184, _d((_M, 1), (_L, 2), (_T, -2)), "J"),
    "ev": (1.602176634e-19, _d((_M, 1), (_L, 2), (_T, -2)), "J"),
    "wh": (3600.0, _d((_M, 1), (_L, 2), (_T, -2)), "J"),
    "w": (1.0, _d((_M, 1), (_L, 2), (_T, -3)), "W"),
    "watt": (1.0, _d((_M, 1), (_L, 2), (_T, -3)), "W"),
    "hp": (745.699872, _d((_M, 1), (_L, 2), (_T, -3)), "W"),
    "v": (1.0, _d((_M, 1), (_L, 2), (_T, -3), (_I, -1)), "V"),
    "volt": (1.0, _d((_M, 1), (_L, 2), (_T, -3), (_I, -1)), "V"),
    "ohm": (1.0, _d((_M, 1), (_L, 2), (_T, -3), (_I, -2)), "ohm"),
    "ohms": (1.0, _d((_M, 1), (_L, 2), (_T, -3), (_I, -2)), "ohm"),
    "siemens": (1.0, _d((_M, -1), (_L, -2), (_T, 3), (_I, 2)), "S"),
    "c": (1.0, _d((_I, 1), (_T, 1)), "C"),
    "coulomb": (1.0, _d((_I, 1), (_T, 1)), "C"),
    "f": (1.0, _d((_M, -1), (_L, -2), (_T, 4), (_I, 2)), "F"),
    "farad": (1.0, _d((_M, -1), (_L, -2), (_T, 4), (_I, 2)), "F"),
    "henry": (1.0, _d((_M, 1), (_L, 2), (_T, -2), (_I, -2)), "H"),
    "hz": (1.0, _d((_T, -1)), "Hz"),
    "hertz": (1.0, _d((_T, -1)), "Hz"),
    "rpm": (1.0 / 60.0, _d((_T, -1)), "Hz"),
    "wb": (1.0, _d((_M, 1), (_L, 2), (_T, -2), (_I, -1)), "Wb"),
    "t": (1.0, _d((_M, 1), (_T, -2), (_I, -1)), "T"),
    "tesla": (1.0, _d((_M, 1), (_T, -2), (_I, -1)), "T"),
    "l": (0.001, _d((_L, 3)), "m^3"),
    "liter": (0.001, _d((_L, 3)), "m^3"),
    "litre": (0.001, _d((_L, 3)), "m^3"),
    "gal": (0.003785411784, _d((_L, 3)), "m^3"),
    "deg": (math.pi / 180.0, ZERO, "rad"),
    "degree": (math.pi / 180.0, ZERO, "rad"),
    "rad": (1.0, ZERO, "rad"),
    "radian": (1.0, ZERO, "rad"),
}

_PREFIX = {
    "y": 1e-24, "z": 1e-21, "a": 1e-18, "f": 1e-15, "p": 1e-12,
    "n": 1e-9, "u": 1e-6, "µ": 1e-6, "m": 1e-3, "c": 1e-2, "d": 1e-1,
    "k": 1e3, "M": 1e6, "G": 1e9, "T": 1e12, "P": 1e15,
    "meg": 1e6, "da": 10.0,
}

_FUN_NAMES = {
    "sin", "cos", "tan", "asin", "acos", "atan", "sinh", "cosh", "tanh",
    "asinh", "acosh", "atanh", "exp", "log", "ln", "log10", "log2", "sqrt",
    "abs", "floor", "ceil", "factorial", "diff", "integrate", "summation",
    "product", "limit", "series", "factor", "expand", "simplify", "apart",
    "together", "cancel", "solveeq", "pi", "ans",
}

_UNIT_NAMES = sorted(_UNITS.keys(), key=len, reverse=True)

_DERIVED = [
    (_d((_M, 1), (_L, 2), (_T, -3), (_I, -1)), "V"),
    (_d((_M, 1), (_L, 2), (_T, -3), (_I, -2)), "ohm"),
    (_d((_M, 1), (_L, 2), (_T, -3)), "W"),
    (_d((_M, 1), (_L, 2), (_T, -2)), "J"),
    (_d((_M, 1), (_L, 1), (_T, -2)), "N"),
    (_d((_M, 1), (_L, -1), (_T, -2)), "Pa"),
    (_d((_M, -1), (_L, -2), (_T, 4), (_I, 2)), "F"),
    (_d((_M, 1), (_L, 2), (_T, -2), (_I, -2)), "H"),
    (_d((_I, 1), (_T, 1)), "C"),
    (_d((_T, -1)), "Hz"),
    (_d((_L, 1), (_T, -1)), "m/s"),
    (_d((_L, 1), (_T, -2)), "m/s^2"),
    (_d((_L, 2)), "m^2"),
    (_d((_L, 3)), "m^3"),
    (_d((_I, 1)), "A"),
    (_d((_L, 1)), "m"),
    (_d((_M, 1)), "kg"),
    (_d((_T, 1)), "s"),
    (_d((_TH, 1)), "K"),
    (_d((_N, 1)), "mol"),
]


class _Q:
    __slots__ = ("v", "d")

    def __init__(self, v, d=ZERO):
        self.v = float(v.v) if isinstance(v, _Q) else float(v)
        dim = []
        for x in (d or ZERO):
            if isinstance(x, _Q):
                dim.append(int(round(x.v)))
            else:
                try:
                    dim.append(int(x))
                except Exception:
                    dim.append(0)
        self.d = tuple(dim) if dim else ZERO

    def _bin(self, other, op, dim_op):
        o = other if isinstance(other, _Q) else _Q(other, ZERO)
        return _Q(op(self.v, o.v), dim_op(self.d, o.d))

    def __add__(self, o):
        o = o if isinstance(o, _Q) else _Q(o, ZERO)
        if self.d != o.d:
            raise ValueError("dim")
        return _Q(self.v + o.v, self.d)

    def __radd__(self, o):
        return self.__add__(o)

    def __sub__(self, o):
        o = o if isinstance(o, _Q) else _Q(o, ZERO)
        if self.d != o.d:
            raise ValueError("dim")
        return _Q(self.v - o.v, self.d)

    def __rsub__(self, o):
        o = o if isinstance(o, _Q) else _Q(o, ZERO)
        if self.d != o.d:
            raise ValueError("dim")
        return _Q(o.v - self.v, self.d)

    def __mul__(self, o):
        o = o if isinstance(o, _Q) else _Q(o, ZERO)
        return _Q(self.v * o.v, tuple(a + b for a, b in zip(self.d, o.d)))

    def __rmul__(self, o):
        return self.__mul__(o)

    def __truediv__(self, o):
        o = o if isinstance(o, _Q) else _Q(o, ZERO)
        if o.v == 0:
            raise ZeroDivisionError
        return _Q(self.v / o.v, tuple(a - b for a, b in zip(self.d, o.d)))

    def __rtruediv__(self, o):
        o = o if isinstance(o, _Q) else _Q(o, ZERO)
        if self.v == 0:
            raise ZeroDivisionError
        return _Q(o.v / self.v, tuple(a - b for a, b in zip(o.d, self.d)))

    def __pow__(self, o):
        e = o.v if isinstance(o, _Q) else float(o)
        ie = int(round(e))
        if abs(e - ie) > 1e-12:
            if self.d != ZERO:
                raise ValueError("dim")
            return _Q(self.v ** e, ZERO)
        return _Q(self.v ** e, tuple(a * ie for a in self.d))

    def __neg__(self):
        return _Q(-self.v, self.d)

    def __pos__(self):
        return self

    def __abs__(self):
        return _Q(abs(self.v), self.d)


def _split_unit(token: str):
    raw = token.replace("Ω", "ohm").replace("ω", "ohm").replace("µ", "u")
    low = raw.lower()
    if low in {"k", "K"}:
        return None
    for name in _UNIT_NAMES:
        if low == name or low.endswith(name):
            if low == name:
                return 1.0, _UNITS[name]
            pref = raw[: len(raw) - len(name)]
            plow = pref.lower()
            if plow in _PREFIX:
                return _PREFIX[plow], _UNITS[name]
            if pref in _PREFIX:
                return _PREFIX[pref], _UNITS[name]
            if pref == "":
                return 1.0, _UNITS[name]
    return None


def _looks_like_units(text: str) -> bool:
    if not text:
        return False
    low = text.lower()
    if any(fn + "(" in low for fn in ("diff", "integrate", "summation", "factor", "expand", "simplify", "solveeq", "limit", "series")):
        return False
    blob = re.sub(r"[0-9eE+.\-*/()^]", " ", text)
    parts = [p for p in re.split(r"[^A-Za-zµΩω°]+", blob) if p]
    for p in parts:
        if p.lower() in _FUN_NAMES:
            continue
        if _split_unit(p) is not None:
            return True
        if p.lower() in {"kohm", "mohm", "uohm", "mohm"}:
            return True
    if re.search(r"[0-9.][ \t]*[Ωω]", text):
        return True
    return False


_NUM = r"(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+\-]?[0-9]+)?"


def _rewrite(text: str) -> str:
    s = unicodedata.normalize("NFKC", text).translate(_DIGIT)
    s = s.replace("×", "*").replace("÷", "/").replace("−", "-").replace("^", "**")
    s = s.replace("π", "pi")
    s = re.sub(r"(\d),(\d)", r"\1.\2", s)

    def repl(m):
        num = m.group(1)
        unit = (m.group(2) or "").strip()
        if not unit:
            return f"_Q({num})"
        got = _split_unit(unit)
        if got is None:
            # engineering: 2k meaning 2000, leftover letter prefix only
            u = unit
            if u.lower() in _PREFIX and u.lower() not in _FUN_NAMES:
                return f"_Q({num}*{_PREFIX[u.lower()]})"
            return m.group(0)
        scale, info = got
        fac, dim, _sym = info
        return f"_Q({float(num) * scale * fac}, {dim})"

    s = re.sub(rf"({_NUM})\s*([A-Za-zµΩω°]+)", repl, s)
    s = re.sub(rf"({_NUM})(?![0-9.eE])", r"_Q(\1)", s)
    s = s.replace("pi", "_Q(" + str(math.pi) + ")")
    return s


_ALLOWED_CALLS = {
    "sin": math.sin, "cos": math.cos, "tan": math.tan,
    "asin": math.asin, "acos": math.acos, "atan": math.atan,
    "sinh": math.sinh, "cosh": math.cosh, "tanh": math.tanh,
    "exp": math.exp, "log": math.log, "ln": math.log, "log10": math.log10,
    "log2": math.log2, "sqrt": math.sqrt, "abs": abs, "floor": math.floor,
}


def _eval_node(node):
    if isinstance(node, ast.Expression):
        return _eval_node(node.body)
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return _Q(node.value)
        raise ValueError("bad")
    if isinstance(node, ast.UnaryOp):
        v = _eval_node(node.operand)
        if isinstance(node.op, ast.USub):
            return -v
        if isinstance(node.op, ast.UAdd):
            return v
        raise ValueError("op")
    if isinstance(node, ast.BinOp):
        a, b = _eval_node(node.left), _eval_node(node.right)
        if isinstance(node.op, ast.Add):
            return a + b
        if isinstance(node.op, ast.Sub):
            return a - b
        if isinstance(node.op, ast.Mult):
            return a * b
        if isinstance(node.op, ast.Div):
            return a / b
        if isinstance(node.op, ast.Pow):
            return a ** b
        raise ValueError("op")
    if isinstance(node, ast.Call):
        if not isinstance(node.func, ast.Name):
            raise ValueError("call")
        name = node.func.id
        if name == "_Q":
            args = [_eval_node(a) if not isinstance(a, ast.Constant) else a.value for a in node.args]
            if len(args) == 1:
                v = args[0]
                return v if isinstance(v, _Q) else _Q(v)
            v = args[0].v if isinstance(args[0], _Q) else float(args[0])
            d = args[1]
            if isinstance(d, ast.Tuple):
                d = tuple(x.value if isinstance(x, ast.Constant) else int(_eval_node(x).v) for x in d.elts)
            elif isinstance(d, (tuple, list)):
                d = tuple(d)
            return _Q(v, d)
        if name not in _ALLOWED_CALLS:
            raise ValueError("fn")
        args = [_eval_node(a) for a in node.args]
        if any(a.d != ZERO for a in args):
            # sin(30 deg) already converted deg to rad dimensionless
            if name in {"sin", "cos", "tan"} and args[0].d == ZERO:
                pass
            else:
                raise ValueError("dim")
        return _Q(_ALLOWED_CALLS[name](args[0].v))
    if isinstance(node, ast.Name):
        if node.id == "e":
            return _Q(math.e)
        raise ValueError("name")
    if isinstance(node, ast.Tuple):
        return tuple(_eval_node(x) if not isinstance(x, ast.Constant) else x.value for x in node.elts)
    raise ValueError("node")


def _unit_label(dim) -> str:
    if dim == ZERO:
        return ""
    for d, name in _DERIVED:
        if d == dim:
            return name
    bits = []
    names = ["m", "kg", "s", "A", "K", "mol", "cd"]
    for i, e in enumerate(dim):
        if e == 1:
            bits.append(names[i])
        elif e == -1:
            bits.append(names[i] + "^-1")
        elif e:
            bits.append(f"{names[i]}^{e}")
    return " ".join(bits)


def _pretty(v: float, unit: str, eng: bool) -> str:
    if not math.isfinite(v):
        return "undefined"
    if abs(v) < 1e-18:
        return "0" + (f" {unit}" if unit else "")
    prefixes = [(1e12, "T"), (1e9, "G"), (1e6, "M"), (1e3, "k"), (1, ""), (1e-3, "m"), (1e-6, "u"), (1e-9, "n"), (1e-12, "p")]
    shown, pref = v, ""
    if unit or eng:
        ax = abs(v)
        for scale, name in prefixes:
            if ax >= scale * 0.999:
                shown = v / scale
                pref = name
                break
        else:
            shown = v / 1e-12
            pref = "p"
    text = f"{shown:.12g}"
    return f"{text} {pref}{unit}".strip()


def try_eval(text: str, eng: bool = False, lang: str = "en"):
    """Return a result dict if the line has units, else None."""
    raw = text or ""
    if not _looks_like_units(raw):
        # 12V/2k with no space after k
        if not re.search(r"[0-9.][ \t]*[A-Za-zΩωµ]", raw):
            return None
        if not _looks_like_units(raw + " "):
            # still try rewrite if a number sits next to a unit letter
            if not re.search(r"[0-9][A-Za-zΩ]", raw):
                return None
    try:
        src = _rewrite(raw)
        # 12 V / 2k  -> treat trailing prefix-only after voltage as ohm
        if re.search(r"/_Q\([0-9.eE+\-]+\)\s*$", src) and "V" in raw:
            pass
        tree = ast.parse(src, mode="eval")
        q = _eval_node(tree)
        if not isinstance(q, _Q):
            return None
        # engineering: 12V/2k with dimensionless kilo after volts -> ohm
        if q.d == _UNITS["v"][1] and re.search(r"/\s*[0-9.]+[kKmM]\b", raw) and "ohm" not in raw.lower() and "Ω" not in raw:
            # 12V/2k would have been V / 2000 = 0.006 V; reinterpret as V/ohm
            src2 = _rewrite(re.sub(r"([0-9.]+)([kKmM])\b", r"\1\2ohm", raw))
            q2 = _eval_node(ast.parse(src2, mode="eval"))
            if isinstance(q2, _Q) and q2.d == _UNITS["a"][1]:
                q = q2
        unit = _unit_label(q.d)
        shown = _pretty(q.v, unit, eng)
        steps = {
            "en": [f"You typed {raw}.", "Numbers were converted to SI units.", f"The result is {shown}."],
            "fa": [f"نوشتی {raw}.", "عددها به SI تبدیل شدند.", f"نتیجه: {shown}."],
            "fi": [f"Kirjoitit {raw}.", "Luvut muunnettiin SI-yksikoihin.", f"Tulos: {shown}."],
        }
        return {
            "ok": True,
            "value": q.v,
            "text": shown,
            "exact": shown,
            "unit": unit,
            "steps": steps.get(lang) or steps["en"],
            "latex": shown.replace("ohm", r"\Omega"),
        }
    except Exception:
        return None
