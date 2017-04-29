import unittest
import os
import inspect
import socket

import time

execfile(os.path.dirname(os.path.abspath(inspect.stack()[0][1]))  + "/../pymmo/pymmo.py")

class TestPyMmoMethods(unittest.TestCase):

    hostname = socket.gethostname()

    def test_mmo_connect(self):
        m = MmoMongoCluster("localhost", 27017, "admin", "admin", "admin")
        c = m.mmo_connect()
        self.assertTrue("MongoClient(host=['localhost:27017']" in str(c))

    def test_mmo_mongos_servers(self):
        m = MmoMongoCluster("localhost", 27017, "admin", "admin", "admin")
        c = m.mmo_connect()
        mongos_servers = m.mmo_mongos_servers(c)
        self.assertEqual(mongos_servers[0], { "hostname": self.hostname, "port": 27017})
        self.assertEqual(mongos_servers[1], { "hostname": self.hostname, "port": 27018})
        self.assertEqual(mongos_servers[2], { "hostname": self.hostname, "port": 27016})

    def test_mmo_config_servers(self):
        m = MmoMongoCluster("localhost", 27017, "admin", "admin", "admin")
        c = m.mmo_connect()
        mongos_servers = m.mmo_config_servers(c)
        self.assertEqual(mongos_servers[0], { "hostname": self.hostname, "port": 27019})
        self.assertEqual(mongos_servers[1], { "hostname": self.hostname, "port": 27020})
        self.assertEqual(mongos_servers[2], { "hostname": self.hostname, "port": 27021})

    def test_mmo_shard_servers(self):
        m = MmoMongoCluster("localhost", 27017, "admin", "admin", "admin")
        c = m.mmo_connect()
        mongos_servers = m.mmo_shard_servers(c)
        self.assertEqual(mongos_servers[0], { "shard": "rs0", "hostname": self.hostname, "port": 30001})
        self.assertEqual(mongos_servers[1], { "shard": "rs0", "hostname": self.hostname, "port": 30002})
        self.assertEqual(mongos_servers[2], { "shard": "rs0", "hostname": self.hostname, "port": 30003})
        self.assertEqual(mongos_servers[3], { "shard": "rs1", "hostname": self.hostname, "port": 30004})
        self.assertEqual(mongos_servers[4], { "shard": "rs1", "hostname": self.hostname, "port": 30005})
        self.assertEqual(mongos_servers[5], { "shard": "rs1", "hostname": self.hostname, "port": 30006})
        self.assertEqual(mongos_servers[6], {"shard": "rs2", "hostname": self.hostname, "port": 30007})
        self.assertEqual(mongos_servers[7], {"shard": "rs2", "hostname": self.hostname, "port": 30008})
        self.assertEqual(mongos_servers[8], {"shard": "rs2", "hostname": self.hostname, "port": 30009})

    def test_mmo_what_process_am_i(self):
        m = MmoMongoCluster("localhost", 27017, "admin", "admin", "admin")
        c = m.mmo_connect()
        i_should_be_a_mongos = m.mmo_what_process_am_i(c)
        self.assertEqual(i_should_be_a_mongos, "mongos")

    def test_mmo_is_mongos(self):
        m = MmoMongoCluster("localhost", 27017, "admin", "admin", "admin")
        c = m.mmo_connect()
        self.assertTrue(m.mmo_is_mongos(c))
        c = m.mmo_connect_mongod(port=30001)
        self.assertFalse(m.mmo_is_mongos(c))

    def test_mmo_is_mongod(self):
        m = MmoMongoCluster("localhost", 27017, "admin", "admin", "admin")
        c = m.mmo_connect_mongod(port=30001)
        self.assertTrue(m.mmo_is_mongod(c))

    def test_mmo_is_configsrv(self):
        m = MmoMongoCluster("localhost", 27017, "admin", "admin", "admin")
        c = m.mmo_connect_mongod(port=27019)
        self.assertTrue(m.mmo_is_configsrv(c))
        c = m.mmo_connect_mongod(port=30001)
        self.assertFalse(m.mmo_is_configsrv(c))

    def test_mmo_is_cfg_rs(self):
        m = MmoMongoCluster("localhost", 27017, "admin", "admin", "admin")
        c = m.mmo_connect_mongod(port=27020)
        self.assertTrue(m.mmo_is_cfg_rs(c))

    def test_mmo_mongo_version(self):
        m = MmoMongoCluster("localhost", 27017, "admin", "admin", "admin")
        c = m.mmo_connect()
        self.assertEquals("3.4.3", m.mmo_mongo_version(c))

    def test_mmo_execute_on_cluster(self):
        m = MmoMongoCluster("localhost", 27017, "admin", "admin", "admin")
        c = m.mmo_connect()
        o = m.mmo_execute_on_cluster(c, "buildinfo")
        self.assertEquals(9, len(o))
        self.assertTrue("openssl" in str(o))

    def test_mmo_replica_state(self):
        """
        Need to change this test or at least prepare the cluster into the expected state
        :return:
        """
        m = MmoMongoCluster("localhost", 27017, "admin", "admin", "admin")
        c = m.mmo_connect_mongod("localhost", 30001, "admin", "admin", "admin")
        o = m.mmo_replica_state(c)
        self.assertEquals(1, o["id"])
        self.assertEquals("PRIMARY", o["name"])
        c = m.mmo_connect_mongod("localhost", 30002, "admin", "admin", "admin")
        o = m.mmo_replica_state(c)
        self.assertEquals(2, o["id"])
        self.assertEquals("SECONDARY", o["name"])
        c = m.mmo_connect_mongod("localhost", 30003, "admin", "admin", "admin")
        o = m.mmo_replica_state(c)
        self.assertEquals(2, o["id"])
        self.assertEquals("SECONDARY", o["name"])
        c = m.mmo_connect_mongod("localhost", 30004, "admin", "admin", "admin")
        o = m.mmo_replica_state(c)
        self.assertEquals(1, o["id"])
        self.assertEquals("PRIMARY", o["name"])
        c = m.mmo_connect_mongod("localhost", 30005, "admin", "admin", "admin")
        o = m.mmo_replica_state(c)
        self.assertEquals(2, o["id"])
        self.assertEquals("SECONDARY", o["name"])
        c = m.mmo_connect_mongod("localhost", 30006, "admin", "admin", "admin")
        o = m.mmo_replica_state(c)
        self.assertEquals(2, o["id"])
        self.assertEquals("SECONDARY", o["name"])
        c = m.mmo_connect_mongod("localhost", 30007, "admin", "admin", "admin")
        o = m.mmo_replica_state(c)
        self.assertEquals(1, o["id"])
        self.assertEquals("PRIMARY", o["name"])
        c = m.mmo_connect_mongod("localhost", 30008, "admin", "admin", "admin")
        o = m.mmo_replica_state(c)
        self.assertEquals(2, o["id"])
        self.assertEquals("SECONDARY", o["name"])
        c = m.mmo_connect_mongod("localhost", 30009, "admin", "admin", "admin")
        o = m.mmo_replica_state(c)
        self.assertEquals(2, o["id"])
        self.assertEquals("SECONDARY", o["name"])

    def test_mmo_execute_on_primaries(self):
        m = MmoMongoCluster("localhost", 27017, "admin", "admin", "admin")
        c = m.mmo_connect()
        o = m.mmo_execute_on_primaries(c, "buildinfo")
        self.assertEquals(3, len(o))
        self.assertTrue("openssl" in str(o))

    def test_mmo_execute_on_secondaries(self):
        m = MmoMongoCluster("localhost", 27017, "admin", "admin", "admin")
        c = m.mmo_connect()
        o = m.mmo_execute_on_secondaries(c, "buildinfo")
        self.assertEquals(6, len(o))
        self.assertTrue("openssl" in str(o))

    def test_mmo_execute_on_secondary_or_primary(self):
        m = MmoMongoCluster("localhost", 27017, "admin", "admin", "admin")
        c = m.mmo_connect()
        o = m.mmo_execute_on_secondary_or_primary(c, "buildinfo")
        self.assertEquals(6, len(o))
        self.assertTrue("openssl" in str(o))

    def test_mmo_shards(self):
        m = MmoMongoCluster("localhost", 27017, "admin", "admin", "admin")
        c = m.mmo_connect()
        shards = m.mmo_shards()
        self.assertEquals([ "rs0", "rs1", "rs2"], shards)

    def test_mmo_replication_status(self):
        m = MmoMongoCluster("localhost", 27017, "admin", "admin", "admin")
        c = m.mmo_connect()
        o = m.mmo_replication_status(c)
        self.assertEquals(3, len(o))
        self.assertTrue("lastHeartbeatRecv" in str(o))

    def test_mmo_replication_status_summary(self):
        m = MmoMongoCluster("localhost", 27017, "admin", "admin", "admin")
        c = m.mmo_connect()
        o = m.mmo_replication_status_summary(c)
        self.assertEquals(12, len(o))
        self.assertTrue("lag" in str(o))

    def test_mmo_cluster_serverStatus(self):
        m = MmoMongoCluster("localhost", 27017, "admin", "admin", "admin")
        c = m.mmo_connect()
        o = m.mmo_cluster_serverStatus(c, False)
        self.assertEquals(9, len(o))
        self.assertTrue("metrics" in str(o))

    def test_mmo_cluster_hostInfo(self):
        m = MmoMongoCluster("localhost", 27017, "admin", "admin", "admin")
        c = m.mmo_connect()
        o = m.mmo_cluster_hostInfo(c, False)
        self.assertEquals(9, len(o))
        self.assertTrue("memSizeMB" in str(o))

    def test_mmo_list_databases_on_cluster(self):
        m = MmoMongoCluster("localhost", 27017, "admin", "admin", "admin")
        c = m.mmo_connect()
        o = m.mmo_list_databases_on_cluster(c, False)
        self.assertEquals(9, len(o))
        self.assertTrue("sizeOnDisk" in str(o))

    def test_mmo_list_collections_on_cluster(self):
        m = MmoMongoCluster("localhost", 27017, "admin", "admin", "admin")
        c = m.mmo_connect()
        o = m.mmo_list_collections_on_cluster(c, False, "test")
        self.assertEquals(9, len(o))
        self.assertTrue("restaurants" in str(o))
        self.assertTrue("sample_messages" in str(o))

    def test_mmo_list_dbhash_on_cluster(self):
        m = MmoMongoCluster("localhost", 27017, "admin", "admin", "admin")
        c = m.mmo_connect()
        o = m.mmo_list_dbhash_on_cluster(c)
        self.assertEquals(3, len(o))
        self.assertTrue("restaurants" in str(o))
        self.assertTrue("sample_messages" in str(o))

    def test_mmo_execute_on_cluster_on_each_db(self):
        m = MmoMongoCluster("localhost", 27017, "admin", "admin", "admin")
        c = m.mmo_connect()
        o = m.mmo_execute_on_cluster_on_each_db(c, "dbHash", False, False)
        self.assertEquals(3, len(o))
        self.assertTrue("collections" in str(o))
        self.assertTrue("md5" in str(o))

    def test_mmo_step_down(self):
        """
        This test is a little complicated. Logic is duplicated from mm.py.
        We test for a change in the PRIMARY of the rs0 replicaset.
        :return:
        """
        m = MmoMongoCluster("localhost", 27017, "admin", "admin", "admin")
        c = m.mmo_connect()
        replicaset = "rs0"
        old_primary, new_primary = None, None
        try:
            rs = m.mmo_replication_status_summary(c)
            shard_server_count=len(rs)
            for doc in rs:
                if doc['replicaset'] == replicaset and doc['state'] == 'PRIMARY':
                    old_primary = doc
            m.mmo_step_down(c, replicaset)
        except Exception as exception:
            timeout=60
            sleep_time=0
            while len(m.mmo_replication_status_summary(c)) < shard_server_count and sleep_time < timeout:
                time.sleep(10) # Wait to allow the election to happen
            else:
                if len(m.mmo_replication_status_summary(c)) == shard_server_count:
                    # Election has happened and all shard servers are back
                    rs = m.mmo_replication_status_summary(c)
                    for doc in rs:
                        if doc['replicaset'] == replicaset and doc['state'] == 'PRIMARY':
                            new_primary = doc
                else:
                    # Timeout has happened or something is wrong
                    raise exception
        # Has the election completed successfully?
        self.assertTrue(old_primary != new_primary)

    def test_mmo_change_profiling_level(self):
        m = MmoMongoCluster("localhost", 27017, "admin", "admin", "admin")
        c = m.mmo_connect()
        o = m.mmo_change_profiling_level(c, -1, None, "admin")
        self.assertEquals(0, o[0]["command_output"]["was"])
        o = m.mmo_change_profiling_level(c, 1, None, "admin")
        o = m.mmo_change_profiling_level(c, -1, None, "admin") # We must request again to get the current state
        self.assertEquals(1, o[0]["command_output"]["was"])
        o = m.mmo_change_profiling_level(c, 2, None, "admin")
        o = m.mmo_change_profiling_level(c, -1, None, "admin")
        self.assertEquals(2, o[0]["command_output"]["was"])
        o = m.mmo_change_profiling_level(c, 0, None, "admin")
        o = m.mmo_change_profiling_level(c, -1, None, "admin")
        self.assertEquals(0, o[0]["command_output"]["was"])

    def test_mmo_sharding_status(self):
        m = MmoMongoCluster("localhost", 27017, "admin", "admin", "admin")
        c = m.mmo_connect()
        o = m.mmo_sharding_status(c)
        self.assertTrue("rs0" in str(o))
        self.assertTrue("rs1" in str(o))
        self.assertTrue("rs2" in str(o))
        self.assertEquals(1.0, o["ok"])
        self.assertEquals(3, len(o["shards"]))
        self.assertEquals("rs0", o["shards"][0]["_id"])
        self.assertEquals("rs1", o["shards"][1]["_id"])
        self.assertEquals("rs2", o["shards"][2]["_id"])

    def test_mmo_repl_set_freeze(self):
        m = MmoMongoCluster("localhost", 27017, "admin", "admin", "admin")
        c = m.mmo_connect()
        o = m.mmo_repl_set_freeze(c, "rhysmacbook.local", 30005, 10)
        self.assertTrue(1.0, o["command_output"]["ok"])

    def test_mmo_repl_set_freeze_nominate_host(self):
        """
        This will fail if the shard server is the current PRIMARY.
        We could make this better by picking a secondary during the test
        :return:
        """
        m = MmoMongoCluster("localhost", 27017, "admin", "admin", "admin")
        c = m.mmo_connect()
        o = m.mmo_repl_set_freeze_nominate_host(c, "rhysmacbook.local", 30006, "rs1", 10)
        self.assertTrue(2, len(o))
        self.assertTrue(1.0, o[0]["command_output"]["ok"])
        self.assertTrue("election_Id", str(o))

    def test_mmo_collection_stats(self):
        m = MmoMongoCluster("localhost", 27017, "admin", "admin", "admin")
        c = m.mmo_connect()
        o = m.mmo_collection_stats(c, "test", "restaurants")
        self.assertEquals(1, o["ok"])
        self.assertEquals("test.restaurants", o["ns"])

    def test_mmo_database_stats(self):
        m = MmoMongoCluster("localhost", 27017, "admin", "admin", "admin")
        c = m.mmo_connect()
        o = m.mmo_database_stats(c, "test")
        self.assertEquals(1, o["ok"])
        self.assertTrue("test" in str(o))

    def test_mmo_replicaset_conf(self):
        m = MmoMongoCluster("localhost", 27017, "admin", "admin", "admin")
        c = m.mmo_connect()
        o = m.mmo_replicaset_conf(c)
        self.assertTrue("members" in str(o))

    def test_mmo_plan_cache(self):
        m = MmoMongoCluster("localhost", 27017, "admin", "admin", "admin")
        c = m.mmo_connect()
        o = m.mmo_plan_cache(c, "test", "restuarants")
        self.assertTrue(type(o) == list)

    def test_mmo_plan_cache_query(self):
        m = MmoMongoCluster("localhost", 27017, "admin", "admin", "admin")
        c = m.mmo_connect()
        o = m.mmo_plan_cache_query(c, "test", "restuarants", {}, {}, {})
        self.assertTrue(type(o) == list)

    def test_mmo_plan_cache_clear(self):
        m = MmoMongoCluster("localhost", 27017, "admin", "admin", "admin")
        c = m.mmo_connect()
        o = m.mmo_plan_cache_clear(c, "test", "restuarants", {}, {}, {})
        self.assertTrue(type(o) == list)

    def test_mmo_chunks(self):
        m = MmoMongoCluster("localhost", 27017, "admin", "admin", "admin")
        c = m.mmo_connect()
        o = m.mmo_chunks(c)
        self.assertTrue(len(o) > 0)
        self.assertTrue(type(o[0]) == dict)
        self.assertTrue("shard" in str(o))
        self.assertTrue("count" in str(o))

    def test_mmo_replset_has_primary(self):
        m = MmoMongoCluster("localhost", 27017, "admin", "admin", "admin")
        c = m.mmo_connect()
        self.assertTrue(m.mmo_replset_has_primary(c, "rs0"))
        self.assertTrue(m.mmo_replset_has_primary(c, "rs1"))
        self.assertTrue(m.mmo_replset_has_primary(c, "rs2"))

def _set_MongoDB_Cluster_Up():
    """
    Run stuff we need to setup the MongoDB Cluster correctly so tests pass. We want a consistent state of the cluster here.
    FOr example the PRIMARY servers should all be the lowerest port number in the replicaset
    :return:
    """
    start_time = time.time()
    hostname = socket.gethostname()
    m = MmoMongoCluster("localhost", 27017, "admin", "admin", "admin")
    c = m.mmo_connect()

    if False: # Should write soemthing to tets the setup first. Perhaps mmo_is_primary(host, port)

        m.mmo_repl_set_freeze_nominate_host(c, hostname, 30001, "rs0", 0)
        try:
            m.mmo_step_down(c, "rs0")
        except Exception as exception:
            if str(exception) == "connection closed":  # This is the expect behaviour
                pass
            else:
                raise exception
        m.mmo_repl_set_freeze_nominate_host(c, hostname, 30004, "rs1", 0)
        try:
            m.mmo_step_down(c, "rs1")
        except Exception as exception:
            if str(exception) == "connection closed":  # This is the expect behaviour
                pass
            else:
                raise exception
        m.mmo_repl_set_freeze_nominate_host(c, hostname, 30007, "rs2", 0)
        try:
            m.mmo_step_down(c, "rs2")
        except Exception as exception:
            if str(exception) == "connection closed":  # This is the expect behaviour
                pass
            else:
                raise exception
        time.sleep(60) # Sleep for a bit to allow elections to complete
        s = round(time.time() - start_time, 2)
        print("Executed setup in %s seconds" % s)

_set_MongoDB_Cluster_Up()

if __name__ == '__main__':
    unittest.main()

