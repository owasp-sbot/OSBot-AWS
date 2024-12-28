import time
from typing                                     import List
from osbot_utils.decorators.methods.type_safe   import type_safe
from osbot_aws.apis.Session                     import Session
from osbot_utils.base_classes.Kwargs_To_Self    import Kwargs_To_Self

class Cloud_Front(Kwargs_To_Self):

    def client(self):
        return Session().client('cloudfront',region_name='us-east-1')


    def distributions(self):
        response = self.client().list_distributions()       # todo: add support for when not all values are returned
        items = response.get('DistributionList', {}).get('Items', [])
        return items

    def invalidate_path(self, distribution_id: str, paths: str):
        return self.invalidate_paths(distribution_id, [paths])

    @type_safe
    def invalidate_paths(self, distribution_id:str, paths: List[str]):
        kwargs = dict(DistributionId    = distribution_id,
                      InvalidationBatch = { 'Paths'          : { 'Quantity': len(paths)            ,
                                                                 'Items'   : paths                 },
                                            'CallerReference': f'invalidation-{int(time.time()) }' })  # Unique reference
        response = self.client().create_invalidation(**kwargs)
        return response
