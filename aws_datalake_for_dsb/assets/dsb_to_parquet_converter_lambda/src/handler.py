import json
import os
from sys import exit
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
    S3_BUCKET_NAME = os.environ['S3_BUCKET_NAME']
    S3_PARQUET_PREFIX = os.environ['S3_PARQUET_PREFIX']
except Exception as e:
    logger.error("ERROR: Unexpected error: Could not initialize globally scoped variables and resources")
    logger.error(e)
    exit()


@tracer.capture_method
def record_handler(record: SQSRecord):
    payload: dict = record.json_body  # if json string data, otherwise record.body for str

    result = payload.get('result')
    timestamp = payload.get('timestamp')
    s3_prefix = payload.get('s3_prefix')
    if result == "success" and s3_prefix:
        logger.debug("DEBUG: Get message for converting files in {}".format(s3_prefix))

        s3_client = boto3.client('s3')
        response = s3_client.list_objects_v2(Bucket=S3_BUCKET_NAME, Prefix=s3_prefix)

        if 'Contents' not in response:
            logger.warn("WARN: No downloaded files were found at prefix {}\nResponse={}".format(s3_prefix, response))
            response['Contents'] = []

        tmp_folder = os.path.join("/tmp", s3_prefix)
        os.makedirs(tmp_folder, exist_ok=True)
        for s3_object in response['Contents']:
            s3_client.download_file(S3_BUCKET_NAME, s3_object['Key'], os.path.join("/tmp", s3_object['Key']))

        results = [html_helper.parse_dsb_html_file(os.path.join(tmp_folder, filename)) for filename in os.listdir(tmp_folder)]

        parquet_filename = "{}.gzip".format(os.path.basename(s3_prefix))
        parquet_fullpath = os.path.join(tmp_folder, parquet_filename)
        html_helper.write_parqet_file(filename=parquet_fullpath, dataframes=results)

        s3_client.upload_file(parquet_fullpath, S3_BUCKET_NAME, f"{S3_PARQUET_PREFIX}/{parquet_filename}")
        for filename in os.listdir(tmp_folder):
            os.remove(os.path.join(tmp_folder, filename))
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