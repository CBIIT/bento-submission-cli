#!/usr/bin/env python3
import argparse
import os, sys
import glob
import datetime
from getpass import getpass
from utils import LIST_JOBS_ACTION, JOB_STATUS_ACTION, LOAD_ACTION, VALIDATE_ACTION, PSWD_ENV, get_logger

def parse_arguments():
    parser = argparse.ArgumentParser(description='Load data into ICDC')
    parser.add_argument('-u', '--user', help='ICDC username', required=True)
    parser.add_argument('-p', '--password', help='ICDC password')
    subparsers = parser.add_subparsers(dest='action', help='Action help', description='Actions', required=True)

    subparsers.add_parser(LIST_JOBS_ACTION, help='List jobs')

    status_parser = subparsers.add_parser(JOB_STATUS_ACTION, help='Query job status')
    status_parser.add_argument('job_id', help='Job id')

    validate_parser = subparsers.add_parser(VALIDATE_ACTION, help='Validate data')
    validate_parser.add_argument('-M', '--max-violations', help='Max violations to display', nargs='?', type=int, default=10)
    validate_parser.add_argument('dir', help='Data directory')

    load_parser = subparsers.add_parser(LOAD_ACTION, help='Load data')
    load_parser.add_argument('-M', '--max-violations', help='Max violations to display', nargs='?', type=int, default=10)
    load_parser.add_argument('dir', help='Data directory')

    return parser.parse_args()

def process_arguments(args, log):
    directory = args.dir if hasattr(args, 'dir') else None

    if directory and not os.path.isdir(directory):
        log.error('{} is not a directory!'.format(directory))
        sys.exit(1)

    password = args.password
    if not password:
        if PSWD_ENV not in os.environ:
            log.error(
                'Password not specified! Please specify password with -p or --password argument, or set {} env var'.format(
                    PSWD_ENV))
            password = getpass(prompt='Please enter your ICDC password:')
            if not password:
                log.error('Data pipeline can not work without a valid password!')
                sys.exit(1)
        else:
            password = os.environ[PSWD_ENV]
            if not password:
                log.error('Password in variable "{}" is empty!'.format(PSWD_ENV))
                sys.exit(1)
    user = args.user
    return (user, password, directory)


def main():
    log = get_logger('Data Pipeline')
    args = parse_arguments()
    user, password, directory = process_arguments(args, log)


    try:
        if args.action == LIST_JOBS_ACTION:
            print('Job id\tStatus')
            print('0001\tValidating')
            print('0002\tLoad succeeded')
            print('0003\tValidation failed')
        elif args.action == JOB_STATUS_ACTION:
            print('Job id\tStatus')
            print('{}\tValidating'.format(args.job_id))
        elif args.action in [LOAD_ACTION, VALIDATE_ACTION]:
            action = 'Loading' if args.action == LOAD_ACTION else "Validating"
            log.info('{} data from "{}"'.format(action, args.dir))
            file_list = glob.glob('{}/*.txt'.format(directory))

            if file_list:
                for file_name in file_list:
                    log.info('{} file: "{}"'.format(action, file_name))
            else:
                log.info('No files to load.')


    except Exception as err:
        log.exception(err)


if __name__ == '__main__':
    main()
