from osbot_aws.aws.dynamo_db.Dynamo_DB__Table import Dynamo_DB__Table


class DyDB__Table(Dynamo_DB__Table):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def add_gsi(self, create_kwargs):
        return self.update_table_create_gsi(create_kwargs)

    def exists(self):
        return super().exists().get('data')

    def info(self):
        return super().info().get('data')

    def not_exists(self):
        return self.exists() is False