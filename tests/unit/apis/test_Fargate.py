import sys ; sys.path.append('..')
import unittest

from unittest import TestCase
from pbx_gs_python_utils.utils.Dev import Dev
from pbx_gs_python_utils.utils.Misc import Misc
from osbot_aws.apis.Fargate import Fargate

@unittest.skip("Needs test that create and destroy the test data")
class test_Fargate(TestCase):
    def setUp(self):
        self.fargate = Fargate(account_id='244560807427')

    def test__init__(self):
        assert type(self.fargate.ecs).__name__ == 'ECS'

    # def test_cluster_delete(self):
    #     clusters_arns = self.fargate.clusters()
    #     result = self.fargate.cluster_delete(clusters_arns[0])
    #     Dev.pprint(result)

    def test_clusters(self):
        result = self.fargate.clusters()
        if len(result) > 0:
            assert 'arn:aws:ecs:' in result[0]

    def test_policy_create_for_task_role(self):
        self.fargate.policy_create_for_task_role('task_role_create_and_run_task')

    def test_policy_create_for_execution_role(self):
        self.fargate.policy_create_for_execution_role('task_execution_role_create_and_run_task')

    # def test_task_create(self):
    #     task_role_arn      = 'aaa'
    #     execution_role_arn = 'bbb'
    #     result = self.fargate.task_create(task_role_arn,execution_role_arn)
    #     task_arn = result.get('taskDefinitionArn')
    #     print()
    #     print(task_arn)

        #self.fargate.task_delete(task_arn)  # delete it
        #print(Misc.word_wrap(result,60))

    def test_task_delete(self):
        tasks  = self.fargate.tasks()
        for task in tasks:
            if 'family_created_via' in task:
                Dev.pprint('deleting task: {0}'.format(task))
                self.fargate.task_delete(task)

    def test_task_run(self):
        # ec2 = Ec2()
        cluster           = 'FargateCluster'
        subnet_id = ' subnet-49391932'
        security_group_id = 'sg-e6ea548e'

        task_name = 'create_and_run_task:44'
        task_arn = 'arn:aws:ecs:eu-west-2:244560807427:task-definition/{0}'.format(task_name)

        task_run_arn = self.fargate.task_run(cluster,task_arn, subnet_id, security_group_id).get('taskArn')

        task_details = self.fargate.task_wait_for_completion(cluster, task_run_arn, sleep_for=1, log_status = True)
        Dev.pprint(task_details)

    def test_task_details(self):
        task_id ='9400bb6b-f76f-4bce-b35d-5a4b15e79bfd'
        cluster = 'FargateCluster'
        tast_arn = 'arn:aws:ecs:eu-west-2:244560807427:task/{0}'.format(task_id)

        result = self.fargate.task_details(cluster, tast_arn)
        Dev.pprint(result)
        Dev.pprint(result.get('lastStatus'))
        Dev.pprint(result.get('containers'))


    def test_tasks(self):
        result = self.fargate.tasks()
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
        self.fargate.cluster_create(cluster_name)

        # Create Roles
        self.fargate.policy_create_for_task_role(task_role)
        self.fargate.policy_create_for_execution_role(execution_role)

        #Create Task
        task_arn     = self.fargate.task_create(task_name, task_role, execution_role).get('taskDefinitionArn')

        # Run Task
        task_run = self.fargate.task_run(cluster_name, task_arn, subnet_id, security_group_id)
        task_run_arn = task_run.get('taskArn')
        task_details = self.fargate.task_wait_for_completion(cluster_name, task_run_arn)

        task_id = 'asd'
        # Get logs

        #group_name  = 'awslogs-temp_task_on_temp_cluster_X29B3K'
        #stream_name = 'awslogs-example/gs-docker-codebuild/f8ccf213-b642-466c-8458-86af9933eca9'
        stream_name = "{0}/{1}{2}".format(log_group_stream_prefix,docker_image_name,task_id)

        messages = self.cloud_watch.logs_get_messages(log_group_name, stream_name)
        # Print details
        Dev.pprint(messages)