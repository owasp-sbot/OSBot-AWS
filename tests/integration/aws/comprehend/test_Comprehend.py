import pytest
from unittest                                               import TestCase
from osbot_utils.type_safe.Type_Safe                        import Type_Safe
from osbot_utils.utils.Env                                  import in_github_action
from osbot_utils.utils.Objects                              import base_types, full_type_name
from osbot_aws.aws.comprehend.Comprehend                    import Comprehend
from osbot_aws.aws.comprehend.Comprehend__Batch             import Comprehend__Batch
from osbot_aws.aws.comprehend.Comprehend__Detect            import Comprehend__Detect
from osbot_aws.aws.comprehend.Comprehend__IAM__Temp_Role    import Comprehend__with_temp_role, Comprehend__Batch__with_temp_role, Comprehend__IAM__Temp_Role


class test_Comprehend(TestCase):
    @classmethod
    def setUpClass(cls):
        if in_github_action():
            pytest.skip("Doesn't work when running all tests")              # todo: fix issue caused by the use of localstack has a target
        cls.comprehend = Comprehend__with_temp_role()

    def test__init__(self):
        with self.comprehend as _:
            assert type(_)       is Comprehend__with_temp_role
            assert base_types(_) == [ Comprehend__IAM__Temp_Role, Comprehend,
                                      Type_Safe, object                     ,
                                      Type_Safe, object                     ]

    def test_client(self):
        with self.comprehend as _:
            assert full_type_name(_.client()) == 'botocore.client.Comprehend'

    def test_detect(self):
        with self.comprehend as _:
            assert type(_.detect()) == Comprehend__Detect

    def test_batch(self):
        with self.comprehend as _:
            assert type(_.batch()) == Comprehend__Batch
