from osbot_aws.Globals import Globals
from osbot_aws.apis.shell.Lambda_Shell import Lambda_Shell
from osbot_aws.apis.shell.Shell_Server import Shell_Server
from osbot_aws.apis.Lambda import Lambda                    # todo: see how to resolve the circular dependency with the Lambda Function


class Shell_Client:

    def __init__(self, aws_lambda: Lambda):
        self.aws_lambda = aws_lambda

    def _lambda_auth_key(self):
        return Lambda_Shell().get_lambda_shell_auth()

    def _invoke(self, method_name, method_kwargs=None):
        event = {'lambda_shell': {'method_name': method_name, 'method_kwargs': method_kwargs}}
        if self.aws_lambda:
            event['lambda_shell']['auth_key'] = self._lambda_auth_key()
            return self.aws_lambda.invoke(event)
        else:
            return Shell_Server().invoke(event)

    def exec(self, executable, params=None, cwd=None):
        return self.process_run(executable, params, cwd).get('stdout').strip()

    def bash(self,command, cwd=None):
        return self._invoke('bash', {'command': command, 'cwd': cwd})

    def process_run(self, executable, params=None, cwd=None):
        return self._invoke('process_run', {'executable' : executable , 'params': params, 'cwd': cwd} )

    def reset(self):
        if self.aws_lambda.s3_bucket is None:                                                                     # if these values are not set
            self.aws_lambda.set_s3_bucket(Globals.lambda_s3_bucket)                                               # use default values
            self.aws_lambda.set_s3_key   (f'{Globals.lambda_s3_key_prefix}/{self.aws_lambda.original_name}.zip')  # which are needed
        return self.aws_lambda.update_lambda_code()                                                               # to trigger the update (which will reset the lambda and force a cold start on next lambda invocation)

    def python_exec(self, code):
        return self._invoke('python_exec', {'code' : code})

    # command methods

    def ls(self, path='', cwd='.'):         # todo: fix vuln: this method allows extra process executions via ; and |
        return self.bash(f'ls {path}', cwd).get('stdout')


    def file_contents(self, path):return self._invoke('file_contents',{'path': path})

    # with not params
    def list_processes(self): return self._invoke('list_processes')
    def memory_usage  (self): return self._invoke('memory_usage')
    def ping          (self): return self._invoke('ping')
    def pwd           (self): return self._invoke('pwd')
    def whoami        (self): return self.exec('whoami')