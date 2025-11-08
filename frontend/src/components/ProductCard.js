import React, { useContext, useState } from 'react';
import { Plus, MapPin, Package, ShoppingCart } from 'lucide-react';
import { WarehousesContext } from '../App';
import ProductImageModal from './ProductImageModal';

// Хелпер для форматирования цены без копеек
const formatPrice = (price) => {
  return Math.round(price).toLocaleString('ru-RU');
};

const ProductCard = ({ product, onAddToCart, cart = [], type = 'tires' }) => {
  const warehouses = useContext(WarehousesContext);
  const [showImageModal, setShowImageModal] = useState(false);
  const [quantity, setQuantity] = useState(4); // По умолчанию 4 шт (комплект)
  const [showAddedNotification, setShowAddedNotification] = useState(false);
  
  // Получаем количество этого товара в корзине
  const cartItem = cart.find(item => item.code === product.code);
  const inCartQuantity = cartItem ? cartItem.quantity : 0;
  
  // Извлекаем данные о складе и остатках
  const getWarehouseInfo = () => {
    // Сначала проверяем обработанные backend данные (они уже приоритизируют Тюмень)
    if (product.warehouse_id !== undefined && product.rest !== undefined) {
      const warehouseId = product.warehouse_id;
      const warehouseName = warehouses[warehouseId];
      return {
        rest: product.rest,
        warehouse_name: warehouseName || `Склад ${warehouseId}`
      };
    }
    
    // Если backend не обработал, берем из whpr
    if (product.whpr && product.whpr.wh_price_rest && product.whpr.wh_price_rest.length > 0) {
      const warehouse = product.whpr.wh_price_rest[0];
      const warehouseId = warehouse.wrh || 0;
      return {
        rest: warehouse.rest || 0,
        warehouse_name: warehouses[warehouseId] || `Склад ${warehouseId}`
      };
    }
    
    // Фоллбэк
    return {
      rest: 0,
      warehouse_name: 'Склад'
    };
  };

  const warehouseInfo = getWarehouseInfo();

  return (
    <>
      <div className="bg-white dark:bg-gray-800 rounded-xl p-4 shadow-sm hover:shadow-md transition-shadow border border-transparent dark:border-gray-700 relative">
        {/* Индикатор количества в корзине */}
        {inCartQuantity > 0 && (
          <div className="absolute top-3 right-3 bg-orange-500 text-white rounded-full px-2.5 py-1 flex items-center space-x-1 shadow-lg z-10">
            <ShoppingCart size={14} />
            <span className="text-xs font-bold">{inCartQuantity}</span>
          </div>
        )}
        
        <div className="flex items-start space-x-4 mb-3">
          {/* Product Image */}
          {product.img_small && (
            <img 
              src={product.img_small} 
              alt={`${product.brand} ${product.model}`}
              className="w-20 h-20 object-contain cursor-pointer hover:opacity-80 transition-opacity flex-shrink-0"
              onClick={() => setShowImageModal(true)}
              onError={(e) => {
                e.target.style.display = 'none';
              }}
            />
          )}
          
          {/* Product Info */}
          <div className="flex-1 min-w-0">
            <h3 className="font-bold text-xl text-gray-900 dark:text-white">{product.brand}</h3>
            <p className="text-gray-600 dark:text-gray-300 text-base">{product.model}</p>
          </div>
          
          {/* Price */}
          <div className="text-right flex-shrink-0">
            <p className="text-2xl font-bold text-blue-600">{formatPrice(product.price)} ₽</p>
          </div>
        </div>

      <div className="space-y-2 mb-4">
        {type === 'tires' ? (
          <>
            <div className="flex items-center text-sm text-gray-700 dark:text-gray-300">
              <span className="font-medium">Размер:</span>
              <span className="ml-2">{product.width || ''}/{product.height || ''} R{product.diameter || ''}</span>
            </div>
            {product.season_name && (
              <div className="flex items-center text-sm text-gray-700 dark:text-gray-300">
                <span className="font-medium">Сезон:</span>
                <span className="ml-2">{product.season_name}</span>
              </div>
            )}
            {product.load_index && product.speed_index && (
              <div className="flex items-center text-sm text-gray-700 dark:text-gray-300">
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
            <div className="flex items-center text-sm text-gray-700 dark:text-gray-300">
              <span className="font-medium">Размер:</span>
              <span className="ml-2">{product.width}x{product.diameter}</span>
            </div>
            {product.pcd && (
              <div className="flex items-center text-sm text-gray-700 dark:text-gray-300">
                <span className="font-medium">PCD:</span>
                <span className="ml-2">{product.pcd}</span>
              </div>
            )}
            {product.et && (
              <div className="flex items-center text-sm text-gray-700 dark:text-gray-300">
                <span className="font-medium">ET:</span>
                <span className="ml-2">{product.et}</span>
              </div>
            )}
            {product.dia && (
              <div className="flex items-center text-sm text-gray-700 dark:text-gray-300">
                <span className="font-medium">DIA:</span>
                <span className="ml-2">{product.dia}</span>
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

      <div className="pt-3 border-t border-gray-100 dark:border-gray-700">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center space-x-4 text-sm text-gray-600 dark:text-gray-300">
            <div className="flex items-center">
              <Package size={16} className="mr-1" />
              <span>{warehouseInfo.rest} шт</span>
            </div>
            <div className="flex items-center">
              <MapPin size={16} className="mr-1" />
              <span>{warehouseInfo.warehouse_name}</span>
            </div>
          </div>
        </div>
        
        {/* Quantity Selector */}
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center space-x-3">
            <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Количество:</span>
            <div className="flex items-center space-x-2">
            <button
              onClick={() => setQuantity(Math.max(1, quantity - 1))}
              className="w-8 h-8 flex items-center justify-center bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 rounded-lg transition-colors text-gray-900 dark:text-white font-bold"
            >
              -
            </button>
            <input
              type="number"
              value={quantity}
              onChange={(e) => setQuantity(Math.max(1, parseInt(e.target.value) || 1))}
              className="w-16 text-center border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-lg py-1"
              min="1"
            />
            <button
              onClick={() => setQuantity(quantity + 1)}
              className="w-8 h-8 flex items-center justify-center bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 rounded-lg transition-colors text-gray-900 dark:text-white font-bold"
            >
              +
            </button>
          </div>
        </div>

        <button
          onClick={() => {
            // Проверка доступного количества
            if (quantity > warehouseInfo.rest) {
              setShowAddedNotification(true);
              setTimeout(() => setShowAddedNotification(false), 3000);
              return;
            }
            
            onAddToCart({ ...product, quantity });
            setShowAddedNotification(true);
            setTimeout(() => setShowAddedNotification(false), 2000);
          }}
          className="w-full bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg flex items-center justify-center space-x-2 transition-colors"
        >
          <Plus size={18} />
          <span>Добавить в корзину</span>
        </button>

        {/* Added Notification */}
        {showAddedNotification && (
          <div className={`mt-2 text-sm py-2 px-3 rounded-lg text-center ${
            quantity > warehouseInfo.rest 
              ? 'bg-red-100 text-red-800' 
              : 'bg-green-100 text-green-800'
          }`}>
            {quantity > warehouseInfo.rest 
              ? `⚠️ Доступно только ${warehouseInfo.rest} шт`
              : `✓ Добавлено ${quantity} шт в корзину`
            }
          </div>
        )}
      </div>
      </div>
      
      {/* Image Modal */}
      <ProductImageModal 
        product={product}
        isOpen={showImageModal}
        onClose={() => setShowImageModal(false)}
      />
    </>
  );
};

export default ProductCard;
