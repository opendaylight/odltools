# Copyright (c) 2018 Red Hat, Inc. and others.  All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

import errno
import logging
import os

# TODO:
# - requests to get flow dumps via ovs-vsctl, ssh
# - group processing

logger = logging.getLogger("ovs.request")


def read_file(filename):
    if os.path.isfile(filename) is False:
        return None

    lines = []
    with open(filename, 'r') as fp:
        for line in fp:
            # strip leading spaces. by default every flow line has a leading space: " cookie=..."
            lines.append(line.lstrip())
    logger.debug("read_file: File: %s: processed %d lines", filename, len(lines))
    return lines


def write_file(filename, lines):
    try:
        os.makedirs(os.path.dirname(filename))
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

    with open(filename, 'w') as fp:
        fp.writelines(lines)
    logger.debug("write_file: File: %s: wrote %d lines", filename, len(lines))
