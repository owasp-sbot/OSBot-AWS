from osbot_aws.aws.dynamo_db.models.DyDB__Resource import DyDB__Resource


class Resource__Config(DyDB__Resource):

    def version(self):
        return self.document.get('version')

    def version__update(self, value):
        self.set_field('version', value)
        self.document['version'] = value