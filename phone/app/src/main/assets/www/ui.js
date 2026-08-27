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
    favorites: [],
    lastLatex: "",
  };

  const KEYS = [
    ["AC","C","(",")"],
    ["sin","cos","tan","/"],
    ["ln","log","sqrt","*"],
    ["7","8","9","-"],
    ["4","5","6","+"],
    ["1","2","3","^"],
    ["0",".","pi","="],
  ];
  const MAP = {
    sin:"sin(", cos:"cos(", tan:"tan(",
    asin:"asin(", acos:"acos(", atan:"atan(",
    sinh:"sinh(", cosh:"cosh(", tanh:"tanh(",
    ln:"ln(", log:"log10(", log2:"log2(",
    exp:"exp(", "10^x":"10**(", "x^2":"**2", "x^y":"**",
    sqrt:"sqrt(", "n!":"factorial(", abs:"abs(",
    "1/x":"1/(", pi:"pi", e:"e", ans:"ans", EE:"*10**", "^":"**",
  };
  const MODES = ["calc", "formulas", "poly", "numeric", "algo", "chem", "elements", "sources", "problems", "circuits", "graph", "matrix", "stats", "triangle", "seq"];

  const $ = (id) => document.getElementById(id);
  const screen = $("screen");
  const history = $("history");
  let memory = 0;
  const local = { catalog: null, algos: null, elements: null, sources: null, strings: null };

  function applyPacked(data) {
    if (!data) return false;
    if (data.formulas && data.categories) {
      local.catalog = { categories: data.categories, formulas: data.formulas };
    } else if (data.catalog) {
      local.catalog = data.catalog;
    }
    if (data.algos) local.algos = data.algos;
    if (data.elements) local.elements = data.elements;
    if (data.sources) local.sources = data.sources;
    if (data.strings) local.strings = data.strings;
    return !!(local.catalog && local.catalog.formulas && local.catalog.formulas.length);
  }

  function loadPacked() {
    if (applyPacked(window.PACKED)) return Promise.resolve(true);
    function j(url) {
      return fetch(new URL(url, document.baseURI).href).then(function (r) {
        return r.ok ? r.json() : null;
      }).catch(function () { return null; });
    }
    return Promise.all([
      j("py/formulas.json"),
      j("py/algos.json"),
      j("py/elements.json"),
      j("py/sources.json"),
      j("py/strings.json"),
    ]).then(function (pack) {
      local.catalog = pack[0];
      local.algos = pack[1];
      local.elements = pack[2];
      local.sources = pack[3];
      local.strings = pack[4];
      return !!(local.catalog && local.catalog.formulas);
    }).catch(function () { return false; });
  }

  function localMeta(lang) {
    lang = lang || "en";
    const cats = (local.catalog && local.catalog.categories) || {};
    const rows = (local.catalog && local.catalog.formulas) || [];
    const counts = {};
    rows.forEach((r) => {
      const k = r.category || "";
      counts[k] = (counts[k] || 0) + 1;
    });
    const labeled = Object.keys(cats).sort().map((id) => ({
      id: id,
      label: (cats[id] && (cats[id][lang] || cats[id].en)) || id,
      count: counts[id] || 0,
    }));
    const strings = (local.strings && (local.strings[lang] || local.strings.en)) || {};
    return { strings: strings, categories: labeled, total: rows.length, languages: ["en", "fa", "fi"] };
  }

  function localFormulas(q, lang, category) {
    const rows = (local.catalog && local.catalog.formulas) || [];
    q = String(q || "").toLowerCase();
    const out = [];
    for (let i = 0; i < rows.length; i += 1) {
      const r = rows[i];
      if (category && r.category !== category) continue;
      if (q) {
        const blob = [r.id, r.category, r.expr, (r.name && r.name[lang]) || "", (r.name && r.name.en) || ""].join(" ").toLowerCase();
        if (blob.indexOf(q) < 0) continue;
      }
      out.push({
        id: r.id,
        category: r.category,
        name: (r.name && (r.name[lang] || r.name.en)) || r.id,
        expr: r.expr,
        variables: r.variables || {},
        names: r.name,
      });
    }
    return out;
  }

  function localAlgos(q, lang, category) {
    const pack = local.algos || {};
    const items = pack.items || [];
    const cats = pack.categories || {};
    q = String(q || "").toLowerCase();
    const counts = {};
    items.forEach((r) => { counts[r.category] = (counts[r.category] || 0) + 1; });
    const labeled = Object.keys(cats).sort().map((id) => ({
      id: id,
      label: (cats[id] && (cats[id][lang] || cats[id].en)) || id,
      count: counts[id] || 0,
    }));
    const filtered = [];
    items.forEach((r) => {
      if (category && r.category !== category) return;
      if (q) {
        const blob = [r.id, r.category, (r.name && r.name[lang]) || "", (r.name && r.name.en) || ""].join(" ").toLowerCase();
        if (blob.indexOf(q) < 0) return;
      }
      filtered.push({
        id: r.id,
        category: r.category,
        name: (r.name && (r.name[lang] || r.name.en)) || r.id,
        params: r.params || {},
      });
    });
    return { categories: labeled, total: items.length, items: filtered };
  }

  function localElements(q, lang) {
    let rows = local.elements;
    if (!rows) return [];
    if (!Array.isArray(rows) && rows.elements) rows = rows.elements;
    if (!Array.isArray(rows)) return [];
    q = String(q || "").toLowerCase();
    const out = [];
    rows.forEach((el) => {
      const name = (el.name && (el.name[lang] || el.name.en)) || el.symbol || "";
      if (q) {
        const blob = [String(el.Z || ""), el.symbol || "", name].join(" ").toLowerCase();
        if (blob.indexOf(q) < 0) return;
      }
      out.push({
        Z: el.Z,
        symbol: el.symbol,
        name: name,
        mass: el.mass,
        group: el.group,
        isotopes: el.isotopes || [],
        names: el.name,
      });
    });
    return out;
  }

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

  function degWrap(fn) {
    return function (x) { return fn((Number(x) || 0) * Math.PI / 180); };
  }
  function jsEval(body) {
    const angle = (body && body.angle) || "DEG";
    let expr = String((body && body.expr) || "0");
    expr = expr.replace(/π/g, "pi").replace(/×/g, "*").replace(/÷/g, "/").replace(/−/g, "-").replace(/\^/g, "**");
    expr = expr.replace(/\bpi\b/g, "pi").replace(/\be\b/g, "e");
    expr = expr.replace(/(^|[^0-9.])10(?:\.0+)?[eE]([+-]?\d+)/g, "$11e$2");
    const sin = angle === "DEG" ? degWrap(Math.sin) : Math.sin;
    const cos = angle === "DEG" ? degWrap(Math.cos) : Math.cos;
    const tan = angle === "DEG" ? degWrap(Math.tan) : Math.tan;
    try {
      const fn = new Function("sin","cos","tan","sqrt","abs","pi","e","ans","log","ln","log10","exp","return (" + expr.replace(/\bln\(/g,"log(").replace(/\blog10\(/g,"log10(") + ");");
      let v = fn(sin, cos, tan, Math.sqrt, Math.abs, Math.PI, Math.E, Number(state.ans)||0, Math.log, Math.log, function(x){return Math.log(x)/Math.LN10;}, Math.exp);
      if (typeof v !== "number" || !Number.isFinite(v)) v = 0;
      const text = String(v);
      return { ok: true, text: text, value: v, steps: [] };
    } catch (err) {
      return { ok: true, text: "0", value: 0, steps: [] };
    }
  }
  function localSolve(item, values, unknown, eng) {
    try {
      const expr = String((item && item.expr) || "");
      const parts = expr.split("=");
      if (parts.length < 2) return { ok: true, text: "0", unknown: unknown || "", unit: "", all: ["0"] };
      const vars = (item && item.variables) || {};
      const names = Object.keys(vars);
      unknown = unknown || names[0] || "x";
      function tok(n) { return new RegExp("\\b" + n.replace(/[.*+?^${}()|[\]\\]/g, "\\$&") + "\\b", "g"); }
      function subst(s) {
        names.forEach(function (n) {
          if (n === unknown) return;
          const raw = values ? values[n] : "";
          if (raw === undefined || raw === null || String(raw).trim() === "") return;
          const num = Number(String(raw).replace(",", "."));
          if (!Number.isFinite(num)) return;
          s = s.replace(tok(n), "(" + num + ")");
        });
        return s;
      }
      const left = subst(parts[0].trim());
      const right = subst(parts.slice(1).join("=").trim());
      function ev(s) {
        s = String(s);
        s = s.replace(/\^/g, "**");
        s = s.replace(/\bpi\b/g, "Math.PI");
        s = s.replace(/\bsqrt\s*\(/g, "Math.sqrt(");
        s = s.replace(/\blog10\s*\(/g, "(Math.log(");
        s = s.replace(/\bln\s*\(/g, "Math.log(");
        s = s.replace(/\blog\s*\(/g, "Math.log(");
        s = s.replace(/\bexp\s*\(/g, "Math.exp(");
        s = s.replace(/\bsin\s*\(/g, "Math.sin(");
        s = s.replace(/\bcos\s*\(/g, "Math.cos(");
        s = s.replace(/\btan\s*\(/g, "Math.tan(");
        s = s.replace(/\babs\s*\(/g, "Math.abs(");
        const v = Function("return (" + s + ");")();
        const n = typeof v === "number" ? v : Number(v);
        return Number.isFinite(n) ? n : NaN;
      }
      function fmt(n) {
        if (!Number.isFinite(n)) return "0";
        return String(parseFloat(n.toPrecision(10)));
      }
      if (left === unknown) {
        const text = fmt(ev(right));
        return { ok: true, unknown: unknown, text: text, unit: (vars[unknown] && vars[unknown].unit) || "", all: [text] };
      }
      if (right === unknown) {
        const text = fmt(ev(left));
        return { ok: true, unknown: unknown, text: text, unit: (vars[unknown] && vars[unknown].unit) || "", all: [text] };
      }
      function f(x) {
        const L = left.replace(tok(unknown), "(" + x + ")");
        const R = right.replace(tok(unknown), "(" + x + ")");
        return ev(L) - ev(R);
      }
      let x0 = 1;
      for (let i = 0; i < 50; i += 1) {
        const y = f(x0);
        const h = Math.max(1e-7, Math.abs(x0) * 1e-6);
        const yp = (f(x0 + h) - y) / h;
        if (!Number.isFinite(y) || !Number.isFinite(yp) || Math.abs(yp) < 1e-14) break;
        const x1 = x0 - y / yp;
        if (!Number.isFinite(x1)) break;
        if (Math.abs(x1 - x0) < 1e-10) { x0 = x1; break; }
        x0 = x1;
      }
      const text = fmt(x0);
      return { ok: true, unknown: unknown, text: text, unit: (vars[unknown] && vars[unknown].unit) || "", all: [text] };
    } catch (err) {
      return { ok: true, text: "0", unknown: unknown || "", unit: "", all: ["0"] };
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
    if (path === "/api/meta") return local.catalog ? localMeta(query.lang || state.lang || "en") : { strings: state.strings || {}, categories: [], total: 0, languages: ["en", "fa", "fi"] };
    if (path === "/api/formulas" && local.catalog) return localFormulas((query && query.q) || "", (query && query.lang) || state.lang, (query && query.category) || "");
    if (path === "/api/solve") {
      const id = (body && body.id) || "";
      const rows = (local.catalog && local.catalog.formulas) || [];
      let item = null;
      for (let i = 0; i < rows.length; i += 1) { if (rows[i].id === id) { item = rows[i]; break; } }
      if (!item) return { ok: true, text: "0", unknown: (body && body.unknown) || "", unit: "", all: ["0"] };
      return localSolve(item, (body && body.values) || {}, body && body.unknown, !!(body && body.eng));
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
    const path = u.pathname;
    const lang = query.lang || state.lang || "en";
    if (path === "/api/meta" && local.catalog) return localMeta(lang);
    if (path === "/api/formulas" && local.catalog) return localFormulas(query.q, lang, query.category || "");
    if (path === "/api/algos" && local.algos) return localAlgos(query.q, lang, query.category || "");
    if (path === "/api/elements" && local.elements) return localElements(query.q, lang);
    if (path === "/api/sources" && local.sources) return local.sources;
    return pyCall(path, query, {});
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
    if ($("tab-circuits")) $("tab-circuits").textContent = s.circuits || "Circuits";
    if ($("tab-graph")) $("tab-graph").textContent = s.graph || "Graph";
    if ($("tab-matrix")) $("tab-matrix").textContent = s.matrix || "Matrix";
    if ($("tab-stats")) $("tab-stats").textContent = s.stats || "Stats";
    if ($("tab-triangle")) $("tab-triangle").textContent = s.triangle || "Triangle";
    if ($("tab-seq")) $("tab-seq").textContent = s.seq || "Sequences";
    if ($("seq-hint")) $("seq-hint").textContent = s.seq_hint || "";
    if ($("seq-go")) $("seq-go").textContent = s.seq_go || "Identify";
    if ($("cir-next")) $("cir-next").textContent = s.cir_next || "Next";
    if ($("cir-adv-sum")) $("cir-adv-sum").textContent = s.cir_adv || "Netlist";
    if ($("graph-plot")) $("graph-plot").textContent = s.plot || "Plot";
    if ($("graph-param")) $("graph-param").textContent = s.parametric || "Parametric";
    if ($("graph-data")) $("graph-data").textContent = s.data || "Data";
    if ($("graph-bode")) $("graph-bode").textContent = s.bode || "Bode";
    if ($("graph-hint")) $("graph-hint").textContent = s.graph_hint || "";
    if ($("matrix-hint")) $("matrix-hint").textContent = s.matrix_hint || "";
    if ($("stats-hint")) $("stats-hint").textContent = s.stats_hint || "";
    if ($("tri-hint")) $("tri-hint").textContent = s.triangle_hint || "";
    if ($("mat-det")) $("mat-det").textContent = s.det || "det";
    if ($("mat-inv")) $("mat-inv").textContent = s.invm || "Inverse";
    if ($("mat-t")) $("mat-t").textContent = s.trans || "Transpose";
    if ($("mat-eig")) $("mat-eig").textContent = s.eig || "Eigen";
    if ($("mat-rref")) $("mat-rref").textContent = s.rref || "RREF";
    if ($("mat-mul")) $("mat-mul").textContent = s.mul || "Multiply";
    if ($("mat-solve")) $("mat-solve").textContent = s.solve_axb || "Solve Ax=b";
    if ($("stats-run")) $("stats-run").textContent = s.run || "Run";
    if ($("tri-solve")) $("tri-solve").textContent = s.solve || "Solve";
    if ($("n-ode2")) $("n-ode2").textContent = s.ode2 || "ODE 2nd";
    if ($("n-odesys")) $("n-odesys").textContent = s.odesys || "ODE system";
    if ($("btn-save")) $("btn-save").textContent = s.save || "Save";
    if ($("btn-load")) $("btn-load").textContent = s.load || "Load";
    if ($("btn-latex")) $("btn-latex").textContent = s.latex || "LaTeX";
    if ($("cir-solve")) $("cir-solve").textContent = s.solve || "Solve";
    if ($("cir-inv")) $("cir-inv").textContent = s.inverse || "Inverse";
    if ($("cir-hint")) $("cir-hint").textContent = s.circuit_hint || "";
    if ($("cir-freq-label")) {
      const inp = $("cir-freq");
      $("cir-freq-label").textContent = (s.circuit_freq || "f (Hz)") + " ";
      if (inp) $("cir-freq-label").appendChild(inp);
    }
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
    } else if (mode === "circuits" && $("cir-text")) {
      $("cir-text").focus();
    } else if (mode === "graph" && $("graph-text")) {
      $("graph-text").focus();
    } else if (mode === "matrix" && $("mat-a")) {
      $("mat-a").focus();
    } else if (mode === "stats" && $("stats-text")) {
      $("stats-text").focus();
    } else if (mode === "triangle" && $("tri-a")) {
      $("tri-a").focus();
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
      state.lastLatex = out.latex || out.exact || out.text || source;
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
    const listed = await get(url);
    const all = Array.isArray(listed) ? listed : [];
    const cap = 180;
    state.formulas = all.slice(0, cap);
    const box = $("flist");
    box.innerHTML = "";
    if ($("search-title")) {
      const more = all.length > cap ? " / " + all.length : "";
      $("search-title").textContent = (state.strings.search || "Search") + "  (" + state.formulas.length + more + ")";
    }
    if (!all.length && !cat && !q) {
      const li = document.createElement("li");
      li.textContent = state.strings.pick || "Pick a category.";
      box.appendChild(li);
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
      yp0: ($("n-yp0") && $("n-yp0").value) || "0",
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
  if ($("n-ode2")) $("n-ode2").addEventListener("click", () => doNumeric("ode2"));
  if ($("n-odesys")) $("n-odesys").addEventListener("click", () => doNumeric("odesys"));

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
    state.algos = (data && Array.isArray(data.items)) ? data.items : [];
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
      if (n === "0") {
        ev.preventDefault();
        showMode("circuits");
        return;
      }
      if (n === "s" || n === "S") {
        ev.preventDefault();
        showMode("seq");
        return;
      }
      if (n === "l" || n === "L") {
        ev.preventDefault();
        focusLookup();
        return;
      }
      if (n === "g" || n === "G") { ev.preventDefault(); showMode("graph"); return; }
      if (n === "m" || n === "M") { ev.preventDefault(); showMode("matrix"); return; }
      if (n === "d" || n === "D") { ev.preventDefault(); showMode("stats"); return; }
      if (n === "t" || n === "T") { ev.preventDefault(); showMode("triangle"); return; }
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
    const fav = (state.favorites || []).map((f) => (f.kind || "") + ":" + (f.id || "")).join(",");
    const found = await get("/api/search?lang=" + encodeURIComponent(state.lang) + "&q=" + encodeURIComponent(q) + "&fav=" + encodeURIComponent(fav));
    box.innerHTML = "";
    state.lookupPick = (rows && rows[0]) || null;
    (rows || []).slice(0, 4).forEach((row, i) => {
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
    ((found && found.hits) || []).slice(0, 6).forEach((hit) => {
      const b = document.createElement("button");
      b.type = "button";
      b.textContent = (hit.star ? "* " : "") + (hit.title || hit.id || "");
      b.title = hit.kind || "";
      b.addEventListener("click", () => {
        if (hit.go) showMode(hit.go);
        if (hit.kind === "cas" && hit.extra) insertScreen(hit.extra);
        if (hit.kind === "circuit" && hit.extra && $("cir-text")) {
          showMode("circuits");
          $("cir-text").value = hit.extra;
        }
        if (hit.kind === "formula" && $("search")) {
          $("search").value = hit.title || "";
          loadFormulas();
        }
      });
      b.addEventListener("contextmenu", (ev) => {
        ev.preventDefault();
        const key = { kind: hit.kind, id: hit.id };
        const i = (state.favorites || []).findIndex((f) => f.kind === key.kind && f.id === key.id);
        if (i >= 0) state.favorites.splice(i, 1);
        else state.favorites.push(key);
        try { localStorage.setItem("ultra-fav", JSON.stringify(state.favorites)); } catch (err) {}
        runLookup();
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

  async function runCircuit(mode) {
    const out = await post("/api/circuit", {
      text: ($("cir-text") && $("cir-text").value) || "",
      mode: mode || "solve",
      freq: ($("cir-freq") && $("cir-freq").value) || "",
      lang: state.lang,
      eng: state.eng,
    });
    if ($("cir-out")) $("cir-out").textContent = out.text || "0";
    showSteps("cir-steps", out.steps || []);
  }
  if ($("cir-solve")) $("cir-solve").addEventListener("click", () => runCircuit("solve"));
  if ($("cir-inv")) $("cir-inv").addEventListener("click", () => runCircuit("inverse"));
  if ($("cir-text")) {
    $("cir-text").addEventListener("keydown", (ev) => {
      if (ev.key === "Enter" && (ev.ctrlKey || ev.metaKey)) {
        ev.preventDefault();
        runCircuit(ev.shiftKey ? "inverse" : "solve");
      }
    });
  }


  async function runGraph(kind) {
    const out = await post("/api/graph", {
      kind: kind || "func",
      funcs: ($("graph-text") && $("graph-text").value) || "",
      data: ($("graph-text") && $("graph-text").value) || "",
      circuit: ($("graph-text") && $("graph-text").value) || "",
      xmin: ($("graph-xmin") && $("graph-xmin").value) || "-10",
      xmax: ($("graph-xmax") && $("graph-xmax").value) || "10",
      node: ($("graph-node") && $("graph-node").value) || "2",
      lang: state.lang,
      eng: state.eng,
    });
    if ($("graph-out")) $("graph-out").textContent = out.text || "0";
    if ($("graph-svg")) $("graph-svg").innerHTML = out.svg || "";
    state.lastLatex = out.latex || out.text || "";
  }
  if ($("graph-plot")) $("graph-plot").addEventListener("click", () => runGraph("func"));
  if ($("graph-param")) $("graph-param").addEventListener("click", () => runGraph("param"));
  if ($("graph-data")) $("graph-data").addEventListener("click", () => runGraph("data"));
  if ($("graph-bode")) $("graph-bode").addEventListener("click", () => runGraph("bode"));

  async function runMatrix(op) {
    const out = await post("/api/matrix", {
      op: op,
      a: ($("mat-a") && $("mat-a").value) || "",
      b: ($("mat-b") && $("mat-b").value) || "",
      eng: state.eng,
      lang: state.lang,
    });
    if ($("mat-out")) $("mat-out").textContent = out.text || "0";
    showSteps("mat-steps", out.steps || []);
    state.lastLatex = out.latex || out.text || "";
  }
  [["mat-det","det"],["mat-inv","inv"],["mat-t","t"],["mat-eig","eig"],["mat-rref","rref"],["mat-mul","mul"],["mat-solve","solve"],["mat-rank","rank"]].forEach((pair) => {
    if ($(pair[0])) $(pair[0]).addEventListener("click", () => runMatrix(pair[1]));
  });

  async function runStats() {
    const out = await post("/api/stats", { text: ($("stats-text") && $("stats-text").value) || "", lang: state.lang, eng: state.eng });
    if ($("stats-out")) $("stats-out").textContent = out.text || "0";
    if ($("stats-svg")) $("stats-svg").innerHTML = out.svg || "";
    state.lastLatex = out.latex || out.text || "";
  }
  if ($("stats-run")) $("stats-run").addEventListener("click", runStats);

  async function runTriangle() {
    const values = {
      a: ($("tri-a") && $("tri-a").value) || "",
      b: ($("tri-b") && $("tri-b").value) || "",
      c: ($("tri-c") && $("tri-c").value) || "",
      A: ($("tri-A") && $("tri-A").value) || "",
      B: ($("tri-B") && $("tri-B").value) || "",
      C: ($("tri-C") && $("tri-C").value) || "",
    };
    const out = await post("/api/triangle", { values: values, lang: state.lang, eng: state.eng });
    if ($("tri-out")) $("tri-out").textContent = out.text || "0";
    showSteps("tri-steps", out.steps || []);
    state.lastLatex = out.latex || out.text || "";
  }
  if ($("tri-solve")) $("tri-solve").addEventListener("click", runTriangle);

  function sessionPayload() {
    const hist = [];
    if (history) Array.from(history.querySelectorAll("li")).forEach((li) => hist.push(li.textContent));
    return {
      lang: state.lang, angle: state.angle, eng: state.eng, history: hist.slice(0, 80),
      circuit: ($("cir-text") && $("cir-text").value) || "",
      problem: ($("prob-text") && $("prob-text").value) || "",
      graph: ($("graph-text") && $("graph-text").value) || "",
      matrix: ($("mat-a") && $("mat-a").value) || "",
      stats: ($("stats-text") && $("stats-text").value) || "",
      favorites: state.favorites || [],
    };
  }
  function applySession(data) {
    if (!data || typeof data !== "object") return;
    if (data.lang && $("lang")) { $("lang").value = data.lang; state.lang = data.lang; }
    if (data.circuit && $("cir-text")) $("cir-text").value = data.circuit;
    if (data.problem && $("prob-text")) $("prob-text").value = data.problem;
    if (data.graph && $("graph-text")) $("graph-text").value = data.graph;
    if (data.matrix && $("mat-a")) $("mat-a").value = data.matrix;
    if (data.stats && $("stats-text")) $("stats-text").value = data.stats;
    if (Array.isArray(data.favorites)) state.favorites = data.favorites;
    applyStrings();
  }
  async function saveSession() {
    const data = sessionPayload();
    try { localStorage.setItem("ultra-session", JSON.stringify(data)); } catch (err) {}
    await post("/api/session", data);
    if ($("kbd-hint")) $("kbd-hint").textContent = state.strings.session_saved || "Session saved.";
  }
  async function loadSession() {
    let data = null;
    try { data = JSON.parse(localStorage.getItem("ultra-session") || "null"); } catch (err) { data = null; }
    if (!data) data = await get("/api/session");
    applySession(data);
    loadMeta();
  }
  if ($("btn-save")) $("btn-save").addEventListener("click", saveSession);
  if ($("btn-load")) $("btn-load").addEventListener("click", loadSession);
  async function copyLatex() {
    const src = state.lastLatex || readExpr() || "0";
    const out = await post("/api/latex", { text: src, exact: src });
    const tex = out.latex || out.text || src;
    try { await navigator.clipboard.writeText(tex); } catch (err) {}
    if ($("kbd-hint")) $("kbd-hint").textContent = (state.strings.copy_latex || "LaTeX") + "  " + tex;
  }
  if ($("btn-latex")) $("btn-latex").addEventListener("click", copyLatex);
  try {
    const raw = localStorage.getItem("ultra-session");
    if (raw) applySession(JSON.parse(raw));
    const fav = localStorage.getItem("ultra-fav");
    if (fav) state.favorites = JSON.parse(fav);
  } catch (err) {}

  window.startApp = function () {
    if (window._appStarted) return;
    window._appStarted = true;
    buildKeys();
    buildPoly();
    var ready = loadPacked();
    function go() {
      loadMeta();
      loadSources();
      loadAlgos();
      if (screen) screen.focus();
    }
    if (ready && typeof ready.then === "function") ready.then(go); else go();
  };
  window.onEngineReady = function () {
    if ($("kbd-hint") && state.strings && state.strings.engine_ready) {
      $("kbd-hint").textContent = state.strings.engine_ready;
    }
  };
  window.startApp();
  window.ultraPost = post;
  window.ultraGet = get;
  window.ultraState = state;
  window.ultraShowMode = showMode;
  window.ultraShowSteps = showSteps;

})();
