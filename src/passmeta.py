#!/usr/bin/env python2
from __future__ import print_function

# TODO: Add a nice module header
# TODO: Add unit tests
# TODO: test plain-text lines
# TODO: Test key-value lines with no key
# TODO: use logger for debug
# TODO: change config: unit=dir or unit=file
# TODO: we get a dir and a file section
# TODO: output to json, xml?
# TODO: same functionality as meta, but expand on it
# TODO: output as csv?
# TODO: make output work for dmenu
import argparse
import os
import sys
import subprocess
import re
import json
import ConfigParser

LAYOUT_FILE_NAME = ".pass-layout"
DEFAULT_LAYOUT = {
    "filename": "ignore",
    "dirname": "ignore",
    "contents": '["password"]',
    "tail": "key:value"
}
# Goal: retrieve password and meta-data in a structured way

DEBUG = True


def error(msg):
    print(msg, file=sys.stderr)


def debug(msg):
    if DEBUG:
        print(msg)


def die(msg, retval):
    error(msg)
    sys.exit(retval)


def get_toplevel_dir():
    """Find the password store"""
    try:
        d = os.environ["PASSWORD_STORE_DIR"]
    except KeyError:
        d = "~/.password-store"
    toplevel = os.path.expanduser(d)
    if not os.path.isdir(toplevel):
        die("Password store '{}' does not exist or is not a directory.".format(toplevel), 1)
    return toplevel


toplevel = get_toplevel_dir()


class Credentials:
    """This class will contains password and metadata"""
    def __init__(self):
        self._passwords = {}
        self._metadata = {}
        self._text = []

    @property
    def passwords(self):
        return self._passwords

    def add_password(self, pwd_path, password):
        if pwd_path in self._passwords:
            die("Setting multiple passwords for " + pwd_path, 9)
        self._passwords[pwd_path] = password

    @property
    def metadata(self):
        return self._metadata

    @property
    def text(self):
        return self._text

    def add_prop(self, key, value):
        self.metadata.setdefault(key, []).append(value)

    def add_dict(self, d):
        for k in d:
            self.add_prop(k, d[k])

    def add_line(self, line):
        self._text.append(line)

    def add(self, x):
        if x is None:
            return
        if type(x) is dict:
            self.add_dict(x)
        elif type(x) is str:
            self.add_line(x)
        else:
            self.add_line(str(x))

    def merge(self, other):
        assert isinstance(other, Credentials)
        for k, v in other.passwords.items():
            self.add_password(k, v)
        for k, v in other.metadata.items():
            for i in v:
                self.add_prop(k, i)
        for l in other.text:
            self.add_line(l)

    def to_json(self):
        return json.dumps({
            'password': self.passwords,
            'metadata': self.metadata,
            'text': self.text
        })

    def __str__(self):
        return str(self.__dict__)

class Layout:
    """This class finds and parses .pass-layout, and can return correct
    key/value pairs given password file data"""
    def __init__(self, directory):
        debug("Creating Layout for " + directory)
        self._file = Layout.search(directory)
        self._config = Layout.load(self._file)
        debug(self._config.items("layout"))
        self._validate()

    @property
    def filename(self):
        return self._config.get('layout', 'filename')

    @property
    def dirname(self):
        return self._config.get('layout', 'dirname')

    @property
    def contents(self):
        return self._contents

    @property
    def tail(self):
        return self._config.get('layout', 'tail')

    @staticmethod
    def search(directory):
        """Search for .pass-layout in parent folders of credentials"""
        debug("Searching for layout file")
        while directory != toplevel:
            debug("Checking " + directory)
            f = os.path.join(directory, LAYOUT_FILE_NAME)
            if os.path.isfile(f):
                debug("Found: " + f)
                return f
            else:
                directory = os.path.dirname(directory)
        debug("Not Found")
        return None

    @staticmethod
    def load(f):
        """Load config from file or, if file not found, return default config"""
        config = ConfigParser.SafeConfigParser(DEFAULT_LAYOUT)
        if f:
            try:
                config.read(f)
            except ConfigParser.ParsingError as e:
                die(e.message, 3)
            if not config.has_section("layout"):
                die("Layout file {} is missing section [layout]".format(f), 3)
        else:
            debug("Using default layout")
            config.add_section("layout")
        return config

    def _validate_dir_or_file(self, param, param_name):
        if param == "ignore":
            return
        else:
            m = re.match(r'prop:\s*(.*)', param)
            if not m:
                die("Invalid value for '{}' -- in layout file {}".format(param_name, self._file), 4)
            if not m.group(1):
                die("Missing propertyname for '{}' -- in layout file {}".format(param_name, self._file), 4)

    def _validate_line_param(self, param, param_name):
        if param == "ignore":
            return
        elif param.startswith("prop"):
            m = re.match(r'prop:\s*(.*)', param)
            if not m:
                die("Invalid value for '{}' -- in layout file {}".format(param_name, self._file), 4)
            if not m.group(1):
                die("Missing propertyname for '{}' -- in layout file {}".format(self._file), 4)
        elif param.startswith("key"):
            m = re.match(r'key(.)value', param)
            if not m:
                die("Invalid value for '{}' -- in layout file {}".format(param_name, self._file), 4)

    def _validate(self):
        """Do some preliminary checks and parsing on layout config"""
        self._validate_dir_or_file(self.dirname, "dirname")
        self._validate_dir_or_file(self.filename, "filename")

        try:
            contents = json.loads(self._config.get('layout', 'contents'))
            if type(contents) is not list:
                die("Value for 'contents' is not a list -- in layout file {}".format(self._file), 4)
            if not all([type(s) is unicode for s in contents]):
                die("'contents' should only contain strings -- in layout file {}".format(self._file), 4)
            self._contents = contents
        except ValueError as e:
            die("Value for 'contents' is not a valid list of strings -- in layout file {}".format(self._file), 4)

        for i, l in enumerate(contents):
            self._validate_line_param(l, "line " + str(i))

        self._validate_line_param(self.tail, "tail")

    # Note: the processing functions assume that validation was passed correctly

    def _process_prop(self, value, layout_param):
        """Sets a property based on a 'prop:X' layout rule; return Credentials object or None"""
        c = Credentials()
        if layout_param == "ignore":
            return c
        m = re.match(r'prop:\s*(.*)', layout_param)
        c.add_prop(m.group(1), value)
        return c

    def _process_key_value(self, line, layout_param):
        """Sets a property based on a 'key:value' layout rule; return Credentials object"""
        c = Credentials()
        m = re.match(r'key(.)value', layout_param)
        sep = m.group(1)
        m = re.match(r'\s*(.*?)' + sep + r'\s*(.*)\s*', line)
        if not m:
            c.add_line(line)
        else:
            c.add_prop(m.group(1), m.group(2))
        return c

    def process_dirname(self, directory):
        """"Get data based on directory name and layout.dirname. Returns dict"""
        return self._process_prop(directory, self.dirname)

    def process_filename(self, filename):
        """"Get data based on file name and layout.filename. Returns dict"""
        return self._process_prop(filename, self.filename)

    def process_contents(self, lines, pwd):
        """"Get data based on file content. Returns a Credentials object"""
        cred = Credentials()
        for i, c in enumerate(self.contents):
            if c == "ignore":
                continue
            elif c == "password":
                cred.add_password(pwd, lines[i])
            elif c.startswith("prop"):
                cred.merge(self._process_prop(lines[i], c))
            elif c.startswith("key"):
                cred.merge(self._process_key_value(lines[i], c))
            else:
                cred.add_line(lines[i])
        return cred

    def process_tail(self, lines):
        cred = Credentials()
        tail = lines[len(self.contents):]
        if self.tail  == "ignore":
            return cred
        elif self.tail.startswith("key"):
            for l in tail:
                cred.merge(self._process_key_value(l, self.tail))
            return cred

        tail = "\n".join(tail)
        if self.tail.startswith("prop"):
            cred.merge(self._process_prop(tail, self.tail))
        else:
            cred.add_line(tail)
        return cred

    def __str__(self):
        return str(self.__dict__)

class PassDataSource(object):
    def __init__(self, directory):
        self.layout = Layout(directory)

    def get_credentials(self):
        raise NotImplementedError

class PasswordFile(PassDataSource):
    def __init__(self, pwd, path):
        debug("Creating Passwordfile for " + pwd)
        super(PasswordFile, self).__init__(os.path.dirname(path))
        self.path = path
        self.pwd = pwd
        self.lines = self.load()

    def load(self):
        try:
            s = subprocess.check_output(["pass", "show", self.pwd])
        except subprocess.CalledProcessError as e:
            die("Error running pass:" + e.message)
        return s.splitlines()

    def get_credentials(self):
        cred = Credentials()
        cred.merge(self.layout.process_dirname(os.path.basename(os.path.dirname(self.path))))
        cred.merge(self.layout.process_filename(os.path.basename(self.pwd)))
        cred.merge(self.layout.process_contents(self.lines, self.pwd))
        cred.merge(self.layout.process_tail(self.lines))
        return cred

    def __str__(self):
        return "Password file {}".format(self.pwd)

class PasswordDir(PassDataSource):
    pass


def get_source(pwd):
    """Determine source data file or dir"""
    path = os.path.join(toplevel, pwd)
    if os.path.isdir(path):
        return PasswordDir(pwd)
    else:
        return PasswordFile(pwd, path)


if __name__ == "__main__":
    src = get_source("ZZP/pluralsight/analytics")
    cred = src.get_credentials()
    print(cred.to_json())
    # parser = argparse.ArgumentParser(
    #     description='Retrieve password and/or metadata from password-store')
    # parser.add_argument("path", nargs=1)
    # args = parser.parse_args()
    #
    # debug("Using password store at " + get_toplevel_dir())
    # #get_source(args.path[0])

