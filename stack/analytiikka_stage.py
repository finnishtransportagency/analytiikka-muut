from aws_cdk import (
    Stage,
    Environment,
    Tags
)

from constructs import Construct

from stack.analytiikka_services_stack import AnalytiikkaServicesStack

from stack.helper_tags import add_tags

"""
Pipeline stage

"""
class AnalytiikkaStage(Stage):

    def __init__(self,
                 scope: Construct, 
                 construct_id: str,
                 environment: str,
                 **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        projectname = self.node.try_get_context('project')

        account = self.account
        region = self.region

        # print(f"stage {environment}: project = '{projectname}'")
        print(f"stage {environment}: account = '{account}'")
        print(f"stage {environment}: region = '{region}'")
        
        services_stack = AnalytiikkaServicesStack(self, 
                                                      f"{projectname}-services-stack-{environment}", 
                                                      environment,
                                                      env = Environment(account = account, region = region )
                                                      )
        
        Tags.of(services_stack).add("Environment", environment, apply_to_launched_instances = True, priority = 300)
        tags = self.node.try_get_context("tags")
        add_tags(services_stack, tags)

