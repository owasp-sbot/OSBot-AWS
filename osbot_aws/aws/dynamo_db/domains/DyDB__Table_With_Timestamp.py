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

    def add_document(self,document):
        from osbot_utils.utils.Misc import timestamp_utc_now

        timestamp = document.get(TIMESTAMP_SORT_KEY)
        if not timestamp:
            document[TIMESTAMP_SORT_KEY] = timestamp_utc_now()
        return super().add_document(document)


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
        all_attribute_definitions = []
        all_gsi_updates           = []
        indexes_create_kwargs = {'attribute_definitions': all_attribute_definitions ,
                                 'gsi_updates'          : all_gsi_updates           }
        if self.table_indexes:
            for index_name in self.table_indexes:
                index_create_kwargs = self.index_create_kwargs(index_name)
                attribute_definitions = index_create_kwargs.get('attribute_definitions')
                gsi_update            = index_create_kwargs.get('gsi_update'           )
                for attribute_definition in attribute_definitions:
                    if attribute_definition not in all_attribute_definitions:
                        all_attribute_definitions.append(attribute_definition)
                all_gsi_updates.append(gsi_update)
        return indexes_create_kwargs

    def create_table_kwargs(self):
        create_table_kwargs               = super().create_table_kwargs()
        new_indexes_create_kwargs         = self.indexes_create_kwargs()
        new_indexes_attribute_definitions = new_indexes_create_kwargs.get('attribute_definitions')
        new_indexes_gsi_updates           = new_indexes_create_kwargs.get('gsi_updates')
        table_attribute_definitions       = create_table_kwargs.get('AttributeDefinitions')
        global_secondary_indexes          = []

        for attribute_definitions in new_indexes_attribute_definitions:
            if attribute_definitions not in table_attribute_definitions:
                table_attribute_definitions.append(attribute_definitions)
        for gsi_update in new_indexes_gsi_updates:
            create_index_config = gsi_update.get('Create')
            global_secondary_indexes.append(create_index_config)

        if global_secondary_indexes:
            create_table_kwargs['GlobalSecondaryIndexes'] = global_secondary_indexes

        return create_table_kwargs

    def query_index_last_n_hours(self, index_name, index_value, hours, query_filter=None):
        from osbot_utils.utils.Misc import timestamp_utc_now, timestamp_utc_now_less_delta

        timestamp_start = timestamp_utc_now_less_delta(hours=hours)  # get timestamp for last n hours
        timestamp_end = timestamp_utc_now()
        return self.query_index_by_timestamp(index_name, index_value, timestamp_start, timestamp_end, query_filter)

    def query_index_by_timestamp(self, index_name, index_value, timestamp_start, timestamp_end, query_filter=None):
        query_kwargs = dict(index_name    = index_name              ,
                            index_type    = INDEX_PARTITION_TYPE    ,
                            index_value   = index_value             ,
                            sort_key      = TIMESTAMP_SORT_KEY      ,
                            sort_key_type = TIMESTAMP_SORT_KEY_TYPE ,
                            start_value   = timestamp_start         ,
                            end_value     = timestamp_end           ,
                            query_filter  = query_filter            )

        return self.query_index_between_range(**query_kwargs)


    def setup(self):
        with self as _:
            if _.not_exists():
                self.create_table(wait_for_table=False)

