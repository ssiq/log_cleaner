import sys
from collections import OrderedDict
import os
import gzip
import datetime

import chardet

from utility import scan_dir, ZipExtractController
from log import Log


def read_log(dir_path):

    def my_cmp(a, b):
        to_datetime = lambda x: datetime.datetime.strptime(x[0]['time'], '%Y-%m-%d at %H:%M:%S %Z - ')
        return to_datetime(a) < to_datetime(b)

    log_list = []
    t = LogTransformer(False)
    if os.path.exists(dir_path) and os.path.isdir(dir_path):
        for file_path in scan_dir(dir_path):
            if file_path.endswith('.log'):
                with open(file_path, 'rb') as f:
                    log = t.transform(f.read())
                    if log.to_list() is not None:
                        log_list.append(log.to_list())
            elif file_path.endswith('.log.gz'):
                with gzip.open(file_path, 'rb') as f:
                    log = t.transform(f.read())
                    if log.to_list() is not None:
                        log_list.append(log.to_list())
        log_list.sort(cmp=my_cmp)
        r = log_list[0]
        for l in log_list[1:]:
            r.extend(l)
        return Log(r)


class LogTransformer(object):
    '''
    This class is used to load log file. It just has a transform function
    used to transform the log string to formatted TransformedLog.
    '''
    def __init__(self, verbose=False):
        self.verbose = verbose

    def _read_to_end(self, s, begin, length=-1):
        if length == -1:
            end = begin
            pre = False
            action_end = False
            while True:
                if end >= len(s):
                    break
                if s[end] == '\n':
                    action_end = True
                    break
                if s[end] == ':':
                    if not pre:
                        pre = True
                    else:
                        break
                elif pre:
                    pre = False
                end += 1
            return s[begin:end-1], end + 1, action_end
        else:
            return s[begin:begin + length], begin + length, True

    def _read_pair(self, s, begin, length=-1):
        k, begin, _ = self._read_to_end(s, begin)
        v, begin, action_end = self._read_to_end(s, begin, length)
        return k, v, begin, action_end

    def _read_one_action(self, s, begin):
        action = OrderedDict()
        time = ''
        while len(time) == 0:
            time, begin, _ = self._read_to_end(s, begin)
        action['time'] = time
        next_length = -1
        while True:
            k, v, begin, action_end = self._read_pair(s, begin, next_length)
            k = k.strip(' ')
            if k == 'length' or k == 'text_length':
                if 'operation_type' in action and action['operation_type'] == 'delete':
                    next_length = -1
                else:
                    next_length = int(v)
            else:
                next_length = -1
            action[k] = v
            if action_end:
                break
        return action, begin

    def transform(self, s):
        begin = 0
        action_list = []
        action_number = 0
        s = s.decode('gbk')
        while begin < len(s):
            action, begin = self._read_one_action(s, begin)
            action_list.append(action)
            action_number += 1
            if self.verbose:
                print "{}:{}".format(action_number, action)
        return Log(action_list)


if __name__ == '__main__':
    # log_path = sys.argv[1]
    # to_path = sys.argv[2]
    # with open(log_path, 'rb') as f:
    #     transformer = LogTransformer(False)
    #     s = f.read()
    #     log_parsed = transformer.transform(s)
        # for t in log_parsed:
            # print '{}'.format(t)
            # print etree.tostring(t)

    # log_parsed.write_xml(to_path)
    with ZipExtractController('test_data/2_log.zip') as f_path:
        read_log(f_path)