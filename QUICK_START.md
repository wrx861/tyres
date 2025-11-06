# ⚡ Быстрый старт

## Установка за 3 минуты

### 1. Установка одной командой:

```bash
wget -qO- https://raw.githubusercontent.com/wrx861/tyres/main/install.sh | sudo bash
```

### 2. Настройте учетные данные:

```bash
sudo nano /opt/tyres-app/backend/.env
```

Замените эти строки:
```
FOURTHCHKI_LOGIN=your_login_here     → ваш логин 4tochki
FOURTHCHKI_PASSWORD=your_password_here → ваш пароль 4tochki
TELEGRAM_BOT_TOKEN=your_bot_token_here → токен Telegram бота
TELEGRAM_ADMIN_ID=your_admin_id_here   → ваш Telegram ID
```

### 3. Обновите URL (для продакшена):

```bash
sudo nano /opt/tyres-app/frontend/.env
```

Замените:
```
REACT_APP_BACKEND_URL=http://localhost:8001
                       ↓
REACT_APP_BACKEND_URL=https://yourdomain.com/api
```

### 4. Перезапустите:

```bash
sudo supervisorctl restart all
```

### 5. Проверьте:

```bash
sudo supervisorctl status
```

Должно быть:
```
tyres-backend    RUNNING
tyres-frontend   RUNNING
```

## 🎉 Готово!

- Backend: http://localhost:8001/docs
- Frontend: http://localhost:3000
- Telegram: настройте WebApp URL в BotFather

## 🆘 Проблемы?

```bash
# Логи backend
sudo tail -f /var/log/tyres-backend.err.log

# Логи frontend  
sudo tail -f /var/log/tyres-frontend.err.log

# MongoDB не запущен?
sudo systemctl start mongod
```

## 📱 Как создать Telegram бота:

1. Напишите @BotFather в Telegram
2. Отправьте `/newbot`
3. Следуйте инструкциям
4. Скопируйте токен → вставьте в `.env`
5. Настройте WebApp:
   - `/setmenubutton` → выберите бота → `@YourBot — Edit`
   - Введите URL: `https://yourdomain.com`

## 🔐 Как узнать свой Telegram ID:

1. Напишите @userinfobot в Telegram
2. Скопируйте ID
3. Вставьте в `.env` как `TELEGRAM_ADMIN_ID`

## 🚀 Что дальше?

- Настройте Nginx для HTTPS
- Добавьте SSL сертификат (Let's Encrypt)
- Настройте автобэкап MongoDB
- Мониторьте логи

---

**Нужна полная документация?** → [README.md](README.md)
