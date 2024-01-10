from functools import cache

from osbot_utils.decorators.methods.remove_return_value import remove_return_value

#from osbot_utils.decorators.methods.cache_on_self import cache_on_self

from osbot_aws.aws.iam.IAM import IAM

class IAM_User:
    def __init__(self, user_name=None):
        self.user_name = user_name

    @cache
    def iam(self):
        return IAM(user_name=self.user_name)

    @cache
    def user(self):
        return self.iam().resource().User(name=self.user_name)

    def arn(self):
        return self.user().arn

    def create(self):
        return self.iam().user_create()

    def delete(self):
        return self.iam().user_delete()

    def exists(self):
        return self.iam().user_exists()

    def _get_attribs(self,target,attribs):
        item = {}
        for attrib in attribs:
            item[attrib] = getattr(target, attrib)
        return item

    def _index_by(self, target, attribs, index_by=None):
        try:
            all_data = getattr(target,'all')()
            results  = []
            for value in all_data:
                results.append(self._get_attribs(value,attribs))
            if index_by is None:
                return results
            indexed = {}
            for item in results:
                indexed[item.get(index_by)] = item
            return indexed
        except Exception as error:
            return {'error': f'{error}'}

    def access_keys(self,index_by=None):
        attribs = ['user_name','id','access_key_id', 'create_date','status']
        return self._index_by(self.user().access_keys, attribs, index_by)

    def groups(self, index_by=None):
        return self._index_by(self.user().groups, ['arn','create_date','group_id','group_name','path'], index_by)

    def user_id(self):
        return self.user().user_id

    def info(self):
        attribs = ['arn', 'create_date', 'password_last_used', 'path', 'permissions_boundary', 'tags', 'user_id', 'user_name']
        return self._get_attribs(self.user(), attribs)

    def policies(self, index_by=None):
        attribs = ['attachment_count', 'create_date', 'default_version_id', 'description', 'is_attachable', 'path', 'permissions_boundary_usage_count', 'policy_id', 'policy_name', 'update_date']
        return self._index_by(self.user().attached_policies,attribs, index_by)

    # def roles(self):
    #     return self.iam().roles()

    @remove_return_value('ResponseMetadata')
    def set_password(self, password, reset_required=True):
        try:
            return self.iam().login_profile_create(password, reset_required=reset_required)
        except Exception as error:
            return {'error' : f'{error}'}

    def user_policies(self, index_by=None):
        attribs = ['attachment_count', 'create_date', 'default_version_id', 'description', 'is_attachable', 'path', 'permissions_boundary_usage_count', 'policy_id', 'policy_name', 'update_date']
        return self._index_by(self.user().policies,attribs, index_by)

    def tags(self):
        return self.user().tags