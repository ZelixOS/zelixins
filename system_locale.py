#!/usr/bin/env python3
"""Apply the selected language to an offline target and its desktop users."""
import configparser
import json
import os
from pathlib import Path
import re
import sys
from desktop_catalog import desktops_for

SYSTEM_LANGUAGES = (
    ('English', 'en_US.UTF-8'),
    ('Türkçe', 'tr_TR.UTF-8'),
    ('Español', 'es_ES.UTF-8'),
)
UI_LOCALES = dict(zip(('en', 'tr', 'es'), (locale for _, locale in SYSTEM_LANGUAGES)))


def configure_locale(target, locale, desktops):
    if locale not in UI_LOCALES.values():
        raise ValueError('Unsupported system language: ' + str(locale))
    selected = {desktop.slug for desktop in desktops_for(desktops)}
    target = Path(target).resolve()
    if target == Path('/') or not (target/'etc/passwd').is_file():
        raise ValueError('Expected a mounted target filesystem, never the running root.')
    short = locale.split('_')[0]
    language = 'en_US:en' if short == 'en' else short+':en_US:en'
    changed = []

    def safe(path):
        if not path.resolve().is_relative_to(target):
            raise ValueError('Locale path escapes the target: ' + str(path))
        return path

    def write(path, text, mode=0o644, owner=None):
        safe(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding='utf-8')
        path.chmod(mode)
        if owner is not None and os.geteuid() == 0:
            os.chown(path, *owner)
        changed.append(path)

    def ini(path, values, mode=0o644, owner=None):
        safe(path)
        parser = configparser.ConfigParser(interpolation=None, strict=False)
        parser.optionxform = str
        if path.exists():
            parser.read(path, encoding='utf-8')
        for section, entries in values.items():
            if not parser.has_section(section):
                parser.add_section(section)
            if section == 'Formats' and 'LANG' in entries:
                # Old per-category values can override the selected Plasma locale.
                for key in list(parser[section]):
                    if key == 'LC_ALL':
                        parser.remove_option(section, key)
                    elif key.startswith('LC_'):
                        parser.set(section, key, locale)
            for key, value in entries.items():
                parser.set(section, key, value)
        import io
        stream = io.StringIO()
        parser.write(stream, space_around_delimiters=False)
        write(path, stream.getvalue(), mode, owner)

    values = {'LANG': locale, 'LC_MESSAGES': locale, 'LANGUAGE': language}
    # Keep unrelated environment settings; remove conflicting locale overrides.
    for relative in ('etc/locale.conf', 'etc/environment'):
        path = safe(target/relative)
        lines = path.read_text().splitlines() if path.exists() else []
        lines = [line for line in lines if not re.match(r'^\s*(?:export\s+)?(?:LANG|LANGUAGE|LC_[A-Z_]+)\s*=', line)]
        lines.extend(key+'='+value for key, value in values.items())
        write(path, '\n'.join(lines)+'\n')
    gen = safe(target/'etc/locale.gen')
    lines = gen.read_text().splitlines() if gen.exists() else []
    for required in dict.fromkeys((locale, 'en_US.UTF-8')):
        entry = required+' UTF-8'
        match = next((i for i, line in enumerate(lines) if line.lstrip('# ').strip() == entry), None)
        if match is None:
            lines.append(entry)
        else:
            lines[match] = entry
    write(gen, '\n'.join(lines)+'\n')

    def user_defaults(home, owner=None):
        ini(home/'.dmrc', {'Desktop': {'Language': locale}}, owner=owner)
        if 'kde-plasma' in selected:
            path = home/'.config/plasma-localerc'
            ini(path, {'Formats': {'LANG': locale}, 'Translations': {'LANGUAGE': language}}, owner=owner)
            if owner is not None and os.geteuid() == 0:
                os.chown(home/'.config', *owner)

    user_defaults(target/'etc/skel')
    for line in (target/'etc/passwd').read_text().splitlines():
        fields = line.split(':')
        if len(fields) != 7:
            continue
        name, _, uid, gid, _, home, _ = fields
        if not 1000 <= int(uid) < 65534 or not home.startswith('/home/'):
            continue
        if not re.fullmatch(r'[a-z_][a-z0-9_-]*', name):
            raise ValueError('Invalid target user name.')
        folder = safe(target/home.lstrip('/'))
        if not folder.is_dir():
            raise ValueError('Missing target user home: ' + home)
        user_defaults(folder, (int(uid), int(gid)))
        # GDM/GNOME read the user's language through AccountsService at login.
        account = target/'var/lib/AccountsService/users'/name
        ini(account, {'User': {'Language': locale}}, mode=0o600)
    return changed


def main():
    target, config, desktops = sys.argv[1:]
    data = json.loads(Path(config).read_text())
    locale = data['locale_config']['sys_lang']
    if '.' not in locale:
        locale += '.'+data['locale_config']['sys_enc']
    configure_locale(target, locale, desktops.split(','))
    print('Configured system and desktop language:', locale)


if __name__ == '__main__':
    main()
