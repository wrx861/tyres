import React, { useState, useEffect } from 'react';
import { ArrowLeft, Package, Clock, CheckCircle, XCircle, Truck } from 'lucide-react';
import { getMyOrders } from '../api/api';

const OrdersPage = ({ user, onBack }) => {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadOrders();
  }, []);

  const loadOrders = async () => {
    try {
      const response = await getMyOrders(user.telegram_id);
      setOrders(response);
    } catch (error) {
      console.error('Ошибка загрузки заказов:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusConfig = (status) => {
    switch (status) {
      case 'pending_confirmation':
        return { icon: Clock, color: 'text-yellow-600 bg-yellow-50', label: 'Ожидает подтверждения' };
      case 'confirmed':
        return { icon: CheckCircle, color: 'text-blue-600 bg-blue-50', label: 'Подтвержден' };
      case 'awaiting_payment':
        return { icon: Clock, color: 'text-yellow-600 bg-yellow-50', label: 'Ожидание оплаты' };
      case 'in_progress':
        return { icon: Truck, color: 'text-blue-600 bg-blue-50', label: 'В работе' };
      case 'delivery':
        return { icon: Truck, color: 'text-purple-600 bg-purple-50', label: 'Доставка' };
      case 'delayed':
        return { icon: Clock, color: 'text-orange-600 bg-orange-50', label: 'Задержка' };
      case 'completed':
        return { icon: CheckCircle, color: 'text-green-600 bg-green-50', label: 'Выполнен' };
      case 'cancelled':
        return { icon: XCircle, color: 'text-red-600 bg-red-50', label: 'Отменен' };
      default:
        return { icon: Package, color: 'text-gray-600 bg-gray-50', label: status };
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="bg-white shadow-sm sticky top-0 z-10">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <div className="flex items-center space-x-4">
            <button onClick={onBack} className="p-2 hover:bg-gray-100 rounded-lg">
              <ArrowLeft size={24} />
            </button>
            <h1 className="text-xl font-bold">Мои заказы</h1>
          </div>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-4 py-6">
        {loading ? (
          <div className="flex justify-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        ) : orders.length === 0 ? (
          <div className="text-center py-12">
            <Package className="mx-auto text-gray-400 mb-4" size={64} />
            <h2 className="text-xl font-semibold text-gray-900 mb-2">Нет заказов</h2>
            <p className="text-gray-600">Вы еще не сделали ни одного заказа</p>
          </div>
        ) : (
          <div className="space-y-4">
            {orders.map((order) => {
              const statusConfig = getStatusConfig(order.status);
              const StatusIcon = statusConfig.icon;
              
              return (
                <div key={order.order_id} className="bg-white rounded-xl p-6 shadow-sm">
                  <div className="flex justify-between items-start mb-4">
                    <div>
                      <p className="text-sm text-gray-600">ID заказа</p>
                      <p className="font-semibold text-gray-900">{order.order_id}</p>
                    </div>
                    <div className={`flex items-center space-x-2 px-3 py-1 rounded-lg ${statusConfig.color}`}>
                      <StatusIcon size={16} />
                      <span className="text-sm font-medium">{statusConfig.label}</span>
                    </div>
                  </div>

                  <div className="space-y-2 mb-4">
                    {order.items.map((item, idx) => (
                      <div key={idx} className="flex justify-between text-sm">
                        <span className="text-gray-700">
                          {item.brand} {item.name} x{item.quantity}
                        </span>
                        <span className="font-medium">{(item.price_final * item.quantity).toLocaleString()} ₽</span>
                      </div>
                    ))}
                  </div>

                  <div className="pt-4 border-t border-gray-200">
                    <div className="flex justify-between items-center">
                      <div>
                        <p className="text-sm text-gray-600">Дата</p>
                        <p className="text-sm font-medium">
                          {new Date(order.created_at).toLocaleDateString('ru-RU', {
                            day: 'numeric',
                            month: 'long',
                            hour: '2-digit',
                            minute: '2-digit'
                          })}
                        </p>
                      </div>
                      <div className="text-right">
                        <p className="text-sm text-gray-600">Итого</p>
                        <p className="text-xl font-bold text-blue-600">{order.total_amount.toLocaleString()} ₽</p>
                      </div>
                    </div>

                    {order.delivery_address && (
                      <div className="mt-3 pt-3 border-t border-gray-100">
                        <p className="text-xs text-gray-600">Адрес доставки:</p>
                        <p className="text-sm text-gray-900">
                          {order.delivery_address.city}, {order.delivery_address.street}, д. {order.delivery_address.house}
                          {order.delivery_address.apartment && `, кв. ${order.delivery_address.apartment}`}
                        </p>
                      </div>
                    )}

                    {order.admin_comment && (
                      <div className="mt-3 pt-3 border-t border-gray-100">
                        <p className="text-xs text-gray-600">Комментарий админа:</p>
                        <p className="text-sm text-gray-900">{order.admin_comment}</p>
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};

export default OrdersPage;
