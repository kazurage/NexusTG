#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Модуль для работы с Telegram ботом.
Обрабатывает подключение к Telegram API, обработку команд и сообщений.
"""

import logging
import asyncio
from typing import List, Optional, Callable
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler, 
    filters, CallbackContext
)

from src.commands import register_commands
from src.config import Config

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class TelegramBot:
    """Основной класс для работы с Telegram ботом"""
    
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
            # Создаем конфигурацию
            config = Config(self.token, self.owner_ids)
            
            # Проверяем валидность токена
            if not await self._validate_token():
                if self.error_callback:
                    self.error_callback("Неверный токен бота. Пожалуйста, проверьте и введите заново.")
                return False
            
            # Создаем приложение с правильными настройками
            builder = Application.builder().token(self.token)
            self.application = builder.build()
            
            # Регистрируем команды
            register_commands(self.application, config, self.message_callback)
            
            # Логируем информацию
            logger.info("Инициализация бота...")
            if self.message_callback:
                self.message_callback("Инициализация бота...")
                
            # Запускаем бота и начинаем обработку обновлений
            await self.application.initialize()
            await self.application.start()
            
            # Запускаем polling - непрерывную проверку новых сообщений от Telegram
            # Это ключевой момент, без которого бот не будет обрабатывать сообщения
            await self.application.updater.start_polling()
            
            logger.info("Бот успешно запущен и готов к работе")
            
            # Устанавливаем флаг, что бот запущен
            self.is_running = True
            
            if self.success_callback:
                self.success_callback("Бот успешно запущен и готов к работе")
                
            return True
            
        except Exception as e:
            logger.error(f"Ошибка при запуске бота: {str(e)}")
            if self.error_callback:
                self.error_callback(f"Ошибка при запуске бота: {str(e)}")
            return False
    
    async def stop_bot(self):
        """Остановка бота"""
        if self.application and self.is_running:
            # Останавливаем polling сначала
            if hasattr(self.application, 'updater') and self.application.updater:
                await self.application.updater.stop()
            
            # Затем останавливаем всё приложение
            await self.application.stop()
            self.is_running = False
            
            logger.info("Бот остановлен")
            if self.message_callback:
                self.message_callback("Бот остановлен")
    
    async def _validate_token(self) -> bool:
        """
        Проверка валидности токена путем попытки получить информацию о боте
        
        Returns:
            bool: True если токен действителен, False если нет
        """
        try:
            # Создаем временное приложение для проверки токена
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
