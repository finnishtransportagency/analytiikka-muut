from aws_cdk import (
    Stack,
    aws_ec2,
    aws_s3,
    aws_iam,
    aws_secretsmanager,
    RemovalPolicy
)


from aws_cdk.aws_iam import ServicePrincipal

from constructs import Construct

from analytiikka_muut.helper_lambda import *
from analytiikka_muut.helper_glue import *





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
        properties = self.node.try_get_context(environment)
        # #glue_script_bucket_name = properties["glue_script_bucket_name"]
        driver_bucket_name = properties["driver_bucket_name"]
        target_bucket_name = properties["ade_staging_bucket_name"]
        lambda_role_name = self.node.try_get_context('lambda_role_name')
        lambda_security_group_name = self.node.try_get_context('lambda_security_group_name')
        glue_role_name = self.node.try_get_context('glue_role_name')
        glue_security_group_name = self.node.try_get_context('glue_security_group_name')

        # print(f"services {environment}: project = '{projectname}'")
        # print(f"services {environment}: account = '{self.account}'")
        # print(f"services {environment}: region = '{self.region}'")
        # print(f"services {environment}: properties = '{properties}'")


        vpcname = properties["vpc_name"]
        vpc = aws_ec2.Vpc.from_lookup(self, "VPC", vpc_name=vpcname)
        # print(f"services {environment}: vpc = '{vpc}'")
        

        lambda_securitygroup = aws_ec2.SecurityGroup.from_lookup_by_name(self, "LambdaSecurityGroup", security_group_name = lambda_security_group_name, vpc = vpc)
        lambda_role = aws_iam.Role.from_role_arn(self, "LambdaRole", f"arn:aws:iam::{self.account}:role/{lambda_role_name}", mutable=False)


        glue_securitygroup = aws_ec2.SecurityGroup.from_lookup_by_name(self, "GlueSecurityGroup", security_group_name = glue_security_group_name, vpc = vpc)
        glue_role = aws_iam.Role.from_role_arn(self, "GlueRole", f"arn:aws:iam::{self.account}:role/{glue_role_name}", mutable=False)

        # glue_script_bucket = aws_s3.Bucket(self,
        #                                    id = glue_script_bucket_name,
        #                                    bucket_name = glue_script_bucket_name, 
        #                                    auto_delete_objects = True,
        #                                    removal_policy = RemovalPolicy.DESTROY)


        #
        # HUOM: Lisää tarvittavat tämän jälkeen. Käytä yllä pääteltyjä asioita tarvittaessa
        #

        dummy = aws_s3.Bucket(self,
                              id = f"vayla-cdk-test-xxxx-{environment}",
                              bucket_name = f"vayla-cdk-test-xxxx-{environment}", 
                              auto_delete_objects = True,
                              removal_policy = RemovalPolicy.DESTROY)


        # Lambda: testi 1
        # HUOM: schedule- määritys: https://docs.aws.amazon.com/lambda/latest/dg/services-cloudwatchevents-expressions.html

        l1 = PythonLambdaFunction(self,
                             id = "testi1",
                             path = "lambda/testi1",
                             index = "testi1.py",
                             handler = "testi1.lambda_handler",
                             description = "Testilambdan kuvaus",
                             role = lambda_role,
                             props = LambdaProperties(vpc = vpc,
                                                      timeout = 2, 
                                                      environment = {
                                                          "target_bucket": target_bucket_name,
                                                          "dummy_input_value": "10001101101"
                                                      },
                                                      tags = [
                                                          { "testitag": "jotain" },
                                                          { "toinen": "arvo" }
                                                      ],
                                                      securitygroups = [ lambda_securitygroup ],
                                                      schedule = "0 10 20 * ? *"
                                                     )
                            )


        # Lambda: servicenow testi
        l2 = JavaLambdaFunction(self,
                           id = "servicenow-sn_customerservice_case",
                           description = "ServiceNow haku taululle sn_customerservice_case",
                           path = "lambda/servicenow",
                           jarname = "servicenow-to-s3-lambda-1.0.0.jar",
                           handler = "com.cgi.lambda.apifetch.LambdaFunctionHandler",
                           role = lambda_role,
                           props = LambdaProperties(vpc = vpc,
                                                    timeout = 15,
                                                    memory = 2048,
                                                    environment={
                                                        "secret_name": "credentials-servicenow-api",
                                                        "query_string_default": "sn_customerservice_case?sysparm_query=sys_updated_onBETWEENjavascript%3Ags.daysAgoStart(3)%40javascript%3Ags.endOfYesterday()%5EORsys_created_onBETWEENjavascript%3Ags.daysAgoStart(3)%40javascript%3Ags.endOfYesterday()&sysparm_display_value=true",
                                                        "query_string_date": "sn_customerservice_case?sysparm_query=sys_created_onON{DATEFILTER}@javascript:gs.dateGenerate(%27{DATEFILTER}%27,%27start%27)@javascript:gs.dateGenerate(%27{DATEFILTER}%27,%27end%27)&sysparm_display_value=true",
                                                        "output_split_limit": "1500",
                                                        "api_limit": "600",
                                                        "output_bucket": target_bucket_name,
                                                        "output_path": "cmdb_ci_service",
                                                        "output_filename": "servicenow_sn_customerservice_case",
                                                        "coordinate_transform": "true",
                                                        "fullscans":"",
                                                        "add_path_ym": "true"
                                                    },
                                                    tags = None,
                                                    securitygroups = [ lambda_securitygroup ],
                                                    schedule = "0 10 1 * ? *"
                                                   )
                          )

        l2 = NodejsLambdaFunction(self,
                             id = "testi2",
                             path = "lambda/testi2",
                             handler = "testi2.lambda_handler",
                             description = "Testilambdan kuvaus",
                             role = lambda_role,
                             props = LambdaProperties(vpc = vpc,
                                                      timeout = 2, 
                                                      environment = {
                                                          "target_bucket": target_bucket_name,
                                                      },
                                                      tags = None,
                                                      securitygroups = [ lambda_securitygroup ],
                                                      schedule = "0 10 20 * ? *"
                                                     )
                            )



        s1_name = f"sampo-db-oracle-{environment}"
        s1 = aws_secretsmanager.Secret(self,
                                       id = s1_name,
                                       secret_name = s1_name,
                                       description = "Db-connection details for TalousDV Sampo Oracle views.",
                                       secret_object_value={
                                           "username": "dummy",
                                           "password": "dummy",
                                           "engine": "oracle",
                                           "host": "todo",
                                           "port": "1521",
                                           "dbname": "SAMPO"
                                           }
                                           )

        c1 = GlueJdbcConnection(self,
                                id = "testi3-connection",
                                vpc = vpc,
                                security_groups = [ glue_securitygroup ],
                                properties = {
                                    "JDBC_CONNECTION_URL": "jdbc:oracle:thin:@//172.17.193.200:1521/ORCL",
                                    "JDBC_DRIVER_CLASS_NAME": "oracle.jdbc.driver.OracleDriver",
                                    "JDBC_DRIVER_PATH": f"s3://{driver_bucket_name}/oracle-driver/ojdbc8.jar",
                                    "SECRET_ID": s1_name
                                })

        g1 = PythonSparkGlueJob(self,
                 id = "testi3", 
                 path = "glue/testi3/testi3.py",
                 timeout = 1,
                 description = "Glue jobin kuvaus",
                 worker = "G 1X",
                 version = None,
                 role = glue_role,
                 tags = None,
                 arguments = None,
                 connections = [ c1 ],
                 enable_spark_ui = False,
                 schedule = "0 12 24 * ? *",
                 schedule_description = "Normaali ajastus"
        )





