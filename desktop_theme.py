#!/usr/bin/env python3
"""Apply GNOME/Xfce appearance once per user, in the matching running session."""
import fcntl
import json
import os
from pathlib import Path
import subprocess
import sys
import time


def session_slug(environment):
    desktops = environment.get('XDG_CURRENT_DESKTOP', '').lower().split(':')
    session = environment.get('XDG_SESSION_DESKTOP', '').lower()
    if 'gnome' in desktops or session in {'gnome', 'gnome-wayland'}:
        return 'gnome'
    if 'xfce' in desktops or session in {'xfce', 'xfce4'}:
        return 'xfce'
    return None


def run(arguments):
    return subprocess.run(arguments, check=True, capture_output=True, text=True).stdout.strip()


def xfconf_set(channel, property_name, value, kind='string'):
    exists = subprocess.run(['xfconf-query', '-c', channel, '-p', property_name],
                            capture_output=True).returncode == 0
    args = ['xfconf-query', '-c', channel, '-p', property_name, '-s', value]
    if not exists:
        args += ['-n', '-t', kind]
    run(args)


def apply(desktop, wallpaper):
    if desktop == 'gnome':
        uri = Path(wallpaper).as_uri()
        run(['gsettings', 'set', 'org.gnome.desktop.background', 'picture-uri', repr(uri)])
        run(['gsettings', 'set', 'org.gnome.desktop.background', 'picture-uri-dark', repr(uri)])
        run(['gsettings', 'set', 'org.gnome.desktop.interface', 'color-scheme', 'prefer-dark'])
        keys = run(['gsettings', 'list-keys', 'org.gnome.desktop.interface']).splitlines()
        if 'accent-color' in keys:
            run(['gsettings', 'set', 'org.gnome.desktop.interface', 'accent-color', 'slate'])
    elif desktop == 'xfce':
        # xfdesktop initializes monitor/workspace properties during session startup.
        properties = []
        for attempt in range(30):
            try:
                properties = run(['xfconf-query', '-c', 'xfce4-desktop', '-l']).splitlines()
            except subprocess.CalledProcessError:
                properties = []
            properties = [p for p in properties if p.endswith(('/last-image', '/image-path'))]
            if properties:
                break
            time.sleep(1)
        if not properties:
            raise RuntimeError('Xfce desktop properties are not ready; retry next login.')
        for property_name in properties:
            xfconf_set('xfce4-desktop', property_name, wallpaper)
        xfconf_set('xsettings', '/Net/ThemeName', 'Materia-dark')
        xfconf_set('xsettings', '/Net/IconThemeName', 'Adwaita')


def initialize(config_path=Path('/etc/zelix/desktops.json')):
    desktop = session_slug(os.environ)
    if desktop is None or not config_path.is_file():
        return 0
    settings = json.loads(config_path.read_text())
    if desktop not in settings['desktops']:
        return 0
    wallpaper = settings['wallpapers'][desktop]
    state = Path(os.environ.get('XDG_STATE_HOME', str(Path.home()/'.local/state')))/'zelix'
    state.mkdir(parents=True, exist_ok=True)
    marker = state/f'appearance-{desktop}-v1.done'
    with (state/f'appearance-{desktop}.lock').open('w') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return 0
        if marker.exists():
            return 0
        with (state/f'appearance-{desktop}.log').open('a') as log:
            try:
                if not Path(wallpaper).is_file():
                    raise RuntimeError('Wallpaper is missing: ' + wallpaper)
                apply(desktop, wallpaper)
                marker.touch()
                log.write('ZelixOS appearance applied successfully.\n')
                return 0
            except (OSError, subprocess.SubprocessError, RuntimeError) as error:
                log.write(f'Appearance failed; will retry next login: {error}\n')
                return 1


if __name__ == '__main__':
    sys.exit(initialize())
