from pymongo import MongoClient
import re
import datetime

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

    def mmo_connect_mongod(self, hostname, port, username, password, authentication_db):
        """
        Initiates a connection to the MongoDB instance.
        :return:
        """
        client = MongoClient(hostname, port)
        client[authentication_db].authenticate(username, password)
        if self.mmo_is_mongod(client) == False:
            raise Exception("MongoDB connection is not a mongod process")
        else:
            return client

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
            config_servers.append( { "hostname": hostname, "port": int(port) } )
        return config_servers

    def mmo_shard_servers(self, mmo_connection):
        """
        Returns a list of dictionaries containing the hostname and port of the MongoDB cluster's mongos servers.
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
        cluster_command_output = []
        for doc in self.mmo_shard_servers(mmo_connection):
            hostname, port, shard = doc["hostname"], doc["port"], doc["shard"]
            auth_dic = self.mmo_get_auth_details_from_connection(mmo_connection)
            c = self.mmo_connect_mongod(hostname, port, auth_dic["username"], auth_dic["password"], auth_dic["authentication_database"])
            if self.mmo_replica_state(c)["name"] == "PRIMARY" and (replicaset == "all" or replicaset == shard):
                command_output = c["admin"].command(command)
                cluster_command_output.append({ "hostname": hostname, "port": port, "shard": shard, "command_output": command_output })
        return cluster_command_output

    def mmo_execute_on_secondaries(self, mmo_connection, command, replicaset="all"): # TODO add execution database?
        """
        Similar to the mmo_execute_on_cluster method but we only execute on the secondaries.
        :param mmo_connection:
        :param command:
        :param replicaset: Optionally execute against a single replicaset or all
        :return: A list of dictionaries, containing hostname, port, shard and command_output, for each SECONDARY mongod in all shards
        """
        cluster_command_output = []
        for doc in self.mmo_shard_servers(mmo_connection):
            hostname, port, shard = doc["hostname"], doc["port"], doc["shard"]
            auth_dic = self.mmo_get_auth_details_from_connection(mmo_connection)
            c = self.mmo_connect_mongod(hostname, port, auth_dic["username"], auth_dic["password"], auth_dic["authentication_database"])
            if self.mmo_replica_state(c)["name"] == "SECONDARY"  and (replicaset == "all" or replicaset == shard):
                command_output = c["admin"].command(command)
                cluster_command_output.append({ "hostname": hostname, "port": port, "shard": shard, "command_output": command_output })
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
            o = self.mmo_execute_on_primaries(mmo_connection, "replSetGetStatus")
            return o
        else:
            raise Exception("Not a mongos process")

    def mmo_replication_status_summary(self, mmo_connection):
        """
        Returns a list of dictionaries dictionary containing the members of all replicasets in a cluster and some basic info about their status.
        The information returned is from the point of view of the PRIMARY in each replicaset

        Example of data returned:

        [{'configVersion': 3,
          'hostname': u'rhysmacbook.local:30001',
          'optimeDate': datetime.datetime(2016, 3, 27, 15, 4, 26),
          'replicaset': u'rs0',
          'slaveDelay': 0.0,
          'state': u'SECONDARY',
          'uptime': 8212},
         {'configVersion': 3,
          'hostname': u'rhysmacbook.local:30002',
          'optimeDate': datetime.datetime(2016, 3, 27, 15, 4, 26),
          'replicaset': u'rs0',
          'slaveDelay': 0.0,
          'state': u'SECONDARY',
          'uptime': 8212},
         {'configVersion': 3,
          'hostname': u'rhysmacbook.local:30003',
          'optimeDate': datetime.datetime(2016, 3, 27, 15, 4, 26),
          'replicaset': u'rs0',
          'slaveDelay': 'NA',
          'state': u'PRIMARY',
          'uptime': 181773},
         {'configVersion': 3,
          'hostname': u'rhysmacbook.local:30004',
          'optimeDate': datetime.datetime(2016, 3, 27, 15, 4, 26),
          'replicaset': u'rs1',
          'slaveDelay': 0.0,
          'state': u'SECONDARY',
          'uptime': 8205},
         {'configVersion': 3,
          'hostname': u'rhysmacbook.local:30005',
          'optimeDate': datetime.datetime(2016, 3, 27, 15, 4, 26),
          'replicaset': u'rs1',
          'slaveDelay': 'NA',
          'state': u'PRIMARY',
          'uptime': 181773},
         {'configVersion': 3,
          'hostname': u'rhysmacbook.local:30006',
          'optimeDate': datetime.datetime(2016, 3, 27, 15, 4, 26),
          'replicaset': u'rs1',
          'slaveDelay': 0.0,
          'state': u'SECONDARY',
          'uptime': 3878}]

        :param mmo_connection:
        :return: A list of dictionaries
        """
        replication_summary = []
        primary_info = {}
        o = self.mmo_replication_status(mmo_connection)
        for replicaset in o:
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
                doc["slaveDelay"] = "NA" # not relevant here
            else: # calculate the slave lag from the PRIMARY optimeDate
                doc["slaveDelay"] = (doc["optimeDate"] - primary_info[doc["replicaset"]]).total_seconds()
        return replication_summary

    def mmo_cluster_serverStatus(self, mmo_connection, inc_mongos):
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
        return self.mmo_execute_on_cluster(mmo_connection, "serverStatus", inc_mongos)

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
        return self.mmo_execute_on_cluster_on_each_db(mmo_connection, "dbHash", False)

    def mmo_execute_on_cluster_on_each_db(self, mmo_connection, command, inc_mongos):
        command_output = []
        for db in mmo_connection.database_names():
                command_output.append(self.mmo_execute_on_cluster(mmo_connection, command, inc_mongos, db))
        return command_output

    def mmo_step_down(self, mmo_connection, replicaset, stepDownSecs=60, catchUpSecs=50):
        """
        Execute the stepDown command against the PRIMARY for the given shard
        :param mmo_connection:
        :param shard:
        :return:
        """
        stepDownCmd = {'replSetStepDown': stepDownSecs, 'secondaryCatchUpPeriodSecs': catchUpSecs}
        return self.mmo_execute_on_primaries(mmo_connection, stepDownCmd, replicaset)

    def mmo_change_profiling_level(self, mmo_connection, profile, slowms=None):
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
        return self.mmo_execute_on_cluster(mmo_connection, profileCmd)


