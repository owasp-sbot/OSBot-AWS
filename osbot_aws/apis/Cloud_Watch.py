import boto3
from osbot_utils.utils.Dev import pprint

from osbot_aws.apis.Boto_Helpers import Boto_Helpers

from osbot_utils.utils.Files import file_create_from_bytes

from osbot_utils.utils.Json import json_parse, json_to_str

from osbot_utils.utils.Misc import list_set, unique

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

    def dashboard(self, dashboard_name):
        try:
            dashboard_data = self.client().get_dashboard(DashboardName=dashboard_name)
            dashboard = {"arn"    : dashboard_data.get('DashboardArn' ),
                         "widgets": (json_parse(dashboard_data.get('DashboardBody')).get('widgets')),
                         "name"   : dashboard_data.get('DashboardName') }
            from osbot_utils.utils.Dev import pprint
            #pprint(dashboard_data)
            return dashboard
        except Exception:          # can't use botocore.errorfactory.ResourceNotFound because that is not exposed
            return {}

    @index_by
    def dashboards(self):
        return self.client().list_dashboards().get('DashboardEntries')

    def dashboards_names(self):
        return list_set(self.dashboards(index_by='DashboardName'))

    def insight_rules(self):
        result = self.client().describe_insight_rules().get('InsightRules')
        return result

    # see https://docs.aws.amazon.com/AmazonCloudWatch/latest/APIReference/CloudWatch-Metric-Widget-Structure.html#CloudWatch-Metric-Widget-Metrics-Array-Format
    # formula is [Namespace, MetricName, Dimension1Name, Dimension1Value, Dimension2Name, Dimension2Value...{Options Object}]
    def metric_widget_image(self, metric_widget, save_to_disk=True, path_image_file=None):
        if type(metric_widget) is not str:
            metric_widget = json_to_str(metric_widget)
        response = self.client().get_metric_widget_image(MetricWidget=metric_widget)
        png_bytes = response.get('MetricWidgetImage')
        if save_to_disk:
            return file_create_from_bytes(bytes=png_bytes, extension=".png", path=path_image_file)
        return png_bytes

    def metric_image(self, namespace, metric_name, dimensions, options=None, region=None, title=None, path_image_file=None):
        if options is None:
            options = {}
        metric = [namespace, metric_name]
        if dimensions:
            for name, value in dimensions.items():
                metric.append(name )         # dimension_name_i
                metric.append(value)         # dimension_value_i
        if options:
            metric.append(options)

        metric_widget = { "metrics": [metric]}
        if region:
            metric_widget['region'] = region
        if title:
            metric_widget['title'] = title

        #"title": "Title of the graph",
            # "view": "timeSeries",
            # "stacked": false,
            # "width": 600,
            # "height": 400,
            # "start": "-PT3H",
            # "end": "P0D"
        return self.metric_widget_image(metric_widget=metric_widget, path_image_file=path_image_file)

    def metric_list_raw(self, namespace, metric_name=None, dimensions=None, recently_active='PT3H'):
        kwargs = {"Namespace": namespace}
        if metric_name:
            kwargs['MetricName'] = metric_name
        if dimensions:
            dimensions_data = []
            for key, value in dimensions.items():
                dimensions_data.append({"Key": key, "Value": value })
            kwargs['Dimensions'] = dimensions_data
        if recently_active:
             kwargs['RecentlyActive'] = recently_active
        return Boto_Helpers.invoke_using_paginator(self.client(), "list_metrics","Metrics", **kwargs)

    # this is paginated, so be careful with using recently_active=None and max_results not being set
    def metric_list(self, namespace, metric_name=None, dimensions=None, recently_active='PT3H', max_results=-1):
        results_paginated = self.metric_list_raw(namespace=namespace, metric_name=metric_name, dimensions=dimensions,recently_active=recently_active)
        results           = {}
        items_added       = 0
        for result in results_paginated:
            #pprint(result)
            _dimensions  = result.get('Dimensions')
            _metric_name = result.get('MetricName')
            _namespace   = result.get('Namespace')

            if results.get(_namespace) is None:
                results[_namespace] = {}
            result_namespace = results[_namespace]

            if result_namespace.get(_metric_name) is None:
                result_namespace[_metric_name] = {}
            result_metric_name = result_namespace[_metric_name]

            for result_dimension in _dimensions:
                dimension_name  = result_dimension.get('Name')
                dimension_value = result_dimension.get('Value')

                if result_metric_name.get(dimension_name) is None:
                    result_metric_name[dimension_name] = []
                result_dimension_name = result_metric_name[dimension_name]

                result_dimension_name.append(dimension_value)
                items_added+=1
            if max_results !=-1 and items_added > max_results:
                break
        pprint(items_added)
        # sort and unique dimensions data
        for namespace in results.values():
            for metric_name, metric_values in namespace.items():
                for dimension_name, dimension_values in metric_values.items():
                    metric_values[dimension_name] = unique(metric_values[dimension_name])

        return results

    def metric_statistics(self, namespace, metric_name, dimensions, start_time=None, end_time=None, period=60, statistics=None, extended_statistics=None, unit=None):
        kwargs = {  "Namespace" : namespace   ,
                    "MetricName": metric_name ,
                    "Dimensions": dimensions  ,       # { 'Name': 'string', 'Value': 'string'},
                    "Period"    : period
                }
        if start_time:
            kwargs['StartTime'] = start_time
        if start_time:
            kwargs['EndTime'] = end_time
        if statistics:
            kwargs['Statistics'] = statistics       # 'SampleCount'|'Average'|'Sum'|'Minimum'|'Maximum',
        if statistics:
            kwargs['ExtendedStatistics'] = extended_statistics
        if unit:
            kwargs['Unit'] = unit                   # 'Seconds'|'Microseconds'|'Milliseconds'|'Bytes'|'Kilobytes'|'Megabytes'|'Gigabytes'|'Terabytes'|'Bits'|'Kilobits'|'Megabits'|'Gigabits'|'Terabits'|'Percent'|'Count'|'Bytes/Second'|'Kilobytes/Second'|'Megabytes/Second'|'Gigabytes/Second'|'Terabytes/Second'|'Bits/Second'|'Kilobits/Second'|'Megabits/Second'|'Gigabits/Second'|'Terabits/Second'|'Count/Second'|'None'
        return self.client().get_metric_statistics(**kwargs)




    def metrics(self):                                          # todo add filter and pagination
        return self.client().list_metrics().get('Metrics')

    def namespaces_list(self):
        return ["AWS/AmplifyHosting" , "AWS/ApiGateway" , "AWS/AppRunner" , "AWS/AppStream" , "AWS/AppSync" ,
                "AWS/Athena" , "Backup" , "AWS/Billing" , "AWS/CertificateManager" , "AWS/ACMPrivateCA" ,
                "AWS/Chatbot" , "AWS/ClientVPN" , "AWS/CloudFront" , "AWS/CloudHSM" , "AWS/CloudSearch" ,
                "AWS/Logs" , "AWS/CodeBuild" , "AWS/CodeGuruProfiler" , "AWS/Cognito" , "AWS/Connect" ,
                "AWS/DataLifecycleManager" , "AWS/DataSync" , "AWS/DMS" , "AWS/DX" , "AWS/DocDB" , "AWS/DynamoDB" ,
                "AWS/DAX" , "AWS/EC2" , "AWS/ElasticGPUs" , "AWS/EC2Spot" , "AWS/AutoScaling" , "AWS/ElasticBeanstalk" ,
                "AWS/EBS" , "AWS/ECS" , "AWS/ECS/ManagedScaling" , "AWS/EFS" , "AWS/ElasticInference" , "AWS/ApplicationELB" ,
                "AWS/NetworkELB" , "AWS/GatewayELB" , "AWS/ELB" , "AWS/ElasticTranscoder" , "AWS/ElastiCache" ,
                "AWS/ElastiCache" , "AWS/ES" , "AWS/ElasticMapReduce" , "AWS/MediaConnect" , "AWS/MediaConvert" ,
                "AWS/MediaLive" , "AWS/MediaPackage" , "AWS/MediaStore" , "AWS/MediaTailor" , "AWS/Events" , "AWS/FSx" ,
                "AWS/FSx" , "AWS/GameLift" , "AWS/GlobalAccelerator" , "Glue" , "AWS/GroundStation" , "AWS/HealthLake" ,
                "AWS/Inspector" , "AWS/IVS" , "AWS/IoT" , "AWS/IoTAnalytics" , "AWS/IoTSiteWise" , "AWS/ThingsGraph" ,
                "AWS/KMS" , "AWS/Cassandra" , "AWS/KinesisAnalytics" , "AWS/Firehose" , "AWS/Kinesis" , "AWS/KinesisVideo" ,
                "AWS/Lambda" , "AWS/Lex" , "AWS/Location" , "AWS/LookoutMetrics" , "AWS/ML" , "AWS/Kafka" , "AWS/AmazonMQ" ,
                "AWS/Neptune" , "AWS/NetworkFirewall" , "AWS/OpsWorks" , "AWS/Polly" , "AWS/QLDB" , "AWS/Redshift" ,
                "AWS/RDS" , "AWS/Robomaker" , "AWS/Route53" , "AWS/SageMaker" , "AWS/SDKMetrics" , "AWS/ServiceCatalog" ,
                "AWS/DDoSProtection" , "AWS/SES" , "AWS/SNS" , "AWS/SQS" , "AWS/S3" , "AWS/SWF" , "AWS/States" ,
                "AWS/StorageGateway" , "AWS/SSM-RunCommand" , "AWS/Textract" , "AWS/Timestream" , "AWS/Transfer" ,
                "AWS/Translate" , "AWS/TrustedAdvisor" , "AWS/NATGateway" , "AWS/TransitGateway" , "AWS/VPN" , "AWS/WAFV2" ,
                "WAF" , "AWS/WorkMail" , "AWS/WorkSpaces"]

    def namespace_metrics(self, namespace, metric_name=None, dimensions=None, recently_active='PT3H'):
        result = self.metric_list(namespace=namespace, metric_name=metric_name, dimensions=dimensions, recently_active=recently_active)
        namespace_data = result.get(namespace,{})
        metrics = {}
        for metric_name, metric_data in namespace_data.items():
            metrics[metric_name] = list_set(metric_data)
        return metrics

    def tags_for_resource(self, resource_arn):
        result = self.client().list_tags_for_resource(ResourceARN=resource_arn)
        return result





