#!/bin/bash

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
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
echo -e "${YELLOW}[2/10] Установка базовых зависимостей...${NC}"
apt-get install -y curl wget git supervisor nginx -qq
check_status "Базовые зависимости установлены"

# 3. Установка Python 3.11
echo -e "${YELLOW}[3/10] Установка Python 3.11...${NC}"
if ! command -v python3.11 &> /dev/null; then
    apt-get install -y software-properties-common -qq
    add-apt-repository ppa:deadsnakes/ppa -y
    apt-get update -qq
    apt-get install -y python3.11 python3.11-venv python3-pip -qq
    check_status "Python 3.11 установлен"
else
    echo -e "${GREEN}✓ Python 3.11 уже установлен${NC}"
fi

# 4. Установка Node.js 18
echo -e "${YELLOW}[4/10] Установка Node.js 18...${NC}"
if ! command -v node &> /dev/null; then
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
    apt-get install -y nodejs -qq
    check_status "Node.js установлен"
else
    echo -e "${GREEN}✓ Node.js уже установлен${NC}"
fi

# 5. Установка Yarn
echo -e "${YELLOW}[5/10] Установка Yarn...${NC}"
if ! command -v yarn &> /dev/null; then
    npm install -g yarn --silent
    check_status "Yarn установлен"
else
    echo -e "${GREEN}✓ Yarn уже установлен${NC}"
fi

# 6. Установка MongoDB
echo -e "${YELLOW}[6/10] Установка MongoDB...${NC}"
if ! command -v mongod &> /dev/null; then
    wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc | apt-key add -
    echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/6.0 multiverse" | tee /etc/apt/sources.list.d/mongodb-org-6.0.list
    apt-get update -qq
    apt-get install -y mongodb-org -qq
    systemctl enable mongod
    systemctl start mongod
    check_status "MongoDB установлен и запущен"
else
    echo -e "${GREEN}✓ MongoDB уже установлен${NC}"
    systemctl start mongod 2>/dev/null
fi

# 7. Клонирование репозитория
echo -e "${YELLOW}[7/10] Клонирование репозитория...${NC}"
APP_DIR="/opt/tyres-app"
if [ -d "$APP_DIR" ]; then
    echo "Директория $APP_DIR существует. Удаляю старую версию..."
    rm -rf $APP_DIR
fi
git clone https://github.com/wrx861/tyres.git $APP_DIR
cd $APP_DIR
check_status "Репозиторий клонирован"

# 8. Настройка backend
echo -e "${YELLOW}[8/10] Настройка backend...${NC}"
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
MONGO_URL=mongodb://localhost:27017/tyres_db
FOURTHCHKI_LOGIN=your_login_here
FOURTHCHKI_PASSWORD=your_password_here
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_ADMIN_ID=your_admin_id_here
USE_MOCK_DATA=false
EOF
    check_status "Backend .env создан"
else
    echo -e "${GREEN}✓ Backend .env уже существует${NC}"
fi

deactivate

# 9. Настройка frontend
echo -e "${YELLOW}[9/10] Настройка frontend...${NC}"
cd $APP_DIR/frontend

# Установка зависимостей
yarn install --silent
check_status "Frontend зависимости установлены"

# Настройка .env файла
if [ ! -f .env ]; then
    cat > .env << EOF
REACT_APP_BACKEND_URL=http://localhost:8001
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
echo -e "${YELLOW}[10/10] Настройка Supervisor...${NC}"
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
autostart=true
autorestart=true
stderr_logfile=/var/log/tyres-frontend.err.log
stdout_logfile=/var/log/tyres-frontend.out.log
environment=PORT="3000"
EOF

supervisorctl reread
supervisorctl update
supervisorctl restart all
check_status "Supervisor настроен и запущен"

echo ""
echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}  Установка завершена!${NC}"
echo -e "${GREEN}================================${NC}"
echo ""
echo -e "Backend доступен по адресу: ${YELLOW}http://localhost:8001${NC}"
echo -e "Frontend доступен по адресу: ${YELLOW}http://localhost:3000${NC}"
echo ""
echo -e "${YELLOW}ВАЖНО:${NC} Отредактируйте файлы .env:"
echo -e "  - ${YELLOW}$APP_DIR/backend/.env${NC} - добавьте учетные данные 4tochki API и Telegram"
echo -e "  - ${YELLOW}$APP_DIR/frontend/.env${NC} - укажите корректный REACT_APP_BACKEND_URL"
echo ""
echo "После редактирования перезапустите сервисы:"
echo -e "  ${YELLOW}sudo supervisorctl restart all${NC}"
echo ""
echo "Проверка статуса:"
echo -e "  ${YELLOW}sudo supervisorctl status${NC}"
echo ""
echo -e "${GREEN}Готово к работе!${NC}"
