(async function () {
  const msg = document.getElementById("boot-msg");
  const boot = document.getElementById("boot");
  function say(t) { if (msg) msg.textContent = t; }
  try {
    say("Loading the math engine…");
    const pyodide = await loadPyodide({ indexURL: "pyodide/" });
    say("Loading numpy and sympy…");
    await pyodide.loadPackage(["numpy", "sympy"]);
    const files = [
      "clean.py", "teach.py", "chemtools.py", "core.py",
      "lookup.py", "algorithms.py", "strings.py", "bridge.py",
      "formulas.json", "elements.json", "sources.json",
    ];
    for (const name of files) {
      say("Reading " + name + "…");
      const res = await fetch("py/" + name);
      const text = await res.text();
      pyodide.FS.writeFile(name, text);
    }
    say("Starting…");
    pyodide.runPython("import bridge, core, chemtools, algorithms, lookup");
    window.pyodide = pyodide;
    window.pyodideReady = true;
    if (boot) boot.style.display = "none";
    if (typeof window.startApp === "function") window.startApp();
  } catch (err) {
    say("Could not start. " + (err && err.message ? err.message : ""));
  }
})();
