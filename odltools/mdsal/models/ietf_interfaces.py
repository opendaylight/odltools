# Copyright (c) 2018 Red Hat, Inc. and others.  All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

from odltools.mdsal.models.model import Model

MODULE = "ietf-interfaces"


def interfaces(store, args):
    return Interfaces(MODULE, store, args)


def interfaces_state(store, args):
    return InterfacesState(MODULE, store, args)


class Interfaces(Model):
    CONTAINER = "interfaces"
    CLIST = "interface"
    CLIST_KEY = "name"


class InterfacesState(Model):
    CONTAINER = "interfaces-state"
    CLIST = "interface"
    CLIST_KEY = "name"
