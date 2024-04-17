# -*- coding: utf-8 -*-

import os
import boto3
import requests
from pydsb import PyDSB
from datetime import datetime
from io import BytesIO
from aws_lambda_powertools import Logger

LOGGER = Logger()
DSB_USERNAME = os.environ['DSB_USERNAME']
DSB_PASSWORD = os.environ['DSB_PASSWORD']
S3_BUCKET_NAME = os.environ['S3_BUCKET_NAME']
S3_DOWNLOAD_PREFIX = os.environ['S3_DOWNLOAD_PREFIX']


def lambda_handler(event, context):
    now = datetime.now()
    s3_client = boto3.client('s3')
    dsb = PyDSB(DSB_USERNAME, DSB_PASSWORD)
    plans = dsb.get_plans()
    LOGGER.info("Fetching {} plans for".format(len(plans)))

    for item in plans:
        response = requests.get(item["url"], params={"authid": dsb.token})
        response.raise_for_status()

        #convert content to bytes, since upload_fileobj requires file like obj
        bytesIO = BytesIO(bytes(response.content))
        key = os.path.join(
            S3_DOWNLOAD_PREFIX,
            now.strftime("%Y%m%d-%H%M%S_plans"),
            "{}.html".format(item["id"]))
        with bytesIO as data:
            s3_client.upload_fileobj(data, S3_BUCKET_NAME, key)

    return 'success'
