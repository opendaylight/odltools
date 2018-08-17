# Copyright (c) 2018 Ericsson India Global Services Pvt Ltd. and others.  All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

import logging

from requests import exceptions

from odltools.common import rest_client

logger = logging.getLogger("netvirt.node.info")


def capture_node_info(args):
    url = ("http://{}:{}/jolokia/read".format(args.ip, args.port))
    odl_client = rest_client.RestClient(username=args.user, password=args.pw, url=url, timeout=2)
    print("--------------------------------------- Getting SyncStatus ---------------------------------------------\n")
    get_cluster_sync_status(odl_client)
    print("--------------------------------------------------------------------------------------------------------\n")
    print("--------------------------------------- Datastore Status -----------------------------------------------\n")
    get_datastore_stats(odl_client)
    print("--------------------------------------------------------------------------------------------------------\n")
    print("----------------------------------- DOMDataBroker CommitStats Details ----------------------------------\n")
    get_dombroker_commit_stats(odl_client)
    print("--------------------------------------------------------------------------------------------------------\n")
    print("----------------------------------- DISTRIBUTED DATASTORE COMMIT RATE ----------------------------------\n")
    get_datastore_commit_rate(odl_client)
    print("--------------------------------------------------------------------------------------------------------\n")
    print("----------------------------------- NETSTAT DETAILS FOR PORT 2550 --------------------------------------\n")
    get_netstat_details_for_akka_port()
    print("--------------------------------------------------------------------------------------------------------\n")
    print("----------------- CPU AND MEMORY UTILIZATION OF THE KARAF PROCESS GATHERED BY 'TOP' --------------------\n")
    get_cpu_and_memory_utilization()
    print("--------------------------------------------------------------------------------------------------------\n")
    print("----------------------------------- FREE AND USED MEMORY IN THE SYSTEM ---------------------------------\n")
    get_free_and_used_memory()
    print("--------------------------------------------------------------------------------------------------------\n")
    print("----------------------------------- NODE HEALTH CHECK STATUS -------------------------------------------\n")
    print(get_node_health_check_status(odl_client))
    print("--------------------------------------------------------------------------------------------------------\n")
    print("-------------------------------------- lsof of KARAF Process -------------------------------------------\n")
    get_karaf_lsof()
    print("--------------------------------------------------------------------------------------------------------\n")


def odl_client_request(odl_client, url):
    try:
        data = odl_client.request('get', url).json()
    except (exceptions.ConnectionError, exceptions.ReadTimeout, ValueError):
        data = None
    return data


def get_distributed_datastore_values(odl_client, shard_type, shard_name, attribute):
    url = ("org.opendaylight.controller:type="+shard_type+",Category=Shards,name="+shard_name+"/"+attribute)
    return odl_client_request(odl_client, url)


def get_distributed_datastore_commit_rate_values(odl_client, name, parameter):
    url = ("org.opendaylight.controller.cluster.datastore:name="+name+"/"+parameter)
    return odl_client_request(odl_client, url)


def get_dom_broker_commit_stats_values(odl_client, type, name, category):
    url = ("org.opendaylight.controller:type="+type+",name="+name+"/"+category)
    return odl_client_request(odl_client, url)


def get_cluster_sync_status(odl_client):
    url = ("org.opendaylight.controller:type=DistributedConfigDatastore,Category=ShardManager,name="
           "shard-manager-config/SyncStatus")
    config_sync_status = odl_client_request(odl_client, url)
    print("Config Sync Status = {}".format(config_sync_status['value']))
    url = ("org.opendaylight.controller:type=DistributedOperationalDatastore,Category=ShardManager,"
           "name=shard-manager-operational/SyncStatus")
    operational_sync_status = odl_client_request(odl_client, url)
    print("Operational Sync Status = {}".format(operational_sync_status['value']))


def get_datastore_stats(odl_client):
    config_shard_url = ("org.opendaylight.controller:type=DistributedConfigDatastore,Category=ShardManager,name=shard"
                        "-manager-config/LocalShards")
    oper_shard_url = ("org.opendaylight.controller:type=DistributedOperationalDatastore,Category=ShardManager,"
                      "name=shard-manager-operational/LocalShards")
    config_shard_information = odl_client_request(odl_client, config_shard_url)
    oper_shard_information = odl_client_request(odl_client, oper_shard_url)
    shard_map = {}
    shard_map['DistributedConfigDatastore'] = config_shard_information['value']
    shard_map['DistributedOperationalDatastore'] = oper_shard_information['value']
    for shard in shard_map:
        shard_list = shard_map[shard]
        for shard_name in shard_list:
            print("---------------------------------------------------------------------------------------------------")
            print("ShardName                   = "+get_distributed_datastore_values(odl_client, shard, shard_name,
                                                                                    "ShardName")['value'])
            print("RaftState                   = "+get_distributed_datastore_values(odl_client, shard, shard_name,
                                                                                    "RaftState")['value'])
            print("AbortTransactionsCount      = {}".format
                  (get_distributed_datastore_values(odl_client, shard, shard_name, "AbortTransactionsCount")['value']))
            print("CommittedTransactionsCount  = {}".format
                  (get_distributed_datastore_values(odl_client, shard, shard_name,
                                                    "CommittedTransactionsCount")['value']))
            print("FailedReadTransactionsCount = {}".format
                  (get_distributed_datastore_values(odl_client, shard, shard_name,
                                                    "FailedReadTransactionsCount")['value']))
            print("FailedTransactionsCount     = {}".format
                  (get_distributed_datastore_values(odl_client, shard, shard_name, "FailedTransactionsCount")['value']))
            print("LeadershipChangeCount       = {}".format
                  (get_distributed_datastore_values(odl_client, shard, shard_name, "LeadershipChangeCount")['value']))
            print("Leader                      = {}".format
                  (get_distributed_datastore_values(odl_client, shard, shard_name, "Leader")['value']))
            print("PendingTxCommitQueueSize    = {}".format
                  (get_distributed_datastore_values(odl_client, shard, shard_name,
                                                    "PendingTxCommitQueueSize")['value']))
            print("ReadOnlyTransactionCount    = {}".format
                  (get_distributed_datastore_values(odl_client, shard, shard_name,
                                                    "ReadOnlyTransactionCount")['value']))
            print("ReadWriteTransactionCount   = {}".format
                  (get_distributed_datastore_values(odl_client, shard, shard_name,
                                                    "ReadWriteTransactionCount")['value']))
            print("WriteOnlyTransactionCount   = {}".format
                  (get_distributed_datastore_values(odl_client, shard, shard_name,
                                                    "WriteOnlyTransactionCount")['value']))
            print("---------------------------------------------------------------------------------------------------")


def get_dombroker_commit_stats(odl_client):
    print("AverageCommitTime   = "+get_dom_broker_commit_stats_values(odl_client, "DOMDataBroker",
                                                                      "CommitStats", "AverageCommitTime")['value'])
    print("LongestCommitTime   = "+get_dom_broker_commit_stats_values(odl_client, "DOMDataBroker",
                                                                      "CommitStats", "LongestCommitTime")['value'])
    print("ShortestCommitTime  = "
          + get_dom_broker_commit_stats_values(odl_client, "DOMDataBroker",
                                               "CommitStats", "ShortestCommitTime")['value']).encode("utf-8")
    print("TotalCommits        = {}".format(get_dom_broker_commit_stats_values(odl_client, "DOMDataBroker",
                                                                               "CommitStats", "TotalCommits")['value']))


def get_datastore_commit_rate(odl_client):
    datastore_types = ['distributed-data-store.config.commit.rate', 'distributed-data-store.operational.commit.rate']
    for datastore_type in datastore_types:
        print(datastore_type+"_Min      = {}".format(get_distributed_datastore_commit_rate_values(
            odl_client, datastore_type, "Min")['value']))
        print(datastore_type+"_Max      = {}".format(get_distributed_datastore_commit_rate_values(
            odl_client, datastore_type, "Max")['value']))
        print(datastore_type+"_Mean     = {}".format(get_distributed_datastore_commit_rate_values(
            odl_client, datastore_type, "Mean")['value']))
        print(datastore_type+"_RateUnit = {}".format(get_distributed_datastore_commit_rate_values(
            odl_client, datastore_type, "RateUnit")['value']))
        print(datastore_type+"_Count    = {}".format(get_distributed_datastore_commit_rate_values(
            odl_client, datastore_type, "Count")['value']))
        print("-------------------------------------------------------------------------------------------------------")


def get_netstat_details_for_akka_port():
    print("TBD")


def get_cpu_and_memory_utilization():
    print("TBD")


def get_free_and_used_memory():
    print("TBD")


def get_node_health_check_status(odl_client):
    url = ("akka:type=Cluster")
    cluster_health_info = odl_client_request(odl_client, url)
    print("Cluster Members = {}".format((cluster_health_info['value'])['Members']))
    print("Cluster Leader = {}".format((cluster_health_info['value'])['Leader']))
    print("Unreachable Members = {}".format((cluster_health_info['value'])['Unreachable']))


def get_karaf_lsof():
    print("TBD")
