import requests

from osbot_utils.decorators.methods.remove_return_value import remove_return_value

from osbot_utils.utils.Misc import datetime_to_str

from osbot_utils.decorators.lists.group_by import group_by

from osbot_utils.decorators.lists.index_by import index_by

from osbot_utils.decorators.methods.cache_on_self import cache_on_self

from osbot_aws.apis.Session import Session


class Cognito_IDP:

    def __init__(self):
        pass

    @cache_on_self
    def cognito(self):
        return Session().client('cognito-idp')

    @remove_return_value(field_name='ResponseMetadata')
    def auth_initiate(self, client_id, username, password):

        auth_parameters = { 'USERNAME': username, 'PASSWORD': password }
        client = self.cognito()
        try:
            response = client.initiate_auth( ClientId=client_id, AuthFlow='USER_PASSWORD_AUTH',AuthParameters=auth_parameters)
            return response
        except client.exceptions.ResourceNotFoundException:
            return {}
        except client.exceptions.NotAuthorizedException:
            return {}

    def auth_user_info(self, project, region, access_token):
        user_info_url = f"https://{project}.auth.{region}.amazoncognito.com/oauth2/userInfo"

        headers = { 'Authorization': f"Bearer {access_token}" }
        response = requests.get(user_info_url, headers=headers)
        return response#.json()

    def user_info(self,  user_pool_id, user_name):
        return self.user(user_pool_id, user_name)

    def user(self, user_pool_id, user_name):
        client = self.cognito()
        try:
            response = client.admin_get_user(UserPoolId=user_pool_id, Username=user_name)
            return self.format_user_data(response)
        except client.exceptions.ResourceNotFoundException:
            return {}
        except client.exceptions.UserNotFoundException:
            return {}


    def user_create(self, user_pool_id, user_name, user_attributes, temporary_password):
        if self.user_exists(user_pool_id, user_name):
            return {}
        kwargs = dict(UserPoolId        = user_pool_id      ,
                      Username          = user_name         ,
                      UserAttributes    = user_attributes   ,
                      TemporaryPassword = temporary_password,
                      #DesiredDeliveryMediums = []          # not working
                      )
        response = self.cognito().admin_create_user(**kwargs)
        return self.format_user_data(response.get('User'))

    def user_delete(self, user_pool_id, user_name):
        if self.user_exists(user_pool_id, user_name):
            client   = self.cognito()
            client.admin_delete_user(UserPoolId=user_pool_id, Username=user_name)
            return True
        return False

    def user_exists(self, user_pool_id, user_name):
        return self.user(user_pool_id, user_name) != {}

    def user_set_password(self, user_pool_id, user_name, password, permanent=True):
        if self.user_exists(user_pool_id, user_name):
            client   = self.cognito()
            try:
                kwargs   = dict(UserPoolId=user_pool_id, Username=user_name, Password=password, Permanent=True)
                client.admin_set_user_password(**kwargs)
                return True
            except client.exceptions.InvalidParameterException:
                return False
        return False

    @index_by
    @group_by
    def users(self, user_pool_id, limit=10):
        response = self.cognito().list_users( UserPoolId=user_pool_id, Limit=limit )
        users = []
        for user_data in response.get('Users'):
            user = self.format_user_data(user_data)
            users.append(user)
        return users

    def format_user_data(self, user_data):
        user = {'user_status'            : user_data.get('UserStatus'                          , None),
                'enabled'                : user_data.get('Enabled'                             , None),
                'user_create_date'       : datetime_to_str(user_data.get('UserCreateDate'      , None)),
                'user_last_modified_date': datetime_to_str(user_data.get('UserLastModifiedDate', None)),
                'username'               : user_data.get('Username'                            , None)}

        for attribute in user_data.get('Attributes', []):
            name       = attribute['Name']
            value      = attribute['Value']
            user[name] = value
        return user

