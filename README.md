mm              mm User Manual              mm

NAME
        mm

SYNOPSYS

        mm [-h] [--summary] [--repl]
                  [--server_status {instance,asserts,flushing,journaling,extra_info,connections,global_lock,network,opcounters,opcounters_repl,security,storage_engine,memory,show_all}]
                  [--host_info {system,os,extra,help}] [--db_hashes] [--databases]
                  [--inc_mongos] [--step_down STEP_DOWN]
                  [--step_down_nominate_host STEP_DOWN_NOMINATE_HOST]
                  [--step_down_nominate_port STEP_DOWN_NOMINATE_PORT]
                  [--replset_freeze REPLSET_FREEZE] [--profiling {-1,0,1,2}]
                  [--slowms SLOWMS] [--sharding] [-H MONGO_HOSTNAME] [-P MONGO_PORT]
                  [-u MONGO_USERNAME] [-p MONGO_PASSWORD] [-D MONGO_AUTH_DB]
                  [-e EXECUTION_DATABASE] [-r REPEAT] [-i INTERVAL] [-c CONNECTION]
                  [-d] [--validate_indexes VALIDATE_INDEXES]
                  [--collection_stats COLLECTION_STATS]
                  [--database_stats DATABASE_STATS]
                  [--command COMMAND] [--balancing {enable,disable}]
                  [--collection COLLECTION] [--verbose_display] [--stacktrace]

DESCRIPTION

        mm is a tool for monitoring and managing MongoDB sharded clusters.

CONNECTION OPTIONS

    Connecting to a MongoDB Cluster can be performed in a couple of ways; Via command-line flags or by using a configuration file. Whichever method is used the initial connection must be a mongos server. mm handles the connections to other server internally. This means you must have created the same user, with the same authentication details, on all replicasets in the cluster.

    Connecting via the command-line

    -H - The host to connect to. Default 'localhost'.
    -P - The port to connect to. Default 27017.
    -u - The username for the connection. Default 'admin'.
    -p - password.
    -D - The database to authentication against. Default 'admin'.

    ./mm -H localhost -P 27017 -u admin -p secret -D admin

    Connecting via a configuration file

    By default mm will look for a configuration file in the directory it is executed from. This file must be called config.cnf and contain at least one valid section. Each section must be specified as follows;

    [Unique name]
    mongo_host: <hostname>
    mongo_port: <port>
    mongo_username: <username>
    mongo_password: <password>
    mongo_auth_db: <authentication database>
    active: True|False

    Example

    [Default]
    mongo_host: localhost
    mongo_port: 27017
    mongo_username: admin
    mongo_password: admin
    mongo_auth_db: admin
    active: True

    The connection details must refer to a mongos server. If a connection is not supplied via command-line parameters mm will use the section called "Default" in the configuration file. Further connections can be specified in the configuration file. They should be given a unique section name. Specific connections can be referred to on the command-line by using the connection name. for example;

        ./mm --connection UniqueConnectionName

    mm will ignore the connection if active is set to False.

OPTIONS

        -h, --help            show this help message and exit
          --summary             Show a summary of the MongoDB Cluster Topology
          --repl                Show a summary of the replicaset state
          --server_status {instance,asserts,flushing,journaling,extra_info,connections,global_lock,network,opcounters,opcounters_repl,security,storage_engine,memory,show_all}
                                Show a summary of the appropriate section from the
                                serverStatus document from all mongod processes.
          --host_info {system,os,extra,help}
                                Show a summary of the appropriate section from the
                                hostInfo document from all mongod processes.
          --db_hashes           Show the db hashes for each database on the cluster
                                and perform some verification.
          --databases           Show a summary fo the databases hosted by the MongoDB
                                cluster
          --inc_mongos          Optionally execute against the mongos servers. This
                                will fail if the command is not supported by mongos.
          --step_down STEP_DOWN
                                Step down the primary from this replicaset
          --step_down_nominate_host STEP_DOWN_NOMINATE_HOST
                                Used in combination with step_down_nominate_port to
                                select a PRIMARY
          --step_down_nominate_port STEP_DOWN_NOMINATE_PORT
                                Used in combination with step_down_nominate_host to
                                select a PRIMARY
          --replset_freeze REPLSET_FREEZE
                                Number of seconds to use with the replSetFreeze
                                command
          --profiling {-1,0,1,2}
                                Display or modify the profiling level of a MongoDB
                                Cluster
          --slowms SLOWMS       Optionally for use with --profiling switch. The
                                threshold in milliseconds at which the database
                                profiler considers a query slow.
          --sharding            List sharding details
          -H MONGO_HOSTNAME, --mongo_hostname MONGO_HOSTNAME
                                Hostname for the MongoDB mongos process to connect to
          -P MONGO_PORT, --mongo_port MONGO_PORT
                                Port for the MongoDB mongos process to connect to
          -u MONGO_USERNAME, --mongo_username MONGO_USERNAME
                                MongoDB username
          -p MONGO_PASSWORD, --mongo_password MONGO_PASSWORD
                                MongoDB password
          -D MONGO_AUTH_DB, --mongo_auth_db MONGO_AUTH_DB
                                MongoDB authentication database
          -e EXECUTION_DATABASE, --execution_database EXECUTION_DATABASE
                                Used by some command to specify the execution
                                database.
          -r REPEAT, --repeat REPEAT
                                Repeat the action N number of times
          -i INTERVAL, --interval INTERVAL
                                Number of seconds between each repeat
          -c CONNECTION, --connection CONNECTION
                                Name of MongoDB connection to use as set in config.cnf
          -d, --debug           Output debug information
          --validate_indexes VALIDATE_INDEXES
                                Collection to validate indexes across all shard
                                servers. This should be provided in the form
                                <database>.<collection>
          --collection_stats COLLECTION_STATS
                                Show a summary of the data from the
                                db.collection.stats() command. Must be supplied in the
                                format <database>.<collection>
          --database_stats DATABASE_STATS
                                Show a summary of the data from the db.stats()
                                command.
          --command COMMAND     Run a custom command against your MongoDB Cluster.
                                Should be provided in document format, i.e. '{
                                command: <value> }'
          --balancing {enable,disable}
                                Enable or disabled balancing. Must be supplied with
                                the --collection argument
          --collection COLLECTION
                                Collection to perform action on. Must be supplied in
                                the format <database>.<collection>
          --verbose_display     Used in various functions display data that is usually
                                supressed
          --stacktrace          By default we don't display the Python stacktace. Use
                                this flag to enable.

EXAMPLES

        Show a summary of the MongoDB topology.

            ./mm --summary

            MongoDB Config Servers
            rhysmacbook.local:27019      rhysmacbook.local:27020      rhysmacbook.local:27021
            MongoDB mongos servers
            rhysmacbook.local:27017      rhysmacbook.local:27018      rhysmacbook.local:27016
            MongoDB mongod shard servers
            rhysmacbook.local:30001      rhysmacbook.local:30002      rhysmacbook.local:30003
            rhysmacbook.local:30004      rhysmacbook.local:30005      rhysmacbook.local:30006
            rhysmacbook.local:30007      rhysmacbook.local:30008      rhysmacbook.local:30009
            MongoDB shards
            rs0   rs1   rs2

        Show a summary of the replication state

            ./mm --repl

            hostname                  replicaset state      configV    uptime     slaveDelay
            rhysmacbook.local:30001   rs0        PRIMARY    3          190        NA
            rhysmacbook.local:30002   rs0        SECONDARY  3          184        0.0
            rhysmacbook.local:30003   rs0        SECONDARY  3          184        0.0
            rhysmacbook.local:30004   rs1        SECONDARY  3          188        0.0
            rhysmacbook.local:30005   rs1        PRIMARY    3          189        NA
            rhysmacbook.local:30006   rs1        SECONDARY  3          183        0.0
            rhysmacbook.local:30007   rs2        PRIMARY    3          189        NA
            rhysmacbook.local:30008   rs2        SECONDARY  3          183        0.0
            rhysmacbook.local:30009   rs2        SECONDARY  3          183        0.0

        Instruct the primary of the given replicaset to step down

            ./mm --step_down rs0

            Output is the same as --repl flag with the addition of a line showing the PRIMARY transition.

        Instruct the primary of the given replicaset to step down and nominate a secondary to take over the role. Note this is not guaranteed but should work in most circumstances. If your cluster has significant replication lag then this request may not be honoured.

            ./mm --step_down rs0 --step_down_nominate_host rhysmacbook.local --step_down_nominate_port 30001

            hostname                  replicaset state      configV    uptime     slaveDelay
            rhysmacbook.local:30001   rs0        PRIMARY    3          433        NA
            rhysmacbook.local:30002   rs0        SECONDARY  3          427        0.0
            rhysmacbook.local:30003   rs0        SECONDARY  3          427        0.0
            rhysmacbook.local:30004   rs1        SECONDARY  3          431        0.0
            rhysmacbook.local:30005   rs1        PRIMARY    3          432        NA
            rhysmacbook.local:30006   rs1        SECONDARY  3          426        0.0
            rhysmacbook.local:30007   rs2        PRIMARY    3          432        NA
            rhysmacbook.local:30008   rs2        SECONDARY  3          426        0.0
            rhysmacbook.local:30009   rs2        SECONDARY  3          426        0.0
            PRIMARY changed from rhysmacbook.local:30003 to rhysmacbook.local:30001

         View system info from your cluster

            ./mm --host_info system

            hostname            shard      port       cpuAddrSize  memSizeMB  numCores   cpuArch  numaEnabled
            rhysmacbook.local   rs0        30001      64           16384      4          x86_64   0
            rhysmacbook.local   rs0        30002      64           16384      4          x86_64   0
            rhysmacbook.local   rs0        30003      64           16384      4          x86_64   0
            rhysmacbook.local   rs1        30004      64           16384      4          x86_64   0
            rhysmacbook.local   rs1        30005      64           16384      4          x86_64   0
            rhysmacbook.local   rs1        30006      64           16384      4          x86_64   0
            rhysmacbook.local   rs2        30007      64           16384      4          x86_64   0
            rhysmacbook.local   rs2        30008      64           16384      4          x86_64   0
            rhysmacbook.local   rs2        30009      64           16384      4          x86_64   0
            Time difference in milliseconds between the cluster nodes: 421.0 ms (not concurrently sampled)

        View os info from your cluster

            ./mm --host_info os

            hostname            shard      port       type       name       version
            rhysmacbook.local   rs0        30001      Darwin     Mac OS X   15.4.0
            rhysmacbook.local   rs0        30002      Darwin     Mac OS X   15.4.0
            rhysmacbook.local   rs0        30003      Darwin     Mac OS X   15.4.0
            rhysmacbook.local   rs1        30004      Darwin     Mac OS X   15.4.0
            rhysmacbook.local   rs1        30005      Darwin     Mac OS X   15.4.0
            rhysmacbook.local   rs1        30006      Darwin     Mac OS X   15.4.0
            rhysmacbook.local   rs2        30007      Darwin     Mac OS X   15.4.0
            rhysmacbook.local   rs2        30008      Darwin     Mac OS X   15.4.0
            rhysmacbook.local   rs2        30009      Darwin     Mac OS X   15.4.0

        Instruct a command to repeat 5 times 10 seconds apart

        ./mm --repl --repeat 5 --interval 10

        Show a summary of databases on the cluster.

        ./mm --databases

        rhysmacbook.local   30001
        name       size       empty
        admin      122880.0   0
        local      5308416.0  0
        test       4562944.0  0
        rhysmacbook.local   30002
        name       size       empty
        admin      176128.0   0
        local      5304320.0  0
        test       4521984.0  0

        Show statistics for a database

        ./mm --database_stats test

        Database stats summary of test
        objects   avgObjSize (b)  datasize (mb)   storageSize (mb)  extents   indexSize (mb)  fileSize  extents free
        25360     419.0           10.1381053925   3.97265625        0         0.38671875      0         0
        Database stats by shard
        0 collections on: rs2/rhysmacbook.local:30007,rhysmacbook.local:30008,rhysmacbook.local:30009
        0 collections on: rs1/rhysmacbook.local:30004,rhysmacbook.local:30005,rhysmacbook.local:30006
        rs0/rhysmacbook.local:30001,rhysmacbook.local:30002,rhysmacbook.local:30003
        collections  objects  avgObjSize (b)  dataSize (mb)   storageSize (mb)  numExtents  indexes  indexSize (mb)  fileSize
        3            25360    419.0           10.14           3.97              0           5        0.39            NA

        Show collections in a database

        ./mm --show_collections test

        rhys
        sample_messages
        restaurants

        Run a custom command

        ./mm --command '{ "listCollections": 1 }' --execution_database test

        Output for this is variable depending on the chosen command.

        Enable debug output and stacktrace output

        ./mm --repl --debug --stacktrace

        Show the db hashes for all collections on all shards in the cluster.

        ./mm --db_hashes

        hostname            shard      port       db         coll #     md5
        rhysmacbook.local   rs0        30001      test       3          5b151c215ef40b662fe79dcf44928e66
        rhysmacbook.local   rs0        30002      test       3          5b151c215ef40b662fe79dcf44928e66
        rhysmacbook.local   rs0        30003      test       3          5b151c215ef40b662fe79dcf44928e66

        By default the above command does not show details for databases where coll # is 0. This excludes the admin and config databases because the system collections are not counted in the collection count. Use this command to override that behaviour.

        ./mm --db_hashes --verbose_display

SEE ALSO

BUGS
