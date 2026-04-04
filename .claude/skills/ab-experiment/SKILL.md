---
name: ab-experiment
description: Инструкции для создания feature flag и эксперимента в PostHog через MCP.
user-invocable: false
---

## 1. Прочитать бриф

Найди самый свежий JSON в `briefs/` и прочитай. Нужны: metric_goal, what_change, hypothesis, where_page, calculated, baseline, mde.

Если брифов нет — спроси: метрику, URL страницы и что тестируем.

## 2. Сгенерировать ключ флага

Из what_change сделай snake_case ключ (латиница, цифры, _, до 40 символов).
Покажи пользователю и спроси подтверждение.

## 3. Создать Feature Flag

MCP PostHog tool `create-feature-flag` с 50/50 сплитом (control + test).

## 4. Создать Эксперимент

MCP PostHog tool `experiment-create`: name, description (гипотеза), feature_flag_key, start_date (сегодня).

## 5. Вывести результат

```
Feature flag: [ключ] (создан, активен)
Эксперимент: [название] (ID: [id])
Сплит: 50/50 (control / test)
Страница: [where_page]

Следующие шаги:
1. `/ab-selector` для GTM-скрипта (если ещё не сделал)
2. Убедись что PostHog JS SDK на сайте
3. В GTM-скрипте ключ: '[ключ]'
4. Результаты — `/ab-results`
```

## 6. Обновить бриф

Добавь в JSON поле `posthog`: { feature_flag_key, experiment_id, created_at }.

## Если эксперимент уже есть

Если в брифе уже есть `posthog` — спроси: «Эксперимент уже создан. Создать новый или `/ab-results`?»
