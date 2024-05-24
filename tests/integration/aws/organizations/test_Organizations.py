from unittest import TestCase

import botocore
import pytest

from osbot_utils.utils.Dev import pprint

from osbot_aws.AWS_Config import AWS_Config

from osbot_utils.utils.Objects import type_full_name

from osbot_aws.aws.organizations.Organizations import Organizations


@pytest.mark.skip("needs quite a lot of privs")
class test_Organizations(TestCase):
    organisations : Organizations
    @classmethod
    def setUpClass(cls):
        cls.organisations = Organizations()

    def test_client(self):
        with self.organisations as _:
            assert type_full_name(_.client()) == 'botocore.client.Organizations'

    def test_account(self):
        with self.organisations as _:

            account_id = _.aws_config.account_id()
            account    = _.account(account_id=account_id)
            pprint(account)

    def test_accounts(self):
        with self.organisations as _:
            accounts = _.accounts()
            pprint(accounts)
