from botocore.exceptions                    import ClientError

from osbot_utils.utils.Dev import pprint
from osbot_utils.utils.Lists import list_get

from osbot_aws.AWS_Config                   import AWS_Config
from osbot_utils.decorators.lists.group_by  import group_by
from osbot_aws.apis.Cloud_Watch_Logs        import Cloud_Watch_Logs
from osbot_utils.decorators.lists.index_by  import index_by
from osbot_utils.decorators.methods.cache   import cache
from osbot_aws.apis.Session                 import Session
from osbot_utils.utils.Misc                 import wait

from osbot_aws.aws.iam.IAM_Role import IAM_Role
from osbot_aws.aws.sts.STS import STS

# todo: find good solution to capture/manage these config values (See also values in EC2 class)
ECS_WAITER_DELAY        = 1             # default was 6 seconds
ECS_WAITER_MAX_ATTEMPTS = 600           # default was 100 times

class ECS:

    def __init__(self):
        self.aws_config = AWS_Config()
        self.account_id = self.aws_config.aws_session_account_id()
        self.region     = self.aws_config.aws_session_region_name()

    def __enter__(self                           ): return self
    def __exit__ (self, exc_type, exc_val, exc_tb): pass

    @cache
    def client(self):
        return Session().client('ecs')

    @cache
    def sts(self):
        return STS()

    @cache
    def cloud_watch_logs(self):
        return Cloud_Watch_Logs()

    @index_by
    def cluster(self, cluster_arn=None):
        if cluster_arn is None:
            cluster_arn = self.cluster_arn()
        result = self.clusters(clusters_arns=[cluster_arn])
        if len(result) == 1:
            return result[0]

    def cluster_arn(self, cluster_name='default'):
        return f'arn:aws:ecs:{self.region}:{self.account_id}:cluster/{cluster_name}'

    def cluster_create(self, cluster_name):
        cluster_arn = self.cluster_arn(cluster_name=cluster_name)
        if self.cluster_exists(cluster_arn):
            return self.cluster(cluster_arn)
        else:
            response = self.client().create_cluster(clusterName=cluster_name)
            return response.get('cluster')
        
    def cluster_delete(self, cluster_arn):
        response = self.client().delete_cluster(cluster=cluster_arn)
        return response.get('cluster')

    def cluster_exists(self, cluster_arn):
        cluster = self.cluster(cluster_arn=cluster_arn)
        if cluster and cluster.get('status') == 'ACTIVE':       # threat inactive cluster as non existent
            return True
        return False

    @index_by
    def clusters(self, clusters_arns=None):
        include         = [ 'ATTACHMENTS' , 'SETTINGS' , 'STATISTICS' , 'TAGS']
        target_clusters = clusters_arns or self.clusters_arns()
        return self.client().describe_clusters(clusters=target_clusters, include=include).get('clusters')

    def clusters_arns(self):
        return self.client().list_clusters().get('clusterArns')

    def container(self, task_arn, image_name, cluster_name='default'):
        return self.containers(task_arn=task_arn, cluster_name=cluster_name, index_by='name').get(image_name)

    def container_definition(self, task_definition_arn, image_name):
       return self.containers_definitions(task_definition_arn=task_definition_arn, index_by='name').get(image_name)

    @index_by
    def containers(self, task_arn, cluster_name='default'):
        return self.task(cluster_name=cluster_name, task_arn=task_arn).get('containers')

    @index_by
    def containers_definitions(self,task_definition_arn):
        return self.task_definition(task_definition_arn=task_definition_arn).get('containerDefinitions')

    @index_by
    @group_by
    def container_instances(self, cluster_name='default', instance_status='ACTIVE'):
        container_instances_arns = self.container_instances_arns(cluster_name=cluster_name, instance_status=instance_status)
        kwargs = { "cluster"            : cluster_name             ,
                   "containerInstances" : container_instances_arns }

        container_instances = self.client().describe_container_instances(**kwargs).get('containerInstances')
        # fix container_instance.get('attributes') since they are not in easy to consume key:value pairs
        for container_instance in container_instances:
            attributes_original = container_instance.get('attributes')
            attributes          = {}
            for attribute in attributes_original:
                key   = attribute.get('name')
                value = attribute.get('value')
                attributes[key] = value
            container_instance['attributes'] = attributes

        return container_instances

    def container_instances_arns(self, cluster_name='default', instance_status='ACTIVE'):
        kwargs = { "cluster": cluster_name }
        if instance_status:
            kwargs["status"] = instance_status

        return self.client().list_container_instances(**kwargs).get('containerInstanceArns')

    def log_stream_config(self, task_arn, task_definition_arn, image_name, cluster_name='default'):
        task                 = self.task(cluster_name=cluster_name, task_arn=task_arn)
        task_arn             = task.get('taskArn')
        task_id              = task_arn.split('/').pop()
        container_definition = self.container_definition(task_definition_arn=task_definition_arn, image_name=image_name)
        log_configuration    = container_definition.get('logConfiguration')
        #image_name           = container_definition.get('name')
        log_group_name       = log_configuration.get('options').get('awslogs-group')
        log_stream_prefix    = log_configuration.get('options').get('awslogs-stream-prefix')
        log_stream_name      = f'{log_stream_prefix}/{image_name}/{task_id}'
        config               = {"log_group_name" : log_group_name  ,
                                "log_stream_name": log_stream_name }
        return config

    def log_stream_exists(self, task_arn, task_definition_arn, image_name, cluster_name='default'):
        config          = self.log_stream_config(task_arn=task_arn, task_definition_arn=task_definition_arn, image_name=image_name, cluster_name=cluster_name)
        log_group_name  = config.get('log_group_name')
        log_stream_name = config.get('log_stream_name')
        return self.cloud_watch_logs().log_stream_exists(log_group_name=log_group_name, log_stream_name=log_stream_name)

    def logs(self, task_arn, task_definition_arn, image_name, cluster_name='default'):
        log_stream_config = self.log_stream_config(task_arn=task_arn, task_definition_arn=task_definition_arn, image_name=image_name, cluster_name=cluster_name)
        log_group_name    = log_stream_config.get('log_group_name')
        log_stream_name   = log_stream_config.get('log_stream_name')
        return self.cloud_watch_logs().log_events(log_group_name=log_group_name, log_stream_name=log_stream_name)

    def logs_wait_for_data(self, task_arn, task_definition_arn, image_name, cluster_name='default',max_attempts=60 ,sleep_for=1):
        for i in range(0, max_attempts):                                                                                                    # for max_attempts
            logs = self.logs(task_arn=task_arn,task_definition_arn=task_definition_arn,image_name=image_name,cluster_name=cluster_name)     # get logs (returns '' if cloud trail doesn't exist or has no data)
            if logs:                                                                                                                        # if there is data
                return logs                                                                                                                 # return it
            wait(sleep_for)                                                                                                                 # if not, wait for sleep_for amount

    def task_definition(self, task_definition_arn=None, task_family=None):
        try:
            if task_definition_arn is None:
                task_definition_arn = task_family
            if task_definition_arn:
                result          = self.client().describe_task_definition(taskDefinition=task_definition_arn)
                task_definition = result.get('taskDefinition')
                if task_definition and task_definition.get('status') == 'ACTIVE':       # threat inactive task definitions as non existent (to address AWS weird bug of not allowing task definitions to be deleted)
                    return task_definition
        except ClientError as e:
            if e.response.get('Error', {}).get('Message') != 'Unable to describe task definition.':
                raise
        return {}


    def task_definition_arn(self, task_family, revision):
        return f'arn:aws:ecs:{self.region}:{self.account_id}:task-definition/{task_family}:{revision}'

    def task_definition_create(self, task_definition_config, skip_if_exists=True):
        cpu                 = task_definition_config.get('cpu'                )
        execution_role_name = task_definition_config.get('execution_role_name')
        log_group_name      = task_definition_config.get('log_group_name'     )
        log_stream_name     = task_definition_config.get('log_stream_name'    )
        image_name          = task_definition_config.get('image_name'         )
        memory              = task_definition_config.get('memory'             )
        network_mode        = task_definition_config.get('network_mode'       )
        task_family         = task_definition_config.get('task_family'        )
        task_role_name      = task_definition_config.get('task_role_name'     )
        requires            = task_definition_config.get('requires'           )

        if skip_if_exists and self.task_definition_exists(task_family=task_family):
            return self.task_definition(task_family=task_family)

        # create policies if needed
        iam_task_role       = self.policy_create_for_task_role(task_role_name)
        iam_execution_role  = self.policy_create_for_execution_role(execution_role_name)
        task_role_arn       = iam_task_role.arn()
        execution_role_arn  = iam_execution_role.arn()

        self.cloud_watch_logs().log_stream_create(log_group_name=log_group_name, log_stream_name=log_stream_name)

        kwargs = { 'family'              : task_family           ,
                   'taskRoleArn'         : task_role_arn         ,
                   'executionRoleArn'    : execution_role_arn    ,
                   'cpu'                 : cpu                   ,
                   'memory'              : memory                ,
                   'networkMode'         : network_mode          ,
                   "containerDefinitions": [ { 'name'            : image_name,
                                               'image'           : f'{self.account_id}.dkr.ecr.{self.region}.amazonaws.com/{image_name}' ,
                                               "logConfiguration": {   "logDriver": "awslogs",
                                                                       "options"  : {  "awslogs-group"        : log_group_name,
                                                                                       "awslogs-region"       : self.region,
                                                                                       "awslogs-stream-prefix": log_stream_name }}, }],
                   "requiresCompatibilities": [ requires] }


        return self.client().register_task_definition(**kwargs).get('taskDefinition')

    def task_definition_delete(self, task_definition_arn):
        result = self.client().deregister_task_definition(taskDefinition=task_definition_arn)
        return result.get('taskDefinition').get('status') == 'INACTIVE'

    def task_definition_exists(self, task_definition_arn=None, task_family=None):
        return self.task_definition(task_definition_arn=task_definition_arn,task_family=task_family) != {}

    def task_definition_not_exists(self, task_definition_arn):
        return self. task_definition_exists(task_definition_arn=task_definition_arn) is False

    def task_definition_setup(self, task_family, image_name, cpu='256', memory='512', network_mode='awsvpc', requires='FARGATE'):
        task_role_name      = f'ecs-role-task__{self.region}__{task_family}'
        execution_role_name = f'ecs-role-execution__{self.region}__{task_family}'
        log_group_name      = f'ecs-task-on-{image_name}'

        return { 'cpu'                : cpu                  ,
                 'image_name'         : image_name           ,
                 'log_group_name'     : log_group_name       ,
                 'log_stream_name'    : task_family          ,
                 'memory'             : memory               ,
                 'execution_role_name': execution_role_name  ,
                 'network_mode'       : network_mode         ,
                 'requires'           : requires             ,
                 'task_family'        : task_family          ,
                 'task_role_name'     : task_role_name       }

    @index_by
    @group_by
    def task_definitions(self, task_family):
        data = []
        task_definitions_arns = self.task_definitions_arns(task_family)
        for task_definition_arn in task_definitions_arns:
            data.append(self.task_definition(task_definition_arn=task_definition_arn))
        return data

    def task_definitions_arns(self, task_family,status='ACTIVE'):
        kwargs = { 'familyPrefix': task_family ,
                    'status'     : status      }

        return self.client().list_task_definitions(**kwargs).get('taskDefinitionArns')

    def task(self, cluster_name, task_arn):
        result = self.client().describe_tasks(cluster=cluster_name, tasks=[task_arn]).get('tasks')
        return list_get(result,0)

    def task_create(self, task_definition_arn, subnet_id, security_group_id, cluster_name='default', launch_type='FARGATE', assign_public_ip='ENABLED', constraint_expression=None):

        kwargs = {
                    'cluster'             : cluster_name         ,
                    'taskDefinition'      : task_definition_arn  ,
                    'launchType'          : launch_type          ,
                    #'networkConfiguration': network_configuration,
                 }
        if launch_type != 'EXTERNAL':
            network_configuration          = {'awsvpcConfiguration': {'subnets': [subnet_id],
                                                                      'securityGroups': [security_group_id],
                                                                      'assignPublicIp': assign_public_ip}}
            kwargs['networkConfiguration'] = network_configuration
        if constraint_expression:
            kwargs['placementConstraints'] = [
                {
                    'type': 'memberOf',
                    'expression': constraint_expression
                }
            ]
        result = self.client().run_task(**kwargs)
        return result.get('tasks')[0]

    def task_create_ec2(self, task_definition_arn):
        kwargs = {"taskDefinition" : task_definition_arn ,
                  "launchType"     : "EC2"               ,
                  "count"          : 1                   }                                           # only create one instance

        result = self.client().run_task(**kwargs)
        return result
        #return result.get('tasks')[0]

    def task_exists(self, cluster_name, task_arn):
        return self.task(cluster_name=cluster_name, task_arn=task_arn) is not None

    def task_stop(self, cluster_name, task_arn):
        kwargs = {'cluster': cluster_name,
                  'task'   : task_arn    }

        return self.client().stop_task(**kwargs).get('taskDefinitionArns')

    # def task_wait_for_completion(self, task_arn, cluster_name='default', sleep_for=1, max_attempts=30, log_status=False):  # todo: replace with waiters that
    #     build_info = ''
    #     for i in range(0,max_attempts):
    #         build_info    = self.task(cluster_name=cluster_name, task_arn=task_arn)
    #         last_Status  = build_info.get('lastStatus')
    #         #current_phase = build_info.get('currentPhase')
    #         if log_status:
    #             Dev.pprint("[{0}] {1}".format(i,last_Status))
    #         if last_Status == 'DEPROVISIONING' or last_Status == 'STOPPED':
    #             return build_info
    #         sleep(sleep_for)
    #     return build_info

    @index_by
    @group_by
    def tasks(self, cluster_name, task_arns=None):
        if task_arns is None:
            task_arns = self.tasks_arns(cluster_name=cluster_name)
        kwargs = {"cluster": cluster_name,
                  "tasks"  : task_arns}
        return self.client().describe_tasks(**kwargs).get('tasks')

    def tasks_arns(self,cluster_name='default', task_family=None):
        all_tasks_arns= []
        all_tasks_arns.extend(self.tasks_arns_on_status(cluster_name=cluster_name, task_family=task_family, status= 'RUNNING'))
        all_tasks_arns.extend(self.tasks_arns_on_status(cluster_name=cluster_name, task_family=task_family, status= 'STOPPED'))
        return all_tasks_arns

    def tasks_arns_on_status(self, cluster_name, task_family=None, status='RUNNING'):
        kwargs = { "cluster"      : cluster_name,
                   'desiredStatus': status     }
        if task_family:
            kwargs['family'] = task_family
        return self.client().list_tasks(**kwargs).get('taskArns')

    def policy_create_for_task_role(self, role_name, skip_if_exists=True):
        policy = { "Version"    : "2008-10-17",
                   "Statement"  : [ { "Effect": "Allow",
                                      "Principal": { "Service": "ecs-tasks.amazonaws.com"},
                                      "Action": "sts:AssumeRole" }]}
        iam_role = IAM_Role(role_name=role_name)
        iam_role.create(policy,skip_if_exists=skip_if_exists)
        return iam_role


    def policy_create_for_execution_role(self, role_name, skip_if_exists=True):
        #cloud_watch_arn = "arn:aws:logs:{0}:{1}:log-group:awslogs-*".format(self.region, self.account_id)
        cloud_watch_arn = f"arn:aws:logs:{self.region}:{self.account_id}:log-group:*"
        role_document   = { "Version"   : "2008-10-17",
                            "Statement" : [ { "Effect": "Allow",
                                              "Principal": { "Service": "ecs-tasks.amazonaws.com"},
                                              "Action": "sts:AssumeRole" }]}
        policy_document = { "Version"  : "2012-10-17",
                            "Statement": [{   "Effect"  :  "Allow"                              ,
                                              "Action"  : [  "ecr:GetAuthorizationToken"        ,
                                                             "ecr:BatchCheckLayerAvailability"  ,
                                                             "ecr:GetDownloadUrlForLayer"       ,
                                                             "ecr:GetRepositoryPolicy"          ,
                                                             "ecr:DescribeRepositories"         ,
                                                             "ecr:ListImages"                   ,
                                                             "ecr:DescribeImages"               ,
                                                             "ecr:BatchGetImage"               ],
                                               "Resource": "*"                                 },
                                          {    "Effect"  : "Allow",
                                               "Action"  : [ "logs:CreateLogStream" ,
                                                             "logs:PutLogEvents"   ],
                                               "Resource": [ cloud_watch_arn ]}]}

        policy_name = 'policy_for_{0}'.format(role_name)

        iam_role = IAM_Role(role_name=role_name)

        if iam_role.exists() and skip_if_exists:
            return iam_role

        if iam_role.create(assume_policy_document=role_document, skip_if_exists=skip_if_exists):
            iam_role.attach_policy(policy_name=policy_name, policy_document=policy_document)
            if policy_name in iam_role.iam.role_policies():
                return iam_role

    def wait_for(self, waiter_type, kwargs):
        waiter = self.client().get_waiter(waiter_type)
        waiter.config.delay        = ECS_WAITER_DELAY
        waiter.config.max_attempts = ECS_WAITER_MAX_ATTEMPTS
        return waiter.wait(**kwargs)


    #todo: add other two waiters: wait_for_services_inactive and wait_for_services_stable

    def wait_for_task_running(self, task_arn, cluster_name='default'):
        waiter_type = 'tasks_running'
        kwargs      = { "cluster" : cluster_name,
                        "tasks"   : [task_arn  ]}
        self.wait_for(waiter_type=waiter_type, kwargs=kwargs)
        return self.task(cluster_name=cluster_name, task_arn=task_arn)

    def wait_for_task_stopped(self, task_arn, cluster_name='default'):
        waiter_type = 'tasks_stopped'
        kwargs      = { "cluster" : cluster_name,
                        "tasks"   : [task_arn  ]}
        self.wait_for(waiter_type=waiter_type, kwargs=kwargs)
        return self.task(cluster_name=cluster_name, task_arn=task_arn)