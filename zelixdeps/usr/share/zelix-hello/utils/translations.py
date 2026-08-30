import os

translations = {
    "Turkish": {
        "welcome_title": "ZelixOS'e Hoşgeldiniz!",
        "welcome_subtitle": "Topluluğumuza katıldığınız için teşekkür ederiz!\n\nBiz ZelixOS geliştiricileri olarak, sistemi inşa ederken aldığımız keyfi sizin de kullanırken almanızı umuyoruz.\nAşağıdaki bağlantılar yeni işletim sisteminize alışmanıza yardımcı olacaktır.\nDeneyimin tadını çıkarın ve geri bildirim göndermekten çekinmeyin.",
        "doc_header": "DOKÜMANTASYON",
        "support_header": "DESTEK",
        "project_header": "PROJE",
        "btn_readme": "Beni Oku",
        "btn_release_info": "Sürüm Notları",
        "btn_wiki": "Wiki",
        "btn_forum": "Forum",
        "btn_software": "Yazılımlar",
        "btn_system": "Sistem / Ayarlar",
        "btn_get_involved": "Katkıda Bulun",
        "btn_development": "Geliştirme",
        "btn_donate": "Bağış Yap",
        "btn_shortcuts": "Klavye Kısayolları Rehberi",
        "lbl_launch_start": "Başlangıçta çalıştır",
        "btn_back": "<- Geri (Ana Ekran)",
        "apps_title": "Yazılım Kurulumu",
        "btn_install": "Kur",
        "btn_install_all": "Tümünü Kur",
        "sys_title": "Sistem ve Güncellemeler",
        "sys_maintenance": "Sistem Bakımı",
        "sys_update": "Sistemi Güncelle (pacman -Syu)",
        "sys_updater_gui": "Grafiksel Güncelleyiciyi Aç (zelix-updater)",
        "sys_clear_cache": "Paket Önbelleğini Temizle (pacman -Sc)",
        "sys_remove_orphans": "Gereksiz (Orphan) Paketleri Sil",
        "sys_optimize_mirrors": "Yansımaları Optimize Et (rate-mirrors)",
        "sys_enable_flathub": "Flathub Deposunu Etkinleştir (Flatpak)",
        "terminal_label": "Terminal Çıktısı:",
        "tw_title": "İnce Ayarlar (Tweaks)",
        "tw_subtitle": "Sistem servislerini ve ayarlarını buradan yönetebilirsiniz.",
        "tw_services": "Servis Yönetimi",
        "tw_bt": "Bluetooth Servisi (bluetooth.service)",
        "tw_fw": "Güvenlik Duvarı (ufw.service)",
        "tw_enable": "Etkinleştir",
        "tw_disable": "Devre Dışı Bırak",
        "cat_gaming": "Oyun",
        "cat_office": "Ofis",
        "cat_editing": "Düzenleme & Medya",
        "cat_browsers": "Tarayıcılar & İletişim",
        "cat_devtools": "Geliştirme & Araçlar",
        "toggle_on": "AÇIK",
        "toggle_off": "KAPALI",
        "confirm_title": "Onay",
        "confirm_update": "Sistemi güncellemek istediğinize emin misiniz?",
        "no_orphans": "Gereksiz paket bulunamadı.",
        "status_running": "Çalışıyor...",
        "msg_success": "İşlem Başarılı",
        "msg_error": "Hata Oluştu",
        "msg_unsupported_term": "Desteklenen bir terminal bulunamadı (alacritty, konsole vb.)",
        "msg_term_fail": "Terminal açılamadı:",
        "shortcuts_title": "ZelixOS Klavye Kısayolları",
        "shortcuts_desc": "Masaüstünde en sık kullanılan kısayollar:",
        "sc_app_launcher": "Uygulama Başlatıcı Menüsü",
        "sc_krunner": "Hızlı Arama & Komut (KRunner)",
        "sc_terminal": "Terminal (Konsole)",
        "sc_file_manager": "Dosya Yöneticisi (Dolphin)",
        "sc_screenshot": "Ekran Görüntüsü (Spectacle)",
        "sc_window_tiling": "Pencere Konumlandırma (Tiling)",
        "sc_lock_logout": "Çıkış / Güç Menüsü",
        "flathub_success": "Flathub deposu başarıyla etkinleştirildi!",
        "btn_close": "Kapat"
    },
    "English": {
        "welcome_title": "Welcome to ZelixOS!",
        "welcome_subtitle": "Thank you for joining our community!\n\nWe, the ZelixOS Developers, hope that you will enjoy using ZelixOS as much as we enjoy building it.\nThe links below will help you get started with your new operating system.\nSo enjoy the experience, and don't hesitate to send us your feedback.",
        "doc_header": "DOCUMENTATION",
        "support_header": "SUPPORT",
        "project_header": "PROJECT",
        "btn_readme": "Read me",
        "btn_release_info": "Release info",
        "btn_wiki": "Wiki",
        "btn_forum": "Forum",
        "btn_software": "Software",
        "btn_system": "System / Tweaks",
        "btn_get_involved": "Get involved",
        "btn_development": "Development",
        "btn_donate": "Donate",
        "btn_shortcuts": "Keyboard Shortcuts Guide",
        "lbl_launch_start": "Launch at start",
        "btn_back": "<- Back (Dashboard)",
        "apps_title": "Software Installation",
        "btn_install": "Install",
        "btn_install_all": "Install All",
        "sys_title": "System and Updates",
        "sys_maintenance": "System Maintenance",
        "sys_update": "Update System (pacman -Syu)",
        "sys_updater_gui": "Open Graphical Updater (zelix-updater)",
        "sys_clear_cache": "Clear Package Cache (pacman -Sc)",
        "sys_remove_orphans": "Remove Orphan Packages",
        "sys_optimize_mirrors": "Optimize Mirrors (rate-mirrors)",
        "sys_enable_flathub": "Enable Flathub Repository (Flatpak)",
        "terminal_label": "Terminal Output:",
        "tw_title": "System Tweaks",
        "tw_subtitle": "Manage system services and settings here.",
        "tw_services": "Service Management",
        "tw_bt": "Bluetooth Service (bluetooth.service)",
        "tw_fw": "Firewall (ufw.service)",
        "tw_enable": "Enable",
        "tw_disable": "Disable",
        "cat_gaming": "Gaming",
        "cat_office": "Office",
        "cat_editing": "Editing & Media",
        "cat_browsers": "Browsers & Communication",
        "cat_devtools": "Development & Tools",
        "toggle_on": "ON",
        "toggle_off": "OFF",
        "confirm_title": "Confirm",
        "confirm_update": "Are you sure you want to update the system?",
        "no_orphans": "No orphan packages found.",
        "status_running": "Running...",
        "msg_success": "Success",
        "msg_error": "Error",
        "msg_unsupported_term": "No supported terminal found (alacritty, konsole etc.)",
        "msg_term_fail": "Failed to launch terminal:",
        "shortcuts_title": "ZelixOS Keyboard Shortcuts",
        "shortcuts_desc": "Most frequently used desktop shortcuts:",
        "sc_app_launcher": "Application Launcher Menu",
        "sc_krunner": "Quick Search & Command (KRunner)",
        "sc_terminal": "Terminal (Konsole)",
        "sc_file_manager": "File Manager (Dolphin)",
        "sc_screenshot": "Screenshot (Spectacle)",
        "sc_window_tiling": "Window Tiling",
        "sc_lock_logout": "Logout / Power Menu",
        "flathub_success": "Flathub repository enabled successfully!",
        "btn_close": "Close"
    }
}

def detect_system_language():
    for var in ["LANG", "LC_ALL", "LC_MESSAGES"]:
        val = os.environ.get(var, "").lower()
        if val.startswith("tr"):
            return "Turkish"
    return "English"

class Translator:
    _current_lang = detect_system_language()
    _listeners = []

    @classmethod
    def set_language(cls, lang):
        if lang in translations:
            cls._current_lang = lang
            cls.notify()

    @classmethod
    def get_language(cls):
        return cls._current_lang

    @classmethod
    def get(cls, key):
        return translations[cls._current_lang].get(key, key)

    @classmethod
    def add_listener(cls, listener):
        cls._listeners.append(listener)

    @classmethod
    def notify(cls):
        for listener in cls._listeners:
            if hasattr(listener, 'retranslate_ui'):
                listener.retranslate_ui()
