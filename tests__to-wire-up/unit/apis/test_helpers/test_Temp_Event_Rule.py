from unittest import TestCase

from osbot_aws.apis.test_helpers.Temp_Event_Rule import Temp_Event_Rule
from osbot_utils.utils.Dev import pprint


class test_Temp_Event_Rule(TestCase):

    def test_simple_execution(self):
        with Temp_Event_Rule() as event_rule:
            assert event_rule.info().get('State') == 'ENABLED'
            assert event_rule.exists() is True
        assert event_rule.exists() is False