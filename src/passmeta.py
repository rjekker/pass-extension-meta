#!/usr/bin/env python2
from __future__ import print_function

# TODO: Add a nice module header
import argparse
import os
import sys
import subprocess
import re
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


class Layout:
    def __init__(self, directory):
        self._file = Layout.search(directory)
        self._config = Layout.load(self._file)
        debug(self._config.items("layout"))

    @property
    def filename(self):
        return self._config.get('layout', 'filename')

    @property
    def dirname(self):
        return self._config.get('layout', 'dirname')

    @property
    def contents(self):
        return self._config.get('layout', 'contents')

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
                return f
            else:
                directory = os.path.dirname(directory)
        debug("Not Found")
        return None

    @staticmethod
    def load(f):
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

    def process_dirname(self, directory):
        m = re.match(r'prop:\s*(.*)', self.dirname)
        if m:
            key = m.group(1)
            if not key:
                die("No property name given for dirname in {}".format(self._file), 4)
            return {key: directory}
        elif self.dirname == "ignore":
            return {}
        else:
            die("Invalid layout for dirname in {}".format(self._file), 4)

    def process_filename(self, file):
        m = re.match(r'prop(:?)\s*(.*)', self.filename)
        if m and m.group(1):
            # We have "prop:key"
            key = m.group(2)
            if not key:
                die("No property name given for filename in {}".format(self._file), 4)
            return {key: file}
        elif m:
            # We have just "prop"
            return {file: None}
        elif self.filename == "ignore":
            return {}
        else:
            die("Invalid layout for filename in {}".format(self._file), 4)


    def __str__(self):
        return str(self.__dict__)

class PassDataSource(object):
    def __init__(self, directory):
        self.layout = Layout(directory)

class PasswordFile(PassDataSource):
    def __init__(self, pwd, path):
        super(PasswordFile, self).__init__(os.path.dirname(path))
        self.path = path
        self.pwd = pwd
        self.lines = self.load()
        self.data = self.get_data()
        debug(self.lines)
        debug(self.data)

    def load(self):
        try:
            s = subprocess.check_output(["pass", "show", self.pwd])
        except subprocess.CalledProcessError as e:
            die("Error running pass:" + e.message)
        return s.splitlines()

    def get_data(self):
        data = self.layout.process_dirname(os.path.basename(os.path.dirname(self.path)))
        data.update(self.layout.process_filename(os.path.basename(self.pwd)))
        return data

    def __str__(self):
        return "Password file {}".format(self.pwd)

class PasswordDir(PassDataSource):
    pass

class Credentials:
    def __init__(self, pwd):
        self.pwd = pwd

        self.source = Credentials.get_source(self.pwd)
        debug(self)

    @staticmethod
    def get_source(pwd):
        """Determine source data file or dir"""
        path = os.path.join(toplevel, pwd)
        if os.path.isdir(path):
            return PasswordDir(pwd)
        else:
            return PasswordFile(pwd, path)

    def __str__(self):
        return "Credentials object from {}".format(
            self.source
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Retrieve password and/or metadata from password-store')
    parser.add_argument("path", nargs=1)
    args = parser.parse_args()

    debug("Using password store at " + get_toplevel_dir())
    cred = Credentials(args.path[0])
