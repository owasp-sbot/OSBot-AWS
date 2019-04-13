from time import sleep

from osbot_aws.apis.CodeBuild import CodeBuild

#todo: add Create_Code_Build tests from gs-docker-codebuild project
class Create_Code_Build:

    def __init__(self,account_id,project_name):
        self.account_id         = account_id
        self.project_name       = project_name
        self.project_repo       = 'https://github.com/pbx-gs/{0}'.format(self.project_name)
        self.service_role       = 'arn:aws:iam::{0}:role/{1}'                  .format(self.account_id, self.project_name)
        self.project_arn        = 'arn:aws:codebuild:eu-west-2:{0}:project/{1}'.format(self.account_id, self.project_name     )
        self.assume_policy      = {'Statement': [{'Action'   : 'sts:AssumeRole'                     ,
                                                  'Effect'   : 'Allow'                              ,
                                                  'Principal': {'Service': 'codebuild.amazonaws.com'}}]}

        self.code_build = CodeBuild(role_name=self.project_name, project_name=self.project_name)

    def create_role_and_policies(self, policies):
        self.code_build.iam.role_create(self.assume_policy)
        policies_arn = self.code_build.policies_create(policies)
        self.code_build.iam.role_policies_attach(policies_arn)
        return self

    def create_project_with_container__docker(self):
        kvargs = {
            'name'        : self.project_name,
            'source'      : { 'type'         : 'GITHUB',
                              'location'     : self.project_repo                 },
            'artifacts'   : {'type'          : 'NO_ARTIFACTS'                    },
            'environment' : {'type'          : 'LINUX_CONTAINER'                  ,
                            'image'          : 'aws/codebuild/docker:18.09.0'     ,
                            'computeType'    : 'BUILD_GENERAL1_LARGE'            },
            'serviceRole' : self.service_role
        }

        return self.code_build.codebuild.create_project(**kvargs)

    def create_project_with_container__gs_docker_codebuild(self):
        kvargs = {
            'name'        : self.project_name,
            'source'      : { 'type'                   : 'GITHUB',
                           'location'                  : self.project_repo                 },
            'artifacts'   : {'type'                    : 'NO_ARTIFACTS'                    },
            'environment' : {'type'                    : 'LINUX_CONTAINER'                  ,
                            'image'                    : '{0}.dkr.ecr.eu-west-2.amazonaws.com/gs-docker-codebuild:latest'.format(self.account_id)     ,
                            'computeType'              : 'BUILD_GENERAL1_LARGE'            ,
                            'imagePullCredentialsType' : 'SERVICE_ROLE'                    },
            'serviceRole' : self.service_role
        }
        return self.code_build.codebuild.create_project(**kvargs)

    def policies__for_docker_build(self):
        cloud_watch_arn = "arn:aws:logs:eu-west-2:{0}:log-group:/aws/codebuild/{1}:log-stream:*".format(self.account_id, self.project_name)
        policies = {"Cloud-Watch-Policy": {"Version": "2012-10-17",
                                           "Statement": [{"Sid": "GsBotPolicy",
                                                          "Effect": "Allow",
                                                          "Action": ["logs:CreateLogGroup",
                                                                     "logs:CreateLogStream",
                                                                     "logs:PutLogEvents"],
                                                          "Resource": [cloud_watch_arn]}]},
                    "Secret-Manager": {
                        "Version": "2012-10-17",
                        "Statement": [{"Sid": "GsBotPolicy",
                                       "Effect": "Allow",
                                       "Action": ["secretsmanager:GetSecretValue", "secretsmanager:DescribeSecret"],
                                       "Resource": [
                                           "arn:aws:secretsmanager:eu-west-2:244560807427:secret:slack-gs-bot-*",
                                           "arn:aws:secretsmanager:eu-west-2:244560807427:secret:elastic_gsuite_data-*"]}]},
                    "Create-Docker-Image": {
                        "Version": "2012-10-17",
                        "Statement": [{"Effect": "Allow",
                                       "Action": ["ecr:BatchCheckLayerAvailability",
                                                  "ecr:CompleteLayerUpload",
                                                  "ecr:GetAuthorizationToken",
                                                  "ecr:InitiateLayerUpload",
                                                  "ecr:PutImage",
                                                  "ecr:UploadLayerPart"],
                                       "Resource": "*"}]},
                    "Create-Repository": {
                        "Version": "2012-10-17",
                        "Statement": [{"Effect": "Allow",
                                       "Action": ["ecr:CreateRepository"],
                                       "Resource": "*"}]}}
        return policies

    def policies__with_ecr(self):
        cloud_watch_arn = "arn:aws:logs:eu-west-2:{0}:log-group:/aws/codebuild/{1}:log-stream:*".format(self.account_id,self.project_name)
        policies = {"Cloud-Watch-Policy"     : { "Version": "2012-10-17",
                                                 "Statement": [{   "Effect": "Allow",
                                                                   "Action": [ "logs:CreateLogGroup"  ,
                                                                               "logs:CreateLogStream" ,
                                                                               "logs:PutLogEvents"   ],
                                                                   "Resource": [ cloud_watch_arn ]}]},
                    "Download_Image"         : { "Version": "2012-10-17",
                                                 "Statement": [{   "Effect": "Allow",
                                                                   "Action": [   "ecr:GetAuthorizationToken",
                                                                                 "ecr:BatchCheckLayerAvailability",
                                                                                 "ecr:GetDownloadUrlForLayer",
                                                                                 "ecr:GetRepositoryPolicy",
                                                                                 "ecr:DescribeRepositories",
                                                                                 "ecr:ListImages",
                                                                                 "ecr:DescribeImages",
                                                                                 "ecr:BatchGetImage"],
                                                                   "Resource": "*"}]}}
        return policies

    def policies__with_ecr_and_3_secrets(self):
        cloud_watch_arn = "arn:aws:logs:eu-west-2:{0}:log-group:/aws/codebuild/{1}:log-stream:*".format(self.account_id,self.project_name)
        policies = {"Cloud-Watch-Policy"     : { "Version": "2012-10-17",
                                                 "Statement": [{   "Sid": "GsBotPolicy",
                                                                   "Effect": "Allow",
                                                                   "Action": [ "logs:CreateLogGroup"  ,
                                                                               "logs:CreateLogStream" ,
                                                                               "logs:PutLogEvents"   ],
                                                                   "Resource": [ cloud_watch_arn ]}]},
                    "Download_Image"         : { "Version": "2012-10-17",
                                                 "Statement": [{   "Effect": "Allow",
                                                                   "Action": [   "ecr:GetAuthorizationToken",
                                                                                 "ecr:BatchCheckLayerAvailability",
                                                                                 "ecr:GetDownloadUrlForLayer",
                                                                                 "ecr:GetRepositoryPolicy",
                                                                                 "ecr:DescribeRepositories",
                                                                                 "ecr:ListImages",
                                                                                 "ecr:DescribeImages",
                                                                                 "ecr:BatchGetImage"],
                                                                   "Resource": "*"}]},
                    "Secret-Manager"        : { "Version"  : "2012-10-17",
                                                "Statement": [{   "Effect"  : "Allow",
                                                                  "Action"  : [ "secretsmanager:GetSecretValue","secretsmanager:DescribeSecret"          ],
                                                                  "Resource": [ "arn:aws:secretsmanager:eu-west-2:244560807427:secret:slack-gs-bot-*"     ,
                                                                                "arn:aws:secretsmanager:eu-west-2:244560807427:secret:elastic*"           ,
                                                                                "arn:aws:secretsmanager:eu-west-2:244560807427:secret:gsuite*"        ]}]}}
        return policies


    def delete_project_role_and_policies(self):
        if self.code_build.iam.role_exists():
            policies_arns = list(self.code_build.iam.role_policies().values())
            self.code_build.iam.role_policies_detach(policies_arns)                 # first detach policies
            self.code_build.iam.policies_delete(policies_arns)                      # then delete the policies
            self.code_build.iam.role_delete()                                       # then delete the role
        if self.code_build.project_exists():
            self.code_build.project_delete()                                        # finally delete the project