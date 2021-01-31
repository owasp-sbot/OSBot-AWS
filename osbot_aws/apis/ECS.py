from time import sleep

from osbot_aws.helpers.IAM_Role import IAM_Role

from osbot_utils.decorators.lists.index_by import index_by

from osbot_aws.AWS_Config import AWS_Config

from osbot_utils.decorators.methods.cache import cache

from osbot_utils.utils.Dev import Dev

from osbot_aws.apis.Cloud_Watch import Cloud_Watch
from osbot_aws.apis.IAM import IAM
from osbot_aws.apis.Session import Session


class ECS:

    def __init__(self):
        self.aws_config  = AWS_Config()
        self.account_id  = self.aws_config.aws_session_account_id()
        self.region      = self.aws_config.aws_session_region_name()

    @cache
    def client(self):
        return Session().client('ecs')

    def cluster_arn(self, cluster_name):
        return f'arn:aws:ecs:{self.region}:{self.account_id}:cluster/{cluster_name}'

    def cluster_create(self, cluster_name):
        response = self.client().create_cluster(clusterName=cluster_name)
        return response.get('cluster')
        
    def cluster_delete(self, cluster_arn):
        response = self.client().delete_cluster(cluster=cluster_arn)
        return response.get('cluster')

    @index_by
    def cluster(self, cluster_arn):
        result = self.clusters(clusters_arns=[cluster_arn])
        if len(result) == 1:
            return result[0]

    @index_by
    def clusters(self, clusters_arns=None):
        include         = [ 'ATTACHMENTS' , 'SETTINGS' , 'STATISTICS' , 'TAGS']
        target_clusters = clusters_arns or self.clusters_arns()
        return self.client().describe_clusters(clusters=target_clusters, include=include).get('clusters')

    def clusters_arns(self):
        return self.client().list_clusters().get('clusterArns')

    def task_get_log_details(self, task_name):
        log_group_name = "awslogs-{0}".format(task_name)
        log_group_region = "eu-west-2"
        log_group_stream_prefix = "awslogs-example"
        cloud_watch = Cloud_Watch()
        if cloud_watch.log_group_exists(log_group_name) is False:
            cloud_watch.log_group_create(log_group_name)
        return log_group_name,log_group_region,log_group_stream_prefix

    def task_create(self, image_name, task_name, task_role_arn, execution_role_arn, cpu='1024', memory='2048', network_mode='awsvpc', requires='FARGATE'):

        (log_group_name, log_group_region, log_group_stream_prefix) = self.task_get_log_details(task_name)

        kwargs = { 'family'              : task_name             ,
                   'taskRoleArn'         : task_role_arn         ,
                   'executionRoleArn'    : execution_role_arn    ,
                   'cpu'                 : cpu                   ,
                   'memory'              : memory                ,
                   'networkMode'         : network_mode          ,
                   "containerDefinitions": [ { 'name'            : image_name,
                                               'image'           : f'{self.account_id}.dkr.ecr.{self.region}.amazonaws.com/{image_name}' ,
                                               "logConfiguration": {   "logDriver": "awslogs",
                                                                       "options"  : {  "awslogs-group"        : log_group_name,
                                                                                       "awslogs-region"       : log_group_region,
                                                                                       "awslogs-stream-prefix": log_group_stream_prefix }}, }],
                   "requiresCompatibilities": [ requires] }

        try:
            return self.client().register_task_definition(**kwargs).get('taskDefinition')
        except Exception as error:
            return "{0}".format(error)

    def task_run(self, cluster, task_arn,subnet_id,security_group):
        kwargs = {
                    'cluster'             : cluster ,
                    'taskDefinition'      : task_arn,
                    'launchType'          : 'FARGATE',
                    'networkConfiguration': { 'awsvpcConfiguration': { 'subnets'        : [ subnet_id],
                                                                       'securityGroups' : [ security_group],
                                                                       'assignPublicIp' : 'ENABLED'  } },
                 }

        try:
            return self.client().run_task(**kwargs).get('tasks')[0]
        except Exception as error:
            return "{0}".format(error)

    def task_delete(self, task_arn):
        return self.client().deregister_task_definition(taskDefinition=task_arn)

    def task_details(self, cluster, task_arn):
        result = self.client().describe_tasks(cluster=cluster, tasks=[task_arn])
        return result.get('tasks').pop()

    def task_wait_for_completion(self, cluster, task_arn, sleep_for=1, max_attempts=30, log_status=False):
        for i in range(0,max_attempts):
            build_info    = self.task_details(cluster, task_arn)
            last_Status  = build_info.get('lastStatus')
            #current_phase = build_info.get('currentPhase')
            if log_status:
                Dev.pprint("[{0}] {1}".format(i,last_Status))
            if last_Status == 'DEPROVISIONING' or last_Status == 'STOPPED':
                return build_info
            sleep(sleep_for)
        return build_info

    def tasks(self):
        return self.client().list_task_definitions().get('taskDefinitionArns')



    def policy_create_for_task_role(self, role_name, skip_if_exists=True):
        policy = { "Version"    : "2008-10-17",
                   "Statement"  : [ { "Effect": "Allow",
                                      "Principal": { "Service": "ecs-tasks.amazonaws.com"},
                                      "Action": "sts:AssumeRole" }]}
        iam_role = IAM_Role(role_name=role_name)
        iam_role.create(policy,skip_if_exists=skip_if_exists)
        return iam_role


    def policy_create_for_execution_role(self, role_name, skip_if_exists=True):
        cloud_watch_arn = "arn:aws:logs:{0}:{1}:log-group:awslogs-*".format(self.region, self.account_id)
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