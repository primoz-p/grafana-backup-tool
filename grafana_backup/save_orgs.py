import os
import json
from grafana_backup.dashboardApi import search_orgs, get_org
from grafana_backup.commons import to_python2_and_3_compatible_string, print_horizontal_line, save_json


def main(args, settings):
    backup_dir = settings.get('BACKUP_DIR')
    timestamp = settings.get('TIMESTAMP')
    limit = settings.get('SEARCH_API_LIMIT')
    grafana_url = settings.get('GRAFANA_URL')
    http_get_headers_basic_auth = settings.get('HTTP_GET_HEADERS_BASIC_AUTH')
    verify_ssl = settings.get('VERIFY_SSL')
    client_cert = settings.get('CLIENT_CERT')
    debug = settings.get('DEBUG')
    pretty_print = settings.get('PRETTY_PRINT')

    folder_path = '{0}/{1}/organizations'.format(backup_dir, timestamp)
    log_file = 'all_organizations.txt'

    if http_get_headers_basic_auth:
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        save_orgs(folder_path, log_file, grafana_url, http_get_headers_basic_auth, verify_ssl, client_cert, debug, pretty_print)
    else:
        print('[ERROR] Backing up organizations needs to set GRAFANA_ADMIN_ACCOUNT and GRAFANA_ADMIN_PASSWORD first.')
        print_horizontal_line()


def get_orgs(grafana_url, http_get_headers, verify_ssl, client_cert, debug):
    (status, content) = search_orgs(grafana_url,                                    http_get_headers,                                    verify_ssl,                                    client_cert,                                    debug)
    if status == 200:
        print("    Orgs found: {0}".format(len(content)))
        return content
    else:
        print("    Error searching orgs:" \
              "\n        status: {0}" \
              "\n        message: {1}".format(status, content))
        return []


def get_individual_org_info_and_save(orgs, folder_path, log_file, grafana_url, http_get_headers,
                                     verify_ssl, client_cert, debug, pretty_print):
    if orgs:
        with open(u"{0}".format(folder_path + '/' + log_file), 'w') as f:
            for organization in orgs:
                (status, content) = get_org(organization['id'], grafana_url, http_get_headers, verify_ssl, client_cert, debug)
                if status == 200:
                    file_name = organization['name'] + "_" + organization['id']

                    file_path = save_json(file_name, organization, folder_path, 'organization', pretty_print)

                    log = 'Organization ID: {0}' \
                          '\n    id: {1}' \
                          '\n    title: {2}' \
                          '\n    saved to: {3}\n' \
                        .format(organization['id'], organization['id'], organization['title'], file_path)
                    print(log)
                    f.write(log)


def save_orgs(folder_path, log_file, grafana_url, http_get_headers, verify_ssl, client_cert, debug, pretty_print):
    orgs = get_orgs(grafana_url, http_get_headers, verify_ssl,
                    client_cert, debug)
    print_horizontal_line()
    get_individual_org_info_and_save(orgs, folder_path, log_file, grafana_url, http_get_headers,
                                     verify_ssl, client_cert, debug, pretty_print)
    print_horizontal_line()
