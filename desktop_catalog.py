"""Desktop descriptions, asset names and the installer's supported login combinations.

The greeter allowlist is deliberately conservative; an omitted pair is not a claim
that it can never work. See docs/DESKTOPS.md for the upstream references.
"""
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Desktop:
    slug: str
    name: str
    profile: str
    session: str
    recommended: str
    greeters: tuple[str, ...]
    packages: tuple[str, ...]
    description_tr: str
    description_en: str
    appearance_tr: str
    appearance_en: str


DESKTOPS = (
    Desktop('kde-plasma', 'KDE Plasma', 'KDE Plasma', 'Wayland', 'sddm',
            ('sddm', 'gdm', 'ly'), (),
            'Geleneksel panel düzeni, kapsamlı ayarlar ve esnek bir masaüstü deneyimi.',
            'A familiar panel layout, extensive settings and a flexible desktop experience.',
            'Aurora koyu görünüm · Beyaz aksan · Mevcut Aurora duvar kâğıdı',
            'Aurora dark appearance · White accent · Existing Aurora wallpaper'),
    Desktop('gnome', 'GNOME', 'GNOME', 'Wayland', 'gdm',
            ('gdm', 'sddm', 'ly'), (),
            'Etkinlikler görünümü ve çalışma alanlarıyla sade, odaklı bir iş akışı.',
            'A focused workflow built around the Activities overview and workspaces.',
            'Koyu görünüm · Nötr vurgu rengi · Özel duvar kâğıdı',
            'Dark appearance · Slate accent · Dedicated wallpaper'),
    Desktop('xfce', 'Xfce4', 'Xfce4', 'X11', 'lightdm-gtk-greeter',
            ('lightdm-gtk-greeter', 'sddm', 'gdm', 'ly'), ('materia-gtk-theme', 'adwaita-icon-theme'),
            'Klasik masaüstü ve panel yapısı; daha az görsel efekt isteyenler için.',
            'A classic desktop and panel layout for those who prefer fewer visual effects.',
            'Materia koyu tema · Adwaita ikonları · Özel duvar kâğıdı',
            'Materia dark theme · Adwaita icons · Dedicated wallpaper'),
    Desktop('hyprland', 'Hyprland', 'Hyprland', 'Wayland', 'sddm',
            ('sddm', 'ly'), ('swaybg',),
            'Dinamik döşeme, klavye odaklı kontrol ve özelleştirilebilir Wayland oturumu.',
            'Dynamic tiling, keyboard-driven control and a customizable Wayland session.',
            'Beyaz odak çerçevesi · Yuvarlatılmış köşeler · Özel duvar kâğıdı',
            'White focus border · Rounded corners · Dedicated wallpaper'),
    Desktop('sway', 'Sway', 'Sway', 'Wayland', 'sddm',
            ('sddm', 'ly'), ('swaybg',),
            'i3 benzeri kısayollar ve düzenlerle klavye odaklı bir Wayland ortamı.',
            'A keyboard-driven Wayland environment with i3-style bindings and layouts.',
            'Beyaz odak çerçevesi · Pencere boşlukları · Özel duvar kâğıdı',
            'White focus border · Window gaps · Dedicated wallpaper'),
    Desktop('i3', 'i3-wm', 'i3-wm', 'X11', 'lightdm-gtk-greeter',
            ('lightdm-gtk-greeter', 'sddm', 'gdm', 'ly'), ('feh',),
            'Pencereleri döşeyen, kısayollarla yönetilen sade bir X11 ortamı.',
            'A minimal X11 environment with tiled windows and keyboard controls.',
            'Beyaz odak çerçevesi · Pencere boşlukları · Özel duvar kâğıdı',
            'White focus border · Window gaps · Dedicated wallpaper'),
    Desktop('bspwm', 'bspwm', 'Bspwm', 'X11', 'lightdm-gtk-greeter',
            ('lightdm-gtk-greeter', 'sddm', 'gdm', 'ly'), ('feh',),
            'Pencereleri ağaç düzeninde bölen; sxhkd ile kontrol edilen bir X11 yöneticisi.',
            'An X11 window manager with tree-based tiling and sxhkd keyboard control.',
            'Beyaz odak çerçevesi · Pencere boşlukları · Özel duvar kâğıdı',
            'White focus border · Window gaps · Dedicated wallpaper'),
)
BY_NAME = {desktop.name: desktop for desktop in DESKTOPS}
BY_SLUG = {desktop.slug: desktop for desktop in DESKTOPS}
GREETER_NAMES = {'sddm': 'SDDM', 'gdm': 'GDM', 'lightdm-gtk-greeter': 'LightDM (GTK)', 'ly': 'Ly (TTY)'}
GREETER_SERVICES = {'sddm': 'sddm', 'gdm': 'gdm', 'lightdm-gtk-greeter': 'lightdm', 'ly': 'ly@tty1'}
IMAGE_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.webp')


def desktops_for(names):
    if isinstance(names, str):
        names = [names]
    result = []
    for name in names:
        desktop = BY_NAME.get(name) or BY_SLUG.get(name)
        if desktop is None:
            raise ValueError('Unknown desktop: ' + str(name))
        if desktop not in result:
            result.append(desktop)
    return result


def compatible_greeters(names):
    desktops = desktops_for(names)
    if not desktops:
        return []
    common = set(desktops[0].greeters)
    for desktop in desktops[1:]:
        common.intersection_update(desktop.greeters)
    return [greeter for greeter in GREETER_NAMES if greeter in common]


def choose_greeter(names, choice='default'):
    desktops = desktops_for(names)
    common = compatible_greeters(names)
    if not desktops or not common:
        raise ValueError('En az bir masaüstü ve ortak giriş yöneticisi seçin / Select desktops with a common greeter.')
    if choice != 'default':
        if choice not in common:
            raise ValueError('Seçilen giriş yöneticisi tüm masaüstleriyle uyumlu değil / Greeter is not supported by all selected desktops.')
        return choice
    # Keep each desktop's recommendation, choosing the first common recommendation.
    return next((desktop.recommended for desktop in desktops if desktop.recommended in common), common[0])


def find_image(folder, stem):
    folder = Path(folder)
    return next((folder/(stem+ext) for ext in IMAGE_EXTENSIONS if (folder/(stem+ext)).is_file()), None)


def appearance_packages(names):
    return list(dict.fromkeys(package for desktop in desktops_for(names) for package in desktop.packages))
