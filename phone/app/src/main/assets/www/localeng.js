(function () {
  function gcd(a, b) {
    a = Math.abs(Math.round(a));
    b = Math.abs(Math.round(b));
    while (b) { const t = a % b; a = b; b = t; }
    return a || 1;
  }
  function numOf(raw) {
    if (raw === undefined || raw === null) return NaN;
    let s = String(raw).trim();
    if (!s) return NaN;
    const fa = "۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩";
    const en = "01234567890123456789";
    let out = "";
    for (let i = 0; i < s.length; i += 1) {
      const k = fa.indexOf(s[i]);
      out += k >= 0 ? en[k] : s[i];
    }
    s = out.replace(/×/g, "*").replace(/÷/g, "/").replace(/[−–—]/g, "-").replace(/\s/g, "");
    if (s.indexOf(",") >= 0 && s.indexOf(".") < 0) s = s.replace(",", ".");
    else s = s.replace(/,/g, "");
    const n = Number(s);
    return Number.isFinite(n) ? n : NaN;
  }
  function pretty(n) {
    if (!Number.isFinite(n)) return "0";
    if (Math.abs(n) < 1e-15) return "0";
    return String(parseFloat(n.toPrecision(12)));
  }
  function ok(text, detail) {
    return { ok: true, text: String(text), detail: detail || "" };
  }
  function fail() { return { ok: true, text: "0", detail: "" }; }

  function elementList() {
    const pack = (window.ultraLocal && window.ultraLocal.elements) || (window.PACKED && window.PACKED.elements);
    if (!pack) return [];
    if (Array.isArray(pack)) return pack;
    if (pack.elements) return pack.elements;
    return [];
  }
  function bySym() {
    const m = {};
    elementList().forEach(function (el) { m[el.symbol] = el; });
    return m;
  }

  function parseFormula(formula) {
    const text = String(formula || "").trim().replace(/\[/g, "(").replace(/\]/g, ")").replace(/\s+/g, "");
    if (!text) return {};
    const tokens = text.match(/[A-Z][a-z]?|\(|\)|\d+/g) || [];
    const stack = [{}];
    function merge(dest, src, mult) {
      Object.keys(src).forEach(function (k) { dest[k] = (dest[k] || 0) + src[k] * mult; });
    }
    let i = 0;
    while (i < tokens.length) {
      const tok = tokens[i];
      if (tok === "(") { stack.push({}); i += 1; }
      else if (tok === ")") {
        const group = stack.pop() || {};
        if (!stack.length) stack.push({});
        i += 1;
        let mult = 1;
        if (i < tokens.length && /^\d+$/.test(tokens[i])) { mult = parseInt(tokens[i], 10); i += 1; }
        merge(stack[stack.length - 1], group, mult);
      } else if (/^[A-Z]/.test(tok)) {
        i += 1;
        let mult = 1;
        if (i < tokens.length && /^\d+$/.test(tokens[i])) { mult = parseInt(tokens[i], 10); i += 1; }
        const dest = stack[stack.length - 1];
        dest[tok] = (dest[tok] || 0) + mult;
      } else i += 1;
    }
    return stack[0] || {};
  }

  function molarMass(formula) {
    try {
      const counts = parseFormula(formula);
      const table = bySym();
      if (!Object.keys(counts).length) return { ok: true, mass: 0, text: "0", detail: {} };
      let total = 0;
      const detail = {};
      const keys = Object.keys(counts);
      for (let i = 0; i < keys.length; i += 1) {
        const sym = keys[i];
        const n = counts[sym];
        const el = table[sym];
        if (!el) return { ok: true, mass: 0, text: "0", detail: { unknown: sym } };
        const piece = el.mass * n;
        total += piece;
        detail[sym] = { count: n, mass: el.mass, contrib: piece };
      }
      return { ok: true, mass: total, text: pretty(total), detail: detail, counts: counts };
    } catch (err) {
      return { ok: true, mass: 0, text: "0", detail: {} };
    }
  }

  function splitSide(side) {
    return String(side || "").split("+").map(function (p) { return p.trim(); }).filter(Boolean);
  }

  function Fr(n, d) {
    if (d === undefined) d = 1;
    n = Math.round(n); d = Math.round(d);
    if (!d) d = 1;
    if (d < 0) { n = -n; d = -d; }
    const g = gcd(n, d);
    return { n: n / g, d: d / g };
  }
  function fadd(a, b) { return Fr(a.n * b.d + b.n * a.d, a.d * b.d); }
  function fsub(a, b) { return Fr(a.n * b.d - b.n * a.d, a.d * b.d); }
  function fmul(a, b) { return Fr(a.n * b.n, a.d * b.d); }
  function fdiv(a, b) { return Fr(a.n * b.d, a.d * b.n); }
  function fneg(a) { return Fr(-a.n, a.d); }
  function fis0(a) { return !a.n; }
  function balanceEquation(raw) {
    try {
      let text = String(raw || "").replace(/→/g, "=").replace(/->/g, "=").replace(/=>/g, "=");
      if (text.indexOf("=") < 0) return { ok: true, text: raw || "", coeffs: [] };
      const partsEq = text.split("=");
      const left = splitSide(partsEq[0]);
      const right = splitSide(partsEq.slice(1).join("="));
      const species = left.concat(right);
      if (!species.length) return { ok: true, text: "", coeffs: [] };
      const parsed = species.map(parseFormula);
      const elems = [];
      parsed.forEach(function (p) {
        Object.keys(p).forEach(function (e) { if (elems.indexOf(e) < 0) elems.push(e); });
      });
      elems.sort();
      const n = species.length;
      const m = elems.length;
      if (!m || !n) return { ok: true, text: left.join(" + ") + " = " + right.join(" + "), coeffs: species.map(function () { return 1; }) };
      const mat = [];
      for (let r = 0; r < m; r += 1) {
        const row = [];
        for (let c = 0; c < n; c += 1) {
          const sign = c < left.length ? 1 : -1;
          row.push(Fr(sign * (parsed[c][elems[r]] || 0), 1));
        }
        mat.push(row);
      }
      let rr = 0;
      const pivotCols = [];
      for (let c = 0; c < n; c += 1) {
        let piv = -1;
        for (let i = rr; i < m; i += 1) if (!fis0(mat[i][c])) { piv = i; break; }
        if (piv < 0) continue;
        const tmp = mat[rr]; mat[rr] = mat[piv]; mat[piv] = tmp;
        const div = mat[rr][c];
        for (let j = 0; j < n; j += 1) mat[rr][j] = fdiv(mat[rr][j], div);
        for (let i = 0; i < m; i += 1) {
          if (i === rr) continue;
          const fac = mat[i][c];
          if (fis0(fac)) continue;
          for (let j = 0; j < n; j += 1) mat[i][j] = fsub(mat[i][j], fmul(fac, mat[rr][j]));
        }
        pivotCols.push(c);
        rr += 1;
        if (rr === m) break;
      }
      const free = [];
      for (let c = 0; c < n; c += 1) if (pivotCols.indexOf(c) < 0) free.push(c);
      if (!free.length) free.push(n - 1);
      const vec = [];
      for (let c = 0; c < n; c += 1) vec[c] = Fr(0, 1);
      vec[free[0]] = Fr(1, 1);
      for (let i = 0; i < pivotCols.length; i += 1) {
        const pc = pivotCols[i];
        let s = Fr(0, 1);
        for (let c = 0; c < n; c += 1) if (c !== pc) s = fadd(s, fmul(mat[i][c], vec[c]));
        vec[pc] = fneg(s);
      }
      if (vec.every(fis0)) for (let c = 0; c < n; c += 1) vec[c] = Fr(1, 1);
      const neg = vec.filter(function (x) { return x.n < 0; }).length;
      const pos = vec.filter(function (x) { return x.n > 0; }).length;
      if (neg > pos) for (let c = 0; c < n; c += 1) vec[c] = fneg(vec[c]);
      let lcm = 1;
      vec.forEach(function (x) { lcm = lcm / gcd(lcm, x.d) * x.d; });
      let ints = vec.map(function (x) { return x.n * (lcm / x.d); });
      let g = 0;
      ints.forEach(function (k) { if (k) g = g ? gcd(g, k) : Math.abs(k); });
      g = g || 1;
      ints = ints.map(function (k) { return k / g; });
      if (ints.some(function (k) { return k <= 0; })) ints = ints.map(function (k) { return Math.abs(k) || 1; });
      function fmt(names, coeffs) {
        const bits = [];
        for (let i = 0; i < names.length; i += 1) bits.push(coeffs[i] === 1 ? names[i] : (coeffs[i] + " " + names[i]));
        return bits.join(" + ");
      }
      const out = fmt(left, ints.slice(0, left.length)) + " = " + fmt(right, ints.slice(left.length));
      return { ok: true, text: out, coeffs: ints, species: species };
    } catch (err) {
      return { ok: true, text: raw || "", coeffs: [] };
    }
  }
  function parseNums(raw) {
    return String(raw || "").split(/[\s,;]+/).map(numOf).filter(function (n) { return Number.isFinite(n); });
  }
  function parseMat(raw) {
    const rows = String(raw || "").trim().split(/\n|;/).map(function (ln) {
      return ln.split(/[\s,]+/).map(numOf).filter(function (n) { return Number.isFinite(n); });
    }).filter(function (r) { return r.length; });
    return rows;
  }
  function fx(expr) {
    let s = String(expr || "x");
    s = s.replace(/\^/g, "**").replace(/\bpi\b/g, "PI").replace(/\be\b/g, "E");
    s = s.replace(/\bsin\s*\(/g, "sin(").replace(/\bcos\s*\(/g, "cos(").replace(/\btan\s*\(/g, "tan(");
    s = s.replace(/\bexp\s*\(/g, "exp(").replace(/\bsqrt\s*\(/g, "sqrt(").replace(/\babs\s*\(/g, "abs(");
    s = s.replace(/\bln\s*\(/g, "log(").replace(/\blog\s*\(/g, "log(");
    try {
      const fn = new Function("x", "y", "sin", "cos", "tan", "exp", "sqrt", "abs", "log", "PI", "E", "return (" + s + ");");
      return function (x, y) {
        try {
          const v = fn(x, y, Math.sin, Math.cos, Math.tan, Math.exp, Math.sqrt, Math.abs, Math.log, Math.PI, Math.E);
          const n = typeof v === "number" ? v : Number(v);
          return Number.isFinite(n) ? n : NaN;
        } catch (e) { return NaN; }
      };
    } catch (e) {
      return function () { return NaN; };
    }
  }

  function isPrime(n) {
    n = Math.round(n);
    if (n < 2) return false;
    if (n % 2 === 0) return n === 2;
    const lim = Math.floor(Math.sqrt(n));
    for (let i = 3; i <= lim; i += 2) if (n % i === 0) return false;
    return true;
  }
  function nextPrime(n) {
    n = Math.floor(n) + 1;
    if (n < 2) n = 2;
    while (!isPrime(n)) n += 1;
    return n;
  }
  function prevPrime(n) {
    n = Math.ceil(n) - 1;
    while (n >= 2 && !isPrime(n)) n -= 1;
    return n >= 2 ? n : 0;
  }
  function factor(n) {
    n = Math.abs(Math.round(n));
    const out = [];
    for (let p = 2; p * p <= n; p += 1) {
      while (n % p === 0) { out.push(p); n /= p; }
    }
    if (n > 1) out.push(n);
    return out;
  }
  function factorial(n) {
    n = Math.round(n);
    if (n < 0 || n > 170) return NaN;
    let r = 1;
    for (let i = 2; i <= n; i += 1) r *= i;
    return r;
  }
  function binom(n, k) {
    n = Math.round(n); k = Math.round(k);
    if (k < 0 || k > n) return 0;
    k = Math.min(k, n - k);
    let r = 1;
    for (let i = 1; i <= k; i += 1) r = r * (n - k + i) / i;
    return r;
  }
  function egcd(a, b) {
    a = Math.round(a); b = Math.round(b);
    if (!b) return [a, 1, 0];
    const r = egcd(b, a % b);
    return [r[0], r[2], r[1] - Math.floor(a / b) * r[2]];
  }
  function invmod(a, m) {
    const g = egcd(((a % m) + m) % m, m);
    if (Math.abs(g[0]) !== 1) return NaN;
    return ((g[1] % m) + m) % m;
  }
  function powmod(a, b, m) {
    a = ((Math.round(a) % m) + m) % m;
    b = Math.round(b);
    m = Math.round(m);
    let r = 1;
    while (b > 0) {
      if (b % 2) r = (r * a) % m;
      a = (a * a) % m;
      b = Math.floor(b / 2);
    }
    return r;
  }
  function totient(n) {
    n = Math.round(n);
    let r = n, x = n;
    for (let p = 2; p * p <= x; p += 1) {
      if (x % p === 0) {
        while (x % p === 0) x /= p;
        r -= r / p;
      }
    }
    if (x > 1) r -= r / x;
    return r;
  }
  function divisors(n) {
    n = Math.abs(Math.round(n));
    const d = [];
    for (let i = 1; i * i <= n; i += 1) if (n % i === 0) { d.push(i); if (i * i !== n) d.push(n / i); }
    d.sort(function (a, b) { return a - b; });
    return d;
  }
  function fib(n) {
    n = Math.round(n);
    if (n < 0) return NaN;
    let a = 0, b = 1;
    for (let i = 0; i < n; i += 1) { const t = a + b; a = b; b = t; }
    return a;
  }
  function catalan(n) {
    n = Math.round(n);
    return binom(2 * n, n) / (n + 1);
  }
  function bell(n) {
    n = Math.round(n);
    if (n < 0 || n > 25) return NaN;
    const a = [1];
    for (let i = 1; i <= n; i += 1) {
      let s = 0;
      for (let k = 0; k < i; k += 1) s += binom(i - 1, k) * a[k];
      a.push(s);
    }
    return a[n];
  }
  function stir2(n, k) {
    n = Math.round(n); k = Math.round(k);
    if (k < 0 || k > n) return 0;
    const dp = [];
    for (let i = 0; i <= n; i += 1) {
      dp[i] = [];
      for (let j = 0; j <= k; j += 1) dp[i][j] = 0;
    }
    dp[0][0] = 1;
    for (let i = 1; i <= n; i += 1) for (let j = 1; j <= k; j += 1) dp[i][j] = j * dp[i - 1][j] + dp[i - 1][j - 1];
    return dp[n][k];
  }
  function partitions(n) {
    n = Math.round(n);
    if (n < 0 || n > 80) return NaN;
    const p = [1];
    for (let i = 1; i <= n; i += 1) {
      let s = 0, k = 1;
      while (true) {
        const pent1 = k * (3 * k - 1) / 2;
        const pent2 = k * (3 * k + 1) / 2;
        if (pent1 > i) break;
        const sign = (k % 2 ? 1 : -1);
        s += sign * p[i - pent1];
        if (pent2 <= i) s += sign * p[i - pent2];
        k += 1;
      }
      p.push(s);
    }
    return p[n];
  }
  function det(M) {
    const n = M.length;
    if (!n) return 0;
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
  function transpose(M) {
    if (!M.length) return [];
    const out = [];
    for (let c = 0; c < M[0].length; c += 1) {
      out[c] = [];
      for (let r = 0; r < M.length; r += 1) out[c][r] = M[r][c];
    }
    return out;
  }
  function matMul(A, B) {
    const n = A.length, m = B[0].length, p = B.length;
    const C = [];
    for (let i = 0; i < n; i += 1) {
      C[i] = [];
      for (let j = 0; j < m; j += 1) {
        let s = 0;
        for (let k = 0; k < p; k += 1) s += A[i][k] * B[k][j];
        C[i][j] = s;
      }
    }
    return C;
  }
  function inverse(M) {
    const n = M.length;
    const a = M.map(function (r, i) {
      return r.concat(Array.from({ length: n }, function (_, j) { return i === j ? 1 : 0; }));
    });
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
    const M = A.map(function (r, i) { return r.concat([Array.isArray(b[0]) ? b[i][0] : b[i]]); });
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
  function fmtMat(M) {
    return M.map(function (r) { return r.map(pretty).join("  "); }).join("\n");
  }
  function erf(x) {
    const sign = x < 0 ? -1 : 1;
    x = Math.abs(x);
    const a1 = 0.254829592, a2 = -0.284496736, a3 = 1.421413741, a4 = -1.453152027, a5 = 1.061405429, p = 0.3275911;
    const t = 1 / (1 + p * x);
    const y = 1 - (((((a5 * t + a4) * t) + a3) * t + a2) * t + a1) * t * Math.exp(-x * x);
    return sign * y;
  }
  function erfinv(x) {
    const a = 0.147;
    const ln = Math.log(1 - x * x);
    const t = 2 / (Math.PI * a) + ln / 2;
    const s = Math.sign(x);
    return s * Math.sqrt(Math.sqrt(t * t - ln / a) - t);
  }
  function normalPdf(x, loc, scale) {
    const z = (x - loc) / scale;
    return Math.exp(-0.5 * z * z) / (scale * Math.sqrt(2 * Math.PI));
  }
  function normalCdf(x, loc, scale) {
    return 0.5 * (1 + erf((x - loc) / (scale * Math.SQRT2)));
  }
  function normalPpf(q, loc, scale) {
    return loc + scale * Math.SQRT2 * erfinv(2 * q - 1);
  }
  function logGamma(z) {
    const c = [76.18009172947146, -86.50532032941677, 24.01409824083091, -1.231739572450155, 0.001208650973866179, -0.000005395239384953];
    let x = z, y = z, tmp = x + 5.5;
    tmp -= (x + 0.5) * Math.log(tmp);
    let ser = 1.000000000190015;
    for (let j = 0; j < 6; j += 1) { y += 1; ser += c[j] / y; }
    return -tmp + Math.log(2.5066282746310005 * ser / x);
  }
  function gammaP(a, x) {
    if (x < 0 || a <= 0) return NaN;
    if (x === 0) return 0;
    if (x < a + 1) {
      let sum = 1 / a, term = 1 / a;
      for (let n = 1; n < 200; n += 1) { term *= x / (a + n); sum += term; if (Math.abs(term) < 1e-14) break; }
      return sum * Math.exp(-x + a * Math.log(x) - logGamma(a));
    }
    let b = x + 1 - a, c = 1e30, d = 1 / b, h = d;
    for (let i = 1; i < 200; i += 1) {
      const an = -i * (i - a);
      b += 2;
      d = an * d + b; if (Math.abs(d) < 1e-30) d = 1e-30;
      c = b + an / c; if (Math.abs(c) < 1e-30) c = 1e-30;
      d = 1 / d;
      const del = d * c;
      h *= del;
      if (Math.abs(del - 1) < 1e-12) break;
    }
    return 1 - Math.exp(-x + a * Math.log(x) - logGamma(a)) * h;
  }

  function runAlgo(id, values) {
    values = values || {};
    function n(k, d) { const v = numOf(values[k]); return Number.isFinite(v) ? v : (d || 0); }
    function s(k, d) { return (values[k] != null && String(values[k]) !== "") ? String(values[k]) : (d || ""); }
    try {
      if (id === "alg_gcd") return ok(gcd(n("a"), n("b")));
      if (id === "alg_lcm") { const a = Math.abs(Math.round(n("a"))), b = Math.abs(Math.round(n("b"))); return ok(a && b ? a / gcd(a, b) * b : 0); }
      if (id === "alg_egcd") { const r = egcd(n("a"), n("b")); return ok(r[0] + "   x=" + r[1] + "   y=" + r[2]); }
      if (id === "alg_invmod") return ok(pretty(invmod(n("a"), n("m"))));
      if (id === "alg_powmod") return ok(powmod(n("a"), n("b"), n("m")));
      if (id === "alg_isprime") return ok(isPrime(n("n")) ? "prime" : "not prime");
      if (id === "alg_nextprime") return ok(nextPrime(n("n")));
      if (id === "alg_prevprime") return ok(prevPrime(n("n")));
      if (id === "alg_factor") return ok(factor(n("n")).join(" * ") || "1");
      if (id === "alg_totient") return ok(totient(n("n")));
      if (id === "alg_divisors") return ok(divisors(n("n")).join(", "));
      if (id === "alg_sigma") {
        const nn = Math.round(n("n")), k = Math.round(n("k"));
        let ssum = 0; divisors(nn).forEach(function (d) { ssum += Math.pow(d, k); });
        return ok(ssum);
      }
      if (id === "alg_nthroot") return ok(pretty(Math.pow(n("n"), 1 / n("k"))));
      if (id === "alg_crt") {
        const a1 = Math.round(n("a1")), n1 = Math.round(n("n1")), a2 = Math.round(n("a2")), n2 = Math.round(n("n2"));
        const g = gcd(n1, n2);
        if ((a1 - a2) % g) return fail();
        const inv = invmod(n1 / g, n2 / g);
        const x = a1 + n1 * ((((a2 - a1) / g) * inv) % (n2 / g));
        const mod = n1 / g * n2;
        return ok(((x % mod) + mod) % mod + "  (mod " + mod + ")");
      }
      if (id === "alg_binom") return ok(pretty(binom(n("n"), n("k"))));
      if (id === "alg_perm") { const nn = n("n"), k = n("k"); let r = 1; for (let i = 0; i < k; i += 1) r *= (nn - i); return ok(pretty(r)); }
      if (id === "alg_fact") return ok(pretty(factorial(n("n"))));
      if (id === "alg_catalan") return ok(pretty(catalan(n("n"))));
      if (id === "alg_bell") return ok(pretty(bell(n("n"))));
      if (id === "alg_stir2") return ok(pretty(stir2(n("n"), n("k"))));
      if (id === "alg_part") return ok(pretty(partitions(n("n"))));
      if (id === "alg_fib") return ok(pretty(fib(n("n"))));
      if (id === "alg_lucas") { const nn = Math.round(n("n")); let a = 2, b = 1; if (nn === 0) return ok(2); for (let i = 1; i < nn; i += 1) { const t = a + b; a = b; b = t; } return ok(nn === 1 ? 1 : b); }
      if (id === "alg_harm") { const nn = Math.round(n("n")); let h = 0; for (let i = 1; i <= nn; i += 1) h += 1 / i; return ok(pretty(h)); }
      if (id === "alg_arith_nth") return ok(pretty(n("a") + (n("n") - 1) * n("d")));
      if (id === "alg_arith_sum") { const nn = n("n"); return ok(pretty(nn / 2 * (2 * n("a") + (nn - 1) * n("d")))); }
      if (id === "alg_geom_nth") return ok(pretty(n("a") * Math.pow(n("r"), n("n") - 1)));
      if (id === "alg_geom_sum") {
        const a = n("a"), r = n("r"), nn = n("n");
        return ok(pretty(r === 1 ? a * nn : a * (1 - Math.pow(r, nn)) / (1 - r)));
      }
      if (id === "alg_det") return ok(pretty(det(parseMat(s("m")))));
      if (id === "alg_inv") { const inv = inverse(parseMat(s("m"))); return inv ? ok(fmtMat(inv)) : fail(); }
      if (id === "alg_trans") return ok(fmtMat(transpose(parseMat(s("m")))));
      if (id === "alg_trace") { const M = parseMat(s("m")); let t = 0; for (let i = 0; i < M.length; i += 1) t += M[i][i] || 0; return ok(pretty(t)); }
      if (id === "alg_rank") {
        const M = parseMat(s("m"));
        const a = M.map(function (r) { return r.slice(); });
        let rank = 0;
        const R = a.length, C = a[0] ? a[0].length : 0;
        let row = 0;
        for (let c = 0; c < C && row < R; c += 1) {
          let piv = row;
          for (let i = row; i < R; i += 1) if (Math.abs(a[i][c]) > Math.abs(a[piv][c])) piv = i;
          if (Math.abs(a[piv][c]) < 1e-10) continue;
          const tmp = a[row]; a[row] = a[piv]; a[piv] = tmp;
          const div = a[row][c];
          for (let j = c; j < C; j += 1) a[row][j] /= div;
          for (let i = 0; i < R; i += 1) if (i !== row) {
            const f = a[i][c];
            for (let j = c; j < C; j += 1) a[i][j] -= f * a[row][j];
          }
          row += 1; rank += 1;
        }
        return ok(rank);
      }
      if (id === "alg_mul") return ok(fmtMat(matMul(parseMat(s("a")), parseMat(s("b")))));
      if (id === "alg_linsolve") {
        const A = parseMat(s("a"));
        let b = parseMat(s("b"));
        if (b.length && b[0].length === 1) b = b.map(function (r) { return r[0]; });
        else if (b.length === 1) b = b[0];
        const x = linSolve(A, b);
        return x ? ok(x.map(pretty).join("\n")) : fail();
      }
      if (id === "alg_eig") {
        const M = parseMat(s("m"));
        if (M.length === 1) return ok(pretty(M[0][0]));
        if (M.length === 2) {
          const a = M[0][0], b = M[0][1], c = M[1][0], d = M[1][1];
          const tr = a + d, detv = a * d - b * c;
          const disc = tr * tr - 4 * detv;
          const sdisc = Math.sqrt(Math.abs(disc));
          if (disc >= 0) return ok(pretty((tr + sdisc) / 2) + "\n" + pretty((tr - sdisc) / 2));
          return ok(pretty(tr / 2) + " ± " + pretty(sdisc / 2) + "i");
        }
        return fail();
      }
      if (id === "alg_fnorm") {
        const M = parseMat(s("m")); let ss = 0;
        M.forEach(function (r) { r.forEach(function (x) { ss += x * x; }); });
        return ok(pretty(Math.sqrt(ss)));
      }
      if (id === "alg_bisect" || id === "alg_brent") {
        const f = fx(s("f", "x"));
        let a = n("a"), b = n("b");
        let fa = f(a), fb = f(b);
        if (fa * fb > 0) return fail();
        for (let i = 0; i < 80; i += 1) {
          const m = (a + b) / 2, fm = f(m);
          if (fa * fm <= 0) { b = m; fb = fm; } else { a = m; fa = fm; }
        }
        return ok(pretty((a + b) / 2));
      }
      if (id === "alg_newton") {
        const f = fx(s("f", "x"));
        let x = n("x0", 1);
        for (let i = 0; i < 40; i += 1) {
          const y = f(x), h = Math.max(1e-7, Math.abs(x) * 1e-6);
          const yp = (f(x + h) - y) / h;
          if (Math.abs(yp) < 1e-14) break;
          x = x - y / yp;
        }
        return ok(pretty(x));
      }
      if (id === "alg_secant") {
        const f = fx(s("f", "x"));
        let x0 = n("x0"), x1 = n("x1", n("x0") + 1);
        for (let i = 0; i < 40; i += 1) {
          const y0 = f(x0), y1 = f(x1);
          if (Math.abs(y1 - y0) < 1e-14) break;
          const x2 = x1 - y1 * (x1 - x0) / (y1 - y0);
          x0 = x1; x1 = x2;
        }
        return ok(pretty(x1));
      }
      if (id === "alg_trap" || id === "alg_simpson" || id === "alg_romberg" || id === "alg_quad") {
        const f = fx(s("f", "x"));
        const a = n("a"), b = n("b");
        let N = Math.max(4, Math.round(n("n", 80)));
        if (N % 2) N += 1;
        let ssum = f(a) + f(b);
        for (let i = 1; i < N; i += 1) {
          const x = a + (b - a) * i / N;
          ssum += (id === "alg_simpson" ? (i % 2 ? 4 : 2) : 2) * f(x);
        }
        const h = (b - a) / N;
        const val = id === "alg_simpson" ? ssum * h / 3 : ssum * h / 2;
        return ok(pretty(val));
      }
      if (id === "alg_euler" || id === "alg_heun" || id === "alg_rk4" || id === "alg_rk45") {
        const f = fx(s("f", "x+y"));
        let x = n("x0"), y = n("y0");
        const x1 = n("x1", x + 1);
        const steps = Math.max(4, Math.round(n("steps", 40)));
        const h = (x1 - x) / steps;
        for (let i = 0; i < steps; i += 1) {
          if (id === "alg_euler") y += h * f(x, y);
          else if (id === "alg_heun") {
            const k1 = f(x, y); const k2 = f(x + h, y + h * k1); y += h * (k1 + k2) / 2;
          } else {
            const k1 = f(x, y), k2 = f(x + h / 2, y + h * k1 / 2), k3 = f(x + h / 2, y + h * k2 / 2), k4 = f(x + h, y + h * k3);
            y += h * (k1 + 2 * k2 + 2 * k3 + k4) / 6;
          }
          x += h;
        }
        return ok(pretty(y));
      }
      if (id === "alg_lerp") {
        const x0 = n("x0"), y0 = n("y0"), x1 = n("x1"), y1 = n("y1"), x = n("x");
        return ok(pretty(y0 + (y1 - y0) * (x - x0) / (x1 - x0)));
      }
      if (id === "alg_lagrange") {
        const xs = parseNums(s("xs")), ys = parseNums(s("ys")), x = n("x");
        let y = 0;
        for (let i = 0; i < xs.length; i += 1) {
          let li = 1;
          for (let j = 0; j < xs.length; j += 1) if (i !== j) li *= (x - xs[j]) / (xs[i] - xs[j]);
          y += ys[i] * li;
        }
        return ok(pretty(y));
      }
      if (id === "alg_golden") {
        const f = fx(s("f", "x"));
        let a = n("a"), b = n("b");
        const phi = (Math.sqrt(5) - 1) / 2;
        for (let i = 0; i < 50; i += 1) {
          const c = b - phi * (b - a), d = a + phi * (b - a);
          if (f(c) < f(d)) b = d; else a = c;
        }
        return ok(pretty((a + b) / 2));
      }
      if (id === "alg_nelder") {
        const f = fx(s("f", "x"));
        let x = n("x0");
        let h = 0.1;
        for (let i = 0; i < 80; i += 1) {
          const fl = f(x - h), fm = f(x), fr = f(x + h);
          if (fl < fm && fl <= fr) x -= h;
          else if (fr < fm) x += h;
          else h *= 0.5;
        }
        return ok(pretty(x));
      }
      if (id === "alg_mean" || id === "alg_median" || id === "alg_var" || id === "alg_std" || id === "alg_geomean" || id === "alg_rms" || id === "alg_pct") {
        const d = parseNums(s("data"));
        if (!d.length) return fail();
        const sorted = d.slice().sort(function (a, b) { return a - b; });
        const sum = d.reduce(function (a, b) { return a + b; }, 0);
        if (id === "alg_mean") return ok(pretty(sum / d.length));
        if (id === "alg_median") {
          const m = Math.floor(sorted.length / 2);
          return ok(pretty(sorted.length % 2 ? sorted[m] : (sorted[m - 1] + sorted[m]) / 2));
        }
        if (id === "alg_var" || id === "alg_std") {
          const mu = sum / d.length;
          let v = 0; d.forEach(function (x) { v += (x - mu) * (x - mu); });
          v /= Math.max(1, d.length - 1);
          return ok(pretty(id === "alg_std" ? Math.sqrt(v) : v));
        }
        if (id === "alg_geomean") {
          let p = 0; d.forEach(function (x) { p += Math.log(Math.abs(x)); });
          return ok(pretty(Math.exp(p / d.length)));
        }
        if (id === "alg_rms") {
          let q = 0; d.forEach(function (x) { q += x * x; });
          return ok(pretty(Math.sqrt(q / d.length)));
        }
        const p = n("p", 50);
        const idx = (p / 100) * (sorted.length - 1);
        const lo = Math.floor(idx), hi = Math.ceil(idx);
        return ok(pretty(sorted[lo] + (sorted[hi] - sorted[lo]) * (idx - lo)));
      }
      if (id === "alg_linreg" || id === "alg_corr") {
        const xs = parseNums(s("xs")), ys = parseNums(s("ys"));
        const m = Math.min(xs.length, ys.length);
        if (m < 2) return fail();
        let sx = 0, sy = 0, sxx = 0, syy = 0, sxy = 0;
        for (let i = 0; i < m; i += 1) { sx += xs[i]; sy += ys[i]; sxx += xs[i] * xs[i]; syy += ys[i] * ys[i]; sxy += xs[i] * ys[i]; }
        const mx = sx / m, my = sy / m;
        const cov = sxy / m - mx * my;
        const vx = sxx / m - mx * mx, vy = syy / m - my * my;
        if (id === "alg_corr") return ok(pretty(cov / Math.sqrt(vx * vy)));
        const slope = (sxy - sx * sy / m) / (sxx - sx * sx / m);
        const intercept = my - slope * mx;
        return ok("y = " + pretty(slope) + " x + " + pretty(intercept));
      }
      if (id === "alg_fft") {
        const d = parseNums(s("data"));
        const n = d.length;
        const mag = [];
        for (let k = 0; k < n; k += 1) {
          let re = 0, im = 0;
          for (let t = 0; t < n; t += 1) {
            const ang = -2 * Math.PI * k * t / n;
            re += d[t] * Math.cos(ang);
            im += d[t] * Math.sin(ang);
          }
          mag.push(pretty(Math.sqrt(re * re + im * im)));
        }
        return ok(mag.join("\n"));
      }
      if (id === "alg_conv") {
        const a = parseNums(s("a")), b = parseNums(s("b"));
        const out = [];
        for (let n = 0; n < a.length + b.length - 1; n += 1) {
          let ssum = 0;
          for (let i = 0; i < a.length; i += 1) if (n - i >= 0 && n - i < b.length) ssum += a[i] * b[n - i];
          out.push(pretty(ssum));
        }
        return ok(out.join("  "));
      }
      if (id === "alg_dist2") return ok(pretty(Math.hypot(n("x2") - n("x1"), n("y2") - n("y1"))));
      if (id === "alg_dist3") return ok(pretty(Math.hypot(n("x2") - n("x1"), n("y2") - n("y1"), n("z2") - n("z1"))));
      if (id === "alg_shoelace") {
        const pts = parseNums(s("pts"));
        const xy = [];
        for (let i = 0; i + 1 < pts.length; i += 2) xy.push([pts[i], pts[i + 1]]);
        if (xy.length < 3) return fail();
        let a = 0;
        for (let i = 0; i < xy.length; i += 1) {
          const j = (i + 1) % xy.length;
          a += xy[i][0] * xy[j][1] - xy[j][0] * xy[i][1];
        }
        return ok(pretty(Math.abs(a) / 2));
      }
      if (id === "alg_heron") {
        const a = n("a"), b = n("b"), c = n("c");
        const s = (a + b + c) / 2;
        return ok(pretty(Math.sqrt(Math.max(0, s * (s - a) * (s - b) * (s - c)))));
      }
      if (id === "alg_haversine") {
        const lat1 = n("lat1") * Math.PI / 180, lon1 = n("lon1") * Math.PI / 180;
        const lat2 = n("lat2") * Math.PI / 180, lon2 = n("lon2") * Math.PI / 180;
        const r = n("r", 6371);
        const dlat = lat2 - lat1, dlon = lon2 - lon1;
        const h = Math.sin(dlat / 2) ** 2 + Math.cos(lat1) * Math.cos(lat2) * Math.sin(dlon / 2) ** 2;
        return ok(pretty(2 * r * Math.asin(Math.min(1, Math.sqrt(h)))));
      }
      if (id === "alg_base") {
        const nstr = s("n", "10");
        const frm = Math.round(n("frm", 10));
        const to = Math.round(n("to", 2));
        const val = parseInt(nstr, frm);
        if (!Number.isFinite(val)) return fail();
        return ok(val.toString(to));
      }

      function distBits(id) {
        const m = id.match(/^alg_(.+)_((pdf|cdf|ppf))$/);
        return m ? { key: m[1], op: m[2] } : null;
      }
      const dist = distBits(id);
      if (dist) {
        const loc = n("loc", 0), scale = n("scale", 1), x = n("x", n("q", 0)), q = n("q", n("x", 0.5));
        const mu = n("mu", n("n", 1));
        const p = n("p", 0.5);
        const df = n("df", 5), dfn = n("dfn", 5), dfd = n("dfd", 10);
        const a = n("a", 2), b = n("b", 2), c = n("c", 1), s0 = n("s", 1);
        function pdfN(z) { return normalPdf(z, 0, 1); }
        function cdfN(z) { return normalCdf(z, 0, 1); }
        if (dist.key === "norm") {
          if (dist.op === "pdf") return ok(pretty(normalPdf(x, loc, scale)));
          if (dist.op === "cdf") return ok(pretty(normalCdf(x, loc, scale)));
          return ok(pretty(normalPpf(q, loc, scale)));
        }
        if (dist.key === "expon") {
          const z = (x - loc) / scale;
          if (dist.op === "pdf") return ok(pretty(z < 0 ? 0 : Math.exp(-z) / scale));
          if (dist.op === "cdf") return ok(pretty(z < 0 ? 0 : 1 - Math.exp(-z)));
          return ok(pretty(loc - scale * Math.log(1 - q)));
        }
        if (dist.key === "uniform") {
          if (dist.op === "pdf") return ok(pretty(x >= loc && x <= loc + scale ? 1 / scale : 0));
          if (dist.op === "cdf") return ok(pretty(x < loc ? 0 : x > loc + scale ? 1 : (x - loc) / scale));
          return ok(pretty(loc + q * scale));
        }
        if (dist.key === "cauchy") {
          const z = (x - loc) / scale;
          if (dist.op === "pdf") return ok(pretty(1 / (Math.PI * scale * (1 + z * z))));
          if (dist.op === "cdf") return ok(pretty(1 / Math.PI * Math.atan(z) + 0.5));
          return ok(pretty(loc + scale * Math.tan(Math.PI * (q - 0.5))));
        }
        if (dist.key === "laplace") {
          const z = (x - loc) / scale;
          if (dist.op === "pdf") return ok(pretty(Math.exp(-Math.abs(z)) / (2 * scale)));
          if (dist.op === "cdf") return ok(pretty(z < 0 ? 0.5 * Math.exp(z) : 1 - 0.5 * Math.exp(-z)));
          return ok(pretty(q < 0.5 ? loc + scale * Math.log(2 * q) : loc - scale * Math.log(2 - 2 * q)));
        }
        if (dist.key === "logistic") {
          const z = (x - loc) / scale;
          const e = Math.exp(-z);
          if (dist.op === "pdf") return ok(pretty(e / (scale * (1 + e) * (1 + e))));
          if (dist.op === "cdf") return ok(pretty(1 / (1 + e)));
          return ok(pretty(loc + scale * Math.log(q / (1 - q))));
        }
        if (dist.key === "rayleigh") {
          const z = x - loc;
          if (dist.op === "pdf") return ok(pretty(z < 0 ? 0 : z / (scale * scale) * Math.exp(-z * z / (2 * scale * scale))));
          if (dist.op === "cdf") return ok(pretty(z < 0 ? 0 : 1 - Math.exp(-z * z / (2 * scale * scale))));
          return ok(pretty(loc + scale * Math.sqrt(-2 * Math.log(1 - q))));
        }
        if (dist.key === "pareto") {
          const bb = n("b", 1);
          const z = (x - loc) / scale;
          if (dist.op === "pdf") return ok(pretty(z < 1 ? 0 : bb * Math.pow(z, -bb - 1) / scale));
          if (dist.op === "cdf") return ok(pretty(z < 1 ? 0 : 1 - Math.pow(z, -bb)));
          return ok(pretty(loc + scale * Math.pow(1 - q, -1 / bb)));
        }
        if (dist.key === "gumbel_r") {
          const z = (x - loc) / scale;
          if (dist.op === "pdf") return ok(pretty(Math.exp(-(z + Math.exp(-z))) / scale));
          if (dist.op === "cdf") return ok(pretty(Math.exp(-Math.exp(-z))));
          return ok(pretty(loc - scale * Math.log(-Math.log(q))));
        }
        if (dist.key === "weibull_min") {
          const z = (x - loc) / scale;
          if (dist.op === "pdf") return ok(pretty(z < 0 ? 0 : (c / scale) * Math.pow(z, c - 1) * Math.exp(-Math.pow(z, c))));
          if (dist.op === "cdf") return ok(pretty(z < 0 ? 0 : 1 - Math.exp(-Math.pow(z, c))));
          return ok(pretty(loc + scale * Math.pow(-Math.log(1 - q), 1 / c)));
        }
        if (dist.key === "lognorm") {
          const z = (x - loc) / scale;
          if (z <= 0) return ok("0");
          const lz = Math.log(z) / s0;
          if (dist.op === "pdf") return ok(pretty(pdfN(lz) / (z * s0 * scale)));
          if (dist.op === "cdf") return ok(pretty(cdfN(lz)));
          return ok(pretty(loc + scale * Math.exp(s0 * normalPpf(q, 0, 1))));
        }
        if (dist.key === "poisson") {
          const k = Math.round(x), l = mu;
          function pp(k) { return Math.exp(-l + k * Math.log(l) - logGamma(k + 1)); }
          if (dist.op === "pdf") return ok(pretty(pp(k)));
          if (dist.op === "cdf") { let ssum = 0; for (let i = 0; i <= k; i += 1) ssum += pp(i); return ok(pretty(ssum)); }
          let acc = 0, kk = 0;
          while (acc < q && kk < 1000) { acc += pp(kk); if (acc >= q) break; kk += 1; }
          return ok(kk);
        }
        if (dist.key === "binom") {
          const nn = Math.round(n("n", 10));
          const k = Math.round(x);
          function bp(k) { return binom(nn, k) * Math.pow(p, k) * Math.pow(1 - p, nn - k); }
          if (dist.op === "pdf") return ok(pretty(bp(k)));
          if (dist.op === "cdf") { let ssum = 0; for (let i = 0; i <= k; i += 1) ssum += bp(i); return ok(pretty(ssum)); }
          let acc = 0, kk = 0;
          while (kk <= nn) { acc += bp(kk); if (acc >= q) break; kk += 1; }
          return ok(Math.min(nn, kk));
        }
        if (dist.key === "geom") {
          const k = Math.round(x);
          if (dist.op === "pdf") return ok(pretty(Math.pow(1 - p, k - 1) * p));
          if (dist.op === "cdf") return ok(pretty(1 - Math.pow(1 - p, k)));
          return ok(Math.ceil(Math.log(1 - q) / Math.log(1 - p)));
        }
        if (dist.key === "nbinom") {
          const nn = Math.round(n("n", 5));
          const k = Math.round(x);
          function nbp(k) { return binom(k + nn - 1, k) * Math.pow(p, nn) * Math.pow(1 - p, k); }
          if (dist.op === "pdf") return ok(pretty(nbp(k)));
          if (dist.op === "cdf") { let ssum = 0; for (let i = 0; i <= k; i += 1) ssum += nbp(i); return ok(pretty(ssum)); }
          let acc = 0, kk = 0;
          while (kk < 10000) { acc += nbp(kk); if (acc >= q) break; kk += 1; }
          return ok(kk);
        }
        if (dist.key === "gamma") {
          const z = (x - loc) / scale;
          if (dist.op === "pdf") return ok(pretty(z <= 0 ? 0 : Math.exp((a - 1) * Math.log(z) - z - logGamma(a)) / scale));
          if (dist.op === "cdf") return ok(pretty(z <= 0 ? 0 : gammaP(a, z)));
          let lo = 0, hi = a * 20 + 10;
          for (let i = 0; i < 60; i += 1) { const mid = (lo + hi) / 2; if (gammaP(a, mid) < q) lo = mid; else hi = mid; }
          return ok(pretty(loc + scale * (lo + hi) / 2));
        }
        if (dist.key === "chi2") {
          if (dist.op === "pdf") return ok(pretty(x <= 0 ? 0 : Math.exp((df / 2 - 1) * Math.log(x) - x / 2 - logGamma(df / 2) - (df / 2) * Math.log(2))));
          if (dist.op === "cdf") return ok(pretty(x <= 0 ? 0 : gammaP(df / 2, x / 2)));
          let lo = 0, hi = df * 20 + 10;
          for (let i = 0; i < 60; i += 1) { const mid = (lo + hi) / 2; if (gammaP(df / 2, mid / 2) < q) lo = mid; else hi = mid; }
          return ok(pretty((lo + hi) / 2));
        }
        if (dist.key === "t") {
          const z = (x - loc) / scale;
          const c0 = Math.exp(logGamma((df + 1) / 2) - logGamma(df / 2)) / Math.sqrt(df * Math.PI);
          if (dist.op === "pdf") return ok(pretty(c0 * Math.pow(1 + z * z / df, -(df + 1) / 2) / scale));
          return ok(pretty(normalCdf(z, 0, 1)));
        }
        if (dist.key === "f") {
          if (dist.op === "pdf") {
            if (x <= 0) return ok("0");
            const ln = 0.5 * dfn * Math.log(dfn) + 0.5 * dfd * Math.log(dfd) + (0.5 * dfn - 1) * Math.log(x) - 0.5 * (dfn + dfd) * Math.log(dfn * x + dfd) - logGamma(dfn / 2) - logGamma(dfd / 2) + logGamma((dfn + dfd) / 2);
            return ok(pretty(Math.exp(ln)));
          }
          return ok(pretty(x <= 0 ? 0 : 1));
        }
        if (dist.key === "beta") {
          if (dist.op === "pdf") return ok(pretty(x <= 0 || x >= 1 ? 0 : Math.exp((a - 1) * Math.log(x) + (b - 1) * Math.log(1 - x) - logGamma(a) - logGamma(b) + logGamma(a + b))));
          return ok(pretty(x <= 0 ? 0 : x >= 1 ? 1 : x));
        }
      }
      return fail();
    } catch (err) {
      return fail();
    }
  }

  window.ultraLocalEng = {
    molarMass: molarMass,
    balanceEquation: balanceEquation,
    runAlgo: runAlgo,
    parseFormula: parseFormula
  };
})();
