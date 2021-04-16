from abc import ABC

from grafana_backup.dashboardApi import search_users, get_user, get_user_org
from grafana_backup.dataDefinition.DataDefinition import DataDefinition


class UsersDataDefinition(DataDefinition, ABC):
    def __init__(self, settings):
        super().__init__(settings, "user")
        self.http_get_headers = settings.get('HTTP_GET_HEADERS_BASIC_AUTH')

    def search_data_execute(self, page, limit, grafana_url, http_get_headers, verify_ssl,
                            client_cert, debug):
        return search_users(page, limit, grafana_url, http_get_headers, verify_ssl, client_cert,
                            debug)

    def load_element(self, element, grafana_url, http_get_headers, verify_ssl, client_cert, debug,
                     uid_support):
        (status, content, api_url) = get_user(element['id'], grafana_url, http_get_headers, verify_ssl,
                                     client_cert, debug)
        if status == 200:
            (status, organizations_content, organizations_api_url) = get_user_org(element['id'], grafana_url,
                                                           http_get_headers, verify_ssl,
                                                           client_cert, debug)
            if status == 200:
                content.update({'orgs': organizations_content})

        return status, content, api_url

