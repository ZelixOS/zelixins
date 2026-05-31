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

# İşlemler tamam, diski ayır
echo "Sistem temizleniyor ve disk ayrılıyor..."
umount /mnt/zelix_target
echo "ZelixOS Aurora yapılandırması başarıyla tamamlandı!"