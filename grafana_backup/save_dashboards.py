import os
from grafana_backup.dashboardApi import search_dashboard, get_dashboard
from grafana_backup.commons import save_json


def main(args, settings):
    backup_dir = settings.get('BACKUP_DIR')
    timestamp = settings.get('TIMESTAMP')
    limit = settings.get('SEARCH_API_LIMIT')
    grafana_url = settings.get('GRAFANA_URL')
    http_get_headers = settings.get('HTTP_GET_HEADERS')
    verify_ssl = settings.get('VERIFY_SSL')
    client_cert = settings.get('CLIENT_CERT')
    debug = settings.get('DEBUG')
    pretty_print = settings.get('PRETTY_PRINT')
    uid_support = settings.get('UID_SUPPORT')

    folder_path = '{0}/{1}/dashboards'.format(backup_dir, timestamp)
    log_file = 'all_dashboards.txt'

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    save_dashboards(folder_path, log_file, grafana_url, http_get_headers,
                    verify_ssl, client_cert, debug, pretty_print, uid_support)


def get_dashboards(page, limit, grafana_url, http_get_headers, verify_ssl, client_cert, debug):
    print("Searching dashboards ...")

    (status, content) = search_dashboard(page, limit, grafana_url, http_get_headers, verify_ssl,
                                         client_cert, debug)
    if status == 200:
        print("    Dashboards found: {0}".format(len(content)))
        return content
    else:
        print("    Error searching dashboards:" \
              "\n        status: {0}" \
              "\n        message: {1}".format(status, content))
        return []


def save_dashboard(dashboard, folder_path, log_file, grafana_url, http_get_headers, verify_ssl,
                   client_cert,
                   debug, pretty_print, uid_support):
    if uid_support:
        board_uri = "uid/{0}".format(dashboard['uid'])
    else:
        board_uri = dashboard['uri']
    board_url = "{0}{1}".format(grafana_url, dashboard['url'])

    url = '{0}/api/dashboards/{1}'.format(grafana_url, board_uri)
    (status, content) = get_dashboard(url, http_get_headers, verify_ssl, client_cert,
                                      debug)
    if status == 200:
        file_name = dashboard['uri'].replace("db/", "") + "_" + dashboard['uid']
        if 'folderTitle' in dashboard and dashboard['folderTitle']:
            file_name = dashboard['folderTitle'] + "/" + file_name

        file_path = save_json(file_name, dashboard, folder_path, 'dashboard',
                              pretty_print)

        log = "Dashboard URI: {0}" \
              "\n    name: '{1}'" \
              "\n    URL: {2}" \
              "\n    id: {3}" \
              "\n    uid: {4}" \
              "\n    saved to: {5}\n" \
            .format(url, dashboard['title'], board_url, dashboard['id'], dashboard['uid'],
                    file_path)
        print(log)
        log_file.write(log)


def save_dashboards(folder_path, log_file, grafana_url, http_get_headers, verify_ssl, client_cert,
                    debug, pretty_print, uid_support):
    limit = 5000  # limit is 5000 above V6.2+
    current_page = 1

    while True:
        dashboards = get_dashboards(current_page, limit, grafana_url, http_get_headers, verify_ssl,
                                    client_cert, debug)
        if not dashboards:
            break

        if dashboards:
            with open(u"{0}".format(folder_path + '/' + log_file), 'w') as f:
                for dashboard in dashboards:
                    save_dashboard(dashboard, folder_path, f, grafana_url, http_get_headers,
                                   verify_ssl, client_cert, debug, pretty_print, uid_support)

        current_page += 1
