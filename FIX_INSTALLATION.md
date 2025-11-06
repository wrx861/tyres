# 🔧 Исправление уже установленного приложения

## Проблема
Backend не запускается с ошибкой: `KeyError: 'DB_NAME'`

## Причина
В файле `.env` отсутствует переменная `DB_NAME` (была только `MONGO_URL` с именем базы внутри URL).

---

## ✅ Решение (для уже установленного приложения)

### Шаг 1: Откройте файл .env

```bash
sudo nano /opt/tyres-app/backend/.env
```

### Шаг 2: Проверьте структуру файла

**Неправильно (старая версия):**
```env
MONGO_URL=mongodb://localhost:27017/tyres_db
FOURTHCHKI_LOGIN=sa56026
...
```

**Правильно (новая версия):**
```env
MONGO_URL=mongodb://localhost:27017
DB_NAME=tires_shop
CORS_ORIGINS=*

# 4tochki API Credentials
FOURTHCHKI_LOGIN=sa56026
FOURTHCHKI_PASSWORD=ваш_пароль
FOURTHCHKI_API_URL=http://api-b2b.4tochki.ru/WCF/ClientService.svc?wsdl

# Telegram Bot
TELEGRAM_BOT_TOKEN=ваш_токен
ADMIN_TELEGRAM_ID=ваш_id

# Pricing
DEFAULT_MARKUP_PERCENTAGE=15

# Mock Mode
USE_MOCK_DATA=false
```

### Шаг 3: Внесите изменения

1. **Измените** `MONGO_URL`:
   - Было: `mongodb://localhost:27017/tyres_db`
   - Стало: `mongodb://localhost:27017`

2. **Добавьте** после MONGO_URL:
   ```env
   DB_NAME=tires_shop
   CORS_ORIGINS=*
   ```

3. **Добавьте комментарии** для читаемости (опционально)

### Шаг 4: Сохраните и выйдите

- Нажмите `Ctrl + O` (сохранить)
- Нажмите `Enter` (подтвердить)
- Нажмите `Ctrl + X` (выйти)

### Шаг 5: Перезапустите сервисы

```bash
sudo supervisorctl restart all
```

### Шаг 6: Проверьте статус

```bash
sudo supervisorctl status
```

**Должно быть:**
```
tyres-backend                    RUNNING   pid 1234, uptime 0:00:05
tyres-frontend                   RUNNING   pid 1235, uptime 0:00:05
```

Если backend в статусе `RUNNING` - всё работает! ✅

---

## 🚨 Если backend всё ещё не запускается

### Проверьте логи ошибок:

```bash
tail -n 50 /var/log/tyres-backend.err.log
```

### Частые проблемы:

**1. MongoDB не запущен**
```bash
sudo systemctl status mongod
sudo systemctl start mongod
```

**2. Неправильные кавычки в .env**
```env
# Неправильно:
MONGO_URL="mongodb://localhost:27017"

# Правильно (без кавычек):
MONGO_URL=mongodb://localhost:27017
```

**3. Отсутствуют зависимости**
```bash
cd /opt/tyres-app/backend
source venv/bin/activate
pip install -r requirements.txt
deactivate
sudo supervisorctl restart tyres-backend
```

---

## 📋 Полный шаблон .env файла

Скопируйте и замените содержимое файла `/opt/tyres-app/backend/.env`:

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

> **Замените** `FOURTHCHKI_PASSWORD`, `TELEGRAM_BOT_TOKEN`, `ADMIN_TELEGRAM_ID` на ваши данные!

---

## 🔄 Для новых установок

Проблема уже исправлена в обновлённом установщике. Скачайте новую версию:

```bash
wget https://raw.githubusercontent.com/wrx861/tyres/main/install.sh
sudo bash install.sh
```

Теперь установщик создаёт `.env` с правильной структурой.

---

## ✅ Проверка что всё работает

После исправления и перезапуска:

```bash
# Проверка статуса
sudo supervisorctl status

# Проверка логов (не должно быть ошибок)
tail -f /var/log/tyres-backend.out.log

# Тест API
curl http://localhost:8001/api/health
# Ответ: {"status":"healthy","database":"connected"}
```

---

## 📞 Всё ещё не работает?

1. Проверьте что MongoDB запущен: `sudo systemctl status mongod`
2. Проверьте что порт 8001 свободен: `sudo netstat -tulpn | grep 8001`
3. Посмотрите полные логи: `tail -n 100 /var/log/tyres-backend.err.log`
4. Проверьте файл .env: `cat /opt/tyres-app/backend/.env`
