import sys ;

import pytest

from osbot_aws.apis.Cloud_Watch_Logs import Cloud_Watch_Logs
from osbot_utils.utils.Misc import random_string

from osbot_aws.AWS_Config import AWS_Config
from osbot_aws.apis.STS import STS

sys.path.append('..')
import unittest

from unittest import TestCase
from osbot_utils.utils.Dev import Dev, pprint
from osbot_utils.utils import Misc
from osbot_aws.apis.ECS import ECS



class test_ECS(TestCase):

    ecs          = None
    cluster_name = None
    cluster_arn  = None

    @classmethod
    def setUpClass(cls) -> None:
        STS().check_current_session_credentials()
        cls.ecs          = ECS()
        cls.logs         = Cloud_Watch_Logs()
        cls.account_id   = cls.ecs.account_id
        cls.region       = cls.ecs.region
        cls.cluster_name = 'test_ecs_cluster_2'
        cls.task_family  = 'test_task_create'
        cls.cluster_arn  = cls.ecs.cluster_arn(cls.cluster_name)

        #create test cluster
        cluster = cls.ecs.cluster_create(cls.cluster_name)
        assert cluster.get('clusterArn'       ) == cls.cluster_arn
        assert cluster.get('clusterName'      ) == cls.cluster_name
        assert cluster.get('runningTasksCount')==0
        assert cls.cluster_arn in cls.ecs.clusters_arns()
        assert cls.ecs.cluster_exists(cluster_arn=cls.cluster_arn) is True
        pprint(cls.ecs.cluster(cluster_arn=cls.cluster_arn))

    @classmethod
    def tearDownClass(cls) -> None:
        cls.ecs.cluster_delete(cls.cluster_name)
        pprint(cls.ecs.cluster(cluster_arn=cls.cluster_arn) )
        pprint( cls.ecs.cluster_exists(cluster_arn=cls.cluster_arn) )
        #assert cls.ecs.cluster_exists(cluster_arn=cls.cluster_arn) is False

    def test__init__(self):
        assert type(self.ecs.client()).__name__ == 'ECS'

    # def test_cluster_create(self):
    #     pass

    # def test_cluster_delete(self):
    #     pass

    def test_cluster(self):
        result  = self.ecs.cluster(cluster_arn=self.cluster_arn)
        assert result.get('clusterName') == self.cluster_name
        assert result.get('clusterArn' ) == self.cluster_arn

        assert self.ecs.cluster(cluster_arn=self.cluster_arn+random_string()) is None

    def test_clusters(self):
        result  = self.ecs.clusters(index_by='clusterName')
        cluster = result.get(self.cluster_name)
        assert cluster.get('clusterArn') == self.ecs.cluster_arn(self.cluster_name)

        pprint(result)

    def test_clusters_arns(self):
        result = self.ecs.clusters_arns()
        if len(result) > 0:
            assert 'arn:aws:ecs:' in result[0]
        pprint(result)

    def test_policy_create_for_task_role(self):
        role_name = 'task_role_create_and_run_task'
        iam_role  = self.ecs.policy_create_for_task_role(role_name)
        assert iam_role.exists() is True                                    # todo: add asserts for the role created
        assert iam_role.delete() is True

    def test_policy_create_for_execution_role(self):
        role_name = 'task_execution_role_create_and_run_task'
        iam_role = self.ecs.policy_create_for_execution_role(role_name)
        assert iam_role.exists() is True                                    # todo: add asserts for the role and policy created
        assert iam_role.delete() is True

    def test_task_definition_create(self):
        task_family           = self.task_family
        image_name          = 'an_docker_image'
        task_role_name      = f'{task_family}_task_role'
        execution_role_name = f'{task_family}_execution_role'
        log_group_name      = "ecs-task-on-{0}".format(image_name)
        log_stream_name     = task_family
        task_role_iam       = self.ecs.policy_create_for_task_role     (task_role_name     )
        execution_role_iam  = self.ecs.policy_create_for_execution_role(execution_role_name)
        task_role_arn       = task_role_iam     .arn()
        execution_role_arn  = execution_role_iam.arn()

        assert task_role_iam     .exists() is True
        assert execution_role_iam.exists() is True

        task_definition = self.ecs.task_definition_create(task_family        = task_family          ,
                                                          image_name         = image_name         ,
                                                          task_role_arn      = task_role_arn      ,
                                                          execution_role_arn = execution_role_arn ,
                                                          log_group_name     = log_group_name     ,
                                                          log_stream_name    = log_stream_name    )

        task_definition_arn = task_definition.get('taskDefinitionArn')
        #assert  task_definition_arn == f'arn:aws:ecs:{self.region}:{self.account_id}:task-definition/{task_name}:1'
        assert task_definition.get('family' ) == task_family
        assert task_definition.get('cpu'    ) == '1024'
        assert task_definition.get('memory' ) == '2048'
        assert self.logs.log_group_exists(log_group_name                  ) is True
        assert self.logs.log_stream_exists(log_group_name, log_stream_name) is True

        assert self.ecs.task_definition_exists(task_definition_arn        ) is True
        assert self.ecs.task_definition_delete(task_definition_arn        ) is True
        assert self.ecs.task_definition_exists(task_definition_arn        ) is False


    def test_task_definition_delete(self):
        task_definitions_arns = self.ecs.task_definitions_arns(self.task_family)
        for task_definition_arn in task_definitions_arns:
            assert self.ecs.task_definition_delete(task_definition_arn=task_definition_arn) is True

    def test_task_definitions(self):
        result = self.ecs.task_definitions(self.task_family)
        pprint(result)

    def test_task_definitions_arns(self):
        result = self.ecs.task_definitions_arns(self.task_family)
        pprint(result)

    def test_task_delete(self):
        tasks  = self.ecs.tasks()
        for task in tasks:
            if 'family_created_via' in task:
                Dev.pprint('deleting task: {0}'.format(task))
                self.ecs.task_delete(task)

    @pytest.mark.skip("to fix")
    def test_task_run(self):
        account_id        = self.ecs.account_id
        region            = self.ecs.region
        docker_image_name = 'ubuntu'
        cluster_name      = self.cluster_name
        task_name         = 'temp_task_on_{0}'  .format(cluster_name)
        task_role         = 'task_role_{0}'     .format(task_name)
        execution_role    = 'execution_role_{0}'.format(task_name)

        cluster           = self.cluster_name #'FargateCluster'
        subnet_id         = 'subnet-49391932'
        security_group_id = 'sg-e6ea548e'

        task_name = 'create_and_run_task:45'
        task_arn = f'arn:aws:ecs:{region}:{account_id}:task-definition/{task_name}'

        task_run_arn = self.ecs.task_run(cluster, task_arn, subnet_id, security_group_id).get('taskArn')

        task_details = self.ecs.task_wait_for_completion(cluster, task_run_arn, sleep_for=1, log_status = True)
        Dev.pprint(task_details)

    @pytest.mark.skip("to fix")
    def test_task_details(self):
        task_id ='9400bb6b-f76f-4bce-b35d-5a4b15e79bfd'
        cluster = 'FargateCluster'
        tast_arn = 'arn:aws:ecs:eu-west-2:244560807427:task/{0}'.format(task_id)

        result = self.ecs.task_details(cluster, tast_arn)
        Dev.pprint(result)
        Dev.pprint(result.get('lastStatus'))
        Dev.pprint(result.get('containers'))

    @pytest.mark.skip("to fix")
    def test_tasks(self):
        result = self.ecs.tasks()
        Dev.pprint(result)
        assert len(result) > 1
        assert ':task-definition/' in result[0]

    @pytest.mark.skip("to fix")
    def test_run_container_on_temp_cluster(self):
        subnet_id               = ' subnet-49391932'
        security_group_id       = 'sg-e6ea548e'
        cluster_name            = Misc.random_string_and_numbers(6,'temp_cluster_')
        task_name               = 'temp_task_on_{0}'.format(cluster_name)
        task_role               = 'task_role_{0}'.format(task_name)
        execution_role          = 'execution_role_{0}'.format(task_name)
        docker_image_name       = 'gs-docker-codebuild'
        log_group_name          = "awslogs-{0}".format(task_name)
        log_group_region        = "eu-west-2"
        log_group_stream_prefix = "awslogs-example"

        # Create Cluster
        self.ecs.cluster_create(cluster_name)

        # Create Roles
        self.ecs.policy_create_for_task_role(task_role)
        self.ecs.policy_create_for_execution_role(execution_role)

        #Create Task
        task_arn     = self.ecs.task_create(task_name, task_role, execution_role).get('taskDefinitionArn')

        # Run Task
        task_run = self.ecs.task_run(cluster_name, task_arn, subnet_id, security_group_id)
        task_run_arn = task_run.get('taskArn')
        task_details = self.ecs.task_wait_for_completion(cluster_name, task_run_arn)

        task_id = 'asd'
        # Get logs

        #group_name  = 'awslogs-temp_task_on_temp_cluster_X29B3K'
        #stream_name = 'awslogs-example/gs-docker-codebuild/f8ccf213-b642-466c-8458-86af9933eca9'
        stream_name = "{0}/{1}{2}".format(log_group_stream_prefix,docker_image_name,task_id)

        messages = self.cloud_watch.logs_get_messages(log_group_name, stream_name)
        # Print details
        Dev.pprint(messages)