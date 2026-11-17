# Zelixins

ZelixOS için Python ve PyQt6 ile yazılmış grafik kurucu. Sistem kurulumu için Archinstall kullanır; kullanıcı, disk, çekirdek, masaüstü ve önyükleyici seçimlerini tek arayüzde toplar.

## Özellikler

- Türkçe ve İngilizce arayüz.
- KDE Plasma, GNOME, Xfce, Hyprland, Sway, i3 ve bspwm seçenekleri.
- Uyumlu giriş yöneticisi seçimi.
- Çekirdek, önyükleyici ve ek yazılım seçimi.
- Kurulum çıktısının arayüzde izlenmesi.
- Kurulum sonrasında ZelixOS ayarlarının ve uygulama paketlerinin uygulanması.

## Çalıştırma

Kurucu, ZelixOS canlı oturumunda kullanılmak üzere hazırlanmıştır:

```bash
zelix-installer
```

Kaynak dizininden arayüzü başlatmak için:

```bash
python myself.py
```

Python, `python-pyqt6`, `qt6-imageformats`, `archinstall`, `arch-install-scripts`, `polkit` ve `util-linux` gereklidir. Kurulum işlemleri yönetici yetkisi ister.

## Disk işlemleri

Kurucu seçilen diski silerek kurulum yapar. Mevcut verileri önceden yedekleyin. Manuel bölümleme sunmaz. Disk, BIOS/UEFI ve yeniden başlatma kontrollerini önce sanal makinede yapın.

## Kaynak düzeni

| Dosya veya dizin | Görevi |
| --- | --- |
| `myself.py` | Kurulum akışı ve arayüz |
| `installer_support.py` | Disk ve yapılandırma yardımcıları |
| `desktop_*.py` | Masaüstü seçenekleri ve görünüm ayarları |
| `zelix_post_install.sh` | Kurulum sonrası işlemler |
| `zelixdeps/` | Ortak ayar ve görünüm dosyaları |
| `backgrounds/`, `previews/`, `icons/` | Arayüz varlıkları |

Paket tarifi [zelix-repo](https://github.com/ZelixOS/zelix-repo/tree/main/zelixins) deposundadır.
