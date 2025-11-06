# 📘 Руководство по установке и настройке Telegram Mini App

## 🚀 Быстрая установка

### Шаг 1: Запуск автоустановщика

```bash
curl -o install.sh https://raw.githubusercontent.com/wrx861/tyres/main/install.sh
sudo bash install.sh
```

### Шаг 2: Ответьте на вопросы установщика

1. **Введите домен** для вашего приложения (например: `tires.yourdomain.com`)
   - Если хотите запустить в режиме разработки, просто нажмите Enter

2. **Установить SSL сертификат?** (рекомендуется для Telegram Mini App)
   - Выберите `y` если домен уже настроен и указывает на ваш сервер
   - Выберите `n` если планируете настроить SSL позже

3. **Email для Let's Encrypt** (только если выбрали SSL)
   - Укажите действующий email для уведомлений о сертификате

## ⚙️ Настройка после установки

### 1. Редактирование конфигурации backend

Откройте файл конфигурации:
```bash
sudo nano /opt/tyres-app/backend/.env
```

Заполните необходимые данные:

```env
# База данных (уже настроено)
MONGO_URL=mongodb://localhost:27017/tyres_db

# Учетные данные API 4tochki
FOURTHCHKI_LOGIN=sa56026
FOURTHCHKI_PASSWORD=F8Aeg3Cnkq
FOURTHCHKI_API_URL=http://api-b2b.4tochki.ru/WCF/ClientService.svc?wsdl

# Telegram бот
TELEGRAM_BOT_TOKEN=8290483601:AAFqXwpx1_paoekO0dt3kR46z471zlDKChI
ADMIN_TELEGRAM_ID=508352361

# Наценка по умолчанию (в процентах)
DEFAULT_MARKUP_PERCENTAGE=15

# Режим работы
USE_MOCK_DATA=false
```

### 2. Где взять учетные данные?

#### API 4tochki
- **Логин и пароль**: Получите на сайте [b2b.4tochki.ru](https://b2b.4tochki.ru)
- **Документация API**: [https://b2b.4tochki.ru/Help/Page?url=index.html](https://b2b.4tochki.ru/Help/Page?url=index.html)

#### Telegram Bot Token
1. Напишите [@BotFather](https://t.me/BotFather) в Telegram
2. Отправьте команду `/newbot`
3. Следуйте инструкциям
4. Скопируйте полученный токен в формате `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`

#### Admin Telegram ID
1. Напишите [@userinfobot](https://t.me/userinfobot) в Telegram
2. Бот пришлет ваш ID (число, например: `508352361`)
3. Скопируйте этот ID

### 3. Перезапуск сервисов

После изменения .env файла:
```bash
sudo supervisorctl restart all
```

### 4. Проверка работы

```bash
# Проверка статуса всех сервисов
sudo supervisorctl status

# Все должно быть в статусе RUNNING:
# tyres-backend    RUNNING
# tyres-frontend   RUNNING
```

## 🌐 Понимание REACT_APP_BACKEND_URL

### ❌ ЧТО ЭТО НЕ ЕСТЬ

**REACT_APP_BACKEND_URL** ≠ `http://api-b2b.4tochki.ru/WCF/ClientService.svc?wsdl`

### ✅ ЧТО ЭТО ТАКОЕ

**REACT_APP_BACKEND_URL** — это адрес **ВАШЕГО backend сервера** (FastAPI), который установлен на вашем сервере.

### 📊 Архитектура приложения

```
Telegram Mini App (React Frontend)
        ↓
REACT_APP_BACKEND_URL (ваш FastAPI backend)
        ↓
API 4tochki
```

### Примеры правильных значений:

- С доменом и SSL: `https://tires.yourdomain.com`
- С доменом без SSL: `http://tires.yourdomain.com`
- По IP адресу: `http://123.45.67.89`
- Локально (разработка): `http://localhost:8001`

### Где это настраивается?

Файл: `/opt/tyres-app/frontend/.env`

```env
REACT_APP_BACKEND_URL=https://tires.yourdomain.com
```

**Важно**: Автоустановщик уже настроил это значение автоматически на основе домена, который вы указали!

## 🔧 Настройка Telegram Mini App

### 1. Создание Telegram Mini App

1. Откройте [@BotFather](https://t.me/BotFather)
2. Отправьте `/newapp`
3. Выберите вашего бота
4. Введите название приложения
5. Введите описание
6. Загрузите иконку (512x512 px)
7. Введите **URL приложения**: `https://yourdomain.com`
8. Выберите тип: Web App

### 2. Важные требования Telegram

- **HTTPS обязателен** для Telegram Mini App
- Сертификат должен быть действительным (Let's Encrypt подходит)
- Порты 80 и 443 должны быть открыты

## 📱 Проверка работы

### Backend API
```bash
curl http://localhost:8001/api/health
# Ответ: {"status":"ok"}
```

### Тест поиска шин
```bash
curl -X POST http://localhost:8001/api/products/search \
  -H "Content-Type: application/json" \
  -d '{
    "type": "tires",
    "filters": {
      "width": 185,
      "height": 60,
      "diameter": 15,
      "season": "winter"
    }
  }'
```

### Frontend
Откройте в браузере:
- С доменом: `https://yourdomain.com`
- Локально: `http://localhost:3000`

## 🐛 Решение проблем

### Backend не запускается

Проверьте логи:
```bash
tail -f /var/log/tyres-backend.err.log
```

Типичные проблемы:
- Неправильные учетные данные 4tochki
- MongoDB не запущен: `sudo systemctl start mongod`
- Порт 8001 занят

### Frontend не запускается

Проверьте логи:
```bash
tail -f /var/log/tyres-frontend.err.log
```

Типичные проблемы:
- Неправильный REACT_APP_BACKEND_URL
- Зависимости не установлены: `cd /opt/tyres-app/frontend && yarn install`

### SSL сертификат не устанавливается

Проверьте:
1. DNS записи: `nslookup yourdomain.com`
2. Порты открыты: `sudo ufw status`
3. Nginx работает: `sudo systemctl status nginx`

Повторная установка SSL:
```bash
sudo certbot --nginx -d yourdomain.com
```

### Nginx показывает 502 Bad Gateway

Проверьте что backend запущен:
```bash
sudo supervisorctl status tyres-backend
```

Перезапустите backend:
```bash
sudo supervisorctl restart tyres-backend
```

## 📊 Полезные команды

```bash
# Управление сервисами
sudo supervisorctl status              # Статус всех сервисов
sudo supervisorctl restart all         # Перезапуск всех
sudo supervisorctl restart tyres-backend   # Перезапуск backend
sudo supervisorctl restart tyres-frontend  # Перезапуск frontend

# Логи
tail -f /var/log/tyres-backend.out.log    # Backend stdout
tail -f /var/log/tyres-backend.err.log    # Backend errors
tail -f /var/log/tyres-frontend.out.log   # Frontend stdout
tail -f /var/log/nginx/error.log          # Nginx errors

# MongoDB
sudo systemctl status mongod           # Статус MongoDB
sudo systemctl restart mongod          # Перезапуск MongoDB
mongosh                                # Консоль MongoDB

# Nginx
sudo nginx -t                          # Тест конфигурации
sudo systemctl restart nginx           # Перезапуск Nginx
```

## 🔐 Безопасность

### Рекомендации:

1. **Файрвол**: Откройте только необходимые порты
   ```bash
   sudo ufw allow 22    # SSH
   sudo ufw allow 80    # HTTP
   sudo ufw allow 443   # HTTPS
   sudo ufw enable
   ```

2. **Обновления**: Регулярно обновляйте систему
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

3. **Бэкапы**: Настройте регулярные бэкапы MongoDB
   ```bash
   mongodump --out /backup/$(date +%Y%m%d)
   ```

## 📞 Поддержка

- **Документация API 4tochki**: [https://b2b.4tochki.ru/Help/Page?url=index.html](https://b2b.4tochki.ru/Help/Page?url=index.html)
- **Telegram Bot API**: [https://core.telegram.org/bots/api](https://core.telegram.org/bots/api)
- **Telegram Mini Apps**: [https://core.telegram.org/bots/webapps](https://core.telegram.org/bots/webapps)

---

## 📝 Итоговая информация

После установки у вас будет:

✅ FastAPI backend на порту 8001  
✅ React frontend на порту 3000  
✅ MongoDB база данных  
✅ Nginx reverse proxy (если указан домен)  
✅ SSL сертификат Let's Encrypt (если выбрали)  
✅ Автоматический запуск всех сервисов через Supervisor  
✅ Интеграция с API 4tochki  
✅ Telegram бот с уведомлениями  

Приложение готово к работе! 🎉
