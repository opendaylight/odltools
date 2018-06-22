# Copyright (c) 2018 Red Hat, Inc. and others.  All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

from odltools.mdsal.models.model import Model

MODULE = "elan"


def elan_instances(store, args):
    return ElanInstances(MODULE, store, args)


def elan_interfaces(store, args):
    return ElanInterfaces(MODULE, store, args)


class ElanInstances(Model):
    CONTAINER = "elan-instances"
    CLIST = "elan-instance"
    CLIST_KEY = "elan-instance-name"


class ElanInterfaces(Model):
    CONTAINER = "elan-interfaces"
    CLIST = "elan-interface"
    CLIST_KEY = "name"
