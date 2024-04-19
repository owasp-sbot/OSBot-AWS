from osbot_aws.aws.dynamo_db.domains.DyDB__Table_With_GSI import DyDB__Table_With_GSI

TIMESTAMP_SORT_KEY          = 'timestamp'
TIMESTAMP_SORT_KEY_TYPE     = 'N'
TIMESTAMP_SORT_KEY_SCHEMA   = 'RANGE'
TIMESTAMP_PROJECTION_TYPE   = 'ALL'

class DyDB__Table_With_Timestamp(DyDB__Table_With_GSI):

    def index_create(self, index_name, index_type, **kwargs):                   # every index here will have a timestamp has default
        kwargs = dict(partition_name  = index_name                ,
                      partition_type  = index_type                ,
                      sort_key        = TIMESTAMP_SORT_KEY        ,
                      sort_key_type   = TIMESTAMP_SORT_KEY_TYPE   ,
                      sort_key_schema = TIMESTAMP_SORT_KEY_SCHEMA ,
                      projection_type = TIMESTAMP_PROJECTION_TYPE )
        result = self.gsi_create(**kwargs).get('data')
        return result                                               # todo improve the data returned by this method