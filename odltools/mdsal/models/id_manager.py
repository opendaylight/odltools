# Copyright (c) 2018 Red Hat, Inc. and others.  All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

from odltools.mdsal.models.model import Model

MODULE = "id-manager"


def id_pools(store, args):
    return IdPools(MODULE, store, args)


class IdPools(Model):
    CONTAINER = "id-pools"
    CLIST = "id-pool"
    CLIST_KEY = "pool-name"
