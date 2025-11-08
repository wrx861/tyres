# 🔧 Исправление: Frontend не запускается

## ❌ Проблема

После установки:
```bash
sudo supervisorctl status
tyres-backend     RUNNING
tyres-frontend    STOPPED   Not started  # ❌
```

Mini App не грузится, потому что frontend не работает.

---

## ✅ Диагностика

### Шаг 1: Проверка конфигурации supervisor

```bash
# Список конфигураций
ls -la /etc/supervisor/conf.d/

# Должен быть файл: tyres-supervisor.conf или tyres-app.conf
```

### Шаг 2: Просмотр конфигурации

```bash
cat /etc/supervisor/conf.d/tyres-supervisor.conf

# Должны быть секции:
# [program:tyres-backend]
# [program:tyres-frontend]
```

### Шаг 3: Проверка логов

```bash
# Где логи?
ls -la /var/log/tyres*

# Если нет логов - значит процесс не запускался
```

---

## 🛠️ Решение 1: Перечитать конфигурацию

```bash
# Перечитать конфигурации
sudo supervisorctl reread

# Применить изменения
sudo supervisorctl update

# Запустить frontend
sudo supervisorctl start tyres-frontend

# Проверить статус
sudo supervisorctl status
```

---

## 🛠️ Решение 2: Ручной запуск для диагностики

```bash
# Перейти в директорию frontend
cd /opt/tyres-app/frontend

# Проверить что node_modules установлены
ls -la node_modules/ | head

# Если нет - установить
yarn install

# Проверить что build существует
ls -la build/

# Если нет - собрать
yarn build

# Попробовать запустить вручную
yarn start
# Или для production:
npx serve -s build -l 3000

# Если запускается - проблема в supervisor конфигурации
# Если не запускается - смотрите ошибку
```

---

## 🛠️ Решение 3: Создать правильную конфигурацию

Если конфигурация supervisor неправильная:

```bash
# Создать конфигурацию
sudo nano /etc/supervisor/conf.d/tyres-supervisor.conf
```

**Содержимое:**

```ini
[program:tyres-backend]
command=/opt/tyres-app/backend/venv/bin/uvicorn server:app --host 0.0.0.0 --port 8001 --workers 1
directory=/opt/tyres-app/backend
autostart=true
autorestart=true
stderr_logfile=/var/log/tyres-backend.err.log
stdout_logfile=/var/log/tyres-backend.out.log
stopsignal=TERM
stopwaitsecs=30
stopasgroup=true
killasgroup=true

[program:tyres-frontend]
command=/usr/bin/npx serve -s build -l 3000
directory=/opt/tyres-app/frontend
autostart=true
autorestart=true
stderr_logfile=/var/log/tyres-frontend.err.log
stdout_logfile=/var/log/tyres-frontend.out.log
stopsignal=TERM
stopwaitsecs=10
stopasgroup=true
killasgroup=true
```

**Затем:**

```bash
# Перечитать
sudo supervisorctl reread

# Обновить
sudo supervisorctl update

# Запустить
sudo supervisorctl start tyres-frontend

# Проверить
sudo supervisorctl status
```

---

## 🛠️ Решение 4: Проверка зависимостей

### Установлен ли serve?

```bash
# Проверка
npx serve --version

# Если нет - установить глобально
sudo npm install -g serve

# Или локально в проекте
cd /opt/tyres-app/frontend
npm install serve
```

### Собран ли frontend?

```bash
cd /opt/tyres-app/frontend

# Должна быть папка build/
ls -la build/

# Если нет - собрать
yarn build

# Проверить что собралось
ls -la build/
# Должны быть: index.html, static/, etc.
```

---

## 🔍 Проверка после исправления

### 1. Статус процессов

```bash
sudo supervisorctl status

# Ожидаем:
# tyres-backend     RUNNING   pid 12345, uptime 0:05:00
# tyres-frontend    RUNNING   pid 12346, uptime 0:05:00
```

### 2. Порты

```bash
sudo netstat -tulnp | grep -E ":(8001|3000)"

# Должно быть:
# tcp ... 0.0.0.0:8001 ... uvicorn
# tcp ... 0.0.0.0:3000 ... node или serve
```

### 3. Backend API

```bash
curl http://localhost:8001/api/health

# Ожидаем:
{"status":"healthy","database":"connected"}
```

### 4. Frontend

```bash
curl -I http://localhost:3000

# Ожидаем:
HTTP/1.1 200 OK
```

### 5. Через nginx (с доменом)

```bash
curl -I https://tyres.shopmarketbot.ru

# Ожидаем:
HTTP/2 200
```

---

## 🧪 Автоматическая проверка

Используйте скрипт проверки:

```bash
sudo bash /opt/tyres-app/check-installation.sh
```

Он проверит:
- ✅ Директории и файлы
- ✅ Python и Node.js окружение
- ✅ Supervisor процессы
- ✅ MongoDB
- ✅ Nginx
- ✅ Порты
- ✅ Backend API
- ✅ Frontend
- ✅ Даст рекомендации

---

## ⚠️ Частые проблемы

### Проблема 1: Permission denied

```bash
sudo supervisorctl start tyres-frontend
# Error: permission denied
```

**Решение:**
```bash
# Проверить права
ls -la /opt/tyres-app/frontend/

# Должен быть владелец root или tyres пользователь
# Если нет - исправить:
sudo chown -R root:root /opt/tyres-app/
```

### Проблема 2: yarn: command not found

```bash
# В конфигурации supervisor используется yarn
command=yarn start
# Но yarn не установлен или не в PATH
```

**Решение:**
```bash
# Вариант 1: Установить yarn глобально
sudo npm install -g yarn

# Вариант 2: Использовать npx serve
# Изменить в конфигурации:
command=/usr/bin/npx serve -s build -l 3000
```

### Проблема 3: Module not found

```bash
# В логах:
Error: Cannot find module 'react'
```

**Решение:**
```bash
cd /opt/tyres-app/frontend
rm -rf node_modules
yarn install
yarn build
sudo supervisorctl restart tyres-frontend
```

### Проблема 4: Port already in use

```bash
# В логах:
Error: listen EADDRINUSE: address already in use :::3000
```

**Решение:**
```bash
# Найти что использует порт
sudo lsof -i :3000

# Убить процесс
sudo kill -9 PID

# Или изменить порт в конфигурации
```

---

## 📊 Правильная структура после установки

```
/opt/tyres-app/
├── backend/
│   ├── venv/              # Python окружение
│   ├── server.py          # FastAPI приложение
│   └── .env               # Переменные окружения
├── frontend/
│   ├── node_modules/      # Node.js зависимости
│   ├── build/             # Собранный frontend (для production)
│   ├── src/               # Исходники
│   └── .env               # Переменные окружения
└── scripts/               # Утилиты

/etc/supervisor/conf.d/
└── tyres-supervisor.conf  # Конфигурация supervisor

/var/log/
├── tyres-backend.err.log  # Логи backend
├── tyres-backend.out.log
├── tyres-frontend.err.log # Логи frontend
└── tyres-frontend.out.log

/etc/nginx/sites-available/
└── tyres-app              # Конфигурация nginx
```

---

## 🚀 Быстрое исправление (если всё плохо)

```bash
# 1. Остановить всё
sudo supervisorctl stop tyres-backend tyres-frontend

# 2. Пересобрать frontend
cd /opt/tyres-app/frontend
yarn install
yarn build

# 3. Проверить конфигурацию supervisor
sudo supervisorctl reread
sudo supervisorctl update

# 4. Запустить
sudo supervisorctl start tyres-backend tyres-frontend

# 5. Проверить
sudo supervisorctl status
curl http://localhost:8001/api/health
curl http://localhost:3000

# 6. Если работает - перезапустить nginx
sudo systemctl restart nginx
```

---

## 📝 Логи для диагностики

```bash
# Backend логи (все)
tail -100 /var/log/tyres-backend.err.log

# Backend логи (без Telegram конфликтов)
tail -100 /var/log/tyres-backend.err.log | grep -v "Conflict"

# Frontend логи
tail -100 /var/log/tyres-frontend.err.log

# Supervisor логи
tail -100 /var/log/supervisor/supervisord.log

# Nginx логи
tail -100 /var/log/nginx/error.log
```

---

**Дата:** 2025-11-08  
**Версия:** 1.0  
**Статус:** ✅ Готово к использованию
