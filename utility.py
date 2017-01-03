import os
import tempfile
import shutil

import scandir
import subprocess32 as subprocess


path_sep = '/'


def get_project_by_path(path):
    pl = path.split(path_sep)
    if pl[0] == '':
        return pl[1]
    else:
        return pl[0]


class ZipExtractController(object):
    def __init__(self, zip_paths):
        if isinstance(zip_paths, str):
            self.zip_paths = [zip_paths]
        elif isinstance(zip_paths, list):
            self.zip_paths = zip_paths
        else:
            raise ValueError('{} parameter error'.format(self.__class__))
        self.temp_dir = None

    def __enter__(self):
        self.temp_dir = tempfile.mkdtemp(dir='/tmp')
        for zip_path in self.zip_paths:
            ex = ['unzip', zip_path, '-d', tempfile.mkdtemp(dir=self.temp_dir)]
            subprocess.call(ex)
        return self.temp_dir

    def __exit__(self, exc_type, exc_val, exc_tb):
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            self.temp_dir = None
        if exc_type is None:
            pass
        else:
            return False


def scan_dir(dir_path):
    def inner_scan_project(in_path):
        for entry in scandir.scandir(in_path):
            # print entry.path
            if entry.is_dir():
                for ii in inner_scan_project(entry.path):
                    yield ii
            elif entry.is_file():
                yield entry.path
    for i in inner_scan_project(dir_path):
        yield i
