from unittest import TestCase

import pytest

from osbot_aws.apis.Cloud_Watch import Cloud_Watch
from osbot_utils.utils.Dev import pprint
from osbot_utils.utils.Misc import list_set


class test_Cloud_Watch(TestCase):

    def setUp(self):
        self.cloud_watch = Cloud_Watch()

    def test_client(self):
        assert type(self.cloud_watch.client()).__name__ == 'CloudWatch'

    def test_alarms(self):
        result = self.cloud_watch.alarms()
        assert list_set(result) == ['composite_alarms', 'metric_alarms']

    @pytest.mark.skip('write test with valid metric and namespace')
    def test_alarms_for_metric(self):
        metric_name = None
        namespace   = None
        result = self.cloud_watch.alarms_for_metric(metric_name=metric_name, namespace=namespace)
        pprint(result)

    def test_anomaly_detectors(self):
        result = self.cloud_watch.anomaly_detectors()
        assert type(result) is list

    def test_dashboards(self):
        result = self.cloud_watch.dashboards()
        assert len(result) > 0

    def test_insight_rules(self):
        result = self.cloud_watch.insight_rules()
        assert type(result) is list

    def test_metrics(self):
        result = self.cloud_watch.metrics()
        assert len(result) == 500

    @pytest.mark.skip('write test with valid resource_arn')
    def test_tags_for_resource(self):
        resource_arn = None
        result = self.cloud_watch.tags_for_resource(resource_arn)
        pprint(result)


