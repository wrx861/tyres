from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
import logging

from services.fourthchki_client import get_fourthchki_client

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/cars", tags=["cars"])

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
    return 15.0

@router.get("/brands")
async def get_car_brands():
    """
    Получить список марок автомобилей
    """
    try:
        client = get_fourthchki_client()
        response = client.get_car_brands()
        
        # Проверяем на ошибки
        if response.get('error'):
            error_msg = response['error'].get('Message', 'Unknown error')
            raise HTTPException(status_code=400, detail=error_msg)
        
        brands = response.get('marka_list', [])
        
        return {
            "success": True,
            "data": brands
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
    """
    Получить список моделей автомобиля
    """
    try:
        client = get_fourthchki_client()
        response = client.get_car_models(brand)
        
        # Проверяем на ошибки
        if response.get('error'):
            error_msg = response['error'].get('Message', 'Unknown error')
            raise HTTPException(status_code=400, detail=error_msg)
        
        models = response.get('model_list', [])
        
        return {
            "success": True,
            "data": models
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
    """
    Получить список годов выпуска автомобиля
    """
    try:
        client = get_fourthchki_client()
        response = client.get_car_years(brand, model)
        
        # Проверяем на ошибки
        if response.get('error'):
            error_msg = response['error'].get('Message', 'Unknown error')
            raise HTTPException(status_code=400, detail=error_msg)
        
        years = response.get('year_list', [])
        
        return {
            "success": True,
            "data": years
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
    """
    Получить список модификаций автомобиля
    """
    try:
        client = get_fourthchki_client()
        response = client.get_car_modifications(brand, model, year_begin, year_end)
        
        # Проверяем на ошибки
        if response.get('error'):
            error_msg = response['error'].get('Message', 'Unknown error')
            raise HTTPException(status_code=400, detail=error_msg)
        
        modifications = response.get('modification_list', [])
        
        return {
            "success": True,
            "data": modifications
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
    """
    Подобрать товары по автомобилю
    """
    try:
        client = get_fourthchki_client()
        markup = await get_markup_percentage(db)
        
        # Преобразуем тип товара в список
        type_list = [product_type] if product_type else ['tyre', 'disk']
        
        response = client.get_goods_by_car(
            brand=brand,
            model=model,
            year_begin=year_begin,
            year_end=year_end,
            modification=modification,
            product_type=type_list,
            podbor_type=[1]  # 1 - оригинал
        )
        
        # Проверяем на ошибки
        if response.get('error'):
            error_msg = response['error'].get('Message', 'Unknown error')
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Применяем наценку к ценам
        if response.get('price_rest_list'):
            for item in response['price_rest_list']:
                if item.get('price'):
                    original_price = float(item['price'])
                    item['price_original'] = original_price
                    item['price'] = apply_markup(original_price, markup)
        
        return {
            "success": True,
            "data": response.get('price_rest_list', []),
            "warehouses": response.get('warehouseLogistics', []),
            "currency": response.get('currencyRate', {}),
            "markup_percentage": markup
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting goods by car: {e}")
        raise HTTPException(status_code=500, detail="Failed to get goods by car")
