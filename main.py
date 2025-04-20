import customtkinter as ctk
import tkinter as tk
from PIL import Image, ImageTk
import os
import time
import threading
import math
import json

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
        
        # Add fullscreen toggle button
        self.fullscreen = False
        self.fullscreen_button = ctk.CTkButton(self, 
                                          text="⛶", 
                                          font=ctk.CTkFont(size=16),
                                          fg_color="transparent",
                                          hover_color="#2A303C",
                                          width=30,
                                          height=30,
                                          corner_radius=15,
                                          command=self.toggle_fullscreen)
        self.fullscreen_button.place(relx=0.97, rely=0.03, anchor="ne")
        
        # Initialize configuration variables
        self.bot_token = ""
        self.owner_ids = []
        
        # Bind window resize event
        self.bind("<Configure>", self.on_window_resize)
    
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
                                     command=self.save_config,
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
        
        self.owner_entries.append(entry)
        
        # Update add button state
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
    
    def create_logo(self):
        """Create a smooth, anti-aliased logo"""
        self.logo_canvas.delete("all")
        
        # Draw outer circle with smoother edges
        self.logo_canvas.create_oval(10, 10, 110, 110, fill=self.primary_blue, outline="", tags="logo")
        
        # Draw inner circle
        self.logo_canvas.create_oval(20, 20, 100, 100, fill=self.dark_bg, outline="", tags="logo")
        
        # Draw "NT" letters with better positioning and font
        self.logo_canvas.create_text(60, 60, text="NT",
                                font=("Segoe UI", 32, "bold"),
                                fill=self.text_color, tags="logo")
    
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
    
    def animate_small_arc(self):
        """Animate a rotating arc around the small logo"""
        if hasattr(self, 'small_logo_canvas'):
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
            
            # Update angle for next animation
            self.small_arc_angle = (self.small_arc_angle + 2) % 360
            
            # Only continue animation if canvas still exists
            if self.small_logo_canvas.winfo_exists():
                self.after(50, self.animate_small_arc)
    
    def start_button_clicked(self):
        """Handle start button click"""
        # Simple visual feedback
        original_color = self.primary_blue
        self.start_button.configure(fg_color=self.accent_green)
        self.update()
        
        # Reset button color after delay
        self.after(200, lambda: self.start_button.configure(fg_color=original_color))
        
        # Switch to configuration screen
        self.after(300, self.create_config_screen)
    
    def save_config(self):
        """Save the configuration"""
        # Get bot token
        bot_token = self.token_entry.get().strip()
        
        # Get owner IDs (non-empty)
        owner_ids = []
        for entry in self.owner_entries:
            owner_id = entry.get().strip()
            if owner_id:
                owner_ids.append(owner_id)
        
        # Validate inputs (simple validation)
        if not bot_token:
            self.show_error("Введите токен бота")
            return
            
        if not owner_ids:
            self.show_error("Добавьте хотя бы одного владельца")
            return
        
        # Store the configuration
        self.bot_token = bot_token
        self.owner_ids = owner_ids
        
        # Save to config file
        config = {
            "bot_token": bot_token,
            "owner_ids": owner_ids
        }
        
        try:
            # Create cfg directory if not exists
            if not os.path.exists("cfg"):
                os.makedirs("cfg")
                
            with open("cfg/config.json", "w") as file:
                json.dump(config, file, indent=4)
                
            # Show success message
            self.show_success("Конфигурация успешно сохранена")
            
            # Here you would proceed to the next screen or start the bot
            # For now, we'll just go back to the welcome screen
            self.after(1500, self.create_welcome_screen)
            
        except Exception as e:
            self.show_error(f"Ошибка при сохранении: {str(e)}")
    
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
    
    def show_success(self, message):
        """Show success message"""
        success_window = ctk.CTkToplevel(self)
        success_window.title("Успех")
        success_window.geometry("350x150")
        success_window.resizable(False, False)
        success_window.configure(fg_color=self.dark_bg)
        
        success_frame = ctk.CTkFrame(success_window, fg_color="transparent")
        success_frame.pack(expand=True, fill="both", padx=20, pady=20)
        
        success_label = ctk.CTkLabel(success_frame, text="✓ Успех", 
                                 font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
                                 text_color=self.accent_green)
        success_label.pack(pady=(0, 10))
        
        message_label = ctk.CTkLabel(success_frame, text=message, 
                                 font=ctk.CTkFont(family="Segoe UI", size=14),
                                 text_color=self.text_color)
        message_label.pack(pady=(0, 15))
        
        ok_button = ctk.CTkButton(success_frame, text="OK", 
                             font=ctk.CTkFont(family="Segoe UI", size=14),
                             fg_color=self.accent_green,
                             hover_color="#09B374",
                             corner_radius=8,
                             command=success_window.destroy,
                             width=100)
        ok_button.pack()
        
        # Make modal and auto-close
        success_window.transient(self)
        success_window.after(1500, success_window.destroy)
    
    def toggle_fullscreen(self):
        """Toggle fullscreen mode"""
        self.fullscreen = not self.fullscreen
        self.attributes("-fullscreen", self.fullscreen)
        
        # Change button text based on state
        if self.fullscreen:
            self.fullscreen_button.configure(text="⮌")
        else:
            self.fullscreen_button.configure(text="⛶")
    
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

if __name__ == "__main__":
    app = NexusTGApp()
    app.mainloop()