import os
import subprocess
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QHBoxLayout, 
                             QPushButton, QGridLayout, QComboBox, QSpacerItem, 
                             QSizePolicy)
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QDesktopServices
from utils.translations import Translator

class DashboardTab(QWidget):
    def __init__(self, parent_window):
        super().__init__()
        self.parent_window = parent_window
        self._init_ui()
        Translator.add_listener(self)
        
    def _init_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(40, 40, 40, 20)
        self.layout.setSpacing(10)
        
        # Header
        header_layout = QVBoxLayout()
        header_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.title = QLabel()
        self.title.setObjectName("dashboard_title")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.subtitle = QLabel()
        self.subtitle.setObjectName("dashboard_subtitle")
        self.subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.subtitle.setWordWrap(True)
        self.subtitle.setMinimumHeight(140)
        self.subtitle.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        
        header_layout.addWidget(self.title)
        header_layout.addSpacing(10)
        header_layout.addWidget(self.subtitle)
        
        self.layout.addLayout(header_layout)
        self.layout.addSpacing(30)
        
        # Grid section
        grid_layout = QGridLayout()
        grid_layout.setSpacing(15)
        
        # Headers
        self.lbl_doc = QLabel()
        self.lbl_sup = QLabel()
        self.lbl_proj = QLabel()
        
        for i, lbl in enumerate([self.lbl_doc, self.lbl_sup, self.lbl_proj]):
            lbl.setObjectName("grid_header")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            grid_layout.addWidget(lbl, 0, i)
            
        # Row 1
        self.btn_readme = QPushButton()
        self.btn_forum = QPushButton()
        self.btn_get_involved = QPushButton()
        
        # Row 2
        self.btn_release_info = QPushButton()
        self.btn_software = QPushButton()
        self.btn_development = QPushButton()
        
        # Row 3
        self.btn_wiki = QPushButton()
        self.btn_system = QPushButton()
        self.btn_donate = QPushButton()
        
        # Add to grid
        grid_layout.addWidget(self.btn_readme, 1, 0)
        grid_layout.addWidget(self.btn_forum, 1, 1)
        grid_layout.addWidget(self.btn_get_involved, 1, 2)
        
        grid_layout.addWidget(self.btn_release_info, 2, 0)
        grid_layout.addWidget(self.btn_software, 2, 1)
        grid_layout.addWidget(self.btn_development, 2, 2)
        
        grid_layout.addWidget(self.btn_wiki, 3, 0)
        grid_layout.addWidget(self.btn_system, 3, 1)
        grid_layout.addWidget(self.btn_donate, 3, 2)
        
        self.layout.addLayout(grid_layout)
        
        self.layout.addSpacing(30)
        
        # Installation section
        install_layout = QVBoxLayout()
        install_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_install = QLabel()
        self.lbl_install.setObjectName("grid_header")
        self.lbl_install.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.btn_install = QPushButton()
        self.btn_install.setObjectName("launch_installer_btn")
        self.btn_install.clicked.connect(self.launch_installer)
        
        install_layout.addWidget(self.lbl_install)
        install_layout.addWidget(self.btn_install)
        self.layout.addLayout(install_layout)
        
        self.layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        
        # Footer
        footer_layout = QHBoxLayout()
        
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["English", "Turkish"])
        # Set current selection
        idx = self.lang_combo.findText(Translator.get_language())
        if idx >= 0:
            self.lang_combo.setCurrentIndex(idx)
        self.lang_combo.setFixedWidth(150)
        self.lang_combo.currentTextChanged.connect(self.change_language)
        
        footer_layout.addWidget(self.lang_combo)
        footer_layout.addStretch()
        
        # Social Icons
        social_layout = QHBoxLayout()
        btn_tg = QPushButton("TG")
        btn_dc = QPushButton("DC")
        btn_gh = QPushButton("GH")
        btn_tg.setObjectName("social_btn")
        btn_dc.setObjectName("social_btn")
        btn_gh.setObjectName("social_btn")
        social_layout.addWidget(btn_tg)
        social_layout.addWidget(btn_dc)
        social_layout.addWidget(btn_gh)
        footer_layout.addLayout(social_layout)
        
        footer_layout.addStretch()
        
        self.lbl_launch = QLabel()
        self.lbl_launch.setObjectName("footer_text")
        
        self.btn_autostart = QPushButton()
        self.btn_autostart.setCheckable(True)
        self.btn_autostart.setObjectName("toggle_btn")
        self.btn_autostart.clicked.connect(self.toggle_autostart)
        
        self.autostart_path = os.path.expanduser("~/.config/autostart/zelix-hello.desktop")
        self.system_autostart_path = "/etc/xdg/autostart/zelix-hello.desktop"
        
        if os.path.exists(self.autostart_path) or os.path.exists(self.system_autostart_path):
            self.btn_autostart.setChecked(True)
            self.btn_autostart.setText("ON")
        else:
            self.btn_autostart.setChecked(False)
            self.btn_autostart.setText("OFF")
        
        footer_layout.addWidget(self.lbl_launch)
        footer_layout.addWidget(self.btn_autostart)
        
        self.layout.addLayout(footer_layout)

        # Connect actions
        self.btn_software.clicked.connect(lambda: self.parent_window.navigate_to(1))
        self.btn_system.clicked.connect(lambda: self.parent_window.navigate_to(2))
        
        # Connect URLs
        self.btn_readme.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://github.com/lanierc/zelixos/blob/main/README.md")))
        self.btn_wiki.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://zelixos.com/docs/docs.html")))
        self.btn_forum.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://forum.zelixos.org")))
        self.btn_release_info.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://github.com/lanierc/zelixos/releases")))
        self.btn_get_involved.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://github.com/lanierc/zelixos")))
        self.btn_development.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://github.com/lanierc/zelixos")))
        self.btn_donate.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://zelixos.com/")))
        
        btn_tg.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://t.me/zelixos")))
        btn_dc.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://discord.gg/zelixos")))
        btn_gh.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://github.com/lanierc/zelixos")))
        
        self.retranslate_ui()

    def change_language(self, lang):
        Translator.set_language(lang)

    def retranslate_ui(self):
        self.title.setText(Translator.get("welcome_title"))
        self.subtitle.setText(Translator.get("welcome_subtitle"))
        
        self.lbl_doc.setText(Translator.get("doc_header"))
        self.lbl_sup.setText(Translator.get("support_header"))
        self.lbl_proj.setText(Translator.get("project_header"))
        
        self.btn_readme.setText(Translator.get("btn_readme"))
        self.btn_release_info.setText(Translator.get("btn_release_info"))
        self.btn_wiki.setText(Translator.get("btn_wiki"))
        self.btn_forum.setText(Translator.get("btn_forum"))
        self.btn_software.setText(Translator.get("btn_software"))
        self.btn_system.setText(Translator.get("btn_system"))
        self.btn_get_involved.setText(Translator.get("btn_get_involved"))
        self.btn_development.setText(Translator.get("btn_development"))
        self.btn_donate.setText(Translator.get("btn_donate"))
        
        self.lbl_install.setText(Translator.get("install_header"))
        self.btn_install.setText(Translator.get("btn_launch_installer"))
        
        self.lbl_launch.setText(Translator.get("lbl_launch_start"))

    def launch_installer(self):
        # Try to get localized Desktop path
        try:
            desktop_path = subprocess.check_output(["xdg-user-dir", "DESKTOP"]).decode("utf-8").strip()
        except Exception:
            desktop_path = os.path.expanduser("~/Desktop")
            if not os.path.exists(desktop_path):
                desktop_path = os.path.expanduser("~/Masaüstü")
        
        desktop_file = os.path.join(desktop_path, "zelix-installer.desktop")
        
        if os.path.exists(desktop_file):
            # Try xdg-open first as it handles Desktop files well in most DEs
            # then fallback to gtk-launch or manual execution
            try:
                subprocess.Popen(["xdg-open", desktop_file])
            except Exception:
                try:
                    subprocess.Popen(["gtk-launch", "zelix-installer.desktop"])
                except Exception as e:
                    print(f"Could not launch installer: {e}")
        else:
            # Fallback: try to launch directly if we know where it is
            fallback_script = os.path.expanduser("~/ZelixBuild/zelixins/myself.py")
            if os.path.exists(fallback_script):
                subprocess.Popen(["alacritty", "-e", "sudo", "python", fallback_script])
            else:
                print(f"Installer desktop file not found at {desktop_file}")

    def toggle_autostart(self):
        autostart_dir = os.path.expanduser("~/.config/autostart")
        if not os.path.exists(autostart_dir):
            os.makedirs(autostart_dir, exist_ok=True)
            
        if self.btn_autostart.isChecked():
            self.btn_autostart.setText("ON")
            desktop_content = (
                "[Desktop Entry]\n"
                "Type=Application\n"
                "Name=Zelix Hello\n"
                "Comment=Welcome to ZelixOS\n"
                "Exec=/usr/share/applications/zelix-hello.desktop\n"
                "Icon=zelixos\n"
                "Terminal=false\n"
            )
            try:
                orig_file = "/usr/share/applications/zelix-hello.desktop"
                if os.path.exists(orig_file):
                    os.symlink(orig_file, self.autostart_path)
                else:
                    with open(self.autostart_path, "w") as f:
                        f.write(desktop_content)
            except Exception as e:
                print(f"Error enabling autostart: {e}")
        else:
            self.btn_autostart.setText("OFF")
            # Remove user autostart
            if os.path.exists(self.autostart_path):
                try:
                    os.remove(self.autostart_path)
                except Exception as e:
                    print(f"Error disabling user autostart: {e}")
            
            # Remove system autostart
            if os.path.exists(self.system_autostart_path):
                try:
                    # Attempt to remove system-wide autostart. 
                    # We use sudo as it's likely a live system or admin user.
                    subprocess.run(["sudo", "rm", "-f", self.system_autostart_path], check=False)
                except Exception as e:
                    print(f"Error disabling system autostart: {e}")
