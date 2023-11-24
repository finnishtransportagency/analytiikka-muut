from aws_cdk import (
    aws_iam,
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




def add_tags(job, tags):
    if tags:
        for _t in tags:
            for k, v in _t.items():
                Tags.of(job).add(k, v, apply_to_launched_instances = True, priority = 300)



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


def get_timeout(timeout: int) -> Duration:
    value = Duration.minutes(1)
    if timeout != None and timeout > 0:
        value = Duration.minutes(timeout)
    return(value)


def get_version(version: str) -> aws_glue_alpha.GlueVersion:
    value = aws_glue_alpha.GlueVersion.V4_0
    if version != "" and version != None:
        value = aws_glue_alpha.GlueVersion.of(version)
    return(value)


def get_path(path: str) -> os.path:
    return(os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), path))




"""

id: Ajon nimi
path: polku projektissa (= /glue/<jobname>)
type: glueetl (= Spark ETL), pythonshell (= Python script), gluestreaming (= Spark streaming), glueRay (= Ray)
timout: aikaraja minuutteina
description: Kuvaus
worker: G.1X, G.2X, G.4X, G.8X, G.025X, Z.2X
version: glue versio
role: IAM roolin nimi
tags: Lisätagit
arguments: oletusparametrit
connections: connectit
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
                 connection_name: str = None,
                 enable_spark_ui: bool = False
                 ):
        super().__init__(scope, id)



        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_glue/CfnJob.html
        # connections = aws_glue.CfnJob.ConnectionsListProperty(connections=["connections"])
        # execution_property=glue.CfnJob.ExecutionPropertyProperty(max_concurrent_runs=123)

        # connectionlist = None
        # if connections != None:
        #     connectionlist = aws_glue.CfnJob.ConnectionsListProperty(connections)
        
        # script_path = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), path)
        # print(f"asset path = '{script_path}'")

        #if connection_name:
        #    connection = aws_glue_alpha.Connection.from_connection_name(self, id = "id", connection_name = connection_name)

        # TODO: connection


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
                                           max_concurrent_runs = 2
                                           )

        add_tags(self.job, tags)



        """
        Ajastus

        TODO: EI TESTATTU

        schedule: cron expressio
        description: Kuvaus
        timeout: Aikaraja minuutteina
        arguments: Parametrit. Nämä korvaavat ajon oletusparametrit jos annettu


        """
        def schedule(schedule: str,
                     description: str = None,
                     timeout: int = None,
                     arguments: dict = None):

            trigger_name = f"{self.job.name}-trigger"

            schedule = f"cron({schedule})"

            self.trigger = aws_glue.CfnTrigger(self,
                                               trigger_name,
                                               name = trigger_name,
                                               actions = [aws_glue.CfnTrigger.ActionProperty(
                                                   arguments = arguments,
                                                   job_name = self.job.name,
                                                   timeout = timeout
                                                   )
                                               ],
                                               type = "SCHEDULED",
                                               description = description,
                                               schedule = schedule,
                                               start_on_creation = False
                                              )
            



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
                 arguments: dict = None
                 ):
        super().__init__(scope, id)



        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_glue/CfnJob.html
        # connections = aws_glue.CfnJob.ConnectionsListProperty(connections=["connections"])
        # execution_property=glue.CfnJob.ExecutionPropertyProperty(max_concurrent_runs=123)

        # script_path = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), path)
        # print(f"asset path = '{script_path}'")

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


