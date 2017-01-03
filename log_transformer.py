import sys
from collections import OrderedDict
import os
import gzip
import datetime
import json

import chardet

from utility import scan_dir, ZipExtractController
from log import Log
import constant


def read_log(dir_path):

    def my_cmp(a, b):
        to_datetime = lambda x: datetime.datetime.strptime(x[0]['time'], '%Y-%m-%d at %H:%M:%S %Z - ')
        return to_datetime(a) < to_datetime(b)

    log_list = []
    t = LogTransformer(False)
    if os.path.exists(dir_path) and os.path.isdir(dir_path):
        for file_path in scan_dir(dir_path):
            print 'to read {}'.format(file_path)
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
            print 'read ended {}'.format(file_path)
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

    def _read_to_end(self, s, begin, length=-1, pre=False, one_sep=False):
        if length == -1:
            end = begin
            action_end = False
            while True:
                if end >= len(s):
                    action_end = True
                    break
                if s[end] == '\n':
                    action_end = True
                    break
                if s[end] == ':':
                    if not pre:
                        pre = True
                    else:
                        break
                elif pre and not one_sep:
                    pre = False
                end += 1
            return s[begin:end-(not one_sep)], end + 1, action_end
        else:
            return s[begin:begin + length], begin + length, True

    def _read_pair(self, s, begin, length=-1):
        k, begin, _ = self._read_to_end(s, begin)
        v, begin, action_end = self._read_to_end(s, begin, length)
        return k, v, begin, action_end

    def _read_message(self, s, begin):
        l = -1
        message = []
        while True:
            t, begin, action_end = self._read_to_end(s, begin, length=l, pre=True, one_sep=True)
            message.append(t)
            if t == 'length' and not action_end:
                t, begin, action_end = self._read_to_end(s, begin, length=l, pre=True, one_sep=True)
                message.append(t)
                l = int(t)
                t, begin, action_end = self._read_to_end(s, begin, length=-1, pre=True, one_sep=True)
                message.append(t)
            if action_end:
                break
        return json.dumps(message), begin

    def _read_one_action(self, s, begin):
        action = OrderedDict()
        time = ''
        while len(time) == 0:
            time, begin, _ = self._read_to_end(s, begin)
            if begin > len(s):
                return False, begin
        action['time'] = time
        next_length = -1
        while True:
            if constant.ACTION_TYPE in action and action[constant.ACTION_TYPE] == constant.OPERATION \
                    and constant.OPERATION_TYPE in action and action[constant.OPERATION_TYPE] == constant.EXCUTION:
                _, begin, _ = self._read_to_end(s, begin)
                message, begin = self._read_message(s, begin)
                action[constant.MESSAGE] = message
                break

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
            if not action:
                break
            action_list.append(action)
            action_number += 1
            if self.verbose:
                print "{}:{}".format(action_number, action)
                print "begin:{}, length of s:{}".format(begin, len(s))
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
    with ZipExtractController('test_data/3_log.zip') as f_path:
        read_log(f_path).write_xml('test_log_out.xml')
        # print read_log(f_path).to_string()