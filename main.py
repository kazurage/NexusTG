import customtkinter as ctk
import tkinter as tk
from PIL import Image, ImageTk
import os
import time
import threading
import math
import json
import asyncio
import sys
import webbrowser

# Добавляем текущую директорию в путь, чтобы импорты работали корректно
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from src.bot import TelegramBot

# Set appearance mode and default color theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class NexusTGApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Window setup
        self.title("NexusTG")
        self.geometry("800x500")
        self.minsize(600, 400)  # Set minimum window size
        self.resizable(True, True)  # Allow resizing
        
        # Set icon if available
        if os.path.exists("icon.ico"):
            self.iconbitmap("icon.ico")
            
        # Colors (Dark clean theme)
        self.dark_bg = "#161A22"
        self.primary_blue = "#2B87D3"
        self.accent_green = "#0AC47E"
        self.text_color = "#FFFFFF"
        self.secondary_text = "#8A8D91"
        self.input_bg = "#1E232E"
        self.input_border = "#333A47"
        
        # Configure master frame with smooth dark background
        self.configure(fg_color=self.dark_bg)
        
        # Create main frame that will expand with window
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(expand=True, fill="both")
        
        # Create initial welcome screen
        self.create_welcome_screen()
        
        # Initialize configuration variables
        self.bot_token = ""
        self.owner_ids = []
        
        # История логов
        self.log_history = []
        self.bot_info = None
        
        # Состояние бота (True=работает, False=остановлен)
        self.bot_is_running = True
        
        # Bind window resize event
        self.bind("<Configure>", self.on_window_resize)
        
        # Проверка наличия конфигурации и автоматический запуск
        self.check_existing_config()
    
    def create_welcome_screen(self):
        """Create the welcome screen"""
        # Clear previous content if any
        for widget in self.main_frame.winfo_children():
            widget.destroy()
            
        # Create content frame (centered)
        self.content_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.content_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Create animated logo
        self.logo_canvas = ctk.CTkCanvas(self.content_frame, width=120, height=120, 
                                    bg=self.dark_bg, highlightthickness=0)
        self.logo_canvas.pack(pady=(0, 20))
        self.create_logo()
        
        # Welcome text
        self.welcome_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.welcome_frame.pack(pady=(0, 5))
        
        self.welcome_label = ctk.CTkLabel(self.welcome_frame, text="Добро пожаловать в", 
                                     font=ctk.CTkFont(family="Segoe UI", size=16),
                                     text_color=self.secondary_text)
        self.welcome_label.pack()
        
        # Brand name with better styling
        self.brand_label = ctk.CTkLabel(self.content_frame, text="NexusTG", 
                                     font=ctk.CTkFont(family="Segoe UI", size=34, weight="bold"),
                                     text_color=self.text_color)
        self.brand_label.pack(pady=(0, 15))
        
        # Description
        self.description_label = ctk.CTkLabel(self.content_frame, 
                                         text="Управляйте вашим компьютером через Telegram легко и безопасно",
                                         font=ctk.CTkFont(family="Segoe UI", size=14),
                                         text_color=self.secondary_text,
                                         wraplength=500)  # Allow text to wrap if window is narrow
        self.description_label.pack(pady=(0, 40))
        
        # Start button with clean design
        self.start_button = ctk.CTkButton(self.content_frame, 
                                     text="Начать", 
                                     font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
                                     fg_color=self.primary_blue,
                                     hover_color="#1976D2",
                                     corner_radius=22,
                                     command=self.start_button_clicked,
                                     width=180,
                                     height=44)
        self.start_button.pack(pady=10)
        
        # Initialize animation
        self.arc_angle = 45
        self.animate_arc()
    
    def create_config_screen(self):
        """Create the configuration screen"""
        # Clear previous content
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        
        # Create header frame
        self.header_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent", height=60)
        self.header_frame.pack(fill="x", padx=20, pady=10)
        
        # Add small logo in header
        self.small_logo_canvas = ctk.CTkCanvas(self.header_frame, width=40, height=40, 
                                          bg=self.dark_bg, highlightthickness=0)
        self.small_logo_canvas.pack(side="left", padx=(0, 10))
        self.create_small_logo()
        
        # Add title in header
        self.header_title = ctk.CTkLabel(self.header_frame, text="NexusTG", 
                                     font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
                                     text_color=self.text_color)
        self.header_title.pack(side="left")
        
        # Create main content area with scroll capability
        self.scroll_frame = ctk.CTkScrollableFrame(self.main_frame, fg_color="transparent")
        self.scroll_frame.pack(expand=True, fill="both", padx=30, pady=(10, 20))
        
        # Configuration title
        self.config_title = ctk.CTkLabel(self.scroll_frame, text="Настройки конфигурации", 
                                     font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold"),
                                     text_color=self.text_color)
        self.config_title.pack(pady=(0, 20), anchor="w")
        
        # Bot token section
        self.token_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        self.token_frame.pack(fill="x", pady=(0, 15))
        
        self.token_label = ctk.CTkLabel(self.token_frame, text="Токен Telegram бота", 
                                   font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
                                   text_color=self.text_color)
        self.token_label.pack(anchor="w", pady=(0, 8))
        
        self.token_desc = ctk.CTkLabel(self.token_frame, 
                                   text="Введите токен бота, полученный от @BotFather", 
                                   font=ctk.CTkFont(family="Segoe UI", size=12),
                                   text_color=self.secondary_text)
        self.token_desc.pack(anchor="w", pady=(0, 10))
        
        self.token_entry = ctk.CTkEntry(self.token_frame, 
                                placeholder_text="Введите токен бота...",
                                width=400,
                                height=36,
                                border_width=1,
                                corner_radius=8,
                                fg_color=self.input_bg,
                                border_color=self.input_border,
                                text_color=self.text_color)
        self.token_entry.pack(anchor="w")
        
        self.add_context_menu(self.token_entry)
        
        # Owner IDs section
        self.owners_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        self.owners_frame.pack(fill="x", pady=(10, 15))
        
        self.owners_label = ctk.CTkLabel(self.owners_frame, text="ID владельцев", 
                                    font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
                                    text_color=self.text_color)
        self.owners_label.pack(anchor="w", pady=(0, 8))
        
        self.owners_desc = ctk.CTkLabel(self.owners_frame, 
                                    text="Добавьте до 3 Telegram ID пользователей, которые смогут управлять ботом", 
                                    font=ctk.CTkFont(family="Segoe UI", size=12),
                                    text_color=self.secondary_text)
        self.owners_desc.pack(anchor="w", pady=(0, 15))
        
        # Container for owner ID entries and add button
        self.owners_container = ctk.CTkFrame(self.owners_frame, fg_color="transparent")
        self.owners_container.pack(fill="x")
        
        # Create initial owner ID entry
        self.owner_entries = []
        self.add_owner_entry()
        
        # Add owner button
        self.add_owner_button = ctk.CTkButton(self.owners_container, 
                                          text="+ Добавить владельца", 
                                          font=ctk.CTkFont(family="Segoe UI", size=12),
                                          fg_color="transparent",
                                          text_color=self.primary_blue,
                                          hover_color="#1E232E",
                                          corner_radius=6,
                                          command=self.add_owner_entry,
                                          width=150,
                                          height=30)
        self.add_owner_button.pack(anchor="w", pady=(10, 0))
        
        # Save configuration button
        self.button_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        self.button_frame.pack(fill="x", pady=(30, 10))
        
        self.save_button = ctk.CTkButton(self.button_frame, 
                                     text="Сохранить", 
                                     font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
                                     fg_color=self.primary_blue,
                                     hover_color="#1976D2",
                                     corner_radius=22,
                                     command=self.save_and_connect,
                                     width=180,
                                     height=44)
        self.save_button.pack(side="left", pady=10, padx=(0, 10))
        
        self.back_button = ctk.CTkButton(self.button_frame, 
                                     text="Назад", 
                                     font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
                                     fg_color="transparent",
                                     hover_color="#1E232E",
                                     border_width=1,
                                     border_color=self.secondary_text,
                                     text_color=self.text_color,
                                     corner_radius=22,
                                     command=self.create_welcome_screen,
                                     width=120,
                                     height=44)
        self.back_button.pack(side="left", pady=10)
        
        # Start another small rotating arc animation for the header logo
        self.small_arc_angle = 45
        self.animate_small_arc()
    
    def add_owner_entry(self):
        """Add a new owner ID entry field"""
        if len(self.owner_entries) >= 3:
            # Maximum 3 owners allowed
            self.add_owner_button.configure(state="disabled")
            return
            
        entry_frame = ctk.CTkFrame(self.owners_container, fg_color="transparent")
        entry_frame.pack(fill="x", pady=(0, 8))
        
        # Owner ID entry
        entry = ctk.CTkEntry(entry_frame, 
                         placeholder_text=f"ID владельца {len(self.owner_entries) + 1}...",
                         width=350,
                         height=36,
                         border_width=1,
                         corner_radius=8,
                         fg_color=self.input_bg,
                         border_color=self.input_border,
                         text_color=self.text_color)
        entry.pack(side="left")
        
        # Only add remove button if not the first entry
        if len(self.owner_entries) > 0:
            remove_button = ctk.CTkButton(entry_frame, 
                                      text="✕", 
                                      font=ctk.CTkFont(family="Segoe UI", size=12),
                                      fg_color="transparent",
                                      text_color=self.secondary_text,
                                      hover_color="#3A3A3A",
                                      width=30,
                                      height=30,
                                      corner_radius=15,
                                      command=lambda f=entry_frame: self.remove_owner_entry(f))
            remove_button.pack(side="left", padx=(10, 0))
        
        self.owner_entries.append({"frame": entry_frame, "entry": entry})
        
        self.add_context_menu(entry)
        
        # Disable add button if maximum reached
        if len(self.owner_entries) >= 3:
            self.add_owner_button.configure(state="disabled")
    
    def remove_owner_entry(self, frame):
        """Remove an owner ID entry field"""
        # Find the entry in the owner_entries list
        for entry in self.owner_entries:
            if entry.winfo_parent() == str(frame):
                self.owner_entries.remove(entry)
                break
                
        # Destroy the frame
        frame.destroy()
        
        # Re-enable add button
        self.add_owner_button.configure(state="normal")
    
    def save_config(self):
        """Save the configuration"""
        # Если мы на экране конфигурации, получаем значения из полей ввода
        if hasattr(self, 'token_entry') and self.token_entry.winfo_exists():
            bot_token = self.token_entry.get().strip()
            
            # Получаем ID владельцев (не пустые)
            owner_ids = []
            for owner_item in self.owner_entries:
                # Получаем виджет ввода из словаря
                entry_widget = owner_item.get("entry")
                if entry_widget and entry_widget.winfo_exists():
                    owner_id = entry_widget.get().strip()
                    if owner_id:
                        owner_ids.append(owner_id)
            
            # Валидация ввода
            if not bot_token:
                self.show_error("Введите токен бота")
                return False
                
            if not owner_ids:
                self.show_error("Добавьте хотя бы одного владельца")
                return False
            
            # Сохраняем конфигурацию
            self.bot_token = bot_token
            self.owner_ids = owner_ids
        
        # Если мы перешли с первого экрана, используем имеющиеся значения
        # Сохраняем в файл конфигурации
        config = {
            "bot_token": self.bot_token,
            "owner_ids": self.owner_ids
        }
        
        try:
            # Создаем директорию cfg, если не существует
            if not os.path.exists("cfg"):
                os.makedirs("cfg")
                
            with open("cfg/config.json", "w") as file:
                json.dump(config, file, indent=4)
                
            return True
            
        except Exception as e:
            self.show_error(f"Ошибка при сохранении: {str(e)}")
            return False
            
    def save_and_connect(self):
        """Save configuration and proceed to loading screen"""
        # Сохраняем конфигурацию
        if self.save_config():
            # Показываем экран загрузки
            self.create_loading_screen()
            
            # Запускаем бота и проверяем валидность токена в отдельном потоке
            loading_thread = threading.Thread(target=self.simulate_loading)
            loading_thread.daemon = True
            loading_thread.start()
    
    def on_window_resize(self, event):
        """Handle window resize events"""
        # Only update layout if the event is from the main window
        if event.widget == self:
            # Update description wraplength based on window width if on welcome screen
            if hasattr(self, 'description_label') and self.description_label.winfo_exists():
                window_width = event.width
                if window_width > 600:
                    self.description_label.configure(wraplength=500)
                else:
                    self.description_label.configure(wraplength=window_width * 0.8)
                    
    def show_error(self, message):
        """Show error message"""
        error_window = ctk.CTkToplevel(self)
        error_window.title("Ошибка")
        error_window.geometry("540x380")  # Увеличиваем размер окна
        error_window.resizable(True, True)  # Разрешаем изменять размер
        error_window.configure(fg_color=self.dark_bg)
        error_window.after(10, lambda: error_window.focus_force())  # Фокус на окне
        
        # Добавляем отступы по краям
        main_container = ctk.CTkFrame(error_window, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Верхняя секция с заголовком и иконкой в стильном контейнере
        header_frame = ctk.CTkFrame(main_container, corner_radius=10, fg_color="#262D3A", height=60)
        header_frame.pack(fill="x", pady=(0, 15))
        
        # Внутренний контейнер для содержимого заголовка с отступами
        header_content = ctk.CTkFrame(header_frame, fg_color="transparent")
        header_content.pack(fill="x", padx=15, pady=12)
        
        # Заголовок с иконкой ошибки в одной строке
        header_left = ctk.CTkFrame(header_content, fg_color="transparent")
        header_left.pack(side="left", anchor="w")
        
        # Создаем рамку для иконки ошибки
        icon_size = 32
        icon_frame = ctk.CTkFrame(header_left, width=icon_size, height=icon_size, 
                              corner_radius=icon_size/2, fg_color="#F24747")
        icon_frame.pack(side="left", padx=(0, 10))
        
        # Делаем фрейм фиксированного размера
        icon_frame.pack_propagate(False)
        
        # Добавляем значок восклицательного знака в рамку
        exclamation = ctk.CTkLabel(icon_frame, text="!", 
                              font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
                               text_color="white")
        exclamation.place(relx=0.5, rely=0.5, anchor="center")
        
        # Заголовок ошибки
        error_title = ctk.CTkLabel(header_left, text="Произошла ошибка", 
                               font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
                                 text_color=self.text_color)
        error_title.pack(side="left")
        
        # Основное содержимое
        content_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, pady=(0, 15))
        
        # Контейнер для текста с ошибкой
        text_container = ctk.CTkFrame(content_frame, fg_color=self.input_bg, corner_radius=8)
        text_container.pack(fill="both", expand=True)
        
        # Внутренний контейнер для текста с отступами
        text_inner = ctk.CTkFrame(text_container, fg_color="transparent")
        text_inner.pack(fill="both", expand=True, padx=2, pady=2)
        
        # Добавляем скроллбар для текстового поля
        scrollbar = ctk.CTkScrollbar(text_inner)
        scrollbar.pack(side="right", fill="y")
        
        # Текстовое поле для текста ошибки с возможностью выделения и копирования
        error_text = tk.Text(text_inner, 
                           wrap="word", 
                           bg="#1A2035", 
                           fg="#E7E7E7",
                           font=("Consolas", 12),
                           bd=0,
                           padx=15,
                           pady=15,
                           highlightthickness=0)
        error_text.pack(side="left", fill="both", expand=True)
        
        # Связываем скроллбар с текстовым полем
        scrollbar.configure(command=error_text.yview)
        error_text.configure(yscrollcommand=scrollbar.set)
        
        # Вставляем текст ошибки
        error_text.insert("1.0", message)
        
        # Добавляем небольшую подсказку о копировании
        hint_text = ctk.CTkLabel(main_container, 
                             text="Совет: выделите текст для копирования или используйте кнопку ниже",
                             font=ctk.CTkFont(family="Segoe UI", size=11),
                             text_color="#767C93")
        hint_text.pack(anchor="w", pady=(0, 10))
        
        # Кнопки действий с красивым дизайном
        buttons_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        buttons_frame.pack(fill="x")
        
        # Разделяем кнопки на правую и левую группы
        left_buttons = ctk.CTkFrame(buttons_frame, fg_color="transparent")
        left_buttons.pack(side="left")
        
        right_buttons = ctk.CTkFrame(buttons_frame, fg_color="transparent")
        right_buttons.pack(side="right")
        
        # Кнопка для копирования текста ошибки
        copy_button = ctk.CTkButton(left_buttons, text="Копировать текст", 
                               font=ctk.CTkFont(family="Segoe UI", size=13),
                               fg_color="#2D5C9E",
                               hover_color="#1F4A8A",
                               corner_radius=6,
                               command=lambda: self.copy_error_text(error_text),
                               width=140,
                               height=36,
                               border_spacing=8,
                               image=self.get_copy_icon())
        copy_button.pack(side="left", padx=(0, 10))
        
        # Кнопка OK для закрытия окна
        ok_button = ctk.CTkButton(right_buttons, text="Закрыть", 
                             font=ctk.CTkFont(family="Segoe UI", size=13),
                             fg_color="#3E4558",
                             hover_color="#333A4D",
                             corner_radius=6,
                             command=error_window.destroy,
                             width=100,
                             height=36)
        ok_button.pack(side="right")
        
        # Добавляем эффект при открытии
        self.animate_error_window(error_window)
        
        # Make modal
        error_window.transient(self)
        error_window.grab_set()
        self.wait_window(error_window)
    
    def animate_error_window(self, window):
        """Анимация появления окна ошибки"""
        # Начинаем с прозрачного окна
        window.attributes('-alpha', 0.0)
        
        # Анимация появления
        def fade_in(alpha=0.0):
            alpha += 0.1
            window.attributes('-alpha', alpha)
            if alpha < 1.0:
                window.after(20, lambda: fade_in(alpha))
        
        # Запускаем анимацию
        fade_in()
    
    def get_copy_icon(self):
        """Создает иконку копирования для кнопки"""
        try:
            # Если PIL доступен, создаем иконку
            from PIL import Image, ImageDraw
            
            # Создаем пустое изображение с прозрачным фоном
            icon_size = 14
            icon = Image.new("RGBA", (icon_size, icon_size), (0, 0, 0, 0))
            draw = ImageDraw.Draw(icon)
            
            # Рисуем значок копирования
            # Передний документ
            draw.rectangle([3, 3, icon_size-1, icon_size-1], outline="white")
            # Задний документ
            draw.rectangle([1, 1, icon_size-3, icon_size-3], outline="white")
            
            return ctk.CTkImage(light_image=icon, dark_image=icon, size=(icon_size, icon_size))
        except Exception:
            # Если создать иконку не удалось, возвращаем None
            return None
    
    def copy_error_text(self, text_widget):
        """Копирует весь текст из текстового виджета в буфер обмена"""
        try:
            text_content = text_widget.get("1.0", "end-1c")  # Получаем весь текст без последнего символа новой строки
            self.clipboard_clear()
            self.clipboard_append(text_content)
            
            # Визуальная обратная связь - выделяем весь текст на короткое время
            text_widget.tag_add("sel", "1.0", "end-1c")
            
            # Кратковременно изменяем цвет фона текста для индикации
            original_bg = text_widget["bg"]
            text_widget.config(bg="#2A3147")
            
            # Возвращаем исходный фон через 500 мс
            def restore_bg():
                text_widget.config(bg=original_bg)
                text_widget.tag_remove("sel", "1.0", "end")
            
            self.after(500, restore_bg)
        except Exception as e:
            print(f"Ошибка при копировании текста: {str(e)}")
    
    def create_logo(self):
        """Create a smooth, anti-aliased logo"""
        self.logo_canvas.delete("all")
        
        # Draw outer circle
        self.logo_canvas.create_oval(10, 10, 110, 110, fill=self.primary_blue, outline="", tags="logo")
        # Draw inner circle
        self.logo_canvas.create_oval(30, 30, 90, 90, fill=self.dark_bg, outline="", tags="logo")
        # Draw "NT" letters
        self.logo_canvas.create_text(60, 60, text="NT",
                                 font=("Segoe UI", 30, "bold"),
                                 fill=self.text_color, tags="logo")
        
        # Start animation
        self.animate_arc()
        
    def create_small_logo(self):
        """Create a smaller version of the logo for the header"""
        self.small_logo_canvas.delete("all")
        
        # Draw outer circle
        self.small_logo_canvas.create_oval(5, 5, 35, 35, fill=self.primary_blue, outline="", tags="logo")
        
        # Draw inner circle
        self.small_logo_canvas.create_oval(8, 8, 32, 32, fill=self.dark_bg, outline="", tags="logo")
        
        # Draw "NT" letters
        self.small_logo_canvas.create_text(20, 20, text="NT",
                                      font=("Segoe UI", 12, "bold"),
                                      fill=self.text_color, tags="logo")
    
    def animate_arc(self):
        """Animate a rotating arc around the logo"""
        try:
            if hasattr(self, 'logo_canvas') and self.logo_canvas.winfo_exists():
                self.logo_canvas.delete("arc")
                
                # Create a rotating arc
                arc_thickness = 2
                radius = 55
                
                # Convert angles to coordinates
                x0 = 60 - radius - arc_thickness
                y0 = 60 - radius - arc_thickness
                x1 = 60 + radius + arc_thickness
                y1 = 60 + radius + arc_thickness
                
                self.logo_canvas.create_arc(
                    x0, y0, x1, y1,
                    start=self.arc_angle, extent=45,
                    style=tk.ARC, width=arc_thickness,
                    outline=self.accent_green, tags="arc")
                
                # Update angle for next animation
                self.arc_angle = (self.arc_angle + 2) % 360
                
                # Only continue animation if canvas still exists
                if self.logo_canvas.winfo_exists():
                    self.after(50, self.animate_arc)
        except Exception:
            # Если произошла ошибка, например, канвас был удален, просто игнорируем
            pass
    
    def animate_small_arc(self):
        """Animate a rotating arc around the small logo"""
        # Безопасная проверка существования канваса перед использованием
        try:
            if hasattr(self, 'small_logo_canvas') and self.small_logo_canvas.winfo_exists():
                self.small_logo_canvas.delete("arc")
                
                # Create a rotating arc
                arc_thickness = 1
                radius = 18
                
                # Convert angles to coordinates
                x0 = 20 - radius - arc_thickness
                y0 = 20 - radius - arc_thickness
                x1 = 20 + radius + arc_thickness
                y1 = 20 + radius + arc_thickness
                
                self.small_logo_canvas.create_arc(
                    x0, y0, x1, y1,
                    start=self.small_arc_angle, extent=45,
                    style=tk.ARC, width=arc_thickness,
                    outline=self.accent_green, tags="arc")
                
                self.small_arc_angle = (self.small_arc_angle + 2) % 360
                
                # Only continue animation if canvas still exists
                if self.small_logo_canvas.winfo_exists():
                    self.after(50, self.animate_small_arc)
        except Exception:
            # Если произошла ошибка, например, канвас был удален, просто игнорируем
            pass
    
    def start_button_clicked(self):
        """Handle start button click"""
        # Простая визуальная обратная связь
        self.start_button.configure(fg_color=self.accent_green)
        self.update()
        
        # Задержка перед переходом к экрану загрузки для отображения изменения цвета кнопки
        def show_loading_and_then_config():
            # Показать короткую загрузку перед переходом к экрану конфигурации
            self.create_initial_loading_screen()
            # Перейти к экрану конфигурации после короткой анимации
            self.after(800, self.create_config_screen)
        
        # Запустить последовательность действий через короткое время
        self.after(200, show_loading_and_then_config)
        
    def create_initial_loading_screen(self):
        """Показать короткую загрузку перед переходом к экрану конфигурации"""
        # Очистить предыдущее содержимое
        for widget in self.main_frame.winfo_children():
            widget.destroy()
            
        # Создаем загрузочный экран
        loading_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        loading_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Создаем логотип
        logo_canvas = ctk.CTkCanvas(loading_frame, width=80, height=80, 
                                 bg=self.dark_bg, highlightthickness=0)
        logo_canvas.pack(pady=(0, 20))
        
        # Рисуем логотип
        logo_canvas.create_oval(5, 5, 75, 75, fill=self.primary_blue, outline="", tags="logo")
        logo_canvas.create_oval(15, 15, 65, 65, fill=self.dark_bg, outline="", tags="logo")
        logo_canvas.create_text(40, 40, text="NT", font=("Segoe UI", 24, "bold"),
                             fill=self.text_color, tags="logo")
        
        # Текст загрузки
        loading_label = ctk.CTkLabel(loading_frame, text="Загрузка...", 
                                  font=ctk.CTkFont(family="Segoe UI", size=16),
                                  text_color=self.text_color)
        loading_label.pack(pady=(10, 0))
    
    def update_loading_progress(self, text, progress):
        """Update loading progress UI"""
        if hasattr(self, 'loading_text') and self.loading_text.winfo_exists():
            self.loading_text.configure(text=text)
            self.progress_bar.set(progress)
            self.progress_text.configure(text=f"{int(progress * 100)}%")
    
    def loading_complete(self):
        """Called when loading is complete"""
        # Добавляем сообщение в лог вместо показа окна успеха
        
        # Переходим к основному экрану управления
        self.create_operation_screen()
    
    def create_operation_screen(self):
        """Создает экран с логированием и управлением"""
        # Clear previous content if any
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        
        # Create top panel
        top_bar = ctk.CTkFrame(self.main_frame, fg_color=self.input_bg, height=60)
        top_bar.pack(fill="x", padx=0, pady=0)
        
        # Панель управления вместо логотипа и имени
        panel_frame = ctk.CTkFrame(top_bar, fg_color="transparent")
        panel_frame.pack(side="left", padx=20)
        
        # Текст "Панель управление"
        panel_label = ctk.CTkLabel(panel_frame, text="Панель управление", 
                           font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
                           text_color=self.text_color)
        panel_label.pack(side="left", padx=(0, 15))
        
        # "Настройки" в виде текста
        settings_label = ctk.CTkLabel(panel_frame, 
                                   text="Настройки", 
                                   font=ctk.CTkFont(family="Segoe UI", size=16),
                                   text_color=self.text_color)
        settings_label.pack(side="left")
        
        # Инициализируем переменные для выпадающего меню
        self.custom_dropdown_visible = False
        self.custom_dropdown_frame = None
        
        # Right side controls
        right_buttons_frame = ctk.CTkFrame(top_bar, fg_color="transparent")
        right_buttons_frame.pack(side="right", padx=20, pady=14)
        
        # Кнопка переключения (определяем цвета в зависимости от состояния бота)
        if hasattr(self, 'bot_is_running') and self.bot_is_running:
            button_text = "Остановить"
            button_color = "#E74C3C"  # Красный для кнопки "Остановить"
            button_hover = "#C0392B"  # Темно-красный при наведении
        else:
            button_text = "Запустить"
            button_color = "#2ECC71"  # Зеленый для кнопки "Запустить"
            button_hover = "#27AE60"  # Темно-зеленый при наведении
            
        self.toggle_bot_button = ctk.CTkButton(right_buttons_frame, 
                                          text=button_text, 
                                          font=ctk.CTkFont(family="Segoe UI", size=14),
                                          fg_color=button_color,
                                          hover_color=button_hover,
                                          height=32,
                                          corner_radius=8,
                                          command=self.toggle_bot_status)
        self.toggle_bot_button.pack(side="left", padx=(0, 15))
        
        # Добавляем кнопку с иконкой проекта справа
        self.logo_button_frame = ctk.CTkFrame(right_buttons_frame, fg_color="transparent", width=40, height=40)
        self.logo_button_frame.pack(side="left")
        
        # Создаем канвас для иконки
        self.project_logo_canvas = ctk.CTkCanvas(self.logo_button_frame, width=40, height=40, 
                                        bg=self.input_bg, highlightthickness=0)
        self.project_logo_canvas.pack()
        
        # Рисуем иконку проекта с улучшенным дизайном
        # Внешний круг с градиентным эффектом
        for i in range(3):
            self.project_logo_canvas.create_oval(
                5 + i, 5 + i, 35 - i, 35 - i, 
                fill="" if i < 2 else self.primary_blue, 
                outline=self.primary_blue, 
                width=1,
                tags="logo"
            )
        
        # Внутренний круг
        self.project_logo_canvas.create_oval(10, 10, 30, 30, fill=self.dark_bg, outline="", tags="logo")
        
        # Текст на иконке
        self.project_logo_canvas.create_text(20, 20, text="NT", fill=self.text_color, 
                                     font=("Segoe UI", 14, "bold"), tags="logo")
        
        # Привязываем нажатие к показу меню
        self.project_logo_canvas.bind("<Button-1>", self.toggle_custom_dropdown)
        
        # Main content area
        content_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Info panel
        info_frame = ctk.CTkFrame(content_frame, fg_color=self.input_bg, corner_radius=10)
        info_frame.pack(fill="x", padx=10, pady=10)
        
        # Bot info
        bot_info_label = ctk.CTkLabel(info_frame, text="Информация о боте", 
                                 font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
                                 text_color=self.text_color)
        bot_info_label.pack(anchor="w", padx=20, pady=(15, 10))
        
        # Get token without full display for security
        token_display = self.bot_token[:6] + "..." + self.bot_token[-4:]
        token_info = ctk.CTkLabel(info_frame, 
                             text=f"Токен: {token_display}", 
                             font=ctk.CTkFont(family="Segoe UI", size=14),
                             text_color=self.secondary_text)
        token_info.pack(anchor="w", padx=20, pady=2)
        
        # Owner IDs info
        owner_count = len(self.owner_ids)
        owners_info = ctk.CTkLabel(info_frame, 
                              text=f"Владельцев: {owner_count}", 
                              font=ctk.CTkFont(family="Segoe UI", size=14),
                              text_color=self.secondary_text)
        owners_info.pack(anchor="w", padx=20, pady=2)
        
        # Status info с учетом текущего состояния и цвета
        status_text = "Активен" if self.bot_is_running else "Остановлен"
        status_color = "#2ECC71" if self.bot_is_running else "#E74C3C"  # Зеленый или красный
        
        self.bot_status_info = ctk.CTkLabel(info_frame, 
                              text=f"Статус: ", 
                              font=ctk.CTkFont(family="Segoe UI", size=14),
                              text_color=self.secondary_text)
        self.bot_status_info.pack(anchor="w", padx=20, pady=(2, 15), side="left")
        
        # Отдельная метка для статуса с цветом
        self.bot_status_value = ctk.CTkLabel(info_frame, 
                              text=status_text, 
                              font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
                              text_color=status_color)
        self.bot_status_value.pack(anchor="w", pady=(2, 15), side="left")
        
        # Command log area
        log_frame = ctk.CTkFrame(content_frame, fg_color=self.input_bg, corner_radius=10)
        log_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        log_label = ctk.CTkLabel(log_frame, text="Лог команд", 
                             font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
                             text_color=self.text_color)
        log_label.pack(anchor="w", padx=20, pady=(15, 10))
        
        # Create a text area for the logs with scrollbar
        log_container = ctk.CTkFrame(log_frame, fg_color="transparent")
        log_container.pack(fill="both", expand=True, padx=20, pady=(0, 15))
        
        scrollbar = ctk.CTkScrollbar(log_container)
        scrollbar.pack(side="right", fill="y")
        
        self.log_text = tk.Text(log_container, wrap="word", bg=self.dark_bg,
                         fg=self.text_color, insertbackground=self.text_color,
                         height=10, bd=0, font=("Consolas", 12))
        self.log_text.pack(side="left", fill="both", expand=True)
        
        # Connect scrollbar to text widget
        scrollbar.configure(command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        # Определяем текущее время для всех логов
        current_time = time.strftime("%H:%M:%S")
        
        # Проверяем, есть ли сохраненная история логов
        if not self.log_history:
            # Если истории нет, добавляем стандартные сообщения
            current_time = time.strftime("%H:%M:%S")
            startup_message = f"[{current_time}] Приложение NexusTG запущено"
            self.log_history.append(startup_message)
        
        # Удаляем дублирующиеся автоматические сообщения о боте
        # Отображаем сохраненную историю логов
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", "end")  # Очищаем текстовое поле перед выводом
        for log_entry in self.log_history:
            self.log_text.insert("end", f"{log_entry}\n")
        self.log_text.see("end")  # Прокрутка к последнему сообщению
        self.log_text.configure(state="disabled")  # Make read-only
    
    def toggle_bot_status(self):
        """Переключение статуса бота (остановка/запуск)"""
        if hasattr(self, 'bot') and hasattr(self.bot, 'is_running') and self.bot.is_running:
            # Останавливаем бота
            threading.Thread(target=self.stop_bot, daemon=True).start()
            
            # Обновляем кнопку на зеленую "Запустить"
            self.toggle_bot_button.configure(
                text="Запустить", 
                fg_color="#2ECC71",  # Зеленый
                hover_color="#27AE60"  # Темно-зеленый
            )
            
            # Обновляем статус на красный "Остановлен" 
            self.bot_status_value.configure(
                text="Остановлен",
                text_color="#E74C3C"  # Красный
            )
            
            self.add_log_message("Бот остановлен")
            # Обновляем состояние бота
            self.bot_is_running = False
        else:
            # Запускаем бота снова
            threading.Thread(target=self.restart_bot, daemon=True).start()
            
            # Обновляем кнопку на красную "Остановить"
            self.toggle_bot_button.configure(
                text="Остановить", 
                fg_color="#E74C3C",  # Красный
                hover_color="#C0392B"  # Темно-красный
            )
            
            # Обновляем статус на зеленый "Активен"
            self.bot_status_value.configure(
                text="Активен",
                text_color="#2ECC71"  # Зеленый
            )
            
            self.add_log_message("Бот запущен")
            # Обновляем состояние бота
            self.bot_is_running = True
    
    def stop_bot(self):
        """Остановка бота"""
        if hasattr(self, 'bot') and self.event_loop:
            # Создаем новый поток для остановки бота
            def stop_bot_thread():
                try:
                    # Важно: используем тот же event_loop, что и при запуске бота
                    if hasattr(self, 'event_loop') and self.event_loop.is_running():
                        # Если у нас есть и работает цикл событий от запуска бота, создаем новую задачу
                        async def stop_task():
                            if hasattr(self, 'bot'):
                                await self.bot.stop_bot()
                        asyncio.run_coroutine_threadsafe(stop_task(), self.event_loop)
                    else:
                        # Создаем новый event_loop как запасной вариант
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        loop.run_until_complete(self.bot.stop_bot())
                        loop.close()
                except Exception as e:
                    error_msg = f"Ошибка при остановке бота: {str(e)}"
                    self.after(0, lambda msg=error_msg: self.show_error(msg))
            
            stop_thread = threading.Thread(target=stop_bot_thread)
            stop_thread.daemon = True
            stop_thread.start()
    
    def restart_bot(self):
        """Перезапуск бота"""
        if hasattr(self, 'bot'):
            # Запускаем бота снова в отдельном потоке
            def restart_bot_thread():
                try:
                    # Используем тот же event_loop, что и при остановке, если он доступен
                    if hasattr(self, 'event_loop') and self.event_loop.is_running():
                        # Если у нас есть и работает цикл событий от запуска бота, создаем новую задачу
                        async def start_task():
                            if hasattr(self, 'bot'):
                                success = await self.bot.start_bot()
                                if not success:
                                    error_msg = "Не удалось запустить бота. Проверьте токен и попробуйте снова."
                                    self.after(0, lambda msg=error_msg: self.show_error(msg))
                        asyncio.run_coroutine_threadsafe(start_task(), self.event_loop)
                    else:
                        # Создаем новый event_loop как запасной вариант
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        success = loop.run_until_complete(self.bot.start_bot())
                        loop.close()
                        if not success:
                            error_msg = "Не удалось запустить бота. Проверьте токен и попробуйте снова."
                            self.after(0, lambda msg=error_msg: self.show_error(msg))
                except Exception as e:
                    error_msg = f"Ошибка при перезапуске бота: {str(e)}"
                    self.after(0, lambda msg=error_msg: self.show_error(msg))
            
            restart_thread = threading.Thread(target=restart_bot_thread)
            restart_thread.daemon = True
            restart_thread.start()
    
    def add_log_message(self, message):
        """Добавление сообщения в лог"""
        if hasattr(self, 'log_text') and self.log_text.winfo_exists():
            current_time = time.strftime("%H:%M:%S")
            log_entry = f"[{current_time}] {message}"
            
            # Сохраняем сообщение в истории логов
            self.log_history.append(log_entry)
            
            # Отображаем в текстовом поле
            self.log_text.configure(state="normal")
            self.log_text.insert("end", f"{log_entry}\n")
            self.log_text.see("end")  # Прокрутка к последнему сообщению
            self.log_text.configure(state="disabled")
    
    def create_loading_screen(self):
        """Create an animated loading screen"""
        # Clear previous content
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        
        # Create content frame (centered)
        self.loading_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.loading_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Create small logo at the top
        loading_logo_canvas = ctk.CTkCanvas(self.loading_frame, width=100, height=100, 
                                        bg=self.dark_bg, highlightthickness=0)
        loading_logo_canvas.pack(pady=(0, 20))
        
        # Draw logo directly instead of calling create_small_logo
        # Draw outer circle
        loading_logo_canvas.create_oval(10, 10, 90, 90, fill=self.primary_blue, outline="", tags="logo")
        # Draw inner circle
        loading_logo_canvas.create_oval(20, 20, 80, 80, fill=self.dark_bg, outline="", tags="logo")
        # Draw "NT" letters
        loading_logo_canvas.create_text(50, 50, text="NT",
                                   font=("Segoe UI", 24, "bold"),
                                   fill=self.text_color, tags="logo")
        
        # Create a rotating arc
        arc_thickness = 2
        radius = 45
        
        # Convert angles to coordinates
        x0 = 50 - radius - arc_thickness
        y0 = 50 - radius - arc_thickness
        x1 = 50 + radius + arc_thickness
        y1 = 50 + radius + arc_thickness
        
        loading_logo_canvas.create_arc(
            x0, y0, x1, y1,
            start=45, extent=45,
            style=tk.ARC, width=arc_thickness,
            outline=self.accent_green, tags="arc")
        
        # Brand name with styling
        self.loading_brand_label = ctk.CTkLabel(self.loading_frame, text="NexusTG", 
                                         font=ctk.CTkFont(family="Segoe UI", size=28, weight="bold"),
                                         text_color=self.text_color)
        self.loading_brand_label.pack(pady=(0, 30))
        
        # Loading text
        self.loading_text = ctk.CTkLabel(self.loading_frame, text="Подключение к Telegram...", 
                                     font=ctk.CTkFont(family="Segoe UI", size=14),
                                     text_color=self.secondary_text)
        self.loading_text.pack(pady=(0, 20))
        
        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(self.loading_frame, width=300, height=10)
        self.progress_bar.pack(pady=(0, 10))
        self.progress_bar.set(0)
        
        # Progress percentage
        self.progress_text = ctk.CTkLabel(self.loading_frame, text="0%", 
                                      font=ctk.CTkFont(family="Segoe UI", size=12),
                                      text_color=self.secondary_text)
        self.progress_text.pack()
    
    def simulate_loading(self):
        """Simulate a loading process"""
        # Запускаем бота в отдельном потоке
        threading.Thread(target=self.start_telegram_bot, daemon=True).start()
    
    def start_telegram_bot(self):
        """Запуск Telegram бота"""
        try:
            def update_progress(text, progress):
                """Вспомогательная функция для обновления прогресса в главном потоке"""
                self.after(0, lambda t=text, p=progress: self.update_loading_progress(t, p))
                self.update()  # Принудительно обновляем GUI
                
            update_progress("Подключение к Telegram...", 0.2)
            time.sleep(0.5)
            
            # Создаем экземпляр бота
            self.bot = TelegramBot(self.bot_token, self.owner_ids)
            
            # Устанавливаем колбэки для взаимодействия с GUI
            self.bot.set_callbacks(
                error_callback=lambda msg: self.after(0, lambda m=msg: self.bot_error_callback(m)),
                success_callback=lambda msg: self.after(0, lambda m=msg: self.bot_success_callback(m)),
                message_callback=lambda msg: self.after(0, lambda m=msg: self.bot_message_callback(m))
            )
            
            update_progress("Проверка токена...", 0.4)
            time.sleep(0.5)
            
            # Создаем новый цикл событий для этого потока
            self.event_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.event_loop)
            
            # Запускаем бота в отдельном потоке, чтобы не блокировать UI
            bot_thread = threading.Thread(target=self._run_bot_async, daemon=True)
            bot_thread.start()
            
            # Продолжаем показывать прогресс загрузки независимо от запуска бота
            update_progress("Загрузка компонентов...", 0.6)
            time.sleep(0.5)
            
            update_progress("Инициализация бота...", 0.8)
            time.sleep(0.5)
            
            update_progress("Готово!", 1.0)
            time.sleep(0.5)
            
            # После полной загрузки переходим к основному экрану
            self.after(500, self.create_operation_screen)
            
        except Exception as e:
            error_message = f"Ошибка при запуске бота: {str(e)}"
            self.after(0, lambda msg=error_message: self.show_error(msg))
            self.after(1500, self.create_config_screen)
    
    def _run_bot_async(self):
        """Запускает бота асинхронно в отдельном потоке"""
        try:
            success = self.event_loop.run_until_complete(self.bot.start_bot())
            if not success:
                error_msg = "Не удалось запустить бота. Проверьте токен и попробуйте снова."
                self.after(0, lambda msg=error_msg: self.show_error(msg))
                self.after(1500, self.create_config_screen)
        except Exception as e:
            error_msg = f"Ошибка при запуске бота: {str(e)}"
            self.after(0, lambda msg=error_msg: self.show_error(msg))
    
    def bot_error_callback(self, message):
        """Колбэк для обработки ошибок от бота"""
        self.after(0, lambda: self.show_error(message))
    
    def bot_success_callback(self, message):
        """Колбэк для обработки успешных действий от бота"""
        # Добавляем сообщение в лог вместо показа окна успеха
        self.after(0, lambda: self.add_log_message(message))
        
    def bot_message_callback(self, message):
        """Колбэк для обработки сообщений от бота"""
        # Добавляем сообщение в лог
        self.after(0, lambda: self.add_log_message(message))
        
        # Если это информация о боте, сохраняем ее
        if "Подключен к боту:" in message:
            self.bot_info = message
            
    def add_context_menu(self, entry_widget):
        """Добавляет контекстное меню к виджету ввода"""
        context_menu = tk.Menu(self, tearoff=0, bg=self.dark_bg, fg=self.text_color)
        context_menu.add_command(label="Вставить", command=lambda: self.paste_to_widget(entry_widget))
        context_menu.add_command(label="Копировать", command=lambda: self.copy_from_widget(entry_widget))
        context_menu.add_command(label="Вырезать", command=lambda: self.cut_from_widget(entry_widget))

        entry_widget.bind("<Button-3>", lambda e: self.show_context_menu(e, context_menu))
    def show_context_menu(self, event, menu):
        """Показывает контекстное меню"""
        menu.post(event.x_root, event.y_root)
    
    def paste_to_widget(self, widget):
        """Вставляет текст из буфера обмена в виджет"""
        try:
            clipboard_text = self.clipboard_get()
            # Вставка текста в позицию курсора
            widget.insert("insert", clipboard_text)
        except Exception as e:
            print(f"Ошибка при вставке: {str(e)}")
    
    def copy_from_widget(self, widget):
        """Копирует выделенный текст из виджета в буфер обмена"""
        try:
            if widget.selection_get():
                self.clipboard_clear()
                self.clipboard_append(widget.selection_get())
        except Exception as e:
            print(f"Ошибка при копировании: {str(e)}")
    
    def cut_from_widget(self, widget):
        """Вырезает выделенный текст из виджета в буфер обмена"""
        try:
            if widget.selection_get():
                self.clipboard_clear()
                self.clipboard_append(widget.selection_get())
                widget.delete("sel.first", "sel.last")
        except Exception as e:
            print(f"Ошибка при вырезании: {str(e)}")
            
    def show_commands_screen(self):
        """Показывает экран с командами бота"""
        # Очищаем текущее содержимое
        for widget in self.main_frame.winfo_children():
            widget.destroy()
            
        # Создаем верхнюю панель с кнопкой возврата
        header_frame = ctk.CTkFrame(self.main_frame, fg_color=self.input_bg, height=60)
        header_frame.pack(fill="x", padx=0, pady=0)
        
        # Кнопка возврата
        back_button = ctk.CTkButton(header_frame, 
                                text="Назад", 
                                font=ctk.CTkFont(family="Segoe UI", size=13),
                                fg_color="transparent",
                                text_color=self.secondary_text,
                                hover_color=self.input_bg,
                                height=28,
                                corner_radius=6,
                                command=self.create_operation_screen)
        back_button.place(x=20, y=18)
        
        # Заголовок экрана
        title_label = ctk.CTkLabel(header_frame, text="Команды бота", 
                               font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
                               text_color=self.text_color)
        title_label.place(relx=0.5, y=30, anchor="center")
        
        # Основной контейнер
        main_container = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Информационный текст
        info_label = ctk.CTkLabel(main_container, 
                              text="Список доступных команд бота:",
                              font=ctk.CTkFont(family="Segoe UI", size=16),
                              text_color=self.text_color)
        info_label.pack(anchor="w", pady=(0, 20))
        
        # Карточка команды /start
        command_card = ctk.CTkFrame(main_container, fg_color=self.input_bg, corner_radius=10)
        command_card.pack(fill="x", pady=5)
        
        # Заголовок команды
        command_title = ctk.CTkLabel(command_card, 
                                 text="/start",
                                 font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
                                 text_color=self.primary_blue)
        command_title.pack(anchor="w", padx=20, pady=(15, 5))
        
        # Описание команды
        command_desc = ctk.CTkLabel(command_card, 
                               text="Запуск бота, показ приветственного сообщения и проверка доступа.",
                               font=ctk.CTkFont(family="Segoe UI", size=14),
                               text_color=self.secondary_text)
        command_desc.pack(anchor="w", padx=20, pady=(0, 5))
        
        # Использование
        usage_title = ctk.CTkLabel(command_card, 
                              text="Использование:", 
                              font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
                              text_color=self.text_color)
        usage_title.pack(anchor="w", padx=20, pady=(10, 5))
        
        # Пример использования
        usage_example = ctk.CTkLabel(command_card, 
                                text="Отправьте боту команду /start",
                                font=ctk.CTkFont(family="Segoe UI", size=14),
                                text_color=self.secondary_text)
        usage_example.pack(anchor="w", padx=20, pady=(0, 15))
        
        # Дополнительная информация
        info_frame = ctk.CTkFrame(main_container, fg_color=self.input_bg, corner_radius=10)
        info_frame.pack(fill="x", pady=(20, 5))
        
        # Заголовок информации
        info_title = ctk.CTkLabel(info_frame, 
                              text="Информация о боте",
                              font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
                              text_color=self.text_color)
        info_title.pack(anchor="w", padx=20, pady=(15, 10))
        
        # Содержимое информации
        bot_info_text = """NexusTG предоставляет удобный интерфейс для управления компьютером через Telegram. 
В настоящее время доступна только базовая команда /start для инициализации бота.

В будущих обновлениях будут добавлены новые команды для удаленного управления компьютером."""
        
        info_content = ctk.CTkTextbox(info_frame, fg_color=self.input_bg, 
                                 text_color=self.secondary_text, 
                                 font=ctk.CTkFont(family="Segoe UI", size=14),
                                 height=100, activate_scrollbars=True)
        info_content.pack(fill="x", padx=20, pady=(0, 15))
        info_content.insert("1.0", bot_info_text)
        info_content.configure(state="disabled")

    def check_existing_config(self):
        """Проверка наличия файла конфигурации и автоматический запуск"""
        config_file = "cfg/config.json"
        
        if os.path.exists(config_file):
            try:
                # Загружаем конфигурацию из файла
                with open(config_file, "r") as file:
                    config = json.load(file)
                
                # Проверяем наличие необходимых данных
                if "bot_token" in config and "owner_ids" in config:
                    self.bot_token = config["bot_token"]
                    self.owner_ids = config["owner_ids"]
                    
                    if self.bot_token and self.owner_ids:
                        # Переходим сразу к экрану загрузки и запуску бота
                        self.create_loading_screen()
                        loading_thread = threading.Thread(target=self.simulate_loading)
                        loading_thread.daemon = True
                        loading_thread.start()
                        return
            except Exception as e:
                # Если возникла ошибка при загрузке конфигурации, показываем экран приветствия
                print(f"Ошибка при загрузке конфигурации: {str(e)}")
                
        # Если конфигурация не найдена или не валидна, показываем экран приветствия
        # (этот код выполняется только если return выше не сработал)

    def toggle_custom_dropdown(self, event=None):
        """Показывает или скрывает кастомное выпадающее меню"""
        if self.custom_dropdown_visible and self.custom_dropdown_frame:
            # Если меню видимо, скрываем его
            self.custom_dropdown_frame.destroy()
            self.custom_dropdown_visible = False
            # Убираем обработчик события клика
            self.unbind("<Button-1>")
        else:
            # Если меню скрыто, показываем его
            self.show_custom_dropdown()
    
    def show_custom_dropdown(self):
        """Показывает красивое кастомное выпадающее меню"""
        # Если меню уже видимо, не создаем его снова
        if self.custom_dropdown_visible and self.custom_dropdown_frame:
            return
            
        try:
            # Получаем размеры окна
            window_width = self.winfo_width()
            window_height = self.winfo_height()
            
            # Фиксированное позиционирование в ПРАВОЙ части окна (верхний угол)
            menu_width = 240  # Примерная ширина меню
            menu_height = 220  # Примерная высота меню
            
            # Позиционируем меню в правой верхней части, с отступом от края
            x = window_width - menu_width - 20  # 20px отступ от правого края
            y = 60  # Отступ от верхнего края (под верхней панелью)
            
            # Проверка, чтобы не выходить за пределы окна
            if x < 10:
                x = 10
            if y < 10:
                y = 10
            if y + menu_height > window_height:
                y = max(10, window_height - menu_height - 10)
            
            # Создаем фрейм для выпадающего меню
            self.custom_dropdown_frame = ctk.CTkFrame(
                self, 
                fg_color="#1D2637",
                corner_radius=10,
                border_width=1,
                border_color="#2D374B"
            )
            
            # Используем place для точного позиционирования относительно окна
            self.custom_dropdown_frame.place(x=x, y=y)
            
            # Добавляем контейнер с отступами
            menu_container = ctk.CTkFrame(self.custom_dropdown_frame, fg_color="transparent")
            menu_container.pack(padx=5, pady=5)
            
            # Заголовок меню
            menu_header = ctk.CTkFrame(menu_container, fg_color="transparent", height=30)
            menu_header.pack(fill="x", padx=10, pady=(5, 10))
            
            # Логотип в заголовке
            logo_size = 24
            logo_frame = ctk.CTkFrame(menu_header, fg_color=self.primary_blue, 
                                width=logo_size, height=logo_size, corner_radius=logo_size/2)
            logo_frame.pack(side="left", padx=(0, 8))
            logo_frame.pack_propagate(False)
            
            logo_text = ctk.CTkLabel(logo_frame, text="NT", font=("Segoe UI", 12, "bold"),
                                text_color=self.text_color)
            logo_text.place(relx=0.5, rely=0.5, anchor="center")
            
            menu_title = ctk.CTkLabel(menu_header, text="NexusTG Меню", 
                                font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
                                text_color=self.text_color)
            menu_title.pack(side="left")
            
            # Кнопки для меню (создаем более эффективно)
            # Кнопка "Команды"
            commands_button = self.create_menu_button(
                menu_container, 
                "Команды", 
                "Управление командами бота",
                self.show_commands_screen,
                icon_text="🔧"
            )
            commands_button.pack(fill="x", padx=5, pady=2)
            
            # Кнопка "Добавить"
            add_button = self.create_menu_button(
                menu_container, 
                "Добавить функцию", 
                "Добавление новых возможностей",
                lambda: self.add_log_message("Нажата кнопка: Добавить функцию"),
                icon_text="➕"
            )
            add_button.pack(fill="x", padx=5, pady=2)
            
            # Разделитель
            separator = ctk.CTkFrame(menu_container, height=1, fg_color="#2D374B")
            separator.pack(fill="x", padx=10, pady=8)
            
            # Кнопка "О программе"
            about_button = self.create_menu_button(
                menu_container, 
                "О программе", 
                "Информация о NexusTG",
                self.show_about_dialog,
                icon_text="ℹ️"
            )
            about_button.pack(fill="x", padx=5, pady=2)
            
            # Отмечаем, что меню отображается
            self.custom_dropdown_visible = True
            
            # Привязываем событие закрытия при клике вне меню (один раз)
            self.bind("<Button-1>", self.close_dropdown_if_outside, add="+")
            
            # Обновляем окно, чтобы меню сразу отобразилось правильно
            self.update_idletasks()
            
            # Добавляем отладочное сообщение
            print(f"Окно: ширина={window_width}, высота={window_height}")
            print(f"Меню: x={x}, y={y}, w={menu_width}, h={menu_height}")
            
        except Exception as e:
            print(f"Ошибка при создании меню: {e}")
            # В случае ошибки сбрасываем состояние
            self.custom_dropdown_visible = False
            if hasattr(self, 'custom_dropdown_frame') and self.custom_dropdown_frame:
                self.custom_dropdown_frame.destroy()
    
    def create_menu_button(self, parent, title, subtitle, command, icon_text=None, is_danger=False):
        """Создает стильную кнопку для кастомного меню"""
        # Цвета для разных состояний кнопок
        normal_fg = "#1D2637"
        hover_color = "#E74C3C" if is_danger else "#273245"
        
        # Создаем основной фрейм с фиксированной высотой
        button_frame = ctk.CTkFrame(
            parent, 
            fg_color=normal_fg, 
            corner_radius=8,
            height=60,
            border_width=0
        )
        button_frame._command = command  # Сохраняем команду как атрибут
        
        # Создаем контейнер для содержимого с отступами
        content_frame = ctk.CTkFrame(button_frame, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=10, pady=5)
        content_frame._command = command  # Сохраняем команду как атрибут
        
        # Добавляем иконку, если она указана
        if icon_text:
            icon_label = ctk.CTkLabel(
                content_frame, 
                text=icon_text,
                font=ctk.CTkFont(size=20),
                width=30,
                text_color=self.text_color
            )
            icon_label.pack(side="left", padx=(5, 10))
            icon_label._command = command  # Сохраняем команду как атрибут
        
        # Создаем контейнер для текстовых меток
        text_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        text_frame.pack(side="left", fill="both", expand=True)
        text_frame._command = command  # Сохраняем команду как атрибут
        
        # Заголовок
        title_label = ctk.CTkLabel(
            text_frame, 
            text=title,
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color="#E74C3C" if is_danger else self.text_color,
            anchor="w",
            wraplength=160,
            justify="left"
        )
        title_label.pack(anchor="w", fill="x")
        title_label._command = command  # Сохраняем команду как атрибут
        
        # Подзаголовок
        subtitle_label = ctk.CTkLabel(
            text_frame, 
            text=subtitle,
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=self.secondary_text,
            anchor="w",
            wraplength=160,
            justify="left"
        )
        subtitle_label.pack(anchor="w", fill="x", pady=(2, 0))
        subtitle_label._command = command  # Сохраняем команду как атрибут
        
        # Общая функция для обработки клика
        def handle_click(event, cmd=command):
            # Закрываем меню и выполняем команду
            self.close_dropdown_and_execute(cmd)()
        
        # Создаем функции для эффектов при наведении
        def on_enter(e):
            button_frame.configure(fg_color=hover_color)
            
        def on_leave(e):
            button_frame.configure(fg_color=normal_fg)
            
        # Привязываем события ко всем компонентам для надежности
        for widget in [button_frame, content_frame, text_frame, title_label, subtitle_label]:
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)
            widget.bind("<Button-1>", handle_click)
            
        # Если есть иконка, привязываем события и к ней
        if icon_text:
            icon_label.bind("<Enter>", on_enter)
            icon_label.bind("<Leave>", on_leave)
            icon_label.bind("<Button-1>", handle_click)
        
        return button_frame
    
    def close_dropdown_if_outside(self, event):
        """Закрывает выпадающее меню при клике вне его области"""
        if not self.custom_dropdown_visible or not self.custom_dropdown_frame:
            return
        
        try:
            # Проверяем, был ли клик вне области меню
            x, y = event.x_root, event.y_root
            frame_x = self.custom_dropdown_frame.winfo_rootx()
            frame_y = self.custom_dropdown_frame.winfo_rooty()
            frame_width = self.custom_dropdown_frame.winfo_width()
            frame_height = self.custom_dropdown_frame.winfo_height()
            
            if not (frame_x <= x <= frame_x + frame_width and frame_y <= y <= frame_y + frame_height):
                # Клик был вне меню - закрываем его
                self.custom_dropdown_frame.destroy()
                self.custom_dropdown_visible = False
                # Убираем обработчик нажатия
                self.unbind("<Button-1>")
        except Exception as e:
            # В случае ошибки просто закрываем меню
            if hasattr(self, 'custom_dropdown_frame') and self.custom_dropdown_frame:
                self.custom_dropdown_frame.destroy()
            self.custom_dropdown_visible = False
            self.unbind("<Button-1>")
    
    def close_dropdown_and_execute(self, command):
        """Закрывает выпадающее меню и выполняет команду"""
        def wrapper():
            try:
                # Сначала закрываем меню
                if self.custom_dropdown_visible and self.custom_dropdown_frame:
                    self.custom_dropdown_frame.destroy()
                    self.custom_dropdown_visible = False
                    # Убираем обработчик нажатия
                    self.unbind("<Button-1>")
                
                # Затем выполняем команду
                self.after(10, command)
            except Exception as e:
                # В случае ошибки продолжаем выполнение команды
                self.after(10, command)
                
        return wrapper
    
    def show_about_dialog(self):
        """Показывает экран 'О программе' внутри основного окна"""
        # Убираем логирование, чтобы избежать дублирования
        # self.add_log_message("Открыт экран 'О программе'")
        
        # Очищаем предыдущее содержимое
        for widget in self.main_frame.winfo_children():
            widget.destroy()
            
        # Создаем верхнюю панель с кнопкой возврата
        header_frame = ctk.CTkFrame(self.main_frame, fg_color=self.input_bg, height=60)
        header_frame.pack(fill="x", padx=0, pady=0)
        
        # Кнопка возврата
        back_button = ctk.CTkButton(header_frame, 
                                text="Назад", 
                                font=ctk.CTkFont(family="Segoe UI", size=13),
                                fg_color="transparent",
                                text_color=self.secondary_text,
                                hover_color=self.input_bg,
                                height=28,
                                corner_radius=6,
                                command=self.create_operation_screen)
        back_button.place(x=20, y=18)
        
        # Заголовок экрана
        title_label = ctk.CTkLabel(header_frame, text="О программе", 
                               font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
                               text_color=self.text_color)
        title_label.place(relx=0.5, y=30, anchor="center")
        
        # Основной контейнер - используем скроллируемый фрейм для адаптивности
        main_container = ctk.CTkScrollableFrame(self.main_frame, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Верхняя секция с анимированным логотипом
        header_content = ctk.CTkFrame(main_container, fg_color="#1A202E", corner_radius=15, height=180)
        header_content.pack(fill="x", pady=(0, 20))
        header_content.pack_propagate(False)  # Предотвращаем изменение размера контейнером
        
        # Контейнер для логотипа и названия
        logo_container = ctk.CTkFrame(header_content, fg_color="transparent")
        logo_container.place(relx=0.5, rely=0.5, anchor="center")
        
        # Анимированный логотип приложения (как на главном экране)
        logo_size = 90
        self.about_logo_canvas = ctk.CTkCanvas(logo_container, width=logo_size, height=logo_size, 
                                          bg="#1A202E", highlightthickness=0)
        self.about_logo_canvas.pack(pady=(0, 15))  # Увеличиваем отступ снизу
        
        # Рисуем логотип
        self.about_logo_canvas.create_oval(10, 10, logo_size-10, logo_size-10, 
                                      fill=self.primary_blue, outline="", tags="logo")
        # Рисуем внутренний круг
        inner_offset = 18
        self.about_logo_canvas.create_oval(inner_offset, inner_offset, 
                                      logo_size-inner_offset, logo_size-inner_offset, 
                                      fill="#1A202E", outline="", tags="logo")
        # Рисуем "NT" в логотипе
        self.about_logo_canvas.create_text(logo_size/2, logo_size/2, text="NT",
                                      font=("Segoe UI", 24, "bold"),
                                      fill=self.text_color, tags="logo")
        
        # Добавляем вращающуюся дугу
        self.about_arc_angle = 45
        self.animate_about_logo_arc()
        
        # Название приложения и версия
        app_name = ctk.CTkLabel(logo_container, text="NexusTG", 
                           font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold"),
                           text_color=self.text_color)
        app_name.pack(pady=(0, 5))
        
        app_version = ctk.CTkLabel(logo_container, text="Версия 1.0.0", 
                              font=ctk.CTkFont(family="Segoe UI", size=14),
                              text_color=self.secondary_text)
        app_version.pack()
        
        # Основной контент - описание приложения
        app_desc_frame = ctk.CTkFrame(main_container, fg_color="#1A202E", corner_radius=15)
        app_desc_frame.pack(fill="x", pady=(0, 20))
        
        # Отступы внутри фрейма
        app_desc_inner = ctk.CTkFrame(app_desc_frame, fg_color="transparent")
        app_desc_inner.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Заголовок описания (по центру)
        desc_title = ctk.CTkLabel(app_desc_inner, text="О приложении", 
                             font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
                             text_color=self.text_color)
        desc_title.pack(anchor="center", pady=(0, 15))
        
        # Краткое описание (по центру)
        desc_text = ctk.CTkLabel(app_desc_inner, 
                            text="NexusTG - мощный инструмент для управления компьютером через Telegram. Безопасно контролируйте ваш ПК с любого устройства.",
                            font=ctk.CTkFont(family="Segoe UI", size=14),
                            text_color=self.secondary_text,
                            justify="center",
                            wraplength=500)
        desc_text.pack(fill="x", pady=(0, 15))
        
        # Ключевые особенности
        features_title = ctk.CTkLabel(app_desc_inner, text="Ключевые особенности", 
                                 font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
                                 text_color=self.text_color)
        features_title.pack(anchor="center", pady=(0, 10))
        
        # Список особенностей
        features = [
            "🔒 Безопасное управление",
            "🌍 Доступ с любой точки мира",
            "⚡ Мгновенный отклик",
            "🧰 Гибкие настройки"
        ]
        
        # Контейнер для списка особенностей (центрирование)
        features_container = ctk.CTkFrame(app_desc_inner, fg_color="transparent")
        features_container.pack(pady=(0, 10))
        
        for feature in features:
            feature_label = ctk.CTkLabel(features_container, 
                                    text=feature,
                                    font=ctk.CTkFont(family="Segoe UI", size=14),
                                    text_color=self.secondary_text)
            feature_label.pack(pady=(0, 5))
        
        # Информация о разработчике - двухстороннее расположение
        dev_frame = ctk.CTkFrame(main_container, fg_color="#1A202E", corner_radius=15)
        dev_frame.pack(fill="x", pady=(0, 15))
        
        # Заголовок раздела о разработчике
        dev_title_frame = ctk.CTkFrame(dev_frame, fg_color="transparent")
        dev_title_frame.pack(fill="x", padx=20, pady=(15, 10))
        
        dev_title = ctk.CTkLabel(dev_title_frame, text="Разработчик и контакты", 
                            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
                            text_color=self.text_color)
        dev_title.pack(anchor="center")
        
        # Контейнер для содержимого
        dev_content = ctk.CTkFrame(dev_frame, fg_color="transparent")
        dev_content.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Разделяем на левую и правую части
        dev_left = ctk.CTkFrame(dev_content, fg_color="transparent")
        dev_left.pack(side="left", fill="both", expand=True)
        
        dev_right = ctk.CTkFrame(dev_content, fg_color="transparent")
        dev_right.pack(side="right", fill="both", expand=True)
        
        # ЛЕВАЯ ЧАСТЬ - Информация о разработчике
        # Загрузка и отображение аватара разработчика
        avatar_size = 120
        avatar_path = "cfg/content/kazurage.png"
        
        # Создаем контейнер для аватарки
        avatar_container = ctk.CTkFrame(dev_left, fg_color="transparent")
        avatar_container.pack(pady=10)
        
        # Загружаем аватарку
        try:
            if os.path.exists(avatar_path):
                # Загружаем и размещаем изображение напрямую с помощью CTkImage
                original_image = Image.open(avatar_path)
                # Убедимся, что размер правильный
                avatar_image = original_image.resize((avatar_size, avatar_size))
                # Создаем CTkImage
                ctk_avatar = ctk.CTkImage(
                    light_image=avatar_image,
                    dark_image=avatar_image,
                    size=(avatar_size, avatar_size)
                )
                
                # Создаем круглый фон для аватарки
                avatar_bg = ctk.CTkFrame(
                    avatar_container,
                    width=avatar_size,
                    height=avatar_size,
                    fg_color=self.primary_blue,
                    corner_radius=avatar_size//2
                )
                avatar_bg.pack()
                avatar_bg.pack_propagate(False)  # Фиксируем размер
                
                # Размещаем изображение поверх круглого фона
                avatar_label = ctk.CTkLabel(
                    avatar_bg,
                    text="",
                    image=ctk_avatar
                )
                avatar_label.place(relx=0.5, rely=0.5, anchor="center")
                
                # Сохраняем ссылку на изображение в атрибуте экземпляра, чтобы оно не было удалено сборщиком мусора
                self.avatar_image = ctk_avatar
                
                print("Аватар успешно загружен")
            else:
                # Если файл не найден, показываем заглушку
                avatar_bg = ctk.CTkFrame(
                    avatar_container,
                    width=avatar_size,
                    height=avatar_size, 
                    fg_color=self.primary_blue,
                    corner_radius=avatar_size//2
                )
                avatar_bg.pack()
                avatar_bg.pack_propagate(False)
                
                avatar_text = ctk.CTkLabel(
                    avatar_bg,
                    text="K", 
                    font=ctk.CTkFont(size=48, weight="bold"),
                    text_color=self.text_color
                )
                avatar_text.place(relx=0.5, rely=0.5, anchor="center")
                print(f"Файл аватара не найден: {avatar_path}")
        except Exception as e:
            # В случае ошибки показываем заглушку
            avatar_bg = ctk.CTkFrame(
                avatar_container,
                width=avatar_size,
                height=avatar_size, 
                fg_color=self.primary_blue,
                corner_radius=avatar_size//2
            )
            avatar_bg.pack()
            avatar_bg.pack_propagate(False)
            
            avatar_text = ctk.CTkLabel(
                avatar_bg,
                text="K", 
                font=ctk.CTkFont(size=48, weight="bold"),
                text_color=self.text_color
            )
            avatar_text.place(relx=0.5, rely=0.5, anchor="center")
            print(f"Ошибка при загрузке аватара: {str(e)}")
        
        # Имя разработчика
        dev_name = ctk.CTkLabel(dev_left, text="kazurage", 
                           font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
                           text_color=self.text_color)
        dev_name.pack()
        
        # Роль
        dev_role = ctk.CTkLabel(dev_left, text="Ведущий разработчик", 
                           font=ctk.CTkFont(family="Segoe UI", size=14),
                           text_color=self.secondary_text)
        dev_role.pack(pady=(0, 10))
        
        # ПРАВАЯ ЧАСТЬ - Кнопки социальных сетей
        contacts_title = ctk.CTkLabel(dev_right, text="Связаться", 
                                 font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
                                 text_color=self.text_color)
        contacts_title.pack(pady=(5, 15))
        
        # Кнопка Telegram-аккаунта
        tg_account_btn = ctk.CTkButton(dev_right, 
                                  text="Telegram", 
                                  font=ctk.CTkFont(family="Segoe UI", size=14),
                                  fg_color=self.primary_blue,
                                  hover_color="#1565c0",
                                  corner_radius=10,
                                  height=38,
                                  width=180,
                                  command=lambda: webbrowser.open("https://t.me/kazurage"))
        tg_account_btn.pack(pady=(0, 10))
        
        # Кнопка Telegram-канала
        tg_channel_btn = ctk.CTkButton(dev_right, 
                                  text="Telegram канал", 
                                  font=ctk.CTkFont(family="Segoe UI", size=14),
                                  fg_color="#0088cc",
                                  hover_color="#0077b3",
                                  corner_radius=10,
                                  height=38,
                                  width=180,
                                  command=lambda: webbrowser.open("https://t.me/INTkazurage"))
        tg_channel_btn.pack(pady=(0, 10))
        
        # Кнопка Github
        github_btn = ctk.CTkButton(dev_right, 
                                  text="Github", 
                                  font=ctk.CTkFont(family="Segoe UI", size=14),
                                  fg_color="#333333",
                                  hover_color="#24292e",
                                  corner_radius=10,
                                  height=38,
                                  width=180,
                                  command=lambda: webbrowser.open("https://github.com/kazurage"))
        github_btn.pack()
    
    def animate_about_logo_arc(self):
        """Анимирует дугу вокруг логотипа на экране 'О программе'"""
        try:
            if hasattr(self, 'about_logo_canvas') and self.about_logo_canvas.winfo_exists():
                self.about_logo_canvas.delete("arc")
                
                # Параметры дуги
                arc_thickness = 2
                radius = 45
                logo_size = 90
                
                # Координаты дуги
                x0 = logo_size/2 - radius - arc_thickness
                y0 = logo_size/2 - radius - arc_thickness
                x1 = logo_size/2 + radius + arc_thickness
                y1 = logo_size/2 + radius + arc_thickness
                
                # Рисуем дугу
                self.about_logo_canvas.create_arc(
                    x0, y0, x1, y1,
                    start=self.about_arc_angle, extent=45,
                    style=tk.ARC, width=arc_thickness,
                    outline=self.accent_green, tags="arc")
                
                # Обновляем угол для следующего кадра
                self.about_arc_angle = (self.about_arc_angle + 2) % 360
                
                # Продолжаем анимацию, если канвас существует
                if self.about_logo_canvas.winfo_exists():
                    self.after(50, self.animate_about_logo_arc)
        except Exception as e:
            # Если произошла ошибка, просто игнорируем
            print(f"Ошибка анимации логотипа на странице 'О программе': {str(e)}")

if __name__ == "__main__":
    app = NexusTGApp()
    app.mainloop()