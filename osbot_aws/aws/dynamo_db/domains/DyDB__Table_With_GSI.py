from osbot_aws.aws.dynamo_db.domains.DyDB__Table import DyDB__Table
from osbot_utils.decorators.lists.group_by       import group_by
from osbot_utils.decorators.lists.index_by       import index_by



class DyDB__Table_With_GSI(DyDB__Table):

    def attribute_definitions(self):
        return self.info().get('AttributeDefinitions', [])

    def can_update_table(self):
        if self.table_status() == 'ACTIVE':
            if self.indexes_status() in [['ACTIVE'], []]:
                return True
        return False

    def index(self, index_name):
        return self.indexes__by_index_name().get(index_name)

    def index_create(self, index_name, index_type, sort_key='timestamp', sort_key_type='N', sort_key_schema='RANGE', projection_type='ALL'):
        kwargs = dict(partition_name  = index_name      ,
                      partition_type  = index_type      ,
                      sort_key        = sort_key        ,
                      sort_key_type   = sort_key_type   ,
                      sort_key_schema = sort_key_schema ,
                      projection_type = projection_type )
        result = self.gsi_create(**kwargs).get('data')              # todo: add check for status =='ok'
        return result                                               # todo improve the data returned by this method
        # table_description = result.get('TableDescription'      , {})
        # table_status      = table_description.get('TableStatus')
        # return table_status

    def index_delete(self, index_name):
        return self.gsi_delete(index_name).get('data')

    def index_exists(self, index_name):
        return index_name in self.indexes_names()

    def index_not_exists(self, index_name):
        return self.index_exists(index_name) is False

    @group_by
    @index_by
    def indexes(self):
        return self.info().get('GlobalSecondaryIndexes', [])

    def indexes__by_index_name(self):
        return self.indexes(index_by='IndexName')

    def indexes_names(self):
        from osbot_utils.utils.Misc import list_set

        return list_set(self.indexes__by_index_name())

    def indexes_status(self):
        from osbot_utils.utils.Misc import list_set

        return list_set(self.indexes(index_by='IndexStatus'))

    def table_status(self):
        return self.info().get('TableStatus')