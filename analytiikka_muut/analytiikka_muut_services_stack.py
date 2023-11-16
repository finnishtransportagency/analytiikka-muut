from aws_cdk import (
    Stack,
    aws_ec2,
    aws_s3,
    aws_iam,
    RemovalPolicy
)


from aws_cdk.aws_iam import ServicePrincipal

from constructs import Construct

from analytiikka_muut.helper_lambda import *

"""
Palvelut stack

"""
class AnalytiikkaMuutServicesStack(Stack):

    def __init__(self,
                 scope: Construct, 
                 construct_id: str,
                 environment: str,
                 **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        """
        Yhteiset arvot projektilta ja ympäristön mukaan
        """
        # projectname = self.node.try_get_context('project')
        properties = self.node.try_get_context(environment)
        target_bucket = properties["ade_staging_bucket_name"]
        lambda_role_name = self.node.try_get_context('lambda_role_name')
        # lambda_security_group_name = self.node.try_get_context('lambda_security_group_name')
        # glue_role_name = self.node.try_get_context('glue_role_name')
        # glue_security_group_name = self.node.try_get_context('glue_security_group_name')

        # print(f"services {environment}: project = '{projectname}'")
        print(f"services {environment}: account = '{self.account}'")
        print(f"services {environment}: region = '{self.region}'")
        # print(f"services {environment}: properties = '{properties}'")

        vpcname = properties["vpc_name"]
        vpc = aws_ec2.Vpc.from_lookup(self, "VPC", vpc_name=vpcname)
        

        # subnets = selection.subnets

        #lambda_securitygroup = aws_ec2.SecurityGroup.from_lookup_by_name(self, "LambdaSecurityGroup", security_group_name = lambda_security_group_name, vpc = vpc)
        #lambda_role = aws_iam.Role.from_role_arn(self, "LambdaRole", f"arn:aws:iam::{self.account}:role/{lambda_role_name}", mutable=False)

        #glue_securitygroup = aws_ec2.SecurityGroup.from_lookup_by_name(self, "GlueSecurityGroup", security_group_name = glue_security_group_name, vpc = vpc)
        #glue_role = aws_iam.Role.from_role_arn(self, "GlueRole", f"arn:aws:iam::{self.account}:role/{glue_role_name}", mutable=False)

        # print(f"services {environment}: vpc = '{vpc}'")
        # print(f"services {environment}: subnets = '{subnets}'")


        # Yhteinen rooli
        lambda_role = aws_iam.Role(self, id = lambda_role_name, role_name= lambda_role_name,
                                   assumed_by= ServicePrincipal("lambda.amazonaws.com"),
                                   managed_policies=[
                                       # logs & S3
                                       aws_iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaExecute"),
                                       # logs & vpc 
                                       aws_iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaVPCAccessExecutionRole")

                                   ]
        )
        
        #,
        #                            inline_policies=[
        #                                aws_iam.PolicyStatement(
        #                                    effect= aws_iam.Effect.ALLOW,
        #                                    actions = ['secretsmanager:GetSecretValue'],
        #                                    resources = ['arn:aws:secretsmanager:${self.region}:${self.account}:secret:*'],
        #                                ),
        #                                aws_iam.PolicyStatement(
        #                                    effect= aws_iam.Effect.ALLOW,
        #                                    actions = ['ssm:GetParameter'],
        #                                    resources = ['arn:aws:ssm:${self.region}:${self.account}:parameter/*'],
        #                                )
        #                            ]
        #                           )
        
        # lambda_role.add_to_policy(
        #     aws_iam.PolicyStatement(
        #         effect= aws_iam.Effect.ALLOW,
        #         actions = ['logs:CreateLogGroup', 'logs:CreateLogStream', 'logs:PutLogEvents'],
        #         resources = ['arn:aws:logs:*:*:*'],
        #     )
        # )
        # lambda_role.add_to_policy(
        #     aws_iam.PolicyStatement(
        #         effect= aws_iam.Effect.ALLOW,
        #         actions = ['secretsmanager:GetSecretValue'],
        #         resources = ['arn:aws:secretsmanager:${self.region}:${self.account}:secret:*'],
        #     )
        # )
        # # lambda_role.add_to_policy(
        #     aws_iam.PolicyStatement(
        #         effect= aws_iam.Effect.ALLOW,
        #         actions = ['ssm:GetParameter'],
        #         resources = ['arn:aws:ssm:${self.region}:${self.account}:parameter/*'],
        #     )
        # )



        #
        # HUOM: Lisää tarvittavat tämän jälkeen. Käytä yllä pääteltyjä asioita tarvittaessa
        #

        dummy = aws_s3.Bucket(self,
                              id = f"vayla-cdk-test-xxxx-{environment}",
                              bucket_name = f"vayla-cdk-test-xxxx-{environment}", 
                              auto_delete_objects = True,
                              removal_policy = RemovalPolicy.DESTROY)



        # Lambda: testi 1
        l1 = PythonLambdaFunction(self,
                             id = "testi1",
                             path = "lambda/testi1",
                             handler = "testi1.lambda_handler",
                             role = lambda_role,
                             props = LambdaProperties(vpc = vpc,
                                                      timeout = 2, 
                                                      environment = {
                                                          "target_bucket": target_bucket
                                                      },
                                                      tags = [
                                                          { "testitag": "jotain" },
                                                          { "toinen": "arvo" }
                                                      ]
                                                     )
                            )
# 
        # # Lambda: servicenow testi
        # l2 = JavaLambdaFunction(self,
        #                    id = "servicenow-sn_customerservice_case",
        #                    path = "lambda/servicenow",
        #                    jarname = "servicenow-to-s3-lambda-1.0.0.jar",
        #                    handler = "com.cgi.lambda.apifetch.LambdaFunctionHandler",
        #                    role = lambda_role,
        #                    props = LambdaProperties(timeout = 15,
        #                                             memory = 2048,
        #                                             environment={
        #                                                 "secret_name": "credentials-servicenow-api",
        #                                                 "query_string_default": "sn_customerservice_case?sysparm_query=sys_updated_onBETWEENjavascript%3Ags.daysAgoStart(3)%40javascript%3Ags.endOfYesterday()%5EORsys_created_onBETWEENjavascript%3Ags.daysAgoStart(3)%40javascript%3Ags.endOfYesterday()&sysparm_display_value=true",
        #                                                 "query_string_date": "sn_customerservice_case?sysparm_query=sys_created_onON{DATEFILTER}@javascript:gs.dateGenerate(%27{DATEFILTER}%27,%27start%27)@javascript:gs.dateGenerate(%27{DATEFILTER}%27,%27end%27)&sysparm_display_value=true",
        #                                                 "output_split_limit": "1500",
        #                                                 "api_limit": "600",
        #                                                 "output_bucket": "sn_customerservice_case",
        #                                                 "output_path": "cmdb_ci_service",
        #                                                 "output_filename": "servicenow_sn_customerservice_case",
        #                                                 "coordinate_transform": "true",
        #                                                 "fullscans":"",
        #                                                 "add_path_ym": "true"
        #                                             },
        #                                             tags = None
        #                                            )
        #                   )

