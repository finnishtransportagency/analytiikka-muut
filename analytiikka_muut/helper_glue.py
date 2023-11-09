from aws_cdk import (
    aws_glue,
    aws_s3_assets,
    Tags
)

import os

from constructs import Construct


"""
Apukoodi glue- ajojen luontiin


"""



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
class PythonGlueJob(Construct):

    def __init__(self,
                 scope: Construct, 
                 id: str, 
                 path: str,
                 type: str,
                 timeout: any,
                 description: str = None,
                 worker: str = None,
                 version: str = None,
                 role: str = None,
                 tags: dict = None,
                 arguments: dict = None,
                 connections: list[str] = None
                 ):
        super().__init__(scope, id)

        if version == "" or version == None:
            version = "4.0"

        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_glue/CfnJob.html
        # connections = aws_glue.CfnJob.ConnectionsListProperty(connections=["connections"])
        # execution_property=glue.CfnJob.ExecutionPropertyProperty(max_concurrent_runs=123)

        connectionlist = None
        if connections != None:
            connectionlist = aws_glue.CfnJob.ConnectionsListProperty(connections)


        
        self.id = id

        script_path = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), path)
        script_asset = aws_s3_assets.Asset(self, "GlueScriptAsset", script_path)

        self.job = aws_glue.CfnJob(self,
                                        name = id,
                                        description = description,
                                        command = {
                                            "name": type,
                                            "python_version": "3",
                                            "script_location": f"s3://{script_asset.s3_bucket_name}/{script_asset.s3_object_key}"
                                        },
                                        role = role,
                                        timeout = timeout,

                                        default_arguments = arguments,
                                        connections = connectionlist,

                                        # HUOM: max_capacity tai worker type jne. Ei molempia
                                        #  max_capacity=None,
                                        glue_version = version,
                                        worker_type = worker,
                                        number_of_workers = 2,
                                        max_retries = 0
                                        )
        



        """
        Ajastus

        schedule: cron expressio
        description: Kuvaus
        timeout: Aikaraja minuutteina
        arguments: Parametrit. Nämä korvaavat ajon oletusparametrit jos annettu


        """
        def create_glue_job_schedule(schedule: str,
                                     description: str = None,
                                     timeout: int = None,
                                     arguments: dict = None):

            cfn_trigger = aws_glue.CfnTrigger(self,
                                              f"{self.id}-trigger",
                                              actions = [aws_glue.CfnTrigger.ActionProperty(
                                                  arguments = arguments,
                                                  job_name = self.job.name,
                                                  timeout = timeout
                                                  )
                                              ],
                                              type = "SCHEDULED",
                                              # the properties below are optional
                                              description = description,
                                              name = f"{self.id}-trigger",
                                              schedule = schedule,
                                              start_on_creation = False
                                             )




        if tags:
            for _t in tags:
                for k, v in _t.items():
                    Tags.of(self.job).add(k, v, apply_to_launched_instances = True, priority = 300)



