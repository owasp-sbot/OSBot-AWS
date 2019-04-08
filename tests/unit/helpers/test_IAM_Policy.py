from unittest import TestCase

from pbx_gs_python_utils.utils.Dev import Dev

from osbot_aws.helpers.IAM_Policy import IAM_Policy


class test_IAM_Policy(TestCase):

    def setUp(self):
        self.account_id = '244560807427'
        self.iam_policy = IAM_Policy()


    def test_add_cloud_watch(self):
        expected_statements = [ { 'Action': [ 'logs:CreateLogGroup','logs:CreateLogStream','logs:PutLogEvents'],
                                  'Effect': 'Allow','Resource': ['abc']}]

        assert self.iam_policy.add_cloud_watch('abc')       == self.iam_policy

        assert self.iam_policy.statement().get('Statement') == expected_statements

    def test_create(self):
        self.iam_policy = IAM_Policy('temp_policy__test_create')
        self.iam_policy.delete()

        result = self.iam_policy.add_cloud_watch('arn:aws:abc').create()

        expected_policy_arn = 'arn:aws:iam::{0}:policy/{1}'.format(self.account_id, self.iam_policy.policy_name)
        status              = result.get('status'    )
        policy_arn          = result.get('policy_arn')
        data                = result.get('data'      )

        assert status                       == 'ok'
        assert policy_arn                   == expected_policy_arn
        assert data.get('Arn'             ) == expected_policy_arn
        assert data.get('Path'            ) == '/'
        assert data.get('DefaultVersionId') == 'v1'
        assert data.get('PolicyName'      ) == self.iam_policy.policy_name

        assert self.iam_policy.statement_from_aws () == [{'Action': ['logs:CreateLogGroup','logs:CreateLogStream','logs:PutLogEvents'],
                                                          'Effect': 'Allow',
                                                          'Resource': ['arn:aws:abc']}]
        assert self.iam_policy.delete() is True

    def test_create___bad_policy_statement(self):
        iam_policy = IAM_Policy('temp_policy__test_create_no_policy')
        response = iam_policy.create()
        assert  response == { 'data'         : 'An error occurred (MalformedPolicyDocument) when calling the CreatePolicy operation: Syntax errors in policy.',
                              'policy_arn'   : None,
                              'policy_name'  : 'temp_policy__test_create_no_policy',
                              'status'       : 'error'}
        assert iam_policy.exists() is False

    def test_create___no_policy_name(self):
        assert IAM_Policy().create() == {'data': 'policy name is None', 'status': 'error'}

    def test_statement(self):
        assert IAM_Policy().statement() == {'Statement': [], 'Version': '2012-10-17'}