import sys
import time
import json
from os import environ
from typing import Any, Dict
import boto3
import pandas as pd
from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.utilities.batch import (
    BatchProcessor,
    EventType,
    process_partial_response,
)
from aws_lambda_powertools.utilities.data_classes.sqs_event import SQSRecord
from aws_lambda_powertools.utilities.typing import LambdaContext
from common import html_helper

processor = BatchProcessor(event_type=EventType.SQS)  
tracer = Tracer()
logger = Logger()

try:
    # Globally scoped variables and resources
    S3_BUCKET_NAME = environ['S3_BUCKET_NAME']
    S3_PARQUET_PREFIX = environ['S3_PARQUET_PREFIX']
except Exception as e:
    logger.error("ERROR: Unexpected error: Could not initialize globally scoped variables and resources")
    logger.error(e)
    sys.exit()


@tracer.capture_method
def record_handler(record: SQSRecord):
    # payload: str = record.json_body  # if json string data, otherwise record.body for str

    if record.body == "success" and record.message_attributes is not None:
        timestamp = message.message_attributes.get('timestamp').get('StringValue')
        s3_prefix = message.message_attributes.get('s3_prefix').get('StringValue')

        logger.debug("DEBUG: Get message for converting files in {}".format(s3_prefix))

        s3_client = boto3.client('s3')
        s3_objectnames = s3_client.list_objects(Bucket=S3_BUCKET_NAME, Prefix=f"{s3_prefix}/*")

        s3_client.download_file(S3_BUCKET_NAME, object_name, os.path.join("/tmp", objectname)) for objectname in s3_objectnames

        tmp_folder = os.path.join("/tmp", s3_prefix)
        results = [html_helper.parse_dsb_html_file(os.path.join(path, filename)) for filename in os.listdir(tmp_folder)]

        parquet_filename = "{}.gzip".format(os.path.basename(s3_prefix))
        parquet_fullpath = os.path.join(tmp_folder, parquet_filename)
        pd.concat(results, ignore_index=True, sort=False).to_parquet(parquet_fullpath, compression='gzip')

        s3_client.upload_file(parquet_fullpath, S3_BUCKET_NAME, f"{S3_PARQUET_PREFIX}/{parquet_filename}")
        os.remove(filename) for filename in os.listdir(tmp_folder)
        os.rmdir(tmp_folder)
        
        logger.info("SUCCESS: Upload parquet file to {}/{}".format(S3_PARQUET_PREFIX, parquet_filename))
    else:
        logger.error("ERROR: Unexpected error: Could not read message from SQS queue.")


@logger.inject_lambda_context
@tracer.capture_lambda_handler
def lambda_handler(event, context: LambdaContext):
    return process_partial_response(  
        event=event,
        record_handler=record_handler,
        processor=processor,
        context=context,
    )