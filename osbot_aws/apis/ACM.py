from osbot_utils.decorators.lists.index_by import index_by
from osbot_utils.decorators.methods.catch import catch

from osbot_aws.apis.Session import Session


class ACM:

    def __init__(self):
        self._acm       = None

    def acm(self):
        if self._acm is None:
            self._acm = Session().client('acm')
        return self._acm

    @catch
    def certificate(self, certificate_arn, include_certs=False):
        cert_info = self.acm().describe_certificate(CertificateArn=certificate_arn).get('Certificate')
        if include_certs:
            cert_data = self.acm().get_certificate(CertificateArn=certificate_arn)
            cert_info['Certificate'     ] = cert_data.get('Certificate')
            cert_info['CertificateChain'] = cert_data.get('CertificateChain')

        return cert_info

    @catch
    def certificate_request(self, domain_name, validation_method='DNS'):
        return self.acm().request_certificate(DomainName=domain_name, ValidationMethod=validation_method)


    @catch
    @index_by
    def certificates(self):
        return self.acm().list_certificates().get('CertificateSummaryList')