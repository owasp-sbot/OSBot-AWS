from osbot_aws.testing.Temp__Random__AWS_Credentials         import Temp_AWS_Credentials
from osbot_local_stack.local_stack.Local_Stack               import Local_Stack
from osbot_utils.type_safe.Type_Safe                         import Type_Safe


class OSBot_AWS__Integration_Tests(Type_Safe):
    local_stack     : Local_Stack           = None
    setup_completed : bool                  = False

osbot_aws_integration_tests = OSBot_AWS__Integration_Tests()

def setup_local_stack() -> Local_Stack:                                         # todo: refactor this to the OSBot_Local_Stack code base
    Temp_AWS_Credentials().with_localstack_credentials()
    local_stack = Local_Stack().activate()
    return local_stack

def setup__osbot_aws__integration_tests():
    with osbot_aws_integration_tests as _:
        if osbot_aws_integration_tests.setup_completed is False:                # make sure we only do the setup once
            _.local_stack      = setup_local_stack()
            _.setup_completed  = True
    return osbot_aws_integration_tests
