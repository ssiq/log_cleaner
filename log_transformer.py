import sys
from collections import OrderedDict
from log import TransformedLog


class LogTransformer(object):
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
        while begin < len(s):
            action, begin = self._read_one_action(s, begin)
            action_list.append(action)
            action_number += 1
            if self.verbose:
                print "{}:{}".format(action_number, action)
        return TransformedLog(action_list)


if __name__ == '__main__':
    log_path = sys.argv[1]
    to_path = sys.argv[2]
    with open(log_path, 'rb') as f:
        transformer = LogTransformer(False)
        s = f.read()
        log_parsed = transformer.transform(s)
        # for t in log_parsed:
            # print '{}'.format(t)
            # print etree.tostring(t)

    with open(to_path, 'w') as f:
        f.write(log_parsed.to_string())