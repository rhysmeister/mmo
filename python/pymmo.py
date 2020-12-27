from pymongo import MongoClient
from pymongo import ReturnDocument
from bson import SON
import re, socket, json, os, pickle

class MmoMongoCluster:

    hostname = None
    port = None
    username = None
    password = None
    authentication_db = None
    mongos_servers = []
    config_servers = []
    shard_servers = []
    shards = []
    config_server_repl_name = None

    def __init__(self, hostname, port, username, password, authentication_db):
        """
        Constructor for the pymmmo class. Provide details for conection to the Mongogo cluster.
        :param hostname:
        :param port:
        :param username:
        :param password:
        :param authentication_db:
        :return:
        """
        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password
        self.authentication_db = authentication_db

        c = self.mmo_connect()

        # Cache information about the cluster
        self.mongos_servers = self.mmo_mongos_servers(c)
        self.config_servers = self.mmo_config_servers(c)
        self.shard_servers = self.mmo_shard_servers(c)

        for d in self.shard_servers:
            if d["shard"] not in self.shards:
                self.shards.append(d["shard"])

        self.config_server_repl_name = self.mmo_config_server_replset_name(c)

    def mmo_is_mongo_up(self, hostname, port=27017):
        """
        Detect is mongo is running on the suggested port
        :param port: Default 27017
        :return:
        """
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        service_up = False
        try:
            s.connect((hostname, port))
            service_up = True
            s.close()
        except socket.error as e:
            pass
        except Exception as e:
            raise e
        return service_up

    def mmo_connect(self):
        """
        Initiates a connection to the MongoDB instance. We insist the connection here is a mongos
        :return:
        """
        client = MongoClient(self.hostname, self.port)
        client[self.authentication_db].authenticate(self.username, self.password)
        if self.mmo_is_mongos(client) == False:
            raise Exception("MongoDB connection is not a mongos process")
        else:
            return client

    def mmo_connect_mongod(self, hostname="localhost", port=27017, username="admin", password="admin", authentication_db="admin"):
        """
        Initiates a connection to the MongoDB instance.
        :return:
        """
        if self.mmo_is_mongo_up(hostname, port):
            client = MongoClient(hostname, port)
            client[authentication_db].authenticate(username, password)
            if self.mmo_is_mongod(client) == False:
                raise Exception("MongoDB connection is not a mongod process")
            else:
                return client
        else:
            raise Exception("mongod process is not up")

    def mmo_connect_mongos(self, hostname, port, username, password, authentication_db):
        """
        Initiates a connection to the MongoDB mongos process.
        :return:
        """
        client = MongoClient(hostname, port)
        client[authentication_db].authenticate(username, password)
        if self.mmo_is_mongos(client) == False:
            raise Exception("MongoDB connection is not a mongos process")
        else:
            return client

    def mmo_mongos_servers(self, mmo_connection):
        """
        Returns a list of dictionaries containing the hostname and port of the MongoDB cluster's mongos servers.
        :param mmo_connection:
        :return:
        """
        mongos_servers = []
        c = mmo_connection["config"].mongos.find({}, { "_id": 1 } )
        for doc in c:
            hostname, port = doc["_id"].split(":")
            mongos_servers.append({ "hostname": hostname, "port": int(port) })
        return mongos_servers

    def mmo_config_servers(self, mmo_connection):
        """
        Returns a list of dictionaries containing the hostname and port of the MongoDB cluster's config servers.
        :param mmo_connection:
        :return:
        """
        config_servers = []
        c = mmo_connection["admin"].command("getCmdLineOpts")["parsed"]["sharding"]["configDB"]
        for item in c.split(","):
            hostname, port = item.split(":")
            if "/" in hostname: # cfg Replset server
                hostname = hostname.partition("/")[2]
            config_servers.append( { "hostname": hostname, "port": int(port) } )
        return config_servers

    def mmo_config_server_replset_name(self, mmo_connection):
        """
        Returns the replset name for a group of config server or null if it is not a replset
        :param mmo_connection:
        :return:
        """
        replset_name = None
        c = mmo_connection["admin"].command("getCmdLineOpts")["parsed"]["sharding"]["configDB"]
        for item in c.split(","):
            if "/" in item:  # cfg Replset server
                replset_name = item.partition("/")[0]
                break
        return replset_name

    def mmo_shard_servers(self, mmo_connection):
        """
        Returns a list of dictionaries containing the hostname and port of the MongoDB cluster's mongod servers.
        :param mmo_connection:
        :return:
        """
        shard_servers = []
        c = mmo_connection["config"].shards.find({})
        for doc in c:
            shard = doc["_id"]
            for host in doc["host"].split(shard + "/", 1)[1].split(","):
                hostname, port = host.split(":")
                shard_servers.append({ "shard": shard, "hostname": hostname, "port": int(port) })
        return shard_servers

    def mmo_what_process_am_i(self, mmo_connection):
        """
        Returns the process name for the given Mongo connection.
        :param mmo_connection:
        :return:
        """
        return mmo_connection["admin"].command("serverStatus")["process"];

    def mmo_is_mongos(self, mmo_connection):
        """
        Returns True if the given Mongo connection is a mongos process
        :param mmo_connection:
        :return:
        """
        return True if self.mmo_what_process_am_i(mmo_connection) == "mongos" else False

    def mmo_is_mongod(self, mmo_connection):
        """
        Returns True if the given Mongo connection is a mongod process
        :param mmo_connection:
        :return:
        """
        return True if self.mmo_what_process_am_i(mmo_connection) == "mongod" else False

    def mmo_is_configsrv(self, mmo_connection):
        """
        Returns True if the given Mongo connection is a config server
        :param mmo_connection:
        :return:
        """
        return True if "configsvr" in str(mmo_connection["admin"].command("getCmdLineOpts")["parsed"]) else False

    def mmo_is_cfg_rs(self, mmo_connection):
        """
        Return True if the config server are running in repl set mode
        :param mmo_connection:
        :return:
        """
        s = None
        if self.mmo_is_configsrv(mmo_connection):
            try:
                r =  mmo_connection["admin"].command("replSetGetStatus")
                s = True
            except Exception as exception:
                if "not running with --replSet" in str(exception):
                    s = False
                else:
                    raise exception
        else:
                raise Exception("Not a config server")
        return s

    def mmo_mongo_version(self, mmo_connection):
        """
        Returns the version string for the given Mongo connection.
        :param mmo_connection:
        :return:
        """
        return mmo_connection["admin"].command("serverStatus")["version"]

    def mmo_current_connections(self, mmo_connection):
        """
        Returns the number of connections for the Mongo instance.
        :param mmo_connection:
        :return:
        """
        return mmo_connection.serverStatus()["connection"]["current"]

    def mmo_get_auth_details_from_connection(self, mmo_connection):
        """
        Extracts the username, password and authentication database from an existing mongo connection.
        Probably need a more reliable way of doing this as connection string format might vary???
        :return: A dictionary containing the auth details
        """
        credentials = str(mmo_connection._MongoClient__all_credentials).split(",")
        quoted = re.compile("(?<=')[^']+(?=')")
        username = quoted.findall(credentials[2])[0]
        password = quoted.findall(credentials[3])[0]
        authentication_database = quoted.findall(credentials[1])[0]
        auth_dict = { "username": username, "password": password, "authentication_database": authentication_database }
        return auth_dict

    def mmo_execute_on_mongos(self, mmo_connection, command, execution_database):
        """
        Executes a command against a single mongos server
        :param mmo_connection:
        :param command:
        :return:
        """
        mongos_server = self.mmo_mongos_servers(mmo_connection)[0]
        hostname, port = mongos_server["hostname"], mongos_server["port"]
        auth_dic = self.mmo_get_auth_details_from_connection(mmo_connection)
        c = self.mmo_connect_mongos(hostname, port, auth_dic["username"], auth_dic["password"], auth_dic["authentication_database"])
        command_output = c[execution_database].command(command)
        return command_output

    def mmo_execute_query_on_mongos(self, mmo_connection, query, execution_database, collection, find_one=False):
        """
        Execute a query against a single mongos server and returns the resulting documents
        :param self:
        :param mmo_connection:
        :param query: Standard MongoDB query document
        :param execution_database:
        :param collection:
        :return:
        """
        mongos_server = self.mmo_mongos_servers(mmo_connection)[0]
        hostname, port = mongos_server["hostname"], mongos_server["port"]
        auth_dic = self.mmo_get_auth_details_from_connection(mmo_connection)
        c = self.mmo_connect_mongos(hostname, port, auth_dic["username"], auth_dic["password"], auth_dic["authentication_database"])
        if find_one:
            query_output = c[execution_database][collection].find_one(query)
        else:
            query_output = c[execution_database][collection].find(query)
        return query_output

    def mmo_execute_update_on_mongos(self, mmo_connection, query, update_document, execution_database, collection, is_update_one=True, upsert=False):
        """
        Executes an update command on mongos
        :param mmo_connection:
        :param query:
        :param update_document:
        :param execution_database:
        :param collection:
        :param is_update_one
        :param upsert
        :return:
        """
        mongos_server = self.mmo_mongos_servers(mmo_connection)[0]
        hostname, port = mongos_server["hostname"], mongos_server["port"]
        auth_dic = self.mmo_get_auth_details_from_connection(mmo_connection)
        c = self.mmo_connect_mongos(hostname,
                                    port,
                                    auth_dic["username"],
                                    auth_dic["password"],
                                    auth_dic["authentication_database"])
        if is_update_one:
            update_output = c[execution_database][collection].find_one_and_update(query, update_document, return_document=ReturnDocument.AFTER, upsert=upsert)
        else:
            update_output = c[execution_database][collection].find_many_and_update(query, update_document, return_document=ReturnDocument.AFTER, upsert=upsert)
        return update_output

    def mmo_execute_on_cluster(self, mmo_connection, command, inc_mongos=False, execution_database="admin"):
        """
        Execute a command on all shard servers (mongod), in a MongoDB Cluster. All commands are executed in the context of the admin database
        :param mmo_connection:
        :param command: The command to execute. This should be a string.
        :param: inc_mongos: Optionally execute the command on the mongos servers
        :return: A list of dictionaries, containing hostname, port, shard and command_output, for each mongod in all shards
        """
        cluster_command_output = []
        for doc in self.mmo_shard_servers(mmo_connection):
            hostname, port, shard = doc["hostname"], doc["port"], doc["shard"]
            auth_dic = self.mmo_get_auth_details_from_connection(mmo_connection)
            c = self.mmo_connect_mongod(hostname, port, auth_dic["username"], auth_dic["password"], auth_dic["authentication_database"])
            command_output = c[execution_database].command(command)
            cluster_command_output.append({ "hostname": hostname, "port": port, "shard": shard, "command_output": command_output, "db": execution_database })
        if inc_mongos:
            for doc in self.mmo_mongos_servers(mmo_connection):
                hostname, port = doc["hostname"], doc["port"]
                auth_dic = self.mmo_get_auth_details_from_connection(mmo_connection)
                c = self.mmo_connect_mongos(hostname, port, auth_dic["username"], auth_dic["password"], auth_dic["authentication_database"])
                command_output = c[execution_database].command(command)
                cluster_command_output.append({ "hostname": hostname, "port": port, "shard": "NA", "command_output": command_output })
        return cluster_command_output

    def mmo_execute_on_primaries(self, mmo_connection, command, replicaset="all"):  # TODO add execution database?
        """
        Similar to the mmo_execute_on_cluster method but we only execute on the primaries.
        :param mmo_connection:
        :param command
        :param replicaset Optionally execute against a single replicaset or all
        :return: A list of dictionaries, containing hostname, port, shard and command_output, for each PRIMARY mongod in all shards
        """

        auth_dic = self.mmo_get_auth_details_from_connection(mmo_connection)

        cluster_command_output = []
        if replicaset == self.config_server_repl_name: # Config server replset
            for doc in self.mmo_config_servers(mmo_connection):
                hostname, port = doc["hostname"], doc["port"]
                try:
                    c = self.mmo_connect_mongod(hostname, port, auth_dic["username"], auth_dic["password"],auth_dic["authentication_database"])
                    if self.mmo_replica_state(c)["name"] == "PRIMARY":
                        command_output = c["admin"].command(command)
                        cluster_command_output.append({"hostname": hostname, "port": port, "shard": replicaset, "command_output": command_output})
                except Exception as excep:
                    if str(excep) == "mongod process is not up":
                        cluster_command_output.append({"hostname": hostname, "port": port, "shard": replicaset, "command_output": {"Error": "mongod process is not up"}})
                    else:
                        raise excep
        else:
            for doc in self.mmo_shard_servers(mmo_connection):
                hostname, port, shard = doc["hostname"], doc["port"], doc["shard"]

                try:
                    c = self.mmo_connect_mongod(hostname, port, auth_dic["username"], auth_dic["password"], auth_dic["authentication_database"])
                    if self.mmo_replica_state(c)["name"] == "PRIMARY" and (replicaset == "all" or replicaset == shard):
                        command_output = c["admin"].command(command)
                        cluster_command_output.append({ "hostname": hostname, "port": port, "shard": shard, "command_output": command_output })
                except Exception as excep:
                    if str(excep) == "mongod process is not up":
                        cluster_command_output.append({ "hostname": hostname, "port": port, "shard": shard, "command_output": { "Error": "mongod process is not up" } })
                    else:
                        raise excep
        return cluster_command_output

    def mmo_execute_on_secondaries(self, mmo_connection, command, replicaset="all", first_available_only=False): # TODO add execution database?
        """
        Similar to the mmo_execute_on_cluster method but we only execute on the secondaries.
        :param mmo_connection:
        :param command:
        :param replicaset: Optionally execute against a single replicaset or all
        :param first_available_only: Only execute against a single secondary, quit when first sucessful
        :return: A list of dictionaries, containing hostname, port, shard and command_output, for each SECONDARY mongod in all shards
        """
        cluster_command_output = []
        replsets_completed = []

        auth_dic = self.mmo_get_auth_details_from_connection(mmo_connection)

        if replicaset == self.config_server_repl_name: # Config server replset
            for doc in self.mmo_config_servers(mmo_connection):
                hostname, port = doc["hostname"], doc["port"]
                try:
                    c = self.mmo_connect_mongod(hostname, port, auth_dic["username"], auth_dic["password"],auth_dic["authentication_database"])
                    if self.mmo_replica_state(c)["name"] == "SECONDARY":
                        command_output = c["admin"].command(command)
                        cluster_command_output.append({"hostname": hostname, "port": port, "shard": replicaset, "command_output": command_output})
                except Exception as excep:
                    if str(excep) == "mongod process is not up":
                        cluster_command_output.append({"hostname": hostname, "port": port, "shard": replicaset, "command_output": {"Error": "mongod process is not up"}})
                    else:
                        raise excep
        else:
            for doc in self.mmo_shard_servers(mmo_connection):
                hostname, port, shard = doc["hostname"], doc["port"], doc["shard"]
                try:

                    c = self.mmo_connect_mongod(hostname, port, auth_dic["username"], auth_dic["password"], auth_dic["authentication_database"])
                    if self.mmo_replica_state(c)["name"] == "SECONDARY"  \
                            and (replicaset == "all" or replicaset == shard)\
                            and shard not in replsets_completed:
                        command_output = c["admin"].command(command)
                        cluster_command_output.append({ "hostname": hostname, "port": port, "shard": shard, "command_output": command_output })
                        if first_available_only:
                            replsets_completed.append(shard)
                except Exception as excep:
                    if str(excep) == "mongod process is not up":
                        cluster_command_output.append({"hostname": hostname, "port": port, "shard": shard, "command_output": {"Error": "This mongod process is not available"}})
                    else:
                        raise excep
        return cluster_command_output


    def mmo_replica_state(self, mmo_connection):
        """
        Return a string of the current replica state for the provided MongoD connection
        :param mmo_connection:
        :return: A string indicating the replica state
        """

        # https://docs.mongodb.org/manual/reference/replica-states/
        replica_states = [
            { "id": 0, "name": "STARTUP", "description": "Not yet an active member of any set. All members start up in this state. The mongod parses the replica set configuration document while in STARTUP." },
            { "id": 1, "name": "PRIMARY", "description": "The member in state primary is the only member that can accept write operations." },
            { "id": 2, "name": "SECONDARY", "description": "A member in state secondary is replicating the data store. Data is available for reads, although they may be stale." },
            { "id": 3, "name": "RECOVERING", "description": "Can vote. Members either perform startup self-checks, or transition from completing a rollback or resync." },
            { "id": 5, "name": "STARTUP2", "description": "The member has joined the set and is running an initial sync." },
            { "id": 6, "name": "UNKNOWN", "description": "The member's state, as seen from another member of the set, is not yet known." },
            { "id": 7, "name": "ARBITER", "description": "Arbiters do not replicate data and exist solely to participate in elections." },
            { "id": 8, "name": "DOWN", "description": "The member, as seen from another member of the set, is unreachable." },
            { "id": 9, "name": "ROLLBACK", "description": "This member is actively performing a rollback. Data is not available for reads." },
            { "id": 10, "name": "REMOVED", "description": "This member was once in a replica set but was subsequently removed." }
        ]

        if self.mmo_is_mongod(mmo_connection):
            return replica_states[mmo_connection["admin"].command("replSetGetStatus")["myState"]]
        else:
            raise Exception("Not a mongod process")

    def mmo_replset_has_primary(self, mmo_connection, rs):
        """
        Returns true if a replicaset has a PRIMARY
        :param mmo_connection:
        :param rs:
        :return:
        """
        rs_status = self.mmo_execute_on_secondaries(mmo_connection, { "replSetGetStatus": 1 }, replicaset=rs, first_available_only=True)
        has_primary = False


        for member in rs_status[0]["command_output"]["members"]:
            if member["stateStr"] == "PRIMARY":
                has_primary = True
                break
        return has_primary

    def mmo_shards(self):
        """
        Returns a list of the shard names for the cluster
        :param mmo_connection:
        :return:
        """
        return self.shards

    def mmo_replication_status(self, mmo_connection):
        """
        Returns a list of dictionaries containing the slaves of a replicaset and their status
        :param mmo_connection:
        :return: A list of dictionaries
        """
        replication_state = []
        if self.mmo_is_mongos(mmo_connection):
            #o = self.mmo_execute_on_primaries(mmo_connection, "replSetGetStatus")
            o = self.mmo_execute_on_secondary_or_primary(mmo_connection, "replSetGetStatus", "all", True)
            #print o2;
            return o
        else:
            raise Exception("Not a mongos process")

    def mmo_configsrv_replication_status(self, mmo_connection):
        """
        If the config sevrer are running in repl set mode return that info, else nothing
        """
        replication_state = []
        if self.mmo_is_mongos(mmo_connection):
            configsrv = self.mmo_config_servers(mmo_connection)[0]
            auth_dic = self.mmo_get_auth_details_from_connection(mmo_connection)
            c = self.mmo_connect_mongod(hostname=configsrv["hostname"],
               	                        port=configsrv["port"],
                       	                username=auth_dic["username"],
                               	        password=auth_dic["password"],
                                       	authentication_db=auth_dic["authentication_database"]
                                       	)
        if self.mmo_is_cfg_rs(c):
            command_output = c["admin"].command("replSetGetStatus")
            shard = command_output["set"]
            replication_state.append({"hostname": configsrv["hostname"], "port": configsrv["port"], "shard": shard, "command_output": command_output})
        else:
            raise Exception("Not a mongos process")
        return replication_state

    def mmo_replication_status_summary(self, mmo_connection):
        """
        Returns a list of dictionaries dictionary containing the members of all replicasets in a cluster and some basic info about their status.
        The information returned is from the point of view of the PRIMARY in each replicaset

        Example of data returned:

        [{'configVersion': 3,
          'hostname': u'rhysmacbook.local:30001',
          'optimeDate': datetime.datetime(2016, 3, 27, 15, 4, 26),
          'replicaset': u'rs0',
          'lag': 0.0,
          'state': u'SECONDARY',
          'uptime': 8212},
         {'configVersion': 3,
          'hostname': u'rhysmacbook.local:30002',
          'optimeDate': datetime.datetime(2016, 3, 27, 15, 4, 26),
          'replicaset': u'rs0',
          'lag': 0.0,
          'state': u'SECONDARY',
          'uptime': 8212},
         {'configVersion': 3,
          'hostname': u'rhysmacbook.local:30003',
          'optimeDate': datetime.datetime(2016, 3, 27, 15, 4, 26),
          'replicaset': u'rs0',
          'lag': 'NA',
          'state': u'PRIMARY',
          'uptime': 181773},
         {'configVersion': 3,
          'hostname': u'rhysmacbook.local:30004',
          'optimeDate': datetime.datetime(2016, 3, 27, 15, 4, 26),
          'replicaset': u'rs1',
          'lag': 0.0,
          'state': u'SECONDARY',
          'uptime': 8205},
         {'configVersion': 3,
          'hostname': u'rhysmacbook.local:30005',
          'optimeDate': datetime.datetime(2016, 3, 27, 15, 4, 26),
          'replicaset': u'rs1',
          'lag': 'NA',
          'state': u'PRIMARY',
          'uptime': 181773},
         {'configVersion': 3,
          'hostname': u'rhysmacbook.local:30006',
          'optimeDate': datetime.datetime(2016, 3, 27, 15, 4, 26),
          'replicaset': u'rs1',
          'lag': 0.0,
          'state': u'SECONDARY',
          'uptime': 3878}]

        :param mmo_connection:
        :return: A list of dictionaries
        """
        replication_summary = []
        primary_info = {}
        o = self.mmo_replication_status(mmo_connection)
        o = o + self.mmo_configsrv_replication_status(mmo_connection)
        replset_hosts_up_down = {}
        for shard in self.shards:
            replset_hosts_up_down[shard] = 0
        for replicaset in o:
            if "Error" not in replicaset["command_output"].keys():
                for member in replicaset["command_output"]["members"]:
                    if member["stateStr"] == "PRIMARY":
                        primary_info[replicaset["command_output"]["set"]] = member["optimeDate"]

                    replication_summary.append( { "replicaset": replicaset["command_output"]["set"],
                                                  "hostname": member["name"],
                                                  "state": member["stateStr"],
                                                  "uptime": member["uptime"],
                                                  "configVersion": member["configVersion"],
                                                  "optimeDate": member["optimeDate"] } )
                for doc in replication_summary:
                    if doc["state"] == "PRIMARY":
                        doc["lag"] = "NA" # not relevant here
                    else: # calculate the slave lag from the PRIMARY optimeDate
                        if doc["replicaset"] in primary_info.keys(): # is there a primary in the replset?
                            try:
                                if hasattr((doc["optimeDate"] - primary_info[doc["replicaset"]]), "total_seconds"): # Does not exist in python 2.6
                                    doc["lag"] = abs((doc["optimeDate"] - primary_info[doc["replicaset"]]).total_seconds())
                                else: # for python 2.6 that does not have total_seconds attribute
                                      # Will only be correct for delays of up to 24 hours
                                    doc["lag"] = abs((doc["optimeDate"] - primary_info[doc["replicaset"]]).seconds) # Primary needs ot be first in this case
                            except:
                                doc["lag"] = "ERR"
                        else:
                            doc["lag"] = "UNK" # We cannot know what the delay is if there is no primary
            else:
                replset_hosts_up_down[replicaset["shard"]] += 1

            #else: Probably redundant code now. Removed ot fix https://github.com/rhysmeister/mmo/issues/34
                    # We cannot know the state of much of the replicaset at this point
            #        replication_summary.append({"replicaset": replicaset["shard"],
            #                                  "hostname": "UNK",
            #                                    "state": "UNK",
            #                                    "uptime": "UNK",
            #                                    "configVersion": "UNK",
            #                                    "optimeDate": "UNK"})


        shard_server_count = {}
        # how many servers in each shard
        for shard in self.shards:
            shard_server_count[shard] = 0
        for s in self.shard_servers:
            shard_server_count[s['shard']] += 1
        # are all the hosts of any shard down?
        for shard in self.shards:
            if replset_hosts_up_down[shard] > 0:
                if replset_hosts_up_down[shard] == shard_server_count[shard]:
                    replication_summary.append({"replicaset": shard,
                                                "hostname": "UNK",
                                                "state": "UNK",
                                                "uptime": "UNK",
                                                "configVersion": "UNK",
                                                "optimeDate": "UNK",
                                                "lag": "UNK"})
        deduped_replication_summary = []
        for d in replication_summary:
            if d not in deduped_replication_summary:
                deduped_replication_summary.append(d)
        return deduped_replication_summary

    def mmo_cluster_serverStatus(self, mmo_connection, inc_mongos, poll=False):
        """
        Return the output of the db.serverStatus() command from all mongod shard servers
        :param self:
        :param mmo_connection:
        :param inc_mongos: Optionally execute on the mongos servers.
        :return: A list of dictionaries - { "hostname": <hostname>,
                                            "port": port,
                                            "shard": <rs name>,
                                            "command_output" <serverStatus doc> }
        See https://docs.mongodb.org/manual/reference/command/serverStatus/#output
        """
        serverStatus = self.mmo_execute_on_cluster(mmo_connection, "serverStatus", inc_mongos)
        if os.path.exists("/tmp/server_status.p"):
            os.rename("/tmp/server_status.p", "/tmp/server_status.previous")
        pickle.dump(serverStatus, open("/tmp/server_status.p", "wb"))
        return serverStatus

    def mmo_cluster_hostInfo(self, mmo_connection, inc_mongos):
        """
        Return the output of the db.hostInfo() command from all mongod shard servers
        :param mmo_connection:
        :param inc_mongos:
        :return: A list of dictionaries - { "hostname": <hostname>,
                                            "port": port,
                                            "shard": <rs name>,
                                            "command_output" <hostInfo doc> }
        See https://docs.mongodb.org/manual/reference/command/hostInfo/
        """
        return self.mmo_execute_on_cluster(mmo_connection, "hostInfo", inc_mongos)

    def mmo_list_databases_on_cluster(self, mmo_connection, inc_mongos):
        return self.mmo_execute_on_cluster(mmo_connection, "listDatabases", inc_mongos)

    def mmo_list_collections_on_cluster(self, mmo_connection, inc_mongos, db):
        return self.mmo_execute_on_cluster(mmo_connection, "listCollections", inc_mongos, db)

    def mmo_list_dbhash_on_cluster(self, mmo_connection):
        # The dbHash command only functions on mongod shard servers or config servers
        return self.mmo_execute_on_cluster_on_each_db(mmo_connection, "dbHash", False, False)

    def mmo_execute_on_cluster_on_each_db(self, mmo_connection, command, inc_mongos, all_collections):
        command_output = []
        for db in mmo_connection.database_names():
                if all_collections:
                    for collection in mmo_connection[db].collection_names():
                        command_output.append(self.mmo_execute_on_cluster(mmo_connection, command, inc_mongos, db))
                else:
                    command_output.append(self.mmo_execute_on_cluster(mmo_connection, command, inc_mongos, db))
        return command_output

    def mmo_step_down(self, mmo_connection, replicaset, stepDownSecs=60, catchUpSecs=50, force=False):
        """
        Execute the stepDown command against the PRIMARY for the given shard
        :param mmo_connection:
        :param shard:
        :return:
        """
        if force:
            stepDownCmd = SON([('replSetStepDown', stepDownSecs),
                               ('secondaryCatchUpPeriodSecs', catchUpSecs),
                               ("force", True)])
        else:
            stepDownCmd = {'replSetStepDown': stepDownSecs, 'secondaryCatchUpPeriodSecs': catchUpSecs}
        return self.mmo_execute_on_primaries(mmo_connection, stepDownCmd, replicaset)

    def mmo_change_profiling_level(self, mmo_connection, profile, slowms=None, database=None):
        """
        Manages the profiling level of a MongoDB Cluster. https://docs.mongodb.com/manual/reference/command/profile/
        Level	Setting
        -1	No change. Returns the current profile level.
        0	Off. No profiling. The default profiler level.
        1	On. Only includes slow operations.
        2	On. Includes all operations.
        :param profile:
        :param slowms:
        :return:
        """
        if profile not in [-1, 0, 1, 2]:
            raise("ERROR: Not a valid profile level.")
        if slowms is not None and profile in [1, 2]:
            profileCmd = { 'profile': profile, 'slowms': slowms }
        else:
            profileCmd = { 'profile': profile }
        if database == "*":
            raise NotImplementedError("Not yet implemented")
            #o = self.mmo_execute_on_cluster_on_each_db(mmo_connection, profileCmd, False)
            #print o
        else:
            o = self.mmo_execute_on_cluster(mmo_connection, profileCmd, False, database)
        return o

    def mmo_sharding_status(self, mmo_connection):
        """
        :param mmo_connection:
        :return:
        """
        return self.mmo_execute_on_mongos(mmo_connection, "listShards", "admin")

    def mmo_repl_set_freeze(self, mmo_connection, hostname, port, seconds):
        """
        Execute the replSetFreeze command against the given MongoDB shard server. The instance will
        not be eligible for election to PRIMARY until the period of time indicated by seconds has passed
        :param mmo_connection:
        :return:
        """
        auth_dic = self.mmo_get_auth_details_from_connection(mmo_connection)
        c = self.mmo_connect_mongod(hostname, port, auth_dic["username"], auth_dic["password"], auth_dic["authentication_database"])
        if self.mmo_is_mongod(c):
            try:
                command_output = c["admin"].command({ "replSetFreeze": seconds })
            except Exception as excep:
                if str(excep) == "cannot freeze node when primary or running for election. state: Primary":
                    command_output = { "msg": str(excep)}
                    pass
                else:
                    raise excep
        else:
            raise Exception("MongoDB connection is not a mongod process")
        return { "hostname": hostname, "port": port, "command_output": command_output }

    def mmo_repl_set_freeze_nominate_host(self, mmo_connection, nominate_hostname, nominate_port, replicaset, seconds):
        """
        This function calls the mmo_repl_set_freeze command against all hosts in a replicaset
        excluding the specified mongo instance.
        :param mmo_connection:
        :param nominate_host: Used in conjunction with nominate_port to influence who becomes PRIMARY
        :param nominate_port:
        :param replicaset:
        :param seconds:
        :return: A list of dictionaries. { "hostname": <hostname>, "port": <port>, "command_output": <command_output> }
        """
        freeze_count = 0 # How many servers have we execute the freeze command against?
        command_output = []
        for shard_host in self.mmo_shard_servers(mmo_connection):
            if shard_host["shard"] == replicaset:
                if (shard_host["hostname"] + ":" + str(shard_host["port"])) != (nominate_hostname + ":" + str(nominate_port)):
                    tmp = self.mmo_repl_set_freeze(mmo_connection, shard_host["hostname"], shard_host["port"], seconds)
                    command_output.append(tmp)
                    freeze_count = freeze_count + 1
        if freeze_count == 0:
            raise Exception("No MongoDB shard servers were frozen. Please check the command.")
        return command_output

    def mmo_verify_indexes_on_collection(self, mmo_connection, execution_database, collection):
        """
        Validate the count and structure of the specified collection on all replicaset hosts  on the cluster
        :param mmo_connection:
        :param db:
        :param collection:
        :return:
        """
        cluster_command_output = []
        for doc in self.mmo_shard_servers(mmo_connection):
            hostname, port, shard = doc["hostname"], doc["port"], doc["shard"]
            auth_dic = self.mmo_get_auth_details_from_connection(mmo_connection)
            c = self.mmo_connect_mongod(hostname,
                                        port,
                                        auth_dic["username"],
                                        auth_dic["password"],
                                        auth_dic["authentication_database"])
            msg = ""
            try:
                if collection in c[execution_database].collection_names():
                    command_output = c[execution_database][collection].list_indexes()
                    list_of_indexes = []
                    for index in command_output:
                        list_of_indexes.append(index)
                    sorted(list_of_indexes)
                else:
                    list_of_indexes = []
                    msg = "Collection does not exist on host"
            except Exception as exception:
                raise exception
            cluster_command_output.append({ "hostname": hostname, "port": port, "shard": shard, "command_output": list_of_indexes, "db": execution_database, "msg": msg })
        return cluster_command_output

    def mmo_collection_stats(self, mmo_connection, execution_database, collection):
        """
        A wrapper around the db.collection.stats() command
        :param mmo_connection:
        :param execution_database:
        :param collection:
        :return:
        """
        command = { "collStats": collection }
        return self.mmo_execute_on_mongos(mmo_connection, command, execution_database)

    def mmo_database_stats(self, mmo_connection, database):
        """
        A wrapper around the db.stats() command
        :param mmo_connection:
        :param database:
        :return:
        """
        command = { "dbstats" : 1 }
        return self.mmo_execute_on_mongos(mmo_connection, command, database)

    def mmo_schema_sumary(self, mmo_connection, schema, limit=200):
        if "." not in schema:
            raise Exception("schema must be supplied in the format <database>.<collection>")
        else:
            database, collection = schema.split(".")
            mongos_server = self.mmo_mongos_servers(mmo_connection)[0]
            hostname, port = mongos_server["hostname"], mongos_server["port"]
            auth_dic = self.mmo_get_auth_details_from_connection(mmo_connection)
            c = self.mmo_connect_mongos(hostname,
                                        port,
                                        auth_dic["username"],
                                        auth_dic["password"],
                                        auth_dic["authentication_database"])
            query_output = c[database][collection].find({}).limit(limit)
            my_schema = {}
            for document in query_output:
                my_schema.update(document)
            return my_schema


    def mmo_replicaset_conf(self, mmo_connection):
        """
        Get the output of rs.conf()
        """
        command = {"replSetGetConfig" : 1}
        return self.mmo_execute_on_primaries(mmo_connection, command)

    def mmo_plan_cache(self, mmo_connection, database, collection):
        """
        Return the contents of the plane cache
        :param mmo_connection:
        :return:
        """
        command = {"planCacheListQueryShapes": collection}
        return self.mmo_execute_on_cluster(mmo_connection, command, False, database)


    def mmo_plan_cache_query(self, mmo_connection, database, collection, query, sort, projection):
        """
        Return the contents of the plane cache
        :param mmo_connection:
        :return:
        """
        command = SON([
                            ("planCacheListPlans", collection),
                            ("query", json.loads(query.replace("'", "\"")) if type(query) != dict else query),
                            ("projection", json.loads(projection.replace("'", "\"")) if type(projection) != dict else projection),
                            ("sort", json.loads(sort.replace("'", "\"")) if type(sort) != dict else sort)
                    ])
        return self.mmo_execute_on_cluster(mmo_connection, command, False, database)

    def mmo_plan_cache_clear(self, mmo_connection, database, collection, query, sort, projection):
        """
        Clear a query from the plan cache
        :param mmo_connection:
        :param database:
        :param collection:
        :param query:
        :param sort:
        :param projection:
        :return:
        """
        command = SON([
                                ("planCacheClear", collection),
                                ("query", json.loads(query.replace("'", "\"")) if type(query) != dict else query),
                                ("projection", json.loads(projection.replace("'", "\"")) if type(projection) != dict else projection),
                                ("sort", json.loads(sort.replace("'", "\"")) if type(sort) != dict else sort)
        ])
        return self.mmo_execute_on_cluster(mmo_connection, command, False, database)

    def mmo_chunks(self, mmo_connection):
        command = {
                        "aggregate": "chunks",
                        "pipeline": [ { "$group": { "_id" : { "ns": "$ns", "shard": "$shard" }, "count" : { "$sum": 1 } } } ],
                    }
        return self.mmo_execute_on_mongos(mmo_connection, command, "config")["result"]

    def mmo_sharded_collection_details(self, mmo_connection):
        return self.mmo_execute_query_on_mongos(mmo_connection, {}, "config", "collections", False)


    def mmo_execute_on_secondary_or_primary(self, mmo_connection, command, replicaset="all", first_available_only=False):  # TODO add execution database?
        """
        Execute on SECONDARY but go for PRIMARY if fails. Shoudl probably only use this in the --repl screen
        :param mmo_connection:
        :param command:
        :param replicaset: Optionally execute against a single replicaset or all
        :param first_available_only: Only execute against a single secondary, quit when first sucessful
        :return: A list of dictionaries, containing hostname, port, shard and command_output, for each SECONDARY mongod in all shards
        """
        cluster_command_output = []
        replsets_completed = set()
        all_replsets = set()
        repl_hosts = self.mmo_shard_servers(mmo_connection)
        for doc in repl_hosts:
            hostname, port, shard = doc["hostname"], doc["port"], doc["shard"]
            all_replsets.add(shard)
            auth_dic = self.mmo_get_auth_details_from_connection(mmo_connection)
            try:
                c = self.mmo_connect_mongod(hostname, port, auth_dic["username"], auth_dic["password"],
                                            auth_dic["authentication_database"])
                if self.mmo_replica_state(c)["name"] == "SECONDARY" \
                        and (replicaset == "all" or replicaset == shard) \
                        and shard not in replsets_completed:
                    secondary_found = True
                    command_output = c["admin"].command(command)
                    cluster_command_output.append(
                        {"hostname": hostname, "port": port, "shard": shard, "command_output": command_output})
                    #if first_available_only:
                    replsets_completed.add(shard)
            except Exception as excep:
                if str(excep) == "mongod process is not up":
                    cluster_command_output.append({"hostname": hostname, "port": port, "shard": shard,
                                                   "command_output": {"Error": "This mongod process is not available"}})
                else:
                        raise excep
        # This is the case where there are no secondaries
        for missing_shard in (all_replsets^replsets_completed):
            for doc in repl_hosts:
                hostname, port, shard = doc["hostname"], doc["port"], doc["shard"]
                try:
                    c = self.mmo_connect_mongod(hostname, port, auth_dic["username"], auth_dic["password"],
                                                auth_dic["authentication_database"])
                    if shard == missing_shard and self.mmo_replica_state(c)["name"] == "PRIMARY":
                        command_output = c["admin"].command(command)
                        cluster_command_output.append({"hostname": hostname, "port": port, "shard": shard, "command_output": command_output})
                except Exception as excep:
                    if str(excep) == "mongod process is not up":
                        cluster_command_output.append({"hostname": hostname, "port": port, "shard": shard,
                                                   "command_output": {"Error": "This mongod process is not available"}})
                    else:
                        raise excep
        return cluster_command_output
