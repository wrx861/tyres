# 🐛 Диагностика проблемы "Привет, Гость!"

## ✅ Добавлен Debug Mode

В приложение добавлен компонент для диагностики проблем с аутентификацией.

---

## 🔧 Как использовать Debug Mode

### 1. Откройте Mini App в Telegram

1. Откройте вашего бота
2. Нажмите кнопку меню
3. Mini App откроется

### 2. Нажмите кнопку "🐛 Debug"

В правом нижнем углу появится кнопка "🐛 Debug"

### 3. Изучите информацию

Debug панель покажет:

#### 👤 User (from App state)
```json
{
  "telegram_id": "508352361",
  "first_name": "SUBA",
  "username": "yourusername",
  "is_admin": true
}
```
- Если `null` - пользователь не аутентифицирован

#### 📱 Telegram WebApp
```json
{
  "version": "7.0",
  "platform": "tdesktop",
  "initDataUnsafe": {
    "user": {
      "id": 508352361,
      "first_name": "SUBA",
      "username": "yourusername",
      "language_code": "ru"
    },
    "auth_date": "1699434000",
    "hash": "abc123..."
  }
}
```

#### 🔗 Backend URL
```
https://tyres.shopmarketbot.ru
```

---

## 📊 Диагностика по результатам

### Случай 1: initDataUnsafe пустой {}

```json
"initDataUnsafe": {}
```

**Проблема:** URL в BotFather неправильный или не обновлён

**Решение:**
1. Откройте @BotFather
2. `/mybots` → Ваш бот → Bot Settings → Menu Button
3. Проверьте URL: `https://tyres.shopmarketbot.ru`
4. Если неправильный - исправьте
5. Закройте Telegram полностью и откройте снова

---

### Случай 2: initDataUnsafe есть, но User null

```json
"initDataUnsafe": {
  "user": {
    "id": 508352361,
    "first_name": "SUBA"
  }
}
// Но User (from App state) = null
```

**Проблема:** Backend не аутентифицирует пользователя

**Возможные причины:**

#### A. Backend недоступен

**Проверка:**
- Нажмите кнопку "Test /api/health" в Debug панели
- Если ошибка → backend недоступен

**Решение:**
```bash
# На сервере
sudo supervisorctl status backend

# Проверить логи
tail -50 /var/log/supervisor/backend.err.log

# Перезапустить
sudo supervisorctl restart backend
```

#### B. CORS проблема

**Проверка консоли браузера (F12):**
```
Access to fetch at 'https://...' from origin 'https://...' 
has been blocked by CORS policy
```

**Решение:**
- Убедитесь что в `backend/server.py` правильно настроен CORS
- Должен разрешать origin: `https://tyres.shopmarketbot.ru`

#### C. Ошибка в /api/auth/telegram

**Проверка консоли браузера (F12):**
```
POST https://tyres.shopmarketbot.ru/api/auth/telegram 
Status: 500 или 400
```

**Решение:**
```bash
# Посмотреть логи backend
tail -100 /var/log/supervisor/backend.err.log | grep -A10 "auth"

# Проверить MongoDB работает
sudo supervisorctl status mongodb
```

---

### Случай 3: User есть, но is_admin: false (нет админки)

```json
"user": {
  "telegram_id": "508352361",
  "is_admin": false  // <-- Должно быть true
}
```

**Проблема:** Пользователь не назначен админом в БД

**Решение:**
```bash
# На сервере подключитесь к MongoDB
mongosh

# Переключитесь на БД
use tires_shop

# Проверьте пользователя
db.users.findOne({"telegram_id": "508352361"})

# Сделайте админом
db.users.updateOne(
  {"telegram_id": "508352361"},
  {"$set": {"is_admin": true}}
)

# Проверьте
db.users.findOne({"telegram_id": "508352361"})
// Должно быть: "is_admin": true
```

---

### Случай 4: Telegram WebApp не доступен

```
❌ Telegram WebApp не доступен
```

**Проблема:** Приложение открыто не в Telegram

**Решение:**
- Не открывайте https://tyres.shopmarketbot.ru в обычном браузере
- Откройте только через Telegram бота
- В обычном браузере всегда будет "Гость"

---

## 🔍 Консоль браузера (F12)

После открытия Mini App в консоли должны быть логи:

```
🚀 Initializing app...
📱 Telegram WebApp initialized: true
👤 Telegram user data: {id: 508352361, first_name: "SUBA", ...}
✅ Telegram user получен: {...}
🔐 Аутентификация пользователя...
✅ User authenticated: {telegram_id: "508352361", ...}
```

### Если видите ошибки:

#### ❌ Не удалось получить данные пользователя
```
❌ Не удалось получить данные пользователя из Telegram
🔍 Проверьте:
  1. URL в BotFather обновлён на: https://tyres.shopmarketbot.ru
  2. Приложение открыто через Telegram (не браузер)
  3. initDataUnsafe: {}
```

**Действия:** Обновите URL в BotFather

#### ❌ Authentication failed
```
❌ Authentication failed: Error: Network Error
Status: undefined
```

**Действия:** Backend недоступен или CORS проблема

---

## 🧪 Ручная проверка

### 1. Проверка Backend

```bash
# Health check
curl https://tyres.shopmarketbot.ru/api/health

# Ожидаем:
{"status":"healthy","database":"connected"}
```

### 2. Проверка аутентификации (с валидными данными)

```bash
curl -X POST https://tyres.shopmarketbot.ru/api/auth/telegram \
  -H "Content-Type: application/json" \
  -d '{
    "telegram_id": "508352361",
    "first_name": "SUBA",
    "username": "yourusername"
  }'

# Ожидаем:
{
  "telegram_id": "508352361",
  "first_name": "SUBA",
  "username": "yourusername",
  "is_admin": true
}
```

### 3. Проверка CORS

```bash
curl -H "Origin: https://tyres.shopmarketbot.ru" \
     -H "Access-Control-Request-Method: POST" \
     -H "Access-Control-Request-Headers: Content-Type" \
     -X OPTIONS \
     https://tyres.shopmarketbot.ru/api/auth/telegram -I

# Должны быть заголовки:
Access-Control-Allow-Origin: https://tyres.shopmarketbot.ru
Access-Control-Allow-Methods: POST, GET, ...
```

---

## 📝 Чек-лист диагностики

- [ ] URL в BotFather = `https://tyres.shopmarketbot.ru`
- [ ] SSL сертификат валиден (замок 🔒)
- [ ] Backend работает (`curl /api/health`)
- [ ] MongoDB работает (`sudo supervisorctl status mongodb`)
- [ ] Приложение открыто через Telegram (не браузер)
- [ ] Debug панель показывает initDataUnsafe.user
- [ ] Консоль браузера (F12) без ошибок
- [ ] CORS разрешает домен
- [ ] Пользователь в БД с is_admin: true

---

## 🚀 Быстрое решение по шагам

### Шаг 1: Проверьте URL в BotFather
```
@BotFather → /mybots → Ваш бот → Bot Settings → Menu Button
URL должен быть: https://tyres.shopmarketbot.ru
```

### Шаг 2: Проверьте backend
```bash
curl https://tyres.shopmarketbot.ru/api/health
```

### Шаг 3: Откройте Mini App через Telegram
- НЕ в браузере!
- Только через бота в Telegram

### Шаг 4: Нажмите "🐛 Debug"
- Изучите что показывает
- Действуйте по инструкциям выше

### Шаг 5: Проверьте консоль (F12)
- Должны быть логи с эмодзи (🚀, 📱, 👤, ✅)
- Если есть ❌ - читайте сообщение ошибки

---

## 💡 Частые решения

### "initDataUnsafe пустой"
→ Обновите URL в BotFather  
→ Перезапустите Telegram

### "Authentication failed: Network Error"
→ Backend недоступен  
→ `sudo supervisorctl restart backend`

### "User null, но initDataUnsafe есть"
→ Проверьте логи backend  
→ `tail -100 /var/log/supervisor/backend.err.log`

### "is_admin: false"
→ Сделайте себя админом в MongoDB  
→ `db.users.updateOne({telegram_id: "..."}, {$set: {is_admin: true}})`

---

**Дата:** 2025-11-08  
**Версия:** 1.0  
**Статус:** ✅ Debug mode активен
