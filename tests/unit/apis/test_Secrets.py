import json
import unittest
from unittest import TestCase

from osbot_utils.utils import Misc

from osbot_aws.apis.Secrets import Secrets


class test_Secrets(TestCase):

    def setUp(self):
        self.id    = 'an_secret'
        self.value = 'goes here'
        self.secrets = Secrets(self.id)
        if self.secrets.deleted():
            self.secrets.undelete()

    def tearDown(self):
        if self.secrets.deleted() is False and self.secrets.exists():
            assert self.secrets.delete() is True

    def test_create(self):
        #if self.secrets.exists() or self.secrets.deleted():
        assert self.secrets.delete_no_recovery() is True

        #assert self.secrets.create(self.value) is True

    def test_delete(self):
        self.secrets.delete()
        assert self.secrets.deleted()    is True
        assert Secrets('aaaa').deleted() is False

    def test_details(self):
        details = self.secrets.details()
        assert details.get('Name') == self.id
        assert self.secrets.set_id('aaaaaa').details() is None

    def test_exists(self):
        assert Secrets('aaaaa').exists()     is False
        self.secrets.undelete()
        assert self.secrets.exists() is True

        self.secrets.delete()
        assert self.secrets.exists() is False

    def test_print(self,):
        def my_print(value):                                        # hook method
            assert "{'ARN': 'arn:aws:secretsmanager:" in value      # confirm data sent to print
            assert "'Name': 'an_secret'"              in value
            assert "'ResponseMetadata': {'HTTPHeader" in value

        import builtins                                             # get print module
        original_print = builtins.print                             # save original print method
        builtins.print = my_print                                   # apply hook
        self.secrets.print()                                        # call function that will call print
        builtins.print = original_print                             # restore original print

    def test_update_to_json_string(self):
        data = { 'the answer is': 42 , 'random_string': Misc.random_string_and_numbers()}
        self.secrets.update_to_json_string(data)
        assert self.secrets.value_from_json_string() == data

    def test_value(self):
        temp_value = Misc.random_string_and_numbers()
        self.secrets.update(temp_value)
        assert self.secrets.value() == temp_value

        assert self.secrets.set_id('abcd').value() is None


    # bugs

    def test_bug__delete_no_recovery__is_not_deleting_it_strait_away(self):
        assert self.secrets.exists()             is True              # confirm secret exists
        assert self.secrets.delete_no_recovery() is True              # this should delete immediately
        assert self.secrets.exists()             is False             # confirm secret doesn't exist
        assert self.secrets.deleted()            is True              # (bug) confirm is marked for deletion (vs already deleted)
        assert self.secrets.create('abc')        is False             # (bug) confirm we can't create a new one with same name
