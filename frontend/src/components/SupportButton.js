import React from 'react';
import { MessageCircle } from 'lucide-react';

const SupportButton = () => {
  const handleSupportClick = () => {
    // ID админа из .env или константа
    const ADMIN_TELEGRAM_ID = '508352361';
    
    // Открываем чат с админом через tg://user?id=
    // Это работает в мобильном Telegram
    const telegramUrl = `tg://user?id=${ADMIN_TELEGRAM_ID}`;
    
    // Пробуем открыть
    window.open(telegramUrl, '_blank');
    
    // Если не сработало (веб версия), показываем инструкцию
    setTimeout(() => {
      if (window.Telegram && window.Telegram.WebApp) {
        // Показываем alert с инструкцией
        window.Telegram.WebApp.showAlert(
          'Для связи с поддержкой:\n\n' +
          '1. Напишите сообщение прямо в этот бот\n' +
          '2. Ваше сообщение будет автоматически переслано администратору\n' +
          '3. Администратор ответит вам через бота',
          () => {}
        );
      }
    }, 500);
  };

  return (
    <button
      onClick={handleSupportClick}
      className="fixed bottom-4 right-4 bg-blue-500 hover:bg-blue-600 text-white px-4 py-3 rounded-full shadow-lg flex items-center space-x-2 transition-all hover:scale-105 z-50"
      aria-label="Поддержка"
    >
      <MessageCircle size={20} />
      <span className="font-medium">Поддержка</span>
    </button>
  );
};

export default SupportButton;
