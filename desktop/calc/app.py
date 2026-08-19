"""Desktop window. Independent of the web interface."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from .engine import DesktopEngine
from .i18n import t
from .sanitize import clean_number


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
        style.configure("Treeview", background=PANEL, fieldbackground=PANEL, foreground=FG, rowheight=24)
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
        for b in (self.btn_calc, self.btn_form, self.btn_poly, self.btn_num):
            self._paint_btn(b, ACCENT if False else BTN)
            b.pack(side="left", padx=4)
        self.lang_box = ttk.Combobox(top, values=["en", "fa", "fi"], width=6, state="readonly")
        self.lang_box.set("en")
        self.lang_box.bind("<<ComboboxSelected>>", self._on_lang)
        self.lang_box.pack(side="right")
        self.lang_lbl = ttk.Label(top, text="")
        self.lang_lbl.pack(side="right", padx=6)

        self.frames = {}
        for name in ("calc", "formulas", "poly", "numeric"):
            fr = tk.Frame(self, bg=BG)
            self.frames[name] = fr
        self._build_calc(self.frames["calc"])
        self._build_formulas(self.frames["formulas"])
        self._build_poly(self.frames["poly"])
        self._build_numeric(self.frames["numeric"])
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
        }
        for key, btn in mapping.items():
            self._paint_btn(btn, ACCENT if key == mode else BTN, "#1c1f24" if key == mode else FG)

    def _on_lang(self, _evt=None) -> None:
        self.lang = self.lang_box.get() or "en"
        self._refresh_texts()
        self._fill_categories()
        self._fill_formula_list()
        if self.formula_id:
            self._show_formula(self.formula_id)

    def _refresh_texts(self) -> None:
        self.title(self.tr("app_title"))
        self.btn_calc.configure(text=self.tr("mode_calc"))
        self.btn_form.configure(text=self.tr("mode_formulas"))
        self.btn_poly.configure(text=self.tr("mode_poly"))
        self.btn_num.configure(text=self.tr("mode_numeric"))
        self.lang_lbl.configure(text=self.tr("language"))
        self.angle_btn.configure(text=self.tr("deg") if self.engine.angle == "DEG" else self.tr("rad"))
        self.eng_btn.configure(text=self.tr("eng"))
        self.search_lbl.configure(text=self.tr("search"))
        self.cat_lbl.configure(text=self.tr("categories"))
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

    # ---------- calculator ----------
    def _build_calc(self, root: tk.Frame) -> None:
        left = tk.Frame(root, bg=BG)
        left.pack(side="left", fill="both", expand=True)
        right = tk.Frame(root, bg=PANEL, width=260)
        right.pack(side="right", fill="y", padx=(10, 0))
        right.pack_propagate(False)

        self.display = tk.Label(
            left,
            text="0",
            anchor="e",
            bg="#11141a",
            fg=FG,
            font=("Consolas", 28),
            padx=14,
            pady=16,
        )
        self.display.pack(fill="x", pady=(0, 8))
        self.status = tk.Label(left, text="", anchor="w", bg=BG, fg=MUTED, font=("Segoe UI", 9))
        self.status.pack(fill="x")

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
                btn.configure(font=("Consolas", 11), pady=10)
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

    def _toggle_angle(self) -> None:
        self.engine.angle = "RAD" if self.engine.angle == "DEG" else "DEG"
        self.angle_btn.configure(text=self.tr("deg") if self.engine.angle == "DEG" else self.tr("rad"))

    def _toggle_eng(self) -> None:
        self.engine.eng = not self.engine.eng
        self._paint_btn(self.eng_btn, GREEN if self.engine.eng else BTN2)

    def _set_display(self, text: str) -> None:
        self.display.configure(text=text if text else "0")

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
            return
        if label == "C":
            self.expr = self.expr[:-1]
            self._set_display(self.expr or "0")
            return
        if label == "<-":
            self.expr = self.expr[:-1]
            self._set_display(self.expr or "0")
            return
        if label == "+/-":
            if self.expr.startswith("-(") and self.expr.endswith(")"):
                self.expr = self.expr[2:-1]
            else:
                self.expr = f"-({self.expr or '0'})"
            self._set_display(self.expr)
            return
        if label == "MC":
            self.engine.memory = 0.0
            return
        if label == "MR":
            self.expr += format(self.engine.memory, "g")
            self._set_display(self.expr)
            return
        if label == "M+":
            out = self.engine.evaluate(self.expr or "0")
            try:
                self.engine.memory += float(out["value"].real if isinstance(out["value"], complex) else out["value"])
            except Exception:
                pass
            return
        if label == "M-":
            out = self.engine.evaluate(self.expr or "0")
            try:
                self.engine.memory -= float(out["value"].real if isinstance(out["value"], complex) else out["value"])
            except Exception:
                pass
            return
        if label == "ENG":
            self._toggle_eng()
            return
        if label == "%":
            out = self.engine.evaluate(f"({self.expr or '0'})/100")
            self.expr = out["text"]
            self._set_display(self.expr)
            return
        if label == "=":
            out = self.engine.evaluate(self.expr or "0")
            shown = out["text"]
            self.history.insert(0, f"{self.expr} = {shown}")
            self.expr = shown
            self._set_display(shown)
            self.status.configure(text=out.get("exact") or self.tr("ready"))
            return
        self.expr += mapping.get(label, label)
        self._set_display(self.expr)

    def _hist_use(self, _evt=None) -> None:
        sel = self.history.curselection()
        if not sel:
            return
        line = self.history.get(sel[0])
        if "=" in line:
            self.expr = line.split("=", 1)[0].strip()
            self._set_display(self.expr)

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
        self.cat_list = tk.Listbox(left, bg=PANEL, fg=FG, highlightthickness=0, bd=0, font=("Segoe UI", 10), width=32)
        self.cat_list.pack(fill="both", expand=True, pady=6)
        self.cat_list.bind("<<ListboxSelect>>", lambda e: self._fill_formula_list())

        self.search_lbl = tk.Label(mid, bg=BG, fg=ACCENT, font=("Segoe UI", 11, "bold"))
        self.search_lbl.pack(anchor="w")
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self._fill_formula_list())
        tk.Entry(mid, textvariable=self.search_var, bg="#11141a", fg=FG, insertbackground=FG, relief="flat").pack(fill="x", pady=6)
        self.formula_list = tk.Listbox(mid, bg=PANEL, fg=FG, highlightthickness=0, bd=0, font=("Segoe UI", 10))
        self.formula_list.pack(fill="both", expand=True)
        self.formula_list.bind("<<ListboxSelect>>", self._on_formula_pick)

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
        self.formula_result.pack(anchor="w", padx=12, pady=(0, 12))

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
        self.cat_list.delete(0, "end")
        self.cat_keys = ["all"]
        self.cat_list.insert("end", "—")
        keys = sorted(self.engine.categories.keys())
        for key in keys:
            names = self.engine.categories[key]
            label = names.get(self.lang) or names.get("en") or key
            self.cat_keys.append(key)
            self.cat_list.insert("end", f"{key.split('.', 1)[0]} / {label}")

    def _selected_category(self) -> str | None:
        sel = self.cat_list.curselection()
        if not sel:
            return None
        key = self.cat_keys[sel[0]]
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

    def _on_formula_pick(self, _evt=None) -> None:
        sel = self.formula_list.curselection()
        if not sel:
            return
        item = self.formula_items[sel[0]]
        self._show_formula(item["id"])

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
            self.eq_entries.append(ent)
        tk.Label(self.var_box, text=self.tr("unknown"), bg=PANEL, fg=MUTED).pack(anchor="w", pady=(8, 2))
        self.unk_entry = tk.Entry(self.var_box, bg="#11141a", fg=FG, insertbackground=FG, relief="flat")
        self.unk_entry.insert(0, ", ".join(self.system_unknowns))
        self.unk_entry.pack(fill="x")

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
            out = self.engine.solve_system(eqs, unknowns)
            if out["solutions"]:
                lines = []
                for i, sol in enumerate(out["solutions"], 1):
                    parts = [f"{k} = {v}" for k, v in sol.items()]
                    lines.append(f"{i})  " + "   ".join(parts))
                self.formula_result.configure(text="\n".join(lines))
            else:
                self.formula_result.configure(text="0")
            return
        if not self.formula_id:
            self.formula_result.configure(text=self.tr("pick_formula"))
            return
        values = {name: ent.get() for name, ent in self.var_widgets.items()}
        unknown = self.unknown_var.get() or None
        out = self.engine.solve_formula(self.formula_id, values, unknown)
        extra = ""
        if out.get("all") and len(out["all"]) > 1:
            extra = "  |  " + ", ".join(out["all"][1:])
        unit = out.get("unit") or ""
        self.formula_result.configure(
            text=f"{self.tr('solved_for')} {out.get('unknown')} = {out.get('text')} {unit}{extra}"
        )

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
        self.poly_out.insert("1.0", text)

    def _poly_roots(self) -> None:
        out = self.engine.polynomial(self._poly_coeffs(), None)
        lines = [self.tr("roots") + ":"] + [f"  {r}" for r in out["roots"]] or ["  0"]
        self.poly_out.delete("1.0", "end")
        self.poly_out.insert("1.0", "\n".join(lines))

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
        for b in (self.n_root_btn, self.n_int_btn, self.n_diff_btn, self.n_ode_btn):
            self._paint_btn(b, BTN2)
            b.pack(side="left", padx=4)
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
        self.n_out.insert("1.0", f"root = {out['text']}")

    def _do_int(self) -> None:
        a = clean_number(self.n_a.get(), 0.0) or 0.0
        b = clean_number(self.n_b.get(), 1.0) or 1.0
        out = self.engine.numeric_integral(self.n_func.get(), a, b)
        extra = f"\nexact: {out['exact']}" if out.get("exact") else ""
        self.n_out.delete("1.0", "end")
        self.n_out.insert("1.0", f"integral = {out['text']}{extra}")

    def _do_diff(self) -> None:
        x0 = clean_number(self.n_a.get(), 0.0) or 0.0
        out = self.engine.numeric_derivative(self.n_func.get(), x0)
        extra = f"\n{out.get('exact','')}"
        self.n_out.delete("1.0", "end")
        self.n_out.insert("1.0", f"d/dx = {out['text']}{extra}")

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
        self.n_out.insert("1.0", "\n".join(lines))


def main() -> None:
    app = UltraDesktop()
    app.hist_title.configure(text=app.tr("history"))
    app.mainloop()
