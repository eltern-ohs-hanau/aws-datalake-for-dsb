import pytest
import aws_cdk as core
import aws_cdk.assertions as assertions

from aws_datalake_for_dsb.dsb_sync_stack import DsbSyncStack


# See here more for testing exmples https://docs.aws.amazon.com/cdk/v2/guide/testing.html
# Assertions reference https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.assertions/Template.html

@pytest.fixture
def stack_template():
    """Returns a template of Dsb Sync Stack with S3 bucket and Lambdas"""

    app = core.App()
    stack = DsbSyncStack(app, "aws-datalake-for-dsb-sync", "testuser", "", "testprefix", "testpath")
    template = assertions.Template.from_stack(stack)
    return template


@pytest.mark.usefixtures("stack_template")
class TestDsbSyncStack:
    def test_s3_bucket_created(self, stack_template):
        stack_template.has_resource("AWS::S3::Bucket", {
            "DeletionPolicy": "Retain"
        })

    def test_sync_lambda_created(self, stack_template):
        stack_template.has_resource_properties("AWS::Lambda::Function", {
            "Runtime": "python3.9"
        })
