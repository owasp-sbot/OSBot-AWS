from unittest                                                   import TestCase
from osbot_aws.apis.Session                                     import URL__LOCAL_STACK__ENDPOINT_URL
from osbot_aws.aws.ec2.EC2                                      import EC2
from osbot_aws.aws.ec2.utils.EC2__with_temp_role                import EC2__with_temp_role
from tests.integration.osbot_aws__objs_for__integration_tests   import setup__osbot_aws__integration_tests


# todo: wire this when OSBOT in GH is running with the new AWS account (and into another class)
    # def test___check_current_identity(self):
    #     with self.ec2__with_temp_role.aws_config as _:
    #         assert _.account_id()                == CURRENT__OSBOT_AWS__TESTS__ACCOUNT_ID
    #         assert _.aws_session_region_name()   == CURRENT__OSBOT_AWS__TESTS__DEFAULT_REGION
    #         assert _.sts__caller_identity_user() == CURRENT__OSBOT_AWS__TESTS__IAM_USER
# todo: fix the fact that the EC2__with_temp_role (i.e. ROLE__temp_osbot__Full_Access__ec2)  role needs this Trust Relationship added manually
# {
#     "Version": "2012-10-17",
#     "Statement": [
#         {
#             "Effect": "Allow",
#             "Principal": {
#                 "AWS": [
#                     "arn:aws:iam::470426667096:user/OSBot-AWS-Dev__Only-IAM",
#                     "arn:aws:iam::470426667096:user/dinis.cruz+aws@owasp.org"
#                 ]
#             },
#             "Action": "sts:AssumeRole"
#         }
#     ]
# }


class test_EC2__with_temp_role(TestCase):

    @classmethod
    def setUpClass(self):
        setup__osbot_aws__integration_tests()
        self.ec2__with_temp_role = EC2__with_temp_role()
        assert EC2().client().meta.endpoint_url == URL__LOCAL_STACK__ENDPOINT_URL
        #self.ec2__with_temp_role._temp_role__iam_reset_credentials()


    def test___init__(self):
        with self.ec2__with_temp_role  as _:
            expected_values = { '_temp_role_config' : _._temp_role_config  ,
                                'aws_config'         : _.aws_config         }
            assert _.__locals__() == expected_values

    def test__iam_assume_role(self):
        with self.ec2__with_temp_role as _:
            iam_assume_policy = _._iam_assume_role()
            assert iam_assume_policy.role_name == 'ROLE__temp_osbot__Full_Access__ec2'

    def test_client(self):
        with self.ec2__with_temp_role as _:
            iam_assume_policy = _._iam_assume_role()
            client            = _.client()

            assert iam_assume_policy.role_exists() is True

            assert client.meta.service_model.service_name == 'ec2'

            assert type(_.key_pairs()) is list   # todo fix LocalStack issue that is happening here: (InternalFailure) when calling the DescribeKeyPairs operation: Service 'ec2' is not enabled. Please check your 'SERVICES' configuration variable.



            #     obj_info(self.ec2__with_temp_role)
    #
    #     #pprint(self.ec2__with_temp_role.)
    #     #pprint(self.ec2__with_temp_role.amis())