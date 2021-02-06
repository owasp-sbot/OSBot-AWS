from unittest import TestCase

from osbot_aws.apis.test_helpers.Temp_SQS_Queue import Temp_SQS_Queue
from osbot_aws.decorators.aws_inject import aws_inject
from osbot_utils.utils.Json          import json_parse
from osbot_aws.apis.Events           import Events
from osbot_utils.utils.Dev           import pprint
from osbot_utils.utils.Misc import date_now, random_string, wait


class test_Events(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.events             = Events()
        cls.rule_name          = random_string(prefix='k8_temp_rule-')
        cls.rule_event_source  = 'temp_event_source' # 'aws.ec2' #
        cls.rule_description   = 'temp_description'
        cls.rule_tags          = {'Name': 'osbot_aws-test_test_rule_create'}

        cls.events.rule_create(rule_name=cls.rule_name, event_source=cls.rule_event_source, description=cls.rule_description, tags=cls.rule_tags)
        assert cls.events.rule_exists(cls.rule_name) is True

    @classmethod
    def tearDownClass(cls) -> None:
        assert cls.events.rule_delete(cls.rule_name) is True


    def test_archive(self):
        archives     = self.events.archives(index_by="ArchiveName")
        archive_name = archives.keys().pop()
        if archive_name:
            archive = self.events.archive(archive_name=archive_name)
            assert archive.get('ArchiveName') == archive_name

    def test_event_put(self):
        with Temp_SQS_Queue(fifo=True) as queue:
            target_id         = queue.name()
            target_arn        = queue.arn()
            rule_name         = self.rule_name
            source_arn        = self.events.rule_arn(self.rule_name)
            service           = 'events.amazonaws.com'
            resource          = queue.arn()
            target_attributes = { 'SqsParameters': { 'MessageGroupId': 'string'}}
            queue.permission_add_for_service(source_arn=source_arn, service=service, resource=resource)

            self.events.target_create(rule_name=rule_name, target_id=target_id, target_arn=target_arn, target_attributes=target_attributes)

            #assert queue.url() == SQS().queue_url_from_queue_arn(queue_arn=queue.arn())

            event_data = f'{{"id":"event_1", "value***": "{random_string()}"}}'
            event = {   'Time'      : date_now(),
                        'Source'    : self.rule_event_source,
                        "DetailType": "myTestType",
                        'Detail'    : event_data,
                        }

            self.events.events_put([event])
            self.events.events_put([event])
            self.events.events_put([event])
            wait(0.5)                                   # todo see if there is a better way to wait for messages to be available
            assert queue.size() > 0

            message  = queue.pop()
            assert message.get('detail') == json_parse(event_data)

            self.events.target_delete(rule_name=rule_name, target_id=target_id)

    def test_rule(self):
        result = self.events.rule(rule_name=self.rule_name)
        assert result.get('Name') == self.rule_name
        pprint(result)

    def test_rule_create(self):
        rule_name = self.rule_name + "__2"
        self.events.rule_create(rule_name=rule_name, event_source=self.rule_event_source, description=self.rule_description, tags=self.rule_tags)
        assert self.events.rule_exists(rule_name=rule_name) is True
        assert self.events.rule_delete(rule_name=rule_name) is True

    @aws_inject('account_id,region')
    def test_target_create(self, account_id, region):
        rule_name     = self.rule_name
        target_id     = random_string()
        target_arn    = f'arn:aws:sqs:{region}:{account_id}:an-queue-name'
        result_create = self.events.target_create(rule_name=rule_name, target_id=target_id, target_arn=target_arn)

        assert result_create == {'FailedEntries': [], 'FailedEntryCount': 0}
        assert (self.events.target_exists(rule_name, target_id))

        assert target_arn in self.events.targets(rule_name=self.rule_name, index_by='Arn')

        result_delete  = self.events.target_delete(rule_name=rule_name, target_id=target_id)
        assert result_delete == {'FailedEntries': [], 'FailedEntryCount': 0}

    def test_rules(self):
        result = self.events.rules(index_by='Name')
        assert self.rule_name in result
        pprint(result)

