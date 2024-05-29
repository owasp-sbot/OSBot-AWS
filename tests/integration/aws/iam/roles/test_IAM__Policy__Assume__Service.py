from unittest import TestCase

from osbot_aws.aws.iam.roles.IAM__Policy__Assume__Service import IAM__Policy__Assume__Service, \
    iam_statement__ec2__assume_service, iam_statement__lambda__assume_service


class test_IAM__Policy__Assume__Service(TestCase):

    def setUp(self):
        self.service_name = 'ec2'
        self.iam_policy_assume_service = IAM__Policy__Assume__Service(self.service_name)

    def test_statement(self):
        expected_statement = {'Action'   : 'sts:AssumeRole'                 ,
                              'Effect'   : 'Allow'                          ,
                              'Principal': {'Service': 'ec2.amazonaws.com' }}

        with self.iam_policy_assume_service as _:
            assert _.statement() == expected_statement

    def test_iam_statement__ec2_assume_service(self):
        assert iam_statement__ec2__assume_service() == {'Action'   : 'sts:AssumeRole'                    ,
                                                        'Effect'   : 'Allow'                             ,
                                                        'Principal': {'Service': 'ec2.amazonaws.com'    }}

    def test_iam_statement__lambda_assume_service(self):
        assert iam_statement__lambda__assume_service() == {'Action'   : 'sts:AssumeRole'                    ,
                                                           'Effect'   : 'Allow'                             ,
                                                           'Principal': {'Service': 'lambda.amazonaws.com' }}