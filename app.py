#!/usr/bin/env python3
import os
import aws_cdk as cdk
from stacks import vpc_stack
from stacks import run_command_stack
from stacks import automation_stack
from stacks import stepfunctions_stack


env = cdk.Environment(
    account=os.environ.get("CDK_DEPLOY_ACCOUNT", os.environ["CDK_DEFAULT_ACCOUNT"]),
    region=os.environ.get("CDK_DEPLOY_REGION", os.environ["CDK_DEFAULT_REGION"]),
)


app = cdk.App()

vpc_stack.HandsonVpc(app, 'HandsonVpcStack', env=env)

run_command_stack.RunCommandStack(app, "RunCommandStack", env=env)

automation_stack.AutomationRunBookStack(app, 'AutomationRunBookStack', env=env)

stepfunctions_stack.StepfunctionsStack(app, 'StepfunctionsStack', env=env)


app.synth()
