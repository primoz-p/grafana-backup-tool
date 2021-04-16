from abc import ABC

from grafana_backup.dashboardApi import search_folders, get_folder, search_datasource, \
    get_datasource
from grafana_backup.dataDefinition.DataDefinition import DataDefinition


class DataSourcesDataDefinition(DataDefinition, ABC):
    def __init__(self, settings):
        super().__init__(settings, "datasource")

    def search_data_execute(self, page, limit, grafana_url, http_get_headers, verify_ssl,
                            client_cert, debug):
        return search_datasource(grafana_url, http_get_headers, verify_ssl, client_cert, debug)

    def load_element(self, element, grafana_url, http_get_headers, verify_ssl, client_cert, debug,
                     uid_support):
        return get_datasource(element['id'], grafana_url, http_get_headers, verify_ssl, client_cert, debug)

