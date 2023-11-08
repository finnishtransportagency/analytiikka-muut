from aws_cdk import (
    aws_lambda,
    aws_logs,
    Duration
)


from constructs import Construct



lambda_properties = {
    "vpc": None,
    "subnets": None,
    "securitygroups": None,
    "timeout": None,
    "memory": None,
    "environment": None
}





def PythonLambdaFunction(scope: Construct,
                         id: str,
                         path: str,
                         handler: str,
                         props: dict
                         ):

    vpc = None
    subnets = None
    securitygroups = None
    timeout = None
    memory = None
    environment = None

    if "vpc" in props:
        vpc = props["vpc"]
    if "subnets" in props:
        subnets = props["subnets"]
    if "securitygroups" in props:
        securitygroups = props["securitygroups"]
    if "timeout" in props:
        timeout = Duration.minutes(props["timeout"])
    if "memory" in props:
        memory = props["memory"]
    if "environment" in props:
        environment = props["environment"]

    func_code = aws_lambda.Code.from_asset(path= path,
                                           bundling={
                    "command": [
                        "bash",
                        "-c",
                        "npm install -g aws-cdk && pip install -r requirements.txt -t /asset-output && cp -au . /asset-output",
                    ],
                    "image": aws_lambda.Runtime.PYTHON_3_11.bundling_image
                }
    )

    func = aws_lambda.Function(scope,
                               id,
                               code = func_code,
                               vpc = vpc,
                               vpc_subnets = subnets,
                               security_groups = securitygroups,
                               log_retention = aws_logs.RetentionDays.THREE_MONTHS,
                               handler = handler,
                               runtime = aws_lambda.Runtime.PYTHON_3_11,
                               timeout = timeout,
                               memory_size = memory,
                               environment = environment
                               )
    return func
       


        


