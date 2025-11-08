import React from 'react';
import { MessageCircle } from 'lucide-react';

const SupportButton = () => {
  const handleSupportClick = () => {
    // Проверяем доступен ли Telegram WebApp
    if (window.Telegram && window.Telegram.WebApp) {
      // Показываем confirm вместо alert (с кнопками)
      const message = 
        '💬 Поддержка\n\n' +
        'Для связи с администратором напишите сообщение прямо в этого бота.\n\n' +
        'Ваше сообщение будет автоматически переслано администратору, и он ответит вам в течение нескольких минут.\n\n' +
        'Закрыть приложение чтобы написать боту?';
      
      // Используем confirm
      window.Telegram.WebApp.showConfirm(
        message,
        (confirmed) => {
          if (confirmed) {
            // Пользователь нажал OK - закрываем Mini App
            window.Telegram.WebApp.close();
          }
          // Если нажал Cancel - ничего не делаем, остаёмся в Mini App
        }
      );
    } else {
      // Fallback для браузера
      const result = window.confirm(
        '💬 Поддержка\n\n' +
        'Для связи с администратором:\n\n' +
        '1. Откройте бота в Telegram\n' +
        '2. Напишите сообщение\n' +
        '3. Ваше сообщение будет переслано администратору\n\n' +
        'Это работает только в Telegram.'
      );
      
      if (result && window.Telegram && window.Telegram.WebApp) {
        window.Telegram.WebApp.close();
      }
    }
  };

  return (
    <button
      onClick={handleSupportClick}
      className="fixed bottom-4 right-4 bg-blue-500 hover:bg-blue-600 text-white px-3 py-2 rounded-full shadow-lg flex items-center space-x-1.5 transition-all hover:scale-105 z-50"
      aria-label="Вопрос"
      title="Связаться с поддержкой"
    >
      <MessageCircle size={18} />
      <span className="font-medium text-sm">Вопрос</span>
    </button>
  );
};

export default SupportButton;
