from osbot_aws.apis.Session                                             import Session
from osbot_aws.aws.session.Session__Kwargs                              import Session__Kwargs
from osbot_utils.decorators.methods.cache_on_self                       import cache_on_self
from osbot_utils.type_safe.Type_Safe                                    import Type_Safe


class Comprehend__Base(Type_Safe):
    session_kwargs : Session__Kwargs

    @cache_on_self
    def client(self):
        return self.session().client(service_name = 'comprehend'                     ,
                                     region_name  = self.session_kwargs.region_name  ,
                                     endpoint_url = self.session_kwargs.endpoint_url )

    def session(self):
        return Session()
