from osbot_utils.decorators.lists.index_by import index_by

from osbot_utils.decorators.methods.cache import cache
from osbot_utils.decorators.methods.cache_on_self import cache_on_self

from osbot_aws.apis.Session import Session
from osbot_utils.utils.Misc import base64_to_str


class ECR:
    def __init__(self):
        pass

    @cache_on_self
    def client(self):
        return Session().client('ecr')

    def authorization_token(self):
        auth_data          = self.client().get_authorization_token().get('authorizationData')[0]
        auth_token         = base64_to_str(auth_data.get('authorizationToken'))
        proxy_endpoint     = auth_data.get('proxyEndpoint')
        username, password = auth_token.split(':')
        return {    "registry": proxy_endpoint  ,
                    "username": username        ,
                    "password": password        }

    def images(self, repository_name):
        result = self.client().describe_images(repositoryName=repository_name)
        return result.get('imageDetails')

    @index_by
    def images_ids(self, repository_name):
        result = self.client().list_images(repositoryName=repository_name)
        return result.get('imageIds')

    def registry(self):
        response = self.client().describe_registry()
        return { 'registry_id'               : response.get('registryId'              ),
                 'replication_configuration' : response.get('replicationConfiguration')}

    def repository_create(self, name, tags=None):
        if self.repository_exists(name):
            return { 'status': 'warning', 'message': f'repository {name} already existed'}
        kwargs = { 'repositoryName' : name,
                   'tags'           :  [] }
        if tags:
            for key,value in tags.items():
                kwargs.get('tags').append({'Key': key , 'Value':value})

        result = self.client().create_repository(**kwargs)
        return result.get('repository')

    def repository_delete(self, name):
        if self.repository_exists(name):
            self.client().delete_repository(repositoryName=name)
            return True
        return False

    def repository_exists(self, name):
        return self.repository_info(name) is not None

    def repository_info(self, name):
        try:
            result = self.client().describe_repositories(repositoryNames=[name])
            return result.get('repositories')[0]                                    # there should only be one repository here
        except:                                                                     # todo catch the actual Exception raised
            return None                                                             # when repository doesn't exist

    @index_by
    def repositories(self):
        response  = self.client().describe_repositories()
        return response.get('repositories')