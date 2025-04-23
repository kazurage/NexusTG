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
import sys
import time
import pyautogui
import psutil
import re
import signal
import json
import urllib.request
import ctypes

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
    
    # Создаем обработчики команд
    async def start_command_handler(update: Update, context: CallbackContext):
        await start_command(update, context, config, message_callback)

    async def screenshot_command_handler(update: Update, context: CallbackContext):
        await screenshot_command(update, context, config, message_callback)
    
    async def ping_command_handler(update: Update, context: CallbackContext):
        await ping_command(update, context, config, message_callback)
    
    async def help_command_handler(update: Update, context: CallbackContext):
        await help_command(update, context, config, message_callback)
    
    async def cpu_command_handler(update: Update, context: CallbackContext):
        await cpu_command(update, context, config, message_callback)
    
    async def ram_command_handler(update: Update, context: CallbackContext):
        await ram_command(update, context, config, message_callback)
    
    async def ps_command_handler(update: Update, context: CallbackContext):
        await ps_command(update, context, config, message_callback)
    
    async def kill_command_handler(update: Update, context: CallbackContext):
        await kill_command(update, context, config, message_callback)
    
    async def ip_command_handler(update: Update, context: CallbackContext):
        await ip_command(update, context, config, message_callback)
    
    async def lock_command_handler(update: Update, context: CallbackContext):
        await lock_command(update, context, config, message_callback)
    
    async def shutdown_command_handler(update: Update, context: CallbackContext):
        await shutdown_command(update, context, config, message_callback)

    async def message_handler(update: Update, context: CallbackContext):
        await handle_message(update, context, config, message_callback)

    # Регистрируем обработчики
    app.add_handler(CommandHandler("start", start_command_handler))
    app.add_handler(CommandHandler("screenshot", screenshot_command_handler))
    app.add_handler(CommandHandler("ping", ping_command_handler))
    app.add_handler(CommandHandler("help", help_command_handler))
    app.add_handler(CommandHandler("cpu", cpu_command_handler))
    app.add_handler(CommandHandler("ram", ram_command_handler))
    app.add_handler(CommandHandler("ps", ps_command_handler))
    app.add_handler(CommandHandler("kill", kill_command_handler))
    app.add_handler(CommandHandler("ip", ip_command_handler))
    app.add_handler(CommandHandler("lock", lock_command_handler))
    app.add_handler(CommandHandler("shutdown", shutdown_command_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    
    logger.info("Команды успешно зарегистрированы")
    if message_callback:
        message_callback("Команды бота успешно зарегистрированы")

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
            "🔧 Список команд можно узнать по команде /help"
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
        
        # Улучшенный ответ на текстовые сообщения с группировкой по категориям
        await update.message.reply_text(
            f"📝 Получено сообщение: \"{text}\"\n\n"
            f"ℹ️ Доступные команды по категориям:\n\n"
            
            f"🔷 ОСНОВНЫЕ\n"
            f"• /start - начало работы\n"
            f"• /help - справка\n\n"
            
            f"📊 МОНИТОРИНГ\n"
            f"• /cpu - загрузка CPU\n"
            f"• /ram - использование RAM\n"
            f"• /ping - проверка сети\n"
            f"• /ip - IP адреса\n\n"
            
            f"⚙️ ПРОЦЕССЫ\n"
            f"• /ps - список программ\n"
            f"• /kill - закрыть программу\n\n"
            
            f"🔒 УПРАВЛЕНИЕ ПК\n"
            f"• /lock - блокировка экрана\n"
            f"• /shutdown - выключение ПК\n\n"
            
            f"🛠️ ДОПОЛНИТЕЛЬНО\n"
            f"• /screenshot - скриншот экрана"
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

async def screenshot_command(update: Update, context: CallbackContext, config: Config,
                           message_callback: Optional[Callable[[str], None]] = None):
    """Обработка команды /screenshot - делает скриншот экрана и определяет активное окно"""
    try:
        user = update.effective_user
        
        # Проверка прав доступа
        if not is_owner(update, config):
            await update.message.reply_text(
                f"⛔ Извините, {user.first_name}, у вас нет доступа к этому боту.\n\n"
                f"Ваш ID: {user.id} не включен в список авторизованных пользователей."
            )
            if message_callback:
                message_callback(f"Попытка доступа к команде /screenshot от неавторизованного пользователя: {user.first_name} (ID: {user.id})")
            return
        
        # Сообщаем, что команда в процессе выполнения
        processing_message = await update.message.reply_text("📸 Создание скриншота...")
        
        # Определяем активное окно (только для Windows)
        window_info = "Неизвестное окно"
        if sys.platform == 'win32':
            try:
                # Используем PowerShell для получения имени активного окна
                command = """
                Add-Type @"
                    using System;
                    using System.Runtime.InteropServices;
                    public class WindowInfo {
                        [DllImport("user32.dll")]
                        public static extern IntPtr GetForegroundWindow();
                        [DllImport("user32.dll")]
                        public static extern int GetWindowText(IntPtr hWnd, System.Text.StringBuilder text, int count);
                        [DllImport("user32.dll")]
                        public static extern int GetWindowThreadProcessId(IntPtr hWnd, out int processId);
                    }
"@
                $hwnd = [WindowInfo]::GetForegroundWindow()
                $process_id = 0
                [WindowInfo]::GetWindowThreadProcessId($hwnd, [ref]$process_id)
                $process = Get-Process -Id $process_id
                $window_title = New-Object System.Text.StringBuilder 256
                [WindowInfo]::GetWindowText($hwnd, $window_title, 256)
                $window_title.ToString() + " (" + $process.ProcessName + ".exe)"
                """
                
                window_info = subprocess.check_output(["powershell", "-Command", command], text=True).strip()
                
                # Извлекаем только имя процесса из полного названия окна
                # Формат: "Название окна (процесс.exe)" -> "процесс.exe"
                if "(" in window_info and ")" in window_info:
                    process_name = window_info.split("(")[-1].replace(")", "")
                    window_info = process_name
            except Exception as e:
                logger.error(f"Ошибка при определении активного окна: {e}")
                window_info = "Ошибка при определении активного окна"
        else:
            window_info = "Определение активного окна поддерживается только в Windows"
        
        # Делаем скриншот
        try:
            # Создаем уникальное имя файла
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            filename = f"screenshot_{timestamp}.png"
            filepath = os.path.join(os.getcwd(), filename)
            
            # Делаем скриншот с помощью pyautogui
            screenshot = pyautogui.screenshot()
            screenshot.save(filepath)
            
            # Логируем информацию
            log_message = f"Создан скриншот: {filename}, активное окно: {window_info}"
            if message_callback:
                message_callback(log_message)
            
            # Отправляем скриншот и информацию пользователю
            with open(filepath, 'rb') as photo:
                await update.message.reply_photo(
                    photo=photo,
                    caption=f"🖥️ Активный процесс: {window_info}"
                )
            
            # Удаляем временное сообщение о создании скриншота
            await processing_message.delete()
            
            # Удаляем файл скриншота после отправки
            try:
                os.remove(filepath)
                if message_callback:
                    message_callback(f"Файл скриншота удален: {filename}")
            except Exception as e:
                if message_callback:
                    message_callback(f"Ошибка при удалении файла скриншота: {str(e)}")
            
        except Exception as e:
            await processing_message.edit_text(f"❌ Ошибка при создании скриншота: {str(e)}")
            if message_callback:
                message_callback(f"Ошибка при создании скриншота: {str(e)}")
    
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

async def ping_command(update: Update, context: CallbackContext, config: Config,
                     message_callback: Optional[Callable[[str], None]] = None):
    """Обработка команды /ping - проверка скорости отклика"""
    try:
        user = update.effective_user
        
        # Проверка прав доступа
        if not is_owner(update, config):
            await update.message.reply_text(
                f"⛔ Извините, {user.first_name}, у вас нет доступа к этому боту.\n\n"
                f"Ваш ID: {user.id} не включен в список авторизованных пользователей."
            )
            if message_callback:
                message_callback(f"Попытка доступа к команде /ping от неавторизованного пользователя: {user.first_name} (ID: {user.id})")
            return
        
        # Замеряем время начала обработки
        start_time = time.time()
        
        # Отправляем временное сообщение
        message = await update.message.reply_text("🔄 Проверка подключения...")
        
        # Измеряем пинг до google.com
        ping_result = "Недоступно"
        try:
            if sys.platform == 'win32':
                # Windows
                ping_process = subprocess.run(
                    ['ping', '-n', '3', 'google.com'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                output = ping_process.stdout
                
                # Извлекаем среднее время из вывода команды
                if "Average" in output:
                    avg_time = output.split("Average =")[1].split("ms")[0].strip()
                    ping_result = f"{avg_time} мс"
            else:
                # Linux/Mac
                ping_process = subprocess.run(
                    ['ping', '-c', '3', 'google.com'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                output = ping_process.stdout
                
                # Извлекаем среднее время из вывода команды
                if "avg" in output:
                    avg_line = output.split("min/avg/max")[1]
                    avg_time = avg_line.split("/")[1].strip()
                    ping_result = f"{avg_time} мс"
        except Exception as e:
            ping_result = f"Ошибка: {str(e)}"
            
        # Считаем общее время выполнения команды
        end_time = time.time()
        execution_time = round((end_time - start_time) * 1000, 2)  # в миллисекундах
        
        # Обновляем сообщение с результатами
        await message.edit_text(
            f"✅ Проверка подключения завершена\n\n"
            f"🔹 Время обработки команды: {execution_time} мс\n"
            f"🔹 Пинг до google.com: {ping_result}\n"
            f"🔹 Статус NexusTG: Онлайн"
        )
        
        # Логируем информацию
        if message_callback:
            message_callback(f"Пинг проверен: {ping_result}, время обработки: {execution_time} мс")
            
    except Exception as e:
        # Отправляем сообщение об ошибке пользователю
        error_message = f"Произошла ошибка при проверке пинга: {str(e)}"
        try:
            await update.message.reply_text(f"❌ {error_message}")
        except Exception:
            pass
        
        # Логируем ошибку
        logger.error(error_message)
        if message_callback:
            message_callback(error_message)

async def help_command(update: Update, context: CallbackContext, config: Config,
                     message_callback: Optional[Callable[[str], None]] = None):
    """Обработка команды /help - показывает справку по доступным командам"""
    try:
        user = update.effective_user
        
        # Проверка прав доступа
        if not is_owner(update, config):
            await update.message.reply_text(
                f"⛔ Извините, {user.first_name}, у вас нет доступа к этому боту.\n\n"
                f"Ваш ID: {user.id} не включен в список авторизованных пользователей."
            )
            if message_callback:
                message_callback(f"Попытка доступа к команде /help от неавторизованного пользователя: {user.first_name} (ID: {user.id})")
            return
        
        # Отправляем справку по командам, сгруппированным по категориям
        await update.message.reply_text(
            f"📋 Справка по командам NexusTG\n\n"
            
            f"🔷 *ОСНОВНЫЕ КОМАНДЫ*\n"
            f"• /start - начало работы с ботом\n"
            f"• /help - показать это сообщение\n\n"
            
            f"📊 *МОНИТОРИНГ СИСТЕМЫ*\n"
            f"• /cpu - информация о загрузке процессора\n"
            f"• /ram - информация об использовании памяти\n"
            f"• /ping - проверка скорости отклика сети\n"
            f"• /ip - локальный и внешний IP с геолокацией\n\n"
            
            f"⚙️ *УПРАВЛЕНИЕ ПРОЦЕССАМИ*\n"
            f"• /ps - список запущенных программ\n"
            f"• /kill <program.exe> - закрыть программу\n\n"
            
            f"🔒 *УПРАВЛЕНИЕ КОМПЬЮТЕРОМ*\n"
            f"• /lock - блокировка экрана (Win+L)\n"
            f"• /shutdown - выключение компьютера\n\n"
            
            f"🛠️ *ДОПОЛНИТЕЛЬНЫЕ ФУНКЦИИ*\n"
            f"• /screenshot - создание скриншота экрана\n\n"
            
            f"📱 Версия: 1.0\n"
            f"📅 Дата обновления: {time.strftime('%d.%m.%Y')}"
        )
        
        # Логируем запрос справки
        if message_callback:
            message_callback(f"Пользователь {user.first_name} (ID: {user.id}) запросил справку")
            
    except Exception as e:
        # Отправляем сообщение об ошибке пользователю
        error_message = f"Произошла ошибка при получении справки: {str(e)}"
        try:
            await update.message.reply_text(f"❌ {error_message}")
        except Exception:
            pass
        
        # Логируем ошибку
        logger.error(error_message)
        if message_callback:
            message_callback(error_message)

async def cpu_command(update: Update, context: CallbackContext, config: Config,
                    message_callback: Optional[Callable[[str], None]] = None):
    """Обработка команды /cpu - показывает текущую загрузку процессора"""
    try:
        user = update.effective_user
        
        # Проверка прав доступа
        if not is_owner(update, config):
            await update.message.reply_text(
                f"⛔ Извините, {user.first_name}, у вас нет доступа к этому боту.\n\n"
                f"Ваш ID: {user.id} не включен в список авторизованных пользователей."
            )
            if message_callback:
                message_callback(f"Попытка доступа к команде /cpu от неавторизованного пользователя: {user.first_name} (ID: {user.id})")
            return
        
        # Замеряем время начала обработки
        start_time = time.time()
        
        # Отправляем временное сообщение
        message = await update.message.reply_text("🔄 Получение информации о процессоре...")
        
        # Собираем информацию о процессоре
        try:
            # Получаем загрузку CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Получаем температуру CPU (если доступна)
            cpu_temp = "Нет данных"
            if hasattr(psutil, "sensors_temperatures"):
                temps = psutil.sensors_temperatures()
                if temps:
                    for name, entries in temps.items():
                        if entries:
                            cpu_temp = f"{entries[0].current}°C"
                            break
            
            # Получаем информацию о процессоре из системы
            cpu_info = "Нет данных"
            if platform.system() == "Windows":
                try:
                    cpu_info = subprocess.check_output("wmic cpu get name", shell=True).decode().strip()
                    cpu_info = cpu_info.split("\n")[1]
                except:
                    pass
            elif platform.system() == "Linux":
                try:
                    cpu_info = subprocess.check_output("cat /proc/cpuinfo | grep 'model name' | head -1", shell=True).decode().strip()
                    cpu_info = cpu_info.split(":")[1].strip()
                except:
                    pass
            elif platform.system() == "Darwin":  # macOS
                try:
                    cpu_info = subprocess.check_output("sysctl -n machdep.cpu.brand_string", shell=True).decode().strip()
                except:
                    pass
                    
            # Получаем количество ядер
            cpu_cores = psutil.cpu_count(logical=False)
            cpu_threads = psutil.cpu_count(logical=True)
            
            # Получаем загрузку по каждому ядру
            per_cpu = psutil.cpu_percent(percpu=True)
            per_cpu_text = "\n".join([f"• Ядро {i+1}: {p}%" for i, p in enumerate(per_cpu)])
            
            # Получаем информацию о процессах, потребляющих больше всего CPU
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
                try:
                    processes.append((proc.info['pid'], proc.info['name'], proc.info['cpu_percent']))
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
            
            top_processes = sorted(processes, key=lambda x: x[2], reverse=True)[:3]
            top_processes_text = "\n".join([f"• {name} (PID: {pid}): {cpu:.1f}%" for pid, name, cpu in top_processes])
            
            # Считаем общее время выполнения команды
            end_time = time.time()
            execution_time = round((end_time - start_time) * 1000, 2)  # в миллисекундах
            
            # Обновляем сообщение с результатами
            await message.edit_text(
                f"💻 Информация о процессоре\n\n"
                f"📊 Общая загрузка: {cpu_percent}%\n"
                f"🔥 Температура: {cpu_temp}\n"
                f"🧠 Процессор: {cpu_info}\n"
                f"⚙️ Ядер: {cpu_cores}, Потоков: {cpu_threads}\n\n"
                f"📈 Загрузка по ядрам:\n{per_cpu_text}\n\n"
                f"🔝 Топ процессов по CPU:\n{top_processes_text}\n\n"
                f"⏱️ Время выполнения: {execution_time} мс"
            )
            
            # Логируем информацию
            if message_callback:
                message_callback(f"Информация о CPU отправлена, загрузка: {cpu_percent}%")
                
        except Exception as e:
            await message.edit_text(f"❌ Ошибка при получении информации о процессоре: {str(e)}")
            if message_callback:
                message_callback(f"Ошибка при получении информации о CPU: {str(e)}")
            
    except Exception as e:
        # Отправляем сообщение об ошибке пользователю
        error_message = f"Произошла ошибка при обработке команды: {str(e)}"
        try:
            await update.message.reply_text(f"❌ {error_message}")
        except Exception:
            pass
        
        # Логируем ошибку
        logger.error(error_message)
        if message_callback:
            message_callback(error_message)

async def ram_command(update: Update, context: CallbackContext, config: Config,
                    message_callback: Optional[Callable[[str], None]] = None):
    """Обработка команды /ram - показывает использование оперативной памяти"""
    try:
        user = update.effective_user
        
        # Проверка прав доступа
        if not is_owner(update, config):
            await update.message.reply_text(
                f"⛔ Извините, {user.first_name}, у вас нет доступа к этому боту.\n\n"
                f"Ваш ID: {user.id} не включен в список авторизованных пользователей."
            )
            if message_callback:
                message_callback(f"Попытка доступа к команде /ram от неавторизованного пользователя: {user.first_name} (ID: {user.id})")
            return
        
        # Замеряем время начала обработки
        start_time = time.time()
        
        # Отправляем временное сообщение
        message = await update.message.reply_text("🔄 Получение информации о памяти...")
        
        # Собираем информацию о памяти
        try:
            # Получаем виртуальную память (RAM)
            virtual_memory = psutil.virtual_memory()
            
            # Преобразуем байты в более читаемый формат
            def get_size(bytes, suffix="B"):
                factor = 1024
                for unit in ["", "K", "M", "G", "T", "P"]:
                    if bytes < factor:
                        return f"{bytes:.2f} {unit}{suffix}"
                    bytes /= factor
                return f"{bytes:.2f} {suffix}"
            
            # Получаем информацию о файле подкачки (swap)
            swap = psutil.swap_memory()
            
            # Получаем информацию о процессах, потребляющих больше всего RAM
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'memory_percent']):
                try:
                    processes.append((proc.info['pid'], proc.info['name'], proc.info['memory_percent']))
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
            
            top_processes = sorted(processes, key=lambda x: x[2], reverse=True)[:3]
            top_processes_text = "\n".join([f"• {name} (PID: {pid}): {ram:.1f}%" for pid, name, ram in top_processes])
            
            # Считаем общее время выполнения команды
            end_time = time.time()
            execution_time = round((end_time - start_time) * 1000, 2)  # в миллисекундах
            
            # Создаем визуальную полосу загрузки
            progress_length = 20
            used_blocks = int(virtual_memory.percent / 100 * progress_length)
            progress_bar = "🟦" * used_blocks + "⬜" * (progress_length - used_blocks)
            
            # Обновляем сообщение с результатами
            await message.edit_text(
                f"🧠 Информация об оперативной памяти\n\n"
                f"📊 Использование RAM: {virtual_memory.percent}%\n"
                f"{progress_bar}\n\n"
                f"💾 Всего: {get_size(virtual_memory.total)}\n"
                f"📈 Используется: {get_size(virtual_memory.used)}\n"
                f"📉 Свободно: {get_size(virtual_memory.available)}\n\n"
                f"🔄 Файл подкачки (SWAP):\n"
                f"• Всего: {get_size(swap.total)}\n"
                f"• Используется: {get_size(swap.used)} ({swap.percent}%)\n\n"
                f"🔝 Топ процессов по RAM:\n{top_processes_text}\n\n"
                f"⏱️ Время выполнения: {execution_time} мс"
            )
            
            # Логируем информацию
            if message_callback:
                message_callback(f"Информация о RAM отправлена, использование: {virtual_memory.percent}%")
                
        except Exception as e:
            await message.edit_text(f"❌ Ошибка при получении информации о памяти: {str(e)}")
            if message_callback:
                message_callback(f"Ошибка при получении информации о RAM: {str(e)}")
            
    except Exception as e:
        # Отправляем сообщение об ошибке пользователю
        error_message = f"Произошла ошибка при обработке команды: {str(e)}"
        try:
            await update.message.reply_text(f"❌ {error_message}")
        except Exception:
            pass
        
        # Логируем ошибку
        logger.error(error_message)
        if message_callback:
            message_callback(error_message)

async def ps_command(update: Update, context: CallbackContext, config: Config,
                   message_callback: Optional[Callable[[str], None]] = None):
    """Обработка команды /ps - показывает список запущенных программ"""
    try:
        user = update.effective_user
        
        # Проверка прав доступа
        if not is_owner(update, config):
            await update.message.reply_text(
                f"⛔ Извините, {user.first_name}, у вас нет доступа к этому боту.\n\n"
                f"Ваш ID: {user.id} не включен в список авторизованных пользователей."
            )
            if message_callback:
                message_callback(f"Попытка доступа к команде /ps от неавторизованного пользователя: {user.first_name} (ID: {user.id})")
            return
        
        # Отправляем временное сообщение
        message = await update.message.reply_text("🔄 Получение списка запущенных программ...")
        
        try:
            # Получаем все запущенные процессы с информацией о CPU, RAM и имени
            start_time = time.time()
            process_list = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
                try:
                    # Фильтруем только запущенные программы (не системные процессы)
                    if proc.info['status'] == 'running' and proc.info['name'].endswith('.exe'):
                        process_list.append({
                            'pid': proc.info['pid'],
                            'name': proc.info['name'],
                            'cpu': proc.info['cpu_percent'],
                            'memory': proc.info['memory_percent']
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
            
            # Сортируем по использованию памяти
            process_list = sorted(process_list, key=lambda x: x['memory'], reverse=True)
            
            # Отображаем только первые 20 процессов, чтобы не перегружать сообщение
            max_programs = min(20, len(process_list))
            
            # Форматируем вывод
            process_text = "\n".join([
                f"• {i+1}. {p['name']} - RAM: {p['memory']:.1f}%, CPU: {p['cpu']:.1f}%, PID: {p['pid']}"
                for i, p in enumerate(process_list[:max_programs])
            ])
            
            # Время выполнения
            execution_time = round((time.time() - start_time) * 1000, 2)
            
            # Проверяем, есть ли что отображать
            if not process_list:
                await message.edit_text("❌ Не удалось получить список запущенных программ.")
                return
            
            # Общее количество программ
            total_count = len(process_list)
            
            # Обновляем сообщение
            await message.edit_text(
                f"📋 Список запущенных программ ({total_count} всего)\n\n"
                f"{process_text}\n\n"
                f"ℹ️ Для закрытия программы используйте:\n"
                f"/kill program.exe\n\n"
                f"⏱️ Время выполнения: {execution_time} мс"
            )
            
            # Логируем информацию
            if message_callback:
                message_callback(f"Отправлен список запущенных программ ({total_count} всего)")
            
        except Exception as e:
            await message.edit_text(f"❌ Ошибка при получении списка программ: {str(e)}")
            if message_callback:
                message_callback(f"Ошибка при выполнении команды /ps: {str(e)}")
    
    except Exception as e:
        # Отправляем сообщение об ошибке пользователю
        error_message = f"Произошла ошибка при обработке команды: {str(e)}"
        try:
            await update.message.reply_text(f"❌ {error_message}")
        except Exception:
            pass
        
        # Логируем ошибку
        logger.error(error_message)
        if message_callback:
            message_callback(error_message)

async def kill_command(update: Update, context: CallbackContext, config: Config,
                     message_callback: Optional[Callable[[str], None]] = None):
    """Обработка команды /kill - закрывает указанную программу"""
    try:
        user = update.effective_user
        
        # Проверка прав доступа
        if not is_owner(update, config):
            await update.message.reply_text(
                f"⛔ Извините, {user.first_name}, у вас нет доступа к этому боту.\n\n"
                f"Ваш ID: {user.id} не включен в список авторизованных пользователей."
            )
            if message_callback:
                message_callback(f"Попытка доступа к команде /kill от неавторизованного пользователя: {user.first_name} (ID: {user.id})")
            return
        
        # Проверяем, указан ли аргумент (имя программы)
        args = context.args
        if not args:
            await update.message.reply_text(
                "❌ Необходимо указать имя программы для закрытия.\n\n"
                "Пример использования:\n"
                "/kill program.exe\n\n"
                "Чтобы получить список запущенных программ, используйте команду /ps"
            )
            return
        
        # Получаем имя программы из аргументов
        program_name = args[0].lower()
        
        # Убедимся, что это exe-файл
        if not program_name.endswith('.exe'):
            program_name += '.exe'
        
        # Отправляем временное сообщение
        message = await update.message.reply_text(f"🔄 Попытка закрыть программу {program_name}...")
        
        try:
            # Ищем процессы с таким именем
            found = False
            closed_count = 0
            
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if proc.info['name'].lower() == program_name.lower():
                        # Процесс найден, пытаемся закрыть
                        proc.terminate()  # Более мягкое закрытие с возможностью сохранения данных
                        found = True
                        closed_count += 1
                        
                        # Ждем немного для корректного завершения
                        try:
                            proc.wait(timeout=3)
                        except psutil.TimeoutExpired:
                            # Если процесс не завершился, принудительно убиваем
                            proc.kill()
                            
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
                    if message_callback:
                        message_callback(f"Ошибка доступа к процессу: {str(e)}")
            
            # Обновляем сообщение в зависимости от результата
            if found:
                await message.edit_text(
                    f"✅ Программа {program_name} успешно закрыта.\n"
                    f"Закрыто процессов: {closed_count}"
                )
                
                # Логируем информацию
                if message_callback:
                    message_callback(f"Закрыта программа {program_name} ({closed_count} процессов)")
            else:
                await message.edit_text(
                    f"❌ Программа {program_name} не найдена среди запущенных процессов.\n\n"
                    f"Для получения списка запущенных программ используйте команду /ps"
                )
        
        except Exception as e:
            await message.edit_text(f"❌ Ошибка при закрытии программы {program_name}: {str(e)}")
            if message_callback:
                message_callback(f"Ошибка при выполнении команды /kill для {program_name}: {str(e)}")
    
    except Exception as e:
        # Отправляем сообщение об ошибке пользователю
        error_message = f"Произошла ошибка при обработке команды: {str(e)}"
        try:
            await update.message.reply_text(f"❌ {error_message}")
        except Exception:
            pass
        
        # Логируем ошибку
        logger.error(error_message)
        if message_callback:
            message_callback(error_message)

async def ip_command(update: Update, context: CallbackContext, config: Config,
                   message_callback: Optional[Callable[[str], None]] = None):
    """Обработка команды /ip - показывает информацию о локальном и внешнем IP с геолокацией"""
    try:
        user = update.effective_user
        
        # Проверка прав доступа
        if not is_owner(update, config):
            await update.message.reply_text(
                f"⛔ Извините, {user.first_name}, у вас нет доступа к этому боту.\n\n"
                f"Ваш ID: {user.id} не включен в список авторизованных пользователей."
            )
            if message_callback:
                message_callback(f"Попытка доступа к команде /ip от неавторизованного пользователя: {user.first_name} (ID: {user.id})")
            return
        
        # Отправляем временное сообщение
        message = await update.message.reply_text("🔄 Получение информации об IP-адресах...")
        
        try:
            # Замеряем время начала обработки
            start_time = time.time()
            
            # Получаем локальный IP-адрес
            local_ip = "Неизвестно"
            try:
                # Создаем сокет для определения локального IP
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                # Подключаемся (не отправляя данные) к внешнему серверу
                s.connect(("8.8.8.8", 80))
                local_ip = s.getsockname()[0]
                s.close()
            except Exception as e:
                local_ip = f"Ошибка: {str(e)}"
            
            # Получаем имя компьютера
            computer_name = socket.gethostname()
            
            # Получаем внешний IP-адрес
            external_ip = "Неизвестно"
            geo_info = {}
            try:
                # Запрос к сервису определения внешнего IP
                with urllib.request.urlopen("https://api.ipify.org") as response:
                    external_ip = response.read().decode('utf-8')
                
                # Получаем информацию о геолокации IP
                with urllib.request.urlopen(f"http://ip-api.com/json/{external_ip}") as response:
                    geo_info = json.loads(response.read().decode('utf-8'))
            except Exception as e:
                external_ip = f"Ошибка: {str(e)}"
            
            # Формируем информацию о местоположении
            location_info = "Неизвестно"
            if geo_info and geo_info.get('status') == 'success':
                country = geo_info.get('country', 'Неизвестно')
                city = geo_info.get('city', 'Неизвестно')
                region = geo_info.get('regionName', '')
                isp = geo_info.get('isp', 'Неизвестно')
                location_info = f"{city}, {region}, {country}\nПровайдер: {isp}"
            
            # Время выполнения
            execution_time = round((time.time() - start_time) * 1000, 2)
            
            # Обновляем сообщение с результатами
            await message.edit_text(
                f"🌐 Информация об IP-адресе\n\n"
                f"🖥️ Компьютер: {computer_name}\n\n"
                f"🏠 Локальный IP: {local_ip}\n\n"
                f"🌍 Внешний IP: {external_ip}\n\n"
                f"📍 Местоположение:\n{location_info}\n\n"
                f"⏱️ Время выполнения: {execution_time} мс"
            )
            
            # Логируем информацию
            if message_callback:
                message_callback(f"Отправлена информация об IP: локальный {local_ip}, внешний {external_ip}")
            
        except Exception as e:
            await message.edit_text(f"❌ Ошибка при получении информации об IP: {str(e)}")
            if message_callback:
                message_callback(f"Ошибка при выполнении команды /ip: {str(e)}")
    
    except Exception as e:
        # Отправляем сообщение об ошибке пользователю
        error_message = f"Произошла ошибка при обработке команды: {str(e)}"
        try:
            await update.message.reply_text(f"❌ {error_message}")
        except Exception:
            pass
        
        # Логируем ошибку
        logger.error(error_message)
        if message_callback:
            message_callback(error_message)

async def lock_command(update: Update, context: CallbackContext, config: Config,
                     message_callback: Optional[Callable[[str], None]] = None):
    """Обработка команды /lock - блокирует экран Windows (Win+L)"""
    try:
        user = update.effective_user
        
        # Проверка прав доступа
        if not is_owner(update, config):
            await update.message.reply_text(
                f"⛔ Извините, {user.first_name}, у вас нет доступа к этому боту.\n\n"
                f"Ваш ID: {user.id} не включен в список авторизованных пользователей."
            )
            if message_callback:
                message_callback(f"Попытка доступа к команде /lock от неавторизованного пользователя: {user.first_name} (ID: {user.id})")
            return
        
        # Отправляем сообщение о блокировке
        message = await update.message.reply_text("🔒 Блокировка экрана...")
        
        try:
            # Выполняем блокировку только на Windows
            if sys.platform == 'win32':
                # Используем ctypes для вызова функции Windows API для блокировки
                try:
                    # Метод 1: Используем функцию LockWorkStation из user32.dll
                    ctypes.windll.user32.LockWorkStation()
                    
                    # Обновляем сообщение об успешной блокировке
                    await message.edit_text("✅ Экран успешно заблокирован")
                    
                    # Логируем информацию
                    if message_callback:
                        message_callback(f"Экран заблокирован по команде от {user.first_name} (ID: {user.id})")
                except Exception as e:
                    # Метод 2 (запасной): Используем rundll32
                    subprocess.call('rundll32.exe user32.dll,LockWorkStation')
                    await message.edit_text("✅ Экран успешно заблокирован (метод 2)")
                    
                    if message_callback:
                        message_callback(f"Экран заблокирован (метод 2) по команде от {user.first_name} (ID: {user.id})")
            else:
                # Для других платформ
                await message.edit_text("❌ Функция блокировки экрана доступна только на Windows")
                if message_callback:
                    message_callback(f"Попытка заблокировать экран на неподдерживаемой платформе: {sys.platform}")
            
        except Exception as e:
            await message.edit_text(f"❌ Ошибка при блокировке экрана: {str(e)}")
            if message_callback:
                message_callback(f"Ошибка при выполнении команды /lock: {str(e)}")
    
    except Exception as e:
        # Отправляем сообщение об ошибке пользователю
        error_message = f"Произошла ошибка при обработке команды: {str(e)}"
        try:
            await update.message.reply_text(f"❌ {error_message}")
        except Exception:
            pass
        
        # Логируем ошибку
        logger.error(error_message)
        if message_callback:
            message_callback(error_message)

async def shutdown_command(update: Update, context: CallbackContext, config: Config,
                         message_callback: Optional[Callable[[str], None]] = None):
    """Обработка команды /shutdown - выключает компьютер"""
    try:
        user = update.effective_user
        
        # Проверка прав доступа
        if not is_owner(update, config):
            await update.message.reply_text(
                f"⛔ Извините, {user.first_name}, у вас нет доступа к этому боту.\n\n"
                f"Ваш ID: {user.id} не включен в список авторизованных пользователей."
            )
            if message_callback:
                message_callback(f"Попытка доступа к команде /shutdown от неавторизованного пользователя: {user.first_name} (ID: {user.id})")
            return
        
        # Запрашиваем подтверждение, чтобы избежать случайного выключения
        confirm_keyboard = [
            ["✅ Подтвердить", "❌ Отмена"]
        ]
        from telegram import ReplyKeyboardMarkup
        
        await update.message.reply_text(
            "⚠️ ВНИМАНИЕ! Вы собираетесь выключить компьютер.\n\n"
            "Все несохраненные данные будут потеряны!\n\n"
            "Вы уверены, что хотите продолжить?",
            reply_markup=ReplyKeyboardMarkup(confirm_keyboard, one_time_keyboard=True, resize_keyboard=True)
        )
        
        # Создаем обработчик для ответа на подтверждение
        async def handle_confirmation(update_inner, context_inner):
            response = update_inner.message.text.lower()
            
            # Удаляем клавиатуру
            from telegram import ReplyKeyboardRemove
            await update_inner.message.reply_text("Обработка...", reply_markup=ReplyKeyboardRemove())
            
            if "подтвердить" in response:
                # Пользователь подтвердил выключение
                shutdown_message = await update_inner.message.reply_text("🔄 Выключение компьютера...")
                
                try:
                    # Логируем действие перед выключением
                    if message_callback:
                        message_callback(f"Выключение компьютера по команде от {user.first_name} (ID: {user.id})")
                    
                    # Выполняем команду выключения в зависимости от ОС
                    if sys.platform == 'win32':
                        # Windows: выключение через 10 секунд с комментарием
                        command = 'shutdown /s /t 10 /c "Выключение по команде через Telegram бота"'
                        subprocess.Popen(command, shell=True)
                        
                        await shutdown_message.edit_text(
                            "✅ Компьютер будет выключен через 10 секунд.\n\n"
                            "Для отмены выполните в командной строке:\n"
                            "`shutdown /a`"
                        )
                    elif sys.platform == 'linux' or sys.platform == 'linux2':
                        # Linux: немедленное выключение
                        command = 'sudo shutdown -h now'
                        subprocess.Popen(command, shell=True)
                        
                        await shutdown_message.edit_text("✅ Компьютер выключается...")
                    elif sys.platform == 'darwin':
                        # macOS: выключение
                        command = 'sudo shutdown -h now'
                        subprocess.Popen(command, shell=True)
                        
                        await shutdown_message.edit_text("✅ Компьютер выключается...")
                    else:
                        await shutdown_message.edit_text(f"❌ Неподдерживаемая операционная система: {sys.platform}")
                
                except Exception as e:
                    await shutdown_message.edit_text(f"❌ Ошибка при выключении: {str(e)}")
                    if message_callback:
                        message_callback(f"Ошибка при выполнении команды /shutdown: {str(e)}")
            else:
                # Пользователь отменил выключение
                await update_inner.message.reply_text("🛑 Выключение компьютера отменено.")
                if message_callback:
                    message_callback(f"Пользователь {user.first_name} (ID: {user.id}) отменил выключение компьютера")
            
            # Удаляем обработчик после использования
            context_inner.application.remove_handler(confirmation_handler)
        
        # Регистрируем временный обработчик для подтверждения
        confirmation_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, handle_confirmation)
        context.application.add_handler(confirmation_handler)
        
        # Логируем запрос на выключение
        if message_callback:
            message_callback(f"Пользователь {user.first_name} (ID: {user.id}) запросил выключение компьютера")
    
    except Exception as e:
        # Отправляем сообщение об ошибке пользователю
        error_message = f"Произошла ошибка при обработке команды: {str(e)}"
        try:
            await update.message.reply_text(f"❌ {error_message}")
        except Exception:
            pass
        
        # Логируем ошибку
        logger.error(error_message)
        if message_callback:
            message_callback(error_message)
