import sys
import time
import json
from os import environ
from typing import Any, Dict
from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.typing import LambdaContext
from common import aws_helper, html_helper

logger = Logger()

try:
    # Globally scoped variables and resources
    S3_BUCKET_NAME = environ['S3_BUCKET_NAME']
    S3_PARQUET_PREFIX = environ['S3_PARQUET_PREFIX']
except Exception as e:
    logger.error("ERROR: Unexpected error: Could not initialize globally scoped variables and resources")
    logger.error(e)
    sys.exit()

@logger.inject_lambda_context
def lambda_handler(event, context):

    #TODO