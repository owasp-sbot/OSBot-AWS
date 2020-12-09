from pprint import pprint
from unittest import TestCase

from osbot_utils.utils.Dev import Dev

from osbot_aws.AWS_Config import AWS_Config
from osbot_aws.tmp_utils.Temp_Assert import Temp_Assert
from osbot_aws.helpers.IAM_Role import IAM_Role

class test_IAM_Role(TestCase):


    def setUp(self):
        self.temp_role_name  = 'test_IAM_Role__temp_role'
        self.iam_role        = IAM_Role(role_name=self.temp_role_name)
        with AWS_Config() as aws_config:
            self.account_id  = aws_config.aws_session_account_id()
            self.region      = aws_config.aws_session_region_name()

    def test___init__(self):
        assert self.iam_role.iam.role_name == self.temp_role_name

    def test_create_for__code_build(self):
        self.iam_role.iam.role_delete()
        result      = self.iam_role.create_for__code_build()
        status      = result.get('status')
        data        = result.get('data')
        role_arn    = result.get('role_arn')
        role_name   = result.get('role_name')
        create_date = data  .get('CreateDate')
        del data['RoleId']
        del data['CreateDate']

        expected_service = 'codebuild.amazonaws.com'
        expected_arn     = 'arn:aws:iam::{0}:role/test_IAM_Role__temp_role'.format(self.account_id )
        expected_data    =  { 'Arn': expected_arn,
                              'AssumeRolePolicyDocument': { 'Statement': [ { 'Action': 'sts:AssumeRole',
                                                                             'Effect': 'Allow',
                                                                             'Principal': { 'Service': expected_service}}]},
                              'Path': '/',
                              'RoleName': 'test_IAM_Role__temp_role'}

        assert status    == 'ok'
        assert role_arn  == expected_arn
        assert role_name == self.temp_role_name
        assert data      == expected_data

        Temp_Assert(create_date).is_today()

        assert self.iam_role.create_for__code_build() == { 'data'     : 'role already exists',
                                                          'role_name': self.temp_role_name,
                                                          'role_arn' : expected_arn,
                                                          'status'   : 'warning'}
        assert self.iam_role.iam.role_delete() is True

    def test_create_for__lambda(self):
        self.iam_role.create_for__lambda().get('role_arn')
        role_info = self.iam_role.iam.role_info()
        service = role_info.get('AssumeRolePolicyDocument').get('Statement')[0].get('Principal').get('Service')
        assert service == 'lambda.amazonaws.com'

        policy_statement = list(self.iam_role.iam.role_policies_statements().values()).pop()

        assert policy_statement ==  [{ 'Action'  : [ 'logs:CreateLogGroup','logs:CreateLogStream','logs:PutLogEvents'],
                                       'Effect'  : 'Allow',
                                       'Resource': [ 'arn:aws:logs:{0}:{1}:log-group:/aws/lambda/*'.format(self.region, self.account_id )]}]

        assert self.iam_role.iam.role_delete() is True            # delete role and policies

    def test_create_for_service_with_policies(self):
        policy_name = "Cloud_Watch"
        policies = { policy_name: {   "Version": "2012-10-17",
                                      "Statement": [ {    "Effect": "Allow",
                                                          "Action": [ "logs:CreateLogGroup"    ,
                                                                      "logs:CreateLogStream"   ,
                                                                      "logs:DescribeLogGroups" ,
                                                                      "logs:DescribeLogStreams",
                                                                      "logs:PutLogEvents"      ,
                                                                      "logs:GetLogEvents"      ,
                                                                      "logs:FilterLogEvents"  ],
                                                          "Resource": "*" }]}}
        service = 'apigateway.amazonaws.com'

        recreate_policy = True
        project_name    = self.temp_role_name
        result          = self.iam_role.create_for_service_with_policies(service, policies, project_name, recreate_policy)
        assert result == { 'policies_arns': [f'arn:aws:iam::{self.account_id}:policy/{policy_name}_{project_name}'],
                           'role_arn'      : f'arn:aws:iam::{self.account_id}:role/{project_name}'}

        temp_policies_arns = result['policies_arns']
        temp_policy_arn    = result['policies_arns'][0]

        assert len(temp_policies_arns)  == 1
        assert self.iam_role.iam.role_exists()

        assert self.iam_role.iam.policy_exists(temp_policy_arn)

        self.iam_role.iam.role_delete()                             # will also delete all associated policies

        assert self.iam_role.iam.policy_not_exists(temp_policy_arn)
        assert self.iam_role.iam.role_not_exists()



