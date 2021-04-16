from abc import ABC

from grafana_backup.dashboardApi import search_folders, get_folder
from grafana_backup.dataDefinition.DataDefinition import DataDefinition


class FoldersDataDefinition(DataDefinition, ABC):
    def __init__(self, settings):
        super().__init__(settings, "folder")

    def search_data_execute(self, page, limit, grafana_url, http_get_headers, verify_ssl,
                            client_cert, debug):
        return search_folders(grafana_url, http_get_headers, verify_ssl, client_cert, debug)

    def load_element(self, element, grafana_url, http_get_headers, verify_ssl, client_cert, debug,
                     uid_support):
        return get_folder(element['uid'], grafana_url, http_get_headers, verify_ssl, client_cert, debug)

