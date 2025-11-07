#!/bin/bash

# Скрипт для исправления конфликта Telegram бота

echo "🔧 Исправление конфликта Telegram бота..."

# Загружаем токен из .env
source /opt/tyres-app/backend/.env

if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
    echo "❌ TELEGRAM_BOT_TOKEN не найден в .env"
    exit 1
fi

echo "📌 Токен найден: ${TELEGRAM_BOT_TOKEN:0:10}..."

# Удаляем webhook (если был установлен)
echo "🗑️  Удаление webhook..."
curl -s "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/deleteWebhook?drop_pending_updates=true" | python3 -m json.tool

# Получаем pending updates и очищаем их
echo "🧹 Очистка pending updates..."
curl -s "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/getUpdates?offset=-1" > /dev/null

echo "✅ Конфликт должен быть исправлен"
echo ""
echo "Теперь перезапустите backend:"
echo "  sudo supervisorctl restart tyres-backend"
