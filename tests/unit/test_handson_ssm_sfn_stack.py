import aws_cdk as core
import aws_cdk.assertions as assertions

from handson_ssm_sfn.handson_ssm_sfn_stack import HandsonSsmSfnStack

# example tests. To run these tests, uncomment this file along with the example
# resource in handson_ssm_sfn/handson_ssm_sfn_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = HandsonSsmSfnStack(app, "handson-ssm-sfn")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
