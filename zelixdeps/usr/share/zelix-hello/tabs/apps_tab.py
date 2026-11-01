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
        self.category_widgets = []
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
        
        self.categories = [
            {
                "key": "cat_aur",
                "is_aur": True,
                "apps": [
                    ("Yay", "yay"),
                    ("Paru", "paru")
                ],
                "extra_deps": ""
            },
            {
                "key": "cat_gaming",
                "apps": [
                    ("Steam", "steam"),
                    ("Lutris", "lutris"),
                    ("RetroArch", "retroarch"),
                    ("Wine", "wine"),
                    ("Winetricks", "winetricks"),
                    ("MangoHud", "mangohud"),
                    ("GameMode", "gamemode"),
                    ("ProtonTricks", "protontricks")
                ],
                "extra_deps": "gamescope vulkan-radeon vulkan-intel vulkan-icd-loader"
            },
            {
                "key": "cat_office",
                "apps": [
                    ("LibreOffice", "libreoffice-fresh"),
                    ("Thunderbird", "thunderbird"),
                    ("Okular", "okular"),
                    ("Xournal++", "xournalpp"),
                    ("KeePassXC", "keepassxc")
                ],
                "extra_deps": ""
            },
            {
                "key": "cat_editing",
                "apps": [
                    ("Kdenlive", "kdenlive"),
                    ("OBS Studio", "obs-studio"),
                    ("GIMP", "gimp"),
                    ("Inkscape", "inkscape"),
                    ("Blender", "blender"),
                    ("VLC", "vlc"),
                    ("Audacity", "audacity"),
                    ("MPV", "mpv")
                ],
                "extra_deps": ""
            },
            {
                "key": "cat_browsers",
                "apps": [
                    ("Firefox", "firefox"),
                    ("Chromium", "chromium"),
                    ("Telegram", "telegram-desktop"),
                    ("Discord", "discord"),
                    ("Spotify", "spotify-launcher"),
                    ("Falkon", "falkon")
                ],
                "extra_deps": ""
            },
            {
                "key": "cat_devtools",
                "apps": [
                    ("VS Code", "code"),
                    ("Neovim", "neovim"),
                    ("Git", "git"),
                    ("Docker", "docker"),
                    ("FileZilla", "filezilla"),
                    ("VirtualBox", "virtualbox")
                ],
                "extra_deps": ""
            }
        ]
        
        self.category_widgets = []
        
        for cat_info in self.categories:
            cat_key = cat_info["key"]
            group = QGroupBox()
            grid = QGridLayout(group)
            grid.setSpacing(15)
            grid.setContentsMargins(20, 30, 20, 20)
            
            # Install All button
            btn_install_all = QPushButton()
            btn_install_all.setObjectName("primary_btn")
            
            apps_list = cat_info["apps"]
            extra_deps = cat_info["extra_deps"]
            
            if cat_info.get("is_aur"):
                btn_install_all.clicked.connect(self.install_all_aur)
            else:
                all_pkgs = " ".join([pkg for _, pkg in apps_list])
                if extra_deps:
                    all_pkgs += " " + extra_deps
                btn_install_all.clicked.connect(lambda checked, pkgs=all_pkgs: self.install_app(pkgs))
            
            cat_widget_entry = {
                "key": cat_key,
                "group": group,
                "btn_install_all": btn_install_all,
                "app_btns": []
            }
            
            grid.addWidget(btn_install_all, 0, 0, 1, 3)
            
            row, col = 1, 0
            for app_name, pkg_name in apps_list:
                btn = QPushButton()
                if cat_info.get("is_aur"):
                    btn.clicked.connect(lambda checked, pkg=pkg_name: self.install_aur_helper(pkg))
                else:
                    btn.clicked.connect(lambda checked, pkg=pkg_name: self.install_app(pkg))
                grid.addWidget(btn, row, col)
                
                cat_widget_entry["app_btns"].append((btn, app_name))
                
                col += 1
                if col > 2:
                    col = 0
                    row += 1
                    
            self.category_widgets.append(cat_widget_entry)
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
            cat_data["group"].setTitle(Translator.get(cat_data["key"]))
            cat_data["btn_install_all"].setText(install_all_text)
            for btn, app_name in cat_data["app_btns"]:
                btn.setText(f"{app_name} {install_text}")

    def get_terminal_cmd(self):
        terminals = [
            ("alacritty", ["alacritty", "-e"]),
            ("konsole", ["konsole", "--hold", "-e"]),
            ("gnome-terminal", ["gnome-terminal", "--"]),
            ("xfce4-terminal", ["xfce4-terminal", "-e"]),
            ("kitty", ["kitty", "--hold", "--"]),
            ("foot", ["foot", "-e"]),
            ("xterm", ["xterm", "-hold", "-e"])
        ]
        
        for term_name, term_cmd in terminals:
            if shutil.which(term_name):
                return term_cmd
        return None

    def install_app(self, packages):
        term_cmd = self.get_terminal_cmd()
        if not term_cmd:
            QMessageBox.warning(self, Translator.get("msg_error"), Translator.get("msg_unsupported_term"))
            return
            
        pkgs_str = " ".join(packages.split())
        shell_script = f"sudo pacman -S --needed {pkgs_str}; echo ''; read -r -p 'İşlem tamamlandı. Kapatmak için Enter tuşuna basın...' dummy"
        command = term_cmd + ["bash", "-c", shell_script]
        try:
            subprocess.Popen(command)
        except Exception as e:
            QMessageBox.warning(self, Translator.get("msg_error"), f"{Translator.get('msg_term_fail')} {e}")

    def install_aur_helper(self, helper):
        term_cmd = self.get_terminal_cmd()
        if not term_cmd:
            QMessageBox.warning(self, Translator.get("msg_error"), Translator.get("msg_unsupported_term"))
            return

        shell_script = (
            f"echo '=== ZelixOS: {helper} AUR Yardımcısı Kurulumu ==='; "
            f"if pacman -Si '{helper}' &>/dev/null; then "
            f"    echo 'Paket depoda bulundu, pacman ile kuruluyor...'; "
            f"    sudo pacman -S --needed '{helper}'; "
            f"else "
            f"    echo 'Paket depolarda bulunamadı, AUR üzerinden derlenip kuruluyor...'; "
            f"    sudo pacman -S --needed --noconfirm base-devel git; "
            f"    TMPDIR=$(mktemp -d); "
            f"    git clone 'https://aur.archlinux.org/{helper}-bin.git' \"$TMPDIR/{helper}\" || "
            f"    git clone 'https://aur.archlinux.org/{helper}.git' \"$TMPDIR/{helper}\"; "
            f"    (cd \"$TMPDIR/{helper}\" && makepkg -si --noconfirm); "
            f"    rm -rf \"$TMPDIR\"; "
            f"fi; "
            f"echo ''; read -r -p 'Kurulum tamamlandı. Kapatmak için Enter tuşuna basın...' dummy"
        )
        command = term_cmd + ["bash", "-c", shell_script]
        try:
            subprocess.Popen(command)
        except Exception as e:
            QMessageBox.warning(self, Translator.get("msg_error"), f"{Translator.get('msg_term_fail')} {e}")

    def install_all_aur(self):
        term_cmd = self.get_terminal_cmd()
        if not term_cmd:
            QMessageBox.warning(self, Translator.get("msg_error"), Translator.get("msg_unsupported_term"))
            return

        shell_script = (
            "echo '=== ZelixOS: yay ve paru AUR Yardımcıları Kurulumu ==='; "
            "for h in yay paru; do "
            "    echo ''; echo \"--- $h Kuruluyor ---\"; "
            "    if pacman -Si \"$h\" &>/dev/null; then "
            "        sudo pacman -S --needed --noconfirm \"$h\"; "
            "    else "
            "        sudo pacman -S --needed --noconfirm base-devel git; "
            "        TMPDIR=$(mktemp -d); "
            "        git clone \"https://aur.archlinux.org/${h}-bin.git\" \"$TMPDIR/$h\" || "
            "        git clone \"https://aur.archlinux.org/${h}.git\" \"$TMPDIR/$h\"; "
            "        (cd \"$TMPDIR/$h\" && makepkg -si --noconfirm); "
            "        rm -rf \"$TMPDIR\"; "
            "    fi; "
            "done; "
            "echo ''; read -r -p 'Tüm kurulumlar tamamlandı. Kapatmak için Enter tuşuna basın...' dummy"
        )
        command = term_cmd + ["bash", "-c", shell_script]
        try:
            subprocess.Popen(command)
        except Exception as e:
            QMessageBox.warning(self, Translator.get("msg_error"), f"{Translator.get('msg_term_fail')} {e}")

