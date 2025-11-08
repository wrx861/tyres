import React, { useState, useEffect } from 'react';
import { ArrowLeft, ChevronRight } from 'lucide-react';
import { getCarBrands, getCarModels, getCarYears, getCarModifications, getGoodsByCar } from '../api/api';
import ProductCard from '../components/ProductCard';

const CarSelectionPage = ({ onAddToCart, onRemoveFromCart, onBack, user, cart }) => {
  const [step, setStep] = useState(1);
  const [brands, setBrands] = useState([]);
  const [models, setModels] = useState([]);
  const [years, setYears] = useState([]);
  const [modifications, setModifications] = useState([]);
  const [results, setResults] = useState([]);
  
  const [selected, setSelected] = useState({
    brand: '',
    model: '',
    year_begin: '',
    year_end: '',
    modification: '',
    product_type: 'tyre'
  });
  
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadBrands();
  }, []);

  const loadBrands = async () => {
    setLoading(true);
    try {
      const response = await getCarBrands();
      setBrands(response.data || []);
    } catch (error) {
      console.error('Ошибка загрузки марок:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleBrandSelect = async (brand) => {
    setSelected({ ...selected, brand });
    setLoading(true);
    try {
      const response = await getCarModels(brand);
      setModels(response.data || []);
      setStep(2);
    } catch (error) {
      console.error('Ошибка загрузки моделей:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleModelSelect = async (model) => {
    setSelected({ ...selected, model });
    setLoading(true);
    try {
      const response = await getCarYears(selected.brand, model);
      setYears(response.data || []);
      setStep(3);
    } catch (error) {
      console.error('Ошибка загрузки годов:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleYearSelect = async (year) => {
    const updatedSelection = { ...selected, year_begin: year, year_end: year };
    setSelected(updatedSelection);
    setLoading(true);
    try {
      const response = await getCarModifications(selected.brand, selected.model, year, year);
      const mods = response.data || [];
      setModifications(mods);
      
      // Если модификаций нет, показываем сообщение
      if (mods.length === 0) {
        console.log('Нет модификаций для выбранного автомобиля');
        setStep(4); // Показываем шаг с сообщением
      } else {
        setStep(4);
      }
    } catch (error) {
      console.error('Ошибка загрузки модификаций:', error);
      setModifications([]);
      setStep(4);
    } finally {
      setLoading(false);
    }
  };

  const handleModificationSelect = async (modification) => {
    const finalSelection = { ...selected, modification };
    setSelected(finalSelection);
    setLoading(true);
    try {
      const response = await getGoodsByCar(finalSelection);
      setResults(response.data || []);
      setStep(5);
    } catch (error) {
      console.error('Ошибка загрузки товаров:', error);
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  const renderBreadcrumb = () => {
    const items = [];
    if (selected.brand) items.push(selected.brand);
    if (selected.model) items.push(selected.model);
    if (selected.year_begin) items.push(selected.year_begin);
    if (selected.modification) items.push(selected.modification);
    
    return items.length > 0 ? (
      <div className="flex items-center space-x-2 text-sm text-gray-600 mb-4">
        {items.map((item, idx) => (
          <React.Fragment key={idx}>
            <span>{item}</span>
            {idx < items.length - 1 && <ChevronRight size={16} />}
          </React.Fragment>
        ))}
      </div>
    ) : null;
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="bg-white shadow-sm sticky top-0 z-10">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <div className="flex items-center space-x-4">
            <button onClick={onBack} className="p-2 hover:bg-gray-100 rounded-lg">
              <ArrowLeft size={24} />
            </button>
            <div className="flex-1">
              <h1 className="text-xl font-bold">Подбор по автомобилю</h1>
              {renderBreadcrumb()}
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-4 py-6">
        {loading && (
          <div className="flex justify-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        )}

        {!loading && step === 1 && (
          <div>
            <h2 className="text-lg font-semibold mb-4">Выберите марку автомобиля</h2>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
              {brands.map((brand) => (
                <button
                  key={brand}
                  onClick={() => handleBrandSelect(brand)}
                  className="bg-white p-4 rounded-lg shadow-sm hover:shadow-md transition-shadow text-left font-medium"
                >
                  {brand}
                </button>
              ))}
            </div>
          </div>
        )}

        {!loading && step === 2 && (
          <div>
            <h2 className="text-lg font-semibold mb-4">Выберите модель</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {models.map((model) => (
                <button
                  key={model}
                  onClick={() => handleModelSelect(model)}
                  className="bg-white p-4 rounded-lg shadow-sm hover:shadow-md transition-shadow text-left font-medium"
                >
                  {model}
                </button>
              ))}
            </div>
          </div>
        )}

        {!loading && step === 3 && (
          <div>
            <h2 className="text-lg font-semibold mb-4">Выберите год выпуска</h2>
            <div className="grid grid-cols-3 md:grid-cols-4 gap-3">
              {years.map((year) => (
                <button
                  key={year}
                  onClick={() => handleYearSelect(year)}
                  className="bg-white p-4 rounded-lg shadow-sm hover:shadow-md transition-shadow text-center font-medium"
                >
                  {year}
                </button>
              ))}
            </div>
          </div>
        )}

        {!loading && step === 4 && (
          <div>
            <h2 className="text-lg font-semibold mb-4">Выберите модификацию двигателя</h2>
            {modifications.length === 0 ? (
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 text-center">
                <p className="text-yellow-800 font-medium mb-4">
                  Модификации не найдены для выбранных параметров
                </p>
                <p className="text-gray-600 mb-4">
                  {selected.brand} {selected.model} ({selected.year_begin})
                </p>
                <button
                  onClick={() => setStep(1)}
                  className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
                >
                  Попробовать другой автомобиль
                </button>
              </div>
            ) : (
              <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                {modifications.map((mod) => (
                  <button
                    key={mod}
                    onClick={() => handleModificationSelect(mod)}
                    className="bg-white p-4 rounded-lg shadow-sm hover:shadow-md transition-shadow text-center font-medium"
                >
                    {mod}
                  </button>
                ))}
              </div>
            )}
          </div>
        )}

        {!loading && step === 5 && (
          <div>
            <div className="bg-white rounded-xl p-4 mb-6 shadow-sm">
              <div className="flex items-center space-x-4">
                <button
                  onClick={() => setSelected({ ...selected, product_type: 'tyre' })}
                  className={`flex-1 py-2 rounded-lg font-medium ${
                    selected.product_type === 'tyre'
                      ? 'bg-blue-500 text-white'
                      : 'bg-gray-100 text-gray-600'
                  }`}
                >
                  Шины
                </button>
                <button
                  onClick={() => setSelected({ ...selected, product_type: 'disk' })}
                  className={`flex-1 py-2 rounded-lg font-medium ${
                    selected.product_type === 'disk'
                      ? 'bg-blue-500 text-white'
                      : 'bg-gray-100 text-gray-600'
                  }`}
                >
                  Диски
                </button>
              </div>
            </div>

            <h2 className="text-lg font-semibold mb-4">
              Найдено: {results.length}
            </h2>
            <div className="space-y-4">
              {results.map((item) => (
                <ProductCard
                  key={item.code}
                  product={item}
                  onAddToCart={onAddToCart}
                  onRemoveFromCart={onRemoveFromCart}
                  cart={cart}
                  type={selected.product_type === 'tyre' ? 'tires' : 'disks'}
                />
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default CarSelectionPage;
