import sys; sys.path.append('..')
from unittest import TestCase

from pbx_gs_python_utils.utils.Dev import Dev
from osbot_aws.apis.Logs import Logs


class test_Logs(TestCase):

    def setUp(self):
        self.logs = Logs()


    def test_log_group_create(self):
        name    = '/unit-tests/test_log_group'
        assert self.logs.group_exists (name) is False
        assert self.logs.group_create (name) == self.logs
        assert self.logs.group_exists (name) is True
        assert self.logs.group_details(name).get('logGroupName') == name
        assert self.logs.group_delete (name) == self.logs
        assert self.logs.group_exists (name) is False

    def test_groups(self):
        assert len(list(self.logs.groups())) > 1
        assert len(self.logs.groups()) > 100

    def test_logs(self):
        group_name  = 'awslogs-temp_task_on_temp_cluster_X29B3K'
        stream_name = 'awslogs-example/gs-docker-codebuild/f8ccf213-b642-466c-8458-86af9933eca9'
        messages    = self.logs.get_messages(group_name, stream_name)
        assert len(messages) > 10