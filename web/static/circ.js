(function () {
  const $ = (id) => document.getElementById(id);
  let cirState = {};

  function lang() {
    const st = window.ultraState || {};
    return st.lang || ($("lang") && $("lang").value) || "en";
  }

  function eng() {
    const st = window.ultraState || {};
    return !!st.eng;
  }

  async function post(url, body) {
    if (window.ultraPost) return window.ultraPost(url, body);
    try {
      const res = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body || {}),
      });
      return await res.json();
    } catch (err) {
      return { ok: true, text: "0", steps: [] };
    }
  }

  function paintGuide(out) {
    if (!out) return;
    cirState = out.state || cirState;
    if ($("cir-q")) $("cir-q").textContent = out.prompt || "";
    if ($("cir-story")) $("cir-story").textContent = (out.story || []).join("\n");
    const box = $("cir-choices");
    if (box) {
      box.innerHTML = "";
      (out.choices || []).forEach((ch) => {
        const b = document.createElement("button");
        b.type = "button";
        b.textContent = ch.label || ch.id;
        if (out.picked && ch.id === out.picked) b.classList.add("on");
        b.addEventListener("click", () => onPick(ch.id));
        box.appendChild(b);
      });
    }
    const row = $("cir-valrow");
    if (row) row.style.display = out.need_value ? "flex" : "none";
    if ($("cir-val")) {
      $("cir-val").placeholder = out.value_hint || "";
      if (!out.need_value) $("cir-val").value = "";
    }
    if ($("cir-next")) $("cir-next").textContent = out.next_label || "Next";
    if ($("cir-guide-out")) {
      const bits = [];
      if (out.formula) bits.push(out.formula);
      if (out.text) bits.push(out.text);
      $("cir-guide-out").textContent = bits.join("\n");
    }
    const stepsEl = $("cir-guide-steps");
    if (window.ultraShowSteps && stepsEl) {
      window.ultraShowSteps("cir-guide-steps", out.steps || []);
    } else if (stepsEl) {
      stepsEl.textContent = (out.steps || []).map((s, i) => (i + 1) + ") " + s).join("\n");
    }
    const act = $("cir-actions");
    if (act) {
      act.innerHTML = "";
      (out.actions || []).forEach((a) => {
        const b = document.createElement("button");
        b.type = "button";
        b.textContent = a.label || a.id;
        if (a.id === "add") b.className = "accent";
        b.addEventListener("click", () => onAction(a.id));
        act.appendChild(b);
      });
    }
  }

  async function send(extra) {
    const body = Object.assign(
      {
        action: "start",
        state: cirState,
        lang: lang(),
        eng: eng(),
        value: ($("cir-val") && $("cir-val").value) || "",
      },
      extra || {}
    );
    const out = await post("/api/circguide", body);
    paintGuide(out);
    if (out && out.need_value && $("cir-val")) $("cir-val").focus();
    return out;
  }

  function onPick(id) {
    if (id === "series" || id === "parallel") {
      send({ action: "connect", conn: id, kind: id });
      return;
    }
    send({ action: "pick", kind: id });
  }

  function onAction(id) {
    send({ action: id });
  }

  if ($("cir-next")) $("cir-next").addEventListener("click", () => send({ action: "next" }));
  if ($("cir-val")) {
    $("cir-val").addEventListener("keydown", (ev) => {
      if (ev.key === "Enter") {
        ev.preventDefault();
        send({ action: "next" });
      }
    });
  }
  if ($("seq-go")) {
    $("seq-go").addEventListener("click", async () => {
      const out = await post("/api/seqfind", {
        text: ($("seq-text") && $("seq-text").value) || "",
        lang: lang(),
        n_next: 5,
      });
      if ($("seq-out")) $("seq-out").textContent = out.text || "0";
    });
  }
  if ($("lang")) {
    $("lang").addEventListener("change", () => send({ action: "start" }));
  }
  send({ action: "start" });
})();
