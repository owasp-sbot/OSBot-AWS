import json

from osbot_utils.utils import Misc

from osbot_aws.apis.Session import Session


class Parameter:                                # todo refactor main methods to SSM class
    def __init__(self, name=None):
        self._ssm = None
        self.name = name

    # helpers
    def ssm(self):
        if self._ssm is None:
            self._ssm = Session().client('ssm')
        return self._ssm

    # methods

    def create(self,value):
        return self.put(value)

    def delete(self):
        if self.exists() is False: return False
        self.ssm().delete_parameter(Name=self.name)
        return self.exists() is False

    def exists(self):

        return self.get() is not None

    def get(self):
        try:
            return self.ssm().get_parameter(Name=self.name).get('Parameter')
        except:
            return None

    def get_secret(self):
        try:
            return self.ssm().get_parameter(Name=self.name,WithDecryption=True).get('Parameter')
        except:
            return None

    def list(self):
        params = {}
        for param in self.ssm().describe_parameters().get('Parameters'):
            params[param.get('Name')] = param
        return params

    def push(self,data):
        return self.put(json.dumps(data))

    def pull(self):
        try:
            return json.loads(self.value())
        except:
            return None

    def push_secret(self,data):
        return self.put_secret(json.dumps(data))

    def pull_secret(self):
        try:
            return json.loads(self.value_secret())
        except:
            return None

    def put(self, value, description='', type='String',overwrite=True):
        return self.ssm().put_parameter(Name=self.name, Value=value, Description=description,Type=type, Overwrite=overwrite)

    def put_secret(self,value,description=''):
        return self.put(value,description=description,type='SecureString')

    def value(self):
        return Misc.get_value(self.get(),'Value')

    def value_secret(self):
        return Misc.get_value(self.get_secret(),'Value')

    def set_name(self,value): self.name = value ; return self