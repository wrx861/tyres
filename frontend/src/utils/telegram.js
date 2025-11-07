/**
 * Утилиты для работы с Telegram Web App
 */

// Получение Telegram Web App объекта
export const getTelegramWebApp = () => {
  if (window.Telegram && window.Telegram.WebApp) {
    return window.Telegram.WebApp;
  }
  return null;
};

// Получение данных пользователя из Telegram
export const getTelegramUser = () => {
  const tg = getTelegramWebApp();
  
  if (tg && tg.initDataUnsafe && tg.initDataUnsafe.user) {
    const user = tg.initDataUnsafe.user;
    return {
      telegram_id: user.id.toString(),
      username: user.username || null,
      first_name: user.first_name || null,
      last_name: user.last_name || null,
      language_code: user.language_code || 'ru'
    };
  }
  
  // Fallback для разработки (если не в Telegram)
  if (process.env.NODE_ENV === 'development') {
    return {
      telegram_id: '508352361', // Ваш тестовый ID
      username: 'testuser',
      first_name: 'Test',
      last_name: 'User',
      language_code: 'ru'
    };
  }
  
  return null;
};

// Инициализация Telegram Web App
export const initTelegramWebApp = () => {
  const tg = getTelegramWebApp();
  
  if (tg) {
    // Растягиваем приложение на весь экран
    tg.expand();
    
    // Включаем подтверждение при закрытии (если есть несохраненные данные)
    // tg.enableClosingConfirmation();
    
    // Устанавливаем цвет темы
    tg.setHeaderColor('#ffffff');
    tg.setBackgroundColor('#f5f5f5');
    
    console.log('Telegram Web App initialized:', {
      version: tg.version,
      platform: tg.platform,
      user: tg.initDataUnsafe?.user
    });
    
    return true;
  }
  
  console.warn('Telegram Web App not available');
  return false;
};

// Проверка, запущено ли приложение в Telegram
export const isTelegramWebApp = () => {
  return !!getTelegramWebApp();
};

// Показать главную кнопку Telegram
export const showMainButton = (text, onClick) => {
  const tg = getTelegramWebApp();
  
  if (tg && tg.MainButton) {
    tg.MainButton.setText(text);
    tg.MainButton.onClick(onClick);
    tg.MainButton.show();
  }
};

// Скрыть главную кнопку Telegram
export const hideMainButton = () => {
  const tg = getTelegramWebApp();
  
  if (tg && tg.MainButton) {
    tg.MainButton.hide();
  }
};

// Показать уведомление
export const showAlert = (message) => {
  const tg = getTelegramWebApp();
  
  if (tg) {
    tg.showAlert(message);
  } else {
    alert(message);
  }
};

// Показать подтверждение
export const showConfirm = (message) => {
  const tg = getTelegramWebApp();
  
  if (tg) {
    return new Promise((resolve) => {
      tg.showConfirm(message, (confirmed) => {
        resolve(confirmed);
      });
    });
  } else {
    return Promise.resolve(window.confirm(message));
  }
};

// Закрыть Mini App
export const closeTelegramWebApp = () => {
  const tg = getTelegramWebApp();
  
  if (tg) {
    tg.close();
  }
};

// Показать всплывающее окно
export const showPopup = (params) => {
  const tg = getTelegramWebApp();
  
  if (tg && tg.showPopup) {
    return new Promise((resolve) => {
      tg.showPopup(params, (buttonId) => {
        resolve(buttonId);
      });
    });
  }
  
  return Promise.resolve(null);
};
