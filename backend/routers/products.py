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

USE_MOCK_DATA = os.environ.get('USE_MOCK_DATA', 'false').lower() == 'true'

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
    page: int = Query(0, ge=0, description="Номер страницы"),
    page_size: int = Query(50, ge=1, le=200, description="Размер страницы"),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Поиск шин по параметрам
    """
    try:
        client = get_fourthchki_client()
        markup = await get_markup_percentage(db)
        
        # Преобразуем сезон в формат API
        season_map = {
            'summer': 's',
            'winter': 'w',
            'all-season': 'ws'
        }
        
        season_list = None
        if season and season in season_map:
            season_list = [season_map[season]]
        
        brand_list = [brand] if brand else None
        
        # Выполняем поиск
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
            "total_pages": response.get('totalPages', 0),
            "warehouses": response.get('warehouseLogistics', []),
            "currency": response.get('currencyRate', {}),
            "markup_percentage": markup
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
    page: int = Query(0, ge=0, description="Номер страницы"),
    page_size: int = Query(50, ge=1, le=200, description="Размер страницы"),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Поиск дисков по параметрам
    """
    try:
        client = get_fourthchki_client()
        markup = await get_markup_percentage(db)
        
        brand_list = [brand] if brand else None
        
        # Выполняем поиск
        response = client.search_disks(
            diameter_min=diameter,
            diameter_max=diameter,
            width_min=width,
            width_max=width,
            brand_list=brand_list,
            page=page,
            page_size=page_size
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
            "total_pages": response.get('totalPages', 0),
            "warehouses": response.get('warehouseLogistics', []),
            "currency": response.get('currencyRate', {}),
            "markup_percentage": markup
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
        client = get_fourthchki_client()
        markup = await get_markup_percentage(db)
        
        response = client.get_goods_info(code)
        
        # Проверяем на ошибки
        if response.get('error'):
            error_msg = response['error'].get('Message', 'Unknown error')
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Применяем наценку к цене
        if response.get('price'):
            original_price = float(response['price'])
            response['price_original'] = original_price
            response['price'] = apply_markup(original_price, markup)
        
        return {
            "success": True,
            "data": response,
            "markup_percentage": markup
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
        client = get_fourthchki_client()
        response = client.get_warehouses()
        
        # Проверяем на ошибки
        if response.get('error'):
            error_msg = response['error'].get('Message', 'Unknown error')
            raise HTTPException(status_code=400, detail=error_msg)
        
        return {
            "success": True,
            "data": response.get('warehouses', [])
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting warehouses: {e}")
        raise HTTPException(status_code=500, detail="Failed to get warehouses")
