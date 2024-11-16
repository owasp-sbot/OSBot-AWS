from unittest import TestCase

from osbot_local_stack.local_stack.Local_Stack import Local_Stack

local_stack = Local_Stack().activate()

def osbot_aws__assert_local_stack():
    assert local_stack.is_local_stack_configuredand_available() is True