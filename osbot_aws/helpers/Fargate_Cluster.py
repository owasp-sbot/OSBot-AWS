from pbx_gs_python_utils.utils.aws.Fargate import Fargate


class Fargate_Cluster(Fargate):

    def __init__(self, account_id):
        super().__init__(account_id)


