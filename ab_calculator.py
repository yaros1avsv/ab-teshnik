#!/usr/bin/env python3
"""
A/B калькулятор — sample size, duration, significance.
Перенесён из n8n ноды «A/B Калькулятор (Python)».

Использование:
  python3 ab_calculator.py '{"type":"sample_size","baseline":0.05,"mde":0.01}'
  python3 ab_calculator.py '{"type":"duration","total_sample":8000,"daily_traffic":200}'
  python3 ab_calculator.py '{"type":"significance","visitors_a":5000,"conversions_a":250,"visitors_b":5000,"conversions_b":300}'
"""

import json
import math
import sys


def sample_size_n(baseline, mde):
    b = float(baseline)
    d = float(mde)
    p2 = min(max(b + d, 1e-6), 0.999)
    z_a, z_b = 1.96, 0.84
    delta = abs(p2 - b)
    if delta < 1e-9:
        return None
    se = b * (1 - b) + p2 * (1 - p2)
    n = ((z_a + z_b) ** 2 * se) / (delta ** 2)
    return int(math.ceil(n))


def z_test_p(n_a, c_a, n_b, c_b):
    if n_a <= 0 or n_b <= 0:
        return None
    p1, p2 = c_a / n_a, c_b / n_b
    p_pool = (c_a + c_b) / (n_a + n_b)
    if p_pool <= 0 or p_pool >= 1:
        return p1, p2, None, 0.0
    se = math.sqrt(p_pool * (1 - p_pool) * (1 / n_a + 1 / n_b))
    z = (p2 - p1) / se if se > 0 else 0.0
    az = abs(z)
    if az > 3.29:
        pv = 0.001
    elif az > 2.58:
        pv = 0.005
    elif az > 1.96:
        pv = 0.04
    elif az > 1.64:
        pv = 0.09
    else:
        pv = 0.5
    lift = ((p2 - p1) / p1 * 100) if p1 > 0 else 0.0
    return p1, p2, pv, lift


def main():
    if len(sys.argv) < 2:
        print(json.dumps({"ok": False, "error": "usage: ab_calculator.py '{\"type\":\"sample_size\",\"baseline\":0.05,\"mde\":0.01}'"}))
        sys.exit(1)

    try:
        d = json.loads(sys.argv[1])
    except json.JSONDecodeError:
        print(json.dumps({"ok": False, "error": "invalid JSON"}))
        sys.exit(1)

    t = d.get("type")
    out = {"ok": True, "type": t}

    if t == "sample_size":
        b = float(d.get("baseline", 0.05))
        m = float(d.get("mde", 0.01))
        n_each = sample_size_n(b, m)
        if n_each is None:
            out = {"ok": False, "error": "mde или baseline некорректны"}
        else:
            out.update({
                "sample_per_variant": n_each,
                "total_sample": n_each * 2,
                "baseline": b,
                "mde": m,
            })

    elif t == "duration":
        ts = int(d.get("total_sample", 0))
        dt = max(int(d.get("daily_traffic", 1)), 1)
        days = math.ceil(ts / dt)
        out.update({
            "days": days,
            "weeks": round(days / 7, 1),
            "total_sample": ts,
            "daily_traffic": dt,
        })

    elif t == "significance":
        na = int(d.get("visitors_a", 0))
        ca = int(d.get("conversions_a", 0))
        nb = int(d.get("visitors_b", 0))
        cb = int(d.get("conversions_b", 0))
        r = z_test_p(na, ca, nb, cb)
        if r is None or r[2] is None:
            out = {"ok": False, "error": "мало данных"}
        else:
            p1, p2, pv, lift = r
            verdict = "Разницы нет или слабая"
            if pv <= 0.05:
                verdict = "Новый вариант лучше" if p2 > p1 else "Старый вариант лучше"
            out.update({
                "rate_a_percent": round(p1 * 100, 2),
                "rate_b_percent": round(p2 * 100, 2),
                "p_value": pv,
                "lift_percent": round(lift, 2),
                "verdict": verdict,
            })

    else:
        out = {"ok": False, "error": "type: sample_size | duration | significance"}

    print(json.dumps(out, ensure_ascii=False))


if __name__ == "__main__":
    main()
