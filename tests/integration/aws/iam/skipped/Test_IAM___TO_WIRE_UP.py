from unittest import TestCase

import pytest


@pytest.mark.skip('Wire up tests')
class Test_IAM___TO_WIRE_UP(TestCase):

    # ------ tests ------


    def test_role_info(self):
        role = self.iam().set_role_name(test_role).role_info()                # also tests the set_role_name function
        assert role.get('Arn'     ) == test_role_arn
        assert role.get('RoleName') == test_role

    @pytest.mark.skip('Fix test')
    def test_role_policies(self):
        policies = self.iam().role_policies()
        assert len(set(policies)) == 0

        iam = IAM(role_name='AWSServiceRoleForAPIGateway')
        assert iam.role_policies() == {'APIGatewayServiceRolePolicy': 'arn:aws:iam::aws:policy/aws-service-role/APIGatewayServiceRolePolicy'}
        assert len(iam.role_policies_statements().get('APIGatewayServiceRolePolicy')[0].get('Action')) > 10

    def test_role_policies_attach__role_policies_detach(self):
        policy_name = 'test_policy'
        policy_document = {"Version": "2012-10-17",                                     # refactor this with policy helper
                           "Statement": [{  "Effect": "Allow",
                                            "Action": "lambda:InvokeFunction",
                                            "Resource": "arn:aws:lambda:*:*:function:*"}]}
        policy_arn = self.iam.policy_create(policy_name, policy_document).get('policy_arn')

        assert len(list(self.iam.role_policies())) == 0
        self.iam.role_policy_attach(policy_arn)
        assert list(self.iam.role_policies())      == ['test_policy']
        self.iam.role_policy_detach(policy_arn)

        assert self.iam.policy_exists(policy_arn) is True
        assert self.iam.policy_delete(policy_arn) is True          # this will not delete a policy that is attached
        assert self.iam.policy_exists(policy_arn) is False

    #@pytest.mark.skip('Fix test')
    def test_roles(self):
        assert len(self.iam.roles())  > 5

    def test_user_access_key_create__delete(self):
        access_key = self.iam.user_access_key_create()
        assert self.iam.access_key__wait_until_key_is_working    (access_key,success_count=1) is True
        self.iam.user_access_keys_delete_all()
        assert self.iam.access_key__wait_until_key_is_not_working(access_key, success_count=1) is True

    # test below was using to get some stats on when the key is enabled
    # def test_user_access_key_create__delete(self):
    #     print()
    #     access_key = self.iam.user_access_key_create()
    #     assert access_key.get('UserName') == test_user
    #     assert len(self.iam.user_access_keys()) > 0
    #     assert self.iam.access_key__wait_until_key_is_working(access_key) is True
    #     print('*******')
    #     print(self.iam.access_key__is_key_working(access_key))
    #     print(self.iam.access_key__is_key_working(access_key))
    #     print(self.iam.access_key__is_key_working(access_key))
    #     print(self.iam.access_key__is_key_working(access_key))
    #     print(self.iam.access_key__is_key_working(access_key))
    #     print(self.iam.access_key__is_key_working(access_key))
    #     print(self.iam.access_key__is_key_working(access_key))
    #     print(self.iam.access_key__is_key_working(access_key))
    #     print('-------')
    #     assert self.iam.user_access_keys_delete_all() is True
    #     print('#######')
    #     assert self.iam.access_key__wait_until_key_is_not_working(access_key) is True
    #     print(self.iam.access_key__is_key_working(access_key))
    #     print(self.iam.access_key__is_key_working(access_key))
    #     print(self.iam.access_key__is_key_working(access_key))
    #     print(self.iam.access_key__is_key_working(access_key))
    #     print(self.iam.access_key__is_key_working(access_key))
    #     print(self.iam.access_key__is_key_working(access_key))
    #     print(self.iam.access_key__is_key_working(access_key))
    #     print(self.iam.access_key__is_key_working(access_key))
    #     print(self.iam.access_key__is_key_working(access_key))
    #     print(self.iam.access_key__is_key_working(access_key))
    #     print(self.iam.access_key__is_key_working(access_key))
    #     print(self.iam.access_key__is_key_working(access_key))
    #     print(self.iam.access_key__is_key_working(access_key))
    #     print(self.iam.access_key__is_key_working(access_key))
    #     print(self.iam.access_key__is_key_working(access_key))
    #     print(self.iam.access_key__is_key_working(access_key))
    #     print(self.iam.access_key__is_key_working(access_key))
    #     print(self.iam.access_key__is_key_working(access_key))
    #     print(self.iam.access_key__is_key_working(access_key))




