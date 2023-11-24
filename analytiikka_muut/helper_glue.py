from aws_cdk import (
    aws_iam,
    aws_ec2,
    aws_glue,
    aws_glue_alpha,
    Duration,
    Tags
)

import os

from constructs import Construct


"""
Apukoodit glue- ajojen luontiin
"""



"""
Lisää tagit
"""
def add_tags(job, tags):
    if tags:
        for _t in tags:
            for k, v in _t.items():
                Tags.of(job).add(k, v, apply_to_launched_instances = True, priority = 300)


"""
Worker type muunnos str -> WorkerType
"""
def get_worker_type(worker: str) -> aws_glue_alpha.WorkerType:
    value = aws_glue_alpha.WorkerType.G_1_X
    if worker == "G 2X":
        value = aws_glue_alpha.WorkerType.G_2_X
    elif worker == "G 4X":
        value = aws_glue_alpha.WorkerType.G_4_X
    elif worker == "G 8X":
        value = aws_glue_alpha.WorkerType.G_8_X
    elif worker == "G 025X":
        value = aws_glue_alpha.WorkerType.G_025_X
    elif worker == "Z 2X":
        value = aws_glue_alpha.WorkerType.Z_2_X
    return(value)

"""
Timeout numero -> Duration
"""
def get_timeout(timeout: int) -> Duration:
    value = Duration.minutes(1)
    if timeout != None and timeout > 0:
        value = Duration.minutes(timeout)
    return(value)


"""
Versio str -> GlueVersion
"""
def get_version(version: str) -> aws_glue_alpha.GlueVersion:
    value = aws_glue_alpha.GlueVersion.V4_0
    if version != "" and version != None:
        value = aws_glue_alpha.GlueVersion.of(version)
    return(value)


"""
Polku
"""
def get_path(path: str) -> os.path:
    return(os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), path))




"""

Properties:
https://docs.aws.amazon.com/glue/latest/dg/aws-glue-api-catalog-connections.html#aws-glue-api-catalog-connections-Connection

"""
class GlueJdbcConnection(Construct):
    """
    Glue connection
    """
    def __init__(self,
                 scope: Construct, 
                 id: str, 
                 vpc: any = None,
                 security_groups: list = None,
                 properties: dict = None
                 ):
        super().__init__(scope, id)

        selected = vpc.select_subnets()
        self.subnets = aws_ec2.SubnetSelection(subnets = selected.subnets)

        self.connection = aws_glue_alpha.Connection(self,
                                                    id = id,
                                                    connection_name = id,
                                                    type = aws_glue_alpha.ConnectionType.JDBC,
                                                    properties = properties,
                                                    security_groups = security_groups,
                                                    subnet = self.subnets.subnets[0]
                                                    )
        



"""

id: Ajon nimi
path: polku projektissa (= /glue/<jobname>)
timeout: aikaraja minuutteina, oletus = 1
description: Kuvaus
worker: G.1X, G.2X, G.4X, G.8X, G.025X, Z.2X, oletus = G.1X
version: glue versio, oletus = 4.0
role: Glue IAM roolin nimi
tags: Lisätagit
arguments: oletusparametrit
connections: connectit, lista
enable_spark_ui:  spark ui päälle/pois, oletus = pois
schedule: ajastus, cron expressio
schedule_description: ajastuksen kuvaus
"""
class PythonSparkGlueJob(Construct):

    def __init__(self,
                 scope: Construct, 
                 id: str, 
                 path: str,
                 timeout: any,
                 description: str = None,
                 worker: str = None,
                 version: str = None,
                 role: aws_iam.Role = None,
                 tags: dict = None,
                 arguments: dict = None,
                 connections: list = None,
                 enable_spark_ui: bool = False,
                 schedule: str = None,
                 schedule_description: str = None
                 ):
        super().__init__(scope, id)

        """
        https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_glue/CfnJob.html
        execution_property=glue.CfnJob.ExecutionPropertyProperty(max_concurrent_runs=123)
        """
        self.job = aws_glue_alpha.Job(self, 
                                           id = id,
                                           job_name = id,
                                           spark_ui = aws_glue_alpha.SparkUIProps(
                                               enabled = enable_spark_ui
                                           ),
                                           executable = aws_glue_alpha.JobExecutable.python_etl(
                                               glue_version = get_version(version),
                                               python_version = aws_glue_alpha.PythonVersion.THREE,
                                               script = aws_glue_alpha.Code.from_asset(get_path(path))
                                           ),
                                           description = description,
                                           default_arguments = arguments,
                                           role = role,
                                           worker_type = get_worker_type(worker),
                                           worker_count = 2,
                                           max_retries = 0,
                                           timeout = get_timeout(timeout),
                                           max_concurrent_runs = 2,
                                           connections = connections
                                           )

        add_tags(self.job, tags)

        if schedule != None and schedule != "":
            trigger_name = f"{id}-trigger"
            schedule = f"cron({schedule})"
            self.trigger = aws_glue.CfnTrigger(self,
                                        id = trigger_name,
                                        actions = [aws_glue.CfnTrigger.ActionProperty(
                                            arguments = arguments,
                                            job_name = id,
                                            timeout = timeout
                                            )
                                        ],
                                        type = "SCHEDULED",
                                        name = trigger_name,
                                        description = schedule_description,
                                        schedule = schedule,
                                        start_on_creation = False
                                       )
            add_tags(self.trigger, tags)







"""
TODO: EI TESTATTU
"""
class PythonShellGlueJob(Construct):

    def __init__(self,
                 scope: Construct, 
                 id: str, 
                 path: str,
                 timeout: any,
                 description: str = None,
                 worker: str = None,
                 version: str = None,
                 role: aws_iam.Role = None,
                 tags: dict = None,
                 arguments: dict = None,
                 schedule: str = None,
                 schedule_description: str = None
                 ):
        super().__init__(scope, id)

        """
        https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_glue/CfnJob.html
        execution_property=glue.CfnJob.ExecutionPropertyProperty(max_concurrent_runs=123)
        """
        self.job = aws_glue_alpha.Job(self, 
                                           id = id,
                                           job_name = id,
                                           executable = aws_glue_alpha.JobExecutable.python_shell(
                                               glue_version = get_version(version),
                                               python_version = aws_glue_alpha.PythonVersion.THREE,
                                               script = aws_glue_alpha.Code.from_asset(get_path(path)),
                                               runtime = aws_glue_alpha.Runtime.of("3.11")
                                           ),
                                           description = description,
                                           default_arguments = arguments,
                                           role = role,
                                           worker_type = get_worker_type(worker),
                                           worker_count = 2,
                                           max_retries = 0,
                                           timeout = get_timeout(timeout),
                                           max_concurrent_runs = 2

                                           )

        add_tags(self.job, tags)

        if schedule != None and schedule != "":
            trigger_name = f"{id}-trigger"
            schedule = f"cron({schedule})"
            self.trigger = aws_glue.CfnTrigger(self,
                                        id = trigger_name,
                                        actions = [aws_glue.CfnTrigger.ActionProperty(
                                            arguments = arguments,
                                            job_name = id,
                                            timeout = timeout
                                            )
                                        ],
                                        type = "SCHEDULED",
                                        name = trigger_name,
                                        description = schedule_description,
                                        schedule = schedule,
                                        start_on_creation = False
                                       )
            add_tags(self.trigger, tags)


