from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
import logging
import os

from services.fourthchki_client import get_fourthchki_client
from services.mock_data import (
    MOCK_CAR_BRANDS,
    MOCK_CAR_MODELS,
    MOCK_YEARS,
    MOCK_MODIFICATIONS,
    generate_mock_goods_by_car
)

logger = logging.getLogger(__name__)

def use_mock_data() -> bool:
    """Проверяем, используем ли mock данные"""
    return os.environ.get('USE_MOCK_DATA', 'false').lower() == 'true'

router = APIRouter(prefix="/cars", tags=["cars"])

def get_db():
    from server import db
    return db

def apply_markup(price: float, markup_percentage: float) -> float:
    return round(price * (1 + markup_percentage / 100), 2)

async def get_markup_percentage(db: AsyncIOMotorDatabase) -> float:
    settings = await db.settings.find_one({}, {"_id": 0})
    if settings:
        return settings.get('markup_percentage', 15.0)
    return 15.0

@router.get("/brands")
async def get_car_brands():
    try:
        if use_mock_data():
            logger.info("Using MOCK data for car brands")
            return {
                "success": True,
                "data": MOCK_CAR_BRANDS,
                "mock_mode": True
            }
        
        client = get_fourthchki_client()
        response = client.get_car_brands()
        
        # Check if there's a meaningful error (not just empty error structure)
        error = response.get('error')
        if error and (error.get('code') or error.get('comment') or error.get('Message')):
            error_msg = error.get('Message') or error.get('comment') or f"Error code: {error.get('code')}"
            raise HTTPException(status_code=400, detail=error_msg)
        
        brands = response.get('marka_list', [])
        # Handle the case where brands is wrapped in a 'string' key
        if isinstance(brands, dict) and 'string' in brands:
            brands = brands['string']
        
        return {
            "success": True,
            "data": brands,
            "mock_mode": False
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting car brands: {e}")
        raise HTTPException(status_code=500, detail="Failed to get car brands")

@router.get("/models")
async def get_car_models(
    brand: str = Query(..., description="Марка автомобиля")
):
    try:
        if use_mock_data():
            logger.info(f"Using MOCK data for car models: {brand}")
            models = MOCK_CAR_MODELS.get(brand, ["Model 1", "Model 2", "Model 3"])
            return {
                "success": True,
                "data": models,
                "mock_mode": True
            }
        
        client = get_fourthchki_client()
        response = client.get_car_models(brand)
        
        # Check if there's a meaningful error (not just empty error structure)
        error = response.get('error')
        if error and (error.get('code') or error.get('comment') or error.get('Message')):
            error_msg = error.get('Message') or error.get('comment') or f"Error code: {error.get('code')}"
            raise HTTPException(status_code=400, detail=error_msg)
        
        models = response.get('model_list', [])
        # Handle the case where models is wrapped in a 'string' key
        if isinstance(models, dict) and 'string' in models:
            models = models['string']
        
        return {
            "success": True,
            "data": models,
            "mock_mode": False
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting car models: {e}")
        raise HTTPException(status_code=500, detail="Failed to get car models")

@router.get("/years")
async def get_car_years(
    brand: str = Query(..., description="Марка автомобиля"),
    model: str = Query(..., description="Модель автомобиля")
):
    try:
        if use_mock_data():
            logger.info(f"Using MOCK data for car years")
            return {
                "success": True,
                "data": MOCK_YEARS,
                "mock_mode": True
            }
        
        client = get_fourthchki_client()
        response = client.get_car_years(brand, model)
        
        # Check if there's a meaningful error (not just empty error structure)
        error = response.get('error')
        if error and (error.get('code') or error.get('comment') or error.get('Message')):
            error_msg = error.get('Message') or error.get('comment') or f"Error code: {error.get('code')}"
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Extract years from the correct structure
        years = []
        year_list = response.get('yearAvto_list', {})
        if isinstance(year_list, dict) and 'yearAvto' in year_list:
            year_data = year_list['yearAvto']
            # Convert year ranges to simple year list
            for year_range in year_data:
                if isinstance(year_range, dict):
                    begin = year_range.get('year_begin')
                    end = year_range.get('year_end')
                    if begin and end:
                        years.extend(range(begin, end + 1))
                else:
                    years.append(year_range)
        elif isinstance(year_list, list):
            years = year_list
        
        # Remove duplicates and sort
        years = sorted(list(set(years)))
        
        return {
            "success": True,
            "data": years,
            "mock_mode": False
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting car years: {e}")
        raise HTTPException(status_code=500, detail="Failed to get car years")

@router.get("/modifications")
async def get_car_modifications(
    brand: str = Query(..., description="Марка автомобиля"),
    model: str = Query(..., description="Модель автомобиля"),
    year_begin: str = Query(..., description="Год начала выпуска"),
    year_end: str = Query(..., description="Год окончания выпуска")
):
    try:
        if use_mock_data():
            logger.info(f"Using MOCK data for modifications")
            return {
                "success": True,
                "data": MOCK_MODIFICATIONS,
                "mock_mode": True
            }
        
        client = get_fourthchki_client()
        response = client.get_car_modifications(brand, model, year_begin, year_end)
        
        # Check if there's a meaningful error (not just empty error structure)
        error = response.get('error')
        if error and (error.get('code') or error.get('comment') or error.get('Message')):
            error_msg = error.get('Message') or error.get('comment') or f"Error code: {error.get('code')}"
            raise HTTPException(status_code=400, detail=error_msg)
        
        modifications = response.get('modification_list', [])
        # Handle None case
        if modifications is None:
            modifications = []
        # Handle the case where modifications is wrapped in a 'string' key
        elif isinstance(modifications, dict) and 'string' in modifications:
            modifications = modifications['string']
        
        return {
            "success": True,
            "data": modifications,
            "mock_mode": False
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting car modifications: {e}")
        raise HTTPException(status_code=500, detail="Failed to get car modifications")

@router.get("/goods")
async def get_goods_by_car(
    brand: str = Query(..., description="Марка автомобиля"),
    model: str = Query(..., description="Модель автомобиля"),
    year_begin: str = Query(..., description="Год начала выпуска"),
    year_end: str = Query(..., description="Год окончания выпуска"),
    modification: str = Query(..., description="Модификация"),
    product_type: str = Query("tyre", description="Тип товара: tyre, disk"),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    try:
        markup = await get_markup_percentage(db)
        
        if use_mock_data():
            logger.info(f"Using MOCK data for goods by car")
            response = generate_mock_goods_by_car(brand, model, product_type)
        else:
            client = get_fourthchki_client()
            type_list = [product_type] if product_type else ['tyre', 'disk']
            
            response = client.get_goods_by_car(
                brand=brand,
                model=model,
                year_begin=year_begin,
                year_end=year_end,
                modification=modification,
                product_type=type_list,
                podbor_type=[1]
            )
        
        # Check if there's a meaningful error (not just empty error structure)
        # Some error codes like 52 are warnings and still return data
        error = response.get('error')
        if error and error.get('code') and error.get('code') not in [52]:
            error_msg = error.get('Message') or error.get('comment') or f"Error code: {error.get('code')}"
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Extract goods data from nested structure
        goods_data = []
        price_rest_list = response.get('price_rest_list', {})
        if isinstance(price_rest_list, dict) and 'TyrePriceRest' in price_rest_list:
            goods_data = price_rest_list['TyrePriceRest']
        elif isinstance(price_rest_list, list):
            goods_data = price_rest_list
        
        # Apply markup to prices and normalize data structure
        TYUMEN_WAREHOUSE_ID = 42  # ID склада Тюмень
        
        for item in goods_data:
            # Parse size from name
            import re
            name = item.get('name', '')
            
            # Try tire pattern first (185/60R15)
            tire_match = re.match(r'(\d+)/(\d+)R(\d+)', name)
            if tire_match:
                item['width'] = int(tire_match.group(1))
                item['height'] = int(tire_match.group(2))
                item['diameter'] = int(tire_match.group(3))
            else:
                # Try disk pattern (7x16)
                disk_match = re.search(r'(\d+\.?\d*)x(\d+)', name)
                if disk_match:
                    item['width'] = float(disk_match.group(1))
                    item['diameter'] = int(disk_match.group(2))
            
            # Extract brand and model if not present
            if not item.get('brand'):
                item['brand'] = item.get('marka', 'Неизвестно')
            
            # Find the best price from warehouse data
            if item.get('whpr') and item['whpr'].get('wh_price_rest'):
                warehouses = item['whpr']['wh_price_rest']
                if warehouses:
                    # Приоритизируем склад Тюмень (ID 42)
                    tyumen_warehouse = next((w for w in warehouses if w.get('wrh') == TYUMEN_WAREHOUSE_ID), None)
                    best_warehouse = tyumen_warehouse if tyumen_warehouse else warehouses[0]
                    
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
            "data": goods_data,
            "warehouses": warehouses,
            "currency": response.get('currencyRate', {}),
            "markup_percentage": markup,
            "mock_mode": use_mock_data()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting goods by car: {e}")
        raise HTTPException(status_code=500, detail="Failed to get goods by car")
