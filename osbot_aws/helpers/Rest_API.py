from osbot_aws.apis.API_Gateway import API_Gateway


class Rest_API:
    def __init__(self, api_name=None, api_id=None):
        self.api_name    = api_name
        self.api_id      = api_id
        self.api_gateway = API_Gateway()

    def create(self):
        self.api_gateway.rest_api_create(self.api_name)
        #data = {'id': rest_api.get('id'),
        #        'name': rest_api.get('name'),
        #        'resource_id': self.resource(rest_api.get('id'), '/').get('id')
        #        }
        return self

    def id(self):
        if self.api_id is None:
            self.api_id = self.api_gateway.rest_api_id(self.api_name)
        return self.api_id

    def exists(self):
        return self.id() is not None

    def resource_id(self, path):
        return self.api_gateway.resource(self.id(), path).get('id')

