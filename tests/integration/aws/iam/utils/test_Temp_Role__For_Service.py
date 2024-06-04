from unittest import TestCase

import pytest

from osbot_aws.OSBot_Setup import CURRENT__OSBOT_AWS__TESTS__ACCOUNT_ID, \
    CURRENT__OSBOT_AWS__TESTS__DEFAULT_REGION, CURRENT__OSBOT_AWS__TESTS__IAM_USER

from osbot_aws.aws.iam.utils.Temp_Role__For_Service     import Temp_Role__For_Service
from osbot_aws.aws.iam.utils.Temp_Role__For_Service__Config import Temp_Role__For_Service__Config
from osbot_utils.helpers.Local_Cache                    import Local_Cache
from osbot_utils.utils.Files                            import path_combine, current_temp_folder
from osbot_utils.utils.Misc                             import list_set, random_text, lower

@pytest.mark.skip("runs ok about 60% of the time, which is really weird")  # todo: figure out why when running in multiple tests (or even just these) step 4 and usually step 6 fails
class test_Temp_Role__For_Service(TestCase):
    boto3_service_name    : str
    required_service      : str
    temp_role_for_service: Temp_Role__For_Service

    @classmethod
    def setUpClass(cls):
        cls.boto3_service_name    = 's3'
        cls.required_service      = 's3'
        cls.random_role_name      = True
        cls.required_services     = [cls.required_service]
        cls.temp_role_config      = Temp_Role__For_Service__Config(boto3_service_name=cls.boto3_service_name, required_services=cls.required_services, random_role_name=cls.random_role_name)
        cls.temp_role_for_service = Temp_Role__For_Service(_temp_role_config=cls.temp_role_config)
        cls.iam_assume_role       = cls.temp_role_for_service._iam_assume_role()
        cls.cached_role           = cls.iam_assume_role.cached_role


    def test_1__check_current_identity(self):
        with self.temp_role_for_service.aws_config as _:
            assert _.account_id()                == CURRENT__OSBOT_AWS__TESTS__ACCOUNT_ID
            assert _.aws_session_region_name()   == CURRENT__OSBOT_AWS__TESTS__DEFAULT_REGION
            assert _.sts__caller_identity_user() == CURRENT__OSBOT_AWS__TESTS__IAM_USER

    def test_2__init__(self):
        with self.temp_role_for_service  as _:
            expected_values = { '_temp_role_config': _._temp_role_config,
                                'aws_config'       : _.aws_config       }
            assert _.__locals__() == expected_values

    def test_3_iam_assume_role(self):
        with self.temp_role_for_service as _:
            iam_assume_role                        = _._iam_assume_role()
            local_role_cache                       = iam_assume_role.cached_role
            expected_caches_folder_name            = '_aws_cached_roles'
            expected_caches_folder                 = path_combine(current_temp_folder(), expected_caches_folder_name)

            assert _._temp_role_config.random_role_name is True
            assert iam_assume_role.policies_to_add      == [{'action': '*', 'resource': '*', 'service': self.required_service}]
            assert iam_assume_role.role_name.startswith(f'ROLE__temp__Full_Access__osbot__for__{self.boto3_service_name}_')

            assert type(local_role_cache)              is Local_Cache
            assert local_role_cache.caches_name        == expected_caches_folder_name
            assert local_role_cache.cache_name         == iam_assume_role.role_name
            assert local_role_cache.path_root_folder() == expected_caches_folder

            # BUG no account id in file_name: todo add account so that we can have multiple roles in different accounts
            assert local_role_cache.path_cache_file () == path_combine(expected_caches_folder, f'{iam_assume_role.role_name}.json')

            assert local_role_cache.cache_exists() is False

    def test_4_create_role_and_credentials(self):
        with self.temp_role_for_service as _:
            _._create_role_and_credentials()
            assert self.iam_assume_role.role_exists() is True
            assert self.cached_role.cache_exists   () is True


    def test_5_validate_cache_data(self):
        with self.temp_role_for_service as _:
            role_config      = _._temp_role_config

            cached_role      = self.iam_assume_role.cached_role
            required_service = self.required_service
            role_name        = role_config.role_name
            action           = role_config.action
            resource         = role_config.resource

            # check local cache data
            assert cached_role.cache_exists() is True
            cache_data               = cached_role.data()
            account_id               = _.aws_config.account_id()
            current_user             =  CURRENT__OSBOT_AWS__TESTS__IAM_USER
            current_user_id          = cache_data.get('current_user_id')
            iam_principal_user       = f'arn:aws:iam::{account_id}:user/{current_user}'
            role_arn                 = f'arn:aws:iam::{account_id}:role/{role_name}'
            role_name__for_session   = cache_data.get('result__credentials').get('AssumedRoleUser').get('Arn').split('/')[-1]
            assumed_role_arn         = f'arn:aws:sts::{account_id}:assumed-role/{role_name}/{role_name__for_session}'
            new_role_id              = cache_data.get('result__role_create').get('data').get('RoleId')
            new_role_created_date    = cache_data.get('result__role_create').get('data').get('CreateDate')
            assumed_role_id          = f'{new_role_id}:{role_name__for_session}'
            assumed_role_credentials = cache_data.get('result__credentials').get('Credentials')

            assert list_set(assumed_role_credentials) == ['AccessKeyId', 'Expiration', 'SecretAccessKey', 'SessionToken']
            assert role_name__for_session.startswith('osbot_sts_session__')                         # this is the default value in STS()assume_role

            expected__assume_policy       =  {'Statement': [ { 'Action'   : 'sts:AssumeRole'              ,
                                                               'Effect'   : 'Allow'                       ,
                                                               'Principal': { 'AWS': iam_principal_user }}],
                                              'Version'  : '2012-10-17'                                    }
            expected_policies             = { f'inline_policy_for_{required_service}____': { 'Statement': [ { 'Action'  : f'{required_service}:{action}',
                                                                                                             'Effect'  : 'Allow',
                                                                                                             'Resource': resource}],
                                                                                             'Version'   : '2012-10-17'}}
            expected__policies_to_add     = [ { 'action' : action,
                                                'resource': resource,
                                                'service' : required_service}]
            expected__result__credentials = { 'AssumedRoleUser': { 'Arn'          : assumed_role_arn,
                                                                   'AssumedRoleId': assumed_role_id },
                                              'Credentials'    : assumed_role_credentials            }
            expected_result__role_create = { 'data': { 'Arn': role_arn,
                                                       'AssumeRolePolicyDocument': { 'Statement': [ { 'Action': 'sts:AssumeRole',
                                                                                                      'Effect': 'Allow',
                                                                                                      'Principal': { 'AWS': iam_principal_user}}],
                                                                                     'Version': '2012-10-17'},
                                                       'CreateDate'              : new_role_created_date,
                                                       'Path'                    : '/'                  ,
                                                       'RoleId'                  : new_role_id          ,
                                                       'RoleName'                : role_name            },
                                             'error': None,
                                             'message': 'user created (skip_if_exists: True)',
                                             'status': 'ok'}

            expected__cached_data = { 'assume_policy'       : expected__assume_policy      ,
                                      'current_account_id'  : account_id                   ,
                                      'current_user_arn'    : iam_principal_user           ,
                                      'current_user_id'     : current_user_id              ,
                                      'policies'            : expected_policies            ,
                                      'policies_to_add'     : expected__policies_to_add    ,
                                      'result__credentials' : expected__result__credentials,
                                      'result__role_create' : expected_result__role_create                  ,
                                      'role_arn'            : f'arn:aws:iam::{account_id}:role/{role_name}' ,
                                      'role_exists'         : True                                          ,
                                      'role_name'           : role_name                                     }
            assert cache_data == expected__cached_data


    def test_6_assume_credentials(self):
        assert self.boto3_service_name == 's3'  # confirm we asked for privs for s3
        with self.temp_role_for_service as _:
            iam_assume_role = _._iam_assume_role()

            iam_assume_role.wait_for_valid_execution('s3', 'list_buckets')

            assumed_role_arn = iam_assume_role.cached_role.data().get('result__credentials').get('AssumedRoleUser').get('Arn')
            service_name     = 's3'
            s3_client        = iam_assume_role.boto3_client(service_name=service_name)
            buckets          = s3_client.list_buckets()
            assert list_set(buckets) == ['Buckets', 'Owner', 'ResponseMetadata']

            with self.assertRaises(Exception) as context:
                service_name = 'ec2'
                ec2_client  = iam_assume_role.boto3_client(service_name=service_name)
                ec2_client.describe_instances()
            assert context.exception.args == ( 'An error occurred (UnauthorizedOperation) when calling the DescribeInstances '
                                              f'operation: You are not authorized to perform this operation. User: {assumed_role_arn} '
                                               'is not authorized to perform: ec2:DescribeInstances because no '
                                               'identity-based policy allows the ec2:DescribeInstances action',)

    def test_7_client(self):
        with self.temp_role_for_service as _:
            s3_client = _.client()
            assert s3_client.meta.service_model.service_name == 's3'
            buckets = s3_client.list_buckets()
            assert list_set(buckets) == ['Buckets', 'Owner', 'ResponseMetadata']


    def test_8_role_delete(self):
        self.iam_assume_role.delete_role()
        self.cached_role.cache_delete()
        assert self.iam_assume_role.role_exists () is False
        assert self.cached_role    .cache_exists() is False


# class test_debug_iam_issue(TestCase):
#
#     def test_bug_recreate_call_to_assume_role(self):
#         role_name             = 'ROLE__temp__Full_Access__for__s3_4wb7ora1643h'
#         #temp_role_config      = Temp_Role__For_Service__Config(role_name=role_name)
#         #temp_role_for_service = Temp_Role__For_Service(_temp_role_config=temp_role_config)
#         #iam_assume_role       = temp_role_for_service._iam_assume_role()
#         iam_assume_role        = IAM_Assume_Role(role_name=role_name)
#         cached_role           = iam_assume_role.cached_role
#
#         assert cached_role.cache_exists   () is True
#         assert iam_assume_role.role_exists() is True
#         #credentials = iam_assume_role.credentials()
#         #pprint(credentials)
#
#         pprint(cached_role.data())