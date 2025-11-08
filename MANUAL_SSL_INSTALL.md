# 🔧 Ручная установка SSL сертификата

## Когда нужно

Если certbot получил сертификат, но не смог его установить:
```
Successfully received certificate.
Certificate is saved at: /etc/letsencrypt/live/YOUR_DOMAIN/fullchain.pem
...
Could not install certificate
```

---

## ✅ Шаги установки

### 1. Проверьте что сертификат получен

```bash
sudo ls -la /etc/letsencrypt/live/tyres.shopmarketbot.ru/

# Должны быть файлы:
# fullchain.pem
# privkey.pem
# cert.pem
# chain.pem
```

### 2. Найдите nginx конфигурацию

```bash
# На production обычно:
ls -la /etc/nginx/sites-available/

# Ищем: tyres-app или tyres
```

### 3. Создайте SSL конфигурацию

```bash
sudo nano /etc/nginx/sites-available/tyres-app
```

**Содержимое:**

```nginx
# HTTP → HTTPS редирект
server {
    listen 80;
    server_name tyres.shopmarketbot.ru;
    return 301 https://$server_name$request_uri;
}

# HTTPS server
server {
    listen 443 ssl http2;
    server_name tyres.shopmarketbot.ru;
    
    # SSL сертификаты
    ssl_certificate /etc/letsencrypt/live/tyres.shopmarketbot.ru/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/tyres.shopmarketbot.ru/privkey.pem;
    
    # SSL настройки
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # Frontend (React)
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Backend API (FastAPI)
    location /api {
        proxy_pass http://localhost:8001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 4. Проверьте конфигурацию

```bash
sudo nginx -t

# Ожидаем:
# nginx: configuration file /etc/nginx/nginx.conf test is successful
```

### 5. Обновите frontend .env

```bash
sudo nano /opt/tyres-app/frontend/.env
```

Измените:
```bash
REACT_APP_BACKEND_URL=https://tyres.shopmarketbot.ru
```

### 6. Пересоберите frontend

```bash
cd /opt/tyres-app/frontend
yarn build
```

### 7. Перезапустите сервисы

```bash
# Nginx
sudo systemctl reload nginx

# Frontend и Backend
sudo supervisorctl restart tyres-frontend
sudo supervisorctl restart tyres-backend

# Или все сразу:
sudo supervisorctl restart all
```

---

## 🔍 Проверка

### 1. Проверка SSL

```bash
# Проверка через curl
curl -I https://tyres.shopmarketbot.ru

# Ожидаем: HTTP/2 200

# Проверка сертификата
openssl s_client -connect tyres.shopmarketbot.ru:443 -servername tyres.shopmarketbot.ru < /dev/null
```

### 2. Проверка Backend API

```bash
curl https://tyres.shopmarketbot.ru/api/health

# Ожидаем:
# {"status":"healthy","database":"connected"}
```

### 3. Проверка Frontend

```bash
curl https://tyres.shopmarketbot.ru

# Ожидаем: HTML код приложения
```

### 4. Проверка в браузере

1. Откройте https://tyres.shopmarketbot.ru
2. Кликните на замок 🔒 в адресной строке
3. Проверьте что сертификат валиден
4. Проверьте что приложение работает

---

## 🔄 Автообновление SSL

Certbot автоматически настроил обновление:

```bash
# Проверка timer
sudo systemctl status certbot.timer

# Тестовое обновление (dry-run)
sudo certbot renew --dry-run

# Просмотр всех сертификатов
sudo certbot certificates
```

---

## ❌ Возможные ошибки

### Ошибка 1: nginx: [emerg] cannot load certificate

**Причина:** Неправильный путь к сертификату

**Решение:**
```bash
# Проверьте путь
sudo ls -la /etc/letsencrypt/live/tyres.shopmarketbot.ru/

# Убедитесь что в конфиге правильный домен:
ssl_certificate /etc/letsencrypt/live/tyres.shopmarketbot.ru/fullchain.pem;
```

### Ошибка 2: 502 Bad Gateway

**Причина:** Backend или Frontend не работают

**Решение:**
```bash
# Проверьте статус
sudo supervisorctl status

# Проверьте логи
tail -50 /var/log/tyres-backend.err.log
tail -50 /var/log/tyres-frontend.err.log
```

### Ошибка 3: ERR_SSL_PROTOCOL_ERROR

**Причина:** nginx не слушает порт 443

**Решение:**
```bash
# Проверьте что nginx слушает 443
sudo netstat -tulnp | grep nginx

# Должно быть:
# tcp  0  0.0.0.0:443  0.0.0.0:*  LISTEN  12345/nginx

# Перезапустите nginx
sudo systemctl restart nginx
```

---

## 📝 Быстрая команда (всё сразу)

Если нужно быстро установить SSL вручную:

```bash
DOMAIN="tyres.shopmarketbot.ru"

# 1. Создать конфигурацию
sudo bash -c "cat > /etc/nginx/sites-available/tyres-app << 'EOF'
server {
    listen 80;
    server_name $DOMAIN;
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name $DOMAIN;
    
    ssl_certificate /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    
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
EOF"

# 2. Обновить frontend .env
sudo sed -i "s|REACT_APP_BACKEND_URL=.*|REACT_APP_BACKEND_URL=https://$DOMAIN|g" /opt/tyres-app/frontend/.env

# 3. Пересобрать frontend
cd /opt/tyres-app/frontend && yarn build

# 4. Перезапустить всё
sudo nginx -t && sudo systemctl reload nginx
sudo supervisorctl restart all

# 5. Проверка
sleep 5
curl -I https://$DOMAIN
curl https://$DOMAIN/api/health
```

---

## ✅ Итог

После установки:

- ✅ HTTPS работает
- ✅ HTTP → HTTPS редирект активен
- ✅ SSL сертификат валиден
- ✅ Автообновление настроено

**Срок действия сертификата:** 90 дней  
**Автообновление:** за 30 дней до истечения

---

**Дата:** 2025-11-07  
**Статус:** ✅ Готово к использованию
