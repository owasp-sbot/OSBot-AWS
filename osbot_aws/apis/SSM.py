from osbot_aws.apis.Session import Session

class OSBot_AWS__SSM:

    def __init__(self):
        self.client = Session().client('ssm')

    def command_run(self, instance_id, command):
        resp = self.client.send_command(
            DocumentName="AWS-RunShellScript",
            Parameters={'commands': [command]},
            InstanceIds=[instance_id],
        )
        return resp

    def commands_list(self):
        return self.client.list_commands()