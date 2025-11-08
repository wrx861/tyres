import React, { useState } from 'react';
import { Wrench, Search, ShoppingCart, Package, Settings } from 'lucide-react';

const HomePage = ({ user, onNavigate, cartCount }) => {
  const [showServiceModal, setShowServiceModal] = useState(false);

  const handleServiceClick = () => {
    setShowServiceModal(true);
    setTimeout(() => setShowServiceModal(false), 2000);
  };

  const menuItems = [
    {
      id: 'tire-service',
      title: 'Шиномонтаж',
      description: 'Услуги шиномонтажа',
      icon: Wrench,
      color: 'bg-blue-500',
      onClick: handleServiceClick
    },
    {
      id: 'search',
      title: 'Поиск шин и дисков',
      description: 'Поиск по размерам',
      icon: Search,
      color: 'bg-green-500'
    },
    {
      id: 'cart',
      title: 'Корзина',
      description: `${cartCount} товаров`,
      icon: ShoppingCart,
      color: 'bg-orange-500',
      badge: cartCount
    },
    {
      id: 'orders',
      title: 'Мои заказы',
      description: 'История заказов',
      icon: Package,
      color: 'bg-purple-500'
    }
  ];

  if (user?.is_admin) {
    menuItems.push({
      id: 'admin',
      title: 'Админ-панель',
      description: 'Управление заказами',
      icon: Settings,
      color: 'bg-red-500'
    });
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white dark:from-gray-800 dark:to-gray-900">
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 shadow-sm">
        <div className="max-w-4xl mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Шины и Диски</h1>
              <p className="text-sm text-gray-600 dark:text-gray-300 mt-1">
                Привет, {user?.first_name || user?.username || 'Гость'}!
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Menu Grid */}
      <div className="max-w-4xl mx-auto px-4 py-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {menuItems.map((item) => {
            const Icon = item.icon;
            return (
              <button
                key={item.id}
                onClick={() => item.onClick ? item.onClick() : onNavigate(item.id)}
                className="bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-sm hover:shadow-md transition-all duration-200 text-left relative overflow-hidden group border border-transparent dark:border-gray-700"
              >
                <div className="flex items-start space-x-4">
                  <div className={`${item.color} p-3 rounded-xl text-white group-hover:scale-110 transition-transform`}>
                    <Icon size={24} />
                  </div>
                  <div className="flex-1">
                    <h3 className="font-semibold text-gray-900 dark:text-white text-lg">{item.title}</h3>
                    <p className="text-sm text-gray-600 dark:text-gray-300 mt-1">{item.description}</p>
                  </div>
                  {item.badge > 0 && (
                    <span className="absolute top-4 right-4 bg-orange-500 text-white text-xs font-bold rounded-full w-6 h-6 flex items-center justify-center">
                      {item.badge}
                    </span>
                  )}
                </div>
              </button>
            );
          })}
        </div>

        {/* Info Banner */}
        <div className="mt-8 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-xl p-4">
          <h3 className="font-medium text-blue-900 dark:text-blue-300 mb-2">ℹ️ Информация</h3>
          <p className="text-sm text-blue-800 dark:text-blue-200">
            Выберите товары и оформите заказ. Все заказы проверяются администратором перед отправкой поставщику.
          </p>
        </div>
      </div>

      {/* Service Modal */}
      {showServiceModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 px-4">
          <div className="bg-white dark:bg-gray-800 rounded-2xl p-8 max-w-sm w-full text-center shadow-2xl animate-fade-in border border-transparent dark:border-gray-700">
            <div className="w-16 h-16 bg-blue-100 dark:bg-blue-900/30 rounded-full flex items-center justify-center mx-auto mb-4">
              <Wrench className="text-blue-600 dark:text-blue-400" size={32} />
            </div>
            <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2">Раздел в разработке</h3>
            <p className="text-gray-600 dark:text-gray-300">Услуги шиномонтажа скоро будут доступны!</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default HomePage;
