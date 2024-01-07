import json
import pprint

from osbot_utils.decorators.methods.cache_on_self   import cache_on_self
from osbot_utils.decorators.lists.index_by          import index_by
from osbot_utils.utils.Json                         import json_dumps
from osbot_aws.apis.Session                         import Session

class Secrets:
    def __init__(self, secret_id):
        self.secret_id = secret_id

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.secret_id}>"

    @cache_on_self
    def client(self):
        return Session().client_secrets_manager()

    def create(self, value='{}'):
        # noinspection PyBroadException
        try:
            if type(value) != str:
                value = json_dumps(value)
            self.client().create_secret( Name = self.secret_id, SecretString = value)
            return self.exists()
        except Exception:
            return False

    def deleted(self):
        details = self.details()
        if details:
            return details.get('DeletedDate') is not None
        return False

    def delete(self):
        self.client().delete_secret(SecretId = self.secret_id)
        return self.exists() is False

    def delete_no_recovery(self):
        self.client().delete_secret(SecretId=self.secret_id, ForceDeleteWithoutRecovery=True)
        return self.exists() is False

    def details(self):
        # noinspection PyBroadException
        try:
            return self.client().describe_secret(SecretId = self.secret_id)
        except:
            return None

    def exists(self):
        return self.details() is not None and self.deleted() is False

    @index_by
    def list(self):
        return self.client().list_secrets().get('SecretList')

    def print(self):
        details = self.details()
        print(pprint.pformat(details))

    def set_id(self, value):
        self.secret_id = value
        return self

    def undelete(self):
        return self.client().restore_secret(SecretId = self.secret_id)

    def update(self, value):
        self.client().update_secret( SecretId = self.secret_id, SecretString = value)
        return self.exists()

    def update_to_json_string(self, data):
        if self.exists() is False:
            self.create()
        value = json.dumps(data)
        self.client().update_secret( SecretId = self.secret_id, SecretString = value)
        return self.exists()

    def value(self):
        if self.exists():
            return self.client().get_secret_value(SecretId=self.secret_id).get('SecretString')
        return None

    def value_from_json_string(self):
        if self.exists():
            value = self.client().get_secret_value(SecretId=self.secret_id).get('SecretString')
            return json.loads(value)
        return None