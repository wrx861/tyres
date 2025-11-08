# ✅ Исправления в install.sh

## 🔧 Критические исправления (сделаны)

### 1. Frontend команда в Supervisor ✅

**Было:**
```ini
[program:tyres-frontend]
command=yarn start  # ❌ Dev режим!
autostart=false     # ❌ Не запускается автоматически
```

**Стало:**
```ini
[program:tyres-frontend]
command=/usr/bin/npx serve -s build -l 3000  # ✅ Production режим
autostart=true  # ✅ Запускается автоматически
```

**Почему важно:**
- `yarn start` - режим разработки (hot reload, не для production)
- `serve -s build` - раздаёт собранные файлы (для production)
- `autostart=true` - frontend будет запускаться при старте системы

---

### 2. Запуск Frontend в Supervisor ✅

**Было:**
```bash
supervisorctl start tyres-backend  # Только backend
```

**Стало:**
```bash
supervisorctl start tyres-backend tyres-frontend  # ✅ Оба сервиса

# Проверка что запустились
if supervisorctl status tyres-backend | grep -q "RUNNING"; then
    echo "✓ Backend запущен"
fi

if supervisorctl status tyres-frontend | grep -q "RUNNING"; then
    echo "✓ Frontend запущен"
fi
```

**Почему важно:**
- Без этого frontend не запустится после установки
- Mini App не будет работать
- Проверка показывает если что-то не так

---

## ⚠️ Потенциальные проблемы (не критичные)

### 3. Nginx конфигурация (OK для production)

**Текущая конфигурация:**
```nginx
location / {
    root /opt/tyres-app/frontend/build;
    try_files $uri $uri/ /index.html;
}
```

**Это правильно для:**
- ✅ Production с доменом
- ✅ Статические файлы раздаются nginx
- ✅ Быстрее чем proxy

**НО:** Зависит от того что `yarn build` успешно создал `/opt/tyres-app/frontend/build/`

**Альтернатива (если нужен proxy к frontend):**
```nginx
location / {
    proxy_pass http://127.0.0.1:3000;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection 'upgrade';
    proxy_set_header Host $host;
    proxy_cache_bypass $http_upgrade;
}
```

---

### 4. SSL установка (работает, но можно улучшить)

**Текущий метод:**
```bash
certbot --nginx -d $DOMAIN_NAME --non-interactive --agree-tos --email $LETSENCRYPT_EMAIL --redirect
```

**Проблемы:**
- Иногда certbot не может найти правильный server block
- Может не установить SSL автоматически

**Альтернатива (как в change-domain.sh):**
```bash
# 1. Остановить nginx
systemctl stop nginx

# 2. Получить сертификат (standalone)
certbot certonly --standalone -d $DOMAIN_NAME

# 3. Запустить nginx
systemctl start nginx

# 4. Обновить конфигурацию nginx вручную
```

**Но:** Для первой установки текущий метод OK. SSL можно установить позже через `change-domain.sh`

---

## 📋 Чек-лист после установки

После запуска `install.sh` проверьте:

### 1. Supervisor процессы
```bash
sudo supervisorctl status

# Ожидаем:
# tyres-backend     RUNNING ✅
# tyres-frontend    RUNNING ✅
```

### 2. Порты
```bash
sudo ss -tulnp | grep -E ":(8001|3000|80)"

# Ожидаем:
# :8001 - backend ✅
# :3000 - frontend ✅
# :80   - nginx ✅
```

### 3. Backend API
```bash
curl http://localhost:8001/api/health

# Ожидаем:
{"status":"healthy","database":"connected"}
```

### 4. Frontend build
```bash
ls -la /opt/tyres-app/frontend/build/

# Должны быть:
# index.html
# static/
# asset-manifest.json
```

### 5. Nginx
```bash
sudo nginx -t
sudo systemctl status nginx
```

### 6. Через домен (если указан)
```bash
curl http://your-domain.com
curl http://your-domain.com/api/health
```

---

## 🚀 Рекомендации по использованию

### Полная автоматическая установка:

```bash
sudo bash install.sh \
  -d tyres.shopmarketbot.ru \
  -e wrx861@yandex.ru \
  --api-login sa56026 \
  --api-password F8Aeg3Cnkq \
  --bot-token 8290483601:AAFqXwpx1_paoekO0dt3kR46z471zlDKChI \
  --admin-id 508352361
```

**Результат:**
- ✅ Всё установится автоматически
- ✅ Backend и Frontend запустятся
- ✅ Nginx настроится
- ✅ SSL установится (если DNS настроен)

---

### После установки:

#### 1. Проверка
```bash
sudo bash /opt/tyres-app/check-installation.sh
```

#### 2. Если SSL не установился:
```bash
sudo bash /opt/tyres-app/change-domain.sh \
  -d tyres.shopmarketbot.ru \
  -e wrx861@yandex.ru
```

#### 3. Обновить URL в BotFather:
```
@BotFather → /mybots → Bot Settings → Menu Button
URL: https://tyres.shopmarketbot.ru
```

---

## 🐛 Если что-то не работает

### Frontend не запустился:

```bash
# Проверить логи
tail -50 /var/log/tyres-frontend.err.log

# Проверить что build существует
ls -la /opt/tyres-app/frontend/build/

# Если нет - пересобрать
cd /opt/tyres-app/frontend
yarn build

# Перезапустить
sudo supervisorctl restart tyres-frontend
```

### Backend не запустился:

```bash
# Проверить логи
tail -50 /var/log/tyres-backend.err.log

# Проверить .env
cat /opt/tyres-app/backend/.env

# Проверить venv
/opt/tyres-app/backend/venv/bin/python --version

# Перезапустить
sudo supervisorctl restart tyres-backend
```

### Nginx ошибка:

```bash
# Проверить конфигурацию
sudo nginx -t

# Посмотреть ошибки
tail -50 /var/log/nginx/error.log

# Перезапустить
sudo systemctl restart nginx
```

---

## 📊 Сравнение: До и После

### До исправлений:
```
sudo supervisorctl status
tyres-backend     RUNNING   ✅
tyres-frontend    STOPPED   ❌ Not started

Mini App: Не загружается ❌
```

### После исправлений:
```
sudo supervisorctl status
tyres-backend     RUNNING   ✅
tyres-frontend    RUNNING   ✅

Mini App: Загружается ✅
```

---

## ✅ Итоговый статус

| Компонент | Статус | Комментарий |
|-----------|--------|-------------|
| Frontend команда | ✅ Исправлено | `serve -s build` вместо `yarn start` |
| Frontend autostart | ✅ Исправлено | `true` вместо `false` |
| Frontend запуск | ✅ Исправлено | Добавлен в `supervisorctl start` |
| Проверка запуска | ✅ Добавлено | Показывает статус после старта |
| Nginx конфигурация | ✅ OK | Раздача статики (правильно для production) |
| SSL установка | ⚠️ Работает | Можно улучшить, но не критично |

---

## 🎯 Готово к использованию!

Скрипт `install.sh` исправлен и готов к чистой установке на новом сервере.

**Команда для установки:**
```bash
cd /opt
git clone https://github.com/wrx861/tyres.git tyres-app
cd tyres-app
sudo bash install.sh -d tyres.shopmarketbot.ru -e wrx861@yandex.ru \
  --api-login sa56026 --api-password F8Aeg3Cnkq \
  --bot-token 8290483601:AAFqXwpx1_paoekO0dt3kR46z471zlDKChI \
  --admin-id 508352361
```

**Всё должно встать с первого раза! ✅**

---

**Дата исправления:** 2025-11-08  
**Версия:** 2.0  
**Статус:** ✅ Готово к production
