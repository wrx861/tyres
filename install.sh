#!/bin/bash

###############################################################################
# Автоматическая установка Telegram Mini App - Магазин Шин и Дисков
# Для Ubuntu/Debian
###############################################################################

set -e  # Остановка при ошибках

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Логирование
LOG_FILE="/var/log/tyres-install.log"

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[ОШИБКА]${NC} $1" | tee -a "$LOG_FILE"
    exit 1
}

warning() {
    echo -e "${YELLOW}[ВНИМАНИЕ]${NC} $1" | tee -a "$LOG_FILE"
}

info() {
    echo -e "${BLUE}[INFO]${NC} $1" | tee -a "$LOG_FILE"
}

# Проверка прав root
if [ "$EUID" -ne 0 ]; then 
    error "Запустите скрипт с sudo: sudo bash install.sh"
fi

clear
cat << "EOF"
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║     🚗 Установка Telegram Mini App                        ║
║        Магазин Шин и Дисков                               ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
EOF

echo ""
log "Начало установки..."

# Запрос параметров
echo ""
info "Введите параметры для установки:"
echo ""

read -p "📦 URL GitHub репозитория: " GITHUB_REPO
read -p "🌐 Домен (например, tyres.vpnsuba.ru): " DOMAIN
read -p "📧 Email для SSL сертификата: " EMAIL
read -p "🔑 Логин 4tochki API: " FOURTHCHKI_LOGIN
read -sp "🔐 Пароль 4tochki API: " FOURTHCHKI_PASSWORD
echo ""
read -p "🤖 Telegram Bot Token: " TELEGRAM_BOT_TOKEN
read -p "👤 Telegram Admin ID: " ADMIN_TELEGRAM_ID
read -p "💰 Процент наценки (по умолчанию 15): " MARKUP_PERCENTAGE
MARKUP_PERCENTAGE=${MARKUP_PERCENTAGE:-15}

echo ""
log "Параметры получены"

# Подтверждение
echo ""
warning "Проверьте введенные данные:"
echo "  Домен: $DOMAIN"
echo "  GitHub: $GITHUB_REPO"
echo "  Email: $EMAIL"
echo "  4tochki Login: $FOURTHCHKI_LOGIN"
echo "  Admin ID: $ADMIN_TELEGRAM_ID"
echo "  Наценка: $MARKUP_PERCENTAGE%"
echo ""
read -p "Всё верно? (y/n): " CONFIRM
if [ "$CONFIRM" != "y" ]; then
    error "Установка отменена"
fi

# 1. Обновление системы
log "Шаг 1/10: Обновление системы..."
apt update -qq
apt upgrade -y -qq

# 2. Установка базовых пакетов
log "Шаг 2/10: Установка базовых пакетов..."
apt install -y -qq \
    git \
    curl \
    wget \
    software-properties-common \
    apt-transport-https \
    ca-certificates \
    gnupg \
    lsb-release

# 3. Установка Python и зависимостей
log "Шаг 3/10: Установка Python 3.9+..."
apt install -y -qq \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    build-essential

# 4. Установка Node.js и Yarn
log "Шаг 4/10: Установка Node.js и Yarn..."
if ! command -v node &> /dev/null; then
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash - >> "$LOG_FILE" 2>&1
    apt install -y -qq nodejs
fi
if ! command -v yarn &> /dev/null; then
    npm install -g yarn >> "$LOG_FILE" 2>&1
fi

# 5. Установка MongoDB
log "Шаг 5/10: Установка MongoDB..."
if ! command -v mongod &> /dev/null; then
    wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc | apt-key add - >> "$LOG_FILE" 2>&1
    echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/6.0 multiverse" | tee /etc/apt/sources.list.d/mongodb-org-6.0.list >> "$LOG_FILE" 2>&1
    apt update -qq
    apt install -y -qq mongodb-org
    systemctl enable mongod >> "$LOG_FILE" 2>&1
    systemctl start mongod >> "$LOG_FILE" 2>&1
fi

# 6. Установка Nginx
log "Шаг 6/10: Установка Nginx..."
if ! command -v nginx &> /dev/null; then
    apt install -y -qq nginx
    systemctl enable nginx >> "$LOG_FILE" 2>&1
    systemctl start nginx >> "$LOG_FILE" 2>&1
fi

# 7. Установка Supervisor
log "Шаг 7/10: Установка Supervisor..."
if ! command -v supervisorctl &> /dev/null; then
    apt install -y -qq supervisor
    systemctl enable supervisor >> "$LOG_FILE" 2>&1
    systemctl start supervisor >> "$LOG_FILE" 2>&1
fi

# 8. Клонирование проекта
log "Шаг 8/10: Клонирование проекта..."
if [ -d "/app" ]; then
    warning "Директория /app уже существует. Создаем backup..."
    mv /app /app.backup.$(date +%Y%m%d%H%M%S)
fi

cd /tmp
rm -rf tyres-app
git clone "$GITHUB_REPO" tyres-app >> "$LOG_FILE" 2>&1 || error "Не удалось клонировать репозиторий"
mv tyres-app /app
cd /app

# 9. Настройка Backend
log "Шаг 9/10: Настройка Backend..."

# Установка Python зависимостей
cd /app/backend
pip3 install -r requirements.txt >> "$LOG_FILE" 2>&1 || error "Не удалось установить Python зависимости"

# Создание .env для backend
cat > /app/backend/.env << EOF
MONGO_URL="mongodb://localhost:27017"
DB_NAME="tires_shop"
CORS_ORIGINS="*"

# 4tochki API Credentials
FOURTHCHKI_LOGIN=$FOURTHCHKI_LOGIN
FOURTHCHKI_PASSWORD=$FOURTHCHKI_PASSWORD
FOURTHCHKI_API_URL=http://api-b2b.4tochki.ru/WCF/ClientService.svc?wsdl

# Telegram Bot
TELEGRAM_BOT_TOKEN=$TELEGRAM_BOT_TOKEN
ADMIN_TELEGRAM_ID=$ADMIN_TELEGRAM_ID

# Pricing
DEFAULT_MARKUP_PERCENTAGE=$MARKUP_PERCENTAGE

# Mock Mode - измените на false когда API заработает
USE_MOCK_DATA=true
EOF

log "Backend .env создан"

# Установка Frontend зависимостей
log "Установка Frontend зависимостей (это может занять несколько минут)..."
cd /app/frontend
yarn install >> "$LOG_FILE" 2>&1 || error "Не удалось установить Frontend зависимости"

# Создание .env для frontend
cat > /app/frontend/.env << EOF
REACT_APP_BACKEND_URL=https://$DOMAIN
WDS_SOCKET_PORT=443
REACT_APP_ENABLE_VISUAL_EDITS=false
ENABLE_HEALTH_CHECK=false
EOF

log "Frontend .env создан"

# 10. Настройка Supervisor
log "Шаг 10/10: Настройка Supervisor..."

cat > /etc/supervisor/conf.d/tyres.conf << EOF
[program:backend]
command=/usr/bin/python3 -m uvicorn server:app --host 0.0.0.0 --port 8001
directory=/app/backend
autostart=true
autorestart=true
stderr_logfile=/var/log/supervisor/backend.err.log
stdout_logfile=/var/log/supervisor/backend.out.log
environment=PATH="/usr/bin",PYTHONUNBUFFERED="1"

[program:frontend]
command=/usr/bin/yarn start
directory=/app/frontend
autostart=true
autorestart=true
stderr_logfile=/var/log/supervisor/frontend.err.log
stdout_logfile=/var/log/supervisor/frontend.out.log
environment=PORT="3000",PATH="/usr/bin:/usr/local/bin"
EOF

supervisorctl reread >> "$LOG_FILE" 2>&1
supervisorctl update >> "$LOG_FILE" 2>&1
supervisorctl start all >> "$LOG_FILE" 2>&1

log "Supervisor настроен"

# Настройка Nginx
log "Настройка Nginx..."

cat > /etc/nginx/sites-available/tyres << EOF
server {
    listen 80;
    server_name $DOMAIN;

    client_max_body_size 10M;

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
        
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:8001;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }

    location /health {
        proxy_pass http://localhost:8001/api/health;
    }
}
EOF

ln -sf /etc/nginx/sites-available/tyres /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

nginx -t >> "$LOG_FILE" 2>&1 || error "Ошибка конфигурации Nginx"
systemctl reload nginx >> "$LOG_FILE" 2>&1

log "Nginx настроен"

# Установка SSL сертификата
log "Установка SSL сертификата..."

if ! command -v certbot &> /dev/null; then
    apt install -y -qq certbot python3-certbot-nginx
fi

certbot --nginx -d "$DOMAIN" --non-interactive --agree-tos -m "$EMAIL" >> "$LOG_FILE" 2>&1 || warning "Не удалось установить SSL. Проверьте DNS записи для $DOMAIN"

# Автообновление сертификата
systemctl enable certbot.timer >> "$LOG_FILE" 2>&1

log "SSL сертификат установлен"

# Ожидание запуска сервисов
log "Ожидание запуска сервисов..."
sleep 10

# Проверка статуса
log "Проверка статуса сервисов..."

# Проверка MongoDB
if systemctl is-active --quiet mongod; then
    log "✓ MongoDB запущен"
else
    error "✗ MongoDB не запущен"
fi

# Проверка Supervisor
BACKEND_STATUS=$(supervisorctl status backend | awk '{print $2}')
FRONTEND_STATUS=$(supervisorctl status frontend | awk '{print $2}')

if [ "$BACKEND_STATUS" == "RUNNING" ]; then
    log "✓ Backend запущен"
else
    warning "✗ Backend не запущен. Статус: $BACKEND_STATUS"
fi

if [ "$FRONTEND_STATUS" == "RUNNING" ]; then
    log "✓ Frontend запущен"
else
    warning "✗ Frontend не запущен. Статус: $FRONTEND_STATUS"
fi

# Проверка Nginx
if systemctl is-active --quiet nginx; then
    log "✓ Nginx запущен"
else
    error "✗ Nginx не запущен"
fi

# Тест API
log "Тестирование API..."
sleep 5

if curl -s http://localhost:8001/api/health | grep -q "healthy"; then
    log "✓ API работает"
else
    warning "✗ API не отвечает. Проверьте логи: tail -f /var/log/supervisor/backend.err.log"
fi

# Создание файла с инструкциями
cat > /root/tyres-commands.txt << EOF
╔════════════════════════════════════════════════════════════╗
║          Полезные команды для управления приложением       ║
╚════════════════════════════════════════════════════════════╝

📊 СТАТУС СЕРВИСОВ:
  sudo supervisorctl status

🔄 ПЕРЕЗАПУСК:
  sudo supervisorctl restart backend
  sudo supervisorctl restart frontend
  sudo supervisorctl restart all

📝 ЛОГИ:
  Backend:  tail -f /var/log/supervisor/backend.err.log
  Frontend: tail -f /var/log/supervisor/frontend.out.log
  Nginx:    tail -f /var/log/nginx/error.log

🧪 ТЕСТИРОВАНИЕ:
  curl https://$DOMAIN/api/health
  curl https://$DOMAIN/api/products/tires/search?width=185

🔧 НАСТРОЙКИ:
  Backend:  /app/backend/.env
  Frontend: /app/frontend/.env

🔄 ПЕРЕКЛЮЧЕНИЕ НА РЕАЛЬНОЕ API:
  sed -i 's/USE_MOCK_DATA=true/USE_MOCK_DATA=false/' /app/backend/.env
  sudo supervisorctl restart backend

📞 АДМИН ID: $ADMIN_TELEGRAM_ID
🌐 ДОМЕН: https://$DOMAIN

Полная документация: /app/README.md
Деплой инструкция: /app/DEPLOYMENT.md
Команды тестирования: /app/TEST_COMMANDS.md
EOF

# Финальное сообщение
clear
cat << "EOF"
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║            ✅ УСТАНОВКА ЗАВЕРШЕНА УСПЕШНО! ✅              ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
EOF

echo ""
log "🎉 Приложение успешно установлено!"
echo ""
info "📍 Ваше приложение доступно по адресу:"
echo ""
echo "   🌐 https://$DOMAIN"
echo ""
info "📊 Статус сервисов:"
supervisorctl status
echo ""
info "📝 Полезные команды сохранены в:"
echo "   /root/tyres-commands.txt"
echo ""
info "📚 Документация:"
echo "   /app/README.md"
echo "   /app/DEPLOYMENT.md"
echo "   /app/TEST_COMMANDS.md"
echo ""
info "🔧 Следующие шаги:"
echo "   1. Настройте Telegram Bot (см. DEPLOYMENT.md)"
echo "   2. Когда API 4tochki заработает, измените USE_MOCK_DATA=false"
echo "   3. Откройте https://$DOMAIN в браузере"
echo ""
log "🎉 Готово! Приятного использования!"
echo ""

# Показать команды
cat /root/tyres-commands.txt
