# Инструкции по исправлению проблем на сервере

## Проблемы, которые нужно исправить:

### 1. Telegram бот не запускается (FATAL)

**Проверка:**
```bash
sudo supervisorctl status tyres-telegram-bot
```

**Решение:**
```bash
# Проверьте конфигурацию supervisor
sudo cat /etc/supervisor/conf.d/tyres.conf

# Убедитесь что секция для бота существует и правильная:
# [program:tyres-telegram-bot]
# command=python3 telegram_bot.py
# directory=/opt/tyres-app
# ...
```

Если конфигурация не правильная, нужно перезапустить install.sh или вручную исправить конфигурацию.

### 2. Frontend не запущен (STOPPED Not started)

Frontend должен быть в режиме `autostart=false` так как Nginx раздает статические файлы из `/opt/tyres-app/frontend/build`.

**Проверка:**
```bash
# Проверьте что frontend собран
ls -la /opt/tyres-app/frontend/build/

# Если build отсутствует:
cd /opt/tyres-app/frontend
yarn build
```

### 3. Логи отсутствуют

**Проверка:**
```bash
# Список файлов логов
ls -la /var/log/tyres*
ls -la /var/log/supervisor/tyres*

# Если логи не существуют, создайте их
sudo touch /var/log/tyres-backend.out.log /var/log/tyres-backend.err.log
sudo touch /var/log/tyres-telegram-bot.out.log /var/log/tyres-telegram-bot.err.log
sudo supervisorctl restart all
```

## Проблемы в коде (уже исправлены):

### 1. ✅ Middleware блокировки
- Теперь SearchPage и CarSelectionPage передают `telegram_id` в запросах
- Middleware корректно проверяет блокировку пользователя

### 2. ✅ Логирование активности
- SearchPage передает `telegram_id` для логирования поиска
- Логи сохраняются в MongoDB коллекции `activity_logs`

### 3. ⚠️ Корзина НЕ интегрирована с API
- Корзина все еще работает локально в памяти браузера
- Для полной интеграции нужно обновить App.js (см. ниже)

## Интеграция корзины с API (опционально):

Если хотите чтобы корзина сохранялась на сервере, замените функции в `/app/frontend/src/App.js`:

```javascript
// Загрузка корзины при инициализации
useEffect(() => {
  if (user?.telegram_id) {
    loadCartFromServer();
  }
}, [user]);

const loadCartFromServer = async () => {
  try {
    const response = await getCart(user.telegram_id);
    setCart(response.items || []);
  } catch (error) {
    console.error('Ошибка загрузки корзины:', error);
  }
};

const addToCart = async (item) => {
  if (!user?.telegram_id) return;
  
  try {
    await addToCart(user.telegram_id, item);
    await loadCartFromServer();
  } catch (error) {
    console.error('Ошибка добавления в корзину:', error);
  }
};
```

## После внесения изменений:

```bash
# 1. Перезапустите backend
sudo supervisorctl restart tyres-backend

# 2. Пересоберите frontend
cd /opt/tyres-app/frontend
yarn build

# 3. Перезапустите nginx
sudo systemctl restart nginx

# 4. Проверьте статус
sudo supervisorctl status
```

## Проверка работы:

### Проверка блокировки:
1. Зайдите в админ панель
2. Заблокируйте тестового пользователя
3. Попробуйте выполнить поиск от имени этого пользователя
4. Должна появиться ошибка: "Слишком много запросов, подождите еще и вернитесь не скоро"

### Проверка логирования:
1. Выполните поиск шин или дисков
2. Зайдите в админ панель → Активность
3. Должны появиться записи о поиске

### Проверка корзины (если интегрирована):
1. Добавьте товар в корзину
2. Закройте приложение
3. Откройте снова
4. Товар должен остаться в корзине
