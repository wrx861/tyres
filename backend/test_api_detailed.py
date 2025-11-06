#!/usr/bin/env python3
"""
Детальное тестирование API 4tochki с логированием XML запросов и ответов
Для отправки в техподдержку
"""

import os
import sys
from pathlib import Path
from zeep import Client, Settings
from zeep.cache import SqliteCache
from zeep.transports import Transport
from zeep.plugins import HistoryPlugin
from requests import Session
from lxml import etree
import json

# Загружаем .env
from dotenv import load_dotenv
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Credentials
LOGIN = os.environ.get('FOURTHCHKI_LOGIN')
PASSWORD = os.environ.get('FOURTHCHKI_PASSWORD')
WSDL_URL = os.environ.get('FOURTHCHKI_API_URL')

print("="*70)
print("ТЕСТИРОВАНИЕ API 4TOCHKI")
print("="*70)
print(f"\nLogin: {LOGIN}")
print(f"Password: {'*' * len(PASSWORD)}")
print(f"WSDL URL: {WSDL_URL}")
print()

# Создаем плагин для логирования
history = HistoryPlugin()

# Настройка транспорта
session = Session()
transport = Transport(session=session, cache=SqliteCache())

# Настройки zeep
settings = Settings(strict=False, xml_huge_tree=True)

# Создаем клиента с плагином истории
try:
    client = Client(WSDL_URL, transport=transport, settings=settings, plugins=[history])
    print("✓ SOAP клиент инициализирован")
except Exception as e:
    print(f"✗ Ошибка инициализации клиента: {e}")
    sys.exit(1)

print("\n" + "="*70)
print("ТЕСТ 1: GetMarkaAvto (получение марок автомобилей)")
print("="*70)

try:
    result = client.service.GetMarkaAvto(login=LOGIN, password=PASSWORD)
    
    # Логируем запрос
    print("\n📤 ОТПРАВЛЕННЫЙ XML ЗАПРОС:")
    print("-" * 70)
    if history.last_sent:
        envelope = history.last_sent['envelope']
        print(etree.tostring(envelope, pretty_print=True, encoding='unicode'))
    
    # Логируем ответ
    print("\n📥 ПОЛУЧЕННЫЙ XML ОТВЕТ:")
    print("-" * 70)
    if history.last_received:
        envelope = history.last_received['envelope']
        print(etree.tostring(envelope, pretty_print=True, encoding='unicode'))
    
    # Проверяем результат
    if hasattr(result, 'error') and result.error:
        print(f"\n✗ ОШИБКА API: {result.error}")
        print(f"   Код: {result.error.code}")
        print(f"   Комментарий: {result.error.comment}")
    else:
        brands = result.marka_list if hasattr(result, 'marka_list') else []
        print(f"\n✓ УСПЕХ! Получено марок: {len(brands)}")
        if brands:
            print(f"   Первые 5 марок: {brands[:5]}")
            
except Exception as e:
    print(f"\n✗ ИСКЛЮЧЕНИЕ: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*70)
print("ТЕСТ 2: GetFindTyre (поиск шин)")
print("="*70)

# Параметры из примера поддержки
filter_data = {
    'season_list': ['w'],  # Зимние
    'width_min': 185,
    'width_max': 185,
    'height_min': 60,
    'height_max': 60,
    'diameter_min': 15,
    'diameter_max': 15,
}

print(f"\nФильтр: {json.dumps(filter_data, indent=2, ensure_ascii=False)}")

try:
    result = client.service.GetFindTyre(
        login=LOGIN,
        password=PASSWORD,
        filter=filter_data,
        page=0,
        pageSize=5
    )
    
    # Логируем запрос
    print("\n📤 ОТПРАВЛЕННЫЙ XML ЗАПРОС:")
    print("-" * 70)
    if history.last_sent:
        envelope = history.last_sent['envelope']
        xml_str = etree.tostring(envelope, pretty_print=True, encoding='unicode')
        print(xml_str)
        
        # Сохраняем в файл для отправки в поддержку
        with open('/tmp/4tochki_request.xml', 'w', encoding='utf-8') as f:
            f.write(xml_str)
        print("\n💾 Запрос сохранен в: /tmp/4tochki_request.xml")
    
    # Логируем ответ
    print("\n📥 ПОЛУЧЕННЫЙ XML ОТВЕТ:")
    print("-" * 70)
    if history.last_received:
        envelope = history.last_received['envelope']
        xml_str = etree.tostring(envelope, pretty_print=True, encoding='unicode')
        print(xml_str)
        
        # Сохраняем в файл для отправки в поддержку
        with open('/tmp/4tochki_response.xml', 'w', encoding='utf-8') as f:
            f.write(xml_str)
        print("\n💾 Ответ сохранен в: /tmp/4tochki_response.xml")
    
    # Проверяем результат
    if hasattr(result, 'error') and result.error:
        print(f"\n✗ ОШИБКА API:")
        print(f"   Код: {result.error.code}")
        print(f"   Комментарий: {result.error.comment}")
    else:
        items = result.price_rest_list if hasattr(result, 'price_rest_list') else []
        print(f"\n✓ УСПЕХ! Найдено шин: {len(items)}")
        if items:
            print("\nПервая шина:")
            item = items[0]
            print(f"   Бренд: {getattr(item, 'brand', 'N/A')}")
            print(f"   Модель: {getattr(item, 'model', 'N/A')}")
            print(f"   Размер: {getattr(item, 'width', '?')}/{getattr(item, 'height', '?')} R{getattr(item, 'diameter', '?')}")
            print(f"   Цена: {getattr(item, 'price', 'N/A')} RUB")
            print(f"   Остаток: {getattr(item, 'rest', 'N/A')} шт")
            
except Exception as e:
    print(f"\n✗ ИСКЛЮЧЕНИЕ: {e}")
    import traceback
    traceback.print_exc()
    
    # Сохраняем ошибку
    with open('/tmp/4tochki_error.txt', 'w', encoding='utf-8') as f:
        f.write(f"Exception: {e}\n\n")
        f.write(traceback.format_exc())
    print("\n💾 Ошибка сохранена в: /tmp/4tochki_error.txt")

print("\n" + "="*70)
print("ТЕСТ 3: GetWarehouses (получение складов)")
print("="*70)

try:
    result = client.service.GetWarehouses(login=LOGIN, password=PASSWORD)
    
    if hasattr(result, 'error') and result.error:
        print(f"\n✗ ОШИБКА API: {result.error}")
    else:
        warehouses = result.warehouses if hasattr(result, 'warehouses') else []
        print(f"\n✓ УСПЕХ! Получено складов: {len(warehouses)}")
        if warehouses:
            print("\nСклады:")
            for wh in warehouses[:3]:
                print(f"   - [{getattr(wh, 'id', '?')}] {getattr(wh, 'name', 'N/A')}")
            
except Exception as e:
    print(f"\n✗ ИСКЛЮЧЕНИЕ: {e}")

print("\n" + "="*70)
print("ИТОГО")
print("="*70)
print("\nФайлы для отправки в техподдержку:")
print("  📄 /tmp/4tochki_request.xml   - XML запрос")
print("  📄 /tmp/4tochki_response.xml  - XML ответ")
print("  📄 /tmp/4tochki_error.txt     - Детали ошибки (если есть)")
print("\nДля просмотра:")
print("  cat /tmp/4tochki_request.xml")
print("  cat /tmp/4tochki_response.xml")
print()
