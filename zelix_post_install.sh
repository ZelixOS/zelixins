#!/bin/bash
# Called only after archinstall succeeds. Arguments are passed as an argv list.
set -Eeuo pipefail
if (( $# < 8 )); then
    echo 'Usage: postinstall ROOT BOOT HOME_OR_DASH DEPS DESKTOPS_CSV GREETER BOOTLOADER MULTILIB [PACKAGES...]' >&2
    exit 2
fi
ROOT_PART=$1 BOOT_PART=$2 HOME_PART=$3 DEPS_PATH=$4
DESKTOPS=$5 GREETER=$6 BOOTLOADER=$7 MULTILIB=$8
shift 8
SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
python "$SCRIPT_DIR/desktop_setup.py" validate "$DESKTOPS" "$GREETER"
[[ $EUID == 0 && -d "$DEPS_PATH" ]] || exit 2
case "$GREETER" in sddm|gdm|lightdm-gtk-greeter|ly) ;; *) exit 2;; esac
case "$MULTILIB" in true|false) ;; *) exit 2;; esac
for device in "$ROOT_PART" "$BOOT_PART"; do [[ -b $device ]] || exit 2; done
[[ $HOME_PART == - || -b $HOME_PART ]] || exit 2
TARGET=$(mktemp -d /mnt/zelix-target.XXXXXXXX)
cleanup() {
    local result=$?
    trap - EXIT
    for path in "$TARGET/home" "$TARGET/boot" "$TARGET"; do
        if mountpoint -q "$path"; then
            if ! umount "$path"; then echo "ERROR: cannot unmount $path" >&2; result=1; fi
        fi
    done
    rmdir "$TARGET" 2>/dev/null || true
    exit "$result"
}
trap cleanup EXIT
trap 'echo "ERROR: post-install failed at line $LINENO" >&2' ERR
mount "$ROOT_PART" "$TARGET"
[[ -d $TARGET/etc && -d $TARGET/usr ]]
mkdir -p "$TARGET/boot" "$TARGET/home"
mount "$BOOT_PART" "$TARGET/boot"
if [[ $HOME_PART != - ]]; then mount "$HOME_PART" "$TARGET/home"; fi

# Copy common assets without leaking KDE and SDDM defaults into other desktops.
for path in "$DEPS_PATH"/*; do
    [[ $(basename "$path") == etc || $(basename "$path") == boot ]] && continue
    cp -a "$path" "$TARGET/"
done
mkdir -p "$TARGET/etc/xdg/autostart"
install -m644 "$DEPS_PATH/etc/xdg/autostart/zelix-hello.desktop" "$TARGET/etc/xdg/autostart/"
if [[ $GREETER == sddm ]]; then
    mkdir -p "$TARGET/etc/sddm.conf.d"
    cp -a "$DEPS_PATH/etc/sddm.conf" "$TARGET/etc/"
    cp -a "$DEPS_PATH/etc/sddm.conf.d/." "$TARGET/etc/sddm.conf.d/"
fi
if [[ ,$DESKTOPS, == *,kde-plasma,* ]]; then
    mkdir -p "$TARGET/etc/skel/.config"
    cp -a "$DEPS_PATH/etc/skel/.config/." "$TARGET/etc/skel/.config/"
    install -m644 "$DEPS_PATH/etc/xdg/autostart/zelix-firstrun-wallpaper.desktop" "$TARGET/etc/xdg/autostart/"
    while IFS=: read -r user _ uid gid _ home _; do
        if (( uid >= 1000 && uid < 65534 )) && [[ $home == /home/* && -d $TARGET$home ]]; then
            mkdir -p "$TARGET$home/.config"
            cp -a "$TARGET/etc/skel/.config/." "$TARGET$home/.config/"
            chown -R "$uid:$gid" "$TARGET$home/.config"
        fi
    done < "$TARGET/etc/passwd"
else
    # Plasma update scripts must not overwrite a future, manually installed KDE session.
    rm -f "$TARGET/usr/share/plasma/shells/org.kde.plasma.desktop/contents/updates/00-zelix-wallpaper.js"
fi
python "$SCRIPT_DIR/desktop_setup.py" install "$TARGET" "$SCRIPT_DIR" "$DESKTOPS" "$GREETER"
cat > "$TARGET/etc/os-release" <<'EOF'
NAME="ZelixOS"
PRETTY_NAME="ZelixOS Aurora"
ID=zelixos
ID_LIKE=arch
BUILD_ID=rolling
HOME_URL="https://zelixos.com"
LOGO=/usr/share/zelix/zelix-icon.png
EOF
printf 'DISTRIB_ID=ZelixOS\nDISTRIB_RELEASE=rolling\nDISTRIB_DESCRIPTION="ZelixOS Aurora"\n' > "$TARGET/etc/lsb-release"
printf 'ZelixOS Aurora \\l\n' > "$TARGET/etc/issue"
# Enforce the same multilib decision in every installation phase.
python - "$TARGET/etc/pacman.conf" "$MULTILIB" "$SCRIPT_DIR" <<'PYCODE'
import sys
from pathlib import Path
sys.path.insert(0, sys.argv[3])
from installer_support import configure_multilib
p = Path(sys.argv[1])
p.write_text(configure_multilib(p.read_text(), sys.argv[2] == 'true'))
PYCODE
if ! grep -q '^\[zelixrepo\]' "$TARGET/etc/pacman.conf"; then
    cat >> "$TARGET/etc/pacman.conf" <<'EOF'

[zelixrepo]
SigLevel = Optional TrustAll
Server = https://github.com/ZelixOS/zelix-repo/releases/download/stable
EOF
fi
if (( $# )); then
    # Package failures are critical; propagate the result to the installer UI.
    arch-chroot "$TARGET" pacman -Syu --noconfirm --needed "$@"
fi
SERVICE=$GREETER
[[ $GREETER == lightdm-gtk-greeter ]] && SERVICE=lightdm
if [[ $GREETER == ly ]]; then
    if [[ -f $TARGET/usr/lib/systemd/system/ly@.service ]]; then
        SERVICE=ly@tty1
        arch-chroot "$TARGET" systemctl disable getty@tty1.service
    else
        SERVICE=ly
    fi
fi
# Some DE profiles install their own display managers. Enable exactly the chosen one.
for other in sddm gdm lightdm plasmalogin ly ly@tty1; do
    [[ $other == "$SERVICE" ]] && continue
    unit=$other
    [[ $other == ly@tty1 ]] && unit=ly@
    if [[ -f $TARGET/usr/lib/systemd/system/$unit.service ]]; then
        arch-chroot "$TARGET" systemctl disable "$other.service"
    fi
done
arch-chroot "$TARGET" systemctl enable "$SERVICE.service"
arch-chroot "$TARGET" systemctl set-default graphical.target

# Keep archinstall's kernel/storage hooks. Add Plymouth rather than replacing them.
python - "$TARGET/etc/mkinitcpio.conf" <<'PY'
import re, sys
from pathlib import Path
p = Path(sys.argv[1])
s = p.read_text()
match = re.search(r'^HOOKS=\(([^)]*)\)', s, re.M)
if not match:
    raise SystemExit('Cannot find mkinitcpio HOOKS')
hooks = match.group(1).replace('"', '').replace("'", '').split()
if 'plymouth' not in hooks:
    index = hooks.index('systemd') + 1 if 'systemd' in hooks else hooks.index('udev') + 1
    hooks.insert(index, 'plymouth')
p.write_text(s[:match.start()] + 'HOOKS=(' + ' '.join(hooks) + ')' + s[match.end():])
PY
rm -f "$TARGET/etc/mkinitcpio.conf.d/archiso.conf"
mkdir -p "$TARGET/etc/plymouth"
install -m644 "$DEPS_PATH/etc/plymouth/plymouthd.conf" "$TARGET/etc/plymouth/"
arch-chroot "$TARGET" plymouth-set-default-theme -R zelix-aurora
if [[ $BOOTLOADER == Grub ]]; then
    install -m644 "$DEPS_PATH/etc/default/grub" "$TARGET/etc/default/grub"
    arch-chroot "$TARGET" grub-mkconfig -o /boot/grub/grub.cfg
elif [[ $BOOTLOADER == Systemd-boot ]]; then
    for entry in "$TARGET"/boot/loader/entries/*.conf; do
        [[ -f $entry ]] || continue
        sed -i 's/Arch Linux/ZelixOS/g; /^options / { /splash/! s/$/ quiet splash/; }' "$entry"
    done
fi
sync
printf 'ZelixOS post-install completed.\n'
