#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Модуль с командами для Telegram бота.
Здесь определяются все команды, которые бот может выполнять.
"""

import logging
import platform
import os
import socket
import subprocess
import asyncio
from typing import Callable, Optional, Dict, Any
from datetime import datetime
import webbrowser
from PIL import ImageGrab
import io

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

from src.config import Config

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def register_commands(app: Application, config: Config, message_callback: Optional[Callable[[str], None]] = None):
    """
    Регистрация всех команд бота
    
    Args:
        app: Telegram Application
        config: Конфигурация бота
        message_callback: Функция для логирования сообщений
    """
    # Логируем регистрацию команд
    logger.info("Регистрация команд бота")
    if message_callback:
        message_callback("Регистрация команд бота")
    
    # Используем прямые функции вместо lambda для улучшения производительности
    # регистрируем команду /start
    async def start_handler(update, context):
        await start_command(update, context, config, message_callback)
    app.add_handler(CommandHandler("start", start_handler))
    
    # регистрируем обработчик текстовых сообщений
    async def message_handler(update, context):
        await handle_message(update, context, config, message_callback)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    
    # Выводим информацию о зарегистрированных командах
    logger.info("Команды успешно зарегистрированы")

# Проверка, является ли пользователь владельцем
def is_owner(update: Update, config: Config) -> bool:
    """Проверка, является ли пользователь владельцем бота"""
    user_id = str(update.effective_user.id)
    return user_id in config.owner_ids

async def start_command(update: Update, context: CallbackContext, config: Config, 
                      message_callback: Optional[Callable[[str], None]] = None):
    """Обработка команды /start"""
    try:
        user = update.effective_user
        # Проверка прав доступа
        if not is_owner(update, config):
            await update.message.reply_text(
                f"⛔ Извините, {user.first_name}, у вас нет доступа к этому боту.\n\n"
                f"Ваш ID: {user.id} не включен в список авторизованных пользователей."
            )
            if message_callback:
                message_callback(f"Попытка доступа от неавторизованного пользователя: {user.first_name} (ID: {user.id})")
            return
        
        # Информация о компьютере для авторизованного пользователя
        computer_name = socket.gethostname()
        system_info = platform.platform()
        
        # Отправляем подробное приветственное сообщение
        await update.message.reply_text(
            f"👋 Привет, {user.first_name}!\n\n"
            f"✅ Вы успешно подключились к NexusTG.\n\n"
            f"💻 Информация о компьютере:\n"
            f"• Имя: {computer_name}\n"
            f"• Система: {system_info}\n\n"
            f"🕒 Время подключения: {datetime.now().strftime('%H:%M:%S')}\n\n"
            f"ℹ️ В данный момент доступна только команда /start. "
            f"Дополнительные функции будут добавлены в будущих обновлениях."
        )
        
        # Логирование успешного запуска
        if message_callback:
            message_callback(f"Пользователь {user.first_name} (ID: {user.id}) успешно подключился к боту")
    
    except Exception as e:
        # Отправляем сообщение об ошибке пользователю
        error_message = f"Произошла ошибка при обработке команды: {str(e)}"
        try:
            await update.message.reply_text(f"❌ {error_message}")
        except Exception:
            pass  # Если сообщение не удалось отправить, просто игнорируем
        
        # Логируем ошибку
        logger.error(error_message)
        if message_callback:
            message_callback(error_message)

async def handle_message(update: Update, context: CallbackContext, config: Config, 
                       message_callback: Optional[Callable[[str], None]] = None):
    """Обработка обычных текстовых сообщений (не команд)"""
    try:
        user = update.effective_user
        if not is_owner(update, config):
            await update.message.reply_text(
                f"⛔ Извините, {user.first_name}, у вас нет доступа к этому боту.\n\n"
                f"Ваш ID: {user.id} не включен в список авторизованных пользователей."
            )
            return
        
        text = update.message.text
        
        # Улучшенный ответ на текстовые сообщения
        await update.message.reply_text(
            f"📝 Получено сообщение: \"{text}\"\n\n"
            f"ℹ️ В данный момент я поддерживаю только команду /start.\n"
            f"Для получения справки отправьте /start."
        )
        
        if message_callback:
            message_callback(f"Получено сообщение от {user.first_name} (ID: {user.id}): {text}")
    
    except Exception as e:
        # Логирование ошибки
        error_message = f"Ошибка при обработке сообщения: {str(e)}"
        logger.error(error_message)
        if message_callback:
            message_callback(error_message)
        
        # Пытаемся отправить сообщение об ошибке пользователю
        try:
            await update.message.reply_text(f"❌ Произошла ошибка при обработке сообщения.")
        except Exception:
            pass  # Если сообщение не удалось отправить, просто игнорируем
