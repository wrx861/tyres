#!/usr/bin/env python3
"""
Скрипт для изучения доступных методов API 4tochki
"""

from zeep import Client
from zeep.cache import SqliteCache
from zeep.transports import Transport
from requests import Session
import os
from dotenv import load_dotenv

load_dotenv('/app/backend/.env')

LOGIN = os.environ.get('FOURTHCHKI_LOGIN')
PASSWORD = os.environ.get('FOURTHCHKI_PASSWORD')
WSDL_URL = os.environ.get('FOURTHCHKI_API_URL')

print("="*60)
print("🔍 Изучение API 4tochki")
print("="*60)

# Создаем клиент
session = Session()
session.verify = False
transport = Transport(session=session, cache=SqliteCache())
client = Client(WSDL_URL, transport=transport)

print("\n📋 Доступные методы API:")
print("-"*60)

for service in client.wsdl.services.values():
    print(f"\n🔹 Сервис: {service.name}")
    for port in service.ports.values():
        operations = sorted(port.binding._operations.values(), key=lambda x: x.name)
        for operation in operations:
            print(f"   • {operation.name}")
            
print("\n" + "="*60)
print("🔍 Поиск методов связанных с брендами:")
print("="*60)

brand_methods = []
for service in client.wsdl.services.values():
    for port in service.ports.values():
        operations = port.binding._operations.values()
        for operation in operations:
            name = operation.name.lower()
            if 'brand' in name or 'marka' in name or 'производ' in name or 'товар' in name:
                brand_methods.append(operation.name)
                print(f"✅ Найден метод: {operation.name}")

if not brand_methods:
    print("❌ Методы с 'brand' в названии не найдены")
    print("\n💡 Проверим методы с 'Get' в начале:")
    for service in client.wsdl.services.values():
        for port in service.ports.values():
            operations = sorted(port.binding._operations.values(), key=lambda x: x.name)
            for operation in operations:
                if operation.name.startswith('Get'):
                    print(f"   • {operation.name}")

print("\n" + "="*60)
print("🧪 Попробуем получить список брендов разными способами")
print("="*60)

# Попытка 1: GetGoodsInfo - может содержать бренды
try:
    print("\n1️⃣ Пробуем GetGoodsInfo с фильтром...")
    response = client.service.GetGoodsInfo(
        login=LOGIN,
        password=PASSWORD,
        filter={'good_name': ''},  # Пустой фильтр
        page=0,
        pageSize=10
    )
    
    if hasattr(response, 'error') and response.error.code:
        print(f"   ❌ Ошибка: {response.error.description}")
    else:
        # Проверим структуру
        if hasattr(response, 'goods_list') and response.goods_list:
            brands = set()
            for good in response.goods_list[:10]:
                if hasattr(good, 'brand'):
                    brands.add(good.brand)
            print(f"   ✅ Найдено брендов в первых 10 товарах: {len(brands)}")
            if brands:
                print(f"   📋 Примеры брендов: {', '.join(list(brands)[:5])}")
except Exception as e:
    print(f"   ❌ Ошибка GetGoodsInfo: {e}")

# Попытка 2: GetFindTyre без фильтров
try:
    print("\n2️⃣ Пробуем GetFindTyre без фильтров (первые 20 шин)...")
    response = client.service.GetFindTyre(
        login=LOGIN,
        password=PASSWORD,
        filter=None,
        page=0,
        pageSize=20
    )
    
    if hasattr(response, 'error') and response.error and response.error.code:
        print(f"   ❌ Ошибка: {response.error.description}")
    else:
        brands = set()
        if hasattr(response, 'tyre_list') and response.tyre_list:
            for tyre in response.tyre_list:
                if hasattr(tyre, 'brand'):
                    brands.add(tyre.brand)
        print(f"   ✅ Найдено уникальных брендов: {len(brands)}")
        if brands:
            sorted_brands = sorted(brands)
            print(f"   📋 Бренды шин: {', '.join(sorted_brands[:10])}")
            if len(sorted_brands) > 10:
                print(f"   ... и еще {len(sorted_brands) - 10} брендов")
except Exception as e:
    print(f"   ❌ Ошибка GetFindTyre: {e}")

# Попытка 3: GetFindDisk без фильтров
try:
    print("\n3️⃣ Пробуем GetFindDisk без фильтров (первые 20 дисков)...")
    response = client.service.GetFindDisk(
        login=LOGIN,
        password=PASSWORD,
        filter=None,
        page=0,
        pageSize=20
    )
    
    if hasattr(response, 'error') and response.error and response.error.code:
        print(f"   ❌ Ошибка: {response.error.description}")
    else:
        brands = set()
        if hasattr(response, 'disk_list') and response.disk_list:
            for disk in response.disk_list:
                if hasattr(disk, 'brand'):
                    brands.add(disk.brand)
        print(f"   ✅ Найдено уникальных брендов: {len(brands)}")
        if brands:
            sorted_brands = sorted(brands)
            print(f"   📋 Бренды дисков: {', '.join(sorted_brands[:10])}")
            if len(sorted_brands) > 10:
                print(f"   ... и еще {len(sorted_brands) - 10} брендов")
except Exception as e:
    print(f"   ❌ Ошибка GetFindDisk: {e}")

print("\n" + "="*60)
print("💡 ВЫВОД:")
print("="*60)
print("""
Если API 4tochki не имеет прямого метода GetBrandList,
можно использовать один из подходов:

1. Кэшировать бренды из запросов GetFindTyre/GetFindDisk
2. Создать статический список популярных брендов
3. Парсить бренды из нескольких запросов с разными параметрами

Рекомендуется: создать endpoint который:
- Делает запрос к API для получения товаров
- Собирает уникальные бренды
- Кэширует результат на сервере (Redis или в памяти)
""")
