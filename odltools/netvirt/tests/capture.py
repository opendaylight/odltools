# Copyright (c) 2018 Red Hat, Inc. and others.  All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

from contextlib import contextmanager
import sys

# String IO is different python 3.5 than 2.7
try:
    from cStringIO import StringIO
except ImportError:
    from io import StringIO


@contextmanager
def capture(command=None, *args, **kwargs):
    out = sys.stdout
    sys.stdout = StringIO()
    try:
        command(*args, **kwargs)
        sys.stdout.seek(0)
        yield sys.stdout.read()
    finally:
        sys.stdout = out
