import json
import re

import requests

from grafana_backup.commons import log_response


def health_check(grafana_url, http_get_headers, verify_ssl, client_cert, debug):
    url = '{0}/api/health'.format(grafana_url)
    print("\n[Pre-Check] grafana health check: {0}".format(url))
    return send_grafana_get(url, http_get_headers, verify_ssl, client_cert, debug)


def auth_check(grafana_url, http_get_headers, verify_ssl, client_cert, debug):
    url = '{0}/api/auth/keys'.format(grafana_url)
    print("\n[Pre-Check] grafana auth check: {0}".format(url))
    return send_grafana_get(url, http_get_headers, verify_ssl, client_cert, debug)


def uid_feature_check(grafana_url, http_get_headers, verify_ssl, client_cert, debug):
    # Get first dashboard on first page
    (status, content, api_url) = search_dashboard(1, 1, grafana_url, http_get_headers, verify_ssl,                                         client_cert, debug)
    if status == 200 and len(content):
        if 'uid' in content[0]:
            uid_support = True
        else:
            uid_support = False
        return uid_support
    else:
        if len(content):
            return "get dashboards failed, status: {0}, msg: {1}".format(status, content)
        else:
            # No dashboards exist, disable uid feature
            return False


def paging_feature_check(grafana_url, http_get_headers, verify_ssl, client_cert, debug):
    def get_first_dashboard_by_page(page):
        (status, content, api_url) = search_dashboard(page, 1, grafana_url, http_get_headers, verify_ssl,
                                             client_cert, debug)
        if status == 200 and len(content):
            dashboard_values = sorted(content[0].items(), key=lambda kv: str(kv[1]))
            return True, dashboard_values
        else:
            if len(content):
                return False, "get dashboards failed, status: {0}, msg: {1}".format(status, content)
            else:
                # No dashboards exist, disable paging feature
                return False, False

    # Get first dashboard on first page
    (status, content) = get_first_dashboard_by_page(1)
    if status is False and content is False:
        return False  # Paging feature not supported
    elif status is True:
        dashboard_one_values = content
    else:
        return content  # Fail Message

    # Get second dashboard on second page
    (status, content) = get_first_dashboard_by_page(2)
    if status is False and content is False:
        return False  # Paging feature not supported
    elif status is True:
        dashboard_two_values = content
    else:
        return content  # Fail Message

    # Compare both pages
    return dashboard_one_values != dashboard_two_values


def search_dashboard(page, limit, grafana_url, http_get_headers, verify_ssl, client_cert, debug):
    return send_grafana_get(
        '{0}/api/search/?type=dash-db&limit={1}&page={2}'.format(grafana_url, limit, page),
        http_get_headers, verify_ssl, client_cert, debug)


def get_dashboard(uri, grafana_url, http_get_headers, verify_ssl, client_cert, debug):
    return send_grafana_get('{0}/api/dashboards/{1}'.format(grafana_url, uri), http_get_headers,
                            verify_ssl, client_cert, debug)


def search_alert_channels(grafana_url, http_get_headers, verify_ssl, client_cert, debug):
    return send_grafana_get('{0}/api/alert-notifications/lookup'.format(grafana_url),
                            http_get_headers, verify_ssl, client_cert, debug)


def get_alert_channel(uid, grafana_url, http_get_headers, verify_ssl, client_cert, debug):
    return send_grafana_get('{0}/api/alert-notifications/uid/{1}'.format(grafana_url, uid),
                            http_get_headers, verify_ssl, client_cert, debug)


def create_alert_channel(payload, grafana_url, http_post_headers, verify_ssl, client_cert, debug):
    return send_grafana_post('{0}/api/alert-notifications'.format(grafana_url), payload,
                             http_post_headers, verify_ssl, client_cert, debug)


def delete_dashboard(board_uri, grafana_url, http_post_headers):
    r = requests.delete('{0}/api/dashboards/db/{1}'.format(grafana_url, board_uri),
                        headers=http_post_headers)
    return int(r.status_code)


def create_dashboard(payload, grafana_url, http_post_headers, verify_ssl, client_cert, debug):
    return send_grafana_post('{0}/api/dashboards/db'.format(grafana_url), payload,
                             http_post_headers, verify_ssl, client_cert, debug)


def search_datasource(grafana_url, http_get_headers, verify_ssl, client_cert, debug):
    return send_grafana_get('{0}/api/datasources'.format(grafana_url), http_get_headers, verify_ssl,
                            client_cert, debug)


def get_datasource(id, grafana_url, http_get_headers, verify_ssl, client_cert, debug):
    return send_grafana_get('{0}/api/datasources/{1}'.format(grafana_url, id), http_get_headers, verify_ssl,
                            client_cert, debug)


def create_datasource(payload, grafana_url, http_post_headers, verify_ssl, client_cert, debug):
    return send_grafana_post('{0}/api/datasources'.format(grafana_url), payload, http_post_headers,
                             verify_ssl, client_cert, debug)


def search_folders(grafana_url, http_get_headers, verify_ssl, client_cert, debug):
    return send_grafana_get('{0}/api/search/?type=dash-folder'.format(grafana_url),
                            http_get_headers, verify_ssl, client_cert, debug)


def get_folder(uid, grafana_url, http_get_headers, verify_ssl, client_cert, debug):
    return send_grafana_get('{0}/api/folders/{1}'.format(grafana_url, uid), http_get_headers,
                            verify_ssl, client_cert, debug)


def get_folder_id_from_old_folder_url(folder_url, grafana_url, http_post_headers, verify_ssl,
                                      client_cert, debug):
    if folder_url != "":
        # Get folder uid
        matches = re.search('dashboards\/[A-Za-z0-9]{1}\/(.*)\/.*', folder_url)
        uid = matches.group(1)

        response = get_folder(uid, grafana_url, http_post_headers, verify_ssl, client_cert, debug)
        if isinstance(response[1], dict):
            folder_data = response[1]
        else:
            folder_data = json.loads(response[1])
        return folder_data['id']
    return 0


def create_folder(payload, grafana_url, http_post_headers, verify_ssl, client_cert, debug):
    return send_grafana_post('{0}/api/folders'.format(grafana_url), payload, http_post_headers,
                             verify_ssl, client_cert, debug)


def search_orgs(grafana_url, http_get_headers, verify_ssl, client_cert, debug):
    return send_grafana_get('{0}/api/orgs'.format(grafana_url), http_get_headers, verify_ssl,
                            client_cert, debug)


def get_org(id, grafana_url, http_get_headers, verify_ssl=False, client_cert=None, debug=True):
    return send_grafana_get('{0}/api/orgs/{1}'.format(grafana_url, id), http_get_headers,
                            verify_ssl, client_cert, debug)


def create_org(payload, grafana_url, http_post_headers, verify_ssl, client_cert, debug):
    return send_grafana_post('{0}/api/orgs'.format(grafana_url), payload, http_post_headers,
                             verify_ssl, client_cert, debug)


def search_users(page, limit, grafana_url, http_get_headers, verify_ssl, client_cert, debug):
    return send_grafana_get('{0}/api/users?perpage={1}&page={2}'.format(grafana_url, limit, page),
                            http_get_headers, verify_ssl, client_cert, debug)


def get_user(id, grafana_url, http_get_headers, verify_ssl=False, client_cert=None, debug=True):
    return send_grafana_get('{0}/api/users/{1}'.format(grafana_url, id), http_get_headers,
                            verify_ssl, client_cert, debug)


def get_user_org(id, grafana_url, http_get_headers, verify_ssl=False, client_cert=None, debug=True):
    return send_grafana_get('{0}/api/users/{1}/orgs'.format(grafana_url, id), http_get_headers,
                            verify_ssl, client_cert, debug)


def create_user(payload, grafana_url, http_post_headers, verify_ssl, client_cert, debug):
    return send_grafana_post('{0}/api/admin/users'.format(grafana_url), payload, http_post_headers,
                             verify_ssl, client_cert, debug)


def add_user_to_org(org_id, payload, grafana_url, http_post_headers, verify_ssl, client_cert,
                    debug):
    return send_grafana_post('{0}/api/orgs/{1}/users'.format(grafana_url, org_id), payload,
                             http_post_headers, verify_ssl, client_cert, debug)


def send_grafana_get(url, http_get_headers, verify_ssl, client_cert, debug):
    r = requests.get(url, headers=http_get_headers, verify=verify_ssl, cert=client_cert)
    if debug:
        log_response(r)

    return r.status_code, r.json(), url


def send_grafana_post(url, json_payload, http_post_headers, verify_ssl=False, client_cert=None,
                      debug=True):
    r = requests.post(url, headers=http_post_headers, data=json_payload, verify=verify_ssl,
                      cert=client_cert)
    if debug:
        log_response(r)

    return r.status_code, r.json(), url
