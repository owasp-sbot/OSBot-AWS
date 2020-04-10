from osbot_aws.apis.Lambda import Lambda
from osbot_aws.apis.shell.Shell_Server import Shell_Server


class Shell_Client:

    def __init__(self, lambda_name=None):
        self.lambda_name = lambda_name

    def _invoke(self, method_name, method_kwargs=None):
        event = {'shell': {'method_name': method_name, 'method_kwargs': method_kwargs}}
        if self.lambda_name:
            return Lambda(self.lambda_name).invoke(event)
        else:
            return Shell_Server().invoke(event)

    def exec(self, executable, params=None, cwd=None):
        return self.process_run(executable, params, cwd).get('stdout').strip()

    def bash(self,command, cwd=None):
        return self._invoke('bash', {'command': command, 'cwd': cwd})

    def ls(self, path='', cwd='.'):         # todo: fix vuln: this method allows extra process executions via ; and |
        return self.bash(f'ls {path}', cwd).get('stdout')

    def process_run(self, executable, params=None, cwd=None):
        return self._invoke('process_run', {'executable' : executable , 'params': params, 'cwd': cwd} )

    def pwd(self):
        return self._invoke('pwd')