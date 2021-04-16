import os
import json
from grafana_backup.dashboardApi import search_folders, get_folder
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
    uid_support = settings.get('UID_SUPPORT')

    folder_path = '{0}/{1}/folders'.format(backup_dir, timestamp)
    log_file = 'all_folders.txt'

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    folders = get_folders(grafana_url, http_get_headers, verify_ssl, client_cert, debug)
    print_horizontal_line()
    get_individual_folder_setting_and_save(folders, folder_path, log_file, grafana_url, http_get_headers, verify_ssl, client_cert, debug, pretty_print, uid_support)
    print_horizontal_line()


def get_folders(grafana_url, http_get_headers, verify_ssl, client_cert, debug):
    print("Searching folders ...")

    (status, content) = search_folders(grafana_url, http_get_headers, verify_ssl, client_cert, debug)

    if status == 200:
        print("    Folders found: {0}".format(len(content)))
        return content
    else:
        print("    Error searching folders:" \
              "\n        status: {0}" \
              "\n        message: {1}".format(status, content))
        return []


def get_individual_folder_setting_and_save(folders, folder_path, log_file, grafana_url, http_get_headers, verify_ssl, client_cert, debug, pretty_print, uid_support):
    if folders:
        with open(u"{0}".format(folder_path + '/' + log_file), 'w+') as f:
            for folder in folders:
                (status, content) = get_folder(folder['uid'], grafana_url, http_get_headers, verify_ssl, client_cert, debug)
                if status == 200:
                    file_name = folder['title'] + "_" + folder['id']

                    file_path = save_json(file_name, folder, folder_path, 'folder', pretty_print)

                    log = 'Folder ID: {0}' \
                          '\n    id: {1}' \
                          '\n    title: {2}' \
                          '\n    saved to: {3}\n' \
                        .format(folder['id'], folder['id'], folder['title'], file_path)
                    print(log)
                    f.write(log)
