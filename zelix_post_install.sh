#!/bin/bash

# Python'dan gelecek olan parametreleri alıyoruz
ROOT_PART=$1
DEPS_PATH=$2

if [ -z "$ROOT_PART" ] || [ -z "$DEPS_PATH" ]; then
    echo "Hata: Hedef disk veya deps klasörü belirtilmedi!"
    exit 1
fi

echo "Hedef Disk: $ROOT_PART dizinine bağlanılıyor..."
mkdir -p /mnt/zelix_target
mount "$ROOT_PART" /mnt/zelix_target

echo "ZelixOS Aurora özel dosyaları (duvar kağıtları, ikonlar vb.) kopyalanıyor..."
# Bu komut zelixdeps hiyerarşisini hedef sisteme birebir aktarır
cp -ar "$DEPS_PATH"/* /mnt/zelix_target/

# =================================================================
# ZELIX OS KİMLİK (IDENTITY) ENJEKSİYONU
# =================================================================
echo "İşletim sistemi kimliği (os-release) oluşturuluyor..."

# 1. /etc/os-release dosyasını tamamen ZelixOS olarak eziyoruz
cat <<EOF > /mnt/zelix_target/etc/os-release
NAME="ZelixOS"
PRETTY_NAME="ZelixOS Aurora"
ID=zelixos
ID_LIKE=arch
BUILD_ID=rolling
ANSI_COLOR="0;34"
HOME_URL="https://lanierc.github.io/zelixos"
DOCUMENTATION_URL="https://lanierc.github.io/zelixos/wiki.html"
SUPPORT_URL="https://lanierc.github.io/zelixos"
BUG_REPORT_URL="https://lanierc.github.io/zelixos/br.html"
LOGO=/usr/share/zelix/zelix-icon.png
EOF

# 2. /etc/issue (TTY terminali açıldığında üstte yazan Hoş Geldiniz yazısı)
echo -e "\e[1;35mZelixOS Linux\e[0m \r (\l)\n" > /mnt/zelix_target/etc/issue

# 3. LSB Release uyumluluğu
cat <<EOF > /mnt/zelix_target/etc/lsb-release
LSB_VERSION=1.4
DISTRIB_ID=ZelixOS 
DISTRIB_RELEASE=rolling
DISTRIB_DESCRIPTION="ZelixOS Aurora"
EOF

# 4. SDDM, Plymouth ve GRUB Yapılandırmalarını Uygula
echo "Görsel temalar (SDDM, Plymouth, GRUB) uygulanıyor..."
if command -v arch-chroot &>/dev/null; then
    # Enable SDDM
    arch-chroot /mnt/zelix_target systemctl enable sddm 2>/dev/null || true
    # Build Plymouth initramfs
    arch-chroot /mnt/zelix_target plymouth-set-default-theme -R zelix-aurora 2>/dev/null || arch-chroot /mnt/zelix_target mkinitcpio -P 2>/dev/null || true
    # Generate GRUB config
    if [ -f "/mnt/zelix_target/boot/grub/grub.cfg" ] || [ -d "/mnt/zelix_target/boot/grub" ]; then
        arch-chroot /mnt/zelix_target grub-mkconfig -o /boot/grub/grub.cfg 2>/dev/null || true
    fi
fi

# İşlemler tamam, diski ayır
echo "Sistem temizleniyor ve disk ayrılıyor..."
sync
umount /mnt/zelix_target 2>/dev/null || true
echo "ZelixOS Aurora yapılandırması başarıyla tamamlandı!"