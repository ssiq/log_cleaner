from collections import defaultdict

import scandir

import constant


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

    def insert(self, offset, content):
        self._check_offset(offset)
        for i in xrange(len(content)):
            self.content.insert(offset+i, content[i])

    def remove(self, offset, length):
        self._check_offset(offset)
        del self.content[offset:offset+length]

    def __str__(self):
        print len(self.content)
        print self.content
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


def rebuild_one_project(log):
    '''
    :paam log: A TransformedLog object which contains the log information
    :return: a Project object rebuilt from the input log object
    '''
    project = Project()
    for action in log:
        if action[constant.ACTION_TYPE] == constant.EDIT:
            if action[constant.OPERATION_TYPE] == constant.INSERT:
                text = action[constant.TEXT]
                offset = action[constant.FILEOFFSET]
                file_path = action[constant.FILEPATH]
                cpp_file = project.get_file(file_path)
                cpp_file.insert(offset, text)
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
    def inner_scan_project(path, project):
        for entry in scandir.scandir(path):
            # print entry.path
            if entry.is_dir():
                inner_scan_project(entry.path, project)
            elif entry.is_file():
                if entry.path.endswith('.cpp') or entry.path.endswith('.h'):
                    with open(entry.path, 'rb') as f:
                        c = f.read()
                        cpp_file = CppFile(list(c))
                    p = entry.path[1:]
                    p = p.replace('\\', '/')
                    project.add_file(p, cpp_file)
    project = Project()
    inner_scan_project(path, project)
    return project


