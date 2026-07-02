import requests
import tkinter as tk
from tkinter import ttk
import threading
import xml.etree.ElementTree as ET

class NewsReaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Google News Reader")
        
        # Оптимальный размер для телефона
        self.root.geometry("360x640")
        self.root.minsize(320, 500)
        self.root.configure(bg="#f5f5f5")
        
        self.news_data = []  # Хранилище новостей
        self.setup_ui()
        self.load_news()
    
    def setup_ui(self):
        # === ВЕРХНЯЯ ПАНЕЛЬ ===
        header = tk.Frame(self.root, bg="#1a73e8", height=50)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        # Заголовок в панели
        tk.Label(
            header,
            text="Google News",
            font=("Arial", 16, "bold"),
            bg="#1a73e8",
            fg="white"
        ).pack(expand=True)
        
        # === СТАТУС-СТРОКА ===
        self.status_label = tk.Label(
            self.root,
            text="Загрузка новостей...",
            font=("Arial", 9),
            bg="#f5f5f5",
            fg="#888888",
            anchor="center"
        )
        self.status_label.pack(fill=tk.X, pady=(8, 4))
        
        # === СПИСОК НОВОСТЕЙ ===
        # Фрейм для Listbox и скроллбара
        list_frame = tk.Frame(self.root, bg="#f5f5f5")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Listbox для новостей
        self.news_listbox = tk.Listbox(
            list_frame,
            font=("Arial", 11),
            bg="white",
            fg="#333333",
            selectbackground="#1a73e8",
            selectforeground="white",
            activestyle="none",
            relief=tk.FLAT,
            highlightthickness=1,
            highlightcolor="#dddddd",
            highlightbackground="#dddddd"
        )
        
        # Скроллбар
        scrollbar = tk.Scrollbar(list_frame, orient=tk.VERTICAL)
        scrollbar.config(command=self.news_listbox.yview)
        self.news_listbox.config(yscrollcommand=scrollbar.set)
        
        # Размещение
        self.news_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Привязка события выбора
        self.news_listbox.bind('<<ListboxSelect>>', self.on_select)
        
        # === КАРТОЧКА ДЕТАЛЕЙ ===
        self.detail_frame = tk.Frame(
            self.root,
            bg="white",
            relief=tk.FLAT,
            highlightbackground="#dddddd",
            highlightthickness=1
        )
        self.detail_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Заголовок новости в карточке
        self.detail_title = tk.Label(
            self.detail_frame,
            text="Выберите новость",
            font=("Arial", 11, "bold"),
            bg="white",
            fg="#333333",
            wraplength=300,
            justify=tk.LEFT,
            anchor="w"
        )
        self.detail_title.pack(fill=tk.X, padx=10, pady=(10, 5))
        
        # Источник в карточке
        self.detail_source = tk.Label(
            self.detail_frame,
            text="",
            font=("Arial", 9),
            bg="white",
            fg="#888888",
            anchor="w"
        )
        self.detail_source.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # === КНОПКА ОБНОВЛЕНИЯ ===
        self.refresh_btn = tk.Button(
            self.root,
            text="Обновить новости",
            command=self.load_news,
            font=("Arial", 11, "bold"),
            bg="#1a73e8",
            fg="white",
            padx=20,
            pady=10,
            cursor="hand2",
            relief=tk.FLAT,
            activebackground="#1557b0",
            activeforeground="white"
        )
        self.refresh_btn.pack(pady=(10, 15))
    
    def load_news(self):
        """Загрузка новостей в фоновом потоке"""
        self.refresh_btn.config(state="disabled", text="Загрузка...")
        self.status_label.config(text="Загрузка новостей...")
        self.news_listbox.delete(0, tk.END)
        self.news_data = []
        
        def task():
            try:
                # RSS-лента Google News
                url = "https://news.google.com/rss?hl=ru&gl=RU&ceid=RU:ru"
                response = requests.get(url, timeout=15)
                response.encoding = 'utf-8'
                
                # Парсим XML
                root = ET.fromstring(response.content)
                
                # Находим все новости
                items = root.findall(".//item")
                
                # Обрабатываем первые 20 новостей
                for i, item in enumerate(items[:20], 1):
                    # Заголовок
                    title_elem = item.find("title")
                    if title_elem is not None and title_elem.text:
                        full_title = title_elem.text.strip()
                    else:
                        continue
                    
                    # Разделяем заголовок и источник
                    if " - " in full_title:
                        parts = full_title.rsplit(" - ", 1)
                        title = parts[0].strip()
                        source = parts[1].strip()
                    else:
                        title = full_title
                        source = "Google News"
                    
                    # Сохраняем данные
                    self.news_data.append({
                        "title": title,
                        "source": source
                    })
                    
                    # Добавляем в Listbox (только номер и заголовок)
                    display_text = f"{i}. {title[:60]}{'...' if len(title) > 60 else ''}"
                    self.news_listbox.insert(tk.END, display_text)
                
                # Обновляем статус
                count = len(self.news_data)
                self.status_label.config(text=f"Загружено новостей: {count}")
                
            except Exception as e:
                self.status_label.config(text="Ошибка загрузки")
                self.news_listbox.insert(tk.END, "❌ Не удалось загрузить новости")
                self.news_listbox.insert(tk.END, "Проверьте подключение к интернету")
            
            finally:
                self.refresh_btn.config(state="normal", text="Обновить новости")
        
        # Запускаем в отдельном потоке
        thread = threading.Thread(target=task, daemon=True)
        thread.start()
    
    def on_select(self, event):
        """Обработка выбора новости из списка"""
        selection = self.news_listbox.curselection()
        if selection:
            index = selection[0]
            if index < len(self.news_data):
                news = self.news_data[index]
                self.detail_title.config(text=news["title"])
                self.detail_source.config(text=f"Источник: {news['source']}")

# Запуск приложения
if __name__ == "__main__":
    root = tk.Tk()
    app = NewsReaderApp(root)
    root.mainloop()
