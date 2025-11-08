#!/bin/bash

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}  Проверка установки${NC}"
echo -e "${GREEN}================================${NC}"
echo ""

# Проверка прав root
if [[ $EUID -ne 0 ]]; then
   echo -e "${YELLOW}Запустите с sudo для полной проверки${NC}"
fi

# Функция для проверки
check_status() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ $1${NC}"
        return 0
    else
        echo -e "${RED}✗ $1${NC}"
        return 1
    fi
}

# 1. Проверка директории приложения
echo -e "${YELLOW}[1/10] Проверка директории приложения...${NC}"
if [ -d "/opt/tyres-app" ]; then
    echo -e "${GREEN}✓ Директория /opt/tyres-app найдена${NC}"
    APP_DIR="/opt/tyres-app"
else
    echo -e "${RED}✗ Директория /opt/tyres-app не найдена${NC}"
    echo -e "${YELLOW}→ Приложение не установлено или установлено в другое место${NC}"
    exit 1
fi
echo ""

# 2. Проверка файлов
echo -e "${YELLOW}[2/10] Проверка файлов...${NC}"
[ -f "$APP_DIR/backend/server.py" ] && echo -e "${GREEN}✓ Backend найден${NC}" || echo -e "${RED}✗ Backend не найден${NC}"
[ -f "$APP_DIR/frontend/package.json" ] && echo -e "${GREEN}✓ Frontend найден${NC}" || echo -e "${RED}✗ Frontend не найден${NC}"
[ -f "$APP_DIR/backend/.env" ] && echo -e "${GREEN}✓ Backend .env найден${NC}" || echo -e "${RED}✗ Backend .env не найден${NC}"
[ -f "$APP_DIR/frontend/.env" ] && echo -e "${GREEN}✓ Frontend .env найден${NC}" || echo -e "${RED}✗ Frontend .env не найден${NC}"
echo ""

# 3. Проверка Python зависимостей
echo -e "${YELLOW}[3/10] Проверка Python окружения...${NC}"
if [ -d "$APP_DIR/backend/venv" ]; then
    echo -e "${GREEN}✓ Python venv найден${NC}"
    PYTHON="$APP_DIR/backend/venv/bin/python"
    $PYTHON --version 2>&1 | grep -q "Python 3" && echo -e "${GREEN}✓ Python 3 установлен${NC}" || echo -e "${RED}✗ Python 3 не найден${NC}"
else
    echo -e "${RED}✗ Python venv не найден${NC}"
fi
echo ""

# 4. Проверка Node.js зависимостей
echo -e "${YELLOW}[4/10] Проверка Node.js...${NC}"
if [ -d "$APP_DIR/frontend/node_modules" ]; then
    echo -e "${GREEN}✓ node_modules найдены${NC}"
else
    echo -e "${RED}✗ node_modules не найдены${NC}"
fi
if [ -d "$APP_DIR/frontend/build" ]; then
    echo -e "${GREEN}✓ Frontend собран (build/ существует)${NC}"
else
    echo -e "${YELLOW}⚠ Frontend не собран (build/ не найден)${NC}"
fi
echo ""

# 5. Проверка Supervisor
echo -e "${YELLOW}[5/10] Проверка Supervisor...${NC}"
if command -v supervisorctl &> /dev/null; then
    echo -e "${GREEN}✓ Supervisor установлен${NC}"
    
    # Проверка процессов
    if supervisorctl status | grep -q "tyres-backend"; then
        BACKEND_STATUS=$(supervisorctl status tyres-backend | awk '{print $2}')
        if [ "$BACKEND_STATUS" = "RUNNING" ]; then
            echo -e "${GREEN}✓ tyres-backend: RUNNING${NC}"
        else
            echo -e "${RED}✗ tyres-backend: $BACKEND_STATUS${NC}"
        fi
    else
        echo -e "${RED}✗ tyres-backend не найден в supervisor${NC}"
    fi
    
    if supervisorctl status | grep -q "tyres-frontend"; then
        FRONTEND_STATUS=$(supervisorctl status tyres-frontend | awk '{print $2}')
        if [ "$FRONTEND_STATUS" = "RUNNING" ]; then
            echo -e "${GREEN}✓ tyres-frontend: RUNNING${NC}"
        else
            echo -e "${RED}✗ tyres-frontend: $FRONTEND_STATUS${NC}"
        fi
    else
        echo -e "${RED}✗ tyres-frontend не найден в supervisor${NC}"
    fi
else
    echo -e "${RED}✗ Supervisor не установлен${NC}"
fi
echo ""

# 6. Проверка MongoDB
echo -e "${YELLOW}[6/10] Проверка MongoDB...${NC}"
if command -v mongosh &> /dev/null || command -v mongo &> /dev/null; then
    echo -e "${GREEN}✓ MongoDB CLI установлен${NC}"
    if systemctl is-active --quiet mongod; then
        echo -e "${GREEN}✓ MongoDB запущен${NC}"
    else
        echo -e "${RED}✗ MongoDB не запущен${NC}"
    fi
else
    echo -e "${YELLOW}⚠ MongoDB CLI не найден${NC}"
fi
echo ""

# 7. Проверка Nginx
echo -e "${YELLOW}[7/10] Проверка Nginx...${NC}"
if command -v nginx &> /dev/null; then
    echo -e "${GREEN}✓ Nginx установлен${NC}"
    
    nginx -t &> /dev/null
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Nginx конфигурация валидна${NC}"
    else
        echo -e "${RED}✗ Nginx конфигурация невалидна${NC}"
    fi
    
    if systemctl is-active --quiet nginx; then
        echo -e "${GREEN}✓ Nginx запущен${NC}"
    else
        echo -e "${RED}✗ Nginx не запущен${NC}"
    fi
    
    # Проверка конфигурации для tyres
    if [ -f "/etc/nginx/sites-available/tyres-app" ] || [ -f "/etc/nginx/sites-available/tyres" ]; then
        echo -e "${GREEN}✓ Nginx конфигурация для tyres найдена${NC}"
    else
        echo -e "${YELLOW}⚠ Nginx конфигурация для tyres не найдена${NC}"
    fi
else
    echo -e "${RED}✗ Nginx не установлен${NC}"
fi
echo ""

# 8. Проверка портов
echo -e "${YELLOW}[8/10] Проверка портов...${NC}"
netstat -tulnp 2>/dev/null | grep -q ":8001 " && echo -e "${GREEN}✓ Backend порт 8001 слушается${NC}" || echo -e "${RED}✗ Backend порт 8001 не слушается${NC}"
netstat -tulnp 2>/dev/null | grep -q ":3000 " && echo -e "${GREEN}✓ Frontend порт 3000 слушается${NC}" || echo -e "${RED}✗ Frontend порт 3000 не слушается${NC}"
netstat -tulnp 2>/dev/null | grep -q ":80 " && echo -e "${GREEN}✓ Nginx порт 80 слушается${NC}" || echo -e "${RED}✗ Nginx порт 80 не слушается${NC}"
netstat -tulnp 2>/dev/null | grep -q ":443 " && echo -e "${GREEN}✓ Nginx порт 443 (SSL) слушается${NC}" || echo -e "${YELLOW}⚠ Nginx порт 443 не слушается (SSL не установлен)${NC}"
echo ""

# 9. Проверка Backend API
echo -e "${YELLOW}[9/10] Проверка Backend API...${NC}"
HEALTH_RESPONSE=$(curl -s http://localhost:8001/api/health 2>/dev/null)
if echo "$HEALTH_RESPONSE" | grep -q "healthy"; then
    echo -e "${GREEN}✓ Backend API отвечает${NC}"
    echo -e "${BLUE}   Response: $HEALTH_RESPONSE${NC}"
else
    echo -e "${RED}✗ Backend API не отвечает${NC}"
fi
echo ""

# 10. Проверка Frontend
echo -e "${YELLOW}[10/10] Проверка Frontend...${NC}"
FRONTEND_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 2>/dev/null)
if [ "$FRONTEND_RESPONSE" = "200" ]; then
    echo -e "${GREEN}✓ Frontend отвечает (HTTP $FRONTEND_RESPONSE)${NC}"
else
    echo -e "${RED}✗ Frontend не отвечает (HTTP $FRONTEND_RESPONSE)${NC}"
fi
echo ""

# Итоговый статус
echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}  Итоговая информация${NC}"
echo -e "${GREEN}================================${NC}"
echo ""

# Backend URL из .env
if [ -f "$APP_DIR/frontend/.env" ]; then
    BACKEND_URL=$(grep REACT_APP_BACKEND_URL $APP_DIR/frontend/.env | cut -d'=' -f2 | tr -d '"')
    echo -e "${BLUE}Backend URL:${NC} $BACKEND_URL"
fi

# Telegram Bot Token
if [ -f "$APP_DIR/backend/.env" ]; then
    BOT_TOKEN=$(grep TELEGRAM_BOT_TOKEN $APP_DIR/backend/.env | cut -d'=' -f2 | tr -d '"')
    if [ -n "$BOT_TOKEN" ]; then
        echo -e "${BLUE}Telegram Bot:${NC} Настроен (Token: ${BOT_TOKEN:0:10}...)"
    else
        echo -e "${YELLOW}Telegram Bot:${NC} Не настроен"
    fi
    
    ADMIN_ID=$(grep ADMIN_TELEGRAM_ID $APP_DIR/backend/.env | cut -d'=' -f2 | tr -d '"')
    if [ -n "$ADMIN_ID" ]; then
        echo -e "${BLUE}Admin ID:${NC} $ADMIN_ID"
    fi
fi

echo ""
echo -e "${BLUE}Полезные команды:${NC}"
echo "  Статус сервисов: sudo supervisorctl status"
echo "  Логи backend: tail -f /var/log/tyres-backend.err.log"
echo "  Логи frontend: tail -f /var/log/tyres-frontend.err.log"
echo "  Перезапуск: sudo supervisorctl restart tyres-backend tyres-frontend"
echo ""

# Рекомендации
echo -e "${YELLOW}Рекомендации:${NC}"

ISSUES=0

if ! supervisorctl status | grep -q "tyres-frontend.*RUNNING"; then
    echo -e "${RED}1. Frontend не запущен${NC}"
    echo "   → sudo supervisorctl start tyres-frontend"
    ISSUES=$((ISSUES + 1))
fi

if ! supervisorctl status | grep -q "tyres-backend.*RUNNING"; then
    echo -e "${RED}2. Backend не запущен${NC}"
    echo "   → sudo supervisorctl start tyres-backend"
    ISSUES=$((ISSUES + 1))
fi

if ! netstat -tulnp 2>/dev/null | grep -q ":443 "; then
    echo -e "${YELLOW}3. SSL не установлен${NC}"
    echo "   → sudo bash /opt/tyres-app/change-domain.sh -d YOUR_DOMAIN -e YOUR_EMAIL"
    ISSUES=$((ISSUES + 1))
fi

if [ $ISSUES -eq 0 ]; then
    echo -e "${GREEN}✓ Всё работает отлично!${NC}"
fi

echo ""
