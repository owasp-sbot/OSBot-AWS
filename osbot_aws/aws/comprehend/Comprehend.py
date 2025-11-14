from osbot_utils.decorators.methods.cache_on_self   import cache_on_self
from osbot_utils.type_safe.Type_Safe                import Type_Safe
from osbot_aws.apis.Session                         import Session
from osbot_aws.aws.comprehend.Comprehend__Batch import Comprehend__Batch
from osbot_aws.aws.comprehend.Comprehend__Detect    import Comprehend__Detect
from osbot_aws.aws.session.Session__Kwargs          import Session__Kwargs


class Comprehend(Type_Safe):
    session_kwargs      : Session__Kwargs

    @cache_on_self
    def client(self):
        return self.session().client(service_name = 'comprehend'                     ,
                                     region_name  = self.session_kwargs.region_name  ,
                                     endpoint_url =  self.session_kwargs.endpoint_url)


    def session(self):
        return Session()

    @cache_on_self
    def detect(self):
        return Comprehend__Detect(client=self.client())

    @cache_on_self
    def batch(self):
        return Comprehend__Batch(client=self.client())