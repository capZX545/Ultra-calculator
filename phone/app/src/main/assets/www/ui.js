(function () {
  const state = {
    lang: "en",
    mode: "calc",
    angle: "DEG",
    eng: false,
    expr: "",
    ans: 0,
    strings: {},
    formulas: [],
    algos: [],
    currentAlgo: null,
    current: null,
    lookupPick: null,
    lastField: null,
    cat: "",
    total: 0,
    system: false,
    eqCount: 2,
    unknownCount: 2,
  };

  const KEYS = [
    ["MC","MR","M+","M-","(",")"],
    ["sin","cos","tan","ln","log","log2"],
    ["asin","acos","atan","exp","10^x","x^2"],
    ["sinh","cosh","tanh","sqrt","x^y","n!"],
    ["pi","e","7","8","9","/"],
    ["ans","%","4","5","6","*"],
    ["1/x","abs","1","2","3","-"],
    ["EE","+/-","0",".","=","+"],
  ];
  const MAP = {
    sin:"sin(", cos:"cos(", tan:"tan(",
    asin:"asin(", acos:"acos(", atan:"atan(",
    sinh:"sinh(", cosh:"cosh(", tanh:"tanh(",
    ln:"ln(", log:"log10(", log2:"log2(",
    exp:"exp(", "10^x":"10**(", "x^2":"**2", "x^y":"**",
    sqrt:"sqrt(", "n!":"factorial(", abs:"abs(",
    "1/x":"1/(", pi:"pi", e:"e", ans:"ans", EE:"*10**",
  };
  const MODES = ["calc", "formulas", "poly", "numeric", "algo", "chem", "elements", "sources", "problems"];

  const $ = (id) => document.getElementById(id);
  const screen = $("screen");
  const history = $("history");
  let memory = 0;

  function setScreen(text) {
    screen.value = text || "0";
    state.expr = text && text !== "0" ? text : (text || "");
  }

  function readExpr() {
    const text = (screen.value || "").trim();
    state.expr = text;
    return text || "0";
  }

  function insertScreen(s) {
    const el = screen;
    el.focus();
    let start = el.selectionStart == null ? el.value.length : el.selectionStart;
    let end = el.selectionEnd == null ? start : el.selectionEnd;
    let val = el.value;
    const whole = start === 0 && end === val.length;
    if (whole && s && "+-*/%".indexOf(s[0]) >= 0 && val && val !== "0") {
      start = val.length;
      end = val.length;
    } else if (val === "0" && s && /[0-9.]/.test(s[0])) {
      val = "";
      start = 0;
      end = 0;
    }
    el.value = val.slice(0, start) + s + val.slice(end);
    const pos = start + s.length;
    try { el.setSelectionRange(pos, pos); } catch (err) {}
    state.expr = el.value === "0" ? "" : el.value;
  }

  function jsEval(body) {
    const angle = (body && body.angle) || "DEG";
    const eng = !!(body && body.eng);
    let expr = String((body && body.expr) || "0");
    expr = expr.replace(/[۰۱۲۳۴۵۶۷۸۹]/g, (d) => "۰۱۲۳۴۵۶۷۸۹".indexOf(d));
    expr = expr.replace(/[٠١٢٣٤٥٦٧٨٩]/g, (d) => "٠١٢٣٤٥٦٧٨٩".indexOf(d));
    expr = expr.replace(/π/g, "pi").replace(/×/g, "*").replace(/÷/g, "/").replace(/−/g, "-").replace(/\^/g, "**");
    const stripped = expr.replace(/\*\*/g, "^").replace(/\s+/g, "");
    if (!/^[0-9A-Za-z_+\-*/%().,^]+$/.test(stripped)) {
      return { ok: true, text: "0", value: 0 };
    }
    const toR = (x) => (angle === "DEG" ? Number(x) * Math.PI / 180 : Number(x));
    const fromR = (x) => (angle === "DEG" ? Number(x) * 180 / Math.PI : Number(x));
    const fact = (n) => {
      n = Math.floor(Number(n));
      if (n < 0 || n > 170) return NaN;
      let a = 1;
      for (let i = 2; i <= n; i += 1) a *= i;
      return a;
    };
    const ns = {
      sin: (x) => Math.sin(toR(x)),
      cos: (x) => Math.cos(toR(x)),
      tan: (x) => Math.tan(toR(x)),
      asin: (x) => fromR(Math.asin(Number(x))),
      acos: (x) => fromR(Math.acos(Number(x))),
      atan: (x) => fromR(Math.atan(Number(x))),
      sinh: Math.sinh,
      cosh: Math.cosh,
      tanh: Math.tanh,
      ln: Math.log,
      log: Math.log,
      log10: Math.log10,
      log2: Math.log2,
      exp: Math.exp,
      sqrt: Math.sqrt,
      abs: Math.abs,
      factorial: fact,
      pi: Math.PI,
      e: Math.E,
      ans: Number(state.ans) || 0,
    };
    try {
      const fn = new Function(
        "sin", "cos", "tan", "asin", "acos", "atan", "sinh", "cosh", "tanh",
        "ln", "log", "log10", "log2", "exp", "sqrt", "abs", "factorial", "pi", "e", "ans",
        "return (" + expr + ");"
      );
      let v = fn(
        ns.sin, ns.cos, ns.tan, ns.asin, ns.acos, ns.atan, ns.sinh, ns.cosh, ns.tanh,
        ns.ln, ns.log, ns.log10, ns.log2, ns.exp, ns.sqrt, ns.abs, ns.factorial, ns.pi, ns.e, ns.ans
      );
      if (typeof v === "number" && !Number.isFinite(v)) v = 0;
      let text;
      if (typeof v !== "number") text = String(v);
      else if (Math.abs(v) < 1e-15) text = "0";
      else if (eng && v !== 0) {
        const exp = Math.floor(Math.log10(Math.abs(v)) / 3) * 3;
        text = (v / Math.pow(10, exp)).toPrecision(8).replace(/\.?0+$/, "") + "e" + (exp >= 0 ? "+" : "") + exp;
      } else text = String(parseFloat(v.toPrecision(12)));
      return { ok: true, text: text, value: v, steps: [] };
    } catch (err) {
      return { ok: true, text: "0", value: 0, steps: [] };
    }
  }

  async function pyCall(path, query, body) {
    if (window.pyodideReady && window.pyodide) {
      try {
        const req = JSON.stringify({ path: path, query: query || {}, body: body || {} });
        window.pyodide.globals.set("_req", req);
        const out = window.pyodide.runPython("import bridge; bridge.handle(_req)");
        return JSON.parse(out);
      } catch (err) {
        if (path === "/api/eval") return jsEval(body || {});
        return { ok: true, text: "0" };
      }
    }
    if (path === "/api/eval") return jsEval(body || {});
    if (path === "/api/meta") {
      return { strings: state.strings || {}, categories: [], total: 0, languages: ["en", "fa", "fi"] };
    }
    return { ok: true, text: "0", solutions: [] };
  }

  async function post(url, body) {
    const u = new URL(url, "https://local.invalid/");
    const query = {};
    u.searchParams.forEach((v, k) => { query[k] = v; });
    return pyCall(u.pathname, query, body || {});
  }

  async function get(url) {
    const u = new URL(url, "https://local.invalid/");
    const query = {};
    u.searchParams.forEach((v, k) => { query[k] = v; });
    return pyCall(u.pathname, query, {});
  }

  function applyStrings() {
    const s = state.strings;
    $("title").textContent = s.title || "Ultra Calculator";
    document.title = s.title || "Ultra Calculator";
    $("tab-calc").textContent = s.calc || "Calculator";
    $("tab-formulas").textContent = s.formulas || "Formulas";
    $("tab-poly").textContent = s.poly || "Polynomial";
    $("tab-numeric").textContent = s.numeric || "Numerical";
    if ($("tab-algo")) $("tab-algo").textContent = s.algo || "Algorithms";
    if ($("btn-arun")) $("btn-arun").textContent = s.run || "Run";
    if ($("algo-search-title")) $("algo-search-title").textContent = s.search || "Search";
    if ($("ahint")) $("ahint").textContent = s.algo_hint || "";
    if ($("tab-chem")) $("tab-chem").textContent = s.chem || "Chemistry";
    if ($("tab-elements")) $("tab-elements").textContent = s.elements || "Elements";
    if ($("tab-sources")) $("tab-sources").textContent = s.sources || "Sources";
    if ($("tab-problems")) $("tab-problems").textContent = s.problems || "Problems";
    if ($("prob-solve")) $("prob-solve").textContent = s.solve || "Solve";
    if ($("prob-inv")) $("prob-inv").textContent = s.inverse || "Inverse";
    if ($("prob-hint")) $("prob-hint").textContent = s.problem_hint || "";
    if ($("prob-unk-label")) {
      const inp = $("prob-unk");
      $("prob-unk-label").textContent = (s.unknown || "Unknown") + " ";
      if (inp) $("prob-unk-label").appendChild(inp);
    }
    if ($("prob-at-label")) {
      const inp = $("prob-at");
      $("prob-at-label").textContent = (s.at_value || "at") + " ";
      if (inp) $("prob-at-label").appendChild(inp);
    }
    if ($("chem-bal")) $("chem-bal").textContent = s.balance || "Balance";
    if ($("chem-mw")) $("chem-mw").textContent = s.molar || "Molar mass";
    if ($("lookup-label")) $("lookup-label").textContent = s.lookup || "Lookup";
    if ($("lookup-insert")) $("lookup-insert").textContent = s.insert || "Insert";
    if ($("lookup-q") && s.lookup_hint) $("lookup-q").placeholder = s.lookup_hint;
    if ($("kbd-hint")) $("kbd-hint").textContent = s.kbd_hint || "";
    $("lang-label").textContent = s.lang || "Language";
    $("hist-title").textContent = s.history || "History";
    $("cat-title").textContent = (s.categories || "Categories") + (state.total ? "  (" + state.total + ")" : "");
    $("search-title").textContent = s.search || "Search";
    $("btn-single").textContent = s.single || "One unknown";
    $("btn-system").textContent = s.system || "System";
    $("btn-add").textContent = s.add || "Add";
    $("btn-del").textContent = s.remove || "Remove";
    $("btn-solve").textContent = s.solve || "Solve";
    $("poly-eval").textContent = s.evaluate || "Evaluate";
    $("poly-roots").textContent = s.roots || "Roots";
    $("n-root").textContent = s.root || "Root";
    $("n-int").textContent = s.integral || "Integral";
    $("n-der").textContent = s.deriv || "Derivative";
    $("n-ode").textContent = s.ode || "ODE";
    $("btn-deg").textContent = state.angle === "DEG" ? (s.deg || "DEG") : (s.rad || "RAD");
    $("btn-eng").classList.toggle("on", state.eng);
    document.body.classList.toggle("rtl", state.lang === "fa");
  }

  function focusMode(mode) {
    if (mode === "calc") {
      screen.focus();
      if (screen.value === "0") screen.select();
    } else if (mode === "formulas" && $("search")) {
      $("search").focus();
    } else if (mode === "poly" && $("c6")) {
      $("c6").focus();
    } else if (mode === "numeric" && $("n-func")) {
      $("n-func").focus();
    } else if (mode === "algo" && $("algo-search")) {
      $("algo-search").focus();
    } else if (mode === "chem" && $("chem-eq")) {
      $("chem-eq").focus();
    } else if (mode === "elements" && $("el-q")) {
      $("el-q").focus();
    } else if (mode === "problems" && $("prob-text")) {
      $("prob-text").focus();
    }
  }

  function showMode(mode) {
    state.mode = mode;
    document.querySelectorAll(".view").forEach((el) => el.classList.remove("show"));
    document.getElementById("view-" + mode).classList.add("show");
    document.querySelectorAll(".tab").forEach((el) => {
      el.classList.toggle("on", el.getAttribute("data-mode") === mode);
    });
    focusMode(mode);
  }

  function buildKeys() {
    const box = $("keys");
    box.innerHTML = "";
    KEYS.forEach((row) => {
      row.forEach((label) => {
        const b = document.createElement("button");
        b.type = "button";
        b.className = "key" + (label === "=" ? " accent" : "");
        b.tabIndex = -1;
        b.textContent = label;
        b.addEventListener("click", () => onKey(label));
        box.appendChild(b);
      });
    });
  }

  async function onKey(label) {
    if (label === "AC") {
      state.expr = "";
      setScreen("0");
      screen.focus();
      screen.select();
      return;
    }
    if (label === "C") {
      const el = screen;
      el.focus();
      const start = el.selectionStart == null ? el.value.length : el.selectionStart;
      const end = el.selectionEnd == null ? start : el.selectionEnd;
      if (end > start) {
        el.value = el.value.slice(0, start) + el.value.slice(end);
        try { el.setSelectionRange(start, start); } catch (err) {}
      } else if (start > 0) {
        el.value = el.value.slice(0, start - 1) + el.value.slice(start);
        try { el.setSelectionRange(start - 1, start - 1); } catch (err) {}
      }
      state.expr = el.value;
      if (!el.value) setScreen("0");
      return;
    }
    if (label === "+/-") {
      const current = readExpr();
      state.expr = current.startsWith("-(") && current.endsWith(")")
        ? current.slice(2, -1)
        : "-(" + (current || "0") + ")";
      setScreen(state.expr);
      screen.focus();
      return;
    }
    if (label === "MC") { memory = 0; return; }
    if (label === "MR") {
      insertScreen(String(memory));
      return;
    }
    if (label === "M+" || label === "M-") {
      const out = await post("/api/eval", payloadExpr());
      const n = Number(out.text);
      if (!Number.isNaN(n)) memory += label === "M+" ? n : -n;
      return;
    }
    if (label === "%") {
      const out = await post("/api/eval", Object.assign(payloadExpr(), { expr: "(" + (readExpr() || "0") + ")/100" }));
      state.expr = out.text;
      setScreen(state.expr);
      screen.focus();
      return;
    }
    if (label === "=") {
      const source = readExpr();
      const out = await post("/api/eval", payloadExpr());
      const line = document.createElement("li");
      line.textContent = source + " = " + out.text;
      line.tabIndex = 0;
      line.addEventListener("click", () => reuseHistory(source));
      line.addEventListener("keydown", (ev) => {
        if (ev.key === "Enter") reuseHistory(source);
      });
      history.insertBefore(line, history.firstChild);
      state.expr = out.text;
      state.ans = out.value;
      setScreen(out.text);
      showSteps("calc-steps", out.steps || []);
      screen.focus();
      screen.select();
      return;
    }
    insertScreen(MAP[label] !== undefined ? MAP[label] : label);
  }

  function reuseHistory(expr) {
    state.expr = expr || "0";
    setScreen(state.expr);
    screen.focus();
    screen.selectionStart = screen.selectionEnd = screen.value.length;
  }

  function payloadExpr() {
    return { expr: readExpr() || "0", angle: state.angle, eng: state.eng, ans: state.ans, lang: state.lang };
  }

  function showSteps(id, lines) {
    const el = $(id);
    if (!el) return;
    const rows = lines || [];
    el.textContent = rows.map((s, i) => (i + 1) + ") " + s).join("\n");
  }

  async function loadMeta() {
    const data = await get("/api/meta?lang=" + encodeURIComponent(state.lang));
    state.strings = data.strings || {};
    applyStrings();
    state.total = data.total || 0;
    if ($("cat-title")) {
      $("cat-title").textContent = (state.strings.categories || "Categories") + "  (" + state.total + ")";
    }
    renderCatList(data);
    await loadFormulas();
    if ($("el-q")) loadElements();
  }

  function renderCatList(data) {
    const box = $("cat-list");
    if (!box) return;
    const keep = state.cat || "";
    box.innerHTML = "";
    const rows = [{ id: "", label: state.strings.all || "All", count: data.total || 0 }].concat(data.categories || []);
    rows.forEach((c) => {
      const li = document.createElement("li");
      const id = c.id || "";
      li.dataset.id = id;
      const name = document.createElement("span");
      name.className = "cname";
      name.textContent = c.label || id;
      const n = document.createElement("span");
      n.className = "n";
      n.textContent = String(c.count || 0);
      li.appendChild(name);
      li.appendChild(n);
      if (id === keep) li.classList.add("on");
      li.addEventListener("click", () => {
        state.cat = id;
        box.querySelectorAll("li").forEach((x) => x.classList.remove("on"));
        li.classList.add("on");
        loadFormulas();
      });
      box.appendChild(li);
    });
    if (!box.querySelector("li.on")) {
      const first = box.querySelector("li");
      if (first) first.classList.add("on");
    }
  }

  async function loadFormulas() {
    const q = $("search").value || "";
    const cat = state.cat || "";
    const url = "/api/formulas?lang=" + encodeURIComponent(state.lang) + "&q=" + encodeURIComponent(q) + "&category=" + encodeURIComponent(cat);
    state.formulas = await get(url);
    const box = $("flist");
    box.innerHTML = "";
    if ($("search-title")) {
      $("search-title").textContent = (state.strings.search || "Search") + "  (" + state.formulas.length + ")";
    }
    state.formulas.forEach((item, i) => {
      const li = document.createElement("li");
      li.textContent = item.name;
      li.tabIndex = 0;
      li.addEventListener("click", () => selectFormula(i, li, false));
      li.addEventListener("keydown", (ev) => {
        if (ev.key === "Enter") {
          ev.preventDefault();
          selectFormula(i, li, true);
        }
      });
      box.appendChild(li);
    });
  }

  function selectFormula(index, li, jump) {
    document.querySelectorAll("#flist li").forEach((n) => n.classList.remove("on"));
    if (li) li.classList.add("on");
    state.current = state.formulas[index];
    $("fname").textContent = state.current.name;
    $("fexpr").textContent = state.current.expr;
    renderFields();
    if (jump) focusFirstVar();
  }

  function focusFirstVar() {
    const inp = document.querySelector("#fields input[data-var], #fields input.eq");
    if (inp) inp.focus();
  }

  function renderFields() {
    const box = $("fields");
    box.innerHTML = "";
    if (state.system) {
      for (let i = 0; i < state.eqCount; i += 1) {
        const input = document.createElement("input");
        input.className = "eq";
        input.value = i === 0 && state.current ? state.current.expr : (i === 1 ? "x - y = 0" : "0 = 0");
        box.appendChild(input);
      }
      const unk = document.createElement("input");
      unk.id = "unks";
      const names = [];
      for (let i = 0; i < state.unknownCount; i += 1) names.push(String.fromCharCode(120 + (i % 3)) + (i >= 3 ? String(i) : ""));
      unk.value = names.join(", ");
      box.appendChild(unk);
      return;
    }
    if (!state.current) {
      $("fname").textContent = state.strings.pick || "";
      return;
    }
    const vars = state.current.variables || {};
    const keys = Object.keys(vars);
    keys.forEach((name, idx) => {
      const meta = vars[name];
      const row = document.createElement("div");
      row.className = "field";
      const radio = document.createElement("input");
      radio.type = "radio";
      radio.name = "unk";
      radio.value = name;
      if (idx === 0) radio.checked = true;
      const lab = document.createElement("span");
      const nm = (meta.name && (meta.name[state.lang] || meta.name.en)) || name;
      lab.textContent = name + "  " + nm + "  [" + (meta.unit || "") + "]";
      const input = document.createElement("input");
      input.dataset.var = name;
      row.appendChild(radio);
      row.appendChild(lab);
      row.appendChild(input);
      box.appendChild(row);
    });
  }

  async function solveNow() {
    if (state.system) {
      const eqs = Array.from(document.querySelectorAll("#fields .eq")).map((el) => el.value);
      const unks = ($("unks") ? $("unks").value : "x").split(/[,\s;]+/).filter(Boolean);
      const out = await post("/api/system", { equations: eqs, unknowns: unks, eng: state.eng, lang: state.lang });
      if (out.solutions && out.solutions.length) {
        $("fresult").textContent = out.solutions.map((sol, i) => {
          return (i + 1) + ") " + Object.keys(sol).map((k) => k + " = " + sol[k]).join("   ");
        }).join("\n");
      } else {
        $("fresult").textContent = "0";
      }
      showSteps("fsteps", out.steps || []);
      return;
    }
    if (!state.current) {
      $("fresult").textContent = state.strings.pick || "";
      return;
    }
    const values = {};
    document.querySelectorAll("#fields input[data-var]").forEach((el) => {
      values[el.dataset.var] = el.value;
    });
    const picked = document.querySelector("#fields input[name=unk]:checked");
    const out = await post("/api/solve", {
      id: state.current.id,
      values: values,
      unknown: picked ? picked.value : null,
      eng: state.eng,
      lang: state.lang,
    });
    const extra = out.all && out.all.length > 1 ? " | " + out.all.slice(1).join(", ") : "";
    $("fresult").textContent = (out.unknown || "") + " = " + out.text + " " + (out.unit || "") + extra;
    showSteps("fsteps", out.steps || []);
  }

  function buildPoly() {
    const box = $("coeffs");
    box.innerHTML = "";
    ["a6","a5","a4","a3","a2","a1","a0"].forEach((name, i) => {
      const lab = document.createElement("label");
      lab.textContent = name;
      const input = document.createElement("input");
      input.id = "c" + i;
      input.value = i === 5 ? "1" : "0";
      lab.appendChild(input);
      box.appendChild(lab);
    });
  }

  function polyCoeffs() {
    const out = [];
    for (let i = 0; i < 7; i += 1) out.push(Number(document.getElementById("c" + i).value || 0));
    return out;
  }

  async function doPoly(kind) {
    const out = await post("/api/poly", {
      coeffs: polyCoeffs(),
      x: kind === "eval" ? $("poly-x").value : null,
      eng: state.eng,
      lang: state.lang,
    });
    const teach = (out.steps || []).map((s, i) => (i + 1) + ") " + s).join("\n");
    if (kind === "roots") {
      $("poly-out").textContent = ((out.roots || []).join("\n") || "0") + (teach ? "\n\n" + teach : "");
      return;
    }
    $("poly-out").textContent =
      "p(x) = " + out.value_text + "\n" +
      "degree = " + out.degree + "\n" +
      "derivative coeffs: " + (out.derivative || []).join(", ") + "\n" +
      "integral coeffs: " + (out.integral || []).join(", ") +
      (teach ? "\n\n" + teach : "");
  }

  async function doNumeric(kind) {
    const out = await post("/api/numeric", {
      kind: kind,
      func: $("n-func").value,
      a: $("n-a").value,
      b: $("n-b").value,
      y0: $("n-y0").value,
      steps: $("n-steps").value,
      eng: state.eng,
      lang: state.lang,
    });
    let text = out.text || "0";
    if (out.exact) text += "\n" + out.exact;
    if (out.path) {
      text += "\n";
      out.path.slice(-20).forEach((p) => { text += "\n" + p[0] + "   " + p[1]; });
    }
    if (out.steps && out.steps.length) {
      text += "\n\n" + out.steps.map((s, i) => (i + 1) + ") " + s).join("\n");
    }
    $("n-out").textContent = text;
  }

  function isTypingField(el) {
    return !!(el && el.matches && el.matches("input, textarea, select"));
  }

  function focusLookup() {
    if ($("lookup-q")) {
      $("lookup-q").focus();
      $("lookup-q").select();
    }
  }

  document.querySelectorAll(".tab").forEach((btn) => {
    btn.addEventListener("click", () => showMode(btn.getAttribute("data-mode")));
  });
  $("lang").addEventListener("change", () => {
    state.lang = $("lang").value;
    loadMeta();
  });
  $("btn-deg").addEventListener("click", () => {
    state.angle = state.angle === "DEG" ? "RAD" : "DEG";
    applyStrings();
  });
  $("btn-eng").addEventListener("click", () => {
    state.eng = !state.eng;
    applyStrings();
  });
  if ($("search")) $("search").addEventListener("input", loadFormulas);
  $("search").addEventListener("keydown", (ev) => {
    if (ev.key === "Enter") {
      ev.preventDefault();
      const first = $("flist").querySelector("li");
      if (first) selectFormula(0, first, true);
    }
  });
  $("btn-single").addEventListener("click", () => {
    state.system = false;
    $("btn-single").classList.add("on");
    $("btn-system").classList.remove("on");
    renderFields();
  });
  $("btn-system").addEventListener("click", () => {
    state.system = true;
    $("btn-system").classList.add("on");
    $("btn-single").classList.remove("on");
    renderFields();
  });
  $("btn-add").addEventListener("click", () => {
    state.system = true;
    state.eqCount += 1;
    state.unknownCount += 1;
    $("btn-system").classList.add("on");
    $("btn-single").classList.remove("on");
    renderFields();
  });
  $("btn-del").addEventListener("click", () => {
    if (state.eqCount > 1) state.eqCount -= 1;
    if (state.unknownCount > 1) state.unknownCount -= 1;
    renderFields();
  });
  $("btn-solve").addEventListener("click", solveNow);
  $("poly-eval").addEventListener("click", () => doPoly("eval"));
  $("poly-roots").addEventListener("click", () => doPoly("roots"));
  $("n-root").addEventListener("click", () => doNumeric("root"));
  $("n-int").addEventListener("click", () => doNumeric("integral"));
  $("n-der").addEventListener("click", () => doNumeric("deriv"));
  $("n-ode").addEventListener("click", () => doNumeric("ode"));

  if ($("algo-search")) $("algo-search").addEventListener("input", loadAlgos);
  if ($("algo-cat")) $("algo-cat").addEventListener("change", () => {
    if ($("algo-cat")) $("algo-cat").dataset.ready = "1";
    loadAlgos();
  });
  if ($("algo-search")) {
    $("algo-search").addEventListener("keydown", (ev) => {
      if (ev.key === "Enter") {
        ev.preventDefault();
        const first = $("alist") && $("alist").querySelector("li");
        if (first) first.click();
      }
    });
  }
  if ($("btn-arun")) $("btn-arun").addEventListener("click", runAlgoNow);
  if ($("afields")) {
    $("afields").addEventListener("keydown", (ev) => {
      if (ev.key === "Enter" && ev.target && ev.target.matches("input")) {
        ev.preventDefault();
        runAlgoNow();
      }
    });
  }

  if ($("chem-bal")) {
    $("chem-bal").addEventListener("click", async () => {
      const out = await post("/api/balance", { eq: $("chem-eq").value, lang: state.lang });
      let t = out.text || "";
      if (out.steps && out.steps.length) t += "\n\n" + out.steps.map((s, i) => (i + 1) + ") " + s).join("\n");
      $("chem-out").textContent = t;
    });
  }
  if ($("chem-mw")) {
    $("chem-mw").addEventListener("click", async () => {
      const raw = $("chem-eq").value.split("=")[0].split("+")[0].trim();
      const out = await post("/api/molar", { formula: raw, lang: state.lang });
      let t = (out.text || "0") + " g/mol\n";
      const d = out.detail || {};
      Object.keys(d).forEach((k) => {
        if (d[k] && d[k].count) t += k + ": " + d[k].count + " x " + d[k].mass + " = " + d[k].contrib + "\n";
      });
      if (out.steps && out.steps.length) t += "\n" + out.steps.map((s, i) => (i + 1) + ") " + s).join("\n");
      $("chem-out").textContent = t;
    });
  }
  if ($("chem-eq")) {
    $("chem-eq").addEventListener("keydown", (ev) => {
      if (ev.key === "Enter") {
        ev.preventDefault();
        $("chem-bal").click();
      }
    });
  }

  async function loadAlgos() {
    if (!$("alist")) return;
    const q = ($("algo-search") && $("algo-search").value) || "";
    const cat = ($("algo-cat") && $("algo-cat").value) || "";
    const data = await get("/api/algos?lang=" + encodeURIComponent(state.lang) + "&q=" + encodeURIComponent(q) + "&category=" + encodeURIComponent(cat));
    const sel = $("algo-cat");
    if (sel && !sel.dataset.ready) {
      sel.innerHTML = "";
      const all = document.createElement("option");
      all.value = "";
      all.textContent = (state.strings.all || "All") + "  (" + ((data && data.total) || 0) + ")";
      sel.appendChild(all);
      ((data && data.categories) || []).forEach((c) => {
        const opt = document.createElement("option");
        opt.value = c.id;
        opt.textContent = (c.label || c.id) + "  (" + (c.count || 0) + ")";
        sel.appendChild(opt);
      });
      sel.dataset.ready = "1";
    }
    state.algos = (data && data.items) || [];
    const box = $("alist");
    box.innerHTML = "";
    state.algos.forEach((item, i) => {
      const li = document.createElement("li");
      li.textContent = item.name;
      li.tabIndex = 0;
      li.addEventListener("click", () => selectAlgo(i, li));
      li.addEventListener("keydown", (ev) => {
        if (ev.key === "Enter") {
          ev.preventDefault();
          selectAlgo(i, li);
        }
      });
      box.appendChild(li);
    });
  }

  function selectAlgo(index, li) {
    document.querySelectorAll("#alist li").forEach((n) => n.classList.remove("on"));
    if (li) li.classList.add("on");
    state.currentAlgo = state.algos[index];
    $("aname").textContent = state.currentAlgo.name;
    const box = $("afields");
    box.innerHTML = "";
    const params = state.currentAlgo.params || {};
    Object.keys(params).forEach((name) => {
      const meta = params[name];
      const row = document.createElement("div");
      row.className = "field";
      const lab = document.createElement("span");
      const nm = (meta.name && (meta.name[state.lang] || meta.name.en)) || name;
      lab.textContent = name + "  " + nm;
      const input = document.createElement("input");
      input.dataset.param = name;
      input.value = meta.default || "";
      row.appendChild(lab);
      row.appendChild(input);
      box.appendChild(row);
    });
    const first = box.querySelector("input");
    if (first) first.focus();
    $("aresult").textContent = "";
  }

  async function runAlgoNow() {
    if (!state.currentAlgo) {
      $("aresult").textContent = (state.strings.pick_algo || "Pick an algorithm.");
      return;
    }
    const values = {};
    document.querySelectorAll("#afields input[data-param]").forEach((el) => {
      values[el.dataset.param] = el.value;
    });
    const out = await post("/api/algo", { id: state.currentAlgo.id, values: values, eng: state.eng });
    $("aresult").textContent = (out.text || "0") + (out.detail ? "\n" + out.detail : "");
  }

  async function loadElements() {
    if (!$("el-list")) return;
    const rows = await get("/api/elements?lang=" + encodeURIComponent(state.lang) + "&q=" + encodeURIComponent(($("el-q") && $("el-q").value) || ""));
    const box = $("el-list");
    box.innerHTML = "";
    (rows || []).forEach((el) => {
      const li = document.createElement("li");
      li.textContent = el.Z + "  " + el.symbol + "  " + el.name;
      li.tabIndex = 0;
      const open = () => {
        document.querySelectorAll("#el-list li").forEach((n) => n.classList.remove("on"));
        li.classList.add("on");
        let t = el.symbol + "  " + el.name + "\nZ = " + el.Z + "\nmass = " + el.mass + "\ngroup = " + el.group + "\n\n";
        t += (state.strings.isotopes || "Isotopes") + ":\n";
        (el.isotopes || []).forEach((iso) => {
          const ab = iso.abundance != null ? iso.abundance + " %" : (iso.note || "");
          t += "  " + el.symbol + "-" + iso.A + "   " + iso.mass + " u   " + ab + "\n";
        });
        $("el-out").textContent = t;
      };
      li.addEventListener("click", open);
      li.addEventListener("keydown", (ev) => {
        if (ev.key === "Enter") {
          ev.preventDefault();
          open();
        }
      });
      box.appendChild(li);
    });
  }
  if ($("el-q")) {
    $("el-q").addEventListener("input", loadElements);
    $("el-q").addEventListener("keydown", (ev) => {
      if (ev.key === "Enter") {
        ev.preventDefault();
        const first = $("el-list") && $("el-list").querySelector("li");
        if (first) first.click();
      }
    });
  }

  async function loadSources() {
    if (!$("src-out")) return;
    const data = await get("/api/sources");
    const pack = (data && data.sources) || {};
    let t = "";
    Object.keys(pack).forEach((k) => {
      const s = pack[k];
      const name = (s.name && (s.name[state.lang] || s.name.en)) || k;
      const note = (s.note && (s.note[state.lang] || s.note.en)) || "";
      t += name + "\n" + (s.url || "") + "\n" + note + "\n\n";
    });
    $("src-out").textContent = t;
  }

  if ($("fields")) {
    $("fields").addEventListener("keydown", (ev) => {
      if (ev.key === "Enter" && ev.target && ev.target.matches("input")) {
        ev.preventDefault();
        solveNow();
      }
    });
  }
  if ($("coeffs")) {
    $("coeffs").addEventListener("keydown", (ev) => {
      if (ev.key === "Enter" && ev.target && ev.target.matches("input")) {
        ev.preventDefault();
        doPoly("eval");
      }
    });
  }
  if ($("poly-x")) {
    $("poly-x").addEventListener("keydown", (ev) => {
      if (ev.key === "Enter") {
        ev.preventDefault();
        doPoly("eval");
      }
    });
  }

  screen.addEventListener("focus", () => {
    if (screen.value === "0") screen.select();
  });
  screen.addEventListener("input", () => {
    state.expr = screen.value === "0" ? "" : screen.value;
  });
  screen.addEventListener("keydown", (ev) => {
    if (ev.key === "Enter") {
      ev.preventDefault();
      onKey("=");
      return;
    }
    if (ev.key === "Escape") {
      ev.preventDefault();
      onKey("AC");
      return;
    }
    if (ev.key === "^") {
      ev.preventDefault();
      insertScreen("**");
    }
  });

  document.querySelectorAll("[data-k]").forEach((b) => {
    b.tabIndex = -1;
    b.addEventListener("click", () => onKey(b.getAttribute("data-k")));
  });

  document.addEventListener("keydown", (ev) => {
    if (ev.altKey && !ev.ctrlKey && !ev.metaKey) {
      const n = ev.key;
      if (n >= "1" && n <= "9") {
        ev.preventDefault();
        showMode(MODES[Number(n) - 1]);
        return;
      }
      if (n === "l" || n === "L") {
        ev.preventDefault();
        focusLookup();
        return;
      }
    }
    if (isTypingField(ev.target)) return;
    if (ev.key === "/" || ev.key === "Slash") {
      ev.preventDefault();
      focusLookup();
      return;
    }
    if (state.mode !== "calc") return;
    if (ev.key === "Enter") {
      ev.preventDefault();
      onKey("=");
      return;
    }
    if (ev.key === "Escape") {
      onKey("AC");
      return;
    }
    if (ev.key === "Backspace") {
      ev.preventDefault();
      onKey("C");
      return;
    }
    if (ev.key.length === 1 && !ev.ctrlKey && !ev.metaKey && !ev.altKey) {
      ev.preventDefault();
      insertScreen(ev.key === "^" ? "**" : ev.key);
    }
  });

  let lookupTimer = 0;
  async function runLookup() {
    const q = ($("lookup-q") && $("lookup-q").value) || "";
    const box = $("lookup-hits");
    if (!box) return;
    if (!q.trim()) {
      box.innerHTML = "";
      state.lookupPick = null;
      return;
    }
    const rows = await get("/api/lookup?lang=" + encodeURIComponent(state.lang) + "&q=" + encodeURIComponent(q));
    box.innerHTML = "";
    state.lookupPick = (rows && rows[0]) || null;
    (rows || []).slice(0, 5).forEach((row, i) => {
      const b = document.createElement("button");
      b.type = "button";
      b.textContent = (row.label + "  " + row.text + " " + (row.unit || "")).trim();
      if (i === 0) b.classList.add("on");
      b.addEventListener("click", () => {
        state.lookupPick = row;
        insertLookup();
      });
      box.appendChild(b);
    });
  }

  function insertLookup() {
    const row = state.lookupPick;
    if (!row) return;
    const text = String(row.insert || row.text || "");
    const field = state.lastField;
    if (field && field.id === "screen") {
      insertScreen(text);
      return;
    }
    if (field && typeof field.value === "string") {
      const start = field.selectionStart == null ? field.value.length : field.selectionStart;
      const end = field.selectionEnd == null ? start : field.selectionEnd;
      field.value = field.value.slice(0, start) + text + field.value.slice(end);
      const pos = start + text.length;
      try { field.setSelectionRange(pos, pos); } catch (err) {}
      field.focus();
      return;
    }
    if (state.mode === "calc") insertScreen(text);
  }

  document.addEventListener("focusin", (ev) => {
    const el = ev.target;
    if (!el || !el.matches) return;
    if (el.id === "lookup-q") return;
    if (el.matches("input, textarea")) state.lastField = el;
  });
  if ($("lookup-q")) {
    $("lookup-q").addEventListener("input", () => {
      clearTimeout(lookupTimer);
      lookupTimer = setTimeout(runLookup, 120);
    });
    $("lookup-q").addEventListener("keydown", (ev) => {
      if (ev.key === "Enter") {
        ev.preventDefault();
        insertLookup();
      }
    });
  }
  if ($("lookup-insert")) $("lookup-insert").addEventListener("click", insertLookup);

  async function runProblem(mode) {
    const out = await post("/api/problem", {
      text: ($("prob-text") && $("prob-text").value) || "",
      mode: mode || "solve",
      unknown: ($("prob-unk") && $("prob-unk").value) || "x",
      at: ($("prob-at") && $("prob-at").value) || "",
      lang: state.lang,
      eng: state.eng,
    });
    if ($("prob-out")) $("prob-out").textContent = out.text || "0";
    showSteps("prob-steps", out.steps || []);
  }

  if ($("prob-solve")) $("prob-solve").addEventListener("click", () => runProblem("solve"));
  if ($("prob-inv")) $("prob-inv").addEventListener("click", () => runProblem("inverse"));
  if ($("prob-text")) {
    $("prob-text").addEventListener("keydown", (ev) => {
      if (ev.key === "Enter" && (ev.ctrlKey || ev.metaKey)) {
        ev.preventDefault();
        runProblem(ev.shiftKey ? "inverse" : "solve");
      }
    });
  }
  if ($("prob-unk")) {
    $("prob-unk").addEventListener("keydown", (ev) => {
      if (ev.key === "Enter") {
        ev.preventDefault();
        runProblem("solve");
      }
    });
  }
  if ($("prob-at")) {
    $("prob-at").addEventListener("keydown", (ev) => {
      if (ev.key === "Enter") {
        ev.preventDefault();
        runProblem("inverse");
      }
    });
  }

  window.startApp = function () {
    if (window._appStarted) return;
    window._appStarted = true;
    buildKeys();
    buildPoly();
    loadMeta();
    loadSources();
    if (screen) screen.focus();
  };
  window.onEngineReady = function () {
    loadMeta();
    loadSources();
  };
  window.startApp();
})();
