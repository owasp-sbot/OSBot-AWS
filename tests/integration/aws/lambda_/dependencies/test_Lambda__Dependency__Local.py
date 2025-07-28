from unittest                                                           import TestCase
from osbot_utils.utils.Zip                                              import zip_bytes__file_list, zip_bytes__files
from osbot_aws.AWS_Config                                               import AWS_Config, DEFAULT__BUCKET_NAME__INFIX__LAMBDA
from osbot_aws.aws.lambda_.schemas.Safe_Str__File__Name__Python_Package import Safe_Str__File__Name__Python_Package
from osbot_utils.utils.Objects                                          import __
from osbot_utils.utils.Files                                            import file_exists, folder_exists, current_temp_folder, path_combine, file_bytes
from osbot_aws.aws.lambda_.dependencies.Lambda__Dependency__Local       import Lambda__Dependency__Local, Schema__Lambda__Dependency__Local_Install__Data, FOLDER_NAME__LAMBDA_DEPENDENCIES_STORAGE
from tests.integration.osbot_aws__objs_for__integration_tests           import setup__osbot_aws__integration_tests, OSBOT_AWS__TEST__AWS_ACCOUNT_ID, OSBOT_AWS__TEST__AWS_DEFAULT_REGION

LAMBDA_DEPENDENCY__SMALL_TEST__PACKAGE = 'colorama==0.4.6'


class test_Lambda__Dependency__Local(TestCase):

    @classmethod
    def setUpClass(cls):
        setup__osbot_aws__integration_tests()
        cls.package_name            = LAMBDA_DEPENDENCY__SMALL_TEST__PACKAGE
        cls.lambda_dependency_local = Lambda__Dependency__Local(package_name=cls.package_name)

    @classmethod
    def tearDownClass(cls):
        with cls.lambda_dependency_local as _:
            if _.exists():
                assert _.delete() is True
                assert _.delete() is False
                assert _.exists() is False


    def test__init__(self):
        with self.lambda_dependency_local as _:
            assert type(_              ) is Lambda__Dependency__Local
            assert type(_.aws_config   ) is AWS_Config
            assert type(_.package_name ) is Safe_Str__File__Name__Python_Package
            assert _.base_folder()       == current_temp_folder()
            assert _.package_name        == LAMBDA_DEPENDENCY__SMALL_TEST__PACKAGE
            assert _.package_name        == 'colorama==0.4.6'
            assert _.target_aws_lambda   is True

    def test__1__setup(self):
        with self.lambda_dependency_local as _:
            assert _.setup()                                == _
            assert folder_exists(_.folder__bucket()) is True

    def test__2__install(self):
        with self.lambda_dependency_local as _:
            target_path        = str(_.path())
            install_data = _.install()
            assert type(install_data)                     is Schema__Lambda__Dependency__Local_Install__Data
            assert _.install__data__exists() is True
            assert folder_exists(target_path)                   is True
            assert install_data.obj() == __( package_name    = self.package_name,
                                                   target_path     = target_path,
                                                   install_data    = __(cwd       = '.'    ,
                                                                        error     = None   ,
                                                                        kwargs    = __(cwd='.', stdout=-1, stderr=-1, timeout=None),
                                                                        runParams = [ 'pip3'                ,
                                                                                      'install'             ,
                                                                                       '--platform'         ,
                                                                                       'manylinux1_x86_64'  ,
                                                                                       '--only-binary=:all:',
                                                                                       '-t'                 ,
                                                                                       target_path          ,
                                                                                       self.package_name    ],
                                                                      status      = 'ok'   ,
                                                                      stdout      = f'Collecting {LAMBDA_DEPENDENCY__SMALL_TEST__PACKAGE}\n'
                                                                                    '  Using cached '
                                                                                    'colorama-0.4.6-py2.py3-none-any.whl.metadata (17 '
                                                                                    'kB)\n'
                                                                                    'Using cached colorama-0.4.6-py2.py3-none-any.whl '
                                                                                    '(25 kB)\n'
                                                                                    'Installing collected packages: colorama\n'
                                                                                    'Successfully installed colorama-0.4.6\n',
                                                                      stderr      = install_data.install_data.get('stderr')),
                                                   installed_files = ['colorama-0.4.6.dist-info/INSTALLER',
                                                                      'colorama-0.4.6.dist-info/METADATA',
                                                                      'colorama-0.4.6.dist-info/RECORD',
                                                                      'colorama-0.4.6.dist-info/REQUESTED',
                                                                      'colorama-0.4.6.dist-info/WHEEL',
                                                                      'colorama-0.4.6.dist-info/licenses/LICENSE.txt',
                                                                      'colorama/__init__.py',
                                                                      'colorama/__pycache__/__init__.cpython-312.pyc',
                                                                      'colorama/__pycache__/ansi.cpython-312.pyc',
                                                                      'colorama/__pycache__/ansitowin32.cpython-312.pyc',
                                                                      'colorama/__pycache__/initialise.cpython-312.pyc',
                                                                      'colorama/__pycache__/win32.cpython-312.pyc',
                                                                      'colorama/__pycache__/winterm.cpython-312.pyc',
                                                                      'colorama/ansi.py',
                                                                      'colorama/ansitowin32.py',
                                                                      'colorama/initialise.py',
                                                                      'colorama/tests/__init__.py',
                                                                      'colorama/tests/__pycache__/__init__.cpython-312.pyc',
                                                                      'colorama/tests/__pycache__/ansi_test.cpython-312.pyc',
                                                                      'colorama/tests/__pycache__/ansitowin32_test.cpython-312.pyc',
                                                                      'colorama/tests/__pycache__/initialise_test.cpython-312.pyc',
                                                                      'colorama/tests/__pycache__/isatty_test.cpython-312.pyc',
                                                                      'colorama/tests/__pycache__/utils.cpython-312.pyc',
                                                                      'colorama/tests/__pycache__/winterm_test.cpython-312.pyc',
                                                                      'colorama/tests/ansi_test.py',
                                                                      'colorama/tests/ansitowin32_test.py',
                                                                      'colorama/tests/initialise_test.py',
                                                                      'colorama/tests/isatty_test.py',
                                                                      'colorama/tests/utils.py',
                                                                      'colorama/tests/winterm_test.py',
                                                                      'colorama/win32.py',
                                                                      'colorama/winterm.py'      ],
                                                   time_stamp   = install_data.time_stamp ,
                                                   duration     = install_data.duration   )

    def test__files__zipped(self):                                                      # as a good example of the performance of zip and locally file access, this test runs in about 13ms
        with self.lambda_dependency_local as _:
            dependency_path = _.path()
            zipped__bytes       = _.files__zipped()
            zipped__files       = zip_bytes__files    (zipped__bytes)
            zipped__files_paths = zip_bytes__file_list(zipped__bytes)

            assert 60000 < len(zipped__bytes) < 70000
            assert len(zipped__files_paths) == 32                                       # confirm we have 32 files in the zip
            assert zipped__files_paths      == _.install__data().installed_files        # confirm they match the files that were installed via pip

            for zipped__file_path, zipped__file_bytes,  in zipped__files.items():       # for each zipped file path and bytes
                full_file_path = path_combine(dependency_path, zipped__file_path)       # calculate the path of the file localluy
                assert file_bytes(full_file_path) == zipped__file_bytes                 # confirm that the file contents match



    def test__install__data__exists(self):
        with self.lambda_dependency_local as _:
            assert _.install__data__exists() is True

    def test__install__data__save(self):
        temp_package_name = 'aaa-ccc-ddd'
        with Lambda__Dependency__Local(package_name=temp_package_name) as _:

            install_data       = Schema__Lambda__Dependency__Local_Install__Data(package_name=temp_package_name)
            install_data__path =  _.install__data__save(install_data)

            assert _.path() == _.folder__bucket() + f'/{temp_package_name}'
            assert file_exists(install_data__path)  is True
            assert _.install__data__exists()        is True
            assert _.install__data().json()         == install_data.json()
            assert _.install__data__delete()        is True
            assert _.install__data__delete()        is False
            assert file_exists(install_data__path)  is False

    def test__folder__bucket(self):
        with self.lambda_dependency_local as _:

            assert _.folder__bucket() == (current_temp_folder() +  # local temp folder (will be /tmp inside a lambda function)
                                                 '/osbot-aws__lambda-dependencies-storage' +  # the FOLDER_NAME__LOCAL__DEPENDENCIES_STORAGE
                                                 '/000000000000--osbot-lambdas--us-east-1')        # using localstack default account-id and region_name and the AWS_Config.DEFAULT__BUCKET_NAME__INFIX__LAMBDA

            assert _.folder__bucket() == (_.base_folder()                           + '/ ' +
                                          FOLDER_NAME__LAMBDA_DEPENDENCIES_STORAGE  + '/' +
                                          OSBOT_AWS__TEST__AWS_ACCOUNT_ID           + '--' +
                                          DEFAULT__BUCKET_NAME__INFIX__LAMBDA       + '--' +
                                          OSBOT_AWS__TEST__AWS_DEFAULT_REGION              )