from osbot_aws.AWS_Config import AWS_Config
from osbot_aws.apis.Session import Session
from osbot_utils.base_classes.Kwargs_To_Self import Kwargs_To_Self
from osbot_utils.decorators.methods.cache_on_self import cache_on_self
from osbot_utils.decorators.methods.remove_return_value import remove_return_value


class Code_Artifact(Kwargs_To_Self):
    aws_config  : AWS_Config
    region_name : str
    @cache_on_self
    def client(self):
        return Session().client('codeartifact', region_name=self.region_name)

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

    def package_version(self, **kwargs):
        return self.client().describe_package_version(**kwargs).get('packageVersion')

    def package_groups(self, **kwargs):
        return self.client().list_package_groups(**kwargs).get('packageGroups')

    @remove_return_value('ResponseMetadata')
    def package_versions(self, **kwargs):
        return self.client().list_package_versions(**kwargs)

    @remove_return_value(field_name='ResponseMetadata')
    def package_version_asset(self, **kwargs):
        return self.client().get_package_version_asset(**kwargs)

    def package_version_assets(self, **kwargs):
        return self.client().list_package_version_assets(**kwargs).get('assets')

    def package_version_dependencies(self, **kwargs):
        return self.client().list_package_version_dependencies(**kwargs).get('dependencies')

    def packages(self, domain, repository):
        return self.client().list_packages(domain=domain, repository=repository).get('packages')

    def repository(self, **kwargs):
        return self.client().describe_repository(**kwargs).get('repository')

    def repository_endpoint(self, **kwargs):
        return self.client().get_repository_endpoint(**kwargs).get('repositoryEndpoint')

    def repositories(self):
        return self.client().list_repositories().get('repositories')