import sys
from collections import OrderedDict
from lxml import etree


class TransformedLog(object):
    def __init__(self, value):
        self.value = value

    def to_string(self):
        pass


class BaseTransformer(object):
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
        class Log(TransformedLog):
            def __init__(self, value):
                super(Log, self).__init__(value)

            def to_string(self):
                return '{}'.format(self.value)

        begin = 0
        action_list = []
        action_number = 0
        while begin < len(s):
            action, begin = self._read_one_action(s, begin)
            action_list.append(action)
            action_number += 1
            if self.verbose:
                print "{}:{}".format(action_number, action)
        return Log(action_list)


class XMLTransformer(BaseTransformer):
    def __init__(self, verbose=False):
        super(XMLTransformer, self).__init__(verbose)

    def _generate_one_action(self, action_dict):
        action = etree.Element('action')
        for k, v in action_dict.items():
            action.set(k, v)
        return action

    def transform(self, s):
        class Log(TransformedLog):
            def __init__(self, value):
                super(Log, self).__init__(value)

            def to_string(self):
                r = '<root>\n'
                for t in self.value:
                    r = r + etree.tostring(t) + '\n'
                r += '</root>'
                return r

        log_list = super(XMLTransformer, self).transform(s)
        root = etree.Element("root")
        for action_dict in log_list.value:
            action = self._generate_one_action(action_dict)
            root.append(action)
        return Log(root)


if __name__ == '__main__':
    log_path = sys.argv[1]
    to_path = sys.argv[2]
    with open(log_path, 'rb') as f:
        transformer = XMLTransformer(False)
        s = f.read()
        log_parsed = transformer.transform(s)
        # for t in log_parsed:
            # print '{}'.format(t)
            # print etree.tostring(t)

    with open(to_path, 'w') as f:
        f.write(log_parsed.to_string())