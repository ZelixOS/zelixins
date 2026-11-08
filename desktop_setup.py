#!/usr/bin/env python3
"""Seed DE-specific defaults on the target disk; never edit the running desktop."""
import argparse
import json
import os
from pathlib import Path
import shlex
import shutil
from desktop_catalog import desktops_for, choose_greeter, find_image

DEFAULT_WALLPAPER = '/usr/share/wallpapers/Zelix/minimalistic.png'


def write_new(path, text, executable=False):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        return False
    path.write_text(text)
    if executable:
        path.chmod(0o755)
    return True


def append_once(path, text):
    path = Path(path)
    existing = path.read_text() if path.exists() else ''
    if '# ZelixOS desktop defaults' in existing or '-- ZelixOS desktop defaults' in existing:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(existing.rstrip() + '\n\n' + text + '\n')


def ensure_config(target, home, relative, defaults, minimal):
    config = home/'.config'/relative
    if config.exists():
        return config
    config.parent.mkdir(parents=True, exist_ok=True)
    for default in defaults:
        source = target/default.lstrip('/')
        if source.is_file():
            shutil.copy2(source, config)
            return config
    config.write_text(minimal)
    return config


def seed_window_manager(target, home, slug, wallpaper):
    quoted = shlex.quote(wallpaper)
    focus = 'client.focused #ffffff #17181d #ffffff #ffffff #ffffff\n'
    if slug == 'sway':
        config = ensure_config(target, home, 'sway/config', ['/etc/sway/config'],
                               'set $mod Mod4\nbindsym $mod+Return exec foot\nbindsym $mod+d exec wmenu-run\n')
        fragment = home/'.config/sway/zelix.conf'
        write_new(fragment, focus + 'default_border pixel 2\ngaps inner 8\n'
                  + 'output * bg "' + wallpaper + '" fill\n')
        append_once(config, '# ZelixOS desktop defaults\ninclude ~/.config/sway/zelix.conf')
    elif slug == 'i3':
        config = ensure_config(target, home, 'i3/config', ['/etc/i3/config'],
                               'set $mod Mod4\nbindsym $mod+Return exec xterm\nbindsym $mod+d exec dmenu_run\n')
        fragment = home/'.config/i3/zelix.conf'
        write_new(fragment, focus + 'default_border pixel 2\ngaps inner 8\n'
                  + 'exec --no-startup-id feh --no-fehbg --bg-fill ' + quoted + '\n')
        append_once(config, '# ZelixOS desktop defaults\ninclude ~/.config/i3/zelix.conf')
    elif slug == 'bspwm':
        config = ensure_config(target, home, 'bspwm/bspwmrc',
                               ['/usr/share/doc/bspwm/examples/bspwmrc'], '#!/bin/sh\nsxhkd &\n')
        config.chmod(config.stat().st_mode | 0o100)
        append_once(config, '# ZelixOS desktop defaults\n'
                    'bspc config focused_border_color "#ffffff"\n'
                    'bspc config normal_border_color "#34353d"\n'
                    'bspc config border_width 2\nbspc config window_gap 10\n'
                    'feh --no-fehbg --bg-fill ' + quoted)
    elif slug == 'hyprland':
        # Current Hyprland ships Lua; older installations still use hyprlang.
        folder = home/'.config/hypr'
        use_lua = (folder/'hyprland.lua').exists() or (
            not (folder/'hyprland.conf').exists() and (target/'usr/share/hypr/hyprland.lua').exists())
        if use_lua:
            config = ensure_config(target, home, 'hypr/hyprland.lua', ['/usr/share/hypr/hyprland.lua'], '')
            fragment = folder/'zelix.lua'
            command = json.dumps('swaybg --image ' + quoted + ' --mode fill')
            write_new(fragment, '''hl.config({
    general = { gaps_in = 8, gaps_out = 12, border_size = 2,
        col = { active_border = "rgba(ffffffff)", inactive_border = "rgba(34353dff)" } },
    decoration = { rounding = 8 },
})
hl.on("hyprland.start", function ()
    hl.exec_cmd(''' + command + ''')
    hl.exec_cmd("waybar")
end)
hl.bind("SUPER + SPACE", hl.dsp.exec_cmd("wofi --show drun"))
''')
            append_once(config, '-- ZelixOS desktop defaults\ndofile(os.getenv("HOME") .. "/.config/hypr/zelix.lua")')
        else:
            config = ensure_config(target, home, 'hypr/hyprland.conf', ['/usr/share/hypr/hyprland.conf'],
                                   '$mainMod = SUPER\nbind = $mainMod, Return, exec, kitty\n')
            fragment = folder/'zelix.conf'
            write_new(fragment, '''general {
    gaps_in = 8
    gaps_out = 12
    border_size = 2
    col.active_border = rgba(ffffffff)
    col.inactive_border = rgba(34353dff)
}
decoration {
    rounding = 8
}
exec-once = swaybg --image ''' + quoted + ''' --mode fill
exec-once = waybar
bind = SUPER, SPACE, exec, wofi --show drun
''')
            append_once(config, '# ZelixOS desktop defaults\nsource = ~/.config/hypr/zelix.conf')


def install_defaults(target, assets, names, greeter):
    target, assets = Path(target).resolve(), Path(assets).resolve()
    desktops = desktops_for(names)
    choose_greeter(names, greeter)
    if target == Path('/') or not (target/'etc/passwd').is_file():
        raise ValueError('Expected a mounted target filesystem, never the running root.')
    wallpapers = {}
    for desktop in desktops:
        # KDE keeps the already configured automatic Aurora background.
        source = None if desktop.slug == 'kde-plasma' else find_image(assets/'backgrounds'/desktop.slug, 'wallpaper')
        # QImageReader works without a display or QApplication. Ignore optional corrupt images.
        if source:
            from PyQt6.QtGui import QImageReader
            if not QImageReader(str(source)).canRead():
                print('WARNING: invalid wallpaper, using Aurora fallback:', source)
                source = None
        if source:
            relative = Path('usr/share/wallpapers/Zelix')/desktop.slug/('wallpaper'+source.suffix)
            destination = target/relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
            wallpapers[desktop.slug] = '/'+str(relative)
        else:
            if not (target/DEFAULT_WALLPAPER.lstrip('/')).is_file():
                raise ValueError('Missing fallback wallpaper: '+DEFAULT_WALLPAPER)
            wallpapers[desktop.slug] = DEFAULT_WALLPAPER
    settings = target/'etc/zelix/desktops.json'
    settings.parent.mkdir(parents=True, exist_ok=True)
    settings.write_text(json.dumps({'version': 1, 'desktops': [d.slug for d in desktops],
                                    'wallpapers': wallpapers}, indent=2)+'\n')
    runtime = target/'usr/share/zelix-desktop-theme/main.py'
    runtime.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(assets/'desktop_theme.py', runtime)
    launcher = target/'usr/local/bin/zelix-desktop-theme'
    launcher.parent.mkdir(parents=True, exist_ok=True)
    launcher.write_text('#!/bin/sh\nexec python /usr/share/zelix-desktop-theme/main.py "$@"\n')
    launcher.chmod(0o755)
    autostart = target/'etc/xdg/autostart/zelix-desktop-theme.desktop'
    autostart.parent.mkdir(parents=True, exist_ok=True)
    autostart.write_text('[Desktop Entry]\nType=Application\nName=ZelixOS Desktop Appearance\n'
                         'Exec=/usr/local/bin/zelix-desktop-theme\nOnlyShowIn=GNOME;XFCE;\nNoDisplay=true\n')
    kde = any(desktop.slug == 'kde-plasma' for desktop in desktops)
    update = target/'usr/share/plasma/shells/org.kde.plasma.desktop/contents/updates/00-zelix-wallpaper.js'
    if kde and update.is_file():
        update.write_text(update.read_text().replace(DEFAULT_WALLPAPER, wallpapers['kde-plasma']))
    for line in (target/'etc/passwd').read_text().splitlines():
        fields = line.split(':')
        if len(fields) != 7 or not fields[2].isdigit():
            continue
        uid, gid = int(fields[2]), int(fields[3])
        if not 1000 <= uid < 65534 or not fields[5].startswith('/home/'):
            continue
        home = (target/fields[5].lstrip('/')).resolve()
        if not home.is_relative_to(target) or not home.is_dir():
            continue
        for desktop in desktops:
            seed_window_manager(target, home, desktop.slug, wallpapers[desktop.slug])
        if os.geteuid() == 0 and (home/'.config').exists():
            shutil.chown(home/'.config', uid, gid)
            for path in (home/'.config').rglob('*'):
                if not path.is_symlink():
                    os.chown(path, uid, gid)
    return wallpapers


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest='action', required=True)
    validation = subparsers.add_parser('validate')
    validation.add_argument('desktops')
    validation.add_argument('greeter')
    install = subparsers.add_parser('install')
    for name in ('target', 'assets', 'desktops', 'greeter'):
        install.add_argument(name)
    args = parser.parse_args()
    names = args.desktops.split(',')
    try:
        choose_greeter(names, args.greeter)
        if args.action == 'install':
            install_defaults(args.target, args.assets, names, args.greeter)
    except (ValueError, OSError) as error:
        parser.error(str(error))


if __name__ == '__main__':
    main()
