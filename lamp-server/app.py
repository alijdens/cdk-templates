#!/usr/bin/env python3

import os

from aws_cdk import core
from lamp_server.lamp_server_stack import CdkStack


if 'SSH_KEY_NAME' not in os.environ:
    raise RuntimeError('SSH_KEY_NAME env variable must be declared in order to deploy')

app = core.App()
CdkStack(
    app,
    'lamp-server',
    ssh_key_name=os.environ['SSH_KEY_NAME'],
    env={
        'region': os.environ["CDK_DEFAULT_REGION"],
        'account': os.environ['CDK_DEFAULT_ACCOUNT'],
    }
)

app.synth()
