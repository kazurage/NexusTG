#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Модуль для хранения и управления конфигурациями бота.
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class Config:
    """Класс для хранения конфигурации бота"""
    
    def __init__(self, token: str, owner_ids: List[str]):
        """
        Инициализация конфигурации
        
        Args:
            token: Токен бота
            owner_ids: Список ID владельцев
        """
        self.token = token
        self.owner_ids = owner_ids
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Преобразование конфигурации в словарь для сохранения
        
        Returns:
            Dict: Словарь с конфигурацией
        """
        return {
            "bot_token": self.token,
            "owner_ids": self.owner_ids
        }
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'Config':
        """
        Создание конфигурации из словаря
        
        Args:
            config_dict: Словарь с конфигурацией
            
        Returns:
            Config: Объект конфигурации
        """
        return cls(
            token=config_dict.get("bot_token", ""),
            owner_ids=config_dict.get("owner_ids", [])
        )
    
    @classmethod
    def load_from_file(cls, file_path: str) -> Optional['Config']:
        """
        Загрузка конфигурации из файла
        
        Args:
            file_path: Путь к файлу конфигурации
            
        Returns:
            Config: Объект конфигурации или None при ошибке
        """
        try:
            if not os.path.exists(file_path):
                logger.error(f"Файл конфигурации не найден: {file_path}")
                return None
                
            with open(file_path, 'r', encoding='utf-8') as f:
                config_dict = json.load(f)
                
            return cls.from_dict(config_dict)
            
        except Exception as e:
            logger.error(f"Ошибка при загрузке конфигурации: {str(e)}")
            return None
    
    def save_to_file(self, file_path: str) -> bool:
        """
        Сохранение конфигурации в файл
        
        Args:
            file_path: Путь для сохранения файла
            
        Returns:
            bool: True при успешном сохранении, False при ошибке
        """
        try:
            # Создаем директорию, если она не существует
            directory = os.path.dirname(file_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)
                
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.to_dict(), f, indent=4)
                
            return True
            
        except Exception as e:
            logger.error(f"Ошибка при сохранении конфигурации: {str(e)}")
            return False
