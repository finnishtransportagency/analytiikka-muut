from aws_cdk import (
    Stack,
    Tags,
    aws_ec2
)

from constructs import Construct

from analytiikka_muut.helper_lambda import *


class AnalytiikkaMuutServicesStack(Stack):

    def __init__(self,
                 scope: Construct, 
                 construct_id: str,
                 environment: str,
                 **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        projectname = self.node.try_get_context('project')
        properties = self.node.try_get_context(environment)
        vpcname = properties["vpc_name"]
        target_bucket = properties["ade_staging_bucket_name"]

        print(f"services {environment}: project = '{projectname}'")
        print(f"services {environment}: account = '{self.account}'")
        print(f"services {environment}: region = '{self.region}'")
        print(f"services {environment}: properties = '{properties}'")

        vpc = aws_ec2.Vpc.from_lookup(self, "VPC", vpc_name=vpcname)
        selection = vpc.select_subnets()
        subnets = selection.subnets

        print(f"services {environment}: vpc = '{vpc}'")
        print(f"services {environment}: subnets = '{subnets}'")


        l1 = PythonLambdaFunction(self,
                         "testi1",
                         "lambda/testi1",
                         "testi1.lambda_handler",
                         {
                             "vpc": None,
                             "subnets": None,
                             "timeout": 1,
                             "environment": {
                                 "target_bucket": target_bucket
                             }
                         }
                         )


#        l2 = helper_lambda.PythonLambdaFunction(scope,
#                         "testi2",
#                         "lambda/testi2",
#                         "testi2.lambda_handler",
#                         {}
#                         )

       


        


