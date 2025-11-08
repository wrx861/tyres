# 🔒 Ручная установка SSL (если автоустановка не сработала)

## ❌ Проблема

После установки SSL не установился:
```
Certbot failed to authenticate some domains (authenticator: nginx)
Detail: Timeout during connect (likely firewall problem)
```

**Причины:**
- Метод `certbot --nginx` не всегда работает
- Nginx может блокировать доступ к `.well-known/acme-challenge/`
- Временные проблемы с сетью

---

## ✅ Решение: Standalone метод

### Шаг 1: Остановить nginx

```bash
sudo systemctl stop nginx
```

### Шаг 2: Получить сертификат

```bash
sudo certbot certonly --standalone \
  -d tyres.shopmarketbot.ru \
  --non-interactive \
  --agree-tos \
  --email wrx861@yandex.ru \
  --preferred-challenges http
```

**Ожидаемый вывод:**
```
Successfully received certificate.
Certificate is saved at: /etc/letsencrypt/live/tyres.shopmarketbot.ru/fullchain.pem
Key is saved at: /etc/letsencrypt/live/tyres.shopmarketbot.ru/privkey.pem
```

### Шаг 3: Создать nginx конфигурацию с SSL

```bash
sudo nano /etc/nginx/sites-available/tyres-app
```

**Вставьте:**

```nginx
# HTTP -> HTTPS redirect
server {
    listen 80;
    server_name tyres.shopmarketbot.ru;
    
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }
    
    location / {
        return 301 https://$server_name$request_uri;
    }
}

# HTTPS server
server {
    listen 443 ssl http2;
    server_name tyres.shopmarketbot.ru;
    
    ssl_certificate /etc/letsencrypt/live/tyres.shopmarketbot.ru/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/tyres.shopmarketbot.ru/privkey.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    add_header Strict-Transport-Security "max-age=31536000" always;
    
    location / {
        root /opt/tyres-app/frontend/build;
        try_files $uri $uri/ /index.html;
        add_header Cache-Control "no-cache, must-revalidate";
    }
    
    location /api {
        proxy_pass http://127.0.0.1:8001;
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

**Сохраните:** Ctrl+O, Enter, Ctrl+X

### Шаг 4: Проверить конфигурацию

```bash
sudo nginx -t
```

**Ожидаем:**
```
nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
nginx: configuration file /etc/nginx/nginx.conf test is successful
```

### Шаг 5: Запустить nginx

```bash
sudo systemctl start nginx
```

### Шаг 6: Обновить frontend .env

```bash
sudo nano /opt/tyres-app/frontend/.env
```

**Измените на:**
```
REACT_APP_BACKEND_URL=https://tyres.shopmarketbot.ru
```

### Шаг 7: Пересобрать frontend

```bash
cd /opt/tyres-app/frontend
yarn build
```

### Шаг 8: Перезапустить frontend

```bash
sudo supervisorctl restart tyres-frontend
```

---

## 🔍 Проверка

### 1. SSL сертификат

```bash
openssl s_client -connect tyres.shopmarketbot.ru:443 -servername tyres.shopmarketbot.ru < /dev/null | grep "Verify return code"

# Ожидаем: Verify return code: 0 (ok)
```

### 2. HTTPS работает

```bash
curl -I https://tyres.shopmarketbot.ru

# Ожидаем: HTTP/2 200
```

### 3. Backend API

```bash
curl https://tyres.shopmarketbot.ru/api/health

# Ожидаем: {"status":"healthy","database":"connected"}
```

### 4. Редирект HTTP -> HTTPS

```bash
curl -I http://tyres.shopmarketbot.ru

# Ожидаем: HTTP/1.1 301 Moved Permanently
# Location: https://tyres.shopmarketbot.ru/
```

### 5. В браузере

Откройте: https://tyres.shopmarketbot.ru
- Замок 🔒 должен быть зелёным
- Сертификат от Let's Encrypt
- Приложение загружается

---

## 🔄 Автообновление SSL

### Настроить автообновление

```bash
# Включить timer
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer

# Проверить статус
sudo systemctl list-timers | grep certbot
```

### Создать hook для перезагрузки nginx

```bash
sudo mkdir -p /etc/letsencrypt/renewal-hooks/deploy

sudo cat > /etc/letsencrypt/renewal-hooks/deploy/reload-nginx.sh << 'EOF'
#!/bin/bash
systemctl reload nginx
EOF

sudo chmod +x /etc/letsencrypt/renewal-hooks/deploy/reload-nginx.sh
```

### Проверить автообновление (dry-run)

```bash
sudo certbot renew --dry-run

# Ожидаем: All simulations succeeded
```

---

## 🚀 Быстрая команда (всё в одной)

```bash
# 1. Получить сертификат
sudo systemctl stop nginx
sudo certbot certonly --standalone -d tyres.shopmarketbot.ru --non-interactive --agree-tos --email wrx861@yandex.ru
sudo systemctl start nginx

# 2. Применить конфигурацию nginx (см. выше)

# 3. Обновить .env и пересобрать
sudo sed -i 's|REACT_APP_BACKEND_URL=.*|REACT_APP_BACKEND_URL=https://tyres.shopmarketbot.ru|g' /opt/tyres-app/frontend/.env
cd /opt/tyres-app/frontend && yarn build

# 4. Перезапустить
sudo nginx -t && sudo systemctl reload nginx
sudo supervisorctl restart tyres-frontend

# 5. Проверить
curl -I https://tyres.shopmarketbot.ru
```

---

## ❌ Возможные ошибки

### Ошибка 1: Port 80 already in use

```bash
sudo systemctl stop nginx
sudo lsof -i :80

# Если другой процесс - убить
sudo kill -9 PID
```

### Ошибка 2: Too many certificates

```
too many certificates already issued for: shopmarketbot.ru
```

**Решение:** Подождите неделю (лимит 5 сертификатов/неделю)

### Ошибка 3: DNS не резолвится

```bash
dig tyres.shopmarketbot.ru +short

# Если пусто - подождите DNS обновления (5-30 минут)
```

### Ошибка 4: Firewall блокирует

```bash
# Проверьте UFW
sudo ufw status

# Откройте порты
sudo ufw allow 80
sudo ufw allow 443
```

---

## 💡 Альтернатива: Использовать скрипт change-domain.sh

Если у вас уже есть скрипт:

```bash
cd /opt/tyres-app
sudo bash change-domain.sh -d tyres.shopmarketbot.ru -e wrx861@yandex.ru
```

Этот скрипт автоматически:
- Удалит старые сертификаты
- Получит новый (standalone)
- Обновит nginx
- Пересоберёт frontend
- Перезапустит всё

---

**Дата:** 2025-11-08  
**Статус:** ✅ Готово к использованию
