import React from 'react';
import { Plus, MapPin, Package } from 'lucide-react';

const ProductCard = ({ product, onAddToCart, type = 'tires' }) => {
  // Извлекаем данные о складе и остатках
  const getWarehouseInfo = () => {
    if (product.whpr && product.whpr.wh_price_rest && product.whpr.wh_price_rest.length > 0) {
      const warehouse = product.whpr.wh_price_rest[0];
      return {
        rest: warehouse.rest || 0,
        warehouse_name: warehouse.wrh || 'Склад'
      };
    }
    return {
      rest: product.rest || 0,
      warehouse_name: product.warehouse_name || 'Склад'
    };
  };

  const warehouseInfo = getWarehouseInfo();

  return (
    <div className="bg-white rounded-xl p-4 shadow-sm hover:shadow-md transition-shadow">
      <div className="flex justify-between items-start mb-3">
        <div className="flex-1">
          <h3 className="font-bold text-xl text-gray-900">{product.brand}</h3>
          <p className="text-gray-600 text-base">{product.model}</p>
        </div>
        <div className="text-right">
          <p className="text-2xl font-bold text-blue-600">{product.price?.toLocaleString()} ₽</p>
        </div>
      </div>

      <div className="space-y-2 mb-4">
        {type === 'tires' ? (
          <>
            <div className="flex items-center text-sm text-gray-700">
              <span className="font-medium">Размер:</span>
              <span className="ml-2">{product.width || ''}/{product.height || ''} R{product.diameter || ''}</span>
            </div>
            {product.season_name && (
              <div className="flex items-center text-sm text-gray-700">
                <span className="font-medium">Сезон:</span>
                <span className="ml-2">{product.season_name}</span>
              </div>
            )}
            {product.load_index && product.speed_index && (
              <div className="flex items-center text-sm text-gray-700">
                <span className="font-medium">Индексы:</span>
                <span className="ml-2">{product.load_index}{product.speed_index}</span>
              </div>
            )}
            {product.thorn && (
              <span className="inline-block bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded">
                Шипованные
              </span>
            )}
            {product.runflat && (
              <span className="inline-block bg-gray-100 text-gray-800 text-xs px-2 py-1 rounded ml-2">
                RunFlat
              </span>
            )}
          </>
        ) : (
          <>
            <div className="flex items-center text-sm text-gray-700">
              <span className="font-medium">Размер:</span>
              <span className="ml-2">{product.width}x{product.diameter}</span>
            </div>
            {product.pcd && (
              <div className="flex items-center text-sm text-gray-700">
                <span className="font-medium">PCD:</span>
                <span className="ml-2">{product.pcd}</span>
              </div>
            )}
            {product.et && (
              <div className="flex items-center text-sm text-gray-700">
                <span className="font-medium">ET:</span>
                <span className="ml-2">{product.et}</span>
              </div>
            )}
            {product.color && (
              <span className="inline-block bg-gray-100 text-gray-800 text-xs px-2 py-1 rounded">
                {product.color}
              </span>
            )}
          </>
        )}
      </div>

      <div className="flex items-center justify-between pt-3 border-t border-gray-100">
        <div className="flex items-center space-x-4 text-sm text-gray-600">
          <div className="flex items-center">
            <Package size={16} className="mr-1" />
            <span>{product.rest} шт</span>
          </div>
          <div className="flex items-center">
            <MapPin size={16} className="mr-1" />
            <span>{product.warehouse_name}</span>
          </div>
        </div>
        <button
          onClick={() => onAddToCart(product)}
          className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg flex items-center space-x-2 transition-colors"
        >
          <Plus size={18} />
          <span>В корзину</span>
        </button>
      </div>
    </div>
  );
};

export default ProductCard;
