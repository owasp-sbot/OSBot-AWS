from time import sleep

from botocore.exceptions import ClientError

from osbot_utils.decorators.lists.group_by  import group_by
from osbot_aws.apis.Cloud_Watch_Logs        import Cloud_Watch_Logs
from osbot_aws.apis.STS                     import STS
from osbot_aws.helpers.IAM_Role             import IAM_Role
from osbot_utils.decorators.lists.index_by  import index_by
from osbot_utils.decorators.methods.cache   import cache
from osbot_utils.utils.Dev                  import Dev
from osbot_aws.apis.Session                 import Session
from osbot_utils.utils.Misc                 import list_get

# todo: find good solution to capture/manage these config values (See also values in EC2 class)
ECS_WAITER_DELAY        = 1             # default was 6 seconds
ECS_WAITER_MAX_ATTEMPTS = 600           # default was 100 times

class ECS:

    def __init__(self):
        self.account_id  = self.sts().current_account_id()
        self.region      = self.sts().current_region_name()

    @cache
    def client(self):
        return Session().client('ecs')

    @cache
    def sts(self):
        return STS()

    @index_by
    def cluster(self, cluster_arn):
        result = self.clusters(clusters_arns=[cluster_arn])
        if len(result) == 1:
            return result[0]

    def cluster_arn(self, cluster_name):
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

    # def task_get_log_details(self, task_name):
    #
    #     cloud_watch =
    #     if cloud_watch.log_group_exists(log_group_name) is False:
    #         cloud_watch.log_group_create(log_group_name)
    #     return log_group_name,log_group_region,log_group_stream_prefix

    def task_definition(self, task_definition_arn):
        if task_definition_arn:
            result          = self.client().describe_task_definition(taskDefinition=task_definition_arn)
            task_definition = result.get('taskDefinition')
            if task_definition and task_definition.get('status') == 'ACTIVE':       # threat inactive task definitions as non existent (to address AWS weird bug of not allowing task definitions to be deleted)
                return task_definition


    def task_definition_arn(self, task_family, revision):
        return f'arn:aws:ecs:{self.region}:{self.account_id}:task-definition/{task_family}:{revision}'

    def task_definition_create(self, task_definition_config):
        cpu                = task_definition_config.get('cpu'               )
        execution_role_arn = task_definition_config.get('execution_role_arn')
        log_group_name     = task_definition_config.get('log_group_name'    )
        log_stream_name    = task_definition_config.get('log_stream_name'   )
        image_name         = task_definition_config.get('image_name'        )
        memory             = task_definition_config.get('memory'            )
        network_mode       = task_definition_config.get('network_mode'      )
        task_family        = task_definition_config.get('task_family'       )
        task_role_arn      = task_definition_config.get('task_role_arn'     )
        requires           = task_definition_config.get('requires'          )

        Cloud_Watch_Logs().log_stream_create(log_group_name=log_group_name, log_stream_name=log_stream_name)

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

        try:
            return self.client().register_task_definition(**kwargs).get('taskDefinition')
        except Exception as error:
            return "{0}".format(error)

    def task_definition_delete(self, task_definition_arn):
        result = self.client().deregister_task_definition(taskDefinition=task_definition_arn)
        return result.get('taskDefinition').get('status') == 'INACTIVE'

    def task_definition_exists(self, task_definition_arn):
        return self.task_definition(task_definition_arn=task_definition_arn) is not None

    def task_definition_latest(self, task_family):
        try:
            result = self.client().describe_task_definition(taskDefinition=task_family)
            return result.get('taskDefinition')
        except ClientError as e:
            if e.response.get('Error', {}).get('Message') == 'Unable to describe task definition.':
                return {}
            raise

    def task_definition_not_exists(self, task_definition_arn):
        return self. task_definition_exists(task_definition_arn=task_definition_arn) is False

    def task_definition_setup(self, task_family, image_name, roles_skip_if_exists=False):
        task_role_name      = f'{task_family}_task_role'
        execution_role_name = f'{task_family}_execution_role'
        log_group_name      = "ecs-task-on-{0}".format(image_name)

        task_role_iam       = self.policy_create_for_task_role     (task_role_name     , skip_if_exists=roles_skip_if_exists)
        execution_role_iam  = self.policy_create_for_execution_role(execution_role_name, skip_if_exists=roles_skip_if_exists)

        task_role_arn       = task_role_iam     .arn()
        execution_role_arn  = execution_role_iam.arn()

        return { 'cpu'                : '1024'               ,      # 1 CPU
                 'image_name'         : image_name           ,
                 'log_group_name'     : log_group_name       ,
                 'log_stream_name'    : task_family          ,
                 'memory'             : '2048'               ,
                 'execution_role_arn' : execution_role_arn   ,
                 'network_mode'       : 'awsvpc'             ,
                 'requires'           : 'FARGATE'            ,      # todo: add support for EC2 Instances
                 'task_family'        : task_family          ,
                 'task_role_arn'      : task_role_arn        }

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

    def task_create(self, cluster_name, task_definition_arn, subnet_id, security_group_id, launch_type='FARGATE', assign_public_ip='ENABLED'):
        kwargs = {
                    'cluster'             : cluster_name        ,
                    'taskDefinition'      : task_definition_arn ,
                    'launchType'          : launch_type         ,
                    'networkConfiguration': { 'awsvpcConfiguration': { 'subnets'        : [ subnet_id        ],
                                                                       'securityGroups' : [ security_group_id],
                                                                       'assignPublicIp' : assign_public_ip   }},
                 }

        try:
            result = self.client().run_task(**kwargs)
            return result.get('tasks')[0]
        except Exception as error:
            return "{0}".format(error)

    def task_exists(self, cluster_name, task_arn):
        return self.task(cluster_name=cluster_name, task_arn=task_arn) is not None

    def task_stop(self, cluster_name, task_arn):
        kwargs = {'cluster': cluster_name,
                  'task'   : task_arn    }

        return self.client().stop_task(**kwargs).get('taskDefinitionArns')

    def task_wait_for_completion(self, cluster_name, task_arn, sleep_for=1, max_attempts=30, log_status=False):
        build_info = ''
        for i in range(0,max_attempts):
            build_info    = self.task(cluster_name, task_arn)
            last_Status  = build_info.get('lastStatus')
            #current_phase = build_info.get('currentPhase')
            if log_status:
                Dev.pprint("[{0}] {1}".format(i,last_Status))
            if last_Status == 'DEPROVISIONING' or last_Status == 'STOPPED':
                return build_info
            sleep(sleep_for)
        return build_info

    @index_by
    @group_by
    def tasks(self, cluster_name, task_arns=None):
        if task_arns is None:
            task_arns = self.tasks_arns(cluster_name=cluster_name)
        kwargs = {"cluster": cluster_name,
                  "tasks"  : task_arns}
        return self.client().describe_tasks(**kwargs).get('tasks')

    def tasks_arns(self,cluster_name, task_family=None):
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

        if iam_role.create(policy_document=role_document, skip_if_exists=skip_if_exists):
            iam_role.attach_policy(policy_name=policy_name, policy_document=policy_document)
            if policy_name in iam_role.iam.role_policies():
                return iam_role

    def wait_for(self, waiter_type, kwargs):
        waiter = self.client().get_waiter(waiter_type)
        waiter.config.delay        = ECS_WAITER_DELAY
        waiter.config.max_attempts = ECS_WAITER_MAX_ATTEMPTS
        return waiter.wait(**kwargs)


    #todo: add other two waiters: wait_for_services_inactive and wait_for_services_stable

    def wait_for_tasks_running(self, cluster_name, task_arn):
        waiter_type = 'tasks_running'
        kwargs      = { "cluster" : cluster_name,
                        "tasks"   : [task_arn  ]}
        self.wait_for(waiter_type, kwargs)
        return self.task(cluster_name=cluster_name, task_arn=task_arn)

    def wait_for_tasks_stopped(self, cluster_name, task_arn):
        waiter_type = 'tasks_stopped'
        kwargs      = { "cluster" : cluster_name,
                        "tasks"   : [task_arn  ]}
        self.wait_for(waiter_type, kwargs)
        return self.task(cluster_name=cluster_name, task_arn=task_arn)