# Copyright (c) 2018 Red Hat, Inc. and others.  All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

from odltools.flows.flow import Flow


class OdlFlow(Flow):
    DPNID = "dpnid"

    def __init__(self, data):
        super(OdlFlow, self).__init__(data)
        self.pdata = []
        self.fdata = []
