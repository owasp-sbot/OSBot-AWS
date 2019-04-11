import  boto3
from    time                                import sleep

from    osbot_aws.apis.IAM                  import IAM
from    pbx_gs_python_utils.utils.Dev       import Dev
from    pbx_gs_python_utils.utils.Misc      import Misc

from osbot_aws.apis.Session import Session


class CodeBuild:

    def __init__(self, project_name, role_name):
        self.codebuild    = Session().client('codebuild')
        self.iam          = IAM(role_name=role_name)
        self.project_name = project_name
        return

    def _invoke_via_paginator(self, method, field_id, use_paginator, **kwargs):
        paginator = self.codebuild.get_paginator(method)
        for page in paginator.paginate(**kwargs):
            for id in page.get(field_id):
                yield id
            if use_paginator is False:
                return

    def all_builds_ids(self, use_paginator = False):
        return self._invoke_via_paginator('list_builds','ids',use_paginator)

    def build_info(self, build_id):
        builds = self.codebuild.batch_get_builds(ids=[build_id]).get('builds')
        return Misc.array_pop(builds,0)

    def build_start(self):
        kvargs = { 'projectName': self.project_name }
        return self.codebuild.start_build(**kvargs).get('build').get('arn')

    def build_wait_for_completion(self, build_id, sleep_for=0.5, max_attempts=20, log_status=False):
        for i in range(0,max_attempts):
            build_info    = self.build_info(build_id)
            build_status  = build_info.get('buildStatus')
            current_phase = build_info.get('currentPhase')
            if log_status:
                Dev.pprint("[{0}] {1} {2}".format(i,build_status,current_phase))
            if build_status != 'IN_PROGRESS':
                return build_info
            sleep(sleep_for)
        return None


    def policies_create(self, policies):                        # does not update, only add new ones
        policies_arns = []
        role_policies = list(self.iam.role_policies().keys())
        for base_name, policy in policies.items():
            policy_name = "{0}_{1}".format(base_name, self.project_name)
            if policy_name in role_policies:
                continue
            policies_arns.append(self.iam.policy_create(policy_name,policy).get('policy_arn'))
        return policies_arns

    def project_builds(self,ids):
        return self.codebuild.batch_get_builds(ids=ids)

    def project_create(self, project_repo, service_role):

        kvargs = {
            'name': self.project_name,
            'source': {'type': 'GITHUB',
                       'location': project_repo},
            'artifacts': {'type': 'NO_ARTIFACTS'},
            'environment': {'type': 'LINUX_CONTAINER',
                            'image': 'aws/codebuild/python:3.7.1-1.7.0',
                            'computeType': 'BUILD_GENERAL1_SMALL'},
            'serviceRole': service_role
        }

        return self.codebuild.create_project(**kvargs)

    def project_delete(self):
        if self.project_exists() is False: return False
        self.codebuild.delete_project(name=self.project_name)
        return self.project_exists() is False

    def project_exists(self):
        return self.project_name in self.projects()


    def project_info(self):
        projects = Misc.get_value(self.codebuild.batch_get_projects(names=[self.project_name]),'projects',[])
        return Misc.array_pop(projects,0)

    def project_builds_ids(self, project_name, use_paginator=False):
        if use_paginator:
            kwargs = { 'projectName' : project_name }
        else:
            kwargs = { 'projectName' : project_name ,
                       'sortOrder'   : 'DESCENDING'  }
        return self._invoke_via_paginator('list_builds_for_project', 'ids',use_paginator, **kwargs)


    def projects(self):
        return self.codebuild.list_projects().get('projects')
