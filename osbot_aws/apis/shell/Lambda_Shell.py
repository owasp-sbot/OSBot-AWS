from functools import wraps

from osbot_utils.decorators.methods.cache import cache

from osbot_aws.apis.Secrets import Secrets
from osbot_aws.apis.shell.Shell_Server import Shell_Server

from osbot_utils.utils.Misc import random_uuid

SHELL_VAR                = 'lambda_shell'
SHELL_VAR_AUTH_KEY       = 'auth_key'
SHELL_VAR_METHOD_NAME    = 'method_name'
SHELL_VAR_METHOD_KWARDS  = 'method_kwargs'
SHELL_VAR_METHOD_INVOKED = 'method_invoked'
SHELL_VAR_RETURN_VALUE   = 'return_value'

# decorator
def lambda_shell(function):
    @wraps(function)
    def wrapper(event, context=None):

        shell_server = Lambda_Shell(event.get(SHELL_VAR))
        if shell_server.valid_shell_request():
            return shell_server.invoke()
        return function(event, context)
    return wrapper

class Lambda_Shell:
    def __init__(self, shell_command=None):
        self.secret_id     = 'lambda_shell_auth'
        self.shell_command = shell_command or {}

    @cache                                                   # cache this value since it doesn't change in the lifetime of a lambda function
    def get_lambda_shell_auth(self):
        return Secrets(self.secret_id).value_from_json_string().get('key')

    def reset_lambda_shell_auth(self):
        value = {'key' : random_uuid() }
        return Secrets(self.secret_id).update_to_json_string(value)

    def valid_shell_request(self):                             # also checks the AUTH
        if self.shell_command:
            if self.shell_command.get(SHELL_VAR_METHOD_NAME):
                expected_auth_key = self.get_lambda_shell_auth()
                request_auth_key = self.shell_command.get(SHELL_VAR_AUTH_KEY)
                if expected_auth_key and request_auth_key and expected_auth_key == request_auth_key:
                    return True
        return False

    def invoke(self):
        exec_result = Shell_Server().invoke(self.shell_command)
        if exec_result and exec_result.get(SHELL_VAR_METHOD_INVOKED):
            return exec_result.get(SHELL_VAR_RETURN_VALUE)