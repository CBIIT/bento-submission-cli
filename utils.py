import logging
import os, sys
import uuid
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import re
from configparser import ConfigParser
import yaml
import subprocess
from urllib.parse import urlparse
from requests import post

def get_logger(name):
    formatter = logging.Formatter('%(asctime)s %(levelname)s: (%(name)s) - %(message)s')
    # formatter = logging.Formatter('[%(levelname)s] %(module)s - %(message)s')
    log_level = os.environ.get('DL_LOG_LEVEL', 'INFO')
    log = logging.getLogger(name)
    log.setLevel(log_level)
    std_handler = logging.StreamHandler()
    std_handler.setFormatter(formatter)
    log.addHandler(std_handler)
    return log

def get_uuid_for_node(node_type, signature):
    """Generate V5 UUID for a node
    Arguments:
        node_type - a string represents type of a node, e.g. case, study, file etc.
        signature - a string that can uniquely identify a node within it's type, e.g. case_id, clinical_study_designation etc.
                    or a long string with all properties and values concat together if no id available

    """
    log = get_logger('Utils')
    icdc_base_uuid = uuid.uuid5(uuid.NAMESPACE_URL, ICDC_DOMAIN)
    # log.debug('Base UUID: {}'.format(icdc_base_uuid))
    type_uuid = uuid.uuid5(icdc_base_uuid, node_type)
    # log.debug('Type UUID: {}'.format(type_uuid))
    node_uuid = uuid.uuid5(type_uuid, signature)
    log.debug('Node UUID: {}'.format(node_uuid))
    return str(node_uuid)


def removeTrailingSlash(uri):
    if uri.endswith('/'):
        return re.sub('/+$', '', uri)
    else:
        return uri

def is_parent_pointer(field_name):
    return re.fullmatch(r'\w+\.\w+', field_name) is not None

def get_host(uri):
    parts = urlparse(uri)
    return parts.hostname

def check_schema_files(schemas, log):
    if not schemas:
        log.error('Please specify schema file(s) with -s or --schema argument')
        return False

    for schema_file in schemas:
        if not os.path.isfile(schema_file):
            log.error('{} is not a file'.format(schema_file))
            return False
    return True


config = ConfigParser()
CONFIG_FILE_ENV_VAR = 'ICDC_DATA_LOADER_CONFIG'
config_file = os.environ.get(CONFIG_FILE_ENV_VAR, 'config.ini')
if config_file and os.path.isfile(config_file):
    config.read(config_file)
else:
    util_log = get_logger('Utils')
    util_log.error('Can\'t find configuration file! Make a copy of config.sample.ini to config.ini'
                   + ' or specify config file in Environment variable {}'.format(CONFIG_FILE_ENV_VAR))
    sys.exit(1)

PROP_FILE_ENV_VAR = 'ICDC_DATA_LOADER_PROP'
util_log = get_logger('Utils')

LOG_LEVEL = os.environ.get('DL_LOG_LEVEL', config.get('log', 'log_level'))
ICDC_DOMAIN = config.get('main', 'domain')
PSWD_ENV = 'ICDC_PASSWORD'
NODES_CREATED = 'nodes_created'
RELATIONSHIP_CREATED = 'relationship_created'
NODES_DELETED = 'nodes_deleted'
RELATIONSHIP_DELETED = 'relationship_deleted'
BLOCK_SIZE = 65536
TEMP_FOLDER = config.get('main', 'temp_folder')
DATE_FORMAT = '%Y-%m-%d'
DATETIME_FORMAT = '%Y%m%d-%H%M%S'
RELATIONSHIP_TYPE = 'relationship_type'
MULTIPLIER = 'Mul'
DEFAULT_MULTIPLIER = 'many_to_one'
ONE_TO_ONE = 'one_to_one'
UUID = 'uuid'
NEW_MODE = 'new'
UPSERT_MODE = 'upsert'
DELETE_MODE = 'delete'
LIST_JOBS_ACTION = 'ls'
JOB_STATUS_ACTION = 'status'
LOAD_ACTION = 'load'
VALIDATE_ACTION = 'validate'
