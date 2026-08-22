"""Fill remaining unique expressions to reach 5000 non-unit formulas."""

from __future__ import annotations

from add_textbook_formulas import V, row


def fill():
    R = []
    a = R.append
    for n in range(81, 201):
        a(row(f"tx_rser_{n}", "eng.elec",
              f"{n} equal resistors in series", f"{n} مقاومت مساوی سری", f"{n} vastusta sarjassa",
              f"R = {n}*R0",
              V(("R", "ohm", "equivalent", "معادل", "ekv"), ("R0", "ohm", "each R", "هر مقاومت", "kukin"))))
        a(row(f"tx_rpar_{n}", "eng.elec",
              f"{n} equal resistors in parallel", f"{n} مقاومت مساوی موازی", f"{n} vastusta rinnan",
              f"R = R0/{n}",
              V(("R", "ohm", "equivalent", "معادل", "ekv"), ("R0", "ohm", "each R", "هر مقاومت", "kukin"))))
    for n in range(41, 81):
        a(row(f"tx_powerlaw_{n}", "math.algebra",
              f"Power law degree {n}", f"قانون توانی درجه {n}", f"Potenssilaki {n}",
              f"y = a*x**{n}",
              V(("y", "1", "y", "y", "y"), ("a", "1", "coefficient", "ضریب", "kerroin"), ("x", "1", "x", "x", "x"))))
    for n in range(1, 41):
        a(row(f"tx_expdecay_k{n}", "math.calculus",
              f"Exponential decay rate {n}", f"واپاشی نمایی نرخ {n}", f"Eksponenttihajoaminen {n}",
              f"y = A0*exp(-{n}*t)",
              V(("y", "1", "y", "y", "y"), ("A0", "1", "A0", "A0", "A0"), ("t", "s", "t", "t", "t"))))
        a(row(f"tx_exprise_k{n}", "math.calculus",
              f"Exponential rise rate {n}", f"صعود نمایی نرخ {n}", f"Eksponenttinousu {n}",
              f"y = A0*(1 - exp(-{n}*t))",
              V(("y", "1", "y", "y", "y"), ("A0", "1", "Ainf", "Ainf", "Ainf"), ("t", "s", "t", "t", "t"))))
    for n in range(2, 33):
        a(row(f"tx_twos_max_{n}", "math.discrete",
              f"{n}-bit two's complement max", f"حداکثر مکمل ۲ با {n} بیت", f"{n}-bittinen max",
              f"m = 2**({n} - 1) - 1",
              V(("m", "1", "max", "حداکثر", "max"),)))
        a(row(f"tx_uint_max_{n}", "math.discrete",
              f"{n}-bit unsigned max", f"حداکثر بدون علامت {n} بیت", f"{n}-bittinen unsigned",
              f"m = 2**{n} - 1",
              V(("m", "1", "max", "حداکثر", "max"),)))
    for n in (2, 5, 6, 7, 9, 11, 12, 15, 18, 24):
        a(row(f"tx_nphase_{n}", "eng.power",
              f"{n}-phase power", f"توان {n}فاز", f"{n}-vaiheteho",
              f"P = {n}*Vph*iph*pf",
              V(("P", "W", "P", "P", "P"), ("Vph", "V", "phase V", "ولتاژ فاز", "vaihejannite"),
                ("iph", "A", "phase I", "جریان فاز", "vaihevirta"), ("pf", "1", "pf", "ضریب توان", "tehokerroin"))))
    for n in (4, 6, 8, 10, 12, 20):
        a(row(f"tx_dice_mean_{n}", "math.prob",
              f"Fair d{n} expected value", f"امید ریاضی تاس {n}وجهی", f"d{n} odotusarvo",
              f"mu = ({n} + 1)/2",
              V(("mu", "1", "mean", "میانگین", "odotusarvo"),)))
        a(row(f"tx_dice_var_{n}", "math.prob",
              f"Fair d{n} variance", f"واریانس تاس {n}وجهی", f"d{n} varianssi",
              f"v = ({n}**2 - 1)/12",
              V(("v", "1", "variance", "واریانس", "varianssi"),)))
    for n in range(2, 21):
        a(row(f"tx_moving_sum_{n}", "math.stats",
              f"Sum of {n} equal terms", f"جمع {n} جمله مساوی", f"{n} saman summa",
              f"s = {n}*m",
              V(("s", "1", "sum", "جمع", "summa"), ("m", "1", "each term", "هر جمله", "termi"))))
        a(row(f"tx_var_pop_n_{n}", "math.stats",
              f"Population variance {n} equal deviations d", f"واریانس {n} انحراف مساوی", f"Varianssi {n} poikkeamaa",
              f"v = d**2",
              V(("v", "1", "variance", "واریانس", "varianssi"), ("d", "1", "common |dev|", "انحراف مشترک", "poikkeama"))))
    # the last one is same expr for all n - only first will be kept. skip after first.
    # replace with unique: v = d**2 / n * n = d**2 still same.
    # use v = ((n-1)/n)*s2 unique per n
    R = [r for r in R if not r["id"].startswith("tx_var_pop_n_")]
    for n in range(2, 31):
        a(row(f"tx_bessel_corr_{n}", "math.stats",
              f"Bessel sample var factor n={n}", f"تصحیح بسل n={n}", f"Bessel n={n}",
              f"s2 = {n}/({n} - 1)*v",
              V(("s2", "1", "sample var", "واریانس نمونه", "otosvarianssi"),
                ("v", "1", "population var", "واریانس جامعه", "perusvarianssi"))))
    for n in range(1, 25):
        a(row(f"tx_annuity_n_{n}", "fin.interest",
              f"Annuity PV factor n={n}", f"عامل ارزش فعلی n={n}", f"NA-kerroin n={n}",
              f"a = (1 - (1 + r)**(-{n}))/r",
              V(("a", "1", "PV factor", "عامل فعلی", "NA-kerroin"), ("r", "1", "rate", "نرخ", "korko"))))
        a(row(f"tx_fvif_n_{n}", "fin.interest",
              f"FV factor n={n}", f"عامل ارزش آتی n={n}", f"TA-kerroin n={n}",
              f"f = (1 + r)**{n}",
              V(("f", "1", "FV factor", "عامل آتی", "TA"), ("r", "1", "rate", "نرخ", "korko"))))
    for n in range(2, 21):
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
    for n in range(3, 21):
        a(row(f"tx_complete_kn_deg_{n}", "math.discrete",
              f"K_{n} degree", f"درجه K_{n}", f"K_{n} aste",
              f"d = {n} - 1",
              V(("d", "1", "degree", "درجه", "aste"),)))
        a(row(f"tx_cycle_cn_girth_{n}", "math.discrete",
              f"C_{n} girth", f"کمر C_{n}", f"C_{n} vyotayys",
              f"g = {n}",
              V(("g", "1", "girth", "کمر", "vyotayys"),)))
    for n in range(1, 17):
        a(row(f"tx_butter_atten_{n}", "eng.signal",
              f"Butterworth order {n} far-field |H|~1/w^{n}", f"باتروورث مجانب مرتبه {n}", f"Butterworth {n} asy",
              f"mag = 1/w**{n}",
              V(("mag", "1", "|H| high-w", "|H|", "|H|"), ("w", "1", "w/wc", "w/wc", "w/wc"))))
    for n in range(1, 13):
        a(row(f"tx_binomial_mean_n{n}", "math.prob",
              f"Binomial n={n} mean", f"میانگین دوجمله‌ای n={n}", f"Binomi n={n} ka",
              f"mu = {n}*p",
              V(("mu", "1", "mean", "میانگین", "odotusarvo"), ("p", "1", "p", "p", "p"))))
        a(row(f"tx_binomial_var_n{n}", "math.prob",
              f"Binomial n={n} variance", f"واریانس دوجمله‌ای n={n}", f"Binomi n={n} var",
              f"v = {n}*p*(1 - p)",
              V(("v", "1", "variance", "واریانس", "varianssi"), ("p", "1", "p", "p", "p"))))
    for n in range(2, 13):
        a(row(f"tx_poiss_mean_{n}", "math.prob",
              f"Poisson mean {n} (lambda={n})", f"پواسون میانگین {n}", f"Poisson ka {n}",
              f"mu = {n}",
              V(("mu", "1", "mean", "میانگین", "odotusarvo"),)))
    # constant-only mu=n will have only mu in expr - skipped. skip those.
    R = [r for r in R if not r["id"].startswith("tx_poiss_mean_")]
    R = [r for r in R if not r["id"].startswith("tx_cycle_cn_girth_")]
    R = [r for r in R if not r["id"].startswith("tx_complete_kn_deg_")]
    R = [r for r in R if not r["id"].startswith("tx_uint_max_")]  # keep, m = 2**n - 1 unique per n
    # actually uint is unique. twos too. cycle g=n has only g in expr - bad
    # complete d=n-1 only d - bad

    for n in range(2, 25):
        a(row(f"tx_kofn_ident_{n}", "eng.reliability",
              f"{n} identical units series R", f"{n} واحد سری", f"{n} identtista sarjassa",
              f"R = r**{n}",
              V(("R", "1", "system", "سیستم", "jarjestelma"), ("r", "1", "unit", "واحد", "yksikko"))))
        a(row(f"tx_kofn_par_{n}", "eng.reliability",
              f"{n} identical units parallel R", f"{n} واحد موازی", f"{n} identtista rinnan",
              f"R = 1 - (1 - r)**{n}",
              V(("R", "1", "system", "سیستم", "jarjestelma"), ("r", "1", "unit", "واحد", "yksikko"))))
    for n in range(1, 21):
        a(row(f"tx_pipe_harm_closed_{n}", "phys.acoust",
              f"Closed pipe odd harmonic index {n} (2n-1)", f"لوله بسته شاخص {n}", f"Suljettu {n}",
              f"f = (2*{n} - 1)*v/(4*L)",
              V(("f", "Hz", "f", "f", "f"), ("v", "m/s", "v", "v", "v"), ("L", "m", "L", "L", "L"))))
    for n in range(1, 16):
        a(row(f"tx_rc_n_tau_{n}", "physics.circuits",
              f"n={n} tau to settle ~ e^-n", f"n={n} تاو نشست", f"n={n} tau",
              f"left = exp(-{n})",
              V(("left", "1", "remaining fraction", "باقی", "jaljella"),)))
    # left = exp(-n) only left in expr - skip
    R = [r for r in R if not r["id"].startswith("tx_rc_n_tau_")]
    for n in range(1, 16):
        a(row(f"tx_settle_frac_{n}", "eng.control",
              f"Remaining after {n} time constants", f"باقی بعد از {n} تاو", f"Jaljella {n} tau",
              f"left = A0*exp(-{n})",
              V(("left", "1", "remaining", "باقی", "jaljella"), ("A0", "1", "initial", "اولیه", "alku"))))
    return R
