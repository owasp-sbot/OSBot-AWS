import requests

from osbot_aws.apis.shell.Shell_Client import Shell_Client

DOCKER__LAMBDA__INVOKE_URL ="http://localhost:9000/2015-03-31/functions/function/invocations"

class Shell_Client__Lambda__Local(Shell_Client):

    def __init__(self, invoke_url=None):
        self.invoke_url = invoke_url or DOCKER__LAMBDA__INVOKE_URL

    def _invoke(self, method_name, method_kwargs=None, return_logs=False):
        auth_key = self._lambda_auth_key()
        payload = {'lambda_shell': {'method_name'  : method_name    ,
                                    'method_kwargs': method_kwargs  ,
                                    'auth_key'     : auth_key       }}
        return requests.post(self.invoke_url, json=payload).json()