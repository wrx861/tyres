#!/bin/bash
# Быстрое исправление Telegram бота

echo "🤖 Настройка Telegram бота..."

# Цвета
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Проверка что скрипт запущен от root
if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}Этот скрипт должен быть запущен с правами root${NC}"
   echo "Используйте: sudo bash BOT_QUICK_FIX.sh"
   exit 1
fi

# Переходим в директорию приложения
cd /opt/tyres-app || exit 1

# Проверяем наличие токена
if ! grep -q "TELEGRAM_BOT_TOKEN" backend/.env; then
    echo -e "${YELLOW}TELEGRAM_BOT_TOKEN не найден в .env${NC}"
    echo "Добавьте его вручную в /opt/tyres-app/backend/.env"
    exit 1
fi

BOT_TOKEN=$(grep "TELEGRAM_BOT_TOKEN" backend/.env | cut -d '=' -f2)
if [ -z "$BOT_TOKEN" ] || [ "$BOT_TOKEN" = "your_bot_token_here" ]; then
    echo -e "${RED}TELEGRAM_BOT_TOKEN не настроен!${NC}"
    echo "Откройте /opt/tyres-app/backend/.env и добавьте настоящий токен"
    exit 1
fi

echo -e "${GREEN}✓ Токен бота найден${NC}"

# Устанавливаем зависимости
echo "📦 Установка зависимостей..."
source backend/venv/bin/activate
pip install -q python-telegram-bot python-dotenv
echo -e "${GREEN}✓ Зависимости установлены${NC}"

# Создаём конфигурацию supervisor
echo "⚙️  Создание конфигурации Supervisor..."

cat > /etc/supervisor/conf.d/tyres-bot.conf << 'EOF'
[program:tyres-telegram-bot]
command=/opt/tyres-app/backend/venv/bin/python3 telegram_bot.py
directory=/opt/tyres-app
user=root
autostart=true
autorestart=true
stderr_logfile=/var/log/tyres-telegram-bot.err.log
stdout_logfile=/var/log/tyres-telegram-bot.out.log
environment=PATH="/opt/tyres-app/backend/venv/bin"
EOF

echo -e "${GREEN}✓ Конфигурация создана${NC}"

# Создаём файлы логов
touch /var/log/tyres-telegram-bot.err.log
touch /var/log/tyres-telegram-bot.out.log

# Обновляем supervisor
echo "🔄 Обновление Supervisor..."
supervisorctl reread
supervisorctl update

# Запускаем бота
echo "🚀 Запуск бота..."
supervisorctl start tyres-telegram-bot

sleep 2

# Проверяем статус
STATUS=$(supervisorctl status tyres-telegram-bot | awk '{print $2}')

if [ "$STATUS" = "RUNNING" ]; then
    echo -e "${GREEN}✅ Бот успешно запущен!${NC}"
    echo ""
    echo "Проверьте работу:"
    echo "1. Откройте вашего бота в Telegram"
    echo "2. Отправьте команду /start"
    echo "3. Должно прийти приветственное сообщение"
    echo ""
    echo "Логи бота: tail -f /var/log/tyres-telegram-bot.err.log"
else
    echo -e "${RED}❌ Бот не запустился!${NC}"
    echo ""
    echo "Проверьте логи:"
    echo "sudo tail -50 /var/log/tyres-telegram-bot.err.log"
    echo ""
    echo "Возможные причины:"
    echo "1. Неверный токен бота"
    echo "2. Бот уже запущен в другом месте"
    echo "3. Проблемы с сетью"
fi
