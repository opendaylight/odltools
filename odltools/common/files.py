# Copyright (c) 2018 Red Hat, Inc. and others.  All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

import errno
import json
import logging
import os
import shutil

logger = logging.getLogger("common.files")


def read(filename):
    if os.path.isfile(filename) is False:
        return None

    with open(filename, 'r') as fp:
        fpbytes = fp.read()
    logger.debug("read: File: {}, read {} characters".format(filename, len(fpbytes)))
    return fpbytes


def readlines(filename):
    if os.path.isfile(filename) is False:
        return None

    lines = []
    with open(filename, 'r') as fp:
        for line in fp:
            lines.append(line.rstrip("\n"))
    logger.debug("readlines: File: {}, read {} lines".format(filename, len(lines)))
    return lines


def writelines(filename, lines, newline=False):
    try:
        os.makedirs(os.path.dirname(filename))
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

    with open(filename, 'w') as fp:
        if newline:
            for line in lines:
                fp.write("{}\n".format(line))
        else:
            fp.writelines(lines)
    logger.debug("writelines: File: {}, wrote {} lines".format(filename, len(lines)))


def debug_print(fname, text1, data):
    logger.debug("%s: request: %s: processed %d lines", fname, text1, len(data))
    # logger.debug("%s:\n%s", fname, json.dumps(data))
    logger.debug("%s:\n%s", fname, json.dumps(data, indent=4, separators=(',', ': ')))


def read_json(filename):
    if os.path.isfile(filename) is False:
        return None

    with open(filename) as json_file:
        data = json.load(json_file)
    if logger.isEnabledFor(logging.DEBUG):
        debug_print("read_file", filename, data)
    return data


def write_json(filename, data, pretty_print=False):
    try:
        os.makedirs(os.path.dirname(filename))
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

    with open(filename, 'w') as fp:
        if pretty_print:
            json.dump(data, fp, indent=4, separators=(',', ': '))
        else:
            json.dump(data, fp)
    if logger.isEnabledFor(logging.DEBUG):
        debug_print("write_json", filename, data)


def rmdir(path):
    if os.path.exists(path):
        if os.path.islink(path):
            os.unlink(path)
        else:
            shutil.rmtree(path)
