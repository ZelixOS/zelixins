"""Installation presets and explicit, opt-in Zelix appearance payloads."""
import argparse
import configparser
import json
from pathlib import Path
import re
import shlex
import shutil

PROFILES = ('minimal', 'standard', 'full', 'custom')
ZELIX_APPS = ('zelix-hello', 'zelix-updater', 'zelix-cli')
COMPONENTS = ('desktop-theme', 'wallpapers', 'sddm-theme', 'plymouth-theme', 'grub-theme')
STANDARD_APPS = ('zelix-hello', 'zelix-updater', 'zelix-cli', 'firefox', 'dolphin', 'konsole', 'fastfetch')
FULL_APPS = (*STANDARD_APPS, 'vlc', 'libreoffice-fresh', 'okular', 'gimp', 'htop', 'git', 'flatpak', 'paru')
STANDARD_COMPONENTS = ('desktop-theme', 'sddm-theme', 'plymouth-theme', 'grub-theme')


def preset(name):
    if name not in PROFILES or name == 'custom':
        raise ValueError('Select a predefined installation type.')
    if name == 'minimal':
        return (), ()
    if name == 'standard':
        return STANDARD_APPS, STANDARD_COMPONENTS
    return FULL_APPS, COMPONENTS


def effective_components(components, greeter, bootloader):
    unknown = set(components) - set(COMPONENTS)
    if unknown:
        raise ValueError('Unknown appearance components: ' + ', '.join(sorted(unknown)))
    return tuple(name for name in COMPONENTS if name in components
                 and (name != 'sddm-theme' or greeter == 'sddm')
                 and (name != 'grub-theme' or bootloader == 'Grub'))


def configure_grub(text, components):
    """Add chosen visual defaults without replacing storage/kernel options."""
    def set_value(text, key, value):
        line = key + '=' + shlex.quote(value)
        pattern = r'^[ \t]*(?:export[ \t]+)?' + key + r'[ \t]*=.*$'
        if re.search(pattern, text, re.M):
            return re.sub(pattern, lambda _: line, text, flags=re.M)
        return text.rstrip() + '\n' + line + '\n'
    text = set_value(text, 'GRUB_DISTRIBUTOR', 'ZelixOS')
    if 'grub-theme' in components:
        text = set_value(text, 'GRUB_THEME', '/boot/grub/themes/zelix-aurora/theme.txt')
        # Legacy GRUB_TERMINAL overrides GRUB_TERMINAL_OUTPUT in grub-mkconfig.
        text = set_value(text, 'GRUB_TERMINAL', '')
        text = set_value(text, 'GRUB_TERMINAL_INPUT', 'console')
        text = set_value(text, 'GRUB_TERMINAL_OUTPUT', 'gfxterm')
        text = set_value(text, 'GRUB_GFXMODE', 'auto')
        text = set_value(text, 'GRUB_GFXPAYLOAD_LINUX', 'keep')
        text = set_value(text, 'GRUB_FONT', '/boot/grub/fonts/unicode.pf2')
        text = set_value(text, 'GRUB_TIMEOUT_STYLE', 'menu')
        text = set_value(text, 'GRUB_TIMEOUT', '5')
    if 'plymouth-theme' in components:
        match = re.search(r'^GRUB_CMDLINE_LINUX_DEFAULT=(.*)$', text, re.M)
        value = shlex.split(match.group(1), comments=True) if match else []
        arguments = ' '.join(value).split()
        arguments += [word for word in ('quiet', 'splash') if word not in arguments]
        text = set_value(text, 'GRUB_CMDLINE_LINUX_DEFAULT', ' '.join(arguments))
    return text


def configure_target_grub(target, components):
    """Make the chosen theme accessible from /boot and configure graphics."""
    target = Path(target).resolve()
    if target == Path('/') or not (target/'etc/passwd').is_file():
        raise ValueError('Expected a mounted target filesystem, never the running root.')
    config = target/'etc/default/grub'
    if not config.resolve().is_relative_to(target):
        raise ValueError('GRUB configuration escapes the target.')
    if 'grub-theme' in components:
        source = target/'usr/share/grub/themes/zelix-aurora'
        destination = target/'boot/grub/themes/zelix-aurora'
        font = target/'boot/grub/fonts/unicode.pf2'
        for path in (source, destination, font):
            if not path.resolve().is_relative_to(target):
                raise ValueError('GRUB asset path escapes the target.')
        for name in ('theme.txt', 'background.png', 'select_c.png', 'select_w.png', 'select_e.png'):
            if not (source/name).is_file():
                raise ValueError('Missing selected GRUB theme asset: ' + name)
        source_font = target/'usr/share/grub/unicode.pf2'
        if not source_font.is_file() or not source_font.resolve().is_relative_to(target):
            raise ValueError('Missing target GRUB unicode font.')
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(source, destination, dirs_exist_ok=True)
        font.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_font, font)
    config.write_text(configure_grub(config.read_text(), components))


def payload_paths(components, desktops, greeter, bootloader):
    """Only listed paths may be copied from zelixdeps; no whole-tree overlays."""
    selected = effective_components(components, greeter, bootloader)
    paths = ['usr/share/zelix', 'usr/share/pixmaps/zelix-installer.png']
    if 'desktop-theme' in selected:
        paths.append('usr/share/wallpapers/Zelix/minimalistic.png')
        if 'kde-plasma' in desktops:
            paths += ['etc/skel/.config', 'usr/share/color-schemes',
                      'usr/share/plasma/look-and-feel',
                      'usr/share/plasma/shells/org.kde.plasma.desktop/contents/updates/00-zelix-wallpaper.js',
                      'usr/local/bin/zelix-first-login',
                      'etc/xdg/autostart/zelix-firstrun-wallpaper.desktop']
    if 'wallpapers' in selected:
        paths += ['usr/share/wallpapers/Zelix', 'usr/share/wallpapers/Zelix Extras']
    if 'sddm-theme' in selected:
        paths += ['usr/share/sddm/themes/zelix-aurora', 'etc/sddm.conf', 'etc/sddm.conf.d']
    if 'plymouth-theme' in selected:
        paths += ['usr/share/plymouth/themes/zelix-aurora', 'etc/plymouth/plymouthd.conf']
    if 'grub-theme' in selected:
        paths.append('usr/share/grub/themes/zelix-aurora')
    # Avoid copying a directory and a child file twice.
    return tuple(path for path in paths if not any(
        path != parent and path.startswith(parent + '/') for parent in paths))


def copy_payload(source, target, components, desktops, greeter, bootloader):
    source, target = Path(source).resolve(), Path(target).resolve()
    if target == Path('/') or not (target / 'etc/passwd').is_file():
        raise ValueError('Expected a mounted target filesystem, never the running root.')
    copied = []
    for relative in payload_paths(components, desktops, greeter, bootloader):
        origin, destination = source / relative, target / relative
        if not origin.exists():
            raise ValueError('Missing selected payload: ' + relative)
        if not destination.resolve().is_relative_to(target):
            raise ValueError('Payload destination escapes the target: ' + relative)
        destination.parent.mkdir(parents=True, exist_ok=True)
        if origin.is_dir():
            shutil.copytree(origin, destination, dirs_exist_ok=True)
        else:
            shutil.copy2(origin, destination)
        copied.append(relative)
    return copied


def home_errors(target):
    """Do not create empty homes over potentially missing home mounts."""
    target = Path(target).resolve()
    if target == Path('/') or not (target/'etc/passwd').is_file():
        raise ValueError('Expected a mounted target filesystem, never the running root.')
    errors = []
    for line in (target/'etc/passwd').read_text().splitlines():
        fields = line.split(':')
        if len(fields) != 7 or not fields[2].isdigit() or not 1000 <= int(fields[2]) < 65534:
            continue
        name, _, uid, gid, _, home, _ = fields
        path = target/home.lstrip('/')
        if not home.startswith('/home/') or not path.resolve().is_relative_to(target):
            errors.append('Invalid target home for user '+name)
        elif not path.is_dir():
            errors.append('Missing home directory for '+name+': '+home+'; check /home mounts before creating it.')
        elif (path.stat().st_uid, path.stat().st_gid) != (int(uid), int(gid)):
            errors.append('Wrong home ownership for '+name+': '+home)
    return errors


def verify_target(target, components, desktops, greeter, bootloader):
    """Check offline installation artifacts; this cannot prove a working login."""
    target = Path(target).resolve()
    if target == Path('/') or not (target/'etc/passwd').is_file():
        raise ValueError('Expected a mounted target filesystem, never the running root.')
    selected = effective_components(components, greeter, bootloader)
    errors = home_errors(target)

    def file(relative, executable=False):
        path = target/relative
        valid = path.resolve().is_relative_to(target) and path.is_file()
        if valid and executable:
            valid = bool(path.stat().st_mode & 0o111)
        if not valid:
            errors.append('Missing or invalid target file: '+relative)
        return path if valid else None

    if 'gnome' in desktops:
        file('usr/bin/gnome-shell', executable=True)
        file('usr/bin/gnome-session', executable=True)
        sessions = list((target/'usr/share/wayland-sessions').glob('*.desktop'))
        sessions += list((target/'usr/share/xsessions').glob('*.desktop'))
        if not any(p.resolve().is_relative_to(target) and p.is_file() and
                   re.search(r'^Exec=.*\bgnome-session\b', p.read_text(), re.M) for p in sessions):
            errors.append('No installed GNOME session entry for the display manager.')
    service = {'lightdm-gtk-greeter': 'lightdm', 'ly': 'ly@'}.get(greeter, greeter)
    if service == 'ly@' and not (target/'usr/lib/systemd/system/ly@.service').is_file():
        service = 'ly'
    file('usr/lib/systemd/system/'+service+'.service')
    if 'sddm-theme' in selected:
        file('usr/share/sddm/themes/zelix-aurora/Main.qml')
        parser = configparser.ConfigParser(interpolation=None, strict=False)
        parser.optionxform = str
        configs = sorted((target/'usr/lib/sddm/sddm.conf.d').glob('*.conf'))
        configs += sorted((target/'etc/sddm.conf.d').glob('*.conf'))
        configs += [target/'etc/sddm.conf']
        for path in configs:
            if path.exists():
                if not path.resolve().is_relative_to(target):
                    errors.append('SDDM configuration escapes the target.')
                    continue
                parser.read(path)
        if parser.get('Theme', 'Current', fallback='') != 'zelix-aurora':
            errors.append('Selected SDDM theme is not active in the effective configuration.')
    if 'plymouth-theme' in selected:
        file('usr/share/plymouth/themes/zelix-aurora/zelix-aurora.plymouth')
        file('usr/share/plymouth/themes/zelix-aurora/zelix-aurora.script')
        conf = file('etc/plymouth/plymouthd.conf')
        if conf and not re.search(r'^Theme\s*=\s*zelix-aurora\s*$', conf.read_text(), re.M):
            errors.append('Selected Plymouth theme is not configured.')
        hooks = file('etc/mkinitcpio.conf')
        if hooks and not re.search(r'^HOOKS=.*\bplymouth\b', hooks.read_text(), re.M):
            errors.append('Plymouth is missing from mkinitcpio HOOKS.')
    if bootloader == 'Grub':
        config = file('boot/grub/grub.cfg')
        if config and not re.search(r'^\s*menuentry\s+[^\n]*ZelixOS', config.read_text(), re.M):
            errors.append('Generated GRUB configuration has no ZelixOS menu entry.')
        if 'grub-theme' in selected:
            file('boot/grub/themes/zelix-aurora/theme.txt')
            file('boot/grub/fonts/unicode.pf2')
    report = {'desktops': desktops, 'greeter': greeter, 'bootloader': bootloader,
              'components': list(selected), 'errors': errors,
              'offline_checks_passed': not errors, 'login_and_reboot_tested': False}
    destination = target/'var/log/zelix-installer/verification.json'
    if not destination.resolve().is_relative_to(target):
        raise ValueError('Verification report escapes the target.')
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(report, indent=2)+'\n')
    if errors:
        raise ValueError('Target verification failed: '+'; '.join(errors))
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('validate', 'copy', 'verify', 'users'))
    parser.add_argument('components', help='Comma-separated IDs, or - for none')
    parser.add_argument('desktops')
    parser.add_argument('greeter')
    parser.add_argument('bootloader')
    parser.add_argument('source', nargs='?')
    parser.add_argument('target', nargs='?')
    args = parser.parse_args()
    selected = [] if args.components == '-' else args.components.split(',')
    effective_components(selected, args.greeter, args.bootloader)
    if args.action in ('copy', 'verify', 'users'):
        if not args.source or not args.target:
            parser.error(args.action+' requires source and target')
        if args.action == 'users':
            if errors := home_errors(args.target):
                raise ValueError('; '.join(errors))
            print('Target user home directories verified.')
            return
        if args.action == 'verify':
            verify_target(args.target, selected, args.desktops.split(','), args.greeter, args.bootloader)
            print('Offline target verification passed; real login/reboot still requires testing.')
            return
        for relative in copy_payload(args.source, args.target, selected,
                                     args.desktops.split(','), args.greeter, args.bootloader):
            print('Installed payload:', relative)


if __name__ == '__main__':
    main()
