class Cleaner(object):
    def __init__(self):
        pass

    def clean(self, log):
        pass


class CodeFixClean(Cleaner):
    def __init__(self):
        super(CodeFixClean, self).__init__()

    def clean(self, log):
        for one_log in log.list():
            pass
