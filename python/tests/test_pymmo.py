import unittest
import os
import inspect
import socket

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

if __name__ == '__main__':
    unittest.main()

