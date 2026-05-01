import platform
import subprocess
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QHBoxLayout, 
                             QPushButton, QGroupBox, QGridLayout)
from PyQt6.QtCore import Qt

class WelcomeTab(QWidget):
    def __init__(self):
        super().__init__()
        self._init_ui()
        
    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # Title
        title = QLabel("ZelixOS'e Hoşgeldiniz!")
        title.setObjectName("title_label")
        layout.addWidget(title)
        
        subtitle = QLabel("Sisteminizi kolayca yönetin ve özelleştirin.")
        subtitle.setObjectName("subtitle_label")
        layout.addWidget(subtitle)
        
        # System Info Group
        sys_group = QGroupBox("Sistem Bilgisi")
        sys_layout = QGridLayout(sys_group)
        
        info = {
            "OS": "ZelixOS",
            "Kernel": platform.release(),
            "Mimari": platform.machine(),
        }
        
        # Try to get DE
        try:
            de = subprocess.check_output("echo $XDG_CURRENT_DESKTOP", shell=True, text=True).strip()
            if not de: de = "Bilinmiyor"
            info["Masaüstü Ortamı"] = de
        except:
            info["Masaüstü Ortamı"] = "Bilinmiyor"
            
        row = 0
        for k, v in info.items():
            k_label = QLabel(f"{k}:")
            k_label.setObjectName("sysinfo_key")
            v_label = QLabel(v)
            v_label.setObjectName("sysinfo_val")
            
            sys_layout.addWidget(k_label, row, 0)
            sys_layout.addWidget(v_label, row, 1)
            row += 1
            
        layout.addWidget(sys_group)
        
        # Quick Links
        links_group = QGroupBox("Hızlı Bağlantılar")
        links_layout = QHBoxLayout(links_group)
        
        btn_wiki = QPushButton("Wiki")
        btn_forum = QPushButton("Forum")
        btn_discord = QPushButton("Discord")
        btn_github = QPushButton("GitHub")
        
        # In a real app, these would open QDesktopServices.openUrl()
        links_layout.addWidget(btn_wiki)
        links_layout.addWidget(btn_forum)
        links_layout.addWidget(btn_discord)
        links_layout.addWidget(btn_github)
        
        layout.addWidget(links_group)
        
        layout.addStretch()
