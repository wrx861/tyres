"""
Mock данные для демонстрации работы приложения
Когда API 4tochki заработает, просто переключим USE_MOCK_DATA=false
"""

# Mock марки автомобилей
MOCK_CAR_BRANDS = [
    "Audi", "BMW", "Ford", "Honda", "Hyundai", "Kia", "Mazda", 
    "Mercedes-Benz", "Nissan", "Renault", "Skoda", "Toyota", 
    "Volkswagen", "Volvo", "Lada"
]

# Mock модели для популярных марок
MOCK_CAR_MODELS = {
    "Toyota": ["Camry", "Corolla", "RAV4", "Land Cruiser", "Highlander"],
    "BMW": ["3 Series", "5 Series", "X3", "X5", "X7"],
    "Mercedes-Benz": ["C-Class", "E-Class", "GLC", "GLE", "S-Class"],
    "Volkswagen": ["Polo", "Tiguan", "Passat", "Golf", "Touareg"],
    "Audi": ["A3", "A4", "A6", "Q3", "Q5", "Q7"],
    "Ford": ["Focus", "Mondeo", "Kuga", "Explorer", "Mustang"],
    "Hyundai": ["Solaris", "Creta", "Tucson", "Santa Fe", "Elantra"],
    "Kia": ["Rio", "Sportage", "Sorento", "Seltos", "K5"],
    "Nissan": ["Qashqai", "X-Trail", "Juke", "Murano", "Almera"],
    "Skoda": ["Octavia", "Rapid", "Kodiaq", "Karoq", "Superb"],
}

# Mock года
MOCK_YEARS = ["2015", "2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023", "2024"]

# Mock модификации
MOCK_MODIFICATIONS = ["1.6", "1.8", "2.0", "2.5", "3.0", "3.5"]

# Mock бренды шин
MOCK_TIRE_BRANDS = [
    "Michelin", "Bridgestone", "Continental", "Goodyear", "Pirelli",
    "Nokian", "Yokohama", "Hankook", "Dunlop", "Kumho", "Toyo",
    "Nexen", "Cooper", "BFGoodrich", "Vredestein", "Falken",
    "Cordiant", "Viatti", "Кама", "Nordman"
]

# Mock модели шин
MOCK_TIRE_MODELS = {
    "Michelin": ["X-Ice North 4", "Primacy 4", "Pilot Sport 4", "CrossClimate"],
    "Bridgestone": ["Blizzak DM-V3", "Turanza T005", "Potenza", "Ecopia"],
    "Continental": ["WinterContact TS 870", "PremiumContact 6", "IceContact 3"],
    "Nokian": ["Hakkapeliitta R3", "Nordman RS2", "Tyres WR D4"],
    "Pirelli": ["Ice Zero FR", "Cinturato P7", "Scorpion Verde"],
}

# Mock шины
def generate_mock_tires(season=None, width=None, height=None, diameter=None, brand=None, page=0, page_size=50):
    """Генерация mock шин"""
    import random
    
    tires = []
    total_items = 150  # Общее количество mock шин
    
    # Фильтрация
    filtered_count = total_items
    if season:
        filtered_count = int(filtered_count * 0.7)
    if width and height and diameter:
        filtered_count = int(filtered_count * 0.3)
    
    # Генерация для текущей страницы
    start_idx = page * page_size
    end_idx = min(start_idx + page_size, filtered_count)
    
    for i in range(start_idx, end_idx):
        tire_brand = brand if brand else random.choice(MOCK_TIRE_BRANDS)
        models = MOCK_TIRE_MODELS.get(tire_brand, ["Model A", "Model B", "Model C"])
        tire_model = random.choice(models)
        
        # Размеры
        tire_width = width if width else random.choice([175, 185, 195, 205, 215, 225, 235])
        tire_height = height if height else random.choice([55, 60, 65, 70])
        tire_diameter = diameter if diameter else random.choice([14, 15, 16, 17, 18])
        
        # Сезон
        seasons = ['w', 's', 'u']
        if season:
            tire_season = season[0] if isinstance(season, list) else season
        else:
            tire_season = random.choice(seasons)
        
        season_names = {'w': 'Зимние', 's': 'Летние', 'u': 'Всесезонные'}
        
        # Цена
        base_price = random.randint(3000, 15000)
        
        tire = {
            'code': f'TIRE{10000 + i}',
            'brand': tire_brand,
            'model': tire_model,
            'width': tire_width,
            'height': tire_height,
            'diameter': tire_diameter,
            'season': tire_season,
            'season_name': season_names[tire_season],
            'price': base_price,
            'rest': random.randint(4, 50),
            'warehouse_id': random.choice([1, 2, 3]),
            'warehouse_name': random.choice(['Москва', 'Санкт-Петербург', 'Екатеринбург']),
            'load_index': random.choice(['91', '95', '99', '103']),
            'speed_index': random.choice(['H', 'T', 'V', 'W']),
            'runflat': random.choice([True, False]),
            'thorn': tire_season == 'w' and random.choice([True, False]),
            'img_small': 'https://via.placeholder.com/120x120/4299e1/ffffff?text=Tire',
            'img_big_my': 'https://via.placeholder.com/400x400/4299e1/ffffff?text=Tire+Detail',
            'img_big_pish': 'https://via.placeholder.com/400x400/4299e1/ffffff?text=Tire+4tochki',
        }
        
        tires.append(tire)
    
    total_pages = (filtered_count + page_size - 1) // page_size
    
    return {
        'success': True,
        'price_rest_list': tires,
        'totalPages': total_pages,
        'currencyRate': {'name': 'RUB', 'rate': 1.0}
    }

# Mock диски
def generate_mock_disks(diameter=None, width=None, brand=None, page=0, page_size=50):
    """Генерация mock дисков"""
    import random
    
    disk_brands = ["K&K", "SKAD", "Tech Line", "Neo", "Venti", "LS", "КиК", "Replica", "PDW"]
    disks = []
    total_items = 120
    
    filtered_count = total_items
    if diameter:
        filtered_count = int(filtered_count * 0.4)
    
    start_idx = page * page_size
    end_idx = min(start_idx + page_size, filtered_count)
    
    for i in range(start_idx, end_idx):
        disk_brand = brand if brand else random.choice(disk_brands)
        disk_diameter = diameter if diameter else random.choice([14, 15, 16, 17, 18, 19, 20])
        disk_width = width if width else random.choice([5.5, 6.0, 6.5, 7.0, 7.5, 8.0])
        
        base_price = random.randint(2500, 12000)
        
        disk = {
            'code': f'DISK{20000 + i}',
            'brand': disk_brand,
            'model': f'D{disk_diameter}x{disk_width}',
            'diameter': disk_diameter,
            'width': disk_width,
            'pcd': random.choice(['4x100', '5x112', '5x114.3', '5x120']),
            'et': random.choice([35, 40, 45, 50]),
            'dia': random.choice([56.1, 60.1, 66.6, 73.1]),
            'color': random.choice(['Серебристый', 'Черный', 'Графит', 'Белый']),
            'price': base_price,
            'rest': random.randint(4, 30),
            'warehouse_id': random.choice([1, 2, 3]),
            'warehouse_name': random.choice(['Москва', 'Санкт-Петербург', 'Екатеринбург']),
        }
        
        disks.append(disk)
    
    total_pages = (filtered_count + page_size - 1) // page_size
    
    return {
        'success': True,
        'price_rest_list': disks,
        'totalPages': total_pages,
        'currencyRate': {'name': 'RUB', 'rate': 1.0}
    }

# Mock подбор по авто
def generate_mock_goods_by_car(brand, model, product_type='tyre'):
    """Генерация mock товаров по автомобилю"""
    if product_type == 'tyre':
        # Для конкретного авто генерируем подходящие шины
        return generate_mock_tires(width=205, height=55, diameter=16, page=0, page_size=20)
    else:
        # Для дисков
        return generate_mock_disks(diameter=16, page=0, page_size=20)

# Mock склады
MOCK_WAREHOUSES = [
    {'id': 1, 'name': 'Москва, Красная Сосна', 'logistics_days': 0},
    {'id': 2, 'name': 'Санкт-Петербург', 'logistics_days': 1},
    {'id': 3, 'name': 'Екатеринбург', 'logistics_days': 2},
]
