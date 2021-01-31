import boto3

from osbot_utils.decorators.lists.index_by import index_by
from osbot_utils.decorators.methods.cache  import cache
from osbot_aws.apis.Session                import Session


class Cloud_Watch():
    def __init__(self):
        pass

    @cache
    def client(self):
        return Session().client('cloudwatch')

    def alarms(self):
        result = self.client().describe_alarms()
        return { "composite_alarms": result.get('CompositeAlarms'),
                 "metric_alarms"   : result.get('MetricAlarms'   )}

    def alarms_for_metric(self, metric_name, namespace):
        result = self.client().describe_alarms_for_metric(MetricName=metric_name, Namespace=namespace)
        return result

    def anomaly_detectors(self):
        result = self.client().describe_anomaly_detectors().get('AnomalyDetectors')
        return result

    @index_by
    def dashboards(self):
        return self.client().list_dashboards().get('DashboardEntries')

    def insight_rules(self):
        result = self.client().describe_insight_rules().get('InsightRules')
        return result

    def metrics(self):                                          # todo add filter and pagination
        return self.client().list_metrics().get('Metrics')


    def tags_for_resource(self, resource_arn):
        result = self.client().list_tags_for_resource(ResourceARN=resource_arn)
        return result



