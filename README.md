# 🚗 4tochki Telegram Mini App

Telegram Mini приложение для продажи шин и дисков с интеграцией API 4tochki.ru.

## ✨ Возможности

- 🔍 Поиск шин и дисков по параметрам
- 🚘 Подбор по автомобилю (марка, модель, год)
- 📍 Фильтрация по городу (Тюмень, Сургут, Лянтор, Москва)
- 📊 Актуальные остатки и цены со складов
- 🛒 Корзина и оформление заказов
- 💰 Админ-панель с управлением наценкой
- 🔔 Уведомления через Telegram:
  - Уведомления о новых заказах
  - Уведомления о новых посетителях магазина (ID, username, имя)
  - Обновления статуса заказов

## 🚀 Установка

### Первичная установка

```bash
wget https://raw.githubusercontent.com/wrx861/tyres/main/install.sh
sudo bash install.sh
```

### Обновление на production сервере

```bash
cd /opt/tyres-app
git pull origin main
sudo bash update.sh
```

Подробнее: см. [UPDATE_GUIDE.md](UPDATE_GUIDE.md)

### Вариант 2: Автоматическая установка с параметрами

```bash
# С доменом и SSL
wget https://raw.githubusercontent.com/wrx861/tyres/main/install.sh
sudo bash install.sh -d tires.yourdomain.com -e your@email.com

# Только с доменом (без SSL)
sudo bash install.sh -d tires.yourdomain.com --no-ssl

# Режим разработки (localhost)
sudo bash install.sh
```

## ⚙️ После установки

1. Настройте `/opt/tyres-app/backend/.env`:
```env
FOURTHCHKI_LOGIN=your_login
FOURTHCHKI_PASSWORD=your_password
TELEGRAM_BOT_TOKEN=your_token
TELEGRAM_ADMIN_ID=your_id
```

2. Обновите `/opt/tyres-app/frontend/.env`:
```env
REACT_APP_BACKEND_URL=https://yourdomain.com/api
```

3. Перезапустите:
```bash
sudo supervisorctl restart all
```

## 📋 Требования

- Ubuntu 20.04+ / Debian 10+
- 2GB RAM минимум
- 10GB свободного места

## 📚 Документация

- Backend API: `http://localhost:8001/docs`
- Frontend: `http://localhost:3000`

## 🔧 Управление

```bash
# Статус сервисов
sudo supervisorctl status

# Перезапуск
sudo supervisorctl restart all

# Логи
sudo tail -f /var/log/supervisor/backend.err.log
sudo tail -f /var/log/supervisor/frontend.err.log

# Проверка Telegram бота (интегрирован в backend)
sudo tail -f /var/log/supervisor/backend.err.log | grep telegram
```

## 🤖 Telegram бот

Бот **интегрирован в backend** и запускается автоматически:
- ✅ Обработка команд: `/start`, `/help`
- ✅ Интерактивное меню: Шиномонтаж → Прайс → Записаться
- ✅ Уведомления админу: новые заказы, новые посетители
- ✅ Уведомления клиентам: статус заказа

**Тестирование:**
```bash
cd /app
python3 test_telegram_bot.py  # Базовый тест
python3 test_bot_menu.py       # Тест меню с кнопками
```

Подробнее: см. [TELEGRAM_BOT_INTEGRATION.md](TELEGRAM_BOT_INTEGRATION.md)

## 📁 Структура

```
tyres/
├── backend/         # FastAPI + MongoDB
├── frontend/        # React + Telegram WebApp
└── install.sh       # Автоустановка
```

## 🐛 Troubleshooting

**Backend не запускается:**
```bash
sudo tail -n 50 /var/log/tyres-backend.err.log
sudo systemctl status mongod
```

**Frontend не запускается:**
```bash
cd /opt/tyres-app/frontend
yarn install
sudo supervisorctl restart tyres-frontend
```

## 📝 Лицензия

MIT License

---
Made with ❤️ for Telegram Mini Apps