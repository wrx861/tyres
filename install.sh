#!/bin/bash

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}  4tochki Telegram Mini App${NC}"
echo -e "${GREEN}  Автоматическая установка${NC}"
echo -e "${GREEN}================================${NC}"
echo ""

# Проверка прав root
if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}Этот скрипт должен быть запущен с правами root${NC}"
   echo "Используйте: sudo bash install.sh"
   exit 1
fi

# Поддержка аргументов командной строки
DOMAIN_NAME=""
LETSENCRYPT_EMAIL=""
USE_HTTPS=false
FOURTHCHKI_LOGIN=""
FOURTHCHKI_PASSWORD=""
TELEGRAM_BOT_TOKEN=""
ADMIN_TELEGRAM_ID=""

# Парсинг аргументов
while [[ $# -gt 0 ]]; do
    case $1 in
        -d|--domain)
            DOMAIN_NAME="$2"
            shift 2
            ;;
        -e|--email)
            LETSENCRYPT_EMAIL="$2"
            USE_HTTPS=true
            shift 2
            ;;
        --no-ssl)
            USE_HTTPS=false
            shift
            ;;
        --api-login)
            FOURTHCHKI_LOGIN="$2"
            shift 2
            ;;
        --api-password)
            FOURTHCHKI_PASSWORD="$2"
            shift 2
            ;;
        --bot-token)
            TELEGRAM_BOT_TOKEN="$2"
            shift 2
            ;;
        --admin-id)
            ADMIN_TELEGRAM_ID="$2"
            shift 2
            ;;
        -h|--help)
            echo "Использование: sudo bash install.sh [ОПЦИИ]"
            echo ""
            echo "Опции домена:"
            echo "  -d, --domain DOMAIN      Домен для приложения (например: tires.yourdomain.com)"
            echo "  -e, --email EMAIL        Email для Let's Encrypt (автоматически включает SSL)"
            echo "  --no-ssl                 Не устанавливать SSL даже если указан домен"
            echo ""
            echo "Опции учетных данных:"
            echo "  --api-login LOGIN        Логин 4tochki API"
            echo "  --api-password PASS      Пароль 4tochki API"
            echo "  --bot-token TOKEN        Telegram Bot Token"
            echo "  --admin-id ID            Admin Telegram ID"
            echo ""
            echo "  -h, --help               Показать эту справку"
            echo ""
            echo "Примеры:"
            echo "  # Полная автоматическая установка"
            echo "  sudo bash install.sh -d tires.example.com -e admin@example.com \\"
            echo "    --api-login sa56026 --api-password mypass \\"
            echo "    --bot-token 123456:ABC --admin-id 508352361"
            echo ""
            echo "  # Только домен (учетные данные в интерактивном режиме)"
            echo "  sudo bash install.sh -d tires.example.com -e admin@example.com"
            echo ""
            echo "  # Полностью интерактивный режим"
            echo "  sudo bash install.sh"
            exit 0
            ;;
        *)
            echo -e "${RED}Неизвестная опция: $1${NC}"
            echo "Используйте --help для справки"
            exit 1
            ;;
    esac
done

# Перенаправляем ввод с терминала один раз для всех интерактивных запросов
exec < /dev/tty

# Если домен не указан через аргументы, запрашиваем интерактивно
if [ -z "$DOMAIN_NAME" ]; then
    echo -e "${BLUE}Настройка домена для Telegram Mini App${NC}"
    echo ""
    echo "Вы можете:"
    echo "  1. Ввести домен для продакшн установки"
    echo "  2. Нажать Enter для режима разработки (localhost)"
    echo ""
    
    read -p "Введите домен для приложения (например: tires.yourdomain.com): " DOMAIN_NAME
    
    if [ -z "$DOMAIN_NAME" ]; then
        echo -e "${YELLOW}Домен не указан. Установка продолжится в режиме разработки (без HTTPS)${NC}"
        USE_HTTPS=false
    else
        echo ""
        echo -e "${BLUE}Установка SSL сертификата (Let's Encrypt)${NC}"
        echo "Для получения SSL сертификата необходимо:"
        echo "  1. Домен $DOMAIN_NAME должен указывать на IP этого сервера"
        echo "  2. Порты 80 и 443 должны быть открыты"
        echo ""
        read -p "Установить SSL сертификат? (y/n): " INSTALL_SSL
        
        if [[ "$INSTALL_SSL" == "y" || "$INSTALL_SSL" == "Y" ]]; then
            USE_HTTPS=true
            read -p "Введите email для уведомлений Let's Encrypt: " LETSENCRYPT_EMAIL
            
            if [ -z "$LETSENCRYPT_EMAIL" ]; then
                echo -e "${RED}Email обязателен для получения SSL сертификата${NC}"
                exit 1
            fi
        else
            USE_HTTPS=false
        fi
    fi
else
    # Домен указан через аргументы
    echo -e "${GREEN}✓ Домен: $DOMAIN_NAME${NC}"
    if [ "$USE_HTTPS" = true ] && [ -n "$LETSENCRYPT_EMAIL" ]; then
        echo -e "${GREEN}✓ SSL будет установлен (Email: $LETSENCRYPT_EMAIL)${NC}"
    fi
fi

echo ""

# Запрос учетных данных для настройки (если не указаны через аргументы)
if [ -z "$FOURTHCHKI_LOGIN" ] || [ -z "$FOURTHCHKI_PASSWORD" ] || [ -z "$TELEGRAM_BOT_TOKEN" ] || [ -z "$ADMIN_TELEGRAM_ID" ]; then
    echo ""
    echo -e "${BLUE}Настройка учетных данных${NC}"
    echo ""
    echo "Для работы приложения необходимы учетные данные:"
    echo "  1. API 4tochki (https://b2b.4tochki.ru)"
    echo "  2. Telegram бот"
    echo ""
    echo -e "${YELLOW}Подсказка:${NC} Нажмите Enter чтобы пропустить (можно настроить позже)"
    echo ""

    if [ -z "$FOURTHCHKI_LOGIN" ]; then
        read -p "Логин 4tochki API: " FOURTHCHKI_LOGIN
    fi
    if [ -z "$FOURTHCHKI_PASSWORD" ]; then
        read -p "Пароль 4tochki API: " FOURTHCHKI_PASSWORD
    fi
    if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
        read -p "Telegram Bot Token (от @BotFather): " TELEGRAM_BOT_TOKEN
    fi
    if [ -z "$ADMIN_TELEGRAM_ID" ]; then
        read -p "Admin Telegram ID (от @userinfobot): " ADMIN_TELEGRAM_ID
    fi
else
    echo ""
    echo -e "${GREEN}✓ Учетные данные переданы через аргументы${NC}"
fi

# Проверка что все данные введены
if [ -z "$FOURTHCHKI_LOGIN" ] || [ -z "$FOURTHCHKI_PASSWORD" ] || [ -z "$TELEGRAM_BOT_TOKEN" ] || [ -z "$ADMIN_TELEGRAM_ID" ]; then
    echo -e "${YELLOW}Внимание: Не все учетные данные были введены${NC}"
    echo "Вы сможете добавить их позже в файле /opt/tyres-app/backend/.env"
    
    # Установка значений по умолчанию
    FOURTHCHKI_LOGIN=${FOURTHCHKI_LOGIN:-"your_login_here"}
    FOURTHCHKI_PASSWORD=${FOURTHCHKI_PASSWORD:-"your_password_here"}
    TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN:-"your_bot_token_here"}
    ADMIN_TELEGRAM_ID=${ADMIN_TELEGRAM_ID:-"your_admin_id_here"}
else
    echo -e "${GREEN}✓ Учетные данные введены${NC}"
fi

echo ""

# Функция для проверки успешности команды
check_status() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ $1${NC}"
    else
        echo -e "${RED}✗ Ошибка: $1${NC}"
        exit 1
    fi
}

# 1. Обновление системы
echo -e "${YELLOW}[1/10] Обновление системы...${NC}"
apt-get update -qq
check_status "Система обновлена"

# 2. Установка базовых зависимостей
echo -e "${YELLOW}[2/12] Установка базовых зависимостей...${NC}"
PACKAGES="curl wget git supervisor nginx"
if [ "$USE_HTTPS" = true ]; then
    PACKAGES="$PACKAGES certbot python3-certbot-nginx"
fi
apt-get install -y $PACKAGES -qq
check_status "Базовые зависимости установлены"

# Отключение IPv6 для nginx
echo -e "${YELLOW}Отключение IPv6...${NC}"
sysctl -w net.ipv6.conf.all.disable_ipv6=1
sysctl -w net.ipv6.conf.default.disable_ipv6=1
echo "net.ipv6.conf.all.disable_ipv6 = 1" >> /etc/sysctl.conf
echo "net.ipv6.conf.default.disable_ipv6 = 1" >> /etc/sysctl.conf
check_status "IPv6 отключен"

# 3. Установка Python 3.11
echo -e "${YELLOW}[3/12] Установка Python 3.11...${NC}"
if ! command -v python3.11 &> /dev/null; then
    apt-get install -y software-properties-common -qq
    add-apt-repository ppa:deadsnakes/ppa -y
    apt-get update -qq
    apt-get install -y python3.11 python3.11-venv python3-pip -qq
    check_status "Python 3.11 установлен"
else
    echo -e "${GREEN}✓ Python 3.11 уже установлен${NC}"
fi

# 4. Установка Node.js 20
echo -e "${YELLOW}[4/12] Установка Node.js 20...${NC}"
if ! command -v node &> /dev/null || [[ "$(node -v)" < "v20" ]]; then
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
    apt-get install -y nodejs -qq
    check_status "Node.js 20+ установлен"
else
    echo -e "${GREEN}✓ Node.js уже установлен и актуален${NC}"
fi

# 5. Установка Yarn
echo -e "${YELLOW}[5/12] Установка Yarn...${NC}"
if ! command -v yarn &> /dev/null; then
    npm install -g yarn --silent
    check_status "Yarn установлен"
else
    echo -e "${GREEN}✓ Yarn уже установлен${NC}"
fi

# 6. Установка MongoDB
echo -e "${YELLOW}[6/12] Установка MongoDB...${NC}"
if ! command -v mongod &> /dev/null; then
    # Определяем версию Ubuntu
    UBUNTU_VERSION=$(lsb_release -cs)
    
    if [ "$UBUNTU_VERSION" = "noble" ] || [ "$UBUNTU_VERSION" = "mantic" ]; then
        # Для Ubuntu 24.04+ используем MongoDB 7.0
        curl -fsSL https://www.mongodb.org/static/pgp/server-7.0.asc | gpg -o /usr/share/keyrings/mongodb-server-7.0.gpg --dearmor
        echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-7.0.gpg ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | tee /etc/apt/sources.list.d/mongodb-org-7.0.list
    else
        # Для старых версий Ubuntu используем MongoDB 6.0
        curl -fsSL https://www.mongodb.org/static/pgp/server-6.0.asc | gpg -o /usr/share/keyrings/mongodb-server-6.0.gpg --dearmor
        echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-6.0.gpg ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/6.0 multiverse" | tee /etc/apt/sources.list.d/mongodb-org-6.0.list
    fi
    
    apt-get update -qq
    apt-get install -y mongodb-org -qq
    systemctl enable mongod
    systemctl start mongod
    
    # Проверка что MongoDB запустился
    sleep 3
    if systemctl is-active --quiet mongod; then
        check_status "MongoDB установлен и запущен"
    else
        echo -e "${RED}✗ MongoDB установлен, но не запущен. Попробуйте: sudo systemctl start mongod${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✓ MongoDB уже установлен${NC}"
    systemctl start mongod 2>/dev/null || true
fi

# 7. Клонирование репозитория
echo -e "${YELLOW}[7/12] Клонирование репозитория...${NC}"
APP_DIR="/opt/tyres-app"
if [ -d "$APP_DIR" ]; then
    echo "Директория $APP_DIR существует. Удаляю старую версию..."
    rm -rf $APP_DIR
fi
git clone https://github.com/wrx861/tyres.git $APP_DIR
cd $APP_DIR
check_status "Репозиторий клонирован"

# 8. Настройка backend
echo -e "${YELLOW}[8/12] Настройка backend...${NC}"
cd $APP_DIR/backend

# Создание виртуального окружения
python3.11 -m venv venv
source venv/bin/activate

# Установка зависимостей
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
check_status "Backend зависимости установлены"

# Настройка .env файла
if [ ! -f .env ]; then
    cat > .env << EOF
MONGO_URL=mongodb://localhost:27017
DB_NAME=tires_shop
CORS_ORIGINS=*

# 4tochki API Credentials
FOURTHCHKI_LOGIN=$FOURTHCHKI_LOGIN
FOURTHCHKI_PASSWORD=$FOURTHCHKI_PASSWORD
FOURTHCHKI_API_URL=http://api-b2b.4tochki.ru/WCF/ClientService.svc?wsdl

# Telegram Bot
TELEGRAM_BOT_TOKEN=$TELEGRAM_BOT_TOKEN
ADMIN_TELEGRAM_ID=$ADMIN_TELEGRAM_ID

# Pricing
DEFAULT_MARKUP_PERCENTAGE=15

# Mock Mode
USE_MOCK_DATA=false
EOF
    check_status "Backend .env создан с учетными данными"
else
    echo -e "${GREEN}✓ Backend .env уже существует${NC}"
fi

deactivate

# 9. Настройка frontend
echo -e "${YELLOW}[9/12] Настройка frontend...${NC}"
cd $APP_DIR/frontend

# Установка зависимостей
yarn install --silent
check_status "Frontend зависимости установлены"

# Настройка .env файла
if [ ! -f .env ]; then
    # Определяем URL backend
    if [ "$USE_HTTPS" = true ]; then
        BACKEND_URL="https://$DOMAIN_NAME"
    elif [ -n "$DOMAIN_NAME" ]; then
        BACKEND_URL="http://$DOMAIN_NAME"
    else
        BACKEND_URL="http://localhost:8001"
    fi
    
    cat > .env << EOF
REACT_APP_BACKEND_URL=$BACKEND_URL
PORT=3000
REACT_APP_ENABLE_VISUAL_EDITS=false
ENABLE_HEALTH_CHECK=false
EOF
    check_status "Frontend .env создан"
else
    echo -e "${GREEN}✓ Frontend .env уже существует${NC}"
fi

# Сборка frontend
yarn build --silent
check_status "Frontend собран"

# 10. Настройка Supervisor
echo -e "${YELLOW}[10/12] Настройка Supervisor...${NC}"
cat > /etc/supervisor/conf.d/tyres-app.conf << 'EOF'
[program:tyres-backend]
command=/opt/tyres-app/backend/venv/bin/uvicorn server:app --host 0.0.0.0 --port 8001
directory=/opt/tyres-app/backend
user=root
autostart=true
autorestart=true
stderr_logfile=/var/log/tyres-backend.err.log
stdout_logfile=/var/log/tyres-backend.out.log

[program:tyres-frontend]
command=yarn start
directory=/opt/tyres-app/frontend
user=root
autostart=false
autorestart=false
stderr_logfile=/var/log/tyres-frontend.err.log
stdout_logfile=/var/log/tyres-frontend.out.log
environment=PORT="3000"
EOF

supervisorctl reread
supervisorctl update
supervisorctl start tyres-backend
check_status "Supervisor настроен и запущен"

# 11. Настройка Nginx
echo -e "${YELLOW}[11/12] Настройка Nginx...${NC}"

if [ -n "$DOMAIN_NAME" ]; then
    # Создаем конфигурацию Nginx для домена
    cat > /etc/nginx/sites-available/tyres-app << EOF
server {
    listen 80;
    server_name $DOMAIN_NAME;

    # Proxy для backend API
    location /api {
        proxy_pass http://localhost:8001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
    }

    # Proxy для frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_cache_bypass \$http_upgrade;
    }
}
EOF

    # Активируем конфигурацию
    ln -sf /etc/nginx/sites-available/tyres-app /etc/nginx/sites-enabled/
    rm -f /etc/nginx/sites-enabled/default
    
    # Проверяем конфигурацию nginx
    nginx -t
    check_status "Nginx настроен"
    
    # Перезапускаем nginx
    systemctl restart nginx
else
    echo -e "${GREEN}✓ Nginx пропущен (режим разработки)${NC}"
fi

# 12. Установка SSL сертификата
if [ "$USE_HTTPS" = true ]; then
    echo -e "${YELLOW}[12/12] Установка SSL сертификата (Let's Encrypt)...${NC}"
    
    # Проверка что домен резолвится
    echo "Проверка DNS для домена $DOMAIN_NAME..."
    if ! host $DOMAIN_NAME > /dev/null 2>&1; then
        echo -e "${YELLOW}Предупреждение: Домен $DOMAIN_NAME не резолвится${NC}"
        echo -e "${YELLOW}Убедитесь что DNS настроен правильно${NC}"
        read -p "Продолжить установку SSL? (y/n): " CONTINUE_SSL
        if [[ "$CONTINUE_SSL" != "y" && "$CONTINUE_SSL" != "Y" ]]; then
            echo -e "${YELLOW}SSL установка пропущена. Вы можете установить SSL позже командой:${NC}"
            echo -e "${YELLOW}sudo certbot --nginx -d $DOMAIN_NAME${NC}"
            USE_HTTPS=false
        fi
    fi
    
    if [ "$USE_HTTPS" = true ]; then
        # Получаем сертификат
        certbot --nginx -d $DOMAIN_NAME --non-interactive --agree-tos --email $LETSENCRYPT_EMAIL --redirect
        
        if [ $? -eq 0 ]; then
            check_status "SSL сертификат установлен"
            
            # Настраиваем автообновление
            systemctl enable certbot.timer
            systemctl start certbot.timer
            echo -e "${GREEN}✓ Автообновление SSL настроено${NC}"
        else
            echo -e "${RED}✗ Не удалось установить SSL сертификат${NC}"
            echo -e "${YELLOW}Проверьте что:${NC}"
            echo "  1. Домен $DOMAIN_NAME указывает на IP этого сервера"
            echo "  2. Порты 80 и 443 открыты в файрволе"
            echo "  3. Nginx запущен и работает"
            echo ""
            echo "Вы можете установить SSL позже командой:"
            echo -e "${YELLOW}sudo certbot --nginx -d $DOMAIN_NAME${NC}"
        fi
    fi
else
    echo -e "${GREEN}✓ SSL установка пропущена${NC}"
fi

echo ""
echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}  Установка завершена!${NC}"
echo -e "${GREEN}================================${NC}"
echo ""

if [ -n "$DOMAIN_NAME" ]; then
    if [ "$USE_HTTPS" = true ]; then
        echo -e "🌐 Приложение доступно по адресу: ${GREEN}https://$DOMAIN_NAME${NC}"
        echo -e "📱 Используйте этот URL в настройках Telegram Mini App"
    else
        echo -e "🌐 Приложение доступно по адресу: ${GREEN}http://$DOMAIN_NAME${NC}"
        echo -e "📱 ${YELLOW}Внимание:${NC} Для Telegram Mini App требуется HTTPS"
    fi
    echo ""
    echo -e "Backend API: ${YELLOW}https://$DOMAIN_NAME/api${NC}" 
    echo -e "Frontend: ${YELLOW}https://$DOMAIN_NAME${NC}"
else
    echo -e "Backend доступен по адресу: ${YELLOW}http://localhost:8001${NC}"
    echo -e "Frontend доступен по адресу: ${YELLOW}http://localhost:3000${NC}"
fi

echo ""

# Проверяем были ли введены учетные данные
if [ "$FOURTHCHKI_LOGIN" != "your_login_here" ] && [ -n "$FOURTHCHKI_LOGIN" ]; then
    echo -e "${GREEN}✅ Учетные данные настроены${NC}"
    echo ""
    echo "Учетные данные сохранены в:"
    echo -e "  ${YELLOW}$APP_DIR/backend/.env${NC}"
    echo ""
else
    echo -e "${YELLOW}⚠️  ВАЖНО: Необходимо добавить учетные данные${NC}"
    echo ""
    echo "Отредактируйте файл:"
    echo -e "  ${YELLOW}$APP_DIR/backend/.env${NC}"
    echo ""
    echo "Добавьте учетные данные:"
    echo "  - FOURTHCHKI_LOGIN=ваш_логин"
    echo "  - FOURTHCHKI_PASSWORD=ваш_пароль"
    echo "  - TELEGRAM_BOT_TOKEN=токен_вашего_бота"
    echo "  - ADMIN_TELEGRAM_ID=ваш_telegram_id"
    echo ""
    echo "После редактирования перезапустите сервисы:"
    echo -e "  ${YELLOW}sudo supervisorctl restart all${NC}"
    echo ""
fi

echo "Для изменения учетных данных в любой момент:"
echo -e "  ${YELLOW}nano $APP_DIR/backend/.env${NC}"
echo "  Затем: ${YELLOW}sudo supervisorctl restart all${NC}"
echo ""
echo "Полезные команды:"
echo -e "  Проверка статуса: ${YELLOW}sudo supervisorctl status${NC}"
echo -e "  Просмотр логов backend: ${YELLOW}tail -f /var/log/tyres-backend.out.log${NC}"
echo -e "  Просмотр логов frontend: ${YELLOW}tail -f /var/log/tyres-frontend.out.log${NC}"
echo -e "  Просмотр логов nginx: ${YELLOW}tail -f /var/log/nginx/error.log${NC}"
echo ""

if [ "$USE_HTTPS" = true ]; then
    echo -e "${GREEN}✓ SSL сертификат установлен и будет обновляться автоматически${NC}"
    echo ""
fi

echo -e "${GREEN}🎉 Готово к работе!${NC}"
echo ""
echo -e "${BLUE}Документация по API 4tochki:${NC}"
echo -e "  https://b2b.4tochki.ru/Help/Page?url=index.html"
echo ""
