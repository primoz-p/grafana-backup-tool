import os
import json
from grafana_backup.dashboardApi import search_datasource
from grafana_backup.commons import print_horizontal_line, save_json


def main(args, settings):
    backup_dir = settings.get('BACKUP_DIR')
    timestamp = settings.get('TIMESTAMP')
    grafana_url = settings.get('GRAFANA_URL')
    http_get_headers = settings.get('HTTP_GET_HEADERS')
    verify_ssl = settings.get('VERIFY_SSL')
    client_cert = settings.get('CLIENT_CERT')
    debug = settings.get('DEBUG')
    pretty_print = settings.get('PRETTY_PRINT')

    folder_path = '{0}/{1}/datasources'.format(backup_dir, timestamp)
    log_file = 'all_datasources.txt'

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    datasources = get_all_datasources_and_save(folder_path, log_file, grafana_url, http_get_headers, verify_ssl, client_cert, debug, pretty_print)
    print_horizontal_line()


def get_datasources(grafana_url, http_get_headers, verify_ssl, client_cert, debug):
    (status, content) = search_datasource(grafana_url, http_get_headers, verify_ssl, client_cert, debug)

    if status == 200:
        print("    Datasources found: {0}".format(len(content)))
        return content
    else:
        print("    Error searching datasources:" \
              "\n        status: {0}" \
              "\n        message: {1}".format(status, content))
        return []


def get_all_datasources_and_save(folder_path, log_file, grafana_url, http_get_headers, verify_ssl, client_cert, debug, pretty_print):
    status_code_and_content = get_datasources(grafana_url, http_get_headers, verify_ssl, client_cert, debug)
    if status_code_and_content[0] == 200:
        datasources = status_code_and_content[1]
        print("There are {0} datasources:".format(len(datasources)))
        with open(u"{0}".format(folder_path + '/' + log_file), 'w') as f:
            for datasource in datasources:
                file_name = datasource['name'] + "_" + datasource['id']

                file_path = save_json(file_name, datasource, folder_path, 'datasource', pretty_print)

                log = 'Datasource ID: {0}' \
                      '\n    id: {1}' \
                      '\n    title: {2}' \
                      '\n    saved to: {3}\n' \
                    .format(datasource['id'], datasource['id'], datasource['title'], file_path)
                print(log)
                f.write(log)
    else:
        print("query datasource failed, status: {0}, msg: {1}".format(status_code_and_content[0],
                                                                      status_code_and_content[1]))
