from osbot_aws.aws.iam.IAM_Role import IAM_Role

class IAM_Role_With_Policy(IAM_Role):

    def __init__(self, role_name=None):
        super().__init__(role_name)

    def policy_template_cloudwatch_allow_all(self):
        return {   "Version": "2012-10-17",
                   "Statement": [ {    "Effect": "Allow",
                                       "Action": [ "logs:CreateLogGroup"    ,
                                                   "logs:CreateLogStream"   ,
                                                   "logs:DescribeLogGroups" ,
                                                   "logs:DescribeLogStreams",
                                                   "logs:PutLogEvents"      ,
                                                   "logs:GetLogEvents"      ,
                                                   "logs:FilterLogEvents"  ],
                                       "Resource": "*" }]}

    def create_api_gateway__cloudwatch_allow_all(self, project_name=None):
        return self.create_cloudwatch_allow_all('apigateway.amazonaws.com', project_name)

    def create_cloudwatch_allow_all(self,service, project_name=None):
        policies = { "Cloud_Watch" : self.policy_template_cloudwatch_allow_all()}
        return self.create_for_service_with_policies(service, policies, project_name)