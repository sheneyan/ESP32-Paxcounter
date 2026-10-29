import importlib.util
import json
from pathlib import Path
import struct
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/package-cardputer.py'

class PackageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location('package_cardputer', SCRIPT)
        cls.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.module)

    def setup_files(self, root):
        app = bytearray(320)
        app[0] = 0xE9
        app[1] = 1
        struct.pack_into('<I', app, 28, 256)
        struct.pack_into('<I', app, 32, 0xABCD5432)
        path = root / 'firmware.bin'
        path.write_bytes(app)
        return path

    def test_package_preserves_application_and_marks_launcher_unverified(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            binary = self.setup_files(root)
            original = binary.read_bytes()
            csv = root / 'partitions.csv'
            csv.write_text('# Name, Type, SubType, Offset, Size, Flags\nnvs,data,nvs,0x9000,0x5000,\napp0,app,ota_0,0x10000,1M,\napp1,0,ota_1,0x110000,0x100000,\n')
            manifest = self.module.package(binary, root / 'out', csv, root)
            self.assertEqual((root / 'out' / 'paxcounter-cardputer-adv.bin').read_bytes(), original)
            self.assertEqual(manifest['size_bytes'], len(original))
            self.assertEqual(manifest['partition_table']['app_slots'][0]['size_bytes'], 1048576)
            self.assertEqual(len(manifest['partition_table']['app_slots']), 2)
            self.assertEqual(manifest['launcher_validation'], 'not_verified')
            self.assertIsNone(manifest['source']['commit'])
            self.assertEqual(json.loads((root / 'out' / 'manifest.json').read_text()), manifest)

    def test_rejects_bootloader_or_merged_image(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            binary = root / 'firmware.bin'
            binary.write_bytes(b'\xe9' + bytes(319))
            with self.assertRaisesRegex(ValueError, 'application'):
                self.module.package(binary, root / 'out', None, root)
            self.assertFalse((root / 'out').exists())

    def test_rejects_image_that_fits_no_app_slot(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            binary = self.setup_files(root)
            csv = root / 'partitions.csv'
            csv.write_text('app0,app,ota_0,0x10000,256,\n')
            with self.assertRaisesRegex(ValueError, 'fit'):
                self.module.package(binary, root / 'out', csv, root)
            self.assertFalse((root / 'out').exists())

    def test_without_partition_evidence_is_explicitly_unknown(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            manifest = self.module.package(self.setup_files(root), root / 'out', None, root)
            self.assertIsNone(manifest['partition_table'])

if __name__ == '__main__':
    unittest.main()
