from time import sleep

import boto3

from pbx_gs_python_utils.utils.Dev import Dev

from osbot_aws.apis.Cloud_Watch import Cloud_Watch
from osbot_aws.apis.IAM import IAM
from osbot_aws.apis.Session import Session


class Fargate:

    def __init__(self,account_id):
        self.ecs        = Session().client('ecs')
        self.account_id = account_id

    def cluster_create(self, cluster_name):
        return self.ecs.create_cluster(clusterName=cluster_name)
        
    def cluster_delete(self, cluster_arn):
        return self.ecs.delete_cluster(cluster=cluster_arn)

    def clusters(self):
        return self.ecs.list_clusters().get('clusterArns')

    def task_get_log_details(self, task_name):
        log_group_name = "awslogs-{0}".format(task_name)
        log_group_region = "eu-west-2"
        log_group_stream_prefix = "awslogs-example"
        cloud_watch = Cloud_Watch()
        if cloud_watch.log_group_exists(log_group_name) is False:
            cloud_watch.log_group_create(log_group_name)
        return log_group_name,log_group_region,log_group_stream_prefix

    def task_create(self, task_name,task_role_arn,execution_role_arn):
        (log_group_name, log_group_region, log_group_stream_prefix) = self.task_get_log_details(task_name)

        kwargs = {
            'family'              : task_name,
            'taskRoleArn'         : task_role_arn,
            'executionRoleArn'    : execution_role_arn,
            'cpu'                 : "1024",
            'memory'              : "2048",
            'networkMode'         : 'awsvpc',
            "containerDefinitions": [ {
                'name'            : 'gs-docker-codebuild',
                'image'           : '{0}.dkr.ecr.eu-west-2.amazonaws.com/gs-docker-codebuild:latest'.format(self.account_id),
                "logConfiguration": {
                                        "logDriver": "awslogs",
                                        "options": {
                                                    "awslogs-group"        : log_group_name,
                                                    "awslogs-region"       : log_group_region,
                                                    "awslogs-stream-prefix": log_group_stream_prefix
                                                   }},

            }],
            "requiresCompatibilities": [ 'FARGATE'] }

        try:
            return self.ecs.register_task_definition(**kwargs).get('taskDefinition')
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
            return self.ecs.run_task(**kwargs).get('tasks')[0]
        except Exception as error:
            return "{0}".format(error)

    def task_delete(self, task_arn):
        return self.ecs.deregister_task_definition(taskDefinition=task_arn)

    def task_details(self, cluster, task_arn):
        result = self.ecs.describe_tasks(cluster=cluster, tasks=[task_arn])
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
        return self.ecs.list_task_definitions().get('taskDefinitionArns')



    def policy_create_for_task_role(self, role_name):
        policy = { "Version"    : "2008-10-17",
                   "Statement"  : [ { "Effect": "Allow",
                                      "Principal": { "Service": "ecs-tasks.amazonaws.com"},
                                      "Action": "sts:AssumeRole" }]}
        IAM(role_name=role_name).role_create(policy)

    def policy_create_for_execution_role(self, role_name):
        region = 'eu-west-2'
        cloud_watch_arn = "arn:aws:logs:{0}:{1}:log-group:awslogs-*".format(region, self.account_id)
        role_policy = { "Version"   : "2008-10-17",
                        "Statement" : [ { "Effect": "Allow",
                                          "Principal": { "Service": "ecs-tasks.amazonaws.com"},
                                          "Action": "sts:AssumeRole" }]}
        policy      = { "Version"  : "2012-10-17",
                        "Statement": [{   "Effect"  :  "Allow"                              ,
                                          "Action"  : [  "ecr:GetAuthorizationToken"        ,
                                                         "ecr:BatchCheckLayerAvailability"  ,
                                                         "ecr:GetDownloadUrlForLayer"       ,
                                                         "ecr:GetRepositoryPolicy"          ,
                                                         "ecr:DescribeRepositories"         ,
                                                         "ecr:ListImages"                   ,
                                                         "ecr:DescribeImages"               ,
                                                         "ecr:BatchGetImage"               ],
                                            "Resource": "*"     },
                                      {
                                           "Effect"  : "Allow",
                                           "Action"  : [ "logs:CreateLogStream" ,
                                                         "logs:PutLogEvents"   ],
                                           "Resource": [ cloud_watch_arn ]}]}

        policy_name = 'policy_for_{0}'.format(role_name)
        iam = IAM(role_name=role_name)

        iam.role_create(role_policy)
        iam.policy_delete(policy_name)
        policy_arn = iam.policy_create(policy_name,policy).get('policy_arn')

        iam.role_policy_attach(policy_arn)



