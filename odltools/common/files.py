# Copyright (c) 2018 Red Hat, Inc. and others.  All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

import errno
import logging
import os

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
