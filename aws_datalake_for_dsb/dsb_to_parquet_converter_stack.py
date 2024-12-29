from aws_cdk import (
    Duration,
    Stack,
    aws_iam,
    aws_lambda,
    aws_lambda_event_sources,
    aws_lambda_python_alpha as aws_lambda_python,
    aws_logs,
    aws_s3,
    aws_sns
    aws_sqs,
)
from constructs import Construct
from aws_solutions_constructs.aws_sns_sqs import SnsToSqs

class DsbToParquetConverterStack(Stack):

    def __init__(self, 
                 scope: Construct,
                 construct_id: str,
                 sns_download_topic: aws_sns.Topic,
                 s3_bucket: aws_s3.Bucket,
                 s3_parquet_prefix: str,
                 **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here

        self._sns_to_sqs = SnsToSqs(
            scope=self,
            id="SnsToSQS",
            existing_topic_obj=sns_download_topic,
            enable_encryption_with_customer_managed_key=False
        )

        # Sync lambda function
        self._function = aws_lambda_python.PythonFunction(
            scope=self,
            id='Lambda',
            entry='./aws_datalake_for_dsb/assets/dsb_converter_lambda',  # Path to function code
            description='Convert files on S3 from DSB html to parquet',
            environment=dict(
                S3_BUCKET_NAME=s3_bucket.bucket_name,
                S3_PARQUET_PREFIX=s3_parquet_prefix
                POWERTOOLS_SERVICE_NAME=construct_id,
                POWERTOOLS_LOG_LEVEL='INFO',
            ),
            handler='lambda_handler',
            index='handler.py',
            log_retention=aws_logs.RetentionDays.ONE_WEEK,
            max_event_age=Duration.hours(1),
            retry_attempts=2,
            runtime=aws_lambda.Runtime.PYTHON_3_9,
            timeout=Duration.seconds(900),
            tracing=aws_lambda.Tracing.DISABLED,
        )

        self._bucket.grant_read_write(self._function.grant_principal)
        self._function.add_event_source(aws_lambda_event_sources.SqsEventSource(self._sns_to_sqs.sqs_queue))