# Copyright (c) 2018 Red Hat, Inc. and others.  All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

import json


def format_json(args, data):
    if args is None or args.pretty_print:
        return json.dumps(data, indent=4, separators=(',', ': '))
    else:
        return json.dumps(data)


def parse_ipv4(ip):
    if ip and '/' in ip:
        ip_arr = ip.split('/')
        if ip_arr[1] == '32':
            return ip_arr[0]
    return ip


def to_hex(data, ele=None):
    if not ele:
        data = ("0x%x" % int(data)) if data else None
        return data
    elif data.get(ele):
        data[ele] = "0x%x" % data[ele]
        return data[ele]
    else:
        return data


def nstr(s):
    if not s:
        return ''
    return str(s)
