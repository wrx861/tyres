# ⚡ Быстрая установка одной командой

## 🚀 Установка на чистом Ubuntu/Debian сервере

### Шаг 1: Подключитесь к серверу по SSH

```bash
ssh root@your-server-ip
```

### Шаг 2: Скачайте и запустите установочный скрипт

```bash
wget https://raw.githubusercontent.com/YOUR-USERNAME/YOUR-REPO/main/install.sh
chmod +x install.sh
sudo bash install.sh
```

### Шаг 3: Следуйте инструкциям скрипта

Скрипт запросит:
- 📦 URL GitHub репозитория
- 🌐 Домен (tyres.vpnsuba.ru)
- 📧 Email для SSL
- 🔑 Логин и пароль 4tochki API
- 🤖 Telegram Bot Token
- 👤 Admin Telegram ID
- 💰 Процент наценки

### Готово! 🎉

Скрипт автоматически:
- ✅ Установит все зависимости (Python, Node.js, MongoDB, Nginx)
- ✅ Клонирует проект из GitHub
- ✅ Настроит .env файлы
- ✅ Настроит Supervisor
- ✅ Настроит Nginx
- ✅ Установит SSL сертификат
- ✅ Запустит все сервисы

После завершения приложение будет доступно по адресу: **https://tyres.vpnsuba.ru**

---

## 📋 Альтернативный способ (если скрипт уже в репозитории)

```bash
# Клонируем репозиторий
git clone https://github.com/YOUR-USERNAME/YOUR-REPO.git
cd YOUR-REPO

# Запускаем установку
sudo bash install.sh
```

---

## 🔧 Что делать после установки?

### 1. Проверьте статус
```bash
sudo supervisorctl status
```

### 2. Проверьте API
```bash
curl https://tyres.vpnsuba.ru/api/health
```

### 3. Настройте Telegram Bot

Откройте [@BotFather](https://t.me/botfather) и выполните:

```
/newapp
- Выберите вашего бота
- Название: Магазин Шин
- Описание: Шины и диски с доставкой
- Фото: загрузите логотип (512x512px)

/setappdomain
- Выберите приложение
- Введите: tyres.vpnsuba.ru

/setmenubutton
- Выберите бота
- Текст кнопки: 🛒 Открыть магазин
- URL: https://tyres.vpnsuba.ru
```

### 4. Откройте приложение

Перейдите на **https://tyres.vpnsuba.ru** в браузере или через вашего Telegram бота!

---

## 🔄 Переключение на реальное API 4tochki

Когда API поставщика заработает:

```bash
sed -i 's/USE_MOCK_DATA=true/USE_MOCK_DATA=false/' /app/backend/.env
sudo supervisorctl restart backend
```

---

## 📞 Полезные команды

### Статус сервисов
```bash
sudo supervisorctl status
```

### Перезапуск
```bash
sudo supervisorctl restart backend
sudo supervisorctl restart frontend
sudo supervisorctl restart all
```

### Логи
```bash
# Backend
tail -f /var/log/supervisor/backend.err.log

# Frontend  
tail -f /var/log/supervisor/frontend.out.log

# Nginx
tail -f /var/log/nginx/error.log
```

### Тестирование
```bash
# Health check
curl https://tyres.vpnsuba.ru/api/health

# Поиск шин
curl "https://tyres.vpnsuba.ru/api/products/tires/search?width=185&height=60&diameter=15"

# Марки авто
curl https://tyres.vpnsuba.ru/api/cars/brands
```

---

## 🐛 Troubleshooting

### Backend не запускается
```bash
cd /app/backend
pip3 install -r requirements.txt
sudo supervisorctl restart backend
tail -f /var/log/supervisor/backend.err.log
```

### Frontend не запускается
```bash
cd /app/frontend
rm -rf node_modules
yarn install
sudo supervisorctl restart frontend
tail -f /var/log/supervisor/frontend.out.log
```

### SSL не установился
```bash
# Проверьте DNS
dig tyres.vpnsuba.ru

# Установите вручную
sudo certbot --nginx -d tyres.vpnsuba.ru
```

### MongoDB не запущен
```bash
sudo systemctl start mongod
sudo systemctl status mongod
```

---

## 📚 Полная документация

После установки все файлы документации доступны в `/app/`:

- `/app/README.md` - общее описание
- `/app/DEPLOYMENT.md` - подробная инструкция деплоя
- `/app/TEST_COMMANDS.md` - команды для тестирования
- `/root/tyres-commands.txt` - шпаргалка с командами

---

## 🎯 Требования к серверу

Минимальные:
- Ubuntu 20.04+ / Debian 11+
- 2 CPU cores
- 2 GB RAM
- 20 GB disk
- Root доступ

Рекомендуемые:
- Ubuntu 22.04 LTS
- 4 CPU cores
- 4 GB RAM
- 50 GB SSD
- Статический IP

---

## 📞 Поддержка

При возникновении проблем:

1. Проверьте логи (команды выше)
2. Убедитесь что DNS настроен правильно
3. Проверьте что порты 80 и 443 открыты
4. Свяжитесь с поддержкой 4tochki: (495) 38-000-77

---

**Успешной установки! 🚀**
