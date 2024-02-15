from datetime import timedelta
from unittest import TestCase
from unittest.mock import patch, call

import botocore
from botocore.client import BaseClient
from botocore.loaders import Loader
from dotenv import load_dotenv

from osbot_utils.helpers.Print_Table import Print_Table
from osbot_utils.testing.Patch_Print import Patch_Print
from osbot_utils.utils.Call_Stack import call_stack_current_frame, call_stack_frames_data
from osbot_utils.utils.Misc import list_set

from osbot_utils.utils.Files import pickle_save_to_file, pickle_load_from_file

from osbot_utils.testing.Hook_Method import Hook_Method

from osbot_utils.utils.trace.Trace_Call import Trace_Call

from osbot_aws.aws.iam.IAM import IAM
from osbot_utils.utils.Dev import pprint

from osbot_utils.testing.Duration import Duration

from osbot_aws.aws.boto3.View_Boto3_Rest_Calls import View_Boto3_Rest_Calls


class test_View_Boto3_Rest_Calls(TestCase):

    def setUp(self):
        self.view_bobo3_rest_calls = View_Boto3_Rest_Calls()
        self.iam = IAM()

    def test___init__(self):
        assert self.view_bobo3_rest_calls.target_module         is BaseClient
        assert self.view_bobo3_rest_calls.target_method         == "_make_api_call"
        assert self.view_bobo3_rest_calls.hook_method           is None
        assert self.view_bobo3_rest_calls.config__print_calls   is True
        assert type(self.view_bobo3_rest_calls.total_duration)  is Duration

    def test___enter__exit__(self):
        print();print()

        def _make_api_call(*args, **kwargs):
            if args[1] == 'ListBuckets':
                return {'Buckets': [{'Name': 'bucket-1'}, {'Name': 'bucket-2'}]}
            #print(f'in _make_api_call ....')
            return {}

        self.view_bobo3_rest_calls.config__print_calls = False

        with self.view_bobo3_rest_calls as hook_method:
            #hook_method.set_mock_call(_make_api_call)
            self.iam.caller_identity()
            self.iam.account_id()
            #self.iam.caller_identity()
        self.view_bobo3_rest_calls.total_duration.set_duration(0.3)

        self.view_bobo3_rest_calls.print_calls()

        #return
        # with Patch_Print() as patched:
        #     self.view_bobo3_rest_calls.print_calls()
        # #
        # assert patched.call_args_list() == [ call(),
        #                                      call(),
        #                                      call('|-------------------------------------------------------------------------------------|' ),
        #                                      call('| BOTO3 REST calls (via BaseClient._make_api_call)                                    |' ),
        #                                      call('|-------------------------------------------------------------------------------------|' ),
        #                                      call('| #  | Method                 | Duration | Params                                     | Return Value                               |'),
        #                                      call('|-------------------------------------------------------------------------------------|' ),
        #                                      call("|  0 | GetCallerIdentity      |     0 ms | ('GetCallerIdentity', {}) | {}     |"         ),
        #                                      call('|-------------------------------------------------------------------------------------|'),
        #                                      call('| Total Duration:    0.3 secs | Total calls: 1          |'                               ),
        #                                      call('|-------------------------------------------------------------------------------------|')]

        #pprint(mock_print.call_args_list)
            # def load_service_model(*args, **kwargs):
            #     print('in load_service_model')
            #     pickle_file = '/var/folders/sj/ks1b_pjd749gk5ssdd1769kc0000gn/T/tmpu6y0igtd.pickle'
            #     pickle_data = pickle_load_from_file(pickle_file)
            #     if args[2] == 'service-2':
            #         return pickle_data[0].get('return_value')
            #     else:
            #         return pickle_data[1].get('return_value')

            # with Hook_Method(botocore.session.Session, 'create_client') as hook_create_client:
            #     self.iam.caller_identity()

            # with Hook_Method(Loader, 'load_service_model') as hook_service_model:
            #     hook_service_model.set_mock_call(load_service_model)
            # assert hook_method.target_module is BaseClient
            # assert hook_method.target_method == "_make_api_call"

            #pprint(hook_method.calls)
                # with Trace_Call() as _:
                #     _.config.duration(0.1).all(20).show_parent_info = True
                #     self.iam.caller_identity()
            #self.iam.caller_identity()
            #self.iam.caller_identity()
        #pprint(hook_method.calls)
        #     assert hook_method.hook_method   is not None
        #     assert hook_method.on_exit_print_calls is True
        #     assert type(hook_method.total_duration) is Duration
        # assert hook_method.hook_method is None

class test_ABC(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.view_bobo3_rest_calls = View_Boto3_Rest_Calls()
        cls.iam = IAM()

    def test_1(self):
        sts = self.iam.sts()

    def test_2(self):
        with self.view_bobo3_rest_calls:
            self.iam.caller_identity()

        with self.view_bobo3_rest_calls:
            self.iam.caller_identity()

    def test_3(self):
        with Duration():
            self.iam.caller_identity()

    def test_4(self):
        with self.view_bobo3_rest_calls:
            self.iam.caller_identity()

    def test_5(self):
        with Trace_Call() as _:
            _.config.duration(0.1).all()
            self.iam.caller_identity()

    def test_6(self):
        with self.view_bobo3_rest_calls:
            self.iam.caller_identity()
