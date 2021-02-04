from osbot_aws.apis.Session import Session


class SQS:

    def client(self):
        return Session().client('sqs')