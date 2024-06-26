import pytest
from unittest import TestCase
from osbot_aws.aws.iam.roles.IAM__Role_for__EC2_Instances import IAM__Role_for__EC2_Instances


@pytest.mark.skip("was failing in GH Actions (with NoSuchEntity error") # todo: fix this
class temp_Role__for__EC2_Instances(TestCase):
    ec2_instances_role : IAM__Role_for__EC2_Instances
    role_name          : str
    delete_on_exit     : bool = True

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.role_name          = 'temp__IAM__Role_for__EC2_Instances'
        cls.ec2_instances_role = IAM__Role_for__EC2_Instances(role_name=cls.role_name)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        if cls.delete_on_exit:
            assert cls.ec2_instances_role.iam_role.delete() is True

    def test_1__create(self):
        with self.ec2_instances_role as _:
            _.create()

    def test_2__attach_policy__full_access__s3(self):
        with self.ec2_instances_role as _:
            _.attach_policy__full_access__s3()


    def test_3__role_policies(self):
        with self.ec2_instances_role as _:
            policies = _.role_policies()
            assert policies == ['Policy__Full_Access__s3']
