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
