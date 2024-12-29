from aws_cdk import (
    Duration,
    Stack,
    CfnParameter,
    aws_events,
    aws_events_targets,
    aws_iam,
    aws_lambda,
    aws_lambda_python_alpha as aws_lambda_python,
    aws_logs,
    aws_s3,
    aws_sns
)
from constructs import Construct
from aws_solutions_constructs.aws_s3_sns import S3ToSns


class DsbSyncStack(Stack):

    @property
    def bucket(self):
        return self._bucket

    @property
    def topic(self):
        return self._download_topic

    def __init__(self, 
                 scope: Construct,
                 construct_id: str,
                 dsb_username: str,
                 dsb_password: str,
                 s3_bucket_prefix: str,
                 s3_download_prefix: str,
                 sns_download_topicname: str,
                 **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The parameters defined for your stack

        self._s3_bucketname = CfnParameter(
            self,
            id="bucketname",
            type="String",
            description="The name of the S3 bucket to save downloaded DSB data",
            default=s3_bucket_prefix + self.account
        ).value_as_string

        self._s3_download_prefix = CfnParameter(
            self,
            id="download_bucketprefix",
            type="String",
            description="The prefix to use for downloaded DSB data on S3 bucket",
            default=s3_download_prefix
        ).value_as_string

        self._download_topicname = CfnParameter(
            self,
            id="download_topicname",
            type="String",
            description="The name of the SNS topic to publish notification on downloaded DSB data",
            default=sns_download_topicname
        ).value_as_string

        # The code that defines your stack goes here

        # Create an S3 bucket
        self._bucket = aws_s3.Bucket(
            scope=self,
            id='Bucket',
            bucket_name=self._s3_bucketname
        )

        self._download_topic = aws_sns.Topic(
            scope=self,
            id='SNS',
            topic_name=self._download_topicname
        )

        # Sync lambda function
        self._function = aws_lambda_python.PythonFunction(
            scope=self,
            id='Lambda',
            entry='./aws_datalake_for_dsb/assets/dsb_sync_lambda',  # Path to function code
            description='Download files from DSB to S3',
            environment=dict(
                DSB_USERNAME=dsb_username,
                DSB_PASSWORD=dsb_password,
                S3_BUCKET_NAME=self._s3_bucketname,
                S3_DOWNLOAD_PREFIX=self._s3_download_prefix,
                SNS_NOTIFICATION_TOPIC_ARN=self._download_topic.topic_arn,
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
        self._download_topic.grant_publish(self._function.grant_principal)

        self._rule = aws_events.Rule(
            scope=self,
            id="LambdaCron",
            description="CloudWatch event trigger for the Sync Lambda",
            enabled=True,
            schedule=aws_events.Schedule.cron(
                minute='0',
                hour='0,5,18',  # Hours are given in UTC time zone
                week_day='MON-FRI',
                month='*',
                year='*'),
        )

        self._rule.add_target(aws_events_targets.LambdaFunction(self._function))  # type: ignore

        self._bucket_topic = S3ToSns(
            scope=self,
            id="BucketToSNS",
            existing_bucket_obj=self._bucket,
            enable_encryption_with_customer_managed_key=False
        )
