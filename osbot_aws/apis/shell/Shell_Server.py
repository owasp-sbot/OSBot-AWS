from osbot_utils.utils.Process import Process


class Shell_Server:

    def invoke(self, event):
        shell         = event.get('shell', {})
        method_name   = shell.get('method_name')
        method_kwargs = shell.get('method_kwargs')
        if method_name:
            if hasattr(Shell_Server,method_name):
                method = getattr(Shell_Server, method_name)
                if type(method_kwargs) is dict:
                    return method(**method_kwargs)
                else:
                    return method()

    @staticmethod  # note: this method by design allows extra commands injection via | and ;
    def bash(command, cwd=None):
        bash_command = 'bash'
        bash_params  = ['-c', command]
        return Shell_Server.process_run(bash_command, bash_params, cwd)


    @staticmethod
    def process_run(executable, params=None, cwd='.'):
        return Process.run(executable,params, cwd)

    @staticmethod
    def ping():
        return 'pong'

    # helper process_run methods
    @staticmethod
    def pwd():
        return Shell_Server.process_run('pwd').get('stdout')