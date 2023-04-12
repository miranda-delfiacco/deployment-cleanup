import logging
import sys
import argparse
from datetime import datetime, timedelta
import boto3


def main(days: int, bucket: str, debug: bool):
    """Main

    Args:
        days (int): Minimum number of days old a deployment folder must be to delete
        bucket (str): S3 Bucket name
        debug (bool): Enable debug mode
    """
    # Configure logging to stdout
    log_format = "%(levelname)s %(asctime)s - %(message)s"
    logging.basicConfig(stream=sys.stdout, format=log_format, level=logging.INFO)
    logger = logging.getLogger('logger')

    # Convert number of days given to a date
    timestamp = get_timstamp(days)

    # Get a list of expired objects in an S3 bucket
    expired_objects = get_expired_objects(timestamp, bucket)

    # Get a list of expired unique top-level keys / folders
    expired_folders = get_parent_folders(expired_objects)

    if debug:
        logger.info("Debug Mode: Listing expired folders in S3 bucket: %s", bucket)
        logger.info(expired_folders)
    else:
        logger.info("Deleting expired folders in S3 bucket: %s", bucket)
        delete_folders(expired_folders, bucket, logger)


def delete_folders(folders: list, bucket: str, log: logging.Logger):
    """Delete top-level folders in an S3 bucket

    Args:
        folders (list): List of top-level folders to delete
    """
    s3_client = boto3.resource('s3')
    s3_bucket = s3_client.Bucket(bucket)

    for item in folders:
        log.info("Deleting folder %s", item)
        s3_bucket.objects.filter(Prefix=item).delete()


def get_parent_folders(expired_objects: list):
    """Return top-level unique folders / keys

    Args:
        expired_objects (list): S3 objects
    """
    folders = set()

    for key in expired_objects:
        folders.add(key.split('/')[0])

    return folders


def get_expired_objects(timestamp: str, bucket: str):
    """Return a list of S3 objects older than timestamp provided

    Args:
        ts (str): Timestamp
        bucket (str): S3 bucket name
    """
    s3_client = boto3.client('s3')
    response = s3_client.get_paginator(
        'list_objects_v2').paginate(Bucket=bucket)
    expired_objects = response.search(
        "Contents[?to_string(LastModified)<='\""+timestamp+"\"'].Key")

    return expired_objects


def get_timstamp(days):
    """Return the date equal to today minus 'days'

    Args:
        days (int): number of days
    """
    timestamp = datetime.today() - timedelta(days=days)

    return str(timestamp.date())


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Script to cleanup old deployments in an S3 bucket")
    parser.add_argument("-d", "--days", type=int,
        help='Minimum number of days old a deployment folder must be to delete', required=True)
    parser.add_argument("-b", "--bucket", type=str,
        help='S3 Bucket name', required=True)
    parser.add_argument("-x", "--debug", action='store_true',
        help='Enable debug mode: log a list of expired folders without deleting anything',
        required=False, default=False)

    args = parser.parse_args()
    main(
        days=args.days,
        bucket=args.bucket,
        debug=args.debug
    )
