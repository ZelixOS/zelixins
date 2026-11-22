"""Mount the generated install layout for post-install; never format devices."""
import argparse
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import uuid
import tempfile
from disk_layout import mount_specs


def run(command, **kwargs):
    return subprocess.run(command, check=True, capture_output=True, **kwargs)


def check_block(path):
    if not stat.S_ISBLK(Path(path).stat().st_mode):
        raise ValueError('Expected a block device: ' + str(path))


def existing_mapper(device):
    data = json.loads(run(['lsblk', '--json', '--paths', '--output', 'PATH,TYPE', device], text=True).stdout)
    found = []
    def visit(node):
        if node['type'] == 'crypt':
            found.append(node['path'])
        for child in node.get('children', []):
            visit(child)
    for node in data['blockdevices']:
        visit(node)
    if len(found) > 1:
        raise ValueError('Multiple open mappings for the selected partition; refusing an ambiguous mount.')
    if found:
        check_block(found[0])
        return found[0]
    return None


def read_password(path):
    path = Path(path)
    if path.stat().st_mode & 0o077:
        raise ValueError('The credentials file must be private (0600).')
    password = json.loads(path.read_text()).get('encryption_password', '')
    if not isinstance(password, str) or len(password) < 8 or '\n' in password or '\x00' in password:
        raise ValueError('Missing or invalid encryption credentials.')
    return password.encode('utf-8')


def save_state(path, state):
    with open(path, 'w', encoding='utf-8') as stream:
        os.fchmod(stream.fileno(), 0o600)
        json.dump(state, stream)


def release(state):
    target = Path(state['target']).resolve()
    if target == Path('/') or not target.name.startswith('zelix-target.'):
        raise ValueError('Invalid managed mount target.')
    errors = []
    for point in list(reversed(state['mounts'])):
        path = Path(point)
        if not path.resolve().is_relative_to(target):
            raise ValueError('Mount state escapes the installation target.')
        try:
            run(['umount', '--', str(path)])
            state['mounts'].remove(point)
        except subprocess.SubprocessError:
            errors.append(str(path))
    # Never close a mapping while any managed mount is still in use.
    if errors:
        raise RuntimeError('Cannot unmount target paths: ' + ', '.join(errors))
    for mapper in list(reversed(state['opened_mappers'])):
        if not re.fullmatch(r'zelixins-[a-f0-9]{32}-[0-9]+', mapper):
            raise ValueError('Unexpected mapper in cleanup state.')
        run(['cryptsetup', 'close', mapper])
        state['opened_mappers'].remove(mapper)


def mount_target(config_path, creds_path, target, state_path, root_device=None, boot_device=None, home_device=None):
    target = Path(target).resolve()
    if target == Path('/') or not target.name.startswith('zelix-target.') or not target.is_dir() or any(target.iterdir()):
        raise ValueError('Expected a new empty Zelix installation mount directory.')
    specs = mount_specs(json.loads(Path(config_path).read_text()))
    if root_device is not None:
        root = next(item['device'] for item in specs if item['mountpoint'] == '/')
        boot = next(item['device'] for item in specs if item['mountpoint'] == '/boot')
        home = next((item['device'] for item in specs if item['mountpoint'] == '/home' and item['device'] != root), '-')
        if (root, boot, home) != (root_device, boot_device, home_device):
            raise ValueError('Partition arguments do not match the generated installation plan.')
    for device in {item['device'] for item in specs}:
        check_block(device)
    state = {'target': str(target), 'mounts': [], 'opened_mappers': []}
    save_state(state_path, state)
    devices = {}
    password = None
    token = uuid.uuid4().hex
    try:
        for spec in specs:
            device = spec['device']
            if device not in devices:
                source = device
                if spec['encrypted']:
                    source = existing_mapper(device)
                    if source is None:
                        if password is None:
                            password = read_password(creds_path)
                        name = f'zelixins-{token}-{len(devices)}'
                        # The password is sent over stdin, never argv, the environment, or logs.
                        run(['cryptsetup', 'open', '--type', 'luks', '--key-file', '-', device, name], input=password)
                        state['opened_mappers'].append(name)
                        save_state(state_path, state)
                        source = '/dev/mapper/' + name
                devices[device] = source
            destination = target / spec['mountpoint'].lstrip('/')
            if not destination.resolve().is_relative_to(target):
                raise ValueError('Target mountpoint resolves outside the installation root.')
            destination.mkdir(parents=True, exist_ok=True)
            command = ['mount', '-t', 'vfat' if spec['filesystem'] == 'fat32' else spec['filesystem']]
            if spec['options']:
                command += ['-o', ','.join(spec['options'])]
            command += ['--', devices[device], str(destination)]
            run(command)
            state['mounts'].append(str(destination))
            save_state(state_path, state)
    except Exception:
        try:
            release(state)
        finally:
            save_state(state_path, state)
        raise
    finally:
        password = None
    print('Post-install filesystems mounted successfully.')
    return state


def validate_fstab(text, specs, mounted_uuids):
    """Require every planned filesystem and Btrfs subvolume, with stable IDs."""
    entries = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        fields = line.split()
        if len(fields) < 4:
            raise ValueError('Malformed fstab entry.')
        entries.setdefault(fields[1], []).append(fields)
    for spec in specs:
        point = spec['mountpoint']
        matches = entries.get(point, [])
        if len(matches) != 1:
            raise ValueError('Expected exactly one fstab entry for '+point)
        source, _, filesystem, options = matches[0][:4]
        if source != 'UUID='+mounted_uuids[point]:
            raise ValueError('fstab UUID does not match mounted target: '+point)
        expected_fs = 'vfat' if spec['filesystem'] == 'fat32' else spec['filesystem']
        if filesystem != expected_fs:
            raise ValueError('fstab filesystem does not match installation plan: '+point)
        opts = options.split(',')
        expected_subvol = next((o.split('=', 1)[1] for o in spec['options'] if o.startswith('subvol=')), None)
        if expected_subvol is not None:
            actual_subvols = [o.split('=', 1)[1].lstrip('/') for o in opts if o.startswith('subvol=')]
            if actual_subvols != [expected_subvol]:
                raise ValueError('fstab Btrfs subvolume does not match installation plan: '+point)


def render_fstab(specs, mounted_uuids):
    """Serialize only the installer's allowlisted, verified target mounts."""
    lines = ['# ZelixOS: generated from the verified installation mount plan.']
    for spec in specs:
        point = spec['mountpoint']
        uuid_value = mounted_uuids[point]
        if not re.fullmatch(r'[A-Za-z0-9-]+', uuid_value):
            raise ValueError('Invalid filesystem UUID for '+point)
        filesystem = 'vfat' if spec['filesystem'] == 'fat32' else spec['filesystem']
        options = ','.join(spec['options']) or 'defaults'
        check = 0 if filesystem in ('btrfs', 'xfs') else 1 if point == '/' else 2
        lines.append(f'UUID={uuid_value} {point} {filesystem} {options} 0 {check}')
    return '\n'.join(lines)+'\n'


def ensure_target_fstab(config_path, target):
    """Repair only the mounted installer target; never use the host mount tree."""
    target = Path(target).resolve()
    if target == Path('/') or not target.name.startswith('zelix-target.') or not (target/'etc/passwd').is_file():
        raise ValueError('Expected a mounted Zelix installation target.')
    config = json.loads(Path(config_path).read_text())
    specs = mount_specs(config)
    uuids = {}
    for spec in specs:
        point = target/spec['mountpoint'].lstrip('/')
        if not point.resolve().is_relative_to(target):
            raise ValueError('fstab mountpoint escapes the target.')
        # --mountpoint requires this exact mount, rather than its parent filesystem.
        value = run(['findmnt', '--noheadings', '--output', 'UUID', '--mountpoint', str(point)], text=True).stdout.strip()
        if not re.fullmatch(r'[A-Za-z0-9-]+', value):
            raise ValueError('Missing unique filesystem UUID at target mount: '+spec['mountpoint'])
        uuids[spec['mountpoint']] = value
    path = target/'etc/fstab'
    backup = target/'etc/fstab.before-zelix'
    if not path.resolve().is_relative_to(target) or not backup.resolve().is_relative_to(target):
        raise ValueError('fstab path escapes the target.')
    original = path.read_text() if path.exists() else ''
    try:
        validate_fstab(original, specs, uuids)
        print('Target fstab matches all planned filesystems and subvolumes.')
        return False
    except ValueError as error:
        print('Regenerating invalid target fstab:', error)
    # Do not repeat a failed/partial genfstab scan. All mounts above have been
    # checked individually; the layout already defines their filesystem/options.
    generated = render_fstab(specs, uuids)
    validate_fstab(generated, specs, uuids)
    if path.exists() and not backup.exists():
        backup.write_text(original)
        backup.chmod(0o600)
    staged = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', dir=path.parent, prefix='.zelix-fstab-', delete=False) as stream:
            staged = Path(stream.name)
            os.fchmod(stream.fileno(), 0o644)
            stream.write(generated)
            stream.flush()
            os.fsync(stream.fileno())
        staged.replace(path)
    finally:
        if staged is not None:
            staged.unlink(missing_ok=True)
    print('Target fstab regenerated and verified for', len(specs), 'mountpoints.')
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('mount', 'unmount', 'fstab'))
    parser.add_argument('paths', nargs='+')
    args = parser.parse_args()
    if os.geteuid() != 0:
        parser.error('Root privileges are required.')
    if args.action == 'fstab':
        if len(args.paths) != 2:
            parser.error('fstab requires CONFIG TARGET')
        ensure_target_fstab(*args.paths)
    elif args.action == 'mount':
        if len(args.paths) not in (4, 7):
            parser.error('mount requires CONFIG CREDS TARGET STATE [ROOT BOOT HOME]')
        mount_target(*args.paths)
    else:
        if len(args.paths) != 1:
            parser.error('unmount requires STATE')
        state_file = Path(args.paths[0])
        if state_file.is_file() and state_file.stat().st_size:
            state = json.loads(state_file.read_text())
            try:
                release(state)
            finally:
                save_state(state_file, state)


if __name__ == '__main__':
    main()
