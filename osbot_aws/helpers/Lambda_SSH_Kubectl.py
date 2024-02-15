from osbot_utils.utils.Json import json_parse
from osbot_utils.utils.Misc import split_lines
from osbot_aws.helpers.Lambda_SSH import Lambda_SSH


class Lambda_SSH_Kubectl(Lambda_SSH):

    def kubectl(self, params):
        ssh_command = f"sudo kubectl {params}"
        return self.invoke_lambda(ssh_command)

    def deployments(self):
        return json_parse(self.kubectl('get deployments -A -o json'))

    def events(self):
        return json_parse(self.kubectl('get events -A -o json'))

    def nodes(self):
        return json_parse(self.kubectl('get nodes -A -o json'))

    def persistent_volumes(self):
        return json_parse(self.kubectl('get pv -A -o json'))

    def pod_logs(self, pod_namespace, pod_name, container_name):
        params = f'logs -n {pod_namespace} {pod_name} {container_name}'
        return split_lines(self.kubectl(params))

    def pod_exec(self, pod_namespace, pod_name, container_name, exec_command):
        params = f'exec -n {pod_namespace} {pod_name} {container_name} -- {exec_command}'
        return self.kubectl(params)

    def pods(self):
        return json_parse(self.kubectl('get pods -A -o json'))

    def services(self):
        return json_parse(self.kubectl('get services -A -o json'))