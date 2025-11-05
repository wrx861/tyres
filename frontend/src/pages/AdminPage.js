import React, { useState, useEffect } from 'react';
import { ArrowLeft, Check, X, Settings, BarChart3 } from 'lucide-react';
import { getPendingOrders, confirmOrder, rejectOrder, getMarkup, updateMarkup, getAdminStats } from '../api/api';

const AdminPage = ({ user, onBack }) => {
  const [tab, setTab] = useState('pending'); // 'pending' or 'settings' or 'stats'
  const [orders, setOrders] = useState([]);
  const [stats, setStats] = useState(null);
  const [markup, setMarkup] = useState(15);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, [tab]);

  const loadData = async () => {
    setLoading(true);
    try {
      if (tab === 'pending') {
        const response = await getPendingOrders(user.telegram_id);
        setOrders(response);
      } else if (tab === 'settings') {
        const response = await getMarkup(user.telegram_id);
        setMarkup(response.markup_percentage);
      } else if (tab === 'stats') {
        const response = await getAdminStats(user.telegram_id);
        setStats(response.stats);
      }
    } catch (error) {
      console.error('Ошибка загрузки данных:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleConfirm = async (orderId) => {
    if (window.confirm('Подтвердить заказ и отправить поставщику?')) {
      try {
        await confirmOrder(orderId, user.telegram_id);
        loadData();
        alert('Заказ подтвержден и отправлен поставщику');
      } catch (error) {
        alert('Ошибка подтверждения заказа');
      }
    }
  };

  const handleReject = async (orderId) => {
    const reason = prompt('Укажите причину отклонения:');
    if (reason) {
      try {
        await rejectOrder(orderId, user.telegram_id, reason);
        loadData();
        alert('Заказ отклонен');
      } catch (error) {
        alert('Ошибка отклонения заказа');
      }
    }
  };

  const handleUpdateMarkup = async () => {
    try {
      await updateMarkup(user.telegram_id, markup);
      alert('Наценка обновлена');
    } catch (error) {
      alert('Ошибка обновления наценки');
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="bg-white shadow-sm sticky top-0 z-10">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <div className="flex items-center space-x-4 mb-4">
            <button onClick={onBack} className="p-2 hover:bg-gray-100 rounded-lg">
              <ArrowLeft size={24} />
            </button>
            <h1 className="text-xl font-bold">Админ-панель</h1>
          </div>
          
          {/* Tabs */}
          <div className="flex space-x-2">
            <button
              onClick={() => setTab('pending')}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                tab === 'pending' ? 'bg-blue-500 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              Заказы
            </button>
            <button
              onClick={() => setTab('stats')}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                tab === 'stats' ? 'bg-blue-500 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              Статистика
            </button>
            <button
              onClick={() => setTab('settings')}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                tab === 'settings' ? 'bg-blue-500 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              Настройки
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-4 py-6">
        {loading ? (
          <div className="flex justify-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        ) : (
          <>
            {tab === 'pending' && (
              <div>
                {orders.length === 0 ? (
                  <div className="text-center py-12">
                    <Check className="mx-auto text-gray-400 mb-4" size={64} />
                    <h2 className="text-xl font-semibold text-gray-900 mb-2">Нет заказов на подтверждение</h2>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {orders.map((order) => (
                      <div key={order.order_id} className="bg-white rounded-xl p-6 shadow-sm">
                        <div className="flex justify-between items-start mb-4">
                          <div>
                            <p className="text-sm text-gray-600">ID заказа</p>
                            <p className="font-semibold text-gray-900">{order.order_id}</p>
                            <p className="text-sm text-gray-600 mt-1">От: {order.user_name}</p>
                          </div>
                          <div className="text-right">
                            <p className="text-2xl font-bold text-blue-600">{order.total_amount.toLocaleString()} ₽</p>
                            <p className="text-xs text-gray-500">
                              {new Date(order.created_at).toLocaleDateString('ru-RU', {
                                day: 'numeric',
                                month: 'short',
                                hour: '2-digit',
                                minute: '2-digit'
                              })}
                            </p>
                          </div>
                        </div>

                        <div className="space-y-2 mb-4">
                          {order.items.map((item, idx) => (
                            <div key={idx} className="flex justify-between text-sm py-2 border-b border-gray-100">
                              <div>
                                <p className="font-medium">{item.brand} {item.name}</p>
                                <p className="text-gray-600 text-xs">
                                  Код: {item.code} | Склад: {item.warehouse_name}
                                </p>
                              </div>
                              <div className="text-right">
                                <p className="font-medium">{item.quantity} шт</p>
                                <p className="text-xs text-gray-600">{item.price_final.toLocaleString()} ₽/шт</p>
                              </div>
                            </div>
                          ))}
                        </div>

                        {order.delivery_address && (
                          <div className="mb-4 p-3 bg-gray-50 rounded-lg">
                            <p className="text-xs text-gray-600 mb-1">Адрес доставки:</p>
                            <p className="text-sm text-gray-900">
                              {order.delivery_address.city}, {order.delivery_address.street}, д. {order.delivery_address.house}
                              {order.delivery_address.apartment && `, кв. ${order.delivery_address.apartment}`}
                            </p>
                            {order.delivery_address.comment && (
                              <p className="text-xs text-gray-600 mt-1">Комментарий: {order.delivery_address.comment}</p>
                            )}
                          </div>
                        )}

                        <div className="flex space-x-3">
                          <button
                            onClick={() => handleConfirm(order.order_id)}
                            className="flex-1 bg-green-500 hover:bg-green-600 text-white py-3 rounded-lg flex items-center justify-center space-x-2 font-medium transition-colors"
                          >
                            <Check size={20} />
                            <span>Подтвердить</span>
                          </button>
                          <button
                            onClick={() => handleReject(order.order_id)}
                            className="flex-1 bg-red-500 hover:bg-red-600 text-white py-3 rounded-lg flex items-center justify-center space-x-2 font-medium transition-colors"
                          >
                            <X size={20} />
                            <span>Отклонить</span>
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {tab === 'stats' && stats && (
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-white rounded-xl p-6 shadow-sm">
                  <p className="text-sm text-gray-600 mb-2">Всего заказов</p>
                  <p className="text-3xl font-bold text-blue-600">{stats.total_orders}</p>
                </div>
                <div className="bg-white rounded-xl p-6 shadow-sm">
                  <p className="text-sm text-gray-600 mb-2">На подтверждении</p>
                  <p className="text-3xl font-bold text-yellow-600">{stats.pending_orders}</p>
                </div>
                <div className="bg-white rounded-xl p-6 shadow-sm">
                  <p className="text-sm text-gray-600 mb-2">Выполнено</p>
                  <p className="text-3xl font-bold text-green-600">{stats.completed_orders}</p>
                </div>
                <div className="bg-white rounded-xl p-6 shadow-sm">
                  <p className="text-sm text-gray-600 mb-2">Отменено</p>
                  <p className="text-3xl font-bold text-red-600">{stats.cancelled_orders}</p>
                </div>
                <div className="bg-white rounded-xl p-6 shadow-sm col-span-2">
                  <p className="text-sm text-gray-600 mb-2">Общая сумма</p>
                  <p className="text-4xl font-bold text-blue-600">{stats.total_revenue.toLocaleString()} ₽</p>
                </div>
                <div className="bg-white rounded-xl p-6 shadow-sm col-span-2">
                  <p className="text-sm text-gray-600 mb-2">Пользователей</p>
                  <p className="text-3xl font-bold text-purple-600">{stats.total_users}</p>
                </div>
              </div>
            )}

            {tab === 'settings' && (
              <div className="bg-white rounded-xl p-6 shadow-sm">
                <h3 className="font-semibold text-lg mb-4">Наценка на товары</h3>
                <div className="mb-6">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Процент наценки (%)
                  </label>
                  <input
                    type="number"
                    value={markup}
                    onChange={(e) => setMarkup(parseFloat(e.target.value))}
                    min="0"
                    max="100"
                    step="0.1"
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-lg"
                  />
                  <p className="text-sm text-gray-600 mt-2">
                    Текущая наценка: {markup}%
                  </p>
                </div>
                <button
                  onClick={handleUpdateMarkup}
                  className="w-full bg-blue-500 hover:bg-blue-600 text-white font-medium py-3 rounded-lg flex items-center justify-center space-x-2 transition-colors"
                >
                  <Settings size={20} />
                  <span>Сохранить</span>
                </button>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default AdminPage;
