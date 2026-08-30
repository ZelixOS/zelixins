import os
import shutil
import subprocess
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QHBoxLayout, 
                             QPushButton, QGridLayout, QComboBox, QSpacerItem, 
                             QSizePolicy, QDialog, QTableWidget, QTableWidgetItem, QHeaderView)
from PyQt6.QtCore import Qt, QUrl, QSize
from PyQt6.QtGui import QDesktopServices, QIcon
from utils.translations import Translator

def get_asset_icon(name):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    local_path = os.path.join(base_dir, "assets", "icons", name)
    if os.path.exists(local_path):
        return QIcon(local_path)
    system_path = os.path.join("/usr/share/zelix-hello/assets/icons", name)
    if os.path.exists(system_path):
        return QIcon(system_path)
    return QIcon()

class ShortcutsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(Translator.get("shortcuts_title"))
        self.setMinimumSize(540, 440)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)

        title = QLabel(Translator.get("shortcuts_title"))
        title.setObjectName("title_label")
        layout.addWidget(title)

        desc = QLabel(Translator.get("shortcuts_desc"))
        desc.setObjectName("dashboard_subtitle")
        layout.addWidget(desc)

        table = QTableWidget()
        table.setColumnCount(2)
        table.setHorizontalHeaderLabels(["Kısayol / Key", "Açıklama / Action"])
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        table.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        shortcuts = [
            ("Super (Win)", Translator.get("sc_app_launcher")),
            ("Alt + Space / Alt + F2", Translator.get("sc_krunner")),
            ("Ctrl + Alt + T", Translator.get("sc_terminal")),
            ("Super + E", Translator.get("sc_file_manager")),
            ("PrintScreen", Translator.get("sc_screenshot")),
            ("Super + ← / → / ↑", Translator.get("sc_window_tiling")),
            ("Ctrl + Alt + Del", Translator.get("sc_lock_logout")),
        ]

        table.setRowCount(len(shortcuts))
        for row, (key, act) in enumerate(shortcuts):
            key_item = QTableWidgetItem(f" {key} ")
            key_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            act_item = QTableWidgetItem(f" {act} ")
            table.setItem(row, 0, key_item)
            table.setItem(row, 1, act_item)

        layout.addWidget(table)

        btn_close = QPushButton(Translator.get("btn_close"))
        btn_close.setObjectName("launch_installer_btn")
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close)


class DashboardTab(QWidget):
    def __init__(self, parent_window):
        super().__init__()
        self.parent_window = parent_window
        self._init_ui()
        Translator.add_listener(self)
        
    def _init_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(40, 40, 40, 20)
        self.main_layout.setSpacing(10)
        
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
        
        self.main_layout.addLayout(header_layout)
        self.main_layout.addSpacing(30)
        
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
        
        self.main_layout.addLayout(grid_layout)
        self.main_layout.addSpacing(30)
        
        # Shortcuts Section (Replaces old installer section)
        shortcuts_layout = QVBoxLayout()
        shortcuts_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.btn_shortcuts = QPushButton()
        self.btn_shortcuts.setObjectName("launch_installer_btn")
        self.btn_shortcuts.clicked.connect(self.show_shortcuts)
        
        shortcuts_layout.addWidget(self.btn_shortcuts)
        self.main_layout.addLayout(shortcuts_layout)
        
        self.main_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        
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
        btn_tg = QPushButton()
        btn_dc = QPushButton()
        btn_gh = QPushButton()
        btn_tg.setObjectName("social_btn")
        btn_dc.setObjectName("social_btn")
        btn_gh.setObjectName("social_btn")
        btn_tg.setIcon(get_asset_icon("telegram.svg"))
        btn_dc.setIcon(get_asset_icon("discord.svg"))
        btn_gh.setIcon(get_asset_icon("github.svg"))
        btn_tg.setIconSize(QSize(20, 20))
        btn_dc.setIconSize(QSize(20, 20))
        btn_gh.setIconSize(QSize(20, 20))
        btn_tg.setToolTip("Telegram")
        btn_dc.setToolTip("Discord")
        btn_gh.setToolTip("GitHub")
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
            self.btn_autostart.setText(Translator.get("toggle_on"))
        else:
            self.btn_autostart.setChecked(False)
            self.btn_autostart.setText(Translator.get("toggle_off"))
        
        footer_layout.addWidget(self.lbl_launch)
        footer_layout.addWidget(self.btn_autostart)
        
        self.main_layout.addLayout(footer_layout)

        # Connect actions
        self.btn_software.clicked.connect(lambda: self.parent_window.navigate_to(1))
        self.btn_system.clicked.connect(lambda: self.parent_window.navigate_to(2))
        
        # Connect URLs
        self.btn_readme.clicked.connect(self.open_readme)
        self.btn_wiki.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://docs.zelixos.com")))
        self.btn_forum.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://forum.zelixos.org")))
        self.btn_release_info.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://github.com/ZelixOS/releases")))
        self.btn_get_involved.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://github.com/ZelixOS")))
        self.btn_development.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://github.com/ZelixOS")))
        self.btn_donate.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://zelixos.com/")))
        
        btn_tg.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://t.me/zelixos")))
        btn_dc.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://discord.gg/zelixos")))
        btn_gh.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://github.com/ZelixOS")))
        
        self.retranslate_ui()

    def show_shortcuts(self):
        dialog = ShortcutsDialog(self)
        dialog.exec()

    def open_readme(self):
        app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        current_lang = Translator.get_language().lower()
        
        if "turkish" in current_lang:
            filenames = ["readme_tr.txt", "readme.txt"]
        else:
            filenames = ["readme_en.txt", "readme.txt"]
            
        readme_path = None
        for fn in filenames:
            local_candidate = os.path.join(app_dir, fn)
            if os.path.exists(local_candidate):
                readme_path = local_candidate
                break
            system_candidate = os.path.join("/usr/share/zelix-hello", fn)
            if os.path.exists(system_candidate):
                readme_path = system_candidate
                break
                
        if readme_path and os.path.exists(readme_path):
            QDesktopServices.openUrl(QUrl.fromLocalFile(readme_path))
        else:
            QDesktopServices.openUrl(QUrl("https://github.com/ZelixOS/blob/main/README.md"))

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
        
        self.btn_shortcuts.setText(Translator.get("btn_shortcuts"))
        
        self.lbl_launch.setText(Translator.get("lbl_launch_start"))
        if self.btn_autostart.isChecked():
            self.btn_autostart.setText(Translator.get("toggle_on"))
        else:
            self.btn_autostart.setText(Translator.get("toggle_off"))

    def toggle_autostart(self):
        autostart_dir = os.path.expanduser("~/.config/autostart")
        if not os.path.exists(autostart_dir):
            os.makedirs(autostart_dir, exist_ok=True)
            
        if self.btn_autostart.isChecked():
            self.btn_autostart.setText(Translator.get("toggle_on"))
            desktop_content = (
                "[Desktop Entry]\n"
                "Type=Application\n"
                "Name=Zelix Hello\n"
                "Comment=Welcome to ZelixOS\n"
                "Exec=zelix-hello\n"
                "Icon=zelixos\n"
                "Terminal=false\n"
            )
            try:
                orig_file = "/usr/share/applications/zelix-hello.desktop"
                if os.path.exists(self.autostart_path) or os.path.islink(self.autostart_path):
                    os.remove(self.autostart_path)
                if os.path.exists(orig_file):
                    os.symlink(orig_file, self.autostart_path)
                else:
                    with open(self.autostart_path, "w", encoding="utf-8") as f:
                        f.write(desktop_content)
            except Exception as e:
                print(f"Error enabling autostart: {e}")
        else:
            self.btn_autostart.setText(Translator.get("toggle_off"))
            # Remove user autostart
            if os.path.exists(self.autostart_path) or os.path.islink(self.autostart_path):
                try:
                    os.remove(self.autostart_path)
                except Exception as e:
                    print(f"Error disabling user autostart: {e}")
            
            # Remove system autostart
            if os.path.exists(self.system_autostart_path):
                try:
                    subprocess.run(["pkexec", "rm", "-f", self.system_autostart_path], check=False)
                except Exception as e:
                    print(f"Error disabling system autostart: {e}")
