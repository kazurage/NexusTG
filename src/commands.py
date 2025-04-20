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
    # Только команда start
    app.add_handler(CommandHandler("start", lambda update, context: start_command(update, context, config, message_callback)))
    
    # Обработка сообщений, которые не являются командами
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, 
                                 lambda update, context: handle_message(update, context, config, message_callback)))

# Проверка, является ли пользователь владельцем
def is_owner(update: Update, config: Config) -> bool:
    """Проверка, является ли пользователь владельцем бота"""
    user_id = str(update.effective_user.id)
    return user_id in config.owner_ids

async def start_command(update: Update, context: CallbackContext, config: Config, 
                      message_callback: Optional[Callable[[str], None]] = None):
    """Обработка команды /start"""
    user = update.effective_user
    if not is_owner(update, config):
        await update.message.reply_text(f"Извините, {user.first_name}, у вас нет доступа к этому боту.")
        if message_callback:
            message_callback(f"Попытка доступа от неавторизованного пользователя: {user.first_name} (ID: {user.id})")
        return
    
    await update.message.reply_text(
        f"Привет, {user.first_name}! Я бот для удаленного управления компьютером.\n"
        f"Это учебный проект NexusTG."
    )
    if message_callback:
        message_callback(f"Пользователь {user.first_name} начал использование бота")

async def handle_message(update: Update, context: CallbackContext, config: Config, 
                       message_callback: Optional[Callable[[str], None]] = None):
    """Обработка обычных текстовых сообщений (не команд)"""
    user = update.effective_user
    if not is_owner(update, config):
        await update.message.reply_text(f"Извините, {user.first_name}, у вас нет доступа к этому боту.")
        return
    
    text = update.message.text
    
    # Простой ответ на текстовые сообщения
    await update.message.reply_text(
        f"Получено сообщение: {text}\n\n"
        f"Это учебный проект NexusTG. Доступна только команда /start."
    )
    
    if message_callback:
        message_callback(f"Получено сообщение от {user.first_name}: {text}")
