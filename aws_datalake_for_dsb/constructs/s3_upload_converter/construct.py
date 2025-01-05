from aws_cdk import (
    Stack,
    aws_lambda,
    aws_sns,
    aws_iam
)
from constructs import Construct
from constructs import Construct
from aws_solutions_constructs.aws_sns_sqs import SnsToSqs
from aws_solutions_constructs.aws_sqs_lambda import SqsToLambda

class S3UploadConverter(Construct):

    @property
    def function(self):
        return self._function

    def __init__(self, scope: Construct, id: str, topic: aws_sns.Topic) -> None:
        super().__init__(scope, id)

        self._stack = SnsToSqs(
            scope=self,
            id='BucketUploadQueue',
            existing_topic_obj=topic
        )

        self._policy_statement = aws_iam.PolicyStatement(
            actions=["kms:Encrypt", "kms:Decrypt"],
            effect=aws_iam.Effect.ALLOW,
            principals=[aws_iam.AccountRootPrincipal()],
            resources=["*"]
        )

        self._stack.encryption_key.add_to_resource_policy(self._policy_statement)