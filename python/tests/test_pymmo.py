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
        self.assertEqual("MongoClient('localhost', 27017)", str(c))

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

    def test_mmo_what_process_am_i(self):
        m = MmoMongoCluster("localhost", 27017, "admin", "admin", "admin")
        c = m.mmo_connect()
        i_should_be_a_mongos = m.mmo_what_process_am_i(c)
        self.assertEqual(i_should_be_a_mongos, "mongos")

    def test_mmo_is_mongos(self):
        m = MmoMongoCluster("localhost", 27017, "admin", "admin", "admin")
        c = m.mmo_connect()
        self.assertTrue(m.mmo_is_mongos(c))

    def test_mmo_is_mongod(self):
        m = MmoMongoCluster("localhost", 27017, "admin", "admin", "admin")
        c = m.mmo_connect()
        pass

    def test_mmo_mongo_version(self):
        m = MmoMongoCluster("localhost", 27017, "admin", "admin", "admin")
        c = m.mmo_connect()
        self.assertEquals("3.2.3", m.mmo_mongo_version(c))

    def test_mmo_execute_on_cluster(self):
        m = MmoMongoCluster("localhost", 27017, "admin", "admin", "admin")
        c = m.mmo_connect()
        o = m.mmo_execute_on_cluster(c, "buildinfo")
        self.assertEquals(6, len(o))
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

    def test_mmo_execute_on_primaries(self):
        m = MmoMongoCluster("localhost", 27017, "admin", "admin", "admin")
        c = m.mmo_connect()
        o = m.mmo_execute_on_primaries(c, "buildinfo")
        self.assertEquals(2, len(o))
        self.assertTrue("openssl" in str(o))

    def test_mmo_execute_on_secondaries(self):
        m = MmoMongoCluster("localhost", 27017, "admin", "admin", "admin")
        c = m.mmo_connect()
        o = m.mmo_execute_on_secondaries(c, "buildinfo")
        self.assertEquals(4, len(o))
        self.assertTrue("openssl" in str(o))

    def test_mmo_shards(self):
        m = MmoMongoCluster("localhost", 27017, "admin", "admin", "admin")
        c = m.mmo_connect()
        shards = m.mmo_shards()
        self.assertEquals([ "rs0", "rs1" ], shards)

    def test_mmo_replication_status(self):
        m = MmoMongoCluster("localhost", 27017, "admin", "admin", "admin")
        c = m.mmo_connect()
        o = m.mmo_replication_status(c)
        self.assertEquals(2, len(o))
        self.assertTrue("lastHeartbeatRecv" in str(o))

    def test_mmo_replication_status_summary(self):
        m = MmoMongoCluster("localhost", 27017, "admin", "admin", "admin")
        c = m.mmo_connect()
        o = m.mmo_replication_status_summary(c)
        self.assertEquals(6, len(o))
        self.assertTrue("slaveDelay" in str(o))

    def test_mmo_cluster_serverStatus(self):
        m = MmoMongoCluster("localhost", 27017, "admin", "admin", "admin")
        c = m.mmo_connect()
        o = m.mmo_cluster_serverStatus(c, False)
        self.assertEquals(6, len(o))
        self.assertTrue("metrics" in str(o))

    def test_mmo_cluster_hostInfo(self):
        m = MmoMongoCluster("localhost", 27017, "admin", "admin", "admin")
        c = m.mmo_connect()
        o = m.mmo_cluster_hostInfo(c, False)
        self.assertEquals(6, len(o))
        self.assertTrue("memSizeMB" in str(o))

    def test_mmo_list_databases_on_cluster(self):
        m = MmoMongoCluster("localhost", 27017, "admin", "admin", "admin")
        c = m.mmo_connect()
        o = m.mmo_list_databases_on_cluster(c, False)
        self.assertEquals(6, len(o))
        self.assertTrue("sizeOnDisk" in str(o))

    def test_mmo_list_collections_on_cluster(self):
        m = MmoMongoCluster("localhost", 27017, "admin", "admin", "admin")
        c = m.mmo_connect()
        o = m.mmo_list_collections_on_cluster(c, False, "test")
        self.assertEquals(6, len(o))
        self.assertTrue("restaurants" in str(o))
        self.assertTrue("sample_messages" in str(o))

    def test_mmo_list_dbhash_on_cluster(self):
        m = MmoMongoCluster("localhost", 27017, "admin", "admin", "admin")
        c = m.mmo_connect()
        o = m.mmo_list_dbhash_on_cluster(c)
        self.assertEquals(4, len(o))
        self.assertTrue("restaurants" in str(o))
        self.assertTrue("sample_messages" in str(o))

    def test_mmo_execute_on_cluster_on_each_db(self):
        m = MmoMongoCluster("localhost", 27017, "admin", "admin", "admin")
        c = m.mmo_connect()
        o = m.mmo_execute_on_cluster_on_each_db(c, "dbHash", False)
        self.assertEquals(4, len(o))
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
        o = m.mmo_change_profiling_level(c, -1)
        self.assertEquals(0, o[0]["command_output"]["was"])
        o = m.mmo_change_profiling_level(c, 1)
        o = m.mmo_change_profiling_level(c, -1) # We must request again to get the current state
        self.assertEquals(1, o[0]["command_output"]["was"])
        o = m.mmo_change_profiling_level(c, 2)
        o = m.mmo_change_profiling_level(c, -1)
        self.assertEquals(2, o[0]["command_output"]["was"])
        o = m.mmo_change_profiling_level(c, 0)
        o = m.mmo_change_profiling_level(c, -1)
        self.assertEquals(0, o[0]["command_output"]["was"])

    def test_mmo_sharding_status(self):
        m = MmoMongoCluster("localhost", 27017, "admin", "admin", "admin")
        c = m.mmo_connect()
        o = m.mmo_sharding_status(c)
        self.assertTrue("rs0" in str(o))
        self.assertTrue("rs1" in str(o))
        self.assertEquals(1.0, o["ok"])
        self.assertEquals(2, len(o["shards"]))
        self.assertEquals("rs0", o["shards"][0]["_id"])
        self.assertEquals("rs1", o["shards"][1]["_id"])

if __name__ == '__main__':
    unittest.main()

