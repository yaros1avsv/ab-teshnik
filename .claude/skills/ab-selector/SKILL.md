---
name: ab-selector
description: Инструкции для поиска CSS-селектора и генерации GTM-скрипта с PostHog feature flag.
user-invocable: false
---

## 1. Получить вводные — ОБЯЗАТЕЛЬНЫЙ ШАГ

ПЕРЕД любыми действиями задай пользователю ДВА вопроса через AskUserQuestion:
1. URL страницы
2. Какой именно элемент нужен — пусть опишет словами (кнопка «Купить», заголовок первого экрана, баннер...)

НЕ ПРОПУСКАЙ этот шаг. НЕ УГАДЫВАЙ элемент. Дождись ответов.

## 2. Найти CSS-селектор — КОНКРЕТНЫЕ ШАГИ

Используй MCP chrome-devtools инструменты СТРОГО В ТАКОМ ПОРЯДКЕ:

**Шаг A.** Вызови `new_page` с URL от пользователя — откроется страница в браузере.

**Шаг B.** Вызови `take_snapshot` — получишь DOM-дерево страницы (accessibility tree). Найди в нём элемент по тексту который описал пользователь.

**Шаг C.** Вызови `evaluate_script` с JS-кодом для получения уникального CSS-селектора найденного элемента. Пример:
```javascript
(() => {
  // Ищем элемент по тексту
  const allElements = document.querySelectorAll('*');
  for (const el of allElements) {
    if (el.textContent.trim().startsWith('ТЕКСТ_ЭЛЕМЕНТА') && el.children.length === 0) {
      // Строим уникальный селектор
      if (el.id) return '#' + el.id;
      let path = [];
      let current = el;
      while (current && current !== document.body) {
        let selector = current.tagName.toLowerCase();
        if (current.className && typeof current.className === 'string') {
          selector += '.' + current.className.trim().split(/\s+/).join('.');
        }
        path.unshift(selector);
        current = current.parentElement;
      }
      const fullSelector = path.join(' > ');
      // Проверяем уникальность
      const count = document.querySelectorAll(fullSelector).length;
      return JSON.stringify({selector: fullSelector, unique: count === 1, count: count, text: el.textContent.trim().slice(0, 80)});
    }
  }
  return JSON.stringify({error: 'Элемент не найден'});
})()
```
Замени ТЕКСТ_ЭЛЕМЕНТА на текст из описания пользователя.

**Шаг D.** Если селектор не уникальный — уточни через `evaluate_script`, добавив родительский контекст или nth-child.

**Шаг E.** Покажи пользователю найденный селектор и спроси подтверждение.

## 3. Генерация GTM-скрипта

После подтверждения селектора — сгенерируй скрипт, подставив НАЙДЕННЫЙ_СЕЛЕКТОР:

```javascript
<script>
var checkPosthog = setInterval(function() {
    if (window.posthog && window.posthog.getFeatureFlag) {
        clearInterval(checkPosthog);
        posthog.onFeatureFlags(function() {
            var variant = posthog.getFeatureFlag('test');
            var el = document.querySelector('НАЙДЕННЫЙ_СЕЛЕКТОР');
            if (!el) return;
            if (variant === 'test') {
                // Здесь изменения для варианта B
            }
            el.addEventListener('click', function() {
                posthog.capture('ab_test_element_clicked', {
                    variant: variant,
                    element_text: el.textContent.trim()
                });
            });
        });
    }
}, 100);
setTimeout(function() {
    clearInterval(checkPosthog);
}, 5000);
</script>
```

## 4. Сохранить скрипт

Сохрани в `scripts/gtm_YYYY-MM-DD_HH-MM.js`.

Скажи: «Скрипт готов. Вставь в GTM как Custom HTML тег. Следующий шаг — скажи "создай эксперимент".»
