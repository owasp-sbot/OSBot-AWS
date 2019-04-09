from osbot_aws.apis.Lambda import Lambda


class Lambda_Package:
    def __init__(self,name):
        self._lambda = Lambda(name)

    def create(self):
        return self._lambda.create()

    def delete(self):
        return self._lambda.delete()