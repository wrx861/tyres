#!/bin/bash

# Скрипт для автоматического исправления .env файла

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}🔧 Автоматическое исправление .env файла${NC}"
echo ""

ENV_FILE="/opt/tyres-app/backend/.env"

# Проверка что файл существует
if [ ! -f "$ENV_FILE" ]; then
    echo -e "${RED}✗ Файл $ENV_FILE не найден${NC}"
    echo "Возможно приложение не установлено или установлено в другую директорию"
    exit 1
fi

echo "Файл найден: $ENV_FILE"
echo ""

# Создание резервной копии
BACKUP_FILE="${ENV_FILE}.backup.$(date +%Y%m%d_%H%M%S)"
cp "$ENV_FILE" "$BACKUP_FILE"
echo -e "${GREEN}✓ Резервная копия создана: $BACKUP_FILE${NC}"
echo ""

# Чтение текущих значений
echo "Чтение текущих значений..."
source "$ENV_FILE"

# Проверка наличия DB_NAME
if grep -q "DB_NAME" "$ENV_FILE"; then
    echo -e "${GREEN}✓ DB_NAME уже присутствует в файле${NC}"
    echo "Файл не требует исправления"
    exit 0
fi

echo -e "${YELLOW}⚠ DB_NAME отсутствует, создаём исправленный файл...${NC}"
echo ""

# Создание нового .env с правильной структурой
cat > "$ENV_FILE" << EOF
MONGO_URL=mongodb://localhost:27017
DB_NAME=tires_shop
CORS_ORIGINS=*

# 4tochki API Credentials
FOURTHCHKI_LOGIN=${FOURTHCHKI_LOGIN:-your_login_here}
FOURTHCHKI_PASSWORD=${FOURTHCHKI_PASSWORD:-your_password_here}
FOURTHCHKI_API_URL=${FOURTHCHKI_API_URL:-http://api-b2b.4tochki.ru/WCF/ClientService.svc?wsdl}

# Telegram Bot
TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN:-your_bot_token_here}
ADMIN_TELEGRAM_ID=${ADMIN_TELEGRAM_ID:-your_admin_id_here}

# Pricing
DEFAULT_MARKUP_PERCENTAGE=${DEFAULT_MARKUP_PERCENTAGE:-15}

# Mock Mode
USE_MOCK_DATA=${USE_MOCK_DATA:-false}
EOF

echo -e "${GREEN}✓ Файл .env исправлен${NC}"
echo ""

echo "Новая структура:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
cat "$ENV_FILE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo -e "${YELLOW}Перезапуск сервисов...${NC}"
supervisorctl restart all
echo ""

echo -e "${GREEN}✓ Готово!${NC}"
echo ""
echo "Проверьте статус:"
echo "  supervisorctl status"
echo ""
echo "Если нужно восстановить старый файл:"
echo "  cp $BACKUP_FILE $ENV_FILE"
echo "  supervisorctl restart all"
