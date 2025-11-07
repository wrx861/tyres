from zeep import Client
from zeep.cache import SqliteCache
from zeep.transports import Transport
from requests import Session
import os
import logging
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

class FourthchkiClient:
    def __init__(self):
        self.login = os.environ.get('FOURTHCHKI_LOGIN')
        self.password = os.environ.get('FOURTHCHKI_PASSWORD')
        self.wsdl_url = os.environ.get('FOURTHCHKI_API_URL')
        
        # Настройка транспорта с кэшированием
        session = Session()
        session.verify = False  # Отключаем проверку SSL если нужно
        transport = Transport(session=session, cache=SqliteCache())
        
        try:
            self.client = Client(self.wsdl_url, transport=transport)
            logger.info("FourthchkiClient initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize SOAP client: {e}")
            raise
    
    def _serialize_zeep_object(self, obj):
        """Конвертирует Zeep объекты в обычные Python словари"""
        if hasattr(obj, '__values__'):
            return {k: self._serialize_zeep_object(v) for k, v in obj.__values__.items()}
        elif isinstance(obj, list):
            return [self._serialize_zeep_object(item) for item in obj]
        elif isinstance(obj, dict):
            return {k: self._serialize_zeep_object(v) for k, v in obj.items()}
        else:
            return obj
    
    def search_tires(
        self,
        season_list: Optional[List[str]] = None,
        width_min: Optional[int] = None,
        width_max: Optional[int] = None,
        height_min: Optional[int] = None,
        height_max: Optional[int] = None,
        diameter_min: Optional[int] = None,
        diameter_max: Optional[int] = None,
        brand_list: Optional[List[str]] = None,
        page: int = 0,
        page_size: int = 50
    ) -> Dict:
        """
        Поиск шин по параметрам
        season_list: ['s' - лето, 'w' - зима, 'ws' - всесезон]
        """
        try:
            filter_data = {}
            
            if season_list:
                filter_data['season_list'] = season_list
            if width_min is not None:
                filter_data['width_min'] = width_min
            if width_max is not None:
                filter_data['width_max'] = width_max
            if height_min is not None:
                filter_data['height_min'] = height_min
            if height_max is not None:
                filter_data['height_max'] = height_max
            if diameter_min is not None:
                filter_data['diameter_min'] = diameter_min
            if diameter_max is not None:
                filter_data['diameter_max'] = diameter_max
            if brand_list:
                filter_data['brand_list'] = brand_list
            
            response = self.client.service.GetFindTyre(
                login=self.login,
                password=self.password,
                filter=filter_data if filter_data else None,
                page=page,
                pageSize=page_size
            )
            
            return self._serialize_zeep_object(response)
        except Exception as e:
            logger.error(f"Error searching tires: {e}")
            raise
    
    def search_disks(
        self,
        diameter_min: Optional[int] = None,
        diameter_max: Optional[int] = None,
        width_min: Optional[float] = None,
        width_max: Optional[float] = None,
        brand_list: Optional[List[str]] = None,
        bolts_count_min: Optional[int] = None,
        bolts_count_max: Optional[int] = None,
        bolts_spacing_min: Optional[float] = None,
        bolts_spacing_max: Optional[float] = None,
        et_min: Optional[float] = None,
        et_max: Optional[float] = None,
        dia_min: Optional[float] = None,
        dia_max: Optional[float] = None,
        color_list: Optional[List[str]] = None,
        type_list: Optional[List[int]] = None,
        page: int = 0,
        page_size: int = 50
    ) -> Dict:
        """Поиск дисков по параметрам"""
        try:
            filter_data = {}
            
            if diameter_min is not None:
                filter_data['diameter_min'] = diameter_min
            if diameter_max is not None:
                filter_data['diameter_max'] = diameter_max
            if width_min is not None:
                filter_data['width_min'] = width_min
            if width_max is not None:
                filter_data['width_max'] = width_max
            if brand_list:
                filter_data['brand_list'] = brand_list
            if bolts_count_min is not None:
                filter_data['bolts_count_min'] = bolts_count_min
            if bolts_count_max is not None:
                filter_data['bolts_count_max'] = bolts_count_max
            if bolts_spacing_min is not None:
                filter_data['bolts_spacing_min'] = bolts_spacing_min
            if bolts_spacing_max is not None:
                filter_data['bolts_spacing_max'] = bolts_spacing_max
            if et_min is not None:
                filter_data['et_min'] = et_min
            if et_max is not None:
                filter_data['et_max'] = et_max
            if dia_min is not None:
                filter_data['dia_min'] = dia_min
            if dia_max is not None:
                filter_data['dia_max'] = dia_max
            if color_list:
                filter_data['color_list'] = color_list
            if type_list:
                filter_data['type_list'] = type_list
            
            response = self.client.service.GetFindDisk(
                login=self.login,
                password=self.password,
                filter=filter_data if filter_data else None,
                page=page,
                pageSize=page_size
            )
            
            return self._serialize_zeep_object(response)
        except Exception as e:
            logger.error(f"Error searching disks: {e}")
            raise
    
    def get_car_brands(self) -> Dict:
        """Получить список марок автомобилей"""
        try:
            response = self.client.service.GetMarkaAvto(
                login=self.login,
                password=self.password
            )
            return self._serialize_zeep_object(response)
        except Exception as e:
            logger.error(f"Error getting car brands: {e}")
            raise
    
    def get_car_models(self, brand: str) -> Dict:
        """Получить список моделей автомобиля"""
        try:
            response = self.client.service.GetModelAvto(
                login=self.login,
                password=self.password,
                marka=brand
            )
            return self._serialize_zeep_object(response)
        except Exception as e:
            logger.error(f"Error getting car models: {e}")
            raise
    
    def get_car_years(self, brand: str, model: str) -> Dict:
        """Получить список годов выпуска"""
        try:
            response = self.client.service.GetYearAvto(
                login=self.login,
                password=self.password,
                marka=brand,
                model=model
            )
            return self._serialize_zeep_object(response)
        except Exception as e:
            logger.error(f"Error getting car years: {e}")
            raise
    
    def get_car_modifications(
        self, 
        brand: str, 
        model: str, 
        year_begin: str, 
        year_end: str
    ) -> Dict:
        """Получить список модификаций автомобиля"""
        try:
            response = self.client.service.GetModificationAvto(
                login=self.login,
                password=self.password,
                marka=brand,
                model=model,
                year_beg=year_begin,
                year_end=year_end
            )
            return self._serialize_zeep_object(response)
        except Exception as e:
            logger.error(f"Error getting car modifications: {e}")
            raise
    
    def get_goods_by_car(
        self,
        brand: str,
        model: str,
        year_begin: str,
        year_end: str,
        modification: str,
        product_type: List[str],  # ['tyre', 'disk']
        podbor_type: List[int] = [1]  # [1] - оригинал, [2] - замена
    ) -> Dict:
        """Подбор товаров по автомобилю"""
        try:
            filter_data = {
                'marka': brand,
                'model': model,
                'year_beg': year_begin,
                'year_end': year_end,
                'modification': modification,
                'type': product_type,
                'podbor_type': podbor_type
            }
            
            response = self.client.service.GetGoodsByCar(
                login=self.login,
                password=self.password,
                filter=filter_data
            )
            
            return self._serialize_zeep_object(response)
        except Exception as e:
            logger.error(f"Error getting goods by car: {e}")
            raise
    
    def get_goods_price_rest_by_code(self, code_list: List[str]) -> Dict:
        """Получить остатки и цены по кодам товаров"""
        try:
            filter_data = {
                'code_list': code_list
            }
            
            response = self.client.service.GetGoodsPriceRestByCode(
                login=self.login,
                password=self.password,
                filter=filter_data
            )
            
            return self._serialize_zeep_object(response)
        except Exception as e:
            logger.error(f"Error getting goods price/rest: {e}")
            raise
    
    def get_goods_info(self, code: str) -> Dict:
        """Получить подробную информацию о товаре"""
        try:
            response = self.client.service.GetGoodsInfo(
                login=self.login,
                password=self.password,
                code=code
            )
            
            return self._serialize_zeep_object(response)
        except Exception as e:
            logger.error(f"Error getting goods info: {e}")
            raise
    
    def create_order(self, order_items: List[Dict]) -> Dict:
        """
        Создать заказ у поставщика
        order_items: [{'code': '2329500', 'quantity': 1, 'wrh': 1}, ...]
        """
        try:
            order_data = {
                'product_list': order_items
            }
            
            response = self.client.service.CreateOrder(
                login=self.login,
                password=self.password,
                order=order_data
            )
            
            return self._serialize_zeep_object(response)
        except Exception as e:
            logger.error(f"Error creating order: {e}")
            raise
    
    def get_order_info(self, order_id: int) -> Dict:
        """Получить информацию о заказе"""
        try:
            response = self.client.service.GetOrderInfo2(
                login=self.login,
                password=self.password,
                orderId=order_id
            )
            
            return self._serialize_zeep_object(response)
        except Exception as e:
            logger.error(f"Error getting order info: {e}")
            raise
    
    def get_warehouses(self) -> Dict:
        """Получить список доступных складов"""
        try:
            response = self.client.service.GetWarehouses(
                login=self.login,
                password=self.password
            )
            
            return self._serialize_zeep_object(response)
        except Exception as e:
            logger.error(f"Error getting warehouses: {e}")
            raise

    
    def get_tire_brands(self, limit: int = 200) -> List[str]:
        """
        Получить список брендов шин
        Делает несколько запросов с разными параметрами для получения максимального списка брендов
        """
        brands = set()
        
        # Запросы с разными размерами для получения большего количества брендов
        size_ranges = [
            {'diameter_min': 13, 'diameter_max': 14},
            {'diameter_min': 15, 'diameter_max': 16},
            {'diameter_min': 17, 'diameter_max': 18},
            {'diameter_min': 19, 'diameter_max': 22},
        ]
        
        try:
            # Запросы с разными размерами
            for size_filter in size_ranges:
                try:
                    response = self.search_tires(page=0, page_size=100, **size_filter)
                    
                    # Извлекаем tire_data из вложенной структуры
                    tire_data = []
                    price_rest_list = response.get('price_rest_list', {})
                    if isinstance(price_rest_list, dict) and 'TyrePriceRest' in price_rest_list:
                        tire_data = price_rest_list['TyrePriceRest']
                    elif isinstance(price_rest_list, list):
                        tire_data = price_rest_list
                    
                    if tire_data:
                        for tyre in tire_data:
                            # Используем поле 'marka' из API
                            brand = tyre.get('brand') or tyre.get('marka')
                            if brand:
                                brands.add(brand)
                        logger.info(f"Found {len([t for t in tire_data if t.get('marka') or t.get('brand')])} brands in range {size_filter}")
                                
                    if len(brands) >= limit:
                        break
                except Exception as e:
                    logger.warning(f"Error in tire brands query with filter {size_filter}: {e}")
                    continue
            
            logger.info(f"Found total {len(brands)} tire brands")
            return sorted(list(brands))
        except Exception as e:
            logger.error(f"Error getting tire brands: {e}")
            return []
    
    def get_disk_brands(self, limit: int = 200) -> List[str]:
        """
        Получить список брендов дисков
        Делает несколько запросов с разными параметрами для получения максимального списка брендов
        """
        brands = set()
        
        # Запросы с разными размерами
        size_ranges = [
            {'diameter_min': 13, 'diameter_max': 14},
            {'diameter_min': 15, 'diameter_max': 16},
            {'diameter_min': 17, 'diameter_max': 18},
            {'diameter_min': 19, 'diameter_max': 22},
        ]
        
        try:
            # Запросы с разными размерами
            for size_filter in size_ranges:
                try:
                    response = self.search_disks(page=0, page_size=100, **size_filter)
                    if 'disk_list' in response and response['disk_list']:
                        for disk in response['disk_list']:
                            if 'brand' in disk and disk['brand']:
                                brands.add(disk['brand'])
                        logger.info(f"Found {len([d for d in response['disk_list'] if 'brand' in d])} brands in range {size_filter}")
                                
                    if len(brands) >= limit:
                        break
                except Exception as e:
                    logger.warning(f"Error in disk brands query with filter {size_filter}: {e}")
                    continue
            
            logger.info(f"Found total {len(brands)} disk brands")
            return sorted(list(brands))
        except Exception as e:
            logger.error(f"Error getting disk brands: {e}")
            return []

# Singleton instance
fourthchki_client = None

def get_fourthchki_client() -> FourthchkiClient:
    global fourthchki_client
    if fourthchki_client is None:
        fourthchki_client = FourthchkiClient()
    return fourthchki_client
