#!/usr/bin/python3

import os
import subprocess
import tempfile
import unittest
from s3_app import tar_dir, s3_copy


class apptest(unittest.TestCase):

    def test_s3_copy(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            test_dir = os.path.join(tmpdir, 'test')
            os.mkdir(test_dir)
            tar_file = os.path.join(test_dir, 'test.tar')
            with open(tar_file, 'w') as f:
                f.write('test')
            # upload failed
            s3_copy(test_dir, aws='/bin/false')
            self.assertTrue(os.path.exists(tar_file))
            s3_copy(test_dir, aws='/bin/true')
            self.assertFalse(os.path.exists(tar_file))

    def test_tar_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tar_file = os.path.join(tmpdir, 'test.tar')
            telem_dir = os.path.join(tmpdir, 'test')
            telem_file = os.path.join(telem_dir, 'blah.json')
            ignored_file = os.path.join(telem_dir, '.ignored_json')
            os.mkdir(telem_dir)
            for test_file in (telem_file, ignored_file):
                with open(test_file, 'w') as f:
                    f.write(test_file)
            tar_dir(telem_dir, tar_file, xz=True)
            self.assertTrue(os.path.exists, tar_file)
            in_tar = set()
            with subprocess.Popen(['/usr/bin/tar', 'Jtvf', tar_file], stdout=subprocess.PIPE) as s:
                for tar_line in s.stdout.readlines():
                    tar_line = tar_line.decode('utf-8').strip().split(' ')
                    in_tar.add(tar_line[-1])
            self.assertTrue(os.path.basename(telem_file) in in_tar)
            self.assertFalse(os.path.basename(ignored_file) in in_tar)
            self.assertTrue(os.path.exists(ignored_file))
            self.assertFalse(os.path.exists(telem_file))


if __name__ == '__main__':
    unittest.main()
