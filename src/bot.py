
# Модуль для работы с Telegram ботом.
# Обрабатывает подключение к Telegram API, обработку команд и сообщений.

import logging
import asyncio
import httpx
import certifi
import ssl
import os
from typing import List, Optional, Callable
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler, 
    filters, CallbackContext
)
from telegram.request import HTTPXRequest

from src.commands import register_commands
from src.config import Config

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class TelegramBot:
    
    def __init__(self, token: str, owner_ids: List[str]):
        """
        Инициализация бота
        
        Args:
            token: Токен бота, полученный от @BotFather
            owner_ids: Список ID владельцев, которые могут управлять ботом
        """
        self.token = token
        self.owner_ids = owner_ids
        self.application = None
        self.is_running = False
        self.error_callback = None
        self.success_callback = None
        self.message_callback = None
        
    def set_callbacks(self, 
                     error_callback: Optional[Callable[[str], None]] = None,
                     success_callback: Optional[Callable[[str], None]] = None,
                     message_callback: Optional[Callable[[str], None]] = None):
        """
        Установка функций обратного вызова для обработки событий
        
        Args:
            error_callback: Функция для вызова при ошибках
            success_callback: Функция для вызова при успешных операциях
            message_callback: Функция для вызова при получении сообщений
        """
        self.error_callback = error_callback
        self.success_callback = success_callback  
        self.message_callback = message_callback
    
    async def start_bot(self) -> bool:
        """
        Запуск бота
        
        Returns:
            bool: True при успешном запуске, False при ошибке
        """
        try:
            config = Config(self.token, self.owner_ids)
            
            token_valid = await self._validate_token()
            if not token_valid:
                if self.error_callback:
                    self.error_callback("Неверный токен бота. Пожалуйста, проверьте и введите заново.")
                return False

            os.environ['PYTHONHTTPSVERIFY'] = '0'
            
            builder = Application.builder().token(self.token)
            self.application = builder.build()
            
            logger.info("Инициализация бота...")
            if self.message_callback:
                self.message_callback("Инициализация бота...")

            register_commands(self.application, config, self.message_callback)
            
            await self.application.initialize()
            await self.application.start()
            
            await self.application.updater.start_polling(
                allowed_updates=Update.ALL_TYPES,
                drop_pending_updates=True
            )
            
            logger.info("Бот успешно запущен и готов к работе")
            self.is_running = True
            
            if self.success_callback:
                self.success_callback("Бот успешно запущен и готов к работе")
            
            while self.is_running:
                await asyncio.sleep(1)
            
            return True
            
        except Exception as e:
            error_msg = f"Ошибка при запуске бота: {str(e)}"
            logger.error(error_msg)
            if self.error_callback:
                self.error_callback(error_msg)
            return False
    
    async def stop_bot(self):
        if self.application and self.is_running:
            try:
                self.is_running = False
                
                current_loop = asyncio.get_event_loop()
                
                if hasattr(self.application, 'updater') and self.application.updater:
                    try:
                        await self.application.updater.stop()
                    except RuntimeError as e:
                        if "got Future" in str(e) and "attached to a different loop" in str(e):
                            logger.warning("Updater использует другой event loop, отметка как остановленный")
                        else:
                            raise e
                
                try:
                    await self.application.stop()
                except RuntimeError as e:
                    if "got Future" in str(e) and "attached to a different loop" in str(e):
                        logger.warning("Application использует другой event loop, отметка как остановленный")
                    else:
                        raise e
                
                self.application = None
                
                logger.info("Бот остановлен")
                if self.message_callback:
                    self.message_callback("Бот остановлен")
            except RuntimeError as e:
                if "got Future" in str(e) and "attached to a different loop" in str(e):
                    logger.error(f"Ошибка цикла событий: {str(e)}")
                    if self.message_callback:
                        self.message_callback("Бот отмечен как остановленный, но возникла ошибка цикла событий")
                else:
                    logger.error(f"Ошибка при остановке бота: {str(e)}")
                    if self.error_callback:
                        self.error_callback(f"Ошибка при остановке бота: {str(e)}")
            except Exception as e:
                logger.error(f"Непредвиденная ошибка при остановке бота: {str(e)}")
                if self.error_callback:
                    self.error_callback(f"Непредвиденная ошибка при остановке бота: {str(e)}")
                
                self.application = None
    
    async def _validate_token(self) -> bool:
        """
        Проверка валидности токена путем попытки получить информацию о боте
        
        Returns:
            bool: True если токен действителен, False если нет
        """
        try:
            os.environ['PYTHONHTTPSVERIFY'] = '0'
            
            app = Application.builder().token(self.token).build()
            
            await app.initialize()
            me = await app.bot.get_me()
            logger.info(f"Подключен к боту: {me.first_name} (@{me.username})")
            await app.shutdown()
            if self.message_callback:
                self.message_callback(f"Подключен к боту: {me.first_name} (@{me.username})")
            return True
        except Exception as e:
            logger.error(f"Ошибка при проверке токена: {str(e)}")
            return False
