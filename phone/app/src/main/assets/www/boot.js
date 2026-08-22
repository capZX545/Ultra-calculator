(async function () {
  const msg = document.getElementById("boot-msg");
  const boot = document.getElementById("boot");
  function say(t) {
    if (msg) msg.textContent = t;
  }

  function showApp() {
    if (boot) boot.classList.add("boot-away");
    if (typeof window.startApp === "function") {
      try { window.startApp(); } catch (err) {}
    }
  }
  showApp();

  function patchWasm() {
    if (typeof WebAssembly === "undefined" || !WebAssembly.instantiateStreaming) return;
    const orig = WebAssembly.instantiateStreaming.bind(WebAssembly);
    WebAssembly.instantiateStreaming = async function (source, imports) {
      try {
        return await orig(source, imports);
      } catch (err) {
        const resp = await Promise.resolve(source);
        const buf = resp && typeof resp.arrayBuffer === "function" ? await resp.arrayBuffer() : resp;
        return WebAssembly.instantiate(buf, imports);
      }
    };
  }
  patchWasm();

  function loadClassic(src) {
    return new Promise(function (resolve, reject) {
      const s = document.createElement("script");
      s.src = src;
      s.async = false;
      s.onload = function () { resolve(); };
      s.onerror = function () { reject(new Error("script " + src)); };
      document.head.appendChild(s);
    });
  }

  try {
    say("Loading the math engine…");
    const indexURL = new URL("pyodide/", document.baseURI).href;
    if (typeof globalThis._createPyodideModule !== "function") {
      await loadClassic(indexURL + "pyodide.asm.js");
    }
    if (typeof loadPyodide !== "function") {
      throw new Error("Pyodide missing");
    }
    const pyodide = await loadPyodide({
      indexURL: indexURL,
      stdLibURL: indexURL + "python_stdlib.zip",
      lockFileURL: indexURL + "pyodide-lock.json",
    });
    say("Loading numpy and sympy…");
    await pyodide.loadPackage(["numpy", "sympy"]);
    const files = [
      "clean.py", "teach.py", "chemtools.py", "core.py",
      "lookup.py", "algorithms.py", "strings.py", "problems.py", "wordprob.py", "circuits.py", "circguide.py", "seqfind.py", "bridge.py",
      "units.py", "graphs.py", "matrixlab.py", "statsdata.py", "triangle.py",
      "searchall.py", "latexout.py", "sessionstore.py",
      "formulas.json", "elements.json", "sources.json",
    ];
    for (let i = 0; i < files.length; i += 1) {
      const name = files[i];
      say("Reading " + name + "…");
      const res = await fetch(new URL("py/" + name, document.baseURI).href);
      if (!res.ok) throw new Error("missing " + name);
      const text = await res.text();
      pyodide.FS.writeFile(name, text);
    }
    say("Starting…");
    pyodide.runPython("import bridge, core, chemtools, algorithms, lookup, problems, wordprob, circuits, circguide, seqfind, units, graphs, matrixlab, statsdata, triangle, searchall, latexout");
    window.pyodide = pyodide;
    window.pyodideReady = true;
    if (typeof window.onEngineReady === "function") {
      try { window.onEngineReady(); } catch (err) {}
    }
    if (boot) boot.style.display = "none";
  } catch (err) {
    say("Calculator is open. Engine: " + (err && err.message ? err.message : "failed"));
    setTimeout(function () {
      if (boot) boot.style.display = "none";
    }, 3500);
  }
})();
