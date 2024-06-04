import pytest
from unittest               import TestCase
from osbot_aws.aws.ec2.EC2  import EC2
from osbot_utils.utils.Dev  import pprint
from osbot_aws.aws.ecs.ECS  import ECS


@pytest.mark.skip('Wire up tests')
class test_ECS_Tasks(TestCase):

    def setUp(self) -> None:
        self.ecs = ECS()
        self.ec2 = EC2()

    def test_setup_and_run_containers_in_ec2(self):
        container_instance = self.ecs.container_instances().pop()
        subnet_id          = container_instance.get('attributes').get('ecs.subnet-id')
        security_group_id  = self.ec2.security_group_default().get('GroupId' )

        task_family     = 'hello-world-in-ec2'
        image_name      = 'hello-world'
        skip_if_exists  = True
        task_definition_config = self.ecs.task_definition_setup(task_family=task_family,image_name=image_name, requires='EC2', network_mode='none')
        task_definition        = self.ecs.task_definition_create(task_definition_config=task_definition_config, skip_if_exists=skip_if_exists)
        task_definition_arn    = task_definition.get('taskDefinitionArn')

        # task_config = { "launch_type"           : "EC2"               ,
        #                 "security_group_id"     : security_group_id   ,
        #                 "subnet_id"             : subnet_id           ,
        #                 "task_definition_arn"   : task_definition_arn }
        #task = self.ecs.task_create(**task_config)
        pprint(task_definition_arn)
        task     = self.ecs.task_create_ec2(task_definition_arn=task_definition_arn)
        task_arn = task.get('taskArn')
        self.ecs.wait_for_task_stopped(task_arn=task_arn)
        pprint(self.ecs.logs(task_arn=task_arn, task_definition_arn=task_definition_arn, image_name=image_name))

    def test_run_containers_in_ec2(self):
        print()
        image_name          = 'hello-world'
        task_definition_arn = 'arn:aws:ecs:eu-west-1:785217600689:task-definition/hello-world-in-ec2:3'
        for j in range(0, 2):
            for i in range(0,12):
                result = self.ecs.task_create_ec2(task_definition_arn=task_definition_arn)
                failures = len(result.get('failures'))
                ok       = len(result.get('tasks'))
                print(f'************** {j} {i} ok: {ok} failures: {failures}')

        return
        task_arn = task.get('taskArn')
        #self.ecs.wait_for_task_stopped(task_arn=task_arn)
        logs     = self.ecs.logs_wait_for_data(task_arn=task_arn, task_definition_arn=task_definition_arn, image_name=image_name)
        pprint(logs)

    def test_start_container_in_ec2__in_default_cluster(self):
        ecs                 = self.ecs
        task_family         = 'testing-ec2'
        task_definition     = ecs.task_definition(task_family=task_family)
        task_definition_arn = task_definition.get('taskDefinitionArn')
        task                = ecs.task_create_ec2(task_definition_arn=task_definition_arn)
        task_arn            = task.get('taskArn')
        ecs.wait_for_task_stopped(task_arn=task_arn)
        pprint(task_arn)