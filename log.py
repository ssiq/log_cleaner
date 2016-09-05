from lxml import etree


class TransformedLog(object):
    def __init__(self, log):
        self.log = log

    def to_string(self):
        return '{}'.format(self.log)

    def to_list(self):
        return self.log

    def _generate_one_action(self, action_dict):
        action = etree.Element('action')
        for k, v in action_dict.items():
            action.set(k, v)
        return action

    def to_xml(self):
        root = etree.Element("root")
        for action_dict in self.log:
            action = self._generate_one_action(action_dict)
            root.append(action)

        return root

    def write_xml(self, path):
        with open(path, 'w') as f:
            f.write(etree.tostring(self.to_xml(), pretty_print=True))
