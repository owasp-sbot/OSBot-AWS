import sys;

from osbot_utils.utils.Misc import wait

from osbot_utils.utils.Dev import pprint

sys.path.append('..')
from unittest import TestCase
from osbot_aws.helpers.ECS_Fargate_Task import ECS_Fargate_Task


class test_ECS_Fargate_Task(TestCase):

    delete_on_tear_down = False

    @classmethod
    def setUpClass(cls) -> None:
        cls.cluster_name        = 'test_ECS_Fargate_Task'
        cls.image_name          = 'hello-world'
        cls.version             = 4
        cls.fargate_task        = ECS_Fargate_Task(cluster_name=cls.cluster_name, image_name=cls.image_name)
        cls.cluster_arn         = cls.fargate_task.cluster_arn()
        cls.task_definition_arn = cls.fargate_task.task_definition_arn()

        cls.fargate_task.setup()
        #cls.fargate_task.create()

    @classmethod
    def tearDownClass(cls) -> None:
        if cls.delete_on_tear_down:
            pass        # todo

    def setUp(self) -> None:
        self.ecs = self.fargate_task.ecs

    def test_setup(self):
        assert self.ecs.cluster_exists        (cluster_arn         = self.cluster_arn        ) is True
        assert self.ecs.task_definition_exists(task_definition_arn = self.task_definition_arn) is True

    def test_create(self):
        task_arn = self.fargate_task.task_arn
        assert self.fargate_task.ecs.task_exists(cluster_name=self.cluster_name, task_arn=task_arn)

    def test_delete_all(self):
        result = self.fargate_task.delete_all()
        pprint(result)

    def test_container(self):
        result = self.fargate_task.container()
        assert result.get('lastStatus') == 'PENDING'
        assert result.get('name'      ) == self.image_name
        assert result.get('taskArn'   ) == self.fargate_task.task_arn

    def test_info(self):
        result = self.fargate_task.info()
        assert result.get('launchType') == 'FARGATE'
        assert result.get('lastStatus') == 'PROVISIONING'

    def test_task_definition(self):
        task_definition = self.fargate_task.task_definition()
        assert task_definition.get('status') == 'ACTIVE'

    def test_task_definition_arn(self):
        task_definition_arn = self.fargate_task.task_definition_arn()
        assert self.ecs.task_definition_exists(task_definition_arn)


    # info: takes about 20 secs to complete
    def test_wait_for_task_running(self):
        task_info = self.fargate_task.wait_for_task_running()
        assert task_info.get('lastStatus') == 'RUNNING'
        assert self.fargate_task.log_stream_exists() is True
        assert 'Hello from Docker!\n' in self.fargate_task.logs()

    # info: takes about 40 secs to complete
    def test_wait_for_task_completed(self):
        task_info = self.fargate_task.wait_for_task_stopped()
        assert task_info.get('lastStatus') == 'STOPPED'

        logs = self.fargate_task.logs()
        assert 'Hello from Docker!\n' in logs

    # mist use cases

    def test_print_logs_when_exist(self):
        for i in range(0,30):
            exists = self.fargate_task.log_stream_exists()
            wait(1)                                         # give it more more secure to capture the logs
            if exists:                                      # when log stream exists
                return
        logs = self.fargate_task.logs()                     # get logs
        assert "Hello from Docker!" in logs                 # confirm we got the correct logs



