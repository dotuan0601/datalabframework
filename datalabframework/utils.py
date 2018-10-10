import errno
import os

import yaml
from jinja2 import Template, filters

from copy import deepcopy

def merge(a, b):
    if not a:
        a = dict()

    if not b:
        b = dict()

    if isinstance(b, dict) and isinstance(a, dict):
        a_and_b = set(a.keys()) & set(b.keys())
        every_key = set(a.keys()) | set(b.keys())
        return {k: merge(a[k], b[k]) if k in a_and_b else
                   deepcopy(a[k] if k in a else b[k]) for k in every_key}

    return deepcopy(b)

def os_sep(path):
    return path.replace("/", os.sep)

def lrchop(s, b='', e=''):
    if s.startswith(b) and len(b)>0:
        s = s[len(b):]
    if s.endswith(e) and len(e)>0:
        s = s[:-len(e)]
    return s

def relative_filename(fullpath_filename, rootpath=os.sep):
    r = lrchop(fullpath_filename,rootpath)
    return r.lstrip(os.sep) if r and r[0]==os.sep else r

def absolute_filename(s, rootpath='.'):
    return s if s.startswith(os.sep) else '{}{}{}'.format(rootpath,os.sep,s)

def breadcrumb_path(fullpath, rootpath=os.sep):
    return '.' + relative_filename(fullpath, rootpath).replace(os.sep,'.')

def get_project_files(ext, rootpath='.', exclude_dirs=[], ignore_dir_with_file='', relative_path=True):
    top  = rootpath

    lst = list()
    for root, dirs, files in os.walk(top, topdown=True):
        for d in exclude_dirs:
            if d in dirs:
                dirs.remove(d)

        if ignore_dir_with_file in files:
            dirs[:] = []
            next
        else:
            for file in files:
                if file.endswith(ext):
                    f = os.path.join(root, file)
                    lst.append(relative_filename(f,rootpath) if relative_path else f)

    return lst

def pretty_print(metadata):
    print(yaml.dump(metadata, indent=2, default_flow_style=False))


def render(m, passes=10):
    # doc = {}
    # for k in m.keys():
    #     doc[k] = yaml.dump(m[k])

    doc = yaml.dump(m)

    filters.FILTERS['env'] = lambda value, key: os.getenv(key, value)
    for i in range(passes):
        template = Template(doc)
        doc = template.render(yaml.load(doc))
    #
    # for k in doc.keys():
    #     for i in range(passes):
    #         doc[k] = template.render(yaml.load(doc[k]))
    #
    # d = {}
    # for k in doc.keys():
    #     d[k] = yaml.load(doc[k])

    doc = yaml.load(doc)
    return doc

def ensure_dir_exists(path, mode=0o777):
    """ensure that a directory exists
    If it doesn't exist, try to create it, protecting against a race condition
    if another process is doing the same.
    The default permissions are determined by the current umask.
    """
    try:
        os.makedirs(path, mode=mode)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise
    if not os.path.isdir(path):
        raise IOError("%r exists but is not a directory" % path)

#get_project_files(ext='metadata.yml', ignore_dir_with_file='metadata.ignore.yml', relative_path=False)
#get_project_files(ext='.ipynb', exclude_dirs=['.ipynb_checkpoints'])
