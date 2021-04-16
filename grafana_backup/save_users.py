import os
import json
from grafana_backup.dashboardApi import get_dashboard, search_users, get_user_org, get_user
from grafana_backup.commons import to_python2_and_3_compatible_string, print_horizontal_line, \
    save_json


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

    if http_get_headers_basic_auth:
        folder_path = '{0}/{1}/users'.format(backup_dir, timestamp)
        log_file = 'all_users.txt'

        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        save_users(folder_path, log_file, limit, grafana_url, http_get_headers_basic_auth,
                   verify_ssl, client_cert, debug, pretty_print)
    else:
        print(
            '[ERROR] Backing up users needs to set ENV GRAFANA_ADMIN_ACCOUNT and GRAFANA_ADMIN_PASSWORD first. \n')
        print_horizontal_line()


def get_users(page, limit, grafana_url, http_get_headers, verify_ssl, client_cert, debug):
    (status, content) = search_users(page, limit, grafana_url, http_get_headers, verify_ssl,
                                     client_cert, debug)
    if status == 200:
        print("    Users found: {0}".format(len(content)))
        return content
    else:
        print("    Error searching users:" \
              "\n        status: {0}" \
              "\n        message: {1}".format(status, content))
        return []


def get_individual_user_and_save(users, folder_path, log_file, grafana_url, http_get_headers,
                                 verify_ssl, client_cert,
                                 debug, pretty_print):
    if users:
        with open(u"{0}".format(folder_path + '/' + log_file), 'w') as f:
            for user in users:
                (status, content) = get_user(user['id'], grafana_url, http_get_headers, verify_ssl,
                                             client_cert, debug)
                if status == 200:
                    user.update(content)

                (status, content) = get_user_org(user['id'], grafana_url, http_get_headers,
                                                 verify_ssl, client_cert, debug)
                if status == 200:
                    user.update({'orgs': content})

                file_name = user['name'] + "_" + user['id']

                file_path = save_json(file_name, user, folder_path, 'user', pretty_print)

                log = 'User ID: {0}' \
                      '\n    id: {1}' \
                      '\n    title: {2}' \
                      '\n    saved to: {3}\n' \
                    .format(user['id'], user['id'], user['title'], file_path)
                print(log)
                f.write(log)


def save_users(folder_path, log_file, limit, grafana_url, http_get_headers, verify_ssl, client_cert,
               debug, pretty_print):
    current_page = 1
    users = get_users(current_page, limit, grafana_url, http_get_headers, verify_ssl, client_cert,
                      debug)
    print_horizontal_line()
    get_individual_user_and_save(users, folder_path, log_file, grafana_url, http_get_headers,
                                 verify_ssl, client_cert,
                                 debug, pretty_print)
    print_horizontal_line()
