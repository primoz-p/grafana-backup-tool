from grafana_backup.api_checks import main as api_checks
from grafana_backup.dataDefinition.AlertChannelsDataDefinition import AlertChannelsDataDefinition
from grafana_backup.dataDefinition.DashboardsDataDefinition import DashboardDataDefinition
from grafana_backup.dataDefinition.DataSourcesDataDefinition import DataSourcesDataDefinition
from grafana_backup.dataDefinition.FoldersDataDefinition import FoldersDataDefinition
from grafana_backup.dataDefinition.OrganizationsDataDefinition import OrganizationsDataDefinition
from grafana_backup.dataDefinition.UsersDataDefinition import UsersDataDefinition
from grafana_backup.save_dashboards import main as save_dashboards
from grafana_backup.save_datasources import main as save_datasources
from grafana_backup.save_folders import main as save_folders
from grafana_backup.save_alert_channels import main as save_alert_channels
from grafana_backup.archive import main as archive
from grafana_backup.s3_upload import main as s3_upload
from grafana_backup.save_orgs import main as save_orgs
from grafana_backup.save_users import main as save_users
from grafana_backup.azure_storage_upload import main as azure_storage_upload
from grafana_backup.gcs_upload import main as gcs_upload
import sys


def main(args, settings):
    arg_components = args.get('--components', False)
    arg_no_archive = args.get('--no-archive', False)

    backup_functions = {'dashboards': DashboardDataDefinition(settings),
                        'datasources': DataSourcesDataDefinition(settings),
                        'folders': FoldersDataDefinition(settings),
                        'alert-channels': AlertChannelsDataDefinition(settings),
                        'organizations': OrganizationsDataDefinition(settings),
                        'users': UsersDataDefinition(settings)}

    (status, json_resp, uid_support, paging_support) = api_checks(settings)

    # Do not continue if API is unavailable or token is not valid
    if not status == 200:
        print("server status is not ok: {0}".format(json_resp))
        sys.exit(1)

    settings.update({'UID_SUPPORT': uid_support})
    settings.update({'PAGING_SUPPORT': paging_support})

    if arg_components:
        arg_components_list = arg_components.split(',')

        # Backup only the components that provided via an argument
        for backup_function in arg_components_list:
            backup_functions[backup_function].save()
    else:
        # Backup every component
        for backup_function in backup_functions.keys():
            backup_functions[backup_function].save()

    aws_s3_bucket_name = settings.get('AWS_S3_BUCKET_NAME')
    azure_storage_container_name = settings.get('AZURE_STORAGE_CONTAINER_NAME')
    gcs_bucket_name = settings.get('GCS_BUCKET_NAME')

    if not arg_no_archive:
        archive(args, settings)
   
    if aws_s3_bucket_name:
        print('Upload archives to S3:')
        s3_upload(args, settings)

    if azure_storage_container_name:
        print('Upload archives to Azure Storage:')
        azure_storage_upload(args, settings)

    if gcs_bucket_name:
        print('Upload archives to GCS:')
        gcs_upload(args, settings)