from unittest                             import TestCase

import pytest

from osbot_utils.utils.Misc               import list_set
from osbot_aws.helpers.Lambda_SSH_Kubectl import Lambda_SSH_Kubectl

@pytest.mark.skip("needs setup that creates a temp server to ssh into")
class test_Lambda_SSH_Kubectl(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.key_name = 'packer'                         # todo: add support for creating a temp EC2 server to test this
        cls.target_host = "54.74.165.194"               #       at the moment these tests need an hardcoded IP of a valid server and key_name
        cls.kubectl = Lambda_SSH_Kubectl(key_name=cls.key_name, target_host=cls.target_host)

    def test_kubectl(self):
        assert 'kubectl controls the Kubernetes cluster manager.\n' in self.kubectl.kubectl('--help')

    def test_deployments(self):
        result = self.kubectl.deployments()
        item   = result.get('items').pop()
        assert item.get('kind')  == 'Deployment'

    def test_events(self):
        result = self.kubectl.events()
        item   = result.get('items').pop()
        assert item.get('kind')  == 'Event'

    def test_nodes(self):
        result = self.kubectl.nodes()
        item   = result.get('items').pop()
        assert item.get('kind')  == 'Node'

    def test_persistent_volumes(self):
        result = self.kubectl.persistent_volumes()
        item   = result.get('items').pop()
        assert item.get('kind')  == 'PersistentVolume'

    def test_pods(self):
        result    = self.kubectl.pods()
        item      = result.get('items').pop()
        spec      = item.get('spec')
        status    = item.get('status')
        kind      = item.get('kind')
        metadata  = item.get('metadata')
        container = spec.get('containers').pop()

        assert list_set(result   ) == [ 'apiVersion', 'items', 'kind', 'metadata']
        assert list_set(item     ) == [ 'apiVersion', 'kind', 'metadata', 'spec', 'status']
        assert list_set(spec     ) == [ 'containers', 'dnsPolicy', 'enableServiceLinks', 'hostname', 'nodeName', 'priority', 'restartPolicy', 'schedulerName', 'securityContext', 'serviceAccount', 'serviceAccountName', 'subdomain', 'terminationGracePeriodSeconds', 'tolerations', 'volumes']
        assert list_set(status   ) == [ 'conditions', 'containerStatuses', 'hostIP', 'phase', 'podIP', 'podIPs', 'qosClass', 'startTime']
        assert list_set(metadata ) == [ 'annotations', 'creationTimestamp', 'generateName', 'labels', 'managedFields', 'name', 'namespace', 'ownerReferences', 'resourceVersion', 'selfLink', 'uid']
        assert list_set(container) == ['args', 'command', 'env', 'image', 'imagePullPolicy', 'name', 'ports', 'resources', 'terminationMessagePath', 'terminationMessagePolicy', 'volumeMounts']
        assert kind               == 'Pod'

        pod_namespace = metadata.get('namespace')
        pod_name       = metadata.get('name')
        container_name = container.get('name')

        exec_command = "uname"
        result_exec  = self.kubectl.pod_exec(pod_namespace, pod_name, container_name, exec_command)
        result_logs  = self.kubectl.pod_logs(pod_namespace, pod_name, container_name)

        assert len(result_logs) > 0
        assert result_exec == 'Linux\n'

    def test_services(self):
        result = self.kubectl.services()
        item   = result.get('items').pop()
        assert item.get('kind')  == 'Service'

