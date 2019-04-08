from unittest import TestCase

from pbx_gs_python_utils.utils.Dev import Dev

from osbot_aws.helpers.IAM_Policy import IAM_Policy


class test_IAM_Policy(TestCase):

    def setUp(self):
        self.iam_policy = IAM_Policy()


    def test_add_cloud_watch(self):
        expected_statements = [{"Effect"  : "Allow",
                                "Action"  : ["logs:CreateLogStream","logs:PutLogEvents"],
                                "Resource": ['abc']}]

        assert self.iam_policy.add_cloud_watch('abc')       == self.iam_policy
        assert self.iam_policy.statement().get('Statement') == expected_statements

    def test_create(self):
        assert self.iam_policy.create() == {'data': 'policy name is None', 'status': 'error'}
        policy_name = 'temp_policy__test_create'
        self.iam_policy = IAM_Policy(policy_name)
        self.iam_policy.delete()
        assert self.iam_policy.create() == { 'data'         : 'An error occurred (MalformedPolicyDocument) when calling the CreatePolicy operation: Syntax errors in policy.',
                                             'policy_arn'   : None,
                                             'policy_name'  : 'temp_policy__test_create',
                                             'status'       : 'error'}
        assert self.iam_policy.exists() is False

        self.iam_policy.add_cloud_watch('arn:aws:abc')
        result = self.iam_policy.create()
        assert result.get('status') == 'ok'

        #Dev.pprint(self.iam_policy.iam.policy_info(policy_name))


    def test_statement(self):
        assert IAM_Policy().statement() == {'Statement': [], 'Version': '2012-10-17'}