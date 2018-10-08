# Copyright (c) 2018 Red Hat, Inc. and others.  All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

import json
import logging

from odltools.common import files
from odltools.common import rest_client

logger = logging.getLogger("mdsal.model")


class Model:
    CONFIG = "config"
    OPERATIONAL = "operational"
    USER = "admin"
    PW = "admin"
    CONTAINER = "container"
    CLIST = "clist"
    CLIST_KEY = "key"

    def __init__(self, modul, store, args, mid=None):
        init_rest_client(args, 5)
        self.module = modul
        self.container = self.CONTAINER
        self.clist = self.CLIST
        self.clist_key = self.CLIST_KEY
        self.store = store
        self.transport = args.transport
        self.ip = args.ip
        self.port = args.port
        self.url_path = make_url_path(self.store, self.module, self.container, mid)
        self.path = args.path
        self.filename = make_filename(self.path, self.store, self.module, self.container, mid)
        self.data = None
        self.data = get_model_data(self.data, self.filename, self.url_path, args)
        if self.data is None:
            logger.warning("Model data was not imported")
            self.data = {}
        elif self.get_clist() is []:
            logger.warning("Model data is wrong")
            self.data = {}

    def get_list(self, data, container_key, child):
        c = data and data.get(container_key, {})
        lst = c.get(child, [])
        return lst

    def get_clist(self):
        return self.get_list(self.data, self.container, self.clist)

    def get_clist_by_key(self, key=None):
        d = {}
        key = key or self.clist_key
        cl = self.get_clist()
        for l in cl:
            d[l[key]] = l
        return d

    def pretty_format(self, data=None):
        if data is None:
            data = self.data
        return json.dumps(data, indent=4, separators=(',', ': '))

    def get_kv(self, k, v, values):
        """
        Return a list of values for the given key
        :param k:
        :param v:
        :param values:
        :return:
        """
        if type(v) is dict:
            for jsonkey in v:
                if jsonkey == k:
                    values.append(v[jsonkey])
                elif type(v[jsonkey]) in (list, dict):
                    self.get_kv(k, v[jsonkey], values)
        elif type(v) is list:
            for item in v:
                if type(item) in (list, dict):
                    self.get_kv(k, item, values)
        return values

    @staticmethod
    def get_dpn_from_ofnodeid(node_id):
        return node_id.split(':')[1] if node_id else 'none'

    @staticmethod
    def get_ofport_from_ncid(ncid):
        return ncid.split(':')[2] if ncid and ncid.startswith('openflow') else 0


def make_filename(path, store, module, name, mid=None):
    if not mid:
        return "{}/{}___{}__{}.json".format(path, store, module, name)
    else:
        fmid = mid.replace("/", "___")
        fmid = fmid.replace(":", "__")
        return "{}/{}___{}__{}___{}.json".format(path, store, module, name, fmid)


def make_filename_from_resource(args, resource):
    sm = SplitResource(resource)
    return make_filename(args.path, sm.store, sm.module, sm.name, sm.mid)


def make_url_path(store, module, name, mid=None):
    if not mid:
        return "{}/{}:{}".format(store, module, name)
    else:
        return "{}/{}:{}/{}".format(store, module, name, mid)


def make_url_path_from_resource(resource):
    sm = SplitResource(resource)
    return make_url_path(sm.store, sm.module, sm.name, sm.mid)


def make_url_parts(args, resource=None):
    url_root = "{}://{}:{}/restconf".format(args.transport, args.ip, args.port)
    if resource is None:
        url_path = None
    else:
        url_path = make_url_path_from_resource(resource)
    return url_root, url_path


odl_client = None


def init_rest_client(args, timeout=5):
    global odl_client
    if odl_client is None:
        url_root, url_path = make_url_parts(args, None)
        odl_client = rest_client.RestClient(username=args.user, password=args.pw, url=url_root, timeout=timeout)
    return odl_client


def get_from_odl(url_path):
    global odl_client
    return odl_client.get_json(url_path)


def get_model_data(data, filename, url_path, args):
    if data is not None:
        return data

    data = files.read_json(filename)
    if data is not None:
        return data

    data = get_from_odl(url_path)
    if data is not None:
        files.write_json(filename, data, args.pretty_print)
        return data


class SplitResource:

    def __init__(self, resource):
        res_split = resource.split("/", 1)
        store = res_split[0]
        path_split = res_split[1].split(":", 1)
        module = path_split[0]
        name_split = path_split[1].partition("/")
        name = name_split[0]
        mid = name_split[2]
        self.store = store
        self.module = module
        self.name = name
        self.mid = mid
        logger.debug("SplitResource: %s", self.__dict__)
