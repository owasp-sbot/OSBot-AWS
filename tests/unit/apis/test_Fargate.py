import sys ;

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
    def setUp(self):
        STS().check_current_session_credentials()
        self.ecs = ECS()
        self.cluster_name = 'test_ecs_cluster_2'
        self.cluster_arn  = self.ecs.cluster_arn(self.cluster_name)

    def test__init__(self):
        assert type(self.ecs.client()).__name__ == 'ECS'

    def test_cluster_create(self):

        cluster     = self.ecs.cluster_create(self.cluster_name)
        assert cluster.get('clusterArn'       ) == self.cluster_arn
        assert cluster.get('clusterName'      ) == self.cluster_name
        assert cluster.get('runningTasksCount')==0
        assert self.cluster_arn in self.ecs.clusters_arns()

        pprint(cluster)

    def test_cluster_delete(self):
        result = self.ecs.cluster_delete(self.cluster_name)
        Dev.pprint(result)
        pprint(self.ecs.clusters())

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

    def test_task_create(self):
        image_name          = 'test_task_create'
        task_name           = 'test_task_create'
        task_role_name      = f'{task_name}_task_role'
        execution_role_name = f'{task_name}_execution_role'
        task_role_iam       = self.ecs.policy_create_for_task_role     (task_role_name     )
        execution_role_iam  = self.ecs.policy_create_for_execution_role(execution_role_name)
        task_role_arn       = task_role_iam     .arn()
        execution_role_arn  = execution_role_iam.arn()

        assert task_role_iam     .exists() is True
        assert execution_role_iam.exists() is True
        pprint('task_role_arn'     , task_role_arn      )
        pprint('execution_role_arn', execution_role_arn )

        result = self.ecs.task_create(image_name, task_name, task_role_arn,execution_role_arn)
        task_arn = result.get('taskDefinitionArn')

        print()
        pprint(task_arn)
        print('********')
        pprint(result)


        #self.fargate.task_delete(task_arn)  # delete it
        #print(Misc.word_wrap(result,60))

    def test_task_delete(self):
        tasks  = self.ecs.tasks()
        for task in tasks:
            if 'family_created_via' in task:
                Dev.pprint('deleting task: {0}'.format(task))
                self.ecs.task_delete(task)

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

    def test_task_details(self):
        task_id ='9400bb6b-f76f-4bce-b35d-5a4b15e79bfd'
        cluster = 'FargateCluster'
        tast_arn = 'arn:aws:ecs:eu-west-2:244560807427:task/{0}'.format(task_id)

        result = self.ecs.task_details(cluster, tast_arn)
        Dev.pprint(result)
        Dev.pprint(result.get('lastStatus'))
        Dev.pprint(result.get('containers'))


    def test_tasks(self):
        result = self.ecs.tasks()
        Dev.pprint(result)
        assert len(result) > 1
        assert ':task-definition/' in result[0]


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