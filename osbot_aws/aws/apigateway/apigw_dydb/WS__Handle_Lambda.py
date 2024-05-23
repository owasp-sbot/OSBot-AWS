from osbot_utils.base_classes.Kwargs_To_Self import Kwargs_To_Self


class WS__Handle_Lambda(Kwargs_To_Self):

    def handle_lambda(self, event, context):
        connection_id = event.get('requestContext', {}).get('connectionId', '')
        route_key     = event.get('requestContext', {}).get('routeKey', '')

        if route_key == '$connect':                                     # Handle the connection event
            return self.route__connect(event, connection_id)

        if route_key == '$disconnect':                                  # Handle the disconnection event
            return self.route_disconnect(event, connection_id)

        if route_key == '$default':                                     # Handle the default route
            return self.route_default(event, connection_id)

        return self.route_unknown(event, connection_id, route_key)      # Handle an unknown route

    def route__connect(self, event, connection_id):
        return {'statusCode': 200, 'body': 'Connected.'                         }

    def route_disconnect(self, event, connection_id):
        return {'statusCode': 200, 'body': 'Disconnected.'                      }

    def route_default(self, event, connection_id):
        return {'statusCode': 200, 'body': 'Message received on default route.' }

    def route_unknown(self, event, connection_id, route_key):
        return {'statusCode': 400, 'body': 'Route not recognized.'              }