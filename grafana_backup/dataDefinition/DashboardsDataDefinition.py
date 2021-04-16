from abc import ABC

from grafana_backup.dashboardApi import search_dashboard, get_dashboard
from grafana_backup.dataDefinition.DataDefinition import DataDefinition


class DashboardDataDefinition(DataDefinition, ABC):
    def __init__(self, settings):
        super().__init__(settings, "dashboard")

    def search_data_execute(self, page, limit, grafana_url, http_get_headers, verify_ssl,
                            client_cert, debug):
        return search_dashboard(page, limit, grafana_url, http_get_headers, verify_ssl, client_cert,
                                debug)

    def load_element(self, element, grafana_url, http_get_headers, verify_ssl, client_cert, debug,
                     uid_support):
        api_url = self.get_api_url(element, uid_support)
        (status, content, api_url) = get_dashboard(api_url, grafana_url, http_get_headers,
                                                   verify_ssl, client_cert, debug)

        return status, content['dashboard'], api_url

    def get_element_filename(self, element):
        file_name = super().get_element_filename(element)
        if 'folderUrl' in element and element['folderUrl']:
            file_name = element['folderUrl'].rsplit('/', 1)[1] + "/" + file_name

        return file_name

    @staticmethod
    def get_api_url(element, uid_support):
        if uid_support:
            board_uri = "uid/{0}".format(element['uid'])
        else:
            board_uri = element['uri']
        return board_uri
