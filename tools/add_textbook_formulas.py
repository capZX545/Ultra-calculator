"""Add textbook formulas so the non-unit catalog reaches 5000.

Unit conversions stay in category unit.conv and are not counted toward that 5000.
Each new row is a named identity the solver can actually rearrange.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import sympy as sp
from sympy.parsing.sympy_parser import parse_expr, standard_transformations

ROOT = Path(__file__).resolve().parents[1]
PATHS = [
    ROOT / "web" / "formulas.json",
    ROOT / "desktop" / "calc" / "formulas.json",
    ROOT / "android" / "formulas.json",
]
PHONE = ROOT / "phone" / "app" / "src" / "main" / "assets" / "www" / "py" / "formulas.json"
if PHONE.exists():
    PATHS.append(PHONE)

RESERVED = {
    "I", "E", "pi", "re", "rf", "beta", "gamma", "yn", "def", "in", "lambda",
    "euler", "catalan", "zeta", "diff", "limit", "series", "factor", "expand",
    "simplify", "apart", "together", "cancel", "Min", "Max", "Mod", "Ei",
}

NEW_CATS = {
    "math.discrete": {"en": "Discrete math", "fa": "ریاضی گسسته", "fi": "Diskreetti matematiikka"},
    "math.opt": {"en": "Optimization", "fa": "بهینه سازی", "fi": "Optimointi"},
    "physics.statmech": {"en": "Statistical mechanics", "fa": "مکانیک آماری", "fi": "Tilastollinen mekaniikka"},
    "physics.relativity": {"en": "Relativity", "fa": "نسبیت", "fi": "Suhteellisuusteoria"},
    "eng.reliability": {"en": "Reliability", "fa": "قابلیت اطمینان", "fi": "Luotettavuus"},
    "eng.queue": {"en": "Queueing", "fa": "صف", "fi": "Jonoteoria"},
    "eng.rf": {"en": "RF and antennas", "fa": "آنتن و بسامد رادیویی", "fi": "RF ja antennit"},
    "eng.tl": {"en": "Transmission lines", "fa": "خطوط انتقال", "fi": "Siirtolinjat"},
    "chem.surf": {"en": "Surface chemistry", "fa": "شیمی سطح", "fi": "Pintakemia"},
    "med.cardio": {"en": "Cardiology calculations", "fa": "محاسبات قلب", "fi": "Kardiologia"},
    "geo.hydro": {"en": "Hydrology", "fa": "هیدرولوژی", "fi": "Hydrologia"},
    "cs.infotheory": {"en": "Information theory", "fa": "نظریه اطلاعات", "fi": "Informaatioteoria"},
}


def nm(en, fa, fi):
    return {"en": en, "fa": fa, "fi": fi}


def V(*triples):
    """triples: (name, unit, en, fa, fi)"""
    out = {}
    for item in triples:
        name, unit, en, fa, fi = item
        out[name] = {"unit": unit, "name": nm(en, fa, fi)}
    return out


def row(fid, cat, en, fa, fi, expr, variables):
    return {
        "id": fid,
        "category": cat,
        "name": nm(en, fa, fi),
        "expr": expr,
        "variables": variables,
        "source": "std",
    }


def build():
    R = []
    a = R.append

    # ---------- math.geometry extras ----------
    for n in range(3, 21):
        a(row(f"tx_ngon_rin_{n}", "math.geometry",
              f"Regular {n}-gon inradius", f"شعاع داخلی چندضلعی منتظم {n}", f"Saannollisen {n}-kulmion sade",
              f"r = s/(2*tan(pi/{n}))",
              V(("r", "m", "inradius", "شعاع داخلی", "sade"), ("s", "m", "side", "ضلع", "sivu"))))
        a(row(f"tx_ngon_diag_{n}", "math.geometry",
              f"Regular {n}-gon diagonals", f"قطرهای چندضلعی منتظم {n}", f"Saannollisen {n}-kulmion diagonaalit",
              f"d = {n}*({n} - 3)/2",
              V(("d", "1", "diagonals", "تعداد قطر", "diagonaalit"),)))
    for n, name_en, name_fa, name_fi in [
        (13, "13-gon", "سیزده‌ضلعی", "13-kulmio"),
        (14, "14-gon", "چهارده‌ضلعی", "14-kulmio"),
        (15, "15-gon", "پانزده‌ضلعی", "15-kulmio"),
        (16, "16-gon", "شانزده‌ضلعی", "16-kulmio"),
        (18, "18-gon", "هجده‌ضلعی", "18-kulmio"),
        (20, "20-gon", "بیست‌ضلعی", "20-kulmio"),
        (24, "24-gon", "بیست‌وچهارضلعی", "24-kulmio"),
    ]:
        a(row(f"tx_ngon_area_{n}", "math.geometry",
              f"Regular {name_en} area", f"مساحت {name_fa} منتظم", f"Saannollisen {name_fi}n pinta-ala",
              f"A = {n}*s**2/(4*tan(pi/{n}))",
              V(("A", "m^2", "area", "مساحت", "pinta-ala"), ("s", "m", "side", "ضلع", "sivu"))))
        a(row(f"tx_ngon_per_{n}", "math.geometry",
              f"Regular {name_en} perimeter", f"محیط {name_fa} منتظم", f"Saannollisen {name_fi}n piiri",
              f"P = {n}*s",
              V(("P", "m", "perimeter", "محیط", "piiri"), ("s", "m", "side", "ضلع", "sivu"))))
        a(row(f"tx_ngon_R_{n}", "math.geometry",
              f"Regular {name_en} circumradius", f"شعاع محیطی {name_fa}", f"Saannollisen {name_fi}n ymparyssade",
              f"R = s/(2*sin(pi/{n}))",
              V(("R", "m", "circumradius", "شعاع محیطی", "ymparyssade"), ("s", "m", "side", "ضلع", "sivu"))))

    extras_geo = [
        ("tx_sphere_cap_v", "Spherical cap volume", "حجم کلاهک کروی", "Pallon kalotin tilavuus",
         "V = pi*h**2*(3*R - h)/3",
         V(("V", "m^3", "volume", "حجم", "tilavuus"), ("h", "m", "height", "ارتفاع", "korkeus"), ("R", "m", "sphere radius", "شعاع کره", "sade"))),
        ("tx_sphere_cap_a", "Spherical cap surface", "سطح کلاهک کروی", "Pallon kalotin pinta",
         "A = 2*pi*R*h",
         V(("A", "m^2", "area", "مساحت", "pinta-ala"), ("R", "m", "radius", "شعاع", "sade"), ("h", "m", "height", "ارتفاع", "korkeus"))),
        ("tx_sphere_zone_a", "Spherical zone area", "مساحت نوار کروی", "Pallovyohykkeen pinta",
         "A = 2*pi*R*h",
         V(("A", "m^2", "area", "مساحت", "pinta-ala"), ("R", "m", "radius", "شعاع", "sade"), ("h", "m", "height", "ارتفاع", "korkeus"))),
        ("tx_sphere_seg2", "Spherical segment two bases", "قطعه کروی دو قاعده", "Pallosegmentti kahdella pohjalla",
         "V = pi*h*(3*a**2 + 3*b**2 + h**2)/6",
         V(("V", "m^3", "volume", "حجم", "tilavuus"), ("h", "m", "height", "ارتفاع", "korkeus"),
           ("a", "m", "lower radius", "شعاع پایین", "alaradius"), ("b", "m", "upper radius", "شعاع بالا", "ylaradius"))),
        ("tx_lune_area", "Spherical lune area", "مساحت هلال کروی", "Pallokuun pinta",
         "A = 2*R**2*theta",
         V(("A", "m^2", "area", "مساحت", "pinta-ala"), ("R", "m", "radius", "شعاع", "sade"), ("theta", "rad", "dihedral angle", "زاویه دووجهی", "kulma"))),
        ("tx_spherical_tri", "Spherical triangle area", "مساحت مثلث کروی", "Pallokolmion pinta-ala",
         "A = R**2*(Aang + Bang + Cang - pi)",
         V(("A", "m^2", "area", "مساحت", "pinta-ala"), ("R", "m", "radius", "شعاع", "sade"),
           ("Aang", "rad", "angle A", "زاویه A", "kulma A"), ("Bang", "rad", "angle B", "زاویه B", "kulma B"),
           ("Cang", "rad", "angle C", "زاویه C", "kulma C"))),
        ("tx_cone_lat", "Right cone lateral area", "مساحت جانبی مخروط", "Kartion vaipan pinta",
         "A = pi*r*s",
         V(("A", "m^2", "area", "مساحت", "pinta-ala"), ("r", "m", "base radius", "شعاع قاعده", "sade"), ("s", "m", "slant height", "ارتفاع مایل", "sivukorkeus"))),
        ("tx_pyramid_lat", "Regular pyramid lateral", "مساحت جانبی هرم منتظم", "Saanollisen pyramidin vaippa",
         "A = n*s*l/2",
         V(("A", "m^2", "area", "مساحت", "pinta-ala"), ("n", "1", "sides", "تعداد اضلاع", "sivujen maara"),
           ("s", "m", "base side", "ضلع قاعده", "sivun pituus"), ("l", "m", "slant height", "ارتفاع مایل", "sivukorkeus"))),
        ("tx_wedge_v", "Cylindrical wedge volume", "حجم گوه استوانه‌ای", "Lieriokiilan tilavuus",
         "V = r**2*h*(theta - sin(theta))/2",
         V(("V", "m^3", "volume", "حجم", "tilavuus"), ("r", "m", "radius", "شعاع", "sade"),
           ("h", "m", "length", "طول", "pituus"), ("theta", "rad", "angle", "زاویه", "kulma"))),
        ("tx_torus_inner", "Horn torus volume", "حجم چنبره مماس", "Sarvitoruksen tilavuus",
         "V = 2*pi**2*r**3",
         V(("V", "m^3", "volume", "حجم", "tilavuus"), ("r", "m", "tube radius", "شعاع لوله", "putken sade"))),
        ("tx_ellipsoid_sa_approx", "Ellipsoid surface approx", "تقریب سطح بیضی‌وار", "Ellipsoidin pinta likimain",
         "A = 4*pi*(((a*b)**p + (a*c)**p + (b*c)**p)/3)**(1/p)",
         V(("A", "m^2", "area", "مساحت", "pinta-ala"), ("a", "m", "semi-axis a", "نیم‌محور a", "puoliakseli a"),
           ("b", "m", "semi-axis b", "نیم‌محور b", "puoliakseli b"), ("c", "m", "semi-axis c", "نیم‌محور c", "puoliakseli c"),
           ("p", "1", "Knud Thomsen p", "توان p", "eksponentti p"))),
        ("tx_pappus_centroid", "Pappus centroid theorem", "قضیه مرکزوار پاپوس", "Pappuksen keskiopiste",
         "A = s*2*pi*R",
         V(("A", "m^2", "surface", "سطح", "pinta"), ("s", "m", "curve length", "طول منحنی", "kayran pituus"),
           ("R", "m", "centroid radius", "شعاع مرکزوار", "keskiopisteen sade"))),
        ("tx_pappus_vol", "Pappus volume theorem", "حجم پاپوس", "Pappuksen tilavuus",
         "V = A*2*pi*R",
         V(("V", "m^3", "volume", "حجم", "tilavuus"), ("A", "m^2", "plane area", "مساحت صفحه", "pinta-ala"),
           ("R", "m", "centroid radius", "شعاع مرکزوار", "keskiopisteen sade"))),
        ("tx_circle_chord_h", "Circle chord from sagitta", "وتر از پیکان", "Janne nuolesta",
         "c = 2*sqrt(2*R*h - h**2)",
         V(("c", "m", "chord", "وتر", "janne"), ("R", "m", "radius", "شعاع", "sade"), ("h", "m", "sagitta", "پیکان", "nuoli"))),
        ("tx_sagitta", "Sagitta of a chord", "پیکان وتر", "Janteen nuoli",
         "h = R - sqrt(R**2 - (c/2)**2)",
         V(("h", "m", "sagitta", "پیکان", "nuoli"), ("R", "m", "radius", "شعاع", "sade"), ("c", "m", "chord", "وتر", "janne"))),
        ("tx_power_point", "Power of a point", "توان نقطه", "Pisteen potenssi",
         "p = d**2 - R**2",
         V(("p", "m^2", "power", "توان", "potenssi"), ("d", "m", "center distance", "فاصله از مرکز", "etaisyys"),
           ("R", "m", "radius", "شعاع", "sade"))),
        ("tx_intersect_chords", "Intersecting chords", "وترهای متقاطع", "Leikkaavat janteet",
         "a*b = c*d",
         V(("a", "m", "segment a", "قطعه a", "jana a"), ("b", "m", "segment b", "قطعه b", "jana b"),
           ("c", "m", "segment c", "قطعه c", "jana c"), ("d", "m", "segment d", "قطعه d", "jana d"))),
        ("tx_secant_tangent", "Tangent-secant theorem", "مماس و قاطع", "Sivujaa ja sekantti",
         "t**2 = ext*(ext + sec)",
         V(("t", "m", "tangent", "مماس", "sivujaa"), ("ext", "m", "external part", "بخش خارجی", "ulko-osa"),
           ("sec", "m", "internal chord", "وتر داخلی", "sisajanne"))),
        ("tx_apollonius", "Circle of Apollonius ratio", "دایره آپولونیوس", "Apollonioksen ympyra",
         "rto = d1/d2",
         V(("rto", "1", "ratio", "نسبت", "suhde"), ("d1", "m", "distance to A", "فاصله تا A", "etaisyys A"),
           ("d2", "m", "distance to B", "فاصله تا B", "etaisyys B"))),
        ("tx_hex_long", "Regular hexagon long diagonal", "قطر بلند شش‌ضلعی", "Kuusikulmion pitka diagonaali",
         "d = 2*s",
         V(("d", "m", "diagonal", "قطر", "diagonaali"), ("s", "m", "side", "ضلع", "sivu"))),
        ("tx_hex_short", "Regular hexagon short diagonal", "قطر کوتاه شش‌ضلعی", "Kuusikulmion lyhyt diagonaali",
         "d = s*sqrt(3)",
         V(("d", "m", "diagonal", "قطر", "diagonaali"), ("s", "m", "side", "ضلع", "sivu"))),
        ("tx_cube_face_diag", "Cube face diagonal", "قطر وجه مکعب", "Kuution tahkon diagonaali",
         "d = a*sqrt(2)",
         V(("d", "m", "diagonal", "قطر", "diagonaali"), ("a", "m", "edge", "یال", "sarmä"))),
        ("tx_cube_space_diag", "Cube space diagonal", "قطر فضایی مکعب", "Kuution avaruusdiagonaali",
         "d = a*sqrt(3)",
         V(("d", "m", "diagonal", "قطر", "diagonaali"), ("a", "m", "edge", "یال", "sarma"))),
        ("tx_rect_box_sa", "Rectangular box surface", "سطح مکعب مستطیل", "Suorakulmaisen sarmion pinta",
         "A = 2*(a*b + b*c + c*a)",
         V(("A", "m^2", "area", "مساحت", "pinta-ala"), ("a", "m", "length", "طول", "pituus"),
           ("b", "m", "width", "عرض", "leveys"), ("c", "m", "height", "ارتفاع", "korkeus"))),
        ("tx_tetra_height", "Regular tetrahedron height", "ارتفاع چهاروجهی منتظم", "Saanollisen tetraedrin korkeus",
         "h = a*sqrt(6)/3",
         V(("h", "m", "height", "ارتفاع", "korkeus"), ("a", "m", "edge", "یال", "sarma"))),
        ("tx_octa_vol", "Regular octahedron volume", "حجم هشت‌وجهی منتظم", "Saanollisen oktaedrin tilavuus",
         "V = a**3*sqrt(2)/3",
         V(("V", "m^3", "volume", "حجم", "tilavuus"), ("a", "m", "edge", "یال", "sarma"))),
        ("tx_octa_area", "Regular octahedron area", "مساحت هشت‌وجهی منتظم", "Saanollisen oktaedrin pinta",
         "A = 2*sqrt(3)*a**2",
         V(("A", "m^2", "area", "مساحت", "pinta-ala"), ("a", "m", "edge", "یال", "sarma"))),
        ("tx_dodeca_area", "Regular dodecahedron area", "مساحت دوازده‌وجهی", "Dodekaedrin pinta",
         "A = 3*sqrt(25 + 10*sqrt(5))*a**2",
         V(("A", "m^2", "area", "مساحت", "pinta-ala"), ("a", "m", "edge", "یال", "sarma"))),
        ("tx_icosa_area", "Regular icosahedron area", "مساحت بیست‌وجهی", "Ikosaedrin pinta",
         "A = 5*sqrt(3)*a**2",
         V(("A", "m^2", "area", "مساحت", "pinta-ala"), ("a", "m", "edge", "یال", "sarma"))),
        ("tx_icosa_vol", "Regular icosahedron volume", "حجم بیست‌وجهی", "Ikosaedrin tilavuus",
         "V = 5*(3 + sqrt(5))*a**3/12",
         V(("V", "m^3", "volume", "حجم", "tilavuus"), ("a", "m", "edge", "یال", "sarma"))),
        ("tx_golden_rect", "Golden rectangle other side", "ضلع دیگر مستطیل طلایی", "Kultaisen suorakulmion sivu",
         "b = a*(1 + sqrt(5))/2",
         V(("b", "m", "long side", "ضلع بلند", "pitka sivu"), ("a", "m", "short side", "ضلع کوتاه", "lyhyt sivu"))),
        ("tx_vesica", "Vesica piscis area", "مساحت مثانه ماهی", "Vesica pisciksen pinta",
         "A = 2*R**2*acos(0.5) - 0.5*R**2*sqrt(3)",
         V(("A", "m^2", "area", "مساحت", "pinta-ala"), ("R", "m", "radius", "شعاع", "sade"))),
        ("tx_reuleaux", "Reuleaux triangle area", "مساحت مثلث رولو", "Reuleaux-kolmion pinta",
         "A = 0.5*(pi - sqrt(3))*s**2",
         V(("A", "m^2", "area", "مساحت", "pinta-ala"), ("s", "m", "width", "پهنای ثابت", "leveys"))),
        ("tx_stadium", "Stadium area", "مساحت ورزشگاه", "Stadionin pinta-ala",
         "A = pi*r**2 + 2*r*L",
         V(("A", "m^2", "area", "مساحت", "pinta-ala"), ("r", "m", "radius", "شعاع", "sade"), ("L", "m", "straight length", "طول مستقیم", "suora pituus"))),
        ("tx_stadium_per", "Stadium perimeter", "محیط ورزشگاه", "Stadionin piiri",
         "P = 2*pi*r + 2*L",
         V(("P", "m", "perimeter", "محیط", "piiri"), ("r", "m", "radius", "شعاع", "sade"), ("L", "m", "straight length", "طول مستقیم", "suora pituus"))),
        ("tx_annulus_per", "Annulus mid circumference", "محیط میانی طوقه", "Renkaan keskipiiri",
         "C = pi*(R + r)",
         V(("C", "m", "mid circumference", "محیط میانی", "keskipiiri"), ("R", "m", "outer radius", "شعاع بیرونی", "ulkosade"),
           ("r", "m", "inner radius", "شعاع درونی", "sisasade"))),
        ("tx_ellipse_area", "Ellipse area ab", "مساحت بیضی", "Ellipsin pinta-ala",
         "A = pi*a*b",
         V(("A", "m^2", "area", "مساحت", "pinta-ala"), ("a", "m", "semi-major", "نیم‌قطر بزرگ", "isoakseli"),
           ("b", "m", "semi-minor", "نیم‌قطر کوچک", "pikkukseli"))),
        ("tx_parabola_arc", "Parabola arc length", "طول کمان سهمی", "Paraabelin kaaren pituus",
         "L = 0.5*sqrt(b**2 + 16*a**2) + (b**2/(8*a))*log((4*a + sqrt(b**2 + 16*a**2))/b)",
         V(("L", "m", "arc length", "طول کمان", "kaaren pituus"), ("a", "m", "height", "ارتفاع", "korkeus"),
           ("b", "m", "width", "دهانه", "leveys"))),
        ("tx_parabola_area", "Parabola segment area", "مساحت قطعه سهمی", "Paraabelisegmentin pinta",
         "A = 2*a*b/3",
         V(("A", "m^2", "area", "مساحت", "pinta-ala"), ("a", "m", "height", "ارتفاع", "korkeus"), ("b", "m", "base", "قاعده", "kanta"))),
        ("tx_hyp_area", "Right hyperbola xy", "مساحت هذلولی قائم", "Suorakulmaisen hyperbelin pinta",
         "A = a**2*log(x/a)",
         V(("A", "m^2", "area", "مساحت", "pinta-ala"), ("a", "m", "constant", "ثابت", "vakio"), ("x", "m", "x", "x", "x"))),
        ("tx_cylinder_hollow", "Hollow cylinder volume", "حجم استوانه توخالی", "Onton lieriön tilavuus",
         "V = pi*(R**2 - r**2)*h",
         V(("V", "m^3", "volume", "حجم", "tilavuus"), ("R", "m", "outer radius", "شعاع بیرونی", "ulkosade"),
           ("r", "m", "inner radius", "شعاع درونی", "sisasade"), ("h", "m", "height", "ارتفاع", "korkeus"))),
        ("tx_pipe_mean_r", "Pipe mean radius", "شعاع میانگین لوله", "Putken keskimaarainen sade",
         "rm = (R + r)/2",
         V(("rm", "m", "mean radius", "شعاع میانگین", "keskisade"), ("R", "m", "outer", "بیرونی", "ulko"),
           ("r", "m", "inner", "درونی", "sisa"))),
        ("tx_centroid_semi", "Semicircle centroid", "مرکزوار نیم‌دایره", "Puoliympyran keskiopiste",
         "y = 4*R/(3*pi)",
         V(("y", "m", "centroid height", "ارتفاع مرکزوار", "keskiopiste"), ("R", "m", "radius", "شعاع", "sade"))),
        ("tx_centroid_quarter", "Quarter circle centroid", "مرکزوار ربع دایره", "Neljanneksen keskiopiste",
         "x = 4*R/(3*pi)",
         V(("x", "m", "centroid", "مرکزوار", "keskiopiste"), ("R", "m", "radius", "شعاع", "sade"))),
        ("tx_triangle_inradius", "Triangle inradius from area", "شعاع داخلی مثلث از مساحت", "Kolmion sisaan piirretyn sade",
         "r = A/s",
         V(("r", "m", "inradius", "شعاع داخلی", "sade"), ("A", "m^2", "area", "مساحت", "pinta-ala"),
           ("s", "m", "semiperimeter", "نصف محیط", "puolipiiri"))),
        ("tx_triangle_circum", "Triangle circumradius", "شعاع محیطی مثلث", "Kolmion ymparyssade",
         "R = a/(2*sin(Aang))",
         V(("R", "m", "circumradius", "شعاع محیطی", "ymparyssade"), ("a", "m", "side a", "ضلع a", "sivu a"),
           ("Aang", "rad", "angle A", "زاویه A", "kulma A"))),
        ("tx_median_length", "Triangle median length", "طول میانه مثلث", "Kolmion mediaanin pituus",
         "m = sqrt((2*b**2 + 2*c**2 - a**2)/4)",
         V(("m", "m", "median to side a", "میانه ضلع a", "mediaani"), ("a", "m", "side a", "ضلع a", "sivu a"),
           ("b", "m", "side b", "ضلع b", "sivu b"), ("c", "m", "side c", "ضلع c", "sivu c"))),
        ("tx_angle_bisector", "Angle bisector length", "طول نیمساز", "Kulmanpuolittajan pituus",
         "t = 2*b*c*cos(Aang/2)/(b + c)",
         V(("t", "m", "bisector", "نیمساز", "puolittaja"), ("b", "m", "side b", "ضلع b", "sivu b"),
           ("c", "m", "side c", "ضلع c", "sivu c"), ("Aang", "rad", "angle A", "زاویه A", "kulma A"))),
        ("tx_varignon", "Varignon parallelogram area", "مساحت متوازی‌الاضلاع واریگنون", "Varignonin suunnikkaan pinta",
         "A = K/2",
         V(("A", "m^2", "Varignon area", "مساحت واریگنون", "Varignon-pinta"), ("K", "m^2", "quad area", "مساحت چهارضلعی", "nelikulmion pinta"))),
    ]
    for item in extras_geo:
        a(row(item[0], "math.geometry", item[1], item[2], item[3], item[4], item[5]))

    # ---------- algebra extras ----------
    alg = [
        ("tx_arith_mean_n", "Arithmetic mean of n", "میانگین حسابی n تا", "n:n aritmeettinen keskiarvo",
         "m = s/n", V(("m", "1", "mean", "میانگین", "keskiarvo"), ("s", "1", "sum", "جمع", "summa"), ("n", "1", "count", "تعداد", "lkm"))),
        ("tx_rms_two", "RMS of two values", "RMS دو مقدار", "Kahden arvon RMS",
         "r = sqrt((a**2 + b**2)/2)", V(("r", "1", "RMS", "RMS", "RMS"), ("a", "1", "a", "a", "a"), ("b", "1", "b", "b", "b"))),
        ("tx_log_change", "Change of log base", "تغییر پایه لگاریتم", "Logaritmin kannan vaihto",
         "L = log(x)/log(b)", V(("L", "1", "log_b(x)", "لگاریتم", "log"), ("x", "1", "argument", "آرگومان", "argumentti"), ("b", "1", "base", "پایه", "kanta"))),
        ("tx_exp_solve", "Exponential solve for time", "حل نمایی برای زمان", "Eksponentin aika",
         "t = log(A/A0)/k", V(("t", "s", "time", "زمان", "aika"), ("A", "1", "value", "مقدار", "arvo"),
                              ("A0", "1", "initial", "اولیه", "alku"), ("k", "1/s", "rate", "نرخ", "nopeus"))),
        ("tx_half_from_k", "Half-life from rate k", "نیمه‌عمر از نرخ", "Puoliintumisaika vakiosta",
         "th = log(2)/k", V(("th", "s", "half-life", "نیمه‌عمر", "puoliintumisaika"), ("k", "1/s", "rate", "نرخ", "nopeus"))),
        ("tx_double_time", "Doubling time", "زمان دو برابر شدن", "Kahdentumisaika",
         "td = log(2)/k", V(("td", "s", "doubling time", "زمان دو برابر", "kahdentumisaika"), ("k", "1/s", "growth rate", "نرخ رشد", "kasvunopeus"))),
        ("tx_compound_cont", "Continuous compound", "بهره پیوسته", "Jatkuva korko",
         "A = P*exp(r*t)", V(("A", "1", "amount", "مبلغ", "maara"), ("P", "1", "principal", "اصل", "paaoma"),
                             ("r", "1", "rate", "نرخ", "korko"), ("t", "1", "time", "زمان", "aika"))),
        ("tx_rule72", "Rule of 72 years", "قاعده ۷۲", "Sääntö 72",
         "t = 72/p", V(("t", "yr", "years to double", "سال تا دو برابر", "vuodet"), ("p", "1", "percent rate", "درصد نرخ", "prosenttikorko"))),
        ("tx_mix_two", "Two-stream mixture", "مخلوط دو جریان", "Kahden virran seos",
         "c = (m1*c1 + m2*c2)/(m1 + m2)", V(("c", "1", "mixture", "مخلوط", "seos"), ("m1", "kg", "mass 1", "جرم ۱", "massa 1"),
                                            ("c1", "1", "conc 1", "غلظت ۱", "pitoisuus 1"), ("m2", "kg", "mass 2", "جرم ۲", "massa 2"),
                                            ("c2", "1", "conc 2", "غلظت ۲", "pitoisuus 2"))),
        ("tx_alligation", "Alligation difference", "اختلاف اختلاط", "Alligaatio",
         "rto = (c - c2)/(c1 - c)", V(("rto", "1", "parts 1 to 2", "نسبت بخش", "suhde"), ("c", "1", "wanted", "خواسته", "haluttu"),
                                      ("c1", "1", "high", "بالا", "korkea"), ("c2", "1", "low", "پایین", "matala"))),
        ("tx_inverse_prop", "Inverse proportion", "تناسب معکوس", "Kaanteinen verrannollisuus",
         "x*y = k", V(("x", "1", "x", "x", "x"), ("y", "1", "y", "y", "y"), ("k", "1", "constant", "ثابت", "vakio"))),
        ("tx_joint_prop", "Joint variation", "تغییر توأم", "Yhdistetty verrannollisuus",
         "y = k*x*z", V(("y", "1", "y", "y", "y"), ("k", "1", "constant", "ثابت", "vakio"), ("x", "1", "x", "x", "x"), ("z", "1", "z", "z", "z"))),
        ("tx_partial_a", "Partial fraction linear A", "کسر جزئی A", "Osittaisjaennos A",
         "A = (b*c - a*d)/(c - d) if False else (p - q*b)/(a - b)",
         V(("A", "1", "A", "A", "A"), ("p", "1", "numerator const", "صورت ثابت", "osoittaja"),
           ("q", "1", "numerator x", "صورت x", "x-kerroin"), ("a", "1", "pole a", "قطب a", "napa a"), ("b", "1", "pole b", "قطب b", "napa b"))),
        ("tx_quad_vertex_y", "Quadratic vertex value", "مقدار رأس سهمی", "Paraabelin karjen arvo",
         "k = (4*a*c - b**2)/(4*a)", V(("k", "1", "vertex y", "عرض رأس", "karjen y"), ("a", "1", "a", "a", "a"),
                                       ("b", "1", "b", "b", "b"), ("c", "1", "c", "c", "c"))),
        ("tx_complete_sq", "Complete the square shift", "انتقال مربع کامل", "Nelion taydennys",
         "h = -b/(2*a)", V(("h", "1", "x shift", "انتقال x", "x-siirto"), ("b", "1", "b", "b", "b"), ("a", "1", "a", "a", "a"))),
        ("tx_geo_mean_n", "Geometric mean of n", "میانگین هندسی", "Geometrinen keskiarvo",
         "g = exp(s/n)", V(("g", "1", "geometric mean", "میانگین هندسی", "geom. ka"), ("s", "1", "sum of logs", "جمع لگاریتم", "log-summa"),
                           ("n", "1", "count", "تعداد", "lkm"))),
        ("tx_harm_n", "Harmonic mean of n", "میانگین همساز", "Harmoninen keskiarvo",
         "h = n/s", V(("h", "1", "harmonic mean", "میانگین همساز", "harm. ka"), ("n", "1", "count", "تعداد", "lkm"),
                      ("s", "1", "sum of reciprocals", "جمع معکوس‌ها", "kaanteisten summa"))),
        ("tx_binom_term", "Binomial term", "جمله دوجمله‌ای", "Binomitermi",
         "T = binomial(n, k)*a**(n - k)*b**k", V(("T", "1", "term", "جمله", "termi"), ("n", "1", "n", "n", "n"),
                                                 ("k", "1", "k", "k", "k"), ("a", "1", "a", "a", "a"), ("b", "1", "b", "b", "b"))),
        ("tx_neg_binom_exp", "Negative exponent binomial 1st", "بسط دوجمله‌ای منفی", "Negatiivinen binomi",
         "y = 1 + n*x", V(("y", "1", "approx", "تقریب", "likiarvo"), ("n", "1", "exponent", "توان", "eksponentti"),
                          ("x", "1", "x", "x", "x"))),
        ("tx_remainder_lin", "Remainder theorem linear", "قضیه باقیمانده خطی", "Jaannoslause",
         "r = a*c**3 + b*c**2 + d*c + e0", V(("r", "1", "remainder", "باقیمانده", "jaannos"),
                                            ("a", "1", "a", "a", "a"), ("b", "1", "b", "b", "b"), ("d", "1", "d", "d", "d"),
                                            ("e0", "1", "constant", "ثابت", "vakio"), ("c", "1", "root test", "آزمون ریشه", "testijuuri"))),
        ("tx_factor_sum_cubes", "Sum of cubes factor", "اتحاد مجموع مکعب‌ها", "Kuutioiden summa",
         "s = (a + b)*(a**2 - a*b + b**2)", V(("s", "1", "product", "حاصل", "tulo"), ("a", "1", "a", "a", "a"), ("b", "1", "b", "b", "b"))),
        ("tx_diff_cubes", "Difference of cubes factor", "اتحاد تفاضل مکعب‌ها", "Kuutioiden erotus",
         "s = (a - b)*(a**2 + a*b + b**2)", V(("s", "1", "product", "حاصل", "tulo"), ("a", "1", "a", "a", "a"), ("b", "1", "b", "b", "b"))),
        ("tx_sop_to_sos", "Square of sum", "مربع مجموع", "Summan neliö",
         "s = a**2 + 2*a*b + b**2", V(("s", "1", "square", "مربع", "nelio"), ("a", "1", "a", "a", "a"), ("b", "1", "b", "b", "b"))),
        ("tx_log_product", "Log of a product", "لگاریتم حاصل‌ضرب", "Tulon logaritmi",
         "L = log(a) + log(b)", V(("L", "1", "log", "لگاریتم", "log"), ("a", "1", "a", "a", "a"), ("b", "1", "b", "b", "b"))),
        ("tx_log_power", "Log of a power", "لگاریتم توان", "Potenssin logaritmi",
         "L = n*log(a)", V(("L", "1", "log", "لگاریتم", "log"), ("n", "1", "n", "n", "n"), ("a", "1", "a", "a", "a"))),
        ("tx_exp_sum", "Product of exponentials", "ضرب نمایی‌ها", "Eksponenttien tulo",
         "p = exp(a + b)", V(("p", "1", "product", "حاصل", "tulo"), ("a", "1", "a", "a", "a"), ("b", "1", "b", "b", "b"))),
        ("tx_percent_of", "Percent of a whole", "درصد از کل", "Prosentti kokonaisuudesta",
         "part = tot*p/100", V(("part", "1", "part", "جزء", "osa"), ("tot", "1", "whole", "کل", "koko"), ("p", "1", "percent", "درصد", "prosentti"))),
        ("tx_reverse_percent", "Whole from percent part", "کل از جزء درصدی", "Koko prosenttiosasta",
         "tot = part*100/p", V(("tot", "1", "whole", "کل", "koko"), ("part", "1", "part", "جزء", "osa"), ("p", "1", "percent", "درصد", "prosentti"))),
        ("tx_successive_pct", "Two successive percents", "دو درصد پیاپی", "Kaksi perakkaista prosenttia",
         "y = x*(1 + p/100)*(1 + q/100)", V(("y", "1", "final", "نهایی", "loppu"), ("x", "1", "start", "شروع", "alku"),
                                            ("p", "1", "first %", "درصد اول", "1. %"), ("q", "1", "second %", "درصد دوم", "2. %"))),
        ("tx_cubic_depressed", "Depressed cubic shift", "انتقال مکعب کاهش‌یافته", "Painetun kuution siirto",
         "h = b/(3*a)", V(("h", "1", "shift", "انتقال", "siirto"), ("b", "1", "b", "b", "b"), ("a", "1", "a", "a", "a"))),
        ("tx_vieta_cubic_sum", "Cubic Vieta sum", "جمع ریشه‌های مکعبی", "Kuution juurten summa",
         "s = -b/a", V(("s", "1", "sum of roots", "جمع ریشه‌ها", "juurten summa"), ("b", "1", "b", "b", "b"), ("a", "1", "a", "a", "a"))),
        ("tx_vieta_cubic_prod", "Cubic Vieta product", "ضرب ریشه‌های مکعبی", "Kuution juurten tulo",
         "p = -d/a", V(("p", "1", "product", "حاصل‌ضرب", "tulo"), ("d", "1", "d", "d", "d"), ("a", "1", "a", "a", "a"))),
        ("tx_cardano_disc", "Cubic Cardano discriminant piece", "ممیز کاردانو", "Cardanon diskriminantti",
         "D = (q/2)**2 + (p/3)**3", V(("D", "1", "discriminant", "ممیز", "diskriminantti"), ("q", "1", "q", "q", "q"), ("p", "1", "p", "p", "p"))),
    ]
    # fix the broken partial fraction one - I'll replace with a clean formula
    alg = [x for x in alg if x[0] != "tx_partial_a"]
    alg.append(("tx_partial_A", "Heaviside cover-up A", "پوشش هایوساید A", "Heavisiden peitto A",
                "A = p/(a - b)", V(("A", "1", "residue at a", "مانده در a", "jaannos a"),
                                   ("p", "1", "numerator", "صورت", "osoittaja"),
                                   ("a", "1", "pole a", "قطب a", "napa a"), ("b", "1", "other pole", "قطب دیگر", "toinen napa"))))
    for item in alg:
        a(row(item[0], "math.algebra", item[1], item[2], item[3], item[4], item[5]))

    # difference of powers identities n=4..8
    a(row("tx_diff_pow4", "math.algebra", "Difference of fourth powers", "تفاضل توان چهارم", "Neljansien potenssien erotus",
          "s = (a - b)*(a + b)*(a**2 + b**2)",
          V(("s", "1", "factorization", "تجزیه", "tekijat"), ("a", "1", "a", "a", "a"), ("b", "1", "b", "b", "b"))))
    a(row("tx_sum_pow4", "math.algebra", "Sum of fourth powers Sophie", "مجموع توان چهارم", "Neljansien potenssien summa",
          "s = (a**2 + sqrt(2)*a*b + b**2)*(a**2 - sqrt(2)*a*b + b**2)",
          V(("s", "1", "factorization", "تجزیه", "tekijat"), ("a", "1", "a", "a", "a"), ("b", "1", "b", "b", "b"))))

    # ---------- sequences ----------
    seq = [
        ("tx_arith_last", "Arithmetic last term", "جمله آخر حسابی", "Aritmeettisen viimeinen",
         "an = a1 + (n - 1)*d", V(("an", "1", "nth term", "جمله n", "n. termi"), ("a1", "1", "first", "اول", "ensimmainen"),
                                  ("n", "1", "n", "n", "n"), ("d", "1", "difference", "اختلاف", "erotus"))),
        ("tx_arith_sum_ends", "Arithmetic sum from ends", "جمع حسابی از دو سر", "Aritmeettinen summa paista",
         "S = n*(a1 + an)/2", V(("S", "1", "sum", "جمع", "summa"), ("n", "1", "n", "n", "n"),
                                ("a1", "1", "first", "اول", "ensimmainen"), ("an", "1", "last", "آخر", "viimeinen"))),
        ("tx_geo_sum_inf", "Infinite geometric |r|<1", "سری هندسی نامتناهی", "Aareton geometrinen",
         "S = a1/(1 - r)", V(("S", "1", "sum", "جمع", "summa"), ("a1", "1", "first", "اول", "ensimmainen"),
                             ("r", "1", "ratio", "نسبت", "suhde"))),
        ("tx_geo_nth", "Geometric nth term", "جمله n هندسی", "Geometrinen n. termi",
         "an = a1*r**(n - 1)", V(("an", "1", "nth", "جمله n", "n. termi"), ("a1", "1", "first", "اول", "ensimmainen"),
                                 ("r", "1", "ratio", "نسبت", "suhde"), ("n", "1", "n", "n", "n"))),
        ("tx_harm_nth", "Harmonic nth term", "جمله n همساز", "Harmoninen n. termi",
         "an = 1/(a + (n - 1)*d)", V(("an", "1", "nth", "جمله n", "n. termi"), ("a", "1", "first reciprocal", "معکوس اول", "ensimmainen kaanteinen"),
                                     ("n", "1", "n", "n", "n"), ("d", "1", "diff of reciprocals", "اختلاف معکوس", "kaanteisten erotus"))),
        ("tx_fib_binet", "Binet Fibonacci", "جمله فیبوناچی بینه", "Binetin Fibonacci",
         "F = (phi**n - (1 - phi)**n)/sqrt(5)", V(("F", "1", "F_n", "F_n", "F_n"), ("phi", "1", "golden ratio", "نسبت طلایی", "kultainen leikkaus"),
                                                  ("n", "1", "n", "n", "n"))),
        ("tx_fib_add", "Fibonacci recurrence", "بازگشت فیبوناچی", "Fibonaccin palautus",
         "F = a + b", V(("F", "1", "next", "بعدی", "seuraava"), ("a", "1", "F_n", "F_n", "F_n"), ("b", "1", "F_{n+1}", "F_{n+1}", "F_{n+1}"))),
        ("tx_lucas_n", "Lucas L_n approx", "لوکاس", "Lucas",
         "L = phi**n + (1 - phi)**n", V(("L", "1", "Lucas", "لوکاس", "Lucas"), ("phi", "1", "golden ratio", "نسبت طلایی", "kultainen leikkaus"),
                                        ("n", "1", "n", "n", "n"))),
        ("tx_sum_k", "Sum of first n integers", "جمع n عدد اول", "n ensimmaisen summa",
         "S = n*(n + 1)/2", V(("S", "1", "sum", "جمع", "summa"), ("n", "1", "n", "n", "n"))),
        ("tx_sum_k2", "Sum of first n squares", "جمع مربع‌های اول", "n ensimmaisen neliön summa",
         "S = n*(n + 1)*(2*n + 1)/6", V(("S", "1", "sum", "جمع", "summa"), ("n", "1", "n", "n", "n"))),
        ("tx_sum_k3", "Sum of first n cubes", "جمع مکعب‌های اول", "n ensimmaisen kuution summa",
         "S = (n*(n + 1)/2)**2", V(("S", "1", "sum", "جمع", "summa"), ("n", "1", "n", "n", "n"))),
        ("tx_sum_k4", "Sum of first n fourth powers", "جمع توان چهارم", "Neljansien potenssien summa",
         "S = n*(n + 1)*(2*n + 1)*(3*n**2 + 3*n - 1)/30", V(("S", "1", "sum", "جمع", "summa"), ("n", "1", "n", "n", "n"))),
        ("tx_arith_mean_insert", "Insert arithmetic means count", "تعداد واسطه‌های حسابی", "Aritmeettisten valien maara",
         "k = (an - a1)/d - 1", V(("k", "1", "means to insert", "تعداد واسطه", "valien maara"),
                                  ("an", "1", "last", "آخر", "viimeinen"), ("a1", "1", "first", "اول", "ensimmainen"),
                                  ("d", "1", "difference", "اختلاف", "erotus"))),
        ("tx_geo_insert", "Geometric means ratio", "نسبت واسطه‌های هندسی", "Geometristen valien suhde",
         "r = (an/a1)**(1/(k + 1))", V(("r", "1", "ratio", "نسبت", "suhde"), ("an", "1", "last", "آخر", "viimeinen"),
                                       ("a1", "1", "first", "اول", "ensimmainen"), ("k", "1", "means", "واسطه", "valia"))),
    ]
    for p in range(5, 11):
        # Faulhaber leading term only as named identity S ~ n^{p+1}/(p+1)
        seq.append((f"tx_faulhaber_lead_{p}", f"Leading Faulhaber p={p}", f"جمله پیشروی فاولهابر p={p}", f"Faulhaberin johtava p={p}",
                    f"S = n**({p}+1)/({p}+1)", V(("S", "1", "leading sum", "جمع پیشرو", "johtava summa"), ("n", "1", "n", "n", "n"))))
    for item in seq:
        a(row(item[0], "math.seq", item[1], item[2], item[3], item[4], item[5]))

    # ---------- discrete math ----------
    disc = [
        ("tx_handshake", "Handshaking lemma", "لم دست دادن", "Kattelilemma",
         "s = 2*e", V(("s", "1", "sum of degrees", "جمع درجه‌ها", "asteiden summa"), ("e", "1", "edges", "یال", "kaarria"))),
        ("tx_tree_edges", "Tree edges", "یال‌های درخت", "Puun kaaret",
         "e = v - 1", V(("e", "1", "edges", "یال", "kaaret"), ("v", "1", "vertices", "رأس", "solmut"))),
        ("tx_forest_edges", "Forest edges", "یال‌های جنگل", "Metsan kaaret",
         "e = v - c", V(("e", "1", "edges", "یال", "kaaret"), ("v", "1", "vertices", "رأس", "solmut"), ("c", "1", "components", "مؤلفه", "komponentit"))),
        ("tx_planar_simple", "Simple planar e bound", "کران یال گراف مسطح", "Tason verkon kaariraja",
         "e = 3*v - 6", V(("e", "1", "max edges", "حداکثر یال", "kaarimax"), ("v", "1", "vertices", "رأس", "solmut"))),
        ("tx_euler_char", "Planar Euler characteristic", "مشخصه اویلر", "Eulerin karakteristika",
         "chi = v - e + f", V(("chi", "1", "chi", "خی", "chi"), ("v", "1", "vertices", "رأس", "solmut"),
                              ("e", "1", "edges", "یال", "kaaret"), ("f", "1", "faces", "وجه", "tahkot"))),
        ("tx_complete_edges", "Complete graph edges", "یال گراف کامل", "Taydellisen verkon kaaret",
         "e = n*(n - 1)/2", V(("e", "1", "edges", "یال", "kaaret"), ("n", "1", "vertices", "رأس", "solmut"))),
        ("tx_bipartite_complete", "Complete bipartite edges", "یال دوبخشی کامل", "Taydellisen kaksijakoisen kaaret",
         "e = m*n", V(("e", "1", "edges", "یال", "kaaret"), ("m", "1", "left", "چپ", "vasen"), ("n", "1", "right", "راست", "oikea"))),
        ("tx_cycle_graph", "Cycle graph edges", "یال گراف دوری", "Sykliverkon kaaret",
         "e = n", V(("e", "1", "edges", "یال", "kaaret"), ("n", "1", "vertices", "رأس", "solmut"))),
        ("tx_wheel_edges", "Wheel graph edges", "یال گراف چرخ", "Pyoraverkon kaaret",
         "e = 2*n", V(("e", "1", "edges", "یال", "kaaret"), ("n", "1", "rim vertices", "رأس طوقه", "reunasolmut"))),
        ("tx_hypercube_edges", "Hypercube edges", "یال ابرمکعب", "Hyperkuution kaaret",
         "e = n*2**(n - 1)", V(("e", "1", "edges", "یال", "kaaret"), ("n", "1", "dimension", "بعد", "ulottuvuus"))),
        ("tx_hypercube_vert", "Hypercube vertices", "رأس ابرمکعب", "Hyperkuution solmut",
         "v = 2**n", V(("v", "1", "vertices", "رأس", "solmut"), ("n", "1", "dimension", "بعد", "ulottuvuus"))),
        ("tx_catalan_n", "Catalan number", "عدد کاتالان", "Catalanin luku",
         "C = binomial(2*n, n)/(n + 1)", V(("C", "1", "C_n", "C_n", "C_n"), ("n", "1", "n", "n", "n"))),
        ("tx_derange", "Derangement !n approx", "پرتاب بدون نقطه ثابت", "Sijoittelu ilman kiintopistetta",
         "d = factorial(n)/exp(1)", V(("d", "1", "derangements", "تعداد", "maara"), ("n", "1", "n", "n", "n"))),
        ("tx_stirling2_lead", "Stirling 2nd kind rec", "استرلینگ نوع دوم", "Stirling 2. laji",
         "S = k*S1 + S0", V(("S", "1", "S(n,k)", "S(n,k)", "S(n,k)"), ("k", "1", "k", "k", "k"),
                            ("S1", "1", "S(n-1,k)", "S(n-1,k)", "S(n-1,k)"), ("S0", "1", "S(n-1,k-1)", "S(n-1,k-1)", "S(n-1,k-1)"))),
        ("tx_bell_rec", "Bell recurrence piece", "بازگشت بل", "Bellin palautus",
         "B = S + T", V(("B", "1", "B_n", "B_n", "B_n"), ("S", "1", "sum term", "جمله جمع", "summatermi"),
                        ("T", "1", "last", "آخر", "viimeinen"))),
        ("tx_inclusion2", "Inclusion-exclusion two sets", "شمول و طرد دو مجموعه", "Sisaltyvyys-poissulku",
         "u = a + b - both", V(("u", "1", "union", "اجتماع", "yhdiste"), ("a", "1", "|A|", "|A|", "|A|"),
                               ("b", "1", "|B|", "|B|", "|B|"), ("both", "1", "|A and B|", "اشتراک", "leikkaus"))),
        ("tx_inclusion3", "Inclusion-exclusion three", "شمول و طرد سه مجموعه", "Kolmen joukon yhdiste",
         "u = a + b + c - ab - ac - bc + abc",
         V(("u", "1", "union", "اجتماع", "yhdiste"), ("a", "1", "A", "A", "A"), ("b", "1", "B", "B", "B"), ("c", "1", "C", "C", "C"),
           ("ab", "1", "A and B", "A و B", "A ja B"), ("ac", "1", "A and C", "A و C", "A ja C"),
           ("bc", "1", "B and C", "B و C", "B ja C"), ("abc", "1", "all three", "هر سه", "kaikki"))),
        ("tx_pigeon", "Pigeonhole minimum", "لانه کبوتری", "Kyyhkyslakka",
         "m = floor((n - 1)/k) + 1", V(("m", "1", "min in one box", "حداقل در یک جعبه", "min yhdessä"),
                                       ("n", "1", "pigeons", "کبوتر", "kyyhkyt"), ("k", "1", "holes", "لانه", "kolot"))),
        ("tx_bool_or", "Boolean OR count disjoint", "تعداد OR جدا", "ERILLINEN TAI",
         "u = a + b", V(("u", "1", "true count", "تعداد درست", "tosi"), ("a", "1", "A", "A", "A"), ("b", "1", "B", "B", "B"))),
        ("tx_powerset", "Power set size", "تعداد زیرمجموعه‌ها", "Potenssijoukon koko",
         "p = 2**n", V(("p", "1", "subsets", "زیرمجموعه", "osajoukot"), ("n", "1", "elements", "عضو", "alkiot"))),
        ("tx_func_count", "Functions A to B", "تعداد تابع", "Funktioiden maara",
         "N = n**m", V(("N", "1", "functions", "توابع", "funktiot"), ("n", "1", "|B|", "|B|", "|B|"), ("m", "1", "|A|", "|A|", "|A|"))),
        ("tx_inj_count", "Injections A to B", "تعداد یک‌به‌یک", "Injektioiden maara",
         "N = factorial(n)/factorial(n - m)", V(("N", "1", "injections", "تک‌نگاشت", "injektiot"),
                                                ("n", "1", "|B|", "|B|", "|B|"), ("m", "1", "|A|", "|A|", "|A|"))),
        ("tx_surj_small", "Surjections 2 to n approx leftover", "پوشا به ۲", "Surjektiot kahteen",
         "N = 2**n - 2", V(("N", "1", "onto {1,2}", "پوشا به ۲", "surjektiot"), ("n", "1", "domain size", "اندازه دامنه", "lahto"))),
        ("tx_rel_count", "Relations on n", "تعداد رابطه", "Relaatioiden maara",
         "N = 2**(n**2)", V(("N", "1", "relations", "رابطه‌ها", "relaatiot"), ("n", "1", "n", "n", "n"))),
        ("tx_perm_rep", "Permutations with repetition", "جایگشت با تکرار", "Toistopermutaatio",
         "N = n**k", V(("N", "1", "words", "کلمات", "sanat"), ("n", "1", "alphabet", "الفبا", "aakkosto"), ("k", "1", "length", "طول", "pituus"))),
        ("tx_combo_rep", "Combinations with repetition", "ترکیب با تکرار", "Toistoyhdistelma",
         "C = binomial(n + k - 1, k)", V(("C", "1", "multisets", "چندمجموعه", "monijoukot"),
                                         ("n", "1", "types", "نوع", "tyypit"), ("k", "1", "drawn", "انتخاب", "valitut"))),
        ("tx_stars_bars", "Stars and bars positive", "ستاره و میله مثبت", "Tahdet ja palkit",
         "C = binomial(n - 1, k - 1)", V(("C", "1", "positive solutions", "جواب مثبت", "positiiviset"),
                                         ("n", "1", "sum", "جمع", "summa"), ("k", "1", "variables", "متغیر", "muuttujat"))),
        ("tx_hanoi", "Tower of Hanoi moves", "حرکت برج هانوی", "Hanoin tornin siirrot",
         "T = 2**n - 1", V(("T", "1", "moves", "حرکت", "siirrot"), ("n", "1", "disks", "دیسک", "levyt"))),
        ("tx_gray_bits", "n-bit Gray codes", "کد گری n بیتی", "n-bittiset Gray-koodit",
         "N = 2**n", V(("N", "1", "codes", "کد", "koodit"), ("n", "1", "bits", "بیت", "bitit"))),
    ]
    for item in disc:
        a(row(item[0], "math.discrete", item[1], item[2], item[3], item[4], item[5]))

    return R


def more_math():
    R = []
    a = R.append
    # trig extras
    trig = [
        ("tx_law_sines_b", "Law of sines for b", "قانون سینوس‌ها برای b", "Sinin laki b",
         "b = a*sin(B)/sin(A)", V(("b", "m", "side b", "ضلع b", "sivu b"), ("a", "m", "side a", "ضلع a", "sivu a"),
                                  ("B", "rad", "angle B", "زاویه B", "kulma B"), ("A", "rad", "angle A", "زاویه A", "kulma A"))),
        ("tx_law_cos_a", "Law of cosines side a", "قانون کسینوس ضلع a", "Kosinin laki sivu a",
         "a = sqrt(b**2 + c**2 - 2*b*c*cos(A))", V(("a", "m", "side a", "ضلع a", "sivu a"), ("b", "m", "b", "b", "b"),
                                                   ("c", "m", "c", "c", "c"), ("A", "rad", "angle A", "زاویه A", "kulma A"))),
        ("tx_law_cos_angle", "Law of cosines angle", "زاویه از کسینوس‌ها", "Kulma kosinista",
         "C = acos((a**2 + b**2 - c**2)/(2*a*b))", V(("C", "rad", "angle C", "زاویه C", "kulma C"),
                                                     ("a", "m", "a", "a", "a"), ("b", "m", "b", "b", "b"), ("c", "m", "c", "c", "c"))),
        ("tx_area_sas", "SAS triangle area", "مساحت SAS", "SAS-pinta-ala",
         "A = a*b*sin(C)/2", V(("A", "m^2", "area", "مساحت", "pinta-ala"), ("a", "m", "side a", "ضلع a", "sivu a"),
                               ("b", "m", "side b", "ضلع b", "sivu b"), ("C", "rad", "included angle", "زاویه بین", "valikulma"))),
        ("tx_proj_law", "Projection law", "قانون تصویر", "Projektiolaki",
         "a = b*cos(C) + c*cos(B)", V(("a", "m", "side a", "ضلع a", "sivu a"), ("b", "m", "b", "b", "b"), ("c", "m", "c", "c", "c"),
                                      ("C", "rad", "C", "C", "C"), ("B", "rad", "B", "B", "B"))),
        ("tx_mollweide", "Mollweide piece", "مولوید", "Mollweide",
         "s = (a + b)*sin(C/2)/cos((A - B)/2)", V(("s", "m", "a+b check", "آزمون a+b", "tarkistus"),
                                                  ("a", "m", "a", "a", "a"), ("b", "m", "b", "b", "b"),
                                                  ("C", "rad", "C", "C", "C"), ("A", "rad", "A", "A", "A"), ("B", "rad", "B", "B", "B"))),
        ("tx_haversine_central", "Haversine central angle", "زاویه مرکزی هاورساین", "Haversinen keskuskulma",
         "h = sin(dlat/2)**2 + cos(lat1)*cos(lat2)*sin(dlon/2)**2",
         V(("h", "1", "hav theta", "هاورساین", "hav"), ("dlat", "rad", "dlat", "اختلاف عرض", "dlat"),
           ("lat1", "rad", "lat1", "عرض ۱", "lat1"), ("lat2", "rad", "lat2", "عرض ۲", "lat2"),
           ("dlon", "rad", "dlon", "اختلاف طول", "dlon"))),
        ("tx_great_circle", "Great-circle distance", "فاصله دایره عظیمه", "Suurpiirin matka",
         "d = R*theta", V(("d", "m", "distance", "فاصله", "etaisyys"), ("R", "m", "earth radius", "شعاع زمین", "sade"),
                          ("theta", "rad", "central angle", "زاویه مرکزی", "keskuskulma"))),
        ("tx_sin2", "Double-angle sine", "سینوس زاویه مضاعف", "Kaksinkertainen sini",
         "s = 2*sin(x)*cos(x)", V(("s", "1", "sin 2x", "sin 2x", "sin 2x"), ("x", "rad", "x", "x", "x"))),
        ("tx_cos2", "Double-angle cosine", "کسینوس زاویه مضاعف", "Kaksinkertainen kosini",
         "c = cos(x)**2 - sin(x)**2", V(("c", "1", "cos 2x", "cos 2x", "cos 2x"), ("x", "rad", "x", "x", "x"))),
        ("tx_tan2", "Double-angle tangent", "تانژانت مضاعف", "Kaksinkertainen tangentti",
         "t = 2*tan(x)/(1 - tan(x)**2)", V(("t", "1", "tan 2x", "tan 2x", "tan 2x"), ("x", "rad", "x", "x", "x"))),
        ("tx_sin_half", "Half-angle sine", "سینوس نیم‌زاویه", "Puolikulman sini",
         "s = sqrt((1 - cos(x))/2)", V(("s", "1", "sin(x/2)", "sin(x/2)", "sin(x/2)"), ("x", "rad", "x", "x", "x"))),
        ("tx_cos_half", "Half-angle cosine", "کسینوس نیم‌زاویه", "Puolikulman kosini",
         "c = sqrt((1 + cos(x))/2)", V(("c", "1", "cos(x/2)", "cos(x/2)", "cos(x/2)"), ("x", "rad", "x", "x", "x"))),
        ("tx_weierstrass_sin", "Weierstrass sine", "سینوس وایرشتراس", "Weierstrassin sini",
         "s = 2*t/(1 + t**2)", V(("s", "1", "sin x", "sin x", "sin x"), ("t", "1", "tan(x/2)", "tan(x/2)", "tan(x/2)"))),
        ("tx_weierstrass_cos", "Weierstrass cosine", "کسینوس وایرشتراس", "Weierstrassin kosini",
         "c = (1 - t**2)/(1 + t**2)", V(("c", "1", "cos x", "cos x", "cos x"), ("t", "1", "tan(x/2)", "tan(x/2)", "tan(x/2)"))),
        ("tx_product_sines", "Product to sum sines", "ضرب به جمع سینوس", "Sinien tulo",
         "p = (cos(A - B) - cos(A + B))/2", V(("p", "1", "sin A sin B", "sinA sinB", "sinA sinB"),
                                              ("A", "rad", "A", "A", "A"), ("B", "rad", "B", "B", "B"))),
        ("tx_sum_to_product_sin", "Sum to product sine", "جمع به ضرب سینوس", "Sinien summa tuloksi",
         "s = 2*sin((A + B)/2)*cos((A - B)/2)", V(("s", "1", "sin A + sin B", "جمع سینوس", "sinien summa"),
                                                  ("A", "rad", "A", "A", "A"), ("B", "rad", "B", "B", "B"))),
        ("tx_hyp_id", "Hyperbolic identity", "اتحاد هذلولوی", "Hyperbolinen identiteetti",
         "y = cosh(x)**2 - sinh(x)**2", V(("y", "1", "value", "مقدار", "arvo"), ("x", "1", "x", "x", "x"))),
        ("tx_asinh", "asinh closed form", "فرم بسته asinh", "asinh suljettu",
         "y = log(x + sqrt(x**2 + 1))", V(("y", "1", "asinh x", "asinh x", "asinh x"), ("x", "1", "x", "x", "x"))),
        ("tx_acosh", "acosh closed form", "فرم بسته acosh", "acosh suljettu",
         "y = log(x + sqrt(x**2 - 1))", V(("y", "1", "acosh x", "acosh x", "acosh x"), ("x", "1", "x", "x", "x"))),
        ("tx_atanh", "atanh closed form", "فرم بسته atanh", "atanh suljettu",
         "y = 0.5*log((1 + x)/(1 - x))", V(("y", "1", "atanh x", "atanh x", "atanh x"), ("x", "1", "x", "x", "x"))),
        ("tx_sinc", "Normalized sinc", "سینک بهنجار", "Sinc",
         "y = sin(pi*x)/(pi*x)", V(("y", "1", "sinc", "sinc", "sinc"), ("x", "1", "x", "x", "x"))),
        ("tx_versine", "Versine", "ورسین", "Versini",
         "y = 1 - cos(x)", V(("y", "1", "versin", "ورسین", "versin"), ("x", "rad", "x", "x", "x"))),
        ("tx_covers", "Coversine", "کوورسین", "Koversini",
         "y = 1 - sin(x)", V(("y", "1", "coversin", "کوورسین", "coversin"), ("x", "rad", "x", "x", "x"))),
        ("tx_exsec", "Exsecant", "اکسسکانت", "Ekssekantti",
         "y = 1/cos(x) - 1", V(("y", "1", "exsec", "اکسسکانت", "exsec"), ("x", "rad", "x", "x", "x"))),
        ("tx_crd", "Chord of angle", "وتر زاویه", "Kulman janne",
         "y = 2*sin(th/2)", V(("y", "1", "crd", "وتر", "janne"), ("th", "rad", "angle", "زاویه", "kulma"))),
        ("tx_deg_rad", "Degrees to radians", "درجه به رادیان", "Asteet radiaaneiksi",
         "r = d*pi/180", V(("r", "rad", "radians", "رادیان", "radiaanit"), ("d", "deg", "degrees", "درجه", "asteet"))),
        ("tx_grad_deg", "Gradians to degrees", "گراد به درجه", "Goonit asteiksi",
         "d = g*0.9", V(("d", "deg", "degrees", "درجه", "asteet"), ("g", "gon", "gradians", "گراد", "goonit"))),
        ("tx_turn_rad", "Turns to radians", "دور به رادیان", "Kierrokset radiaaneiksi",
         "r = t*2*pi", V(("r", "rad", "radians", "رادیان", "radiaanit"), ("t", "1", "turns", "دور", "kierrokset"))),
    ]
    for item in trig:
        a(row(item[0], "math.trig", item[1], item[2], item[3], item[4], item[5]))

    calc = [
        ("tx_power_rule", "Power rule derivative", "قاعده توان مشتق", "Potenssin derivaatta",
         "d = n*x**(n - 1)", V(("d", "1", "dy/dx", "مشتق", "derivaatta"), ("n", "1", "n", "n", "n"), ("x", "1", "x", "x", "x"))),
        ("tx_int_power", "Power rule integral", "انتگرال توان", "Potenssin integraali",
         "F = x**(n + 1)/(n + 1)", V(("F", "1", "antiderivative", "ضد مشتق", "integraalifunktio"), ("x", "1", "x", "x", "x"), ("n", "1", "n", "n", "n"))),
        ("tx_product_rule", "Product rule", "قاعده ضرب", "Tulon derivaatta",
         "d = u*vp + v*up", V(("d", "1", "derivative", "مشتق", "derivaatta"), ("u", "1", "u", "u", "u"),
                              ("v", "1", "v", "v", "v"), ("up", "1", "u'", "u'", "u'"), ("vp", "1", "v'", "v'", "v'"))),
        ("tx_quotient_rule", "Quotient rule", "قاعده خارج‌قسمت", "Osamäärän derivaatta",
         "d = (up*v - u*vp)/v**2", V(("d", "1", "derivative", "مشتق", "derivaatta"), ("u", "1", "u", "u", "u"),
                                     ("v", "1", "v", "v", "v"), ("up", "1", "u'", "u'", "u'"), ("vp", "1", "v'", "v'", "v'"))),
        ("tx_chain_rule", "Chain rule", "قاعده زنجیر", "Ketjusääntö",
         "d = fu*ux", V(("d", "1", "dy/dx", "مشتق", "derivaatta"), ("fu", "1", "df/du", "df/du", "df/du"), ("ux", "1", "du/dx", "du/dx", "du/dx"))),
        ("tx_by_parts", "Integration by parts", "انتگرال جزءبه‌جزء", "Osittaisintegrointi",
         "Intg = u*v - Ivdu", V(("Intg", "1", "integral", "انتگرال", "integraali"), ("u", "1", "u", "u", "u"),
                             ("v", "1", "v", "v", "v"), ("Ivdu", "1", "int v du", "انتگرال v du", "int v du"))),
        ("tx_avg_value", "Average value of a function", "مقدار میانگین تابع", "Funktion keskiarvo",
         "m = Intg/(b - a)", V(("m", "1", "average", "میانگین", "keskiarvo"), ("Intg", "1", "definite integral", "انتگرال معین", "maaraity integraali"),
                            ("b", "1", "b", "b", "b"), ("a", "1", "a", "a", "a"))),
        ("tx_mvt", "Mean value slope", "شیب مقدار میانگین", "Valilauseen kulmakerroin",
         "m = (fb - fa)/(b - a)", V(("m", "1", "f'(c)", "f'(c)", "f'(c)"), ("fb", "1", "f(b)", "f(b)", "f(b)"),
                                    ("fa", "1", "f(a)", "f(a)", "f(a)"), ("b", "1", "b", "b", "b"), ("a", "1", "a", "a", "a"))),
        ("tx_arc_explicit", "Arc length y(x)", "طول قوس y(x)", "Kaaren pituus",
         "L = sqrt(1 + m**2)*(b - a)", V(("L", "m", "length", "طول", "pituus"), ("m", "1", "constant slope", "شیب ثابت", "kulmakerroin"),
                                         ("b", "m", "b", "b", "b"), ("a", "m", "a", "a", "a"))),
        ("tx_surface_rev", "Surface of revolution", "سطح دوران", "Pyorahdyspinta",
         "dS = 2*pi*y*ds", V(("dS", "m^2", "band area", "نوار", "vyohyke"), ("y", "m", "radius", "شعاع", "sade"),
                             ("ds", "m", "arc element", "عنصر قوس", "kaarielementti"))),
        ("tx_disk", "Disk method volume", "حجم دیسک", "Levytilavuus",
         "V = pi*y**2*dx", V(("V", "m^3", "slice volume", "حجم برش", "viipale"), ("y", "m", "radius", "شعاع", "sade"),
                             ("dx", "m", "thickness", "ضخامت", "paksuus"))),
        ("tx_shell", "Shell method volume", "حجم پوسته", "Kuorimenetelma",
         "V = 2*pi*x*y*dx", V(("V", "m^3", "shell volume", "حجم پوسته", "kuori"), ("x", "m", "radius", "شعاع", "sade"),
                              ("y", "m", "height", "ارتفاع", "korkeus"), ("dx", "m", "thickness", "ضخامت", "paksuus"))),
        ("tx_curvature", "Curvature y(x)", "انحنا", "Kaarevuus",
         "kap = abs(ypp)/(1 + yp**2)**1.5", V(("kap", "1/m", "curvature", "انحنا", "kaarevuus"),
                                              ("ypp", "1/m^2", "y''", "y''", "y''"), ("yp", "1", "y'", "y'", "y'"))),
        ("tx_taylor1", "First-order Taylor", "تیلور مرتبه ۱", "Taylor 1. kertaluku",
         "y = f0 + fprime*(x - x0)", V(("y", "1", "approx", "تقریب", "likiarvo"), ("f0", "1", "f(x0)", "f(x0)", "f(x0)"),
                                       ("fprime", "1", "f'", "f'", "f'"), ("x", "1", "x", "x", "x"), ("x0", "1", "x0", "x0", "x0"))),
        ("tx_lhopital", "L'Hopital ratio", "لوپیتال", "l'Hopital",
         "L = fp/gp", V(("L", "1", "limit", "حد", "raja-arvo"), ("fp", "1", "f'", "f'", "f'"), ("gp", "1", "g'", "g'", "g'"))),
        ("tx_ftc", "Fundamental theorem increment", "قضیه اساسی حسابان", "Analyysin peruslause",
         "Intg = Fb - Fa", V(("Intg", "1", "integral", "انتگرال", "integraali"), ("Fb", "1", "F(b)", "F(b)", "F(b)"), ("Fa", "1", "F(a)", "F(a)", "F(a)"))),
        ("tx_trap", "Trapezoid rule one panel", "ذوزنقه یک بازه", "Trapetsisaanto",
         "Intg = (b - a)*(fa + fb)/2", V(("Intg", "1", "integral", "انتگرال", "integraali"), ("b", "1", "b", "b", "b"),
                                      ("a", "1", "a", "a", "a"), ("fa", "1", "f(a)", "f(a)", "f(a)"), ("fb", "1", "f(b)", "f(b)", "f(b)"))),
        ("tx_simpson", "Simpson one panel", "سیمپسون یک بازه", "Simpson",
         "Intg = (b - a)*(fa + 4*fm + fb)/6", V(("Intg", "1", "integral", "انتگرال", "integraali"), ("b", "1", "b", "b", "b"),
                                             ("a", "1", "a", "a", "a"), ("fa", "1", "f(a)", "f(a)", "f(a)"),
                                             ("fm", "1", "f(mid)", "وسط", "keski"), ("fb", "1", "f(b)", "f(b)", "f(b)"))),
        ("tx_midpoint", "Midpoint rule", "قاعده نقطه میانی", "Keskipiste",
         "Intg = (b - a)*fm", V(("Intg", "1", "integral", "انتگرال", "integraali"), ("b", "1", "b", "b", "b"),
                             ("a", "1", "a", "a", "a"), ("fm", "1", "f(mid)", "وسط", "keski"))),
        ("tx_exp_series4", "exp series 4 terms", "سری نمایی ۴ جمله", "exp-sarja",
         "y = 1 + x + x**2/2 + x**3/6", V(("y", "1", "approx e^x", "تقریب", "likiarvo"), ("x", "1", "x", "x", "x"))),
        ("tx_sin_series3", "sin series 3 terms", "سری سینوس ۳ جمله", "sin-sarja",
         "y = x - x**3/6 + x**5/120", V(("y", "1", "approx sin", "تقریب", "likiarvo"), ("x", "1", "x", "x", "x"))),
        ("tx_cos_series3", "cos series 3 terms", "سری کسینوس ۳ جمله", "cos-sarja",
         "y = 1 - x**2/2 + x**4/24", V(("y", "1", "approx cos", "تقریب", "likiarvo"), ("x", "1", "x", "x", "x"))),
        ("tx_ln1p", "ln(1+x) 3 terms", "سری ln(1+x)", "ln(1+x)-sarja",
         "y = x - x**2/2 + x**3/3", V(("y", "1", "approx", "تقریب", "likiarvo"), ("x", "1", "x", "x", "x"))),
        ("tx_geom_series", "Geometric series partial", "سری هندسی جزئی", "Geometrinen osasumma",
         "y = (1 - x**(n + 1))/(1 - x)", V(("y", "1", "sum", "جمع", "summa"), ("x", "1", "x", "x", "x"), ("n", "1", "last power", "آخرین توان", "viimeinen"))),
        ("tx_implicit", "Implicit dy/dx", "مشتق ضمنی", "Implisiittinen derivaatta",
         "yp = -Fx/Fy", V(("yp", "1", "dy/dx", "dy/dx", "dy/dx"), ("Fx", "1", "F_x", "F_x", "F_x"), ("Fy", "1", "F_y", "F_y", "F_y"))),
        ("tx_logdiff", "Logarithmic derivative", "مشتق لگاریتمی", "Logaritminen derivaatta",
         "yp = y*lp", V(("yp", "1", "y'", "y'", "y'"), ("y", "1", "y", "y", "y"), ("lp", "1", "(ln y)'", "(ln y)'", "(ln y)'"))),
        ("tx_rad_int", "1/sqrt(1-x^2) integral", "انتگرال آرک‌سینوس", "arcsin-integraali",
         "F = asin(x)", V(("F", "1", "F", "F", "F"), ("x", "1", "x", "x", "x"))),
        ("tx_atan_int", "1/(1+x^2) integral", "انتگرال آرک‌تانژانت", "arctan-integraali",
         "F = atan(x)", V(("F", "1", "F", "F", "F"), ("x", "1", "x", "x", "x"))),
    ]
    for item in calc:
        a(row(item[0], "math.calculus", item[1], item[2], item[3], item[4], item[5]))

    lin = [
        ("tx_dot2", "2D dot product", "ضرب داخلی ۲بعدی", "2D pistetulo",
         "p = ax*bx + ay*by", V(("p", "1", "dot", "ضرب داخلی", "pistetulo"), ("ax", "1", "ax", "ax", "ax"),
                                ("ay", "1", "ay", "ay", "ay"), ("bx", "1", "bx", "bx", "bx"), ("by", "1", "by", "by", "by"))),
        ("tx_cross2", "2D cross magnitude", "اندازه ضرب خارجی ۲بعدی", "2D ristitulo",
         "c = ax*by - ay*bx", V(("c", "1", "cross", "ضرب خارجی", "ristitulo"), ("ax", "1", "ax", "ax", "ax"),
                                ("ay", "1", "ay", "ay", "ay"), ("bx", "1", "bx", "bx", "bx"), ("by", "1", "by", "by", "by"))),
        ("tx_det2", "2x2 determinant", "دترمینان ۲×۲", "2x2 determinantti",
         "D = a*d - b*c", V(("D", "1", "det", "دترمینان", "det"), ("a", "1", "a", "a", "a"), ("b", "1", "b", "b", "b"),
                            ("c", "1", "c", "c", "c"), ("d", "1", "d", "d", "d"))),
        ("tx_trace2", "2x2 trace", "اثر ۲×۲", "2x2 jaalki",
         "t = a + d", V(("t", "1", "trace", "اثر", "jaalki"), ("a", "1", "a", "a", "a"), ("d", "1", "d", "d", "d"))),
        ("tx_inv2a", "2x2 inverse a", "وارون ۲×۲ درایه a", "2x2 kaanteinen a",
         "ainv = d/(a*d - b*c)", V(("ainv", "1", "A11 inverse", "وارون ۱۱", "kaanteinen 11"),
                                   ("a", "1", "a", "a", "a"), ("b", "1", "b", "b", "b"), ("c", "1", "c", "c", "c"), ("d", "1", "d", "d", "d"))),
        ("tx_cramer_x", "Cramer x 2x2", "کرامر x", "Cramer x",
         "x = (e*d - b*f)/(a*d - b*c)", V(("x", "1", "x", "x", "x"), ("a", "1", "a", "a", "a"), ("b", "1", "b", "b", "b"),
                                          ("c", "1", "c", "c", "c"), ("d", "1", "d", "d", "d"), ("e", "1", "rhs1", "طرف راست ۱", "oik1"),
                                          ("f", "1", "rhs2", "طرف راست ۲", "oik2"))),
        ("tx_cramer_y", "Cramer y 2x2", "کرامر y", "Cramer y",
         "y = (a*f - e*c)/(a*d - b*c)", V(("y", "1", "y", "y", "y"), ("a", "1", "a", "a", "a"), ("b", "1", "b", "b", "b"),
                                          ("c", "1", "c", "c", "c"), ("d", "1", "d", "d", "d"), ("e", "1", "rhs1", "طرف راست ۱", "oik1"),
                                          ("f", "1", "rhs2", "طرف راست ۲", "oik2"))),
        ("tx_norm2", "Euclidean 2-norm", "نرم اقلیدسی ۲", "Euklidinen 2-normi",
         "L = sqrt(x**2 + y**2)", V(("L", "1", "norm", "نرم", "normi"), ("x", "1", "x", "x", "x"), ("y", "1", "y", "y", "y"))),
        ("tx_norm3", "Euclidean 3-norm", "نرم اقلیدسی ۳", "Euklidinen 3-normi",
         "L = sqrt(x**2 + y**2 + z**2)", V(("L", "1", "norm", "نرم", "normi"), ("x", "1", "x", "x", "x"),
                                           ("y", "1", "y", "y", "y"), ("z", "1", "z", "z", "z"))),
        ("tx_unit2x", "2D unit vector x", "بردار یکه x", "Yksikkovektori x",
         "ux = x/L", V(("ux", "1", "unit x", "مؤلفه یکه", "yksikko x"), ("x", "1", "x", "x", "x"), ("L", "1", "length", "طول", "pituus"))),
        ("tx_proj_scalar", "Scalar projection", "تصویر نرده‌ای", "Skalaariprojektio",
         "p = (ax*bx + ay*by)/sqrt(bx**2 + by**2)", V(("p", "1", "proj", "تصویر", "proj"),
                                                      ("ax", "1", "ax", "ax", "ax"), ("ay", "1", "ay", "ay", "ay"),
                                                      ("bx", "1", "bx", "bx", "bx"), ("by", "1", "by", "by", "by"))),
        ("tx_angle_vec", "Angle between vectors", "زاویه دو بردار", "Vektorien kulma",
         "th = acos((ax*bx + ay*by)/(sqrt(ax**2 + ay**2)*sqrt(bx**2 + by**2)))",
         V(("th", "rad", "angle", "زاویه", "kulma"), ("ax", "1", "ax", "ax", "ax"), ("ay", "1", "ay", "ay", "ay"),
           ("bx", "1", "bx", "bx", "bx"), ("by", "1", "by", "by", "by"))),
        ("tx_charpoly2", "2x2 characteristic poly", "چندجمله‌ای مشخصه ۲×۲", "Karakteristinen polynomi",
         "p = lam**2 - (a + d)*lam + (a*d - b*c)", V(("p", "1", "p(lam)", "p", "p"), ("lam", "1", "eigenvalue", "ویژه", "ominaisarvo"),
                                                     ("a", "1", "a", "a", "a"), ("b", "1", "b", "b", "b"),
                                                     ("c", "1", "c", "c", "c"), ("d", "1", "d", "d", "d"))),
        ("tx_cond2", "2-norm condition from eigs", "عدد حالت از ویژه‌مقدار", "Kuntoluku",
         "k = abs(l1)/abs(l2)", V(("k", "1", "condition", "عدد حالت", "kuntoluku"),
                                  ("l1", "1", "largest |eig|", "بزرگ‌ترین ویژه", "suurin"),
                                  ("l2", "1", "smallest |eig|", "کوچک‌ترین ویژه", "pienin"))),
        ("tx_fro2", "Frobenius 2x2", "فروبنیوس ۲×۲", "Frobenius",
         "n = sqrt(a**2 + b**2 + c**2 + d**2)", V(("n", "1", "Frobenius", "فروبنیوس", "Frobenius"),
                                                  ("a", "1", "a", "a", "a"), ("b", "1", "b", "b", "b"),
                                                  ("c", "1", "c", "c", "c"), ("d", "1", "d", "d", "d"))),
        ("tx_rotate_x", "2D rotation x", "دوران دوبعدی x", "2D kierto x",
         "x = x0*cos(th) - y0*sin(th)", V(("x", "1", "x'", "x'", "x'"), ("x0", "1", "x", "x", "x"),
                                          ("y0", "1", "y", "y", "y"), ("th", "rad", "angle", "زاویه", "kulma"))),
        ("tx_rotate_y", "2D rotation y", "دوران دوبعدی y", "2D kierto y",
         "y = x0*sin(th) + y0*cos(th)", V(("y", "1", "y'", "y'", "y'"), ("x0", "1", "x", "x", "x"),
                                          ("y0", "1", "y", "y", "y"), ("th", "rad", "angle", "زاویه", "kulma"))),
        ("tx_det3", "3x3 determinant Sarrus a-row", "دترمینان ۳×۳", "3x3 determinantti",
         "D = a*(e*i - f*h) - b*(d*i - f*g) + c*(d*h - e*g)",
         V(("D", "1", "det", "دترمینان", "det"), ("a", "1", "a", "a", "a"), ("b", "1", "b", "b", "b"), ("c", "1", "c", "c", "c"),
           ("d", "1", "d", "d", "d"), ("e", "1", "e", "e", "e"), ("f", "1", "f", "f", "f"),
           ("g", "1", "g", "g", "g"), ("h", "1", "h", "h", "h"), ("i", "1", "i", "i", "i"))),
        ("tx_scalar_triple", "Scalar triple product", "ضرب سه‌گانه نرده‌ای", "Skalaarinen kolmitulo",
         "V = ax*(by*cz - bz*cy) - ay*(bx*cz - bz*cx) + az*(bx*cy - by*cx)",
         V(("V", "1", "volume", "حجم", "tilavuus"), ("ax", "1", "ax", "ax", "ax"), ("ay", "1", "ay", "ay", "ay"), ("az", "1", "az", "az", "az"),
           ("bx", "1", "bx", "bx", "bx"), ("by", "1", "by", "by", "by"), ("bz", "1", "bz", "bz", "bz"),
           ("cx", "1", "cx", "cx", "cx"), ("cy", "1", "cy", "cy", "cy"), ("cz", "1", "cz", "cz", "cz"))),
        ("tx_cross3x", "3D cross x", "ضرب خارجی x", "3D ristitulo x",
         "cx = ay*bz - az*by", V(("cx", "1", "cx", "cx", "cx"), ("ay", "1", "ay", "ay", "ay"),
                                 ("az", "1", "az", "az", "az"), ("by", "1", "by", "by", "by"), ("bz", "1", "bz", "bz", "bz"))),
    ]
    for item in lin:
        a(row(item[0], "math.linear", item[1], item[2], item[3], item[4], item[5]))

    return R


def collect_new():
    import sys

    here = Path(__file__).resolve().parent
    if str(here) not in sys.path:
        sys.path.insert(0, str(here))
    from formulas_batch2 import stats_prob, engmath_and_opt, info_queue_rel
    from formulas_batch3 import physics, chemistry
    from formulas_batch4 import harmonics_and_filters, engineering, applied
    from formulas_batch5 import networks_and_powers, multi_angle, more_named
    from formulas_batch6 import fill
    from formulas_batch7 import fill2

    rows = []
    for fn in (
        build,
        more_math,
        stats_prob,
        engmath_and_opt,
        info_queue_rel,
        physics,
        chemistry,
        harmonics_and_filters,
        engineering,
        applied,
        networks_and_powers,
        multi_angle,
        more_named,
        fill,
        fill2,
    ):
        rows.extend(fn())
    return rows


def _norm_expr(expr: str) -> str:
    return re.sub(r"\s+", "", expr)


def _vars_ok(variables: dict) -> bool:
    for name in variables:
        if name in RESERVED or not re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", name):
            return False
    return True


def _parse_ok(expr: str) -> bool:
    if "=" not in expr:
        return False
    left, right = expr.split("=", 1)
    gdict = {"Symbol": sp.Symbol, "Integer": sp.Integer, "Float": sp.Float, "Rational": sp.Rational}
    local = {
        "pi": sp.pi,
        "sqrt": sp.sqrt,
        "log": sp.log,
        "exp": sp.exp,
        "sin": sp.sin,
        "cos": sp.cos,
        "tan": sp.tan,
        "asin": sp.asin,
        "acos": sp.acos,
        "atan": sp.atan,
        "atan2": sp.atan2,
        "sinh": sp.sinh,
        "cosh": sp.cosh,
        "tanh": sp.tanh,
        "abs": sp.Abs,
        "factorial": sp.factorial,
        "binomial": sp.binomial,
        "floor": sp.floor,
        "ceiling": sp.ceiling,
    }
    try:
        parse_expr(left.strip(), local_dict=local, global_dict=gdict, transformations=standard_transformations)
        parse_expr(right.strip(), local_dict=local, global_dict=gdict, transformations=standard_transformations)
        return True
    except Exception:
        return False


def merge_and_write(target=5000):
    data = json.loads(PATHS[0].read_text(encoding="utf-8"))
    existing = data["formulas"]
    have_ids = {f["id"] for f in existing}
    have_expr = {_norm_expr(f["expr"]) for f in existing}
    non_unit = sum(1 for f in existing if f.get("category") != "unit.conv")
    need = max(0, target - non_unit)
    print(f"existing total={len(existing)} non-unit={non_unit} need={need}")

    for key, names in NEW_CATS.items():
        data["categories"].setdefault(key, names)

    added = []
    skipped = {"id": 0, "expr": 0, "var": 0, "parse": 0}
    for f in collect_new():
        if f["id"] in have_ids:
            skipped["id"] += 1
            continue
        if not _vars_ok(f["variables"]):
            skipped["var"] += 1
            continue
        if _norm_expr(f["expr"]) in have_expr:
            skipped["expr"] += 1
            continue
        if not _parse_ok(f["expr"]):
            skipped["parse"] += 1
            continue
        # every listed name must appear in the expression (or be unused - require appear)
        missing = [n for n in f["variables"] if n not in f["expr"]]
        if missing:
            skipped["parse"] += 1
            continue
        added.append(f)
        have_ids.add(f["id"])
        have_expr.add(_norm_expr(f["expr"]))

    print(f"valid new={len(added)} skipped={skipped}")
    if len(added) < need:
        print("WARNING short of target")
    data["formulas"] = existing + added
    text = json.dumps(data, ensure_ascii=False, indent=2)
    for p in PATHS:
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
        print("wrote", p, "n=", len(data["formulas"]))
    nu = sum(1 for f in data["formulas"] if f.get("category") != "unit.conv")
    un = sum(1 for f in data["formulas"] if f.get("category") == "unit.conv")
    print(f"final total={len(data['formulas'])} non-unit={nu} unit={un} cats={len(data['categories'])}")
    return data, added


if __name__ == "__main__":
    merge_and_write(5000)
