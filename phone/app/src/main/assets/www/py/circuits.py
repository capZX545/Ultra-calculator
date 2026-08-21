"""Circuit reader and solver for the web app. Independent copy."""

from __future__ import annotations

import math
import re
import unicodedata

_DIGIT = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")

_SUF = {
    "t": 1e12, "g": 1e9, "meg": 1e6, "k": 1e3,
    "m": 1e-3, "u": 1e-6, "µ": 1e-6, "n": 1e-9, "p": 1e-12, "f": 1e-15,
}


def _num(raw: str, default=None):
    if raw is None:
        return default
    text = unicodedata.normalize("NFKC", str(raw)).strip().translate(_DIGIT)
    if not text or text in {"?", "x", "unknown"}:
        return None
    text = text.replace(" ", "").replace("ω", "").replace("ohm", "").replace("Ω", "")
    text = text.replace("×", "*")
    m = re.fullmatch(r"([+\-]?[0-9]*\.?[0-9]+(?:[eE][+\-]?[0-9]+)?)([a-zA-Zµ]*)", text)
    if not m:
        try:
            return float(text)
        except Exception:
            return default
    val = float(m.group(1))
    suf = (m.group(2) or "").lower()
    if suf in {"a", "v", "w", "hz", "s", "h", "f"}:
        suf = ""
    if suf.endswith(("ohm", "hz", "f", "h", "s", "v", "a", "w")) and len(suf) > 1:
        suf = suf[:-1] if suf[-1] in "fhsvaw" else suf
    if suf == "meg":
        return val * 1e6
    if suf in _SUF:
        return val * _SUF[suf]
    if suf == "M":
        return val * 1e6
    return val


def _pretty(x, unit: str = "", eng: bool = False) -> str:
    try:
        if isinstance(x, complex):
            if abs(x.imag) < 1e-12:
                return _pretty(x.real, unit, eng)
            sign = "+" if x.imag >= 0 else "-"
            return f"{_pretty(x.real, '', eng)} {sign} j{_pretty(abs(x.imag), '', eng)}" + (f" {unit}" if unit else "")
        v = float(x)
    except Exception:
        return str(x)
    if not math.isfinite(v):
        return "undefined"
    if abs(v) < 1e-18:
        return "0" + (f" {unit}" if unit else "")
    ax = abs(v)
    prefixes = [(1e12, "T"), (1e9, "G"), (1e6, "M"), (1e3, "k"), (1, ""), (1e-3, "m"), (1e-6, "u"), (1e-9, "n"), (1e-12, "p")]
    pref = ""
    shown = v
    if eng or unit:
        for scale, name in prefixes:
            if ax >= scale * 0.999:
                shown = v / scale
                pref = name
                break
        else:
            shown = v / 1e-12
            pref = "p"
    text = f"{shown:.8g}"
    return f"{text} {pref}{unit}".strip()


def _ge(A, b):
    n = len(b)
    M = [[complex(A[i][j]) for j in range(n)] + [complex(b[i])] for i in range(n)]
    for col in range(n):
        piv = max(range(col, n), key=lambda r: abs(M[r][col]))
        M[col], M[piv] = M[piv], M[col]
        if abs(M[col][col]) < 1e-18:
            return None
        div = M[col][col]
        for j in range(col, n + 1):
            M[col][j] /= div
        for r in range(n):
            if r == col:
                continue
            f = M[r][col]
            if f == 0:
                continue
            for j in range(col, n + 1):
                M[r][j] -= f * M[col][j]
    return [M[i][n] for i in range(n)]


def _fail(lang: str) -> dict:
    msg = {
        "en": "Could not solve the circuit. Showing 0.",
        "fa": "مدار حل نشد. ۰.",
        "fi": "Piiria ei voitu ratkaista. 0.",
    }
    return {"ok": True, "text": "0", "detail": "", "steps": [msg.get(lang) or msg["en"]]}


def _steps(lang: str, kind: str, **kw) -> list[str]:
    packs = {
        "en": {
            "read": "Circuit: {raw}",
            "dc": "DC operating point (node 0 is ground).",
            "ac": "AC analysis at {f} Hz.",
            "nodes": "Node voltages: {text}",
            "curr": "Currents: {text}",
            "series": "Series resistance {vals} = {text}.",
            "par": "Parallel resistance {vals} = {text}.",
            "ohm": "Ohm: {text}",
            "div": "Voltage divider: {text}",
            "rc": "RC: {text}",
            "th": "Thevenin between {a} and {b}: {text}",
            "inv": "Unknown {name} = {text}",
            "kind": "{what}",
        },
        "fa": {
            "read": "مدار: {raw}",
            "dc": "نقطه کار DC (گره ۰ زمین است).",
            "ac": "تحلیل AC در {f} هرتز.",
            "nodes": "ولتاژ گره‌ها: {text}",
            "curr": "جریان‌ها: {text}",
            "series": "مقاومت سری {vals} = {text}.",
            "par": "مقاومت موازی {vals} = {text}.",
            "ohm": "اهم: {text}",
            "div": "مقسم ولتاژ: {text}",
            "rc": "RC: {text}",
            "th": "تونن بین {a} و {b}: {text}",
            "inv": "مجهول {name} = {text}",
            "kind": "{what}",
        },
        "fi": {
            "read": "Piiri: {raw}",
            "dc": "DC-tyopiste (solmu 0 on maa).",
            "ac": "AC-analyysi taajuudella {f} Hz.",
            "nodes": "Solmujannitteet: {text}",
            "curr": "Virrat: {text}",
            "series": "Sarjaresistanssi {vals} = {text}.",
            "par": "Rinnakkaisresistanssi {vals} = {text}.",
            "ohm": "Ohm: {text}",
            "div": "Jannitejakaja: {text}",
            "rc": "RC: {text}",
            "th": "Thevenin {a}–{b}: {text}",
            "inv": "Tuntematon {name} = {text}",
            "kind": "{what}",
        },
    }
    pack = packs.get(lang) or packs["en"]
    key = kind if kind in pack else "kind"
    try:
        return [pack[key].format(**kw)]
    except Exception:
        return [str(kw.get("text") or "0")]


def _is_gnd(name: str) -> bool:
    n = str(name).strip().lower()
    return n in {"0", "gnd", "ground", "g", "earth"}


class _Net:
    def __init__(self):
        self.elems = []
        self.freq = 0.0
        self.find = []
        self.thev = None
        self.eq = None
        self.tran = None

    def add(self, kind, name, n1, n2, val, extra=None):
        self.elems.append({"k": kind, "name": name, "n1": n1, "n2": n2, "val": val, "extra": extra or {}})


def _parse_net(text: str) -> _Net:
    net = _Net()
    counts = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("*") or line.startswith("#"):
            continue
        if line.startswith("."):
            parts = line[1:].split()
            if not parts:
                continue
            cmd = parts[0].lower()
            if cmd in {"ac", "freq", "f"} and len(parts) >= 2:
                net.freq = _num(parts[1], 0.0) or 0.0
            elif cmd in {"op", "dc"}:
                net.freq = 0.0
            elif cmd in {"find", "print"}:
                net.find.extend(parts[1:])
            elif cmd in {"thevenin", "th"} and len(parts) >= 3:
                net.thev = (parts[1], parts[2])
            elif cmd in {"eq", "want"}:
                net.eq = " ".join(parts[1:])
            elif cmd in {"tran", "transient"} and len(parts) >= 3:
                net.tran = (_num(parts[1], 1e-6) or 1e-6, _num(parts[2], 1e-3) or 1e-3)
            continue
        parts = line.replace(",", " ").split()
        if len(parts) < 3:
            continue
        head = parts[0]
        kind = head[0].upper()
        allowed = "RCLVIEFGHDQM"
        if kind not in allowed or (len(head) > 1 and not head[1].isalnum() and head[1] not in "?!_"):
            if head.upper() in set(allowed):
                kind = head.upper()
            else:
                continue
        counts[kind] = counts.get(kind, 0) + 1
        name = head if len(head) > 1 else f"{kind}{counts[kind]}"
        extra = {}
        if kind in "EG" and len(parts) >= 6:
            n1, n2 = parts[1], parts[2]
            extra = {"nc1": parts[3], "nc2": parts[4]}
            val = parts[5]
            net.add(kind, name, n1, n2, val, extra)
            continue
        if kind in "FH" and len(parts) >= 5:
            n1, n2 = parts[1], parts[2]
            extra = {"vname": parts[3]}
            val = parts[4]
            net.add(kind, name, n1, n2, val, extra)
            continue
        if kind == "D" and len(parts) >= 3:
            n1, n2 = parts[1], parts[2]
            val = parts[3] if len(parts) > 3 else "1e-14"
            if len(parts) > 4:
                extra["n"] = parts[4]
            net.add(kind, name, n1, n2, val, extra)
            continue
        if kind == "Q" and len(parts) >= 4:
            nc, nb, ne = parts[1], parts[2], parts[3]
            extra = {"n3": ne, "model": "npn", "beta": "100"}
            rest = [p.lower() for p in parts[4:]]
            for p in rest:
                if p in {"npn", "pnp"}:
                    extra["model"] = p
                elif p.startswith("beta") or p[0].isdigit() or p[0] in "?":
                    if "beta=" in p:
                        extra["beta"] = p.split("=", 1)[1]
                    elif extra.get("beta") == "100" and _num(p) is not None:
                        extra["beta"] = p
            val = extra.get("beta") or "100"
            net.add(kind, name, nc, nb, val, extra)
            continue
        if kind == "M" and len(parts) >= 4:
            nd, ng, ns = parts[1], parts[2], parts[3]
            extra = {"n3": ns, "model": "nmos", "kp": "2e-4", "vt": "0.7"}
            rest = parts[4:]
            for p in rest:
                pl = p.lower()
                if pl in {"nmos", "pmos"}:
                    extra["model"] = pl
                elif pl.startswith("kp="):
                    extra["kp"] = p.split("=", 1)[1]
                elif pl.startswith("vt="):
                    extra["vt"] = p.split("=", 1)[1]
                elif _num(p) is not None and extra["kp"] == "2e-4":
                    extra["kp"] = p
            net.add(kind, name, nd, ng, extra.get("kp"), extra)
            continue
        if len(parts) < 4:
            continue
        n1, n2, val = parts[1], parts[2], parts[3]
        extra = {"raw": parts[4]} if len(parts) > 4 else {}
        net.add(kind, name, n1, n2, val, extra)
    return net


def _nodes(net: _Net):
    names = []
    for e in net.elems:
        for n in (e["n1"], e["n2"]):
            if not _is_gnd(n) and n not in names:
                names.append(n)
    return names


def _idx(names, n):
    if _is_gnd(n):
        return None
    try:
        return names.index(n)
    except Exception:
        return None


def _vsrc_list(net: _Net):
    return [e for e in net.elems if e["k"] in {"V", "E", "H"}]


def _solve_mna(net: _Net, freq: float, subst: dict | None = None, vprev=None, iprev=None, h=None, vnl=None):
    names = _nodes(net)
    vsources = _vsrc_list(net)
    n_n = len(names)
    n_v = len(vsources)
    n = n_n + n_v
    if n == 0:
        return None, names, vsources
    A = [[0j] * n for _ in range(n)]
    b = [0j] * n
    w = 2 * math.pi * float(freq or 0.0)
    vprev = vprev or {}
    iprev = iprev or {}
    vnl = vnl or {}

    def stamp_g(i, j, g):
        if i is not None:
            A[i][i] += g
        if j is not None:
            A[j][j] += g
        if i is not None and j is not None:
            A[i][j] -= g
            A[j][i] -= g

    def vn_guess(nm):
        if _is_gnd(nm):
            return 0.0
        return float(vnl.get(nm, 0.0).real if isinstance(vnl.get(nm, 0.0), complex) else vnl.get(nm, 0.0))

    vindex = {e["name"]: k for k, e in enumerate(vsources)}

    for e in net.elems:
        i = _idx(names, e["n1"])
        j = _idx(names, e["n2"])
        raw = subst.get(e["name"], e["val"]) if subst else e["val"]
        extra = e.get("extra") if isinstance(e.get("extra"), dict) else {}
        if e["k"] == "R":
            r = _num(raw)
            if r is None or abs(r) < 1e-18:
                continue
            stamp_g(i, j, 1.0 / r)
        elif e["k"] == "C":
            c = _num(raw) or 0.0
            if h and h > 0:
                geq = c / h
                stamp_g(i, j, geq)
                vcap = vprev.get(e["name"], 0.0)
                if i is not None:
                    b[i] += geq * vcap
                if j is not None:
                    b[j] -= geq * vcap
            elif freq and w:
                stamp_g(i, j, 1j * w * c)
        elif e["k"] == "L":
            L = _num(raw) or 0.0
            if h and h > 0 and abs(L) > 1e-18:
                geq = h / L
                stamp_g(i, j, geq)
                il = iprev.get(e["name"], 0.0)
                if i is not None:
                    b[i] -= il
                if j is not None:
                    b[j] += il
            elif freq and w and abs(L) > 1e-18:
                stamp_g(i, j, 1.0 / (1j * w * L))
            else:
                stamp_g(i, j, 1e9)
        elif e["k"] == "I":
            cur = _num(raw) or 0.0
            if i is not None:
                b[i] -= cur
            if j is not None:
                b[j] += cur
        elif e["k"] == "G":
            gm = _num(raw) or 0.0
            c1 = _idx(names, extra.get("nc1"))
            c2 = _idx(names, extra.get("nc2"))
            if i is not None:
                if c1 is not None:
                    A[i][c1] += gm
                if c2 is not None:
                    A[i][c2] -= gm
            if j is not None:
                if c1 is not None:
                    A[j][c1] -= gm
                if c2 is not None:
                    A[j][c2] += gm
        elif e["k"] == "F":
            gain = _num(raw) or 0.0
            ctrl = extra.get("vname")
            pk = vindex.get(ctrl)
            if pk is None:
                continue
            p = n_n + pk
            if i is not None:
                A[i][p] += gain
            if j is not None:
                A[j][p] -= gain
        elif e["k"] == "D":
            Is = abs(_num(raw) or 1e-14) or 1e-14
            niss = _num(extra.get("n"), 1.0) or 1.0
            Vt = 0.026 * niss
            vd = vn_guess(e["n1"]) - vn_guess(e["n2"])
            vd = max(-1.5, min(0.9, vd))
            ex = math.exp(vd / Vt)
            Id = Is * (ex - 1.0)
            Geq = Is / Vt * ex
            Ieq = Id - Geq * vd
            stamp_g(i, j, Geq)
            if i is not None:
                b[i] -= Ieq
            if j is not None:
                b[j] += Ieq
        elif e["k"] == "Q":
            beta = abs(_num(e["val"]) or 100.0) or 100.0
            Is = 1e-14
            model = (extra.get("model") or "npn").lower()
            nc, nb, ne = e["n1"], e["n2"], extra.get("n3") or "0"
            ic, ib, ie = _idx(names, nc), _idx(names, nb), _idx(names, ne)
            vbe = vn_guess(nb) - vn_guess(ne)
            if model == "pnp":
                vbe = -vbe
            vbe = max(-1.5, min(0.9, vbe))
            Vt = 0.026
            ex = math.exp(vbe / Vt)
            Ic = Is * (ex - 1.0)
            gm = Is / Vt * ex
            gpi = gm / beta
            Ib = Ic / beta
            Ieq_c = Ic - gm * vbe
            Ieq_b = Ib - gpi * vbe
            sign = 1.0 if model != "pnp" else -1.0
            stamp_g(ib, ie, gpi)
            if ic is not None:
                if ib is not None:
                    A[ic][ib] += gm * sign
                if ie is not None:
                    A[ic][ie] -= gm * sign
                b[ic] -= Ieq_c * sign
            if ib is not None:
                b[ib] -= Ieq_b * sign
            if ie is not None:
                b[ie] += (Ieq_c + Ieq_b) * sign
        elif e["k"] == "M":
            Kp = abs(_num(extra.get("kp") or e["val"]) or 2e-4) or 2e-4
            Vt0 = _num(extra.get("vt"), 0.7) or 0.7
            model = (extra.get("model") or "nmos").lower()
            nd, ng, ns = e["n1"], e["n2"], extra.get("n3") or "0"
            idn, ign, isn = _idx(names, nd), _idx(names, ng), _idx(names, ns)
            vgs = vn_guess(ng) - vn_guess(ns)
            vds = vn_guess(nd) - vn_guess(ns)
            if model == "pmos":
                vgs, vds = -vgs, -vds
            Id = 0.0
            gm = 0.0
            gds = 0.0
            if vgs > Vt0:
                von = vgs - Vt0
                if vds < von:
                    Id = Kp * (von * vds - 0.5 * vds * vds)
                    gm = Kp * vds
                    gds = Kp * (von - vds)
                else:
                    Id = 0.5 * Kp * von * von
                    gm = Kp * von
                    gds = 0.0
            Ieq = Id - gm * vgs - gds * vds
            sign = 1.0 if model != "pmos" else -1.0
            stamp_g(idn, isn, gds)
            if idn is not None:
                if ign is not None:
                    A[idn][ign] += gm * sign
                if isn is not None:
                    A[idn][isn] -= gm * sign
                b[idn] -= Ieq * sign
            if isn is not None:
                if ign is not None:
                    A[isn][ign] -= gm * sign
                if isn is not None:
                    A[isn][isn] += gm * sign
                b[isn] += Ieq * sign
    for k, e in enumerate(vsources):
        i = _idx(names, e["n1"])
        j = _idx(names, e["n2"])
        p = n_n + k
        extra = e.get("extra") if isinstance(e.get("extra"), dict) else {}
        if i is not None:
            A[i][p] += 1
            A[p][i] += 1
        if j is not None:
            A[j][p] -= 1
            A[p][j] -= 1
        raw = subst.get(e["name"], e["val"]) if subst else e["val"]
        if e["k"] == "V":
            b[p] += _num(raw) or 0.0
        elif e["k"] == "E":
            gain = _num(raw) or 0.0
            c1 = _idx(names, extra.get("nc1"))
            c2 = _idx(names, extra.get("nc2"))
            if c1 is not None:
                A[p][c1] -= gain
            if c2 is not None:
                A[p][c2] += gain
        elif e["k"] == "H":
            r = _num(raw) or 0.0
            ctrl = extra.get("vname")
            pk = vindex.get(ctrl)
            if pk is not None:
                A[p][n_n + pk] -= r
    x = _ge(A, b)
    return x, names, vsources


def _currents(net, names, vsources, x, freq):
    if x is None:
        return []
    w = 2 * math.pi * float(freq or 0.0)
    out = []
    vmap = {names[i]: x[i] for i in range(len(names))}
    vmap_g = 0j

    def vn(n):
        if _is_gnd(n):
            return vmap_g
        return vmap.get(n, 0j)

    for e in net.elems:
        va, vb = vn(e["n1"]), vn(e["n2"])
        if e["k"] == "R":
            r = _num(e["val"])
            if r is None or abs(r) < 1e-18:
                continue
            out.append((e["name"], (va - vb) / r))
        elif e["k"] == "C" and freq and w:
            c = _num(e["val"]) or 0.0
            out.append((e["name"], (va - vb) * 1j * w * c))
        elif e["k"] == "L":
            L = _num(e["val"]) or 0.0
            if freq and w and abs(L) > 1e-18:
                out.append((e["name"], (va - vb) / (1j * w * L)))
        elif e["k"] == "I":
            out.append((e["name"], _num(e["val"]) or 0.0))
        elif e["k"] == "V":
            try:
                k = vsources.index(e)
                out.append((e["name"], x[len(names) + k]))
            except Exception:
                pass
    return out


def _format_solution(net, x, names, vsources, freq, lang, eng):
    if x is None:
        return _fail(lang)
    nodes = []
    for i, n in enumerate(names):
        nodes.append(f"V({n})={_pretty(x[i], 'V', eng)}")
    curs = _currents(net, names, vsources, x, freq)
    clines = [f"I({nm})={_pretty(iv, 'A', eng)}" for nm, iv in curs]
    shown = "; ".join(nodes) if nodes else "0"
    extra = "; ".join(clines)
    steps = _steps(lang, "read", raw="") + _steps(lang, "ac" if freq else "dc", f=_pretty(freq, "Hz", eng) if freq else "")
    steps += _steps(lang, "nodes", text=shown)
    if extra:
        steps += _steps(lang, "curr", text=extra)
        shown = shown + " | " + extra
    return {"ok": True, "text": shown, "detail": extra, "nodes": nodes, "currents": clines, "steps": [s for s in steps if s]}


def _ohm_style(text: str, lang: str, eng: bool) -> dict | None:
    kv = {}
    for m in re.finditer(r"\b([VIRCvlrcLtauTf]+)\s*=\s*([^\s,;]+)", text):
        kv[m.group(1).upper()] = m.group(2)
    if not kv:
        return None
    V, I, R = _num(kv.get("V")), _num(kv.get("I")), _num(kv.get("R"))
    C, L = _num(kv.get("C")), _num(kv.get("L"))
    t = _num(kv.get("T") or kv.get("TAU"))
    f = _num(kv.get("F"))
    bits = []
    if V is not None and I is not None and R is None:
        R = V / I if I else None
        bits.append(f"R={_pretty(R, 'ohm', eng)}")
    if V is not None and R is not None and I is None:
        I = V / R if R else None
        bits.append(f"I={_pretty(I, 'A', eng)}")
    if I is not None and R is not None and V is None:
        V = I * R
        bits.append(f"V={_pretty(V, 'V', eng)}")
    if V is not None and I is not None and R is not None:
        bits.append(f"P={_pretty(V * I, 'W', eng)}")
    if R is not None and C is not None:
        tau = R * C
        bits.append(f"tau={_pretty(tau, 's', eng)}")
        bits.append(f"fc={_pretty(1.0 / (2 * math.pi * tau), 'Hz', eng)}" if tau else "")
        if t is not None and V is not None:
            bits.append(f"Vc_charge={_pretty(V * (1 - math.exp(-t / tau)), 'V', eng)}")
            bits.append(f"Vc_discharge={_pretty(V * math.exp(-t / tau), 'V', eng)}")
    if R is not None and L is not None:
        bits.append(f"tau={_pretty(L / R, 's', eng)}" if R else "")
        bits.append(f"fc={_pretty(R / (2 * math.pi * L), 'Hz', eng)}" if L else "")
    bits = [b for b in bits if b]
    if not bits:
        return None
    shown = "; ".join(bits)
    return {"ok": True, "text": shown, "detail": "", "steps": _steps(lang, "ohm", text=shown)}


def _list_vals(text: str):
    vals = []
    for p in re.split(r"[\s,;]+", text):
        if not p or "=" in p:
            continue
        if re.match(r"^[+\-]?[0-9]", p):
            v = _num(p)
            if v is not None:
                vals.append(v)
    return vals


def _shortcuts(text: str, lang: str, eng: bool) -> dict | None:
    low = text.strip()
    first = (low.split() or [""])[0].lower().translate(_DIGIT)
    rest = low[len(first):].strip()
    ohm = _ohm_style(text, lang, eng)
    if first in {"ohm", "ohms", "اهم"}:
        return ohm or _fail(lang)
    if first in {"series", "seri", "سری"}:
        vals = _list_vals(rest)
        if not vals:
            return ohm
        s = sum(vals)
        shown = _pretty(s, "ohm", eng)
        return {"ok": True, "text": shown, "detail": "", "steps": _steps(lang, "series", vals=", ".join(_pretty(v, "ohm", eng) for v in vals), text=shown)}
    if first in {"parallel", "par", "موازی"}:
        vals = _list_vals(rest)
        if not vals:
            return ohm
        acc = 0.0
        for v in vals:
            if abs(v) < 1e-18:
                continue
            acc += 1.0 / v
        s = 1.0 / acc if acc else 0.0
        shown = _pretty(s, "ohm", eng)
        return {"ok": True, "text": shown, "detail": "", "steps": _steps(lang, "par", vals=", ".join(_pretty(v, "ohm", eng) for v in vals), text=shown)}
    if first in {"divider", "div", "مقسم"}:
        kv = {}
        for m in re.finditer(r"\b([A-Za-z0-9]+)\s*=\s*([^\s,;]+)", rest):
            kv[m.group(1).lower()] = m.group(2)
        nums = _list_vals(rest)
        Vin = _num(kv.get("vin") or kv.get("v")) if kv else (nums[0] if nums else None)
        R1 = _num(kv.get("r1")) if kv else (nums[1] if len(nums) > 1 else None)
        R2 = _num(kv.get("r2")) if kv else (nums[2] if len(nums) > 2 else None)
        if Vin is None and nums:
            Vin, R1, R2 = (nums + [None, None, None])[:3]
        if None in (Vin, R1, R2) or (R1 + R2) == 0:
            return ohm
        Vout = Vin * R2 / (R1 + R2)
        I = Vin / (R1 + R2)
        shown = f"Vout={_pretty(Vout, 'V', eng)}; I={_pretty(I, 'A', eng)}"
        return {"ok": True, "text": shown, "detail": "", "steps": _steps(lang, "div", text=shown)}
    if first in {"rc", "rl"}:
        return ohm
    if ohm:
        return ohm
    return None


def _thevenin(net: _Net, a: str, b: str, freq: float, lang: str, eng: bool) -> dict:
    probe = f"_TH_{a}_{b}"
    net2 = _Net()
    net2.elems = list(net.elems)
    net2.freq = freq
    x, names, vs = _solve_mna(net2, freq)
    if x is None:
        return _fail(lang)
    vmap = {names[i]: x[i] for i in range(len(names))}
    va = 0j if _is_gnd(a) else vmap.get(a, 0j)
    vb = 0j if _is_gnd(b) else vmap.get(b, 0j)
    voc = va - vb
    net3 = _Net()
    net3.elems = list(net.elems)
    net3.add("V", probe, a, b, "0")
    x3, names3, vs3 = _solve_mna(net3, freq)
    isc = 0j
    if x3 is not None:
        try:
            k = vs3.index(next(e for e in vs3 if e["name"] == probe))
            isc = x3[len(names3) + k]
        except Exception:
            isc = 0j
    rth = voc / isc if abs(isc) > 1e-18 else float("inf")
    shown = f"Voc={_pretty(voc, 'V', eng)}; Isc={_pretty(isc, 'A', eng)}; Rth={_pretty(rth, 'ohm', eng)}"
    return {"ok": True, "text": shown, "detail": "", "steps": _steps(lang, "th", a=a, b=b, text=shown)}


def _inverse(net: _Net, freq: float, lang: str, eng: bool) -> dict:
    unknown = None
    for e in net.elems:
        if e["val"] in {"?", "x", "X"} or str(e["val"]).endswith("?"):
            unknown = e
            break
    if unknown is None:
        return _fail(lang)
    eq = net.eq or ""
    m = re.search(r"V\(\s*([^)]+)\s*\)\s*=\s*([^\s]+)", eq, re.I)
    if not m:
        m = re.search(r"I\(\s*([^)]+)\s*\)\s*=\s*([^\s]+)", eq, re.I)
        want_i = True if m else False
    else:
        want_i = False
    if not m:
        return _fail(lang)
    target_name = m.group(1).strip()
    target_val = _num(m.group(2))
    if target_val is None:
        return _fail(lang)

    def err(trial: float) -> float:
        x, names, vs = _solve_mna(net, freq, subst={unknown["name"]: str(trial)})
        if x is None:
            return 1e99
        if want_i:
            curs = _currents(net, names, vs, x, freq)
            for nm, iv in curs:
                if nm.lower() == target_name.lower():
                    return abs(complex(iv) - target_val)
            return 1e99
        vmap = {names[i]: x[i] for i in range(len(names))}
        v = 0j if _is_gnd(target_name) else vmap.get(target_name, vmap.get(target_name.upper(), 0j))
        return abs(complex(v) - target_val)

    best, best_e = 1.0, err(1.0)
    for exp in range(-6, 10):
        for mul in (1.0, 1.5, 2.2, 3.3, 4.7, 6.8):
            trial = mul * (10 ** exp)
            e = err(trial)
            if e < best_e:
                best, best_e = trial, e
    lo = max(best / 8.0, 1e-12)
    hi = best * 8.0
    for _ in range(55):
        m1 = math.exp((2 * math.log(lo) + math.log(hi)) / 3)
        m2 = math.exp((math.log(lo) + 2 * math.log(hi)) / 3)
        if err(m1) < err(m2):
            hi = m2
        else:
            lo = m1
    best = math.sqrt(lo * hi)
    unit = "ohm" if unknown["k"] == "R" else ("F" if unknown["k"] == "C" else ("H" if unknown["k"] == "L" else ""))
    shown = _pretty(best, unit, eng)
    return {"ok": True, "text": shown, "detail": "", "steps": _steps(lang, "inv", name=unknown["name"], text=shown)}


def _has_nl(net: _Net) -> bool:
    return any(e["k"] in {"D", "Q", "M"} for e in net.elems)


def _solve_nl(net: _Net, freq: float):
    names = _nodes(net)
    vnl = {n: 0.0 for n in names}
    x = None
    vs = _vsrc_list(net)
    for _ in range(50):
        x, names, vs = _solve_mna(net, freq, vnl=vnl)
        if x is None:
            return None, names, vs
        mx = 0.0
        nxt = {}
        for i, n in enumerate(names):
            val = x[i]
            old = vnl.get(n, 0.0)
            try:
                nv = float(val.real if isinstance(val, complex) else val)
                ov = float(old.real if isinstance(old, complex) else old)
            except Exception:
                nv, ov = 0.0, 0.0
            nxt[n] = ov + 0.6 * (nv - ov) if abs(nv - ov) > 0.5 else nv
            mx = max(mx, abs(nv - ov))
        vnl = nxt
        if mx < 1e-7:
            break
    return x, names, vs


def _tran(net: _Net, tstep: float, tstop: float, lang: str, eng: bool) -> dict:
    tstep = max(float(tstep or 1e-6), 1e-12)
    tstop = max(float(tstop or 1e-3), tstep)
    n = int(min(800, max(8, round(tstop / tstep))))
    h = tstop / n
    vprev = {}
    iprev = {}
    names = _nodes(net)
    path = []
    last_x = None
    last_vs = []
    t = 0.0
    for k in range(n + 1):
        vnl = {n: 0.0 for n in names}
        x = None
        vs = last_vs
        for _ in range(12 if _has_nl(net) else 1):
            x, names, vs = _solve_mna(net, 0.0, vprev=vprev, iprev=iprev, h=h, vnl=vnl)
            if x is None:
                break
            if not _has_nl(net):
                break
            nxt = {}
            for i, nm in enumerate(names):
                val = x[i]
                nxt[nm] = float(val.real if isinstance(val, complex) else val)
            vnl = nxt
        if x is None:
            break
        last_x, last_vs = x, vs
        vmap = {names[i]: x[i] for i in range(len(names))}
        for e in net.elems:
            if e["k"] == "C":
                va = 0j if _is_gnd(e["n1"]) else vmap.get(e["n1"], 0j)
                vb = 0j if _is_gnd(e["n2"]) else vmap.get(e["n2"], 0j)
                vprev[e["name"]] = (va - vb).real if isinstance(va - vb, complex) else float(va - vb)
            elif e["k"] == "L":
                va = 0j if _is_gnd(e["n1"]) else vmap.get(e["n1"], 0j)
                vb = 0j if _is_gnd(e["n2"]) else vmap.get(e["n2"], 0j)
                L = _num(e["val"]) or 0.0
                if abs(L) > 1e-18:
                    iprev[e["name"]] = iprev.get(e["name"], 0.0) + h / L * float((va - vb).real if isinstance(va - vb, complex) else va - vb)
        row = [t] + [float((x[i].real if isinstance(x[i], complex) else x[i])) for i in range(len(names))]
        path.append(row)
        t += h
    if last_x is None:
        return _fail(lang)
    out = _format_solution(net, last_x, names, last_vs, 0.0, lang, eng)
    bits = []
    for row in path[:: max(1, len(path) // 12)][-12:]:
        vs = " ".join(f"{names[i]}={_pretty(row[i+1], 'V', eng)}" for i in range(len(names)))
        bits.append(f"t={_pretty(row[0], 's', eng)}  {vs}")
    extra = "\n".join(bits)
    out["text"] = (out.get("text") or "0") + " | tran " + extra.replace("\n", " ; ")
    out["path"] = path[-80:]
    out["nodes"] = names
    out["steps"] = (out.get("steps") or []) + _steps(lang, "kind", what=f"transient to {tstop} s, {n} steps")
    return out


def run(raw: str, mode: str = "solve", freq: str = "", lang: str = "en", eng: bool = False) -> dict:
    try:
        text = unicodedata.normalize("NFKC", str(raw or "")).strip().translate(_DIGIT)
        if not text:
            return _fail(lang)
        sc = _shortcuts(text, lang, eng)
        if sc is not None and not re.match(r"^[RCLVIEFGHDQM]\w*\s+\S+\s+\S+", text, re.I | re.M):
            return sc
        net = _parse_net(text)
        f = _num(freq, None)
        if f is None:
            f = net.freq or 0.0
        if (mode or "").lower().startswith("inv") or any(str(e["val"]) in {"?", "x", "X"} for e in net.elems):
            if net.eq:
                return _inverse(net, f, lang, eng)
        if net.thev:
            return _thevenin(net, net.thev[0], net.thev[1], f, lang, eng)
        if not net.elems:
            if sc is not None:
                return sc
            return _fail(lang)
        if net.tran or (mode or "").lower().startswith("tran"):
            ts, tf = net.tran or (1e-6, 1e-3)
            return _tran(net, ts, tf, lang, eng)
        if _has_nl(net) and not f:
            x, names, vs = _solve_nl(net, f)
        else:
            x, names, vs = _solve_mna(net, f)
        out = _format_solution(net, x, names, vs, f, lang, eng)
        out["steps"] = _steps(lang, "read", raw=text.splitlines()[0] if text else "") + (out.get("steps") or [])
        return out
    except Exception:
        return _fail(lang)
