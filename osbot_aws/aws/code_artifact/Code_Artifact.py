from osbot_aws.AWS_Config import AWS_Config
from osbot_aws.apis.Session import Session
from osbot_utils.base_classes.Kwargs_To_Self import Kwargs_To_Self
from osbot_utils.decorators.methods.cache_on_self import cache_on_self
from osbot_utils.decorators.methods.remove_return_value import remove_return_value
from osbot_utils.utils.Files import stream_to_bytes
from osbot_utils.utils.Zip import gz_tar_bytes__file_list, gz_zip_bytes__file_list, zip_bytes__file_list, \
    zip_bytes__extract_to_folder


class Code_Artifact(Kwargs_To_Self):
    aws_config  : AWS_Config
    region_name : str
    @cache_on_self
    def client(self):
        return Session().client('codeartifact', region_name=self.region_name)

    def asset_name__gz(self, package_name, version):
        package_name = package_name.replace('-', '_')           # can't have - in asset_name
        asset_name   = f'{package_name}-{version}.tar.gz'
        return asset_name

    def asset_name__whl(self, package_name, version):
        package_name = package_name.replace('-', '_')
        asset_name   = f'{package_name}-{version}-py3-none-any.whl'
        return asset_name

    def authorization_token(self, domain):
        return self.client().get_authorization_token(domain=domain).get('authorizationToken')

    def domain(self, domain):
        return self.client().describe_domain(domain=domain).get('domain')

    def domains(self):
        return self.client().list_domains().get('domains')

    def package(self, **kwargs):
        return self.client().describe_package(**kwargs).get('package')

    def package_group(self, **kwargs):
        return self.client().describe_package_group(**kwargs).get('packageGroup')

    def package_groups(self, **kwargs):
        return self.client().list_package_groups(**kwargs).get('packageGroups')

    def package_version(self, **kwargs):
        return self.client().describe_package_version(**kwargs).get('packageVersion')

    @remove_return_value(field_name='ResponseMetadata')
    def package_version_asset(self, **kwargs):
        return self.client().get_package_version_asset(**kwargs)

    def package_version_asset__bytes(self, **kwargs):
        response    = self.package_version_asset(**kwargs)
        asset       = response.get('asset')
        asset_bytes = stream_to_bytes(asset)
        return asset_bytes

    def package_version_asset__files__gz(self, domain, repository,package_name, package_version):
        kwargs =dict(domain         = domain           ,
                     repository     = repository       , #'pypi-store'     ,
                     format         = 'pypi'           ,
                     package        = package_name     ,
                     packageVersion = package_version  )
        asset_name               = self.asset_name__gz(package_name, package_version)
        kwargs['packageVersion'] = package_version
        kwargs['asset'         ] = asset_name
        asset_bytes              = self.package_version_asset__bytes(**kwargs)
        asset_files              = gz_tar_bytes__file_list(asset_bytes)
        return asset_files

    def package_version_asset__files__whl(self, domain, repository,package_name, package_version):
        kwargs =dict(domain         = domain           ,
                     repository     = repository       , #'pypi-store'     ,
                     format         = 'pypi'           ,
                     package        = package_name     ,
                     packageVersion = package_version  )
        asset_name               = self.asset_name__whl(package_name, package_version)
        kwargs['packageVersion'] = package_version
        kwargs['asset'         ] = asset_name
        asset_bytes              = self.package_version_asset__bytes(**kwargs)
        asset_files              = zip_bytes__file_list(asset_bytes)
        return asset_files

    def package_version_asset__whl__extract_to_folder(self, target_folder, **kwargs):
        response    = self.package_version_asset(**kwargs)
        asset       = response.get('asset')
        asset_bytes = stream_to_bytes(asset)
        return zip_bytes__extract_to_folder(asset_bytes, target_folder)

    def package_version_assets(self, **kwargs):
        return self.client().list_package_version_assets(**kwargs).get('assets')

    def package_version_create(self, **kwargs):
        return self.client().publish_package_version(**kwargs)

    def package_version_dependencies(self, **kwargs):
        return self.client().list_package_version_dependencies(**kwargs).get('dependencies')

    @remove_return_value('ResponseMetadata')
    def package_versions(self, **kwargs):
        return self.client().list_package_versions(**kwargs)


    def packages(self, domain, repository):
        return self.client().list_packages(domain=domain, repository=repository).get('packages')

    def repository(self, **kwargs):
        return self.client().describe_repository(**kwargs).get('repository')

    def repository_endpoint(self, **kwargs):
        return self.client().get_repository_endpoint(**kwargs).get('repositoryEndpoint')

    def repositories(self):
        return self.client().list_repositories().get('repositories')