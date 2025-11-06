# 🚗 4tochki Telegram Mini App

Telegram Mini приложение для продажи шин и дисков с интеграцией API 4tochki.ru.

## ✨ Возможности

- 🔍 Поиск шин и дисков по параметрам
- 🚘 Подбор по автомобилю (марка, модель, год)
- 📍 Фильтрация по городу (Тюмень, Сургут, Лянтор, Москва)
- 📊 Актуальные остатки и цены со складов
- 🛒 Корзина и оформление заказов
- 💰 Админ-панель с управлением наценкой
- 🔔 Уведомления через Telegram

## 🚀 Установка одной командой

```bash
wget -qO- https://raw.githubusercontent.com/wrx861/tyres/main/install.sh | sudo bash
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
sudo tail -f /var/log/tyres-backend.err.log
sudo tail -f /var/log/tyres-frontend.err.log
```

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