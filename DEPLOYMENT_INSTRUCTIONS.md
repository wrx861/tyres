# 🚀 Инструкция по развертыванию приложения

## ✅ Что было сделано:

1. **Удалена кнопка Emergent** - из index.html
2. **Расширенный поиск дисков** - добавлены параметры PCD, ET, DIA, цвет, тип
3. **Отображение изображений** - товары теперь с фото
4. **Уведомления админа** - о новых посетителях и заказах
5. **Исправлен install.sh** - добавлены DB_NAME, CORS_ORIGINS, запрос учетных данных
6. **Вся документация** - SETUP_GUIDE.md, INSTALL_QUICK.md, ADMIN_ACCESS.md и др.

---

## 📤 Шаг 1: Сохранить в GitHub

### Через интерфейс Emergent:

1. Нажмите кнопку **"Save to GitHub"** или **"Push to GitHub"**
2. Все изменения автоматически загрузятся в репозиторий
3. Дождитесь завершения (статус "Success")

### Или вручную через Git:

```bash
cd /app
git add .
git commit -m "Production ready: Убрана кнопка Emergent, расширенные фильтры, изображения, исправлен install.sh"
git push origin main
```

---

## 🖥️ Шаг 2: Развернуть на новом сервере

### Вариант А: Полная автоматическая установка

```bash
wget https://raw.githubusercontent.com/wrx861/tyres/main/install.sh

sudo bash install.sh \
  -d tyres.vpnsuba.ru \
  -e ваш@email.com \
  --api-login sa56026 \
  --api-password F8Aeg3Cnkq \
  --bot-token 8290483601:AAFqXwpx1_paoekO0dt3kR46z471zlDKChI \
  --admin-id 508352361
```

**Замените:**
- `tyres.vpnsuba.ru` → ваш домен
- `ваш@email.com` → ваш email для Let's Encrypt
- Учетные данные → ваши реальные данные

### Вариант Б: Интерактивная установка

```bash
wget https://raw.githubusercontent.com/wrx861/tyres/main/install.sh
sudo bash install.sh
```

Установщик последовательно запросит:
1. Домен
2. SSL email (если домен указан)
3. Логин 4tochki API
4. Пароль 4tochki API
5. Telegram Bot Token
6. Admin Telegram ID

---

## 🔄 Шаг 3: Обновить существующую установку

Если приложение уже установлено на `/opt/tyres-app`:

```bash
cd /opt/tyres-app

# Обновить код из GitHub
git pull origin main

# Пересобрать frontend
cd frontend
yarn build

# Перезапустить backend
sudo supervisorctl restart tyres-backend

# Перезапустить nginx
sudo systemctl restart nginx
```

---

## ✅ Шаг 4: Проверка работы

### Проверка сервисов:

```bash
sudo supervisorctl status
```

Должно быть:
```
tyres-backend    RUNNING ✅
tyres-frontend   STOPPED (это нормально, nginx раздаёт статику)
```

### Проверка сайта:

```bash
# Главная страница
curl -I https://tyres.vpnsuba.ru
# Ответ: HTTP/1.1 200 OK

# Backend API
curl https://tyres.vpnsuba.ru/api/health
# Ответ: {"status":"healthy","database":"connected"}
```

### Проверка в браузере/Mini App:

1. ✅ Главная страница загружается
2. ✅ **НЕТ кнопки "Made with Emergent"** внизу
3. ✅ Отображается "Привет, [ваше имя]"
4. ✅ Товары отображаются с изображениями
5. ✅ Поиск дисков работает с расширенными фильтрами
6. ✅ Если ваш ID = 508352361 → видна кнопка "Админ-панель"

---

## 🎯 Production Ready конфигурация

### Nginx (раздача статики):

```nginx
server {
    server_name tyres.vpnsuba.ru;

    location /api {
        proxy_pass http://127.0.0.1:8001;
        # ... остальные настройки
    }

    location / {
        root /opt/tyres-app/frontend/build;
        try_files $uri $uri/ /index.html;
        add_header Cache-Control "no-cache, must-revalidate";
    }

    listen 443 ssl;
    ssl_certificate /etc/letsencrypt/live/tyres.vpnsuba.ru/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/tyres.vpnsuba.ru/privkey.pem;
}
```

### Supervisor (только backend):

```ini
[program:tyres-backend]
command=/opt/tyres-app/backend/venv/bin/uvicorn server:app --host 0.0.0.0 --port 8001
directory=/opt/tyres-app/backend
autostart=true
autorestart=true

[program:tyres-frontend]
autostart=false  # Frontend не нужен, nginx раздаёт статику
autorestart=false
```

---

## 🔧 Важные файлы и настройки

### Backend .env (/opt/tyres-app/backend/.env):

```env
MONGO_URL=mongodb://localhost:27017
DB_NAME=tires_shop
CORS_ORIGINS=*

# 4tochki API Credentials
FOURTHCHKI_LOGIN=sa56026
FOURTHCHKI_PASSWORD=F8Aeg3Cnkq
FOURTHCHKI_API_URL=http://api-b2b.4tochki.ru/WCF/ClientService.svc?wsdl

# Telegram Bot
TELEGRAM_BOT_TOKEN=8290483601:AAFqXwpx1_paoekO0dt3kR46z471zlDKChI
ADMIN_TELEGRAM_ID=508352361

# Pricing
DEFAULT_MARKUP_PERCENTAGE=15

# Mock Mode
USE_MOCK_DATA=false
```

### Frontend .env (/opt/tyres-app/frontend/.env):

```env
REACT_APP_BACKEND_URL=https://tyres.vpnsuba.ru
PORT=3000
REACT_APP_ENABLE_VISUAL_EDITS=false
ENABLE_HEALTH_CHECK=false
```

---

## 📚 Дополнительная документация

После развертывания доступны следующие руководства:

- **SETUP_GUIDE.md** - Полное руководство по установке и настройке
- **INSTALL_QUICK.md** - Быстрая установка за 2 команды
- **ADMIN_ACCESS.md** - Как войти в админ-панель
- **FIX_INSTALLATION.md** - Решение типичных проблем
- **CREDENTIALS_FIX.md** - Настройка учетных данных

---

## 🚨 Решение проблем

### Проблема: "502 Bad Gateway"

```bash
# Проверьте backend
sudo supervisorctl status tyres-backend

# Проверьте логи
tail -f /var/log/tyres-backend.err.log

# Перезапустите
sudo supervisorctl restart tyres-backend
```

### Проблема: "Кнопка Emergent всё ещё видна"

```bash
# Пересоберите frontend
cd /opt/tyres-app/frontend
yarn build

# Очистите кэш браузера/Telegram
# В Telegram: Настройки → Данные и память → Очистить кэш
```

### Проблема: "Не вижу кнопку Админ-панель"

```bash
# Проверьте ваш Telegram ID
# Откройте @userinfobot

# Проверьте ADMIN_TELEGRAM_ID
grep ADMIN_TELEGRAM_ID /opt/tyres-app/backend/.env

# Если не совпадает, измените и перезапустите
sudo nano /opt/tyres-app/backend/.env
sudo supervisorctl restart tyres-backend
```

---

## ✅ Чеклист развертывания

- [ ] Сохранено в GitHub (Save to GitHub)
- [ ] Скачан install.sh с GitHub
- [ ] Запущена установка с правильными параметрами
- [ ] Все сервисы RUNNING
- [ ] Backend API отвечает (curl https://domain/api/health)
- [ ] Сайт открывается в браузере
- [ ] НЕТ кнопки "Made with Emergent"
- [ ] Товары отображаются с изображениями
- [ ] Админ-панель доступна (если ID совпадает)
- [ ] Тестовый заказ создаётся успешно
- [ ] Уведомления приходят в Telegram

---

## 🎉 Готово!

После выполнения всех шагов у вас будет полностью рабочее production приложение:

✅ Без брендинга Emergent  
✅ С расширенными фильтрами поиска  
✅ С изображениями товаров  
✅ С админ-панелью  
✅ С уведомлениями в Telegram  
✅ С SSL сертификатом  
✅ Оптимизированное для продакшна  

**Приятного использования!** 🚀
