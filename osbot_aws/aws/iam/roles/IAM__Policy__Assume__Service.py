from osbot_aws.aws.iam.roles.IAM__Statement__Principal import IAM__Statement__Principal


class IAM__Policy__Assume__Service(IAM__Statement__Principal):
    action       : str =  'sts:AssumeRole'
    effect       : str = 'Allow'

    def __init__(self, service_name):
        self.principal_type  = 'Service'
        self.principal_value = f'{service_name}.amazonaws.com'
        super().__init__()


def iam_statement__codebuild__assume_service():
    return IAM__Policy__Assume__Service('codebuild').statement()

def iam_statement__ec2__assume_service():
    return IAM__Policy__Assume__Service('ec2').statement()

def iam_statement__lambda__assume_service():
    return IAM__Policy__Assume__Service('lambda').statement()