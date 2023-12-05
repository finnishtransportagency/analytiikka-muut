#!/usr/bin/env python3
import os

import aws_cdk as cdk

from stack.analytiikka_stack import AnalytiikkaStack


app = cdk.App()

projectname = app.node.try_get_context('project')
dev_account_name = os.environ["CDK_DEFAULT_ACCOUNT"]
region_name = os.environ["CDK_DEFAULT_REGION"]

AnalytiikkaStack(app, 
                     f"{projectname}-stack",
                     env = cdk.Environment(account = dev_account_name, region = region_name)
                )

#
# Yhteiset tagit kaikille
# Environment tag lisätään kaikille stagessa (dev/prod)
_tags_lst = app.node.try_get_context("tags")
if _tags_lst:
    for _t in _tags_lst:
        for k, v in _t.items():
            cdk.Tags.of(app).add(k, v, apply_to_launched_instances = True, priority = 300)



app.synth()
