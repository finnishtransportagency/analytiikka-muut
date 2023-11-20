from aws_cdk import (
    aws_lambda,
    aws_lambda_python_alpha,
    aws_events,
    aws_events_targets,
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

PYTHON OK

"""





"""
Lambda parametrit
"""
class LambdaProperties:
    def __init__(self, vpc = None, securitygroups = None, timeout: int = None, memory: int = None, environment: dict = None, tags: dict = None, schedule: str = None):
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
        self.schedule = schedule



"""
Lisää tagit
"""
def add_tags(function, tags):
    if tags:
        for _t in tags:
            for k, v in _t.items():
                Tags.of(function).add(k, v, apply_to_launched_instances = True, priority = 300)


"""
Lisää ajastus
"""
def add_schedule(self, function, schedule):
    if schedule != None and schedule != "":
        rule_name = f"{function.function_name}-schedule"
        rule = aws_events.Rule(self,
                               rule_name,
                               rule_name = rule_name,
                               schedule = aws_events.Schedule.expression(f"cron({schedule})")
        )
        rule.add_target(aws_events_targets.LambdaFunction(function))





"""
Python lambda

Jos tarvitaan layer: https://github.com/aws-samples/aws-cdk-examples/blob/master/python/lambda-layer/app.py


"""
class PythonLambdaFunction(Construct):

    def __init__(self,
                 scope: Construct, 
                 id: str, 
                 path: str,
                 index: str,
                 handler: str,
                 description: str,
                 role: aws_iam.Role,
                 props: LambdaProperties
                 ):
        super().__init__(scope, id)
        
        self.function = aws_lambda_python_alpha.PythonFunction(
            self, 
            id,
            function_name = id,
            description = description,
            runtime = aws_lambda.Runtime.PYTHON_3_11,
            entry = path,
            index = index,
            handler = handler,
            role = role,
            vpc = props.vpc,
            security_groups = props.securitygroups,
            timeout = props.timeout,
            memory_size = props.memory,
            environment = props.environment,
            log_retention = aws_logs.RetentionDays.THREE_MONTHS
            )

        add_tags(self.function, props.tags)
        add_schedule(self, self.function, props.schedule)

        # if props.schedule != None and props.schedule != "":
        #     rule = aws_events.Rule(self,
        #                            f"{id}-schedule",
        #                            schedule = aws_events.Schedule.expression(f"cron({props.schedule})")
        #     )
        #     rule.add_target(aws_events_targets.LambdaFunction(self.function))




"""
Java lambda

"""
class JavaLambdaFunction(Construct):

    def __init__(self,
                 scope: Construct, 
                 id: str, 
                 description: str,
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
                                            function_name = id,
                                            description = description,
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
        add_schedule(self, self.function, props.schedule)



"""
Node.js lambda
"""
class NodejsLambdaFunction(Construct):

    def __init__(self,
                 scope: Construct, 
                 id: str, 
                 path: str,
                 handler: str,
                 description: str,
                 role: aws_iam.Role,
                 props: LambdaProperties
                 ):
        super().__init__(scope, id)

        self.function = aws_lambda.Function(self,
                                            id,
                                            function_name = id,
                                            description = description,
                                            code = aws_lambda.AssetCode(path = path),
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
        add_schedule(self, self.function, props.schedule)



        

