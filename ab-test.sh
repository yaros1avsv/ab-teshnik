#!/bin/bash
# A/B Тест Помощник — entry point
# Проверка окружения → сбор брифа → запуск Claude для анализа

set -e
cd "$(dirname "$0")"

# ═══ Цвета ═══
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# ═══ 1. Приветствие ═══
echo ""
echo -e "${BLUE}🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪${NC}"
echo -e "${BLUE}  A/B ТЕСТ ПОМОЩНИК${NC}"
echo -e "${BLUE}  Планирование → Селектор → Эксперимент → Результаты${NC}"
echo -e "${BLUE}🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪${NC}"
echo ""

# ═══ 2. Проверка зависимостей ═══
echo -e "${YELLOW}Проверяю окружение...${NC}"

# Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ python3 не найден. Установи Python 3.${NC}"
    exit 1
fi
echo -e "${GREEN}✓ python3${NC}"

# Claude CLI
if ! command -v claude &> /dev/null; then
    echo -e "${RED}✗ claude CLI не найден. Установи: npm install -g @anthropic-ai/claude-code${NC}"
    exit 1
fi
echo -e "${GREEN}✓ claude CLI${NC}"

# npx
if ! command -v npx &> /dev/null; then
    echo -e "${RED}✗ npx не найден. Установи Node.js.${NC}"
    exit 1
fi
echo -e "${GREEN}✓ npx${NC}"

# ═══ 3. Проверка MCP серверов ═══
echo ""
echo -e "${YELLOW}Проверяю MCP серверы...${NC}"

CLAUDE_JSON="$HOME/.claude.json"
PROJECT_DIR="$(pwd)"
NEED_DEVTOOLS=false
NEED_POSTHOG=false

if [ ! -f "$CLAUDE_JSON" ]; then
    echo -e "${RED}✗ $CLAUDE_JSON не найден. Запусти 'claude' хотя бы раз.${NC}"
    exit 1
fi

# Проверяем chrome-devtools (в проекте или глобально)
if python3 -c "
import json, sys
with open('$CLAUDE_JSON') as f:
    data = json.load(f)
# Проверяем в проекте
projects = data.get('projects', {})
project = projects.get('$PROJECT_DIR', {})
if 'chrome-devtools' in project.get('mcpServers', {}):
    sys.exit(0)
# Проверяем глобально
if 'chrome-devtools' in data.get('mcpServers', {}):
    sys.exit(0)
sys.exit(1)
" 2>/dev/null; then
    echo -e "${GREEN}✓ chrome-devtools MCP${NC}"
else
    echo -e "${RED}✗ chrome-devtools MCP не настроен${NC}"
    NEED_DEVTOOLS=true
fi

# Проверяем posthog (в проекте или глобально)
if python3 -c "
import json, sys
with open('$CLAUDE_JSON') as f:
    data = json.load(f)
# Проверяем в проекте
projects = data.get('projects', {})
project = projects.get('$PROJECT_DIR', {})
if 'posthog' in project.get('mcpServers', {}):
    sys.exit(0)
# Проверяем глобально
if 'posthog' in data.get('mcpServers', {}):
    sys.exit(0)
sys.exit(1)
" 2>/dev/null; then
    echo -e "${GREEN}✓ posthog MCP${NC}"
else
    echo -e "${RED}✗ posthog MCP не настроен${NC}"
    NEED_POSTHOG=true
fi

# ═══ 4. Установка MCP если нужно ═══
if [ "$NEED_DEVTOOLS" = true ] || [ "$NEED_POSTHOG" = true ]; then
    echo ""
    echo -e "${YELLOW}Некоторые MCP серверы не настроены. Установить? (y/n)${NC}"
    read -r INSTALL_MCP

    if [[ "$INSTALL_MCP" =~ ^[yYдД] ]]; then

        # Chrome DevTools
        if [ "$NEED_DEVTOOLS" = true ]; then
            echo -e "${YELLOW}Добавляю chrome-devtools MCP...${NC}"
            python3 -c "
import json
with open('$CLAUDE_JSON') as f:
    data = json.load(f)
if 'projects' not in data:
    data['projects'] = {}
if '$PROJECT_DIR' not in data['projects']:
    data['projects']['$PROJECT_DIR'] = {}
if 'mcpServers' not in data['projects']['$PROJECT_DIR']:
    data['projects']['$PROJECT_DIR']['mcpServers'] = {}
data['projects']['$PROJECT_DIR']['mcpServers']['chrome-devtools'] = {
    'type': 'stdio',
    'command': 'npx',
    'args': ['chrome-devtools-mcp@latest'],
    'env': {}
}
with open('$CLAUDE_JSON', 'w') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
"
            echo -e "${GREEN}✓ chrome-devtools добавлен${NC}"
        fi

        # PostHog
        if [ "$NEED_POSTHOG" = true ]; then
            echo ""
            echo -e "${YELLOW}Для PostHog нужен Personal API Key.${NC}"
            echo -e "${YELLOW}Получи его: PostHog → Settings → Personal API Keys → Create key${NC}"
            echo -e "${YELLOW}Ключ начинается с phx_...${NC}"
            echo ""
            echo -ne "${YELLOW}Вставь PostHog API Key (или Enter чтобы пропустить): ${NC}"
            read -rs POSTHOG_KEY
            echo ""

            if [ -n "$POSTHOG_KEY" ]; then
                echo -ne "${YELLOW}URL PostHog (Enter для https://us.posthog.com/): ${NC}"
                read -r POSTHOG_URL
                POSTHOG_URL=${POSTHOG_URL:-https://us.posthog.com/}

                python3 -c "
import json
with open('$CLAUDE_JSON') as f:
    data = json.load(f)
if 'mcpServers' not in data:
    data['mcpServers'] = {}
data['mcpServers']['posthog'] = {
    'type': 'http',
    'url': 'https://mcp.posthog.com/mcp',
    'headers': {
        'Authorization': 'Bearer $POSTHOG_KEY'
    },
    'env': {
        'POSTHOG_BASE_URL': '$POSTHOG_URL'
    }
}
with open('$CLAUDE_JSON', 'w') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
"
                echo -e "${GREEN}✓ posthog добавлен (глобально)${NC}"
            else
                echo -e "${YELLOW}Пропускаю PostHog. Без него не будут работать создание экспериментов и результаты.${NC}"
            fi
        fi

        echo ""
        echo -e "${GREEN}MCP настроен. Серверы будут доступны в сессии Claude.${NC}"
    else
        echo -e "${YELLOW}Пропускаю установку MCP.${NC}"
    fi
fi

# ═══ 5. Директории ═══
mkdir -p briefs scripts

# ═══ 6. Сбор брифа ═══
echo ""
echo -e "${YELLOW}Собираем бриф A/B-теста...${NC}"
echo ""

python3 -u ab_brief_collect.py

# Достаём последний файл брифа
BRIEF_JSON=$(ls -t briefs/brief_*.json 2>/dev/null | head -1)

if [ -z "$BRIEF_JSON" ]; then
    echo -e "${RED}Ошибка: бриф не сохранён${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}Бриф сохранён: $BRIEF_JSON${NC}"
echo ""

# ═══ 7. Запуск Claude для анализа ═══
echo -e "${BLUE}Запускаю Claude для анализа брифа...${NC}"
echo -e "${BLUE}После анализа можешь писать:${NC}"
echo -e "${BLUE}  • «найди селектор» — поиск CSS-элемента на странице${NC}"
echo -e "${BLUE}  • «создай эксперимент» — создание в PostHog${NC}"
echo -e "${BLUE}  • «покажи результаты» — метрики из PostHog${NC}"
echo ""

exec ccr code "Бриф A/B-теста собран и сохранён в $BRIEF_JSON. Проанализируй его — прочитай файл, проверь правила, рассчитай выборку через ab_calculator.py и выведи сводку."
