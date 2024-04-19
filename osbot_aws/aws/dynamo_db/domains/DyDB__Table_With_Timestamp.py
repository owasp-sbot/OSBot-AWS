from osbot_aws.aws.dynamo_db.domains.DyDB__Table_With_GSI import DyDB__Table_With_GSI

TIMESTAMP_SORT_KEY          = 'timestamp'
TIMESTAMP_SORT_KEY_TYPE     = 'N'
TIMESTAMP_SORT_KEY_SCHEMA   = 'RANGE'
TIMESTAMP_PROJECTION_TYPE   = 'ALL'
INDEX_PARTITION_TYPE        = 'S'

class DyDB__Table_With_Timestamp(DyDB__Table_With_GSI):

    table_indexes : list

    def __init__(self,**kwargs):
        super().__init__(**kwargs)



    def index_create_kwargs(self, index_name):                   # every index here will have a timestamp has default
        kwargs = dict(partition_name  = index_name                ,
                      partition_type  = INDEX_PARTITION_TYPE      ,
                      sort_key        = TIMESTAMP_SORT_KEY        ,
                      sort_key_type   = TIMESTAMP_SORT_KEY_TYPE   ,
                      sort_key_schema = TIMESTAMP_SORT_KEY_SCHEMA ,
                      projection_type = TIMESTAMP_PROJECTION_TYPE )
        index_create_kwargs = self.gsi_create_kwargs(**kwargs).get('data')
        return index_create_kwargs

    def indexes_create_kwargs(self):
        indexes_create_kwargs = {}

        if self.table_indexes:
            for index_name in self.table_indexes:
                pass


    def index_create(self, index_name, **kwargs):
        index_create_kwargs = self.index_create_kwargs(index_name)
        return self.gsi_create_index(**index_create_kwargs).get('data')

    def indexes_exist(self):
        if not self.table_indexes:                                  # if there are no indexes current defined in this class don't return True
            return False
        current_indexes = self.indexes_names()
        for index_name in self.table_indexes:
            if index_name not in current_indexes:
                return False
        return True

    def setup(self):
        with self as _:
            if _.not_exists():
                "print-creating table"
                self.create_table(wait_for_table=True)

