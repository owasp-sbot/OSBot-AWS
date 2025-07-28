from osbot_utils.utils.Env                                   import set_env
from osbot_aws.testing.Temp__Random__AWS_Credentials         import Temp_AWS_Credentials
from osbot_local_stack.local_stack.Local_Stack               import Local_Stack
from osbot_utils.type_safe.Type_Safe                         import Type_Safe

OSBOT_AWS__TEST__AWS_ACCOUNT_ID     = '000000000000'               # default local-stack account id for lambdas
OSBOT_AWS__TEST__AWS_DEFAULT_REGION = 'us-east-1'                  # default local-stack region for lambdas

class OSBot_AWS__Integration_Tests(Type_Safe):
    local_stack     : Local_Stack           = None
    setup_completed : bool                  = False

osbot_aws_integration_tests = OSBot_AWS__Integration_Tests()

def setup_local_stack() -> Local_Stack:                                         # todo: refactor this to the OSBot_Local_Stack code base
    Temp_AWS_Credentials().set_vars()
    set_env('AWS_ACCOUNT_ID'    , OSBOT_AWS__TEST__AWS_ACCOUNT_ID    )         # todo: fix the Temp_AWS_Credentials so that we don't need use this set_env
    set_env('AWS_DEFAULT_REGION', OSBOT_AWS__TEST__AWS_DEFAULT_REGION)
    local_stack = Local_Stack().activate()
    return local_stack

def setup__osbot_aws__integration_tests():
    with osbot_aws_integration_tests as _:
        if osbot_aws_integration_tests.setup_completed is False:                # make sure we only do the setup once
            _.local_stack      = setup_local_stack()
            _.setup_completed  = True
    return osbot_aws_integration_tests
