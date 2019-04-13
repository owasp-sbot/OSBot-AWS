import unittest
from unittest import TestCase

from pbx_gs_python_utils.utils.Dev import Dev

from osbot_aws.apis.Cloud_Trail import Cloud_Trail

@unittest.skip("Needs test that create and destroy the test data, and move send_to_elk to an helper class")
class test_CloudTrail_To_Elk(TestCase):

    def setUp(self):
        self.cloud_trail = Cloud_Trail()

    def send_to_elk(self, data,id_key):
        from pbx_gs_python_utils.utils.Elastic_Search import Elastic_Search
        self.index_id = 'gs-cst-cloud-trail'
        self.aws_secret_id = 'elastic-logs-server-1'
        self.elastic = Elastic_Search(index=self.index_id, aws_secret_id=self.aws_secret_id)
        self.elastic.create_index()
        return self.elastic.add_bulk(data,id_key)

    def test__init__(self):
        assert type(self.cloud_trail).__name__ == 'Cloud_Trail'

    # TODO
    def test_events(self):
        events = self.cloud_trail.events()
        result = self.send_to_elk(events,'EventId')
        Dev.pprint(result)