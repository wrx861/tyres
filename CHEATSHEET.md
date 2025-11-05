# 📝 Шпаргалка - Быстрый старт

## 🚀 Установка на новом сервере (3 команды)

```bash
# 1. Скачать скрипт
wget https://raw.githubusercontent.com/YOUR-USERNAME/YOUR-REPO/main/install.sh

# 2. Сделать исполняемым
chmod +x install.sh

# 3. Запустить
sudo bash install.sh
```

**ИЛИ одной строкой:**
```bash
wget https://raw.githubusercontent.com/YOUR-USERNAME/YOUR-REPO/main/install.sh && chmod +x install.sh && sudo bash install.sh
```

---

## 📦 Загрузка в GitHub (первый раз)

```bash
cd /app
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPO.git
git branch -M main
git push -u origin main
```

---

## 🔧 Управление сервисами

```bash
# Статус
sudo supervisorctl status

# Перезапуск всех
sudo supervisorctl restart all

# Перезапуск backend
sudo supervisorctl restart backend

# Перезапуск frontend
sudo supervisorctl restart frontend
```

---

## 📝 Просмотр логов

```bash
# Backend ошибки
tail -f /var/log/supervisor/backend.err.log

# Frontend вывод
tail -f /var/log/supervisor/frontend.out.log

# Nginx ошибки
tail -f /var/log/nginx/error.log

# Все логи supervisor
tail -f /var/log/supervisor/*.log
```

---

## 🧪 Тестирование API

```bash
# Health check
curl https://tyres.vpnsuba.ru/api/health

# Поиск шин
curl "https://tyres.vpnsuba.ru/api/products/tires/search?width=185&height=60&diameter=15"

# Марки авто
curl https://tyres.vpnsuba.ru/api/cars/brands

# Склады
curl https://tyres.vpnsuba.ru/api/products/warehouses
```

---

## 🔄 Обновление из GitHub

```bash
cd /app
git pull
sudo supervisorctl restart all
```

---

## 🔄 Переключение на реальное API

```bash
# Изменить режим
sed -i 's/USE_MOCK_DATA=true/USE_MOCK_DATA=false/' /app/backend/.env

# Перезапустить backend
sudo supervisorctl restart backend

# Проверить
curl "https://tyres.vpnsuba.ru/api/products/tires/search?width=185"
```

---

## 🔐 Настройки

### Backend .env
```bash
nano /app/backend/.env
```

### Frontend .env
```bash
nano /app/frontend/.env
```

### Supervisor конфиг
```bash
nano /etc/supervisor/conf.d/tyres.conf
```

### Nginx конфиг
```bash
nano /etc/nginx/sites-available/tyres
sudo nginx -t
sudo systemctl reload nginx
```

---

## 🐛 Быстрое решение проблем

### Backend не работает
```bash
cd /app/backend
pip3 install -r requirements.txt
sudo supervisorctl restart backend
tail -f /var/log/supervisor/backend.err.log
```

### Frontend не работает
```bash
cd /app/frontend
rm -rf node_modules
yarn install
sudo supervisorctl restart frontend
tail -f /var/log/supervisor/frontend.out.log
```

### MongoDB не запущен
```bash
sudo systemctl start mongod
sudo systemctl status mongod
```

### SSL проблемы
```bash
sudo certbot --nginx -d tyres.vpnsuba.ru
```

---

## 📊 Мониторинг

```bash
# Использование CPU/RAM
htop

# Дисковое пространство
df -h

# Порты
netstat -tulpn | grep -E ':(3000|8001|27017)'

# Процессы Python
ps aux | grep python

# Процессы Node
ps aux | grep node
```

---

## 🗄️ Работа с MongoDB

```bash
# Подключиться
mongo

# Использовать БД
use tires_shop

# Посмотреть пользователей
db.users.find().pretty()

# Посмотреть заказы
db.orders.find().pretty()

# Посмотреть настройки
db.settings.find().pretty()

# Удалить все заказы (для теста)
db.orders.deleteMany({})

# Выход
exit
```

---

## 🔑 Создать админа вручную

```bash
mongo tires_shop

db.users.insertOne({
  telegram_id: "508352361",
  username: "admin",
  first_name: "Admin",
  is_admin: true,
  created_at: new Date()
})

exit
```

---

## 📱 Настройка Telegram Bot

В [@BotFather](https://t.me/botfather):

```
/newapp
/setappdomain → tyres.vpnsuba.ru
/setmenubutton → 🛒 Открыть магазин → https://tyres.vpnsuba.ru
```

---

## 🔄 Резервное копирование

```bash
# Backup MongoDB
mongodump --db tires_shop --out /backup/$(date +%Y%m%d)

# Backup проекта
tar -czf /backup/app-$(date +%Y%m%d).tar.gz /app

# Backup .env файлов
cp /app/backend/.env /backup/backend.env.$(date +%Y%m%d)
cp /app/frontend/.env /backup/frontend.env.$(date +%Y%m%d)
```

---

## 🔢 Версии

```bash
# Python
python3 --version

# Node.js
node --version

# Yarn
yarn --version

# MongoDB
mongod --version

# Nginx
nginx -v
```

---

## 📞 Важные ссылки и данные

- **Домен:** https://tyres.vpnsuba.ru
- **Admin ID:** 508352361
- **4tochki Login:** CarZona
- **API URL:** http://api-b2b.4tochki.ru/WCF/ClientService.svc?wsdl
- **Telegram Bot:** @your_bot
- **GitHub:** https://github.com/YOUR-USERNAME/YOUR-REPO

---

## 📚 Полная документация

- `/app/README.md` - описание проекта
- `/app/DEPLOYMENT.md` - подробная инструкция
- `/app/QUICK_INSTALL.md` - быстрая установка
- `/app/TEST_COMMANDS.md` - команды тестирования
- `/app/GITHUB_SETUP.md` - загрузка в GitHub

---

## 🆘 Служба поддержки

**4tochki:**
- Телефон: (495) 38-000-77, (495) 13-000-77
- Проверить API: свяжитесь с поддержкой

**Сервер проблемы:**
- Проверьте логи (команды выше)
- Перезапустите сервисы
- Проверьте DNS и SSL

---

**Сохраните эту шпаргалку! 📌**
