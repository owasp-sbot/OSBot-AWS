from unittest import TestCase

import pytest
from osbot_utils.utils.Files import file_create_from_bytes, file_exists

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

    def test_dashboard(self):
        dashboards_names = self.cloud_watch.dashboards_names()
        for dashboard_name in dashboards_names:
            dashboard = self.cloud_watch.dashboard(dashboard_name=dashboard_name)
            assert list_set(dashboard) == ['arn', 'name', 'widgets']
            for widget in dashboard.get('widgets'):
                assert list_set(widget) == ['height', 'properties', 'type', 'width', 'x', 'y']
            pprint(dashboard)



    @pytest.mark.skip('write test with with creating and deleting dashboards')
    def test_dashboards(self):
        result = self.cloud_watch.dashboards()
        assert len(result) > 0

    def test_insight_rules(self):
        result = self.cloud_watch.insight_rules()
        assert type(result) is list

    def test_metric_image(self):
        image_in_tmp = "/tmp/cloud_watch_metric.png"
        instance_id = "i-0a2a089f3dd878051"#"i-0f9b8338610fc96e7"
        options = {
            "id"        : "m1"          ,
            "stat"      : "Average"     ,
            "label"     : "Median value",
            "visible"   : True          ,
            "color"     : "#0000FF"     ,
            "yAxis"     : "left"        ,
            "period"    : 1800
        }
        kwargs = {"namespace"       : "AWS/EC2"                  ,
                  "metric_name"     : "CPUUtilization"           ,
                  "dimensions"      : {"InstanceId": instance_id},
                  "path_image_file" : image_in_tmp               ,
                  "options"         : options                    ,
                  "title"           : "Metric Title"}

        result = self.cloud_watch.metric_image(**kwargs)
        pprint(result)
        # , path_image_file = image_in_tmp

    def test_metric_list(self):
        kwargs = {"namespace"       : "AWS/EC2"                  }
        result = self.cloud_watch.metric_list(**kwargs)
        pprint(result)

    def test_metric_widget_image(self):
        metric_widget = {"metrics": [["AWS/EC2", "CPUUtilization"]]}
        metric_image = self.cloud_watch.metric_widget_image(metric_widget=metric_widget, save_to_disk=True)
        assert file_exists(metric_image)

    def test_metrics(self):
        result = self.cloud_watch.metrics()
        assert len(result) == 500

    @pytest.mark.skip('write test with valid resource_arn')
    def test_tags_for_resource(self):
        resource_arn = None
        result = self.cloud_watch.tags_for_resource(resource_arn)
        pprint(result)




