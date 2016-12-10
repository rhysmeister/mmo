
#!/usr/bin/env bash
################################################################
# Author: Rhys Campbell                                        #
# Created: 2016-02-21                                          #
# Description: Shell functions for creating, and tearing down  #
# a MongoDB sharded cluster for testing purposes. Note the     #
# mmo_teardown_cluster function will completely destroy        #
# the running mongo cluster incuding removing all data.        #
# Intended for unit testing MMO Python code.                   #
# Ensure the path to mongod, mongos etc is in your $PATH       #
# variable. Developed using mongodb-osx-x86_64-3.2.3, earlier  #
# version probably won't correctly. Should work unmodifed on   #
# GNU/Linux as well. Let me know if not.                       #
# Usage:                                                       #
#			#1 - source file to make mmo functions available   #
#			linux> . mmo_mongodb_cluster.sh                    #
#           #2 - Setup the cluster                             #
#           linux> mmo_setup_cluster                           #
#           #3 - Destory the cluster (gets rid of ALL data)    #
#           linux> mmo_teardown_cluster                        #
#           #4 - Launch cluster processes (skips data & config)#
#           linux> mmo_start_with_existing_data                #
#                                                              #
# Cluster Info:	3 x config servers 27019, 27020, & 27021       #
#               3 x mongos servers 27016, 27017 & 27018        #
#               9 x mongod servers. Split into 3 replicasets.  #
#               rs0 30001, 30002 & 30003                       #
#               rs1 30004, 30005 & 30006                       #
#				rs2 30007, 30008 & 30009 (Can be turned off).  #
#               WiredTiger Storage Engine 200MB Cache.         #
# Users details: u: admin pw: admin                            #
#                u: pytest pw: secret                          # 
################################################################  

#set -e;
set -u;
#set -x;

MMO_SHARDED_CLUSTER_TEST_TEMP="mmo_sharded_cluster_test_temp"; # MongoDB datadir where all cluster data will be placed
THIRD_SHARD=1;	# 0 = off, 1 = on
RS_CONFIG=1; # 0 = off, 1 = on Use replicaset config servers

function mmo_murder_cluster()
{
	killall mongos && echo "mongos processes have been murdered." && killall mongod && echo "mongod processes have been murdered.";
}

function mmo_teardown_cluster()
{
	mmo_murder_cluster;
	cd ~;
	sleep 5 && echo "Waiting for all processes to die...";
	rm -Rf ${MMO_SHARDED_CLUSTER_TEST_TEMP} && echo "Directory ${MMO_SHARDED_CLUSTER_TEST_TEMP} removed.";
	rm -f /tmp/mongodb*.sock && echo "Removed socket files.";
}

function mmo_change_to_datadir()
{
	cd ~;
	cd ${MMO_SHARDED_CLUSTER_TEST_TEMP};
}

function mmo_create_directories()
{
	cd ~;
	mkdir -p ${MMO_SHARDED_CLUSTER_TEST_TEMP};
	cd ${MMO_SHARDED_CLUSTER_TEST_TEMP};
	mkdir config1 config2 config3 mongos1 mongos2 mongos3 shard0_30001 shard0_30002 shard0_30003 shard1_30004 shard1_30005 shard1_30006;
	if [ ${THIRD_SHARD} -eq 1 ]; then
		mkdir shard2_30007 shard2_30008 shard2_30009 
	fi;
}

function mmo_create_config_servers()
{
	ADDITIONAL_OPTIONS="$1";
	mmo_change_to_datadir
	if [ ${RS_CONFIG} -eq 1 ]; then
		mongod --configsvr --port 27019 --dbpath ./config1 --logpath config1.log --smallfiles ${ADDITIONAL_OPTIONS} --replSet "csReplSet";
		mongod --configsvr --port 27020 --dbpath ./config2 --logpath config2.log --smallfiles ${ADDITIONAL_OPTIONS} --replSet "csReplSet";
		mongod --configsvr --port 27021 --dbpath ./config3 --logpath config3.log --smallfiles ${ADDITIONAL_OPTIONS} --replSet "csReplSet";
	else
		mongod --configsvr --port 27019 --dbpath ./config1 --logpath config1.log --smallfiles ${ADDITIONAL_OPTIONS};
		mongod --configsvr --port 27020 --dbpath ./config2 --logpath config2.log --smallfiles ${ADDITIONAL_OPTIONS};
		mongod --configsvr --port 27021 --dbpath ./config3 --logpath config3.log --smallfiles ${ADDITIONAL_OPTIONS};	
	fi;
}

function mmo_create_mongos_servers()
{
		ADDITIONAL_OPTIONS="$1";
		mmo_change_to_datadir
		mongos --configdb "$(hostname):27019,$(hostname):27020,$(hostname):27021" --logpath mongos1.log --port 27017 ${ADDITIONAL_OPTIONS};
		mongos --configdb "$(hostname):27019,$(hostname):27020,$(hostname):27021" --logpath mongos2.log --port 27018 ${ADDITIONAL_OPTIONS};
		mongos --configdb "$(hostname):27019,$(hostname):27020,$(hostname):27021" --logpath mongos3.log --port 27016 ${ADDITIONAL_OPTIONS};
}

function mmo_create_mongod_shard_servers()
{
	ADDITIONAL_OPTIONS="$1";
	mmo_change_to_datadir
	# shard0 mongod instances
	mongod --smallfiles --nojournal --storageEngine wiredTiger --wiredTigerEngineConfigString="cache_size=200M" --dbpath ./shard0_30001  --port 30001 --replSet "rs0" --logpath shard0_30001.log ${ADDITIONAL_OPTIONS}; 
	mongod --smallfiles --nojournal --storageEngine wiredTiger --wiredTigerEngineConfigString="cache_size=200M" --dbpath ./shard0_30002  --port 30002 --replSet "rs0" --logpath shard0_30002.log ${ADDITIONAL_OPTIONS};
	mongod --smallfiles --nojournal --storageEngine wiredTiger --wiredTigerEngineConfigString="cache_size=200M" --dbpath ./shard0_30003  --port 30003 --replSet "rs0" --logpath shard0_30003.log ${ADDITIONAL_OPTIONS};
	# shard1 mongod instances
	mongod --smallfiles --nojournal --storageEngine wiredTiger --wiredTigerEngineConfigString="cache_size=200M" --dbpath ./shard1_30004  --port 30004 --replSet "rs1" --logpath shard1_30004.log ${ADDITIONAL_OPTIONS};
	mongod --smallfiles --nojournal --storageEngine wiredTiger --wiredTigerEngineConfigString="cache_size=200M" --dbpath ./shard1_30005  --port 30005 --replSet "rs1" --logpath shard1_30005.log ${ADDITIONAL_OPTIONS};
	mongod --smallfiles --nojournal --storageEngine wiredTiger --wiredTigerEngineConfigString="cache_size=200M" --dbpath ./shard1_30006  --port 30006 --replSet "rs1" --logpath shard1_30006.log ${ADDITIONAL_OPTIONS};
	if [ ${THIRD_SHARD} -eq 1 ]; then
		mongod --smallfiles --nojournal --storageEngine wiredTiger --wiredTigerEngineConfigString="cache_size=200M" --dbpath ./shard2_30007  --port 30007 --replSet "rs2" --logpath shard2_30007.log ${ADDITIONAL_OPTIONS};
		mongod --smallfiles --nojournal --storageEngine wiredTiger --wiredTigerEngineConfigString="cache_size=200M" --dbpath ./shard2_30008  --port 30008 --replSet "rs2" --logpath shard2_30008.log ${ADDITIONAL_OPTIONS};
		mongod --smallfiles --nojournal --storageEngine wiredTiger --wiredTigerEngineConfigString="cache_size=200M" --dbpath ./shard2_30009  --port 30009 --replSet "rs2" --logpath shard2_30009.log ${ADDITIONAL_OPTIONS};
	fi;
}

function mmo_configure_replicaset_rs0()
{
	mongo --port 30001 <<EOF
	rs.initiate();
	while(rs.status()['myState'] != 1) {
		print("State is not yet PRIMARY. Waiting...");
	}	
	rs.add("$(hostname):30002");
	rs.add("$(hostname):30003");
EOF
	STATUS=$?;
	return $STATUS;
}

function mmo_configure_replicaset_rs1()
{
	mongo --port 30004 <<EOF
	rs.initiate();
	while(rs.status()['myState'] != 1) {
		print("State is not yet PRIMARY. Waiting...");
	}	
	rs.add("$(hostname):30005");
	rs.add("$(hostname):30006");
EOF
}

function mmo_configure_replicaset_rs2()
{
	mongo --port 30007 <<EOF
	rs.initiate();
	while(rs.status()['myState'] != 1) {
		print("State is not yet PRIMARY. Waiting...");
	}	
	rs.add("$(hostname):30008");
	rs.add("$(hostname):30009");
EOF
}

function mmo_configure_replicaset_cfgsrv()
{
	mongo --port 27019 <<EOF
	rs.initiate({
					_id: "csReplSet",
					configsvr: true,
					version: 1,
					members: [ 
								{ _id: 0, host: "$(hostname):27019" },
								{ _id: 1, host: "$(hostname):27020" },
								{ _id: 2, host: "$(hostname):27021" }   
							]
				});
EOF
}

function mmo_configure_sharding()
{
	mongo <<EOF 
	sh.addShard( "rs0/$(hostname):30001" );
	sh.addShard( "rs1/$(hostname):30004" );
	sh.enableSharding("test");
	sh.shardCollection("test.sample_messages", { "t_u": 1 } );
EOF
	if [ ${THIRD_SHARD} -eq 1 ]; then
		mongo <<EOF
		sh.addShard( "rs2/$(hostname):30007" );
EOF
	fi;
}

function mmo_create_admin_user()
{
	PORT=$1;
	mongo --port ${PORT} admin<<EOF
	db.createUser(
	{
		user: "admin",
		pwd: "admin",
		roles: [ { role: "root", db: "admin" } ]
	}
	);
EOF
}

function mmo_wait_for_slaves()
{
		PORT=$1;
		while [ "$(echo "db.printSlaveReplicationInfo()" | mongo --port ${PORT} admin | grep "behind the primary" | uniq | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//' | sort -r)" != "0 secs (0 hrs) behind the primary" ];
		do
			echo "Slaves have not yet caught up....";
			echo "db.printSlaveReplicationInfo()" | mongo --port ${PORT} admin;
			sleep 10;
		done;
	
}

function mmo_create_pytest_user()
{
	PORT=$1;
	mongo --port ${PORT} admin<<EOF
	db.createUser( 
	{ 
			"user": "pytest", 
			"pwd": "secret",
			"customData": { comment: "User for MMO python unit tests." },
			roles: [ { role: "root", db: "admin" } ]
	} 
	);
EOF

}

function mmo_check_processes()
{
	NUM_MONGOD=$(pgrep -x mongod | wc -l);
	NUM_MONGOS=$(pgrep -x mongos | wc -l);
	if [ ${THIRD_SHARD} -eq 1 ]; then
		if [ "$NUM_MONGOD" -ne 12 ]; then echo "WARNING: Not all mongod processes are running. Expected 12 but $NUM_MONGOD running."; else echo "All expected mongod processes are running."; fi;
		if [ "$NUM_MONGOS" -ne 3 ]; then echo "WARNING: Not all mongos processes are running. Expected 3 but $NUM_MONGOS running."; else echo "All expected mongos processes are running."; fi;
	else
		if [ "$NUM_MONGOD" -ne 9 ]; then echo "WARNING: Not all mongod processes are running. Expected 9 but $NUM_MONGOD running."; else echo "All expected mongod processes are running."; fi;
		if [ "$NUM_MONGOS" -ne 3 ]; then echo "WARNING: Not all mongos processes are running. Expected 3 but $NUM_MONGOS running."; else echo "All expected mongos processes are running."; fi;
	fi;
}

function mmo_generate_key_file()
{
	cd ~;
	cd ${MMO_SHARDED_CLUSTER_TEST_TEMP};
	openssl rand -base64 741 > keyfile.txt;
	chmod 600 keyfile.txt;
}

# This function assumes there is already data in the cluster and we just want ot fire
# up the cluster after a VM reboot
function mmo_start_with_existing_data()
{
	mmo_create_config_servers "$(echo '--auth --fork --keyFile keyfile.txt')" && echo "OK restarted config servers with auth enabled.";
    mmo_create_mongos_servers "$(echo '--fork --keyFile keyfile.txt')" && echo "OK restarted mongos servers with auth enabled.";
    mmo_create_mongod_shard_servers "$(echo '--auth --fork --keyFile keyfile.txt')" && echo "OK restarted mongod servers with auth enabled.";
	mmo_check_processes;
}

# safely shutdown a mongod or mongos process
function mmo_shutdown_server()
{
	PORT=$1;
	mongo --username "admin" --password "admin" --port ${PORT} admin<<EOF
	db.shutdownServer({force: true});
EOF
}

# Shutdown config servers identified by port convention
function mmo_shutdown_config_servers()
{
	mmo_shutdown_server 27019;
	mmo_shutdown_server 27020;
	mmo_shutdown_server 27021;
}

# Shutdown mongos servers identified by port convention
function mmo_shutdown_mongos_servers()
{
	mmo_shutdown_server 27017;
	mmo_shutdown_server 27018;
	mmo_shutdown_server 27016;
}

# Shutdown mongod servers identified by port convention
function mmo_shutdown_mongod_servers()
{
	mmo_shutdown_server 30001;
	mmo_shutdown_server 30002;
	mmo_shutdown_server 30003;
	mmo_shutdown_server 30004;
	mmo_shutdown_server 30005;
	mmo_shutdown_server 30006;
	if [ ${THIRD_SHARD} -eq 1 ]; then
		mmo_shutdown_server 30007;
		mmo_shutdown_server 30008;
		mmo_shutdown_server 30009;
	fi;
}

# Shutdown the entire cluster; mongos, config server and shard servers
function mmo_shutdown_cluster()
{
	mmo_shutdown_config_servers && echo "Shutdown all config servers.";
	mmo_shutdown_mongod_servers && echo "Shutdown all mongod servers.";
	mmo_shutdown_mongos_servers && echo "Shutdown all mongos servers.";
}

function mmo_load_sample_dataset()
{
	DELETE_FILE_AFTER_USE=$1;
	DATA_URL=https://raw.githubusercontent.com/mongodb/docs-assets/primer-dataset/primer-dataset.json;
	if [ ! -e /tmp/primer-dataset.json ]; then
		wget ${DATA_URL} --directory-prefix=/tmp;
	fi;
	mongoimport --authenticationDatabase admin --username admin --password admin --db test --collection restaurants --drop --file /tmp/primer-dataset.json;
	if [ ${DELETE_FILE_AFTER_USE} -eq "1" ]; then
		rm /tmp/primer-dataset.json;
	fi;
}

function mmo_kill_replset()
{
		rs="$1";
		if [ "$rs" == "rs0" ]; then
			mmo_shutdown_server 30001;
			mmo_shutdown_server 30002;
			mmo_shutdown_server 30003;		
		elif [ "$rs" == "rs1" ]; then
			mmo_shutdown_server 30004;
			mmo_shutdown_server 30005;
			mmo_shutdown_server 30006;		
		elif [ "$rs" == "rs2" ]; then
			mmo_shutdown_server 30007;
			mmo_shutdown_server 30008;
			mmo_shutdown_server 30009;		
		else
			echo "Invalid replset name";
			return 1;
		fi;
}

function mmo_setup_cluster()
{
	mmo_create_directories && echo "OK created directories";
	mmo_create_config_servers "$(echo '--fork --logRotate reopen --logappend')" && echo "OK started configuration servers. Sleeping for 30 seconds." && sleep 30;
	C_PORT=27017;
	if [ "$RS_CONFIG" -eq 1 ]; then
		mmo_configure_replicaset_cfgsrv && echo "OK configured cfgsrv replica set";
		C_PORT=27019;
	fi;
	mmo_create_mongos_servers "$(echo '--fork --logRotate reopen --logappend')" && echo "OK started mongos servers." && sleep 5;
	mmo_create_mongod_shard_servers "$(echo '--fork --logRotate reopen --logappend')" && echo "OK started mongod shard servers";
	echo "Sleeping for sixty seconds before attempting replicaset & shard configuration." && sleep 60;
	mmo_configure_replicaset_rs0 && echo "OK configured replicaset rs0." && sleep 5;
	mmo_configure_replicaset_rs1 && echo "OK configured replicaset rs1." && sleep 5;
	mmo_configure_replicaset_rs2 && echo "OK configured replicaset rs2." && sleep 5;
	mmo_configure_sharding && echo "OK configured Sharding and sharded test.sample_messages by t_u.";
	mmo_create_admin_user "$C_PORT" && echo "OK created cluster admin user (but auth is not enabled yet).";
	mmo_create_admin_user 30001 && echo "OK created admin user on rs0 (but auth is not enabled yet).";
	mmo_create_admin_user 30004 && echo "OK created admin user on rs1 (but auth is not enabled yet).";
	mmo_create_pytest_user "$C_PORT" && echo "OK created cluster pytest user (but auth is not enabled yet).";
	mmo_create_pytest_user 30001 && echo "OK created pytest user on rs0 (but auth is not enabled yet).";
	mmo_create_pytest_user 30004 && echo "OK created pytest user on rs1 (but auth is not enabled yet).";
	if [ ${THIRD_SHARD} -eq 1 ]; then
		mmo_create_admin_user 30007 && echo "OK created admin user on rs2 (but auth is not enabled yet).";
		mmo_create_pytest_user 30007 && echo "OK created pytest user on rs2 (but auth is not enabled yet).";
	fi
	# should call function here to put test data in the cluster
	mmo_wait_for_slaves 30001; # Wait for slaves to catch up
	mmo_wait_for_slaves 30004; # Also other repl set
	if [ ${THIRD_SHARD} -eq 1 ]; then
		mmo_wait_for_slaves 30007;	
	fi
	echo "Have a little sleep..." && sleep 10;
	mmo_shutdown_cluster && echo "Shutdown entire MongoDB Cluster";
	mmo_murder_cluster
	echo "Preparing to restart MongoDB processes with auth enabled.";
	mmo_generate_key_file && echo "OK created MongoDB keyfile.";
	mmo_create_config_servers "$(echo '--auth --fork --keyFile keyfile.txt --logRotate reopen --logappend')" && echo "OK restarted config servers with auth enabled.";
	mmo_create_mongos_servers "$(echo '--fork --keyFile keyfile.txt --logRotate reopen --logappend')" && echo "OK restarted mongos servers with auth enabled.";
	mmo_create_mongod_shard_servers "$(echo '--auth --fork --keyFile keyfile.txt --logRotate reopen --logappend')" && echo "OK restarted mongod servers with auth enabled.";
	mmo_load_sample_dataset 0 && echo "Loaded collection into test.sample_restaurants";
	mmo_check_processes;
	set +u;
}
