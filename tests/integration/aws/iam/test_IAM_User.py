from unittest import TestCase
import pytest

from osbot_utils.utils.trace.Trace_Call import trace_calls

from osbot_aws.AWS_Config                                   import AWS_Config
from osbot_utils.utils.Misc                                 import random_password
from osbot_aws.aws.iam.IAM_User                             import IAM_User
from tests.integration._caches.OSBot__Unit_Test_User import OSBot__Unit_Test_User


class test_IAM_User(TestCase):
    user_name : str

   #@classmethod
    # @trace_calls(include=['test','osb'], contains=['load_dotenv'], show_types=True,
    #              show_lines=True, title='in setup', show_locals=False, show_internals=True,
    #              print_traces=False, print_lines=True)
    def setUp(cls):
        cls.asw_config      = AWS_Config()
        cls.user_name       = 'OSBot__Unit_Test_User'
        cls.test_data       = OSBot__Unit_Test_User()
        cls.user            = IAM_User(cls.user_name)
        cls.test_data._user = cls.user                  # make sure we are using the same object here


    # def tearDown(self):
    #     self.test_data._cache_delete()

    # @trace_calls(include        = ['osbot' , 'test'     ],
    #              ignore         = ['codecs' ,'pprint', 'osbot_utils',
    #                                'dotenv', 'posixpath', 're'],
    #              title          = 'in method',
    #              enabled        = False,
    #              show_class     = True ,
    #              show_locals    = True ,
    #              extra_data     = False ,
    #              show_types=True,
    #              show_internals = True ,
    #              source_code    = False,
    #              show_lines     = False ,
    #              print_traces   = True ,
    #              print_lines    = False )
    # #@print_boto3_calls
    # def test_abc(self):
    #     print()
    #     print()
    #     def start_here():
    #         a = 123
    #         with View_Boto3_Rest_Calls() as boto3_calls:
    #             pprint(self.user.access_keys())
    #             # self.test_data.data__access_keys = None
    #             # result = self.test_data.access_keys
    #             # #self.test_data.abc = 123
    #             # print(result)
    #             # #pprint(self.test_data._cache_data())
    #     start_here()
    #
    #
    # def test_tracing(self):
    #     trace_call = Trace_Call()
    #     trace_call.config.locked()
    #
    #     with trace_call.config as _:
    #         _.capture("*")
    #         _.all()
    #         _.locals()
    #         #_.deep_copy_locals = True
    #         #_.show_method_class = True
    #         #_.show_parent_info = True
    #         #_.lines()
    #         #_.print_config()
    #         _.print_traces_on_exit = False
    #
    #     with trace_call:
    #
    #         def an_method(b,c):
    #             #ob = obj_data(locals())
    #             a_1 = 2 +b
    #             c['a'] = a_1
    #             return a_1
    #         def an_answer(c):
    #             a_2 = 1
    #             c['a'] = 2
    #             a_2 = an_method(a_2, c)
    #             a_2 = an_method(a_2, c)
    #             a_2 = an_method(a_2, c)
    #             pprint(c)
    #             return a_2
    #         an_answer({'a' : 1})
    #
    #     pprint(trace_call.stats())
    #     #pprint(trace_call.stack.root_node.all_children())
    #     #for node in trace_call.stack.root_node.all_children():
    #     #    print(node.locals)
    #     def replace(*args, **kwargs):
    #         print(args, kwargs)
    #
    #     #globals().get('pprint').__globals__.get('original_pprint').pprint = replace
    #     globals().get('pprint').__globals__.get('original_pprint').pprint = replace
    #     pprint('aaaa')
    #     #pprint(trace_call.view_data())


    def test_arn(self):
        self.result = self.user.arn()

    @pytest.mark.skip('refactor to use a temp user name, i.e. not the main one used for the other tests')
    def test_create_exists_delete(self):
        assert self.user.create().get('UserName') == self.user_name
        assert self.user.exists() is True
        assert self.user.delete() is True
        assert self.user.exists() is False

    # @trace_calls(contains=['request'], include=['osbot', '_boto3'],
    #              show_locals=True, max_string=200,extra_data=True,
    #              print_traces=True, print_lines=False, show_types=True,show_class=True)
    def test_access_keys(self):
        result = self.user.access_keys()
        assert result == []

    def test_groups(self):
        result = self.user.groups(index_by='group_name')
        assert result == {}

    def test_user_id(self):
        assert self.user.user_id() == self.test_data.user_id()

    def test_info(self):
        cache_user_info = self.test_data.user_info
        result          = self.user.info()
        result['create_date']  = str(result.get('create_date'))
        assert result == { 'arn'                 : cache_user_info.get('Arn'        ),
                           'create_date'         : cache_user_info.get('CreateDate' ),
                           'password_last_used'  : None,
                           'path'                : cache_user_info.get('Path'       ),
                           'permissions_boundary': None,
                           'tags'                : None,
                           'user_id'             : cache_user_info.get('UserId'     ),
                           'user_name'           : cache_user_info.get('UserName'   )}

    def test_policies(self):
        assert self.user.policies() == []

    def test_set_password(self):

        result = self.user.set_password(random_password(), reset_required=False)
        if result.get('error'):         # todo: figure out why this test returns this error the 2nd time
            assert result.get('error') == 'An error occurred (EntityAlreadyExists) when calling the ' \
                                          'CreateLoginProfile operation: Login Profile for user '     \
                                          'OSBot__Unit_Test_User already exists.'

    # def test_roles(self):
    #     roles = self.user.roles()
    #
    #     pprint(roles)

    def test_tags(self):
        assert self.user.tags() is None
