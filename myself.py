#!/usr/bin/env python3
import sys
import os
import json
import uuid
import subprocess
import re
import socket
import urllib.request
import tempfile
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QStackedWidget, QFrame, QComboBox, QHBoxLayout,
    QFormLayout, QListWidget, QListWidgetItem, QCheckBox, QMessageBox,
    QSpacerItem, QSizePolicy, QPlainTextEdit
)
from PyQt6.QtCore import Qt, QProcess, QTimer
from PyQt6.QtGui import QPixmap, QIcon

# ─────────────────────────────────────────────
#  Dil / Language support
# ─────────────────────────────────────────────
LANGUAGES = {
    "tr": {
        # Welcome
        "welcome_subtitle": "Geleceğin başlangıcına hoş geldiniz.",
        "start_install": "KURULUMA BAŞLA",
        "lang_label": "Dil / Language",

        # Sidebar steps
        "step_1": "1. Hoş Geldiniz",
        "step_2": "2. Sistem Ayarları",
        "step_3": "3. Ayna Seçimi",
        "step_4": "4. Disk Seçimi",
        "step_5": "5. Kullanıcılar",
        "step_6": "6. Ekstra Paketler",
        "step_7": "7. Özet",
        "step_8": "8. Kurulum",

        # Navigation
        "back": "GERİ",
        "next": "İLERİ",

        # SystemConfigPage
        "sys_title": "Sistem ve Bölge Ayarları",
        "desktop_env": "Masaüstü Ortamı:",
        "keyboard": "Klavye Düzeni:",
        "timezone": "Zaman Dilimi:",
        "kernel": "Çekirdek (Kernel):",
        "bootloader": "Önyükleyici:",
        "greeter": "Giriş Yöneticisi:",

        # DiskConfigPage
        "disk_title": "Disk Yapılandırması",
        "disk_warn":  "DİKKAT: Seçilen diskteki tüm veriler silinecek ve yeniden biçimlendirilecektir!",
        "disk_select": "Kurulum Diski Seçin:",
        "disk_refresh": "Diskleri Yenile",
        "disk_unknown_model": "Bilinmeyen Model",
        "disk_fallback": "/dev/sda (Bilinmiyor)",

        # UserAccountPage
        "user_title": "Kullanıcılar ve Güvenlik",
        "root_pass_placeholder": "Root Şifresi Belirleyin",
        "root_pass_label": "Root Şifresi:",
        "root_confirm_placeholder": "Root Şifresini Onaylayın",
        "root_confirm_label": "Şifre Onay:",
        "username_placeholder": "Kullanıcı Adı",
        "username_label": "Ad:",
        "password_placeholder": "Şifre",
        "password_label": "Şifre:",
        "user_confirm_placeholder": "Şifreyi Onaylayın",
        "user_confirm_label": "Şifre Onay:",
        "admin_check": "Yönetici Yetkisi (sudo)",
        "add_user_btn": "KULLANICI EKLE",
        "added_users_label": "Eklenen Kullanıcılar:",
        "remove_user_btn": "SEÇİLİ KULLANICIYI SİL",
        "error_title": "Hata",
        "error_empty_fields": "Kullanıcı adı ve şifre boş bırakılamaz.",
        "error_duplicate_user": "Bu kullanıcı zaten eklendi.",
        "error_passwords_mismatch": "Şifreler uyuşmuyor.",
        "error_invalid_username": "Geçersiz kullanıcı adı. Sadece küçük harf, sayı, alt çizgi ve tire içerebilir. Bir harf veya alt çizgi ile başlamalı ve en fazla 32 karakter olmalıdır.",
        "user_validation_title": "Kullanıcı Gerekli",
        "user_validation_msg": (
            "Masaüstü ortamına (KDE/GNOME vb.) sadece Root hesabı ile giriş yapılamaz.\n\n"
            "Lütfen giriş yapabilmek için en az 1 kullanıcı ekleyin!"
        ),
        "role_admin": "Yönetici",
        "role_standard": "Standart",

        # MirrorConfigPage
        "mirror_title": "Ayna (Mirror) Seçimi",
        "mirror_desc": "Yükleme hızını artırmak için size en yakın bölgeleri seçin (Örn: Turkey, Germany).",

        # ExtraPackagesPage
        "extra_title": "Ekstra Paket Seçimi",
        "extra_desc": "Kurulumdan sonra yüklenmesini istediğiniz ek programları seçin. Boş bırakabilirsiniz.",
        "extra_cat_gaming": "🎮 Oyun",
        "extra_cat_dev": "🛠️ Geliştirme",
        "extra_cat_multimedia": "🎬 Multimedya",
        "extra_cat_office": "📄 Ofis",
        "extra_cat_internet": "🌐 İnternet",
        "extra_cat_system": "🔧 Sistem Araçları",
        "extra_multilib": "Multilib deposunu etkinleştir (32-bit uygulama desteği, Steam vb. için gerekli)",
        "extra_selected_count": "{count} paket seçildi",
        "summary_extra_pkgs": "<b>Ekstra Paketler:</b>",
        "summary_multilib": "<b>Multilib:</b>",
        "summary_multilib_on": "Etkin",
        "summary_multilib_off": "Kapalı",

        # SummaryPage
        "summary_title": "Kurulum Özeti",
        "summary_disk": "<b>Hedef Disk:</b>",
        "summary_desktop": "<b>Masaüstü:</b>",
        "summary_kb_tz": "<b>Klavye / Bölge:</b>",
        "summary_mirrors": "<b>Aynalar:</b>",
        "summary_kernel": "<b>Çekirdek:</b>",
        "summary_bootloader": "<b>Önyükleyici:</b>",
        "summary_greeter": "<b>Giriş Yöneticisi:</b>",
        "summary_root_pw": "<b>Root Şifresi:</b>",
        "summary_root_set": "Atandı",
        "summary_root_none": "Yok",
        "summary_users": "<b>Kullanıcılar:</b>",
        "summary_no_users": "  Yok (Sadece Root)",
        "start_install_btn": "KURULUMU BAŞLAT",
        "confirm_title": "Onay",
        "confirm_msg": "Disk biçimlendirilecek ve kurulum başlayacak. Emin misiniz?",

        # InstallProgressPage
        "install_title_running": "Kurulum Sürüyor...",
        "install_log_header": "--- ZelixOS Ana Kurulumu Başlıyor ---\nLütfen bilgisayarı kapatmayın...\n",
        "install_title_done": "Kurulum Tamamlandı!",
        "install_title_fail": "Kurulum Başarısız Oldu!",
        "install_done_msg": "\n--- ZELİX OS SİSTEMİNİZE BAŞARIYLA KURULDU ---",
        "install_fail_msg": "\n--- HATA: İŞLEM KOD {code} İLE SONLANDI ---",
        "reboot_btn": "SİSTEMİ YENİDEN BAŞLAT",
        "post_warn_no_deps": "\n[Uyarı] 'zelixdeps' klasörü bulunamadı. Ekstra ZelixOS dosyaları atlanıyor...",
        "post_copy_header": "\n--- ZelixOS Ek Paketleri ve Yapılandırması Kopyalanıyor ---",
        "post_target_disk": "Hedef Disk: {part}",
        "post_copy_done": "-> zelixdeps klasöründeki tüm dosyalar sisteme yerleştirildi!",
        "post_copy_error": "-> Dosya kopyalama sırasında hata oluştu: {err}",
        "post_root_partition": "Kök Bölüm: {part}",
        "post_boot_partition": "Önyükleme Bölümü: {part}",
        "post_source": "Kaynak: {src}",
        "post_error_no_disk": "-> [HATA] Disk seçilmedi!",
        "post_warn_lsblk_fail": "-> [UYARI] lsblk ile bölüm tespiti başarısız, isim tabanlı tahmine geçiliyor...",
        "post_error_script_fail": "-> [HATA] Post-install script başarısız oldu (Kod {code})",

        # Worldwide fallback
        "worldwide": "Worldwide",
        "no_internet_msg": "Kurulum için aktif bir internet bağlantısı gereklidir. Lütfen ağ ayarlarınızı kontrol edin.",
        "uefi_warning": "UYARI: Sistem UEFI modunda başlatılmadı. Bazı özellikler sınırlı olabilir. Lütfen Bootloader olarak GRUB seçin.",
    },
    "en": {
        # Welcome
        "welcome_subtitle": "Welcome to the vision of the future.",
        "start_install": "START INSTALLATION",
        "lang_label": "Language / Dil",
        "no_internet_msg": "An active internet connection is required for installation. Please check your network settings.",
        "uefi_warning": "WARNING: System not booted in UEFI mode. Some features may be limited. Please select GRUB as Bootloader.",

        # Sidebar steps
        "step_1": "1. Welcome",
        "step_2": "2. System Settings",
        "step_3": "3. Mirror Selection",
        "step_4": "4. Disk Selection",
        "step_5": "5. Users",
        "step_6": "6. Extra Packages",
        "step_7": "7. Summary",
        "step_8": "8. Installation",

        # Navigation
        "back": "BACK",
        "next": "NEXT",

        # SystemConfigPage
        "sys_title": "System & Region Settings",
        "desktop_env": "Desktop Environment:",
        "keyboard": "Keyboard Layout:",
        "timezone": "Timezone:",
        "kernel": "Kernel:",
        "bootloader": "Bootloader:",
        "greeter": "Greeter:",

        # DiskConfigPage
        "disk_title": "Disk Configuration",
        "disk_warn":  "WARNING: All data on the selected disk will be erased and reformatted!",
        "disk_select": "Select Installation Disk:",
        "disk_refresh": "Refresh Disks",
        "disk_unknown_model": "Unknown Model",
        "disk_fallback": "/dev/sda (Unknown)",

        # UserAccountPage
        "user_title": "Users & Security",
        "root_pass_placeholder": "Set Root Password",
        "root_pass_label": "Root Password:",
        "root_confirm_placeholder": "Confirm Root Password",
        "root_confirm_label": "Confirm Password:",
        "username_placeholder": "Username",
        "username_label": "Name:",
        "password_placeholder": "Password",
        "password_label": "Password:",
        "user_confirm_placeholder": "Confirm Password",
        "user_confirm_label": "Confirm Password:",
        "admin_check": "Administrator (sudo)",
        "add_user_btn": "ADD USER",
        "added_users_label": "Added Users:",
        "remove_user_btn": "REMOVE SELECTED USER",
        "error_title": "Error",
        "error_empty_fields": "Username and password cannot be empty.",
        "error_duplicate_user": "This user has already been added.",
        "error_passwords_mismatch": "Passwords do not match.",
        "error_invalid_username": "Invalid username. Use only lowercase letters, numbers, underscores, and hyphens. Must start with a letter or underscore and be max 32 characters.",
        "user_validation_title": "User Required",
        "user_validation_msg": (
            "You cannot log into a desktop environment (KDE/GNOME etc.) as root only.\n\n"
            "Please add at least 1 user to be able to log in!"
        ),
        "role_admin": "Admin",
        "role_standard": "Standard",

        # MirrorConfigPage
        "mirror_title": "Mirror Selection",
        "mirror_desc": "Select the nearest regions to increase download speed (e.g. Turkey, Germany).",

        # ExtraPackagesPage
        "extra_title": "Extra Package Selection",
        "extra_desc": "Select additional programs to install. You can leave this empty.",
        "extra_cat_gaming": "🎮 Gaming",
        "extra_cat_dev": "🛠️ Development",
        "extra_cat_multimedia": "🎬 Multimedia",
        "extra_cat_office": "📄 Office",
        "extra_cat_internet": "🌐 Internet",
        "extra_cat_system": "🔧 System Tools",
        "extra_multilib": "Enable multilib repository (32-bit app support, required for Steam etc.)",
        "extra_selected_count": "{count} packages selected",
        "summary_extra_pkgs": "<b>Extra Packages:</b>",
        "summary_multilib": "<b>Multilib:</b>",
        "summary_multilib_on": "Enabled",
        "summary_multilib_off": "Disabled",

        # SummaryPage
        "summary_title": "Installation Summary",
        "summary_disk": "<b>Target Disk:</b>",
        "summary_desktop": "<b>Desktop:</b>",
        "summary_kb_tz": "<b>Keyboard / Region:</b>",
        "summary_mirrors": "<b>Mirrors:</b>",
        "summary_kernel": "<b>Kernel:</b>",
        "summary_bootloader": "<b>Bootloader:</b>",
        "summary_greeter": "<b>Greeter:</b>",
        "summary_root_pw": "<b>Root Password:</b>",
        "summary_root_set": "Set",
        "summary_root_none": "None",
        "summary_users": "<b>Users:</b>",
        "summary_no_users": "  None (Root only)",
        "start_install_btn": "START INSTALLATION",
        "confirm_title": "Confirm",
        "confirm_msg": "The disk will be formatted and installation will begin. Are you sure?",

        # InstallProgressPage
        "install_title_running": "Installation in Progress...",
        "install_log_header": "--- ZelixOS Core Installation Starting ---\nPlease do not shut down...\n",
        "install_title_done": "Installation Complete!",
        "install_title_fail": "Installation Failed!",
        "install_done_msg": "\n--- ZELIX OS WAS SUCCESSFULLY INSTALLED ON YOUR SYSTEM ---",
        "install_fail_msg": "\n--- ERROR: PROCESS EXITED WITH CODE {code} ---",
        "reboot_btn": "REBOOT SYSTEM",
        "post_warn_no_deps": "\n[Warning] 'zelixdeps' folder not found. Skipping extra ZelixOS files...",
        "post_copy_header": "\n--- Copying ZelixOS Extra Packages and Configuration ---",
        "post_target_disk": "Target Disk: {part}",
        "post_copy_done": "-> All files from zelixdeps were installed to the system!",
        "post_copy_error": "-> Error during file copy: {err}",
        "post_root_partition": "Root Partition: {part}",
        "post_boot_partition": "Boot Partition: {part}",
        "post_source": "Source: {src}",
        "post_error_no_disk": "-> [ERROR] No disk selected!",
        "post_warn_lsblk_fail": "-> [WARNING] Partition detection with lsblk failed, falling back to name-based guessing...",
        "post_error_script_fail": "-> [ERROR] Post-install script failed (Code {code})",

        # Worldwide fallback
        "worldwide": "Worldwide",
    },
}

# Global language state — pages can access via get_text()
_current_lang = "tr"


def get_text(key: str) -> str:
    """Returns the UI string for the current language."""
    return LANGUAGES.get(_current_lang, LANGUAGES["tr"]).get(key, key)


def set_language(lang_code: str):
    global _current_lang
    _current_lang = lang_code


# ─────────────────────────────────────────────
#  System helpers
# ─────────────────────────────────────────────

def run_sys_command(command, fallback):
    """Runs a system command and returns its output lines as a list."""
    try:
        # Use shell=True if the command is a string with spaces, or split it
        if isinstance(command, str):
            cmd_args = command.split()
        else:
            cmd_args = command
            
        result = subprocess.run(cmd_args, capture_output=True, text=True, check=True)
        lines = result.stdout.strip().split('\n')
        return lines if lines else fallback
    except Exception:
        return fallback


def is_uefi():
    """Checks if the system is booted in UEFI mode."""
    return os.path.isdir("/sys/firmware/efi")


def check_internet():
    """Checks for internet connection using HTTP first, then ICMP as fallback.
    
    Some corporate/institutional networks block ICMP (ping), so we try
    an HTTP HEAD request first, which is more universally reliable.
    """
    # Method 1: HTTP HEAD request (works even if ICMP is blocked)
    try:
        req = urllib.request.Request("http://archlinux.org", method="HEAD")
        urllib.request.urlopen(req, timeout=3)
        return True
    except Exception:
        pass

    # Method 2: TCP socket connection to Cloudflare DNS
    try:
        sock = socket.create_connection(("1.1.1.1", 53), timeout=3)
        sock.close()
        return True
    except Exception:
        pass

    # Method 3: ICMP ping as last resort
    try:
        subprocess.run(["ping", "-c", "1", "-W", "2", "8.8.8.8"],
                       capture_output=True, check=True)
        return True
    except Exception:
        return False




def get_current_keymap():
    """Detects current keyboard layout."""
    try:
        res = subprocess.run(["localectl", "status"], capture_output=True, text=True)
        for line in res.stdout.split('\n'):
            if "X11 Layout" in line:
                return line.split(":")[1].strip()
    except:
        pass
    return None


def get_current_timezone():
    """Detects current system timezone."""
    try:
        res = subprocess.run(["timedatectl", "show", "--property=Timezone", "--value"], capture_output=True, text=True)
        tz = res.stdout.strip()
        return tz if tz else None
    except:
        pass
    return None


def scan_disks():
    """Scans available disks via lsblk."""
    unknown_model = get_text("disk_unknown_model")
    fallback = [get_text("disk_fallback")]
    try:
        result = subprocess.run(
            ['lsblk', '-d', '-n', '-o', 'NAME,SIZE,MODEL'],
            capture_output=True, text=True, check=True
        )
        disks = []
        for line in result.stdout.strip().split('\n'):
            if line:
                parts = line.split()
                if len(parts) >= 2:
                    name = parts[0]
                    # Skip loop and ram devices
                    if name.startswith("loop") or name.startswith("ram"):
                        continue
                    dev_path = f"/dev/{name}"
                    size = parts[1]
                    model = " ".join(parts[2:]) if len(parts) > 2 else unknown_model
                    disks.append(f"{dev_path} ({size}) - {model}")
        return disks if disks else fallback
    except Exception:
        return ["/dev/sda (50G) - Virtual Disk", "/dev/nvme0n1 (500G) - NVMe Disk"]


def get_disk_size_bytes(disk_path):
    """Returns the total size of a disk in bytes."""
    try:
        res = subprocess.run(
            ['lsblk', '-b', '-d', '-n', '-o', 'SIZE', disk_path],
            capture_output=True, text=True, check=True
        )
        return int(res.stdout.strip())
    except Exception:
        return 50 * 1024 ** 3  # Fallback: 50 GiB


# ─────────────────────────────────────────────
#  Base page
# ─────────────────────────────────────────────

class InstallerPage(QWidget):
    """Base page class with shared layout."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        # Use 'main_layout' to avoid shadowing QWidget.layout()
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(40, 40, 40, 40)

    def retranslate(self):
        """Override in subclasses to refresh all translatable text."""
        pass


# ─────────────────────────────────────────────
#  Welcome Page
# ─────────────────────────────────────────────

class WelcomePage(InstallerPage):
    def __init__(self, parent):
        super().__init__(parent)

        spacer_top = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self.main_layout.addItem(spacer_top)

        title = QLabel("ZelixOS")
        title.setStyleSheet("font-size: 80px; font-weight: bold; color: #9b59b6; letter-spacing: 2px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.subtitle = QLabel()
        self.subtitle.setStyleSheet("font-size: 18px; color: #bdc3c7; margin-bottom: 20px;")
        self.subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Logo
        self.logo_label = QLabel()
        dirr = os.path.dirname(os.path.abspath(__file__))
        local_logo = os.path.join(dirr, "icons", "zelixos_logo.png")
        logo_path = local_logo if os.path.exists(local_logo) else "/usr/share/zelixins/icons/zelixos_logo.png"
        self.logo_pixmap = QPixmap(logo_path)
        if not self.logo_pixmap.isNull():
            scaled_logo = self.logo_pixmap.scaled(350, 350, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.logo_label.setPixmap(scaled_logo)
        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.logo_label.setStyleSheet("margin-bottom: 10px; border: none; background: transparent;")

        # Language switcher
        lang_row = QHBoxLayout()
        lang_row.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lang_label = QLabel()
        self.lang_label.setStyleSheet("color: #bdc3c7; font-size: 14px; margin-right: 8px;")
        self.lang_combo = QComboBox()
        self.lang_combo.addItem("Türkçe", "tr")
        self.lang_combo.addItem("English", "en")
        self.lang_combo.setFixedWidth(120)
        self.lang_combo.currentIndexChanged.connect(self._on_lang_changed)
        lang_row.addWidget(self.lang_label)
        lang_row.addWidget(self.lang_combo)

        btn_layout = QHBoxLayout()
        btn_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.start_btn = QPushButton()
        self.start_btn.setFixedSize(300, 55)
        self.start_btn.clicked.connect(lambda: self.main_window.next_page())
        btn_layout.addWidget(self.start_btn)

        self.main_layout.addWidget(self.logo_label)
        self.main_layout.addWidget(title)
        self.main_layout.addWidget(self.subtitle)
        self.main_layout.addSpacing(10)
        self.main_layout.addLayout(lang_row)
        self.main_layout.addSpacing(20)
        
        # Internet Warning
        self.net_warn = QLabel()
        self.net_warn.setStyleSheet("color: #e74c3c; font-weight: bold; margin-bottom: 10px;")
        self.net_warn.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.net_warn.setWordWrap(True)
        self.net_warn.hide()
        self.main_layout.addWidget(self.net_warn)

        self.main_layout.addLayout(btn_layout)

        spacer_bottom = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self.main_layout.addItem(spacer_bottom)
        
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.update_internet_status)
        self.refresh_timer.start(5000) # Check every 5s

        self.retranslate()
        self.update_internet_status()

    def update_internet_status(self):
        has_net = check_internet()
        if has_net:
            self.start_btn.setEnabled(True)
            self.net_warn.hide()
        else:
            self.start_btn.setEnabled(False)
            self.net_warn.setText(get_text("no_internet_msg"))
            self.net_warn.show()

    def _on_lang_changed(self, index):
        code = self.lang_combo.itemData(index)
        set_language(code)
        self.main_window.retranslate_all()

    def retranslate(self):
        self.subtitle.setText(get_text("welcome_subtitle"))
        self.start_btn.setText(get_text("start_install"))
        self.lang_label.setText(get_text("lang_label") + ":")
        self.update_internet_status()


# ─────────────────────────────────────────────
#  System Config Page
# ─────────────────────────────────────────────

class SystemConfigPage(InstallerPage):
    # Internal kernel IDs that archinstall understands
    KERNELS = [
        ("Linux (Stable)",          "linux"),
        ("Linux LTS (Long-Term)",    "linux-lts"),
        ("Linux Zen (Desktop)",      "linux-zen"),
        ("Linux Hardened (Security)","linux-hardened"),
    ]

    # Internal bootloader IDs
    BOOTLOADERS = [
        ("Systemd-boot (UEFI)",  "Systemd-boot"),
        ("GRUB (BIOS/UEFI)",     "Grub"),
        ("rEFInd (UEFI)",        "Refind"),
    ]

    def __init__(self, parent):
        super().__init__(parent)

        self.title_label = QLabel()
        self.title_label.setStyleSheet("font-size: 28px; color: #eff0f1; font-weight: bold; margin-bottom: 20px;")
        self.main_layout.addWidget(self.title_label)

        self.form_layout = QFormLayout()
        self.form_layout.setSpacing(20)

        # Desktop Environment
        self.de_label = QLabel()
        self.de_combo = QComboBox()
        self.de_combo.addItems(["KDE Plasma", "GNOME", "Xfce4", "Hyprland", "Sway", "i3-wm", "bspwm" ] )
        self.form_layout.addRow(self.de_label, self.de_combo)

        # Keyboard Layout
        self.kb_label = QLabel()
        self.kb_combo = QComboBox()
        self.kb_combo.setEditable(True)
        self.kb_combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.load_keymaps()
        self.form_layout.addRow(self.kb_label, self.kb_combo)

        # Timezone
        self.tz_label = QLabel()
        self.tz_combo = QComboBox()
        self.tz_combo.setEditable(True)
        self.tz_combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.load_timezones()
        self.form_layout.addRow(self.tz_label, self.tz_combo)

        # Kernel — multi-select list so the user can install several kernels
        self.kernel_label = QLabel()
        self.kernel_list = QListWidget()
        self.kernel_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        self.kernel_list.setFixedHeight(88)   # exactly 4 items visible
        for display, _key in self.KERNELS:
            self.kernel_list.addItem(display)
        self.kernel_list.item(0).setSelected(True)  # Linux (Stable) selected by default
        self.form_layout.addRow(self.kernel_label, self.kernel_list)

        # Bootloader
        self.bootloader_label = QLabel()
        self.bootloader_combo = QComboBox()
        for display, _key in self.BOOTLOADERS:
            self.bootloader_combo.addItem(display)
        self.form_layout.addRow(self.bootloader_label, self.bootloader_combo)

        # Greeter Selection
        self.greeter_label = QLabel()
        self.greeter_combo = QComboBox()
        # Default option + common ones
        self.greeter_combo.addItem("Default (DE Dependent)", "default")
        self.greeter_combo.addItems(["sddm", "gdm", "lightdm-gtk-greeter", "ly"])
        self.form_layout.addRow(self.greeter_label, self.greeter_combo)

        self.main_layout.addLayout(self.form_layout)
        
        # UEFI Warning
        self.uefi_warn = QLabel()
        self.uefi_warn.setStyleSheet("color: #e67e22; font-weight: bold; margin-top: 10px;")
        self.uefi_warn.setWordWrap(True)
        if not is_uefi():
            self.uefi_warn.setText(get_text("uefi_warning"))
            self.uefi_warn.show()
        else:
            self.uefi_warn.hide()
        self.main_layout.addWidget(self.uefi_warn)

        self.main_layout.addStretch()

        nav_layout = QHBoxLayout()
        self.back_btn = QPushButton()
        self.back_btn.clicked.connect(lambda: self.main_window.prev_page())
        self.next_btn = QPushButton()
        self.next_btn.clicked.connect(lambda: self.main_window.next_page())

        nav_layout.addWidget(self.back_btn)
        nav_layout.addStretch()
        nav_layout.addWidget(self.next_btn)
        self.main_layout.addLayout(nav_layout)

        self.retranslate()

    def load_keymaps(self):
        keymaps = run_sys_command("localectl list-keymaps", ["us", "trq", "tr-f", "de", "fr", "uk"])
        self.kb_combo.clear()
        self.kb_combo.addItems(keymaps)
        
        current = get_current_keymap()
        if current:
            idx = self.kb_combo.findText(current)
            if idx >= 0:
                self.kb_combo.setCurrentIndex(idx)
            else:
                # If not found exactly, try to find a match (e.g. "tr" in "trq")
                for i in range(self.kb_combo.count()):
                    if current in self.kb_combo.itemText(i):
                        self.kb_combo.setCurrentIndex(i)
                        break
        else:
            idx = self.kb_combo.findText("trq")
            if idx >= 0:
                self.kb_combo.setCurrentIndex(idx)

    def load_timezones(self):
        timezones = run_sys_command("timedatectl list-timezones", [
            "UTC", "Europe/Istanbul", "America/New_York", "Europe/London", 
            "Europe/Paris", "Europe/Berlin", "Asia/Dubai", "Asia/Tokyo", 
            "Asia/Seoul", "America/Los_Angeles", "America/Chicago", 
            "America/Sao_Paulo", "Australia/Sydney"
        ])
        self.tz_combo.clear()
        self.tz_combo.addItems(timezones)
        
        current = get_current_timezone()
        if current:
            idx = self.tz_combo.findText(current)
            if idx >= 0:
                self.tz_combo.setCurrentIndex(idx)
        else:
            idx = self.tz_combo.findText("Europe/Istanbul")
            if idx >= 0:
                self.tz_combo.setCurrentIndex(idx)

    def selected_kernels(self) -> list:
        """Returns a list of archinstall kernel package names for all selected items."""
        selected_displays = {item.text() for item in self.kernel_list.selectedItems()}
        kernels = [key for display, key in self.KERNELS if display in selected_displays]
        return kernels if kernels else ["linux"]

    def selected_bootloader(self) -> str:
        """Returns the archinstall bootloader string for the current selection."""
        idx = self.bootloader_combo.currentIndex()
        return self.BOOTLOADERS[idx][1] if 0 <= idx < len(self.BOOTLOADERS) else "Systemd-boot"

    def retranslate(self):
        self.title_label.setText(get_text("sys_title"))
        self.de_label.setText(get_text("desktop_env"))
        self.kb_label.setText(get_text("keyboard"))
        self.tz_label.setText(get_text("timezone"))
        self.kernel_label.setText(get_text("kernel"))
        # hint text is appended in parentheses
        hint = " (Ctrl+Click)" if _current_lang == "en" else " (Ctrl+Tıkla)"
        self.kernel_label.setText(get_text("kernel").rstrip(":") + hint + ":")
        self.bootloader_label.setText(get_text("bootloader"))
        self.greeter_label.setText(get_text("greeter"))
        self.back_btn.setText(get_text("back"))
        self.next_btn.setText(get_text("next"))
        if not is_uefi():
            self.uefi_warn.setText(get_text("uefi_warning"))


# ─────────────────────────────────────────────
#  Disk Config Page
# ─────────────────────────────────────────────

class DiskConfigPage(InstallerPage):
    def __init__(self, parent):
        super().__init__(parent)

        self.title_label = QLabel()
        self.title_label.setStyleSheet("font-size: 28px; color: #eff0f1; font-weight: bold; margin-bottom: 10px;")
        self.main_layout.addWidget(self.title_label)

        self.warn_label = QLabel()
        self.warn_label.setStyleSheet("color: #e74c3c; font-weight: bold; margin-bottom: 20px;")
        self.warn_label.setWordWrap(True)
        self.main_layout.addWidget(self.warn_label)

        self.disk_combo = QComboBox()
        self.refresh_disks()

        self.disk_form = QFormLayout()
        self.disk_select_label = QLabel()
        self.disk_form.addRow(self.disk_select_label, self.disk_combo)

        self.refresh_btn = QPushButton()
        self.refresh_btn.setStyleSheet("background: #34495e; padding: 8px;")
        self.refresh_btn.clicked.connect(self.refresh_disks)
        self.disk_form.addRow("", self.refresh_btn)

        self.main_layout.addLayout(self.disk_form)
        self.main_layout.addStretch()

        nav_layout = QHBoxLayout()
        self.back_btn = QPushButton()
        self.back_btn.clicked.connect(lambda: self.main_window.prev_page())
        self.next_btn = QPushButton()
        self.next_btn.clicked.connect(lambda: self.main_window.next_page())

        nav_layout.addWidget(self.back_btn)
        nav_layout.addStretch()
        nav_layout.addWidget(self.next_btn)
        self.main_layout.addLayout(nav_layout)

        self.retranslate()

    def refresh_disks(self):
        self.disk_combo.clear()
        self.disk_combo.addItems(scan_disks())

    def retranslate(self):
        self.title_label.setText(get_text("disk_title"))
        self.warn_label.setText(get_text("disk_warn"))
        self.disk_select_label.setText(get_text("disk_select"))
        self.refresh_btn.setText(get_text("disk_refresh"))
        self.back_btn.setText(get_text("back"))
        self.next_btn.setText(get_text("next"))


# ─────────────────────────────────────────────
#  User Account Page
# ─────────────────────────────────────────────

class UserAccountPage(InstallerPage):
    def __init__(self, parent):
        super().__init__(parent)
        self.users = []

        self.title_label = QLabel()
        self.title_label.setStyleSheet("font-size: 28px; color: #eff0f1; font-weight: bold; margin-bottom: 10px;")
        self.main_layout.addWidget(self.title_label)

        # Root password row (with Confirm Password)
        root_layout = QHBoxLayout()
        self.root_pass_label = QLabel()
        self.root_pass = QLineEdit()
        self.root_pass.setEchoMode(QLineEdit.EchoMode.Password)
        
        self.root_confirm_label = QLabel()
        self.root_confirm = QLineEdit()
        self.root_confirm.setEchoMode(QLineEdit.EchoMode.Password)
        
        root_layout.addWidget(self.root_pass_label)
        root_layout.addWidget(self.root_pass)
        root_layout.addWidget(self.root_confirm_label)
        root_layout.addWidget(self.root_confirm)
        self.main_layout.addLayout(root_layout)

        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("background-color: #31363b; margin: 15px 0;")
        self.main_layout.addWidget(line)

        # User add form
        user_add_layout = QFormLayout()
        self.username_label_w = QLabel()
        self.username_input = QLineEdit()

        self.password_label_w = QLabel()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.password_confirm_label_w = QLabel()
        self.password_confirm_input = QLineEdit()
        self.password_confirm_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.admin_check = QCheckBox()
        self.admin_check.setChecked(True)

        self.add_user_btn = QPushButton()
        self.add_user_btn.setStyleSheet("background: #2980b9;")
        self.add_user_btn.clicked.connect(self.add_user)

        user_add_layout.addRow(self.username_label_w, self.username_input)
        user_add_layout.addRow(self.password_label_w, self.password_input)
        user_add_layout.addRow(self.password_confirm_label_w, self.password_confirm_input)
        user_add_layout.addRow("", self.admin_check)
        user_add_layout.addRow("", self.add_user_btn)
        self.main_layout.addLayout(user_add_layout)

        # User list
        self.added_users_label = QLabel()
        self.main_layout.addWidget(self.added_users_label)
        self.user_list_widget = QListWidget()
        self.user_list_widget.setFixedHeight(100)
        self.main_layout.addWidget(self.user_list_widget)

        self.remove_user_btn = QPushButton()
        self.remove_user_btn.setStyleSheet("background: #c0392b; padding: 8px;")
        self.remove_user_btn.clicked.connect(self.remove_user)
        self.main_layout.addWidget(self.remove_user_btn)

        self.main_layout.addStretch()

        nav_layout = QHBoxLayout()
        self.back_btn = QPushButton()
        self.back_btn.clicked.connect(lambda: self.main_window.prev_page())
        self.next_btn = QPushButton()
        self.next_btn.clicked.connect(self.validate_and_next)

        nav_layout.addWidget(self.back_btn)
        nav_layout.addStretch()
        nav_layout.addWidget(self.next_btn)
        self.main_layout.addLayout(nav_layout)

        self.retranslate()

    def add_user(self):
        uname = self.username_input.text().strip().lower()
        upass = self.password_input.text()
        uconfirm = self.password_confirm_input.text()
        is_admin = self.admin_check.isChecked()

        if not uname or not upass:
            QMessageBox.warning(self, get_text("error_title"), get_text("error_empty_fields"))
            return

        # Username validation: a-z, 0-9, _, -; start with letter/underscore; max 32 chars
        if not re.match(r"^[a-z_][a-z0-9_-]*$", uname) or len(uname) > 32:
            QMessageBox.warning(self, get_text("error_title"), get_text("error_invalid_username"))
            return

        if upass != uconfirm:
            QMessageBox.warning(self, get_text("error_title"), get_text("error_passwords_mismatch"))
            return

        if any(u['username'] == uname for u in self.users):
            QMessageBox.warning(self, get_text("error_title"), get_text("error_duplicate_user"))
            return

        self.users.append({"username": uname, "password": upass, "sudo": is_admin})
        role = get_text("role_admin") if is_admin else get_text("role_standard")
        self.user_list_widget.addItem(f"{uname} ({role})")

        self.username_input.clear()
        self.password_input.clear()
        self.password_confirm_input.clear()
        self.username_input.setFocus()

    def remove_user(self):
        row = self.user_list_widget.currentRow()
        if row >= 0:
            self.user_list_widget.takeItem(row)
            self.users.pop(row)

    def validate_and_next(self):
        root_pw = self.root_pass.text()
        root_confirm_pw = self.root_confirm.text()
        if root_pw != root_confirm_pw:
            QMessageBox.warning(self, get_text("error_title"), get_text("error_passwords_mismatch"))
            return

        if not self.users:
            QMessageBox.warning(
                self,
                get_text("user_validation_title"),
                get_text("user_validation_msg"),
            )
            return
        self.main_window.next_page()

    def retranslate(self):
        self.title_label.setText(get_text("user_title"))
        self.root_pass_label.setText(get_text("root_pass_label"))
        self.root_pass.setPlaceholderText(get_text("root_pass_placeholder"))
        self.root_confirm_label.setText(get_text("root_confirm_label"))
        self.root_confirm.setPlaceholderText(get_text("root_confirm_placeholder"))
        self.username_label_w.setText(get_text("username_label"))
        self.username_input.setPlaceholderText(get_text("username_placeholder"))
        self.password_label_w.setText(get_text("password_label"))
        self.password_input.setPlaceholderText(get_text("password_placeholder"))
        self.password_confirm_label_w.setText(get_text("user_confirm_label"))
        self.password_confirm_input.setPlaceholderText(get_text("user_confirm_placeholder"))
        self.admin_check.setText(get_text("admin_check"))
        self.add_user_btn.setText(get_text("add_user_btn"))
        self.added_users_label.setText(get_text("added_users_label"))
        self.remove_user_btn.setText(get_text("remove_user_btn"))
        self.back_btn.setText(get_text("back"))
        self.next_btn.setText(get_text("next"))


# ─────────────────────────────────────────────
#  Mirror Config Page
# ─────────────────────────────────────────────

class MirrorConfigPage(InstallerPage):
    def __init__(self, parent):
        super().__init__(parent)

        self.title_label = QLabel()
        self.title_label.setStyleSheet("font-size: 28px; color: #eff0f1; font-weight: bold; margin-bottom: 10px;")
        self.main_layout.addWidget(self.title_label)

        self.desc_label = QLabel()
        self.desc_label.setStyleSheet("color: #bdc3c7; margin-bottom: 20px;")
        self.desc_label.setWordWrap(True)
        self.main_layout.addWidget(self.desc_label)

        # Multi-selection list with internal keys (English) for archinstall
        self.mirror_list = QListWidget()
        self.mirror_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)

        # (display_name, internal_key) — internal key is what archinstall expects
        self.mirror_regions = [
            ("Türkiye",          "Türkiye"),
            ("Germany",         "Germany"),
            ("France",          "France"),
            ("United Kingdom",  "United Kingdom"),
            ("United States",   "United States"),
            ("Worldwide",       "Worldwide"),
            ("Bulgaria",        "Bulgaria"),
            ("Greece",          "Greece"),
            ("Netherlands",     "Netherlands"),
            ("Spain",           "Spain"),
            ("Azerbaijan",      "Azerbaijan"),
            ("Colombia",        "Colombia"),
            ("Mexico",          "Mexico"),
            ("Saudi Arabia",    "Saudi Arabia"),
            ("Egypt",           "Egypt"),
        ]

        for display, _key in self.mirror_regions:
            item = QListWidgetItem(display)
            self.mirror_list.addItem(item)
            # Default-select Turkey and United States
            if display in ("Türkiye", "United States"):
                item.setSelected(True)

        self.main_layout.addWidget(self.mirror_list)
        self.main_layout.addStretch()

        nav_layout = QHBoxLayout()
        self.back_btn = QPushButton()
        self.back_btn.clicked.connect(lambda: self.main_window.prev_page())
        self.next_btn = QPushButton()
        self.next_btn.clicked.connect(lambda: self.main_window.next_page())

        nav_layout.addWidget(self.back_btn)
        nav_layout.addStretch()
        nav_layout.addWidget(self.next_btn)
        self.main_layout.addLayout(nav_layout)

        self.retranslate()

    def get_selected_regions(self):
        """Returns the internal (English) keys of selected mirror regions."""
        selected_display = {item.text() for item in self.mirror_list.selectedItems()}
        return [key for display, key in self.mirror_regions if display in selected_display]

    def retranslate(self):
        self.title_label.setText(get_text("mirror_title"))
        self.desc_label.setText(get_text("mirror_desc"))
        self.back_btn.setText(get_text("back"))
        self.next_btn.setText(get_text("next"))


# ─────────────────────────────────────────────
#  Extra Packages Page
# ─────────────────────────────────────────────

class ExtraPackagesPage(InstallerPage):
    """Allows users to select optional packages to install, grouped by category."""

    # (category_lang_key, [(display_name, package_name), ...])
    PACKAGE_CATEGORIES = [
        ("extra_cat_gaming", [
            ("Steam", "steam"),
            ("Lutris", "lutris"),
            ("Wine", "wine"),
            ("GameMode", "gamemode"),
            ("MangoHud", "mangohud"),
            ("ProtonUp-Qt", "protonup-qt"),
        ]),
        ("extra_cat_dev", [
            ("Visual Studio Code (OSS)", "code"),
            ("Git", "git"),
            ("Base-Devel", "base-devel"),
            ("Python", "python"),
            ("Node.js", "nodejs"),
            ("Docker", "docker"),
            ("GCC", "gcc"),
        ]),
        ("extra_cat_multimedia", [
            ("VLC", "vlc"),
            ("GIMP", "gimp"),
            ("OBS Studio", "obs-studio"),
            ("Audacity", "audacity"),
            ("Kdenlive", "kdenlive"),
            ("Spotify (Flatpak)", "flatpak:spotify"),
        ]),
        ("extra_cat_office", [
            ("LibreOffice", "libreoffice-fresh"),
            ("Thunderbird", "thunderbird"),
            ("Okular (PDF)", "okular"),
            ("Evince (PDF)", "evince"),
        ]),
        ("extra_cat_internet", [
            ("Discord", "discord"),
            ("Telegram", "telegram-desktop"),
            ("qBittorrent", "qbittorrent"),
            ("Chromium", "chromium"),
        ]),
        ("extra_cat_system", [
            ("Timeshift", "timeshift"),
            ("Htop", "htop"),
            ("Btop", "btop"),
            ("Fastfetch", "fastfetch"),
            ("Flatpak", "flatpak"),
            ("GParted", "gparted"),
            ("Fish Shell", "fish"),
        ]),
    ]

    def __init__(self, parent):
        super().__init__(parent)

        self.title_label = QLabel()
        self.title_label.setStyleSheet("font-size: 28px; color: #eff0f1; font-weight: bold; margin-bottom: 5px;")
        self.main_layout.addWidget(self.title_label)

        self.desc_label = QLabel()
        self.desc_label.setStyleSheet("color: #bdc3c7; margin-bottom: 10px;")
        self.desc_label.setWordWrap(True)
        self.main_layout.addWidget(self.desc_label)

        # Multilib checkbox (always visible, prominent)
        self.multilib_check = QCheckBox()
        self.multilib_check.setChecked(True)  # Enabled by default per user request
        self.multilib_check.setStyleSheet(
            "font-size: 14px; font-weight: bold; color: #e67e22; padding: 8px; "
            "background-color: #1b1e20; border: 1px solid #34495e; border-radius: 6px;"
        )
        self.main_layout.addWidget(self.multilib_check)
        self.main_layout.addSpacing(5)

        # Selected count label
        self.count_label = QLabel()
        self.count_label.setStyleSheet("color: #9b59b6; font-weight: bold; font-size: 13px;")
        self.count_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.main_layout.addWidget(self.count_label)

        # Scrollable area for package categories
        from PyQt6.QtWidgets import QScrollArea, QGridLayout
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea { border: none; background: transparent; }
            QScrollArea > QWidget > QWidget { background: transparent; }
        """)

        scroll_content = QWidget()
        self.grid_layout = QGridLayout(scroll_content)
        self.grid_layout.setSpacing(10)

        self.category_checkboxes = {}  # {package_name: QCheckBox}

        col = 0
        row = 0
        for cat_key, packages in self.PACKAGE_CATEGORIES:
            # Category frame
            cat_frame = QFrame()
            cat_frame.setStyleSheet("""
                QFrame { 
                    background-color: #1b1e20; 
                    border: 1px solid #31363b; 
                    border-radius: 8px; 
                    padding: 8px; 
                }
            """)
            cat_layout = QVBoxLayout(cat_frame)
            cat_layout.setSpacing(4)

            cat_label = QLabel(get_text(cat_key))
            cat_label.setStyleSheet("font-size: 15px; font-weight: bold; color: #9b59b6; border: none;")
            cat_layout.addWidget(cat_label)
            # Store reference for retranslate
            cat_frame.setProperty("cat_key", cat_key)
            cat_frame.setProperty("cat_label", cat_label)

            for display_name, pkg_name in packages:
                cb = QCheckBox(display_name)
                cb.setStyleSheet("color: #bdc3c7; font-size: 13px; border: none; padding: 2px;")
                cb.stateChanged.connect(self._update_count)
                cat_layout.addWidget(cb)
                self.category_checkboxes[pkg_name] = cb

            self.grid_layout.addWidget(cat_frame, row, col)
            col += 1
            if col >= 2:
                col = 0
                row += 1

        scroll_area.setWidget(scroll_content)
        self.main_layout.addWidget(scroll_area)

        # Navigation
        nav_layout = QHBoxLayout()
        self.back_btn = QPushButton()
        self.back_btn.clicked.connect(lambda: self.main_window.prev_page())
        self.next_btn = QPushButton()
        self.next_btn.clicked.connect(lambda: self.main_window.next_page())

        nav_layout.addWidget(self.back_btn)
        nav_layout.addStretch()
        nav_layout.addWidget(self.next_btn)
        self.main_layout.addLayout(nav_layout)

        self.retranslate()
        self._update_count()

    def _update_count(self):
        count = sum(1 for cb in self.category_checkboxes.values() if cb.isChecked())
        self.count_label.setText(get_text("extra_selected_count").format(count=count))

    def get_selected_packages(self) -> list:
        """Returns list of selected package names."""
        selected = []
        for pkg_name, cb in self.category_checkboxes.items():
            if cb.isChecked():
                selected.append(pkg_name)
        return selected

    def is_multilib_enabled(self) -> bool:
        return self.multilib_check.isChecked()

    def retranslate(self):
        self.title_label.setText(get_text("extra_title"))
        self.desc_label.setText(get_text("extra_desc"))
        self.multilib_check.setText(get_text("extra_multilib"))
        self.back_btn.setText(get_text("back"))
        self.next_btn.setText(get_text("next"))
        self._update_count()

        # Update category labels
        for row_idx in range(self.grid_layout.rowCount()):
            for col_idx in range(self.grid_layout.columnCount()):
                item = self.grid_layout.itemAtPosition(row_idx, col_idx)
                if item and item.widget():
                    frame = item.widget()
                    cat_key = frame.property("cat_key")
                    cat_label = frame.property("cat_label")
                    if cat_key and cat_label:
                        cat_label.setText(get_text(cat_key))


# ─────────────────────────────────────────────
#  Summary Page
# ─────────────────────────────────────────────

class SummaryPage(InstallerPage):
    def __init__(self, parent):
        super().__init__(parent)

        self.title_label = QLabel()
        self.title_label.setStyleSheet("font-size: 28px; color: #eff0f1; font-weight: bold; margin-bottom: 20px;")
        self.main_layout.addWidget(self.title_label)

        from PyQt6.QtWidgets import QTextBrowser
        self.summary_box = QTextBrowser()
        self.summary_box.setOpenExternalLinks(False)
        self.summary_box.setStyleSheet("""
            QTextBrowser {
                background-color: #1b1e20;
                border: 1px solid #31363b;
                border-radius: 10px;
                padding: 6px;
                font-size: 14px;
                color: #eff0f1;
            }
        """)
        self.main_layout.addWidget(self.summary_box)

        self.main_layout.addStretch()

        nav_layout = QHBoxLayout()
        self.back_btn = QPushButton()
        self.back_btn.clicked.connect(lambda: self.main_window.prev_page())

        self.finish_btn = QPushButton()
        self.finish_btn.setStyleSheet("background: #e74c3c; color: white; font-weight: bold; font-size: 16px;")
        self.finish_btn.clicked.connect(self.start_install_process)

        nav_layout.addWidget(self.back_btn)
        nav_layout.addStretch()
        nav_layout.addWidget(self.finish_btn)
        self.main_layout.addLayout(nav_layout)

        self.retranslate()

    @staticmethod
    def _row(label: str, value: str, value_color: str = "#eff0f1") -> str:
        """Returns one HTML table row for the summary."""
        return (
            f'<tr>'
            f'<td style="padding:6px 14px 6px 0; color:#9b59b6; white-space:nowrap;"><b>{label}</b></td>'
            f'<td style="padding:6px 0; color:{value_color};">{value}</td>'
            f'</tr>'
        )

    @staticmethod
    def _section(heading: str) -> str:
        return (
            f'<tr><td colspan="2" style="padding-top:14px; padding-bottom:2px;">'
            f'<span style="color:#7f8c8d; font-size:11px; letter-spacing:1px;">'
            f'{heading.upper()}</span></td></tr>'
        )

    def update_summary(self):
        # Page index map: 0=Welcome, 1=System, 2=Mirror, 3=Disk, 4=User, 5=Extra, 6=Summary, 7=Install
        sys_page    = self.main_window.pages[1]   # SystemConfigPage
        mirror_page = self.main_window.pages[2]   # MirrorConfigPage
        disk_page   = self.main_window.pages[3]   # DiskConfigPage
        user_page   = self.main_window.pages[4]   # UserAccountPage
        extra_page  = self.main_window.pages[5]   # ExtraPackagesPage

        disk_sel       = disk_page.disk_combo.currentText()
        mirrors        = ", ".join(mirror_page.get_selected_regions()) or get_text("worldwide")
        kernels_sel    = ", ".join(
            d for d, _k in sys_page.KERNELS
            if d in {i.text() for i in sys_page.kernel_list.selectedItems()}
        ) or "linux"
        bootloader_sel = sys_page.bootloader_combo.currentText()
        greeter_sel    = sys_page.greeter_combo.currentText()
        root_pw_status = (
            f'<span style="color:#2ecc71;">&#10003; {get_text("summary_root_set")}</span>'
            if user_page.root_pass.text()
            else f'<span style="color:#e74c3c;">&#10007; {get_text("summary_root_none")}</span>'
        )

        # Build user rows
        if user_page.users:
            user_rows = "".join(
                self._row(
                    f"&nbsp;&nbsp;{u['username']}",
                    f'<span style="color:{"#e67e22" if u["sudo"] else "#3498db"};">' +
                    (get_text("role_admin") if u["sudo"] else get_text("role_standard")) +
                    '</span>',
                )
                for u in user_page.users
            )
        else:
            user_rows = self._row("&nbsp;&nbsp;", get_text("summary_no_users"), "#7f8c8d")

        if _current_lang == "tr":
            sec_system  = "Sistem"
            sec_disk    = "Disk"
            sec_security = "Güvenlik"
            sec_users   = "Kullanıcılar"
            sec_extras  = "Ekstra Paketler"
        else:
            sec_system  = "System"
            sec_disk    = "Disk"
            sec_security = "Security"
            sec_users   = "Users"
            sec_extras  = "Extra Packages"

        # Build extra packages info
        extra_pkgs = extra_page.get_selected_packages()
        multilib_on = extra_page.is_multilib_enabled()
        multilib_status = (
            f'<span style="color:#2ecc71;">&#10003; {get_text("summary_multilib_on")}</span>'
            if multilib_on
            else f'<span style="color:#e74c3c;">&#10007; {get_text("summary_multilib_off")}</span>'
        )
        if extra_pkgs:
            extra_pkgs_display = ", ".join(extra_pkgs[:10])
            if len(extra_pkgs) > 10:
                extra_pkgs_display += f" (+{len(extra_pkgs) - 10})"
        else:
            extra_pkgs_display = "-"

        html = f"""
        <table width="100%" cellspacing="0" cellpadding="0">
          {self._section(sec_system)}
          {self._row(get_text('summary_desktop').replace('<b>','').replace('</b>',''),
                     sys_page.de_combo.currentText())}
          {self._row(get_text('summary_kb_tz').replace('<b>','').replace('</b>',''),
                     f"{sys_page.kb_combo.currentText()} &nbsp;/&nbsp; {sys_page.tz_combo.currentText()}")}
          {self._row(get_text('summary_mirrors').replace('<b>','').replace('</b>',''), mirrors)}
          {self._row(get_text('summary_kernel').replace('<b>','').replace('</b>',''),
                     f'<span style="color:#2ecc71;">{kernels_sel}</span>')}
          {self._row(get_text('summary_bootloader').replace('<b>','').replace('</b>',''),
                     f'<span style="color:#2ecc71;">{bootloader_sel}</span>')}
          {self._row(get_text('summary_greeter').replace('<b>','').replace('</b>',''),
                     f'<span style="color:#2ecc71;">{greeter_sel}</span>')}

          {self._section(sec_disk)}
          {self._row(get_text('summary_disk').replace('<b>','').replace('</b>',''),
                     f'<span style="color:#e74c3c;">{disk_sel}</span>')}

          {self._section(sec_security)}
          {self._row(get_text('summary_root_pw').replace('<b>','').replace('</b>',''),
                     root_pw_status)}

          {self._section(sec_users)}
          {user_rows}

          {self._section(sec_extras)}
          {self._row(get_text('summary_multilib').replace('<b>','').replace('</b>',''),
                     multilib_status)}
          {self._row(get_text('summary_extra_pkgs').replace('<b>','').replace('</b>',''),
                     f'<span style="color:#3498db;">{extra_pkgs_display}</span>')}
        </table>
        """
        self.summary_box.setHtml(html)

    def start_install_process(self):
        reply = QMessageBox.question(
            self,
            get_text("confirm_title"),
            get_text("confirm_msg"),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            if not self.generate_json():
                return
            self.main_window.next_page()          # Move to install progress page (index 7)
            self.main_window.pages[7].start_installation()

    @staticmethod
    def _build_package_list(sys_page, extra_packages=None) -> list:
        """Builds the package list dynamically based on bootloader, DE, and user selections."""
        base_packages = ["firefox", "dolphin", "konsole", "python-pyqt6", "sudo"]

        # Add bootloader-specific packages
        bootloader = sys_page.selected_bootloader()
        if bootloader == "Grub":
            base_packages.extend(["grub", "efibootmgr", "os-prober"])
        elif bootloader == "Refind":
            base_packages.append("refind")
        # Systemd-boot doesn't need extra packages

        # Add greeter packages based on manual choice or DE default
        greeter_data = sys_page.greeter_combo.currentData()
        if greeter_data != "default":
            if greeter_data == "lightdm-gtk-greeter":
                base_packages.extend(["lightdm", "lightdm-gtk-greeter"])
            else:
                base_packages.append(greeter_data)
        else:
            de = sys_page.de_combo.currentText()
            if de == "KDE Plasma":
                base_packages.append("sddm")
            elif de == "GNOME":
                base_packages.append("gdm")
            elif de in ("Xfce4", "Sway", "i3-wm"):
                base_packages.extend(["lightdm", "lightdm-gtk-greeter"])
            elif de in ("Hyprland", "bspwm"):
                base_packages.append("sddm")

        # Add user-selected extra packages (skip flatpak: prefixed ones)
        if extra_packages:
            for pkg in extra_packages:
                if pkg.startswith("flatpak:"):
                    # Flatpak apps will be installed post-install
                    if "flatpak" not in base_packages:
                        base_packages.append("flatpak")
                else:
                    base_packages.append(pkg)

        # Remove duplicates while preserving order
        seen = set()
        unique_packages = []
        for pkg in base_packages:
            if pkg not in seen:
                seen.add(pkg)
                unique_packages.append(pkg)

        return unique_packages

    @staticmethod
    def _build_custom_commands(multilib_enabled: bool, extra_packages: list) -> list:
        """Builds post-install custom commands for archinstall.
        
        These commands run inside the chroot after base installation.
        """
        commands = []

        if multilib_enabled:
            # Enable multilib repository in pacman.conf
            # The sed command uncomments the [multilib] section and its Include line
            commands.append(
                'sed -i "/\\[multilib\\]/,/Include/ s/^#//" /etc/pacman.conf'
            )
            commands.append("pacman -Sy --noconfirm")

        # Install flatpak apps if any were selected
        flatpak_apps = [pkg.split(":", 1)[1] for pkg in extra_packages if pkg.startswith("flatpak:")]
        if flatpak_apps:
            commands.append("flatpak remote-add --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo")
            for app_name in flatpak_apps:
                # Map friendly names to flatpak IDs
                flatpak_ids = {
                    "spotify": "com.spotify.Client",
                }
                flatpak_id = flatpak_ids.get(app_name, app_name)
                commands.append(f"flatpak install -y flathub {flatpak_id}")

        return commands

    def generate_json(self):
        """Generates archinstall 4.x-compatible config and creds JSON files."""
        sys_page    = self.main_window.pages[1]
        mirror_page = self.main_window.pages[2]
        disk_page   = self.main_window.pages[3]
        user_page   = self.main_window.pages[4]
        extra_page  = self.main_window.pages[5]

        # --- Extra packages ---
        extra_packages = extra_page.get_selected_packages()
        multilib_enabled = extra_page.is_multilib_enabled()

        # --- Mirror regions ---
        selected_regions = mirror_page.get_selected_regions()
        if not selected_regions:
            selected_regions = ["Worldwide"]
        mirror_dict = {region: [] for region in selected_regions}

        # --- Disk info ---
        selected_disk_path = disk_page.disk_combo.currentText().split(" ")[0]
        selected_de = sys_page.de_combo.currentText()

        # Greeter choices per DE (GreeterType enum values)
        greeters = {
            "KDE Plasma": "sddm",
            "GNOME": "gdm",
            "Xfce4": "lightdm-gtk-greeter",
            "Hyprland": "sddm",
            "Sway": "lightdm-gtk-greeter",
            "i3-wm": "lightdm-gtk-greeter",
            "bspwm": "sddm",
        }
        # --- Compute partition sizes ---
        total_bytes = get_disk_size_bytes(selected_disk_path)
        MiB = 1024 * 1024
        total_mib   = total_bytes // MiB

        boot_start_mib = 1
        boot_size_mib  = 512
        root_start_mib = boot_start_mib + boot_size_mib  # 513 MiB

        # Reserve 1 MiB at end for GPT backup header
        usable_mib = total_mib - root_start_mib - 1

        if usable_mib < (20 * 1024):
            # Disk < 20 GiB: no separate home, everything goes to root
            root_size_mib = usable_mib
            home_size_mib = 0
        else:
            # Allocate 40% to root (min 20 GiB, max 100 GiB), rest to home
            calculated_root_mib = int(usable_mib * 0.4)
            root_size_mib = min(max(calculated_root_mib, 20 * 1024), 100 * 1024)
            home_size_mib = usable_mib - root_size_mib

        home_start_mib = root_start_mib + root_size_mib

        # archinstall Size serialisation format
        sector_512 = {"unit": "B", "value": 512}

        def make_size(value_mib):
            return {
                "sector_size": sector_512,
                "unit": "MiB",
                "value": value_mib,
            }

        partition_list = [
            {
                "btrfs": [],
                "flags": ["boot", "esp"],
                "fs_type": "fat32",
                "start": make_size(boot_start_mib),
                "size": make_size(boot_size_mib),
                "mount_options": [],
                "mountpoint": "/boot",
                "status": "create",
                "type": "primary",
                "dev_path": None,
                "obj_id": str(uuid.uuid4()),
            },
            {
                "btrfs": [],
                "flags": [],
                "fs_type": "ext4",
                "start": make_size(root_start_mib),
                "size": make_size(root_size_mib),
                "mount_options": [],
                "mountpoint": "/",
                "status": "create",
                "type": "primary",
                "dev_path": None,
                "obj_id": str(uuid.uuid4()),
            },
        ]

        if home_size_mib > 0:
            partition_list.append({
                "btrfs": [],
                "flags": [],
                "fs_type": "ext4",
                "start": make_size(home_start_mib),
                "size": make_size(home_size_mib),
                "mount_options": [],
                "mountpoint": "/home",
                "status": "create",
                "type": "primary",
                "dev_path": None,
                "obj_id": str(uuid.uuid4()),
            })

        # ═══════════════════════════════════════════════════════════
        # 1. MAIN CONFIG — archinstall 4.x compatible
        # ═══════════════════════════════════════════════════════════
        arch_config = {
            "archinstall-language": "English",

            "app_config": {
                "audio_config": {"audio": "pipewire"},
            },

            "mirror_config": {
                "mirror_regions": mirror_dict,
            },

            "bootloader_config": {
                "bootloader": sys_page.selected_bootloader(),
                "uki": False,
                "removable": True,
            },

            "disk_config": {
                "config_type": "manual_partitioning",
                "device_modifications": [
                    {
                        "device": selected_disk_path,
                        "partitions": partition_list,
                        "wipe": True,
                    }
                ],
            },

            "hostname": "zelixos",
            "kernels": sys_page.selected_kernels(),
            "locale_config": {
                "kb_layout": sys_page.kb_combo.currentText(),
                "sys_enc": "UTF-8",
                "sys_lang": "en_US.UTF-8",
            },

            "network_config": {"type": "nm"},

            "ntp": True,
            "packages": self._build_package_list(sys_page, extra_packages),
            "parallel_downloads": 0,

            "additional_repositories": ["multilib"] if multilib_enabled else [],

            "profile_config": {
                "gfx_driver": None,
                "greeter": (
                    sys_page.greeter_combo.currentText() 
                    if sys_page.greeter_combo.currentData() != "default" 
                    else greeters.get(selected_de, "sddm")
                ),
                "profile": {
                    "main": "Desktop",
                    "details": [selected_de],
                },
            },

            "services": [],
            "custom_commands": self._build_custom_commands(multilib_enabled, extra_packages),
            "swap": {"enabled": True, "algorithm": "zstd"},
            "timezone": sys_page.tz_combo.currentText(),
        }

        # ═══════════════════════════════════════════════════════════
        # 2. USER CREDENTIALS (CREDS)
        # ═══════════════════════════════════════════════════════════
        arch_creds = {}

        formatted_users = []
        for u in user_page.users:
            formatted_users.append({
                "username": u["username"],
                "!password": u["password"],
                "sudo": u["sudo"],
                "groups": [],
            })

        if formatted_users:
            arch_creds["!users"] = formatted_users

        # Root password: fall back to first user's password if not set
        root_pw = user_page.root_pass.text()
        if not root_pw and user_page.users:
            root_pw = user_page.users[0]["password"]
        if root_pw:
            arch_creds["!root-password"] = root_pw

        # Clean up any old temp config files before generating new ones
        if hasattr(self.main_window, "cleanup_install_files"):
            self.main_window.cleanup_install_files()

        config_path = None
        creds_path = None
        try:
            with tempfile.NamedTemporaryFile(delete=False, mode="w", encoding="utf-8",
                                              prefix="zelix_config_", suffix=".json") as config_file:
                config_path = config_file.name
                json.dump(arch_config, config_file, indent=4, ensure_ascii=False)

            with tempfile.NamedTemporaryFile(delete=False, mode="w", encoding="utf-8",
                                              prefix="zelix_creds_", suffix=".json") as creds_file:
                creds_path = creds_file.name
                json.dump(arch_creds, creds_file, indent=4, ensure_ascii=False)

            self.main_window.install_config_path = config_path
            self.main_window.install_creds_path = creds_path
            return True
        except Exception as e:
            if config_path and os.path.exists(config_path):
                try:
                    os.remove(config_path)
                except Exception:
                    pass
            if creds_path and os.path.exists(creds_path):
                try:
                    os.remove(creds_path)
                except Exception:
                    pass
            QMessageBox.critical(self, "Error", f"Install config generation failed:\n{e}")
            return False

    def retranslate(self):
        self.title_label.setText(get_text("summary_title"))
        self.finish_btn.setText(get_text("start_install_btn"))
        self.back_btn.setText(get_text("back"))
        self.next_btn.setText(get_text("next")) if hasattr(self, "next_btn") else None


# ─────────────────────────────────────────────
#  Install Progress Page
# ─────────────────────────────────────────────

class InstallProgressPage(InstallerPage):
    """Shows archinstall logs live and copies ZelixOS post-install files."""

    def __init__(self, parent):
        super().__init__(parent)

        self.title_label = QLabel()
        self.title_label.setStyleSheet(
            "font-size: 28px; font-weight: bold; color: #f39c12; margin-bottom: 10px;"
        )
        self.main_layout.addWidget(self.title_label)

        self.log_console = QPlainTextEdit()
        self.log_console.setReadOnly(True)
        self.log_console.setStyleSheet("""
            background-color: #0c0c0c;
            color: #00ff00;
            font-family: 'Consolas', 'Monospace';
            font-size: 13px;
            padding: 10px;
            border-radius: 5px;
        """)
        self.main_layout.addWidget(self.log_console)

        self.ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')

        self.finish_btn = QPushButton()
        self.finish_btn.setStyleSheet(
            "background: #2ecc71; color: black; font-weight: bold; font-size: 16px;"
        )
        self.finish_btn.hide()
        self.finish_btn.clicked.connect(lambda: os.system("reboot"))
        self.main_layout.addWidget(self.finish_btn)

        self.process = QProcess(self)
        self.process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.finished.connect(self.process_finished)

        self.retranslate()

    def start_installation(self):
        config_path = getattr(self.main_window, "install_config_path", None)
        creds_path = getattr(self.main_window, "install_creds_path", None)

        if not config_path or not creds_path:
            QMessageBox.critical(self, "Error", "Installation config files could not be found.")
            return

        self.log_console.clear()
        self.log_console.appendPlainText(get_text("install_log_header"))

        self.process.start("pkexec", [
            "archinstall",
            "--silent",
            "--config", config_path,
            "--creds", creds_path,
        ])

    def handle_stdout(self):
        data = self.process.readAllStandardOutput()
        raw_text = bytes(data).decode("utf8", errors="replace")
        clean_text = self.ansi_escape.sub('', raw_text)

        if clean_text.strip():
            self.log_console.appendPlainText(clean_text.strip())

        scrollbar = self.log_console.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def process_finished(self, exit_code, exit_status):
        if exit_code == 0:
            self.run_post_install()
            self.title_label.setText(get_text("install_title_done"))
            self.title_label.setStyleSheet(
                "font-size: 28px; font-weight: bold; color: #2ecc71;"
            )
            self.log_console.appendPlainText(get_text("install_done_msg"))
            self.finish_btn.show()
        else:
            self.title_label.setText(get_text("install_title_fail"))
            self.title_label.setStyleSheet(
                "font-size: 28px; font-weight: bold; color: #e74c3c;"
            )
            self.log_console.appendPlainText(
                get_text("install_fail_msg").format(code=exit_code)
            )

        if hasattr(self.main_window, "cleanup_install_files"):
            self.main_window.cleanup_install_files()

    def run_post_install(self):
        """Copies ZelixOS-specific files (zelixdeps) to the newly installed disk."""
        dirr = os.path.dirname(os.path.abspath(__file__))
        deps_path = os.path.join(dirr, "zelixdeps")

        if not os.path.exists(deps_path):
            self.log_console.appendPlainText(get_text("post_warn_no_deps"))
            return

        # Determine root and boot partition paths dynamically using lsblk
        disk_page = self.main_window.pages[3]
        selected_disk_text = disk_page.disk_combo.currentText()
        if not selected_disk_text:
            self.log_console.appendPlainText(get_text("post_error_no_disk"))
            return
            
        selected_disk = selected_disk_text.split(" ")[0]

        # Dynamic partition detection using lsblk + PARTTYPE
        # Instead of guessing /dev/sdaX or /dev/nvme0n1pX, we query the 
        # actual partition table to find boot (ESP/fat32) and root (ext4) partitions.
        root_part = None
        boot_part = None
        try:
            result = subprocess.run(
                ['lsblk', '-n', '-o', 'NAME,FSTYPE,PARTFLAGS,MOUNTPOINT', '-r', selected_disk],
                capture_output=True, text=True, check=True
            )
            for line in result.stdout.strip().split('\n'):
                cols = line.split()
                if len(cols) < 2:
                    continue
                part_name = f"/dev/{cols[0]}"
                fstype = cols[1] if len(cols) > 1 else ""
                
                # Skip the disk device itself
                if part_name == selected_disk:
                    continue
                
                if fstype in ("vfat", "fat32") and boot_part is None:
                    boot_part = part_name
                elif fstype == "ext4" and root_part is None:
                    root_part = part_name
        except Exception:
            pass

        # Fallback to name-based guessing if lsblk detection failed
        if not root_part or not boot_part:
            self.log_console.appendPlainText(get_text("post_warn_lsblk_fail"))
            if any(x in selected_disk for x in ("nvme", "mmcblk", "loop")):
                if not boot_part:
                    boot_part = f"{selected_disk}p1"
                if not root_part:
                    root_part = f"{selected_disk}p2"
            else:
                if not boot_part:
                    boot_part = f"{selected_disk}1"
                if not root_part:
                    root_part = f"{selected_disk}2"

        self.log_console.appendPlainText(get_text("post_copy_header"))
        self.log_console.appendPlainText(get_text("post_root_partition").format(part=root_part))
        self.log_console.appendPlainText(get_text("post_boot_partition").format(part=boot_part))
        self.log_console.appendPlainText(get_text("post_source").format(src=deps_path))
        QApplication.processEvents()

        # Bundle all privileged commands into one bash script to avoid
        # multiple pkexec password prompts. Added bootloader branding.
        # Includes a cleanup trap for safe umount on any failure.
        script_content = f"""#!/bin/bash

# Cleanup trap — ensures partitions are always unmounted on exit
BOOT_MOUNTED=0
cleanup() {{
    echo "Temizlik yapılıyor..."
    [ "$BOOT_MOUNTED" == "1" ] && umount /mnt/zelix_target/boot 2>/dev/null
    mountpoint -q /mnt/zelix_target && umount /mnt/zelix_target 2>/dev/null
}}
trap cleanup EXIT

set -e

# Log file for debugging
LOGFILE="/tmp/zelixos_postinstall.log"
exec > >(tee -a "$LOGFILE") 2>&1

echo "Hedef dizinler hazırlanıyor..."
mkdir -p /mnt/zelix_target

echo "Kök bölüm bağlanıyor: {root_part}"
if ! mount {root_part} /mnt/zelix_target; then
    echo "HATA: Kök bölüm ({root_part}) bağlanamadı!"
    exit 1
fi

# Verify mount succeeded by checking for essential directories
if [ ! -d "/mnt/zelix_target/etc" ] && [ ! -d "/mnt/zelix_target/usr" ]; then
    echo "HATA: Kök bölüm bağlandı ama boş görünüyor. Kurulum başarısız olmuş olabilir."
    exit 1
fi

mkdir -p /mnt/zelix_target/boot
echo "Önyükleme bölümü bağlanıyor: {boot_part}"
if mount {boot_part} /mnt/zelix_target/boot; then
    BOOT_MOUNTED=1
else
    echo "UYARI: Önyükleme bölümü bağlanamadı, önyükleyici isimlendirmesi atlanıyor."
fi

echo "Dosyalar kopyalanıyor..."
if [ -d "{deps_path}" ] && [ "$(ls -A {deps_path})" ]; then
    cp -arv "{deps_path}/." /mnt/zelix_target/
else
    echo "UYARI: zelixdeps klasörü boş veya erişilemez, atlanıyor."
fi

echo "ZelixOS Branding ayarlanıyor..."
mkdir -p /mnt/zelix_target/etc

# os-release & lsb-release
cat <<EOF > /mnt/zelix_target/etc/os-release
NAME="ZelixOS"
PRETTY_NAME="ZelixOS Aurora"
ID=zelixos
ID_LIKE=arch
BUILD_ID=rolling
ANSI_COLOR="0;34"
HOME_URL="https://zelixos.com"
DOCUMENTATION_URL="https://zelixos.com/docs/docs.html"
SUPPORT_URL="https://zelixos.com"
BUG_REPORT_URL="https://zelixos.com/br.html"
LOGO=/usr/share/zelix/zelix-icon.png
EOF

cat <<EOF > /mnt/zelix_target/etc/lsb-release
DISTRIB_ID=ZelixOS
DISTRIB_RELEASE=rolling
DISTRIB_DESCRIPTION="ZelixOS Aurora"
EOF

echo "ZelixOS Aurora \\l" > /mnt/zelix_target/etc/issue
echo "zelixos" > /mnt/zelix_target/etc/hostname

# Bootloader Branding
if [ "$BOOT_MOUNTED" == "1" ]; then
    echo "Önyükleyici etiketleri güncelleniyor..."
    
    # 1. systemd-boot
    if [ -d "/mnt/zelix_target/boot/loader/entries" ]; then
        echo "systemd-boot girişleri düzenleniyor..."
        sed -i 's/Arch Linux/ZelixOS/g' /mnt/zelix_target/boot/loader/entries/*.conf 2>/dev/null || true
    fi
    
    # 2. GRUB
    if [ -f "/mnt/zelix_target/etc/default/grub" ]; then
        echo "GRUB yapılandırması güncelleniyor..."
        sed -i 's/GRUB_DISTRIBUTOR="Arch"/GRUB_DISTRIBUTOR="ZelixOS"/g' /mnt/zelix_target/etc/default/grub
        # Run grub-mkconfig inside chroot
        if command -v arch-chroot &> /dev/null; then
            arch-chroot /mnt/zelix_target grub-mkconfig -o /boot/grub/grub.cfg || true
        fi
    fi
fi

# Always enable multilib repository (ZelixOS default)
echo "Multilib deposu etkinleştiriliyor..."
if [ -f "/mnt/zelix_target/etc/pacman.conf" ]; then
    # Uncomment [multilib] section and its Include line
    sed -i '/\\[multilib\\]/,/Include/ s/^#//' /mnt/zelix_target/etc/pacman.conf
    echo "-> Multilib deposu etkinleştirildi."
else
    echo "UYARI: pacman.conf bulunamadı, multilib atlanıyor."
fi

# Add zelixrepo to the installed system
echo "ZelixRepo ekleniyor..."
if [ -f "/mnt/zelix_target/etc/pacman.conf" ]; then
    if ! grep -q "\\[zelixrepo\\]" /mnt/zelix_target/etc/pacman.conf; then
        cat <<EOF >> /mnt/zelix_target/etc/pacman.conf

[zelixrepo]
SigLevel = Optional TrustAll
Server = https://raw.githubusercontent.com/ZelixOS/zelix-repo/main/x86_64
EOF
        echo "-> ZelixRepo başarıyla eklendi."
    else
        echo "-> ZelixRepo zaten mevcut."
    fi
fi

echo "Senkronize ediliyor..."
sync

echo "İşlem başarıyla tamamlandı!"
# cleanup trap handles umount automatically
"""

        script_path = None
        try:
            with tempfile.NamedTemporaryFile(delete=False, mode="w", encoding="utf-8",
                                              prefix="zelix_post_install_", suffix=".sh") as f:
                script_path = f.name
                f.write(script_content)
            os.chmod(script_path, 0o755)

            # Use QProcess to run pkexec so we can see the script's output in our console
            res = subprocess.run(["pkexec", "/bin/bash", script_path], capture_output=True, text=True)
            
            if res.returncode == 0:
                self.log_console.appendPlainText(res.stdout)
                self.log_console.appendPlainText(get_text("post_copy_done"))
            else:
                self.log_console.appendPlainText(get_text("post_error_script_fail").format(code=res.returncode))
                self.log_console.appendPlainText(res.stderr)
                self.log_console.appendPlainText(res.stdout)
        except Exception as e:
            self.log_console.appendPlainText(get_text("post_copy_error").format(err=e))
        finally:
            if os.path.exists(script_path):
                try:
                    os.remove(script_path)
                except:
                    pass

    def retranslate(self):
        self.title_label.setText(get_text("install_title_running"))
        self.finish_btn.setText(get_text("reboot_btn"))


# ─────────────────────────────────────────────
#  Main Window
# ─────────────────────────────────────────────

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ZelixOS Installer v1.04")
        self.setMinimumSize(800, 600)
        self.resize(1024, 720)

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Left sidebar
        sidebar = QFrame()
        sidebar.setFixedWidth(250)
        sidebar.setStyleSheet("background-color: #1b1e20; border-right: 2px solid #31363b;")

        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(20, 40, 20, 20)

        logo_container = QHBoxLayout()
        logo_container.setContentsMargins(0, 0, 0, 0)
        logo_container.setSpacing(10)

        side_logo_label = QLabel()
        side_logo_label.setFixedSize(32, 32)
        side_logo_label.setStyleSheet("border: none; background: transparent;")
        
        dirr = os.path.dirname(os.path.abspath(__file__))
        local_logo = os.path.join(dirr, "icons", "zelixos_logo.png")
        logo_path = local_logo if os.path.exists(local_logo) else "/usr/share/zelixins/icons/zelixos_logo.png"
        
        side_logo_pixmap = QPixmap(logo_path)
        if not side_logo_pixmap.isNull():
            scaled_side_logo = side_logo_pixmap.scaled(32, 32, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            side_logo_label.setPixmap(scaled_side_logo)
        
        logo_text = QLabel("ZelixOS")
        logo_text.setStyleSheet("font-size: 24px; font-weight: bold; color: #9b59b6; border: none; background: transparent;")
        
        logo_container.addWidget(side_logo_label)
        logo_container.addWidget(logo_text)
        logo_container.addStretch()
        
        sidebar_layout.addLayout(logo_container)
        sidebar_layout.addSpacing(40)

        # Step labels — refreshed by retranslate_all()
        self.step_labels = [QLabel() for _ in range(8)]
        for lbl in self.step_labels:
            sidebar_layout.addWidget(lbl)

        sidebar_layout.addStretch()

        # Right content area
        content_frame = QFrame()
        content_frame.setStyleSheet("background-color: #24272b;")
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(0, 0, 0, 0)

        self.stacked_widget = QStackedWidget()

        self.pages = [
            WelcomePage(self),          # 0
            SystemConfigPage(self),     # 1
            MirrorConfigPage(self),     # 2
            DiskConfigPage(self),       # 3
            UserAccountPage(self),      # 4
            ExtraPackagesPage(self),    # 5
            SummaryPage(self),          # 6
            InstallProgressPage(self),  # 7
        ]
        for page in self.pages:
            self.stacked_widget.addWidget(page)

        content_layout.addWidget(self.stacked_widget)
        main_layout.addWidget(sidebar)
        main_layout.addWidget(content_frame)

        self.install_config_path = None
        self.install_creds_path = None

        self.setStyleSheet("""
            QWidget {
                font-family: 'Segoe UI', sans-serif;
                color: #eff0f1;
            }
            QLineEdit, QComboBox, QListWidget {
                background-color: #1b1e20;
                border: 1px solid #31363b;
                border-radius: 6px;
                padding: 10px;
                font-size: 15px;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 1px solid #9b59b6;
            }
            QPushButton {
                background: #8e44ad;
                color: white;
                border-radius: 6px;
                padding: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #9b59b6;
            }
        """)

        self.retranslate_all()

    def cleanup_install_files(self):
        for attr in ("install_config_path", "install_creds_path"):
            path = getattr(self, attr, None)
            if path and os.path.exists(path):
                try:
                    os.remove(path)
                except Exception:
                    pass
            if hasattr(self, attr):
                delattr(self, attr)

        self.install_config_path = None
        self.install_creds_path = None

    def closeEvent(self, event):
        self.cleanup_install_files()
        event.accept()

    def retranslate_all(self):
        """Re-applies all translatable strings to every page and sidebar."""
        step_keys = ["step_1", "step_2", "step_3", "step_4", "step_5", "step_6", "step_7", "step_8"]
        for lbl, key in zip(self.step_labels, step_keys):
            lbl.setText(get_text(key))

        for page in self.pages:
            page.retranslate()

        self.update_sidebar()

    def next_page(self):
        idx = self.stacked_widget.currentIndex()
        if idx < self.stacked_widget.count() - 1:
            if idx + 1 == 6:  # Summary page is at index 6
                self.pages[6].update_summary()
            self.stacked_widget.setCurrentIndex(idx + 1)
            self.update_sidebar()

    def prev_page(self):
        idx = self.stacked_widget.currentIndex()
        # Block going back once installation has started (page 7)
        if idx > 0 and idx != 7:
            self.stacked_widget.setCurrentIndex(idx - 1)
            self.update_sidebar()

    def update_sidebar(self):
        idx = self.stacked_widget.currentIndex()
        for i, lbl in enumerate(self.step_labels):
            if i == idx:
                lbl.setStyleSheet(
                    "font-size: 16px; margin-bottom: 15px; color: #9b59b6; font-weight: bold;"
                )
            elif i < idx:
                lbl.setStyleSheet(
                    "font-size: 16px; margin-bottom: 15px; color: #2ecc71;"
                )
            else:
                lbl.setStyleSheet(
                    "font-size: 16px; margin-bottom: 15px; color: #7f8c8d;"
                )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())