import json
import pytest
from unittest.mock import patch, MagicMock
from collections import namedtuple

import gundnsadmin
from gundnsadmin.models.user import User
from gundnsadmin.models.domain import Domain
from gundnsadmin.lib.validators import validate_zone
from gundnsadmin.lib.schema import DomainSchema
from tests.conftest import load_data


class TestUnitApiZoneUser(object):
    @pytest.fixture
    def common_data_mock(self, app, initial_data):

        self.google_setting_patcher = patch(
            'gundnsadmin.services.google.Setting',
            spec=gundnsadmin.models.setting.Setting)
        self.github_setting_patcher = patch(
            'gundnsadmin.services.github.Setting',
            spec=gundnsadmin.models.setting.Setting)
        self.azure_setting_patcher = patch(
            'gundnsadmin.services.azure.Setting',
            spec=gundnsadmin.models.setting.Setting)
        self.oidc_setting_patcher = patch(
            'gundnsadmin.services.oidc.Setting',
            spec=gundnsadmin.models.setting.Setting)
        self.helpers_setting_patcher = patch(
            'gundnsadmin.lib.helper.Setting',
            spec=gundnsadmin.models.setting.Setting)
        self.models_setting_patcher = patch(
            'gundnsadmin.models.setting.Setting',
            spec=gundnsadmin.models.setting.Setting)
        self.domain_model_setting_patcher = patch(
            'gundnsadmin.models.domain.Setting',
            spec=gundnsadmin.models.setting.Setting)
        self.record_model_setting_patcher = patch(
            'gundnsadmin.models.record.Setting',
            spec=gundnsadmin.models.setting.Setting)
        self.server_model_setting_patcher = patch(
            'gundnsadmin.models.server.Setting',
            spec=gundnsadmin.models.setting.Setting)
        self.mock_user_patcher = patch(
            'gundnsadmin.decorators.User',
            spec=gundnsadmin.models.user.User)
        self.mock_hist_patcher = patch(
            'gundnsadmin.routes.api.History',
            spec=gundnsadmin.models.history.History)
        self.mock_setting_patcher = patch(
            'gundnsadmin.routes.api.Setting',
            spec=gundnsadmin.models.setting.Setting)
        self.mock_decorators_setting_patcher = patch(
            'gundnsadmin.decorators.Setting',
            spec=gundnsadmin.models.setting.Setting)
        self.base_route_user_patcher = patch(
            'gundnsadmin.routes.base.User',
            spec=gundnsadmin.models.user.User)

        with app.app_context():
            self.mock_google_setting = self.google_setting_patcher.start()
            self.mock_github_setting = self.github_setting_patcher.start()
            self.mock_azure_setting = self.azure_setting_patcher.start()
            self.mock_oidc_setting = self.oidc_setting_patcher.start()
            self.mock_base_route_user = self.base_route_user_patcher.start()
            self.mock_helpers_setting = self.helpers_setting_patcher.start()
            self.mock_models_setting = self.models_setting_patcher.start()
            self.mock_domain_model_setting = self.domain_model_setting_patcher.start(
            )
            self.mock_record_model_setting = self.record_model_setting_patcher.start(
            )
            self.mock_server_model_setting = self.server_model_setting_patcher.start(
            )
            self.mock_user = self.mock_user_patcher.start()
            self.mock_hist = self.mock_hist_patcher.start()
            self.mock_setting = self.mock_setting_patcher.start()
            self.mock_decorators_setting = self.mock_decorators_setting_patcher.start()

            self.mock_google_setting.return_value.get.side_effect = load_data
            self.mock_github_setting.return_value.get.side_effect = load_data
            self.mock_azure_setting.return_value.get.side_effect = load_data
            self.mock_oidc_setting.return_value.get.side_effect = load_data
            self.mock_helpers_setting.return_value.get.side_effect = load_data
            self.mock_models_setting.return_value.get.side_effect = load_data
            self.mock_domain_model_setting.return_value.get.side_effect = load_data
            self.mock_record_model_setting.return_value.get.side_effect = load_data
            self.mock_server_model_setting.return_value.get.side_effect = load_data
            self.mock_decorators_setting.return_value.get.side_effect = load_data
            self.mock_setting.return_value.get.side_effect = load_data

            self.mockk = MagicMock()
            self.mockk.role.name = "User"

            self.mock_user.query.filter.return_value.first.return_value = self.mockk
            self.mock_user.return_value.is_validate.return_value = True
            self.mock_base_route_user.query.filter.return_value.first.return_value = self.mockk
            self.mock_base_route_user.return_value.is_validate.return_value = True

        yield

        for patcher in [
            self.google_setting_patcher,
            self.github_setting_patcher,
            self.azure_setting_patcher,
            self.oidc_setting_patcher,
            self.base_route_user_patcher,
            self.helpers_setting_patcher,
            self.models_setting_patcher,
            self.domain_model_setting_patcher,
            self.record_model_setting_patcher,
            self.server_model_setting_patcher,
            self.mock_user_patcher,
            self.mock_hist_patcher,
            self.mock_setting_patcher,
            self.mock_decorators_setting_patcher,
        ]:
            patcher.stop()


    def test_create_zone(self, client, common_data_mock, zone_data,
                         basic_auth_user_headers, created_zone_data):
        with patch('gundnsadmin.lib.helper.requests.request') as mock_post, \
                patch('gundnsadmin.routes.api.Domain') as mock_domain:
            mock_post.return_value.status_code = 201
            mock_post.return_value.content = json.dumps(created_zone_data)
            mock_post.return_value.headers = {}
            mock_domain.return_value.update.return_value = True

            res = client.post("/api/v1/pdnsadmin/zones",
                              headers=basic_auth_user_headers,
                              data=json.dumps(zone_data),
                              content_type="application/json")
            data = res.get_json(force=True)
            data['rrsets'] = []

            validate_zone(data)
            assert res.status_code == 201

    def test_get_multiple_zones(self, client, common_data_mock, zone_data,
                                basic_auth_user_headers):
        with patch('gundnsadmin.routes.api.get_user_domains') as mock_user_domains:
            test_domain = Domain(1, name=zone_data['name'].rstrip("."))
            mock_user_domains.return_value = [test_domain]

            res = client.get("/api/v1/pdnsadmin/zones",
                             headers=basic_auth_user_headers)
            data = res.get_json(force=True)

            fake_domain = namedtuple("Domain", data[0].keys())(*data[0].values())
            domain_schema = DomainSchema(many=True)

            json.dumps(domain_schema.dump([fake_domain]))
            assert res.status_code == 200

    def test_delete_zone(self, client, common_data_mock, zone_data,
                         basic_auth_user_headers):
        with patch('gundnsadmin.lib.helper.requests.request') as mock_delete, \
                patch('gundnsadmin.routes.api.Domain') as mock_domain, \
                patch('gundnsadmin.routes.api.get_user_domains') as mock_user_domains:
            test_domain = Domain(1, name=zone_data['name'].rstrip("."))

            mock_domain.return_value.update.return_value = True
            mock_user_domains.return_value = [test_domain]
            mock_delete.return_value.status_code = 204
            mock_delete.return_value.content = ''

            zone_url_format = "/api/v1/pdnsadmin/zones/{0}"
            zone_url = zone_url_format.format(zone_data['name'].rstrip("."))
            res = client.delete(zone_url, headers=basic_auth_user_headers)

            assert res.status_code == 204
