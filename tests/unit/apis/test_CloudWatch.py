from coverage.backunittest import TestCase

from pbx_gs_python_utils.utils.aws.Cloud_Watch import Cloud_Watch


class test_Cloud_Watch(TestCase):

    def setUp(self):
        self.cloud_watch = Cloud_Watch()

    def test__init__(self):
        type(self.cloud_watch.cloudwatch).__name__ == 'CloudWatch'

