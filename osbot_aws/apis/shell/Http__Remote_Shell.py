import requests
from osbot_utils.type_safe.Type_Safe    import Type_Safe
from osbot_utils.utils.Dev              import pprint
from osbot_aws.apis.shell.Shell_Client  import Shell_Client

class Http__Remote_Shell(Type_Safe, Shell_Client):
    target_url: str = None

    def _invoke(self, method_name, method_kwargs=None, return_logs=False):
        auth_key = self._lambda_auth_key()

        payload  = {'lambda_shell': {'method_name'  : method_name    ,
                                     'method_kwargs': method_kwargs  ,
                                     'auth_key'     : auth_key       }}
        response = requests.post(self.target_url, json=payload)
        if response.headers.get('Content-Type') == 'application/json':
            return response.json()
        return response.text.strip()

    def exec_print(self, executable, *params):
        result = self.exec(executable, params)
        pprint(result)
        return result

    def function(self, function):
        return self.python_exec_function(function)

    def function__print(self,function):
        result = self.function(function)
        pprint(result)
        return result

    # helper execution methods

    def env_vars(self):
        def return_dict_environ():
            from os import environ
            return dict(environ)
        return self.function(return_dict_environ)