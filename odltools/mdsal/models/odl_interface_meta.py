# Copyright (c) 2018 Red Hat, Inc. and others.  All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

from odltools.mdsal.models.model import Model

MODULE = "odl-interface-meta"


def if_indexes_interface_map(store, args):
    return IfIndexesInterfaceMap(MODULE, store, args)


class IfIndexesInterfaceMap(Model):
    CONTAINER = "if-indexes-interface-map"
    CLIST = "if-index-interface"
    CLIST_KEY = "if-index"
