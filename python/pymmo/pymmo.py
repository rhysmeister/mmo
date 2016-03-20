from pymongo import MongoClient

class MmoMongoCluster:

    hostname = None
    port = None
    username = None
    password = None
    authentication_db = None
    mongos_servers = []
    config_servers = []
    shard_servers = []

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

    def mmo_connect(self):
        """
        Initiates a connection to the MongoDB instance.
        :return:
        """
        client = MongoClient(self.hostname, self.port)
        client[self.authentication_db].authenticate(self.username, self.password)
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



