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
    page: int = Query(0, ge=0, description="Номер страницы"),
    page_size: int = Query(50, ge=1, le=200, description="Размер страницы"),
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
        
        # Extract warehouse data
        warehouses = []
        warehouse_logistics = response.get('warehouseLogistics', {})
        if isinstance(warehouse_logistics, dict) and 'WarehouseLogistic' in warehouse_logistics:
            warehouses = warehouse_logistics['WarehouseLogistic']
        elif isinstance(warehouse_logistics, list):
            warehouses = warehouse_logistics
        
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
    width: Optional[float] = Query(None, description="Ширина (например, 6.5)"),
    brand: Optional[str] = Query(None, description="Бренд"),
    city: Optional[str] = Query(None, description="Город (для фильтрации по складам)"),
    page: int = Query(0, ge=0, description="Номер страницы"),
    page_size: int = Query(50, ge=1, le=200, description="Размер страницы"),
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
            
            response = client.search_disks(
                diameter_min=diameter,
                diameter_max=diameter,
                width_min=width,
                width_max=width,
                brand_list=brand_list,
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
        
        for item in disk_data:
            # Parse disk size from name (e.g., "7x16 5x114.3 ET45")
            import re
            name = item.get('name', '')
            # Pattern for disk size: WidthxDiameter
            size_match = re.search(r'(\d+\.?\d*)x(\d+)', name)
            if size_match:
                item['width'] = float(size_match.group(1))
                item['diameter'] = int(size_match.group(2))
            
            # Extract brand and model if not present
            if not item.get('brand'):
                item['brand'] = item.get('marka', 'Неизвестно')
            
            # Find the best price from warehouse data
            if item.get('whpr') and item['whpr'].get('wh_price_rest'):
                warehouses = item['whpr']['wh_price_rest']
                if warehouses:
                    # Приоритизируем склады из выбранного города
                    priority_warehouse = next((w for w in warehouses if w.get('wrh') in priority_warehouses), None)
                    best_warehouse = priority_warehouse if priority_warehouse else warehouses[0]
                    
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
        
        # Extract warehouse data
        warehouses = []
        warehouse_logistics = response.get('warehouseLogistics', {})
        if isinstance(warehouse_logistics, dict) and 'WarehouseLogistic' in warehouse_logistics:
            warehouses = warehouse_logistics['WarehouseLogistic']
        elif isinstance(warehouse_logistics, list):
            warehouses = warehouse_logistics
        
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
