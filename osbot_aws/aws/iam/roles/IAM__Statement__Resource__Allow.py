from osbot_aws.aws.iam.roles.IAM__Statement__Resource import IAM__Statement__Resource


class IAM__Statement__Resource__Allow(IAM__Statement__Resource):
    effect   : str = 'Allow'

    def __init__(self, actions, resource):
        self.actions  = actions
        self.resource = resource
        super().__init__()