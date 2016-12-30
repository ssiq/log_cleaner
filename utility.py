
path_sep = '/'


def get_project_by_path(path):
    pl = path.split(path_sep)
    if pl[0] == '':
        return pl[1]
    else:
        return pl[0]
