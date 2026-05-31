from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QGroupBox, 
                             QGridLayout, QPushButton, QMessageBox, QScrollArea, QHBoxLayout)
from PyQt6.QtCore import Qt
import subprocess
import shutil
from utils.translations import Translator

class AppsTab(QWidget):
    def __init__(self, parent_window):
        super().__init__()
        self.parent_window = parent_window
        self._init_ui()
        Translator.add_listener(self)
        
    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Header with back button
        header_layout = QHBoxLayout()
        self.btn_back = QPushButton()
        self.btn_back.setObjectName("back_btn")
        self.btn_back.clicked.connect(lambda: self.parent_window.navigate_to(0))
        header_layout.addWidget(self.btn_back)
        header_layout.addStretch()
        main_layout.addLayout(header_layout)
        
        self.title = QLabel()
        self.title.setObjectName("title_label")
        main_layout.addWidget(self.title)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll.setStyleSheet("background-color: transparent;")
        
        scroll_widget = QWidget()
        layout = QVBoxLayout(scroll_widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setSpacing(25)
        
        self.categories = {
            "Gaming": {
                "apps": [
                    ("RetroArch", "retroarch"),
                    ("Lutris", "lutris"),
                    ("ProtonTricks", "protontricks"),
                    ("MangoHud", "mangohud"),
                    ("Wine", "wine")
                ],
                "extra_deps": "gamemode gamescope wine-staging winetricks vulkan-radeon vulkan-intel vulkan-icd-loader"
            },
            "Office": {
                "apps": [
                    ("LibreOffice", "libreoffice-fresh"),
                    ("Okular", "okular"),
                    ("Calligra", "calligra")
                ],
                "extra_deps": ""
            },
            "Editing": {
                "apps": [
                    ("Kdenlive", "kdenlive"),
                    ("OBS Studio", "obs-studio"),
                    ("GIMP", "gimp"),
                    ("Blender", "blender")
                ],
                "extra_deps": ""
            },
            "Browsers & Comm": {
                "apps": [
                    ("Firefox", "firefox"),
                    ("Chromium", "chromium"),
                    ("Falkon", "falkon"),
                    ("Telegram", "telegram-desktop")
                ],
                "extra_deps": ""
            }
        }
        
        self.category_widgets = []
        
        for cat_name, cat_data in self.categories.items():
            group = QGroupBox(cat_name)
            grid = QGridLayout(group)
            grid.setSpacing(15)
            grid.setContentsMargins(20, 30, 20, 20)
            
            # Install All button
            btn_install_all = QPushButton()
            btn_install_all.setObjectName("primary_btn")
            
            apps_list = cat_data["apps"]
            extra_deps = cat_data["extra_deps"]
            
            all_pkgs = " ".join([pkg for _, pkg in apps_list])
            if extra_deps:
                all_pkgs += " " + extra_deps
                
            btn_install_all.clicked.connect(lambda checked, pkgs=all_pkgs: self.install_app(pkgs))
            
            # Save references to update text later
            self.category_widgets.append({
                "btn_install_all": btn_install_all,
                "app_btns": []
            })
            
            grid.addWidget(btn_install_all, 0, 0, 1, 3)
            
            row, col = 1, 0
            for app_name, pkg_name in apps_list:
                btn = QPushButton()
                btn.clicked.connect(lambda checked, pkg=pkg_name: self.install_app(pkg))
                grid.addWidget(btn, row, col)
                
                self.category_widgets[-1]["app_btns"].append((btn, app_name))
                
                col += 1
                if col > 2:
                    col = 0
                    row += 1
                    
            layout.addWidget(group)
            
        scroll.setWidget(scroll_widget)
        main_layout.addWidget(scroll)
        
        self.retranslate_ui()

    def retranslate_ui(self):
        self.btn_back.setText(Translator.get("btn_back"))
        self.title.setText(Translator.get("apps_title"))
        
        install_text = Translator.get("btn_install")
        install_all_text = Translator.get("btn_install_all")
        
        for cat_data in self.category_widgets:
            cat_data["btn_install_all"].setText(install_all_text)
            for btn, app_name in cat_data["app_btns"]:
                btn.setText(f"{app_name} {install_text}")

    def install_app(self, packages):
        terminals = [
            ("alacritty", ["alacritty", "-e"]),
            ("konsole", ["konsole", "-e"]),
            ("gnome-terminal", ["gnome-terminal", "--"]),
            ("xfce4-terminal", ["xfce4-terminal", "-e"]),
            ("kitty", ["kitty", "--"])
        ]
        
        selected_term = None
        for term_name, term_cmd in terminals:
            if shutil.which(term_name):
                selected_term = term_cmd
                break
                
        if not selected_term:
            QMessageBox.warning(self, Translator.get("msg_error"), Translator.get("msg_unsupported_term"))
            return
            
        command = selected_term + ["sudo", "pacman", "-S"] + packages.split()
        try:
            subprocess.Popen(command)
        except Exception as e:
            QMessageBox.warning(self, Translator.get("msg_error"), f"{Translator.get('msg_term_fail')} {e}")
