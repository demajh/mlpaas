import aws_cdk as core
import aws_cdk.assertions as assertions

from dbtfargate.dbtfargate_stack import DbtfargateStack

# example tests. To run these tests, uncomment this file along with the example
# resource in dbtfargate/dbtfargate_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = DbtfargateStack(app, "dbtfargate")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
