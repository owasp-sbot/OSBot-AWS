from osbot_aws.aws.sts.STS import STS
from osbot_aws.deploy.Deploy_Lambda import Deploy_Lambda

from osbot_utils.utils.Files import file_name, file_contents

from osbot_aws.lambdas.server_ssh import run
from osbot_aws.apis.Secrets import Secrets


class Lambda_SSH:

    def __init__(self, key_name, target_host):
        self.sts            = STS()
        self.region         = self.sts.current_region_name()
        self.key_name       = key_name
        self.target_host    = target_host
        self.lambda_handler = run
        self.lambda_layer   = f"arn:aws:lambda:{self.region}:553035198032:layer:git-lambda2:8"      # todo: rebuild this layer (https://github.com/lambci/git-lambda-layer)
        self.ssh_user       = 'ubuntu'
        self.deploy         = Deploy_Lambda(self.lambda_handler)
        self.lambda_name    = self.deploy.package.lambda_name
        self.aws_lambda     = self.deploy.package.aws_lambda

    def deploy_lambda(self):
        self.deploy.add_osbot_aws()
        if self.deploy.deploy():
            self.aws_lambda.set_layers([self.lambda_layer])
            self.aws_lambda.update_lambda_configuration()
        return self.aws_lambda.exists()

    def invoke_lambda(self, ssh_command):
        ssh_key    = self.get_key_from_secret_store()
        payload = { 'target_host' : self.target_host,
                    'ssh_key'     : ssh_key         ,
                    'ssh_key_name': self.key_name   ,
                    'ssh_user'    : self.ssh_user   ,
                    'ssh_command' : ssh_command     }

        return self.aws_lambda.invoke(payload)

    def get_key_from_secret_store(self):
        secret_name = f"ssh_key_{self.key_name}.pem"
        return Secrets(secret_name).value()

    def upload_ssh_key_to_secret_store(self, path_to_ssh_key):
        key_name    = file_name(path_to_ssh_key)
        secret_name = f"ssh_key_{key_name}"
        secret_data = file_contents(path_to_ssh_key)
        return Secrets(secret_name).create(secret_data)