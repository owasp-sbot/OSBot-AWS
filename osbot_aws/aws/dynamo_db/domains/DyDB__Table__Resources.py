from osbot_aws.aws.dynamo_db.domains.DyDB__Table     import DyDB__Table
from osbot_aws.aws.dynamo_db.models.DyDB__Document   import DyDB__Document
from osbot_aws.aws.dynamo_db.models.Resource__Config import Resource__Config
from osbot_utils.decorators.methods.cache_on_self    import cache_on_self

KEY_NAME__TABLE__RESOURCES = 'resource'

class DyDB__Table__Resources(DyDB__Table):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.key_name =  KEY_NAME__TABLE__RESOURCES

    def resources_types(self):
        resources_types = {'config': Resource__Config}
        return resources_types

    @cache_on_self
    def resources(self):
        resources = {}
        for resource_name, resource_type in self.resources_types().items():
            document = {KEY_NAME__TABLE__RESOURCES: resource_name}
            resource = resource_type(table =self, document=document)
            resources[resource_name] = resource
        return resources

    def resource(self, resource_name) -> DyDB__Document:
        return self.resources().get(resource_name)