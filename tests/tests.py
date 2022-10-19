import unittest
import os
import sys
import pathlib
from datetime import timedelta
from datetime import datetime

sys.path.insert(0,str(pathlib.Path(__file__).parent.resolve() / ".."))
print(sys.path)
from src.cleaner import get_config, parse_time, needs_deletion

class TestClass(unittest.TestCase):
    
    def setUp(self):
        self.env = {
                "CLEANER_EXPIRATION_DURATION" : "1h19m",
                "CLEANER_CLEANING_INTERVAL"   : "6m18s",
                "CLEANER_ENDPOINT"            : "test:8999",
                "CLEANER_PATH"                : "test/test",
                "CLEANER_LOG_LVL"             : "DEBUG",
                "CLEANER_DRY_RUN"             : "FALSE"
        }
        os.environ.update(self.env)

    def test_get_config(self):

        expected_config = {
                "expiration_duration" : self.env["CLEANER_EXPIRATION_DURATION"],
                "cleaning_interval"   : self.env["CLEANER_CLEANING_INTERVAL"],
                "endpoint"            : self.env["CLEANER_ENDPOINT"],
                "path"                : self.env["CLEANER_PATH"],
                "log_lvl"             : self.env["CLEANER_LOG_LVL"],
                "dry_run"             : self.env["CLEANER_DRY_RUN"]
        }
        actual_config = get_config()

        self.assertEqual(actual_config, expected_config)


    def test_parse_time(self):

        self.assertEqual(parse_time("10s"), timedelta(seconds=10) )
        self.assertEqual(parse_time("10m"), timedelta(seconds=600) )
        self.assertEqual(parse_time("2h"), timedelta(seconds=7200) )
        self.assertEqual(parse_time("2h1m5s"), timedelta(seconds=7265))

    def test_needs_deletion(self):
        c = get_config()
        expired_date = datetime.now() - parse_time(c["expiration_duration"]) - timedelta(seconds=1)
        expired_timestamp = int(expired_date.timestamp())
        self.assertTrue(needs_deletion(expired_timestamp))

        fresh_date = datetime.now() - parse_time(c["expiration_duration"]) + timedelta(seconds=1)
        fresh_timestamp = int(fresh_date.timestamp())
        self.assertFalse(needs_deletion(fresh_timestamp))


if __name__ == '__main__':
    unittest.main()
