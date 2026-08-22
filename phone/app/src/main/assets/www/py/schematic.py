"""Schematic capture: parts + wires -> netlist -> solve. Independent copy."""

from __future__ import annotations

import math

try:
    import circuits
except Exception:
    try:
        from . import circuits
    except Exception:
        circuits = None


# Two-terminal half-length in grid cells (pin is 2 cells from center).
_SPAN = 2

_TWO = ("R", "C", "L", "V", "I", "D")
_THREE = ("Q", "M")


def _rot_offset(dx, dy, rot):
    r = int(rot or 0) % 360
    if r == 90:
        return -dy, dx
    if r == 180:
        return -dx, -dy
    if r == 270:
        return dy, -dx
    return dx, dy


def pins_of(part: dict) -> list[dict]:
    """Return [{name, x, y}, ...] in grid cells. pin 0 is n+ / anode / C / D."""
    x = int(part.get("x") or 0)
    y = int(part.get("y") or 0)
    rot = int(part.get("rot") or 0)
    k = str(part.get("k") or "R").upper()
    if k == "GND":
        return [{"name": "p", "x": x, "y": y}]
    if k in _THREE:
        # C/D up, B/G left, E/S down
        pts = [(0, -_SPAN, "c" if k == "Q" else "d"), (-_SPAN, 0, "b" if k == "Q" else "g"), (0, _SPAN, "e" if k == "Q" else "s")]
        out = []
        for dx, dy, name in pts:
            rx, ry = _rot_offset(dx, dy, rot)
            out.append({"name": name, "x": x + rx, "y": y + ry})
        return out
    # two-terminal: pin0 left (-), pin1 right (+) in local frame, then rotate
    p0 = _rot_offset(-_SPAN, 0, rot)
    p1 = _rot_offset(_SPAN, 0, rot)
    n0, n1 = ("p", "n") if k != "D" else ("a", "k")
    if k == "V":
        n0, n1 = "+", "-"
    return [
        {"name": n0, "x": x + p0[0], "y": y + p0[1]},
        {"name": n1, "x": x + p1[0], "y": y + p1[1]},
    ]


def _seg_points(x1, y1, x2, y2):
    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
    pts = []
    if x1 == x2:
        lo, hi = (y1, y2) if y1 <= y2 else (y2, y1)
        for y in range(lo, hi + 1):
            pts.append((x1, y))
    elif y1 == y2:
        lo, hi = (x1, x2) if x1 <= x2 else (x2, x1)
        for x in range(lo, hi + 1):
            pts.append((x, y1))
    else:
        # not axis aligned: treat as two points only
        pts = [(x1, y1), (x2, y2)]
    return pts


class _UF:
    def __init__(self):
        self.p = {}

    def add(self, a):
        if a not in self.p:
            self.p[a] = a

    def find(self, a):
        self.add(a)
        while self.p[a] != a:
            self.p[a] = self.p[self.p[a]]
            a = self.p[a]
        return a

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.p[rb] = ra


def extract(doc: dict) -> dict:
    """Assign node numbers and build a netlist string."""
    parts = list((doc or {}).get("parts") or [])
    wires = list((doc or {}).get("wires") or [])
    uf = _UF()
    pin_at = []  # (part, pin_index, point)

    for w in wires:
        pts = _seg_points(w.get("x1", 0), w.get("y1", 0), w.get("x2", 0), w.get("y2", 0))
        if not pts:
            continue
        prev = pts[0]
        uf.add(prev)
        for pt in pts[1:]:
            uf.add(pt)
            uf.union(prev, pt)
            prev = pt

    for part in parts:
        for i, pin in enumerate(pins_of(part)):
            pt = (int(pin["x"]), int(pin["y"]))
            uf.add(pt)
            pin_at.append((part, i, pt, pin["name"]))

    # Ground: any GND part, or a pin sitting on a GND pin's set
    gnd_roots = set()
    for part in parts:
        if str(part.get("k") or "").upper() == "GND":
            for pin in pins_of(part):
                gnd_roots.add(uf.find((int(pin["x"]), int(pin["y"]))))

    # Number remaining connected sets
    roots = []
    for part, i, pt, name in pin_at:
        r = uf.find(pt)
        if r not in gnd_roots and r not in roots:
            roots.append(r)
    num = {r: str(i + 1) for i, r in enumerate(roots)}
    for r in gnd_roots:
        num[r] = "0"

    assignment = {}
    lines = []
    counts = {}
    for part in parts:
        k = str(part.get("k") or "R").upper()
        if k == "GND":
            continue
        pins = pins_of(part)
        nodes = []
        pinmap = {}
        for i, pin in enumerate(pins):
            pt = (int(pin["x"]), int(pin["y"]))
            n = num.get(uf.find(pt), "0")
            nodes.append(n)
            pinmap[pin["name"]] = n
        name = str(part.get("id") or "").strip()
        if not name or name.upper() == "GND":
            counts[k] = counts.get(k, 0) + 1
            name = f"{k}{counts[k]}"
        assignment[name] = pinmap
        val = str(part.get("val") if part.get("val") is not None else "").strip()
        extra = str(part.get("extra") or "").strip()
        if k in _TWO:
            if not val:
                val = {"R": "1k", "C": "1u", "L": "1m", "V": "12", "I": "1m", "D": "1e-14"}.get(k, "1")
            # V pin0 is +, pin1 is -
            lines.append(f"{name} {nodes[0]} {nodes[1]} {val}")
        elif k == "Q":
            model = extra or "npn"
            beta = val or "100"
            # pins: c, b, e
            lines.append(f"{name} {nodes[0]} {nodes[1]} {nodes[2]} {model} {beta}")
        elif k == "M":
            model = extra or "nmos"
            kp = val or "2e-4"
            lines.append(f"{name} {nodes[0]} {nodes[1]} {nodes[2]} {model} {kp}")

    net = "\n".join(lines)
    return {
        "netlist": net,
        "assignment": assignment,
        "node_of": {f"{a[0].get('id')}:{a[3]}": num.get(uf.find(a[2]), "0") for a in pin_at},
        "points": {f"{px},{py}": num.get(uf.find((px, py)), "0") for (px, py) in uf.p},
    }


def example_divider() -> dict:
    """12 V, 1k then 2k to ground. Classic 8 V mid node."""
    return {
        "parts": [
            {"id": "V1", "k": "V", "x": 6, "y": 8, "rot": 90, "val": "12"},
            {"id": "R1", "k": "R", "x": 12, "y": 6, "rot": 0, "val": "1k"},
            {"id": "R2", "k": "R", "x": 14, "y": 8, "rot": 90, "val": "2k"},
            {"id": "GND1", "k": "GND", "x": 6, "y": 14, "rot": 0, "val": ""},
        ],
        "wires": [
            {"x1": 6, "y1": 6, "x2": 10, "y2": 6},
            {"x1": 6, "y1": 10, "x2": 6, "y2": 14},
            {"x1": 14, "y1": 10, "x2": 6, "y2": 10},
        ],
    }


def _esc(s) -> str:
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _cell(doc) -> int:
    try:
        return max(16, min(int((doc or {}).get("cell") or 28), 48))
    except Exception:
        return 28


def _xy(gx, gy, cell, ox, oy):
    return ox + gx * cell, oy + gy * cell


def render(doc: dict, result: dict | None = None, width: int = 960, height: int = 560) -> str:
    """High-contrast schematic SVG. Coordinates in grid cells."""
    cell = _cell(doc)
    ox, oy = 16, 16
    parts = list((doc or {}).get("parts") or [])
    wires = list((doc or {}).get("wires") or [])
    voltages = (result or {}).get("vmap") or {}
    currents = (result or {}).get("imap") or {}
    points = (result or {}).get("points") or {}

    # extent
    xs, ys = [0], [0]
    for p in parts:
        xs.append(int(p.get("x") or 0))
        ys.append(int(p.get("y") or 0))
    for w in wires:
        xs += [int(w.get("x1") or 0), int(w.get("x2") or 0)]
        ys += [int(w.get("y1") or 0), int(w.get("y2") or 0)]
    maxx, maxy = max(xs) + 4, max(ys) + 4
    width = max(width, ox * 2 + maxx * cell)
    height = max(height, oy * 2 + maxy * cell)

    bits = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">',
        f'<rect width="{width}" height="{height}" fill="#0e1116"/>',
    ]
    # grid
    for gx in range(0, maxx + 2):
        x = ox + gx * cell
        bits.append(f'<line x1="{x}" y1="{oy}" x2="{x}" y2="{oy + maxy * cell}" stroke="#1c232c" stroke-width="1"/>')
    for gy in range(0, maxy + 2):
        y = oy + gy * cell
        bits.append(f'<line x1="{ox}" y1="{y}" x2="{ox + maxx * cell}" y2="{y}" stroke="#1c232c" stroke-width="1"/>')

    # wires
    for w in wires:
        x1, y1 = _xy(int(w.get("x1") or 0), int(w.get("y1") or 0), cell, ox, oy)
        x2, y2 = _xy(int(w.get("x2") or 0), int(w.get("y2") or 0), cell, ox, oy)
        bits.append(
            f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#d5dde6" stroke-width="2.4" stroke-linecap="round"/>'
        )

    # junction dots: count wire incidences per point
    hit = {}
    for w in wires:
        for pt in _seg_points(w.get("x1", 0), w.get("y1", 0), w.get("x2", 0), w.get("y2", 0)):
            if pt == (int(w.get("x1") or 0), int(w.get("y1") or 0)) or pt == (int(w.get("x2") or 0), int(w.get("y2") or 0)):
                hit[pt] = hit.get(pt, 0) + 1
    for pt, n in hit.items():
        if n >= 3:
            x, y = _xy(pt[0], pt[1], cell, ox, oy)
            bits.append(f'<circle cx="{x}" cy="{y}" r="3.6" fill="#d5dde6"/>')

    for part in parts:
        bits.append(_draw_part(part, cell, ox, oy, currents))

    # node voltage tags
    seen = set()
    for key, node in points.items():
        if not node or node == "0":
            continue
        if "," not in key:
            continue
        try:
            gx, gy = key.split(",", 1)
            gx, gy = int(gx), int(gy)
        except Exception:
            continue
        tag = voltages.get(str(node))
        if not tag or node in seen:
            continue
        # only label if this point is a pin or a junction
        if hit.get((gx, gy), 0) < 2 and not any(
            (int(pn["x"]), int(pn["y"])) == (gx, gy) for p in parts for pn in pins_of(p)
        ):
            continue
        seen.add(node)
        x, y = _xy(gx, gy, cell, ox, oy)
        bits.append(
            f'<rect x="{x + 6}" y="{y - 16}" width="{8 * len(tag) + 10}" height="16" rx="2" fill="#1c1f24" stroke="#c4a35a"/>'
        )
        bits.append(
            f'<text x="{x + 10}" y="{y - 4}" fill="#c4a35a" font-size="11" font-family="Consolas,monospace">{_esc(tag)}</text>'
        )

    bits.append("</svg>")
    return "".join(bits)


def _draw_part(part, cell, ox, oy, currents):
    k = str(part.get("k") or "R").upper()
    rot = int(part.get("rot") or 0) % 360
    cx, cy = _xy(int(part.get("x") or 0), int(part.get("y") or 0), cell, ox, oy)
    name = _esc(part.get("id") or k)
    val = _esc(part.get("val") or "")
    cur = currents.get(part.get("id") or "")
    label = name + ((" " + val) if val else "")
    if cur:
        label += "  " + _esc(cur)
    body = _symbol_paths(k, cell)
    # rotate around center
    g = f'<g transform="translate({cx:.1f},{cy:.1f}) rotate({rot})">'
    g += body
    g += "</g>"
    # label not rotated
    g += (
        f'<text x="{cx + 8}" y="{cy - cell * 0.85:.1f}" fill="#c4a35a" font-size="12" '
        f'font-family="Segoe UI,Tahoma,sans-serif">{label}</text>'
    )
    return g


def _symbol_paths(k: str, cell: int) -> str:
    """Local coordinates, 0 at center, pins at x=±2*cell."""
    L = 2 * cell
    ink = "#e8eaed"
    gold = "#c4a35a"
    if k == "R":
        # IEC rectangle + leads
        return (
            f'<line x1="{-L}" y1="0" x2="{-0.7 * cell}" y2="0" stroke="{ink}" stroke-width="2.2"/>'
            f'<rect x="{-0.7 * cell}" y="{-0.32 * cell}" width="{1.4 * cell}" height="{0.64 * cell}" '
            f'fill="none" stroke="{ink}" stroke-width="2.2"/>'
            f'<line x1="{0.7 * cell}" y1="0" x2="{L}" y2="0" stroke="{ink}" stroke-width="2.2"/>'
        )
    if k == "C":
        return (
            f'<line x1="{-L}" y1="0" x2="{-0.18 * cell}" y2="0" stroke="{ink}" stroke-width="2.2"/>'
            f'<line x1="{-0.18 * cell}" y1="{-0.55 * cell}" x2="{-0.18 * cell}" y2="{0.55 * cell}" stroke="{ink}" stroke-width="2.6"/>'
            f'<line x1="{0.18 * cell}" y1="{-0.55 * cell}" x2="{0.18 * cell}" y2="{0.55 * cell}" stroke="{ink}" stroke-width="2.6"/>'
            f'<line x1="{0.18 * cell}" y1="0" x2="{L}" y2="0" stroke="{ink}" stroke-width="2.2"/>'
        )
    if k == "L":
        arcs = []
        # four humps
        x0 = -0.8 * cell
        r = 0.2 * cell
        for i in range(4):
            cx = x0 + (i * 2 + 1) * r
            arcs.append(
                f'<path d="M {cx - r:.1f} 0 A {r:.1f} {r:.1f} 0 0 1 {cx + r:.1f} 0" fill="none" stroke="{ink}" stroke-width="2.2"/>'
            )
        return (
            f'<line x1="{-L}" y1="0" x2="{x0:.1f}" y2="0" stroke="{ink}" stroke-width="2.2"/>'
            + "".join(arcs)
            + f'<line x1="{x0 + 8 * r:.1f}" y1="0" x2="{L}" y2="0" stroke="{ink}" stroke-width="2.2"/>'
        )
    if k == "V":
        r = 0.62 * cell
        return (
            f'<line x1="{-L}" y1="0" x2="{-r}" y2="0" stroke="{ink}" stroke-width="2.2"/>'
            f'<circle cx="0" cy="0" r="{r}" fill="#14181f" stroke="{gold}" stroke-width="2.2"/>'
            f'<text x="{-0.38 * cell}" y="{-0.08 * cell}" fill="{gold}" font-size="{0.42 * cell:.0f}" font-family="serif">+</text>'
            f'<text x="{0.12 * cell}" y="{-0.08 * cell}" fill="{ink}" font-size="{0.5 * cell:.0f}" font-family="serif">−</text>'
            f'<line x1="{r}" y1="0" x2="{L}" y2="0" stroke="{ink}" stroke-width="2.2"/>'
        )
    if k == "I":
        r = 0.62 * cell
        return (
            f'<line x1="{-L}" y1="0" x2="{-r}" y2="0" stroke="{ink}" stroke-width="2.2"/>'
            f'<circle cx="0" cy="0" r="{r}" fill="#14181f" stroke="{gold}" stroke-width="2.2"/>'
            f'<line x1="{-0.28 * cell}" y1="0" x2="{0.28 * cell}" y2="0" stroke="{gold}" stroke-width="2"/>'
            f'<polygon points="{0.28 * cell:.1f},0 {0.08 * cell:.1f},{-0.12 * cell:.1f} {0.08 * cell:.1f},{0.12 * cell:.1f}" fill="{gold}"/>'
            f'<line x1="{r}" y1="0" x2="{L}" y2="0" stroke="{ink}" stroke-width="2.2"/>'
        )
    if k == "D":
        return (
            f'<line x1="{-L}" y1="0" x2="{-0.35 * cell}" y2="0" stroke="{ink}" stroke-width="2.2"/>'
            f'<polygon points="{-0.35 * cell:.1f},{-0.4 * cell:.1f} {-0.35 * cell:.1f},{0.4 * cell:.1f} {0.28 * cell:.1f},0" fill="none" stroke="{gold}" stroke-width="2.2"/>'
            f'<line x1="{0.28 * cell}" y1="{-0.4 * cell}" x2="{0.28 * cell}" y2="{0.4 * cell}" stroke="{gold}" stroke-width="2.4"/>'
            f'<line x1="{0.28 * cell}" y1="0" x2="{L}" y2="0" stroke="{ink}" stroke-width="2.2"/>'
        )
    if k == "GND":
        return (
            f'<line x1="0" y1="{-0.2 * cell}" x2="0" y2="0" stroke="{ink}" stroke-width="2.2"/>'
            f'<line x1="{-0.45 * cell}" y1="0" x2="{0.45 * cell}" y2="0" stroke="{ink}" stroke-width="2.4"/>'
            f'<line x1="{-0.3 * cell}" y1="{0.16 * cell}" x2="{0.3 * cell}" y2="{0.16 * cell}" stroke="{ink}" stroke-width="2"/>'
            f'<line x1="{-0.15 * cell}" y1="{0.32 * cell}" x2="{0.15 * cell}" y2="{0.32 * cell}" stroke="{ink}" stroke-width="2"/>'
        )
    if k == "Q":
        r = 0.7 * cell
        return (
            f'<circle cx="0" cy="0" r="{r}" fill="#14181f" stroke="{gold}" stroke-width="2"/>'
            f'<line x1="{-L}" y1="0" x2="{-0.25 * cell}" y2="0" stroke="{ink}" stroke-width="2"/>'
            f'<line x1="{-0.25 * cell}" y1="{-0.35 * cell}" x2="{-0.25 * cell}" y2="{0.35 * cell}" stroke="{gold}" stroke-width="2.4"/>'
            f'<line x1="{-0.25 * cell}" y1="{-0.18 * cell}" x2="0" y2="{-L}" stroke="{ink}" stroke-width="2"/>'
            f'<line x1="{-0.25 * cell}" y1="{0.18 * cell}" x2="0" y2="{L}" stroke="{ink}" stroke-width="2"/>'
            f'<polygon points="{-0.02 * cell:.1f},{0.55 * cell:.1f} {0.12 * cell:.1f},{0.72 * cell:.1f} {-0.14 * cell:.1f},{0.78 * cell:.1f}" fill="{gold}"/>'
        )
    if k == "M":
        return (
            f'<line x1="{-L}" y1="0" x2="{-0.2 * cell}" y2="0" stroke="{ink}" stroke-width="2"/>'
            f'<line x1="{-0.2 * cell}" y1="{-0.45 * cell}" x2="{-0.2 * cell}" y2="{0.45 * cell}" stroke="{gold}" stroke-width="2.4"/>'
            f'<line x1="{-0.05 * cell}" y1="{-0.45 * cell}" x2="{-0.05 * cell}" y2="{0.45 * cell}" stroke="{gold}" stroke-width="2"/>'
            f'<line x1="{-0.05 * cell}" y1="{-0.28 * cell}" x2="{0.15 * cell}" y2="{-0.28 * cell}" stroke="{ink}" stroke-width="2"/>'
            f'<line x1="{0.15 * cell}" y1="{-0.28 * cell}" x2="0" y2="{-L}" stroke="{ink}" stroke-width="2"/>'
            f'<line x1="{-0.05 * cell}" y1="{0.28 * cell}" x2="0" y2="{L}" stroke="{ink}" stroke-width="2"/>'
        )
    return f'<circle cx="0" cy="0" r="{0.3 * cell}" fill="none" stroke="{ink}"/>'


def _parse_maps(text: str):
    vmap, imap = {}, {}
    if not text:
        return vmap, imap
    for chunk in text.replace("|", ";").split(";"):
        chunk = chunk.strip()
        m = None
        if chunk.startswith("V(") and "=" in chunk:
            try:
                node = chunk.split("(", 1)[1].split(")", 1)[0].strip()
                val = chunk.split("=", 1)[1].strip()
                vmap[node] = val
            except Exception:
                pass
        if chunk.startswith("I(") and "=" in chunk:
            try:
                name = chunk.split("(", 1)[1].split(")", 1)[0].strip()
                val = chunk.split("=", 1)[1].strip()
                imap[name] = val
            except Exception:
                pass
    return vmap, imap


def run(doc: dict | None = None, mode: str = "solve", freq: str = "", lang: str = "en", eng: bool = False) -> dict:
    try:
        doc = doc or {}
        if not doc.get("parts"):
            doc = example_divider()
        info = extract(doc)
        net = info.get("netlist") or ""
        if not net.strip():
            msg = {"en": "No solvable parts. Place a source and a load, then wire them.", "fa": "قطعه‌ای برای حل نیست. منبع و بار بگذار و سیم بکش.", "fi": "Ei ratkaistavaa. Lisaa lahde ja kuorma, sitten johdot."}
            return {"ok": True, "text": "0", "netlist": "", "svg": render(doc), "steps": [msg.get(lang) or msg["en"]], "assignment": {}, "points": {}, "vmap": {}, "imap": {}}
        if circuits is None:
            return {"ok": True, "text": "0", "netlist": net, "svg": render(doc), "steps": [], "assignment": info.get("assignment") or {}}
        out = circuits.run(net, mode=mode or "solve", freq=freq or "", lang=lang, eng=eng)
        vmap, imap = _parse_maps(out.get("text") or "")
        out["netlist"] = net
        out["assignment"] = info.get("assignment") or {}
        out["points"] = info.get("points") or {}
        out["vmap"] = vmap
        out["imap"] = imap
        out["svg"] = render(doc, out)
        steps = list(out.get("steps") or [])
        steps = [
            {"en": "Schematic converted to a netlist.", "fa": "شماتیک به نت‌لیست تبدیل شد.", "fi": "Kaavio muutettiin nettilistaksi."}.get(lang)
            or "Schematic converted to a netlist.",
            net.replace("\n", " / "),
        ] + steps
        out["steps"] = [s for s in steps if s]
        return out
    except Exception:
        msg = {"en": "Could not solve the schematic. Showing 0.", "fa": "شماتیک حل نشد. ۰.", "fi": "Kaaviota ei voitu ratkaista. 0."}
        return {"ok": True, "text": "0", "netlist": "", "svg": "", "steps": [msg.get(lang) or msg["en"]]}


def pins_json(doc: dict) -> list:
    rows = []
    for part in (doc or {}).get("parts") or []:
        for i, pin in enumerate(pins_of(part)):
            rows.append({"id": part.get("id"), "i": i, "name": pin["name"], "x": pin["x"], "y": pin["y"]})
    return rows
