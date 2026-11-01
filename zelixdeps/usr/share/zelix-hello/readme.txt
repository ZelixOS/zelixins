======================================================================
                     ZelixOS'e Hoş Geldiniz!
======================================================================

ZelixOS, modern, kararlı ve kullanıcı dostu bir Arch Linux tabanlı
işletim sistemidir. Sisteminizden en iyi şekilde yararlanabilmeniz için
bazı temel bilgileri aşağıda bulabilirsiniz.

1. Paket Yönetimi & AUR (Arch User Repository)
----------------------------------------------------------------------
ZelixOS, paket yöneticisi olarak 'pacman' kullanır.
Ayrıca 'yay' ve 'paru' gibi popüler AUR yardımcılarını "Zelix Hello"
üzerinden tek tıkla kurabilir veya terminalde kullanabilirsiniz.

* Sistem güncellemesi yapmak için:
  sudo pacman -Syu  (veya AUR ile: yay -Syu / paru -Syu)

* Yeni bir paket/yazılım kurmak için:
  sudo pacman -S paket_adi  (veya AUR ile: yay -S paket_adi)

* Bir paketi ve bağımlılıklarını kaldırmak için:
  sudo pacman -Rns paket_adi

* Sistemdeki gereksiz (orphan) paketleri temizlemek için:
  pacman -Qdtq | sudo pacman -Rns -
  
* Ya da doğrudan "Zelix Hello" ve "Zelix Updater" üzerinden terminal
  açmaya gerek kalmadan tüm bu işlemleri gerçekleştirebilirsiniz!

2. Masaüstü Kısayolları ve Kontroller
----------------------------------------------------------------------
NOT: Super klavyenizdeki Windows tuşudur.
* Terminali Açmak: Ctrl + Alt + T
* Uygulama Menüsü: Super
* Hızlı Arama & Komut (KRunner): Alt + Space / Alt + F2
* Dosya Yöneticisi (Dolphin): Super + E
* Ekran Görüntüsü (Spectacle): PrintScreen
* Pencereleri Hizalama: Super + Sol / Sağ / Yukarı
* Sistemden Çıkış / Kapatma: Ctrl + Alt + Del

3. Önemli Bağlantılar ve Yardım
----------------------------------------------------------------------
* Resmi Web Sitesi: https://zelixos.com
* Sürüm Notları: https://zelixos.com/release-aurora.html
* Wiki & Dokümantasyon: https://docs.zelixos.com
* GitHub Sayfası: https://github.com/ZelixOS
* Telegram Topluluğu: https://t.me/zelixos
* Discord Sunucusu: https://discord.gg/zelixos

Keyifli kullanımlar dileriz!
- Muhammed Yasir Peker & ZelixOS Ekibi

======================================================================
                      Welcome to ZelixOS!
======================================================================

ZelixOS is a modern, reliable, and user-friendly operating system
based on Arch Linux. Below you will find essential information to
help you get the most out of your new operating system.

1. Package Management & AUR (Arch User Repository)
----------------------------------------------------------------------
ZelixOS uses 'pacman' as its primary package manager.
You can also install popular AUR helpers like 'yay' and 'paru'
with a single click via "Zelix Hello" or use them in terminal.

* To update the system:
  sudo pacman -Syu  (or with AUR: yay -Syu / paru -Syu)

* To install a new package/software:
  sudo pacman -S package_name  (or with AUR: yay -S package_name)

* To remove a package and its unused dependencies:
  sudo pacman -Rns package_name

* To clean orphan packages and package cache:
  zelix clean   (or pacman -Qdtq | sudo pacman -Rns -)

* Or you can perform all these actions easily with the graphical
  "Zelix Hello" and "Zelix Updater" tools without touching the terminal!

2. Desktop Shortcuts & Controls
----------------------------------------------------------------------
NOTE: 'Super' refers to the Windows key on your keyboard.
* Open Terminal: Ctrl + Alt + T
* Application Menu: Super
* Quick Runner & Search (KRunner): Alt + Space / Alt + F2
* File Manager (Dolphin): Super + E
* Take Screenshot (Spectacle): PrintScreen
* Window Tiling: Super + Left / Right / Up
* System Logout / Power Menu: Ctrl + Alt + Del

3. Important Links & Support
----------------------------------------------------------------------
* Official Website: https://zelixos.com
* Release Notes: https://zelixos.com/release-aurora.html
* Wiki & Documentation: https://docs.zelixos.com
* GitHub Organization: https://github.com/ZelixOS
* Telegram Community: https://t.me/zelixos
* Discord Server: https://discord.gg/zelixos

We hope you enjoy your experience with ZelixOS!
- Muhammed Yasir Peker & The ZelixOS Team
======================================================================
