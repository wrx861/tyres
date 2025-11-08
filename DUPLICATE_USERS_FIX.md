# Исправление дублирования создания пользователей

## Проблема

При открытии Telegram Mini App создавались **2 пользователя** вместо одного.

### Симптомы:
- В админ-панели появлялись дублирующиеся записи пользователей с одинаковым `telegram_id`
- Происходило при каждом первом открытии Mini App новым пользователем

## Причина

**React.StrictMode** в `frontend/src/index.js` вызывает `useEffect` дважды при монтировании компонента в development режиме.

### Как это происходило:
1. `App.js` → `useEffect` вызывает `initializeApp()`
2. `initializeApp()` → вызывает `authenticateUser(telegramUser)`
3. В StrictMode оба вызова происходят почти одновременно
4. Оба отправляют `POST /api/auth/telegram` на backend
5. Backend проверяет существование пользователя: `find_one(telegram_id)`
6. Оба запроса получают `null` (пользователь не существует)
7. Оба запроса пытаются создать нового пользователя → **2 пользователя в БД**

## Решение

Реализована трехуровневая защита от дублирования:

### 1. Frontend защита (App.js)

```javascript
// Добавлены useRef для отслеживания состояния инициализации
const isInitializing = useRef(false);
const isInitialized = useRef(false);

useEffect(() => {
  // Предотвращаем повторные вызовы
  if (isInitializing.current || isInitialized.current) {
    return;
  }
  
  isInitializing.current = true;
  initializeApp();
}, []);
```

**Что это дает:**
- Защита от двойного вызова `initializeApp()` в React.StrictMode
- Первый вызов выполняется, последующие игнорируются

### 2. Backend защита на уровне БД (server.py)

```python
@app.on_event("startup")
async def startup_event():
    # Создаем уникальный индекс на telegram_id
    await db.users.create_index("telegram_id", unique=True)
    logger.info("✅ Unique index on telegram_id created/verified")
```

**Что это дает:**
- MongoDB отклоняет попытки создать пользователя с существующим `telegram_id`
- Защита на уровне базы данных (самая надежная)

### 3. Backend обработка race condition (auth.py)

```python
try:
    await db.users.insert_one(user_dict)
    logger.info(f"New user created: {user_data.telegram_id}")
except Exception as insert_error:
    # Если произошла ошибка дубликата ключа (race condition)
    if "duplicate key" in str(insert_error).lower() or "E11000" in str(insert_error):
        logger.warning(f"Duplicate user creation attempt detected for {user_data.telegram_id}")
        # Возвращаем существующего пользователя
        existing_user = await db.users.find_one({"telegram_id": user_data.telegram_id})
        return User(**existing_user)
```

**Что это дает:**
- Graceful обработка ошибки duplicate key
- При попытке создать дубликат возвращается существующий пользователь
- Логирование попыток дублирования для мониторинга

## Тестирование

Проведено полное тестирование с использованием `test_duplicate_users.py`:

### ✅ Тест 1: Создание нового пользователя
- Новый пользователь создается корректно
- В БД создается ровно 1 запись

### ✅ Тест 2: Повторная попытка создания
- Возвращается существующий пользователь
- Количество записей в БД не увеличивается

### ✅ Тест 3: Проверка отсутствия дубликатов
- В БД существует только 1 запись с данным telegram_id

### ✅ Тест 4: Симуляция race condition
- 5 параллельных запросов создания пользователя
- В БД создается только 1 запись
- 4 запроса получают существующего пользователя

**Результат: 4/4 тестов пройдено (100% успех)**

## Файлы изменены

1. **frontend/src/App.js**
   - Добавлены `useRef` для защиты от повторных вызовов
   - Обновлена логика `useEffect`

2. **backend/server.py**
   - Добавлено создание уникального индекса при старте приложения

3. **backend/routers/auth.py**
   - Добавлена обработка ошибки duplicate key
   - Улучшено логирование

## Проверка состояния БД

```bash
# Проверка уникального индекса
db.users.getIndexes()
# Результат: telegram_id_1 с unique=True ✅

# Проверка дубликатов
db.users.aggregate([
  {$group: {_id: "$telegram_id", count: {$sum: 1}}},
  {$match: {count: {$gt: 1}}}
])
# Результат: [] (дубликатов нет) ✅
```

## Мониторинг

Для отслеживания попыток создания дубликатов проверяйте логи backend:

```bash
tail -f /var/log/tyres-backend.err.log | grep -E "(New user created|Existing user authenticated|Duplicate user creation)"
```

**Нормальное поведение:**
- `New user created: <telegram_id>` - первое создание пользователя
- `Existing user authenticated: <telegram_id>` - повторный вход

**Проблемное поведение (требует внимания):**
- `Duplicate user creation attempt detected` - race condition (обработан корректно, но стоит мониторить частоту)

## Заключение

Проблема дублирования пользователей **полностью решена** на трех уровнях:
1. Frontend - предотвращение множественных вызовов
2. Database - уникальный индекс
3. Backend - graceful обработка race conditions

Все тесты пройдены успешно. Приложение готово к использованию.

---
**Дата исправления:** 8 ноября 2025  
**Версия:** 1.0
