from unittest import TestCase

from pbx_gs_python_utils.utils.Dev import Dev
from pbx_gs_python_utils.utils.Misc import Misc

from osbot_aws.apis.Parameter import Parameter


class test_Parameters(TestCase):

    def setUp(self):
        self.name   = 'test_param'
        self.value  = 'an value'
        self.param = Parameter(self.name)
        self.result = None
        if self.param.exists() is False:            #  todo: move this to class methods
            self.param.create(self.value)

    def tearDown(self):
        if self.result is not None:
            Dev.pprint(self.result)
        self.param.delete()                         #  todo: move this to class methods

    def test_ssm(self):
        assert type(self.param.ssm()).__name__ == 'SSM'

    def test_delete(self):
        assert self.param.delete() is True

    def test_list(self):
        assert self.name in set(self.param.list())

    def test_get(self):
        assert self.param.set_name('aaa_bbbb').get() is None

    def test_put(self):
        value = Misc.random_string_and_numbers()
        assert self.param.get().get('Type') =='String'
        self.param.put(value)
        assert self.param.value() == value

    def test_push_pull(self):
        data = {'answer' : 42}
        self.param.push(data)
        assert  self.param.pull() == data

    def test_push_pull__secret(self):
        data = {'answer is a secret' : 42}
        self.param.push_secret(data)
        assert  self.param.pull_secret() == data

    def test_put_secret(self):
        value = Misc.random_string_and_numbers()
        self.param.put_secret(value)
        assert value              == self.param.value_secret()
        assert self.param.value() != self.param.value_secret()

    def test_value(self):
        self.result = self.param.value()


