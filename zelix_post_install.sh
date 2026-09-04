#!/bin/bash
set -x

ROOT_PART=$1
DEPS_PATH=$2

if [ -z "$ROOT_PART" ] || [ -z "$DEPS_PATH" ]; then
    echo "Hata: Hedef disk veya deps klasörü belirtilmedi!"
    exit 1
fi

echo "Hedef Disk: $ROOT_PART dizinine bağlanılıyor..."
mkdir -p /mnt/zelix_target
mount "$ROOT_PART" /mnt/zelix_target

# BTRFS @ alt hacmi kontrolü
if [ -d "/mnt/zelix_target/@/etc" ]; then
    echo "BTRFS @ alt hacmi algılandı, kök bağlanıyor..."
    umount /mnt/zelix_target
    mount -o subvol=@ "$ROOT_PART" /mnt/zelix_target
fi

echo "ZelixOS Aurora özel dosyaları (duvar kağıtları, ikonlar, temalar) kopyalanıyor..."
cp -ar "$DEPS_PATH"/* /mnt/zelix_target/

# 1. İşletim sistemi kimliği (os-release)
cat << 'OS_EOF' > /mnt/zelix_target/etc/os-release
NAME="ZelixOS"
PRETTY_NAME="ZelixOS Aurora"
ID=zelixos
ID_LIKE=arch
BUILD_ID=rolling
ANSI_COLOR="0;34"
HOME_URL="https://zelixos.com"
DOCUMENTATION_URL="https://docs.zelixos.com"
SUPPORT_URL="https://zelixos.com"
BUG_REPORT_URL="https://zelixos.com/br.html"
LOGO=/usr/share/zelix/zelix-icon.png
OS_EOF

echo -e "\e[1;34mZelixOS Aurora\e[0m \r (\l)\n" > /mnt/zelix_target/etc/issue
cat << 'LSB_EOF' > /mnt/zelix_target/etc/lsb-release
LSB_VERSION=1.4
DISTRIB_ID=ZelixOS
DISTRIB_RELEASE=rolling
DISTRIB_DESCRIPTION="ZelixOS Aurora"
LSB_EOF

# 2. Archiso kalıntılarını temizle
rm -f /mnt/zelix_target/etc/mkinitcpio.conf.d/archiso.conf /mnt/zelix_target/etc/mkinitcpio.conf.d/archiso* 2>/dev/null || true

# 3. mkinitcpio & Plymouth
cat << 'MKC_EOF' > /mnt/zelix_target/etc/mkinitcpio.conf
MODULES=()
BINARIES=()
FILES=()
HOOKS=(base udev plymouth autodetect modconf kms keyboard keymap consolefont block filesystems fsck)
COMPRESSION="zstd"
MKC_EOF

mkdir -p /mnt/zelix_target/etc/plymouth
cat << 'PLY_EOF' > /mnt/zelix_target/etc/plymouth/plymouthd.conf
[Daemon]
Theme=zelix-aurora
ShowDelay=0
DeviceTimeout=8
PLY_EOF

if command -v arch-chroot &>/dev/null; then
    arch-chroot /mnt/zelix_target plymouth-set-default-theme -R zelix-aurora 2>/dev/null || arch-chroot /mnt/zelix_target mkinitcpio -P 2>/dev/null || true
fi

# 4. GRUB Yapılandırması ve Teması
mkdir -p /mnt/zelix_target/boot/grub/themes/zelix-aurora /mnt/zelix_target/usr/share/grub/themes/zelix-aurora
cp -r /mnt/zelix_target/usr/share/grub/themes/zelix-aurora/* /mnt/zelix_target/boot/grub/themes/zelix-aurora/ 2>/dev/null || true

if [ -f "/mnt/zelix_target/etc/default/grub" ]; then
    sed -i 's/GRUB_DISTRIBUTOR="Arch"/GRUB_DISTRIBUTOR="ZelixOS"/g' /mnt/zelix_target/etc/default/grub
    sed -i 's|^#*GRUB_THEME=.*|GRUB_THEME="/usr/share/grub/themes/zelix-aurora/theme.txt"|' /mnt/zelix_target/etc/default/grub
    grep -q "GRUB_THEME" /mnt/zelix_target/etc/default/grub || echo 'GRUB_THEME="/usr/share/grub/themes/zelix-aurora/theme.txt"' >> /mnt/zelix_target/etc/default/grub
    sed -i 's/GRUB_CMDLINE_LINUX_DEFAULT=".*"/GRUB_CMDLINE_LINUX_DEFAULT="quiet splash loglevel=3"/' /mnt/zelix_target/etc/default/grub
    sed -i 's/GRUB_TERMINAL_OUTPUT=".*"/GRUB_TERMINAL_OUTPUT="gfxterm"/' /mnt/zelix_target/etc/default/grub
    grep -q "GRUB_TERMINAL_OUTPUT" /mnt/zelix_target/etc/default/grub || echo 'GRUB_TERMINAL_OUTPUT="gfxterm"' >> /mnt/zelix_target/etc/default/grub
    
    if command -v arch-chroot &>/dev/null; then
        arch-chroot /mnt/zelix_target grub-mkconfig -o /boot/grub/grub.cfg 2>/dev/null || true
    fi
fi

# 5. SDDM Yapılandırması
mkdir -p /mnt/zelix_target/etc/sddm.conf.d
cat << 'SDDM_EOF' > /mnt/zelix_target/etc/sddm.conf
[Theme]
Current=zelix-aurora
CursorTheme=breeze_cursors
SDDM_EOF

cat << 'SDDM_EOF2' > /mnt/zelix_target/etc/sddm.conf.d/zelix.conf
[Theme]
Current=zelix-aurora
CursorTheme=breeze_cursors
SDDM_EOF2

cat << 'SDDM_EOF3' > /mnt/zelix_target/etc/sddm.conf.d/kde_settings.conf
[Theme]
Current=zelix-aurora
CursorTheme=breeze_cursors
SDDM_EOF3

if command -v arch-chroot &>/dev/null; then
    arch-chroot /mnt/zelix_target systemctl enable sddm 2>/dev/null || true
    arch-chroot /mnt/zelix_target systemctl set-default graphical.target 2>/dev/null || true
fi

# 6. KDE Koyu Mavi Tema & Duvar Kağıdının Kullanıcılara Uygulanması
chmod 644 /mnt/zelix_target/etc/skel/.config/* 2>/dev/null || true
for user_home in /mnt/zelix_target/home/*; do
    if [ -d "$user_home" ]; then
        user_name=$(basename "$user_home")
        mkdir -p "$user_home/.config"
        cp -rn /mnt/zelix_target/etc/skel/.config/* "$user_home/.config/" 2>/dev/null || true
        cp -f /mnt/zelix_target/etc/skel/.config/kdeglobals "$user_home/.config/kdeglobals" 2>/dev/null || true
        arch-chroot /mnt/zelix_target chown -R "$user_name:$user_name" "/home/$user_name" 2>/dev/null || true
    fi
done

# 7. Pacman Repoları (multilib & zelixrepo)
if [ -f "/mnt/zelix_target/etc/pacman.conf" ]; then
    sed -i '/\[multilib\]/,/Include/ s/^#//' /mnt/zelix_target/etc/pacman.conf
    if ! grep -q "\[zelixrepo\]" /mnt/zelix_target/etc/pacman.conf; then
        cat << 'PAC_EOF' >> /mnt/zelix_target/etc/pacman.conf

[zelixrepo]
SigLevel = Optional TrustAll
Server = https://raw.githubusercontent.com/ZelixOS/zelix-repo/main/x86_64
PAC_EOF
    fi
fi

echo "Sistem temizleniyor ve disk ayrılıyor..."
sync
umount /mnt/zelix_target 2>/dev/null || true
echo "ZelixOS Aurora yapılandırması başarıyla tamamlandı!"
