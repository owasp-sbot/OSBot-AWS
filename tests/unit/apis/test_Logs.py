import sys;
from time import sleep

sys.path.append('..')

from pbx_gs_python_utils.utils.Misc import Misc
from unittest import TestCase

from pbx_gs_python_utils.utils.Dev import Dev
from osbot_aws.apis.Logs import Logs


class test_Logs(TestCase):

    log_group       = '/unit-tests/test_log_group'
    stream_name     = 'tmp_stream'
    logs            = Logs(log_group,stream_name)
    delete_on_exit  = True

    @classmethod
    def setUpClass(cls):
        if test_Logs.delete_on_exit:
            assert test_Logs.logs.group_create() is True

    @classmethod
    def tearDownClass(cls):
        if test_Logs.delete_on_exit:
            assert test_Logs.logs.group_delete() is True

    def setUp(self):
        self.logs = Logs(test_Logs.log_group,test_Logs.stream_name)
        self.logs.stream_create()

    def test_events(self):
        assert self.logs.events().get('events') == []
        message_1 = 'an message'
        message_2 = 'another message'
        result = self.logs.event_add(message_1)
        assert result.get('status') == 'ok'
        assert 'An error occurred (DataAlreadyAcceptedException)' in self.logs.event_add('an message').get('data')
        assert self.logs.event_add(message_2,sequence_token=result.get('nextSequenceToken')).get('status') == 'ok'
        sleep(1)                              # wait for log events to be processed
        assert len(self.logs.events().get('events')) ==2
        assert self.logs.messages() == [message_1, message_2]

    def test_log_group_create_delete_exists_info(self):
        tmp_log_group = Misc.random_string_and_numbers(prefix='/unit-tests/test_log_group_')
        temp_logs     = Logs(tmp_log_group,'')
        assert temp_logs.group_exists () is False
        assert temp_logs.group_create () is True
        assert temp_logs.group_exists () is True
        assert temp_logs.group_info   ().get('logGroupName') == tmp_log_group
        assert temp_logs.group_delete () == True
        assert temp_logs.group_exists () is False

    def test_groups(self):
        assert len(list(self.logs.groups())) > 1
        assert len(self.logs.groups()) > 100

    def test_streams__exists_delete_create(self):
        assert self.logs.stream_exists() is True                                        # log stream is created by setUpClass
        assert self.logs.streams().pop().get('logStreamName') == test_Logs.stream_name
        assert self.logs.stream_delete() is True
        assert self.logs.stream_delete() is False
        assert self.logs.streams() == []
        assert self.logs.stream_create() is True
        assert self.logs.stream_create() is False