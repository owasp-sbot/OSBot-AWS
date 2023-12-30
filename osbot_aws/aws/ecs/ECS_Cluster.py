from osbot_utils.utils.Misc import random_string

from osbot_aws.aws.ecs.ECS import ECS


class ECS_Cluster:
    def __init__(self, cluster_name=None):
        self.ecs          = ECS()
        self.cluster_name = cluster_name or random_string(prefix='test_ecs_cluster')