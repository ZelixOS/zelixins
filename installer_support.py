"""Side-effect-free policy shared by the installer and its tests."""
import uuid

from desktop_catalog import DESKTOPS, GREETER_SERVICES, choose_greeter

GREETERS = {desktop.name: desktop.recommended for desktop in DESKTOPS}
MULTILIB_PACKAGES = {'steam'}
ZELIX_PACKAGES = {'yay', 'paru', 'zelix-hello', 'zelix-updater', 'mkinitcpio-openswap',
                  'alci-calamares', 'calamares', 'ckbcomp', 'gquick-git', 'qrun-code-git'}


def selected_greeter(desktops, choice):
    return choose_greeter(desktops, choice)


def validate_choices(size_bytes, uefi, bootloader, kernels, multilib, packages):
    if size_bytes < 25 * 1024**3:
        raise ValueError('Disk en az 25 GiB olmalı / Disk must be at least 25 GiB.')
    if not uefi and bootloader != 'Grub':
        raise ValueError('BIOS kurulumunda GRUB seçilmeli / BIOS requires GRUB.')
    if not kernels:
        raise ValueError('En az bir çekirdek seçin / Select at least one kernel.')
    if not multilib and MULTILIB_PACKAGES.intersection(packages):
        raise ValueError('Steam için multilib gerekli / Steam requires multilib.')


def partition_path(disk, number):
    return f'{disk}{"p" if disk[-1].isdigit() else ""}{number}'


def build_partitions(size_bytes, uefi, kernel_count):
    # Reserve room for several kernel + fallback initramfs images on the ESP.
    boot_mib = max(1024, 512 * kernel_count)
    usable = size_bytes // (1024**2) - boot_mib - 2
    root_mib = min(max(int(usable * .4), 20 * 1024), 100 * 1024)
    home_mib = usable - root_mib
    if home_mib < 4 * 1024:
        root_mib, home_mib = usable, 0
    def part(start, size, fs, mount, flags):
        def units(n):
            return {'sector_size': {'unit': 'B', 'value': 512}, 'unit': 'MiB', 'value': n}
        return {'btrfs': [], 'flags': flags, 'fs_type': fs, 'start': units(start),
                'size': units(size), 'mount_options': [], 'mountpoint': mount,
                'status': 'create', 'type': 'primary', 'dev_path': None,
                'obj_id': str(uuid.uuid4())}
    parts = [part(1, boot_mib, 'fat32' if uefi else 'ext4', '/boot',
                  ['boot', 'esp'] if uefi else ['boot']),
             part(1 + boot_mib, root_mib, 'ext4', '/', [])]
    if home_mib:
        parts.append(part(1 + boot_mib + root_mib, home_mib, 'ext4', '/home', []))
    return parts


def configure_multilib(text, enabled):
    """Toggle only the multilib stanza, leaving other repositories unchanged."""
    lines = text.splitlines(keepends=True)
    in_block = False
    found = False
    for i, line in enumerate(lines):
        if line.strip() in ('[multilib]', '#[multilib]'):
            in_block = found = True
            lines[i] = '[multilib]\n' if enabled else '#[multilib]\n'
        elif in_block:
            if line.lstrip('# ').startswith('['):
                in_block = False
            elif line.lstrip('# ').startswith('Include'):
                value = line.lstrip('# ')
                lines[i] = value if enabled else '#' + value
                in_block = False
    if enabled and not found:
        lines.append('\n[multilib]\nInclude = /etc/pacman.d/mirrorlist\n')
    return ''.join(lines)
