from unittest import TestCase
from osbot_aws.apis.shell.Shell_Client import Shell_Client
from osbot_aws.apis.shell.Lambda_Shell import lambda_shell, Lambda_Shell, add_lambda_shell_decorator
from osbot_aws.apis.Lambda import Lambda
from osbot_aws.helpers.S3_Zip_From_Files import S3_Zip_From_Files
from osbot_aws.apis.test_helpers.Temp_Lambda                  import Temp_Lambda
from osbot_aws.helpers.Lambda_Layers_OSBot import Lambda_Layers_OSBot

from osbot_utils.utils.Dev import pprint

from osbot_aws.helpers.Lambda_From_S3 import Lambda_From_S3
from osbot_utils.utils.Functions import function_source_code


#@lambda_shell

def run(event, context=None):
    from osbot_aws.aws.s3.S3   import S3
    from osbot_utils.utils.Zip import unzip_file
    from osbot_utils.utils.Zip import zip_bytes_to_file
    s3              = S3()
    s3_key          = event.get('s3_key')
    s3_bucket       = event.get('s3_bucket')
    zip_bytes       = s3.file_bytes(s3_bucket, s3_key)
    target_file     = '/tmp/temp_lambda.zip'
    target_folder   = '/tmp/temp_lambda'

    zip_bytes_to_file(zip_bytes, target_file)
    result = unzip_file(target_file, target_folder)
    #files     = zip_bytes_file_list(zip_bytes)

    return f"testing lambda from S3 .... :{result}"

def exec_inside_lambda():
    from osbot_utils.utils.Files import files_list
    from osbot_utils.utils.Files import file_contents
    return file_contents('/tmp/temp_lambda/test.txt')


class test_Lambda_From_S3(TestCase):

    def setUp(self):
        self.lambda_from_s3 = Lambda_From_S3()
        self.osbot_layers   = Lambda_Layers_OSBot()
        self.file_name      = 'temp_lambda_1'
        self.s3_zip_file    = S3_Zip_From_Files(file_name=self.file_name)
        self.event          = dict(s3_key = self.s3_zip_file.s3_key, s3_bucket= self.s3_zip_file.s3_bucket)

    def test_run__locally(self):

        print()
        # with self.s3_zip_file as _:
        #     _.add_file_from_content('test.txt', 'hello world')
        #     _.s3_file_create()
        result = run(self.event)
        pprint(result)

    def test_run__using_temp_lambda(self):
        print()
        delete_on_exit = True
        lambda_code    = add_lambda_shell_decorator(function_source_code(run))
        lambda_layer   = self.osbot_layers.osbot_aws()
        with Temp_Lambda(lambda_code=lambda_code, with_layer=lambda_layer, delete_on_exit=delete_on_exit) as _:
            pprint(_.invoke(self.event))
            pprint(_.lambda_name)
            pprint(_.info())

    def test_invoke_temp_lambda(self):
        #lambda_name     = 'temp_lambda_0F3KOJ'
        lambda_name      = 'temp_lambda_NP91GR'
        lambda_function = Lambda(lambda_name)
        assert lambda_function.exists() is True

        shell_client = Shell_Client(lambda_function)
        #pprint(shell_client.exec('touch', ['/var/task/aaa.txt']))
        #pprint((shell_client.pwd()))
        print()
        print(shell_client.ls('/tmp/temp_lambda'))
        print(shell_client.python_exec_function(exec_inside_lambda) )
        return

        # result = lambda_function.invoke(self.event)
        # pprint(result)
        #lambda_shell.reset_lambda_shell_auth()
        payload = {'shell': {'method_name': 'ping', 'auth_key': lambda_shell.get_lambda_shell_auth()}}
        pprint(payload)
        result = lambda_function.invoke(payload)
        pprint(result)
        #assert lambda_run(payload) == 'pong'

        #lambda_function.delete()
        #assert lambda_function.exists() is False

