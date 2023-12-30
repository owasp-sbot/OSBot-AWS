import os
from unittest import TestCase

from osbot_utils.utils.Dev import pprint

from osbot_aws.apis.STS import STS
from osbot_aws.aws.ecs.ECS import ECS
from osbot_aws.aws.ecs.ECS_Cluster import ECS_Cluster


class test_ECS_Cluster(TestCase):

    def setUp(self):
        self.ecs_cluster = ECS_Cluster()

    def test__init__(self):
        assert type(self.ecs_cluster.ecs) is ECS
        assert self.ecs_cluster.cluster_name.startswith('test_ecs_cluster_')