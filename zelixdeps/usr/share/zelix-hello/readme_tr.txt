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

ZelixOS deneyiminizi kişiselleştirmek için "Zelix Hello" uygulaması
üzerindeki sekmeleri kullanmaya devam edebilirsiniz.

Keyifli kullanımlar dileriz!
- Muhammed Yasir Peker & ZelixOS Ekibi
======================================================================
