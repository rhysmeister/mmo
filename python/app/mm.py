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

execfile(os.path.dirname(os.path.abspath(inspect.stack()[0][1]))  + "/../pymmo/pymmo.py")

def display_cluster_state(mmo):
    """
    Print out a overview of the MongoDB Cluster and its status. The inital connection should be a mongos for this to work correctly.
    :param self:
    :param mmo: A instance of the MmoMongoCluster class
    :return:
    """
    c = mmo.mmo_connect()
    config_servers = mmo.mmo_config_servers(c)
    mongos_servers = mmo.mmo_mongos_servers(c)
    mongod_shard_servers = mmo.mmo_shard_servers(c)
    shards = mmo.mmo_shards()
    print_list_of_hosts("MongoDB Config Servers", config_servers)
    print_list_of_hosts("MongoDB mongos servers", mongos_servers)
    print_list_of_hosts("MongoDB mongod shard servers", mongod_shard_servers)
    print "MongoDB shards"
    for shard in shards:
        sys.stdout.write("{0}   ".format(shard))
    print ""
    rs = mmo.mmo_replication_status_summary(c)
    print_replication_summary(rs)

def print_replication_summary(replication_summary):
    print "{:<30} {:<10} {:<10} {:<10} {:<10} {:<10}".format("hostname", "replicaset", "state", "configV", "uptime", "slaveDelay")
    for host in replication_summary:
        print "{:<30} {:<10} {:<10} {:<10} {:<10} {:<10}".format(host["hostname"], host["replicaset"], host["state"], host["configVersion"], host["uptime"], host["slaveDelay"])


def print_list_of_hosts(title, host_list):
    """
    Prints the title followed by the hosts in the list.
    :param title:
    :param host_list: [ { "hostname": <string>, "port": <int> }, ...]
    :return:
    """
    print title
    print_count = 0
    for host in host_list:
        if print_count % 3 == 0: # max 3 hosts per line
            print ""
        sys.stdout.write("{0}:{1}      ".format(host["hostname"], host["port"]))
        print_count+=1
    print ""

# Just connect to the default host for now. Options to come later
mmo = MmoMongoCluster("localhost", 27017, "admin", "admin", "admin")
display_cluster_state(mmo)





