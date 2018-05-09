import hashlib
import os
import sys


def get_sha1(filename):
    if not os.path.exists(filename):
        sys.exit('ERROR: File "%s" was not found!' % filename)
    with open(filename, 'rb') as f:
        contents = f.read()
    return hashlib.sha1(contents).hexdigest()


def get_sha256(filename):
    if not os.path.exists(filename):
        sys.exit('ERROR: File "%s" was not found!' % filename)
    with open(filename, 'rb') as f:
        contents = f.read()
    return hashlib.sha256(contents).hexdigest()