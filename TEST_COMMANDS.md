# 🧪 Команды для тестирования приложения

## Быстрая проверка статуса

```bash
# Статус всех сервисов
sudo supervisorctl status

# Проверка портов
netstat -tulpn | grep -E ':(3000|8001|27017)'
```

## Тестирование Backend API

### 1. Health Check
```bash
curl http://localhost:8001/api/health
```

### 2. Поиск шин
```bash
curl "http://localhost:8001/api/products/tires/search?width=185&height=60&diameter=15&season=winter&page_size=3"
```

### 3. Поиск дисков
```bash
curl "http://localhost:8001/api/products/disks/search?diameter=15&page_size=3"
```

### 4. Марки автомобилей
```bash
curl "http://localhost:8001/api/cars/brands"
```

### 5. Модели Toyota
```bash
curl "http://localhost:8001/api/cars/models?brand=Toyota"
```

### 6. Склады
```bash
curl "http://localhost:8001/api/products/warehouses"
```

## Тестирование создания заказа

### 1. Создать тестового пользователя
```bash
curl -X POST "http://localhost:8001/api/auth/telegram" \
  -H "Content-Type: application/json" \
  -d '{
    "telegram_id": "999999999",
    "username": "testclient",
    "first_name": "Test",
    "last_name": "Client"
  }'
```

### 2. Создать заказ
```bash
curl -X POST "http://localhost:8001/api/orders?telegram_id=999999999" \
  -H "Content-Type: application/json" \
  -d '{
    "items": [
      {
        "code": "TIRE10000",
        "name": "Test Tire",
        "brand": "Michelin",
        "quantity": 4,
        "price_base": 5000,
        "price_final": 5750,
        "warehouse_id": 1,
        "warehouse_name": "Москва"
      }
    ],
    "delivery_address": {
      "city": "Москва",
      "street": "Тверская",
      "house": "10",
      "apartment": "25",
      "comment": "Позвоните за час"
    }
  }'
```

### 3. Посмотреть заказы пользователя
```bash
curl "http://localhost:8001/api/orders/my?telegram_id=999999999"
```

## Тестирование админ-функций

### 1. Создать админа (если не создан)
```bash
curl -X POST "http://localhost:8001/api/auth/telegram" \
  -H "Content-Type: application/json" \
  -d '{
    "telegram_id": "508352361",
    "username": "admin",
    "first_name": "Admin",
    "last_name": "User"
  }'
```

### 2. Получить заказы на подтверждение
```bash
curl "http://localhost:8001/api/orders/admin/pending?telegram_id=508352361"
```

### 3. Подтвердить заказ (замените ORDER_ID)
```bash
curl -X POST "http://localhost:8001/api/orders/ORD-20251105165653/confirm?telegram_id=508352361" \
  -H "Content-Type: application/json" \
  -d '{"admin_comment": "Заказ подтвержден, ожидайте доставку"}'
```

### 4. Отклонить заказ (замените ORDER_ID)
```bash
curl -X POST "http://localhost:8001/api/orders/ORD-20251105165653/reject?telegram_id=508352361" \
  -H "Content-Type: application/json" \
  -d '{"reason": "Товар закончился"}'
```

### 5. Получить статистику
```bash
curl "http://localhost:8001/api/admin/stats?telegram_id=508352361"
```

### 6. Получить наценку
```bash
curl "http://localhost:8001/api/admin/markup?telegram_id=508352361"
```

### 7. Изменить наценку на 20%
```bash
curl -X PUT "http://localhost:8001/api/admin/markup?telegram_id=508352361" \
  -H "Content-Type: application/json" \
  -d '{"markup_percentage": 20}'
```

## Проверка Frontend

```bash
# Проверка что frontend отдает HTML
curl -I http://localhost:3000

# Проверка через браузер
# Откройте: http://localhost:3000
```

## Проверка MongoDB

```bash
# Подключение к MongoDB
mongo

# Внутри mongo shell:
use tires_shop
db.users.find().pretty()
db.orders.find().pretty()
db.settings.find().pretty()

# Выход: exit
```

## Логи

```bash
# Backend логи (ошибки)
tail -f /var/log/supervisor/backend.err.log

# Backend логи (вывод)
tail -f /var/log/supervisor/backend.out.log

# Frontend логи
tail -f /var/log/supervisor/frontend.out.log

# Все логи supervisor
tail -f /var/log/supervisor/*.log
```

## Перезапуск сервисов

```bash
# Перезапуск backend
sudo supervisorctl restart backend

# Перезапуск frontend
sudo supervisorctl restart frontend

# Перезапуск всех
sudo supervisorctl restart all

# Остановка всех
sudo supervisorctl stop all

# Запуск всех
sudo supervisorctl start all
```

## Очистка базы данных (для тестов)

```bash
# Подключитесь к mongo
mongo

# Очистите коллекции
use tires_shop
db.orders.deleteMany({})
db.users.deleteMany({})

# Или удалите всю базу
use tires_shop
db.dropDatabase()

# Выход
exit
```

## Проверка производительности

```bash
# Нагрузочное тестирование (установите apache2-utils)
sudo apt install apache2-utils

# 100 запросов, 10 одновременно
ab -n 100 -c 10 http://localhost:8001/api/health

# Проверка времени ответа
time curl "http://localhost:8001/api/products/tires/search?width=185"
```

## Мониторинг ресурсов

```bash
# Использование CPU и памяти
htop

# Дисковое пространство
df -h

# Использование памяти процессами
ps aux --sort=-%mem | head -10

# Сетевые соединения
netstat -tuln
```

## Быстрая диагностика проблем

```bash
# 1. Проверка что все запущено
sudo supervisorctl status

# 2. Проверка портов
sudo netstat -tulpn | grep -E ':(3000|8001|27017)'

# 3. Проверка логов на ошибки
sudo tail -100 /var/log/supervisor/backend.err.log | grep -i error
sudo tail -100 /var/log/supervisor/frontend.err.log | grep -i error

# 4. Проверка MongoDB
sudo systemctl status mongod

# 5. Тест API
curl http://localhost:8001/api/health

# 6. Тест Frontend
curl -I http://localhost:3000
```

## Полный цикл тестирования

```bash
#!/bin/bash
echo "🧪 Начало тестирования..."

echo "1. Проверка сервисов..."
sudo supervisorctl status

echo "2. Health check..."
curl -s http://localhost:8001/api/health | jq

echo "3. Поиск шин..."
curl -s "http://localhost:8001/api/products/tires/search?width=185&page_size=2" | jq '.data[0]'

echo "4. Марки авто..."
curl -s "http://localhost:8001/api/cars/brands" | jq '.data[:5]'

echo "5. Создание пользователя..."
curl -s -X POST "http://localhost:8001/api/auth/telegram" \
  -H "Content-Type: application/json" \
  -d '{"telegram_id":"777777","username":"test","first_name":"Test"}' | jq

echo "✅ Тестирование завершено!"
```

Сохраните этот скрипт как `test.sh`, сделайте исполняемым (`chmod +x test.sh`) и запустите (`./test.sh`)
