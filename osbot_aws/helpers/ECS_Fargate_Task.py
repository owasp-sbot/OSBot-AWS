from osbot_aws.apis.Cloud_Watch_Logs import Cloud_Watch_Logs
from osbot_utils.decorators.lists.index_by import index_by

from osbot_aws.AWS_Config import AWS_Config
from osbot_aws.apis.EC2 import EC2

from osbot_aws.apis.ECS import ECS
from osbot_aws.apis.STS import STS


class ECS_Fargate_Task:

    def __init__(self, cluster_name, image_name, subnet_id=None, security_group_id=None):
        self.ecs                = ECS()
        self.ec2                = EC2()
        self.cloud_watch_logs   = Cloud_Watch_Logs()
        self.aws_config         = AWS_Config()                                         # load config from env variables
        self.account_id         = self.cloud_watch_logs.account_id
        self.region_name        = self.cloud_watch_logs.region_name
        self.cluster_name       = cluster_name
        self.image_name         = image_name
        self.subnet_id          = subnet_id
        self.security_group_id  = security_group_id
        self.task_family        = f"family__{self.image_name}"
        self.task_name          = f'task__{self.cluster_name}'
        self.iam_execution_role = f'fargate-execution-role_{self.region_name}_{self.task_family}'
        self.iam_task_role      = f'fargate-task-role_{self.region_name}_{self.task_family}'
        self.task_arn           = None

    # helper methods
    def cluster_arn(self):
        return self.ecs.cluster_arn(cluster_name=self.cluster_name)

    def delete_all(self):
        return self.ecs.task_definitions_arns(task_family=self.task_family)
        pass

    def setup(self):
        self.setup_cluster()
        self.setup_task_definition()
        return self

    def setup_cluster(self):
        self.ecs.cluster_create                  (cluster_name = self.cluster_name      )
        self.ecs.policy_create_for_task_role     (role_name    = self.iam_task_role     )
        self.ecs.policy_create_for_execution_role(role_name    = self.iam_execution_role)

    def setup_task_definition(self):
        task_definition_arn = self.task_definition_arn()
        if self.ecs.task_definition_exists(task_definition_arn=task_definition_arn):
            return {}                                                                   # todo: find better return value and pattern for this workflow
        task_definition_config = self.ecs.task_definition_setup (task_family=self.task_family,image_name=self.image_name)
        task_definition        = self.ecs.task_definition_create(task_definition_config=task_definition_config)
        return { "task_definition_config": task_definition_config, "task_definition": task_definition }

    def task_config(self):
        task_config = { "cluster_name"          : self.cluster_name                                                          ,
                        "security_group_id"     : self.security_group_id or self.ec2.security_group_default().get('GroupId' ),
                        "subnet_id"             : self.subnet_id         or self.ec2.subnet_default_for_az ().get('SubnetId'),
                        "task_definition_arn"   : self.task_definition_arn()                                                 }

        return task_config

    def task_definition(self):
        return self.ecs.task_definition_latest(task_family=self.task_family)

    def task_definition_arn(self):
        return self.task_definition().get('taskDefinitionArn')

    # main methods

    def create(self, task_config=None):
        if task_config is None:
            task_config = self.task_config()

        task          = self.ecs.task_create(**task_config)
        self.task_arn = task.get('taskArn')

        return task

    def container(self):
        return self.containers(index_by='name').get(self.image_name)

    def container_definition(self):
       return self.containers_definitions(index_by='name').get(self.image_name)

    @index_by
    def containers(self):
        return self.info().get('containers')

    @index_by
    def containers_definitions(self):
        return self.task_definition().get('containerDefinitions')

    def info(self):
        return self.ecs.task(cluster_name=self.cluster_name, task_arn=self.task_arn)

    def log_stream_config(self):
        task                 = self.ecs.task(cluster_name=self.cluster_name, task_arn=self.task_arn)
        task_arn             = task.get('taskArn')
        task_id              = task_arn.split('/').pop()
        container_definition = self.container_definition()
        log_configuration    = container_definition.get('logConfiguration')
        image_name           = container_definition.get('name')
        log_group_name       = log_configuration.get('options').get('awslogs-group')
        log_stream_prefix    = log_configuration.get('options').get('awslogs-stream-prefix')
        log_stream_name      = f'{log_stream_prefix}/{image_name}/{task_id}'
        config               = {"log_group_name" : log_group_name  ,
                                "log_stream_name": log_stream_name }
        return config

    def log_stream_exists(self):
        config          = self.log_stream_config()
        log_group_name  = config.get('log_group_name')
        log_stream_name = config.get('log_stream_name')
        return self.cloud_watch_logs.log_stream_exists(log_group_name=log_group_name, log_stream_name=log_stream_name)

    def logs(self):
        log_stream_config = self.log_stream_config()
        log_group_name    = log_stream_config.get('log_group_name')
        log_stream_name   = log_stream_config.get('log_stream_name')
        return self.cloud_watch_logs.log_events(log_group_name=log_group_name, log_stream_name=log_stream_name)

    def status(self):
        return self.info().get('lastStatus')

    def wait_for_task_running(self):
        return self.ecs.wait_for_tasks_running(cluster_name=self.cluster_name, task_arn=self.task_arn)

    def wait_for_task_stopped(self):
        return self.ecs.wait_for_tasks_stopped(cluster_name=self.cluster_name, task_arn=self.task_arn)