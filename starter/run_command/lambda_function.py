import os
import time
import boto3
from aws_lambda_powertools import Logger
from aws_xray_sdk import core as x_ray

logger = Logger()
x_ray.patch_all()

ec2 = boto3.client('ec2')
ssm = boto3.client('ssm')


def select_ec2_instance() -> list:
    resp = ec2.describe_instances(
        Filters=[{
                    'Name': 'instance-state-name',
                    'Values': ['running']
                }])

    logger.info({
        'function': 'ec2.describe_instances()',
        'resp:': resp})

    instances = [instance['InstanceId']
                 for reservation in resp['Reservations']
                 for instance in reservation['Instances']]
    return instances


def run_commands(instances, commands):

    response = ssm.send_command(
        InstanceIds=instances,      # Todo: InstanceIds or Targets
        # Targets=[                 # Todo: Tag指定されたInstanceにRunCommandを実行
        #     {
        #         'Key': 'tag:env',
        #         'Values': [
        #             'handson',
        #         ]
        #     }
        # ],
        DocumentName='AWS-RunShellScript',
        Parameters={
            'workingDirectory': ['/usr/bin'],  # default work directory: /usr/bin
            'commands': commands,
            'executionTimeout': ['7200'],
        },
        OutputS3KeyPrefix='run-shell',
        CloudWatchOutputConfig={
            'CloudWatchOutputEnabled': True  # log group: aws/ssm/AWS-RunShellScript
        }
    )
    logger.info({'function': 'ssm.send_command', 'response:': response})

    if not len(response['Command']['InstanceIds']):
        # 注意: Targetsでsend_command()するとInstanceIdが返らない。
        logger.info({'function': "exit() no instances in ['Command']['InstanceIds']"})
        return

    time.sleep(10)  # 非同期でRunCommandのOutputを取得する

    command_id = response['Command']['CommandId']
    for instance_id in response['Command']['InstanceIds']:
        output = ssm.get_command_invocation(CommandId=command_id, InstanceId=instance_id)
        logger.info({'output:': output})


@logger.inject_lambda_context(log_event=True)
def lambda_handler(event, context):

    try:
        # 起動中のInstanceを取得
        instances = select_ec2_instance()

        if not len(instances):  # no instance
            return
        logger.info({'function': 'select_ec2_instance()', 'instances:': instances})

        # SSM Run Commandをsend
        # commands = [
        #     'date +"%T.%N"',
        #     "echo %s > /tmp/from_lambda.log" % instances[0],
        #     "date",
        #     "pwd",
        #     "ls",
        #     "curl https://www.google.com/",
        #     'date +"%T.%N"',
        # ]
        commands = [
            'echo --- yum update ---',
            'sudo yum -y update',
        ]

        run_commands(instances=instances, commands=commands)
        return

    except Exception as e:
        logger.error(e)
        raise e
