from aws_cdk import (
    aws_lambda,
    aws_logs,
    Duration,
    BundlingOutput,
    aws_iam,
    aws_ec2,
    Tags
)

from constructs import Construct


"""
Apukoodit lambdojen luontiin

HUOM: triggerit puuttuu


"""





"""
Lambda parametrit
"""
class LambdaProperties:

    def __init__(self, vpc = None, securitygroups = None, timeout: int = None, memory: int = None, environment: dict = None, tags: dict = None):
        self.vpc = vpc
        self.subnets = None
        if vpc != None:
            selected = vpc.select_subnets()
            self.subnets = aws_ec2.SubnetSelection(subnets = selected.subnets)
        self.securitygroups = securitygroups
        self.timeout = Duration.minutes(timeout)
        self.memory = memory
        self.environment = environment
        self.tags = tags


def add_tags(function, tags):
    if tags:
        for _t in tags:
            for k, v in _t.items():
                print(f"k = '{k}', v = '{v}'")
                Tags.of(function).add(k, v, apply_to_launched_instances = True, priority = 300)



"""
Python lambda

"""
class PythonLambdaFunction(Construct):

    def __init__(self,
                 scope: Construct, 
                 id: str, 
                 path: str,
                 handler: str,
                 role: aws_iam.Role,
                 props: LambdaProperties
                 ):
        super().__init__(scope, id)

        func_code = aws_lambda.Code.from_asset(path = path,
                                               bundling = {
                                                   "command": [
                                                       "bash",
                                                       "-c",
                                                       "pip install --upgrade pip && pip install -r requirements.txt -t /asset-output && cp -au . /asset-output",
                                                    ],
                                                    "image": aws_lambda.Runtime.PYTHON_3_11.bundling_image,
                                                    "user": "root"
                                               }
                                              )

        self.function = aws_lambda.Function(self,
                                            id,
                                            code = func_code,
                                            vpc = props.vpc,
                                            vpc_subnets = props.subnets,
                                            security_groups = props.securitygroups,
                                            log_retention = aws_logs.RetentionDays.THREE_MONTHS,
                                            handler = handler,
                                            runtime = aws_lambda.Runtime.PYTHON_3_11,
                                            timeout = props.timeout,
                                            memory_size = props.memory,
                                            environment = props.environment,
                                            role = role
                                           )
        add_tags(self.function, props.tags)




"""
Java lambda

"""
class JavaLambdaFunction(Construct):

    def __init__(self,
                 scope: Construct, 
                 id: str, 
                 path: str,
                 jarname: str,
                 handler: str,
                 role: aws_iam.Role,
                 props: LambdaProperties
                 ):
        super().__init__(scope, id)

        func_code = aws_lambda.Code.from_asset(path = path,
                                               bundling = {
                                                   "command": [
                                                       "bash",
                                                       "-c",
                                                       f"mvn clean install && cp ./target/{jarname} /asset-output/",
                                                    ],
                                                    "image": aws_lambda.Runtime.JAVA_11.bundling_image,
                                                    "user": "root",
                                                    "output_type": BundlingOutput.ARCHIVED
                                               }
                                              )

        self.function = aws_lambda.Function(self,
                                            id,
                                            code = func_code,
                                            vpc = props.vpc,
                                            vpc_subnets = props.subnets,
                                            security_groups = props.securitygroups,
                                            log_retention = aws_logs.RetentionDays.THREE_MONTHS,
                                            handler = handler,
                                            runtime = aws_lambda.Runtime.JAVA_11,
                                            timeout = props.timeout,
                                            memory_size = props.memory,
                                            environment = props.environment,
                                            role = role
                                           )

        add_tags(self.function, props.tags)



"""
Node.js lambda
"""
class NodejsLambdaFunction(Construct):

    def __init__(self,
                 scope: Construct, 
                 id: str, 
                 path: str,
                 handler: str,
                 role: aws_iam.Role,
                 props: LambdaProperties
                 ):
        super().__init__(scope, id)

        func_code = aws_lambda.Code.from_asset(path = path,
                                               bundling = {
                                                   "command": [
                                                       "bash",
                                                       "-c",
                                                       "echo \"TODO: NODEJS INSTALL COMMAND\"",
                                                    ],
                                                    "image": aws_lambda.Runtime.NODEJS_18_X.bundling_image,
                                                    "user": "root"
                                               }
                                              )

        self.function = aws_lambda.Function(self,
                                            id,
                                            code = func_code,
                                            vpc = props.vpc,
                                            vpc_subnets = props.subnets,
                                            security_groups = props.securitygroups,
                                            log_retention = aws_logs.RetentionDays.THREE_MONTHS,
                                            handler = handler,
                                            runtime = aws_lambda.Runtime.NODEJS_18_X,
                                            timeout = props.timeout,
                                            memory_size = props.memory,
                                            environment = props.environment,
                                            role = role
                                           )

        add_tags(self.function, props.tags)




        

