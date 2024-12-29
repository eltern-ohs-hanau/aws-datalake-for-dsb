#!/usr/bin/env python3
import os
from aws_cdk import App, Environment, Tags
from aws_datalake_for_dsb.dsb_sync_stack import DsbSyncStack
from aws_datalake_for_dsb.dsb_to_parquet_converter_stack import DsbToParquetConverterStack

# For more information, see https://docs.aws.amazon.com/cdk/latest/guide/environments.html
env = Environment(
    account=os.getenv('CDK_DEFAULT_ACCOUNT'),
    region=os.getenv('CDK_DEFAULT_REGION')
)

tags = {
    'Project': 'aws-datalake-for-dsb'
}

app = App()
for key in tags:
    Tags.of(app).add(key, tags[key])

dsb_username = app.node.get_context("dsb:username")
dsb_password = app.node.get_context("dsb:password")
default_s3_bucket_prefix = app.node.try_get_context("default-s3-bucket-prefix")
default_s3_download_prefix = app.node.try_get_context("default-s3-download-prefix")
default-s3-parquet-prefix = app.node.try_get_context("default-s3-parquet-prefix")
default_sns_download_topic = app.node.try_get_context("default-sns-download-topic")

# TODO return props
DsbSyncStack(
    app,
    "aws-datalake-for-dsb-sync",
    dsb_username=dsb_username,
    dsb_password=dsb_password,
    s3_bucket_prefix=default_s3_bucket_prefix,
    s3_download_prefix=default_s3_download_prefix,
    sns_download_topic=default_sns_download_topic,
    env=env
)


DsbToParquetConverterStack(
    app,
    "aws-datalake-for-dsb-parquet-converter",
    sns_download_topic=default_sns_download_topic,
    s3_download_bucket=default_s3_bucket_prefix,
    s3_parquet_prefix=default_s3_parquet_prefix,
    env=env
)

app.synth()
