import React, { useState, useEffect } from 'react';
import { ArrowLeft, Check, X, Settings, BarChart3, Users, Activity } from 'lucide-react';
import { getPendingOrders, getAllOrders, confirmOrder, rejectOrder, updateOrderStatus, getMarkup, updateMarkup, getAdminStats, getAllUsers, blockUser, unblockUser, getUserActivity } from '../api/api';

const AdminPage = ({ user, onBack }) => {
  const [tab, setTab] = useState('pending'); // 'pending', 'settings', 'stats', 'users', 'activity'
  const [orders, setOrders] = useState([]);
  const [stats, setStats] = useState(null);
  const [markup, setMarkup] = useState(15);
  const [users, setUsers] = useState([]);
  const [activity, setActivity] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, [tab]);

  const loadData = async () => {
    setLoading(true);
    try {
      if (tab === 'pending') {
        const response = await getAllOrders(user.telegram_id);
        setOrders(response);
      } else if (tab === 'settings') {
        const response = await getMarkup(user.telegram_id);
        setMarkup(response.markup_percentage);
      } else if (tab === 'stats') {
        const response = await getAdminStats(user.telegram_id);
        setStats(response.stats);
      } else if (tab === 'users') {
        const response = await getAllUsers(user.telegram_id);
        setUsers(response.users);
      } else if (tab === 'activity') {
        const response = await getUserActivity(user.telegram_id);
        setActivity(response.logs);
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

  const handleBlockUser = async (userTelegramId) => {
    if (window.confirm('Заблокировать этого пользователя?')) {
      try {
        await blockUser(user.telegram_id, userTelegramId);
        loadData();
        alert('Пользователь заблокирован');
      } catch (error) {
        alert('Ошибка блокировки пользователя');
      }
    }
  };

  const handleUnblockUser = async (userTelegramId) => {
    if (window.confirm('Разблокировать этого пользователя?')) {
      try {
        await unblockUser(user.telegram_id, userTelegramId);
        loadData();
        alert('Пользователь разблокирован');
      } catch (error) {
        alert('Ошибка разблокировки пользователя');
      }
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
          <div className="flex space-x-2 overflow-x-auto">
            <button
              onClick={() => setTab('pending')}
              className={`px-4 py-2 rounded-lg font-medium transition-colors whitespace-nowrap ${
                tab === 'pending' ? 'bg-blue-500 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              Заказы
            </button>
            <button
              onClick={() => setTab('users')}
              className={`px-4 py-2 rounded-lg font-medium transition-colors whitespace-nowrap ${
                tab === 'users' ? 'bg-blue-500 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              Пользователи
            </button>
            <button
              onClick={() => setTab('activity')}
              className={`px-4 py-2 rounded-lg font-medium transition-colors whitespace-nowrap ${
                tab === 'activity' ? 'bg-blue-500 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              Активность
            </button>
            <button
              onClick={() => setTab('stats')}
              className={`px-4 py-2 rounded-lg font-medium transition-colors whitespace-nowrap ${
                tab === 'stats' ? 'bg-blue-500 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              Статистика
            </button>
            <button
              onClick={() => setTab('settings')}
              className={`px-4 py-2 rounded-lg font-medium transition-colors whitespace-nowrap ${
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
                            </p>
                            {order.delivery_address.phone && (
                              <p className="text-sm text-gray-900 mt-1">
                                <span className="font-medium">📞 Телефон:</span> {order.delivery_address.phone}
                              </p>
                            )}
                            {order.delivery_address.comment && (
                              <p className="text-xs text-gray-600 mt-1">Комментарий: {order.delivery_address.comment}</p>
                            )}
                          </div>
                        )}

                        {/* Кнопки действий в зависимости от статуса */}
                        {order.status === 'pending_confirmation' ? (
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
                        ) : (
                          <div className="space-y-3">
                            <p className="text-xs text-gray-600">Изменить статус:</p>
                            <div className="grid grid-cols-2 gap-2">
                              <button
                                onClick={() => handleStatusChange(order.order_id, 'awaiting_payment')}
                                className="bg-yellow-500 hover:bg-yellow-600 text-white py-2 px-3 rounded-lg text-sm font-medium transition-colors"
                              >
                                💳 Ожидание оплаты
                              </button>
                              <button
                                onClick={() => handleStatusChange(order.order_id, 'in_progress')}
                                className="bg-blue-500 hover:bg-blue-600 text-white py-2 px-3 rounded-lg text-sm font-medium transition-colors"
                              >
                                ⚙️ В работе
                              </button>
                              <button
                                onClick={() => handleStatusChange(order.order_id, 'delivery')}
                                className="bg-purple-500 hover:bg-purple-600 text-white py-2 px-3 rounded-lg text-sm font-medium transition-colors"
                              >
                                🚚 Доставка
                              </button>
                              <button
                                onClick={() => handleStatusChange(order.order_id, 'delayed')}
                                className="bg-orange-500 hover:bg-orange-600 text-white py-2 px-3 rounded-lg text-sm font-medium transition-colors"
                              >
                                ⏰ Задержка
                              </button>
                              <button
                                onClick={() => handleStatusChange(order.order_id, 'completed')}
                                className="bg-green-600 hover:bg-green-700 text-white py-2 px-3 rounded-lg text-sm font-medium transition-colors"
                              >
                                ✅ Выполнен
                              </button>
                              <button
                                onClick={() => handleStatusChange(order.order_id, 'cancelled')}
                                className="bg-gray-600 hover:bg-gray-700 text-white py-2 px-3 rounded-lg text-sm font-medium transition-colors"
                              >
                                ❌ Отменить
                              </button>
                            </div>
                          </div>
                        )}
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

            {tab === 'users' && (
              <div className="space-y-4">
                {users.length === 0 ? (
                  <div className="text-center py-12 bg-white rounded-xl">
                    <Users className="mx-auto text-gray-400 mb-4" size={64} />
                    <h2 className="text-xl font-semibold text-gray-900 mb-2">Нет пользователей</h2>
                  </div>
                ) : (
                  users.map((u) => (
                    <div key={u.telegram_id} className="bg-white rounded-xl p-6 shadow-sm">
                      <div className="flex justify-between items-start mb-3">
                        <div>
                          <p className="font-semibold text-lg text-gray-900">
                            {u.first_name} {u.last_name}
                          </p>
                          {u.username && (
                            <p className="text-sm text-gray-600">@{u.username}</p>
                          )}
                          <p className="text-xs text-gray-500 mt-1">ID: {u.telegram_id}</p>
                        </div>
                        <div className="text-right">
                          {u.is_admin && (
                            <span className="inline-block px-3 py-1 bg-purple-100 text-purple-800 text-xs font-semibold rounded-full mb-2">
                              Админ
                            </span>
                          )}
                          {u.is_blocked && (
                            <span className="inline-block px-3 py-1 bg-red-100 text-red-800 text-xs font-semibold rounded-full">
                              Заблокирован
                            </span>
                          )}
                        </div>
                      </div>
                      <div className="flex items-center space-x-4 text-xs text-gray-600 mb-4">
                        <span>Регистрация: {new Date(u.created_at).toLocaleDateString('ru-RU')}</span>
                        {u.last_activity && (
                          <span>Последняя активность: {new Date(u.last_activity).toLocaleDateString('ru-RU')}</span>
                        )}
                      </div>
                      {!u.is_admin && (
                        <button
                          onClick={() => u.is_blocked ? handleUnblockUser(u.telegram_id) : handleBlockUser(u.telegram_id)}
                          className={`w-full py-2 rounded-lg font-medium transition-colors ${
                            u.is_blocked
                              ? 'bg-green-500 hover:bg-green-600 text-white'
                              : 'bg-red-500 hover:bg-red-600 text-white'
                          }`}
                        >
                          {u.is_blocked ? 'Разблокировать' : 'Заблокировать'}
                        </button>
                      )}
                    </div>
                  ))
                )}
              </div>
            )}

            {tab === 'activity' && (
              <div className="space-y-3">
                {activity.length === 0 ? (
                  <div className="text-center py-12 bg-white rounded-xl">
                    <Activity className="mx-auto text-gray-400 mb-4" size={64} />
                    <h2 className="text-xl font-semibold text-gray-900 mb-2">Нет активности</h2>
                  </div>
                ) : (
                  activity.map((log, idx) => (
                    <div key={idx} className="bg-white rounded-lg p-4 shadow-sm">
                      <div className="flex justify-between items-start mb-2">
                        <div>
                          <p className="font-medium text-gray-900">
                            {log.activity_type === 'tire_search' && 'Поиск шин'}
                            {log.activity_type === 'disk_search' && 'Поиск дисков'}
                            {log.activity_type === 'car_selection' && 'Подбор по авто'}
                            {log.activity_type === 'order_created' && 'Создан заказ'}
                            {log.activity_type === 'cart_add' && 'Добавление в корзину'}
                            {log.activity_type === 'cart_remove' && 'Удаление из корзины'}
                          </p>
                          {log.username && (
                            <p className="text-xs text-gray-600">@{log.username} (ID: {log.telegram_id})</p>
                          )}
                        </div>
                        <span className="text-xs text-gray-500">
                          {new Date(log.timestamp).toLocaleString('ru-RU', {
                            day: 'numeric',
                            month: 'short',
                            hour: '2-digit',
                            minute: '2-digit'
                          })}
                        </span>
                      </div>
                      {log.search_params && (
                        <div className="text-xs text-gray-600 mt-2 p-2 bg-gray-50 rounded">
                          {Object.entries(log.search_params).map(([key, value]) => (
                            value !== null && value !== undefined && (
                              <span key={key} className="mr-3">
                                <strong>{key}:</strong> {String(value)}
                              </span>
                            )
                          ))}
                        </div>
                      )}
                      {log.result_count !== null && log.result_count !== undefined && (
                        <p className="text-xs text-green-600 mt-2">
                          Найдено результатов: {log.result_count}
                        </p>
                      )}
                    </div>
                  ))
                )}
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
