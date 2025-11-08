#!/bin/bash

# Скрипт для исправления проблемы дублирования пользователей
# Автоматически применяет исправления и удаляет существующие дубликаты

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}======================================================================${NC}"
echo -e "${BLUE}Исправление проблемы дублирования пользователей${NC}"
echo -e "${BLUE}======================================================================${NC}"
echo ""

# Шаг 1: Обновление кода
echo -e "${YELLOW}Шаг 1/4: Обновление кода...${NC}"
echo ""

echo "Копирование backend файлов..."
sudo cp /app/backend/server.py /opt/tyres-app/backend/server.py
sudo cp /app/backend/routers/auth.py /opt/tyres-app/backend/routers/auth.py
echo -e "${GREEN}✅ Backend файлы обновлены${NC}"

echo ""
echo "Копирование frontend файлов..."
sudo cp /app/frontend/src/App.js /opt/tyres-app/frontend/src/App.js
echo -e "${GREEN}✅ Frontend файлы обновлены${NC}"

echo ""
echo "Пересборка frontend (это займет ~1-2 минуты)..."
cd /opt/tyres-app/frontend
sudo yarn build > /dev/null 2>&1
echo -e "${GREEN}✅ Frontend пересобран${NC}"

# Шаг 2: Перезапуск сервисов
echo ""
echo -e "${YELLOW}Шаг 2/4: Перезапуск сервисов...${NC}"
echo ""

sudo supervisorctl restart tyres-backend tyres-frontend
sleep 3

# Проверка статуса
STATUS=$(sudo supervisorctl status tyres-backend tyres-frontend)
echo "$STATUS"

if echo "$STATUS" | grep -q "RUNNING"; then
    echo -e "${GREEN}✅ Сервисы запущены${NC}"
else
    echo -e "${RED}❌ Ошибка запуска сервисов${NC}"
    exit 1
fi

# Шаг 3: Проверка дубликатов
echo ""
echo -e "${YELLOW}Шаг 3/4: Проверка дубликатов...${NC}"
echo ""

sudo cp /app/remove_duplicate_users.py /opt/tyres-app/remove_duplicate_users.py
sudo chmod +x /opt/tyres-app/remove_duplicate_users.py

cd /opt/tyres-app
OUTPUT=$(sudo /opt/tyres-app/backend/venv/bin/python3 remove_duplicate_users.py)
echo "$OUTPUT"

if echo "$OUTPUT" | grep -q "Дубликатов не найдено"; then
    echo ""
    echo -e "${GREEN}✅ Дубликатов нет! Всё готово!${NC}"
    echo ""
    echo -e "${BLUE}======================================================================${NC}"
    echo -e "${GREEN}Исправление завершено успешно!${NC}"
    echo -e "${BLUE}======================================================================${NC}"
    exit 0
fi

# Шаг 4: Удаление дубликатов (если они найдены)
echo ""
echo -e "${YELLOW}Шаг 4/4: Удаление дубликатов...${NC}"
echo ""
echo -e "${RED}Найдены дубликаты! Необходимо их удалить.${NC}"
echo ""
echo -e "${YELLOW}Хотите удалить дубликаты сейчас? (yes/no)${NC}"
read -p "> " CONFIRM

if [ "$CONFIRM" = "yes" ]; then
    echo ""
    echo "Удаление дубликатов..."
    sudo /opt/tyres-app/backend/venv/bin/python3 remove_duplicate_users.py --confirm
    echo ""
    echo -e "${GREEN}✅ Дубликаты удалены!${NC}"
else
    echo ""
    echo -e "${YELLOW}⚠️  Удаление отменено.${NC}"
    echo ""
    echo "Для удаления дубликатов позже, выполните:"
    echo "cd /opt/tyres-app && sudo /opt/tyres-app/backend/venv/bin/python3 remove_duplicate_users.py --confirm"
fi

echo ""
echo -e "${BLUE}======================================================================${NC}"
echo -e "${GREEN}Исправление завершено!${NC}"
echo -e "${BLUE}======================================================================${NC}"
