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
import html
import hashlib
from install_profiles import PROFILES, COMPONENTS, ZELIX_APPS, preset, effective_components
from installer_translations import extend_languages, PACKAGE_ES
from installer_support import (selected_greeter, validate_choices, build_partitions,
                               partition_path, ZELIX_PACKAGES, post_install_packages)
from desktop_catalog import DESKTOPS, desktops_for, appearance_packages
from desktop_page import DesktopPage
from installation_type_page import InstallationTypePage
from bottom_navigation import BottomNavigation
from language_support import apply_qt_language
from system_locale import SYSTEM_LANGUAGES, UI_LOCALES
from disk_page import DiskConfigPage
from disk_layout import FILESYSTEM_PACKAGES
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QStackedWidget, QFrame, QComboBox, QHBoxLayout,
    QFormLayout, QListWidget, QListWidgetItem, QCheckBox, QMessageBox,
    QSpacerItem, QSizePolicy, QPlainTextEdit, QTreeWidget, QTreeWidgetItem,
    QAbstractItemView
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
        "step_3": "3. Masaüstü Ortamları",
        "step_4": "4. Ayna Seçimi",
        "step_5": "5. Disk Seçimi",
        "step_6": "6. Kullanıcılar",
        "step_7": "7. Ekstra Paketler",
        "step_8": "8. Özet",
        "step_9": "9. Kurulum",

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
        "extra_title": "Ek Paketler",
        "extra_desc": "Kurulumdan sonra yüklenecek uygulamaları seçin. Firefox varsayılan olarak seçilidir.",
        "extra_cat_browsers": "Tarayıcılar",
        "extra_cat_communication": "İletişim",
        "extra_cat_terminals": "Terminal ve Editörler",
        "extra_cat_graphics": "Grafik",
        "extra_cat_utilities": "Araçlar",
        "extra_cat_custom": "Özel Paketler",
        "extra_cat_gaming": "Oyun",
        "extra_cat_dev": "Geliştirme",
        "extra_cat_multimedia": "Multimedya",
        "extra_cat_office": "Ofis",
        "extra_cat_system": "Sistem",
        "extra_multilib": "Multilib deposunu etkinleştir (32-bit uygulama desteği, Steam vb. için gerekli)",
        "extra_multilib_steam": "Multilib deposunu etkinleştir (Steam seçiliyken zorunludur)",
        "extra_selected_count_one": "{count}/{total} paket seçildi",
        "extra_selected_count": "{count}/{total} paket seçildi",
        "extra_search": "Uygulama veya paket ara…",
        "extra_selected_only": "Yalnızca seçilenleri göster",
        "extra_custom_placeholder": "Depo paket adı yazın (ör. kitty)",
        "extra_custom_add": "Ekle",
        "extra_custom_remove": "Kaldır",
        "extra_custom_invalid": "Geçersiz paket adı. Küçük harf, sayı ve . _ + - karakterlerini kullanın.",
        "extra_custom_not_found": "“{package}” etkin Arch depolarında bulunamadı.",
        "extra_custom_exists": "“{package}” zaten listede; paket seçildi.",
        "extra_custom_check_title": "Paket Doğrulaması",
        "extra_custom_recheck_failed": "Şu özel paketler artık etkin depolarda bulunamıyor:\n\n{packages}",
        "extra_source_arch": "Arch",
        "extra_source_flatpak": "Flatpak",
        "extra_source_aur": "AUR",
        "extra_source_zelix": "Zelix Repo",
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
        "step_3": "3. Desktop Environments",
        "step_4": "4. Mirror Selection",
        "step_5": "5. Disk Selection",
        "step_6": "6. Users",
        "step_7": "7. Extra Packages",
        "step_8": "8. Summary",
        "step_9": "9. Installation",

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
        "extra_title": "Additional Packages",
        "extra_desc": "Choose applications to install with the system. Firefox is selected by default.",
        "extra_cat_browsers": "Browsers",
        "extra_cat_communication": "Communication",
        "extra_cat_terminals": "Terminals and Editors",
        "extra_cat_graphics": "Graphics",
        "extra_cat_utilities": "Utilities",
        "extra_cat_custom": "Custom Packages",
        "extra_cat_gaming": "Gaming",
        "extra_cat_dev": "Development",
        "extra_cat_multimedia": "Multimedia",
        "extra_cat_office": "Office",
        "extra_cat_system": "System",
        "extra_multilib": "Enable multilib repository (32-bit app support, required for Steam etc.)",
        "extra_multilib_steam": "Enable multilib repository (required while Steam is selected)",
        "extra_selected_count_one": "{count} of {total} selected",
        "extra_selected_count": "{count} of {total} selected",
        "extra_search": "Search applications or packages…",
        "extra_selected_only": "Show selected only",
        "extra_custom_placeholder": "Enter a repository package name (e.g. kitty)",
        "extra_custom_add": "Add",
        "extra_custom_remove": "Remove",
        "extra_custom_invalid": "Invalid package name. Use lowercase letters, numbers, and . _ + - characters.",
        "extra_custom_not_found": "“{package}” was not found in the enabled Arch repositories.",
        "extra_custom_exists": "“{package}” is already listed; the package was selected.",
        "extra_custom_check_title": "Package Validation",
        "extra_custom_recheck_failed": "These custom packages are no longer available in the enabled repositories:\n\n{packages}",
        "extra_source_arch": "Arch",
        "extra_source_flatpak": "Flatpak",
        "extra_source_aur": "AUR",
        "extra_source_zelix": "Zelix Repo",
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

extend_languages(LANGUAGES)

# Global language state — pages can access via get_text()
_current_lang = "en"


def get_text(key: str) -> str:
    """Returns the UI string for the current language."""
    return LANGUAGES.get(_current_lang, LANGUAGES["en"]).get(key, LANGUAGES["en"].get(key, key))


def set_language(lang_code: str):
    global _current_lang
    _current_lang = lang_code
    apply_qt_language(lang_code)


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
            ['lsblk', '-d', '-n', '-o', 'NAME,SIZE,MODEL,TYPE'],
            capture_output=True, text=True, check=True
        )
        disks = []
        for line in result.stdout.strip().split('\n'):
            if line:
                parts = line.split()
                if len(parts) >= 3 and parts[-1] == "disk":
                    parts = parts[:-1]
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
        return []


def get_disk_size_bytes(disk_path):
    """Returns the total size of a disk in bytes."""
    try:
        res = subprocess.run(
            ['lsblk', '-b', '-d', '-n', '-o', 'SIZE', disk_path],
            capture_output=True, text=True, check=True
        )
        return int(res.stdout.strip())
    except Exception:
        return 0  # Fail closed: never invent a target disk capacity.


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
        title.setStyleSheet("font-size: 76px; font-weight: bold; color: #FFFFFF; letter-spacing: 2px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.subtitle = QLabel()
        self.subtitle.setStyleSheet("font-size: 16px; color: #9E9EA8; margin-bottom: 20px;")
        self.subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Logo
        self.logo_label = QLabel()
        dirr = os.path.dirname(os.path.realpath(__file__))
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
        self.lang_label.setStyleSheet("color: #9E9EA8; font-size: 14px; margin-right: 8px;")
        self.lang_combo = QComboBox()
        self.lang_combo.addItem("English", "en")
        self.lang_combo.addItem("Türkçe", "tr")
        self.lang_combo.addItem("Español", "es")
        self.lang_combo.setFixedWidth(120)
        self.lang_combo.currentIndexChanged.connect(self._on_lang_changed)
        lang_row.addWidget(self.lang_label)
        lang_row.addWidget(self.lang_combo)

        btn_layout = QHBoxLayout()
        btn_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.start_btn = QPushButton()
        self.start_btn.setObjectName("primary_btn")
        self.start_btn.setFixedSize(300, 52)
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
        self.net_warn.setStyleSheet("color: #FF5555; font-weight: bold; margin-bottom: 10px;")
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
        self.form_layout.setFieldGrowthPolicy(
            QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow
        )

        self.system_language_label = QLabel()
        self.system_language_combo = QComboBox()
        self.system_language_combo.addItem('', 'installer')
        for name, locale in SYSTEM_LANGUAGES:
            self.system_language_combo.addItem(name, locale)
        self.form_layout.addRow(self.system_language_label, self.system_language_combo)
        self.system_language_note = QLabel()
        self.system_language_note.setWordWrap(True)
        self.system_language_note.setStyleSheet('color: #a5afbf; font-size: 11px;')
        self.form_layout.addRow('', self.system_language_note)

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
        self.kernel_list.setMinimumHeight(148)
        self.kernel_list.setMaximumHeight(180)
        self.kernel_list.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        for display, _key in self.KERNELS:
            self.kernel_list.addItem(display)
            self.kernel_list.item(self.kernel_list.count() - 1).setData(Qt.ItemDataRole.UserRole, _key)
        self.kernel_list.item(0).setSelected(True)  # Linux (Stable) selected by default
        self.form_layout.addRow(self.kernel_label, self.kernel_list)

        # Bootloader
        self.bootloader_label = QLabel()
        self.bootloader_combo = QComboBox()
        for display, _key in self.BOOTLOADERS:
            self.bootloader_combo.addItem(display)
        if not is_uefi():
            self.bootloader_combo.setCurrentIndex(1)
        self.form_layout.addRow(self.bootloader_label, self.bootloader_combo)

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
        self.next_btn.setObjectName("primary_btn")
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
        
        # Use a predictable, location-independent default for new installations.
        idx = self.tz_combo.findText("UTC")
        if idx < 0:
            self.tz_combo.insertItem(0, "UTC")
            idx = 0
        self.tz_combo.setCurrentIndex(idx)

    def selected_kernels(self) -> list:
        """Returns a list of archinstall kernel package names for all selected items."""
        kernels = [item.data(Qt.ItemDataRole.UserRole) for item in self.kernel_list.selectedItems()]
        return kernels if kernels else ["linux"]

    def selected_system_locale(self):
        selected = self.system_language_combo.currentData()
        return UI_LOCALES[_current_lang] if selected == 'installer' else selected

    def selected_bootloader(self) -> str:
        """Returns the archinstall bootloader string for the current selection."""
        idx = self.bootloader_combo.currentIndex()
        return self.BOOTLOADERS[idx][1] if 0 <= idx < len(self.BOOTLOADERS) else "Systemd-boot"

    def retranslate(self):
        self.title_label.setText(get_text("sys_title"))
        self.system_language_label.setText(get_text('system_language'))
        self.system_language_combo.setItemText(0, get_text('system_language_follow'))
        self.system_language_note.setText(get_text('system_language_note'))
        self.kb_label.setText(get_text("keyboard"))
        self.tz_label.setText(get_text("timezone"))
        self.kernel_label.setText(get_text("kernel"))
        # hint text is appended in parentheses
        for index, (_display, key) in enumerate(self.KERNELS):
            self.kernel_list.item(index).setText(get_text('kernel_' + key))
        hint = get_text("kernel_hint")
        self.kernel_label.setText(get_text("kernel").rstrip(":") + hint + ":")
        self.bootloader_label.setText(get_text("bootloader"))
        self.back_btn.setText(get_text("back"))
        self.next_btn.setText(get_text("next"))
        if not is_uefi():
            self.uefi_warn.setText(get_text("uefi_warning"))


# ─────────────────────────────────────────────
#  Disk Config Page
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
        self.add_user_btn.setStyleSheet("background: #FFFFFF; color: #000000; font-weight: bold; border-radius: 6px; padding: 10px;")
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
        self.remove_user_btn.setStyleSheet("background: #241315; color: #FF7070; border: 1px solid #4A1E22; border-radius: 6px; padding: 8px;")
        self.remove_user_btn.clicked.connect(self.remove_user)
        self.main_layout.addWidget(self.remove_user_btn)

        self.main_layout.addStretch()

        nav_layout = QHBoxLayout()
        self.back_btn = QPushButton()
        self.back_btn.clicked.connect(lambda: self.main_window.prev_page())
        self.next_btn = QPushButton()
        self.next_btn.setObjectName("primary_btn")
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
    WORLDWIDE_MIRRORS = [
        "https://geo.mirror.pkgbuild.com/$repo/os/$arch",
    ]

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
            item.setData(Qt.ItemDataRole.UserRole, _key)
            self.mirror_list.addItem(item)
            if display == "Worldwide":
                item.setSelected(True)

        self.main_layout.addWidget(self.mirror_list)
        self.main_layout.addStretch()

        nav_layout = QHBoxLayout()
        self.back_btn = QPushButton()
        self.back_btn.clicked.connect(lambda: self.main_window.prev_page())
        self.next_btn = QPushButton()
        self.next_btn.setObjectName("primary_btn")
        self.next_btn.clicked.connect(lambda: self.main_window.next_page())

        nav_layout.addWidget(self.back_btn)
        nav_layout.addStretch()
        nav_layout.addWidget(self.next_btn)
        self.main_layout.addLayout(nav_layout)

        self.retranslate()

    def get_selected_regions(self):
        """Returns the internal (English) keys of selected mirror regions."""
        return [item.data(Qt.ItemDataRole.UserRole) for item in self.mirror_list.selectedItems()]

    def get_selected_mirrors(self):
        """Return selected regions with concrete servers where one is defined."""
        return {
            region: list(self.WORLDWIDE_MIRRORS) if region == "Worldwide" else []
            for region in self.get_selected_regions()
        }

    def retranslate(self):
        for index, (_display, key) in enumerate(self.mirror_regions):
            self.mirror_list.item(index).setText(get_text('region_' + key))
        self.title_label.setText(get_text("mirror_title"))
        self.desc_label.setText(get_text("mirror_desc"))
        self.back_btn.setText(get_text("back"))
        self.next_btn.setText(get_text("next"))


# ─────────────────────────────────────────────
#  Extra Packages Page
# ─────────────────────────────────────────────

class ExtraPackagesPage(InstallerPage):
    """Optional packages shown by category."""

    # name, package, source, Turkish description, English description, default
    PACKAGE_CATEGORIES = [
        ("extra_cat_browsers", [
            ("Firefox", "firefox", "extra_source_arch",
             "Özgür, gizlilik odaklı web tarayıcısı.",
             "Free, privacy-focused web browser.", True),
            ("Chromium", "chromium", "extra_source_arch",
             "Chromium tabanlı hızlı ve sade tarayıcı.",
             "Fast, minimal Chromium-based browser.", False),
            ("Falkon", "falkon", "extra_source_arch",
             "Qt ile geliştirilmiş hafif web tarayıcısı.",
             "Lightweight web browser built with Qt.", False),
            ("Tor Browser Launcher", "torbrowser-launcher", "extra_source_arch",
             "Tor Browser'ı güvenli biçimde indirip başlatır.",
             "Securely downloads and launches Tor Browser.", False),
            ("Brave", "aur:brave-bin", "extra_source_aur",
             "Gizlilik korumaları yerleşik Chromium tabanlı tarayıcı.",
             "Chromium-based browser with built-in privacy protections.", False),
            ("LibreWolf", "librewolf", "extra_source_arch",
             "Firefox tabanlı, gizlilik ve güvenlik odaklı tarayıcı.",
             "Firefox-based browser focused on privacy and security.", False),
            ("Helium", "aur:helium-browser-bin", "extra_source_aur",
             "Gizlilik odaklı, sadeleştirilmiş Chromium tabanlı tarayıcı.",
             "Privacy-focused, streamlined Chromium-based browser.", False),
        ]),
        ("extra_cat_communication", [
            ("Thunderbird", "thunderbird", "extra_source_arch",
             "E-posta, takvim ve haber istemcisi.",
             "Email, calendar, and news client.", False),
            ("Discord", "discord", "extra_source_arch",
             "Topluluklar için sesli ve yazılı iletişim.",
             "Voice and text chat for communities.", False),
            ("Telegram Desktop", "telegram-desktop", "extra_source_arch",
             "Telegram'ın resmi masaüstü istemcisi.",
             "Official Telegram desktop client.", False),
            ("qBittorrent", "qbittorrent", "extra_source_arch",
             "Reklamsız, açık kaynak BitTorrent istemcisi.",
             "Ad-free, open-source BitTorrent client.", False),
            ("Signal Desktop", "signal-desktop", "extra_source_arch",
             "Uçtan uca şifreli mesajlaşma istemcisi.",
             "End-to-end encrypted messaging client.", False),
            ("Element", "element-desktop", "extra_source_arch",
             "Matrix ağı için açık kaynak iletişim istemcisi.",
             "Open-source communication client for Matrix.", False),
        ]),
        ("extra_cat_terminals", [
            ("Alacritty", "alacritty", "extra_source_arch", "GPU hızlandırmalı hızlı terminal emülatörü.", "Fast GPU-accelerated terminal emulator.", False),
            ("Kitty", "kitty", "extra_source_arch", "GPU hızlandırmalı, özellikli terminal emülatörü.", "Feature-rich GPU-accelerated terminal emulator.", False),
            ("WezTerm", "wezterm", "extra_source_arch", "Çapraz platform, Lua ile yapılandırılan terminal.", "Cross-platform terminal configured with Lua.", False),
            ("Foot", "foot", "extra_source_arch", "Wayland için hafif ve hızlı terminal.", "Lightweight and fast terminal for Wayland.", False),
            ("Ghostty", "ghostty", "extra_source_arch", "Modern, hızlı ve yerel terminal emülatörü.", "Modern, fast, and native terminal emulator.", False),
            ("Terminator", "terminator", "extra_source_arch", "Bölünebilir çoklu terminal çalışma alanı.", "Multi-terminal workspace with split panes.", False),
            ("Neovim", "neovim", "extra_source_arch", "Genişletilebilir terminal metin düzenleyicisi.", "Extensible terminal text editor.", False),
            ("Helix", "helix", "extra_source_arch", "Modern ve modal terminal metin düzenleyicisi.", "Modern modal terminal text editor.", False),
            ("Kate", "kate", "extra_source_arch", "KDE'nin güçlü grafiksel metin düzenleyicisi.", "Powerful graphical text editor from KDE.", False),
            ("Geany", "geany", "extra_source_arch", "Hafif kod düzenleyici ve geliştirme ortamı.", "Lightweight code editor and development environment.", False),
        ]),
        ("extra_cat_gaming", [
            ("Steam", "steam", "extra_source_arch",
             "Linux oyun mağazası ve oyun kütüphanesi.",
             "Linux game store and library.", False),
            ("Lutris", "lutris", "extra_source_arch",
             "Farklı kaynaklardaki oyunları tek yerde yönetir.",
             "Manages games from different sources in one place.", False),
            ("Wine", "wine", "extra_source_arch",
             "Windows uygulamaları için uyumluluk katmanı.",
             "Compatibility layer for Windows applications.", False),
            ("Winetricks", "winetricks", "extra_source_arch",
             "Wine bileşenlerini ve yaygın çalışma ortamlarını yönetir.",
             "Manages Wine components and common runtimes.", False),
            ("GameMode", "gamemode", "extra_source_arch",
             "Oyun sırasında sistem performansını optimize eder.",
             "Optimizes system performance while gaming.", False),
            ("MangoHud", "mangohud", "extra_source_arch",
             "FPS ve sistem bilgilerini oyun üzerinde gösterir.",
             "Shows FPS and system information in games.", False),
            ("ProtonUp-Qt", "flatpak:net.davidotek.pupgui2", "extra_source_flatpak",
             "Proton-GE gibi uyumluluk araçlarını yönetir.",
             "Manages compatibility tools such as Proton-GE.", False),
        ]),
        ("extra_cat_dev", [
            ("Code (OSS)", "code", "extra_source_arch", "Açık kaynak kod düzenleyici.", "Open-source code editor.", False),
            ("Git", "git", "extra_source_arch", "Dağıtık sürüm kontrol sistemi.", "Distributed version control system.", False),
            ("Base-devel", "base-devel", "extra_source_arch", "Arch paketleri derlemek için temel araçlar.", "Core tools for building Arch packages.", False),
            ("Python", "python", "extra_source_arch", "Python programlama dili ve çalışma ortamı.", "Python language and runtime.", False),
            ("Node.js", "nodejs", "extra_source_arch", "Sunucu tarafı JavaScript çalışma ortamı.", "Server-side JavaScript runtime.", False),
            ("Docker", "docker", "extra_source_arch", "Konteyner geliştirme ve çalıştırma platformu.", "Container development and runtime platform.", False),
            ("GCC", "gcc", "extra_source_arch", "GNU C ve C++ derleyici koleksiyonu.", "GNU C and C++ compiler collection.", False),
        ]),
        ("extra_cat_multimedia", [
            ("VLC", "vlc", "extra_source_arch", "Çok formatlı video ve müzik oynatıcı.", "Multi-format video and music player.", False),
            ("GIMP", "gimp", "extra_source_arch", "Gelişmiş görsel düzenleme uygulaması.", "Advanced image editing application.", False),
            ("OBS Studio", "obs-studio", "extra_source_arch", "Ekran kaydı ve canlı yayın aracı.", "Screen recording and live streaming tool.", False),
            ("Audacity", "audacity", "extra_source_arch", "Ses kaydı ve düzenleme uygulaması.", "Audio recording and editing application.", False),
            ("Kdenlive", "kdenlive", "extra_source_arch", "Doğrusal olmayan video düzenleyici.", "Non-linear video editor.", False),
            ("Spotify", "flatpak:com.spotify.Client", "extra_source_flatpak", "Müzik ve podcast istemcisi.", "Music and podcast client.", False),
            ("MPV", "mpv", "extra_source_arch", "Hafif ve güçlü komut satırı medya oynatıcısı.", "Lightweight and powerful command-line media player.", False),
            ("Celluloid", "celluloid", "extra_source_arch", "MPV için sade grafiksel arayüz.", "Simple graphical interface for MPV.", False),
            ("HandBrake", "handbrake", "extra_source_arch", "Video dönüştürme ve sıkıştırma aracı.", "Video transcoding and compression tool.", False),
        ]),
        ("extra_cat_graphics", [
            ("Inkscape", "inkscape", "extra_source_arch", "Vektörel çizim ve tasarım uygulaması.", "Vector illustration and design application.", False),
            ("Krita", "krita", "extra_source_arch", "Dijital çizim ve boyama uygulaması.", "Digital painting and illustration application.", False),
            ("Blender", "blender", "extra_source_arch", "3B modelleme, animasyon ve render paketi.", "3D modeling, animation, and rendering suite.", False),
        ]),
        ("extra_cat_office", [
            ("LibreOffice", "libreoffice-fresh", "extra_source_arch", "Belge, tablo ve sunum ofis paketi.", "Office suite for documents, sheets, and presentations.", False),
            ("Okular", "okular", "extra_source_arch", "PDF ve belge görüntüleyici.", "PDF and document viewer.", False),
            ("Evince", "evince", "extra_source_arch", "Sade ve hızlı belge görüntüleyici.", "Simple and fast document viewer.", False),
        ]),
        ("extra_cat_utilities", [
            ("Flameshot", "flameshot", "extra_source_arch", "Açıklama araçları içeren ekran görüntüsü uygulaması.", "Screenshot tool with annotation features.", False),
            ("KeePassXC", "keepassxc", "extra_source_arch", "Yerel ve güvenli parola yöneticisi.", "Local and secure password manager.", False),
            ("FileZilla", "filezilla", "extra_source_arch", "FTP, FTPS ve SFTP dosya aktarım istemcisi.", "FTP, FTPS, and SFTP file transfer client.", False),
            ("Remmina", "remmina", "extra_source_arch", "Uzak masaüstü bağlantı istemcisi.", "Remote desktop connection client.", False),
            ("Syncthing", "syncthing", "extra_source_arch", "Eşler arası dosya eşitleme aracı.", "Peer-to-peer file synchronization tool.", False),
        ]),
        ("extra_cat_system", [
            ("Timeshift", "timeshift", "extra_source_arch", "Sistem anlık görüntüsü ve geri yükleme aracı.", "System snapshot and restore utility.", False),
            ("Htop", "htop", "extra_source_arch", "Terminal tabanlı süreç görüntüleyici.", "Terminal-based process viewer.", False),
            ("Btop", "btop", "extra_source_arch", "Modern kaynak ve süreç izleyicisi.", "Modern resource and process monitor.", False),
            ("Fastfetch", "fastfetch", "extra_source_arch", "Terminalde sistem bilgilerini gösterir.", "Displays system information in the terminal.", False),
            ("Flatpak", "flatpak", "extra_source_arch", "Dağıtımdan bağımsız uygulama altyapısı.", "Distribution-independent application platform.", False),
            ("GParted", "gparted", "extra_source_arch", "Grafiksel disk bölümleme aracı.", "Graphical disk partition editor.", False),
            ("Fish Shell", "fish", "extra_source_arch", "Kullanıcı dostu komut satırı kabuğu.", "User-friendly command-line shell.", False),
            ("Yay", "yay", "extra_source_zelix", "AUR paketleri için yardımcı araç.", "Helper for installing AUR packages.", False),
            ("Paru", "paru", "extra_source_zelix", "Rust ile geliştirilmiş AUR yardımcısı.", "AUR helper written in Rust.", False),
        ]),
        ("extra_cat_custom", []),
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

        self.search_input = QLineEdit()
        self.search_input.setClearButtonEnabled(True)
        self.search_input.textChanged.connect(self._apply_filter)
        self.main_layout.addWidget(self.search_input)

        self.package_tree = QTreeWidget()
        self.package_tree.setColumnCount(1)
        self.package_tree.setHeaderHidden(True)
        self.package_tree.setRootIsDecorated(True)
        self.package_tree.setIndentation(20)
        self.package_tree.setUniformRowHeights(True)
        self.package_tree.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.package_tree.setStyleSheet("""
            QTreeWidget {
                background: #17181D;
                border: 1px solid #2B2C34;
                border-radius: 6px;
                color: #E6E6E6;
                font-size: 13px;
                outline: none;
            }
            QTreeWidget::item { height: 30px; }
            QTreeWidget::item:hover { background: #252630; }
            QTreeWidget::item:selected { background: #30313A; color: #FFFFFF; }
            QScrollBar:vertical {
                background: #121318;
                width: 9px;
                margin: 0;
            }
            QScrollBar::handle:vertical {
                background: #55565F;
                border-radius: 4px;
                min-height: 24px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: none; }
        """)

        self.package_items = {}
        self.package_metadata = {}
        self.category_items = {}
        self.category_packages = {}
        self.custom_packages = set()
        self.package_tree.blockSignals(True)

        categories = [
            ('extra_cat_zelix', [
                ('Zelix Hello', 'zelix-hello', 'extra_source_zelix', 'Karşılama ve sistem araçları.', 'Welcome and system tools.', False),
                ('Zelix Updater', 'zelix-updater', 'extra_source_zelix', 'Sistem güncellemeleri.', 'System updates.', False),
                ('Zelix CLI', 'zelix-cli', 'extra_source_zelix', 'Komut satırı yönetim aracı.', 'Command-line management.', False),
            ]),
            ('extra_cat_utilities_builtin', [
                ('Dolphin', 'dolphin', 'extra_source_arch', 'Dosya yöneticisi.', 'File manager.', False),
                ('Konsole', 'konsole', 'extra_source_arch', 'KDE terminali.', 'KDE terminal.', False),
                ('SDDM Settings', 'sddm-kcm', 'extra_source_arch', 'SDDM yapılandırma modülü.', 'SDDM configuration module.', False),
            ]),
            *self.PACKAGE_CATEGORIES,
        ]
        for cat_key, packages in categories:
            category_item = QTreeWidgetItem(self.package_tree)
            category_item.setFlags(
                category_item.flags()
                | Qt.ItemFlag.ItemIsUserCheckable
            )
            category_item.setCheckState(0, Qt.CheckState.Unchecked)
            category_font = category_item.font(0)
            category_font.setBold(True)
            category_item.setFont(0, category_font)

            self.category_items[cat_key] = category_item
            self.category_packages[cat_key] = []

            for display_name, pkg_name, source_key, desc_tr, desc_en, recommended in packages:
                package_item = QTreeWidgetItem(category_item)
                package_item.setFlags(package_item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                package_item.setText(0, display_name)
                package_item.setCheckState(
                    0, Qt.CheckState.Checked if recommended else Qt.CheckState.Unchecked
                )
                package_item.setToolTip(0, f"{pkg_name} - {get_text(source_key)}")
                self.package_items[pkg_name] = package_item
                self.package_metadata[pkg_name] = {
                    "name": display_name,
                    "source_key": source_key,
                    "desc_tr": desc_tr,
                    "desc_en": desc_en,
                    "recommended": recommended,
                    "category": cat_key,
                }
                self.category_packages[cat_key].append(pkg_name)

        self.package_tree.blockSignals(False)
        self.package_tree.itemChanged.connect(self._on_tree_item_changed)
        self.package_tree.currentItemChanged.connect(self._update_custom_remove_button)
        self.category_items["extra_cat_browsers"].setExpanded(True)
        self.main_layout.addWidget(self.package_tree, 1)

        custom_layout = QHBoxLayout()
        self.custom_package_input = QLineEdit()
        self.custom_package_input.returnPressed.connect(self._add_custom_package)
        self.custom_add_btn = QPushButton()
        self.custom_add_btn.clicked.connect(self._add_custom_package)
        self.custom_remove_btn = QPushButton()
        self.custom_remove_btn.setEnabled(False)
        self.custom_remove_btn.clicked.connect(self._remove_selected_custom_package)
        custom_layout.addWidget(self.custom_package_input, 1)
        custom_layout.addWidget(self.custom_add_btn)
        custom_layout.addWidget(self.custom_remove_btn)
        self.main_layout.addLayout(custom_layout)

        self.multilib_check = QCheckBox()
        self.multilib_check.setChecked(True)
        self.multilib_check.setStyleSheet(
            "font-size: 12px; color: #D0D0D0; padding: 4px;"
        )
        self.main_layout.addWidget(self.multilib_check)

        nav_layout = QHBoxLayout()
        self.count_label = QLabel()
        self.count_label.setStyleSheet("color: #9E9EA8; font-size: 12px;")
        self.back_btn = QPushButton()
        self.back_btn.clicked.connect(lambda: self.main_window.prev_page())
        self.next_btn = QPushButton()
        self.next_btn.setObjectName("primary_btn")
        self.next_btn.clicked.connect(lambda: self.main_window.next_page())

        nav_layout.addWidget(self.count_label)
        nav_layout.addStretch()
        nav_layout.addWidget(self.back_btn)
        nav_layout.addWidget(self.next_btn)
        self.main_layout.addLayout(nav_layout)

        self.multilib_check.toggled.connect(self._sync_multilib_requirement)
        self.multilib_check.toggled.connect(self._mark_custom)
        self.retranslate()
        self._update_count()

    def _mark_custom(self, *_args):
        if hasattr(self.main_window, 'profile_page'):
            self.main_window.profile_page.mark_custom()

    def apply_profile_packages(self, packages):
        selected = set(packages)
        self.package_tree.blockSignals(True)
        for package, item in self.package_items.items():
            item.setCheckState(0, Qt.CheckState.Checked if package in selected else Qt.CheckState.Unchecked)
        self.package_tree.blockSignals(False)
        self.multilib_check.setChecked(False)
        self._refresh_category_states()
        self._sync_multilib_requirement()
        self._update_count()

    def _is_package_selected(self, package):
        return self.package_items[package].checkState(0) == Qt.CheckState.Checked

    def _set_package_selected(self, package, selected):
        state = Qt.CheckState.Checked if selected else Qt.CheckState.Unchecked
        self.package_items[package].setCheckState(0, state)

    @staticmethod
    def _repository_has_package(package):
        """Check an exact package name against the enabled pacman repositories."""
        try:
            result = subprocess.run(
                ["pacman", "-Si", "--", package],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=10,
                check=False,
            )
            return result.returncode == 0
        except (OSError, subprocess.TimeoutExpired):
            return False

    def _add_custom_package(self):
        package = self.custom_package_input.text().strip().lower()
        if not package:
            return
        if not re.fullmatch(r"[a-z0-9][a-z0-9@._+\-]*", package):
            QMessageBox.warning(
                self, get_text("extra_custom_check_title"), get_text("extra_custom_invalid")
            )
            return

        if package in self.package_items:
            self._set_package_selected(package, True)
            metadata = self.package_metadata[package]
            self.category_items[metadata["category"]].setExpanded(True)
            self.package_tree.setCurrentItem(self.package_items[package])
            self.package_tree.scrollToItem(self.package_items[package])
            self.custom_package_input.clear()
            return

        if not self._repository_has_package(package):
            QMessageBox.warning(
                self,
                get_text("extra_custom_check_title"),
                get_text("extra_custom_not_found").format(package=package),
            )
            return

        cat_key = "extra_cat_custom"
        category_item = self.category_items[cat_key]
        self.package_tree.blockSignals(True)
        package_item = QTreeWidgetItem(category_item)
        package_item.setFlags(package_item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
        package_item.setText(0, package)
        package_item.setCheckState(0, Qt.CheckState.Checked)
        package_item.setToolTip(0, f"{package} - {get_text('extra_source_arch')}")

        self.package_items[package] = package_item
        self.package_metadata[package] = {
            "name": package,
            "source_key": "extra_source_arch",
            "desc_tr": package,
            "desc_en": package,
            "recommended": False,
            "category": cat_key,
        }
        self.category_packages[cat_key].append(package)
        self.custom_packages.add(package)
        self._mark_custom()
        self.package_tree.blockSignals(False)
        self.custom_package_input.clear()
        self._refresh_category_states()
        self._update_count()
        self._apply_filter()
        category_item.setExpanded(True)
        self.package_tree.setCurrentItem(package_item)
        self.package_tree.scrollToItem(package_item)

    def _selected_custom_package(self):
        current = self.package_tree.currentItem()
        if current is None:
            return None
        return next(
            (package for package in self.custom_packages if self.package_items.get(package) is current),
            None,
        )

    def _update_custom_remove_button(self, _current=None, _previous=None):
        self.custom_remove_btn.setEnabled(self._selected_custom_package() is not None)

    def _remove_selected_custom_package(self):
        package = self._selected_custom_package()
        if package is None:
            return
        item = self.package_items.pop(package)
        item.parent().removeChild(item)
        self.package_metadata.pop(package, None)
        self.category_packages["extra_cat_custom"].remove(package)
        self.custom_packages.discard(package)
        self._refresh_category_states()
        self._update_count()
        self._apply_filter()
        self._update_custom_remove_button()

    def unavailable_custom_packages(self):
        """Revalidate custom packages immediately before installation starts."""
        return sorted(
            package for package in self.custom_packages
            if self._is_package_selected(package) and not self._repository_has_package(package)
        )

    def _on_tree_item_changed(self, item, _column):
        self._mark_custom()
        # Checking a category applies its state to every package beneath it.
        if item.parent() is None and item.checkState(0) != Qt.CheckState.PartiallyChecked:
            self.package_tree.blockSignals(True)
            for index in range(item.childCount()):
                if not item.child(index).isDisabled():
                    item.child(index).setCheckState(0, item.checkState(0))
            self.package_tree.blockSignals(False)

        self._refresh_category_states()
        self._sync_multilib_requirement()
        self._update_count()

    def _refresh_category_states(self):
        self.package_tree.blockSignals(True)
        for cat_key, category_item in self.category_items.items():
            packages = self.category_packages[cat_key]
            selected = sum(self._is_package_selected(package) for package in packages)
            if selected == 0:
                state = Qt.CheckState.Unchecked
            elif selected == len(packages):
                state = Qt.CheckState.Checked
            else:
                state = Qt.CheckState.PartiallyChecked
            category_item.setCheckState(0, state)
            category_item.setText(0, f"{get_text(cat_key)}   {selected}/{len(packages)}")
        self.package_tree.blockSignals(False)

    def _sync_multilib_requirement(self, _checked=False):
        steam_selected = self._is_package_selected("steam")
        if steam_selected:
            self.multilib_check.setChecked(True)
        self.multilib_check.setEnabled(not steam_selected)
        key = "extra_multilib_steam" if steam_selected else "extra_multilib"
        self.multilib_check.setText(get_text(key))

    def _apply_filter(self, _value=None):
        query = self.search_input.text().strip().casefold()

        for cat_key, category_item in self.category_items.items():
            category_has_match = False
            for package in self.category_packages[cat_key]:
                metadata = self.package_metadata[package]
                searchable = " ".join((
                    metadata["name"], package, metadata["desc_tr"], metadata["desc_en"],
                    PACKAGE_ES.get(package, ''), self.package_items[package].text(0)
                )).casefold()
                visible = not query or query in searchable
                self.package_items[package].setHidden(not visible)
                category_has_match = category_has_match or visible
            category_item.setHidden(not category_has_match)
            if query and category_has_match:
                category_item.setExpanded(True)

    def _update_count(self, _state=None):
        count = len(self.get_selected_packages())
        total = sum(not package.startswith('component:') for package in self.package_items)
        key = "extra_selected_count_one" if count == 1 else "extra_selected_count"
        self.count_label.setText(get_text(key).format(count=count, total=total))

    def get_selected_packages(self) -> list:
        """Returns list of selected package names."""
        return [package for package in self.package_items
                if not package.startswith('component:') and self._is_package_selected(package)]

    def get_selected_package_names(self) -> list:
        """Returns user-facing names for the installation summary."""
        return [
            self.package_metadata[package]["name"]
            for package in self.get_selected_packages()
        ]

    def is_multilib_enabled(self) -> bool:
        return self.multilib_check.isChecked()

    def retranslate(self):
        self.title_label.setText(get_text("extra_title"))
        self.desc_label.setText(get_text("extra_desc"))
        self.search_input.setPlaceholderText(get_text("extra_search"))
        self.custom_package_input.setPlaceholderText(get_text("extra_custom_placeholder"))
        self.custom_add_btn.setText(get_text("extra_custom_add"))
        self.custom_remove_btn.setText(get_text("extra_custom_remove"))
        self.back_btn.setText(get_text("back"))
        self.next_btn.setText(get_text("next"))
        self.package_tree.blockSignals(True)
        for package, metadata in self.package_metadata.items():
            description = metadata["desc_tr"] if _current_lang == "tr" else metadata["desc_en"]
            if _current_lang == 'es':
                description = PACKAGE_ES.get(package, description)
            item = self.package_items[package]
            if package.startswith('component:'):
                name = package.split(':', 1)[1]
                item.setText(0, get_text('component_' + name))
                description = get_text('component_' + name + '_desc')
            item.setToolTip(
                0, f"{description}\n{package} - {get_text(metadata['source_key'])}"
            )
        self.package_tree.blockSignals(False)
        self._refresh_category_states()
        self._sync_multilib_requirement()
        self._update_count()
        self._apply_filter()


# ─────────────────────────────────────────────
#  Summary Page
# ─────────────────────────────────────────────

class SummaryPage(InstallerPage):
    def __init__(self, parent):
        super().__init__(parent)
        self.main_layout.setContentsMargins(28, 24, 28, 20)
        self.main_layout.setSpacing(12)

        self.title_label = QLabel()
        self.title_label.setStyleSheet("font-size: 28px; color: #eff0f1; font-weight: bold;")
        self.main_layout.addWidget(self.title_label)

        from PyQt6.QtWidgets import QTextBrowser
        self.summary_box = QTextBrowser()
        self.summary_box.setOpenExternalLinks(False)
        self.summary_box.setStyleSheet("""
            QTextBrowser {
                background-color: #141519;
                border: 1px solid #262730;
                border-radius: 8px;
                padding: 16px;
                font-size: 14px;
                color: #FFFFFF;
            }
        """)
        self.summary_box.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.main_layout.addWidget(self.summary_box, 1)

        nav_layout = QHBoxLayout()
        self.back_btn = QPushButton()
        self.back_btn.clicked.connect(lambda: self.main_window.prev_page())

        self.finish_btn = QPushButton()
        self.finish_btn.setStyleSheet("background: #FFFFFF; color: #000000; font-weight: bold; font-size: 15px; border-radius: 6px; padding: 12px 24px;")
        self.finish_btn.clicked.connect(self.start_install_process)

        nav_layout.addWidget(self.back_btn)
        nav_layout.addStretch()
        nav_layout.addWidget(self.finish_btn)
        self.main_layout.addLayout(nav_layout)

        self.retranslate()

    @staticmethod
    def _row(label: str, value: str, value_color: str = "#FFFFFF") -> str:
        """Returns one HTML table row for the summary."""
        return (
            f'<tr>'
            f'<td width="28%" style="padding:7px 18px 7px 0; color:#AAAAAA;"><b>{label}</b></td>'
            f'<td width="72%" style="padding:7px 0; color:{value_color};">{value}</td>'
            f'</tr>'
        )

    @staticmethod
    def _section(heading: str) -> str:
        return (
            f'<tr><td colspan="2" style="padding-top:14px; padding-bottom:2px;">'
            f'<span style="color:#888892; font-size:11px; letter-spacing:1px;">'
            f'{heading.upper()}</span></td></tr>'
        )

    def update_summary(self):
        # Pages are named so adding selection steps cannot redirect installation actions.
        sys_page    = self.main_window.system_page   # SystemConfigPage
        mirror_page = self.main_window.mirror_page   # MirrorConfigPage
        disk_page   = self.main_window.disk_page   # DiskConfigPage
        user_page   = self.main_window.user_page   # UserAccountPage
        extra_page  = self.main_window.extra_page   # ExtraPackagesPage

        disk_sel       = disk_page.disk_combo.currentText()
        mirrors        = ", ".join(mirror_page.get_selected_regions()) or get_text("worldwide")
        kernels_sel = ", ".join(item.text() for item in sys_page.kernel_list.selectedItems()) or "linux"
        bootloader_sel = sys_page.bootloader_combo.currentText()
        greeter_sel    = self.main_window.desktop_page.greeter_combo.currentText()
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

        sec_system = get_text('section_system')
        storage = disk_page.storage_settings()
        home_description = get_text('disk_home_separate').format(filesystem=storage['home_fs']) if storage['separate_home'] else get_text('disk_home_shared')
        sec_disk = get_text('section_disk')
        sec_security = get_text('section_security')
        sec_users = get_text('section_users')
        sec_extras = get_text('section_extras')

        # Build extra packages info
        extra_pkgs = extra_page.get_selected_package_names()
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

        summary_html = f"""
        <table width="100%" cellspacing="0" cellpadding="0">
          {self._section(sec_system)}
          {self._row(get_text('system_language'), dict((locale, name) for name, locale in SYSTEM_LANGUAGES)[sys_page.selected_system_locale()])}
          {self._row(get_text('summary_desktop').replace('<b>','').replace('</b>',''),
                     ", ".join(self.main_window.desktop_page.selected_desktops()))}
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

          {self._row(get_text('summary_root_fs'), storage['root_fs'])}
          {self._row(get_text('summary_home_layout'), home_description)}
          {self._row(get_text('summary_root_space'), str(storage['root_gib']) + ' GiB' if storage['separate_home'] else get_text('disk_root_all'))}

          {self._section(sec_security)}
          {self._row(get_text('summary_root_pw').replace('<b>','').replace('</b>',''),
                     root_pw_status)}

          {self._section(sec_users)}
          {user_rows}

          {self._section(sec_extras)}
          {self._row(get_text('summary_profile'), get_text('profile_' + self.main_window.profile_page.installation_profile()))}
          {self._row(get_text('summary_components'), html.escape(', '.join(self.main_window.profile_page.get_selected_component_names()) or '-'))}
          {self._row(get_text('summary_multilib').replace('<b>','').replace('</b>',''),
                     multilib_status)}
          {self._row(get_text('summary_extra_pkgs').replace('<b>','').replace('</b>',''),
                     f'<span style="color:#3498db;">{extra_pkgs_display}</span>')}
        </table>
        """
        self.summary_box.setHtml(summary_html)

    def start_install_process(self):
        unavailable = self.main_window.extra_page.unavailable_custom_packages()
        if unavailable:
            QMessageBox.warning(
                self,
                get_text("extra_custom_check_title"),
                get_text("extra_custom_recheck_failed").format(
                    packages="\n".join(f"- {package}" for package in unavailable)
                ),
            )
            return

        reply = QMessageBox.question(
            self,
            get_text("confirm_title"),
            get_text("confirm_msg") + "\n\n" + self.main_window.disk_page.disk_combo.currentText(),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            if not self.generate_json():
                return
            self.main_window.next_page()          # Move to install progress page
            self.main_window.install_page.start_installation()

    @staticmethod
    def _build_package_list(sys_page, desktop_names, greeter, extra_packages=None, components=()) -> list:
        """Builds the package list dynamically based on bootloader, DE, and user selections."""
        components = effective_components(components, greeter, sys_page.selected_bootloader())
        base_packages = ['sudo', 'polkit']
        if any(desktop.slug == 'kde-plasma' for desktop in desktops_for(desktop_names)):
            base_packages.append('qt6-translations')
        if 'desktop-theme' in components:
            base_packages.extend(['python', *appearance_packages(desktop_names)])
        if 'plymouth-theme' in components:
            base_packages.append('plymouth')
        if 'sddm-theme' in components:
            base_packages.extend(['qt6-svg', 'qt6-imageformats', 'qt6-5compat',
                                  'qt5-quickcontrols2', 'qt5-graphicaleffects'])

        # Add bootloader-specific packages
        bootloader = sys_page.selected_bootloader()
        if bootloader == "Grub":
            base_packages.extend(["grub", "efibootmgr", "os-prober"])
        elif bootloader == "Refind":
            base_packages.append("refind")
        # Systemd-boot doesn't need extra packages

        if {"Hyprland", "Sway"}.intersection(desktop_names):
            base_packages.append("polkit")
        if greeter == "lightdm-gtk-greeter":
            base_packages.extend(["lightdm", greeter])
        else:
            base_packages.append(greeter)

        # ZelixRepo packages must NOT be passed to archinstall/pacstrap directly,
        # because archinstall only knows official Arch repos. They will be installed
        # post-install after zelixrepo is added to pacman.conf.
        # Add user-selected extra packages (skip flatpak: and zelixrepo packages)
        if extra_packages:
            for pkg in extra_packages:
                if pkg.startswith("flatpak:"):
                    # Flatpak apps will be installed post-install
                    if "flatpak" not in base_packages:
                        base_packages.append("flatpak")
                elif pkg.startswith("aur:"):
                    # AUR packages are installed after archinstall as a regular user.
                    continue
                elif pkg in ZELIX_PACKAGES:
                    # Zelixrepo packages will be installed post-install
                    continue
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
        # Branding is applied only after assets are copied, in zelix_post_install.sh.
        apps = [p.split(":", 1)[1] for p in extra_packages if p.startswith("flatpak:")]
        if not apps:
            return []
        commands = ["flatpak remote-add --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo"]
        for app in apps:
            app_id = {"spotify": "com.spotify.Client"}.get(app, app)
            commands.append(f"flatpak install -y flathub {app_id}")
        return commands

    def generate_json(self):
        """Generates archinstall 4.x-compatible config and creds JSON files."""
        sys_page    = self.main_window.system_page
        mirror_page = self.main_window.mirror_page
        disk_page   = self.main_window.disk_page
        user_page   = self.main_window.user_page
        extra_page  = self.main_window.extra_page

        # --- Extra packages ---
        extra_packages = extra_page.get_selected_packages()
        multilib_enabled = extra_page.is_multilib_enabled()
        components = self.main_window.profile_page.get_selected_components()

        # --- Mirror regions ---
        mirror_dict = mirror_page.get_selected_mirrors()
        if not mirror_dict:
            mirror_dict = {"Worldwide": list(mirror_page.WORLDWIDE_MIRRORS)}

        # --- Disk info ---
        selected_disk_path = disk_page.disk_combo.currentText().split(" ")[0]
        desktop_page = self.main_window.desktop_page
        selected_desktops = desktop_page.selected_desktops()
        total_bytes = get_disk_size_bytes(selected_disk_path)
        storage = disk_page.storage_settings()
        try:
            greeter = desktop_page.selected_greeter()
            if not os.path.exists(selected_disk_path):
                raise ValueError("policy_disk_missing")
            # A mounted target may contain the running/live system or user data.
            result = subprocess.run(
                ["lsblk", "--json", "--output", "TYPE,MOUNTPOINTS", selected_disk_path],
                capture_output=True, text=True, check=True)
            devices = json.loads(result.stdout)["blockdevices"]
            def mounted(device):
                return any(device.get("mountpoints") or []) or any(
                    mounted(child) for child in device.get("children", []))
            if not devices or devices[0]["type"] != "disk" or any(mounted(d) for d in devices):
                raise ValueError("policy_disk_mounted")
            validate_choices(total_bytes, is_uefi(), sys_page.selected_bootloader(),
                             sys_page.selected_kernels(), multilib_enabled, extra_packages)
            partition_list = disk_page.planned_partitions(total_bytes)
        except (ValueError, OSError, subprocess.SubprocessError) as e:
            QMessageBox.critical(self, get_text("config_error"), get_text(str(e)))
            return False

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
                "removable": is_uefi() and sys_page.selected_bootloader() == "Grub",
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
                "sys_lang": sys_page.selected_system_locale(),
            },

            "network_config": {"type": "nm"},

            "ntp": True,
            "packages": self._build_package_list(sys_page, selected_desktops, greeter, extra_packages, components),
            "parallel_downloads": 0,

            "additional_repositories": ["multilib"] if multilib_enabled else [],

            "profile_config": {
                "gfx_driver": None,
                "greeter": greeter,
                "profile": {
                    "main": "Desktop",
                    "details": [desktop.profile for desktop in desktops_for(selected_desktops)],
                    "custom_settings": {desktop.profile: {"seat_access": "systemd-logind"}
                                        for desktop in desktops_for(selected_desktops)
                                        if desktop.slug in {"hyprland", "sway"}},
                },
            },

            "services": [],
            "custom_commands": self._build_custom_commands(multilib_enabled, extra_packages),
            "swap": {"enabled": True, "algorithm": "zstd"},
            "timezone": sys_page.tz_combo.currentText(),
        }

        for partition in partition_list:
            if filesystem_package := FILESYSTEM_PACKAGES.get(partition['fs_type']):
                arch_config['packages'].append(filesystem_package)
        arch_config['packages'] = list(dict.fromkeys(arch_config['packages']))

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

            self.main_window.install_target = {
                "disk": selected_disk_path,
                "storage": storage,
                "root": partition_path(selected_disk_path, 2),
                "boot": partition_path(selected_disk_path, 1),
                "home": partition_path(selected_disk_path, 3) if len(partition_list) == 3 else "-",
                "desktops": [desktop.slug for desktop in desktops_for(selected_desktops)], "greeter": greeter,
                "bootloader": sys_page.selected_bootloader(),
                "multilib": "true" if multilib_enabled else "false",
                "packages": post_install_packages(extra_packages),
                "components": components,
                "installation_type": self.main_window.profile_page.installation_profile(),
            }
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
            QMessageBox.critical(self, get_text("error_title"), get_text("config_failed").format(error=e))
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
            "font-size: 26px; font-weight: bold; color: #FFFFFF; margin-bottom: 10px;"
        )
        self.main_layout.addWidget(self.title_label)

        self.log_console = QPlainTextEdit()
        self.log_console.setReadOnly(True)
        self.log_console.setStyleSheet("""
            background-color: #0A0B0E;
            color: #D8D8E0;
            border: 1px solid #202128;
            font-family: 'Consolas', 'Monospace';
            font-size: 13px;
            padding: 10px;
            border-radius: 6px;
        """)
        self.main_layout.addWidget(self.log_console)

        self.ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')

        self.finish_btn = QPushButton()
        self.finish_btn.setStyleSheet(
            "background: #FFFFFF; color: #000000; font-weight: bold; font-size: 16px; border-radius: 6px; padding: 12px;"
        )
        self.finish_btn.hide()
        self.finish_btn.clicked.connect(lambda: os.system("reboot"))
        self.main_layout.addWidget(self.finish_btn)

        self.process = QProcess(self)
        self.process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.finished.connect(self.process_finished)
        self.process.errorOccurred.connect(self.process_error)
        self.log_path = None
        self.expected_completion = None
        self.completion_received = False
        self._completion_output = ''

        self.retranslate()

    def start_installation(self):
        config_path = getattr(self.main_window, "install_config_path", None)
        creds_path = getattr(self.main_window, "install_creds_path", None)

        if not config_path or not creds_path:
            QMessageBox.critical(self, get_text("error_title"), get_text("config_missing"))
            return

        try:
            with open(config_path, 'rb') as config_stream:
                self.expected_completion = hashlib.file_digest(config_stream, 'sha256').hexdigest()
        except OSError:
            self.install_failed(get_text('config_missing'))
            return

        self.log_console.clear()
        fd, self.log_path = tempfile.mkstemp(prefix="zelix-install-", suffix=".log")
        os.close(fd)
        self.log_console.appendPlainText("Log: " + self.log_path)
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
        # A normal process exit alone cannot prove that post-install ran.
        # Preserve chunk boundaries until the complete per-install receipt arrives.
        self._completion_output = (self._completion_output + clean_text.replace('\r\n', '\n'))[-4096:]
        if self.expected_completion:
            receipt = '\nZELIX_INSTALL_VERIFIED=' + self.expected_completion + '\n'
            if receipt in '\n' + self._completion_output:
                self.completion_received = True
        if self.log_path:
            with open(self.log_path, "a", encoding="utf-8") as log:
                log.write(clean_text)

        if clean_text.strip():
            self.log_console.appendPlainText(clean_text.strip())

        scrollbar = self.log_console.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def process_finished(self, exit_code, exit_status):
        if exit_code != 0 or exit_status != QProcess.ExitStatus.NormalExit:
            self.install_failed(get_text("install_fail_msg").format(code=exit_code))
            return
        # Keep post-install asynchronous so output remains visible and Qt stays responsive.
        self.run_post_install()

    def install_failed(self, message):
        self.title_label.setText(get_text("install_title_fail"))
        self.title_label.setStyleSheet("font-size: 28px; color: #e74c3c;")
        self.log_console.appendPlainText(message)
        self.main_window.cleanup_install_files()
        self.main_window.disk_page.clear_secrets()

    def process_error(self, error):
        if error == QProcess.ProcessError.FailedToStart:
            self.install_failed(get_text("process_failed").format(error=self.process.errorString()))

    def run_post_install(self):
        base = os.path.dirname(os.path.realpath(__file__))
        deps = os.path.join(base, "zelixdeps")
        script = os.path.join(base, "zelix_post_install.sh")
        target = getattr(self.main_window, "install_target", None)
        if not target or not os.path.isdir(deps) or not os.path.isfile(script):
            self.install_failed(get_text("post_missing"))
            return
        try:
            result = subprocess.run(
                # PATH alone does not enable lsblk's children hierarchy.
                ["lsblk", "--json", "--tree", "--paths", "--output", "PATH,TYPE", target["disk"]],
                capture_output=True, text=True, check=True)
            devices = json.loads(result.stdout)["blockdevices"]
            parts = {c["path"] for d in devices for c in d.get("children", []) if c["type"] == "part"}
            expected = {target[k] for k in ("root", "boot", "home") if target[k] != "-"}
            if not expected.issubset(parts):
                raise ValueError(
                    get_text('post_partitions').format(
                        disk=target['disk'], missing=', '.join(sorted(expected - parts)),
                        found=', '.join(sorted(parts)) or '-'))
        except (ValueError, OSError, subprocess.SubprocessError) as e:
            self.install_failed(str(e))
            return
        self.process.finished.disconnect(self.process_finished)
        self.process.finished.connect(self.post_install_finished)
        self.completion_received = False
        self._completion_output = ''
        args = [script, '--config', self.main_window.install_config_path,
                '--creds', self.main_window.install_creds_path, target["root"], target["boot"], target["home"], deps,
                ",".join(target["desktops"]), target["greeter"], target["bootloader"], target["multilib"],
                ",".join(target["components"]) or "-", *target["packages"]]
        self.process.start("/bin/bash" if os.geteuid() == 0 else "pkexec",
                           args if os.geteuid() == 0 else ["/bin/bash", *args])

    def post_install_finished(self, exit_code, exit_status):
        self.handle_stdout()
        if exit_code != 0 or exit_status != QProcess.ExitStatus.NormalExit:
            self.install_failed(get_text("post_failed").format(log=self.log_path))
            return
        if self.completion_received is not True:
            self.install_failed(get_text('post_failed').format(log=self.log_path))
            return
        self.title_label.setText(get_text("install_title_done"))
        self.log_console.appendPlainText(get_text("install_done_msg"))
        self.finish_btn.show()
        self.main_window.cleanup_install_files()
        self.main_window.disk_page.clear_secrets()

    def retranslate(self):
        self.title_label.setText(get_text("install_title_running"))
        self.finish_btn.setText(get_text("reboot_btn"))


# ─────────────────────────────────────────────
#  Main Window
# ─────────────────────────────────────────────

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ZelixOS Installer")
        for icon_candidate in (
            "/usr/share/zelix/zelix-installer.png",
            "/usr/share/pixmaps/zelix-installer.png",
            "/usr/share/zelix/zelix-icon.png",
        ):
            if os.path.exists(icon_candidate):
                self.setWindowIcon(QIcon(icon_candidate))
                break
        self.setMinimumSize(800, 600)
        self.resize(1024, 720)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Right content area
        content_frame = QFrame()
        content_frame.setObjectName("installer_content")
        content_frame.setStyleSheet("QFrame#installer_content { background-color: #121318; }")
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(0, 0, 0, 0)

        self.stacked_widget = QStackedWidget()

        self.pages = [
            WelcomePage(self),
            SystemConfigPage(self),
            DesktopPage(self, get_text, lambda: _current_lang),
            MirrorConfigPage(self),
            DiskConfigPage(self, get_text, scan_disks, get_disk_size_bytes, is_uefi),
            UserAccountPage(self),
            ExtraPackagesPage(self),
            SummaryPage(self),
            InstallProgressPage(self),
        ]
        for name, page in zip(("welcome_page", "system_page", "desktop_page", "mirror_page",
                               "disk_page", "user_page", "extra_page", "summary_page", "install_page"), self.pages):
            setattr(self, name, page)
        self.system_page.kernel_list.itemSelectionChanged.connect(self.disk_page.refresh_layout)
        self.profile_page = InstallationTypePage(self, get_text)
        self.pages.insert(2, self.profile_page)
        for page in self.pages:
            self.stacked_widget.addWidget(page)

        content_layout.addWidget(self.stacked_widget)
        main_layout.addWidget(content_frame, 1)
        self.navigator = BottomNavigation(self, len(self.pages), get_text)
        self.step_labels = self.navigator.step_buttons
        main_layout.addWidget(self.navigator)
        # Keep each page's existing validation/confirmation handlers as the actions.
        for page in self.pages:
            if page is self.install_page:
                continue
            for name in ('back_btn', 'next_btn', 'start_btn', 'finish_btn'):
                button = getattr(page, name, None)
                if button is not None:
                    button.hide()

        self.install_config_path = None
        self.install_creds_path = None

        self.setStyleSheet("""
            QWidget {
                font-family: 'Segoe UI', 'Noto Sans', sans-serif;
                color: #FFFFFF;
            }
            QLineEdit, QComboBox, QListWidget {
                background-color: #17181D;
                border: 1px solid #282932;
                border-radius: 6px;
                padding: 10px;
                font-size: 14px;
                color: #FFFFFF;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 1px solid #FFFFFF;
            }
            QPushButton {
                background-color: #1A1B22;
                color: #FFFFFF;
                border: 1px solid #2C2D38;
                border-radius: 6px;
                padding: 10px 18px;
                font-weight: 600;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #252630;
                border: 1px solid #444654;
                color: #FFFFFF;
            }
            QPushButton:pressed {
                background-color: #FFFFFF;
                color: #000000;
            }
            QPushButton#primary_btn {
                background-color: #FFFFFF;
                color: #000000;
                border: 1px solid #FFFFFF;
                font-weight: bold;
            }
            QPushButton#primary_btn:hover {
                background-color: #E0E0E0;
                border: 1px solid #E0E0E0;
                color: #000000;
            }
            QPushButton#primary_btn:pressed {
                background-color: #CCCCCC;
            }
            QPushButton:disabled {
                background-color: #111215;
                color: #444450;
                border: 1px solid #1C1D24;
            }
            QPushButton#primary_btn:disabled {
                background-color: #1E1F26;
                color: #555565;
                border: 1px solid #2A2B35;
            }
        """)

        self.retranslate_all()
        self.footer_timer = QTimer(self)
        self.footer_timer.timeout.connect(self.sync_footer)
        self.footer_timer.start(250)

    def forward_control(self):
        page = self.stacked_widget.currentWidget()
        if page is self.install_page:
            return None
        if page is self.welcome_page:
            return page.start_btn
        if page is self.summary_page:
            return page.finish_btn
        return page.next_btn

    def continue_from_footer(self):
        button = self.forward_control()
        if button is not None and button.isEnabled():
            button.click()
        self.sync_footer()

    def go_back_from_footer(self):
        if self.stacked_widget.currentWidget() is not self.install_page:
            self.prev_page()

    def sync_footer(self):
        self.navigator.sync(self.stacked_widget.currentIndex(), self.pages.index(self.install_page), self.forward_control())

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
        progress = self.install_page
        if progress.process.state() != QProcess.ProcessState.NotRunning:
            QMessageBox.warning(self, get_text("step_10"), get_text("still_running"))
            event.ignore()
            return
        self.cleanup_install_files()
        self.disk_page.clear_secrets()
        event.accept()

    def retranslate_all(self):
        """Re-applies all translatable strings to every page and sidebar."""
        self.navigator.retranslate()

        for page in self.pages:
            page.retranslate()

        self.update_sidebar()

    def next_page(self):
        idx = self.stacked_widget.currentIndex()
        self.go_to_page(idx + 1, allow_install_page=True)

    def go_to_page(self, target_index, allow_install_page=False):
        """Navigate to a setup page while preserving installer safety checks."""
        current_index = self.stacked_widget.currentIndex()
        install_index = self.pages.index(self.install_page)

        if not 0 <= target_index < len(self.pages):
            return False

        # Installation is intentionally one-way once the process page opens.
        if current_index == install_index and target_index != install_index:
            return False

        # The progress page may only be opened by SummaryPage after the user
        # confirms the destructive disk operation.
        if target_index == install_index and not allow_install_page:
            return False

        # Keep the desktop/greeter compatibility validation when skipping
        # forward via either the Next button or the clickable sidebar.
        if current_index == self.pages.index(self.desktop_page) and target_index > current_index:
            try:
                self.desktop_page.selected_greeter()
            except ValueError as error:
                QMessageBox.warning(self, get_text("greeter"), get_text(str(error)))
                return False

        if current_index == self.pages.index(self.disk_page) and target_index > current_index:
            if not self.disk_page.validate_settings():
                return False

        self.profile_page.refresh_compatibility()

        if self.pages[target_index] is self.summary_page:
            self.summary_page.update_summary()

        self.stacked_widget.setCurrentIndex(target_index)
        self.update_sidebar()
        return True

    def prev_page(self):
        idx = self.stacked_widget.currentIndex()
        self.go_to_page(idx - 1)

    def update_sidebar(self):
        # Retained as the shared page-change hook used by existing navigation.
        self.sync_footer()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setDesktopFileName("zelix-installer")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
