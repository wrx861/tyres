from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
import logging
import os

from services.fourthchki_client import get_fourthchki_client
from services.mock_data import (
    generate_mock_tires, 
    generate_mock_disks, 
    MOCK_WAREHOUSES
)
from services.brands_data import TIRE_BRANDS, DISK_BRANDS

logger = logging.getLogger(__name__)

def use_mock_data() -> bool:
    """Проверяем, используем ли mock данные"""
    return os.environ.get('USE_MOCK_DATA', 'false').lower() == 'true'

router = APIRouter(prefix="/products", tags=["products"])

def get_db():
    from server import db
    return db

def apply_markup(price: float, markup_percentage: float) -> float:
    """Применить наценку к цене"""
    return round(price * (1 + markup_percentage / 100), 2)

async def get_markup_percentage(db: AsyncIOMotorDatabase) -> float:
    """Получить текущий процент наценки"""
    settings = await db.settings.find_one({}, {"_id": 0})
    if settings:
        return settings.get('markup_percentage', 15.0)
    return float(os.environ.get('DEFAULT_MARKUP_PERCENTAGE', '15'))

@router.get("/tires/search")
async def search_tires(
    width: Optional[int] = Query(None, description="Ширина шины (например, 185)"),
    height: Optional[int] = Query(None, description="Высота профиля (например, 60)"),
    diameter: Optional[int] = Query(None, description="Диаметр (например, 15)"),
    season: Optional[str] = Query(None, description="Сезон: summer, winter, all-season"),
    brand: Optional[str] = Query(None, description="Бренд"),
    city: Optional[str] = Query(None, description="Город (для фильтрации по складам)"),
    sort_by: Optional[str] = Query(None, description="Сортировка: price_asc (дешевле), price_desc (дороже)"),
    page: int = Query(0, ge=0, description="Номер страницы"),
    page_size: int = Query(2000, ge=1, le=2000, description="Размер страницы"),
    telegram_id: Optional[str] = Query(None, description="Telegram ID пользователя для логирования"),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Поиск шин по параметрам
    """
    try:
        markup = await get_markup_percentage(db)
        
        season_map = {
            'summer': 's',
            'winter': 'w',
            'all-season': 'u'
        }
        
        season_list = None
        if season and season in season_map:
            season_list = [season_map[season]]
        
        if use_mock_data():
            logger.info("Using MOCK data for tires search")
            response = generate_mock_tires(
                season=season_list,
                width=width,
                height=height,
                diameter=diameter,
                brand=brand,
                page=page,
                page_size=page_size
            )
        else:
            client = get_fourthchki_client()
            brand_list = [brand] if brand else None
            
            response = client.search_tires(
                season_list=season_list,
                width_min=width,
                width_max=width,
                height_min=height,
                height_max=height,
                diameter_min=diameter,
                diameter_max=diameter,
                brand_list=brand_list,
                page=page,
                page_size=page_size
            )
        
        # Check if there's a meaningful error (not just empty error structure)
        error = response.get('error')
        if error and (error.get('code') or error.get('comment') or error.get('Message')):
            error_msg = error.get('Message') or error.get('comment') or f"Error code: {error.get('code')}"
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Extract tire data from nested structure
        tire_data = []
        price_rest_list = response.get('price_rest_list', {})
        if isinstance(price_rest_list, dict) and 'TyrePriceRest' in price_rest_list:
            tire_data = price_rest_list['TyrePriceRest']
        elif isinstance(price_rest_list, list):
            tire_data = price_rest_list
        
        # Маппинг городов к ID складов
        CITY_WAREHOUSES = {
            'Тюмень': [42],
            'Сургут': [525, 1948, 1131, 1694, 1882, 1456],
            'Лянтор': [1477],
            'Нефтеюганск': [1212, 459, 1824],
            'Белый Яр': [1997],
            'Екатеринбург': [1431],
            'Челябинск': [2017],
            'Москва': [1, 232],
            'Санкт-Петербург': [1655]
        }
        TYUMEN_WAREHOUSE_ID = 42  # ID склада Тюмень по умолчанию
        
        # Определяем приоритетные склады на основе выбранного города
        priority_warehouses = CITY_WAREHOUSES.get(city, [TYUMEN_WAREHOUSE_ID]) if city else [TYUMEN_WAREHOUSE_ID]
        
        filtered_tire_data = []
        
        for item in tire_data:
            # Parse tire size from name (e.g., "185/60R15")
            import re
            name = item.get('name', '')
            size_match = re.match(r'(\d+)/(\d+)R(\d+)', name)
            if size_match:
                item['width'] = int(size_match.group(1))
                item['height'] = int(size_match.group(2))
                item['diameter'] = int(size_match.group(3))
            
            # Extract brand and model if not present
            if not item.get('brand'):
                item['brand'] = item.get('marka', 'Неизвестно')
            
            
            # Extract image URLs
            item['img_small'] = item.get('img_small', '')
            item['img_big_my'] = item.get('img_big_my', '')
            item['img_big_pish'] = item.get('img_big_pish', '')
            # Fallback: if img_big_my is empty, use img_big_pish
            if not item['img_big_my']:
                item['img_big_my'] = item['img_big_pish']
            # Find the best price from warehouse data
            if item.get('whpr') and item['whpr'].get('wh_price_rest'):
                warehouses = item['whpr']['wh_price_rest']
                if warehouses:
                    # ФИЛЬТРАЦИЯ: ищем склады только из выбранного города
                    city_warehouses = [w for w in warehouses if w.get('wrh') in priority_warehouses]
                    
                    # Если в выбранном городе нет товара, пропускаем
                    if not city_warehouses and city:
                        continue
                    
                    # Выбираем лучший склад (из города или любой)
                    best_warehouse = city_warehouses[0] if city_warehouses else warehouses[0]
                    
                    best_price = float(best_warehouse.get('price', 0))
                    item['price_original'] = best_price
                    item['price'] = apply_markup(best_price, markup)
                    
                    # Extract warehouse info for display
                    item['rest'] = best_warehouse.get('rest', 0)
                    wrh_id = best_warehouse.get('wrh', 0)
                    item['warehouse_name'] = f'Склад {wrh_id}'
                    item['warehouse_id'] = wrh_id
                    
                    # Сохраняем все склады для отображения (опционально)
                    item['all_warehouses'] = warehouses
                    
                    filtered_tire_data.append(item)
        
        # Заменяем tire_data на отфильтрованный список
        tire_data = filtered_tire_data
        
        # Сортировка по цене
        if sort_by == 'price_asc':
            tire_data.sort(key=lambda x: x.get('price', 0))
        elif sort_by == 'price_desc':
            tire_data.sort(key=lambda x: x.get('price', 0), reverse=True)
        
        # Extract warehouse data
        warehouses = []
        warehouse_logistics = response.get('warehouseLogistics', {})
        if isinstance(warehouse_logistics, dict) and 'WarehouseLogistic' in warehouse_logistics:
            warehouses = warehouse_logistics['WarehouseLogistic']
        elif isinstance(warehouse_logistics, list):
            warehouses = warehouse_logistics
        
        # Логируем активность поиска шин
        if telegram_id:
            from datetime import datetime, timezone
            user = await db.users.find_one({"telegram_id": telegram_id})
            # Используем username или first_name в качестве идентификатора
            user_display = None
            if user:
                user_display = user.get("username") or user.get("first_name") or f"User_{telegram_id[-4:]}"
            activity_log = {
                "telegram_id": telegram_id,
                "username": user_display,
                "activity_type": "tire_search",
                "search_params": {
                    "width": width,
                    "height": height,
                    "diameter": diameter,
                    "season": season,
                    "brand": brand,
                    "city": city
                },
                "result_count": len(tire_data),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            await db.activity_logs.insert_one(activity_log)
        
        return {
            "success": True,
            "data": tire_data,
            "total_pages": response.get('totalPages', 0),
            "warehouses": warehouses,
            "currency": response.get('currencyRate', {}),
            "markup_percentage": markup,
            "mock_mode": use_mock_data()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error searching tires: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to search tires: {str(e)}")

@router.get("/disks/search")
async def search_disks(
    diameter: Optional[int] = Query(None, description="Диаметр (например, 15)"),
    width: Optional[float] = Query(None, description="Ширина обода (например, 6.5)"),
    brand: Optional[str] = Query(None, description="Бренд"),
    pcd: Optional[str] = Query(None, description="PCD - количество отверстий и диаметр (например, 5x114.3)"),
    et_min: Optional[float] = Query(None, description="Вылет минимальный (например, 35)"),
    et_max: Optional[float] = Query(None, description="Вылет максимальный (например, 45)"),
    dia_min: Optional[float] = Query(None, description="Диаметр ступичного отверстия мин (например, 60.1)"),
    dia_max: Optional[float] = Query(None, description="Диаметр ступичного отверстия макс (например, 73.1)"),
    color: Optional[str] = Query(None, description="Цвет диска"),
    disk_type: Optional[int] = Query(None, description="Тип диска: 0-Литой, 1-Штампованный, 2-Кованный"),
    city: Optional[str] = Query(None, description="Город (для фильтрации по складам)"),
    sort_by: Optional[str] = Query(None, description="Сортировка: price_asc (дешевле), price_desc (дороже)"),
    page: int = Query(0, ge=0, description="Номер страницы"),
    page_size: int = Query(50, ge=1, le=200, description="Размер страницы"),
    telegram_id: Optional[str] = Query(None, description="Telegram ID пользователя для логирования"),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Поиск дисков по параметрам
    """
    try:
        markup = await get_markup_percentage(db)
        
        if use_mock_data():
            logger.info("Using MOCK data for disks search")
            response = generate_mock_disks(
                diameter=diameter,
                width=width,
                brand=brand,
                page=page,
                page_size=page_size
            )
        else:
            client = get_fourthchki_client()
            brand_list = [brand] if brand else None
            color_list = [color] if color else None
            type_list = [disk_type] if disk_type is not None else None
            
            # Parse PCD (e.g., "5x114.3" -> bolts_count=5, bolts_spacing=114.3)
            bolts_count = None
            bolts_spacing = None
            if pcd:
                import re
                pcd_match = re.match(r'(\d+)x([\d.]+)', pcd)
                if pcd_match:
                    bolts_count = int(pcd_match.group(1))
                    bolts_spacing = float(pcd_match.group(2))
            
            response = client.search_disks(
                diameter_min=diameter,
                diameter_max=diameter,
                width_min=width,
                width_max=width,
                brand_list=brand_list,
                bolts_count_min=bolts_count,
                bolts_count_max=bolts_count,
                bolts_spacing_min=bolts_spacing,
                bolts_spacing_max=bolts_spacing,
                et_min=et_min,
                et_max=et_max,
                dia_min=dia_min,
                dia_max=dia_max,
                color_list=color_list,
                type_list=type_list,
                page=page,
                page_size=page_size
            )
        
        # Check if there's a meaningful error (not just empty error structure)
        error = response.get('error')
        if error and (error.get('code') or error.get('comment') or error.get('Message')):
            error_msg = error.get('Message') or error.get('comment') or f"Error code: {error.get('code')}"
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Extract disk data from nested structure
        disk_data = []
        price_rest_list = response.get('price_rest_list', {})
        if isinstance(price_rest_list, dict) and 'DiskPriceRest' in price_rest_list:
            disk_data = price_rest_list['DiskPriceRest']
        elif isinstance(price_rest_list, dict) and 'TyrePriceRest' in price_rest_list:
            # Sometimes disks might use the same structure as tires
            disk_data = price_rest_list['TyrePriceRest']
        elif isinstance(price_rest_list, list):
            disk_data = price_rest_list
        
        # Маппинг городов к ID складов
        CITY_WAREHOUSES = {
            'Тюмень': [42],
            'Сургут': [525, 1948, 1131, 1694, 1882, 1456],
            'Лянтор': [1477],
            'Нефтеюганск': [1212, 459, 1824],
            'Белый Яр': [1997],
            'Екатеринбург': [1431],
            'Челябинск': [2017],
            'Москва': [1, 232],
            'Санкт-Петербург': [1655]
        }
        TYUMEN_WAREHOUSE_ID = 42  # ID склада Тюмень по умолчанию
        
        # Определяем приоритетные склады на основе выбранного города
        priority_warehouses = CITY_WAREHOUSES.get(city, [TYUMEN_WAREHOUSE_ID]) if city else [TYUMEN_WAREHOUSE_ID]
        
        filtered_disk_data = []
        
        for item in disk_data:
            # Parse disk size from name (e.g., "7x16 5x114.3 ET45 DIA60.1")
            import re
            name = item.get('name', '')
            
            # Pattern for disk size: WidthxDiameter (первое вхождение)
            size_match = re.search(r'(\d+\.?\d*)x(\d+)', name)
            if size_match:
                item['width'] = float(size_match.group(1))
                item['diameter'] = int(size_match.group(2))
                
                # Удаляем найденный размер из строки для дальнейшего парсинга PCD
                # Это предотвратит захват размера как PCD
                size_str = size_match.group(0)
                name_without_size = name.replace(size_str, '', 1)
            else:
                name_without_size = name
            
            # Parse PCD (разболтовка): 5x114.3 или 4x100
            # Ищем второе вхождение паттерна NxN (после удаления размера)
            pcd_match = re.search(r'(\d)x([\d.]+)', name_without_size)
            if pcd_match:
                item['pcd'] = f"{pcd_match.group(1)}x{pcd_match.group(2)}"
            
            # Parse ET (вылет): ET45 или ET-5
            et_match = re.search(r'ET[:\s]*(-?\d+\.?\d*)', name, re.IGNORECASE)
            if et_match:
                item['et'] = et_match.group(1)
            
            # Parse DIA (диаметр ступичного отверстия): DIA60.1 или d60.1
            dia_match = re.search(r'(?:DIA|d)[:\s]*([\d.]+)', name, re.IGNORECASE)
            if dia_match:
                item['dia'] = dia_match.group(1)
            
            # Extract brand and model if not present
            if not item.get('brand'):
                item['brand'] = item.get('marka', 'Неизвестно')
            
            
            # Extract image URLs
            item['img_small'] = item.get('img_small', '')
            item['img_big_my'] = item.get('img_big_my', '')
            item['img_big_pish'] = item.get('img_big_pish', '')
            # Fallback: if img_big_my is empty, use img_big_pish
            if not item['img_big_my']:
                item['img_big_my'] = item['img_big_pish']
            # Find the best price from warehouse data
            if item.get('whpr') and item['whpr'].get('wh_price_rest'):
                warehouses = item['whpr']['wh_price_rest']
                if warehouses:
                    # ФИЛЬТРАЦИЯ: ищем склады только из выбранного города
                    city_warehouses = [w for w in warehouses if w.get('wrh') in priority_warehouses]
                    
                    # Если в выбранном городе нет товара, пропускаем
                    if not city_warehouses and city:
                        continue
                    
                    # Выбираем лучший склад (из города или любой)
                    best_warehouse = city_warehouses[0] if city_warehouses else warehouses[0]
                    
                    best_price = float(best_warehouse.get('price', 0))
                    item['price_original'] = best_price
                    item['price'] = apply_markup(best_price, markup)
                    
                    # Extract warehouse info for display
                    item['rest'] = best_warehouse.get('rest', 0)
                    wrh_id = best_warehouse.get('wrh', 0)
                    item['warehouse_name'] = f'Склад {wrh_id}'
                    item['warehouse_id'] = wrh_id
                    
                    # Сохраняем все склады для отображения (опционально)
                    item['all_warehouses'] = warehouses
                    
                    filtered_disk_data.append(item)
        
        # Заменяем disk_data на отфильтрованный список
        disk_data = filtered_disk_data
        
        # Сортировка по цене
        if sort_by == 'price_asc':
            disk_data.sort(key=lambda x: x.get('price', 0))
        elif sort_by == 'price_desc':
            disk_data.sort(key=lambda x: x.get('price', 0), reverse=True)
        
        # Extract warehouse data
        warehouses = []
        warehouse_logistics = response.get('warehouseLogistics', {})
        if isinstance(warehouse_logistics, dict) and 'WarehouseLogistic' in warehouse_logistics:
            warehouses = warehouse_logistics['WarehouseLogistic']
        elif isinstance(warehouse_logistics, list):
            warehouses = warehouse_logistics
        
        # Логируем активность поиска дисков
        if telegram_id:
            from datetime import datetime, timezone
            user = await db.users.find_one({"telegram_id": telegram_id})
            # Используем username или first_name в качестве идентификатора
            user_display = None
            if user:
                user_display = user.get("username") or user.get("first_name") or f"User_{telegram_id[-4:]}"
            activity_log = {
                "telegram_id": telegram_id,
                "username": user_display,
                "activity_type": "disk_search",
                "search_params": {
                    "diameter": diameter,
                    "width": width,
                    "brand": brand,
                    "pcd": pcd,
                    "et_min": et_min,
                    "et_max": et_max,
                    "dia_min": dia_min,
                    "dia_max": dia_max,
                    "color": color,
                    "disk_type": disk_type,
                    "city": city
                },
                "result_count": len(disk_data),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            await db.activity_logs.insert_one(activity_log)
        
        return {
            "success": True,
            "data": disk_data,
            "total_pages": response.get('totalPages', 0),
            "warehouses": warehouses,
            "currency": response.get('currencyRate', {}),
            "markup_percentage": markup,
            "mock_mode": use_mock_data()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error searching disks: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to search disks: {str(e)}")

@router.get("/info/{code}")
async def get_product_info(
    code: str,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Получить подробную информацию о товаре по коду
    """
    try:
        markup = await get_markup_percentage(db)
        
        if use_mock_data():
            # В mock режиме возвращаем фейковую информацию
            return {
                "success": True,
                "data": {
                    "code": code,
                    "brand": "Michelin",
                    "model": "X-Ice North 4",
                    "price": apply_markup(8500, markup),
                    "price_original": 8500,
                    "rest": 12,
                },
                "markup_percentage": markup,
                "mock_mode": True
            }
        
        client = get_fourthchki_client()
        response = client.get_goods_info(code)
        
        # Check if there's a meaningful error (not just empty error structure)
        error = response.get('error')
        if error and (error.get('code') or error.get('comment') or error.get('Message')):
            error_msg = error.get('Message') or error.get('comment') or f"Error code: {error.get('code')}"
            raise HTTPException(status_code=400, detail=error_msg)
        
        if response.get('price'):
            original_price = float(response['price'])
            response['price_original'] = original_price
            response['price'] = apply_markup(original_price, markup)
        
        return {
            "success": True,
            "data": response,
            "markup_percentage": markup,
            "mock_mode": False
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting product info: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get product info: {str(e)}")

@router.get("/warehouses")
async def get_warehouses():
    """
    Получить список доступных складов
    """
    try:
        if use_mock_data():
            return {
                "success": True,
                "data": MOCK_WAREHOUSES,
                "mock_mode": True
            }
        
        client = get_fourthchki_client()
        response = client.get_warehouses()
        
        # Check if there's a meaningful error (not just empty error structure)
        error = response.get('error')
        if error and (error.get('code') or error.get('comment') or error.get('Message')):
            error_msg = error.get('Message') or error.get('comment') or f"Error code: {error.get('code')}"
            raise HTTPException(status_code=400, detail=error_msg)
        
        return {
            "success": True,
            "data": response.get('warehouses', []),
            "mock_mode": False
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting warehouses: {e}")
        raise HTTPException(status_code=500, detail="Failed to get warehouses")


@router.get("/brands/tires")
async def get_tire_brands(
    telegram_id: Optional[str] = Query(None, description="Telegram ID пользователя")
):
    """
    Получить список брендов шин
    Возвращает статический список брендов с сайта 4tochki.ru
    """
    return {
        "success": True,
        "brands": TIRE_BRANDS,
        "total": len(TIRE_BRANDS)
    }

@router.get("/brands/disks")
async def get_disk_brands(
    telegram_id: Optional[str] = Query(None, description="Telegram ID пользователя")
):
    """
    Получить список брендов дисков
    Возвращает статический список брендов с сайта 4tochki.ru
    """
    return {
        "success": True,
        "brands": DISK_BRANDS,
        "total": len(DISK_BRANDS)
    }

