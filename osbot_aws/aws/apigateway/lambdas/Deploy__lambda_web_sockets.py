from osbot_aws.aws.apigateway.lambdas.lambda_web_sockets import run
from osbot_aws.deploy.Deploy_Lambda import Deploy_Lambda


class Deploy__lambda_web_sockets:

    def __init__(self):
        self.handler       = run
        self.deploy_lambda = Deploy_Lambda(self.handler)

    def update(self):
        self.deploy_lambda.add_osbot_utils()
        return self.deploy_lambda.update()

    def invoke_lambda(self, payload=None):
        return self.deploy_lambda.invoke(payload)
