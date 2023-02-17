#!/usr/bin/env python3
import os
import aws_cdk as cdk
from hook_cdk.hook_cdk_stack import HookCdkStack
env = cdk.Environment(region=os.environ["CDK_REGION"],account=os.environ["CDK_ACCOUNT"])
app = cdk.App()
HookCdkStack(app, "HookCdkStack",env=env)
app.synth()
