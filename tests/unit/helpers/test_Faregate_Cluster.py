import sys; sys.path.append('..')
from unittest import TestCase
from osbot_aws.helpers.Fargate_Cluster import Fargate_Cluster


class test_Fargate_Cluster(TestCase):

    def setUp(self):
        self.account_id = '244560807427'
        self.cluster = Fargate_Cluster(self.account_id)      # remove from ctor


    def test___init__(self):
        assert self.cluster.account_id == self.account_id