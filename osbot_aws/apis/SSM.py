from osbot_utils.decorators.lists.index_by import index_by

from osbot_utils.decorators.lists.group_by import group_by

from osbot_utils.decorators.methods.cache import cache
from osbot_utils.decorators.methods.cache_on_self import cache_on_self

from osbot_aws.apis.Session import Session

class SSM:

    def __init__(self):
        pass

    @cache_on_self
    def client(self):
        return Session().client('ssm')

    def command_run(self, instance_id, command):
        resp = self.client().send_command(
            DocumentName="AWS-RunShellScript",
            Parameters={'commands': [command]},
            InstanceIds=[instance_id],
        )
        return resp

    def commands_list(self):
        return self.client().list_commands()

    @index_by
    @group_by
    def parameters(self, filter_value, filter_key='Name', filter_option='Equals'):
        kwargs = { "ParameterFilters": [{ 'Key'   : filter_key         ,
                                          'Option': filter_option      ,
                                          'Values': [filter_value]    }]}
        return self.client().describe_parameters(**kwargs).get("Parameters")