#!/usr/bin/env python3
"""Package an ESP-IDF application image; never writes to a device.

Example:
  python3 scripts/package-cardputer.py --partition-table /path/to/default_8MB.csv
The supplied CSV describes the build, not the device's current Launcher layout.
"""
import argparse
import csv
import hashlib
import io
import json
from pathlib import Path
import struct
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def number(value):
    value = value.strip()
    if value[-1:].upper() in ('K', 'M'):
        return int(value[:-1], 0) * {'K': 1024, 'M': 1024 * 1024}[value[-1].upper()]
    return int(value, 0)


def partition_info(path, image_size):
    data = path.read_bytes()
    rows = []
    slots = []
    for row in csv.reader(io.StringIO(data.decode('utf-8-sig'))):
        if not row or not row[0].strip() or row[0].lstrip().startswith('#'):
            continue
        if len(row) < 5:
            raise ValueError('Partition CSV row requires at least five fields')
        name, kind, subtype, offset, size = (x.strip() for x in row[:5])
        entry = {'name': name, 'type': kind, 'subtype': subtype,
                 'offset': offset or 'auto', 'size_bytes': number(size)}
        rows.append(entry)
        if kind in ('app', '0', '0x00', '0x0'):
            slots.append({**entry, 'image_fits': image_size <= entry['size_bytes']})
    if not slots or not any(slot['image_fits'] for slot in slots):
        raise ValueError('Application does not fit any app slot in supplied partition table')
    return {'path': str(path.resolve()), 'sha256': sha256(data),
            'partitions': rows, 'app_slots': slots,
            'evidence': 'supplied_build_csv_not_device_layout'}


def git_source(root):
    def run(*args):
        result = subprocess.run(['git', '-C', str(root), *args],
                                capture_output=True, text=True, check=False)
        return result.stdout.strip() if result.returncode == 0 else None
    commit = run('rev-parse', 'HEAD')
    status = run('status', '--porcelain=v1') if commit else None
    return {'commit': commit, 'dirty': bool(status) if status is not None else None,
            'status': status.splitlines() if status is not None else None,
            'provenance': 'packaging_time_checkout_not_proof_of_build_source'}


def package(binary, output, partition_table=None, source_root=ROOT):
    binary, output = Path(binary), Path(output)
    data = binary.read_bytes()
    # ESP-IDF's app descriptor follows the image header and first segment header.
    # Bootloaders and merged flash images do not have this application marker here.
    if (len(data) < 288 or data[0] != 0xE9 or data[1] == 0
            or struct.unpack_from('<I', data, 32)[0] != 0xABCD5432):
        raise ValueError('Expected ESP-IDF application-only firmware.bin, not a bootloader or merged image')
    manifest = {
        'schema_version': 1,
        'artifact': 'paxcounter-cardputer-adv.bin',
        'image_type': 'application_only',
        'size_bytes': len(data),
        'sha256': sha256(data),
        'source': git_source(source_root),
        'partition_table': partition_info(Path(partition_table), len(data)) if partition_table else None,
        'launcher_validation': 'not_verified',
        'hardware_validation': 'not_verified',
    }
    output.mkdir(parents=True, exist_ok=True)
    (output / manifest['artifact']).write_bytes(data)
    (output / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    (output / 'SHA256SUMS').write_text(f"{manifest['sha256']}  {manifest['artifact']}\n")
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--binary', type=Path, default=ROOT / '.pio/build/cardputer-adv/firmware.bin')
    parser.add_argument('--output', type=Path, default=ROOT / 'dist/cardputer-adv')
    parser.add_argument('--partition-table', type=Path,
                        help='Build CSV; if omitted, partition evidence is recorded as unknown')
    args = parser.parse_args()
    try:
        manifest = package(args.binary, args.output, args.partition_table)
    except (OSError, ValueError) as error:
        parser.exit(1, f'Packaging failed: {error}\n')
    print(f"{args.output / manifest['artifact']}: {manifest['size_bytes']} bytes")
    print(f"SHA-256: {manifest['sha256']}")
    print('Launcher installation and hardware behavior: not verified')


if __name__ == '__main__':
    main()
