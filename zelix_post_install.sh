#!/bin/bash
# Called only after archinstall succeeds. Arguments are passed as an argv list.
set -Eeuo pipefail
CONFIG_FILE= CREDS_FILE=
while [[ ${1:-} == --* ]]; do
    (( $# >= 2 )) || exit 2
    case "$1" in
        --config) CONFIG_FILE=$2;;
        --creds) CREDS_FILE=$2;;
        *) exit 2;;
    esac
    shift 2
done
[[ -f $CONFIG_FILE && -f $CREDS_FILE ]] || { echo 'Missing installation configuration/credentials.' >&2; exit 2; }
if (( $# < 9 )); then
    echo 'Usage: postinstall --config CONFIG --creds CREDS ROOT BOOT HOME_OR_DASH DEPS DESKTOPS_CSV GREETER BOOTLOADER MULTILIB COMPONENTS_CSV_OR_DASH [PACKAGES...]' >&2
    exit 2
fi
ROOT_PART=$1 BOOT_PART=$2 HOME_PART=$3 DEPS_PATH=$4
DESKTOPS=$5 GREETER=$6 BOOTLOADER=$7 MULTILIB=$8
APPEARANCE=$9
shift 9
SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
python "$SCRIPT_DIR/desktop_setup.py" validate "$DESKTOPS" "$GREETER"
python "$SCRIPT_DIR/install_profiles.py" validate "$APPEARANCE" "$DESKTOPS" "$GREETER" "$BOOTLOADER"
has_component() { [[ ,$APPEARANCE, == *,$1,* ]]; }
[[ $EUID == 0 && -d "$DEPS_PATH" ]] || exit 2
case "$GREETER" in sddm|gdm|lightdm-gtk-greeter|ly) ;; *) exit 2;; esac
case "$MULTILIB" in true|false) ;; *) exit 2;; esac
for device in "$ROOT_PART" "$BOOT_PART"; do [[ -b $device ]] || exit 2; done
[[ $HOME_PART == - || -b $HOME_PART ]] || exit 2
TARGET=$(mktemp -d /mnt/zelix-target.XXXXXXXX)
MOUNT_STATE=$(mktemp /tmp/zelix-mount-state.XXXXXXXX)
AUR_SUDOERS=
cleanup() {
    local result=$?
    trap - EXIT
    # Explicit exit statements do not trigger ERR, so persist their failure too.
    if (( result != 0 )) && [[ -d $TARGET/var/log/zelix-installer ]]; then
        printf 'failed: %s; exit: %s\n' "${STAGE:-mount}" "$result" > "$TARGET/var/log/zelix-installer/stage"
    fi
    if [[ -n $AUR_SUDOERS ]]; then
        rm -f "$AUR_SUDOERS"
    fi
    if python "$SCRIPT_DIR/disk_mount.py" unmount "$MOUNT_STATE"; then
        rm -f "$MOUNT_STATE"
    else
        echo "ERROR: cannot release target filesystems; state: $MOUNT_STATE" >&2
        result=1
    fi
    rmdir "$TARGET" 2>/dev/null || true
    exit "$result"
}
trap cleanup EXIT
STAGE=mount
record_failure() {
    echo "ERROR: post-install failed at line $1 (stage: $STAGE)" >&2
    if [[ -d $TARGET/var/log/zelix-installer ]]; then
        printf 'failed: %s; line: %s\n' "$STAGE" "$1" > "$TARGET/var/log/zelix-installer/stage"
    fi
}
trap 'record_failure "$LINENO"' ERR
python "$SCRIPT_DIR/disk_mount.py" mount "$CONFIG_FILE" "$CREDS_FILE" "$TARGET" "$MOUNT_STATE" "$ROOT_PART" "$BOOT_PART" "$HOME_PART"
[[ -d $TARGET/etc && -d $TARGET/usr ]]
mkdir -p "$TARGET/var/log/zelix-installer"
set_stage() {
    STAGE=$1
    printf '%s\n' "$STAGE" > "$TARGET/var/log/zelix-installer/stage"
    printf 'ZelixOS post-install stage: %s\n' "$STAGE"
}
set_stage fstab
python "$SCRIPT_DIR/disk_mount.py" fstab "$CONFIG_FILE" "$TARGET"
set_stage users
python "$SCRIPT_DIR/install_profiles.py" users "$APPEARANCE" "$DESKTOPS" "$GREETER" "$BOOTLOADER" "$DEPS_PATH" "$TARGET"
set_stage packages

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
PACMAN_PACKAGES=()
AUR_PACKAGES=()
for package in "$@"; do
    if [[ $package == aur:* ]]; then
        aur_package=${package#aur:}
        [[ $aur_package =~ ^[a-z0-9][a-z0-9@._+-]*$ ]] || exit 2
        AUR_PACKAGES+=("$aur_package")
    else
        PACMAN_PACKAGES+=("$package")
    fi
done
if (( ${#AUR_PACKAGES[@]} )); then
    PACMAN_PACKAGES+=(base-devel git paru)
fi
if (( ${#PACMAN_PACKAGES[@]} )); then
    # Package failures are critical; propagate the result to the installer UI.
    arch-chroot "$TARGET" pacman -Syu --noconfirm --needed "${PACMAN_PACKAGES[@]}"
fi
if (( ${#AUR_PACKAGES[@]} )); then
    AUR_ACCOUNT=$(awk -F: '$3 >= 1000 && $3 < 65534 && $6 ~ /^\/home\// {print $1 ":" $6; exit}' "$TARGET/etc/passwd")
    [[ -n $AUR_ACCOUNT ]] || { echo 'ERROR: AUR installation requires a regular user.' >&2; exit 1; }
    AUR_USER=${AUR_ACCOUNT%%:*}
    AUR_HOME=${AUR_ACCOUNT#*:}
    mkdir -p "$TARGET/etc/sudoers.d"
    AUR_SUDOERS="$TARGET/etc/sudoers.d/90-zelixins-aur"
    printf '%s ALL=(root) NOPASSWD: /usr/bin/pacman\n' "$AUR_USER" > "$AUR_SUDOERS"
    chmod 440 "$AUR_SUDOERS"
    arch-chroot "$TARGET" runuser -u "$AUR_USER" -- \
        env HOME="$AUR_HOME" paru -S --needed --noconfirm --skipreview -- "${AUR_PACKAGES[@]}"
    rm -f "$AUR_SUDOERS"
    AUR_SUDOERS=
fi
set_stage appearance
# Apply after package updates so their defaults cannot overwrite branding/themes.
# Copy only explicitly selected payload groups; branding remains part of ZelixOS.
python "$SCRIPT_DIR/install_profiles.py" copy "$APPEARANCE" "$DESKTOPS" "$GREETER" "$BOOTLOADER" "$DEPS_PATH" "$TARGET"
if has_component desktop-theme; then
    if [[ ,$DESKTOPS, == *,kde-plasma,* ]]; then
        while IFS=: read -r user _ uid gid _ home _; do
            if (( uid >= 1000 && uid < 65534 )) && [[ $home == /home/* && -d $TARGET$home ]]; then
                mkdir -p "$TARGET$home/.config"
                cp -a "$TARGET/etc/skel/.config/." "$TARGET$home/.config/"
                chown -R "$uid:$gid" "$TARGET$home/.config"
            fi
        done < "$TARGET/etc/passwd"
    fi
    python "$SCRIPT_DIR/desktop_setup.py" install "$TARGET" "$SCRIPT_DIR" "$DESKTOPS" "$GREETER"
fi
cat > "$TARGET/etc/os-release" <<'EOF'
NAME="ZelixOS"
PRETTY_NAME="ZelixOS Aurora"
ID=zelixos
ID_LIKE=arch
BUILD_ID=rolling
HOME_URL="https://zelixos.com"
DOCUMENTATION_URL="https://docs.zelixos.com/"
SUPPORT_URL="https://www.reddit.com/r/ZelixOS/"
BUG_REPORT_URL="https://zelixos.com/br.html"
LOGO=/usr/share/zelix/zelix-icon.png
EOF
printf 'DISTRIB_ID=ZelixOS\nDISTRIB_RELEASE=rolling\nDISTRIB_DESCRIPTION="ZelixOS Aurora"\n' > "$TARGET/etc/lsb-release"
printf 'ZelixOS Aurora \\l\n' > "$TARGET/etc/issue"

SERVICE=$GREETER
set_stage display-manager
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

# Preserve archinstall's kernel/storage hooks; Plymouth is strictly opt-in.
set_stage boot
rm -f "$TARGET/etc/mkinitcpio.conf.d/archiso.conf"
if has_component plymouth-theme; then
    python - "$TARGET/etc/mkinitcpio.conf" <<'PYCODE'
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
PYCODE
    # Arch's -R helper exits successfully even when mkinitcpio fails. Run the
    # theme setter and image rebuild separately so a failed rebuild stops install.
    arch-chroot "$TARGET" plymouth-set-default-theme zelix-aurora
    arch-chroot "$TARGET" mkinitcpio -P
    shopt -s nullglob
    INITRAMFS_IMAGES=("$TARGET"/boot/initramfs-*.img)
    shopt -u nullglob
    ((${#INITRAMFS_IMAGES[@]})) || {
        echo 'ERROR: mkinitcpio did not produce a boot initramfs.' >&2
        exit 1
    }
    for image in "${INITRAMFS_IMAGES[@]}"; do
        listing=$(lsinitcpio -l "$image") || {
            echo "ERROR: cannot inspect generated initramfs: $image" >&2
            exit 1
        }
        grep -Fq 'usr/bin/plymouthd' <<<"$listing" || {
            echo "ERROR: Plymouth daemon is missing from initramfs: $image" >&2
            exit 1
        }
        grep -Fq 'usr/share/plymouth/themes/zelix-aurora/zelix-aurora.plymouth' <<<"$listing" || {
            echo "ERROR: selected Plymouth theme is missing from initramfs: $image" >&2
            exit 1
        }
    done
fi
if [[ $BOOTLOADER == Grub ]]; then
    python - "$TARGET" "$APPEARANCE" "$SCRIPT_DIR" <<'PYCODE'
import sys
from pathlib import Path
sys.path.insert(0, sys.argv[3])
from install_profiles import configure_target_grub
configure_target_grub(Path(sys.argv[1]), sys.argv[2].split(','))
PYCODE
    arch-chroot "$TARGET" grub-mkconfig -o /boot/grub/grub.cfg
    arch-chroot "$TARGET" grub-script-check /boot/grub/grub.cfg
    if has_component grub-theme; then
        # grub-mkconfig can succeed while silently omitting an unreadable theme.
        grep -Eq '^[[:space:]]*set theme=.*/grub/themes/zelix-aurora/theme\.txt' "$TARGET/boot/grub/grub.cfg" || {
            echo 'ERROR: selected Zelix GRUB theme was not included in grub.cfg.' >&2
            exit 1
        }
        grep -Eq '^[[:space:]]*insmod gfxmenu' "$TARGET/boot/grub/grub.cfg" || {
            echo 'ERROR: graphical GRUB theme support was not generated.' >&2
            exit 1
        }
    fi
elif [[ $BOOTLOADER == Systemd-boot ]]; then
    for entry in "$TARGET"/boot/loader/entries/*.conf; do
        [[ -f $entry ]] || continue
        sed -i 's/Arch Linux/ZelixOS/g' "$entry"
        if has_component plymouth-theme; then
            sed -i '/^options / { /splash/! s/$/ quiet splash/; }' "$entry"
        fi
    done
elif [[ $BOOTLOADER == Refind ]] && has_component plymouth-theme; then
    # Archinstall's rEFInd stanza is outside GRUB/systemd-boot configuration.
    for conf in "$TARGET/boot/refind_linux.conf" "$TARGET/boot/EFI/refind/refind_linux.conf"; do
        [[ -f $conf ]] || continue
        python - "$conf" <<'PYCODE'
import shlex, sys
from pathlib import Path
p = Path(sys.argv[1])
lines = []
for line in p.read_text().splitlines():
    if line.strip() and not line.lstrip().startswith('#'):
        fields = shlex.split(line)
        if len(fields) == 2:
            options = fields[1].split()
            options += [word for word in ('quiet', 'splash') if word not in options]
            line = '"' + fields[0] + '" "' + ' '.join(options) + '"'
    lines.append(line)
p.write_text('\n'.join(lines) + '\n')
PYCODE
    done
fi
python "$SCRIPT_DIR/system_locale.py" "$TARGET" "$CONFIG_FILE" "$DESKTOPS"
arch-chroot "$TARGET" locale-gen
set_stage verification
python "$SCRIPT_DIR/install_profiles.py" verify "$APPEARANCE" "$DESKTOPS" "$GREETER" "$BOOTLOADER" "$DEPS_PATH" "$TARGET"
sync
set_stage completed
printf 'ZelixOS post-install completed.\n'
python - "$CONFIG_FILE" <<'PYCODE'
import hashlib, sys
with open(sys.argv[1], 'rb') as stream:
    print('ZELIX_INSTALL_VERIFIED=' + hashlib.file_digest(stream, 'sha256').hexdigest())
PYCODE
