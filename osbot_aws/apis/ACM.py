from osbot_aws.apis.Session import Session


class ACM:

    def __init__(self):
        self._acm       = None

    # helpers

    def _index_by(self, values, index_by=None):
        if index_by is None:
            return list(values)
        results = {}
        for item in values:
            results[item.get(index_by)] = item
        return results

    def acm(self):
        if self._acm is None:
            self._acm = Session().client('acm')
        return self._acm

    # main methods

    def certificates(self, index_by=None):
        return self._index_by(self.acm().list_certificates().get('CertificateSummaryList'),index_by=index_by)