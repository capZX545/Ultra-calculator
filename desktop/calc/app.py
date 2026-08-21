"""Desktop window. Independent of the web interface."""

from __future__ import annotations

import json
from pathlib import Path

import tkinter as tk
from tkinter import ttk

from .algorithms import catalog as algo_catalog, list_algos, run_algo
from .chemtools import balance_equation, find_element, list_elements, molar_mass
from .engine import DesktopEngine
from .i18n import t
from .lookup import lookup
from .circuits import run as run_circuit
from .problems import run as run_problem
from .sanitize import clean_number
from . import teach
from . import graphs
from . import matrixlab
from . import statsdata
from . import triangle
from . import searchall
from . import sessionstore
from . import latexout


BG = "#1c1f24"
PANEL = "#262b33"
BTN = "#323842"
BTN2 = "#3d4654"
ACCENT = "#c4a35a"
FG = "#e8eaed"
MUTED = "#9aa3ad"
RED = "#8b4a44"
GREEN = "#3d6b55"


class UltraDesktop(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.engine = DesktopEngine()
        self.lang = "en"
        self.mode = "calc"
        self.expr = ""
        self.formula_id = None
        self.var_widgets = {}
        self.last_target = None
        self.lookup_pick = None
        self.unknown_var = tk.StringVar(value="")
        self.system_eqs = []
        self.system_unknowns = ["x"]
        self.title(t(self.lang, "app_title"))
        self.geometry("1100x720")
        self.minsize(960, 640)
        self.configure(bg=BG)
        self._style()
        self._build()
        self._refresh_texts()

    def _style(self) -> None:
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("TFrame", background=BG)
        style.configure("Panel.TFrame", background=PANEL)
        style.configure("TLabel", background=BG, foreground=FG, font=("Segoe UI", 11))
        style.configure("Muted.TLabel", background=BG, foreground=MUTED, font=("Segoe UI", 10))
        style.configure("Panel.TLabel", background=PANEL, foreground=FG, font=("Segoe UI", 11))
        style.configure("Head.TLabel", background=BG, foreground=ACCENT, font=("Segoe UI", 13, "bold"))
        style.configure("TButton", background=BTN, foreground=FG, font=("Segoe UI", 10), padding=6)
        style.map("TButton", background=[("active", BTN2)])
        style.configure("TCombobox", fieldbackground=PANEL, background=PANEL, foreground=FG)
        style.configure("TEntry", fieldbackground="#11141a", foreground=FG)
        style.configure("Treeview", background=PANEL, fieldbackground=PANEL, foreground=FG, rowheight=24, borderwidth=0)
        style.configure("Treeview.Heading", background=BG, foreground=ACCENT, font=("Segoe UI", 10, "bold"), borderwidth=0)
        style.map("Treeview", background=[("selected", BTN2)], foreground=[("selected", FG)])
        style.configure("TRadiobutton", background=PANEL, foreground=FG)
        style.configure("TCheckbutton", background=PANEL, foreground=FG)

    def tr(self, key: str) -> str:
        return t(self.lang, key)

    def _build(self) -> None:
        top = tk.Frame(self, bg=BG)
        top.pack(fill="x", padx=12, pady=8)
        self.btn_calc = tk.Button(top, command=lambda: self._set_mode("calc"))
        self.btn_form = tk.Button(top, command=lambda: self._set_mode("formulas"))
        self.btn_poly = tk.Button(top, command=lambda: self._set_mode("poly"))
        self.btn_num = tk.Button(top, command=lambda: self._set_mode("numeric"))
        self.btn_algo = tk.Button(top, command=lambda: self._set_mode("algo"))
        self.btn_chem = tk.Button(top, command=lambda: self._set_mode("chem"))
        self.btn_el = tk.Button(top, command=lambda: self._set_mode("elements"))
        self.btn_src = tk.Button(top, command=lambda: self._set_mode("sources"))
        self.btn_prob = tk.Button(top, command=lambda: self._set_mode("problems"))
        self.btn_cir = tk.Button(top, command=lambda: self._set_mode("circuits"))
        self.btn_graph = tk.Button(top, command=lambda: self._set_mode("graph"))
        self.btn_matrix = tk.Button(top, command=lambda: self._set_mode("matrix"))
        self.btn_stats = tk.Button(top, command=lambda: self._set_mode("stats"))
        self.btn_tri = tk.Button(top, command=lambda: self._set_mode("triangle"))
        for b in (self.btn_calc, self.btn_form, self.btn_poly, self.btn_num, self.btn_algo, self.btn_chem, self.btn_el, self.btn_src, self.btn_prob, self.btn_cir, self.btn_graph, self.btn_matrix, self.btn_stats, self.btn_tri):
            self._paint_btn(b, BTN)
            b.pack(side="left", padx=3)
        self.btn_save = tk.Button(top, command=self._save_session)
        self.btn_load = tk.Button(top, command=self._load_session)
        self.btn_latex = tk.Button(top, command=self._copy_latex)
        for b in (self.btn_save, self.btn_load, self.btn_latex):
            self._paint_btn(b, BTN2)
            b.pack(side="right", padx=2)
        self.lang_box = ttk.Combobox(top, values=["en", "fa", "fi"], width=6, state="readonly")
        self.lang_box.set("en")
        self.lang_box.bind("<<ComboboxSelected>>", self._on_lang)
        self.lang_box.pack(side="right")
        self.lang_lbl = ttk.Label(top, text="")
        self.lang_lbl.pack(side="right", padx=6)

        self._build_lookup()

        self.frames = {}
        for name in ("calc", "formulas", "poly", "numeric", "algo", "chem", "elements", "sources", "problems", "circuits", "graph", "matrix", "stats", "triangle"):
            fr = tk.Frame(self, bg=BG)
            self.frames[name] = fr
        self._build_calc(self.frames["calc"])
        self._build_formulas(self.frames["formulas"])
        self._build_poly(self.frames["poly"])
        self._build_numeric(self.frames["numeric"])
        self._build_algo(self.frames["algo"])
        self._build_chem(self.frames["chem"])
        self._build_elements(self.frames["elements"])
        self._build_sources(self.frames["sources"])
        self._build_problems(self.frames["problems"])
        self._build_circuits(self.frames["circuits"])
        self._build_graph(self.frames["graph"])
        self._build_matrix(self.frames["matrix"])
        self._build_stats(self.frames["stats"])
        self._build_triangle(self.frames["triangle"])
        self._bind_keys()
        self._set_mode("calc")

    def _paint_btn(self, btn: tk.Button, color: str = BTN, fg: str = FG) -> None:
        btn.configure(
            bg=color,
            fg=fg,
            activebackground=BTN2,
            activeforeground=FG,
            relief="flat",
            bd=0,
            padx=10,
            pady=7,
            font=("Segoe UI", 10),
            highlightthickness=0,
        )

    def _set_mode(self, mode: str) -> None:
        self.mode = mode
        for name, fr in self.frames.items():
            fr.pack_forget()
        self.frames[mode].pack(fill="both", expand=True, padx=12, pady=8)
        mapping = {
            "calc": self.btn_calc,
            "formulas": self.btn_form,
            "poly": self.btn_poly,
            "numeric": self.btn_num,
            "algo": self.btn_algo,
            "chem": self.btn_chem,
            "elements": self.btn_el,
            "sources": self.btn_src,
            "problems": self.btn_prob,
            "circuits": self.btn_cir,
            "graph": self.btn_graph,
            "matrix": self.btn_matrix,
            "stats": self.btn_stats,
            "triangle": self.btn_tri,
        }
        for key, btn in mapping.items():
            self._paint_btn(btn, ACCENT if key == mode else BTN, "#1c1f24" if key == mode else FG)
        self.after(20, lambda m=mode: self._focus_mode(m))

    def _on_lang(self, _evt=None) -> None:
        self.lang = self.lang_box.get() or "en"
        self._refresh_texts()
        self._fill_categories()
        self._fill_formula_list()
        if self.formula_id:
            self._show_formula(self.formula_id)
        if hasattr(self, "el_list"):
            self._fill_elements()
        if hasattr(self, "algo_list"):
            self._fill_algo_cats()
            self._fill_algos()

    def _refresh_texts(self) -> None:
        self.title(self.tr("app_title"))
        self.btn_calc.configure(text=self.tr("mode_calc"))
        self.btn_form.configure(text=self.tr("mode_formulas"))
        self.btn_poly.configure(text=self.tr("mode_poly"))
        self.btn_num.configure(text=self.tr("mode_numeric"))
        if hasattr(self, "btn_algo"):
            self.btn_algo.configure(text=self.tr("mode_algo"))
        if hasattr(self, "algo_run_btn"):
            self.algo_run_btn.configure(text=self.tr("run"))
        if hasattr(self, "algo_search_lbl"):
            self.algo_search_lbl.configure(text=self.tr("search"))
            self.algo_cat_lbl.configure(text=self.tr("categories"))
        self.btn_chem.configure(text=self.tr("mode_chem"))
        self.btn_el.configure(text=self.tr("mode_elements"))
        self.btn_src.configure(text=self.tr("mode_sources"))
        if hasattr(self, "btn_prob"):
            self.btn_prob.configure(text=self.tr("mode_problems"))
        if hasattr(self, "prob_solve_btn"):
            self.prob_solve_btn.configure(text=self.tr("solve"))
            self.prob_inv_btn.configure(text=self.tr("inverse"))
            self.prob_unk_lbl.configure(text=self.tr("unknown"))
            self.prob_at_lbl.configure(text=self.tr("at_value"))
            self.prob_hint.configure(text=self.tr("problem_hint"))
        if hasattr(self, "btn_cir"):
            self.btn_cir.configure(text=self.tr("mode_circuits"))
        if hasattr(self, "btn_graph"):
            self.btn_graph.configure(text=self.tr("mode_graph"))
            self.btn_matrix.configure(text=self.tr("mode_matrix"))
            self.btn_stats.configure(text=self.tr("mode_stats"))
            self.btn_tri.configure(text=self.tr("mode_triangle"))
        if hasattr(self, "btn_save"):
            self.btn_save.configure(text=self.tr("save"))
            self.btn_load.configure(text=self.tr("load"))
            self.btn_latex.configure(text=self.tr("latex"))
        if hasattr(self, "n_ode2_btn"):
            self.n_ode2_btn.configure(text=self.tr("ode2"))
            self.n_sys_btn.configure(text=self.tr("odesys"))
        if hasattr(self, "cir_solve_btn"):
            self.cir_solve_btn.configure(text=self.tr("solve"))
            self.cir_inv_btn.configure(text=self.tr("inverse"))
            self.cir_freq_lbl.configure(text=self.tr("circuit_freq"))
            self.cir_hint.configure(text=self.tr("circuit_hint"))
        if hasattr(self, "graph_hint"):
            self.graph_hint.configure(text=self.tr("graph_hint"))
            self.matrix_hint.configure(text=self.tr("matrix_hint"))
            self.stats_hint.configure(text=self.tr("stats_hint"))
            self.tri_hint.configure(text=self.tr("triangle_hint"))
            if hasattr(self, "stats_run_btn"):
                self.stats_run_btn.configure(text=self.tr("run"))
            if hasattr(self, "tri_solve_btn"):
                self.tri_solve_btn.configure(text=self.tr("solve"))
        self.lang_lbl.configure(text=self.tr("language"))
        if hasattr(self, "lookup_lbl"):
            self.lookup_lbl.configure(text=self.tr("lookup"))
            self.lookup_insert_btn.configure(text=self.tr("insert"))
        if hasattr(self, "kbd_hint"):
            self.kbd_hint.configure(text=self.tr("kbd_hint"))
        if hasattr(self, "chem_bal_btn"):
            self.chem_bal_btn.configure(text=self.tr("balance"))
            self.chem_mw_btn.configure(text=self.tr("molar"))
        self.angle_btn.configure(text=self.tr("deg") if self.engine.angle == "DEG" else self.tr("rad"))
        self.eng_btn.configure(text=self.tr("eng"))
        self.search_lbl.configure(text=self.tr("search"))
        total = len(getattr(self.engine, "formulas", []) or [])
        self.cat_lbl.configure(text=f"{self.tr('categories')}  ({total})")
        if hasattr(self, "cat_list") and isinstance(self.cat_list, ttk.Treeview):
            self.cat_list.heading("name", text=self.tr("categories"))
            self.cat_list.heading("n", text="#")
        self.solve_btn.configure(text=self.tr("solve"))
        self.single_btn.configure(text=self.tr("single_mode"))
        self.system_btn.configure(text=self.tr("system_mode"))
        self.add_eq_btn.configure(text=self.tr("add_equation"))
        self.del_eq_btn.configure(text=self.tr("remove_equation"))
        self.poly_eval_btn.configure(text=self.tr("evaluate"))
        self.poly_root_btn.configure(text=self.tr("roots"))
        self.n_root_btn.configure(text=self.tr("numeric_root"))
        self.n_int_btn.configure(text=self.tr("numeric_integral"))
        self.n_diff_btn.configure(text=self.tr("numeric_diff"))
        self.n_ode_btn.configure(text=self.tr("numeric_ode"))

    def _build_lookup(self) -> None:
        bar = tk.Frame(self, bg=PANEL)
        bar.pack(fill="x", padx=12, pady=(0, 4))
        self.lookup_lbl = tk.Label(bar, bg=PANEL, fg=ACCENT, font=("Segoe UI", 10, "bold"))
        self.lookup_lbl.pack(side="left", padx=(8, 6))
        self.lookup_var = tk.StringVar()
        self.lookup_var.trace_add("write", lambda *_: self._run_lookup())
        self.lookup_entry = tk.Entry(
            bar,
            textvariable=self.lookup_var,
            bg="#11141a",
            fg=FG,
            insertbackground=FG,
            relief="flat",
            width=16,
        )
        self.lookup_entry.pack(side="left", padx=4, ipady=3)
        self.lookup_entry.bind("<Return>", lambda e: self._insert_lookup())
        self.lookup_insert_btn = tk.Button(bar, command=self._insert_lookup)
        self._paint_btn(self.lookup_insert_btn, ACCENT, "#1c1f24")
        self.lookup_insert_btn.pack(side="right", padx=6)
        self.lookup_hits = tk.Frame(bar, bg=PANEL)
        self.lookup_hits.pack(side="left", fill="x", expand=True, padx=6)
        self.bind_all("<FocusIn>", self._track_focus)

    def _track_focus(self, ev) -> None:
        w = ev.widget
        if w is getattr(self, "lookup_entry", None):
            return
        if isinstance(w, (tk.Entry, tk.Text)):
            self.last_target = w

    def _run_lookup(self) -> None:
        if not hasattr(self, "lookup_hits"):
            return
        rows = lookup(self.lookup_var.get(), self.lang)
        for child in self.lookup_hits.winfo_children():
            child.destroy()
        self.lookup_pick = rows[0] if rows else None
        for i, row in enumerate(rows[:5]):
            label = f"{row['label']}  {row['text']} {row.get('unit') or ''}".strip()
            btn = tk.Button(self.lookup_hits, text=label, command=lambda r=row: self._pick_lookup(r))
            self._paint_btn(btn, GREEN if i == 0 else BTN2)
            btn.configure(font=("Segoe UI", 9), padx=6, pady=2)
            btn.pack(side="left", padx=2)

    def _pick_lookup(self, row: dict) -> None:
        self.lookup_pick = row
        self._insert_lookup()

    def _insert_lookup(self) -> None:
        row = self.lookup_pick
        if not row:
            if hasattr(self, "status"):
                self.status.configure(text=self.tr("lookup_need_field"))
            return
        text = str(row.get("insert") or row.get("text") or "")
        w = self.last_target
        if w is None:
            if self.mode == "calc" and hasattr(self, "display"):
                self._insert_into_display(text)
            elif hasattr(self, "status"):
                self.status.configure(text=self.tr("lookup_need_field"))
            return
        try:
            if isinstance(w, tk.Text):
                w.insert("insert", text)
                return
            try:
                w.delete("sel.first", "sel.last")
            except tk.TclError:
                pass
            w.insert("insert", text)
        except Exception:
            if self.mode == "calc":
                self._insert_into_display(text)
        if w is getattr(self, "display", None):
            self.expr = self.display.get()

    def _bind_keys(self) -> None:
        modes = ["calc", "formulas", "poly", "numeric", "algo", "chem", "elements", "sources", "problems"]
        for i, mode in enumerate(modes, 1):
            self.bind_all(f"<Alt-Key-{i}>", lambda e, m=mode: self._hot_mode(m))
            self.bind_all(f"<Control-Key-{i}>", lambda e, m=mode: self._hot_mode(m))
        self.bind_all("<Alt-Key-0>", lambda e: self._hot_mode("circuits"))
        self.bind_all("<Control-Key-0>", lambda e: self._hot_mode("circuits"))
        self.bind_all("<Alt-g>", lambda e: self._hot_mode("graph"))
        self.bind_all("<Alt-G>", lambda e: self._hot_mode("graph"))
        self.bind_all("<Alt-m>", lambda e: self._hot_mode("matrix"))
        self.bind_all("<Alt-M>", lambda e: self._hot_mode("matrix"))
        self.bind_all("<Alt-d>", lambda e: self._hot_mode("stats"))
        self.bind_all("<Alt-D>", lambda e: self._hot_mode("stats"))
        self.bind_all("<Alt-t>", lambda e: self._hot_mode("triangle"))
        self.bind_all("<Alt-T>", lambda e: self._hot_mode("triangle"))
        self.bind_all("<Alt-l>", self._hot_lookup)
        self.bind_all("<Alt-L>", self._hot_lookup)
        self.bind_all("<Control-l>", self._hot_lookup)
        self.bind_all("<Control-L>", self._hot_lookup)
        self.bind_all("<Key>", self._global_key)

    def _hot_mode(self, mode: str, _ev=None):
        self._set_mode(mode)
        return "break"

    def _hot_lookup(self, _ev=None):
        if hasattr(self, "lookup_entry"):
            self.lookup_entry.focus_set()
            self.lookup_entry.selection_range(0, "end")
        return "break"

    def _focus_mode(self, mode: str) -> None:
        if mode == "calc" and hasattr(self, "display"):
            self.display.focus_set()
            if self.display.get() == "0":
                self.display.selection_range(0, "end")
        elif mode == "formulas" and hasattr(self, "search_entry"):
            self.search_entry.focus_set()
        elif mode == "poly" and getattr(self, "coeff_entries", None):
            self.coeff_entries[-1].focus_set()
        elif mode == "numeric" and hasattr(self, "n_func"):
            self.n_func.focus_set()
        elif mode == "algo" and hasattr(self, "algo_search"):
            self.algo_search.focus_set()
        elif mode == "chem" and hasattr(self, "chem_eq"):
            self.chem_eq.focus_set()
        elif mode == "elements" and hasattr(self, "el_q"):
            self.el_q.focus_set()
        elif mode == "problems" and hasattr(self, "prob_text"):
            self.prob_text.focus_set()
        elif mode == "circuits" and hasattr(self, "cir_text"):
            self.cir_text.focus_set()
        elif mode == "graph" and hasattr(self, "graph_text"):
            self.graph_text.focus_set()
        elif mode == "matrix" and hasattr(self, "mat_a"):
            self.mat_a.focus_set()
        elif mode == "stats" and hasattr(self, "stats_text"):
            self.stats_text.focus_set()
        elif mode == "triangle" and hasattr(self, "tri_a"):
            self.tri_a.focus_set()

    def _is_typing_widget(self, w) -> bool:
        return isinstance(w, (tk.Entry, tk.Text, ttk.Entry, ttk.Combobox))

    def _global_key(self, ev):
        w = ev.widget
        if self._is_typing_widget(w):
            return
        if ev.state & 0x4 or ev.state & 0x8:
            return
        if ev.keysym in {"Alt_L", "Alt_R", "Control_L", "Control_R", "Shift_L", "Shift_R", "Super_L", "Super_R"}:
            return
        if ev.char == "/" or ev.keysym == "slash":
            return self._hot_lookup()
        if self.mode != "calc":
            return
        if ev.keysym in {"Return", "KP_Enter"}:
            self._key("=")
            return "break"
        if ev.keysym == "Escape":
            self._key("AC")
            return "break"
        if ev.keysym == "BackSpace":
            self._key("C")
            return "break"
        if ev.char and ev.char.isprintable() and (ev.char.isalnum() or ev.char in ".+-*/()^=%,"):
            if hasattr(self, "display"):
                self.display.focus_set()
                self._insert_into_display("**" if ev.char == "^" else ev.char)
            return "break"

    def _select_all_display(self, _ev=None):
        self.display.selection_range(0, "end")
        self.display.icursor("end")
        return "break"

    def _on_display_focus(self, _ev=None) -> None:
        if self.display.get() == "0":
            self.display.selection_range(0, "end")

    def _sync_expr(self, _ev=None) -> None:
        if not hasattr(self, "display"):
            return
        text = self.display.get()
        self.expr = "" if text == "0" else text

    def _on_display_key(self, ev):
        if ev.keysym in {"Return", "KP_Enter"}:
            self._key("=")
            return "break"
        if ev.keysym == "Escape":
            self._key("AC")
            return "break"
        if ev.char == "^":
            self._insert_into_display("**")
            return "break"
        if ev.char and (ev.char.isdigit() or ev.char == ".") and self.display.get() == "0":
            try:
                all_sel = (
                    self.display.selection_present()
                    and int(self.display.index("sel.first")) == 0
                    and int(self.display.index("sel.last")) == 1
                )
            except (tk.TclError, ValueError):
                all_sel = False
            i = int(self.display.index("insert"))
            if all_sel or i >= 1:
                if not all_sel:
                    self.display.delete(0, "end")
        return None

    def _insert_into_display(self, s: str) -> None:
        w = self.display
        try:
            if w.selection_present():
                first = int(w.index("sel.first"))
                last = int(w.index("sel.last"))
                whole = first == 0 and last == len(w.get())
                if whole and s and s[0] in "+-*/%":
                    w.selection_clear()
                    w.icursor("end")
                else:
                    w.delete("sel.first", "sel.last")
        except (tk.TclError, ValueError):
            pass
        cur = w.get()
        if cur == "0" and s and (s[0].isdigit() or s[0] == "."):
            w.delete(0, "end")
        w.insert("insert", s)
        self.expr = w.get()
        if self.expr == "0":
            self.expr = ""
        w.focus_set()

    def _read_display(self) -> str:
        try:
            text = self.display.get().strip()
        except Exception:
            text = self.expr
        self.expr = text
        return text or "0"

    # ---------- calculator ----------
    def _build_calc(self, root: tk.Frame) -> None:
        left = tk.Frame(root, bg=BG)
        left.pack(side="left", fill="both", expand=True)
        right = tk.Frame(root, bg=PANEL, width=260)
        right.pack(side="right", fill="y", padx=(10, 0))
        right.pack_propagate(False)

        self.display = tk.Entry(
            left,
            justify="right",
            bg="#11141a",
            fg=FG,
            insertbackground=ACCENT,
            relief="flat",
            font=("Consolas", 28),
            highlightthickness=1,
            highlightbackground="#11141a",
            highlightcolor=ACCENT,
        )
        self.display.insert(0, "0")
        self.display.pack(fill="x", pady=(0, 4), ipady=14)
        self.display.bind("<Return>", lambda e: self._key("=") or "break")
        self.display.bind("<KP_Enter>", lambda e: self._key("=") or "break")
        self.display.bind("<Escape>", lambda e: self._key("AC") or "break")
        self.display.bind("<KeyPress>", self._on_display_key)
        self.display.bind("<KeyRelease>", self._sync_expr)
        self.display.bind("<FocusIn>", self._on_display_focus)
        self.display.bind("<Control-a>", self._select_all_display)
        self.display.bind("<Control-A>", self._select_all_display)
        self.kbd_hint = tk.Label(
            left,
            text="",
            anchor="w",
            bg=BG,
            fg=MUTED,
            font=("Segoe UI", 9),
            wraplength=720,
            justify="left",
        )
        self.kbd_hint.pack(fill="x", pady=(0, 6))
        self.status = tk.Label(left, text="", anchor="w", bg=BG, fg=MUTED, font=("Segoe UI", 9))
        self.status.pack(fill="x")
        self.calc_steps = tk.Text(left, bg=PANEL, fg=FG, relief="flat", height=6, font=("Segoe UI", 10), wrap="word")
        self.calc_steps.pack(fill="x", pady=(4, 0))
        self.calc_steps.insert("1.0", "")

        bar = tk.Frame(left, bg=BG)
        bar.pack(fill="x", pady=6)
        self.angle_btn = tk.Button(bar, command=self._toggle_angle)
        self.eng_btn = tk.Button(bar, command=self._toggle_eng)
        self._paint_btn(self.angle_btn, GREEN)
        self._paint_btn(self.eng_btn, BTN2)
        self.angle_btn.pack(side="left", padx=3)
        self.eng_btn.pack(side="left", padx=3)

        keys = [
            ["MC", "MR", "M+", "M-", "AC", "C"],
            ["sin", "cos", "tan", "ln", "log", "log2"],
            ["asin", "acos", "atan", "exp", "10^x", "x^2"],
            ["sinh", "cosh", "tanh", "sqrt", "x^y", "n!"],
            ["pi", "e", "(", ")", "+/-", "/"],
            ["7", "8", "9", "*", "1/x", "%"],
            ["4", "5", "6", "-", "abs", "mod"],
            ["1", "2", "3", "+", "EE", "ans"],
            ["0", ".", "=", "ENG", "<-", ""],
        ]
        grid = tk.Frame(left, bg=BG)
        grid.pack(fill="both", expand=True, pady=6)
        for r, row in enumerate(keys):
            for c, label in enumerate(row):
                if not label:
                    continue
                color = ACCENT if label == "=" else (RED if label in {"AC", "C"} else BTN)
                btn = tk.Button(grid, text=label, command=lambda s=label: self._key(s))
                self._paint_btn(btn, color, "#1c1f24" if label == "=" else FG)
                btn.configure(font=("Consolas", 11), pady=10, takefocus=0)
                btn.grid(row=r, column=c, sticky="nsew", padx=3, pady=3)
        for i in range(6):
            grid.columnconfigure(i, weight=1)
        for i in range(len(keys)):
            grid.rowconfigure(i, weight=1)

        ttk.Label(right, text="", style="Panel.TLabel").pack(anchor="w", padx=10, pady=(10, 4))
        self.hist_title = tk.Label(right, text="", bg=PANEL, fg=ACCENT, font=("Segoe UI", 11, "bold"))
        self.hist_title.pack(anchor="w", padx=10, pady=(8, 4))
        self.history = tk.Listbox(right, bg="#11141a", fg=FG, highlightthickness=0, bd=0, font=("Consolas", 10))
        self.history.pack(fill="both", expand=True, padx=8, pady=8)
        self.history.bind("<Double-Button-1>", self._hist_use)
        self.history.bind("<Return>", self._hist_use)

    def _toggle_angle(self) -> None:
        self.engine.angle = "RAD" if self.engine.angle == "DEG" else "DEG"
        self.angle_btn.configure(text=self.tr("deg") if self.engine.angle == "DEG" else self.tr("rad"))

    def _toggle_eng(self) -> None:
        self.engine.eng = not self.engine.eng
        self._paint_btn(self.eng_btn, GREEN if self.engine.eng else BTN2)

    def _set_display(self, text: str) -> None:
        shown = text if text else "0"
        self.display.delete(0, "end")
        self.display.insert(0, shown)
        self.display.icursor("end")

    def _key(self, label: str) -> None:
        mapping = {
            "sin": "sin(",
            "cos": "cos(",
            "tan": "tan(",
            "asin": "asin(",
            "acos": "acos(",
            "atan": "atan(",
            "sinh": "sinh(",
            "cosh": "cosh(",
            "tanh": "tanh(",
            "ln": "ln(",
            "log": "log10(",
            "log2": "log2(",
            "exp": "exp(",
            "10^x": "10**(",
            "x^2": "**2",
            "x^y": "**",
            "sqrt": "sqrt(",
            "n!": "factorial(",
            "abs": "abs(",
            "mod": "%",
            "1/x": "1/(",
            "pi": "pi",
            "e": "e",
            "ans": "ans",
            "EE": "*10**",
        }
        if label == "AC":
            self.expr = ""
            self._set_display("0")
            self.display.focus_set()
            self.display.selection_range(0, "end")
            return
        if label in {"C", "<-"}:
            try:
                if self.display.selection_present():
                    self.display.delete("sel.first", "sel.last")
                else:
                    i = int(self.display.index("insert"))
                    if i > 0:
                        self.display.delete(i - 1)
            except (tk.TclError, ValueError):
                self.expr = self.expr[:-1]
                self._set_display(self.expr or "0")
                return
            self.expr = self.display.get()
            if not self.expr:
                self._set_display("0")
            self.display.focus_set()
            return
        if label == "+/-":
            current = self._read_display()
            if current.startswith("-(") and current.endswith(")"):
                current = current[2:-1]
            else:
                current = f"-({current or '0'})"
            self.expr = current
            self._set_display(self.expr)
            self.display.focus_set()
            return
        if label == "MC":
            self.engine.memory = 0.0
            return
        if label == "MR":
            self._insert_into_display(format(self.engine.memory, "g"))
            return
        if label == "M+":
            out = self.engine.evaluate(self._read_display() or "0")
            try:
                self.engine.memory += float(out["value"].real if isinstance(out["value"], complex) else out["value"])
            except Exception:
                pass
            return
        if label == "M-":
            out = self.engine.evaluate(self._read_display() or "0")
            try:
                self.engine.memory -= float(out["value"].real if isinstance(out["value"], complex) else out["value"])
            except Exception:
                pass
            return
        if label == "ENG":
            self._toggle_eng()
            return
        if label == "%":
            out = self.engine.evaluate(f"({self._read_display() or '0'})/100")
            self.expr = out["text"]
            self._set_display(self.expr)
            self.display.focus_set()
            return
        if label == "=":
            source = self._read_display() or "0"
            out = self.engine.evaluate(source, lang=self.lang)
            shown = out["text"]
            self.history.insert(0, f"{source} = {shown}")
            self.expr = shown
            self._set_display(shown)
            self.status.configure(text=out.get("exact") or self.tr("ready"))
            self._show_steps(self.calc_steps, out.get("steps") or [])
            self.display.focus_set()
            self.display.selection_range(0, "end")
            return
        self._insert_into_display(mapping.get(label, label))

    def _hist_use(self, _evt=None) -> None:
        sel = self.history.curselection()
        if not sel:
            return
        line = self.history.get(sel[0])
        if "=" in line:
            self.expr = line.split("=", 1)[0].strip()
            self._set_display(self.expr)
            self.display.focus_set()
            self.display.icursor("end")

    # ---------- formulas ----------
    def _build_formulas(self, root: tk.Frame) -> None:
        left = tk.Frame(root, bg=BG, width=260)
        left.pack(side="left", fill="y")
        mid = tk.Frame(root, bg=BG, width=280)
        mid.pack(side="left", fill="both", expand=False, padx=8)
        right = tk.Frame(root, bg=PANEL)
        right.pack(side="left", fill="both", expand=True)

        self.cat_lbl = tk.Label(left, bg=BG, fg=ACCENT, font=("Segoe UI", 11, "bold"))
        self.cat_lbl.pack(anchor="w")
        self.cat_list = ttk.Treeview(left, columns=("name", "n"), show="headings", selectmode="browse", height=22)
        self.cat_list.heading("name", text="", anchor="w")
        self.cat_list.heading("n", text="", anchor="e")
        self.cat_list.column("name", width=200, stretch=True, anchor="w")
        self.cat_list.column("n", width=64, stretch=False, anchor="e")
        self.cat_list.pack(fill="both", expand=True, pady=6)
        self.cat_list.bind("<<TreeviewSelect>>", lambda e: self._fill_formula_list())

        self.search_lbl = tk.Label(mid, bg=BG, fg=ACCENT, font=("Segoe UI", 11, "bold"))
        self.search_lbl.pack(anchor="w")
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self._fill_formula_list())
        self.search_entry = tk.Entry(mid, textvariable=self.search_var, bg="#11141a", fg=FG, insertbackground=FG, relief="flat")
        self.search_entry.pack(fill="x", pady=6)
        self.search_entry.bind("<Return>", self._pick_first_formula)
        self.formula_list = tk.Listbox(mid, bg=PANEL, fg=FG, highlightthickness=0, bd=0, font=("Segoe UI", 10))
        self.formula_list.pack(fill="both", expand=True)
        self.formula_list.bind("<<ListboxSelect>>", self._on_formula_pick)
        self.formula_list.bind("<Return>", self._on_formula_pick)

        self.formula_title = tk.Label(right, bg=PANEL, fg=ACCENT, font=("Segoe UI", 14, "bold"), wraplength=480, justify="left")
        self.formula_title.pack(anchor="w", padx=12, pady=(12, 4))
        self.formula_expr = tk.Label(right, bg=PANEL, fg=FG, font=("Consolas", 13), wraplength=480, justify="left")
        self.formula_expr.pack(anchor="w", padx=12, pady=(0, 8))

        modebar = tk.Frame(right, bg=PANEL)
        modebar.pack(fill="x", padx=12, pady=4)
        self.single_btn = tk.Button(modebar, command=lambda: self._set_solver_mode(False))
        self.system_btn = tk.Button(modebar, command=lambda: self._set_solver_mode(True))
        self._paint_btn(self.single_btn, GREEN)
        self._paint_btn(self.system_btn, BTN2)
        self.single_btn.pack(side="left", padx=3)
        self.system_btn.pack(side="left", padx=3)
        self.system = False

        self.var_box = tk.Frame(right, bg=PANEL)
        self.var_box.pack(fill="both", expand=True, padx=12, pady=8)

        bot = tk.Frame(right, bg=PANEL)
        bot.pack(fill="x", padx=12, pady=8)
        self.solve_btn = tk.Button(bot, command=self._solve_current)
        self.add_eq_btn = tk.Button(bot, command=self._add_eq)
        self.del_eq_btn = tk.Button(bot, command=self._del_eq)
        self._paint_btn(self.solve_btn, ACCENT, "#1c1f24")
        self._paint_btn(self.add_eq_btn, BTN2)
        self._paint_btn(self.del_eq_btn, BTN2)
        self.solve_btn.pack(side="left")
        self.add_eq_btn.pack(side="left", padx=4)
        self.del_eq_btn.pack(side="left")

        self.formula_result = tk.Label(right, bg=PANEL, fg=FG, font=("Consolas", 16), wraplength=500, justify="left")
        self.formula_result.pack(anchor="w", padx=12, pady=(0, 4))
        self.formula_steps = tk.Text(right, bg="#11141a", fg=FG, relief="flat", height=10, font=("Segoe UI", 10), wrap="word")
        self.formula_steps.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        self._fill_categories()
        self._fill_formula_list()
        self._set_solver_mode(False)

    def _set_solver_mode(self, system: bool) -> None:
        self.system = system
        self._paint_btn(self.single_btn, GREEN if not system else BTN2)
        self._paint_btn(self.system_btn, GREEN if system else BTN2)
        if self.formula_id:
            self._show_formula(self.formula_id)
        else:
            self._show_system_editor()

    def _fill_categories(self) -> None:
        for row in self.cat_list.get_children():
            self.cat_list.delete(row)
        total = len(self.engine.formulas)
        self.cat_list.insert("", "end", iid="all", values=(self.tr("all_cats"), total))
        for key in sorted(self.engine.categories.keys()):
            names = self.engine.categories[key]
            label = names.get(self.lang) or names.get("en") or key
            n = self.engine.cat_counts.get(key, 0)
            self.cat_list.insert("", "end", iid=key, values=(label, n))
        self.cat_lbl.configure(text=f"{self.tr('categories')}  ({total})")

    def _selected_category(self) -> str | None:
        sel = self.cat_list.selection()
        if not sel:
            return None
        key = sel[0]
        return None if key == "all" else key

    def _fill_formula_list(self) -> None:
        query = self.search_var.get() if hasattr(self, "search_var") else ""
        cat = self._selected_category()
        items = self.engine.search(query, self.lang)
        if cat:
            items = [it for it in items if it["category"] == cat]
        self.formula_items = items
        self.formula_list.delete(0, "end")
        for it in items:
            name = it["name"].get(self.lang) or it["name"].get("en")
            self.formula_list.insert("end", name)
        if hasattr(self, "search_lbl"):
            self.search_lbl.configure(text=f"{self.tr('search')}  ({len(items)})")

    def _pick_first_formula(self, _evt=None):
        if not getattr(self, "formula_items", None):
            return "break"
        self.formula_list.selection_clear(0, "end")
        self.formula_list.selection_set(0)
        self.formula_list.activate(0)
        self._show_formula(self.formula_items[0]["id"])
        self._focus_first_var()
        return "break"

    def _focus_first_var(self) -> None:
        if self.var_widgets:
            next(iter(self.var_widgets.values())).focus_set()
        elif getattr(self, "eq_entries", None):
            self.eq_entries[0].focus_set()

    def _on_formula_pick(self, _evt=None) -> None:
        sel = self.formula_list.curselection()
        if not sel:
            return
        item = self.formula_items[sel[0]]
        self._show_formula(item["id"])
        if _evt is not None and getattr(_evt, "keysym", "") == "Return":
            self._focus_first_var()

    def _clear_vars(self) -> None:
        for child in self.var_box.winfo_children():
            child.destroy()
        self.var_widgets = {}

    def _show_formula(self, fid: str) -> None:
        self.formula_id = fid
        item = self.engine.by_id[fid]
        self.formula_title.configure(text=item["name"].get(self.lang) or item["name"]["en"])
        self.formula_expr.configure(text=item["expr"])
        self._clear_vars()
        if self.system:
            self._show_system_editor(seed=item["expr"])
            return
        names = list(item["variables"].keys())
        self.unknown_var.set(names[0] if names else "")
        for name, meta in item["variables"].items():
            row = tk.Frame(self.var_box, bg=PANEL)
            row.pack(fill="x", pady=3)
            label = meta["name"].get(self.lang) or meta["name"]["en"]
            unit = meta.get("unit") or ""
            rb = tk.Radiobutton(
                row,
                text="",
                variable=self.unknown_var,
                value=name,
                bg=PANEL,
                fg=FG,
                selectcolor=BG,
                activebackground=PANEL,
            )
            rb.pack(side="left")
            tk.Label(row, text=f"{name}  {label}  [{unit}]", bg=PANEL, fg=FG, width=36, anchor="w").pack(side="left")
            ent = tk.Entry(row, bg="#11141a", fg=FG, insertbackground=FG, relief="flat", width=16)
            ent.pack(side="right")
            ent.bind("<Return>", lambda e: self._solve_current() or "break")
            self.var_widgets[name] = ent
        self.formula_result.configure(text="")

    def _show_system_editor(self, seed: str | None = None) -> None:
        self._clear_vars()
        if seed and not self.system_eqs:
            self.system_eqs = [seed]
        if not self.system_eqs:
            self.system_eqs = ["x + y = 1", "x - y = 0"]
        if not self.system_unknowns:
            self.system_unknowns = ["x", "y"]
        tk.Label(self.var_box, text=self.tr("system_mode"), bg=PANEL, fg=ACCENT).pack(anchor="w")
        self.eq_entries = []
        for eq in self.system_eqs:
            ent = tk.Entry(self.var_box, bg="#11141a", fg=FG, insertbackground=FG, relief="flat")
            ent.insert(0, eq)
            ent.pack(fill="x", pady=3)
            ent.bind("<Return>", lambda e: self._solve_current() or "break")
            self.eq_entries.append(ent)
        tk.Label(self.var_box, text=self.tr("unknown"), bg=PANEL, fg=MUTED).pack(anchor="w", pady=(8, 2))
        self.unk_entry = tk.Entry(self.var_box, bg="#11141a", fg=FG, insertbackground=FG, relief="flat")
        self.unk_entry.insert(0, ", ".join(self.system_unknowns))
        self.unk_entry.pack(fill="x")
        self.unk_entry.bind("<Return>", lambda e: self._solve_current() or "break")

    def _add_eq(self) -> None:
        self.system = True
        current = [e.get() for e in getattr(self, "eq_entries", [])] or list(self.system_eqs)
        current.append("0 = 0")
        self.system_eqs = current
        if len(self.system_unknowns) < len(current):
            nxt = chr(ord("x") + (len(self.system_unknowns) % 3))
            name = nxt if nxt not in self.system_unknowns else f"u{len(self.system_unknowns)}"
            self.system_unknowns.append(name)
        self._show_system_editor()

    def _del_eq(self) -> None:
        current = [e.get() for e in getattr(self, "eq_entries", [])] or list(self.system_eqs)
        if len(current) > 1:
            current.pop()
        self.system_eqs = current
        if len(self.system_unknowns) > 1:
            self.system_unknowns.pop()
        self._show_system_editor()

    def _solve_current(self) -> None:
        if self.system:
            eqs = [e.get() for e in getattr(self, "eq_entries", [])]
            raw = self.unk_entry.get() if hasattr(self, "unk_entry") else "x"
            unknowns = [p.strip() for p in raw.replace(";", ",").split(",") if p.strip()] or ["x"]
            self.system_eqs = eqs
            self.system_unknowns = unknowns
            out = self.engine.solve_system(eqs, unknowns, lang=self.lang)
            if out["solutions"]:
                lines = []
                for i, sol in enumerate(out["solutions"], 1):
                    parts = [f"{k} = {v}" for k, v in sol.items()]
                    lines.append(f"{i})  " + "   ".join(parts))
                self.formula_result.configure(text="\n".join(lines))
            else:
                self.formula_result.configure(text="0")
            self._show_steps(self.formula_steps, out.get("steps") or [])
            return
        if not self.formula_id:
            self.formula_result.configure(text=self.tr("pick_formula"))
            return
        values = {name: ent.get() for name, ent in self.var_widgets.items()}
        unknown = self.unknown_var.get() or None
        out = self.engine.solve_formula(self.formula_id, values, unknown, lang=self.lang)
        extra = ""
        if out.get("all") and len(out["all"]) > 1:
            extra = "  |  " + ", ".join(out["all"][1:])
        unit = out.get("unit") or ""
        self.formula_result.configure(
            text=f"{self.tr('solved_for')} {out.get('unknown')} = {out.get('text')} {unit}{extra}"
        )
        self._show_steps(self.formula_steps, out.get("steps") or [])

    # ---------- polynomial ----------
    def _build_poly(self, root: tk.Frame) -> None:
        tk.Label(root, text="a6 x^6 + a5 x^5 + a4 x^4 + a3 x^3 + a2 x^2 + a1 x + a0", bg=BG, fg=ACCENT, font=("Consolas", 12)).pack(anchor="w")
        row = tk.Frame(root, bg=BG)
        row.pack(fill="x", pady=10)
        self.coeff_entries = []
        for i, lab in enumerate(["a6", "a5", "a4", "a3", "a2", "a1", "a0"]):
            box = tk.Frame(row, bg=BG)
            box.pack(side="left", padx=6)
            tk.Label(box, text=lab, bg=BG, fg=MUTED).pack()
            ent = tk.Entry(box, width=8, bg="#11141a", fg=FG, insertbackground=FG, relief="flat", justify="center")
            ent.insert(0, "0" if i < 6 else "0")
            ent.pack()
            ent.bind("<Return>", lambda e: self._poly_eval() or "break")
            self.coeff_entries.append(ent)
        self.coeff_entries[-1].delete(0, "end")
        self.coeff_entries[-1].insert(0, "0")
        self.coeff_entries[-2].delete(0, "end")
        self.coeff_entries[-2].insert(0, "1")
        xr = tk.Frame(root, bg=BG)
        xr.pack(fill="x", pady=6)
        tk.Label(xr, text="x", bg=BG, fg=MUTED).pack(side="left")
        self.poly_x = tk.Entry(xr, width=10, bg="#11141a", fg=FG, insertbackground=FG, relief="flat")
        self.poly_x.insert(0, "1")
        self.poly_x.pack(side="left", padx=6)
        self.poly_x.bind("<Return>", lambda e: self._poly_eval() or "break")
        self.poly_eval_btn = tk.Button(xr, command=self._poly_eval)
        self.poly_root_btn = tk.Button(xr, command=self._poly_roots)
        self._paint_btn(self.poly_eval_btn, ACCENT, "#1c1f24")
        self._paint_btn(self.poly_root_btn, BTN2)
        self.poly_eval_btn.pack(side="left", padx=4)
        self.poly_root_btn.pack(side="left", padx=4)
        self.poly_out = tk.Text(root, bg=PANEL, fg=FG, relief="flat", height=16, font=("Consolas", 11))
        self.poly_out.pack(fill="both", expand=True, pady=8)

    def _poly_coeffs(self) -> list[float]:
        vals = []
        for ent in self.coeff_entries:
            vals.append(clean_number(ent.get(), 0.0) or 0.0)
        return vals

    def _show_steps(self, box, lines) -> None:
        if box is None:
            return
        try:
            box.delete("1.0", "end")
            box.insert("1.0", teach.format_steps(list(lines or [])))
        except Exception:
            pass

    def _poly_eval(self) -> None:
        x = clean_number(self.poly_x.get(), 0.0) or 0.0
        out = self.engine.polynomial(self._poly_coeffs(), x)
        der = " + ".join(f"{a:g} x^{len(out['derivative'])-1-i}" for i, a in enumerate(out["derivative"]))
        integ = " + ".join(f"{a:g} x^{len(out['integral'])-1-i}" for i, a in enumerate(out["integral"]))
        text = (
            f"p(x) = {out['value_text']}\n"
            f"degree = {out['degree']}\n"
            f"{self.tr('derivative')}: {der}\n"
            f"{self.tr('integral')}: {integ} + C\n"
        )
        self.poly_out.delete("1.0", "end")
        extra = teach.format_steps(teach.steps_poly(self.lang, "eval", x, out["value_text"], out["degree"], None))
        self.poly_out.insert("1.0", text + "\n" + extra)

    def _poly_roots(self) -> None:
        out = self.engine.polynomial(self._poly_coeffs(), None)
        lines = [self.tr("roots") + ":"] + [f"  {r}" for r in out["roots"]] or ["  0"]
        self.poly_out.delete("1.0", "end")
        extra = teach.format_steps(teach.steps_poly(self.lang, "roots", None, "", None, out["roots"]))
        self.poly_out.insert("1.0", "\n".join(lines) + "\n\n" + extra)

    # ---------- numeric ----------
    def _build_numeric(self, root: tk.Frame) -> None:
        form = tk.Frame(root, bg=BG)
        form.pack(fill="x")
        self.n_func = self._labeled_entry(form, "f(x)  or  f(x,y)", "x**2")
        self.n_a = self._labeled_entry(form, "a / x0", "0")
        self.n_b = self._labeled_entry(form, "b / x1", "1")
        self.n_y0 = self._labeled_entry(form, "y0", "1")
        self.n_steps = self._labeled_entry(form, "steps", "40")
        btns = tk.Frame(root, bg=BG)
        btns.pack(fill="x", pady=8)
        self.n_root_btn = tk.Button(btns, command=self._do_root)
        self.n_int_btn = tk.Button(btns, command=self._do_int)
        self.n_diff_btn = tk.Button(btns, command=self._do_diff)
        self.n_ode_btn = tk.Button(btns, command=self._do_ode)
        self.n_ode2_btn = tk.Button(btns, command=self._do_ode2)
        self.n_sys_btn = tk.Button(btns, command=self._do_odesys)
        for b in (self.n_root_btn, self.n_int_btn, self.n_diff_btn, self.n_ode_btn, self.n_ode2_btn, self.n_sys_btn):
            self._paint_btn(b, BTN2)
            b.pack(side="left", padx=4)
        self.n_yp0 = self._labeled_entry(form, "y'(x0)", "0")
        self.n_out = tk.Text(root, bg=PANEL, fg=FG, relief="flat", height=16, font=("Consolas", 11))
        self.n_out.pack(fill="both", expand=True)

    def _labeled_entry(self, parent, label, default):
        row = tk.Frame(parent, bg=BG)
        row.pack(fill="x", pady=3)
        tk.Label(row, text=label, bg=BG, fg=MUTED, width=16, anchor="w").pack(side="left")
        ent = tk.Entry(row, bg="#11141a", fg=FG, insertbackground=FG, relief="flat")
        ent.insert(0, default)
        ent.pack(side="left", fill="x", expand=True)
        return ent

    def _do_root(self) -> None:
        a = clean_number(self.n_a.get(), 0.0) or 0.0
        b = clean_number(self.n_b.get(), 1.0) or 1.0
        out = self.engine.numeric_root(self.n_func.get(), a, b)
        self.n_out.delete("1.0", "end")
        extra = teach.format_steps(teach.steps_numeric(self.lang, "root", a, b, None, out["text"]))
        self.n_out.insert("1.0", f"root = {out['text']}\n\n{extra}")

    def _do_int(self) -> None:
        a = clean_number(self.n_a.get(), 0.0) or 0.0
        b = clean_number(self.n_b.get(), 1.0) or 1.0
        out = self.engine.numeric_integral(self.n_func.get(), a, b)
        extra = f"\nexact: {out['exact']}" if out.get("exact") else ""
        self.n_out.delete("1.0", "end")
        teach_l = teach.format_steps(teach.steps_numeric(self.lang, "integral", a, b, None, out["text"]))
        self.n_out.insert("1.0", f"integral = {out['text']}{extra}\n\n{teach_l}")

    def _do_diff(self) -> None:
        x0 = clean_number(self.n_a.get(), 0.0) or 0.0
        out = self.engine.numeric_derivative(self.n_func.get(), x0)
        extra = f"\n{out.get('exact','')}"
        self.n_out.delete("1.0", "end")
        teach_l = teach.format_steps(teach.steps_numeric(self.lang, "deriv", x0, None, None, out["text"]))
        self.n_out.insert("1.0", f"d/dx = {out['text']}{extra}\n\n{teach_l}")

    def _do_ode(self) -> None:
        x0 = clean_number(self.n_a.get(), 0.0) or 0.0
        x1 = clean_number(self.n_b.get(), 1.0) or 1.0
        y0 = clean_number(self.n_y0.get(), 0.0) or 0.0
        steps = int(clean_number(self.n_steps.get(), 40.0) or 40)
        out = self.engine.numeric_ode(self.n_func.get(), x0, y0, x1, steps)
        lines = [f"y({x1:g}) = {out['text']}", ""]
        for xv, yv in out.get("path", [])[-20:]:
            lines.append(f"{xv:10.5g}   {yv:10.5g}")
        self.n_out.delete("1.0", "end")
        teach_l = teach.format_steps(teach.steps_numeric(self.lang, "ode", x0, x1, y0, out["text"]))
        self.n_out.insert("1.0", "\n".join(lines) + "\n\n" + teach_l)

    def _build_algo(self, root: tk.Frame) -> None:
        left = tk.Frame(root, bg=BG, width=240)
        left.pack(side="left", fill="y")
        mid = tk.Frame(root, bg=BG, width=280)
        mid.pack(side="left", fill="both", expand=False, padx=8)
        right = tk.Frame(root, bg=PANEL)
        right.pack(side="left", fill="both", expand=True)

        self.algo_cat_lbl = tk.Label(left, bg=BG, fg=ACCENT, font=("Segoe UI", 11, "bold"))
        self.algo_cat_lbl.pack(anchor="w")
        self.algo_cats = tk.Listbox(left, bg=PANEL, fg=FG, highlightthickness=0, bd=0, font=("Segoe UI", 10), width=30)
        self.algo_cats.pack(fill="both", expand=True, pady=6)
        self.algo_cats.bind("<<ListboxSelect>>", lambda e: self._fill_algos())

        self.algo_search_lbl = tk.Label(mid, bg=BG, fg=ACCENT, font=("Segoe UI", 11, "bold"))
        self.algo_search_lbl.pack(anchor="w")
        self.algo_q = tk.StringVar()
        self.algo_q.trace_add("write", lambda *_: self._fill_algos())
        self.algo_search = tk.Entry(mid, textvariable=self.algo_q, bg="#11141a", fg=FG, insertbackground=FG, relief="flat")
        self.algo_search.pack(fill="x", pady=6)
        self.algo_search.bind("<Return>", self._pick_first_algo)
        self.algo_list = tk.Listbox(mid, bg=PANEL, fg=FG, highlightthickness=0, bd=0, font=("Segoe UI", 10))
        self.algo_list.pack(fill="both", expand=True)
        self.algo_list.bind("<<ListboxSelect>>", self._on_algo_pick)
        self.algo_list.bind("<Return>", self._on_algo_pick)

        self.algo_title = tk.Label(right, bg=PANEL, fg=ACCENT, font=("Segoe UI", 14, "bold"), wraplength=480, justify="left")
        self.algo_title.pack(anchor="w", padx=12, pady=(12, 4))
        self.algo_hint = tk.Label(right, bg=PANEL, fg=MUTED, font=("Segoe UI", 9), wraplength=480, justify="left")
        self.algo_hint.pack(anchor="w", padx=12)
        self.algo_box = tk.Frame(right, bg=PANEL)
        self.algo_box.pack(fill="both", expand=True, padx=12, pady=8)
        bot = tk.Frame(right, bg=PANEL)
        bot.pack(fill="x", padx=12, pady=8)
        self.algo_run_btn = tk.Button(bot, command=self._run_algo)
        self._paint_btn(self.algo_run_btn, ACCENT, "#1c1f24")
        self.algo_run_btn.pack(side="left")
        self.algo_out = tk.Text(right, bg="#11141a", fg=FG, relief="flat", height=10, font=("Consolas", 12))
        self.algo_out.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        self.algo_id = None
        self.algo_fields = {}
        self.algo_items = []
        self._fill_algo_cats()
        self._fill_algos()

    def _fill_algo_cats(self) -> None:
        cats, items, _ = algo_catalog()
        counts = {}
        for row in items:
            key = row.get("category") or ""
            counts[key] = counts.get(key, 0) + 1
        self.algo_cats.delete(0, "end")
        self.algo_cat_keys = ["all"]
        self.algo_cats.insert("end", f"{self.tr('all_cats')}  ({len(items)})")
        for key in sorted(cats):
            names = cats[key]
            label = names.get(self.lang) or names.get("en") or key
            n = counts.get(key, 0)
            self.algo_cat_keys.append(key)
            self.algo_cats.insert("end", f"{label}  ({n})")

    def _selected_algo_cat(self) -> str | None:
        sel = self.algo_cats.curselection()
        if not sel:
            return None
        key = self.algo_cat_keys[sel[0]]
        return None if key == "all" else key

    def _fill_algos(self) -> None:
        q = self.algo_q.get() if hasattr(self, "algo_q") else ""
        cat = self._selected_algo_cat() if hasattr(self, "algo_cats") else None
        items = list_algos(q, self.lang, cat)
        self.algo_items = items
        self.algo_list.delete(0, "end")
        for it in items:
            self.algo_list.insert("end", it["name"])

    def _pick_first_algo(self, _evt=None):
        if not self.algo_items:
            return "break"
        self.algo_list.selection_clear(0, "end")
        self.algo_list.selection_set(0)
        self.algo_list.activate(0)
        self._show_algo(self.algo_items[0])
        return "break"

    def _on_algo_pick(self, _evt=None) -> None:
        sel = self.algo_list.curselection()
        if not sel:
            return
        self._show_algo(self.algo_items[sel[0]])

    def _show_algo(self, item: dict) -> None:
        self.algo_id = item["id"]
        self.algo_title.configure(text=item["name"])
        self.algo_hint.configure(text=self.tr("algo_hint"))
        for child in self.algo_box.winfo_children():
            child.destroy()
        self.algo_fields = {}
        for name, meta in (item.get("params") or {}).items():
            row = tk.Frame(self.algo_box, bg=PANEL)
            row.pack(fill="x", pady=3)
            label = (meta.get("name") or {}).get(self.lang) or (meta.get("name") or {}).get("en") or name
            tk.Label(row, text=f"{name}  {label}", bg=PANEL, fg=FG, width=28, anchor="w").pack(side="left")
            ent = tk.Entry(row, bg="#11141a", fg=FG, insertbackground=FG, relief="flat")
            ent.insert(0, str(meta.get("default") or ""))
            ent.pack(side="left", fill="x", expand=True)
            ent.bind("<Return>", lambda e: self._run_algo() or "break")
            self.algo_fields[name] = ent
        self.algo_out.delete("1.0", "end")
        if self.algo_fields:
            next(iter(self.algo_fields.values())).focus_set()

    def _run_algo(self) -> None:
        if not self.algo_id:
            self.algo_out.delete("1.0", "end")
            self.algo_out.insert("1.0", self.tr("pick_algo"))
            return
        values = {name: ent.get() for name, ent in self.algo_fields.items()}
        out = run_algo(self.algo_id, values, self.engine.eng)
        text = out.get("text") or "0"
        extra = out.get("detail") or ""
        self.algo_out.delete("1.0", "end")
        self.algo_out.insert("1.0", text + (("\n" + extra) if extra else ""))

    def _build_chem(self, root: tk.Frame) -> None:
        tk.Label(root, text="H2 + O2 = H2O    |    Ca(OH)2", bg=BG, fg=MUTED).pack(anchor="w")
        self.chem_eq = tk.Entry(root, bg="#11141a", fg=FG, insertbackground=FG, relief="flat")
        self.chem_eq.insert(0, "C2H6 + O2 = CO2 + H2O")
        self.chem_eq.pack(fill="x", pady=6)
        self.chem_eq.bind("<Return>", lambda e: self._do_balance() or "break")
        row = tk.Frame(root, bg=BG)
        row.pack(fill="x")
        self.chem_bal_btn = tk.Button(row, command=self._do_balance)
        self.chem_mw_btn = tk.Button(row, command=self._do_molar)
        self._paint_btn(self.chem_bal_btn, ACCENT, "#1c1f24")
        self._paint_btn(self.chem_mw_btn, BTN2)
        self.chem_bal_btn.pack(side="left", padx=4)
        self.chem_mw_btn.pack(side="left", padx=4)
        self.chem_out = tk.Text(root, bg=PANEL, fg=FG, relief="flat", height=16, font=("Consolas", 12))
        self.chem_out.pack(fill="both", expand=True, pady=8)

    def _do_balance(self) -> None:
        out = balance_equation(self.chem_eq.get())
        self.chem_out.delete("1.0", "end")
        raw = self.chem_eq.get()
        shown = out.get("text") or ""
        extra = teach.format_steps(teach.steps_chem(self.lang, raw, shown, False))
        self.chem_out.insert("1.0", shown + "\n\n" + extra)

    def _do_molar(self) -> None:
        out = molar_mass(self.chem_eq.get().split("=")[0].split("+")[0].strip())
        lines = [f"{out.get('text')} g/mol"]
        for sym, info in (out.get("detail") or {}).items():
            if isinstance(info, dict) and "count" in info:
                lines.append(f"  {sym}: {info['count']} x {info['mass']} = {info['contrib']}")
        extra = teach.format_steps(teach.steps_chem(self.lang, self.chem_eq.get(), out.get("text") or "0", True))
        self.chem_out.delete("1.0", "end")
        self.chem_out.insert("1.0", "\n".join(lines) + "\n\n" + extra)

    def _build_elements(self, root: tk.Frame) -> None:
        top = tk.Frame(root, bg=BG)
        top.pack(fill="x")
        self.el_q = tk.Entry(top, bg="#11141a", fg=FG, insertbackground=FG, relief="flat")
        self.el_q.pack(side="left", fill="x", expand=True)
        self.el_q.bind("<KeyRelease>", lambda e: self._fill_elements())
        body = tk.Frame(root, bg=BG)
        body.pack(fill="both", expand=True, pady=8)
        self.el_list = tk.Listbox(body, bg=PANEL, fg=FG, highlightthickness=0, bd=0, width=28, font=("Consolas", 10))
        self.el_list.pack(side="left", fill="y")
        self.el_list.bind("<<ListboxSelect>>", self._show_element)
        self.el_out = tk.Text(body, bg=PANEL, fg=FG, relief="flat", font=("Consolas", 11))
        self.el_out.pack(side="left", fill="both", expand=True, padx=(8, 0))
        self._el_items = []
        self._fill_elements()

    def _fill_elements(self) -> None:
        q = self.el_q.get() if hasattr(self, "el_q") else ""
        self._el_items = list_elements(q)
        self.el_list.delete(0, "end")
        for el in self._el_items:
            name = el["name"].get(self.lang) or el["name"]["en"]
            self.el_list.insert("end", f"{el['Z']:3}  {el['symbol']:<3}  {name}")

    def _pick_first_element(self, _evt=None):
        if not self._el_items:
            return "break"
        self.el_list.selection_clear(0, "end")
        self.el_list.selection_set(0)
        self.el_list.activate(0)
        self._show_element()
        return "break"

    def _show_element(self, _evt=None) -> None:
        sel = self.el_list.curselection()
        if not sel:
            return
        el = self._el_items[sel[0]]
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
            extra = iso.get("note") if iso.get("abundance") is not None and iso.get("note") else ""
            lines.append(f"  {el['symbol']}-{iso['A']}   {iso['mass']} u   {ab}  {extra}")
        self.el_out.delete("1.0", "end")
        self.el_out.insert("1.0", "\n".join(lines))

    def _build_problems(self, root: tk.Frame) -> None:
        self.prob_hint = tk.Label(
            root,
            bg=BG,
            fg=MUTED,
            wraplength=900,
            justify="left",
            font=("Segoe UI", 10),
        )
        self.prob_hint.pack(fill="x", pady=(0, 6))
        self.prob_text = tk.Text(
            root,
            bg="#11141a",
            fg=FG,
            insertbackground=FG,
            relief="flat",
            height=6,
            font=("Consolas", 14),
            wrap="word",
        )
        self.prob_text.pack(fill="x", pady=4)
        self.prob_text.insert("1.0", "2*x + 3 = 11")
        row = tk.Frame(root, bg=BG)
        row.pack(fill="x", pady=6)
        self.prob_unk_lbl = tk.Label(row, bg=BG, fg=MUTED)
        self.prob_unk_lbl.pack(side="left")
        self.prob_unk = tk.Entry(row, width=8, bg="#11141a", fg=FG, insertbackground=FG, relief="flat")
        self.prob_unk.insert(0, "x")
        self.prob_unk.pack(side="left", padx=6)
        self.prob_at_lbl = tk.Label(row, bg=BG, fg=MUTED)
        self.prob_at_lbl.pack(side="left", padx=(12, 0))
        self.prob_at = tk.Entry(row, width=10, bg="#11141a", fg=FG, insertbackground=FG, relief="flat")
        self.prob_at.pack(side="left", padx=6)
        self.prob_solve_btn = tk.Button(row, command=lambda: self._run_problem("solve"))
        self.prob_inv_btn = tk.Button(row, command=lambda: self._run_problem("inverse"))
        self._paint_btn(self.prob_solve_btn, ACCENT, "#1c1f24")
        self._paint_btn(self.prob_inv_btn, BTN2)
        self.prob_solve_btn.pack(side="left", padx=6)
        self.prob_inv_btn.pack(side="left", padx=4)
        self.prob_result = tk.Label(
            root,
            bg=PANEL,
            fg=FG,
            font=("Consolas", 16),
            wraplength=900,
            justify="left",
            anchor="w",
        )
        self.prob_result.pack(fill="x", pady=8, ipady=10)
        self.prob_steps = tk.Text(root, bg=PANEL, fg=FG, relief="flat", height=14, font=("Segoe UI", 10), wrap="word")
        self.prob_steps.pack(fill="both", expand=True)
        self.prob_text.bind("<Control-Return>", lambda e: self._run_problem("solve") or "break")
        self.prob_unk.bind("<Return>", lambda e: self._run_problem("solve") or "break")
        self.prob_at.bind("<Return>", lambda e: self._run_problem("inverse") or "break")

    def _run_problem(self, mode: str) -> None:
        try:
            raw = self.prob_text.get("1.0", "end").strip()
            unknown = (self.prob_unk.get() or "x").strip() or "x"
            at = (self.prob_at.get() or "").strip()
            out = run_problem(raw, mode=mode, unknown=unknown, at=at, lang=self.lang, eng=self.engine.eng)
        except Exception:
            out = {"text": "0", "steps": []}
        self.prob_result.configure(text=out.get("text") or "0")
        self._show_steps(self.prob_steps, out.get("steps") or [])

    def _build_circuits(self, root: tk.Frame) -> None:
        self.cir_hint = tk.Label(root, bg=BG, fg=MUTED, wraplength=900, justify="left", font=("Segoe UI", 10))
        self.cir_hint.pack(fill="x", pady=(0, 6))
        self.cir_text = tk.Text(root, bg="#11141a", fg=FG, insertbackground=FG, relief="flat", height=10, font=("Consolas", 13), wrap="word")
        self.cir_text.pack(fill="x", pady=4)
        self.cir_text.insert("1.0", "V1 1 0 12\nR1 1 2 1k\nR2 2 0 2k")
        row = tk.Frame(root, bg=BG)
        row.pack(fill="x", pady=6)
        self.cir_freq_lbl = tk.Label(row, bg=BG, fg=MUTED)
        self.cir_freq_lbl.pack(side="left")
        self.cir_freq = tk.Entry(row, width=10, bg="#11141a", fg=FG, insertbackground=FG, relief="flat")
        self.cir_freq.pack(side="left", padx=6)
        self.cir_solve_btn = tk.Button(row, command=lambda: self._run_circuit("solve"))
        self.cir_inv_btn = tk.Button(row, command=lambda: self._run_circuit("inverse"))
        self._paint_btn(self.cir_solve_btn, ACCENT, "#1c1f24")
        self._paint_btn(self.cir_inv_btn, BTN2)
        self.cir_solve_btn.pack(side="left", padx=6)
        self.cir_inv_btn.pack(side="left", padx=4)
        self.cir_result = tk.Label(root, bg=PANEL, fg=FG, font=("Consolas", 14), wraplength=900, justify="left", anchor="w")
        self.cir_result.pack(fill="x", pady=8, ipady=10)
        self.cir_steps = tk.Text(root, bg=PANEL, fg=FG, relief="flat", height=12, font=("Segoe UI", 10), wrap="word")
        self.cir_steps.pack(fill="both", expand=True)
        self.cir_text.bind("<Control-Return>", lambda e: self._run_circuit("solve") or "break")

    def _run_circuit(self, mode: str) -> None:
        try:
            raw = self.cir_text.get("1.0", "end").strip()
            freq = (self.cir_freq.get() or "").strip()
            out = run_circuit(raw, mode=mode, freq=freq, lang=self.lang, eng=self.engine.eng)
        except Exception:
            out = {"text": "0", "steps": []}
        self.cir_result.configure(text=out.get("text") or "0")
        self._show_steps(self.cir_steps, out.get("steps") or [])

    def _do_ode2(self) -> None:
        x0 = clean_number(self.n_a.get(), 0.0) or 0.0
        x1 = clean_number(self.n_b.get(), 1.0) or 1.0
        y0 = clean_number(self.n_y0.get(), 0.0) or 0.0
        yp0 = clean_number(self.n_yp0.get(), 0.0) or 0.0
        steps = int(clean_number(self.n_steps.get(), 40.0) or 40)
        out = self.engine.numeric_ode2(self.n_func.get(), x0, y0, yp0, x1, steps)
        self.n_out.delete("1.0", "end")
        self.n_out.insert("1.0", out.get("text") or "0")
        self.last_latex = out.get("text") or "0"

    def _do_odesys(self) -> None:
        x0 = clean_number(self.n_a.get(), 0.0) or 0.0
        x1 = clean_number(self.n_b.get(), 1.0) or 1.0
        steps = int(clean_number(self.n_steps.get(), 40.0) or 40)
        out = self.engine.numeric_odesys(self.n_func.get(), x0, self.n_y0.get(), x1, steps)
        self.n_out.delete("1.0", "end")
        self.n_out.insert("1.0", out.get("text") or "0")
        self.last_latex = out.get("text") or "0"

    def _build_graph(self, root: tk.Frame) -> None:
        self.graph_hint = tk.Label(root, bg=BG, fg=MUTED, wraplength=900, justify="left")
        self.graph_hint.pack(fill="x")
        self.graph_text = tk.Text(root, bg="#11141a", fg=FG, insertbackground=FG, relief="flat", height=6, font=("Consolas", 13))
        self.graph_text.pack(fill="x", pady=4)
        self.graph_text.insert("1.0", "sin(x)\nx**2/10")
        row = tk.Frame(root, bg=BG)
        row.pack(fill="x")
        self.graph_xmin = tk.Entry(row, width=8, bg="#11141a", fg=FG, insertbackground=FG, relief="flat")
        self.graph_xmax = tk.Entry(row, width=8, bg="#11141a", fg=FG, insertbackground=FG, relief="flat")
        self.graph_xmin.insert(0, "-10")
        self.graph_xmax.insert(0, "10")
        self.graph_xmin.pack(side="left", padx=4)
        self.graph_xmax.pack(side="left", padx=4)
        for lab, kind in (("plot", "func"), ("parametric", "param"), ("data", "data"), ("bode", "bode")):
            b = tk.Button(row, command=lambda k=kind: self._run_graph(k))
            self._paint_btn(b, ACCENT if kind == "func" else BTN2, "#1c1f24" if kind == "func" else FG)
            b.configure(text=self.tr(lab) if lab != "plot" else self.tr("plot"))
            b.pack(side="left", padx=3)
            setattr(self, f"graph_{kind}_btn", b)
        self.graph_svg = tk.Label(root, bg="#11141a")
        self.graph_svg.pack(fill="both", expand=True)
        self.graph_out = tk.Label(root, bg=PANEL, fg=FG, font=("Consolas", 12), wraplength=900, justify="left", anchor="w")
        self.graph_out.pack(fill="x")

    def _run_graph(self, kind: str) -> None:
        raw = self.graph_text.get("1.0", "end").strip()
        out = graphs.run(kind, raw, xmin=self.graph_xmin.get(), xmax=self.graph_xmax.get(), data=raw, circuit=raw, lang=self.lang, eng=self.engine.eng)
        self.graph_out.configure(text=out.get("text") or "0")
        self.last_latex = out.get("latex") or out.get("text") or ""
        svg = out.get("svg") or ""
        if svg:
            try:
                import tempfile
                from pathlib import Path
                p = Path(tempfile.gettempdir()) / "ultra_plot.svg"
                p.write_text(svg, encoding="utf-8")
                img = tk.PhotoImage(file=str(p))
                self.graph_svg.configure(image=img)
                self.graph_svg.image = img
            except Exception:
                self.graph_out.configure(text=(out.get("text") or "0") + "\n(SVG shown as text)\n" + svg[:400])

    def _build_matrix(self, root: tk.Frame) -> None:
        self.matrix_hint = tk.Label(root, bg=BG, fg=MUTED, wraplength=900, justify="left")
        self.matrix_hint.pack(fill="x")
        self.mat_a = tk.Text(root, bg="#11141a", fg=FG, insertbackground=FG, relief="flat", height=5, font=("Consolas", 13))
        self.mat_a.pack(fill="x", pady=4)
        self.mat_a.insert("1.0", "1, 2\n3, 4")
        self.mat_b = tk.Text(root, bg="#11141a", fg=FG, insertbackground=FG, relief="flat", height=4, font=("Consolas", 13))
        self.mat_b.pack(fill="x", pady=4)
        self.mat_b.insert("1.0", "5\n6")
        row = tk.Frame(root, bg=BG)
        row.pack(fill="x")
        for lab, op in (("det", "det"), ("invm", "inv"), ("trans", "t"), ("eig", "eig"), ("rref", "rref"), ("mul", "mul"), ("solve_axb", "solve")):
            b = tk.Button(row, command=lambda o=op: self._run_matrix(o))
            self._paint_btn(b, ACCENT if op == "det" else BTN2, "#1c1f24" if op == "det" else FG)
            b.configure(text=self.tr(lab))
            b.pack(side="left", padx=3)
        self.mat_out = tk.Text(root, bg=PANEL, fg=FG, relief="flat", height=12, font=("Consolas", 12))
        self.mat_out.pack(fill="both", expand=True, pady=8)

    def _run_matrix(self, op: str) -> None:
        out = matrixlab.run(op, self.mat_a.get("1.0", "end"), self.mat_b.get("1.0", "end"), eng=self.engine.eng, lang=self.lang)
        self.mat_out.delete("1.0", "end")
        self.mat_out.insert("1.0", (out.get("text") or "0") + "\n\n" + "\n".join(out.get("steps") or []))
        self.last_latex = out.get("latex") or out.get("text") or ""

    def _build_stats(self, root: tk.Frame) -> None:
        self.stats_hint = tk.Label(root, bg=BG, fg=MUTED, wraplength=900, justify="left")
        self.stats_hint.pack(fill="x")
        self.stats_text = tk.Text(root, bg="#11141a", fg=FG, insertbackground=FG, relief="flat", height=10, font=("Consolas", 13))
        self.stats_text.pack(fill="x", pady=4)
        self.stats_text.insert("1.0", "1\n2\n3\n4\n5")
        b = tk.Button(root, command=self._run_stats)
        self._paint_btn(b, ACCENT, "#1c1f24")
        b.configure(text=self.tr("run"))
        b.pack(anchor="w")
        self.stats_run_btn = b
        self.stats_out = tk.Text(root, bg=PANEL, fg=FG, relief="flat", height=12, font=("Consolas", 12))
        self.stats_out.pack(fill="both", expand=True, pady=8)

    def _run_stats(self) -> None:
        out = statsdata.run(self.stats_text.get("1.0", "end"), eng=self.engine.eng, lang=self.lang)
        self.stats_out.delete("1.0", "end")
        self.stats_out.insert("1.0", out.get("text") or "0")
        self.last_latex = out.get("latex") or out.get("text") or ""

    def _build_triangle(self, root: tk.Frame) -> None:
        self.tri_hint = tk.Label(root, bg=BG, fg=MUTED, wraplength=900, justify="left")
        self.tri_hint.pack(fill="x")
        row = tk.Frame(root, bg=BG)
        row.pack(fill="x", pady=8)
        self.tri_vars = {}
        for name in ("a", "b", "c", "A", "B", "C"):
            box = tk.Frame(row, bg=BG)
            box.pack(side="left", padx=6)
            tk.Label(box, text=name, bg=BG, fg=MUTED).pack()
            ent = tk.Entry(box, width=8, bg="#11141a", fg=FG, insertbackground=FG, relief="flat", justify="center")
            if name == "a":
                ent.insert(0, "3")
            elif name == "b":
                ent.insert(0, "4")
            elif name == "c":
                ent.insert(0, "5")
            ent.pack()
            ent.bind("<Return>", lambda e: self._run_triangle() or "break")
            self.tri_vars[name] = ent
        self.tri_a = self.tri_vars["a"]
        b = tk.Button(root, command=self._run_triangle)
        self._paint_btn(b, ACCENT, "#1c1f24")
        b.configure(text=self.tr("solve"))
        b.pack(anchor="w")
        self.tri_solve_btn = b
        self.tri_out = tk.Text(root, bg=PANEL, fg=FG, relief="flat", height=12, font=("Consolas", 12))
        self.tri_out.pack(fill="both", expand=True, pady=8)

    def _run_triangle(self) -> None:
        values = {k: e.get() for k, e in self.tri_vars.items()}
        out = triangle.run(values, lang=self.lang, eng=self.engine.eng)
        self.tri_out.delete("1.0", "end")
        self.tri_out.insert("1.0", (out.get("text") or "0") + "\n\n" + "\n".join(out.get("steps") or []))
        self.last_latex = out.get("latex") or out.get("text") or ""

    def _save_session(self) -> None:
        data = {
            "lang": self.lang,
            "circuit": self.cir_text.get("1.0", "end").strip() if hasattr(self, "cir_text") else "",
            "problem": self.prob_text.get("1.0", "end").strip() if hasattr(self, "prob_text") else "",
            "graph": self.graph_text.get("1.0", "end").strip() if hasattr(self, "graph_text") else "",
            "matrix": self.mat_a.get("1.0", "end").strip() if hasattr(self, "mat_a") else "",
            "stats": self.stats_text.get("1.0", "end").strip() if hasattr(self, "stats_text") else "",
        }
        out = sessionstore.save(data)
        if hasattr(self, "status"):
            self.status.configure(text=self.tr("session_saved") + " " + (out.get("text") or ""))

    def _load_session(self) -> None:
        data = sessionstore.load()
        if not data:
            return
        if data.get("circuit") and hasattr(self, "cir_text"):
            self.cir_text.delete("1.0", "end")
            self.cir_text.insert("1.0", data["circuit"])
        if data.get("problem") and hasattr(self, "prob_text"):
            self.prob_text.delete("1.0", "end")
            self.prob_text.insert("1.0", data["problem"])
        if data.get("graph") and hasattr(self, "graph_text"):
            self.graph_text.delete("1.0", "end")
            self.graph_text.insert("1.0", data["graph"])
        if data.get("matrix") and hasattr(self, "mat_a"):
            self.mat_a.delete("1.0", "end")
            self.mat_a.insert("1.0", data["matrix"])
        if data.get("stats") and hasattr(self, "stats_text"):
            self.stats_text.delete("1.0", "end")
            self.stats_text.insert("1.0", data["stats"])

    def _copy_latex(self) -> None:
        src = getattr(self, "last_latex", "") or (self._read_display() if hasattr(self, "display") else "0")
        tex = latexout.of_result(src, src)
        try:
            self.clipboard_clear()
            self.clipboard_append(tex)
        except Exception:
            pass
        if hasattr(self, "status"):
            self.status.configure(text=tex[:80])

    def _build_sources(self, root: tk.Frame) -> None:
        box = tk.Text(root, bg=PANEL, fg=FG, relief="flat", font=("Segoe UI", 11), wrap="word")
        box.pack(fill="both", expand=True)
        path = Path(__file__).with_name("sources.json")
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            data = {"sources": {}}
        lines = []
        for key, src in (data.get("sources") or {}).items():
            name = (src.get("name") or {}).get(self.lang) or (src.get("name") or {}).get("en") or key
            note = (src.get("note") or {}).get(self.lang) or (src.get("note") or {}).get("en") or ""
            lines.append(str(name))
            if src.get("url"):
                lines.append(src["url"])
            lines.append(str(note))
            lines.append("")
        box.insert("1.0", "\n".join(lines))
        box.configure(state="disabled")


def main() -> None:
    app = UltraDesktop()
    app.hist_title.configure(text=app.tr("history"))
    app.mainloop()
