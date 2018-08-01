# Copyright (c) 2018 Red Hat, Inc. and others.  All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

import os


class Args:
    def __init__(self, jobname=None, path="/tmp"):
        self.jobname = jobname
        self.path = path


def get_resources_path():
    return os.path.join(os.path.dirname(__file__), '../../tests/resources')
