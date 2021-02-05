from botocore.exceptions import ClientError

from osbot_utils.decorators.methods.remove_return_value import remove_return_value

from osbot_utils.decorators.lists.index_by import index_by

from osbot_aws.apis.Session               import Session

from osbot_utils.decorators.methods.cache import cache


class Events:
    @cache
    def client(self):
        return Session().client('events')

    @remove_return_value('ResponseMetadata')
    def archive(self, archive_name):
        return self.client().describe_archive(ArchiveName=archive_name)

    @index_by
    def archives(self, event_source_arn=None, name_prefix=None):
        kwargs = {}
        if event_source_arn: kwargs['EventSourceArn'] = event_source_arn
        if name_prefix: kwargs['NamePrefix'] = name_prefix
        return self.client().list_archives(**kwargs).get('Archives')

    @remove_return_value('ResponseMetadata')
    def events_put(self, events):
        return self.client().put_events(Entries=events)


    @remove_return_value('ResponseMetadata')
    def rule(self, rule_name, event_bus_name=None):
        try:
            kwargs = {'Name': rule_name}
            if event_bus_name: kwargs['EventBusName'] = event_bus_name
            return self.client().describe_rule(**kwargs)
        except ClientError as e:                                                    # todo: refactor this pattern into a helper with statement (which receives as param the Error.Code value
            if e.response.get('Error', {}).get('Code') == 'ResourceNotFoundException':
                return None
            raise

    @remove_return_value('ResponseMetadata')
    def rule_create(self, rule_name, event_source, description=None, role_arn=None, tags=None):
        kwargs = {  "Name"          : rule_name                            ,
                    "EventPattern"  : f'{{ "source": ["{event_source}"] }}',
                    "Description"   : description or ''                    ,
                    "State"         : 'ENABLED'                            ,
                    "Tags"          : []                                   ,
                    #ScheduleExpression = 'string',
                    #EventBusName = 'string'
                    }
        if role_arn: kwargs['RoleArn'] = role_arn
        if tags:
            for key,value in tags.items():
                kwargs['Tags'].append({'Key':key, 'Value':value})
        return self.client().put_rule(**kwargs).get('RuleArn')

    def rule_delete(self, rule_name , event_bus_name=None):
        if self.rule_not_exists(rule_name): return False
        kwargs = { "Name" :rule_name,
                   "Force": True    }
        if event_bus_name: kwargs['EventBusName'] = event_bus_name
        self.client().delete_rule(**kwargs)
        return self.rule_not_exists(rule_name)

    def rule_exists(self, rule_name):
        return self.rule(rule_name=rule_name) is not None

    def rule_not_exists(self, rule_name):
        return self.rule_exists(rule_name) is False

    @index_by
    def rules(self, name_prefix=None, event_bus_name=None):
        kwargs = {}
        if name_prefix   : kwargs['NamePrefix'  ] = name_prefix
        if event_bus_name: kwargs['EventBusName'] = event_bus_name
        return self.client().list_rules(**kwargs).get('Rules')

    @remove_return_value('ResponseMetadata')
    def target_create(self, rule_name, target_id, target_arn):
        target = {"Arn": target_arn ,
                  "Id" : target_id  }

        kwargs = { "Rule"   : rule_name    ,
                   "Targets" : [target]     }

        return self.client().put_targets(**kwargs)

    @remove_return_value('ResponseMetadata')
    def target_delete(self, rule_name, target_id, event_bus_name=None):
        kwargs = {"Rule" : rule_name   ,
                  "Ids"  : [target_id] ,
                  "Force": True        }
        if event_bus_name: kwargs['EventBusName'] = event_bus_name
        return self.client().remove_targets(**kwargs)

    @index_by
    @remove_return_value('ResponseMetadata')
    def targets(self, rule_name, event_bus_name=None):
        kwargs = {'Rule': rule_name}
        if event_bus_name: kwargs['EventBusName'] = event_bus_name
        return self.client().list_targets_by_rule(**kwargs).get('Targets')