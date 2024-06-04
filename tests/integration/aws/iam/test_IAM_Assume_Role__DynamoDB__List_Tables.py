from unittest import TestCase

from osbot_aws.aws.iam.IAM_Assume_Role import IAM_Assume_Role
from osbot_aws.testing.Pytest import skip_pytest___aws_pytest_user_name__is_not_set



class test_IAM_Assume_Role__DynamoDB__List_Tables(TestCase):

    @classmethod
    def setUpClass(cls):
        skip_pytest___aws_pytest_user_name__is_not_set()

    def setUp(self):
        self.role_name = "temp_role__for_dynamo_db_access"

    #@print_boto3_calls(config__print_return_value=False)
    def test_1_get_dynamo_db_tables(self):

        policies_to_add = [dict(service="dynamodb", action="ListTables", resource="*")]
        iam_assume_role = IAM_Assume_Role(role_name=self.role_name, policies_to_add=policies_to_add)
        with iam_assume_role as _:
            _.create_role(recreate=True)
            client_dynamodb = _.boto3_client(service_name='dynamodb', region_name = 'eu-west-2')
            table_names     = client_dynamodb.list_tables().get('TableNames')
            assert type(table_names) is list

    # #  todo: document better this bug: research more the interesting error that is happening when we quickly create and delete a role (the credentials work for a couple seconds and then stop working)
    # #  note: this test is commented out, but all passed ok when executed locally
    # #        the problem seems to happen when we do _.create_role(recreate=True) which creates and deletes a role very fast
    # def test_2_bug_race_condition_in_delete_and_create_role(self):
    #     iam_assume_role = IAM_Assume_Role(role_name=self.role_name)
    #     max_count = 10
    #     with pytest.raises(ClientError) as exc_info_1:
    #         with iam_assume_role as _:
    #             for i in range(max_count):
    #                 client_dynamodb = _.boto3_client(service_name='dynamodb', region_name='eu-west-2')
    #                 assert len(client_dynamodb.list_tables().get('TableNames')) > 0
    #                 wait_for(1)
    #                 print(f'ok after {i} seconds')
    #     print(f'failed after {i} seconds')
    #     assert ("An error occurred (AccessDeniedException)" in str(exc_info_1.value)) or ("UnrecognizedClientException"                            in str(exc_info_1.value))
    #     assert ("dynamodb:ListTables"                       in str(exc_info_1.value)) or ("The security token included in the request is invalid"  in str(exc_info_1.value))
    #     assert i != max_count
    #
    #     with pytest.raises(ClientError) as exc_info_2:
    #         with iam_assume_role as _:
    #             client_dynamodb_2 = _.boto3_client(service_name='dynamodb', region_name='eu-west-2')
    #             client_dynamodb_2.list_tables().get('TableNames')
    #     print(f'failed again on next request')
    #     assert ("An error occurred (AccessDeniedException)" in str(exc_info_2.value)) or ("UnrecognizedClientException"                            in str(exc_info_2.value))
    #     assert ("dynamodb:ListTables"                       in str(exc_info_2.value)) or ("The security token included in the request is invalid"  in str(exc_info_2.value))
    #
    #     # todo: find out for some reason this wasn't working, but the code is the same as test_3_bug_race_condition_in_delete_and_create_role
    #     #       maybe something to do with cached creds in current test?
    #     # wait_for(3)
    #     # iam_assume_role_2 = IAM_Assume_Role(role_name=self.role_name)
    #     # with iam_assume_role_2 as _:
    #     #     _.credentials_reset()
    #     #     client_dynamodb_3 = _.boto3_client(service_name='dynamodb', region_name='eu-west-2')
    #     #     client_dynamodb_3.list_tables().get('TableNames')
    #     # print('ok after reseting credentials')
    #
    # def test_3_bug_race_condition_in_delete_and_create_role(self):
    #     iam_assume_role = IAM_Assume_Role(role_name=self.role_name)
    #     with iam_assume_role as _:
    #         _.credentials_reset()
    #         client_dynamodb_3 = _.boto3_client(service_name='dynamodb', region_name='eu-west-2')
    #         client_dynamodb_3.list_tables().get('TableNames')
    #     print('ok after reseting credentials')