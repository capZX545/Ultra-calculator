(function () {
  function faNum(s) {
    s = String(s == null ? "" : s);
    const a = "۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", b = "01234567890123456789";
    let o = "";
    for (let i = 0; i < s.length; i += 1) {
      const k = a.indexOf(s[i]);
      o += k >= 0 ? b[k] : s[i];
    }
    return o.replace(/×/g, "*").replace(/÷/g, "/").replace(/[−–—]/g, "-");
  }
  function num(raw, d) {
    if (raw === undefined || raw === null || String(raw).trim() === "") return d;
    let s = faNum(raw).trim().replace(/\s/g, "");
    if (s.indexOf(",") >= 0 && s.indexOf(".") < 0) s = s.replace(",", ".");
    else s = s.replace(/,/g, "");
    const m = s.match(/^([+\-]?\d*\.?\d+(?:[eE][+\-]?\d+)?)([a-zA-Zµμ]*)$/);
    const suf = { t: 1e12, g: 1e9, meg: 1e6, k: 1e3, m: 1e-3, u: 1e-6, µ: 1e-6, μ: 1e-6, n: 1e-9, p: 1e-12, f: 1e-15 };
    if (m) {
      let v = Number(m[1]);
      const u = (m[2] || "").toLowerCase();
      if (u === "meg") v *= 1e6;
      else if (suf[u] != null) v *= suf[u];
      return Number.isFinite(v) ? v : d;
    }
    const n = Number(s);
    return Number.isFinite(n) ? n : d;
  }
  function pretty(n) {
    if (typeof n === "object" && n && n.re != null) {
      if (Math.abs(n.im) < 1e-12) return pretty(n.re);
      const sign = n.im >= 0 ? "+" : "-";
      return pretty(n.re) + " " + sign + " j" + pretty(Math.abs(n.im));
    }
    n = Number(n);
    if (!Number.isFinite(n)) return "0";
    if (Math.abs(n) < 1e-15) return "0";
    if (Math.abs(n - Math.round(n)) < 1e-10) return String(Math.round(n));
    return String(parseFloat(n.toPrecision(12)));
  }
  function fx(expr) {
    let s = faNum(expr || "0");
    s = s.replace(/\^/g, "**").replace(/π/g, "pi");
    s = s.replace(/\bpi\b/g, "PI").replace(/\be\b/g, "E");
    s = s.replace(/\bsin\s*\(/g, "sin(").replace(/\bcos\s*\(/g, "cos(").replace(/\btan\s*\(/g, "tan(");
    s = s.replace(/\bexp\s*\(/g, "exp(").replace(/\bsqrt\s*\(/g, "sqrt(").replace(/\babs\s*\(/g, "abs(");
    s = s.replace(/\bln\s*\(/g, "log(").replace(/\blog10\s*\(/g, "log10(").replace(/\blog\s*\(/g, "log(");
    try {
      const fn = new Function("x", "y", "sin", "cos", "tan", "exp", "sqrt", "abs", "log", "log10", "PI", "E",
        "return (" + s + ");");
      return function (x, y) {
        try {
          const v = fn(x, y == null ? 0 : y, Math.sin, Math.cos, Math.tan, Math.exp, Math.sqrt, Math.abs, Math.log,
            Math.log10 || function (z) { return Math.log(z) / Math.LN10; }, Math.PI, Math.E);
          const n = typeof v === "number" ? v : Number(v);
          return Number.isFinite(n) ? n : NaN;
        } catch (e) { return NaN; }
      };
    } catch (e) { return function () { return NaN; }; }
  }
  function parseMat(text) {
    const rows = [];
    String(text || "").replace(/;/g, "\n").split(/\n/).forEach(function (ln) {
      const row = faNum(ln).trim().split(/[\s,]+/).map(function (p) { return num(p, NaN); }).filter(function (n) { return Number.isFinite(n); });
      if (row.length) rows.push(row);
    });
    if (!rows.length) return null;
    const w = Math.max.apply(null, rows.map(function (r) { return r.length; }));
    return rows.map(function (r) { while (r.length < w) r.push(0); return r; });
  }
  function fmtMat(M) {
    return M.map(function (r) { return r.map(pretty).join(", "); }).join("; ");
  }
  function det(M) {
    const n = M.length;
    const a = M.map(function (r) { return r.slice(); });
    let d = 1;
    for (let i = 0; i < n; i += 1) {
      let piv = i;
      for (let r = i + 1; r < n; r += 1) if (Math.abs(a[r][i]) > Math.abs(a[piv][i])) piv = r;
      if (Math.abs(a[piv][i]) < 1e-12) return 0;
      if (piv !== i) { const t = a[i]; a[i] = a[piv]; a[piv] = t; d = -d; }
      d *= a[i][i];
      for (let r = i + 1; r < n; r += 1) {
        const f = a[r][i] / a[i][i];
        for (let c = i; c < n; c += 1) a[r][c] -= f * a[i][c];
      }
    }
    return d;
  }
  function inverse(M) {
    const n = M.length;
    const a = M.map(function (r, i) { return r.concat(Array.from({ length: n }, function (_, j) { return i === j ? 1 : 0; })); });
    for (let i = 0; i < n; i += 1) {
      let piv = i;
      for (let r = i + 1; r < n; r += 1) if (Math.abs(a[r][i]) > Math.abs(a[piv][i])) piv = r;
      if (Math.abs(a[piv][i]) < 1e-12) return null;
      const tmp = a[i]; a[i] = a[piv]; a[piv] = tmp;
      const div = a[i][i];
      for (let c = 0; c < 2 * n; c += 1) a[i][c] /= div;
      for (let r = 0; r < n; r += 1) if (r !== i) {
        const f = a[r][i];
        for (let c = 0; c < 2 * n; c += 1) a[r][c] -= f * a[i][c];
      }
    }
    return a.map(function (r) { return r.slice(n); });
  }
  function linSolve(A, b) {
    const n = A.length;
    const M = A.map(function (r, i) { return r.concat([b[i]]); });
    for (let i = 0; i < n; i += 1) {
      let piv = i;
      for (let r = i + 1; r < n; r += 1) if (Math.abs(M[r][i]) > Math.abs(M[piv][i])) piv = r;
      if (Math.abs(M[piv][i]) < 1e-12) return null;
      const tmp = M[i]; M[i] = M[piv]; M[piv] = tmp;
      const div = M[i][i];
      for (let c = 0; c <= n; c += 1) M[i][c] /= div;
      for (let r = 0; r < n; r += 1) if (r !== i) {
        const f = M[r][i];
        for (let c = 0; c <= n; c += 1) M[r][c] -= f * M[i][c];
      }
    }
    return M.map(function (r) { return r[n]; });
  }

  function polyWork(coeffs, x) {
    const c = (coeffs || []).slice(0, 7).map(function (v) { return num(v, 0); });
    while (c.length < 7) c.unshift(0);
    let deg = 0;
    for (let i = 0; i < c.length; i += 1) if (Math.abs(c[i]) > 1e-15) { deg = 6 - i; break; }
    const der = [];
    for (let i = 0; i < 6; i += 1) der.push(c[i] * (6 - i));
    const integ = [0].concat(c.map(function (v, i) { return v / (7 - i); }));
    let value = 0;
    if (x != null && String(x) !== "") {
      const xv = num(x, 0);
      for (let i = 0; i < c.length; i += 1) value = value * xv + c[i];
    }
    const roots = [];
    const a = c[0], b = c[1], cc = c[2], d = c[3], e = c[4], f = c[5], g = c[6];
    if (deg === 1) roots.push(pretty(-g / f));
    else if (deg === 2) {
      const A = f, B = g, C = 0;
      const disc = A * A - 4 * (c[5] ? 0 : 0);
    }
    function quad(A, B, C) {
      if (Math.abs(A) < 1e-15) return Math.abs(B) < 1e-15 ? [] : [-C / B];
      const disc = B * B - 4 * A * C;
      if (disc >= 0) return [(-B + Math.sqrt(disc)) / (2 * A), (-B - Math.sqrt(disc)) / (2 * A)];
      const re = -B / (2 * A), im = Math.sqrt(-disc) / (2 * A);
      return [re + " + " + im + "i", re + " - " + im + "i"];
    }
    let rts = [];
    if (deg === 1) rts = [pretty(-c[6] / c[5])];
    else if (deg === 2) rts = quad(c[4], c[5], c[6]).map(pretty);
    else if (deg === 0) rts = [];
    else {
      const fpoly = function (z) {
        let s = 0;
        for (let i = 0; i < c.length; i += 1) s = s * z + c[i];
        return s;
      };
      const guesses = [-10, -2, -1, 0, 1, 2, 10];
      guesses.forEach(function (g0) {
        let z = g0;
        for (let i = 0; i < 40; i += 1) {
          const y = fpoly(z);
          const h = Math.max(1e-7, Math.abs(z) * 1e-6);
          const yp = (fpoly(z + h) - y) / h;
          if (Math.abs(yp) < 1e-14) break;
          z -= y / yp;
        }
        if (Number.isFinite(z) && Math.abs(fpoly(z)) < 1e-6) {
          const t = pretty(z);
          if (rts.indexOf(t) < 0) rts.push(t);
        }
      });
    }
    return {
      ok: true,
      degree: deg,
      value_text: pretty(value),
      roots: rts,
      derivative: der,
      integral: integ
    };
  }

  function numeric(kind, body) {
    const f = fx(body.func || "x");
    const a = num(body.a, 0), b = num(body.b, 1), y0 = num(body.y0, 0);
    const steps = Math.max(4, Math.min(400, Math.round(num(body.steps, 40))));
    if (kind === "root") {
      let lo = a, hi = b, flo = f(lo), fhi = f(hi);
      if (flo * fhi > 0) {
        let x = (lo + hi) / 2;
        for (let i = 0; i < 50; i += 1) {
          const y = f(x), h = Math.max(1e-7, Math.abs(x) * 1e-6);
          const yp = (f(x + h) - y) / h;
          if (Math.abs(yp) < 1e-14) break;
          x -= y / yp;
        }
        return { ok: true, text: pretty(x) };
      }
      for (let i = 0; i < 60; i += 1) {
        const m = (lo + hi) / 2, fm = f(m);
        if (flo * fm <= 0) { hi = m; fhi = fm; } else { lo = m; flo = fm; }
      }
      return { ok: true, text: pretty((lo + hi) / 2) };
    }
    if (kind === "integral") {
      const n = 80;
      const h = (b - a) / n;
      let s = f(a) + f(b);
      for (let i = 1; i < n; i += 1) s += (i % 2 ? 4 : 2) * f(a + i * h);
      return { ok: true, text: pretty(s * h / 3), exact: "" };
    }
    if (kind === "deriv") {
      const h = Math.max(1e-6, Math.abs(a) * 1e-6);
      return { ok: true, text: pretty((f(a + h) - f(a - h)) / (2 * h)), exact: "" };
    }
    let x = a, y = y0, h = (b - a) / steps;
    const path = [[x, y]];
    for (let i = 0; i < steps; i += 1) {
      const k1 = f(x, y), k2 = f(x + h / 2, y + h * k1 / 2), k3 = f(x + h / 2, y + h * k2 / 2), k4 = f(x + h, y + h * k3);
      y += h * (k1 + 2 * k2 + 2 * k3 + k4) / 6;
      x += h;
      path.push([x, y]);
    }
    return { ok: true, text: pretty(y), path: path.slice(-80) };
  }

  function triangle(values) {
    function N(k) { const v = values ? values[k] : ""; return (v === "" || v == null) ? null : num(v, null); }
    let a = N("a"), b = N("b"), c = N("c"), A = N("A"), B = N("B"), C = N("C");
    function rad(d) { return d * Math.PI / 180; }
    function deg(r) { return r * 180 / Math.PI; }
    function ang(x, y, z) {
      let t = (y * y + z * z - x * x) / (2 * y * z);
      t = Math.max(-1, Math.min(1, t));
      return Math.acos(t);
    }
    function pack() {
      if (min3(a, b, c) <= 0) return { ok: true, text: "0", steps: [] };
      const s = (a + b + c) / 2;
      const area = Math.sqrt(Math.max(0, s * (s - a) * (s - b) * (s - c)));
      if (area <= 0) return { ok: true, text: "0", steps: [] };
      if (A == null) A = deg(ang(a, b, c));
      if (B == null) B = deg(ang(b, a, c));
      if (C == null) C = 180 - A - B;
      const shown = "a=" + pretty(a) + "; b=" + pretty(b) + "; c=" + pretty(c) +
        "; A=" + pretty(A) + " deg; B=" + pretty(B) + " deg; C=" + pretty(C) +
        " deg; area=" + pretty(area) + "; peri=" + pretty(a + b + c);
      return { ok: true, text: shown, steps: [shown], area: area };
    }
    function min3(x, y, z) { return Math.min(x, y, z); }
    const ns = [a, b, c].filter(function (v) { return v != null; }).length;
    const na = [A, B, C].filter(function (v) { return v != null; }).length;
    if (ns === 3) {
      if (a + b <= c || a + c <= b || b + c <= a) return { ok: true, text: "0", steps: [] };
      A = deg(ang(a, b, c)); B = deg(ang(b, a, c)); C = 180 - A - B;
      return pack();
    }
    if (na === 2) {
      if (A == null) A = 180 - B - C;
      else if (B == null) B = 180 - A - C;
      else C = 180 - A - B;
    }
    if ([A, B, C].filter(function (v) { return v != null; }).length === 3 && ns >= 1) {
      if (a != null) { b = a * Math.sin(rad(B)) / Math.sin(rad(A)); c = a * Math.sin(rad(C)) / Math.sin(rad(A)); }
      else if (b != null) { a = b * Math.sin(rad(A)) / Math.sin(rad(B)); c = b * Math.sin(rad(C)) / Math.sin(rad(B)); }
      else { a = c * Math.sin(rad(A)) / Math.sin(rad(C)); b = c * Math.sin(rad(B)) / Math.sin(rad(C)); }
      return pack();
    }
    if (ns === 2 && na === 1) {
      if (A != null && b != null && c != null) { a = Math.sqrt(b * b + c * c - 2 * b * c * Math.cos(rad(A))); B = deg(ang(b, a, c)); C = 180 - A - B; return pack(); }
      if (B != null && a != null && c != null) { b = Math.sqrt(a * a + c * c - 2 * a * c * Math.cos(rad(B))); A = deg(ang(a, b, c)); C = 180 - A - B; return pack(); }
      if (C != null && a != null && b != null) { c = Math.sqrt(a * a + b * b - 2 * a * b * Math.cos(rad(C))); A = deg(ang(a, b, c)); B = 180 - A - C; return pack(); }
    }
    return { ok: true, text: "0", steps: [] };
  }

  function stats(text) {
    const xs = faNum(text || "").split(/[\s,;]+/).map(function (p) { return num(p, NaN); }).filter(function (n) { return Number.isFinite(n); });
    if (!xs.length) return { ok: true, text: "0", svg: "" };
    const n = xs.length;
    const sum = xs.reduce(function (a, b) { return a + b; }, 0);
    const mean = sum / n;
    let v = 0; xs.forEach(function (x) { v += (x - mean) * (x - mean); });
    v /= Math.max(1, n - 1);
    const sorted = xs.slice().sort(function (a, b) { return a - b; });
    const med = n % 2 ? sorted[(n - 1) / 2] : (sorted[n / 2 - 1] + sorted[n / 2]) / 2;
    const mn = sorted[0], mx = sorted[n - 1];
    const textOut = "n=" + n + "  mean=" + pretty(mean) + "  median=" + pretty(med) +
      "  var=" + pretty(v) + "  std=" + pretty(Math.sqrt(v)) + "  min=" + pretty(mn) + "  max=" + pretty(mx);
    const bins = 8;
    const w = 640, h = 220, pad = 20;
    const width = (mx - mn) || 1;
    const counts = Array(bins).fill(0);
    xs.forEach(function (x) {
      let i = Math.floor((x - mn) / width * bins);
      if (i >= bins) i = bins - 1;
      if (i < 0) i = 0;
      counts[i] += 1;
    });
    const maxc = Math.max.apply(null, counts) || 1;
    let svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ' + w + " " + h + '" width="100%" height="180">';
    svg += '<rect width="' + w + '" height="' + h + '" fill="#11141a"/>';
    const bw = (w - 2 * pad) / bins;
    counts.forEach(function (c, i) {
      const bh = (c / maxc) * (h - 2 * pad);
      svg += '<rect x="' + (pad + i * bw + 2) + '" y="' + (h - pad - bh) + '" width="' + (bw - 4) + '" height="' + bh + '" fill="#c4a35a"/>';
    });
    svg += "</svg>";
    return { ok: true, text: textOut, svg: svg };
  }

  function graph(body) {
    const lines = String(body.funcs || body.text || "sin(x)").split(/\n/).map(function (s) { return s.trim(); }).filter(Boolean);
    const xmin = num(body.xmin, -10), xmax = num(body.xmax, 10);
    const n = 200;
    const series = [];
    let ymin = Infinity, ymax = -Infinity;
    lines.forEach(function (ln, idx) {
      const f = fx(ln);
      const pts = [];
      for (let i = 0; i <= n; i += 1) {
        const x = xmin + (xmax - xmin) * i / n;
        const y = f(x);
        if (Number.isFinite(y)) {
          pts.push([x, y]);
          if (y < ymin) ymin = y;
          if (y > ymax) ymax = y;
        }
      }
      series.push({ name: ln, pts: pts, color: ["#c4a35a", "#6aa84f", "#6fa8dc", "#e06666"][idx % 4] });
    });
    if (!Number.isFinite(ymin) || !Number.isFinite(ymax) || ymin === ymax) { ymin = -1; ymax = 1; }
    const pad = 0.08 * (ymax - ymin || 1);
    ymin -= pad; ymax += pad;
    const w = 640, h = 400, m = 36;
    function X(x) { return m + (x - xmin) / (xmax - xmin) * (w - 2 * m); }
    function Y(y) { return h - m - (y - ymin) / (ymax - ymin) * (h - 2 * m); }
    let svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ' + w + " " + h + '" width="100%">';
    svg += '<rect width="' + w + '" height="' + h + '" fill="#11141a"/>';
    svg += '<line x1="' + X(xmin) + '" y1="' + Y(0) + '" x2="' + X(xmax) + '" y2="' + Y(0) + '" stroke="#3d4654"/>';
    svg += '<line x1="' + X(0) + '" y1="' + Y(ymin) + '" x2="' + X(0) + '" y2="' + Y(ymax) + '" stroke="#3d4654"/>';
    series.forEach(function (s) {
      let d = "";
      s.pts.forEach(function (p, i) { d += (i ? "L" : "M") + X(p[0]) + " " + Y(p[1]) + " "; });
      svg += '<path d="' + d + '" fill="none" stroke="' + s.color + '" stroke-width="2"/>';
    });
    svg += "</svg>";
    const text = series.map(function (s) { return s.name + "  n=" + s.pts.length; }).join("\n");
    return { ok: true, text: text || "0", svg: svg };
  }

  function seqfind(text, lang) {
    const T = lang === "fa"
      ? { need: "حداقل دو عدد بنویس، مثلاً ۲ ۵ ۸ ۱۱.", none: "با این جمله‌ها نوع مشخصی پیدا نشد.", type: "نوع", formula: "فرمول", next: "جمله‌های بعدی", given: "جمله‌های داده‌شده" }
      : { need: "Enter at least two numbers, e.g. 2 5 8 11.", none: "No standard sequence type matched these terms.", type: "Type", formula: "Formula", next: "Next terms", given: "Given terms" };
    const vals = faNum(text || "").replace(/،/g, " ").split(/[\s,;]+/).map(function (p) { return num(p, NaN); }).filter(function (n) { return Number.isFinite(n); });
    if (vals.length < 2) return { ok: true, text: T.need, hits: [], steps: [T.need] };
    function close(a, b) { return Math.abs(a - b) <= 1e-8 * Math.max(1, Math.abs(a), Math.abs(b)); }
    const hits = [];
    const k = vals.length, nnext = 5;
    const d0 = vals[1] - vals[0];
    let arith = true;
    for (let i = 2; i < k; i += 1) if (!close(vals[i] - vals[i - 1], d0)) arith = false;
    if (arith) {
      const nxt = [];
      for (let i = 0; i < nnext; i += 1) nxt.push(pretty(vals[0] + (k + i) * d0));
      hits.push({ name: lang === "fa" ? "حسابی" : "Arithmetic", formula: "a_n = a1 + (n-1)*d", params: "a1=" + pretty(vals[0]) + " d=" + pretty(d0), next: nxt.join(", ") });
    }
    if (Math.abs(vals[0]) > 1e-15) {
      const r0 = vals[1] / vals[0];
      let geo = true;
      for (let i = 2; i < k; i += 1) {
        if (Math.abs(vals[i - 1]) < 1e-15) { geo = false; break; }
        if (!close(vals[i] / vals[i - 1], r0)) geo = false;
      }
      if (geo && !arith) {
        const nxt = [];
        for (let i = 0; i < nnext; i += 1) nxt.push(pretty(vals[0] * Math.pow(r0, k + i)));
        hits.push({ name: lang === "fa" ? "هندسی" : "Geometric", formula: "a_n = a1 * r**(n-1)", params: "a1=" + pretty(vals[0]) + " r=" + pretty(r0), next: nxt.join(", ") });
      }
    }
    if (k >= 3) {
      let fib = true;
      for (let i = 2; i < k; i += 1) if (!close(vals[i], vals[i - 1] + vals[i - 2])) fib = false;
      if (fib) {
        const nxt = [];
        let a = vals[k - 2], b = vals[k - 1];
        for (let i = 0; i < nnext; i += 1) { const t = a + b; a = b; b = t; nxt.push(pretty(b)); }
        hits.push({ name: lang === "fa" ? "فیبوناچی" : "Fibonacci-like", formula: "a_n = a_(n-1)+a_(n-2)", params: "a1=" + pretty(vals[0]) + " a2=" + pretty(vals[1]), next: nxt.join(", ") });
      }
    }
    if (!hits.length) return { ok: true, text: T.none, hits: [], steps: [T.none] };
    const lines = [T.given + ": " + vals.map(pretty).join(", ")];
    hits.forEach(function (h) {
      lines.push(T.type + ": " + h.name);
      lines.push(T.formula + ": " + h.formula);
      if (h.params) lines.push(h.params);
      if (h.next) lines.push(T.next + ": " + h.next);
      lines.push("");
    });
    return { ok: true, text: lines.join("\n").trim(), hits: hits, steps: lines };
  }

  function matrix(op, a, b) {
    const A = parseMat(a);
    if (!A) return { ok: true, text: "0", steps: [] };
    op = String(op || "det").toLowerCase();
    if (op === "det") return { ok: true, text: pretty(det(A)), steps: ["det(A) = " + pretty(det(A))] };
    if (op === "t" || op === "trans") {
      const T = [];
      for (let c = 0; c < A[0].length; c += 1) {
        T[c] = [];
        for (let r = 0; r < A.length; r += 1) T[c][r] = A[r][c];
      }
      return { ok: true, text: fmtMat(T), steps: ["A^T"] };
    }
    if (op === "inv") {
      const I = inverse(A);
      return I ? { ok: true, text: fmtMat(I), steps: ["A inverse"] } : { ok: true, text: "0", steps: [] };
    }
    if (op === "rank") {
      const I = inverse(A);
      return { ok: true, text: String(Math.abs(det(A)) > 1e-10 ? A.length : A.length - 1), steps: [] };
    }
    if (op === "mul") {
      const B = parseMat(b);
      if (!B) return { ok: true, text: "0", steps: [] };
      const C = [];
      for (let i = 0; i < A.length; i += 1) {
        C[i] = [];
        for (let j = 0; j < B[0].length; j += 1) {
          let s = 0;
          for (let k = 0; k < B.length; k += 1) s += A[i][k] * B[k][j];
          C[i][j] = s;
        }
      }
      return { ok: true, text: fmtMat(C), steps: ["A B"] };
    }
    if (op === "solve") {
      const B = parseMat(b);
      if (!B) return { ok: true, text: "0", steps: [] };
      const bb = B.map(function (r) { return r[0]; });
      const x = linSolve(A, bb);
      return x ? { ok: true, text: x.map(pretty).join("; "), steps: ["Ax=b"] } : { ok: true, text: "0", steps: [] };
    }
    if (op === "eig" && A.length === 2) {
      const p = A[0][0], q = A[0][1], r = A[1][0], s = A[1][1];
      const tr = p + s, d = p * s - q * r, disc = tr * tr - 4 * d;
      if (disc >= 0) return { ok: true, text: pretty((tr + Math.sqrt(disc)) / 2) + ", " + pretty((tr - Math.sqrt(disc)) / 2), steps: [] };
      return { ok: true, text: pretty(tr / 2) + " ± " + pretty(Math.sqrt(-disc) / 2) + "i", steps: [] };
    }
    if (op === "rref") {
      const M = A.map(function (row) { return row.slice(); });
      const R = M.length, C = M[0].length;
      let row = 0;
      for (let c = 0; c < C && row < R; c += 1) {
        let piv = row;
        for (let i = row; i < R; i += 1) if (Math.abs(M[i][c]) > Math.abs(M[piv][c])) piv = i;
        if (Math.abs(M[piv][c]) < 1e-10) continue;
        const tmp = M[row]; M[row] = M[piv]; M[piv] = tmp;
        const div = M[row][c];
        for (let j = 0; j < C; j += 1) M[row][j] /= div;
        for (let i = 0; i < R; i += 1) if (i !== row) {
          const f = M[i][c];
          for (let j = 0; j < C; j += 1) M[i][j] -= f * M[row][j];
        }
        row += 1;
      }
      return { ok: true, text: fmtMat(M), steps: ["RREF"] };
    }
    return { ok: true, text: fmtMat(A), steps: [] };
  }

  function problem(text, unknown, mode, at) {
    const raw = faNum(text || "").trim();
    const u = (unknown || "x").trim() || "x";
    if (!raw) return { ok: true, text: "0", steps: [] };
    if ((mode || "solve").toLowerCase().indexOf("inv") === 0) {
      const m = parseMat(raw);
      if (m && m.length === m[0].length && m.length >= 2) {
        const I = inverse(m);
        return I ? { ok: true, text: fmtMat(I), steps: ["inverse matrix"] } : { ok: true, text: "0", steps: [] };
      }
    }
    const lines = raw.split(/\n|;/).map(function (s) { return s.trim(); }).filter(Boolean);
    if (lines.length >= 2 && lines.every(function (ln) { return ln.indexOf("=") >= 0; })) {
      return { ok: true, text: "0", steps: ["system needs two linear equations of two unknowns"] };
    }
    if (raw.indexOf("=") >= 0) {
      const parts = raw.split("=");
      const left = parts[0].trim(), right = parts.slice(1).join("=").trim();
      const item = { expr: left + " = " + right, variables: {} };
      item.variables[u] = { unit: "" };
      const f = window.ultraState && window.ultraState;
      if (window.ultraLocalEng && false) {}
      const fn = function (x) {
        const L = fx(left.replace(new RegExp("\\b" + u + "\\b", "g"), "(" + x + ")"));
        const R = fx(right.replace(new RegExp("\\b" + u + "\\b", "g"), "(" + x + ")"));
        return L(0) - R(0);
      };
      function evalSide(side, x) {
        const s = side.replace(new RegExp("\\b" + u + "\\b", "g"), "(" + x + ")");
        return fx(s)(0);
      }
      let best = NaN, bestAbs = Infinity;
      [1, 0, -1, 10, 0.5, -10, 2].forEach(function (g) {
        let x0 = g;
        for (let i = 0; i < 40; i += 1) {
          const y = evalSide(left, x0) - evalSide(right, x0);
          const h = Math.max(1e-7, Math.abs(x0) * 1e-6);
          const yp = ((evalSide(left, x0 + h) - evalSide(right, x0 + h)) - y) / h;
          if (!Number.isFinite(y) || !Number.isFinite(yp) || Math.abs(yp) < 1e-14) break;
          x0 -= y / yp;
        }
        const yb = evalSide(left, x0) - evalSide(right, x0);
        if (Number.isFinite(x0) && Number.isFinite(yb) && Math.abs(yb) < bestAbs) {
          bestAbs = Math.abs(yb); best = x0;
        }
      });
      if (Number.isFinite(best) && bestAbs < 1e-4) {
        return { ok: true, text: pretty(best), unknown: u, steps: [u + " = " + pretty(best)] };
      }
    }
    const v = fx(raw)(0);
    if (Number.isFinite(v)) return { ok: true, text: pretty(v), steps: [pretty(v)] };
    return { ok: true, text: "0", steps: [] };
  }

  function lookup(q, lang) {
    q = String(q || "").trim().toLowerCase();
    if (!q) return [];
    const pack = window.PACKED || {};
    const rows = pack.formulas || [];
    const out = [];
    for (let i = 0; i < rows.length && out.length < 8; i += 1) {
      const r = rows[i];
      const name = (r.name && (r.name[lang] || r.name.en)) || r.id;
      const blob = [r.id, r.expr, name].join(" ").toLowerCase();
      if (blob.indexOf(q) < 0) continue;
      const vars = Object.keys(r.variables || {});
      if (vars.length === 1 && r.expr.indexOf("=") >= 0) {
        const rhs = r.expr.split("=")[1];
        const n = Number(String(rhs).trim());
        if (Number.isFinite(n)) {
          out.push({ label: name, text: pretty(n), unit: (r.variables[vars[0]] && r.variables[vars[0]].unit) || "", insert: pretty(n) });
          continue;
        }
      }
      out.push({ label: name, text: r.expr, unit: "", insert: r.expr.split("=")[0].trim() });
    }
    const els = (pack.elements && pack.elements.elements) || [];
    els.forEach(function (el) {
      if (out.length >= 10) return;
      const name = (el.name && (el.name[lang] || el.name.en)) || el.symbol;
      const blob = [el.symbol, String(el.Z), name].join(" ").toLowerCase();
      if (blob.indexOf(q) >= 0) out.push({ label: el.symbol + " " + name, text: String(el.mass), unit: "u", insert: String(el.mass) });
    });
    return out;
  }

  function search(q, lang) {
    q = String(q || "").trim().toLowerCase();
    const hits = [];
    if (!q) return { hits: hits };
    const pack = window.PACKED || {};
    (pack.formulas || []).some(function (r) {
      const name = (r.name && (r.name[lang] || r.name.en)) || r.id;
      if ((name + " " + r.expr + " " + r.id).toLowerCase().indexOf(q) >= 0) {
        hits.push({ kind: "formula", id: r.id, title: name, go: "formulas" });
        return hits.length >= 8;
      }
      return false;
    });
    ((pack.algos && pack.algos.items) || []).some(function (r) {
      const name = (r.name && (r.name[lang] || r.name.en)) || r.id;
      if ((name + " " + r.id).toLowerCase().indexOf(q) >= 0) {
        hits.push({ kind: "algo", id: r.id, title: name, go: "algo" });
        return hits.length >= 12;
      }
      return false;
    });
    return { hits: hits };
  }

  const CIR_T = {
    en: {
      ask_a: "What is the first circuit?", ask_b: "What is the second circuit?",
      ask_conn: "How are those two circuits connected?",
      series: "Series", parallel: "Parallel", next: "Next", add: "Add another part", reset: "Start over", back: "Back",
      R: "resistor", C: "capacitor", L: "inductor",
      r_series: "Req = R1 + R2", r_par: "Req = R1 R2 / (R1 + R2)",
      c_series: "Ceq = C1 C2 / (C1 + C2)", c_par: "Ceq = C1 + C2",
      l_series: "Leq = L1 + L2", l_par: "Leq = L1 L2 / (L1 + L2)",
      need_val: "Type the value first.", need_kind: "Pick the type first.", bad_val: "That value was not read. Try 4.7k or 10u."
    },
    fa: {
      ask_a: "مدار اول چیست؟", ask_b: "مدار دوم چیست؟",
      ask_conn: "این دو مدار چطور به هم وصل شده‌اند؟",
      series: "سری", parallel: "موازی", next: "بعدی", add: "یک قطعه دیگر اضافه کن", reset: "از اول", back: "برگشت",
      R: "مقاومت", C: "خازن", L: "سلف",
      r_series: "Req = R1 + R2", r_par: "Req = R1 R2 / (R1 + R2)",
      c_series: "Ceq = C1 C2 / (C1 + C2)", c_par: "Ceq = C1 + C2",
      l_series: "Leq = L1 + L2", l_par: "Leq = L1 L2 / (L1 + L2)",
      need_val: "اول مقدار را بنویس.", need_kind: "اول نوع را انتخاب کن.", bad_val: "مقدار خوانده نشد. مثلاً ۴.۷k یا ۱۰u"
    }
  };
  function blankCir() {
    return { phase: "a", a: {}, b: {}, conn: "", freq: null, eq: {}, hist: [], picked: "", text: "", formula: "", steps: [] };
  }
  function copyCir(st) {
    const s = st && typeof st === "object" ? st : {};
    const o = blankCir();
    o.phase = s.phase || "a";
    o.a = Object.assign({}, s.a || {});
    o.b = Object.assign({}, s.b || {});
    o.conn = s.conn || "";
    o.freq = s.freq;
    o.eq = Object.assign({}, s.eq || {});
    o.hist = Array.isArray(s.hist) ? s.hist.slice() : [];
    o.picked = s.picked || "";
    o.text = s.text || "";
    o.formula = s.formula || "";
    o.steps = Array.isArray(s.steps) ? s.steps.slice() : [];
    return o;
  }
  function engOhm(v) {
    const ax = Math.abs(v);
    const pref = [[1e6, "M"], [1e3, "k"], [1, ""], [1e-3, "m"], [1e-6, "u"], [1e-9, "n"], [1e-12, "p"]];
    for (let i = 0; i < pref.length; i += 1) if (ax >= pref[i][0] * 0.999) return pretty(v / pref[i][0]) + " " + pref[i][1];
    return pretty(v);
  }
  function cirView(state, lang, note) {
    const p = CIR_T[lang] || CIR_T.en;
    const phase = state.phase || "a";
    let prompt = p.ask_a, choices = [{ id: "R", label: p.R }, { id: "C", label: p.C }, { id: "L", label: p.L }];
    let need_value = true, value_hint = "ohm  1k  4.7k";
    if (phase === "b") prompt = p.ask_b;
    if (phase === "conn") { prompt = p.ask_conn; choices = [{ id: "series", label: p.series }, { id: "parallel", label: p.parallel }]; need_value = false; value_hint = ""; }
    if (phase === "done") { prompt = (lang === "fa" ? "معادل = " : "Equivalent = ") + (state.text || "0"); choices = []; need_value = false; value_hint = ""; }
    const story = [];
    if (state.a && state.a.kind) story.push((lang === "fa" ? "مدار اول: " : "First: ") + p[state.a.kind] + " " + engOhm(state.a.val) + (state.a.kind === "R" ? "ohm" : state.a.kind === "C" ? "F" : "H"));
    if (state.b && state.b.kind && (phase === "conn" || phase === "done")) story.push((lang === "fa" ? "مدار دوم: " : "Second: ") + p[state.b.kind] + " " + engOhm(state.b.val));
    if (note) story.push(note);
    const actions = [];
    if (phase === "done") {
      actions.push({ id: "add", label: p.add });
      actions.push({ id: "reset", label: p.reset });
    } else if (phase !== "a") actions.push({ id: "back", label: p.back });
    return {
      ok: true, phase: phase, prompt: prompt, choices: choices, need_value: need_value, value_hint: value_hint,
      picked: state.picked || "", next_label: p.next, story: story, text: state.text || "", formula: state.formula || "",
      steps: state.steps || [], actions: actions, state: state
    };
  }
  function cirFinish(state, lang) {
    const p = CIR_T[lang] || CIR_T.en;
    const a = state.a || {}, b = state.b || {};
    const va = Number(a.val), vb = Number(b.val);
    const ka = a.kind, kb = b.kind, conn = state.conn;
    let eqv = 0, formula = "", unit = "ohm";
    if (ka === kb && ka === "R") {
      formula = conn === "parallel" ? p.r_par : p.r_series;
      eqv = conn === "parallel" ? (va * vb / (va + vb)) : (va + vb);
      unit = "ohm";
    } else if (ka === kb && ka === "C") {
      formula = conn === "parallel" ? p.c_par : p.c_series;
      eqv = conn === "parallel" ? (va + vb) : (va * vb / (va + vb));
      unit = "F";
    } else if (ka === kb && ka === "L") {
      formula = conn === "parallel" ? p.l_par : p.l_series;
      eqv = conn === "parallel" ? (va * vb / (va + vb)) : (va + vb);
      unit = "H";
    } else {
      state.phase = "done";
      state.text = "0";
      state.steps = [lang === "fa" ? "جنس‌ها فرق دارند. فرکانس لازم است." : "Different kinds. Frequency needed."];
      return cirView(state, lang);
    }
    const shown = engOhm(eqv) + unit;
    state.phase = "done";
    state.text = shown;
    state.formula = formula;
    state.eq = { kind: ka, val: eqv };
    state.steps = [formula, shown];
    return cirView(state, lang);
  }
  function circguide(body) {
    body = body || {};
    const lang = body.lang === "fa" ? "fa" : (body.lang === "fi" ? "en" : (body.lang || "en"));
    const p = CIR_T[lang] || CIR_T.en;
    let action = String(body.action || "start").toLowerCase();
    let state = copyCir(body.state);
    const kind = String(body.kind || body.choice || body.conn || "").toUpperCase();
    const value = body.value;
    if (action === "start" || action === "reset" || action === "") return cirView(blankCir(), lang);
    if (action === "back") {
      if (state.phase === "b") { state.phase = "a"; state.b = {}; }
      else if (state.phase === "conn") { state.phase = "b"; state.conn = ""; }
      else if (state.phase === "done") { state.phase = "conn"; }
      else state = blankCir();
      return cirView(state, lang);
    }
    if (action === "add") {
      if (!state.eq || state.eq.val == null) return cirView(blankCir(), lang);
      const nxt = blankCir();
      nxt.a = { kind: state.eq.kind, val: state.eq.val };
      nxt.phase = "b";
      nxt.hist = (state.hist || []).concat([(lang === "fa" ? "معادل تا اینجا: " : "Equivalent so far: ") + (state.text || "")]);
      return cirView(nxt, lang);
    }
    if (action === "pick" || action === "connect") {
      if (kind === "SERIES" || body.conn === "series" || body.kind === "series") {
        state.conn = "series";
        return cirFinish(state, lang);
      }
      if (kind === "PARALLEL" || body.conn === "parallel" || body.kind === "parallel") {
        state.conn = "parallel";
        return cirFinish(state, lang);
      }
      if (kind === "R" || kind === "C" || kind === "L") {
        state.picked = kind;
        const which = state.phase === "b" ? "b" : "a";
        const part = Object.assign({}, state[which] || {});
        part.kind = kind;
        state[which] = part;
        return cirView(state, lang);
      }
      return cirView(state, lang, p.need_kind);
    }
    if (action === "next" || action === "value" || action === "set") {
      if (state.phase === "conn") {
        const raw = String(body.conn || body.kind || value || "").toLowerCase();
        if (raw.indexOf("par") >= 0 || raw === "موازی") state.conn = "parallel";
        else if (raw.indexOf("ser") >= 0 || raw === "سری") state.conn = "series";
        else return cirView(state, lang, p.need_kind);
        return cirFinish(state, lang);
      }
      const which = state.phase === "b" ? "b" : "a";
      const part = Object.assign({}, state[which] || {});
      if (state.picked) part.kind = state.picked;
      const parsed = num(value, null);
      if (value != null && String(value).trim() !== "") {
        if (parsed == null) return cirView(state, lang, p.bad_val);
        part.val = Math.abs(parsed);
      }
      state[which] = part;
      if (!part.kind) return cirView(state, lang, p.need_kind);
      if (part.val == null) return cirView(state, lang, p.need_val);
      if (state.phase !== "b") { state.phase = "b"; state.picked = ""; return cirView(state, lang); }
      state.phase = "conn";
      state.picked = "";
      return cirView(state, lang);
    }
    return cirView(state, lang);
  }

  function system(eqs, unks) {
    eqs = eqs || [];
    unks = unks || ["x", "y"];
    if (eqs.length >= 2 && unks.length >= 2) {
      function coeffs(eq, names) {
        const parts = String(eq).split("=");
        const left = parts[0] || "0", right = parts[1] || "0";
        const expr = "(" + left + ")-(" + right + ")";
        const z = [];
        names.forEach(function (n, i) {
          const vals = names.map(function (_, j) { return i === j ? 1 : 0; });
          let s = expr;
          names.forEach(function (nm, j) { s = s.replace(new RegExp("\\b" + nm + "\\b", "g"), "(" + vals[j] + ")"); });
          z.push(fx(s)(0));
        });
        let s0 = expr;
        names.forEach(function (nm) { s0 = s0.replace(new RegExp("\\b" + nm + "\\b", "g"), "(0)"); });
        z.push(fx(s0)(0));
        return z;
      }
      const names = unks.slice(0, 2);
      const r1 = coeffs(eqs[0], names), r2 = coeffs(eqs[1], names);
      const A = [[r1[0], r1[1]], [r2[0], r2[1]]];
      const b = [-r1[2], -r2[2]];
      const x = linSolve(A, b);
      if (!x) return { ok: true, solutions: [], text: "0" };
      const sol = {};
      names.forEach(function (n, i) { sol[n] = pretty(x[i]); });
      return { ok: true, solutions: [sol], text: names.map(function (n) { return n + " = " + sol[n]; }).join("  ") };
    }
    return { ok: true, solutions: [], text: "0" };
  }

  function handle(path, query, body) {
    body = body || {};
    query = query || {};
    const lang = query.lang || body.lang || "en";
    if (path === "/api/poly") return polyWork(body.coeffs, body.x);
    if (path === "/api/numeric") return numeric(body.kind || "root", body);
    if (path === "/api/triangle") return triangle(body.values || {});
    if (path === "/api/stats") return stats(body.text || "");
    if (path === "/api/graph") return graph(body);
    if (path === "/api/seqfind") return seqfind(body.text || "", lang);
    if (path === "/api/matrix") return matrix(body.op, body.a, body.b);
    if (path === "/api/problem") return problem(body.text || "", body.unknown || "x", body.mode, body.at);
    if (path === "/api/circguide") return circguide(body);
    if (path === "/api/system") return system(body.equations, body.unknowns);
    if (path === "/api/lookup") return lookup(query.q || "", lang);
    if (path === "/api/search") return search(query.q || "", lang);
    if (path === "/api/latex") return { ok: true, text: body.text || "0", latex: body.exact || body.text || "0" };
    if (path === "/api/session") return body && Object.keys(body).length ? { ok: true } : {};
    return null;
  }

  window.ultraExtras = { handle: handle, seqfind: seqfind, triangle: triangle, circguide: circguide };
})();
