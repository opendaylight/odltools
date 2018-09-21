# Copyright (c) 2018 Red Hat, Inc. and others.  All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html


class FlowTable(object):

    def __init__(self, data, flow_type, dpnid, name):
        self.rdata = data
        self.flow_type = flow_type
        self.dpnid = dpnid
        self.name = name
        self.tables = {}
        self.fdata = []

    def parse(self):
        pass

    def format(self):
        pass

    def add_flow(self, flow):
        tableid = int(flow.pdata.get(Flow.TABLE))
        flows = self.tables.get(tableid, [])
        flows.append(flow)
        self.tables[tableid] = flows

    def num_flows(self, tableid=None):
        num = 0
        if tableid:
            flows = self.tables.get(tableid, [])
            num = len(flows)
        else:
            for tableid, flows in self.tables.items():
                num += len(flows)
        return num


flow_keys = {
    "BARRIER": "barrier",
    "COOKIE": "cookie",
    "DURATION": "duration",
    "TABLE": "table",
    "N_PACKETS": "n_packets",
    "N_BYTES": "n_bytes",
    "MATCH": "match",
    "ACTIONS": "actions",
    "IDLE_TIMEOUT": "idle_timeout",
    "SEND_FLOW_REMOVED": "send_flow_rem",
    "PRIORITY": "priority",
    "GOTO": "goto",
    "RESUBMIT": "resubmit",
    "FLOW_NAME": "flow-name",
    "ID": "id",
    "INSTRUCTIONS": "instructions"
}


class Flow(object):
    BARRIER = "barrier"
    COOKIE = "cookie"
    DURATION = "duration"
    TABLE = "table"
    N_PACKETS = "n_packets"
    N_BYTES = "n_bytes"
    MATCH = "match"
    ACTIONS = "actions"
    IDLE_TIMEOUT = "idle_timeout"
    SEND_FLOW_REMOVED = "send_flow_rem"
    PRIORITY = "priority"
    GOTO = "goto"
    RESUBMIT = "resubmit"
    FLOW_NAME = "flow-name"
    ID = "id"
    INSTRUCTIONS = "instructions"

    def __init__(self, data):
        self.rdata = data  # the raw data for the flow
        self.pdata = self.pdata_init()  # map of parsed elements from the flow
        self.fdata = None  # line of formatted parsed data

    def parse(self):
        pass

    def pdata_init(self):
        pdata = {val: "" for key, val in flow_keys.items()}
        return pdata
