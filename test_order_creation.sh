#!/bin/bash

echo "🧪 Тестирование создания заказа..."

# Создаем тестовый заказ
curl -X POST "http://localhost:8001/api/orders" \
  -H "Content-Type: application/json" \
  -d '{
    "items": [
      {
        "code": "TEST123",
        "name": "Тестовая шина 185/65R15",
        "brand": "Michelin",
        "quantity": 4,
        "price_base": 5000,
        "price_final": 5750,
        "warehouse_id": 1,
        "warehouse_name": "Склад №1"
      }
    ],
    "delivery_address": {
      "city": "Тюмень",
      "street": "Ленина",
      "house": "15",
      "phone": "+7 999 123 45 67",
      "comment": "Тестовый заказ"
    }
  }' \
  -G --data-urlencode "telegram_id=123456789"

echo -e "\n\n✅ Заказ создан!"
echo "Проверяем в БД..."
mongosh --quiet tires_shop --eval "db.orders.find().sort({created_at: -1}).limit(1).pretty()"
