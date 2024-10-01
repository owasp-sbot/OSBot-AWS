from osbot_aws.AWS_Config                           import AWS_Config
from osbot_aws.apis.shell.Lambda_Shell              import Lambda_Shell
from osbot_aws.apis.shell.Shell_Server              import Shell_Server
from osbot_aws.aws.lambda_.Lambda                   import Lambda                    # todo: see how to resolve the circular dependency with the Lambda Function
from osbot_utils.decorators.methods.cache_on_self   import cache_on_self
from osbot_utils.utils.Functions                    import function_source_code


class Shell_Client:

    def __init__(self, aws_lambda: Lambda):
        self.aws_lambda = aws_lambda

    @cache_on_self
    def _lambda_auth_key(self):
        return Lambda_Shell().get_lambda_shell_auth()

    def _invoke(self, method_name, method_kwargs=None,return_logs=False):
        event = {'lambda_shell': {'method_name': method_name, 'method_kwargs': method_kwargs}}
        if self.aws_lambda:
            event['lambda_shell']['auth_key'] = self._lambda_auth_key()
            if return_logs:
                return self.aws_lambda.invoke_return_logs(event)
            else:
                return self.aws_lambda.invoke(event)
        else:
            return Shell_Server().invoke(event)

    def bash(self,command, cwd=None):
        return self._invoke('bash', {'command': command, 'cwd': cwd})

    def exec(self, executable, params=None, cwd=None):
        result = self.process_run(executable, params, cwd)
        std_out = result.get('stdout', '').strip()
        std_err = result.get('stderr', '').strip()
        std_console = std_out + std_err
        if std_console:
            return std_console
        if result.get('errorMessage'):
            return f'Error: {result.get("errorMessage")}'
        return result

    def exec_function(self, function, return_logs=False):
        return self.python_exec_function(function,return_logs=return_logs)

    def exec_function_return_logs(self, function):
        return self.python_exec_function(function,return_logs=True)

    def process_run(self, executable, params=None, cwd=None):
        return self._invoke('process_run', {'executable' : executable , 'params': params, 'cwd': cwd} )

    def reset(self):
        if self.aws_lambda.s3_bucket is None:                                                                     # if these values are not set
            self.aws_lambda.set_s3_bucket(AWS_Config().lambda_s3_bucket())                                               # use default values
            self.aws_lambda.set_s3_key   (f'{AWS_Config().lambda_s3_folder_lambdas()}/{self.aws_lambda.original_name}.zip')  # which are needed
        return self.aws_lambda.update_lambda_code()                                                               # to trigger the update (which will reset the lambda and force a cold start on next lambda invocation)

    def python_exec(self, code, return_logs=False):
        return self._invoke('python_exec', {'code' : code}, return_logs=return_logs)

    def python_exec_function(self, function, return_logs=False):
        function_name = function.__name__
        function_code = function_source_code(function)
        exec_code     = f"{function_code}\nresult= {function_name}()"
        return self.python_exec(exec_code, return_logs=return_logs)

    # command methods

    def ls(self, path='', cwd='.'):         # todo: fix vuln: this method allows extra process executions via ; and |
        return self.bash(f'ls {path}', cwd).get('stdout')


    def file_contents(self, path):return self._invoke('file_contents',{'path': path})

    # with not params

    def disk_space    (self): return self._invoke('disk_space'    )
    def list_processes(self): return self._invoke('list_processes')
    def memory_usage  (self): return self._invoke('memory_usage'  )
    def ping          (self): return self._invoke('ping'          )
    def ps            (self): return self.exec   ('ps'            )
    def pwd           (self): return self._invoke('pwd'           )
    def whoami        (self): return self.exec   ('whoami'        )