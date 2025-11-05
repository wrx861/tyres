import os
import logging
from telegram import Bot
from telegram.error import TelegramError
from typing import Optional

logger = logging.getLogger(__name__)

class TelegramNotifier:
    def __init__(self):
        self.bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
        self.admin_id = os.environ.get('ADMIN_TELEGRAM_ID')
        
        if not self.bot_token:
            logger.warning("TELEGRAM_BOT_TOKEN not set")
            self.bot = None
        else:
            try:
                self.bot = Bot(token=self.bot_token)
                logger.info("Telegram bot initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Telegram bot: {e}")
                self.bot = None
    
    async def send_message(self, chat_id: str, text: str) -> bool:
        """Отправить сообщение пользователю"""
        if not self.bot:
            logger.warning("Bot not initialized, skipping message")
            return False
        
        try:
            await self.bot.send_message(chat_id=chat_id, text=text, parse_mode='HTML')
            logger.info(f"Message sent to {chat_id}")
            return True
        except TelegramError as e:
            logger.error(f"Failed to send message to {chat_id}: {e}")
            return False
    
    async def notify_admin_new_order(
        self, 
        order_id: str, 
        user_name: str, 
        total_amount: float,
        items_count: int
    ) -> bool:
        """Уведомить админа о новом заказе"""
        message = (
            f"🔔 <b>Новый заказ!</b>\n\n"
            f"📦 Заказ: <b>#{order_id}</b>\n"
            f"👤 Клиент: {user_name}\n"
            f"📊 Товаров: {items_count} шт.\n"
            f"💰 Сумма: <b>{total_amount:,.2f} ₽</b>\n\n"
            f"⚡️ Требуется подтверждение в админ-панели"
        )
        return await self.send_message(self.admin_id, message)
    
    async def notify_user_order_confirmed(
        self,
        user_telegram_id: str,
        order_id: str,
        admin_comment: Optional[str] = None
    ) -> bool:
        """Уведомить клиента о подтверждении заказа"""
        message = (
            f"✅ <b>Заказ подтвержден!</b>\n\n"
            f"📦 Заказ: <b>#{order_id}</b>\n"
            f"🚀 Ваш заказ отправлен поставщику\n\n"
        )
        if admin_comment:
            message += f"💬 Комментарий: {admin_comment}\n\n"
        message += "Мы сообщим вам о дальнейших изменениях статуса."
        
        return await self.send_message(user_telegram_id, message)
    
    async def notify_user_order_rejected(
        self,
        user_telegram_id: str,
        order_id: str,
        reason: str
    ) -> bool:
        """Уведомить клиента об отклонении заказа"""
        message = (
            f"❌ <b>Заказ отклонен</b>\n\n"
            f"📦 Заказ: <b>#{order_id}</b>\n"
            f"📝 Причина: {reason}\n\n"
            f"Свяжитесь с нами для уточнения деталей."
        )
        return await self.send_message(user_telegram_id, message)
    
    async def notify_user_order_sent_to_supplier(
        self,
        user_telegram_id: str,
        order_id: str,
        supplier_order_number: str
    ) -> bool:
        """Уведомить клиента об отправке заказа поставщику"""
        message = (
            f"📦 <b>Заказ в обработке</b>\n\n"
            f"📦 Ваш заказ: <b>#{order_id}</b>\n"
            f"🏭 Номер у поставщика: <b>{supplier_order_number}</b>\n\n"
            f"Ожидайте дальнейших обновлений."
        )
        return await self.send_message(user_telegram_id, message)
    
    async def notify_user_order_completed(
        self,
        user_telegram_id: str,
        order_id: str
    ) -> bool:
        """Уведомить клиента о выполнении заказа"""
        message = (
            f"🎉 <b>Заказ выполнен!</b>\n\n"
            f"📦 Заказ: <b>#{order_id}</b>\n\n"
            f"Благодарим за покупку! 🙏"
        )
        return await self.send_message(user_telegram_id, message)

# Singleton instance
telegram_notifier = None

def get_telegram_notifier() -> TelegramNotifier:
    global telegram_notifier
    if telegram_notifier is None:
        telegram_notifier = TelegramNotifier()
    return telegram_notifier
