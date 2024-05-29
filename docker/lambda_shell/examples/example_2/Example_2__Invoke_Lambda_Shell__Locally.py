import requests
from unittest import TestCase


from docker.lambda_shell                             import examples
from osbot_aws.apis.shell.Shell_Client__Local_Docker import Shell_Client__Lambda__Local
from osbot_utils.utils.Dev                           import pprint
from osbot_utils.utils.Env                           import load_dotenv
from osbot_utils.utils.Files                         import parent_folder, path_combine
from osbot_utils.utils.Process                       import run_process


class Docker_Composer__Build_And_Run:

    def __init__(self, cwd_folder):
        self.cwd_folder = cwd_folder

    def build(self):
        result = run_process('docker-compose', ['build'], cwd=self.cwd_folder)
        return result.get('stderr')

    def logs(self, service_name=''):
        # docker compose  logs osbot_aws__lambda
        params = ['logs']
        if service_name:
            params.append(service_name)
        result = run_process('docker-compose', params, cwd=self.cwd_folder)
        return result.get('stdout')

    def down(self):
        result = run_process('docker-compose', ['down'], cwd=self.cwd_folder)
        return result.get('stderr')

    def up(self):
        result = run_process('docker-compose', ['up', '-d'], cwd=self.cwd_folder)
        return result.get('stderr')

class Example_2__Invoke_Lambda_Shell__Locally:


    def __init__(self):
        self.cwd_folder = parent_folder(examples.path)
        self.url_invoke = "http://localhost:9000/2015-03-31/functions/function/invocations"
        self.docker_composer = Docker_Composer__Build_And_Run(self.cwd_folder)

    def build_and_run(self):
        payload       = {}
        result_build  = self.docker_composer.build()
        result_up     = self.docker_composer.up   ()
        result_invoke = self.make_request         (payload)
        result_logs   = self.docker_composer.logs ()
        result_down   = self.docker_composer.down ()

        #pprint(result_build )
        #pprint(result_up    )
        pprint(result_invoke)
        #print(result_logs   )
        #pprint(result_down  )

    def just_start(self):
        return self.docker_composer.up()

    def just_stop(self):
        return self.docker_composer.up()

    def make_request(self, payload):
        return requests.post(self.url_invoke, json=payload).json()


class test_Example_2__Invoke_Lambda_Shell__Locally(TestCase):

    def setUp(self):
        self.example = Example_2__Invoke_Lambda_Shell__Locally()

    def test_1_just_start(self):
        self.example.just_start()

    def test_2_invoke_lambda(self):
        result = self.example.make_request({})
        pprint(result)

    def test_2_invoke_lambda_shell(self):
        env_file = path_combine(__file__, '../.env')
        load_dotenv(env_file)
        lambda_shell = Shell_Client__Lambda__Local()
        assert lambda_shell.ping() == 'pong'
        assert lambda_shell.pwd () == '/var/task\n'

        def the_answer():
            return f'is {40+2}'

        assert lambda_shell.exec_function(the_answer) == 'is 42'


    def test_3_just_stop(self):
        self.example.just_start()

    def test_build_and_run(self):
        self.example.build_and_run()



if __name__ == '__main__':
    Example_2__Invoke_Lambda_Shell__Locally().build_and_run()