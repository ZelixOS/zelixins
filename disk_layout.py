"""Pure disk-layout policy and Archinstall-compatible serialization."""
import uuid

FILESYSTEMS = ('ext4', 'btrfs', 'xfs', 'f2fs', 'ext3', 'ext2')
OTHER_FORMATS = ('fat12', 'fat16', 'fat32', 'ntfs', 'linux-swap')
FILESYSTEM_PACKAGES = {'btrfs': 'btrfs-progs', 'xfs': 'xfsprogs', 'f2fs': 'f2fs-tools'}
MIN_ROOT_MIB = 20 * 1024
MIN_HOME_MIB = 8 * 1024


def partition_device(disk, number):
    return f'{disk}{"p" if disk[-1].isdigit() else ""}{number}'


def validate_encryption(password, confirmation):
    if len(password) < 8 or '\n' in password or '\x00' in password:
        raise ValueError('disk_password_short')
    if password != confirmation:
        raise ValueError('error_passwords_mismatch')


def build_partitions(size_bytes, uefi, kernel_count, root_fs='ext4', separate_home=False,
                     home_fs='ext4', root_gib=50, compression=True):
    if root_fs not in FILESYSTEMS or home_fs not in FILESYSTEMS:
        raise ValueError('disk_invalid_filesystem')
    if size_bytes < 25 * 1024**3:
        raise ValueError('policy_disk_size')
    if kernel_count < 1:
        raise ValueError('policy_kernel')
    boot_mib = max(1024, 512 * kernel_count)
    usable_mib = size_bytes // (1024**2) - boot_mib - 2
    root_mib = int(root_gib * 1024) if separate_home else usable_mib
    home_mib = usable_mib - root_mib if separate_home else 0
    if root_mib < MIN_ROOT_MIB or (separate_home and home_mib < MIN_HOME_MIB):
        raise ValueError('disk_layout_space')

    def part(start, size, fs, mount, flags):
        def units(value):
            return {'sector_size': {'unit': 'B', 'value': 512}, 'unit': 'MiB', 'value': value}
        options = ['noatime', 'compress=zstd'] if fs == 'btrfs' and compression else []
        return {'btrfs': [], 'flags': flags, 'fs_type': fs, 'start': units(start),
                'size': units(size), 'mount_options': options, 'mountpoint': mount,
                'status': 'create', 'type': 'primary', 'dev_path': None, 'obj_id': str(uuid.uuid4())}
    partitions = [part(1, boot_mib, 'fat32' if uefi else 'ext4', '/boot',
                       ['boot', 'esp'] if uefi else ['boot']),
                  part(1 + boot_mib, root_mib, root_fs, '/', [])]
    if root_fs == 'btrfs':
        root = partitions[1]
        root['mountpoint'] = None
        root['btrfs'] = [
            {'name': '@', 'mountpoint': '/'},
            {'name': '@log', 'mountpoint': '/var/log'},
            {'name': '@cache', 'mountpoint': '/var/cache'},
            {'name': '@snapshots', 'mountpoint': '/.snapshots'},
        ]
        if not separate_home:
            root['btrfs'].append({'name': '@home', 'mountpoint': '/home'})
    if separate_home:
        partitions.append(part(1 + boot_mib + root_mib, home_mib, home_fs, '/home', []))
    return partitions


def encryption_configuration(partitions):
    return {'encryption_type': 'luks',
            'partitions': [p['obj_id'] for p in partitions if p['mountpoint'] != '/boot'],
            'lvm_volumes': []}


def mount_specs(config):
    """Derive a strict post-install mount plan from the exact generated layout."""
    layout = config['disk_config']
    devices = layout['device_modifications']
    if len(devices) != 1:
        raise ValueError('Expected one installation disk.')
    disk = devices[0]['device']
    if not disk.startswith('/dev/') or '..' in disk.split('/'):
        raise ValueError('Invalid installation disk.')
    encrypted = set(layout.get('disk_encryption', {}).get('partitions', []))
    encryption = layout.get('disk_encryption')
    if encryption and (encryption.get('encryption_type') != 'luks' or encryption.get('lvm_volumes')):
        raise ValueError('Post-install mounting supports partition-based LUKS only.')
    result = []
    partitions = devices[0]['partitions']
    ids = {part['obj_id'] for part in partitions}
    if not encrypted.issubset(ids):
        raise ValueError('Unknown encrypted partition ID.')
    allowed_mounts = {'/', '/boot', '/home', '/var/log', '/var/cache', '/.snapshots'}
    for index, part in enumerate(partitions, 1):
        filesystem = part['fs_type']
        if filesystem not in (*FILESYSTEMS, 'fat32') or part['status'] != 'create':
            raise ValueError('Unsupported partition layout.')
        options = list(part['mount_options'])
        if set(options) - {'noatime', 'compress=zstd'}:
            raise ValueError('Unsupported mount options.')
        subvolumes = part['btrfs']
        if subvolumes and filesystem != 'btrfs':
            raise ValueError('Subvolumes require Btrfs.')
        mounts = subvolumes or [{'name': None, 'mountpoint': part['mountpoint']}]
        for item in mounts:
            point = item['mountpoint']
            if point not in allowed_mounts:
                raise ValueError('Unexpected mountpoint.')
            name = item['name']
            if name is not None:
                if name not in {'@', '@home', '@log', '@cache', '@snapshots'}:
                    raise ValueError('Unexpected subvolume.')
                mount_options = options + ['subvol=' + name]
            else:
                mount_options = options
            is_encrypted = part['obj_id'] in encrypted
            if point == '/boot' and is_encrypted:
                raise ValueError('The boot partition must remain unencrypted.')
            result.append({'device': partition_device(disk, index), 'mountpoint': point,
                           'filesystem': filesystem, 'options': mount_options, 'encrypted': is_encrypted})
    points = [item['mountpoint'] for item in result]
    if points.count('/') != 1 or points.count('/boot') != 1 or len(points) != len(set(points)):
        raise ValueError('Invalid or duplicate target mountpoints.')
    return sorted(result, key=lambda item: (len(item['mountpoint'].split('/')), item['mountpoint']))
