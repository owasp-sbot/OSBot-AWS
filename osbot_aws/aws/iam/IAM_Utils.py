from osbot_aws.aws.lambda_.Lambda import Lambda
from osbot_aws.aws.iam.IAM        import IAM


class IAM_Utils:            # todo see if there is a better home for the methods below

    def __init__(self):
        self.arn_aws_policy_service_sqs_lambda = 'arn:aws:iam::aws:policy/service-role/AWSLambdaSQSQueueExecutionRole'

    def policy_add_sqs_permissions_to_lambda_role(self, lambda_name):
        aws_lambda    = Lambda(lambda_name)
        iam_role_name = aws_lambda.configuration().get('Role').split(':role/').pop()
        IAM(role_name=iam_role_name).role_policy_attach(self.arn_aws_policy_service_sqs_lambda)
        return iam_role_name

    def policy_remove_sqs_permissions_to_lambda_role(self, lambda_name):
        aws_lambda    = Lambda(lambda_name)
        iam_role_name = aws_lambda.configuration().get('Role').split(':role/').pop()
        IAM(role_name=iam_role_name).role_policy_detach(self.arn_aws_policy_service_sqs_lambda)
        return iam_role_name