import os
import json
from grafana_backup.dashboardApi import search_alert_channels
from grafana_backup.commons import to_python2_and_3_compatible_string, print_horizontal_line, save_json


def main(args, settings):
    backup_dir = settings.get('BACKUP_DIR')
    timestamp = settings.get('TIMESTAMP')
    grafana_url = settings.get('GRAFANA_URL')
    http_get_headers = settings.get('HTTP_GET_HEADERS')
    verify_ssl = settings.get('VERIFY_SSL')
    client_cert = settings.get('CLIENT_CERT')
    debug = settings.get('DEBUG')
    pretty_print = settings.get('PRETTY_PRINT')

    folder_path = '{0}/{1}/alert_channels'.format(backup_dir, timestamp)
    log_file = 'all_alert_channels.txt'

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    alert_channels = get_all_alert_channels_in_grafana(grafana_url, http_get_headers, verify_ssl, client_cert, debug)
    get_individual_alert_channel_and_save(alert_channels, folder_path, log_file, pretty_print)
    print_horizontal_line()


def get_all_alert_channels_in_grafana(grafana_url, http_get_headers, verify_ssl, client_cert, debug):
    (status, content) = search_alert_channels(grafana_url, http_get_headers, verify_ssl, client_cert, debug)
    if status == 200:
        print("    Aler channels found: {0}".format(len(content)))
        return content
    else:
        print("    Error searching alert channels:" \
              "\n        status: {0}" \
              "\n        message: {1}".format(status, content))
        return []


def get_individual_alert_channel_and_save(channels, folder_path, log_file, pretty_print):
    if channels:
        with open(u"{0}".format(folder_path + '/' + log_file), 'w') as f:
            for alert_channel in channels:
                file_name = alert_channel['name'] + "_" + alert_channel['id']

                file_path = save_json(file_name, alert_channel, folder_path, 'alert_channel', pretty_print)

                log = 'Channel ID: {0}' \
                      '\n    id: {1}' \
                      '\n    title: {2}' \
                      '\n    saved to: {3}\n' \
                    .format(alert_channel['id'], alert_channel['id'], alert_channel['title'], file_path)
                print(log)
                f.write(log)
