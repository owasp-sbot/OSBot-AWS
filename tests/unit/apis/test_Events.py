from unittest import TestCase

from osbot_utils.utils.Json import json_parse, json_to_str

from osbot_aws.apis.Events import Events
from osbot_aws.apis.SQS import SQS
from osbot_aws.apis.STS import STS
from osbot_aws.helpers.SQS_Queue import SQS_Queue
from osbot_utils.utils.Dev import pprint
from osbot_utils.utils.Misc import list_pop, date_now, random_string


class test_Events(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.events             = Events()
        cls.rule_name          = 'osbot_temp_rule'
        cls.rule_event_source  = 'temp_event_source' # 'aws.ec2' #
        cls.rule_description   = 'temp_description'
        cls.rule_tags          = {'Name': 'osbot_aws-test_test_rule_create'}

        #cls.events.rule_create(rule_name=cls.rule_name, event_source=cls.rule_event_source, description=cls.rule_description, tags=cls.rule_tags)
        #assert cls.events.rule_exists(cls.rule_name) is True

    #@classmethod
    #def tearDownClass(cls) -> None:
        #assert cls.events.rule_delete(cls.rule_name) is True

    #def setUp(self) -> None:
        #STS().check_current_session_credentials()
        #self.rule_name = 'ec2-events-v2'


    def test_archive(self):
        archives     = self.events.archives(index_by="ArchiveName")
        archive_name = archives.keys().pop()
        if archive_name:
            archive = self.events.archive(archive_name=archive_name)
            assert archive.get('ArchiveName') == archive_name

    def test_event_put(self):
        event_data = f'{{"id":"event_1", "value***": "{random_string()}"}}'
        event = {   'Time'      : date_now(),
                    'Source'    : self.rule_event_source,
                    "DetailType": "myTestType",
                    'Detail'    : event_data,
                    }

        # rule_name = self.rule_name
        # target_id = "test-target-1"
        # target_arn = 'arn:aws:sqs:eu-west-2:785217600689:testing-ec2-events-queue'
        # result = self.events.target_create(rule_name=rule_name, target_id=target_id, target_arn=target_arn)
        # pprint(result)
        pprint(event)
        result = self.events.events_put([event])
        pprint(result)

        #result = self.events.target_delete(rule_name=rule_name, target_id=target_id)
        #pprint(result)

    def test_rule(self):
        result = self.events.rule(rule_name=self.rule_name)
        assert result.get('Name') == self.rule_name

    def test_rule_create(self):
        role_arn = "arn:aws:events:eu-west-2:785217600689:rule/test-2"
        rule_name = self.rule_name + "__2"
        result = self.events.rule_create(rule_name=rule_name, event_source=self.rule_event_source, description=self.rule_description, tags=self.rule_tags,
                                         role_arn=role_arn)
        assert self.events.rule_exists(self.rule_name) is True

        pprint(result)

        target_id = "test-target-1"
        target_arn = 'arn:aws:sqs:eu-west-2:785217600689:testing-ec2-events-queue'
        result = self.events.target_create(rule_name=rule_name, target_id=target_id, target_arn=target_arn)

        pprint(result)

        event_data = f'{{"id":"event_1", "value": "{random_string()}"}}'
        event = {   'Time'      : date_now(),
                    'Source'    : self.rule_event_source,
                    "DetailType": "myTestType",
                    'Detail'    : event_data,
                    }
        result = self.events.events_put([event])
        pprint(result)

    def test_target_create(self):
        rule_name  = self.rule_name
        target_id  = "test-target-1"
        target_arn = 'arn:aws:sqs:eu-west-2:785217600689:testing-ec2-events-queue'
        result = self.events.target_create(rule_name=rule_name, target_id=target_id, target_arn=target_arn)
        pprint(result)
        result  = self.events.target_delete(rule_name=rule_name, target_id=target_id)
        pprint(result)

    def test_targets(self):
        sqs        = SQS()
        result     = self.events.targets(rule_name=self.rule_name, index_by='Arn')
        queue_arn  = result.keys().first()
        queue_url  = sqs.queue_url_from_queue_arn(queue_arn=queue_arn)
        queue      = SQS_Queue(queue_url=queue_url)
        #pprint(result)
        action = f'SendMessage'
        rule_role_arn       = 'arn:aws:events:eu-west-2:785217600689:rule/osbot_temp_rule'
        policy_statement_id = f'allow-rule-{self.rule_name}'
        new_statement  = {'Action'   : 'sqs:SendMessage',
                         'Condition': {'ArnEquals': {'aws:SourceArn':rule_role_arn}},
                         'Effect'   : 'Allow',
                         'Principal': {'Service': 'events.amazonaws.com'},
                         'Resource' : queue_arn,
                         'Sid'      : policy_statement_id}


        #queue.add_permission(queue_url=queue_url, label=f'permission_for_{self.rule}', )
        policy  = queue.policy()
        pprint(new_statement)

        policy.get('Statement').append(new_statement)

        policy_str = json_to_str(policy)
        #
        queue.attributes_update({"Policy":policy_str})

        pprint(queue.policy())

        #queue.permission_delete(policy_statement_id)
        #assert queue.info().get('QueueArn') == queue_arn
        #pprint(queue.sqs().client().add_permission(**kwargs) )
        #pprint(json_parse(queue.info().get('Policy')))


    def test_rules(self):
        result = self.events.rules(index_by='Name')
        assert self.rule_name in result
        pprint(result)

