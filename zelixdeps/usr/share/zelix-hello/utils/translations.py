translations = {
    "Turkish": {
        "welcome_title": "ZelixOS'e Hoşgeldiniz!",
        "welcome_subtitle": "Topluluğumuza katıldığınız için teşekkür ederiz!\n\nBiz ZelixOS geliştiricileri olarak, sistemi inşa ederken aldığımız keyfi sizin de kullanırken almanızı umuyoruz.\nAşağıdaki bağlantılar yeni işletim sisteminize alışmanıza yardımcı olacaktır.\nDeneyimin tadını çıkarın ve geri bildirim göndermekten çekinmeyin.",
        "doc_header": "DOKÜMANTASYON",
        "support_header": "DESTEK",
        "project_header": "PROJE",
        "install_header": "KURULUM",
        "btn_readme": "Beni Oku",
        "btn_release_info": "Sürüm Notları",
        "btn_wiki": "Wiki",
        "btn_forum": "Forum",
        "btn_software": "Yazılımlar",
        "btn_system": "Sistem / Ayarlar",
        "btn_get_involved": "Katkıda Bulun",
        "btn_development": "Geliştirme",
        "btn_donate": "Bağış Yap",
        "btn_launch_installer": "Yükleyiciyi Başlat",
        "lbl_launch_start": "Başlangıçta çalıştır",
        "btn_back": "<- Geri (Ana Ekran)",
        "apps_title": "Yazılım Kurulumu",
        "btn_install": "Kur",
        "btn_install_all": "Tümünü Kur",
        "sys_title": "Sistem ve Güncellemeler",
        "sys_update": "Sistemi Güncelle (pacman -Syu)",
        "sys_clear_cache": "Paket Önbelleğini Temizle (pacman -Sc)",
        "sys_remove_orphans": "Gereksiz (Orphan) Paketleri Sil",
        "tw_title": "İnce Ayarlar (Tweaks)",
        "tw_subtitle": "Sistem servislerini ve ayarlarını buradan yönetebilirsiniz.",
        "tw_services": "Servis Yönetimi",
        "tw_bt": "Bluetooth Servisi (bluetooth.service)",
        "tw_fw": "Güvenlik Duvarı (ufw.service)",
        "tw_enable": "Etkinleştir",
        "tw_disable": "Devre Dışı Bırak",
        "msg_success": "Başarılı",
        "msg_error": "Hata",
        "msg_unsupported_term": "Desteklenen bir terminal bulunamadı (alacritty, konsole vb.)",
        "msg_term_fail": "Terminal açılamadı:"
    },
    "English": {
        "welcome_title": "Welcome to ZelixOS!",
        "welcome_subtitle": "Thank you for joining our community!\n\nWe, the ZelixOS Developers, hope that you will enjoy using ZelixOS as much as we enjoy building it.\nThe links below will help you get started with your new operating system.\nSo enjoy the experience, and don't hesitate to send us your feedback.",
        "doc_header": "DOCUMENTATION",
        "support_header": "SUPPORT",
        "project_header": "PROJECT",
        "install_header": "INSTALLATION",
        "btn_readme": "Read me",
        "btn_release_info": "Release info",
        "btn_wiki": "Wiki",
        "btn_forum": "Forum",
        "btn_software": "Software",
        "btn_system": "System / Tweaks",
        "btn_get_involved": "Get involved",
        "btn_development": "Development",
        "btn_donate": "Donate",
        "btn_launch_installer": "Launch installer",
        "lbl_launch_start": "Launch at start",
        "btn_back": "<- Back (Dashboard)",
        "apps_title": "Software Installation",
        "btn_install": "Install",
        "btn_install_all": "Install All",
        "sys_title": "System and Updates",
        "sys_update": "Update System (pacman -Syu)",
        "sys_clear_cache": "Clear Package Cache (pacman -Sc)",
        "sys_remove_orphans": "Remove Orphan Packages",
        "tw_title": "System Tweaks",
        "tw_subtitle": "Manage system services and settings here.",
        "tw_services": "Service Management",
        "tw_bt": "Bluetooth Service (bluetooth.service)",
        "tw_fw": "Firewall (ufw.service)",
        "tw_enable": "Enable",
        "tw_disable": "Disable",
        "msg_success": "Success",
        "msg_error": "Error",
        "msg_unsupported_term": "No supported terminal found (alacritty, konsole etc.)",
        "msg_term_fail": "Failed to launch terminal:"
    }
}

class Translator:
    _current_lang = "Turkish"
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
