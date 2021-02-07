import sys ;

import pytest
from osbot_utils.testing.Catch import Catch

from osbot_utils.decorators.methods.catch import catch

from osbot_aws.apis.Cloud_Watch_Logs import Cloud_Watch_Logs
from osbot_aws.apis.EC2 import EC2
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
        cls.cluster = cls.ecs.cluster_create(cls.cluster_name)
        assert cls.cluster.get('clusterArn'       ) == cls.cluster_arn
        assert cls.cluster.get('clusterName'      ) == cls.cluster_name
        assert cls.cluster.get('runningTasksCount')==0
        assert cls.cluster_arn in cls.ecs.clusters_arns()
        assert cls.ecs.cluster_exists(cluster_arn=cls.cluster_arn) is True

    # @classmethod
    # def tearDownClass(cls) -> None:
    #     cls.ecs.cluster_delete(cls.cluster_name)
    #     assert cls.ecs.cluster_exists(cluster_arn=cls.cluster_arn) is False

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

    def test_clusters_arns(self):
        result = self.ecs.clusters_arns()
        assert self.cluster_arn in result

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
        task_family = self.task_family
        image_name  = 'an_docker_image'
        task_definition_config = self.ecs.task_definition_setup(task_family=task_family, image_name=image_name)
        log_group_name         = task_definition_config.get('log_group_name' )
        log_stream_name        = task_definition_config.get('log_stream_name')

        task_definition = self.ecs.task_definition_create(task_definition_config=task_definition_config)

        task_definition_arn = task_definition.get('taskDefinitionArn')
        revision            = task_definition.get('revision')
        assert  task_definition_arn           == self.ecs.task_definition_arn(task_family, revision)
        assert task_definition.get('family' ) == task_family
        assert task_definition.get('cpu'    ) == '1024'
        assert task_definition.get('memory' ) == '2048'

        assert self.logs.log_group_exists(log_group_name                  ) is True
        assert self.logs.log_stream_exists(log_group_name, log_stream_name) is True

        assert self.ecs.task_definition_exists(task_definition_arn        ) is True
        assert self.ecs.task_definition_delete(task_definition_arn        ) is True
        assert self.ecs.task_definition_exists(task_definition_arn        ) is False

    # (already tested in test_task_definition_create)
    # def test_task_definition_delete(self):
    #     task_definitions_arns = self.ecs.task_definitions_arns(self.task_family)
    #     for task_definition_arn in task_definitions_arns:
    #         assert self.ecs.task_definition_delete(task_definition_arn=task_definition_arn) is True


    def test_task_run(self):
        ec2                    = EC2()
        image_name             = 'ubuntu' # 'hello-world' #
        task_family            = f"test_run_for_{image_name}"
        task_definition_config = self.ecs.task_definition_setup(task_family=task_family, image_name=image_name)
        task_definition        = self.ecs.task_definition_create(task_definition_config=task_definition_config)
        task_definition_arn    = task_definition.get('taskDefinitionArn')
        pprint(task_definition_arn)
        #task_definition_arn    =  'arn:aws:ecs:eu-west-2:785217600689:task/test_ecs_cluster_2/0177a42f9a3b4df6b4e3fc71c9a91544'

        subnet_id              = ec2.subnet_default_for_az().get('SubnetId')
        security_group_id      = ec2.security_group_default().get('GroupId')


        #account_id             = self.ecs.account_id
        #region                 = self.ecs.region

        cluster_name           = self.cluster_name
        task_name              = 'temp_task_on_{0}'  .format(cluster_name)
        #task_role              = 'task_role_{0}'     .format(task_name)
        #execution_role         = 'execution_role_{0}'.format(task_name)

        cluster                = self.cluster_name #'FargateCluster'
        #subnet_id              = 'subnet-49391932'
        #security_group_id      = 'sg-e6ea548e'

        #task_name = 'create_and_run_task:45'
        #task_arn = f'arn:aws:ecs:{region}:{account_id}:task-definition/{task_name}'
        task_arn = task_definition_arn
        task_run_arn = self.ecs.task_create(cluster, task_arn, subnet_id, security_group_id)
        pprint(task_run_arn)

        #task_details = self.ecs.task_details(cluster=cluster,task_arn=task_run_arn)
        #self.ecs.task_wait_for_completion(cluster, task_run_arn, sleep_for=1, log_status = True)
        #pprint(task_details)

        #self.ecs.task_definition_delete(task_definition_arn=task_definition_arn)

        #Dev.pprint(task_details)

    @pytest.mark.skip("to fix")
    def test_task_details(self):
        task_id ='9400bb6b-f76f-4bce-b35d-5a4b15e79bfd'
        cluster = 'FargateCluster'
        tast_arn = 'arn:aws:ecs:eu-west-2:244560807427:task/{0}'.format(task_id)

        result = self.ecs.task_details(cluster, tast_arn)
        Dev.pprint(result)
        Dev.pprint(result.get('lastStatus'))
        Dev.pprint(result.get('containers'))

    def test_task_definitions(self):
        result = self.ecs.tasks_definitions()
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
        task_run = self.ecs.task_create(cluster_name, task_arn, subnet_id, security_group_id)
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


class test_Simulate_Test_Run_Error(TestCase):

    def setUp(self):
        STS().check_current_session_credentials()
        self.cluster_name        = 'Simulate_Test_Run'
        #self.image_name          = 'ubuntu'
        self.image_name          = "hello-world"
        self.task_family         = f"test_run_for_{self.image_name}"
        self.task_name           = f'temp_task_on_{self.cluster_name}'
        self.execution_role      = f'{self.task_family}_execution_role'
        self.task_role           = f'{self.task_family}_task_role'
        self.cluster             = None

        #self.cluster_arn         = 'arn:aws:ecs:eu-west-1:785217600689:cluster/Simulate_Test_Run'
        self.task_definition_arn = 'arn:aws:ecs:eu-west-1:785217600689:task-definition/test_run_for_hello-world:1'
        self.task_id             = '1e9fbeba27fb43cc889e4b546123a0af'
        self.task_arn            = f'arn:aws:ecs:eu-west-1:785217600689:task/Simulate_Test_Run/{self.task_id}'
        self.ecs                 = ECS()

    def test_create_roles(self):
        self.ecs.policy_create_for_task_role     (self.task_role     , skip_if_exists=False)
        self.ecs.policy_create_for_execution_role(self.execution_role, skip_if_exists=False)

    def test_setup_cluster(self):
        self.cluster     = self.ecs.cluster_create(cluster_name=self.cluster_name)
        self.cluster_arn = self.ecs.cluster_arn(cluster_name=self.cluster_name)
        assert self.ecs.cluster_exists(cluster_arn=self.cluster_arn)
        pprint(self.cluster_arn)

    def test_create_task_definition(self):
        task_definition_config   = self.ecs.task_definition_setup(task_family=self.task_family, image_name=self.image_name)
        task_definition          = self.ecs.task_definition_create(task_definition_config=task_definition_config)
        task_definition_arn      = task_definition.get('taskDefinitionArn')

        self.task_definition_arn = task_definition_arn
        pprint(self.task_definition_arn)

    def test_task_create(self):
        ec2                    = EC2()
        subnet_id              = ec2.subnet_default_for_az().get('SubnetId')
        security_group_id      = ec2.security_group_default().get('GroupId')
        task                   = self.ecs.task_create(cluster_name=self.cluster_name, task_definition_arn=self.task_definition_arn, subnet_id=subnet_id, security_group_id=security_group_id)

        self.task_arn = task.get('taskArn')
        #self.ecs.task_wait_for_completion()
        pprint(self.task_arn)

    def test_task_details(self):
        task_definition = self.ecs.task_definition(task_definition_arn=self.task_definition_arn)
        task            = self.ecs.task_details(cluster_name=self.cluster_name, task_arn=self.task_arn)

        print('\n\n\n*********** task definition*************\n')
        pprint(task_definition)
        print('\n\n\n*********** task *************\n')
        pprint(task)
        #self.ecs.task_wait_for_completion(cluster_name=self.cluster_name, task_arn=self.task_arn,log_status=True)
        #with Catch():
        #    #pprint(self.ecs.tasks(cluster_name=self.cluster_name))
        #    pprint(self.ecs.tasks(cluster_name=self.cluster_name))

    def test_task_logs(self):
        task_definition      = self.ecs.task_definition(task_definition_arn=self.task_definition_arn)
        task                 = self.ecs.task_details(cluster_name=self.cluster_name, task_arn=self.task_arn)
        task_arn             = task.get('taskArn')
        task_id              = task_arn.split('/').pop()
        container_definition = task_definition.get('containerDefinitions')[0]
        log_configuration    = container_definition.get('logConfiguration')
        image_name           = container_definition.get('name')

        log_group_name     = log_configuration.get('options').get('awslogs-group')
        log_stream_prefix  = log_configuration.get('options').get('awslogs-stream-prefix')
        #pprint(log_configuration)
        logs = Cloud_Watch_Logs()
        #pprint(logs.log_streams(log_group_name=log_group_name, log_stream_name_prefix=log_stream_prefix))
        log_stream_name = f'{log_stream_prefix}/{image_name}/{task_id}'
        #pprint(log_stream)
        print()
        print(logs.log_events(log_group_name=log_group_name,log_stream_name=log_stream_name))

