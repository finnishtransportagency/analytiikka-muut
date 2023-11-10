from aws_cdk import (
    Stack,
    Environment,
    aws_secretsmanager,
    aws_codepipeline_actions
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
        gitrepo = self.node.try_get_context('gitrepo')
        gitbranch = self.node.try_get_context('gitbranch')
        gittokensecretname = self.node.try_get_context('gittokensecretname')
        
        
        prodaccountparameter = self.node.try_get_context('prodaccountparameter')
        # print(f"cicd: prod account param = {prodaccountparameter}")

        # gitconnectionparameterident = self.node.try_get_context('gitconnectionparameterident')
        # gitconnectionid = ssm.StringParameter.value_from_lookup(self, f"{projectname}-{gitconnectionparameterident}")
        # print(f"cicd: git connection ident = {gitconnectionparameterident}")

        prodaccount = ssm.StringParameter.value_from_lookup(self, prodaccountparameter)

        # print(f"cicd: dev account = {devaccount}")
        # print(f"cicd: app region = {appregion}")
        # print(f"cicd: prod account = {prodaccount}")


        gitsecret = aws_secretsmanager.Secret.from_secret_name_v2(self, "gittoken", secret_name = gittokensecretname)
        # print(f"cicd: git repo = {gitrepo}")
        # print(f"cicd: git branch = {gitbranch}")
        # print(f"cicd: git token = {gitsecret.secret_value}")
        

        # Pipeline
        pipeline =  CodePipeline(self, 
                                 f"{projectname}-pipe",
                                 pipeline_name = f"{projectname}-pipe",
                                 docker_enabled_for_self_mutation = True,
                                 cross_account_keys = True,
                                 # docker_enabled_for_synth = True,
                                 # self_mutation = True,
                                 synth=ShellStep("Synth",
                                                 input=CodePipelineSource.git_hub(repo_string = gitrepo,
                                                                                  branch = gitbranch,
                                                                                  authentication = gitsecret.secret_value,
                                                                                  trigger = aws_codepipeline_actions.GitHubTrigger("WEBHOOK")
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

        """
        .connection(gituser,
                                            gitbranch,
                                            connection_arn = f"arn:aws:codestar-connections:{appregion}:{devaccount}:connection/{gitconnectionid}"
                                           ),
        """


        """
        synth: new ShellStep("Synth", {
  input: CodePipelineSource.gitHub("jokurepo", "main", {
    authentication: SecretValue.secretsManager("github-token"),
    trigger: GitHubTrigger.WEBHOOK,
  }),
        """

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

