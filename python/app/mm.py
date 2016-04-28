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

from bgcolours import bgcolours
from collections import Counter

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
    TODO add additional stat if screen space
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

def display_opcounters_for_cluster(mmo, c, inc_mongos, repl=False):
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

    When repl = True we'll displau the opcounters from the replication document instead

    "opcountersRepl" : {
   "insert" : <num>,
   "query" : <num>,
   "update" : <num>,
   "delete" : <num>,
   "getmore" : <num>,
   "command" : <num>
    },

    :param mmo:
    :param c:
    :param inc_mongos:
    :return:
    """

    document = "opcounters"
    if repl:
        document = "opcountersRepl"

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
                                                                                                   doc["command_output"][document]["insert"],
                                                                                                   doc["command_output"][document]["query"],
                                                                                                   doc["command_output"][document]["update"],
                                                                                                   doc["command_output"][document]["delete"],
                                                                                                   doc["command_output"][document]["getmore"],
                                                                                                   doc["command_output"][document]["command"]))

def display_globalLock_for_cluster(mmo, c, in_mongos):
    """
    Display the global lock document for the database.
    "globalLock" : {
   "totalTime" : <num>,
   "currentQueue" : {
      "total" : <num>,
      "readers" : <num>,
      "writers" : <num>
   },
   "activeClients" : {
      "total" : <num>,
      "readers" : <num>,
      "writers" : <num>
   }
    },
    :param mmo:
    :param c:
    :param in_mongos:
    :return:
    """
    serverStatus = mmo.mmo_cluster_serverStatus(c, in_mongos)
    sys.stdout.write( "{:<30} {:<10} {:<10} {:<10} {:<30} {:<30}\n".format("",
                                                                           "",
                                                                           "",
                                                                           "",
                                                                           "currentQueue",
                                                                           "activeClients"))
    sys.stdout.write( "{:<30} {:<10} {:<10} {:<10} {:<10} {:<10} {:<10} {:<10} {:<10} {:<10}\n".format( "hostname",
                                                                                                        "shard",
                                                                                                        "port",
                                                                                                        "totalTime",
                                                                                                        "total",
                                                                                                         "readers",
                                                                                                         "writers",
                                                                                                         "total",
                                                                                                         "readers",
                                                                                                         "writers"))
    for doc in serverStatus:
        sys.stdout.write( "{:<30} {:<10} {:<10} {:<10} {:<10} {:<10} {:<10} {:<10} {:<10} {:<10}\n".format(doc["hostname"],
                                                                                    doc["shard"],
                                                                                    doc["port"],
                                                                                    doc["command_output"]["globalLock"]["totalTime"],
                                                                                    doc["command_output"]["globalLock"]["currentQueue"]["total"],
                                                                                    doc["command_output"]["globalLock"]["currentQueue"]["readers"],
                                                                                    doc["command_output"]["globalLock"]["currentQueue"]["writers"],
                                                                                    doc["command_output"]["globalLock"]["activeClients"]["total"],
                                                                                    doc["command_output"]["globalLock"]["activeClients"]["readers"],
                                                                                    doc["command_output"]["globalLock"]["activeClients"]["writers"]))

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

def display_security_for_cluster(mmo, c, inc_mongos):
    """
    Print the security document for each mongod shard in the cluster.
    TODO - This document is only present if the feature is enabled. Add soemthign to check for the key and exit gracefully
    "security" : {
   "SSLServerSubjectName": <string>,
   "SSLServerHasCertificateAuthority": <boolean>,
   "SSLServerCertificateExpirationDate": <date>
    }
    """
    serverStatus = mmo.mmo_cluster_serverStatus(c, inc_mongos)
    sys.stdout.write( "{:<30} {:<10} {:<10} {:<20} {:<32} {:<34}\n".format("hostname",
                                                                           "shard",
                                                                           "port",
                                                                           "SSLServerSubjectName",
                                                                           "SSLServerHasCertificateAuthority",
                                                                           "SSLServerCertificateExpirationDate"))
    for doc in serverStatus:
        sys.stdout.write( "{:<30} {:<10} {:<10}  {:<20} {:<32} {:<34}\n".format(doc["hostname"],
                                                                              doc["shard"],
                                                                               doc["port"],
                                                                               doc["command_output"]["security"]["SSLServerSubjectName"],
                                                                               doc["command_output"]["security"]["SSLServerHasCertificateAuthority"],
                                                                               doc["command_output"]["security"]["SSLServerCertificateExpirationDate"]))

def display_storage_engine_for_cluster(mmo, c, inc_mongos):
    """
    Display the storage engine details for each host in the cluster
    "storageEngine" : {
   "name" : <string>,
   "supportsCommittedReads" : <boolean>
    },
    """
    serverStatus = mmo.mmo_cluster_serverStatus(c, inc_mongos)
    sys.stdout.write( "{:<30} {:<10} {:<10} {:<15} {:<22}\n".format("hostname",
                                                                    "shard",
                                                                    "port",
                                                                    "name",
                                                                    "supportsCommittedReads"))
    for doc in serverStatus:
        sys.stdout.write( "{:<30} {:<10} {:<10} {:<15} {:<22}\n".format(doc["hostname"],
                                                                                doc["shard"],
                                                                                doc["port"],
                                                                                doc["command_output"]["storageEngine"]["name"],
                                                                                doc["command_output"]["storageEngine"]["supportsCommittedReads"]))

def display_wired_tiger_for_cluster(mmo, c, sub_doc, inc_mongos):
    """
    Display wired tiger stats
    """
    raise "Not implemented!"

def display_mem_for_cluster(mmo, c, inc_mongos):
    """
    Display details from the mem document for each mongod process in the cluster
    "mem" : {
   "bits" : <int>,
   "resident" : <int>,
   "virtual" : <int>,
   "supported" : <boolean>,
   "mapped" : <int>,
   "mappedWithJournal" : <int>
    },
    """
    serverStatus = mmo.mmo_cluster_serverStatus(c, inc_mongos)
    sys.stdout.write("{:<30} {:<10} {:<10} {:<10} {:<10} {:<10} {:<10} {:<10} {:<18}\n".format("hostname",
                                                                                                "shard",
                                                                                                "port",
                                                                                                "bits",
                                                                                                "resident",
                                                                                                "virtual",
                                                                                                "supported",
                                                                                                "mapped",
                                                                                                "mappedWithJournal"))
    for doc in serverStatus:
        sys.stdout.write("{:<30} {:<10} {:<10} {:<10} {:<10} {:<10} {:<10} {:<10} {:<18}\n".format(doc["hostname"],
                                                                                                   doc["shard"],
                                                                                                   doc["port"],
                                                                                                   doc["command_output"]["mem"]["bits"],
                                                                                                   doc["command_output"]["mem"]["resident"],
                                                                                                   doc["command_output"]["mem"]["virtual"],
                                                                                                   doc["command_output"]["mem"]["supported"],
                                                                                                   doc["command_output"]["mem"]["mapped"],
                                                                                                   doc["command_output"]["mem"].get("mappedWithJournal", "NA"))) # Only present for MMAPv1
def display_host_info_for_cluster(mmo, c, inc_mongos, sub_command):
    """
    Summaries the content of the host_info document
    {
   "system" : {
          "currentTime" : ISODate("<timestamp>"),
          "hostname" : "<hostname>",
          "cpuAddrSize" : <number>,
          "memSizeMB" : <number>,
          "numCores" : <number>,
          "cpuArch" : "<identifier>",
          "numaEnabled" : <boolean>
   },
   "os" : {
          "type" : "<string>",
          "name" : "<string>",
          "version" : "<string>"
   },
   "extra" : {
          "versionString" : "<string>",
          "libcVersion" : "<string>",
          "kernelVersion" : "<string>",
          "cpuFrequencyMHz" : "<string>",
          "cpuFeatures" : "<string>",
          "pageSize" : <number>,
          "numPages" : <number>,
          "maxOpenFiles" : <number>
   },
   "ok" : <return>
    }
    :param mmo:
    :param c:
    :param inc_mongos:
    :return:
    """
    hostInfo = mmo.mmo_cluster_hostInfo(c, inc_mongos)

    if sub_command == "system":
        currentTimes = set() # So we can compare the currentTime of each host
        sys.stdout.write("{:<30} {:<10} {:<10} {:<12} {:<10} {:<10} {:<8} {:<10}\n".format("hostname",
                                                                                                  "shard",
                                                                                                  "port",
                                                                                                  "cpuAddrSize",
                                                                                                  "memSizeMB",
                                                                                                  "numCores",
                                                                                                  "cpuArch",
                                                                                                  "numaEnabled"))
        for doc in hostInfo:
            sys.stdout.write("{:<30} {:<10} {:<10} {:<12} {:<10} {:<10} {:<8} {:<10}\n".format(doc["hostname"],
                                                                                                       doc["shard"],
                                                                                                       doc["port"],
                                                                                                       doc["command_output"]["system"]["cpuAddrSize"],
                                                                                                       doc["command_output"]["system"]["memSizeMB"],
                                                                                                       doc["command_output"]["system"]["numCores"],
                                                                                                       doc["command_output"]["system"]["cpuArch"],
                                                                                                       doc["command_output"]["system"]["numaEnabled"]))
            currentTimes.add(doc["command_output"]["system"]["currentTime"])
        diff = max(currentTimes) - min(currentTimes)
        diff = diff.total_seconds() * 1000
        line = "Time difference in milliseconds between the cluster nodes: " + str(diff) + " ms (not concurrently sampled)"

        print line
    elif sub_command == "os":
        sys.stdout.write("{:<30} {:<10} {:<10} {:<10} {:<10} {:<10}\n".format("hostname",
                                                                              "shard",
                                                                              "port",
                                                                              "type",
                                                                              "name",
                                                                              "version"))
        for doc in hostInfo:
            sys.stdout.write("{:<30} {:<10} {:<10} {:<10} {:<10} {:<10} \n".format(doc["hostname"],
                                                                                   doc["shard"],
                                                                                   doc["port"],
                                                                                   doc["command_output"]["os"]["type"],
                                                                                   doc["command_output"]["os"]["name"],
                                                                                   doc["command_output"]["os"]["version"]))
    elif sub_command == "extra":
        versionStrings = [] # Too big to display so we'll collect and output later
        max_hostname_length = 0
        sys.stdout.write("{:<30} {:<10} {:<10} {:<12} {:<15} {:<18} {:<10} {:<10} {:<12}\n".format("hostname",
                                                                                                                  "shard",
                                                                                                                  "port",
                                                                                                                  #"versionString",
                                                                                                                  "libcVersion",
                                                                                                                  "kernelVersion",
                                                                                                                  "cpuFrequencyMHz",
                                                                                                                  #"cpuFeatures",
                                                                                                                  "pageSize",
                                                                                                                  "numPages",
                                                                                                                  "maxOpenFiles"))
        for doc in hostInfo:
            sys.stdout.write("{:<30} {:<10} {:<10} {:<12} {:<15} {:<18} {:<10} {:<10} {:<12}\n".format(doc["hostname"],
                                                                                                       doc["shard"],
                                                                                                       doc["port"],
                                                                                                       #doc["command_output"]["extra"]["versionString"],
                                                                                                       doc["command_output"]["extra"].get("libcVersion", "NA"),
                                                                                                       doc["command_output"]["extra"].get("kernelVersion", "NA"),
                                                                                                       doc["command_output"]["extra"]["cpuFrequencyMHz"],
                                                                                                       #doc["command_output"]["extra"]["cpuFeatures"], Too big
                                                                                                       doc["command_output"]["extra"]["pageSize"],
                                                                                                       doc["command_output"]["extra"].get("numPages", "NA"),
                                                                                                       doc["command_output"]["extra"].get("maxOpenFiles", "NA")))
            versionStrings.append({ "hostname": doc["hostname"],
                                    "port": doc["port"],
                                    "versionString": doc["command_output"]["extra"]["versionString"]})
            if len(doc["hostname"]) > max_hostname_length: # TODO Extract this to it's own function so we can reuse
                max_hostname_length = len(doc["hostname"])
        print "Version Strings: "
        for v in versionStrings:
            line = "{:<" + str(max_hostname_length + 2) + "} {:<10} {:<100}"
            print line.format(v["hostname"],
                              v["port"],
                              v["versionString"])

def display_dbHash_info_for_cluster(mmo, c):
    dbHashes = mmo.mmo_list_dbhash_on_cluster(c)

    print "{:<30} {:<10} {:<10} {:<10} {:<10} {:<10}".format("hostname", "shard", "port", "db", "collections", "md5")
    for doc in dbHashes:
        for entry in doc:
            print "{:<30} {:<10} {:<10} {:<10} {:<10} {:<10}".format(entry["hostname"],
                                                                     entry["shard"],
                                                                     entry["port"],
                                                                     entry["db"],
                                                                     len(entry["command_output"]["collections"]),
                                                                     entry["command_output"]["md5"])
    #print dbHashes

def print_server_status_help():
    print "Extracts and displays certain bits of information from the serverStatus document produced in the mongo shell command db.serverStatus()"
    print "Usage: mm --server_status <option>"
    print "Options: "
    print "{:<30} {:<100}".format("instance", "Show the instance info from all the shard mongod processes")
    print "{:<30} {:<100}".format("asserts", "Show the asserts stats from all the shard mongod processes")
    print "{:<30} {:<100}\n{:<30} {:<100}".format("flushing",
                                                  "Show the flushing stats from all the shard mongod processes.",
                                                  "",
                                                  "Only applies to the MMAPv1 engine.")
    print "{:<30} {:<100}\n{:<30} {:<100}".format("journaling",
                                                  "Show the journal stats from all the shard mongod processes.",
                                                  "",
                                                  "Only applies to the MMAPv1 engine and journaling must be enabled.")
    print "{:<30} {:<100}".format("extra_info", "Show the extra_info section from the serverStatus document.")
    print "{:<30} {:<100}".format("connections", "Show the connection stats from all the shard mongod processes")
    print "{:<30} {:<100}".format("global_lock", "Show the global locks stats from all the shard mongod processes")
    print "{:<30} {:<100}".format("network", "Show the network stats from all the shard mongod processes")
    print "{:<30} {:<100}".format("opcounters", "Show the opcounters stats from all the shard mongod processes")
    print "{:<30} {:<100}".format("opcounters_repl", "Show the opcountersRepl stats from all the shard mongod processes")
    print "{:<30} {:<100}".format("security", "Show the security info from all the shard mongod processes")
    print "{:<30} {:<100}".format("storage_engine", "Show the storage engine info from all the shard mongod processes")
    print "{:<30} {:<100}".format("memory", "Show the memory info from all the shard mongod processes")
    print "{:<30} {:<100}".format("show_all", "Show all supported information screens")
    print "{:<30} {:<100}".format("help", "Show this help message")

def print_host_info_help():
    print "Extracts and displays information from the hostInfo document produced in the mongo shell by the mongo shell command db.hostInfo()"
    print "Usage: mm --host_info <option>"
    print "Options: "
    print "{:<30} {:<100}".format("system", "An embedded document providing information about the ",
                                            "underlying environment of the system running the mongod or mongos")
    print "{:<30} {:<100}\n{:<30} {:<100}".format("os",
                                                  "An embedded document that contains information about the operating system ",
                                                  "",
                                                  "running the mongod and mongos.")
    print "{:<30} {:<100}\n{:<30} {:<100}\n{:<30} {:<100}".format("extra",
                                                                  "An embedded document with extra information about the operating ",
                                                                  "",
                                                                "system and the underlying hardware. The content of the extra embedded ",
                                                                  "",
                                                                "document  depends on the operating system.")
    print "{:<30} {:<100}".format("help", "Show this help message")

"""
MAIN SECTION STARTS HERE
"""
parser = argparse.ArgumentParser(description='MongoDB Manager')
parser.add_argument('--summary', action='store_true', help='Show a summary of the MongoDB Cluster Topology')
parser.add_argument('--repl', action='store_true', help='Show a summary of the replicaset state')

server_status_choices = ['instance',
                         'asserts',
                         'flushing',
                         'journaling',
                         'extra_info',
                         'connections',
                         'global_lock',
                         'network',
                         'opcounters',
                         'opcounters_repl',
                         'security',
                         'storage_engine',
                         'memory',
                         'show_all']
parser.add_argument('--server_status', type=str, default="", choices=server_status_choices, help="Show a summary of the appropriate section from the serverStatus document from all mongod processes.")
host_info_choices = ["system",
                     "os",
                     "extra",
                     "help"]
parser.add_argument('--host_info', type=str, default="", choices=host_info_choices, help="Show a summary of the appropriate section from the hostInfo document from all mongod processes.")

parser.add_argument('--dbHashes', action='store_true', help='Show the dbHashes for each database on the cluster and perform some verification.')

parser.add_argument('--inc_mongos', action='store_true', help='Optionally execute against the mongos servers. This will fail if the command is not supported by mongos.')

parser.add_argument("-H", "--mongo_hostname", type=str, default="localhost", required=False, help="Hostname for the MongoDB mongos process to connect to")
parser.add_argument("-P", "--mongo_port", type=int, default=27017, required=False, help="Port for the MongoDB mongos process to connect to")
parser.add_argument("-u", "--mongo_username", type=str, default="admin", required=False, help="MongoDB username")
parser.add_argument("-p", "--mongo_password", type=str, default="admin", required=False, help="MongoDB password")
parser.add_argument("-D", "--mongo_auth_db", type=str, default="admin", required=False, help="MongoDB authentication database")

parser.add_argument("-r", "--repeat", type=int, default=1, required=False, help="Repeat the action N number of times")
parser.add_argument("-i", "--interval", type=int, default=2, required=False, help="Number of seconds between each repeat")

args = parser.parse_args()
# TODO Add hostinfo stuff
###################################################
# Main program starts here
###################################################

mmo = MmoMongoCluster(args.mongo_hostname, args.mongo_port, args.mongo_username, args.mongo_password, args.mongo_auth_db)
c = mmo.mmo_connect()

if c:
    while args.repeat != 0:
        if args.summary or args.server_status == "show_all":
            display_cluster_state(mmo, c)
        if args.repl or args.server_status == "show_all":
            rs = mmo.mmo_replication_status_summary(c)
            print_replication_summary(rs)
        if args.server_status in ["instance", "show_all"]:
            display_instance_info_for_cluster(mmo, c, args.inc_mongos)
        if args.server_status in ["asserts", "show_all"]:
            display_asserts_for_cluster(mmo, c, args.inc_mongos)
        if args.server_status in ["flushing", "show_all"]:
            display_backgroundFlushing_for_cluster(mmo, c, args.inc_mongos)
        if args.server_status in ["journaling", "show_all"]:
            display_journaling_for_cluster(mmo, c, args.inc_mongos)
        if args.server_status in ["extra_info", "show_all"]:
            display_extra_info_for_cluster(mmo, c, args.inc_mongos)
        if args.server_status in ["connections", "show_all"]:
            display_connections_for_cluster(mmo, c, args.inc_mongos)
        if args.server_status in ["global_lock", "show_all"]:
            display_globalLock_for_cluster(mmo, c, args.inc_mongos)
        if args.server_status in ["network", "show_all"]:
            display_network_for_cluster(mmo, c, args.inc_mongos)
        if args.server_status in ["opcounters", "show_all"]:
            display_opcounters_for_cluster(mmo, c, args.inc_mongos, False)
        if args.server_status in ["opcounters_repl", "show_all"]:
            display_opcounters_for_cluster(mmo, c, args.inc_mongos, True)
        if args.server_status in ["security", "show_all"]:
            display_security_for_cluster(mmo, c, args.inc_mongos)
        if args.server_status in ["storage_engine", "show_all"]:
            display_storage_engine_for_cluster(mmo, c, args.inc_mongos)
        if args.server_status in ["memory", "show_all"]:
            display_mem_for_cluster(mmo, c, args.inc_mongos)
        if args.host_info in host_info_choices:
            if args.host_info == "help":
                print_host_info_help()
            else:
                display_host_info_for_cluster(mmo, c, args.inc_mongos, args.host_info)
        if args.dbHashes:
            display_dbHash_info_for_cluster(mmo, c)
        if args.server_status == "help":
            print_server_status_help()
        args.repeat -= 1
        if args.repeat > 0:
            time.sleep(args.interval)
            os.system('cls' if os.name == 'nt' else 'clear')
    else:
        exit(1)






