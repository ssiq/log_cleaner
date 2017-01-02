from collections import defaultdict

import scandir

import constant
from log_transformer import read_log


class LogNoMatchException(Exception):
    pass


class CppFile(object):
    '''
    This class is used to maintain a cpp file content
    '''
    def __init__(self, c=None):
        if c is not None:
            self.content = c
        else:
            self.content = []

    def _check_offset(self, offset):
        if offset > len(self.content):
            raise LogNoMatchException

    def insert(self, offset, content, insert_max_length=50):
        offset = int(offset)
        # self._check_offset(offset)
        # if insert_max_length != -1 and len(content) > insert_max_length:
        #     raise LogNoMatchException
        for i in xrange(len(content)):
            self.content.insert(offset+i, content[i])

    def remove(self, offset, length):
        offset = int(offset)
        length = int(length)
        # self._check_offset(offset)
        del self.content[offset:offset+length]

    def __str__(self):
        return ''.join(self.content)

    def __eq__(self, other):
        if not isinstance(other, CppFile):
            return False
        return self.content == other.content


class Project(object):
    '''
    This class is used to maintain the project
    '''
    def __init__(self):
        self.projects = defaultdict(lambda: CppFile())

    def add_file(self, path, f=CppFile()):
        if path in self.projects:
            raise Exception('re create one file with same path')
        else:
            self.projects[path] = f

    def delete_file(self, path):
        del self.projects[path]

    def get_file(self, path):
        return self.projects[path]

    def __eq__(self, other):
        if not isinstance(other, Project):
            return False
        return self.projects == other.projects

    def __str__(self):
        s = ''
        for k, v in self.projects.items():
            s += 'file {}\n {} \n\n'.format(k, str(v))
        return s


def rebuild_one_project(log, insert_max_length=50):
    '''
    :paam log: A TransformedLog object which contains the log information
    :return: a Project object rebuilt from the input log object
    '''
    project = Project()
    for action in log.to_list():
        print action
        print
        if action[constant.ACTION_TYPE] == constant.EDIT:
            if action[constant.OPERATION_TYPE] == constant.INSERT:
                text = action[constant.TEXT]
                offset = action[constant.FILEOFFSET]
                file_path = action[constant.FILEPATH]
                cpp_file = project.get_file(file_path)
                cpp_file.insert(offset, text, insert_max_length=insert_max_length)
            elif action[constant.OPERATION_TYPE] == constant.DELETE:
                file_path = action[constant.FILEPATH]
                offset = action[constant.FILEOFFSET]
                length = action[constant.LENGTH]
                project.get_file(file_path).remove(offset, length)
            elif action[constant.OPERATION_TYPE] == constant.RESOURCE:
                if not (action[constant.RESOURCE_PATH].endswith('.cpp') or
                        action[constant.RESOURCE_PATH].endswith('.h')):
                    continue
                if action[constant.TYPE] == constant.DELETE:
                    project.delete_file(action[constant.RESOURCE_PATH])
    return project


def scan_project(path):
    '''
    :param path: the project base path
    :return: a Project object built by scanning the project directory from the path
    '''
    def inner_scan_project(in_path, in_project):
        for entry in scandir.scandir(in_path):
            # print entry.path
            if entry.is_dir():
                inner_scan_project(entry.path, in_project)
            elif entry.is_file():
                if entry.path.endswith('.cpp') or entry.path.endswith('.h'):
                    with open(entry.path, 'rb') as f:
                        c = f.read()
                        cpp_file = CppFile(list(c))
                    p = entry.path[len(path):]
                    p = p.replace('\\', '/')
                    in_project.add_file(p, cpp_file)
    project = Project()
    inner_scan_project(path, project)
    return project


if __name__ == '__main__':
    import sys
    from utility import ZipExtractController
    log_path, project_path = sys.argv[1], sys.argv[2]
    with ZipExtractController(log_path) as log_dir_path, ZipExtractController(project_path) as project_dir_path:
        # print project_dir_path
        #project = scan_project(project_dir_path)
        # print project
        log = read_log(log_dir_path)
        rebuilt_project = rebuild_one_project(log, -1)
        print rebuilt_project

