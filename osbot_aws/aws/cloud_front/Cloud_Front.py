from osbot_aws.apis.Session import Session

from osbot_utils.base_classes.Kwargs_To_Self import Kwargs_To_Self


class Cloud_Front(Kwargs_To_Self):

    def client(self):
        return Session().client('cloudfront',region_name='us-east-1')


    def distributions(self):
        response = self.client().list_distributions()       # todo: add support for when not all values are returned
        items = response.get('DistributionList', {}).get('Items', [])
        return items

