from abc import ABC

from grafana_backup.dashboardApi import search_orgs, get_org
from grafana_backup.dataDefinition.DataDefinition import DataDefinition


class OrganizationsDataDefinition(DataDefinition, ABC):
    def __init__(self, settings):
        super().__init__(settings, "organization")
        self.http_get_headers = settings.get('HTTP_GET_HEADERS_BASIC_AUTH')

    def search_data_execute(self, page, limit, grafana_url, http_get_headers, verify_ssl,
                            client_cert, debug):
        return search_orgs(grafana_url, http_get_headers, verify_ssl, client_cert, debug)

    def load_element(self, element, grafana_url, http_get_headers, verify_ssl, client_cert, debug,
                     uid_support):
        return get_org(element['id'], grafana_url, http_get_headers, verify_ssl, client_cert, debug)

