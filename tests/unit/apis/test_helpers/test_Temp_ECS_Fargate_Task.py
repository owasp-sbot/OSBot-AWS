from unittest import TestCase

from osbot_aws.apis.test_helpers.Temp_ECS_Fargate_Task import Temp_ECS_Fargate_Task
from osbot_utils.testing.Duration import Duration
from osbot_utils.utils.Dev import pprint

#ami-0c15700b4e6bf474e - amzn2-ami-ecs-hvm-2.0.20210202-x86_64-ebs  (from https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs-optimized_AMI.html)
class test_Temp_ECS_Fargate_Task(TestCase):

    def test__enter__leave__(self):
        image_name   = 'hello-world'

        with Temp_ECS_Fargate_Task(image_name=image_name, delete_on_exit=True) as fargate_task:
            pprint(fargate_task.create())
            assert 'Hello from Docker!\n' in fargate_task.logs_wait_for_data()