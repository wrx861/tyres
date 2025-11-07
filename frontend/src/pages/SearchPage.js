import React, { useState, useEffect } from 'react';
import { ArrowLeft, Search as SearchIcon } from 'lucide-react';
import { searchTires, searchDisks, getTireBrands, getDiskBrands } from '../api/api';
import ProductCard from '../components/ProductCard';

const SearchPage = ({ onAddToCart, onBack, user }) => {
  const [searchType, setSearchType] = useState('tires'); // 'tires' or 'disks'
  const [filters, setFilters] = useState({
    width: '',
    height: '',
    diameter: '',
    season: '',
    brand: '',
    city: 'Тюмень', // По умолчанию Тюмень
    sort_by: '', // Сортировка по цене
    // Фильтры для дисков
    pcd: '',
    et_min: '',
    et_max: '',
    dia_min: '',
    dia_max: '',
    color: '',
    disk_type: ''
  });
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);
  const [tireBrands, setTireBrands] = useState([]);
  const [diskBrands, setDiskBrands] = useState([]);
  const [brandsLoading, setBrandsLoading] = useState(false);

  const cities = [
    'Тюмень',
    'Сургут',
    'Лянтор',
    'Нефтеюганск',
    'Белый Яр',
    'Екатеринбург',
    'Челябинск',
    'Москва',
    'Санкт-Петербург'
  ];

  const handleSearch = async () => {
    setLoading(true);
    setSearched(true);
    try {
      const params = {
        page: 0,
        page_size: 20
      };

      // Добавляем сортировку если выбрана
      if (filters.sort_by) params.sort_by = filters.sort_by;
      
      // Добавляем telegram_id для логирования и проверки блокировки
      if (user?.telegram_id) params.telegram_id = user.telegram_id;

      if (searchType === 'tires') {
        if (filters.width) params.width = parseInt(filters.width);
        if (filters.height) params.height = parseInt(filters.height);
        if (filters.diameter) params.diameter = parseInt(filters.diameter);
        if (filters.season) params.season = filters.season;
        if (filters.brand) params.brand = filters.brand;
        if (filters.city) params.city = filters.city;
        
        const response = await searchTires(params);
        setResults(response.data || []);
      } else {
        if (filters.diameter) params.diameter = parseInt(filters.diameter);
        if (filters.width) params.width = parseFloat(filters.width);
        if (filters.brand) params.brand = filters.brand;
        if (filters.city) params.city = filters.city;
        if (filters.pcd) params.pcd = filters.pcd;
        if (filters.et_min) params.et_min = parseFloat(filters.et_min);
        if (filters.et_max) params.et_max = parseFloat(filters.et_max);
        if (filters.dia_min) params.dia_min = parseFloat(filters.dia_min);
        if (filters.dia_max) params.dia_max = parseFloat(filters.dia_max);
        if (filters.color) params.color = filters.color;
        if (filters.disk_type !== '') params.disk_type = parseInt(filters.disk_type);
        
        const response = await searchDisks(params);
        setResults(response.data || []);
      }
    } catch (error) {
      console.error('Ошибка поиска:', error);
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm sticky top-0 z-10">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <div className="flex items-center space-x-4">
            <button onClick={onBack} className="p-2 hover:bg-gray-100 rounded-lg">
              <ArrowLeft size={24} />
            </button>
            <h1 className="text-xl font-bold">Поиск</h1>
          </div>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-4 py-6">
        {/* Type Toggle */}
        <div className="bg-white rounded-xl p-1 shadow-sm mb-6 flex">
          <button
            onClick={() => { setSearchType('tires'); setResults([]); setSearched(false); }}
            className={`flex-1 py-3 rounded-lg font-medium transition-colors ${
              searchType === 'tires' 
                ? 'bg-blue-500 text-white' 
                : 'text-gray-600 hover:bg-gray-50'
            }`}
          >
            Шины
          </button>
          <button
            onClick={() => { setSearchType('disks'); setResults([]); setSearched(false); }}
            className={`flex-1 py-3 rounded-lg font-medium transition-colors ${
              searchType === 'disks' 
                ? 'bg-blue-500 text-white' 
                : 'text-gray-600 hover:bg-gray-50'
            }`}
          >
            Диски
          </button>
        </div>

        {/* Filters */}
        <div className="bg-white rounded-xl p-6 shadow-sm mb-6">
          <h3 className="font-semibold text-lg mb-4">Фильтры</h3>
          
          {/* Выбор города */}
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Город (склад)
            </label>
            <select
              value={filters.city}
              onChange={(e) => setFilters({ ...filters, city: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              {cities.map(city => (
                <option key={city} value={city}>{city}</option>
              ))}
            </select>
          </div>

          {/* Сортировка по цене */}
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Сортировка по цене
            </label>
            <select
              value={filters.sort_by}
              onChange={(e) => setFilters({ ...filters, sort_by: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">Без сортировки</option>
              <option value="price_asc">Сначала дешевые</option>
              <option value="price_desc">Сначала дорогие</option>
            </select>
          </div>
          
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Ширина {searchType === 'tires' ? '(мм)' : '(дюймы)'}
              </label>
              <input
                type="number"
                value={filters.width}
                onChange={(e) => setFilters({ ...filters, width: e.target.value })}
                placeholder={searchType === 'tires' ? '185' : '6.5'}
                step={searchType === 'tires' ? '5' : '0.5'}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            {searchType === 'tires' && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Высота (профиль)
                </label>
                <input
                  type="number"
                  value={filters.height}
                  onChange={(e) => setFilters({ ...filters, height: e.target.value })}
                  placeholder="60"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            )}

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Диаметр (R)
              </label>
              <input
                type="number"
                value={filters.diameter}
                onChange={(e) => setFilters({ ...filters, diameter: e.target.value })}
                placeholder="15"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            {searchType === 'tires' && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Сезон
                </label>
                <select
                  value={filters.season}
                  onChange={(e) => setFilters({ ...filters, season: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="">Все</option>
                  <option value="summer">Летние</option>
                  <option value="winter">Зимние</option>
                  <option value="all-season">Всесезонные</option>
                </select>
              </div>
            )}

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Бренд
              </label>
              <input
                type="text"
                value={filters.brand}
                onChange={(e) => setFilters({ ...filters, brand: e.target.value })}
                placeholder="Например: Michelin"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            {/* Дополнительные фильтры для дисков */}
            {searchType === 'disks' && (
              <>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    PCD (сверловка)
                  </label>
                  <input
                    type="text"
                    value={filters.pcd}
                    onChange={(e) => setFilters({ ...filters, pcd: e.target.value })}
                    placeholder="5x114.3"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Вылет ET (мин)
                  </label>
                  <input
                    type="number"
                    value={filters.et_min}
                    onChange={(e) => setFilters({ ...filters, et_min: e.target.value })}
                    placeholder="35"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Вылет ET (макс)
                  </label>
                  <input
                    type="number"
                    value={filters.et_max}
                    onChange={(e) => setFilters({ ...filters, et_max: e.target.value })}
                    placeholder="45"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    DIA (мин)
                  </label>
                  <input
                    type="number"
                    value={filters.dia_min}
                    onChange={(e) => setFilters({ ...filters, dia_min: e.target.value })}
                    placeholder="60.1"
                    step="0.1"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    DIA (макс)
                  </label>
                  <input
                    type="number"
                    value={filters.dia_max}
                    onChange={(e) => setFilters({ ...filters, dia_max: e.target.value })}
                    placeholder="73.1"
                    step="0.1"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Цвет
                  </label>
                  <input
                    type="text"
                    value={filters.color}
                    onChange={(e) => setFilters({ ...filters, color: e.target.value })}
                    placeholder="Серебристый"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Тип диска
                  </label>
                  <select
                    value={filters.disk_type}
                    onChange={(e) => setFilters({ ...filters, disk_type: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="">Все</option>
                    <option value="0">Литой</option>
                    <option value="1">Штампованный</option>
                    <option value="2">Кованный</option>
                  </select>
                </div>
              </>
            )}
          </div>

          <button
            onClick={handleSearch}
            disabled={loading}
            className="w-full mt-6 bg-blue-500 hover:bg-blue-600 text-white font-medium py-3 rounded-lg flex items-center justify-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {loading ? (
              <>
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                <span>Поиск...</span>
              </>
            ) : (
              <>
                <SearchIcon size={20} />
                <span>Найти</span>
              </>
            )}
          </button>
        </div>

        {/* Results */}
        {searched && (
          <div>
            <h3 className="font-semibold text-lg mb-4">
              {results.length > 0 ? `Найдено: ${results.length}` : 'Ничего не найдено'}
            </h3>
            <div className="space-y-4">
              {results.map((item) => (
                <ProductCard
                  key={item.code}
                  product={item}
                  onAddToCart={onAddToCart}
                  type={searchType}
                />
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default SearchPage;
