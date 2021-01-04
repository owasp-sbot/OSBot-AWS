import json
import pprint

from osbot_utils.decorators.lists.index_by import index_by
from osbot_utils.utils.Json import json_dumps

from osbot_aws.apis.Session import Session


class Secrets:
    def __init__(self, id):
        self.aws_secrets = Session().client('secretsmanager')
        self.id = id

    def create(self, value='{}'):
        try:
            if type(value) != str:
                value = json_dumps(value)
            self.aws_secrets.create_secret( Name = self.id, SecretString = value)
            return self.exists()
        except Exception as error:
            return False

    def deleted(self):
        details = self.details()
        if details:
            return details.get('DeletedDate') is not None
        return False

    def delete(self):
        self.aws_secrets.delete_secret(SecretId = self.id)
        return self.exists() is False

    def delete_no_recovery(self):
        self.aws_secrets.delete_secret(SecretId=self.id, ForceDeleteWithoutRecovery=True)
        return self.exists() is False

    def details(self):
        try:
            return self.aws_secrets.describe_secret(SecretId = self.id)
        except:
            return None

    def exists(self):
        return self.details() is not None and self.deleted() is False

    @index_by
    def list(self):
        return self.aws_secrets.list_secrets().get('SecretList')

    def print(self):
        details = self.details()
        print(pprint.pformat(details))

    def set_id(self, value):
        self.id = value
        return self

    def undelete(self):
        return self.aws_secrets.restore_secret(SecretId = self.id)

    def update(self, value):
        self.aws_secrets.update_secret( SecretId = self.id, SecretString = value)
        return self.exists()

    def update_to_json_string(self, data):
        if self.exists() is False:
            self.create()
        value = json.dumps(data)
        self.aws_secrets.update_secret( SecretId = self.id, SecretString = value)
        return self.exists()

    def value(self):
        if self.exists():
            return self.aws_secrets.get_secret_value(SecretId=self.id).get('SecretString')
        return None

    def value_from_json_string(self):
        if self.exists():
            value = self.aws_secrets.get_secret_value(SecretId=self.id).get('SecretString')
            return json.loads(value)
        return None