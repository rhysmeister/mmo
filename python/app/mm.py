"""
Author: Rhys Campbell
Name: mm - "MongoDB Manager"
Created: 2016/03/28
Description: A demo app using the pymmo library.

History:

2016/03/28  RC      Initial version.

"""
import inspect
import os
import sys
import argparse
import time
from curses import wrapper

from bgcolours import bgcolours

execfile(os.path.dirname(os.path.abspath(inspect.stack()[0][1]))  + "/../pymmo/pymmo.py")

def display_cluster_state(mmo, c):
    """
    Print out a overview of the MongoDB Cluster and its status. The inital connection should be a mongos for this to work correctly.
    :param self:
    :param mmo: A instance of the MmoMongoCluster class
    :return:
    """
    config_servers = mmo.mmo_config_servers(c)
    mongos_servers = mmo.mmo_mongos_servers(c)
    mongod_shard_servers = mmo.mmo_shard_servers(c)
    shards = mmo.mmo_shards()
    print_list_of_hosts("MongoDB Config Servers", config_servers, bgcolours.OKGREEN)
    print_list_of_hosts("MongoDB mongos servers", mongos_servers, bgcolours.OKGREEN)
    print_list_of_hosts("MongoDB mongod shard servers", mongod_shard_servers, bgcolours.OKGREEN)
    print(bgcolours.BOLD + "MongoDB shards" + bgcolours.ENDC)
    for shard in shards:
        sys.stdout.write( bgcolours.OKGREEN + "{0}   ".format(shard) + bgcolours.ENDC)
    print("")


def print_replication_summary(replication_summary):
    sys.stdout.write(bgcolours.BOLD + "{:<30} {:<10} {:<10} {:<10} {:<10} {:<10}\n".format("hostname", "replicaset", "state", "configV", "uptime", "slaveDelay") + bgcolours.ENDC)
    for host in replication_summary:
        sys.stdout.write(bgcolours.OKGREEN + "{:<30} {:<10} {:<10} {:<10} {:<10} {:<10}\n".format(host["hostname"], host["replicaset"], host["state"], host["configVersion"], host["uptime"], host["slaveDelay"]) + bgcolours.ENDC)


def print_list_of_hosts(title, host_list, colour):
    """
    Prints the title followed by the hosts in the list.
    :param title:
    :param host_list: [ { "hostname": <string>, "port": <int> }, ...]
    :return:
    """
    sys.stdout.write(bgcolours.BOLD + title + bgcolours.ENDC + "\n")
    print_count = 0
    for host in host_list:
        if print_count % 3 == 0 and print_count > 0:  # max 3 hosts per line
            sys.stdout.write("\n")
        sys.stdout.write(colour + "{0}:{1}      ".format(host["hostname"], host["port"]) + bgcolours.ENDC)
        print_count+=1
    print("")


"""
Thse functions below could be abstracted into a single function. Something like...
display_serverStatus_output(mmo, c, headers, display_columnss)
Where headers is a list of the titles we want to show and display_columns are the paths to the appropriate data
"""

def display_instance_info_for_cluster(mmo, c, inc_mongos):
    """
    "host" : <string>,
    "advisoryHostFQDNs" : <array>,
    "version" : <string>,
    "process" : <"mongod"|"mongos">,
    "pid" : <num>,
    "uptime" : <num>,
    "uptimeMillis" : <num>,
    "uptimeEstimate" : <num>,
    "localTime" : ISODate(""),
    :param mmo:
    :param c:
    :param: inc_mongos
    :return:
    """
    serverStatus = mmo.mmo_cluster_serverStatus(c, inc_mongos)
    sys.stdout.write( "{:<30} {:<10} {:<10} {:<10} {:<10} {:<10} {:<10} {:<10}\n".format("hostname",
                                                                                          "shard",
                                                                                          "port",
                                                                                          "version",
                                                                                          "process",
                                                                                          "pid",
                                                                                          "uptime",
                                                                                          "localTime"))
    for doc in serverStatus:
        sys.stdout.write( "{:<30} {:<10} {:<10} {:<10} {:<10} {:<10} {:<10} {:<10}\n".format(doc["hostname"],
                                                                                              doc["shard"],
                                                                                              doc["port"],
                                                                                              doc["command_output"]["version"],
                                                                                              doc["command_output"]["process"],
                                                                                              doc["command_output"]["pid"],
                                                                                              doc["command_output"]["uptime"],
                                                                                              doc["command_output"]["localTime"]))

def display_asserts_for_cluster(mmo, c, inc_mongos):
    """
    Print the asserts for all the shard mongod processes in the cluster
    """
    serverStatus = mmo.mmo_cluster_serverStatus(c, inc_mongos)
    sys.stdout.write( "{:<30} {:<10} {:<10} {:<10} {:<10} {:<10} {:<10} {:<10}\n".format("hostname",
                                                                                         "shard",
                                                                                         "port",
                                                                                         "regular",
                                                                                         "warning",
                                                                                         "msg",
                                                                                         "user",
                                                                                         "rollovers"))
    for doc in serverStatus:
        sys.stdout.write( "{:<30} {:<10} {:<10} {:<10} {:<10} {:<10} {:<10} {:<10}\n".format(doc["hostname"],
                                                                                             doc["shard"],
                                                                                             doc["port"],
                                                                                             doc["command_output"]["asserts"]["regular"],
                                                                                             doc["command_output"]["asserts"]["warning"],
                                                                                             doc["command_output"]["asserts"]["msg"],
                                                                                             doc["command_output"]["asserts"]["user"],
                                                                                             doc["command_output"]["asserts"]["rollovers"]) )
def display_backgroundFlushing_for_cluster(mmo, c, inc_mongos):
    """
    "backgroundFlushing" : {
   "flushes" : <num>,
   "total_ms" : <num>,
   "average_ms" : <num>,
   "last_ms" : <num>,
   "last_finished" : ISODate("...")
    },
    Note this only applies to the MMAPv1 engine
    :param mmo:
    :param c:
    :param inc_mongos:
    :return:
    """
    serverStatus = mmo.mmo_cluster_serverStatus(c, inc_mongos)
    sys.stdout.write( "{:<30} {:<10} {:<10} {:<10} {:<10} {:<10} {:<10} {:<10}\n".format("hostname",
                                                                                                "shard",
                                                                                                "port",
                                                                                                "flushes",
                                                                                                "total_ms",
                                                                                                "average_ms",
                                                                                                "last_ms",
                                                                                                "last_finished"))
    for doc in serverStatus:
        sys.stdout.write( "{:<30} {:<10} {:<10} {:<10} {:<10} {:<10} {:<10} {:<10}\n".format(doc["hostname"],
                                                                               doc["shard"],
                                                                               doc["port"],
                                                                               doc["command_output"]["backgroundFlushing"]["flushes"],
                                                                               doc["command_output"]["backgroundFlushing"]["total_ms"],
                                                                               doc["command_output"]["backgroundFlushing"]["average_ms"],
                                                                               doc["command_output"]["backgroundFlushing"]["last_ms"],
                                                                               doc["command_output"]["backgroundFlushing"]["last_finished"]))

def display_journaling_for_cluster(mmo, c, inc_mongos):
    """
    "dur" : {
   "commits" : <num>,
   "journaledMB" : <num>,
   "writeToDataFilesMB" : <num>,
   "compression" : <num>,
   "commitsInWriteLock" : <num>,
   "earlyCommits" : <num>,
   "timeMs" : {
      "dt" : <num>,
      "prepLogBuffer" : <num>,
      "writeToJournal" : <num>,
      "writeToDataFiles" : <num>,
      "remapPrivateView" : <num>,
      "commits" : <num>,
      "commitsInWriteLock" : <num>
   }
}
    TODO add addiotnal stat if screen space
    :param mmo:
    :param c:
    :param inc_mongos:
    :return:
    """
    serverStatus = mmo.mmo_cluster_serverStatus(c, inc_mongos)
    sys.stdout.write( "{:<30} {:<10} {:<10} {:<10} {:<10} {:<10} {:<10} {:<10} {:<10}\n".format("hostname",
                                                                                                   "shard",
                                                                                                   "port",
                                                                                                   "commits",
                                                                                                   "journaledMB",
                                                                                                   "writeToDataFilesMB",
                                                                                                   "compression",
                                                                                                   "commitsInWriteLock",
                                                                                                   "earlyCommits"))
    for doc in serverStatus:
        sys.stdout.write( "{:<30} {:<10} {:<10} {:<10} {:<10} {:<10} {:<10} {:<10} {:<10}\n".format(doc["hostname"],
                                                                                                    doc["shard"],
                                                                                                    doc["port"],
                                                                                                    doc["dur"]["commits"],
                                                                                                    doc["dur"]["journaledMB"],
                                                                                                    doc["dur"]["writeToDataFilesMB"],
                                                                                                    doc["dur"]["compression"],
                                                                                                    doc["dur"]["commitsInWriteLock"],
                                                                                                    doc["dur"]["earlyCommits"]))
def display_extra_info_for_cluster(mmo, c, inc_mongos):
    """
    Show the stats from the extra_info section of the serverStatus document
    "extra_info" : {
   "note" : "fields vary by platform.",
   "heap_usage_bytes" : <num>,
   "page_faults" : <num>
    }
    :param mmo:
    :param c:
    :param inc_mongos:
    :return:
    """
    serverStatus = mmo.mmo_cluster_serverStatus(c, inc_mongos)
    sys.stdout.write( "{:<30} {:<10} {:<10} {:<10} {:<10} {:<10}\n".format("hostname",
                                                                           "shard",
                                                                           "port",
                                                                           "note",
                                                                           "heap_usage_bytes",
                                                                           "page_faults"))
    for doc in serverStatus:
        print doc.get('command_output.extra_info.page_faults', 'Missing: key_name')
        sys.stdout.write( "{:<30} {:<10} {:<10} {:<10} {:<10} {:<10}\n".format(doc["hostname"],
                                                                               doc["shard"],
                                                                               doc["port"],
                                                                               doc["command_output"]["extra_info"]["heap"],
                                                                               doc["command_output"]["extra_info"]["heap_usage_bytes"],
                                                                               doc["command_output"]["extra_info"]["page_faults"]))

def display_connections_for_cluster(mmo, c, inc_mongos):
    """
    Print the connection stats for the shard mongod process in the cluster
    """
    serverStatus = mmo.mmo_cluster_serverStatus(c, inc_mongos)
    sys.stdout.write( "{:<30} {:<10} {:<10} {:<10} {:<10} {:<10}\n".format("hostname",
                                                                           "shard",
                                                                           "port",
                                                                           "current",
                                                                           "available",
                                                                           "totalCreated"))
    for doc in serverStatus:
        sys.stdout.write( "{:<30} {:<10} {:<10} {:<10} {:<10} {:<10}\n".format(doc["hostname"],
                                                                               doc["shard"],
                                                                               doc["port"],
                                                                               doc["command_output"]["connections"]["current"],
                                                                               doc["command_output"]["connections"]["available"],
                                                                               doc["command_output"]["connections"]["totalCreated"]))

def display_opcounters_for_cluster(mmo, c, inc_mongos):
    """
    Display the opcounters for all nodes in the cluster
    "opcounters" : {
   "insert" : <num>,
   "query" : <num>,
   "update" : <num>,
   "delete" : <num>,
   "getmore" : <num>,
   "command" : <num>
    }
    :param mmo:
    :param c:
    :param inc_mongos:
    :return:
    """
    serverStatus = mmo.mmo_cluster_serverStatus(c, inc_mongos)
    sys.stdout.write( "{:<30} {:<10} {:<10} {:<10} {:<10} {:<10} {:<10} {:<10} {:<10}\n".format("hostname",
                                                                                                   "shard",
                                                                                                   "port",
                                                                                                   "insert",
                                                                                                   "query",
                                                                                                   "update",
                                                                                                   "delete",
                                                                                                   "getmore",
                                                                                                   "command"))
    for doc in serverStatus:
        sys.stdout.write( "{:<30} {:<10} {:<10} {:<10} {:<10} {:<10} {:<10} {:<10} {:<10}\n".format(doc["hostname"],
                                                                                                   doc["shard"],
                                                                                                   doc["port"],
                                                                                                   doc["command_output"]["opcounters"]["insert"],
                                                                                                   doc["command_output"]["opcounters"]["query"],
                                                                                                   doc["command_output"]["opcounters"]["update"],
                                                                                                   doc["command_output"]["opcounters"]["delete"],
                                                                                                   doc["command_output"]["opcounters"]["getmore"],
                                                                                                   doc["command_output"]["opcounters"]["command"]))


def display_network_for_cluster(mmo, c, inc_mongos):
    """
    Print the network stats for the shard mongod process in the cluster
    """
    serverStatus = mmo.mmo_cluster_serverStatus(c, inc_mongos)
    sys.stdout.write( "{:<30} {:<10} {:<10} {:<10} {:<10} {:<10}\n".format("hostname",
                                                                           "shard",
                                                                           "port",
                                                                           "bytesIn",
                                                                           "bytesOut",
                                                                           "numRequests"))
    for doc in serverStatus:
        sys.stdout.write( "{:<30} {:<10} {:<10} {:<10} {:<10} {:<10}\n".format(doc["hostname"],
                                                                               doc["shard"],
                                                                               doc["port"],
                                                                               doc["command_output"]["network"]["bytesIn"],
                                                                               doc["command_output"]["network"]["bytesOut"],
                                                                               doc["command_output"]["network"]["numRequests"]))

"""
MAIN SECTION STARTS HERE
"""
parser = argparse.ArgumentParser(description='MongoDB Manager')
parser.add_argument('--summary', action='store_true', help='Show a summary of the MongoDB Cluster Topology')
parser.add_argument('--repl', action='store_true', help='Show a summary of the replicaset state')
parser.add_argument('--instance', action='store_true', help='Show the instance info from all the shard mongod processes')
parser.add_argument('--asserts', action='store_true', help='Show the asserts stats from all the shard mongod processes')
parser.add_argument('--flushing', action='store_true', help='Show the flushing stats from all the shard mongod processes. Only applies to the MMAPv1 engine.')
parser.add_argument('--journaling', action='store_true', help='Show the journal stats from all the shard mongod processes. Only applies to the MMAPv1 engine and journaling must be enabled.')
parser.add_argument('--extra_info', action='store_true', help='Show the extra_info section from the serverStatus document.')
parser.add_argument('--connections', action='store_true', help='Show the connection stats from all the shard mongod processes')
parser.add_argument('--network', action='store_true', help='Show the network stats from all the shard mongod processes')
parser.add_argument('--opcounters', action='store_true', help='Show the opcounters stats from all the shard mongod processes')
parser.add_argument('--show_all', action='store_true', help='Show all information screens')
parser.add_argument('--inc_mongos', action='store_true', help='Optionally execute against the mongos servers. This will fail if the command is not supported by mongos.')
parser.add_argument("-H", "--mongo_hostname", type=str, default="localhost", required=False, help="Hostname for the MongoDB mongos process to connect to")
parser.add_argument("-P", "--mongo_port", type=int, default=27017, required=False, help="Port for the MongoDB mongos process to connect to")
parser.add_argument("-u", "--mongo_username", type=str, default="admin", required=False, help="MongoDB username")
parser.add_argument("-p", "--mongo_password", type=str, default="admin", required=False, help="MongoDB password")
parser.add_argument("-D", "--mongo_auth_db", type=str, default="admin", required=False, help="MongoDB authentication database")
parser.add_argument("-r", "--repeat", type=int, default=1, required=False, help="Repeat the action N number of times")
parser.add_argument("-i", "--interval", type=int, default=2, required=False, help="Number of seconds between each repeat")
args = parser.parse_args()

###################################################
# Main program starts here
###################################################

mmo = MmoMongoCluster(args.mongo_hostname, args.mongo_port, args.mongo_username, args.mongo_password, args.mongo_auth_db)
c = mmo.mmo_connect()

if c:
    while args.repeat != 0:
        if args.summary or args.show_all:
            display_cluster_state(mmo, c)
        if args.repl or args.show_all:
            rs = mmo.mmo_replication_status_summary(c)
            print_replication_summary(rs)
        if args.instance or args.show_all:
            display_instance_info_for_cluster(mmo, c, args.inc_mongos)
        if args.asserts or args.show_all:
            display_asserts_for_cluster(mmo, c, args.inc_mongos)
        if args.flushing or args.show_all:
            display_backgroundFlushing_for_cluster(mmo, c, args.inc_mongos)
        if args.journaling or args.show_all:
            display_journaling_for_cluster(mmo, c, args.inc_mongos)
        if args.extra_info or args.show_all:
            display_extra_info_for_cluster(mmo, c, args.inc_mongos)
        if args.connections or args.show_all:
            display_connections_for_cluster(mmo, c, args.inc_mongos)
        if args.network or args.show_all:
            display_network_for_cluster(mmo, c, args.inc_mongos)
        if args.opcounters or args.show_all:
            display_opcounters_for_cluster(mmo, c, args.inc_mongos)
        args.repeat -= 1
        if args.repeat > 0:
            time.sleep(args.interval)
            os.system('cls' if os.name == 'nt' else 'clear')
    else:
        exit(1)






