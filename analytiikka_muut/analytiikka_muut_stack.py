from aws_cdk import (
    Stack,
    Environment
)

from aws_cdk.pipelines import (
    CodePipeline, 
    CodePipelineSource, 
    ShellStep, 
    ManualApprovalStep
)

import aws_cdk.aws_ssm as ssm

from constructs import Construct

from analytiikka_muut.analytiikka_muut_stage import AnalytiikkaMuutStage

"""
CICD stack

"""
class AnalytiikkaMuutStack(Stack):

    def __init__(self,
                 scope: Construct, 
                 construct_id: str, 
                 **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        devaccount = self.account
        appregion = self.region

        projectname = self.node.try_get_context('project')
        gituser = self.node.try_get_context('gituser')
        gitbranch = self.node.try_get_context('gitbranch')
        gitconnectionparameterident = self.node.try_get_context('gitconnectionparameterident')
        prodaccountparameter = self.node.try_get_context('prodaccountparameter')

        # print(f"cicd: git connection ident = {gitconnectionparameterident}")
        # print(f"cicd: prod account param = {prodaccountparameter}")

        gitconnectionid = ssm.StringParameter.value_from_lookup(self, f"{projectname}-{gitconnectionparameterident}")
        prodaccount = ssm.StringParameter.value_from_lookup(self, prodaccountparameter)

        # print(f"cicd: dev account = {devaccount}")
        # print(f"cicd: app region = {appregion}")
        # print(f"cicd: prod account = {prodaccount}")
        # print(f"cicd: git user = {gituser}")
        # print(f"cicd: git branch = {gitbranch}")
        # print(f"cicd: git connection = {gitconnectionid}")

        # Pipeline
        pipeline =  CodePipeline(self, 
                                 f"{projectname}-pipe",
                                 pipeline_name = f"{projectname}-pipe",
                                 docker_enabled_for_self_mutation = True,
                                 cross_account_keys = True,
                                 # docker_enabled_for_synth = True,
                                 # self_mutation = True,
                                 synth=ShellStep("Synth",
                                                 input=CodePipelineSource.connection(gituser,
                                                                                     gitbranch,
                                                                                     connection_arn = f"arn:aws:codestar-connections:{appregion}:{devaccount}:connection/{gitconnectionid}"
                                                                                    ),
                                                 commands=[
                                                     "npm install -g aws-cdk",
                                                     "python -m pip install -r requirements.txt",
                                                     "npm ci",
                                                     "npm run build",
                                                     "npx cdk synth"
                                                 ]
                                                )
                                )

        # Kehitys stage
        dev_stage = pipeline.add_stage(AnalytiikkaMuutStage(self,
                                                            f"{projectname}-dev",
                                                            "dev",
                                                            env = Environment(account = devaccount, region = appregion)
                                                            )
                                                           )

        # Tuotanto stage
        prod_stage = pipeline.add_stage(AnalytiikkaMuutStage(self,
                                                             f"{projectname}-prod",
                                                             "prod",
                                                             env = Environment(account = prodaccount, region = appregion)
                                                             )
                                                            )

        # Tuotannon manuaalihyväksyntä
        prod_stage.add_pre(ManualApprovalStep('prod-approval'))

