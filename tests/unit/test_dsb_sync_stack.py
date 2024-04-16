import aws_cdk as core
import aws_cdk.assertions as assertions

from aws_datalake_for_dsb.dsb_sync_stack import DsbSyncStack

# example tests. To run these tests, uncomment this file along with the example
# resource in aws_datalake_for_dsb/dsb_sync_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = DsbSyncStack(app, "aws-datalake-for-dsb-sync")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
