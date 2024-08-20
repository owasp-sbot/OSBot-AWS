from unittest               import TestCase

import pytest

from osbot_aws.aws.apigateway.API_Gateway_V2 import API_Gateway_V2
from osbot_aws.testing.TestCase__API_Gateway_V2 import TestCase__API_Gateway_V2
from osbot_utils.utils.Misc import list_set
from osbot_utils.utils.Objects import obj_info


@pytest.mark.skip('needs active API Gateway setup')
class test_API_Gateway_V2(TestCase__API_Gateway_V2):
    api_gateway : API_Gateway_V2

    def test_client(self):
        client = self.api_gateway_v2.client()
        assert client.meta.region_name                      == 'eu-west-1'        # todo: move this to a global OSBot_AWS Config
        assert client.meta.service_model.service_name       == 'apigatewayv2'
        assert list_set(client.meta.method_to_api_mapping)  == ['create_api', 'create_api_mapping', 'create_authorizer', 'create_deployment', 'create_domain_name', 'create_integration', 'create_integration_response', 'create_model', 'create_route', 'create_route_response', 'create_stage', 'create_vpc_link',
                                                                 'delete_access_log_settings', 'delete_api', 'delete_api_mapping', 'delete_authorizer', 'delete_cors_configuration', 'delete_deployment', 'delete_domain_name', 'delete_integration', 'delete_integration_response', 'delete_model', 'delete_route', 'delete_route_request_parameter', 'delete_route_response', 'delete_route_settings','delete_stage', 'delete_vpc_link',
                                                                 'export_api', 'get_api', 'get_api_mapping', 'get_api_mappings', 'get_apis', 'get_authorizer', 'get_authorizers', 'get_deployment', 'get_deployments', 'get_domain_name', 'get_domain_names', 'get_integration', 'get_integration_response', 'get_integration_responses', 'get_integrations', 'get_model', 'get_model_template', 'get_models', 'get_route', 'get_route_response', 'get_route_responses', 'get_routes', 'get_stage', 'get_stages', 'get_tags', 'get_vpc_link', 'get_vpc_links',
                                                                 'import_api',
                                                                 'reimport_api', 'reset_authorizers_cache',
                                                                 'tag_resource', 'untag_resource', 'update_api', 'update_api_mapping', 'update_authorizer', 'update_deployment', 'update_domain_name', 'update_integration', 'update_integration_response', 'update_model', 'update_route', 'update_route_response', 'update_stage', 'update_vpc_link']

    def test_api(self):
        with self.api_gateway_v2 as _:
            for api_name, api_details in _.apis_by_name().items():
                assert list_set(api_details) == ['ApiEndpoint', 'ApiId', 'ApiKeySelectionExpression', 'CreatedDate',
                                                 'DisableExecuteApiEndpoint', 'Name', 'ProtocolType', 'RouteSelectionExpression', 'Tags']
                api_id = api_details.get("ApiId")
                assert _.api(api_id) == api_details
                break


