import base64
from unittest                                                                   import TestCase
from osbot_aws.testing.skip_tests                                               import skip__if_not__in_github_actions
from osbot_utils.testing.Temp_File                                              import Temp_File
from osbot_aws.lambdas.dev.hello_world                                          import run
from osbot_aws.deploy.Deploy_Lambda                                             import Deploy_Lambda
from osbot_utils.utils.Functions                                                import function_source_code
from osbot_aws.apis.test_helpers.Temp_Lambda                                    import Temp_Lambda
from osbot_aws.aws.lambda_.dependencies.Lambda__Dependency                      import Lambda__Dependency
from osbot_utils.utils.Files                                                    import current_temp_folder
from osbot_aws.aws.lambda_.dependencies.Lambda__Dependency__S3                  import Lambda__Dependency__S3
from osbot_utils.type_safe.Type_Safe                                            import Type_Safe
from osbot_aws.aws.lambda_.dependencies.Lambda__Dependency__Base                import Lambda__Dependency__Base
from osbot_utils.utils.Objects                                                  import base_types
from osbot_aws.aws.lambda_.dependencies.Lambda__Dependency__Inside_Lambda       import Lambda__Dependency__Inside_Lambda, FOLDER_NAME__LAMBDA_DEPENDENCIES__INSIDE_LAMBDA
from tests.integration.aws.lambda_.dependencies.test_Lambda__Dependency__Local  import LAMBDA_DEPENDENCY__SMALL_TEST__PACKAGE
from tests.integration.osbot_aws__objs_for__integration_tests                   import setup__osbot_aws__integration_tests

class test_Lambda__Dependency__Inside_Lambda(TestCase):

    @classmethod
    def setUpClass(cls):
        skip__if_not__in_github_actions()
        setup__osbot_aws__integration_tests()
        cls.package_name                    = LAMBDA_DEPENDENCY__SMALL_TEST__PACKAGE
        cls.lambda_dependency               = Lambda__Dependency               (package_name=cls.package_name)
        cls.lambda_dependency_inside_lambda = Lambda__Dependency__Inside_Lambda(package_name=cls.package_name)

    def test__init__(self):
        with self.lambda_dependency_inside_lambda as _:
            assert type(_) is Lambda__Dependency__Inside_Lambda
            assert base_types(_)                == [Lambda__Dependency__Base, Type_Safe, object]
            assert type(_.lambda_dependency_s3) is Lambda__Dependency__S3

    def test_01__setup__install_and_upload(self):
        with self.lambda_dependency.dependency__local as _:                 #
            _.setup  ()
            _.install()
            file_bytes      = _.files__zipped()
            installed_files = _.install__data().installed_files
            assert _.exists() is True

        with self.lambda_dependency.dependency__s3 as _:
            _.setup()
            _.upload(file_bytes=file_bytes)
            assert _.exists() is True
            assert _.files__paths() == installed_files

    def test_02__load(self):
        with self.lambda_dependency_inside_lambda as _:
            result = _.load()
            assert _.exists()     is True
            assert len(_.files()) == 32
            assert result         == True

    def test_03__temp_lambda__with_no_dependencies(self):
        def run(event, context):
            return 'this has no dependencies'

        lambda_code = function_source_code(run)

        with Temp_Lambda(wait_max_attempts=400, lambda_code=lambda_code) as _:
            assert 'temp_lambda_'              in _.aws_lambda.name
            assert _.invoke({'name': 'world'}) == 'this has no dependencies'
            assert _.exists           ()       is True
            assert _.tmp_folder.exists()       is True

        assert _.tmp_folder.exists() is False
        assert _.exists           () is False

    def test_04__temp_lambda__boto_3__list_buckets(self):
        def run(event, context):
            import boto3
            s3       = boto3.client('s3')
            response = s3.list_buckets()
            buckets  = [bucket['Name'] for bucket in response['Buckets']]
            return buckets


        lambda_code = function_source_code(run)

        with Temp_Lambda(wait_max_attempts=100, lambda_code=lambda_code) as _:
            assert _.invoke() == self.lambda_dependency.dependency__s3.s3.buckets()

    def test_05__temp_lambda__boto_3__get_dependency_bytes(self):
        with self.lambda_dependency.dependency__s3 as _:
            assert _.bucket__name() == '000000000000--osbot-lambdas--us-east-1'
            assert  _.path       () == 'lambdas-dependencies/colorama==0.4.6.zip'

        def run(event, context):
            import boto3
            import base64
            s3          = boto3.client('s3')
            bucket_name = '000000000000--osbot-lambdas--us-east-1'              # target s3 bucket
            s3_key      = 'lambdas-dependencies/colorama==0.4.6.zip'            # target s3 key

            response    = s3.get_object(Bucket=bucket_name, Key=s3_key)         # Get the file's bytes
            file_bytes  = response['Body'].read()                               # Read the content of the file as bytes
            file_base64  = base64.b64encode(file_bytes).decode('utf-8')         # Convert the file bytes to Base64
            return file_base64                                                  # Returning the file's Base64 encoded string


        lambda_code = function_source_code(run)

        with Temp_Lambda(wait_max_attempts=100, lambda_code=lambda_code) as _:
            zipped_bytes__base64 = _.invoke()
            zipped_bytes         = base64.b64decode(zipped_bytes__base64)

            assert zipped_bytes == self.lambda_dependency.dependency__s3.bytes()        # confirm it matches the zipped dependency bytes

    def test_06__temp_lambda__boto_3__import_dependency(self):
        def run(event, context):
            import os
            import boto3
            import zipfile
            import sys
            import io
            # S3 details
            bucket_name = '000000000000--osbot-lambdas--us-east-1'
            s3_key      = 'lambdas-dependencies/colorama==0.4.6.zip'

            # Get the zipped bytes from S3
            s3 = boto3.client('s3')
            response = s3.get_object(Bucket=bucket_name, Key=s3_key)
            zip_bytes = response['Body'].read()

            # Step 2: Create a temp folder in /tmp
            temp_folder = '/tmp/lambdas-dependencies/colorama==0.4.6'
            os.makedirs(temp_folder, exist_ok=True)

            # Step 3: Extract the zip bytes into the temp folder
            zip_buffer = io.BytesIO(zip_bytes)
            with zipfile.ZipFile(zip_buffer, 'r') as zip_ref:
                zip_ref.extractall(temp_folder)

            # Step 4: Try to load colorama
            try:
                import colorama
            except ImportError:
                 result__step_4 = "Failed to import colorama."

            # Step 5: Add the extracted folder to sys.path
            sys.path.append(temp_folder)

            # Step 6: Now we can import and use colorama
            # noinspection PyUnresolvedReferences
            import colorama
            colorama.init()                 # Example usage of colorama
            result__step_6 = "Colorama library is ready to use!"

            return dict(result__step_4 = result__step_4,
                        result__step_6 = result__step_6)

        lambda_code = function_source_code(run)

        with Temp_Lambda(wait_max_attempts=100, lambda_code=lambda_code) as _:
            assert  _.invoke() == { 'result__step_4': 'Failed to import colorama.',
                                    'result__step_6': 'Colorama library is ready to use!'}

    def test_7__using_lambda_deploy__hello_world(self):

        handler = run                                               # this is in osbot_aws.lambdas.dev.hello_world
        with Deploy_Lambda(handler=handler) as _:
            assert handler.__module__                      == 'osbot_aws.lambdas.dev.hello_world'
            assert _.lambda_name()                         == 'osbot_aws.lambdas.dev.hello_world'
            assert _.exists()                              is False
            assert _.deploy()                              is True                                  # this will call .add_function_source_code() which will add all the osbot_aws files
            assert _.exists()                              is True
            assert '/osbot_aws/lambdas/dev/hello_world.py' in _.files()  # which include the file in this lambda
            assert _.invoke(dict(name='ABC'))              == 'From lambda code, hello ABC'
            assert _.delete()                              is True
            assert _.exists()                              is False

    def test_08__using_lambda_deploy__run_function_code(self):

        def run(event, context):
            return 'hello from inside lambda in test_8'

        source_code = function_source_code(run)
        module_name = 'test_Lambda__Dependency__Inside_Lambda'
        file_name   = module_name + '.py'

        with Deploy_Lambda(handler=run) as _:
            assert run.__module__                          == module_name
            assert _.lambda_name()                         == module_name
            assert _.exists()                              is False
            with Temp_File(file_name=file_name, contents=source_code, return_file_path=True) as temp_file:
                _.add_file(temp_file)
                assert _.files()                                     == ['/' + file_name]
                assert _.deploy()                                    is True
                assert _.files()                                     == ['/' + file_name]
                assert _.exists()                                    is True
                assert _.invoke(dict(name='ABC'))                    == 'hello from inside lambda in test_8'
                assert _.info().get('Configuration').get('CodeSize') == 249
                assert _.delete()                                    is True
                assert _.exists()                                    is False


    def test_09__using_lambda_deploy__load_dependency__using__osbot_aws(self):
        def run(event, context):
            from osbot_aws.aws.lambda_.dependencies.Lambda__Dependency__Inside_Lambda import Lambda__Dependency__Inside_Lambda
            package_name                     = 'colorama==0.4.6'
            with Lambda__Dependency__Inside_Lambda(package_name=package_name) as _:
                if _.load():
                    # noinspection PyUnresolvedReferences
                    import colorama
                    return f'{colorama}'
                else:
                    return 'failed to import depdenency'

        source_code = function_source_code(run)
        module_name = 'test_Lambda__Dependency__Inside_Lambda'
        file_name   = module_name + '.py'
        with Temp_File(file_name=file_name, contents=source_code, return_file_path=True) as temp_file:
            with Deploy_Lambda(handler=run) as _:
                _.add_file     (temp_file)
                _.add_osbot_aws()
                assert _.deploy() is True
                assert _.info().get('Configuration').get('CodeSize') > 500000           # here is the problem of adding add_osbot_aws just for loading the dependency (we end up having to add 500k of code to the zip file)
                assert _.invoke() == ("<module 'colorama' from "
                                      "'/tmp/osbot-aws__lambda-dependencies__inside-lambda/colorama==0.4.6/colorama/__init__.py'>")
                assert _.delete() is True

    def test_10__using_lambda_deploy__load_dependency__using__osbot_aws__load_dependencies(self):
        def run(event, context):
            from osbot_aws.aws.lambda_.dependencies.Lambda__Dependencies import load_dependency
            package_name                     = 'colorama==0.4.6'

            load_dependency(package_name)
            # noinspection PyUnresolvedReferences
            import colorama
            return f'{colorama}'

        source_code = function_source_code(run)
        module_name = 'test_Lambda__Dependency__Inside_Lambda'
        file_name   = module_name + '.py'

        with Temp_File(file_name=file_name, contents=source_code, return_file_path=True) as temp_file:
            with Deploy_Lambda(handler=run) as _:
                _.add_file     (temp_file)
                _.add_osbot_aws()
                assert _.deploy() is True
                assert _.invoke() == ("<module 'colorama' from "
                                      "'/tmp/osbot-aws__lambda-dependencies__inside-lambda/colorama==0.4.6/colorama/__init__.py'>")
                #assert _.delete() is True

    def test_11__using_lambda_deploy__confirm_we_can_upload_file_with_only_boto3_code(self):

        def run(event, context):                        # this runs inside the lambda environment
            import os
            import types
            assert sorted(os.listdir('/var/task')) == [ 'boto3__lambda.py'                         ,             # confirm the files are added ok to the '/var/task' (which is the folder lambda deployment copies the files from the provided zip folder
                                                        'test_Lambda__Dependency__Inside_Lambda.py']
            # noinspection PyUnresolvedReferences
            import boto3__lambda                                                   # confirm we can import the boto3__lambda module
            assert type(boto3__lambda) is types.ModuleType                         # and that it is a module
            return boto3__lambda.ping()

        # the rest of this code runs locally
        from osbot_aws.aws.lambda_ import boto3__lambda
        source_code = function_source_code(run)
        module_name = 'test_Lambda__Dependency__Inside_Lambda'
        file_name   = module_name + '.py'
        file_to_add = boto3__lambda.__file__


        with Temp_File(file_name=file_name, contents=source_code, return_file_path=True) as lambda_handler:
            with Deploy_Lambda(handler=run) as _:
                _.add_file(file_to_add)
                _.add_file     (lambda_handler)
                assert _.files() == [ '/boto3__lambda.py'    ,
                                      '/test_Lambda__Dependency__Inside_Lambda.py']
                assert _.deploy() is True
                assert _.invoke() == boto3__lambda.ping() == 'pong'
                assert _.info().get('Configuration').get('CodeSize') < 1300                                              # confirm that size of the code uploaded is still very small
                assert _.delete() is True

    def test_12__using_lambda_deploy__load_dependency__using__only_boto_3_code(self):
        def run(event, context):
            # noinspection PyUnresolvedReferences
            from boto3__lambda import load_dependency
            return load_dependency('colorama==0.4.6')

        source_code = function_source_code(run)
        module_name = 'test_Lambda__Dependency__Inside_Lambda'
        file_name   = module_name + '.py'

        with Temp_File(file_name=file_name, contents=source_code, return_file_path=True) as lambda_handler:
            with Deploy_Lambda(handler=run) as _:
                _.add_file__boto3__lambda()
                _.add_file     (lambda_handler)
                assert _.deploy() is True
                assert _.invoke() == 'colorama==0.4.6 (loaded from S3)'
                assert _.info().get('Configuration').get('CodeSize') < 1300                                              # confirm that size of the code uploaded is still very small
                assert _.delete() is True

    def test_dependencies_folder(self):
        with self.lambda_dependency_inside_lambda as _:
            assert _.dependencies_folder() == f'{current_temp_folder()}/osbot-aws__lambda-dependencies__inside-lambda'
            assert _.dependencies_folder() == f'{current_temp_folder()}/{FOLDER_NAME__LAMBDA_DEPENDENCIES__INSIDE_LAMBDA}'

    def test_folder(self):
        with self.lambda_dependency_inside_lambda as _:
            assert _.folder() == f'{_.dependencies_folder()}/colorama==0.4.6'
