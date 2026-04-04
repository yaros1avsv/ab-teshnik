---
name: ab-results
description: Инструкции для получения результатов и метрик A/B-экспериментов из PostHog.
user-invocable: false
---

## 1. Получить список экспериментов

MCP PostHog tool `experiment-get-all`. Покажи активные, спроси какой смотреть.

## 2. Получить результаты

MCP PostHog tool `experiment-results-get` с ID эксперимента. Извлеки: варианты, визиты, конверсии, confidence.

## 3. Рассчитать статистику

Если PostHog не вернул significance — вызови:
```bash
python3 ab_calculator.py '{"type":"significance","visitors_a":N,"conversions_a":C,"visitors_b":N,"conversions_b":C}'
```

## 4. Вывести результаты

```
Эксперимент: [название] (ID: [id])
Статус: [running / complete / draft]
Период: [start] — [end или "сейчас"]

         | Control | Test    | Разница
---------|---------|---------|--------
Визиты   | [n1]    | [n2]    |
Конверсии| [c1]    | [c2]    |
CR       | [p1]%   | [p2]%   | [lift]%
                               p = [p_value]

Вердикт: [...]
```

## 5. Рекомендации

- Значимо → «Останови и внедряй победителя.»
- Не значимо → «Продолжай тест, проверяй через [X] дней.»
- Мало данных → «Проверь что PostHog SDK отправляет события.»

## 6. Остановка (опционально)

Если просят — MCP PostHog tool `experiment-update`.
