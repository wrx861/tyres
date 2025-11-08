#!/bin/bash

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}  Смена домена и SSL сертификата${NC}"
echo -e "${GREEN}================================${NC}"
echo ""

# Проверка прав root
if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}Этот скрипт должен быть запущен с правами root${NC}"
   echo ""
   echo "Использование:"
   echo "  sudo bash change-domain.sh -d new-domain.com -e admin@example.com"
   echo "  sudo bash change-domain.sh -d new-domain.com --no-ssl"
   echo "  sudo bash change-domain.sh --help"
   exit 1
fi

# Параметры по умолчанию
NEW_DOMAIN=""
LETSENCRYPT_EMAIL=""
USE_SSL=true
FORCE=false
APP_DIR="/opt/tyres-app"

# Парсинг аргументов
while [[ $# -gt 0 ]]; do
    case $1 in
        -d|--domain)
            NEW_DOMAIN="$2"
            shift 2
            ;;
        -e|--email)
            LETSENCRYPT_EMAIL="$2"
            shift 2
            ;;
        --no-ssl)
            USE_SSL=false
            shift
            ;;
        -f|--force)
            FORCE=true
            shift
            ;;
        -h|--help)
            echo "Использование: sudo bash change-domain.sh [ОПЦИИ]"
            echo ""
            echo "Опции:"
            echo "  -d, --domain DOMAIN      Новый домен (обязательно)"
            echo "  -e, --email EMAIL        Email для Let's Encrypt (обязательно для SSL)"
            echo "  --no-ssl                 Не получать SSL сертификат"
            echo "  -f, --force              Пропустить проверки DNS и портов"
            echo "  -h, --help               Показать эту справку"
            echo ""
            echo "Примеры:"
            echo "  # Смена домена с SSL"
            echo "  sudo bash change-domain.sh -d tires.newdomain.com -e admin@example.com"
            echo ""
            echo "  # Смена домена без SSL"
            echo "  sudo bash change-domain.sh -d tires.newdomain.com --no-ssl"
            echo ""
            echo "  # Принудительная смена (без проверок)"
            echo "  sudo bash change-domain.sh -d tires.newdomain.com -e admin@example.com -f"
            exit 0
            ;;
        *)
            echo -e "${RED}Неизвестная опция: $1${NC}"
            echo "Используйте --help для справки"
            exit 1
            ;;
    esac
done

# Проверка обязательных параметров
if [ -z "$NEW_DOMAIN" ]; then
    echo -e "${RED}Ошибка: Домен не указан${NC}"
    echo "Используйте: sudo bash change-domain.sh -d new-domain.com -e admin@example.com"
    exit 1
fi

if [ "$USE_SSL" = true ] && [ -z "$LETSENCRYPT_EMAIL" ]; then
    echo -e "${RED}Ошибка: Email обязателен для получения SSL сертификата${NC}"
    echo "Используйте: sudo bash change-domain.sh -d $NEW_DOMAIN -e admin@example.com"
    echo "Или без SSL: sudo bash change-domain.sh -d $NEW_DOMAIN --no-ssl"
    exit 1
fi

# Проверка что директория приложения существует
if [ ! -d "$APP_DIR" ]; then
    echo -e "${RED}Ошибка: Директория $APP_DIR не найдена${NC}"
    echo "Убедитесь что приложение установлено."
    exit 1
fi

echo -e "${BLUE}Новый домен:${NC} $NEW_DOMAIN"
if [ "$USE_SSL" = true ]; then
    echo -e "${BLUE}SSL:${NC} Да (Email: $LETSENCRYPT_EMAIL)"
else
    echo -e "${BLUE}SSL:${NC} Нет"
fi
echo ""

# Функция для проверки успешности команды
check_status() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ $1${NC}"
        return 0
    else
        echo -e "${RED}✗ Ошибка: $1${NC}"
        return 1
    fi
}

# Получаем текущий IP сервера
SERVER_IP=$(curl -s ifconfig.me || curl -s icanhazip.com)
echo -e "${BLUE}IP сервера:${NC} $SERVER_IP"
echo ""

# Проверки (можно пропустить с флагом --force)
if [ "$FORCE" = false ]; then
    echo -e "${YELLOW}[1/11] Проверка DNS...${NC}"
    DOMAIN_IP=$(dig +short $NEW_DOMAIN | tail -n1)
    
    if [ -z "$DOMAIN_IP" ]; then
        echo -e "${RED}✗ DNS запись для $NEW_DOMAIN не найдена${NC}"
        echo ""
        echo "Создайте A-запись:"
        echo "  $NEW_DOMAIN → $SERVER_IP"
        echo ""
        echo "Для принудительного продолжения используйте флаг --force"
        exit 1
    fi
    
    if [ "$DOMAIN_IP" != "$SERVER_IP" ]; then
        echo -e "${YELLOW}⚠ Домен указывает на другой IP${NC}"
        echo "  Домен → $DOMAIN_IP"
        echo "  Сервер → $SERVER_IP"
        echo ""
        read -p "Продолжить? (y/n): " CONTINUE
        if [[ ! $CONTINUE =~ ^[Yy]$ ]]; then
            echo "Отменено."
            exit 0
        fi
    else
        echo -e "${GREEN}✓ DNS настроен корректно${NC}"
    fi
    
    # Проверка портов для SSL
    if [ "$USE_SSL" = true ]; then
        echo -e "${YELLOW}Проверка портов 80 и 443...${NC}"
        
        if ! netstat -tulnp | grep -q ":80 "; then
            echo -e "${YELLOW}⚠ Порт 80 не прослушивается${NC}"
        else
            echo -e "${GREEN}✓ Порт 80 открыт${NC}"
        fi
        
        if ! netstat -tulnp | grep -q ":443 "; then
            echo -e "${YELLOW}⚠ Порт 443 не прослушивается (будет открыт после получения SSL)${NC}"
        else
            echo -e "${GREEN}✓ Порт 443 открыт${NC}"
        fi
    fi
else
    echo -e "${YELLOW}[1/11] Проверка DNS пропущена (--force)${NC}"
fi
echo ""

# Создание backup
echo -e "${YELLOW}[2/11] Создание backup конфигураций...${NC}"
BACKUP_DIR="/opt/tyres-app-domain-backup-$(date +%Y%m%d_%H%M%S)"
mkdir -p $BACKUP_DIR

# Определяем имя nginx конфига для backup
NGINX_BACKUP_NAME=""
if [ -f "/etc/nginx/sites-available/tyres-app" ]; then
    NGINX_BACKUP_NAME="tyres-app"
elif [ -f "/etc/nginx/sites-available/tyres" ]; then
    NGINX_BACKUP_NAME="tyres"
fi

# Backup nginx конфигурации
if [ -n "$NGINX_BACKUP_NAME" ]; then
    cp /etc/nginx/sites-available/$NGINX_BACKUP_NAME $BACKUP_DIR/nginx-$NGINX_BACKUP_NAME
    check_status "Backup nginx конфигурации"
fi

# Backup .env файлов
if [ -f "$APP_DIR/frontend/.env" ]; then
    cp $APP_DIR/frontend/.env $BACKUP_DIR/frontend.env
    check_status "Backup frontend .env"
fi

if [ -f "$APP_DIR/backend/.env" ]; then
    cp $APP_DIR/backend/.env $BACKUP_DIR/backend.env
    check_status "Backup backend .env"
fi

echo -e "${GREEN}✓ Backup создан: $BACKUP_DIR${NC}"
echo ""

# Сохраняем старый домен
OLD_BACKEND_URL=$(grep REACT_APP_BACKEND_URL $APP_DIR/frontend/.env | cut -d'=' -f2 | tr -d '"' || echo "")
if [ -n "$OLD_BACKEND_URL" ]; then
    OLD_DOMAIN=$(echo $OLD_BACKEND_URL | sed 's|https\?://||' | sed 's|/.*||')
    echo -e "${BLUE}Старый домен:${NC} $OLD_DOMAIN"
else
    OLD_DOMAIN="localhost"
fi
echo ""

# Обновление nginx конфигурации
echo -e "${YELLOW}[3/11] Обновление nginx конфигурации...${NC}"

# Определяем имя конфигурационного файла
if [ -f "/etc/nginx/sites-available/tyres-app" ]; then
    NGINX_CONFIG_NAME="tyres-app"
elif [ -f "/etc/nginx/sites-available/tyres" ]; then
    NGINX_CONFIG_NAME="tyres"
else
    # Создаем новый файл
    NGINX_CONFIG_NAME="tyres-app"
fi

NGINX_CONFIG="/etc/nginx/sites-available/$NGINX_CONFIG_NAME"

if [ "$USE_SSL" = true ]; then
    # Сначала создаем конфигурацию для HTTP (для получения SSL)
    cat > $NGINX_CONFIG << EOF
server {
    listen 80;
    server_name $NEW_DOMAIN;
    
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_cache_bypass \$http_upgrade;
    }
    
    location /api {
        proxy_pass http://localhost:8001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_cache_bypass \$http_upgrade;
    }
}
EOF
else
    # Конфигурация без SSL
    cat > $NGINX_CONFIG << EOF
server {
    listen 80;
    server_name $NEW_DOMAIN;
    
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_cache_bypass \$http_upgrade;
    }
    
    location /api {
        proxy_pass http://localhost:8001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_cache_bypass \$http_upgrade;
    }
}
EOF
fi

check_status "Nginx конфигурация обновлена"

# Создаем symlink если нужно
if [ ! -L "/etc/nginx/sites-enabled/$NGINX_CONFIG_NAME" ]; then
    ln -s $NGINX_CONFIG /etc/nginx/sites-enabled/$NGINX_CONFIG_NAME
    echo -e "${GREEN}✓ Symlink создан${NC}"
fi

# Проверка конфигурации nginx
echo -e "${YELLOW}Проверка конфигурации nginx...${NC}"
nginx -t
if [ $? -ne 0 ]; then
    echo -e "${RED}✗ Ошибка в конфигурации nginx${NC}"
    echo -e "${YELLOW}Откат к backup...${NC}"
    if [ -f "$BACKUP_DIR/nginx-$NGINX_CONFIG_NAME" ]; then
        cp $BACKUP_DIR/nginx-$NGINX_CONFIG_NAME $NGINX_CONFIG
    fi
    nginx -t
    exit 1
fi
echo -e "${GREEN}✓ Конфигурация nginx валидна${NC}"
echo ""

# Перезапуск nginx
echo -e "${YELLOW}[4/11] Перезапуск nginx...${NC}"
systemctl reload nginx
check_status "Nginx перезапущен"
echo ""

# Получение SSL сертификата
if [ "$USE_SSL" = true ]; then
    echo -e "${YELLOW}[5/11] Получение SSL сертификата...${NC}"
    echo -e "${BLUE}Домен:${NC} $NEW_DOMAIN"
    echo -e "${BLUE}Email:${NC} $LETSENCRYPT_EMAIL"
    echo ""
    
    # Пробуем автоматическую установку
    certbot --nginx -d $NEW_DOMAIN --email $LETSENCRYPT_EMAIL --agree-tos --non-interactive --redirect 2>&1 | tee /tmp/certbot_output.log
    
    # Проверяем результат
    if grep -q "Successfully received certificate" /tmp/certbot_output.log; then
        echo -e "${GREEN}✓ SSL сертификат получен${NC}"
        
        # Проверяем установлен ли он в nginx
        if grep -q "Deploying certificate" /tmp/certbot_output.log && ! grep -q "Could not install certificate" /tmp/certbot_output.log; then
            echo -e "${GREEN}✓ SSL сертификат установлен в nginx${NC}"
            NEW_BACKEND_URL="https://$NEW_DOMAIN"
        else
            echo -e "${YELLOW}⚠ SSL сертификат получен, но не установлен автоматически${NC}"
            echo -e "${YELLOW}→ Устанавливаем вручную...${NC}"
            
            # Ручная установка SSL в nginx конфигурацию
            cat > $NGINX_CONFIG << EOF
server {
    listen 80;
    server_name $NEW_DOMAIN;
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name $NEW_DOMAIN;
    
    ssl_certificate /etc/letsencrypt/live/$NEW_DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$NEW_DOMAIN/privkey.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_cache_bypass \$http_upgrade;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    location /api {
        proxy_pass http://localhost:8001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_cache_bypass \$http_upgrade;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF
            
            # Проверяем конфигурацию
            if nginx -t > /dev/null 2>&1; then
                systemctl reload nginx
                echo -e "${GREEN}✓ SSL сертификат установлен вручную${NC}"
                NEW_BACKEND_URL="https://$NEW_DOMAIN"
            else
                echo -e "${RED}✗ Ошибка конфигурации nginx${NC}"
                USE_SSL=false
                NEW_BACKEND_URL="http://$NEW_DOMAIN"
            fi
        fi
    else
        echo -e "${RED}✗ Ошибка получения SSL сертификата${NC}"
        echo -e "${YELLOW}Продолжаем без SSL...${NC}"
        USE_SSL=false
        NEW_BACKEND_URL="http://$NEW_DOMAIN"
    fi
else
    echo -e "${YELLOW}[5/11] Получение SSL пропущено${NC}"
    NEW_BACKEND_URL="http://$NEW_DOMAIN"
fi
echo ""

# Обновление frontend/.env
echo -e "${YELLOW}[6/11] Обновление frontend/.env...${NC}"
sed -i "s|REACT_APP_BACKEND_URL=.*|REACT_APP_BACKEND_URL=$NEW_BACKEND_URL|g" $APP_DIR/frontend/.env
check_status "Frontend .env обновлен"

echo -e "${BLUE}Новый REACT_APP_BACKEND_URL:${NC} $NEW_BACKEND_URL"
echo ""

# Пересборка frontend
echo -e "${YELLOW}[7/11] Пересборка frontend с новым URL...${NC}"
cd $APP_DIR/frontend
yarn build > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Frontend пересобран${NC}"
else
    echo -e "${RED}✗ Ошибка пересборки frontend${NC}"
    echo -e "${YELLOW}Откат...${NC}"
    cp $BACKUP_DIR/frontend.env $APP_DIR/frontend/.env
    cp $BACKUP_DIR/nginx-tyres /etc/nginx/sites-available/tyres
    systemctl reload nginx
    exit 1
fi
echo ""

# Перезапуск сервисов
echo -e "${YELLOW}[8/11] Перезапуск сервисов...${NC}"

# Определяем имена процессов supervisor
if supervisorctl status | grep -q "tyres-frontend"; then
    FRONTEND_NAME="tyres-frontend"
    BACKEND_NAME="tyres-backend"
else
    FRONTEND_NAME="frontend"
    BACKEND_NAME="backend"
fi

supervisorctl restart $FRONTEND_NAME
sleep 2
check_status "Frontend перезапущен"

supervisorctl restart $BACKEND_NAME
sleep 2
check_status "Backend перезапущен"
echo ""

# Проверка работоспособности
echo -e "${YELLOW}[9/11] Проверка работоспособности...${NC}"
sleep 3

# Проверка nginx
if systemctl is-active --quiet nginx; then
    echo -e "${GREEN}✓ Nginx работает${NC}"
else
    echo -e "${RED}✗ Nginx не работает${NC}"
fi

# Проверка backend
if curl -s http://localhost:8001/api/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Backend API работает${NC}"
else
    echo -e "${YELLOW}⚠ Backend API не отвечает${NC}"
fi

# Проверка frontend
if curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Frontend работает${NC}"
else
    echo -e "${YELLOW}⚠ Frontend не отвечает${NC}"
fi

# Проверка домена
if [ "$USE_SSL" = true ]; then
    if curl -s -k https://$NEW_DOMAIN > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Домен доступен через HTTPS${NC}"
    else
        echo -e "${YELLOW}⚠ Домен не доступен через HTTPS (возможно DNS еще не обновился)${NC}"
    fi
fi
echo ""

# Настройка автообновления SSL
if [ "$USE_SSL" = true ]; then
    echo -e "${YELLOW}[10/11] Настройка автообновления SSL...${NC}"
    
    # Проверяем что certbot timer активен
    if systemctl is-active --quiet certbot.timer; then
        echo -e "${GREEN}✓ Автообновление SSL уже настроено${NC}"
    else
        systemctl enable certbot.timer
        systemctl start certbot.timer
        check_status "Автообновление SSL настроено"
    fi
else
    echo -e "${YELLOW}[10/11] Автообновление SSL пропущено${NC}"
fi
echo ""

# Очистка старых backup
echo -e "${YELLOW}[11/11] Очистка старых backup...${NC}"
BACKUP_COUNT=$(ls -d /opt/tyres-app-domain-backup-* 2>/dev/null | wc -l)
if [ $BACKUP_COUNT -gt 3 ]; then
    ls -dt /opt/tyres-app-domain-backup-* | tail -n +4 | xargs rm -rf
    REMOVED=$((BACKUP_COUNT - 3))
    echo -e "${GREEN}✓ Удалено старых backup: $REMOVED${NC}"
else
    echo -e "${GREEN}✓ Старых backup нет (всего: $BACKUP_COUNT)${NC}"
fi
echo ""

# Итоговая информация
echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}  Смена домена завершена!${NC}"
echo -e "${GREEN}================================${NC}"
echo ""

echo -e "${BLUE}Старый домен:${NC} $OLD_DOMAIN"
echo -e "${BLUE}Новый домен:${NC} $NEW_DOMAIN"
echo ""

if [ "$USE_SSL" = true ]; then
    echo -e "${GREEN}🌐 Приложение доступно:${NC} https://$NEW_DOMAIN"
    echo -e "${GREEN}📱 Backend API:${NC} https://$NEW_DOMAIN/api"
    echo -e "${GREEN}🔒 SSL:${NC} Установлен и будет обновляться автоматически"
else
    echo -e "${YELLOW}🌐 Приложение доступно:${NC} http://$NEW_DOMAIN"
    echo -e "${YELLOW}📱 Backend API:${NC} http://$NEW_DOMAIN/api"
    echo -e "${YELLOW}⚠️ SSL:${NC} Не установлен"
fi
echo ""

echo -e "${BLUE}Backup конфигураций:${NC} $BACKUP_DIR"
echo ""

echo -e "${YELLOW}Для отката к старому домену:${NC}"
echo "  sudo cp $BACKUP_DIR/frontend.env $APP_DIR/frontend/.env"
echo "  sudo cp $BACKUP_DIR/nginx-tyres /etc/nginx/sites-available/tyres"
echo "  sudo systemctl reload nginx"
echo "  sudo supervisorctl restart all"
echo ""

if [ "$USE_SSL" = true ]; then
    echo -e "${GREEN}✓ Готово! SSL сертификат активен.${NC}"
else
    echo -e "${YELLOW}Для установки SSL позже:${NC}"
    echo "  sudo bash change-domain.sh -d $NEW_DOMAIN -e your-email@example.com"
fi
echo ""

echo -e "${GREEN}🎉 Домен успешно изменен!${NC}"
echo ""
