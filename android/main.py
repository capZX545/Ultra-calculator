"""Android app. Independent of the desktop and web folders."""

from __future__ import annotations

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.factory import Factory
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.screenmanager import Screen, ScreenManager, SlideTransition
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from kivy.utils import platform

import algorithms
import chemtools
import core
import lookup
import circuits
import circguide
import seqfind
import problems
import graphs
import matrixlab
import statsdata
import triangle
import sessionstore
import latexout
import teach
from strings import ui_text

if platform not in ("android", "ios"):
    from kivy.config import Config

    Config.set("graphics", "width", "400")
    Config.set("graphics", "height", "780")

Window.softinput_mode = "below_target"

BG = (0.11, 0.12, 0.14, 1)
PANEL = (0.15, 0.17, 0.20, 1)
BTN = (0.20, 0.22, 0.26, 1)
ACCENT = (0.77, 0.64, 0.35, 1)
FG = (0.91, 0.92, 0.93, 1)
MUTED = (0.60, 0.64, 0.68, 1)
INK = (0.07, 0.08, 0.10, 1)
ON = (0.24, 0.42, 0.33, 1)


def t(lang: str, key: str) -> str:
    return ui_text(lang, key)


def fmt_steps(lines) -> str:
    return teach.format_steps(list(lines or []))


class DarkButton(Button):
    def __init__(self, text="", accent=False, **kwargs):
        super().__init__(
            text=text,
            background_normal="",
            background_down="",
            background_color=ACCENT if accent else BTN,
            color=(0.11, 0.12, 0.14, 1) if accent else FG,
            font_size=dp(14),
            size_hint_y=None,
            height=dp(42),
            **kwargs,
        )


class DarkInput(TextInput):
    def __init__(self, **kwargs):
        kwargs.setdefault("background_color", INK)
        kwargs.setdefault("foreground_color", FG)
        kwargs.setdefault("cursor_color", ACCENT)
        kwargs.setdefault("multiline", False)
        kwargs.setdefault("font_size", dp(15))
        kwargs.setdefault("size_hint_y", None)
        kwargs.setdefault("height", dp(42))
        kwargs.setdefault("padding", [dp(8), dp(10)])
        super().__init__(**kwargs)
        self.bind(focus=self._mark)

    def _mark(self, _w, focused):
        if focused:
            app = App.get_running_app()
            if app:
                app.last_field = self


class RowBtn(RecycleDataViewBehavior, Button):
    index = 0
    kind = "formula"

    def __init__(self, **kwargs):
        super().__init__(
            background_normal="",
            background_color=PANEL,
            color=FG,
            font_size=dp(14),
            halign="left",
            valign="middle",
            text_size=(None, None),
            **kwargs,
        )

    def refresh_view_attrs(self, rv, index, data):
        self.index = index
        self.kind = data.get("kind", "formula")
        self.text = data.get("text", "")
        self.halign = "right" if App.get_running_app().lang == "fa" else "left"
        return super().refresh_view_attrs(rv, index, data)

    def on_release(self):
        app = App.get_running_app()
        if self.kind == "formula":
            app.open_formula(self.index)
        elif self.kind == "algo":
            app.open_algo(self.index)
        elif self.kind == "element":
            app.open_element(self.index)
        elif self.kind == "cat":
            app.pick_category(self.index)
        elif self.kind == "acat":
            app.pick_algo_cat(self.index)


Factory.register("RowBtn", cls=RowBtn)


class ListView(RecycleView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.viewclass = "RowBtn"
        layout = RecycleBoxLayout(
            default_size=(None, dp(44)),
            default_size_hint=(1, None),
            size_hint_y=None,
            orientation="vertical",
            spacing=dp(2),
        )
        layout.bind(minimum_height=layout.setter("height"))
        self.add_widget(layout)


class UltraAndroid(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.lang = "en"
        self.angle = "DEG"
        self.eng = False
        self.ans = 0
        self.memory = 0.0
        self.last_field = None
        self.mode = "calc"
        self.formula_rows = []
        self.algo_rows = []
        self.element_rows = []
        self.cat_rows = []
        self.acat_rows = []
        self.current_formula = None
        self.current_algo = None
        self.var_inputs = {}
        self.unknown = ""
        self.sm = None
        self.screen = None
        self.lookup_box = None
        self.hits_box = None
        self.nav_bar = None
        self.title_lbl = None
        self.lang_spin = None

    def tr(self, key: str) -> str:
        return t(self.lang, key)

    def build(self):
        self.title = "Ultra Calculator"
        Window.clearcolor = BG
        root = BoxLayout(orientation="vertical", padding=dp(8), spacing=dp(6))

        top = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(6))
        self.title_lbl = Label(text=self.tr("title"), color=ACCENT, bold=True, font_size=dp(16), halign="left")
        self.lang_spin = Spinner(text="en", values=["en", "fa", "fi"], size_hint_x=None, width=dp(72),
                                 background_normal="", background_color=BTN, color=FG)
        self.lang_spin.bind(text=self._on_lang)
        top.add_widget(self.title_lbl)
        top.add_widget(self.lang_spin)
        root.add_widget(top)

        nav_scroll = ScrollView(size_hint_y=None, height=dp(44), do_scroll_y=False, bar_width=0)
        self.nav_bar = BoxLayout(size_hint_x=None, spacing=dp(4), padding=0)
        self.nav_bar.bind(minimum_width=self.nav_bar.setter("width"))
        nav_scroll.add_widget(self.nav_bar)
        root.add_widget(nav_scroll)

        look = BoxLayout(size_hint_y=None, height=dp(42), spacing=dp(6))
        look.add_widget(Label(text=self.tr("lookup"), color=ACCENT, size_hint_x=None, width=dp(70), font_size=dp(13)))
        self.lookup_box = DarkInput(hint_text=self.tr("lookup_hint"))
        self.lookup_box.bind(text=lambda *_: Clock.schedule_once(lambda dt: self._run_lookup(), 0.12))
        look.add_widget(self.lookup_box)
        ins = DarkButton(text=self.tr("insert"), accent=True, size_hint_x=None, width=dp(80))
        ins.bind(on_release=lambda *_: self._insert_lookup())
        look.add_widget(ins)
        root.add_widget(look)
        self.hits_box = BoxLayout(size_hint_y=None, height=dp(36), spacing=dp(4))
        root.add_widget(self.hits_box)

        self.sm = ScreenManager(transition=SlideTransition(duration=0.12))
        self.sm.add_widget(self._calc_screen())
        self.sm.add_widget(self._formulas_screen())
        self.sm.add_widget(self._fsolve_screen())
        self.sm.add_widget(self._poly_screen())
        self.sm.add_widget(self._numeric_screen())
        self.sm.add_widget(self._algo_screen())
        self.sm.add_widget(self._arun_screen())
        self.sm.add_widget(self._chem_screen())
        self.sm.add_widget(self._elements_screen())
        self.sm.add_widget(self._edetail_screen())
        self.sm.add_widget(self._sources_screen())
        self.sm.add_widget(self._problems_screen())
        self.sm.add_widget(self._circuits_screen())
        self.sm.add_widget(self._graph_screen())
        self.sm.add_widget(self._matrix_screen())
        self.sm.add_widget(self._stats_screen())
        self.sm.add_widget(self._triangle_screen())
        self.sm.add_widget(self._seq_screen())
        root.add_widget(self.sm)

        self._paint_nav()
        self.go("calc")
        Clock.schedule_once(lambda dt: self._load_lists(), 0.2)
        return root

    def _on_lang(self, _spin, value):
        self.lang = value or "en"
        self.title_lbl.text = self.tr("title")
        self._paint_nav()
        self._load_lists()
        if hasattr(self, "prob_hint") and self.prob_hint:
            self.prob_hint.text = self.tr("problem_hint")
        if hasattr(self, "cir_hint") and self.cir_hint:
            self.cir_hint.text = self.tr("circuit_hint")
            self._cir_send("start")
        if hasattr(self, "seq_hint") and self.seq_hint:
            self.seq_hint.text = self.tr("seq_hint")
        src = self.sm.get_screen("sources")
        if hasattr(src, "reload"):
            src.reload()

    def _paint_nav(self):
        self.nav_bar.clear_widgets()
        items = [
            ("calc", "calc"),
            ("formulas", "formulas"),
            ("poly", "poly"),
            ("numeric", "numeric"),
            ("algo", "algo"),
            ("chem", "chem"),
            ("elements", "elements"),
            ("sources", "sources"),
            ("problems", "problems"),
            ("circuits", "circuits"),
            ("graph", "graph"),
            ("matrix", "matrix"),
            ("stats", "stats"),
            ("triangle", "triangle"),
            ("seq", "seq"),
        ]
        for mode, key in items:
            b = DarkButton(text=self.tr(key), accent=(self.mode == mode))
            b.size_hint_x = None
            b.width = dp(110)
            b.bind(on_release=lambda _w, m=mode: self.go(m))
            self.nav_bar.add_widget(b)

    def go(self, mode: str):
        self.mode = mode
        mapping = {
            "calc": "calc",
            "formulas": "formulas",
            "poly": "poly",
            "numeric": "numeric",
            "algo": "algo",
            "chem": "chem",
            "elements": "elements",
            "sources": "sources",
            "problems": "problems",
            "circuits": "circuits",
            "graph": "graph",
            "matrix": "matrix",
            "stats": "stats",
            "triangle": "triangle",
            "seq": "seq",
        }
        self.sm.current = mapping.get(mode, "calc")
        self._paint_nav()
        if mode == "calc" and self.screen:
            self.screen.focus = True

    def _load_lists(self):
        self.refresh_categories()
        self.refresh_formulas()
        self.refresh_algos()
        self.refresh_elements()

    # ----- lookup -----
    def _run_lookup(self):
        self.hits_box.clear_widgets()
        rows = lookup.lookup(self.lookup_box.text, self.lang)
        self.lookup_pick = rows[0] if rows else None
        for i, row in enumerate(rows[:4]):
            label = f"{row['label']} {row['text']}"
            b = DarkButton(text=label[:28], accent=(i == 0))
            b.font_size = dp(11)
            b.bind(on_release=lambda _w, r=row: self._pick_lookup(r))
            self.hits_box.add_widget(b)

    def _pick_lookup(self, row):
        self.lookup_pick = row
        self._insert_lookup()

    def _insert_lookup(self):
        row = getattr(self, "lookup_pick", None)
        if not row:
            return
        text = str(row.get("insert") or row.get("text") or "")
        field = self.last_field
        if field is None and self.screen is not None:
            field = self.screen
        if field is None:
            return
        field.insert_text(text)
        field.focus = True

    # ----- calculator -----
    def _calc_screen(self):
        sc = Screen(name="calc")
        box = BoxLayout(orientation="vertical", spacing=dp(6))
        self.screen = DarkInput(text="0", font_size=dp(22), height=dp(56), halign="right")
        self.screen.bind(on_text_validate=lambda *_: self._eval())
        box.add_widget(self.screen)
        self.calc_hint = Label(text=self.tr("kbd_hint"), color=MUTED, font_size=dp(11),
                               size_hint_y=None, height=dp(36), text_size=(dp(360), None), halign="left")
        box.add_widget(self.calc_hint)
        self.calc_steps = Label(text="", color=FG, font_size=dp(12), size_hint_y=None, height=dp(90),
                                text_size=(dp(360), dp(90)), valign="top", halign="left")
        box.add_widget(self.calc_steps)
        keys = [
            ["AC", "C", self.tr("deg"), "ENG"],
            ["sin", "cos", "tan", "/"],
            ["ln", "log", "sqrt", "*"],
            ["7", "8", "9", "-"],
            ["4", "5", "6", "+"],
            ["1", "2", "3", "^"],
            ["0", ".", "pi", "="],
        ]
        grid = GridLayout(cols=4, spacing=dp(4), size_hint_y=1)
        self.deg_btn = None
        for row in keys:
            for lab in row:
                accent = lab == "="
                b = DarkButton(text=lab, accent=accent)
                b.height = dp(46)
                if lab in (self.tr("deg"), "DEG", "RAD") or lab == self.tr("deg"):
                    self.deg_btn = b
                    b.text = self.tr("deg") if self.angle == "DEG" else self.tr("rad")
                    b.bind(on_release=lambda *_: self._toggle_angle())
                elif lab == "ENG":
                    b.bind(on_release=lambda *_: self._toggle_eng())
                else:
                    b.bind(on_release=lambda _w, s=lab: self._key(s))
                grid.add_widget(b)
        box.add_widget(grid)
        sc.add_widget(box)
        return sc

    def _toggle_angle(self):
        self.angle = "RAD" if self.angle == "DEG" else "DEG"
        if self.deg_btn:
            self.deg_btn.text = self.tr("deg") if self.angle == "DEG" else self.tr("rad")

    def _toggle_eng(self):
        self.eng = not self.eng

    def _key(self, lab: str):
        mapping = {
            "sin": "sin(", "cos": "cos(", "tan": "tan(",
            "ln": "ln(", "log": "log10(", "sqrt": "sqrt(",
            "pi": "pi", "^": "**",
        }
        if lab == "AC":
            self.screen.text = "0"
            return
        if lab == "C":
            self.screen.text = self.screen.text[:-1] or "0"
            return
        if lab == "=":
            self._eval()
            return
        cur = self.screen.text
        add = mapping.get(lab, lab)
        if cur == "0" and add[:1].isdigit():
            self.screen.text = add
        else:
            self.screen.text = ("" if cur == "0" else cur) + add

    def _eval(self):
        source = self.screen.text or "0"
        out = core.eval_line(source, angle=self.angle, eng=self.eng, ans=self.ans, lang=self.lang)
        self.ans = out.get("value") or 0
        self.screen.text = out.get("text") or "0"
        self.calc_steps.text = fmt_steps(out.get("steps") or [])

    # ----- formulas -----
    def _formulas_screen(self):
        sc = Screen(name="formulas")
        box = BoxLayout(orientation="vertical", spacing=dp(6))
        self.cat_title = Label(text=self.tr("categories"), color=ACCENT, size_hint_y=None, height=dp(24))
        box.add_widget(self.cat_title)
        self.cat_rv = ListView(size_hint_y=0.38)
        box.add_widget(self.cat_rv)
        row = BoxLayout(size_hint_y=None, height=dp(42), spacing=dp(6))
        self.fsearch = DarkInput(hint_text=self.tr("search"))
        self.fsearch.bind(text=lambda *_: self.refresh_formulas())
        row.add_widget(self.fsearch)
        box.add_widget(row)
        self.flist = ListView()
        box.add_widget(self.flist)
        sc.add_widget(box)
        return sc

    def refresh_categories(self):
        cats, rows, _ = core.catalog()
        counts = {}
        for r in rows:
            counts[r["category"]] = counts.get(r["category"], 0) + 1
        data = [{"text": f"{self.tr('all')}    {len(rows)}", "kind": "cat"}]
        self.cat_rows = [None]
        for key in sorted(cats):
            names = cats[key]
            label = names.get(self.lang) or names.get("en") or key
            n = counts.get(key, 0)
            data.append({"text": f"{label}    {n}", "kind": "cat"})
            self.cat_rows.append(key)
        self.cat_rv.data = data
        self.cat_title.text = f"{self.tr('categories')}  ({len(rows)})"

    def pick_category(self, index: int):
        self.current_cat = self.cat_rows[index] if 0 <= index < len(self.cat_rows) else None
        self.refresh_formulas()

    def refresh_formulas(self):
        q = self.fsearch.text if self.fsearch else ""
        cat = getattr(self, "current_cat", None)
        self.formula_rows = core.list_formulas(q, self.lang, cat)
        self.flist.data = [{"text": it["name"], "kind": "formula"} for it in self.formula_rows]

    def open_formula(self, index: int):
        if index < 0 or index >= len(self.formula_rows):
            return
        self.current_formula = self.formula_rows[index]
        self._fill_formula_fields()
        self.sm.current = "fsolve"

    def _fsolve_screen(self):
        sc = Screen(name="fsolve")
        outer = BoxLayout(orientation="vertical", spacing=dp(6))
        back = DarkButton(text=self.tr("back"))
        back.bind(on_release=lambda *_: self.go("formulas"))
        outer.add_widget(back)
        self.fname = Label(text="", color=ACCENT, size_hint_y=None, height=dp(36), font_size=dp(16))
        self.fexpr = Label(text="", color=FG, size_hint_y=None, height=dp(40), font_size=dp(14))
        outer.add_widget(self.fname)
        outer.add_widget(self.fexpr)
        scroll = ScrollView()
        self.ffields = GridLayout(cols=1, size_hint_y=None, spacing=dp(6), padding=dp(4))
        self.ffields.bind(minimum_height=self.ffields.setter("height"))
        scroll.add_widget(self.ffields)
        outer.add_widget(scroll)
        solve = DarkButton(text=self.tr("solve"), accent=True)
        solve.bind(on_release=lambda *_: self._solve_formula())
        outer.add_widget(solve)
        self.fresult = Label(text="", color=FG, size_hint_y=None, height=dp(40), font_size=dp(16))
        self.fsteps = Label(text="", color=MUTED, font_size=dp(12), size_hint_y=None, height=dp(140),
                            text_size=(dp(360), dp(140)), valign="top", halign="left")
        outer.add_widget(self.fresult)
        outer.add_widget(self.fsteps)
        sc.add_widget(outer)
        return sc

    def _fill_formula_fields(self):
        item = self.current_formula or {}
        self.fname.text = item.get("name") or ""
        self.fexpr.text = item.get("expr") or ""
        self.ffields.clear_widgets()
        self.var_inputs = {}
        names = list((item.get("variables") or {}).keys())
        self.unknown = names[0] if names else ""
        self.unk_spin = Spinner(text=self.unknown, values=names or [""], size_hint_y=None, height=dp(40),
                                background_normal="", background_color=BTN, color=FG)
        self.unk_spin.bind(text=lambda _s, v: setattr(self, "unknown", v))
        self.ffields.add_widget(Label(text=self.tr("unknown"), color=MUTED, size_hint_y=None, height=dp(22)))
        self.ffields.add_widget(self.unk_spin)
        for name, meta in (item.get("variables") or {}).items():
            lab = (meta.get("name") or {}).get(self.lang) or (meta.get("name") or {}).get("en") or name
            unit = meta.get("unit") or ""
            self.ffields.add_widget(Label(text=f"{name}  {lab}  [{unit}]", color=FG, size_hint_y=None, height=dp(22)))
            inp = DarkInput()
            inp.bind(on_text_validate=lambda *_: self._solve_formula())
            self.ffields.add_widget(inp)
            self.var_inputs[name] = inp
        self.fresult.text = ""
        self.fsteps.text = ""

    def _solve_formula(self):
        item = self.current_formula
        if not item:
            self.fresult.text = self.tr("pick")
            return
        values = {name: inp.text for name, inp in self.var_inputs.items()}
        out = core.solve_named(item["id"], values, unknown=self.unknown, eng=self.eng, lang=self.lang)
        extra = ""
        if out.get("all") and len(out["all"]) > 1:
            extra = "  |  " + ", ".join(out["all"][1:])
        self.fresult.text = f"{out.get('unknown')} = {out.get('text')} {out.get('unit') or ''}{extra}"
        self.fsteps.text = fmt_steps(out.get("steps") or [])

    # ----- polynomial -----
    def _poly_screen(self):
        sc = Screen(name="poly")
        box = BoxLayout(orientation="vertical", spacing=dp(6))
        box.add_widget(Label(text="a6 x^6 + ... + a0", color=ACCENT, size_hint_y=None, height=dp(24)))
        grid = GridLayout(cols=4, spacing=dp(4), size_hint_y=None, height=dp(90))
        self.coeffs = []
        for i, name in enumerate(["a6", "a5", "a4", "a3", "a2", "a1", "a0"]):
            cell = BoxLayout(orientation="vertical")
            cell.add_widget(Label(text=name, color=MUTED, size_hint_y=None, height=dp(18), font_size=dp(11)))
            inp = DarkInput(text="0" if i != 5 else "1", height=dp(36))
            cell.add_widget(inp)
            self.coeffs.append(inp)
            grid.add_widget(cell)
        box.add_widget(grid)
        xr = BoxLayout(size_hint_y=None, height=dp(42), spacing=dp(6))
        xr.add_widget(Label(text="x", color=MUTED, size_hint_x=None, width=dp(20)))
        self.poly_x = DarkInput(text="1")
        xr.add_widget(self.poly_x)
        ev = DarkButton(text=self.tr("evaluate"), accent=True)
        ev.bind(on_release=lambda *_: self._poly("eval"))
        rt = DarkButton(text=self.tr("roots"))
        rt.bind(on_release=lambda *_: self._poly("roots"))
        xr.add_widget(ev)
        xr.add_widget(rt)
        box.add_widget(xr)
        self.poly_out = Label(text="", color=FG, font_size=dp(13), text_size=(dp(360), dp(280)),
                              valign="top", halign="left")
        box.add_widget(self.poly_out)
        sc.add_widget(box)
        return sc

    def _poly(self, kind: str):
        coeffs = [inp.text for inp in self.coeffs]
        x = None if kind == "roots" else self.poly_x.text
        out = core.poly_work(coeffs, x, self.eng)
        if kind == "roots":
            text = "\n".join(out.get("roots") or ["0"])
            extra = fmt_steps(teach.steps_poly(self.lang, "roots", None, "", out.get("degree"), out.get("roots") or []))
        else:
            text = f"p(x) = {out.get('value_text')}\ndegree = {out.get('degree')}"
            extra = fmt_steps(teach.steps_poly(self.lang, "eval", x, out.get("value_text") or "0", out.get("degree"), None))
        self.poly_out.text = text + "\n\n" + extra

    # ----- numeric -----
    def _numeric_screen(self):
        sc = Screen(name="numeric")
        box = BoxLayout(orientation="vertical", spacing=dp(6))
        self.n_func = DarkInput(text="x**2", hint_text="f(x) or f(x,y)")
        self.n_a = DarkInput(text="0", hint_text="a / x0")
        self.n_b = DarkInput(text="1", hint_text="b / x1")
        self.n_y0 = DarkInput(text="1", hint_text="y0")
        for w in (self.n_func, self.n_a, self.n_b, self.n_y0):
            box.add_widget(w)
        row = BoxLayout(size_hint_y=None, height=dp(42), spacing=dp(4))
        for kind, key in (("root", "root"), ("integral", "integral"), ("deriv", "deriv"), ("ode", "ode"), ("ode2", "ode2"), ("odesys", "odesys")):
            b = DarkButton(text=self.tr(key))
            b.bind(on_release=lambda _w, k=kind: self._numeric(k))
            row.add_widget(b)
        box.add_widget(row)
        self.n_out = Label(text="", color=FG, font_size=dp(13), text_size=(dp(360), dp(240)), valign="top")
        box.add_widget(self.n_out)
        sc.add_widget(box)
        return sc

    def _numeric(self, kind: str):
        func = self.n_func.text or "x"
        try:
            a = float(self.n_a.text or 0)
        except Exception:
            a = 0.0
        try:
            b = float(self.n_b.text or 1)
        except Exception:
            b = 1.0
        try:
            y0 = float(self.n_y0.text or 1)
        except Exception:
            y0 = 1.0
        if kind == "integral":
            out = core.n_integral(func, a, b, self.eng)
            steps = teach.steps_numeric(self.lang, "integral", a, b, None, out.get("text") or "0")
        elif kind == "deriv":
            out = core.n_deriv(func, a, self.eng)
            steps = teach.steps_numeric(self.lang, "deriv", a, None, None, out.get("text") or "0")
        elif kind == "ode":
            out = core.n_ode(func, a, y0, b, 40, self.eng)
            steps = teach.steps_numeric(self.lang, "ode", a, b, y0, out.get("text") or "0")
        else:
            out = core.n_root(func, a, b, self.eng)
            steps = teach.steps_numeric(self.lang, "root", a, b, None, out.get("text") or "0")
        extra = out.get("exact") or ""
        self.n_out.text = (out.get("text") or "0") + (("\n" + extra) if extra else "") + "\n\n" + fmt_steps(steps)

    # ----- algorithms -----
    def _algo_screen(self):
        sc = Screen(name="algo")
        box = BoxLayout(orientation="vertical", spacing=dp(6))
        self.acat_rv = ListView(size_hint_y=0.35)
        box.add_widget(self.acat_rv)
        self.asearch = DarkInput(hint_text=self.tr("search"))
        self.asearch.bind(text=lambda *_: self.refresh_algos())
        box.add_widget(self.asearch)
        self.alist = ListView()
        box.add_widget(self.alist)
        sc.add_widget(box)
        return sc

    def refresh_algos(self):
        cats, items, _ = algorithms.catalog()
        counts = {}
        for it in items:
            counts[it["category"]] = counts.get(it["category"], 0) + 1
        data = [{"text": f"{self.tr('all')}    {len(items)}", "kind": "acat"}]
        self.acat_rows = [None]
        for key in sorted(cats):
            names = cats[key]
            label = names.get(self.lang) or names.get("en") or key
            data.append({"text": f"{label}    {counts.get(key, 0)}", "kind": "acat"})
            self.acat_rows.append(key)
        self.acat_rv.data = data
        q = self.asearch.text if self.asearch else ""
        cat = getattr(self, "current_acat", None)
        self.algo_rows = algorithms.list_algos(q, self.lang, cat)
        self.alist.data = [{"text": it["name"], "kind": "algo"} for it in self.algo_rows]

    def pick_algo_cat(self, index: int):
        self.current_acat = self.acat_rows[index] if 0 <= index < len(self.acat_rows) else None
        self.refresh_algos()

    def open_algo(self, index: int):
        if index < 0 or index >= len(self.algo_rows):
            return
        self.current_algo = self.algo_rows[index]
        self._fill_algo_fields()
        self.sm.current = "arun"

    def _arun_screen(self):
        sc = Screen(name="arun")
        box = BoxLayout(orientation="vertical", spacing=dp(6))
        back = DarkButton(text=self.tr("back"))
        back.bind(on_release=lambda *_: self.go("algo"))
        box.add_widget(back)
        self.aname = Label(text="", color=ACCENT, size_hint_y=None, height=dp(36))
        box.add_widget(self.aname)
        scroll = ScrollView()
        self.afields = GridLayout(cols=1, size_hint_y=None, spacing=dp(6))
        self.afields.bind(minimum_height=self.afields.setter("height"))
        scroll.add_widget(self.afields)
        box.add_widget(scroll)
        run = DarkButton(text=self.tr("run"), accent=True)
        run.bind(on_release=lambda *_: self._run_algo())
        box.add_widget(run)
        self.aresult = Label(text="", color=FG, font_size=dp(14), text_size=(dp(360), dp(160)), valign="top")
        box.add_widget(self.aresult)
        sc.add_widget(box)
        return sc

    def _fill_algo_fields(self):
        item = self.current_algo or {}
        self.aname.text = item.get("name") or ""
        self.afields.clear_widgets()
        self.algo_inputs = {}
        for name, meta in (item.get("params") or {}).items():
            lab = (meta.get("name") or {}).get(self.lang) or (meta.get("name") or {}).get("en") or name
            self.afields.add_widget(Label(text=f"{name}  {lab}", color=FG, size_hint_y=None, height=dp(22)))
            inp = DarkInput(text=str(meta.get("default") or ""))
            inp.bind(on_text_validate=lambda *_: self._run_algo())
            self.afields.add_widget(inp)
            self.algo_inputs[name] = inp
        self.aresult.text = ""

    def _run_algo(self):
        item = self.current_algo
        if not item:
            self.aresult.text = self.tr("pick_algo")
            return
        values = {name: inp.text for name, inp in self.algo_inputs.items()}
        out = algorithms.run_algo(item["id"], values, eng=self.eng)
        self.aresult.text = (out.get("text") or "0") + (("\n" + out["detail"]) if out.get("detail") else "")

    # ----- chemistry -----
    def _chem_screen(self):
        sc = Screen(name="chem")
        box = BoxLayout(orientation="vertical", spacing=dp(6))
        box.add_widget(Label(text="H2 + O2 = H2O", color=MUTED, size_hint_y=None, height=dp(24)))
        self.chem_eq = DarkInput(text="C2H6 + O2 = CO2 + H2O")
        self.chem_eq.bind(on_text_validate=lambda *_: self._chem("bal"))
        box.add_widget(self.chem_eq)
        row = BoxLayout(size_hint_y=None, height=dp(42), spacing=dp(6))
        b1 = DarkButton(text=self.tr("balance"), accent=True)
        b1.bind(on_release=lambda *_: self._chem("bal"))
        b2 = DarkButton(text=self.tr("molar"))
        b2.bind(on_release=lambda *_: self._chem("mw"))
        row.add_widget(b1)
        row.add_widget(b2)
        box.add_widget(row)
        self.chem_out = Label(text="", color=FG, font_size=dp(14), text_size=(dp(360), dp(240)), valign="top")
        box.add_widget(self.chem_out)
        sc.add_widget(box)
        return sc

    def _chem(self, kind: str):
        raw = self.chem_eq.text or ""
        if kind == "mw":
            out = chemtools.molar_mass(raw.split("=")[0].split("+")[0].strip())
            lines = [f"{out.get('text')} g/mol"]
            for sym, info in (out.get("detail") or {}).items():
                if isinstance(info, dict) and "count" in info:
                    lines.append(f"  {sym}: {info['count']} x {info['mass']} = {info['contrib']}")
            extra = fmt_steps(teach.steps_chem(self.lang, raw, out.get("text") or "0", True))
            self.chem_out.text = "\n".join(lines) + "\n\n" + extra
            return
        out = chemtools.balance_equation(raw)
        extra = fmt_steps(teach.steps_chem(self.lang, raw, out.get("text") or "", False))
        self.chem_out.text = (out.get("text") or "") + "\n\n" + extra

    # ----- elements -----
    def _elements_screen(self):
        sc = Screen(name="elements")
        box = BoxLayout(orientation="vertical", spacing=dp(6))
        self.el_q = DarkInput(hint_text="Fe / 26 / iron")
        self.el_q.bind(text=lambda *_: self.refresh_elements())
        box.add_widget(self.el_q)
        self.elist = ListView()
        box.add_widget(self.elist)
        sc.add_widget(box)
        return sc

    def refresh_elements(self):
        q = self.el_q.text if self.el_q else ""
        self.element_rows = chemtools.list_elements(q)
        data = []
        for el in self.element_rows:
            name = el["name"].get(self.lang) or el["name"]["en"]
            data.append({"text": f"{el['Z']:3}  {el['symbol']:<3}  {name}", "kind": "element"})
        self.elist.data = data

    def open_element(self, index: int):
        if index < 0 or index >= len(self.element_rows):
            return
        el = self.element_rows[index]
        name = el["name"].get(self.lang) or el["name"]["en"]
        lines = [
            f"{el['symbol']}  {name}",
            f"{self.tr('atomic_n')}: {el['Z']}",
            f"{self.tr('atomic_m')}: {el['mass']}",
            f"group: {el['group']}",
            "",
            self.tr("isotopes") + ":",
        ]
        for iso in el.get("isotopes") or []:
            ab = f"{iso.get('abundance')} %" if iso.get("abundance") is not None else (iso.get("note") or "")
            lines.append(f"  {el['symbol']}-{iso['A']}   {iso['mass']} u   {ab}")
        self.edetail.text = "\n".join(lines)
        self.sm.current = "edetail"

    def _edetail_screen(self):
        sc = Screen(name="edetail")
        box = BoxLayout(orientation="vertical", spacing=dp(6))
        back = DarkButton(text=self.tr("back"))
        back.bind(on_release=lambda *_: self.go("elements"))
        box.add_widget(back)
        self.edetail = Label(text="", color=FG, font_size=dp(14), text_size=(dp(360), dp(520)), valign="top", halign="left")
        box.add_widget(self.edetail)
        sc.add_widget(box)
        return sc

    # ----- problems -----
    def _problems_screen(self):
        sc = Screen(name="problems")
        box = BoxLayout(orientation="vertical", spacing=dp(6))
        self.prob_hint = Label(
            text=self.tr("problem_hint"),
            color=MUTED,
            font_size=dp(12),
            size_hint_y=None,
            height=dp(64),
            text_size=(dp(360), dp(64)),
            valign="top",
            halign="left",
        )
        box.add_widget(self.prob_hint)
        self.prob_text = DarkInput(text="2*x + 3 = 11", multiline=True, height=dp(90))
        self.prob_text.bind(on_text_validate=lambda *_: self._run_problem("solve"))
        box.add_widget(self.prob_text)
        row = BoxLayout(size_hint_y=None, height=dp(42), spacing=dp(6))
        self.prob_unk = DarkInput(text="x", hint_text=self.tr("unknown"), size_hint_x=0.3)
        self.prob_at = DarkInput(text="", hint_text=self.tr("at_value"), size_hint_x=0.3)
        row.add_widget(self.prob_unk)
        row.add_widget(self.prob_at)
        box.add_widget(row)
        btns = BoxLayout(size_hint_y=None, height=dp(42), spacing=dp(6))
        self.prob_solve_btn = DarkButton(text=self.tr("solve"), accent=True)
        self.prob_solve_btn.bind(on_release=lambda *_: self._run_problem("solve"))
        self.prob_inv_btn = DarkButton(text=self.tr("inverse"))
        self.prob_inv_btn.bind(on_release=lambda *_: self._run_problem("inverse"))
        btns.add_widget(self.prob_solve_btn)
        btns.add_widget(self.prob_inv_btn)
        box.add_widget(btns)
        self.prob_out = Label(
            text="",
            color=FG,
            font_size=dp(16),
            size_hint_y=None,
            height=dp(48),
            text_size=(dp(360), dp(48)),
            valign="top",
            halign="left",
        )
        box.add_widget(self.prob_out)
        self.prob_steps = Label(
            text="",
            color=MUTED,
            font_size=dp(12),
            text_size=(dp(360), dp(220)),
            valign="top",
            halign="left",
        )
        box.add_widget(self.prob_steps)
        sc.add_widget(box)
        return sc

    def _circuits_screen(self):
        sc = Screen(name="circuits")
        box = BoxLayout(orientation="vertical", spacing=dp(6))
        self.cir_state = {}
        self.cir_hint = Label(
            text=self.tr("circuit_hint"),
            color=MUTED,
            font_size=dp(12),
            size_hint_y=None,
            height=dp(44),
            text_size=(dp(360), dp(44)),
            valign="top",
            halign="left",
        )
        box.add_widget(self.cir_hint)
        self.cir_q = Label(text="", color=ACCENT, font_size=dp(16), bold=True, size_hint_y=None, height=dp(36),
                           text_size=(dp(360), dp(36)), valign="middle", halign="left")
        box.add_widget(self.cir_q)
        self.cir_story = Label(text="", color=MUTED, font_size=dp(12), size_hint_y=None, height=dp(48),
                              text_size=(dp(360), dp(48)), valign="top", halign="left")
        box.add_widget(self.cir_story)
        self.cir_choices = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(6))
        box.add_widget(self.cir_choices)
        valrow = BoxLayout(size_hint_y=None, height=dp(42), spacing=dp(6))
        self.cir_val = DarkInput(text="", hint_text="")
        self.cir_val.bind(on_text_validate=lambda *_: self._cir_send("next"))
        valrow.add_widget(self.cir_val)
        self.cir_next = DarkButton(text=self.tr("cir_next"), accent=True, size_hint_x=None, width=dp(90))
        self.cir_next.bind(on_release=lambda *_: self._cir_send("next"))
        valrow.add_widget(self.cir_next)
        box.add_widget(valrow)
        self.cir_guide_out = Label(text="", color=FG, font_size=dp(15), size_hint_y=None, height=dp(44),
                                  text_size=(dp(360), dp(44)), valign="top", halign="left")
        box.add_widget(self.cir_guide_out)
        self.cir_guide_steps = Label(text="", color=MUTED, font_size=dp(12), size_hint_y=None, height=dp(90),
                                    text_size=(dp(360), dp(90)), valign="top", halign="left")
        box.add_widget(self.cir_guide_steps)
        self.cir_actions = BoxLayout(size_hint_y=None, height=dp(42), spacing=dp(6))
        box.add_widget(self.cir_actions)
        self.cir_text = DarkInput(text="V1 1 0 12\nR1 1 2 1k\nR2 2 0 2k", multiline=True, height=dp(70))
        box.add_widget(self.cir_text)
        self.cir_freq = DarkInput(text="", hint_text=self.tr("circuit_freq"))
        box.add_widget(self.cir_freq)
        btns = BoxLayout(size_hint_y=None, height=dp(42), spacing=dp(6))
        b1 = DarkButton(text=self.tr("solve"), accent=True)
        b1.bind(on_release=lambda *_: self._run_circuit("solve"))
        b2 = DarkButton(text=self.tr("inverse"))
        b2.bind(on_release=lambda *_: self._run_circuit("inverse"))
        btns.add_widget(b1)
        btns.add_widget(b2)
        box.add_widget(btns)
        self.cir_out = Label(text="", color=FG, font_size=dp(14), size_hint_y=None, height=dp(64),
                             text_size=(dp(360), dp(64)), valign="top", halign="left")
        box.add_widget(self.cir_out)
        self.cir_steps = Label(text="", color=MUTED, font_size=dp(12), text_size=(dp(360), dp(180)), valign="top")
        box.add_widget(self.cir_steps)
        sc.add_widget(box)
        Clock.schedule_once(lambda dt: self._cir_send("start"), 0.2)
        return sc

    def _cir_send(self, action, kind="", conn=""):
        try:
            out = circguide.run({
                "action": action,
                "state": getattr(self, "cir_state", {}) or {},
                "kind": kind,
                "conn": conn,
                "value": self.cir_val.text if getattr(self, "cir_val", None) else "",
                "lang": self.lang,
                "eng": self.eng,
            })
        except Exception:
            out = {"prompt": "", "story": [], "choices": [], "text": "0", "steps": [], "state": {}, "actions": []}
        self._cir_paint(out)

    def _cir_paint(self, out):
        if not isinstance(out, dict):
            return
        self.cir_state = out.get("state") or {}
        if getattr(self, "cir_q", None):
            self.cir_q.text = out.get("prompt") or ""
            self.cir_story.text = "\n".join(out.get("story") or [])
        if getattr(self, "cir_choices", None):
            self.cir_choices.clear_widgets()
            picked = out.get("picked") or ""
            for ch in out.get("choices") or []:
                cid = ch.get("id") or ""
                b = DarkButton(text=ch.get("label") or cid, accent=(picked == cid))
                b.bind(on_release=lambda _w, i=cid: self._cir_click(i))
                self.cir_choices.add_widget(b)
        if getattr(self, "cir_val", None):
            self.cir_val.hint_text = out.get("value_hint") or ""
            if not out.get("need_value"):
                self.cir_val.text = ""
        if getattr(self, "cir_next", None):
            self.cir_next.text = out.get("next_label") or self.tr("cir_next")
        bits = []
        if out.get("formula"):
            bits.append(str(out["formula"]))
        if out.get("text"):
            bits.append(str(out["text"]))
        if getattr(self, "cir_guide_out", None):
            self.cir_guide_out.text = "\n".join(bits)
            self.cir_guide_steps.text = fmt_steps(out.get("steps") or [])
        if getattr(self, "cir_actions", None):
            self.cir_actions.clear_widgets()
            for act in out.get("actions") or []:
                aid = act.get("id") or ""
                b = DarkButton(text=act.get("label") or aid, accent=(aid == "add"))
                b.bind(on_release=lambda _w, i=aid: self._cir_send(i))
                self.cir_actions.add_widget(b)

    def _cir_click(self, kind):
        if kind in {"series", "parallel"}:
            self._cir_send("connect", kind=kind, conn=kind)
            return
        self._cir_send("pick", kind=kind)

    def _seq_screen(self):
        sc = Screen(name="seq")
        box = BoxLayout(orientation="vertical", spacing=dp(6))
        self.seq_hint = Label(text=self.tr("seq_hint"), color=MUTED, font_size=dp(12), size_hint_y=None, height=dp(48), text_size=(dp(360), dp(48)))
        box.add_widget(self.seq_hint)
        self.seq_text = DarkInput(text="2, 5, 8, 11", multiline=True, height=dp(90))
        box.add_widget(self.seq_text)
        b = DarkButton(text=self.tr("seq_go"), accent=True)
        b.bind(on_release=lambda *_: self._run_seq())
        box.add_widget(b)
        self.seq_out = Label(text="", color=FG, font_size=dp(13), text_size=(dp(360), dp(360)), valign="top")
        box.add_widget(self.seq_out)
        sc.add_widget(box)
        return sc

    def _run_seq(self):
        try:
            out = seqfind.run(self.seq_text.text if self.seq_text else "", lang=self.lang, n_next=5)
        except Exception:
            out = {"text": "0"}
        self.seq_out.text = out.get("text") or "0"

    def _run_circuit(self, mode: str):
        try:
            raw = self.cir_text.text if self.cir_text else ""
            freq = self.cir_freq.text if self.cir_freq else ""
            out = circuits.run(raw, mode=mode, freq=freq, lang=self.lang, eng=self.eng)
        except Exception:
            out = {"text": "0", "steps": []}
        self.cir_out.text = out.get("text") or "0"
        self.cir_steps.text = fmt_steps(out.get("steps") or [])

    def _run_problem(self, mode: str):
        try:
            raw = self.prob_text.text if self.prob_text else ""
            unknown = (self.prob_unk.text if self.prob_unk else "x") or "x"
            at = self.prob_at.text if self.prob_at else ""
            out = problems.run(raw, mode=mode, unknown=unknown, at=at, lang=self.lang, eng=self.eng)
        except Exception:
            out = {"text": "0", "steps": []}
        self.prob_out.text = out.get("text") or "0"
        self.prob_steps.text = fmt_steps(out.get("steps") or [])

    def _graph_screen(self):
        sc = Screen(name="graph")
        box = BoxLayout(orientation="vertical", spacing=dp(6))
        self.graph_text = DarkInput(text="sin(x)", multiline=True, height=dp(90))
        box.add_widget(self.graph_text)
        row = BoxLayout(size_hint_y=None, height=dp(42), spacing=dp(4))
        for kind, key in (("func", "plot"), ("param", "parametric"), ("bode", "bode")):
            b = DarkButton(text=self.tr(key) if key != "parametric" else "Param")
            b.bind(on_release=lambda _w, k=kind: self._run_graph(k))
            row.add_widget(b)
        box.add_widget(row)
        self.graph_out = Label(text="", color=FG, font_size=dp(13), text_size=(dp(360), dp(280)), valign="top")
        box.add_widget(self.graph_out)
        sc.add_widget(box)
        return sc

    def _run_graph(self, kind):
        try:
            out = graphs.run(kind, self.graph_text.text, circuit=self.graph_text.text, data=self.graph_text.text, lang=self.lang, eng=self.eng)
        except Exception:
            out = {"text": "0"}
        self.graph_out.text = (out.get("text") or "0") + "\n" + (out.get("svg") or "")[:400]

    def _matrix_screen(self):
        sc = Screen(name="matrix")
        box = BoxLayout(orientation="vertical", spacing=dp(6))
        self.mat_a = DarkInput(text="1, 2; 3, 4", multiline=True, height=dp(70))
        self.mat_b = DarkInput(text="5; 6", multiline=True, height=dp(50))
        box.add_widget(self.mat_a)
        box.add_widget(self.mat_b)
        row = BoxLayout(size_hint_y=None, height=dp(42), spacing=dp(4))
        for op, key in (("det", "det"), ("inv", "invm"), ("eig", "eig"), ("solve", "solve")):
            b = DarkButton(text=self.tr(key) if key in ("det", "invm") else op)
            b.bind(on_release=lambda _w, o=op: self._run_matrix(o))
            row.add_widget(b)
        box.add_widget(row)
        self.mat_out = Label(text="", color=FG, font_size=dp(14), text_size=(dp(360), dp(220)), valign="top")
        box.add_widget(self.mat_out)
        sc.add_widget(box)
        return sc

    def _run_matrix(self, op):
        try:
            out = matrixlab.run(op, self.mat_a.text, self.mat_b.text, eng=self.eng, lang=self.lang)
        except Exception:
            out = {"text": "0"}
        self.mat_out.text = out.get("text") or "0"

    def _stats_screen(self):
        sc = Screen(name="stats")
        box = BoxLayout(orientation="vertical", spacing=dp(6))
        self.stats_text = DarkInput(text="1\n2\n3\n4\n5", multiline=True, height=dp(120))
        box.add_widget(self.stats_text)
        b = DarkButton(text=self.tr("run"), accent=True)
        b.bind(on_release=lambda *_: self._run_stats())
        box.add_widget(b)
        self.stats_out = Label(text="", color=FG, font_size=dp(13), text_size=(dp(360), dp(280)), valign="top")
        box.add_widget(self.stats_out)
        sc.add_widget(box)
        return sc

    def _run_stats(self):
        try:
            out = statsdata.run(self.stats_text.text, eng=self.eng, lang=self.lang)
        except Exception:
            out = {"text": "0"}
        self.stats_out.text = out.get("text") or "0"

    def _triangle_screen(self):
        sc = Screen(name="triangle")
        box = BoxLayout(orientation="vertical", spacing=dp(6))
        self.tri_in = {}
        grid = GridLayout(cols=3, spacing=dp(4), size_hint_y=None, height=dp(90))
        for name, default in (("a", "3"), ("b", "4"), ("c", "5"), ("A", ""), ("B", ""), ("C", "")):
            cell = BoxLayout(orientation="vertical")
            cell.add_widget(Label(text=name, color=MUTED, size_hint_y=None, height=dp(18)))
            inp = DarkInput(text=default, height=dp(36))
            self.tri_in[name] = inp
            cell.add_widget(inp)
            grid.add_widget(cell)
        box.add_widget(grid)
        b = DarkButton(text=self.tr("solve"), accent=True)
        b.bind(on_release=lambda *_: self._run_triangle())
        box.add_widget(b)
        self.tri_out = Label(text="", color=FG, font_size=dp(13), text_size=(dp(360), dp(280)), valign="top")
        box.add_widget(self.tri_out)
        sc.add_widget(box)
        return sc

    def _run_triangle(self):
        values = {k: inp.text for k, inp in self.tri_in.items()}
        try:
            out = triangle.run(values, lang=self.lang, eng=self.eng)
        except Exception:
            out = {"text": "0"}
        self.tri_out.text = out.get("text") or "0"

    # ----- sources -----
    def _sources_screen(self):
        sc = Screen(name="sources")

        def reload():
            import json
            from pathlib import Path

            data = json.loads(Path(__file__).with_name("sources.json").read_text(encoding="utf-8"))
            pack = data.get("sources") or {}
            lines = []
            for k, s in pack.items():
                name = (s.get("name") or {}).get(self.lang) or (s.get("name") or {}).get("en") or k
                note = (s.get("note") or {}).get(self.lang) or (s.get("note") or {}).get("en") or ""
                lines.append(str(name))
                if s.get("url"):
                    lines.append(s["url"])
                lines.append(str(note))
                lines.append("")
            body.text = "\n".join(lines)

        box = BoxLayout(orientation="vertical")
        scroll = ScrollView()
        body = Label(text="", color=FG, font_size=dp(13), size_hint_y=None, text_size=(dp(360), None),
                     valign="top", halign="left")
        body.bind(texture_size=lambda w, s: setattr(w, "height", s[1]))
        scroll.add_widget(body)
        box.add_widget(scroll)
        sc.add_widget(box)
        sc.reload = reload
        Clock.schedule_once(lambda dt: reload(), 0.3)
        return sc


if __name__ == "__main__":
    UltraAndroid().run()
