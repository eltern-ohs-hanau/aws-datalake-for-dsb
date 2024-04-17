from aws_cdk import (
    Duration,
    Stack,
    aws_events,
    aws_events_targets,
    aws_iam,
    aws_lambda,
    aws_lambda_python_alpha as aws_lambda_python,
    aws_logs,
    aws_s3,
)

from constructs import Construct


class DsbSyncStack(Stack):

    def __init__(self, 
                 scope: Construct,
                 construct_id: str,
                 dsb_username: str,
                 dsb_password: str,
                 default_s3_bucket_prefix: str,
                 default_s3_download_prefix: str,
                 **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here

        self._bucketname = default_s3_bucket_prefix + self.account

        # Create an S3 bucket
        self._bucket = aws_s3.Bucket(
            scope=self,
            id='Bucket',
            bucket_name=self._bucketname
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
                S3_BUCKET_NAME=self._bucketname,
                S3_DOWNLOAD_PREFIX=default_s3_download_prefix,
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
