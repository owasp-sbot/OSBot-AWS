from osbot_aws.apis.CodeBuild import CodeBuild
from osbot_aws.aws.iam.IAM import IAM


#todo: add Create_Code_Build tests from gs-docker-codebuild project
class Create_Code_Build:

    def __init__(self, project_name, github_org='owasp-sbot', source_version='master', build_spec='buildspec.yml', docker_type='LINUX_CONTAINER',docker_image='aws/codebuild/docker:18.09.0',compute_type='BUILD_GENERAL1_SMALL'):
        self.iam                = IAM()
        self.build_spec         = build_spec
        self.github_org         = github_org
        self.source_version     = source_version
        self.docker_type        = docker_type
        self.docker_image       = docker_image
        self.compute_type       = compute_type
        self.project_name       = project_name
        self.account_id         = self.iam.account_id()
        self.region             = self.iam.region()
        self.project_repo       = f'https://github.com/{self.github_org}/{self.project_name}'
        self.service_role       = f'arn:aws:iam::{self.account_id}:role/{self.project_name}'
        self.project_arn        = f'arn:aws:codebuild:{self.region}:{self.account_id}:project/{self.project_name}'
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
            'name'         : self.project_name,
            'source'       : { 'type'         : 'GITHUB',
                               'location'     : self.project_repo                  ,
                               'buildspec'    : self.build_spec                   },
            'sourceVersion': self.source_version                                   ,
            'artifacts'    : {'type'          : 'NO_ARTIFACTS'                    },
            'environment'  : {'type'          : self.docker_type                   ,
                              'image'         : self.docker_image                  ,
                              'computeType'   : self.compute_type                  },
            'serviceRole'  : self.service_role
        }

        return self.code_build.codebuild.create_project(**kvargs)

    def create_project_with_container__gs_docker_codebuild(self):
        kvargs = {
            'name'         : self.project_name,
            'source'       : { 'type'                   : 'GITHUB',
                               'location'               : self.project_repo                  ,
                               'buildspec'              : self.build_spec                   },
            'sourceVersion': self.source_version                                             ,
            'artifacts'    : {'type'                    : 'NO_ARTIFACTS'                    },
            'environment'  : {'type'                    : self.docker_type                   ,
                             'image'                    : f'{self.account_id}.dkr.ecr.{self.region}.amazonaws.com/{self.project_name}:latest'.lower(),
                             'computeType'              : self.compute_type                  ,
                             'imagePullCredentialsType' : 'SERVICE_ROLE'                    },
            'serviceRole'  : self.service_role
        }
        return self.code_build.codebuild.create_project(**kvargs)

    def policies__for_docker_build(self):
        cloud_watch_arn = f"arn:aws:logs:{self.region}:{self.account_id}:log-group:/aws/codebuild/{self.project_name}:log-stream:*"
        policies = {"Cloud-Watch-Policy": {"Version": "2012-10-17",
                                           "Statement": [{"Sid": "GsBotPolicy",
                                                          "Effect": "Allow",
                                                          "Action": ["logs:CreateLogGroup",
                                                                     "logs:CreateLogStream",
                                                                     "logs:PutLogEvents"],
                                                          "Resource": [ cloud_watch_arn ]}]},
                    "Secret-Manager": {
                        "Version": "2012-10-17",
                        "Statement": [{"Sid": "GsBotPolicy",
                                       "Effect": "Allow",
                                       "Action": ["secretsmanager:GetSecretValue", "secretsmanager:DescribeSecret"],
                                       "Resource": [
                                           f"arn:aws:secretsmanager:{self.region}:{self.account_id}:secret:slack-gs-bot-*",
                                           f"arn:aws:secretsmanager:{self.region}:{self.account_id}:secret:gw-elastic-server-*"]}]},  # todo: refactor
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
        cloud_watch_arn = f"arn:aws:logs:{self.region}:{self.account_id}:log-group:/aws/codebuild/{self.project_name}:log-stream:*"
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
        cloud_watch_arn = f"arn:aws:logs:{self.region}:{self.account_id}:log-group:/aws/codebuild/{self.project_name}:log-stream:*"
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
                                                                  "Action"  : [  "secretsmanager:GetSecretValue","secretsmanager:DescribeSecret"          ],
                                                                  "Resource": [ f"arn:aws:secretsmanager:{self.region}:{self.account_id}:secret:slack-gs-bot-*"     ,
                                                                                f"arn:aws:secretsmanager:{self.region}:{self.account_id}:secret:gw-elastic*"        ,
                                                                                f"arn:aws:secretsmanager:{self.region}:{self.account_id}:secret:gsuite*"            ,
                                                                                f"arn:aws:secretsmanager:{self.region}:{self.account_id}:secret:git__*"         ]}]}}
        return policies


    def delete_project_role_and_policies(self):
        if self.code_build.iam.role_exists():
            policies_arns = list(self.code_build.iam.role_policies().values())
            self.code_build.iam.role_policies_detach(policies_arns)                 # first detach policies
            self.code_build.iam.policies_delete(policies_arns)                      # then delete the policies
            self.code_build.iam.role_delete()                                       # then delete the role
        if self.code_build.project_exists():
            self.code_build.project_delete()                                        # finally delete the project