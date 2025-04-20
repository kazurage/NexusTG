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
        error_window.geometry("350x150")
        error_window.resizable(False, False)
        error_window.configure(fg_color=self.dark_bg)
        
        error_frame = ctk.CTkFrame(error_window, fg_color="transparent")
        error_frame.pack(expand=True, fill="both", padx=20, pady=20)
        
        error_label = ctk.CTkLabel(error_frame, text="⚠️ Ошибка", 
                              font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
                              text_color="#FF5252")
        error_label.pack(pady=(0, 10))
        
        message_label = ctk.CTkLabel(error_frame, text=message, 
                                 font=ctk.CTkFont(family="Segoe UI", size=14),
                                 text_color=self.text_color)
        message_label.pack(pady=(0, 15))
        
        ok_button = ctk.CTkButton(error_frame, text="OK", 
                             font=ctk.CTkFont(family="Segoe UI", size=14),
                             fg_color="#FF5252",
                             hover_color="#E64747",
                             corner_radius=8,
                             command=error_window.destroy,
                             width=100)
        ok_button.pack()
        
        # Make modal
        error_window.transient(self)
        error_window.grab_set()
        self.wait_window(error_window)
    
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
        """Create the main operation screen after successful loading"""
        # Clear previous content
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        
        # Create header with title
        header_frame = ctk.CTkFrame(self.main_frame, fg_color=self.input_bg, height=60)
        header_frame.pack(fill="x", padx=0, pady=0)
        
        # Добавляем заголовок и кнопку настроек
        header_left_frame = ctk.CTkFrame(header_frame, fg_color="transparent", height=60)
        header_left_frame.place(x=20, y=18)
        
        header_title = ctk.CTkLabel(header_left_frame, text="Панель управления", 
                                 font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
                                 text_color=self.text_color)
        header_title.pack(side="left")
        
        # Добавляем кнопку настроек
        settings_button = ctk.CTkButton(header_left_frame, 
                                   text="Настройки", 
                                   font=ctk.CTkFont(family="Segoe UI", size=13),
                                   fg_color="transparent",
                                   text_color=self.secondary_text,
                                   hover_color=self.input_bg,
                                   height=28,
                                   width=20,
                                   corner_radius=6,
                                   command=lambda: self.add_log_message("Нажата кнопка настроек"))
        settings_button.pack(side="left", padx=(15, 0))
        
        # Создаем выпадающее меню с улучшенным стилем
        self.dropdown_menu = tk.Menu(self, tearoff=0, bg=self.dark_bg, fg=self.text_color, 
                               activebackground=self.primary_blue, activeforeground="white",
                               relief="solid", bd=1, font=("Segoe UI", 11))
        
        # Привязываем кнопки к соответствующим методам
        self.dropdown_menu.add_command(label="Команды", command=self.show_commands_screen)
        self.dropdown_menu.add_command(label="Добавить", command=lambda: self.add_log_message("Нажата кнопка: Добавить"))
        self.dropdown_menu.add_command(label="Настройки", command=lambda: self.add_log_message("Нажата кнопка: Настройки"))
        self.dropdown_menu.add_separator()
        self.dropdown_menu.add_command(label="NexusTG", command=lambda: self.add_log_message("Нажата кнопка: NexusTG"))
        
        # Фрейм для кнопок справа
        right_buttons_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        right_buttons_frame.place(relx=0.98, y=30, anchor="e")
        
        # Добавляем кнопку остановки/запуска бота
        self.toggle_bot_button = ctk.CTkButton(right_buttons_frame, 
                                          text="Остановить", 
                                          font=ctk.CTkFont(family="Segoe UI", size=14),
                                          fg_color=self.primary_blue,
                                          hover_color="#1565c0",
                                          height=32,
                                          corner_radius=8,
                                          command=self.toggle_bot_status)
        self.toggle_bot_button.pack(side="left", padx=(0, 15))
        
        # Добавляем кнопку с иконкой проекта справа
        logo_button_frame = ctk.CTkFrame(right_buttons_frame, fg_color="transparent", width=40, height=40)
        logo_button_frame.pack(side="left")
        
        # Создаем канвас для иконки
        self.project_logo_canvas = ctk.CTkCanvas(logo_button_frame, width=40, height=40, 
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
        
        # Функция для показа выпадающего меню при нажатии на иконку
        def show_menu(event):
            self.dropdown_menu.post(event.x_root, event.y_root)
        
        # Привязываем нажатие к показу меню
        self.project_logo_canvas.bind("<Button-1>", show_menu)
        
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
        
        # Status info
        self.bot_status_info = ctk.CTkLabel(info_frame, 
                              text=f"Статус: Активен", 
                              font=ctk.CTkFont(family="Segoe UI", size=14),
                              text_color=self.secondary_text)
        self.bot_status_info.pack(anchor="w", padx=20, pady=(2, 15))
        
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
        
        # Добавляем информативные логи
        current_time = time.strftime("%H:%M:%S")
        self.log_text.insert("end", f"[{current_time}] Приложение NexusTG запущено\n")
        
        # Добавляем информацию о боте, если она есть
        if hasattr(self, 'bot_info') and self.bot_info:
            self.log_text.insert("end", f"[{current_time}] {self.bot_info}\n")
        
        self.log_text.insert("end", f"[{current_time}] Бот готов к работе. Доступна команда /start\n")
        self.log_text.see("end")  # Прокрутка к последнему сообщению
        self.log_text.configure(state="disabled")  # Make read-only
        
    def toggle_bot_status(self):
        """Переключение статуса бота (остановка/запуск)"""
        if hasattr(self, 'bot') and self.bot.is_running:
            # Останавливаем бота
            threading.Thread(target=self.stop_bot, daemon=True).start()
            self.toggle_bot_button.configure(text="Запустить", fg_color="#28a745", hover_color="#218838")
            self.bot_status_info.configure(text="Статус: Остановлен")
            self.add_log_message("Бот остановлен")
        else:
            # Запускаем бота снова
            threading.Thread(target=self.restart_bot, daemon=True).start()
            self.toggle_bot_button.configure(text="Остановить", fg_color=self.primary_blue, hover_color="#1565c0")
            self.bot_status_info.configure(text="Статус: Активен")
            self.add_log_message("Бот запущен")
    
    def stop_bot(self):
        """Остановка бота"""
        if hasattr(self, 'bot') and self.event_loop:
            self.event_loop.run_until_complete(self.bot.stop_bot())
    
    def restart_bot(self):
        """Перезапуск бота"""
        if hasattr(self, 'bot'):
            # Запускаем бота снова
            self.event_loop.run_until_complete(self.bot.start_bot())
    
    def add_log_message(self, message):
        """Добавление сообщения в лог"""
        if hasattr(self, 'log_text') and self.log_text.winfo_exists():
            current_time = time.strftime("%H:%M:%S")
            self.log_text.configure(state="normal")
            self.log_text.insert("end", f"[{current_time}] {message}\n")
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
            # Установка значений прогресса
            self.update_loading_progress("Подключение к Telegram...", 0.2)
            time.sleep(0.5)
            
            # Создаем экземпляр бота
            self.bot = TelegramBot(self.bot_token, self.owner_ids)
            
            # Устанавливаем колбэки для взаимодействия с GUI
            self.bot.set_callbacks(
                error_callback=self.bot_error_callback,
                success_callback=self.bot_success_callback,
                message_callback=self.bot_message_callback
            )
            
            self.update_loading_progress("Проверка токена...", 0.4)
            time.sleep(0.5)
            
            # Создаем цикл событий для асинхронного запуска бота
            self.event_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.event_loop)
            
            # Запуск бота и проверка валидности токена
            success = self.event_loop.run_until_complete(self.bot.start_bot())
            
            if not success:
                # Если токен невалидный, показываем ошибку
                self.after(0, lambda: self.show_error("Неверный токен бота. Пожалуйста, проверьте и введите заново."))
                self.after(1500, self.create_config_screen)  # Возврат к экрану конфигурации
                return
            
            # Продолжаем загрузку, если токен валидный
            self.update_loading_progress("Загрузка компонентов...", 0.6)
            time.sleep(0.5)
            
            self.update_loading_progress("Инициализация бота...", 0.8)
            time.sleep(0.5)
            
            self.update_loading_progress("Готово!", 1.0)
            time.sleep(0.5)
            
            # Переход к основному экрану
            self.after(500, self.loading_complete)
            
        except Exception as e:
            # В случае ошибки показываем сообщение и возвращаемся к экрану конфигурации
            error_message = f"Ошибка при запуске бота: {str(e)}"
            self.after(0, lambda: self.show_error(error_message))
            self.after(1500, self.create_config_screen)
    
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
                        loading_thread = threading.Thread(target=self.start_telegram_bot)
                        loading_thread.daemon = True
                        loading_thread.start()
                        return
            except Exception as e:
                # Если возникла ошибка при загрузке конфигурации, показываем экран приветствия
                print(f"Ошибка при загрузке конфигурации: {str(e)}")
                
        # Если конфигурация не найдена или не валидна, показываем экран приветствия
        # (этот код выполняется только если return выше не сработал)

if __name__ == "__main__":
    app = NexusTGApp()
    app.mainloop()