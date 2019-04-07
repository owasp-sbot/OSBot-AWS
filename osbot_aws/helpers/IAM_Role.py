from osbot_aws.apis.IAM import IAM


class IAM_Role:
    def __init__(self,role_name):
        self.iam = IAM(role_name=role_name)

    def create_for_lambda(self):
        return self.create_for_service('lambda.amazonaws.com')

    def create_for_code_build(self):
        return self.create_for_service('codebuild.amazonaws.com')

    def create_for_service(self,service):
        role_arn =  self.iam.role_arn()
        if role_arn:
            return {'status':'warning', 'data': 'role already exists', 'role_name': self.iam.role_name , 'role_arn': role_arn}
        else:
            policy_document = {'Statement': [{'Action': 'sts:AssumeRole',
                                              'Effect': 'Allow',
                                              'Principal': {'Service': service}}]}
            data = self.iam.role_create(policy_document)
            return {'status': 'ok', 'data': data, 'role_name': self.iam.role_name, 'role_arn': data.get('Arn') }
