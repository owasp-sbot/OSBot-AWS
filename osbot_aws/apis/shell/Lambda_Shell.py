import uuid
from functools import wraps

from osbot_aws.apis.Secrets import Secrets
from osbot_aws.apis.shell.Shell_Server import Shell_Server
from osbot_utils.utils.Misc import random_uuid


def lambda_shell(function):
    @wraps(function)
    def wrapper(event, context=None):

        exec_result = Shell_Server().invoke(event)
        if exec_result and exec_result.get('method_invoked'):
            return exec_result.get('return_value')

        return function(event, context)
    return wrapper

class Lambda_Shell:
    def __init__(self):
        self.secret_id = 'lambda_shell_auth'

    def get_lambda_shell_auth(self):
        return Secrets(self.secret_id).value_from_json_string()

    def reset_lambda_shell_auth(self):
        value = {'key' : random_uuid() }
        return Secrets(self.secret_id).update_to_json_string(value)