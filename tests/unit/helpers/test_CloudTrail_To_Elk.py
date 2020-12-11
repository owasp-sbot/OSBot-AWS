import json

import pytest

from osbot_aws.apis.IAM import IAM

from osbot_aws.helpers.Test_Helper import Test_Helper
from osbot_aws.apis.Cloud_Trail import Cloud_Trail

@pytest.mark.skip('Fix tests')
class test_CloudTrail(Test_Helper):

    def setUp(self):
        super().setUp()
        self.cloud_trail = Cloud_Trail()
        self.s3_bucket     = 'gw-tf-cloud-trails'
        self.trail_name    = 'test_trail'

        #self.s3_key_prefix = 'test-from-console' # self.trail_name
        #self.trail_name    = 'arn:aws:cloudtrail:eu-west-2:311800962295:trail/test-trail-via-console'

    def test__init__(self):
        assert type(self.cloud_trail).__name__ == 'Cloud_Trail'

    def test_event_selectors(self):
        self.result = self.cloud_trail.event_selectors(self.trail_name)

    def test_events(self):
        self.result = self.cloud_trail.events(self.cloud_trail.date_minutes_ago(20), self.cloud_trail.date_now())

    def test_events_in_last(self):
        events = self.cloud_trail.events_in_last(50)
        self.result = list(events)

    def test_tags(self):
        self.result = self.cloud_trail.tags([])

    def test_trail(self):
        self.result = self.cloud_trail.trail(self.trail_name)

    def test_trail_create(self):
        iam            = IAM()
        account_id     = iam.account_id()
        region         = iam.region()
        s3_key_prefix  = self.trail_name
        sns_topic_name = None

        self.result = self.cloud_trail.trail_create(self.trail_name, account_id, region, self.s3_bucket, s3_key_prefix)

    def test_trail_delete(self):
        self.result = self.cloud_trail.trail_delete(self.trail_name)

    def test_trail_start_stop(self):
        self.cloud_trail.trail_start(self.trail_name)
        assert self.cloud_trail.trail(self.trail_name).get('IsLogging') is True
        self.cloud_trail.trail_stop(self.trail_name)
        assert self.cloud_trail.trail(self.trail_name).get('IsLogging') is False

    def test_trails(self):
        self.result = self.cloud_trail.trails()


    def test_log_files__send_to_elk(self):
        iam         = IAM()
        account_id  = iam.account_id()
        region      = iam.region()
        year        = '2020'
        month       = '02'
        day         = '16'
        max         = 200
        log_files   = self.cloud_trail.log_files(self.trail_name, account_id, region, year, month, day)
        records     = self.cloud_trail.log_files_records(self.trail_name, log_files[0:max])

        self.result = self.send_to_elk(records, 'eventID')

    def send_to_elk(self, data,id_key):
        index_id = 'gw-cloud-trail'
        self.aws_secret_id = 'gw-elastic-server-1'
        from gw_bot.elastic.Elastic_Search import Elastic_Search
        self.elastic = Elastic_Search(index=index_id, aws_secret_id=self.aws_secret_id)
        #self.elastic.create_index().create_index_pattern(time_field='eventTime')
        #self.elastic.delete_index()
        return self.elastic.add_bulk(data,id_key)


    #
    # def test_send_events_to_elk(self):
    #     events = self.cloud_trail.events()
    #     result = self.send_to_elk(events,'EventId')
    #     Dev.pprint(result)

    ## test experiments

    def test_get_available_log_files(self):
        iam        = IAM()
        account_id = iam.account_id()
        region     = iam.region()
        log_type   = 'CloudTrail'
        year       = '2020'
        month      = '02'
        day        = '16'
        hour       = ''
        minute     = ''
        s3_prefix = f'{self.s3_key_prefix}/AWSLogs/{account_id}/'                           \
                    f'{log_type}/{region}/{year}/{month}/{day}/'
        s3          = self.cloud_trail.s3
        s3_files    = s3.find_files(self.s3_bucket, prefix=s3_prefix)
        print('-------')
        total = 0
        for s3_file in sorted(s3_files):
            contents    = s3.file_contents_from_gzip(self.s3_bucket,s3_file)
            records = json.loads(contents).get("Records")
            total += len(records)
            print(f'{len(records): 4} : {total : 4} : {s3_file.split("/").pop()}')

