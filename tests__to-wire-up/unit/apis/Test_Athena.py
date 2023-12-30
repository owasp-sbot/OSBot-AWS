import unittest

from osbot_aws.apis.Athena import Athena

@unittest.skip("Needs test that create and destroy the test data")
class Test_Create_Lambda(unittest.TestCase):

    def setUp(self):
        self.athena = Athena()

    def test_query_status(self):
        query_id = 'a6196fb5-c36a-4a4e-a41e-6d33a51dbfad'
        assert self.athena.query_status(query_id) == 'SUCCEEDED'

    def test_query_results(self):
        query_id = 'd67863d0-3f8d-4ccf-94c7-cc65c0dcd311'
        results = self.athena.query_results(query_id)
        ips = [row['ip'] for row in results]
        assert '1.1.1.1' in ips
        assert len(ips) > 35

    def test_run_query(self):
        query     = 'SELECT * FROM "dd"."ipdata" '
        database  = 'dd'
        s3_output = 's3://gs-team-tests/dinis/athena-logs/created-by-tests'
        query_id = self.athena.start_query(query, database, s3_output)
        assert self.athena.query_status(query_id) == 'RUNNING'
        self.athena.wait_for_query(query_id)
        assert self.athena.query_status(query_id) == 'SUCCEEDED'
        print(query_id)

if __name__ == '__main__':
    unittest.main()