======================================================================
                      Welcome to ZelixOS!
======================================================================

ZelixOS is a modern, reliable, and user-friendly operating system
based on Arch Linux. Below you will find essential information to
help you get the most out of your new operating system.

1. Package Management & AUR (Arch User Repository)
----------------------------------------------------------------------
ZelixOS uses 'pacman' as its primary package manager.
You can also install popular AUR helpers like 'yay' and 'paru'
with a single click via "Zelix Hello" or use them in terminal.

* To update the system:
  sudo pacman -Syu  (or with AUR: yay -Syu / paru -Syu)

* To install a new package/software:
  sudo pacman -S package_name  (or with AUR: yay -S package_name)

* To remove a package and its unused dependencies:
  sudo pacman -Rns package_name

* To clean orphan packages and package cache:
  zelix clean   (or pacman -Qdtq | sudo pacman -Rns -)

* Or you can perform all these actions easily with the graphical
  "Zelix Hello" and "Zelix Updater" tools without touching the terminal!

2. Desktop Shortcuts & Controls
----------------------------------------------------------------------
NOTE: 'Super' refers to the Windows key on your keyboard.
* Open Terminal: Ctrl + Alt + T
* Application Menu: Super
* Quick Runner & Search (KRunner): Alt + Space / Alt + F2
* File Manager (Dolphin): Super + E
* Take Screenshot (Spectacle): PrintScreen
* Window Tiling: Super + Left / Right / Up
* System Logout / Power Menu: Ctrl + Alt + Del

3. Important Links & Support
----------------------------------------------------------------------
* Official Website: https://zelixos.com
* Release Notes: https://zelixos.com/release-aurora.html
* Wiki & Documentation: https://docs.zelixos.com
* GitHub Organization: https://github.com/ZelixOS
* Telegram Community: https://t.me/zelixos
* Discord Server: https://discord.gg/zelixos

You can continue using the tabs in the "Zelix Hello" application
to customize your desktop experience, install popular applications,
and configure system tweaks.

We hope you enjoy your experience with ZelixOS!
- Muhammed Yasir Peker & The ZelixOS Team
======================================================================
