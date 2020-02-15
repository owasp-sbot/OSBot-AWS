import unittest
from unittest import TestCase

from osbot_aws.apis.IAM import IAM

from osbot_aws.apis.S3 import S3
from pbx_gs_python_utils.utils.Dev import Dev

from gw_bot.helpers.Test_Helper import Test_Helper
from osbot_aws.apis.Cloud_Trail import Cloud_Trail

class test_CloudTrail_To_Elk(Test_Helper):

    def setUp(self):
        super().setUp()
        self.cloud_trail = Cloud_Trail()

    def test__init__(self):
        assert type(self.cloud_trail).__name__ == 'Cloud_Trail'

    def test_events(self):
        self.result = self.cloud_trail.events(self.cloud_trail.date_minutes_ago(20), self.cloud_trail.date_now())

    def test_events_in_last(self):
        events = self.cloud_trail.events_in_last(50)
        self.result = list(events)

    def test_tags(self):
        self.result = self.cloud_trail.tags([])

    def test_trail_create(self):
        region         = IAM().region()
        name           = 'test_trail'
        s3_bucket      = 'gw-bot-trails'
        s3_key_prefix  = name
        sns_topic_name = 'test_sns_topic'
        S3().bucket_create(s3_bucket,region)

        self.result = self.cloud_trail.trail_create(name, s3_bucket, s3_key_prefix, sns_topic_name)


    def test_trails(self):
        self.result = self.cloud_trail.trails()

    # def send_to_elk(self, data,id_key):
    #     from pbx_gs_python_utils.utils.Elastic_Search import Elastic_Search
    #     self.index_id = 'gs-cst-cloud-trail'
    #     self.aws_secret_id = 'elastic-logs-server-1'
    #     self.elastic = Elastic_Search(index=self.index_id, aws_secret_id=self.aws_secret_id)
    #     self.elastic.create_index()
    #     return self.elastic.add_bulk(data,id_key)
    #
    # def test_send_events_to_elk(self):
    #     events = self.cloud_trail.events()
    #     result = self.send_to_elk(events,'EventId')
    #     Dev.pprint(result)