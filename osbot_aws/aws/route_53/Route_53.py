from osbot_utils.utils.Misc import wait_for

from osbot_utils.decorators.methods.cache_on_self import cache_on_self

from osbot_utils.utils.Dev import pprint

from osbot_utils.decorators.methods.remove_return_value import remove_return_value

from osbot_utils.decorators.lists.group_by import group_by
from osbot_utils.decorators.lists.index_by import index_by
from osbot_utils.decorators.methods.catch import catch

from osbot_aws.apis.Session            import Session


class Route_53:

    @cache_on_self
    def client(self):
        return Session().client('route53',region_name='us-east-1')

    @cache_on_self
    def client_domains(self):
        return Session().client('route53domains',region_name='us-east-1')

    # Main methods

    def change_details(self, change_id):
        response = self.client().get_change(Id=change_id)
        return response.get('ChangeInfo')

    @catch
    @index_by
    def domains(self):
        return self.client_domains().list_domains().get('Domains')

    @remove_return_value('ResponseMetadata')
    def hosted_zone(self, hosted_zone_id):
        return self.client().get_hosted_zone(Id= hosted_zone_id)

    @catch
    @index_by
    def hosted_zones(self):
        return self.client().list_hosted_zones().get('HostedZones')

    def record_set__change(self, hosted_zone_id, action, resource_record_set):
        change = { "Action"           : action,
                   "ResourceRecordSet": resource_record_set }
        return self.record_set__changes(hosted_zone_id, [change])

    def record_set__changes(self, hosted_zone_id, changes):
        kwargs = {  "HostedZoneId" : hosted_zone_id,
                    "ChangeBatch": { "Changes": changes }}

        return self.client().change_resource_record_sets(**kwargs)

    def record_set__delete__alias(self, hosted_zone_id, record_name, record_type, alias_dns_name, alias_hosted_zone_id):
        resource_record_set = dict(Name        = record_name,
                                   Type        = record_type,
                                   AliasTarget = dict(DNSName              = alias_dns_name      ,
                                                      HostedZoneId         = alias_hosted_zone_id,
                                                      EvaluateTargetHealth = False               ))
        kwargs = dict(hosted_zone_id      = hosted_zone_id      ,
                      action              = 'DELETE'            ,
                      resource_record_set = resource_record_set )

        return self.record_set__change(**kwargs)

    @catch
    def record_set__upsert(self, record_name, record_type, alias_target,hosted_zone_id,alias_hosted_zone_id):
        params = {  "HostedZoneId" : hosted_zone_id,
                    "ChangeBatch": { "Changes": [{ "Action": "UPSERT",
                                                   "ResourceRecordSet": { "Name": record_name,
                                                                          "Type": record_type,
                                                                          "AliasTarget": { "DNSName"             : alias_target         ,
                                                                                           "HostedZoneId"        : alias_hosted_zone_id ,
                                                                                           "EvaluateTargetHealth": False                }}}]}}
        return self.client().change_resource_record_sets(**params)



    def record_set(self, hosted_zone_id, record_name, record_type):
        kwargs = dict(HostedZoneId    = hosted_zone_id,
                      StartRecordName = record_name   ,                                         # this is a trick to get the search
                      StartRecordType = record_type   ,                                         # since the search is 'starts with'
                      MaxItems        = "1"           )                                         # we ask for just one


        record_sets = self.client().list_resource_record_sets(**kwargs).get('ResourceRecordSets')

        if len(record_sets) == 1:                                                               # if we got an answer
            record_set = record_sets[0]                                                         # get the first
            record_set_name = record_set.get('Name')                                            # get the record_set name
            if record_set_name == record_name or record_set_name == record_name + '.':          # if the name matches the provided name or the provided name + '.'
                return    record_set                                                            # return it
        return {}

    @catch
    @group_by
    def record_sets(self, hosted_zone_id):
        return self.client().list_resource_record_sets(HostedZoneId=hosted_zone_id).get('ResourceRecordSets')

    @remove_return_value('ResponseMetadata')
    def check_dns_answer(self, hosted_zone_id, record_name, record_type='A'):
        kwargs = dict(HostedZoneId = hosted_zone_id ,
                      RecordName   = record_name    ,
                      RecordType   = record_type    ) #'SOA' | 'A' | 'TXT' | 'NS' | 'CNAME' | 'MX' | 'NAPTR' | 'PTR' | 'SRV' | 'SPF' | 'AAAA' | 'CAA' | 'DS',)
        return self.client().test_dns_answer(**kwargs)

    # this can actulaly take quite a long time, some DNS changes take more than 1 minute
    def wait_for_change_status(self, change_id, status, max_attempts=30, sleep_for=1):
        for i in range(0, max_attempts):
            response       = self.change_details(change_id)
            current_status = response.get('Status')
            if current_status == status:
                return True
            wait_for(sleep_for)
        return False

    def wait_for_change_completed(self, change_id, max_attempts=30):
        return self.wait_for_change_status(change_id, 'INSYNC', max_attempts=max_attempts)