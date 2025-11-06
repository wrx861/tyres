# 🚗 Магазин Шин и Дисков - Telegram Mini App

Полнофункциональное приложение для продажи шин и дисков через Telegram с интеграцией API поставщика 4tochki.ru

## 📋 Описание

Современный Telegram Mini App для продажи шин и дисков с системой подтверждения заказов администратором.

**Функции:**
- ✅ Поиск шин и дисков по параметрам
- ✅ Подбор по автомобилю (марка → модель → год → модификация)
- ✅ Корзина и оформление заказа
- ✅ Система подтверждения заказов админом
- ✅ История заказов
- ✅ Админ-панель с управлением наценкой
- ✅ Telegram уведомления
- ✅ Интеграция с API 4tochki.ru

## 🏗️ Технологии

**Backend:** FastAPI, MongoDB, Zeep (SOAP), python-telegram-bot  
**Frontend:** React, TailwindCSS, Axios, Lucide Icons

## 🚀 Быстрый старт

### 1. Клонирование и установка

```bash
git clone <your-repo>
cd tire-wheel-finder

# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd ../frontend
yarn install
```

### 2. Настройка переменных окружения

**backend/.env:**
```bash
MONGO_URL="mongodb://localhost:27017"
DB_NAME="tires_shop"
FOURTHCHKI_LOGIN=CarZona
FOURTHCHKI_PASSWORD=Qq28061q.
FOURTHCHKI_API_URL=http://api-b2b.4tochki.ru/WCF/ClientService.svc?wsdl
TELEGRAM_BOT_TOKEN=8290483601:AAFqXwpx1_paoekO0dt3kR46z471zlDKChI
ADMIN_TELEGRAM_ID=508352361
DEFAULT_MARKUP_PERCENTAGE=15
USE_MOCK_DATA=true
```

**frontend/.env:**
```bash
REACT_APP_BACKEND_URL=https://tyres.vpnsuba.ru
```

### 3. Запуск через Supervisor

```bash
sudo supervisorctl restart all
```

### 4. Переключение на реальное API

Когда API 4tochki заработает, измените в `backend/.env`:
```bash
USE_MOCK_DATA=false
```

## 📱 Настройка Telegram Mini App

1. Создайте бота через [@BotFather](https://t.me/botfather)
2. Команды:
   ```
   /newapp
   /setappdomain - tyres.vpnsuba.ru
   /setappphoto - загрузите иконку
   ```

## 📊 API Endpoints

- `POST /api/auth/telegram` - авторизация
- `GET /api/products/tires/search` - поиск шин
- `GET /api/products/disks/search` - поиск дисков
- `GET /api/cars/brands` - марки авто
- `GET /api/cars/goods` - подбор по авто
- `POST /api/orders` - создать заказ
- `GET /api/admin/orders/pending` - заказы на подтверждение (админ)
- `POST /api/admin/orders/{id}/confirm` - подтвердить заказ (админ)

## 🔐 Безопасность

- Авторизация через Telegram ID
- Admin ID: `508352361`
- Все заказы проверяются админом перед отправкой поставщику

## 📈 Мониторинг

```bash
# Статус сервисов
sudo supervisorctl status

# Логи
tail -f /var/log/supervisor/backend.err.log
tail -f /var/log/supervisor/frontend.out.log

# Перезапуск
sudo supervisorctl restart backend
sudo supervisorctl restart frontend
```

## 🐛 Troubleshooting

**Backend не запускается:**
```bash
cd /app/backend
pip install -r requirements.txt
sudo supervisorctl restart backend
```

**API 4tochki не работает:**
```bash
# Включите mock режим
echo "USE_MOCK_DATA=true" >> /app/backend/.env
sudo supervisorctl restart backend
```

**Frontend ошибки:**
```bash
cd /app/frontend
rm -rf node_modules
yarn install
sudo supervisorctl restart frontend
```

## 📞 Контакты

- Поддержка 4tochki: (495) 38-000-77, (495) 13-000-77
- Домен: tyres.vpnsuba.ru
- Admin Telegram ID: 508352361

---
**Разработано для CarZona** 🚗
