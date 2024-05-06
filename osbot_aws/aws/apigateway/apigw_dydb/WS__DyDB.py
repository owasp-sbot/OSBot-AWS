from boto3.dynamodb.types import TypeSerializer

from osbot_aws.aws.apigateway.apigw_dydb.WS__Connection         import WS__Connection
from osbot_aws.aws.dynamo_db.domains.DyDB__Table_With_Timestamp import DyDB__Table_With_Timestamp
from osbot_aws.utils.Execution_Env                              import current_execution_env
from osbot_utils.utils.Json                                     import to_json_str, from_json_str
from osbot_utils.utils.Misc                                     import date_time_now, timestamp_utc_now, timestamp_to_str_time

DYNAMO_DB__TABLE_NAME__WEB_SOCKETS = 'osbot__web_sockets'
TABLE_WEB_SOCKETS__INDEXES_NAMES   = ['date', 'status']

WS_CONNECTION_STATE__ACTIVE        = 'active'
WS_CONNECTION_STATE__DISCONNECTED  = 'disconnected'

class WS__DyDB(DyDB__Table_With_Timestamp):

    env: str = current_execution_env()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.table_name    = DYNAMO_DB__TABLE_NAME__WEB_SOCKETS
        self.table_indexes = TABLE_WEB_SOCKETS__INDEXES_NAMES

    def handle_route(self, connection_id, source=None, lambda_event=None):
        timestamp         = timestamp_utc_now()
        lambda_event_body = (lambda_event or {}).get('body')
        request_data      = from_json_str(lambda_event_body)
        if not request_data:
            request_data = {"request": lambda_event_body}

        response_message = self.handle_request_data(connection_id, request_data)

        topic = 'ws__dydb'
        data  = { 'action'        : 'show_message'  ,
                  'connection_id' : connection_id   ,
                  'response'      : response_message}
        #data.update(request_message)

        client_message = dict(when=timestamp_to_str_time(timestamp),
                              topic=topic,
                              data=data)

        body = to_json_str(client_message)

        return {'statusCode': 200, 'body': body }

    def register_connection(self, connection_id, source=None, lambda_event=None):
        status             = WS_CONNECTION_STATE__ACTIVE
        event_for_action   = { 'action'      : 'connect'           ,
                               'timestamp'   : timestamp_utc_now() ,
                               'source'      : source              ,
                               'status'      : status              ,
                               'lambda_event': lambda_event        }

        kwargs             = dict(id            = connection_id       ,  # index
                                  status        = status              ,  # index
                                  env           = self.env            ,
                                  events        = [event_for_action]  )

        ws_connection      = WS__Connection(**kwargs)
        document           = ws_connection.json()
        response = super().add_document(document)
        if response.get('document'):
            return response.get('document', {})
        return response

    def register_disconnect(self, connection_id, source=None, lambda_event=None):
        status             = WS_CONNECTION_STATE__DISCONNECTED
        timestamp          = timestamp_utc_now()
        event_for_action   = { 'action'      : 'disconnect'        ,
                               'timestamp'   : timestamp           ,
                               'source'      : source              ,
                               'status'      : status              ,
                               'lambda_event': lambda_event        }
        dydb_document = self.dydb_document(connection_id, load_data=False)
        dydb_document.add_to_list('events', event_for_action       )       # todo: add dydb_document ability to update different types of fields
        dydb_document.set_field  ('status', status                 )       #       like in this case: append to a list and set couple values
        dydb_document.set_field  ('timestamp_disconnect', timestamp)       # todo : add dydb_document.set_fields feature (to prevent multiple calls)


    def handle_request_data(self, connection_id, request_data):
        command = request_data.get('command')                                                # todo: see if should have this here, or if handling these commands should be done by the ones who implement this class
        if command == 'register':
            name  = request_data.get('name' , 'NA')
            state = request_data.get('state', 'NA')
            dydb_document = self.dydb_document(connection_id, load_data=False)
            dydb_document.set_field ('connection_name', name)                               # todo: replace with call to set multiple fields at the same time
            dydb_document.set_field('state'          , state)
            return {'message': f'registered device {name} with state {state}'}
        if command == 'Whoami':
            dydb_document = self.dydb_document(connection_id)
            connection_name = dydb_document.value('connection_name')
            state           = dydb_document.value('state')
            return f"you are '{connection_name}' and are in the state {state}"

        return {'message': f'no command provided : {request_data}' }