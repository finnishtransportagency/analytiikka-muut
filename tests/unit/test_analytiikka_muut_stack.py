import aws_cdk as core
import aws_cdk.assertions as assertions

from analytiikka_muut.analytiikka_muut_stack import AnalytiikkaMuutStack

# example tests. To run these tests, uncomment this file along with the example
# resource in analytiikka_muut/analytiikka_muut_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = AnalytiikkaMuutStack(app, "analytiikka-muut")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
