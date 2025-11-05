import React, { useState, useEffect } from 'react';
import './App.css';
import { getTelegramUser, authenticateUser } from './api/api';
import HomePage from './pages/HomePage';
import SearchPage from './pages/SearchPage';
import CarSelectionPage from './pages/CarSelectionPage';
import CartPage from './pages/CartPage';
import OrdersPage from './pages/OrdersPage';
import AdminPage from './pages/AdminPage';

function App() {
  const [user, setUser] = useState(null);
  const [currentPage, setCurrentPage] = useState('home');
  const [cart, setCart] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    initializeApp();
  }, []);

  const initializeApp = async () => {
    try {
      // Получаем данные пользователя из Telegram
      const telegramUser = getTelegramUser();
      
      if (telegramUser) {
        // Аутентифицируем пользователя
        const authenticatedUser = await authenticateUser(telegramUser);
        setUser(authenticatedUser);
      }
    } catch (error) {
      console.error('Ошибка инициализации:', error);
    } finally {
      setLoading(false);
    }
  };

  const addToCart = (item) => {
    setCart(prev => {
      const existing = prev.find(i => i.code === item.code);
      if (existing) {
        return prev.map(i => 
          i.code === item.code 
            ? { ...i, quantity: i.quantity + 1 }
            : i
        );
      }
      return [...prev, { ...item, quantity: 1 }];
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
        return <SearchPage onAddToCart={addToCart} onBack={() => setCurrentPage('home')} />;
      case 'car-selection':
        return <CarSelectionPage onAddToCart={addToCart} onBack={() => setCurrentPage('home')} />;
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
    <div className="min-h-screen bg-gray-50">
      {renderPage()}
    </div>
  );
}

export default App;
