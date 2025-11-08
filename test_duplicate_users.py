#!/usr/bin/env python3
"""
Тест исправления дублирования создания пользователей

Проверяет что при открытии Mini App создается только 1 пользователь,
а не 2 как было раньше.

Реализованные исправления:
1. Frontend: защита от повторных вызовов через useRef
2. Backend: уникальный индекс на telegram_id в MongoDB
3. Backend: обработка ошибки duplicate key в /api/auth/telegram
"""

import requests
import asyncio
import aiohttp
import time
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
import os

# Configuration
BACKEND_URL = "https://order-info-enhance.preview.emergentagent.com/api"
MONGO_URL = "mongodb://localhost:27017"
DB_NAME = "tires_shop"
ADMIN_TELEGRAM_ID = "508352361"

# Test user IDs
TEST_USER_ID = "test_999111222"
RACE_TEST_USER_ID = f"test_race_{int(time.time())}"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

def print_test(message):
    print(f"\n{Colors.BLUE}{'='*80}{Colors.RESET}")
    print(f"{Colors.BLUE}{message}{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*80}{Colors.RESET}")

def print_success(message):
    print(f"{Colors.GREEN}✅ {message}{Colors.RESET}")

def print_error(message):
    print(f"{Colors.RED}❌ {message}{Colors.RESET}")

def print_warning(message):
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.RESET}")

def print_info(message):
    print(f"ℹ️  {message}")

async def get_db():
    """Подключение к MongoDB"""
    client = AsyncIOMotorClient(MONGO_URL)
    return client[DB_NAME]

async def count_users_in_db(telegram_id: str) -> int:
    """Подсчитать количество пользователей с данным telegram_id в БД"""
    db = await get_db()
    count = await db.users.count_documents({"telegram_id": telegram_id})
    return count

async def get_user_from_db(telegram_id: str):
    """Получить пользователя из БД"""
    db = await get_db()
    user = await db.users.find_one({"telegram_id": telegram_id}, {"_id": 0})
    return user

async def delete_test_user(telegram_id: str):
    """Удалить тестового пользователя из БД (для очистки перед тестом)"""
    db = await get_db()
    result = await db.users.delete_many({"telegram_id": telegram_id})
    if result.deleted_count > 0:
        print_info(f"Удалено {result.deleted_count} тестовых пользователей с ID {telegram_id}")

def test_1_create_new_user():
    """
    Тест 1: Создание нового пользователя
    - POST /api/auth/telegram с новым telegram_id
    - Проверить что пользователь создан
    - Проверить логи: должно быть "New user created: test_999111222"
    """
    print_test("ТЕСТ 1: Создание нового пользователя")
    
    # Очистка перед тестом
    print_info("Очистка тестовых данных перед тестом...")
    asyncio.run(delete_test_user(TEST_USER_ID))
    
    # Создаем нового пользователя
    print_info(f"Отправка POST /api/auth/telegram с telegram_id={TEST_USER_ID}")
    
    payload = {
        "telegram_id": TEST_USER_ID,
        "username": "test_user",
        "first_name": "Test",
        "last_name": "User"
    }
    
    response = requests.post(f"{BACKEND_URL}/auth/telegram", json=payload)
    
    print_info(f"Статус ответа: {response.status_code}")
    
    if response.status_code == 200:
        user_data = response.json()
        print_info(f"Ответ: {user_data}")
        
        # Проверяем что пользователь создан
        if user_data.get("telegram_id") == TEST_USER_ID:
            print_success(f"Пользователь создан с telegram_id={TEST_USER_ID}")
        else:
            print_error(f"Неверный telegram_id в ответе: {user_data.get('telegram_id')}")
            return False
        
        # Проверяем количество пользователей в БД
        count = asyncio.run(count_users_in_db(TEST_USER_ID))
        print_info(f"Количество пользователей с telegram_id={TEST_USER_ID} в БД: {count}")
        
        if count == 1:
            print_success("В БД создан ровно 1 пользователь")
        else:
            print_error(f"В БД найдено {count} пользователей вместо 1")
            return False
        
        print_success("ТЕСТ 1 ПРОЙДЕН")
        return True
    else:
        print_error(f"Ошибка создания пользователя: {response.status_code} - {response.text}")
        return False

def test_2_duplicate_user_attempt():
    """
    Тест 2: Повторная попытка создания того же пользователя
    - POST /api/auth/telegram с тем же telegram_id
    - Проверить что возвращается существующий пользователь (не создается новый)
    - Проверить логи: должно быть "Existing user authenticated: test_999111222"
    """
    print_test("ТЕСТ 2: Повторная попытка создания того же пользователя")
    
    # Проверяем что пользователь уже существует
    count_before = asyncio.run(count_users_in_db(TEST_USER_ID))
    print_info(f"Количество пользователей в БД перед тестом: {count_before}")
    
    if count_before == 0:
        print_error("Пользователь не существует. Сначала запустите Тест 1")
        return False
    
    # Пытаемся создать того же пользователя снова
    print_info(f"Отправка POST /api/auth/telegram с тем же telegram_id={TEST_USER_ID}")
    
    payload = {
        "telegram_id": TEST_USER_ID,
        "username": "test_user_updated",  # Изменяем username
        "first_name": "Test Updated",
        "last_name": "User Updated"
    }
    
    response = requests.post(f"{BACKEND_URL}/auth/telegram", json=payload)
    
    print_info(f"Статус ответа: {response.status_code}")
    
    if response.status_code == 200:
        user_data = response.json()
        print_info(f"Ответ: {user_data}")
        
        # Проверяем что вернулся существующий пользователь (со старыми данными)
        if user_data.get("first_name") == "Test" and user_data.get("username") == "test_user":
            print_success("Возвращен существующий пользователь (данные не изменились)")
        else:
            print_warning(f"Данные пользователя: first_name={user_data.get('first_name')}, username={user_data.get('username')}")
        
        # Проверяем что количество пользователей не увеличилось
        count_after = asyncio.run(count_users_in_db(TEST_USER_ID))
        print_info(f"Количество пользователей в БД после теста: {count_after}")
        
        if count_after == count_before:
            print_success(f"Количество пользователей не изменилось: {count_after}")
        else:
            print_error(f"Количество пользователей увеличилось с {count_before} до {count_after}")
            return False
        
        print_success("ТЕСТ 2 ПРОЙДЕН")
        return True
    else:
        print_error(f"Ошибка: {response.status_code} - {response.text}")
        return False

def test_3_no_duplicates_in_db():
    """
    Тест 3: Проверка отсутствия дубликатов в БД
    - Запросить всех пользователей с telegram_id = test_999111222
    - Подтвердить что существует только 1 запись
    """
    print_test("ТЕСТ 3: Проверка отсутствия дубликатов в БД")
    
    count = asyncio.run(count_users_in_db(TEST_USER_ID))
    print_info(f"Количество пользователей с telegram_id={TEST_USER_ID} в БД: {count}")
    
    if count == 1:
        print_success("В БД существует ровно 1 запись - дубликатов нет")
        
        # Получаем данные пользователя
        user = asyncio.run(get_user_from_db(TEST_USER_ID))
        print_info(f"Данные пользователя: {user}")
        
        print_success("ТЕСТ 3 ПРОЙДЕН")
        return True
    elif count == 0:
        print_error("Пользователь не найден в БД")
        return False
    else:
        print_error(f"Найдено {count} дубликатов пользователя в БД")
        return False

async def create_user_async(session, telegram_id, index):
    """Асинхронное создание пользователя"""
    payload = {
        "telegram_id": telegram_id,
        "username": f"race_user_{index}",
        "first_name": f"Race{index}",
        "last_name": f"Test{index}"
    }
    
    try:
        async with session.post(f"{BACKEND_URL}/auth/telegram", json=payload) as response:
            status = response.status
            data = await response.json()
            return status, data
    except Exception as e:
        return None, str(e)

async def test_4_race_condition_async():
    """
    Тест 4: Симуляция race condition
    - Отправить несколько параллельных запросов создания пользователя с новым ID
    - Проверить что в БД создана только 1 запись
    - Проверить логи на предмет предупреждений "Duplicate user creation attempt detected"
    """
    print_test("ТЕСТ 4: Симуляция race condition (параллельные запросы)")
    
    # Очистка перед тестом
    print_info(f"Очистка тестовых данных для {RACE_TEST_USER_ID}...")
    await delete_test_user(RACE_TEST_USER_ID)
    
    # Отправляем 5 параллельных запросов
    num_requests = 5
    print_info(f"Отправка {num_requests} параллельных запросов создания пользователя...")
    
    async with aiohttp.ClientSession() as session:
        tasks = [create_user_async(session, RACE_TEST_USER_ID, i) for i in range(num_requests)]
        results = await asyncio.gather(*tasks)
    
    # Анализируем результаты
    success_count = sum(1 for status, _ in results if status == 200)
    print_info(f"Успешных ответов (200 OK): {success_count}/{num_requests}")
    
    # Проверяем количество пользователей в БД
    await asyncio.sleep(1)  # Даем время на запись в БД
    count = await count_users_in_db(RACE_TEST_USER_ID)
    print_info(f"Количество пользователей с telegram_id={RACE_TEST_USER_ID} в БД: {count}")
    
    if count == 1:
        print_success("В БД создан ровно 1 пользователь несмотря на параллельные запросы")
        print_success("ТЕСТ 4 ПРОЙДЕН - Race condition обработан корректно")
        return True
    else:
        print_error(f"В БД найдено {count} пользователей вместо 1")
        print_error("Race condition НЕ обработан - создались дубликаты")
        return False

def test_4_race_condition():
    """Обертка для асинхронного теста 4"""
    return asyncio.run(test_4_race_condition_async())

def check_backend_logs():
    """
    Проверка логов backend на наличие ключевых сообщений
    """
    print_test("ПРОВЕРКА ЛОГОВ BACKEND")
    
    print_info("Проверяем логи backend на наличие ключевых сообщений...")
    
    try:
        import subprocess
        
        # Проверяем логи на "New user created"
        result = subprocess.run(
            ["tail", "-n", "100", "/var/log/supervisor/backend.err.log"],
            capture_output=True,
            text=True
        )
        
        logs = result.stdout
        
        # Ищем ключевые сообщения
        if f"New user created: {TEST_USER_ID}" in logs:
            print_success(f"Найдено: 'New user created: {TEST_USER_ID}'")
        else:
            print_warning(f"Не найдено: 'New user created: {TEST_USER_ID}'")
        
        if f"Existing user authenticated: {TEST_USER_ID}" in logs:
            print_success(f"Найдено: 'Existing user authenticated: {TEST_USER_ID}'")
        else:
            print_warning(f"Не найдено: 'Existing user authenticated: {TEST_USER_ID}'")
        
        if "Duplicate user creation attempt detected" in logs:
            print_success("Найдено: 'Duplicate user creation attempt detected'")
            print_info("Это означает что race condition был обработан корректно")
        else:
            print_info("Не найдено: 'Duplicate user creation attempt detected'")
            print_info("Это нормально если не было race condition")
        
        if "Unique index on telegram_id created/verified" in logs:
            print_success("Найдено: 'Unique index on telegram_id created/verified'")
            print_info("Уникальный индекс на telegram_id создан/проверен")
        else:
            print_warning("Не найдено подтверждение создания уникального индекса")
        
    except Exception as e:
        print_error(f"Ошибка при чтении логов: {e}")

def main():
    """Запуск всех тестов"""
    print(f"\n{Colors.BLUE}{'='*80}{Colors.RESET}")
    print(f"{Colors.BLUE}ТЕСТИРОВАНИЕ ИСПРАВЛЕНИЯ ДУБЛИРОВАНИЯ СОЗДАНИЯ ПОЛЬЗОВАТЕЛЕЙ{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*80}{Colors.RESET}")
    print(f"\nBackend URL: {BACKEND_URL}")
    print(f"Test User ID: {TEST_USER_ID}")
    print(f"Race Test User ID: {RACE_TEST_USER_ID}")
    print(f"Timestamp: {datetime.now().isoformat()}\n")
    
    results = []
    
    # Запускаем тесты
    results.append(("Тест 1: Создание нового пользователя", test_1_create_new_user()))
    results.append(("Тест 2: Повторная попытка создания", test_2_duplicate_user_attempt()))
    results.append(("Тест 3: Проверка отсутствия дубликатов", test_3_no_duplicates_in_db()))
    results.append(("Тест 4: Симуляция race condition", test_4_race_condition()))
    
    # Проверяем логи
    check_backend_logs()
    
    # Итоговый отчет
    print(f"\n{Colors.BLUE}{'='*80}{Colors.RESET}")
    print(f"{Colors.BLUE}ИТОГОВЫЙ ОТЧЕТ{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*80}{Colors.RESET}\n")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = f"{Colors.GREEN}✅ ПРОЙДЕН{Colors.RESET}" if result else f"{Colors.RED}❌ ПРОВАЛЕН{Colors.RESET}"
        print(f"{test_name}: {status}")
    
    print(f"\n{Colors.BLUE}Всего тестов: {total}{Colors.RESET}")
    print(f"{Colors.GREEN}Пройдено: {passed}{Colors.RESET}")
    print(f"{Colors.RED}Провалено: {total - passed}{Colors.RESET}")
    
    if passed == total:
        print(f"\n{Colors.GREEN}{'='*80}{Colors.RESET}")
        print(f"{Colors.GREEN}🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!{Colors.RESET}")
        print(f"{Colors.GREEN}{'='*80}{Colors.RESET}\n")
        print_info(f"Тестовые пользователи НЕ удалены из БД (как указано в требованиях):")
        print_info(f"  - {TEST_USER_ID}")
        print_info(f"  - {RACE_TEST_USER_ID}")
    else:
        print(f"\n{Colors.RED}{'='*80}{Colors.RESET}")
        print(f"{Colors.RED}❌ НЕКОТОРЫЕ ТЕСТЫ ПРОВАЛЕНЫ{Colors.RESET}")
        print(f"{Colors.RED}{'='*80}{Colors.RESET}\n")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
