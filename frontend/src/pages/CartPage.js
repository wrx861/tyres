import React, { useState } from 'react';
import { ArrowLeft, Trash2, Minus, Plus, ShoppingBag } from 'lucide-react';
import { createOrder } from '../api/api';

const CartPage = ({ cart, user, onUpdateQuantity, onRemove, onClear, onBack }) => {
  const [deliveryAddress, setDeliveryAddress] = useState({
    city: '',
    street: '',
    house: '',
    apartment: '',
    phone: '',
    comment: ''
  });
  const [submitting, setSubmitting] = useState(false);
  const [orderCreated, setOrderCreated] = useState(false);

  const total = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);

  const handleSubmitOrder = async () => {
    if (!deliveryAddress.city || !deliveryAddress.street || !deliveryAddress.house || !deliveryAddress.phone) {
      alert('Пожалуйста, заполните все обязательные поля (город, улица, дом, телефон)');
      return;
    }
    
    // Проверка формата телефона (базовая)
    const phoneRegex = /^[\d\s\+\-\(\)]{10,}$/;
    if (!phoneRegex.test(deliveryAddress.phone)) {
      alert('Пожалуйста, введите корректный номер телефона');
      return;
    }

    setSubmitting(true);
    try {
      const orderData = {
        items: cart.map(item => ({
          code: item.code,
          name: `${item.brand} ${item.model}`,
          brand: item.brand,
          quantity: item.quantity,
          price_base: item.price_original || item.price,
          price_final: item.price,
          warehouse_id: item.warehouse_id || 1,
          warehouse_name: item.warehouse_name || 'Москва'
        })),
        delivery_address: deliveryAddress
      };

      await createOrder(orderData, user.telegram_id);
      setOrderCreated(true);
      onClear();
    } catch (error) {
      console.error('Ошибка создания заказа:', error);
      alert('Не удалось создать заказ. Попробуйте позже.');
    } finally {
      setSubmitting(false);
    }
  };

  if (orderCreated) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="bg-white rounded-2xl p-8 max-w-md mx-4 text-center shadow-lg">
          <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <ShoppingBag className="text-green-600" size={32} />
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Заказ оформлен!</h2>
          <p className="text-gray-600 mb-6">
            Ваш заказ отправлен на подтверждение администратору. Мы уведомим вас о статусе заказа.
          </p>
          <button
            onClick={onBack}
            className="w-full bg-blue-500 hover:bg-blue-600 text-white font-medium py-3 rounded-lg transition-colors"
          >
            На главную
          </button>
        </div>
      </div>
    );
  }

  if (cart.length === 0) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="bg-white shadow-sm">
          <div className="max-w-4xl mx-auto px-4 py-4">
            <div className="flex items-center space-x-4">
              <button onClick={onBack} className="p-2 hover:bg-gray-100 rounded-lg">
                <ArrowLeft size={24} />
              </button>
              <h1 className="text-xl font-bold">Корзина</h1>
            </div>
          </div>
        </div>
        <div className="max-w-4xl mx-auto px-4 py-12 text-center">
          <ShoppingBag className="mx-auto text-gray-400 mb-4" size={64} />
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Корзина пуста</h2>
          <p className="text-gray-600">Добавьте товары для оформления заказа</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="bg-white shadow-sm sticky top-0 z-10">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <div className="flex items-center space-x-4">
            <button onClick={onBack} className="p-2 hover:bg-gray-100 rounded-lg">
              <ArrowLeft size={24} />
            </button>
            <h1 className="text-xl font-bold">Корзина ({cart.length})</h1>
          </div>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-4 py-6">
        {/* Cart Items */}
        <div className="space-y-4 mb-6">
          {cart.map((item) => (
            <div key={item.code} className="bg-white rounded-xl p-4 shadow-sm">
              <div className="flex items-start space-x-4 mb-3">
                {/* Product Image */}
                {item.img_small && (
                  <img 
                    src={item.img_small} 
                    alt={`${item.brand} ${item.model}`}
                    className="w-16 h-16 object-contain flex-shrink-0"
                    onError={(e) => {
                      e.target.style.display = 'none';
                    }}
                  />
                )}
                
                <div className="flex-1 flex justify-between items-start">
                  <div>
                    <h3 className="font-semibold text-gray-900">{item.brand}</h3>
                    <p className="text-sm text-gray-600">{item.model}</p>
                    <p className="text-xs text-gray-500 mt-1">
                      {item.width && item.height && item.diameter
                        ? `${item.width}/${item.height} R${item.diameter}`
                        : `${item.width}x${item.diameter}`}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="font-bold text-blue-600">{(item.price * item.quantity).toLocaleString()} ₽</p>
                    <p className="text-xs text-gray-500">{item.price.toLocaleString()} ₽ / шт</p>
                  </div>
                </div>
              </div>

              <div className="flex items-center justify-between pt-3 border-t border-gray-100">
                <div className="flex items-center space-x-3">
                  <button
                    onClick={() => onUpdateQuantity(item.code, item.quantity - 1)}
                    className="p-2 rounded-lg bg-gray-100 hover:bg-gray-200"
                  >
                    <Minus size={16} />
                  </button>
                  <span className="font-medium w-8 text-center">{item.quantity}</span>
                  <button
                    onClick={() => onUpdateQuantity(item.code, item.quantity + 1)}
                    className="p-2 rounded-lg bg-gray-100 hover:bg-gray-200"
                  >
                    <Plus size={16} />
                  </button>
                </div>
                <button
                  onClick={() => onRemove(item.code)}
                  className="text-red-500 hover:text-red-600 p-2"
                >
                  <Trash2 size={20} />
                </button>
              </div>
            </div>
          ))}
        </div>

        {/* Delivery Address */}
        <div className="bg-white rounded-xl p-6 shadow-sm mb-6">
          <h3 className="font-semibold text-lg mb-4">Адрес доставки</h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Город *</label>
              <input
                type="text"
                value={deliveryAddress.city}
                onChange={(e) => setDeliveryAddress({ ...deliveryAddress, city: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Москва"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Улица *</label>
              <input
                type="text"
                value={deliveryAddress.street}
                onChange={(e) => setDeliveryAddress({ ...deliveryAddress, street: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Ленинский проспект"
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Дом *</label>
                <input
                  type="text"
                  value={deliveryAddress.house}
                  onChange={(e) => setDeliveryAddress({ ...deliveryAddress, house: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="15"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Квартира</label>
                <input
                  type="text"
                  value={deliveryAddress.apartment}
                  onChange={(e) => setDeliveryAddress({ ...deliveryAddress, apartment: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="45"
                />
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Комментарий</label>
              <textarea
                value={deliveryAddress.comment}
                onChange={(e) => setDeliveryAddress({ ...deliveryAddress, comment: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                rows="3"
                placeholder="Комментарий к заказу"
              />
            </div>
          </div>
        </div>

        {/* Order Summary */}
        <div className="bg-white rounded-xl p-6 shadow-sm mb-6">
          <div className="flex justify-between items-center mb-4">
            <span className="text-gray-600">Товаров:</span>
            <span className="font-medium">{cart.reduce((sum, item) => sum + item.quantity, 0)} шт</span>
          </div>
          <div className="flex justify-between items-center text-xl font-bold pt-4 border-t border-gray-200">
            <span>Итого:</span>
            <span className="text-blue-600">{total.toLocaleString()} ₽</span>
          </div>
        </div>

        {/* Submit Button */}
        <button
          onClick={handleSubmitOrder}
          disabled={submitting}
          className="w-full bg-blue-500 hover:bg-blue-600 text-white font-medium py-4 rounded-xl flex items-center justify-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors shadow-lg"
        >
          {submitting ? (
            <>
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
              <span>Оформление...</span>
            </>
          ) : (
            <>
              <ShoppingBag size={20} />
              <span>Оформить заказ</span>
            </>
          )}
        </button>

        <p className="text-sm text-gray-600 text-center mt-4">
          После оформления заказ будет отправлен на подтверждение администратору
        </p>
      </div>
    </div>
  );
};

export default CartPage;
