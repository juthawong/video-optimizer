# encoding: utf-8
from datetime import datetime
import os
import re


class PIDFile(object):
    def __init__(self, pid_file):
        self.__file = pid_file

    def check_pid(self):
        if not os.path.exists(self.__file):
            return True

        with open(self.__file, "r") as f:
            pid = int(f.read().strip())

            try:
                os.kill(pid, 0)
            except OSError:
                return True
            else:
                return False

    def __enter__(self):
        if not self.check_pid():
            raise RuntimeError("Program already running.")

        with open(self.__file, "w+") as f:
            f.write(str(os.getpid()))
            f.flush()

    def __exit__(self, *args):
        if os.path.exists(self.__file):
            os.unlink(self.__file)


def cast_type(value):
    if isinstance(value, basestring):
        value = value.strip()

        if value.isdigit():
            return int(value)

        if value == 'N/A':
            return None

        if re.match("^\d+\.\d*$", value):
            return float(value)

        if re.match("^0x[0-9a-fA-F]+$", value):
            return int(value, 16)

        if re.match("^\d{4}-\d{1,2}-\d{1,2} \d{1,2}:\d{1,2}:\d{1,2}$", value):
            return datetime.strptime(value, "%Y-%m-%d %H:%M:%S")

    elif isinstance(value, dict):
        value = Dict(value)
        for key, val in tuple(value.items()):
            value[key] = cast_type(val)

        return value

    elif isinstance(value, list):
        out = []
        for item in value:
            out.append(cast_type(item))

        return out
    return value


def humanize(num, suffix='B', divider=1024.):
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(num) < divider:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)


class Dict(dict):
    def __init__(self, somedict=None):
        if not somedict:
            somedict = {}

        dict.__init__(self, somedict)

        for key, value in tuple(self.items()):
            if isinstance(value, dict):
                self[key] = Dict(value)

    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__