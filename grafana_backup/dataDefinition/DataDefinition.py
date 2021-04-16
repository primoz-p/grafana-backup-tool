import abc
import os
from abc import ABC

from grafana_backup.commons import save_json


class DataDefinition(ABC):
    def __init__(self, settings, name):
        self.name = name

        self.backup_dir = settings.get('BACKUP_DIR')
        self.timestamp = settings.get('TIMESTAMP')
        self.limit = settings.get('SEARCH_API_LIMIT')
        self.grafana_url = settings.get('GRAFANA_URL')
        self.http_get_headers = settings.get('HTTP_GET_HEADERS')
        self.verify_ssl = settings.get('VERIFY_SSL')
        self.client_cert = settings.get('CLIENT_CERT')
        self.debug = settings.get('DEBUG')
        self.pretty_print = settings.get('PRETTY_PRINT')
        self.uid_support = settings.get('UID_SUPPORT')

        self.folder_path = '{0}/{1}/{2}s'.format(self.backup_dir, self.timestamp,
                                                 self.name.replace(' ', '_'))
        self.log_path = '{0}/{1}/{2}s.txt'.format(self.backup_dir, self.timestamp,
                                                  self.name.replace(' ', '_'))

    def save(self):
        if not os.path.exists(self.folder_path):
            os.makedirs(self.folder_path)

        page = 1
        data = self.search_data(page)
        if data:
            with open(u"{0}".format(self.log_path), 'w') as f:
                for element in data:
                    self.save_element(element, f)

    def search_data(self, page):
        print("Searching {0}s ...".format(self.name.lower()))

        (status, content, api_url) = self.search_data_execute(page, self.limit, self.grafana_url,                                                     self.http_get_headers,                                                     self.verify_ssl, self.client_cert, self.debug)
        if status == 200:
            print("    {0}s found: {1}".format(self.name.title(), len(content)))
            return content
        else:
            print("    Error searching {0}s:"
                  "\n        status: {1}"
                  "\n        message: {2}".format(self.name.lower(), status, content))
            return []

    def save_element(self, element, log_file):

        (status, content, api_url) = self.load_element(element, self.grafana_url,
                                                       self.http_get_headers, self.verify_ssl,
                                                       self.client_cert, self.debug,
                                                       self.uid_support)
        if status == 200:
            file_name = self.get_element_filename(element)

            file_path = save_json(file_name, content, self.folder_path, self.name.lower(),
                                  self.pretty_print)

            log = "{0}: '{1}'".format(self.name.title(),
                                     self.get_element_main_description(element))
            for element_name in ['uid', 'id', 'name', 'title']:
                if element_name in element:
                    log += "\n    {0}: {1}".format(element_name, element[element_name])
            if 'url' in element and element['url']:
                url = element['url']
                if not url.startswith('http') and not url.startswith('172'):
                    url = "{0}{1}".format(self.grafana_url, url)
                log += "\n    URL: {0}".format(url)
            log += "\n    API: {0}".format(api_url)

            log += "\n    saved to: {0}".format(file_path)

            print(log)
            log_file.write(log + '\n')

    @abc.abstractmethod
    def search_data_execute(self, page, limit, grafana_url, http_get_headers, verify_ssl,
                            client_cert, debug):
        raise NotImplementedError

    @abc.abstractmethod
    def load_element(self, element, grafana_url, http_get_headers, verify_ssl, client_cert, debug,
                     uid_support):
        pass

    @staticmethod
    def get_element_main_description(element):
        for element_name in ['name', 'title']:
            if element_name in element:
                return element[element_name]

    def get_element_filename(self, element):
        if 'uid' in element:
            file_name = str(element['uid'])
        elif 'id' in element:
            file_name = str(element['id'])
        if 'uri' in element:
            file_name += "_" + element['uri'].replace('db/', '')

        return file_name
