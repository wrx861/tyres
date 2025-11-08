#!/usr/bin/env python3
"""
Скрипт для удаления дубликатов пользователей из MongoDB

ВАЖНО: Для каждого telegram_id оставляет самую РАННЮЮ запись (по created_at),
остальные дубликаты удаляет.
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from datetime import datetime

# Загружаем переменные окружения
load_dotenv('/opt/tyres-app/backend/.env')

MONGO_URL = os.environ['MONGO_URL']
DB_NAME = os.environ['DB_NAME']

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

def print_success(message):
    print(f"{Colors.GREEN}✅ {message}{Colors.RESET}")

def print_error(message):
    print(f"{Colors.RED}❌ {message}{Colors.RESET}")

def print_warning(message):
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.RESET}")

def print_info(message):
    print(f"{Colors.BLUE}ℹ️  {message}{Colors.RESET}")

async def find_duplicates():
    """Найти все дубликаты telegram_id"""
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    print_info("Поиск дубликатов в базе данных...")
    
    pipeline = [
        {
            "$group": {
                "_id": "$telegram_id",
                "count": {"$sum": 1},
                "docs": {"$push": {
                    "telegram_id": "$telegram_id",
                    "first_name": "$first_name",
                    "last_name": "$last_name",
                    "username": "$username",
                    "created_at": "$created_at",
                    "is_admin": "$is_admin"
                }}
            }
        },
        {
            "$match": {"count": {"$gt": 1}}
        },
        {
            "$sort": {"count": -1}
        }
    ]
    
    duplicates = await db.users.aggregate(pipeline).to_list(length=None)
    client.close()
    
    return duplicates

async def remove_duplicates(dry_run=True):
    """
    Удалить дубликаты, оставив самую раннюю запись для каждого telegram_id
    
    Args:
        dry_run (bool): Если True, только показывает что будет удалено без фактического удаления
    """
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    duplicates = await find_duplicates()
    
    if not duplicates:
        print_success("Дубликатов не найдено! База данных чистая.")
        client.close()
        return
    
    print_warning(f"Найдено {len(duplicates)} групп дубликатов:")
    print()
    
    total_to_delete = 0
    
    for dup in duplicates:
        telegram_id = dup['_id']
        count = dup['count']
        docs = dup['docs']
        
        print(f"\n{'='*80}")
        print(f"Telegram ID: {telegram_id}")
        print(f"Количество дубликатов: {count}")
        print("-" * 80)
        
        # Сортируем по created_at, чтобы найти самую раннюю запись
        sorted_docs = sorted(docs, key=lambda x: x.get('created_at', '9999-99-99'))
        
        # Первая запись - самая ранняя, её оставляем
        keep_doc = sorted_docs[0]
        delete_docs = sorted_docs[1:]
        
        print_success(f"ОСТАВЛЯЕМ (самая ранняя):")
        print(f"  Имя: {keep_doc.get('first_name', 'N/A')} {keep_doc.get('last_name', 'N/A')}")
        print(f"  Username: @{keep_doc.get('username', 'N/A')}")
        print(f"  Создан: {keep_doc.get('created_at', 'N/A')}")
        print(f"  Админ: {keep_doc.get('is_admin', False)}")
        
        print()
        print_error(f"УДАЛЯЕМ ({len(delete_docs)} дубликатов):")
        
        for idx, doc in enumerate(delete_docs, 1):
            print(f"  {idx}. Имя: {doc.get('first_name', 'N/A')} {doc.get('last_name', 'N/A')}")
            print(f"     Username: @{doc.get('username', 'N/A')}")
            print(f"     Создан: {doc.get('created_at', 'N/A')}")
            total_to_delete += 1
    
    print()
    print("="*80)
    print_warning(f"ИТОГО: Будет удалено {total_to_delete} дубликатов из {sum(d['count'] for d in duplicates)} записей")
    print("="*80)
    
    if dry_run:
        print()
        print_info("Это был пробный запуск (DRY RUN). Ничего не удалено.")
        print_info("Чтобы удалить дубликаты, запустите скрипт с параметром --confirm")
    else:
        print()
        print_warning("Начинаем удаление дубликатов...")
        
        deleted_count = 0
        
        for dup in duplicates:
            telegram_id = dup['_id']
            docs = dup['docs']
            
            # Сортируем по created_at
            sorted_docs = sorted(docs, key=lambda x: x.get('created_at', '9999-99-99'))
            
            # Оставляем самую раннюю запись
            keep_created_at = sorted_docs[0].get('created_at')
            
            # Удаляем все записи КРОМЕ самой ранней
            # Используем created_at для идентификации, так как _id у нас нет
            result = await db.users.delete_many({
                "telegram_id": telegram_id,
                "created_at": {"$ne": keep_created_at}
            })
            
            deleted_count += result.deleted_count
            print_info(f"Telegram ID {telegram_id}: удалено {result.deleted_count} дубликатов")
        
        print()
        print_success(f"Успешно удалено {deleted_count} дубликатов!")
        
        # Проверяем что дубликатов больше нет
        remaining_duplicates = await find_duplicates()
        if not remaining_duplicates:
            print_success("Проверка: дубликатов больше нет! ✨")
        else:
            print_error(f"Внимание: Остались дубликаты! Количество: {len(remaining_duplicates)}")
    
    client.close()

async def main():
    import sys
    
    print()
    print(f"{Colors.BLUE}{'='*80}{Colors.RESET}")
    print(f"{Colors.BLUE}Скрипт удаления дубликатов пользователей{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*80}{Colors.RESET}")
    print()
    
    # Проверяем параметры запуска
    confirm = "--confirm" in sys.argv or "-y" in sys.argv
    
    if confirm:
        print_warning("РЕЖИМ: Реальное удаление (--confirm)")
        print()
        response = input("Вы уверены что хотите удалить дубликаты? (yes/no): ")
        if response.lower() != 'yes':
            print_info("Отменено пользователем")
            return
    else:
        print_info("РЕЖИМ: Пробный запуск (DRY RUN)")
        print_info("Для реального удаления запустите с параметром --confirm")
    
    print()
    await remove_duplicates(dry_run=not confirm)
    print()

if __name__ == "__main__":
    asyncio.run(main())
