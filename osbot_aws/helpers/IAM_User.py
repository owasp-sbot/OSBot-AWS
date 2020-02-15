from functools import lru_cache

from osbot_aws.apis.IAM import IAM


class IAM_User:
    def __init__(self,user_name=None):
        self.iam       = IAM(user_name=user_name)
        self.user      = self.iam.resource().User(name=user_name)


    def arn(self):
        return self.user.arn

    def create(self):
        return self.iam.user_create()

    def delete(self):
        return self.iam.user_delete()

    def exists(self):
        return self.iam.user_exists()

    def _index_by(self, target, attribs, index_by=None):
        try:
            all_data = getattr(target,'all')()
            results  = []
            for value in all_data:
                item = {}
                for attrib in attribs:
                    item[attrib] = getattr(value, attrib)
                results.append(item)
            if index_by is None:
                return results
            indexed = {}
            for item in results:
                indexed[item.get(index_by)] = item
            return indexed
        except Exception as error:
            return {'error': f'{error}'}


    def groups(self, index_by=None):
        return self._index_by(self.user.groups, ['arn','create_date','group_id','group_name','path'], index_by)

    def id(self):
        return self.user.user_id

    def policies(self):
        data = self.user.policies.all()
        for item in data:
            print('------')
        return type(data)

    def tags(self):
        return self.user.tags