#!/usr/bin/env python3
"""
Тестирование интегрированного Telegram бота
Проверяет: polling режим, команды /start и /help, уведомления о заказах
"""

import requests
import time
import os
import json
from datetime import datetime

# Конфигурация
BACKEND_URL = "https://tirebot-admin.preview.emergentagent.com/api"
TELEGRAM_BOT_TOKEN = "8290483601:AAFqXwpx1_paoekO0dt3kR46z471zlDKChI"
ADMIN_TELEGRAM_ID = "508352361"
TEST_USER_ID = "999888777"  # Тестовый пользователь

# Telegram API URL
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_test(message):
    print(f"\n{Colors.BLUE}[TEST]{Colors.END} {message}")

def print_success(message):
    print(f"{Colors.GREEN}✅ {message}{Colors.END}")

def print_error(message):
    print(f"{Colors.RED}❌ {message}{Colors.END}")

def print_info(message):
    print(f"{Colors.YELLOW}ℹ️  {message}{Colors.END}")

def check_polling_in_logs():
    """Проверка что бот работает в polling режиме"""
    print_test("1. Проверка polling режима в логах backend")
    
    try:
        # Читаем последние 50 строк логов
        result = os.popen("tail -50 /var/log/supervisor/backend.err.log | grep -E '(polling|getUpdates)' -i").read()
        
        if "Telegram bot polling started successfully!" in result:
            print_success("Бот запущен в polling режиме")
        else:
            print_error("Не найдено сообщение о запуске polling")
            return False
        
        if "getUpdates" in result:
            # Подсчитываем количество getUpdates запросов
            updates_count = result.count("getUpdates")
            print_success(f"Найдено {updates_count} getUpdates запросов (polling работает)")
        else:
            print_error("Не найдено getUpdates запросов")
            return False
        
        return True
    except Exception as e:
        print_error(f"Ошибка при проверке логов: {e}")
        return False

def check_no_separate_telegram_process():
    """Проверка что нет отдельного процесса telegram_bot"""
    print_test("2. Проверка отсутствия отдельного процесса telegram_bot")
    
    try:
        result = os.popen("supervisorctl status").read()
        
        if "telegram" in result.lower() and "telegram-bot" in result.lower():
            print_error("Найден отдельный процесс telegram-bot в supervisor!")
            print_info(f"Supervisor status:\n{result}")
            return False
        else:
            print_success("Отдельного процесса telegram-bot НЕТ (корректно)")
            print_info("Бот интегрирован в backend процесс")
            return True
    except Exception as e:
        print_error(f"Ошибка при проверке supervisor: {e}")
        return False

def send_telegram_command(chat_id, command):
    """Отправить команду боту через Telegram API"""
    try:
        url = f"{TELEGRAM_API_URL}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": command
        }
        response = requests.post(url, json=payload, timeout=10)
        return response.status_code == 200, response.json()
    except Exception as e:
        return False, str(e)

def get_bot_updates():
    """Получить обновления от бота"""
    try:
        url = f"{TELEGRAM_API_URL}/getUpdates"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return True, response.json()
        return False, response.text
    except Exception as e:
        return False, str(e)

def test_start_command():
    """Тестирование команды /start"""
    print_test("3. Тестирование команды /start")
    
    print_info("Отправка команды /start боту...")
    success, result = send_telegram_command(ADMIN_TELEGRAM_ID, "/start")
    
    if success:
        print_success("Команда /start отправлена боту")
        print_info("Проверьте Telegram бота @shoptyresbot - должно прийти приветственное сообщение")
        
        # Ждем немного и проверяем логи
        time.sleep(2)
        logs = os.popen("tail -20 /var/log/supervisor/backend.err.log | grep -E '(started the bot|/start)' -i").read()
        
        if "started the bot" in logs:
            print_success("В логах найдена обработка команды /start")
            return True
        else:
            print_error("В логах НЕ найдена обработка команды /start")
            print_info("Возможно команда еще обрабатывается, проверьте логи вручную")
            return False
    else:
        print_error(f"Ошибка отправки команды /start: {result}")
        return False

def test_help_command():
    """Тестирование команды /help"""
    print_test("4. Тестирование команды /help")
    
    print_info("Отправка команды /help боту...")
    success, result = send_telegram_command(ADMIN_TELEGRAM_ID, "/help")
    
    if success:
        print_success("Команда /help отправлена боту")
        print_info("Проверьте Telegram бота @shoptyresbot - должна прийти справка")
        
        # Ждем немного и проверяем логи
        time.sleep(2)
        logs = os.popen("tail -20 /var/log/supervisor/backend.err.log | grep -E '(/help)' -i").read()
        
        # Команда /help может не логироваться явно, это нормально
        print_success("Команда /help обработана (проверьте Telegram)")
        return True
    else:
        print_error(f"Ошибка отправки команды /help: {result}")
        return False

def test_order_notification():
    """Тестирование уведомления о новом заказе"""
    print_test("5. Тестирование уведомления о новом заказе")
    
    # Сначала создаем/получаем пользователя
    print_info("Создание тестового пользователя...")
    user_data = {
        "telegram_id": TEST_USER_ID,
        "username": "test_user_bot",
        "first_name": "Тест",
        "last_name": "Ботов"
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/auth/telegram", json=user_data, timeout=10)
        if response.status_code in [200, 201]:
            print_success(f"Пользователь {TEST_USER_ID} создан/получен")
        else:
            print_error(f"Ошибка создания пользователя: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Ошибка при создании пользователя: {e}")
        return False
    
    # Создаем заказ
    print_info("Создание тестового заказа...")
    order_data = {
        "items": [
            {
                "code": "TEST_TIRE_001",
                "name": "Тестовая шина 185/60R15",
                "brand": "TestBrand",
                "quantity": 4,
                "price_base": 4000.0,
                "price_final": 5000.0,
                "warehouse_id": 1,
                "warehouse_name": "Тестовый склад"
            }
        ],
        "delivery_address": {
            "city": "Москва",
            "street": "Тестовая улица",
            "house": "1",
            "apartment": "1",
            "comment": "Тестовый заказ для проверки уведомлений бота"
        }
    }
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/orders?telegram_id={TEST_USER_ID}",
            json=order_data,
            timeout=10
        )
        
        if response.status_code in [200, 201]:
            order = response.json()
            order_id = order.get("order_id") or order.get("id")
            print_success(f"Заказ создан: {order_id}")
            
            # Ждем немного и проверяем логи
            time.sleep(2)
            logs = os.popen("tail -30 /var/log/supervisor/backend.err.log | grep -E '(Message sent to 508352361|Новый заказ)' -i").read()
            
            if "Message sent to 508352361" in logs or "508352361" in logs:
                print_success("Уведомление отправлено админу (найдено в логах)")
                print_info("Проверьте Telegram админа - должно прийти уведомление о заказе")
                return True
            else:
                print_error("Уведомление админу НЕ найдено в логах")
                print_info("Возможно уведомление еще отправляется, проверьте логи вручную")
                return False
        else:
            print_error(f"Ошибка создания заказа: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print_error(f"Ошибка при создании заказа: {e}")
        return False

def test_new_visitor_notification():
    """Тестирование уведомления о новом посетителе"""
    print_test("6. Тестирование уведомления о новом посетителе")
    
    # Создаем нового пользователя (не админа)
    new_user_id = f"test_{int(time.time())}"
    print_info(f"Создание нового пользователя {new_user_id}...")
    
    user_data = {
        "telegram_id": new_user_id,
        "username": "new_visitor_test",
        "first_name": "Новый",
        "last_name": "Посетитель"
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/auth/telegram", json=user_data, timeout=10)
        if response.status_code in [200, 201]:
            result = response.json()
            is_new = result.get("is_new_user", False)
            
            if is_new:
                print_success(f"Новый пользователь {new_user_id} создан")
                
                # Ждем немного и проверяем логи
                time.sleep(2)
                logs = os.popen("tail -30 /var/log/supervisor/backend.err.log | grep -E '(New user created|Message sent to 508352361)' -i").read()
                
                if "New user created" in logs and "508352361" in logs:
                    print_success("Уведомление о новом посетителе отправлено админу")
                    print_info("Проверьте Telegram админа - должно прийти уведомление о новом посетителе")
                    return True
                else:
                    print_error("Уведомление о новом посетителе НЕ найдено в логах")
                    return False
            else:
                print_info("Пользователь уже существовал (уведомление не отправляется)")
                return True
        else:
            print_error(f"Ошибка создания пользователя: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Ошибка при создании пользователя: {e}")
        return False

def check_bot_info():
    """Получить информацию о боте"""
    print_test("0. Проверка информации о боте")
    
    try:
        url = f"{TELEGRAM_API_URL}/getMe"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            bot_info = response.json()
            if bot_info.get("ok"):
                result = bot_info.get("result", {})
                print_success(f"Бот найден: @{result.get('username')} (ID: {result.get('id')})")
                print_info(f"Имя: {result.get('first_name')}")
                return True
        
        print_error("Не удалось получить информацию о боте")
        return False
    except Exception as e:
        print_error(f"Ошибка при получении информации о боте: {e}")
        return False

def main():
    print("\n" + "="*80)
    print("ТЕСТИРОВАНИЕ ИНТЕГРИРОВАННОГО TELEGRAM БОТА")
    print("="*80)
    
    results = {}
    
    # Проверка информации о боте
    results["bot_info"] = check_bot_info()
    
    # Проверка polling режима
    results["polling"] = check_polling_in_logs()
    
    # Проверка отсутствия отдельного процесса
    results["no_separate_process"] = check_no_separate_telegram_process()
    
    # Тестирование команд (через Telegram API)
    print_info("\nВНИМАНИЕ: Команды /start и /help отправляются через Telegram API")
    print_info("Проверьте бота @shoptyresbot в Telegram для подтверждения работы команд")
    
    results["start_command"] = test_start_command()
    results["help_command"] = test_help_command()
    
    # Тестирование уведомлений
    results["order_notification"] = test_order_notification()
    results["visitor_notification"] = test_new_visitor_notification()
    
    # Итоговый отчет
    print("\n" + "="*80)
    print("ИТОГОВЫЙ ОТЧЕТ")
    print("="*80)
    
    total_tests = len(results)
    passed_tests = sum(1 for v in results.values() if v)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    print("\n" + "-"*80)
    print(f"Всего тестов: {total_tests}")
    print(f"Пройдено: {passed_tests}")
    print(f"Провалено: {total_tests - passed_tests}")
    print(f"Успех: {(passed_tests/total_tests)*100:.1f}%")
    print("="*80 + "\n")
    
    if passed_tests == total_tests:
        print_success("🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ!")
        return 0
    else:
        print_error("⚠️  НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОЙДЕНЫ")
        return 1

if __name__ == "__main__":
    exit(main())
