from abc import ABC

from grafana_backup.dashboardApi import search_alert_channels, get_alert_channel
from grafana_backup.dataDefinition.DataDefinition import DataDefinition


class AlertChannelsDataDefinition(DataDefinition, ABC):
    def __init__(self, settings):
        super().__init__(settings, "alert channel")

    def search_data_execute(self, page, limit, grafana_url, http_get_headers, verify_ssl,
                            client_cert, debug):
        return search_alert_channels(grafana_url, http_get_headers, verify_ssl, client_cert, debug)

    def load_element(self, element, grafana_url, http_get_headers, verify_ssl, client_cert, debug,
                     uid_support):
        return get_alert_channel(element['uid'], grafana_url, http_get_headers, verify_ssl, client_cert, debug)

