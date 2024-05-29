import requests
from unittest                   import TestCase
from docker.lambda_shell        import examples
from osbot_utils.utils.Dev      import pprint
from osbot_utils.utils.Files    import parent_folder
from osbot_utils.utils.Process  import run_process


class Example_1__Build_And_Run:

    def __init__(self):
        self.cwd_folder = parent_folder(examples.path)
        self.url_invoke = "http://localhost:9000/2015-03-31/functions/function/invocations"

    def docker_compose_build(self):
        result = run_process('docker-compose', ['build'], cwd=self.cwd_folder)
        return result.get('stderr')

    def docker_compose_logs(self, service_name=''):
        # docker compose  logs osbot_aws__lambda
        params = ['logs']
        if service_name:
            params.append(service_name)
        result = run_process('docker-compose', params, cwd=self.cwd_folder)
        return result.get('stdout')

    def docker_compose_up(self):
        result = run_process('docker-compose', ['up', '-d'], cwd=self.cwd_folder)
        return result.get('stderr')

    def docker_compose_down(self):
        result = run_process('docker-compose', ['down'], cwd=self.cwd_folder)
        return result.get('stderr')

    def make_request(self, payload):
        return requests.post(self.url_invoke, json=payload).json()

    def main(self):
        payload       = {}
        result_build  = self.docker_compose_build()
        result_up     = self.docker_compose_up   ()
        result_invoke = self.make_request        (payload)
        result_logs   = self.docker_compose_logs()
        result_down = self.docker_compose_down   ()

        pprint(result_up    )
        pprint(result_build    )
        pprint(result_invoke )
        print(result_logs   )
        pprint(result_down  )


class test_Example_1__Build_And_Run(TestCase):

    def setUp(self):
        self.example = Example_1__Build_And_Run()

    def test_main(self):
        self.example.main()

if __name__ == '__main__':
    Example_1__Build_And_Run().main()