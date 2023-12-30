from osbot_aws.apis.Cloud_Watch_Logs import Cloud_Watch_Logs
from osbot_aws.aws.ecs.ECS           import ECS


class ECS_Actions:

    def __init__(self):
        self.ecs          = ECS()
        self.logs         = Cloud_Watch_Logs()
        self.account_id   = self.ecs.account_id
        self.region       = self.ecs.region
        self.cluster_name = 'test_ecs_cluster_2'
        self.task_family  = 'test_task_create'
        self.cluster_arn  = self.ecs.cluster_arn(self.cluster_name)

    def create_cluster(self):
        return self.ecs.cluster_create(self.cluster_name)

    def delete_cluster(self):
        return self.ecs.cluster_delete(self.cluster_arn)

    def info_cluster(self):
        return self.ecs.clusters()
