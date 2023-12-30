import pytest
from unittest                           import TestCase
from osbot_utils.utils.Dev              import pprint
from osbot_aws.apis.Cloud_Watch_Logs    import Cloud_Watch_Logs
from osbot_aws.aws.ecs.ECS              import ECS
from osbot_aws.aws.ecs.ECS_Actions      import ECS_Actions


@pytest.mark.skip('Wire up tests')
class test_ECS_Actions(TestCase):

    def setUp(self) -> None:
        self.ecs_actions = ECS_Actions()

    def test__init__(self):
        assert type(self.ecs_actions.ecs    ) is ECS
        assert type(self.ecs_actions.logs   ) is Cloud_Watch_Logs
        assert self.ecs_actions.account_id
        assert self.ecs_actions.region
        assert self.ecs_actions.account_id    == self.ecs_actions.logs.account_id
        assert self.ecs_actions.region        == self.ecs_actions.logs.region_name

    def test_create_cluster(self):
        cluster = self.ecs_actions.create_cluster()
        assert cluster.get('clusterArn'       ) == self.ecs_actions.cluster_arn
        assert cluster.get('clusterName'      ) == self.ecs_actions.cluster_name
        assert cluster.get('runningTasksCount')==0
        assert self.ecs_actions.cluster_arn in self.ecs_actions.ecs.clusters_arns()
        assert self.ecs_actions.ecs.cluster_exists(cluster_arn=self.ecs_actions.cluster_arn) is True

    def test_delete_cluster(self):
        result = self.ecs_actions.delete_cluster()
        pprint(result)

    def test_info_cluster(self):
        result = self.ecs_actions.info_cluster()
        assert result == []
