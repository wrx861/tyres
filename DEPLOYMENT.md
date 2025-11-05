# 🚀 Инструкция по развертыванию на tyres.vpnsuba.ru

## ✅ Что уже готово

- ✅ Backend полностью настроен и работает
- ✅ Frontend полностью готов
- ✅ Mock данные работают (150+ шин, 120+ дисков)
- ✅ MongoDB настроена
- ✅ API endpoints протестированы
- ✅ Система заказов работает
- ✅ Админ-панель функционирует

## 📋 Требования на хостинге

- Ubuntu/Debian Linux
- Python 3.9+
- Node.js 16+ и yarn
- MongoDB
- Nginx
- Supervisor
- SSL сертификат (certbot)
- Открытые порты: 80, 443

## 🔧 Шаг 1: Подготовка сервера

```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка зависимостей
sudo apt install -y python3-pip python3-venv nodejs npm nginx supervisor mongodb certbot python3-certbot-nginx

# Установка yarn
npm install -g yarn

# Создание директории проекта
sudo mkdir -p /app
sudo chown -R $USER:$USER /app
```

## 📦 Шаг 2: Загрузка проекта

```bash
# Перейдите в директорию
cd /app

# Загрузите проект из GitHub (замените на ваш репозиторий)
git clone <your-github-repo-url> .

# Или скопируйте файлы напрямую
```

## 🔑 Шаг 3: Настройка переменных окружения

### Backend (.env)
```bash
cat > /app/backend/.env << 'EOF'
MONGO_URL="mongodb://localhost:27017"
DB_NAME="tires_shop"
CORS_ORIGINS="*"

# 4tochki API
FOURTHCHKI_LOGIN=CarZona
FOURTHCHKI_PASSWORD=Qq28061q.
FOURTHCHKI_API_URL=http://api-b2b.4tochki.ru/WCF/ClientService.svc?wsdl

# Telegram Bot
TELEGRAM_BOT_TOKEN=8290483601:AAFqXwpx1_paoekO0dt3kR46z471zlDKChI
ADMIN_TELEGRAM_ID=508352361

# Settings
DEFAULT_MARKUP_PERCENTAGE=15

# Mock Mode - измените на false когда API заработает
USE_MOCK_DATA=true
EOF
```

### Frontend (.env)
```bash
cat > /app/frontend/.env << 'EOF'
REACT_APP_BACKEND_URL=https://tyres.vpnsuba.ru
WDS_SOCKET_PORT=443
REACT_APP_ENABLE_VISUAL_EDITS=false
ENABLE_HEALTH_CHECK=false
EOF
```

## 📥 Шаг 4: Установка зависимостей

```bash
# Backend
cd /app/backend
pip3 install -r requirements.txt

# Frontend
cd /app/frontend
yarn install
```

## ⚙️ Шаг 5: Настройка Supervisor

```bash
sudo tee /etc/supervisor/conf.d/tyres.conf << 'EOF'
[program:backend]
command=/usr/bin/python3 -m uvicorn server:app --host 0.0.0.0 --port 8001
directory=/app/backend
autostart=true
autorestart=true
stderr_logfile=/var/log/supervisor/backend.err.log
stdout_logfile=/var/log/supervisor/backend.out.log
user=$USER
environment=PATH="/usr/bin",PYTHONUNBUFFERED="1"

[program:frontend]
command=/usr/bin/yarn start
directory=/app/frontend
autostart=true
autorestart=true
stderr_logfile=/var/log/supervisor/frontend.err.log
stdout_logfile=/var/log/supervisor/frontend.out.log
user=$USER
environment=PORT="3000",PATH="/usr/bin:/usr/local/bin"
EOF

# Перезагрузка supervisor
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start all
```

## 🌐 Шаг 6: Настройка Nginx

```bash
sudo tee /etc/nginx/sites-available/tyres << 'EOF'
server {
    listen 80;
    server_name tyres.vpnsuba.ru;

    # Размер загружаемых файлов
    client_max_body_size 10M;

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:8001;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts для API
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }

    # Health check
    location /health {
        proxy_pass http://localhost:8001/api/health;
    }
}
EOF

# Активация конфигурации
sudo ln -sf /etc/nginx/sites-available/tyres /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl reload nginx
```

## 🔒 Шаг 7: Установка SSL сертификата

```bash
# Получить SSL сертификат от Let's Encrypt
sudo certbot --nginx -d tyres.vpnsuba.ru --non-interactive --agree-tos -m your-email@example.com

# Автообновление сертификата
sudo systemctl enable certbot.timer
```

## 🎭 Шаг 8: Настройка Telegram Bot

1. Откройте [@BotFather](https://t.me/botfather) в Telegram
2. Создайте Mini App:
   ```
   /newapp
   - Выберите вашего бота
   - Название: Магазин Шин
   - Описание: Шины и диски с доставкой
   - Фото: загрузите логотип (512x512px)
   - GIF: пропустите
   ```
3. Установите домен:
   ```
   /setappdomain
   - Выберите приложение
   - Введите: tyres.vpnsuba.ru
   ```
4. Настройте меню бота:
   ```
   /setmenubutton
   - Выберите бота
   - Текст кнопки: 🛒 Открыть магазин
   - URL: https://tyres.vpnsuba.ru
   ```

## 🔍 Шаг 9: Проверка работоспособности

```bash
# Проверка статуса сервисов
sudo supervisorctl status

# Должно быть:
# backend    RUNNING
# frontend   RUNNING

# Проверка логов
tail -f /var/log/supervisor/backend.err.log
tail -f /var/log/supervisor/frontend.out.log

# Проверка API
curl https://tyres.vpnsuba.ru/api/health
# Ответ: {"status":"healthy","database":"connected"}

# Проверка Frontend
curl -I https://tyres.vpnsuba.ru
# Ответ: HTTP/2 200
```

## 📊 Шаг 10: Мониторинг

### Просмотр логов
```bash
# Backend
tail -f /var/log/supervisor/backend.err.log

# Frontend
tail -f /var/log/supervisor/frontend.out.log

# Nginx
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

### Перезапуск сервисов
```bash
# Перезапуск backend
sudo supervisorctl restart backend

# Перезапуск frontend
sudo supervisorctl restart frontend

# Перезапуск всех
sudo supervisorctl restart all

# Перезагрузка Nginx
sudo systemctl reload nginx
```

## 🔄 Переключение на реальное API 4tochki

Когда поставщик подтвердит работу API:

```bash
# 1. Остановите backend
sudo supervisorctl stop backend

# 2. Измените режим
sed -i 's/USE_MOCK_DATA=true/USE_MOCK_DATA=false/' /app/backend/.env

# 3. Запустите backend
sudo supervisorctl start backend

# 4. Проверьте работу
curl "https://tyres.vpnsuba.ru/api/products/tires/search?width=185&height=60&diameter=15&page_size=2"
```

## 🐛 Troubleshooting

### Backend не запускается
```bash
# Проверьте зависимости
cd /app/backend
pip3 install -r requirements.txt

# Проверьте MongoDB
sudo systemctl status mongod
sudo systemctl start mongod

# Проверьте логи
tail -100 /var/log/supervisor/backend.err.log
```

### Frontend не запускается
```bash
# Переустановите зависимости
cd /app/frontend
rm -rf node_modules yarn.lock
yarn install

# Проверьте логи
tail -100 /var/log/supervisor/frontend.err.log
```

### API 4tochki не отвечает
```bash
# Включите mock режим
echo "USE_MOCK_DATA=true" >> /app/backend/.env
sudo supervisorctl restart backend

# Свяжитесь с 4tochki
# Тел: (495) 38-000-77, (495) 13-000-77
```

### Nginx ошибки
```bash
# Проверьте конфигурацию
sudo nginx -t

# Проверьте логи
tail -100 /var/log/nginx/error.log

# Перезапустите
sudo systemctl restart nginx
```

## 📈 Оптимизация производительности

### Кэширование статики (опционально)
```bash
# Добавьте в Nginx конфиг для /api location:
location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

### Ограничение rate limit
```bash
# В http секции Nginx:
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;

# В location /api:
limit_req zone=api_limit burst=20 nodelay;
```

## 🔐 Безопасность

```bash
# Firewall
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# Обновления безопасности
sudo apt install unattended-upgrades
sudo dpkg-reconfigure --priority=low unattended-upgrades
```

## ✅ Чеклист готовности к запуску

- [ ] Сервер настроен и обновлен
- [ ] Проект загружен в /app
- [ ] .env файлы настроены
- [ ] Зависимости установлены
- [ ] Supervisor настроен и сервисы запущены
- [ ] Nginx настроен
- [ ] SSL сертификат установлен
- [ ] Telegram Bot создан и настроен
- [ ] Домен tyres.vpnsuba.ru указывает на сервер
- [ ] API тесты проходят успешно
- [ ] Frontend открывается в браузере

## 📞 Поддержка

При проблемах:
1. Проверьте логи (см. раздел Мониторинг)
2. Перезапустите сервисы
3. Свяжитесь с техподдержкой 4tochki: (495) 38-000-77

---

**Успешного запуска! 🚀**
