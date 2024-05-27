from os import getenv
from unittest import TestCase

import pytest

from osbot_aws.aws.code_artifact.Code_Artifact import Code_Artifact
from osbot_utils.utils.Files import stream_to_file, file_delete
from osbot_utils.utils.Misc import in_github_action, list_set
from osbot_utils.utils.Objects import obj_info, base_types
from osbot_utils.utils.Zip import zip_file_list

ENV_VAR__CODE_ARTIFACT__TEST_DOMAIN_NAME = 'CODE_ARTIFACT__TEST_DOMAIN_NAME'
ENV_VAR__CODE_ARTIFACT__TEST_REGION_NAME = 'CODE_ARTIFACT__TEST_REGION_NAME'

class test_Code_Artifact(TestCase):
    code_artifact : Code_Artifact
    domain_name   : str
    region_name   : str
    @classmethod
    def setUpClass(cls):
        if in_github_action:
            pytest.mark.skip(reason="Code Artifact tests need account with code artifacts")
        cls.code_artifact = Code_Artifact()
        cls.domain_name   = getenv(ENV_VAR__CODE_ARTIFACT__TEST_DOMAIN_NAME)
        cls.region_name   = getenv(ENV_VAR__CODE_ARTIFACT__TEST_REGION_NAME)
        cls.code_artifact.aws_config.set_aws_session_region_name(cls.region_name)


    def test_client(self):
        assert self.code_artifact.client().meta.service_model.service_name == 'codeartifact'


    def test_authorization_token(self):
        with self.code_artifact as _:
            token = _.authorization_token(self.domain_name)
            assert len(token) > 512

    def test_domain(self):
        with self.code_artifact as _:
            domain = _.domain(self.domain_name)
            assert list_set(domain) == ['arn', 'assetSizeBytes', 'createdTime', 'encryptionKey', 'name', 'owner', 'repositoryCount', 's3BucketArn', 'status']

    def test_domains(self):
        with self.code_artifact as _:
            domains = _.domains()
            for domain in domains:
                assert list_set(domain) == ['arn', 'createdTime', 'encryptionKey', 'name', 'owner', 'status']

    def test_package(self):
        with self.code_artifact as _:
            package_name    = 'requests'
            kwargs = dict(domain         = self.domain_name,
                          repository     = 'pypi-store'    ,
                          format         = 'pypi'          ,
                          package        = package_name    )
            package = _.package(**kwargs)
            assert list_set(package) ==['format', 'name', 'originConfiguration']

    def test_package_group(self):
        with self.code_artifact as _:
            kwargs = dict(domain         = self.domain_name,
                          packageGroup   = '/*')
            package_group = _.package_group(**kwargs)
            assert list_set(package_group) == ['arn', 'createdTime', 'description', 'domainName', 'domainOwner', 'originConfiguration', 'pattern']

    def test_package_version(self):
        with self.code_artifact as _:
            package_name    = 'requests'
            package_version = '2.32.2'
            kwargs = dict(domain         = self.domain_name,
                          repository     = 'pypi-store'    ,
                          format         = 'pypi'          ,
                          package        = package_name    ,
                          packageVersion = package_version )
            package_version = _.package_version(**kwargs)
            assert package_version == {   'displayName'         : 'requests'                          ,
                                          'format'              : 'pypi'                              ,
                                          'homePage'            : 'https://requests.readthedocs.io'   ,
                                          'licenses'            : [{'name': 'Apache-2.0'}]            ,
                                          'origin'              : { 'domainEntryPoint': {'externalConnectionName': 'public:pypi'},
                                                                    'originType'      : 'EXTERNAL'}   ,
                                          'packageName'         :  'requests'                         ,
                                          'publishedTime'       : package_version.get('publishedTime'),
                                          'revision'            : package_version.get('revision'     ),
                                          'sourceCodeRepository': 'https://github.com/psf/requests'   ,
                                          'status'              : 'Published'                         ,
                                          'summary'             : 'Python HTTP for Humans.'           ,
  'version': '2.32.2'}

    def test_package_groups(self):
        with self.code_artifact as _:
            kwargs          = dict(domain = self.domain_name)
            package_groups  = _.package_groups(**kwargs)
            for package_group in package_groups:
                assert list_set(package_group) == ['arn', 'createdTime', 'description', 'domainName', 'domainOwner', 'originConfiguration', 'pattern']

    def test_package_versions(self):
        with self.code_artifact as _:
            package_name = 'requests'
            kwargs = dict(domain     = self.domain_name  ,
                          repository = 'pypi-store'      ,
                          format     = 'pypi'            ,
                          package    = package_name      )
            package_versions = _.package_versions(**kwargs)
            assert package_versions.get('package') == package_name
            for version in package_versions.get('versions'):
                assert list_set(version) == ['origin', 'revision', 'status', 'version']

    def test_package_version_asset(self):
        with self.code_artifact as _:
            package_name    = 'requests'
            package_version = '2.32.2'
            package_asset   = 'requests-2.32.2-py3-none-any.whl'
            kwargs = dict(domain         = self.domain_name,
                          repository     = 'pypi-store'    ,
                          format         = 'pypi'          ,
                          package        = package_name    ,
                          packageVersion = package_version ,
                          asset          = package_asset)
            package_version_asset = _.package_version_asset(**kwargs)
            assert package_version_asset == { 'asset'                 : package_version_asset.get('asset'),
                                              'assetName'             : 'requests-2.32.2-py3-none-any.whl',
                                              'packageVersion'        : '2.32.2',
                                              'packageVersionRevision': package_version_asset.get('packageVersionRevision')}

            asset_streaming_body = package_version_asset.get('asset')           # get the file stream
            temp_file            = stream_to_file(asset_streaming_body)         # save it locally
            assert 'requests/api.py' in zip_file_list(temp_file)                # open it up and confirm that requests file is in there
            file_delete(temp_file)


    def test_package_version_assets(self):
        with self.code_artifact as _:
            package_name    = 'requests'
            package_version = '2.32.2'
            kwargs          = dict(domain         = self.domain_name,
                                   repository     = 'pypi-store'    ,
                                   format         = 'pypi'          ,
                                   package        = package_name    ,
                                   packageVersion = package_version )
            version_assets  = _.package_version_assets(**kwargs)
            for asset in version_assets:
                assert list_set(asset              ) == ['hashes', 'name', 'size'            ]
                assert list_set(asset.get('hashes')) == ['MD5', 'SHA-1', 'SHA-256', 'SHA-512']

    def test_package_version_dependencies(self):
        with self.code_artifact as _:
            package_name    = 'requests'
            package_version = '2.32.2'
            kwargs = dict(domain         = self.domain_name,
                          repository     = 'pypi-store'    ,
                          format         = 'pypi'          ,
                          package        = package_name    ,
                          packageVersion = package_version )
            package_version_dependencies = _.package_version_dependencies(**kwargs)
            for dependency in package_version_dependencies:
                assert list_set(dependency) == ['dependencyType', 'package', 'versionRequirement']

    def test_packages(self):
        with self.code_artifact as _:
            kwargs = dict(domain = self.domain_name, repository =self.domain_name) # or repository='pypi-store'
            packages = _.packages(**kwargs)
            for package in packages:
                assert list_set(package) == ['format', 'originConfiguration', 'package']

    def test_repository(self):
        with self.code_artifact as _:
            domain_name     = self.domain_name
            repository_name = 'pypi-store'
            kwargs = dict(domain     = domain_name     ,
                          repository = repository_name )
            repository = _.repository(**kwargs)
            assert list_set(repository) == ['administratorAccount', 'arn', 'createdTime',
                                             'description', 'domainName', 'domainOwner',
                                            'externalConnections', 'name', 'upstreams']

    def test_repository_endpoint(self):
        with self.code_artifact as _:
            region_name     = _.aws_config.region_name()
            account_id      = _.aws_config.account_id()
            domain_name     = self.domain_name
            repository_name = 'pypi-store'
            kwargs = dict(domain     = domain_name     ,
                          repository = repository_name ,
                          format     = 'pypi'          )
            repository_endpoint = _.repository_endpoint(**kwargs)
            assert repository_endpoint ==  f'https://{domain_name}-{account_id}.d.codeartifact.{region_name}.amazonaws.com/pypi/{repository_name}/'


    def test_repositories(self):
        with self.code_artifact as _:
            repositories = _.repositories()
            for repository in repositories:
                assert list_set(repository) == ['administratorAccount', 'arn', 'createdTime',
                                                'description', 'domainName', 'domainOwner', 'name']