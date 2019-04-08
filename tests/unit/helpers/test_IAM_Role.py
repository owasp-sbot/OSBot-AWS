from unittest import TestCase

from pbx_gs_python_utils.utils.Dev import Dev

from osbot_aws._tmp_utils.Temp_Assert import Temp_Assert
from osbot_aws.helpers.IAM_Policy import IAM_Policy
from osbot_aws.helpers.IAM_Role import IAM_Role

account_id     = '244560807427'

class test_IAM_Role(TestCase):


    def setUp(self):
        self.temp_role_name  = 'test_IAM_Role__temp_role'
        self.iam_role        = IAM_Role(role_name=self.temp_role_name)

    def test___init__(self):
        assert self.iam_role.iam.role_name == self.temp_role_name

    def test_create_for_code_build(self):
        self.iam_role.iam.role_delete()
        result      = self.iam_role.create_for_code_build()
        status      = result.get('status')
        data        = result.get('data')
        role_arn    = result.get('role_arn')
        role_name   = result.get('role_name')
        create_date = data  .get('CreateDate')
        del data['RoleId']
        del data['CreateDate']

        expected_service = 'codebuild.amazonaws.com'
        expected_arn     = 'arn:aws:iam::{0}:role/test_IAM_Role__temp_role'.format(account_id)
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

        assert self.iam_role.create_for_code_build() == { 'data'     : 'role already exists',
                                                          'role_name': self.temp_role_name,
                                                          'role_arn' : expected_arn,
                                                          'status'   : 'warning'}
        assert self.iam_role.iam.role_delete() is True

#    User: arn:aws:sts::244560807427:assumed-role/temp_role_for_lambda_invocation/temp_lambda_K698AJ
#    is not authorized to perform:
#    logs:CreateLogStream on resource: log-stream:2019/04/08/[$LATEST]3ce3a3b8ab5c45fb853683467d035cc9",

    def test_create_for_lambda(self):
        self.iam_role.create_for_lambda().get('role_arn')
        role_info = self.iam_role.iam.role_info()
        service = role_info.get('AssumeRolePolicyDocument').get('Statement')[0].get('Principal').get('Service')
        assert service == 'lambda.amazonaws.com'



        temp_policy_name = 'temp_policy_{0}'.format(self.temp_role_name)

        cloud_watch_arn  = "arn:aws:logs:{0}:{0}:log-group:/aws/lambda/*".format('eu-west-2','244560807427')

        policy_arn = IAM_Policy(temp_policy_name).add_cloud_watch(cloud_watch_arn).create().get('policy_arn')

        #Dev.pprint(policy_arn)

        # policy_statement = { "Version": "2012-10-17",
        #                      "Statement": [{ "Effect": "Allow",
        #                                      "Action": ["logs:CreateLogStream",
        #                                                 "logs:PutLogEvents"],
        #                                      "Resource": [cloud_watch_arn] }]}
        #
        # policy_arn = self.iam_role.iam.policy_create(temp_policy_name, policy_statement).get('policy_arn')
        self.iam_role.iam.role_policy_attach(policy_arn)

        Dev.pprint(self.iam_role.iam.role_policies())

        assert self.iam_role.iam.role_delete() is True

