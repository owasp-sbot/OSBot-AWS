from unittest import TestCase
from osbot_utils.utils.Misc import random_string
from osbot_aws.apis.Cloud_Watch_Logs import Cloud_Watch_Logs
from osbot_utils.utils.Dev import pprint


class test_Cloud_Watch_Logs(TestCase):
    logs            = None
    log_group_name  = None
    log_stream_name = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.logs = Cloud_Watch_Logs()
        cls.log_group_name  = "temp_log_group_name"
        cls.log_stream_name = "temp_log_stream_name"

        # create temp log group
        assert cls.logs.log_group_exists(cls.log_group_name) is False
        assert cls.logs.log_group_create(log_group_name=cls.log_group_name).get('message') == f'log group created ok: {cls.log_group_name}'
        assert cls.logs.log_group_exists(cls.log_group_name) is True
        # create temp log stream
        assert cls.logs.log_stream_exists(cls.log_group_name, cls.log_stream_name) is False
        assert cls.logs.log_stream_create(log_group_name=cls.log_group_name, log_stream_name=cls.log_stream_name).get('message') == f"log stream created ok: {cls.log_stream_name}"
        assert cls.logs.log_stream_exists(cls.log_group_name, cls.log_stream_name) is True

    @classmethod
    def tearDownClass(cls) -> None:
        # delete temp log stream
        assert cls.logs.log_stream_exists(cls.log_group_name, cls.log_stream_name) is True
        assert cls.logs.log_stream_delete(cls.log_group_name, cls.log_stream_name).get('message') == f"log stream deleted ok: {cls.log_stream_name}"
        assert cls.logs.log_stream_exists(cls.log_group_name, cls.log_stream_name) is False
        # delete temp log group
        assert cls.logs.log_group_delete(log_group_name=cls.log_group_name).get('message') == f'log group deleted ok: {cls.log_group_name}'
        assert cls.logs.log_group_exists(cls.log_group_name) is False


    def test_client(self):
        assert type(self.logs.client()).__name__ == 'CloudWatchLogs'

    def test_destinations(self):
        result = self.logs.destinations()
        assert result == []                                    # todo add test for this method

    def test_export_tasks(self):
        result = self.logs.export_tasks()
        assert result == []                                    # todo add test for this method

    def test_log_group(self):
        result = self.logs.log_group(log_group_name=self.log_group_name)
        assert result.get('logGroupName') == self.log_group_name
        assert result.get('arn'         ) == self.logs.log_group_arn(log_group_name=self.log_group_name)


    def test_log_groups(self):
        result = self.logs.log_groups(log_group_prefix=self.log_group_name)
        assert len(result) == 1
        assert result[0].get('logGroupName') == self.log_group_name

    def test_log_stream_create(self):
        bad_log_group_name = random_string()
        assert self.logs.log_stream_create(bad_log_group_name,'').get('message') == f'log group does not exist: {bad_log_group_name}'

        assert self.logs.log_stream(self.log_group_name, self.log_stream_name).get('logStreamName') == self.log_stream_name


    def test_log_streams(self):
        bad_log_group_name = random_string()
        assert self.logs.log_streams(bad_log_group_name) == []

        result = self.logs.log_streams(self.log_group_name)
        assert len(result) == 1
        assert result[0].get('arn'          ) == self.logs.log_stream_arn(self.log_group_name, self.log_stream_name)
        assert result[0].get('logStreamName') == self.log_stream_name


    def test_metric_filters(self):
        result = self.logs.metric_filters()
        assert result == []                                    # todo add test for this method

    def test_queries(self):
        result = self.logs.queries()
        assert result == []                                    # todo add test for this method

    def test_query_definitions(self):
        result = self.logs.query_definitions()
        assert result == []                                    # todo add test for this method

    def test_resource_policies(self):
        result = self.logs.resource_policies()
        assert result == []                                    # todo add test for this method

    def test_subscription_filters(self):
        result = self.logs.subscription_filters(log_group_name=self.log_group_name)
        assert result == []                                    # todo add test for this method
