import React, { useState, useEffect, createContext } from 'react';
import './App.css';
import { authenticateUser, getWarehouses } from './api/api';
import { initTelegramWebApp, getTelegramUser } from './utils/telegram';
import HomePage from './pages/HomePage';
import SearchPage from './pages/SearchPage';
import CarSelectionPage from './pages/CarSelectionPage';
import CartPage from './pages/CartPage';
import OrdersPage from './pages/OrdersPage';
import AdminPage from './pages/AdminPage';

// Контекст для складов
export const WarehousesContext = createContext({});

function App() {
  const [user, setUser] = useState(null);
  const [currentPage, setCurrentPage] = useState('home');
  const [cart, setCart] = useState(() => {
    // Загружаем корзину из localStorage при инициализации
    const savedCart = localStorage.getItem('cart');
    return savedCart ? JSON.parse(savedCart) : [];
  });
  const [loading, setLoading] = useState(true);
  const [warehouses, setWarehouses] = useState({});

  // Сохраняем корзину в localStorage при каждом изменении
  useEffect(() => {
    localStorage.setItem('cart', JSON.stringify(cart));
  }, [cart]);

  useEffect(() => {
    initializeApp();
  }, []);

  const initializeApp = async () => {
    try {
      console.log('🚀 Initializing app...');
      
      // Инициализация Telegram Web App
      const tgInitialized = initTelegramWebApp();
      console.log('📱 Telegram WebApp initialized:', tgInitialized);
      
      // Получаем данные пользователя из Telegram
      const telegramUser = getTelegramUser();
      console.log('👤 Telegram user data:', telegramUser);
      
      if (!telegramUser) {
        console.error('❌ Не удалось получить данные пользователя из Telegram');
        console.error('🔍 Проверьте:');
        console.error('  1. URL в BotFather обновлён на:', window.location.origin);
        console.error('  2. Приложение открыто через Telegram (не браузер)');
        console.error('  3. initDataUnsafe:', window.Telegram?.WebApp?.initDataUnsafe);
        return;
      }
      
      console.log('✅ Telegram user получен:', telegramUser);
      
      // Аутентифицируем пользователя
      try {
        console.log('🔐 Аутентификация пользователя...');
        const authenticatedUser = await authenticateUser(telegramUser);
        setUser(authenticatedUser);
        console.log('✅ User authenticated:', authenticatedUser);
      } catch (authError) {
        console.error('❌ Authentication failed:', authError);
        console.error('Status:', authError.response?.status);
        console.error('Data:', authError.response?.data);
        console.error('Message:', authError.message);
      }

      // Загружаем список складов для маппинга ID -> название города
      try {
        const warehousesData = await getWarehouses();
        const warehouseMap = {};
        
        if (warehousesData.data && warehousesData.data.WarehouseInfo) {
          warehousesData.data.WarehouseInfo.forEach(wh => {
            // Извлекаем город из названия (например, "ОХ г. Сургут..." -> "Сургут")
            const match = wh.name.match(/г\.\s*([А-Яа-яёЁ\s-]+?)(?:\s|$|,|\(|И|О)/);
            let city = match ? match[1].trim() : wh.shortName || `Склад ${wh.id}`;
            
            // Убираем лишние слова после города
            city = city.split(/\s+/).slice(0, 2).join(' '); // Максимум 2 слова
            
            warehouseMap[wh.id] = city;
          });
        }
        
        setWarehouses(warehouseMap);
      } catch (error) {
        console.error('Ошибка загрузки складов:', error);
      }
    } catch (error) {
      console.error('Ошибка инициализации:', error);
    } finally {
      setLoading(false);
    }
  };

  const addToCart = (item) => {
    const qtyToAdd = item.quantity || 1;
    setCart(prev => {
      const existing = prev.find(i => i.code === item.code);
      if (existing) {
        return prev.map(i => 
          i.code === item.code 
            ? { ...i, quantity: i.quantity + qtyToAdd }
            : i
        );
      }
      return [...prev, { ...item, quantity: qtyToAdd }];
    });
  };

  const removeFromCart = (code) => {
    setCart(prev => prev.filter(item => item.code !== code));
  };

  const updateCartQuantity = (code, quantity) => {
    if (quantity <= 0) {
      removeFromCart(code);
    } else {
      setCart(prev => prev.map(item => 
        item.code === code ? { ...item, quantity } : item
      ));
    }
  };

  const clearCart = () => {
    setCart([]);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Загрузка...</p>
        </div>
      </div>
    );
  }

  const renderPage = () => {
    switch (currentPage) {
      case 'home':
        return <HomePage user={user} onNavigate={setCurrentPage} cartCount={cart.length} />;
      case 'search':
        return <SearchPage user={user} onAddToCart={addToCart} onBack={() => setCurrentPage('home')} />;
      case 'car-selection':
        return <CarSelectionPage user={user} onAddToCart={addToCart} onBack={() => setCurrentPage('home')} />;
      case 'cart':
        return (
          <CartPage 
            cart={cart}
            user={user}
            onUpdateQuantity={updateCartQuantity}
            onRemove={removeFromCart}
            onClear={clearCart}
            onBack={() => setCurrentPage('home')}
          />
        );
      case 'orders':
        return <OrdersPage user={user} onBack={() => setCurrentPage('home')} />;
      case 'admin':
        return <AdminPage user={user} onBack={() => setCurrentPage('home')} />;
      default:
        return <HomePage user={user} onNavigate={setCurrentPage} cartCount={cart.length} />;
    }
  };

  return (
    <WarehousesContext.Provider value={warehouses}>
      <div className="min-h-screen bg-gray-50">
        {renderPage()}
      </div>
      
      {/* Debug Info Component */}
      <DebugInfo user={user} />
    </WarehousesContext.Provider>
  );
}

export default App;
