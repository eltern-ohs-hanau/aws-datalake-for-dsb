#!/usr/bin/env python3
import os
from aws_cdk import App, Environment, Tags
from aws_datalake_for_dsb.dsb_sync_stack import DsbSyncStack

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

DsbSyncStack(
    app,
    "aws-datalake-for-dsb-sync",
    dsb_username=dsb_username,
    dsb_password=dsb_password,
    default_s3_bucket_prefix=default_s3_bucket_prefix,
    default_s3_download_prefix=default_s3_download_prefix,
    env=env
)

app.synth()
