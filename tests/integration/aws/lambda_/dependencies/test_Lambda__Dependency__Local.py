from unittest                                                           import TestCase
from osbot_aws.AWS_Config                                               import AWS_Config, DEFAULT__BUCKET_NAME__INFIX__LAMBDA
from osbot_aws.aws.lambda_.schemas.Safe_Str__File__Name__Python_Package import Safe_Str__File__Name__Python_Package
from osbot_utils.utils.Objects                                          import __
from osbot_utils.utils.Files                                            import file_exists, folder_exists, current_temp_folder
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
            if _.local__dependency__exists():
                assert _.local__dependency__delete() is True
                assert _.local__dependency__delete() is False
                assert _.local__dependency__exists() is False


    def test__init__(self):
        with self.lambda_dependency_local as _:
            assert type(_              ) is Lambda__Dependency__Local
            assert type(_.aws_config   ) is AWS_Config
            assert type(_.package_name ) is Safe_Str__File__Name__Python_Package
            assert _.base_folder         == current_temp_folder()
            assert _.package_name        == LAMBDA_DEPENDENCY__SMALL_TEST__PACKAGE
            assert _.package_name        == 'colorama==0.4.6'
            assert _.target_aws_lambda   is True

    def test__1__setup(self):
        with self.lambda_dependency_local as _:
            assert _.setup()                                == _
            assert folder_exists(_.local__folder__bucket()) is True

    def test_local__folder__bucket(self):
        with self.lambda_dependency_local as _:

            assert _.local__folder__bucket() == (current_temp_folder()                     +        # local temp folder (will be /tmp inside a lambda function)
                                                 '/osbot-aws__lambda-dependencies-storage' +        # the FOLDER_NAME__LOCAL__DEPENDENCIES_STORAGE
                                                 '/000000000000--osbot-lambdas--us-east-1' )        # using localstack default account-id and region_name and the AWS_Config.DEFAULT__BUCKET_NAME__INFIX__LAMBDA

            assert _.local__folder__bucket() == (_.base_folder                             + '/ '+
                                                 FOLDER_NAME__LAMBDA_DEPENDENCIES_STORAGE  + '/'  +
                                                 OSBOT_AWS__TEST__AWS_ACCOUNT_ID           + '--' +
                                                 DEFAULT__BUCKET_NAME__INFIX__LAMBDA       + '--' +
                                                 OSBOT_AWS__TEST__AWS_DEFAULT_REGION    )

    def test_local__dependency__install(self):
        with self.lambda_dependency_local as _:
            target_path        = str(_.local__dependency__path())
            local_install_data = _.local__dependency__install()
            assert type(local_install_data)                     is Schema__Lambda__Dependency__Local_Install__Data
            assert _.local__dependency__install__data__exists() is True
            assert folder_exists(target_path)                   is True
            assert local_install_data.obj() == __( package_name    = self.package_name,
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
                                                                      stderr      = local_install_data.install_data.get('stderr')),
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
                                                   time_stamp   = local_install_data.time_stamp ,
                                                   duration     = local_install_data.duration   )

    def test_local__dependency__install__data(self):
        with self.lambda_dependency_local as _:
            assert _.local__dependency__install__data__exists() is True

    def test_local__dependency__path(self):
        temp_package_name = 'aaa-ccc-ddd'
        with Lambda__Dependency__Local(package_name=temp_package_name) as _:

            local_install_data       = Schema__Lambda__Dependency__Local_Install__Data(package_name=temp_package_name)
            local_install_data__path =  _.local__dependency__install__data__save(local_install_data)

            assert _.local__dependency__path()                  == _.local__folder__bucket() + f'/{temp_package_name}'
            assert file_exists(local_install_data__path)        is True
            assert _.local__dependency__install__data__exists() is True
            assert _.local__dependency__install__data().json()  == local_install_data.json()
            assert _.local__dependency__install__data__delete() is True
            assert _.local__dependency__install__data__delete() is False
            assert file_exists(local_install_data__path)        is False