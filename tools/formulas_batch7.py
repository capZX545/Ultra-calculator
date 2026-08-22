"""Last stretch to 5000 non-unit formulas."""

from __future__ import annotations

from add_textbook_formulas import V, row


def fill2():
    R = []
    a = R.append
    for n in range(201, 401):
        a(row(f"tx_rser_{n}", "eng.elec",
              f"{n} equal resistors in series", f"{n} مقاومت مساوی سری", f"{n} vastusta sarjassa",
              f"R = {n}*R0",
              V(("R", "ohm", "equivalent", "معادل", "ekv"), ("R0", "ohm", "each R", "هر مقاومت", "kukin"))))
        a(row(f"tx_rpar_{n}", "eng.elec",
              f"{n} equal resistors in parallel", f"{n} مقاومت مساوی موازی", f"{n} vastusta rinnan",
              f"R = R0/{n}",
              V(("R", "ohm", "equivalent", "معادل", "ekv"), ("R0", "ohm", "each R", "هر مقاومت", "kukin"))))
    for n in range(81, 121):
        a(row(f"tx_powerlaw_{n}", "math.algebra",
              f"Power law degree {n}", f"قانون توانی درجه {n}", f"Potenssilaki {n}",
              f"y = a*x**{n}",
              V(("y", "1", "y", "y", "y"), ("a", "1", "coefficient", "ضریب", "kerroin"), ("x", "1", "x", "x", "x"))))
    for n in range(41, 81):
        a(row(f"tx_expdecay_k{n}", "math.calculus",
              f"Exponential decay rate {n}", f"واپاشی نمایی نرخ {n}", f"Eksponenttihajoaminen {n}",
              f"y = A0*exp(-{n}*t)",
              V(("y", "1", "y", "y", "y"), ("A0", "1", "A0", "A0", "A0"), ("t", "s", "t", "t", "t"))))
        a(row(f"tx_exprise_k{n}", "math.calculus",
              f"Exponential rise rate {n}", f"صعود نمایی نرخ {n}", f"Eksponenttinousu {n}",
              f"y = A0*(1 - exp(-{n}*t))",
              V(("y", "1", "y", "y", "y"), ("A0", "1", "Ainf", "Ainf", "Ainf"), ("t", "s", "t", "t", "t"))))
    for n in range(25, 51):
        a(row(f"tx_annuity_n_{n}", "fin.interest",
              f"Annuity PV factor n={n}", f"عامل ارزش فعلی n={n}", f"NA-kerroin n={n}",
              f"a = (1 - (1 + r)**(-{n}))/r",
              V(("a", "1", "PV factor", "عامل فعلی", "NA-kerroin"), ("r", "1", "rate", "نرخ", "korko"))))
        a(row(f"tx_fvif_n_{n}", "fin.interest",
              f"FV factor n={n}", f"عامل ارزش آتی n={n}", f"TA-kerroin n={n}",
              f"f = (1 + r)**{n}",
              V(("f", "1", "FV factor", "عامل آتی", "TA"), ("r", "1", "rate", "نرخ", "korko"))))
    for n in range(21, 41):
        a(row(f"tx_geo_partial_{n}", "math.seq",
              f"Geometric partial sum {n} terms", f"جمع جزئی هندسی {n} جمله", f"Geometrinen osasumma {n}",
              f"S = a1*(r**{n} - 1)/(r - 1)",
              V(("S", "1", "sum", "جمع", "summa"), ("a1", "1", "first", "اول", "ensimmainen"),
                ("r", "1", "ratio", "نسبت", "suhde"))))
        a(row(f"tx_arith_n_{n}", "math.seq",
              f"Arithmetic sum {n} terms", f"جمع حسابی {n} جمله", f"Aritmeettinen summa {n}",
              f"S = {n}*(2*a1 + ({n} - 1)*d)/2",
              V(("S", "1", "sum", "جمع", "summa"), ("a1", "1", "first", "اول", "ensimmainen"),
                ("d", "1", "difference", "اختلاف", "erotus"))))
    for n in range(25, 51):
        a(row(f"tx_kofn_ident_{n}", "eng.reliability",
              f"{n} identical units series R", f"{n} واحد سری", f"{n} identtista sarjassa",
              f"R = r**{n}",
              V(("R", "1", "system", "سیستم", "jarjestelma"), ("r", "1", "unit", "واحد", "yksikko"))))
        a(row(f"tx_kofn_par_{n}", "eng.reliability",
              f"{n} identical units parallel R", f"{n} واحد موازی", f"{n} identtista rinnan",
              f"R = 1 - (1 - r)**{n}",
              V(("R", "1", "system", "سیستم", "jarjestelma"), ("r", "1", "unit", "واحد", "yksikko"))))
    for n in range(13, 41):
        a(row(f"tx_binomial_mean_n{n}", "math.prob",
              f"Binomial n={n} mean", f"میانگین دوجمله‌ای n={n}", f"Binomi n={n} ka",
              f"mu = {n}*p",
              V(("mu", "1", "mean", "میانگین", "odotusarvo"), ("p", "1", "p", "p", "p"))))
        a(row(f"tx_binomial_var_n{n}", "math.prob",
              f"Binomial n={n} variance", f"واریانس دوجمله‌ای n={n}", f"Binomi n={n} var",
              f"v = {n}*p*(1 - p)",
              V(("v", "1", "variance", "واریانس", "varianssi"), ("p", "1", "p", "p", "p"))))
    for n in range(33, 65):
        a(row(f"tx_twos_max_{n}", "math.discrete",
              f"{n}-bit two's complement max", f"حداکثر مکمل ۲ با {n} بیت", f"{n}-bittinen max",
              f"m = 2**({n} - 1) - 1",
              V(("m", "1", "max", "حداکثر", "max"),)))
        a(row(f"tx_uint_max_{n}", "math.discrete",
              f"{n}-bit unsigned max", f"حداکثر بدون علامت {n} بیت", f"{n}-bittinen unsigned",
              f"m = 2**{n} - 1",
              V(("m", "1", "max", "حداکثر", "max"),)))
    return R
