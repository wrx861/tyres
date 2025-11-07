#!/usr/bin/env python3
"""
Тестирование извлечения брендов из GetFindTyre и GetFindDisk
"""

import sys
sys.path.append('/app/backend')

from services.fourthchki_client import FourthchkiClient
import json

print("="*60)
print("🔍 Извлечение брендов шин и дисков")
print("="*60)

client = FourthchkiClient()

# 1. Получить бренды шин
print("\n1️⃣ Получение брендов ШИНЫ (без фильтров, первые 100)...")
try:
    response = client.search_tires(page=0, page_size=100)
    
    tire_brands = set()
    if 'tyre_list' in response and response['tyre_list']:
        for tyre in response['tyre_list']:
            if 'brand' in tyre and tyre['brand']:
                tire_brands.add(tyre['brand'])
    
    print(f"✅ Найдено уникальных брендов шин: {len(tire_brands)}")
    if tire_brands:
        sorted_brands = sorted(tire_brands)
        print(f"📋 Бренды шин:")
        for i, brand in enumerate(sorted_brands, 1):
            print(f"   {i}. {brand}")
    
except Exception as e:
    print(f"❌ Ошибка: {e}")

# 2. Получить бренды дисков
print("\n2️⃣ Получение брендов ДИСКИ (без фильтров, первые 100)...")
try:
    response = client.search_disks(page=0, page_size=100)
    
    disk_brands = set()
    if 'disk_list' in response and response['disk_list']:
        for disk in response['disk_list']:
            if 'brand' in disk and disk['brand']:
                disk_brands.add(disk['brand'])
    
    print(f"✅ Найдено уникальных брендов дисков: {len(disk_brands)}")
    if disk_brands:
        sorted_brands = sorted(disk_brands)
        print(f"📋 Бренды дисков:")
        for i, brand in enumerate(sorted_brands, 1):
            print(f"   {i}. {brand}")
    
except Exception as e:
    print(f"❌ Ошибка: {e}")

# 3. Попробуем разные параметры для получения больше брендов
print("\n3️⃣ Дополнительная выборка с разными размерами...")
all_tire_brands = set()
all_disk_brands = set()

# Разные размеры шин
tire_sizes = [
    {'diameter_min': 13, 'diameter_max': 14},
    {'diameter_min': 15, 'diameter_max': 16},
    {'diameter_min': 17, 'diameter_max': 18},
    {'diameter_min': 19, 'diameter_max': 20},
]

for size_filter in tire_sizes:
    try:
        response = client.search_tires(page=0, page_size=50, **size_filter)
        if 'tyre_list' in response and response['tyre_list']:
            for tyre in response['tyre_list']:
                if 'brand' in tyre and tyre['brand']:
                    all_tire_brands.add(tyre['brand'])
    except:
        pass

print(f"✅ Всего найдено брендов шин: {len(all_tire_brands)}")

# Разные размеры дисков
disk_sizes = [
    {'diameter_min': 13, 'diameter_max': 14},
    {'diameter_min': 15, 'diameter_max': 16},
    {'diameter_min': 17, 'diameter_max': 18},
    {'diameter_min': 19, 'diameter_max': 20},
]

for size_filter in disk_sizes:
    try:
        response = client.search_disks(page=0, page_size=50, **size_filter)
        if 'disk_list' in response and response['disk_list']:
            for disk in response['disk_list']:
                if 'brand' in disk and disk['brand']:
                    all_disk_brands.add(disk['brand'])
    except:
        pass

print(f"✅ Всего найдено брендов дисков: {len(all_disk_brands)}")

# Объединенный список
print("\n" + "="*60)
print("📊 ИТОГОВЫЙ СПИСОК БРЕНДОВ")
print("="*60)

print(f"\n🚗 ШИНЫ ({len(all_tire_brands)} брендов):")
for brand in sorted(all_tire_brands):
    print(f"   • {brand}")

print(f"\n⚙️ ДИСКИ ({len(all_disk_brands)} брендов):")
for brand in sorted(all_disk_brands):
    print(f"   • {brand}")

# Сохраним в JSON для использования
brands_data = {
    'tires': sorted(all_tire_brands),
    'disks': sorted(all_disk_brands),
    'combined': sorted(all_tire_brands | all_disk_brands)
}

with open('/app/brands_cache.json', 'w', encoding='utf-8') as f:
    json.dump(brands_data, f, ensure_ascii=False, indent=2)

print(f"\n✅ Данные сохранены в /app/brands_cache.json")
print(f"📊 Всего уникальных брендов: {len(brands_data['combined'])}")
