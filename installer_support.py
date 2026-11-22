"""Side-effect-free policy shared by the installer and its tests."""
from disk_layout import build_partitions, partition_device as partition_path

from desktop_catalog import DESKTOPS, GREETER_SERVICES, choose_greeter
from install_profiles import ZELIX_APPS

GREETERS = {desktop.name: desktop.recommended for desktop in DESKTOPS}
MULTILIB_PACKAGES = {'steam'}
ZELIX_PACKAGES = {'yay', 'paru', *ZELIX_APPS, 'mkinitcpio-openswap',
                  'alci-calamares', 'calamares', 'ckbcomp', 'gquick-git', 'qrun-code-git'}


def selected_greeter(desktops, choice):
    return choose_greeter(desktops, choice)


def post_install_packages(selected_packages):
    """Only selected Zelix repository and AUR applications are installed."""
    packages = (
        package for package in selected_packages
        if package in ZELIX_PACKAGES or package.startswith('aur:')
    )
    return list(dict.fromkeys(packages))


def validate_choices(size_bytes, uefi, bootloader, kernels, multilib, packages):
    if size_bytes < 25 * 1024**3:
        raise ValueError('policy_disk_size')
    if not uefi and bootloader != 'Grub':
        raise ValueError('policy_bios')
    if not kernels:
        raise ValueError('policy_kernel')
    if not multilib and MULTILIB_PACKAGES.intersection(packages):
        raise ValueError('policy_multilib')


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
