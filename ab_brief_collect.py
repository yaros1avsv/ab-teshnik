#!/usr/bin/env python3 -u
"""
Сбор брифа A/B-теста — 10 вопросов в терминале → JSON.
Перенесено из FSM-ноды n8n «Бриф: пошагово (staticData)».
"""

import json
import os
from datetime import datetime

STEPS = [
    {
        "key": "metric_goal",
        "title": "Шаг 1/10 — Метрика и цель",
        "question": "Какую метрику хотим улучшить и зачем это бизнесу?",
        "hint": "Один тест — одна метрика. Пример: «поднять CR в заявку с 3% до 4%»",
    },
    {
        "key": "what_change",
        "title": "Шаг 2/10 — Что меняем",
        "question": "Что именно сравниваем A vs B?",
        "hint": "Одно изменение за тест. Пример: «текущий заголовок vs новый с цифрами»",
    },
    {
        "key": "hypothesis",
        "title": "Шаг 3/10 — Гипотеза",
        "question": "Почему новый вариант должен работать лучше?",
        "hint": "Формула: «Если [изменение], то [метрика] изменится, потому что [причина]»",
    },
    {
        "key": "where_page",
        "title": "Шаг 4/10 — Где",
        "question": "URL или путь страницы для теста?",
        "hint": "Конкретная страница, не «весь сайт»",
    },
    {
        "key": "traffic_source",
        "title": "Шаг 5/10 — Трафик",
        "question": "Откуда трафик? (SEO, контекст, соцсети, email, смешанный)",
        "hint": "Источник влияет на поведение — SEO и рекламный трафик ведут себя по-разному",
    },
    {
        "key": "devices",
        "title": "Шаг 6/10 — Устройства",
        "question": "Какие устройства? (все / десктоп / мобайл / десктоп+планшет)",
        "hint": "Введи один из вариантов",
    },
    {
        "key": "baseline",
        "title": "Шаг 7/10 — Baseline конверсии",
        "question": "Текущий показатель метрики? (число в % или «не знаю»)",
        "hint": "Пример: «3.2%» или «примерно 5%» или «не знаю»",
    },
    {
        "key": "daily_traffic",
        "title": "Шаг 8/10 — Трафик в день",
        "question": "Сколько визитов в день на эту страницу? (число или «не знаю»)",
        "hint": "Если < 200 — тест может занять месяцы",
    },
    {
        "key": "mde",
        "title": "Шаг 9/10 — MDE",
        "question": "Минимальный эффект, который хочешь увидеть?",
        "hint": "Пример: «+1 п.п.» или «+20% относительно» или «не знаю»",
    },
    {
        "key": "notes",
        "title": "Шаг 10/10 — Заметки",
        "question": "Что ещё важно? Сезонность, редизайн, ограничения?",
        "hint": "Можно «нет» или «—»",
    },
]


def ask(step):
    print(f"\n{'=' * 50}", flush=True)
    print(f"  {step['title']}", flush=True)
    print(f"{'=' * 50}", flush=True)
    print(f"  {step['question']}", flush=True)
    print(f"  💡 {step['hint']}", flush=True)
    print(flush=True)
    answer = input("  → ").strip()
    return answer if answer else "не указано"


def parse_number(value):
    """Пытается извлечь число из строки, возвращает None если не получилось."""
    if not value or value.lower() in ("не знаю", "не указано", "—", "-", "нет"):
        return None
    cleaned = value.replace("%", "").replace(",", ".").strip()
    try:
        return float(cleaned)
    except ValueError:
        return None


def main():
    print("\n" + "🧪 " * 20)
    print("  A/B ТЕСТ — БРИФ")
    print("  Ответь на 10 вопросов, я соберу всё в JSON")
    print("🧪 " * 20)

    answers = {}
    for step in STEPS:
        answers[step["key"]] = ask(step)

    # Парсим числовые поля
    baseline_raw = parse_number(answers["baseline"])
    if baseline_raw and baseline_raw > 1:
        baseline_raw = baseline_raw / 100  # 5% → 0.05
    daily_raw = parse_number(answers["daily_traffic"])
    mde_raw = parse_number(answers["mde"])
    if mde_raw is not None:
        if mde_raw >= 1:
            mde_raw = mde_raw / 100  # 1 п.п. → 0.01, 20% → 0.20

    brief = {
        "created": datetime.now().isoformat(),
        "metric_goal": answers["metric_goal"],
        "what_change": answers["what_change"],
        "hypothesis": answers["hypothesis"],
        "where_page": answers["where_page"],
        "traffic_source": answers["traffic_source"],
        "devices": answers["devices"],
        "baseline": baseline_raw,
        "baseline_raw": answers["baseline"],
        "daily_traffic": int(daily_raw) if daily_raw else None,
        "daily_traffic_raw": answers["daily_traffic"],
        "mde": mde_raw,
        "mde_raw": answers["mde"],
        "notes": answers["notes"],
    }

    # Сохраняем
    os.makedirs("briefs", exist_ok=True)
    filename = f"briefs/brief_{datetime.now().strftime('%Y-%m-%d_%H-%M')}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(brief, f, ensure_ascii=False, indent=2)

    print(f"\n{'=' * 50}")
    print(f"  ✅ Бриф сохранён: {filename}")
    print(f"{'=' * 50}")
    print(json.dumps(brief, ensure_ascii=False, indent=2))

    return filename


if __name__ == "__main__":
    main()
