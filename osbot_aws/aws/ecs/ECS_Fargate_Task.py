from osbot_aws.apis.Cloud_Watch_Logs        import Cloud_Watch_Logs
from osbot_utils.decorators.lists.index_by  import index_by
from osbot_aws.AWS_Config                   import AWS_Config
from osbot_aws.aws.ec2.EC2                  import EC2
from osbot_aws.aws.ecs.ECS                  import ECS
from osbot_aws.aws.iam.IAM                  import IAM


class ECS_Fargate_Task:

    def __init__(self, cluster_name, image_name, subnet_id=None, security_group_id=None):
        self.ecs                   = ECS()
        self.ec2                   = EC2()
        self.cloud_watch_logs      = Cloud_Watch_Logs()
        self.aws_config            = AWS_Config()                                         # load config from env variables
        self.account_id            = self.cloud_watch_logs.account_id
        self.region_name           = self.cloud_watch_logs.region_name
        self.cluster_name          = cluster_name
        self.image_name            = image_name
        self.subnet_id             = subnet_id
        self.security_group_id     = security_group_id
        self.task_family           = f"family__{self.image_name}"
        self.task_name             = f'task__{self.cluster_name}'
        self.launch_type           = 'FARGATE'
        #self.iam_execution_role = f'fargate-execution-role_{self.region_name}_{self.task_family}'
        #self.iam_task_role      = f'fargate-task-role_{self.region_name}_{self.task_family}'
        self.task_arn              = None
        self.constraint_expression = None

    # helper methods
    def cluster_arn(self):
        return self.ecs.cluster_arn(cluster_name=self.cluster_name)

    def delete_cluster_task_definition_tasks_roles(self):
        # stop task
        self.stop()
        self.wait_for_task_stopped()

        # delete task_definitions
        task_definitions_arns = self.ecs.task_definitions_arns(task_family=self.task_family)
        for task_definition_arn in task_definitions_arns:
            self.ecs.task_definition_delete(task_definition_arn=task_definition_arn)


        # delete roles
        task_definition_config = self.ecs.task_definition_setup(task_family=self.task_family, image_name=self.image_name)
        execution_role_name    = task_definition_config.get('execution_role_name')
        task_role_name         = task_definition_config.get('task_role_name')
        IAM(role_name=execution_role_name).role_delete()
        IAM(role_name=task_role_name     ).role_delete()

        # delete cluster
        self.ecs.cluster_delete(cluster_arn=self.cluster_arn())

    def setup(self):
        self.setup_cluster()
        self.setup_task_definition()
        return self

    def setup_cluster(self):
        self.ecs.cluster_create                  (cluster_name = self.cluster_name      )
        #self.ecs.policy_create_for_task_role     (role_name    = self.iam_task_role     )
        #self.ecs.policy_create_for_execution_role(role_name    = self.iam_execution_role)

    def setup_task_definition(self):
        task_definition_arn = self.task_definition_arn()

        if self.ecs.task_definition_exists(task_definition_arn=task_definition_arn):
            return {}                                                                   # todo: find better return value and pattern for this workflow
        task_definition_config = self.ecs.task_definition_setup(task_family=self.task_family,image_name=self.image_name)
        task_definition        = self.ecs.task_definition_create(task_definition_config=task_definition_config)
        return { "task_definition_config": task_definition_config, "task_definition": task_definition }

    def stop(self):
        return self.ecs.task_stop(cluster_name=self.cluster_name, task_arn=self.task_arn)

    def task_config(self):
        task_config = { "cluster_name"          : self.cluster_name                                                          ,
                        "security_group_id"     : self.security_group_id or self.ec2.security_group_default().get('GroupId' ),
                        "subnet_id"             : self.subnet_id         or self.ec2.subnet_default_for_az ().get('SubnetId'),
                        "task_definition_arn"   : self.task_definition_arn()                                                 ,
                        "launch_type"           : self.launch_type                                                           ,
                        'constraint_expression' : self.constraint_expression                                                 }

        return task_config

    def task_definition(self):
        return self.ecs.task_definition(task_family=self.task_family)

    def task_definition_arn(self):
        return self.task_definition().get('taskDefinitionArn')

    # main methods

    def create(self, task_config=None):
        if task_config is None:
            task_config = self.task_config()

        task          = self.ecs.task_create(**task_config)
        self.task_arn = task.get('taskArn')

        return task                                                                     # return status_ok and capture potential error

    def container(self):
        return self.ecs.container(task_arn=self.task_arn , image_name=self.image_name, cluster_name=self.cluster_name)

    def container_definition(self):
       return self.ecs.container_definition(task_definition_arn=self.task_definition_arn, image_name=self.image_name)

    @index_by
    def containers(self):
        return self.ecs.containers(task_arn=self.task_arn ,cluster_name=self.cluster_name)

    @index_by
    def containers_definitions(self):
        return self.ecs.containers_definitions(task_definition_arn=self.task_definition_arn)

    def info(self):
        return self.ecs.task(cluster_name=self.cluster_name, task_arn=self.task_arn)

    def log_stream_config(self):
        return self.ecs.log_stream_config(task_arn=self.task_arn, task_definition_arn=self.task_definition_arn(), image_name=self.image_name, cluster_name=self.cluster_name)

    def log_stream_exists(self):
        return self.ecs.log_stream_exists(task_arn=self.task_arn, task_definition_arn=self.task_definition_arn(), image_name=self.image_name, cluster_name=self.cluster_name)

    def logs(self):
        return self.ecs.logs(task_arn=self.task_arn, task_definition_arn=self.task_definition_arn(), image_name=self.image_name, cluster_name=self.cluster_name)

    def logs_wait_for_data(self, max_attempts=60 ,sleep_for=1):
        return self.ecs.logs_wait_for_data(task_arn=self.task_arn, task_definition_arn=self.task_definition_arn(), image_name=self.image_name, cluster_name=self.cluster_name,max_attempts=max_attempts ,sleep_for=sleep_for)

    def status(self):
        return self.info().get('lastStatus')

    def wait_for_task_running(self):
        return self.ecs.wait_for_task_running(cluster_name=self.cluster_name, task_arn=self.task_arn)

    def wait_for_task_stopped(self):
        return self.ecs.wait_for_task_stopped(cluster_name=self.cluster_name, task_arn=self.task_arn)