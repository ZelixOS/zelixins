# Zelixins

The graphical installer for ZelixOS, written in Python and PyQt6. It uses Archinstall and provides a single interface for user accounts, disks, kernels, desktops, and bootloaders.

## Features

- English and Turkish interface.
- KDE Plasma, GNOME, Xfce, Hyprland, Sway, i3, and bspwm options.
- Compatible login manager selection.
- Kernel, bootloader, and additional software selection.
- Installation output displayed in the interface.
- ZelixOS settings and application packages applied after installation.

## Running

The installer is intended for the ZelixOS live session:

```bash
zelix-installer
```

To launch the interface from the source directory:

```bash
python myself.py
```

Requires Python, `python-pyqt6`, `qt6-imageformats`, `archinstall`, `arch-install-scripts`, `polkit`, and `util-linux`. Installation operations require administrator privileges.

## Disk operations

Installation erases the selected disk. Back up existing data first. Manual partitioning is not available. Test disk operations, BIOS/UEFI installation, and reboot behavior in a virtual machine before using physical hardware.

## Source structure

| File or directory | Purpose |
| --- | --- |
| `myself.py` | Installation flow and interface |
| `installer_support.py` | Disk and configuration helpers |
| `desktop_*.py` | Desktop options and appearance settings |
| `zelix_post_install.sh` | Post-installation operations |
| `zelixdeps/` | Shared configuration and appearance files |
| `backgrounds/`, `previews/`, `icons/` | Interface assets |

The package recipe is maintained in [zelix-repo](https://github.com/ZelixOS/zelix-repo/tree/main/zelixins).
