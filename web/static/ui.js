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
    current: null,
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

  const $ = (id) => document.getElementById(id);
  const screen = $("screen");
  const history = $("history");
  let memory = 0;

  function setScreen(text) {
    screen.textContent = text || "0";
  }

  async function post(url, body) {
    try {
      const res = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body || {}),
      });
      return await res.json();
    } catch (err) {
      return { ok: true, text: "0", solutions: [] };
    }
  }

  async function get(url) {
    try {
      const res = await fetch(url);
      return await res.json();
    } catch (err) {
      return [];
    }
  }

  function applyStrings() {
    const s = state.strings;
    $("title").textContent = s.title || "Ultra Calculator";
    document.title = s.title || "Ultra Calculator";
    $("tab-calc").textContent = s.calc || "Calculator";
    $("tab-formulas").textContent = s.formulas || "Formulas";
    $("tab-poly").textContent = s.poly || "Polynomial";
    $("tab-numeric").textContent = s.numeric || "Numerical";
    if ($("tab-chem")) $("tab-chem").textContent = s.chem || "Chemistry";
    if ($("tab-elements")) $("tab-elements").textContent = s.elements || "Elements";
    if ($("chem-bal")) $("chem-bal").textContent = s.balance || "Balance";
    if ($("chem-mw")) $("chem-mw").textContent = s.molar || "Molar mass";
    $("lang-label").textContent = s.lang || "Language";
    $("hist-title").textContent = s.history || "History";
    $("cat-title").textContent = s.search ? " " : " ";
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

  function showMode(mode) {
    state.mode = mode;
    document.querySelectorAll(".view").forEach((el) => el.classList.remove("show"));
    document.getElementById("view-" + mode).classList.add("show");
    document.querySelectorAll(".tab").forEach((el) => {
      el.classList.toggle("on", el.getAttribute("data-mode") === mode);
    });
  }

  function buildKeys() {
    const box = $("keys");
    box.innerHTML = "";
    KEYS.forEach((row) => {
      row.forEach((label) => {
        const b = document.createElement("button");
        b.type = "button";
        b.className = "key" + (label === "=" ? " accent" : "");
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
      return;
    }
    if (label === "C") {
      state.expr = state.expr.slice(0, -1);
      setScreen(state.expr);
      return;
    }
    if (label === "+/-") {
      state.expr = state.expr.startsWith("-(") ? state.expr.slice(2, -1) : "-(" + (state.expr || "0") + ")";
      setScreen(state.expr);
      return;
    }
    if (label === "MC") { memory = 0; return; }
    if (label === "MR") {
      state.expr += String(memory);
      setScreen(state.expr);
      return;
    }
    if (label === "M+" || label === "M-") {
      const out = await post("/api/eval", payloadExpr());
      const n = Number(out.text);
      if (!Number.isNaN(n)) memory += label === "M+" ? n : -n;
      return;
    }
    if (label === "%") {
      const out = await post("/api/eval", Object.assign(payloadExpr(), { expr: "(" + (state.expr || "0") + ")/100" }));
      state.expr = out.text;
      setScreen(state.expr);
      return;
    }
    if (label === "=") {
      const out = await post("/api/eval", payloadExpr());
      const line = document.createElement("li");
      line.textContent = (state.expr || "0") + " = " + out.text;
      line.addEventListener("click", () => {
        state.expr = (state.expr || "0");
        setScreen(state.expr);
      });
      history.insertBefore(line, history.firstChild);
      state.expr = out.text;
      state.ans = out.value;
      setScreen(out.text);
      return;
    }
    state.expr += MAP[label] !== undefined ? MAP[label] : label;
    setScreen(state.expr);
  }

  function payloadExpr() {
    return { expr: state.expr || "0", angle: state.angle, eng: state.eng, ans: state.ans };
  }

  async function loadMeta() {
    const data = await get("/api/meta?lang=" + encodeURIComponent(state.lang));
    state.strings = data.strings || {};
    applyStrings();
    const sel = $("category");
    sel.innerHTML = "";
    const all = document.createElement("option");
    all.value = "";
    all.textContent = "—";
    sel.appendChild(all);
    (data.categories || []).forEach((c) => {
      const opt = document.createElement("option");
      opt.value = c.id;
      opt.textContent = c.id.split(".")[0] + " / " + c.label;
      sel.appendChild(opt);
    });
    await loadFormulas();
    if ($("el-q")) loadElements();
  }

  async function loadFormulas() {
    const q = $("search").value || "";
    const cat = $("category").value || "";
    const url = "/api/formulas?lang=" + encodeURIComponent(state.lang) + "&q=" + encodeURIComponent(q) + "&category=" + encodeURIComponent(cat);
    state.formulas = await get(url);
    const box = $("flist");
    box.innerHTML = "";
    state.formulas.forEach((item, i) => {
      const li = document.createElement("li");
      li.textContent = item.name;
      li.addEventListener("click", () => selectFormula(i, li));
      box.appendChild(li);
    });
  }

  function selectFormula(index, li) {
    document.querySelectorAll("#flist li").forEach((n) => n.classList.remove("on"));
    if (li) li.classList.add("on");
    state.current = state.formulas[index];
    $("fname").textContent = state.current.name;
    $("fexpr").textContent = state.current.expr;
    renderFields();
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
      const out = await post("/api/system", { equations: eqs, unknowns: unks, eng: state.eng });
      if (out.solutions && out.solutions.length) {
        $("fresult").textContent = out.solutions.map((sol, i) => {
          return (i + 1) + ") " + Object.keys(sol).map((k) => k + " = " + sol[k]).join("   ");
        }).join("\n");
      } else {
        $("fresult").textContent = "0";
      }
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
    });
    const extra = out.all && out.all.length > 1 ? " | " + out.all.slice(1).join(", ") : "";
    $("fresult").textContent = (out.unknown || "") + " = " + out.text + " " + (out.unit || "") + extra;
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
    });
    if (kind === "roots") {
      $("poly-out").textContent = (out.roots || []).join("\n") || "0";
      return;
    }
    $("poly-out").textContent =
      "p(x) = " + out.value_text + "\n" +
      "degree = " + out.degree + "\n" +
      "derivative coeffs: " + (out.derivative || []).join(", ") + "\n" +
      "integral coeffs: " + (out.integral || []).join(", ");
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
    });
    let text = out.text || "0";
    if (out.exact) text += "\n" + out.exact;
    if (out.path) {
      text += "\n";
      out.path.slice(-20).forEach((p) => { text += "\n" + p[0] + "   " + p[1]; });
    }
    $("n-out").textContent = text;
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
  $("category").addEventListener("change", loadFormulas);
  $("search").addEventListener("input", loadFormulas);
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

  document.addEventListener("keydown", (ev) => {
    if (state.mode !== "calc") return;
    if (ev.key === "Enter") { ev.preventDefault(); onKey("="); return; }
    if (ev.key === "Backspace") { ev.preventDefault(); onKey("C"); return; }
    if (ev.key === "Escape") { onKey("AC"); return; }
    if ("0123456789.+-*/()".indexOf(ev.key) >= 0) {
      state.expr += ev.key;
      setScreen(state.expr);
    }
  });

  buildKeys();
  buildPoly();
  loadMeta();
})();
