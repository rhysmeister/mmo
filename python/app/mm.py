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
MAIN SECTION STARTS HERE
"""
parser = argparse.ArgumentParser(description='MongoDB Manager')
parser.add_argument('--summary', action='store_true', help='Show a summary of the MongoDB Cluster Topology')
parser.add_argument('--repl', action='store_true', help='Show a summary of the replicaset state')
parser.add_argument('--show_all', action='store_true', help='Show all information screens')
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
        args.repeat -= 1
        if args.repeat > 0:
            time.sleep(args.interval)
            sys.stdout.flush()
    else:
        exit(1)






