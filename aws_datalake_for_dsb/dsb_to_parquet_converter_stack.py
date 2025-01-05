from aws_cdk import (
    Duration,
    Stack,
    CfnParameter,
    aws_iam,
    aws_lambda,
    aws_lambda_event_sources,
    aws_lambda_python_alpha as aws_lambda_python,
    aws_logs,
    aws_s3,
    aws_sns,
    aws_sns_subscriptions,
    aws_sqs,
)
from constructs import Construct


class DsbToParquetConverterStack(Stack):

    def __init__(self, 
                 scope: Construct,
                 construct_id: str,
                 sns_download_topic: aws_sns.Topic,
                 s3_download_bucket: aws_s3.Bucket,
                 s3_parquet_prefix: str,
                 **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        LAMBDA_TIMEOUT = 900

        # The parameters defined for your stack

        self._s3_parquet_prefix = CfnParameter(
            self,
            id="parquet_bucketprefix",
            type="String",
            description="The prefix to use for parsed DSB data on S3 bucket",
            default=s3_parquet_prefix
        ).value_as_string

        # The code that defines your stack goes here

        self._dead_letter_queue = aws_sqs.Queue(
            self,
            id="DLQ",
            retention_period=Duration.days(7)
        )
        self._download_queue = aws_sqs.Queue(
            self,
            id="SQS",
            dead_letter_queue=aws_sqs.DeadLetterQueue(max_receive_count=1, queue=self._dead_letter_queue),
            visibility_timeout = Duration.seconds(LAMBDA_TIMEOUT * 6)
        )

        sqs_subscription = aws_sns_subscriptions.SqsSubscription(
            self._download_queue,
            raw_message_delivery=True
        )
        sns_download_topic.add_subscription(sqs_subscription)


        # Sync lambda function
        self._function = aws_lambda_python.PythonFunction(
            scope=self,
            id='Lambda',
            entry='./aws_datalake_for_dsb/assets/dsb_to_parquet_converter_lambda/src',  # Path to function code
            description='Convert files on S3 from DSB html to parquet',
            environment=dict(
                S3_BUCKET_NAME=s3_download_bucket.bucket_name,
                S3_PARQUET_PREFIX=self._s3_parquet_prefix,
                POWERTOOLS_SERVICE_NAME=construct_id,
                POWERTOOLS_LOG_LEVEL='INFO',
            ),
            handler='lambda_handler',
            index='handler.py',
            events=[aws_lambda_event_sources.SqsEventSource(self._download_queue)],
            dead_letter_queue_enabled=True,
            dead_letter_queue=self._dead_letter_queue,
            log_retention=aws_logs.RetentionDays.ONE_WEEK,
            max_event_age=Duration.hours(1),
            retry_attempts=2,
            runtime=aws_lambda.Runtime.PYTHON_3_9,
            timeout=Duration.seconds(LAMBDA_TIMEOUT),
            tracing=aws_lambda.Tracing.DISABLED,
        )

        s3_download_bucket.grant_read_write(self._function.grant_principal)